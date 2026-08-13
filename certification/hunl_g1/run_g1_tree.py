#!/usr/bin/env python3
"""Gate G1 tree layer — certify hunl/config.py + hunl/tree.py against the
UNTOUCHED ACPC game.c (compiled verbatim together with rng.c;
betting_oracle.c is only a stdin driver).

EXHAUSTIVE corpus: every reachable river entry pot-half in HUNL —
{100} (unraised) plus every integer in [200, 19999] — 19,800 river
states. For every node of every tree, the state is replayed in the real
ACPC state machine from the hand start (pre-flop/flop/turn scaffold) and
we compare: full state snapshots, raiseIsValid windows, validity of every
tree action, and negative/boundary probes. Any mismatch = fail-fast.

Run from quant-trade root: python3 certification/hunl_g1/run_g1_tree.py
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.config import DEFAULT_CONFIG as CFG  # noqa: E402
from hunl.tree import RiverTreeBuilder, count_nodes  # noqa: E402

ORACLE_DIR = Path(
    "/workspace/deepstack_leduc_v1.1-bitexact-certified/reference_lua/ACPCServer")
GAME_FILE = ORACLE_DIR / "holdem.nolimit.2p.reverse_blinds.game"
SCRATCH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/g1_tree")
SCRATCH.mkdir(parents=True, exist_ok=True)
T0 = time.time()
report: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    report.append(msg)


POTS = [100] + list(range(2 * CFG.big_blind, CFG.stack))  # {100} u [200,19999]

oracle_bin = SCRATCH / "betting_oracle"
subprocess.run(
    ["cc", "-O2", "-o", str(oracle_bin),
     str(ROOT / "certification/hunl_g1/betting_oracle.c"),
     str(ORACLE_DIR / "game.c"), str(ORACLE_DIR / "rng.c"),
     "-I", str(ORACLE_DIR)], check=True)
gc_sha = hashlib.sha256((ORACLE_DIR / "game.c").read_bytes()).hexdigest()
log(f"oracle compiled from untouched game.c (sha256 {gc_sha}) + rng.c")
log(f"corpus: EXHAUSTIVE — all {len(POTS):,} reachable river entry pots")


def scaffold(pot_half: int) -> list[str]:
    if pot_half == CFG.big_blind:
        return ["c", "c", "c", "c", "c", "c"]
    return ["c", "c", f"r{pot_half}", "c", "c", "c"]


builder = RiverTreeBuilder(CFG)
cmd_f = open(SCRATCH / "commands.txt", "w")
pred_f = open(SCRATCH / "predicted.txt", "w")
ctx_f = open(SCRATCH / "ctx.txt", "w")
cmd_f.write("G " + str(GAME_FILE) + "\n")

stats = {"pots": len(POTS), "trees_nodes": 0, "decision_nodes": 0,
         "terminal_nodes": 0, "action_cmp": 0, "replies": 0}
boundary = {"short_allin_windows": 0, "allin_dedupe": 0, "menu_reduced": 0,
            "fold_illegal_checked": 0, "no_raise_states": 0,
            "exact_stack_exhaustion": 0, "min_raise_probes": 0}
manifests: list[str] = []
t_gen = time.time()


def emit(cmd_lines: list[str], pred_lines: list[str], ctx: str) -> None:
    cmd_f.write("\n".join(cmd_lines) + "\n")
    if pred_lines:
        pred_f.write("\n".join(pred_lines) + "\n")
        ctx_f.write((ctx + "\n") * len(pred_lines))
        stats["replies"] += len(pred_lines)


for pot in POTS:
    root = builder.build(pot)
    stats["trees_nodes"] += count_nodes(root)
    manifests.append(f"{pot}:{builder.manifest_sha256(root)}")
    base = scaffold(pot)

    def visit(node, path: list[str]):
        prefix = base + path
        ctx = f"pot={pot} path={'/'.join(path) or 'root'}"
        cmds = ["N"] + ["A " + a for a in prefix] + ["S"]
        preds: list[str] = []
        if node.terminal is not None:
            stats["terminal_nodes"] += 1
            folded = [0, 0]
            if node.terminal == "fold":
                folded[node.folder] = 1
                assert node.folder in (0, 1)
            else:
                assert node.spent[0] == node.spent[1], ctx
            preds.append(f"S 1 3 -1 {node.spent[0]} {node.spent[1]} "
                         f"{node.max_spent} {node.min_raise_to} "
                         f"{folded[0]} {folded[1]}")
            emit(cmds, preds, ctx)
            return
        stats["decision_nodes"] += 1
        preds.append(f"S 0 3 {node.player} {node.spent[0]} {node.spent[1]} "
                     f"{node.max_spent} {node.min_raise_to} 0 0")
        win = builder.raise_window(node)
        cmds.append("R")
        if win is None:
            preds.append("R 0 -1 -1")
        else:
            preds.append(f"R 1 {win[0]} {win[1]}")
        probes: list[tuple[str, int]] = [
            ("f", 1 if builder.fold_valid(node) else 0), ("c", 1)]
        if not builder.fold_valid(node):
            boundary["fold_illegal_checked"] += 1
        our_raises = sorted(s for a, s in node.actions if a == "raise")
        for r in our_raises:
            probes.append((f"r{r}", 1))
        M = node.max_spent
        probes.append((f"r{M}", 0))
        if win is None:
            boundary["no_raise_states"] += 1
            probes.append((f"r{M + 1}", 0))
            probes.append((f"r{CFG.stack}", 0))
        else:
            mn, mx = win
            probes.append((f"r{mn}", 1))
            boundary["min_raise_probes"] += 1
            if mn == mx == CFG.stack:
                boundary["short_allin_windows"] += 1
                if M + 1 < mn:
                    probes.append((f"r{M + 1}", 0))
                    probes.append((f"r{mx - 1}", 0))
            elif mn - 1 > M:
                probes.append((f"r{mn - 1}", 0))
            probes.append((f"r{mx + 1}", 0))
            cands = CFG.raise_to_candidates(M, node.action_depth)
            if any(c > mx for c in cands):
                boundary["menu_reduced"] += 1
            if any(c == mx for c in cands):
                boundary["allin_dedupe"] += 1
            if mx == CFG.stack and any(s == CFG.stack for s in our_raises):
                boundary["exact_stack_exhaustion"] += 1
        for astr, expv in probes:
            cmds.append("Q " + astr)
            preds.append(f"Q {expv}")
        stats["action_cmp"] += len(probes)
        emit(cmds, preds, ctx)

        for (a, s), child in zip(node.actions, node.children):
            assert child.spent[0] >= node.spent[0] and \
                child.spent[1] >= node.spent[1], "non-monotonic contribution"
            assert max(child.spent) <= CFG.stack, "negative remaining stack"
            assert sum(child.spent) >= sum(node.spent), "pot not conservative"
        assert len(set(node.actions)) == len(node.actions), "dup actions"
        assert node.actions, "decision node without legal action"
        for (a, s), child in zip(node.actions, node.children):
            visit(child, path + [{"fold": "f", "call": "c"}.get(a) or f"r{s}"])

    visit(root, [])

cmd_f.close(); pred_f.close(); ctx_f.close()
log(f"generated: {stats['trees_nodes']:,} nodes "
    f"({stats['decision_nodes']:,} decision, {stats['terminal_nodes']:,} "
    f"terminal), {stats['replies']:,} predicted oracle replies "
    f"in {time.time()-t_gen:.0f}s")

# --------------------------------------------------------- run oracle --
t = time.time()
with open(SCRATCH / "commands.txt") as fin, \
     open(SCRATCH / "replies.txt", "w") as fout:
    rc = subprocess.run([str(oracle_bin)], stdin=fin, stdout=fout,
                        stderr=subprocess.PIPE, text=True)
if rc.returncode != 0:
    log(f"ORACLE FAIL-FAST rc={rc.returncode}: {rc.stderr[-500:]}")
    raise SystemExit(1)
log(f"oracle executed in {time.time()-t:.0f}s")

# ------------------------------------------------------------ compare --
t = time.time()
n = 0
with open(SCRATCH / "replies.txt") as fr, \
     open(SCRATCH / "predicted.txt") as fp, \
     open(SCRATCH / "ctx.txt") as fc:
    for got, want, ctx in zip(fr, fp, fc):
        n += 1
        if got != want:
            log(f"FIRST DIVERGENCE at reply {n}: oracle {got.strip()!r} != "
                f"ours {want.strip()!r} [{ctx.strip()}]")
            raise SystemExit(1)
    assert next(fr, None) is None and next(fp, None) is None, \
        "reply/prediction count mismatch"
assert n == stats["replies"]
log(f"oracle comparison: ALL {n:,} replies IDENTICAL ({time.time()-t:.0f}s)")

# ------------------------------------------------- determinism anchor --
combined = hashlib.sha256("\n".join(manifests).encode()).hexdigest()
code = ("import sys, hashlib; sys.path.insert(0, %r); "
        "from hunl.tree import RiverTreeBuilder; "
        "from hunl.config import DEFAULT_CONFIG as C; "
        "b = RiverTreeBuilder(); "
        "pots = [100] + list(range(2*C.big_blind, C.stack)); "
        "m = [str(p) + ':' + b.manifest_sha256(b.build(p)) for p in pots]; "
        "print(hashlib.sha256(chr(10).join(m).encode()).hexdigest())"
        % str(ROOT))
subs = [subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, check=True).stdout.strip()
        for _ in range(2)]
assert subs[0] == subs[1] == combined, f"determinism drift {subs}"
log(f"determinism: combined manifest SHA-256 {combined} identical across "
    "in-process + 2 fresh subprocess builds (all pots)")

log("boundary coverage: " + ", ".join(f"{k}={v:,}" for k, v in boundary.items()))
for k, v in boundary.items():
    assert v > 0, f"boundary case {k} not exercised"

log(f"\nG1 TREE RESULT: PASS (total {time.time()-T0:.0f}s)")
(ROOT / "certification/hunl_g1/G1_TREE_RESULT.txt").write_text(
    "\n".join(report) + "\n")
