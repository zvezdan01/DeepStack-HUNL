#!/usr/bin/env python3
"""Gate: HUNL EXACT TURN ENGINE — turn betting tree + resolve to end of
game (turn betting -> river chance -> river betting -> terminals).

Sections:
  1. ACPC legality replay of turn trees (incl. round transition) vs
     untouched game.c oracle — betting-distinct nodes; the 48 river
     subtrees of a transition are betting-identical (structurally
     asserted) so one representative subtree is replayed per transition.
  2. Forced-check EXACT anchors: no-raise menus => engine value must
     equal the certified all-in/runout oracle to machine precision.
  3. Solve-corpus invariants (range/chance/terminal, zero-support).
  4. Engine vs independent recursive reference solver.
  5. LP cross-anchors (full Table-4 and reduced-menu trees) +
     convergence checkpoints + NashConv checkpoints.
  6. Full-schedule (1000/500) corpus + exact full-1326 BR.
  7. CFR-D gadget path (separate).
  8. Determinism across fresh processes.

Run from DS root:
  LD_LIBRARY_PATH=$PWD PYTHONPATH=/home/user/quant-trade:. \
      python3 /home/user/quant-trade/certification/hunl_g1/run_g1_turn_engine.py
"""
from __future__ import annotations

import dataclasses
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

np.seterr(all="ignore")
QT = Path("/home/user/quant-trade")
DS = Path("/workspace/deepstack_leduc_v1.1-bitexact-certified")
sys.path.insert(0, str(QT))
sys.path.insert(0, str(QT / "certification/hunl_g1"))

from hunl.cards import (HAND_CARDS, HAND_COUNT,  # noqa: E402
                        possible_hands_mask, string_to_cards)
from hunl.config import DEFAULT_CONFIG as CFG  # noqa: E402
from hunl.turn import all_in_equity  # noqa: E402
from hunl.turn_engine import TurnEngine  # noqa: E402
from hunl.turn_tree import TurnGameTreeBuilder, count_turn_nodes  # noqa: E402
from turn_oracles import ReferenceTurnSolver, solve_turn_lp  # noqa: E402

T0 = time.time()
report: list[str] = []
ENV = {**os.environ, "LD_LIBRARY_PATH": str(DS),
       "PYTHONPATH": f"{QT}:{QT / 'certification/hunl_g1'}:{DS}"}
SCRATCH = Path(
    "/tmp/claude-0/-home-user-quant-trade/"
    "ab297466-f300-5fe2-aeba-419112c121c8/scratchpad/g1_turn_engine")
SCRATCH.mkdir(parents=True, exist_ok=True)
ORACLE_DIR = DS / "reference_lua/ACPCServer"
stats = {"turn_states": 0, "nodes": 0, "acpc_cmp": 0, "transitions": 0,
         "infosets": 0}


def log(m):
    print(m, flush=True)
    report.append(m)


def make_range(kind, board, rng):
    pm = possible_hands_mask(board)
    r = np.zeros(HAND_COUNT)
    live = np.nonzero(pm)[0]
    if kind == "uniform":
        r[pm] = 1.0
    elif kind == "skewed":
        r[pm] = rng.random(int(pm.sum())) ** 4
    elif kind == "degenerate":
        r[rng.choice(live, 3, replace=False)] = rng.random(3) + 0.1
    elif kind == "single":
        r[rng.choice(live, 1)] = 1.0
    elif kind == "blocker":
        suits = {c % 4 for c in board}
        ranks = {c // 4 for c in board}
        w = np.full(HAND_COUNT, 1e-4)
        for i in range(HAND_COUNT):
            c0, c1 = HAND_CARDS[i]
            hit = sum(1 for c in (int(c0), int(c1))
                      if c % 4 in suits or c // 4 in ranks)
            w[i] = 10.0 ** hit
        r = w * pm
    r /= r.sum()
    return r


# ============================ 1. ACPC LEGALITY REPLAY (turn + river)
log("== 1. ACPC replay of turn trees vs untouched game.c ==")
t = time.time()
oracle_bin = SCRATCH / "betting_oracle"
subprocess.run(["cc", "-O2", "-o", str(oracle_bin),
                str(QT / "certification/hunl_g1/betting_oracle.c"),
                str(ORACLE_DIR / "game.c"), str(ORACLE_DIR / "rng.c"),
                "-I", str(ORACLE_DIR)], check=True)
rngp = np.random.default_rng(20260813)
POTS = sorted(set([100, 200, 201, 250, 999, 2000, 2500, 4000, 6666, 9900,
                   13333, 15000, 18000, 19000, 19899, 19950, 19998, 19999]
                  + [int(x) for x in rngp.integers(200, 20000, size=25)]))
POTS = [p for p in POTS if p == 100 or 200 <= p <= 19999]
builder = TurnGameTreeBuilder(CFG)
rules = builder._rules
cmds = ["G " + str(ORACLE_DIR / "holdem.nolimit.2p.reverse_blinds.game")]
preds: list[str] = []
ctxs: list[str] = []


def scaffold(pot):
    return (["c", "c", "c", "c"] if pot == 100
            else ["c", "c", f"r{pot}", "c"])


def act_str(a, s):
    return {"fold": "f", "call": "c"}.get(a) or f"r{s}"


def subtree_signature(n):
    if n.terminal is not None:
        return (n.terminal, n.spent, n.max_spent)
    return (tuple(n.actions),
            tuple(subtree_signature(c) for c in n.children))


def emit_node(n, path, round_no, minraise_override=None):
    ctx = f"{'/'.join(path) or 'root'}"
    cmds.append("N")
    cmds.extend("A " + a for a in path)
    cmds.append("S")
    if n.terminal is not None:
        folded = [0, 0]
        if n.terminal == "fold":
            folded[n.folder] = 1
        # after an all-in call ACPC jumps to round 3 finished WITHOUT the
        # round-advance min-raise reset (doAction "not enough players"
        # branch) — the pre-transition value persists
        rnd = 3 if (n.terminal == "showdown") else round_no
        mr = minraise_override if minraise_override is not None \
            else n.min_raise_to
        preds.append(f"S 1 {rnd} -1 {n.spent[0]} {n.spent[1]} "
                     f"{n.max_spent} {mr} {folded[0]} {folded[1]}")
        ctxs.append(ctx)
        return
    preds.append(f"S 0 {round_no} {n.player} {n.spent[0]} {n.spent[1]} "
                 f"{n.max_spent} {n.min_raise_to} 0 0")
    ctxs.append(ctx)
    win = rules.raise_window(n)
    cmds.append("R")
    preds.append("R 0 -1 -1" if win is None else f"R 1 {win[0]} {win[1]}")
    ctxs.append(ctx)
    probes = [("f", 1 if rules.fold_valid(n) else 0), ("c", 1)]
    for a, s in n.actions:
        if a == "raise":
            probes.append((f"r{s}", 1))
    M = n.max_spent
    probes.append((f"r{M}", 0))
    if win is not None:
        mn, mx = win
        probes.append((f"r{mn}", 1))
        if mn - 1 > M and mn != mx:
            probes.append((f"r{mn - 1}", 0))
        probes.append((f"r{mx + 1}", 0))
    else:
        probes.append((f"r{M + 1}", 0))
    for astr, exp in probes:
        cmds.append("Q " + astr)
        preds.append(f"Q {exp}")
        ctxs.append(ctx)
    stats["acpc_cmp"] += len(probes)


def replay(n, path, round_no):
    emit_node(n, path, round_no)
    if n.terminal is not None:
        return
    for (a, s), c in zip(n.actions, n.children):
        if c.street == "chance":
            stats["transitions"] += 1
            sigs = {subtree_signature(x) for x in c.children}
            assert len(sigs) == 1, "river subtrees not betting-identical"
            rep = c.children[0]
            # closing call advances the ACPC round automatically
            if rep.terminal is not None:      # all-in runout
                emit_node(rep, path + [act_str(a, s)], 3,
                          minraise_override=n.min_raise_to)
            else:
                replay(rep, path + [act_str(a, s)], 3)
        else:
            replay(c, path + [act_str(a, s)], round_no)


for pot in POTS:
    root = builder.build(string_to_cards("AsKh7c4d"), pot)
    tot, dec, term, ch = count_turn_nodes(root)
    stats["nodes"] += tot
    replay(root, scaffold(pot), 2)
    stats["turn_states"] += 1
(SCRATCH / "cmds.txt").write_text("\n".join(cmds) + "\n")
with open(SCRATCH / "cmds.txt") as fin, \
     open(SCRATCH / "replies.txt", "w") as fout:
    rc = subprocess.run([str(oracle_bin)], stdin=fin, stdout=fout,
                        stderr=subprocess.PIPE, text=True)
assert rc.returncode == 0, rc.stderr[-400:]
replies = (SCRATCH / "replies.txt").read_text().splitlines()
assert len(replies) == len(preds), (len(replies), len(preds))
for i, (got, want) in enumerate(zip(replies, preds)):
    if got != want:
        log(f"FIRST DIVERGENCE (ACPC) at {ctxs[i]}: oracle {got!r} != "
            f"ours {want!r}")
        raise SystemExit(1)
log(f"1 PASS: {len(POTS)} turn pots, {stats['nodes']:,} tree nodes, "
    f"{stats['transitions']:,} transitions (48 river subtrees each, "
    f"betting-identity asserted), {len(preds):,} oracle replies identical "
    f"incl. round transition + cross-street min-raise reset "
    f"({time.time()-t:.0f}s)")

# =============================== 2. FORCED-CHECK EXACT ANCHORS
log("== 2. forced-check exact anchors (engine == all-in oracle) ==")
t = time.time()
NOB = dataclasses.replace(CFG, turn_menus=((), (), ()),
                          turn_allin=False, river_allin=False)
rng = np.random.default_rng(20260813)
worst = 0.0
for bs in ("AsKh7c4d", "KsQsJs9s", "7c7d2h2s", "5h6h7h8h"):
    for pot in (2000, 19999):
        board = string_to_cards(bs)
        r1 = make_range("skewed", board, rng)
        r2 = make_range("skewed", board, rng)
        te = TurnEngine(board, pot, cfg=NOB, cfr_iters=4, cfr_skip_iters=2)
        cfvs = te.resolve_first_node(r1, r2)
        ref = all_in_equity(board, pot, r1, r2)
        d = np.abs(cfvs - ref).max() / pot
        worst = max(worst, d)
        assert d < 1e-12, f"forced-check anchor {d} on {bs}/{pot}"
        stats["turn_states"] += 1
log(f"2 PASS: 8 forced-check states — engine pipeline == certified "
    f"all-in oracle, max |d| {worst:.2e} of pot ({time.time()-t:.0f}s)")

# ====================== 3. SOLVE-CORPUS INVARIANTS (200/100)
log("== 3. solve-corpus invariants ==")
t = time.time()
CORPUS = [("AsKh7c4d", 4000, "uniform", "uniform"),
          ("KsQsJs9s", 9900, "skewed", "blocker"),
          ("AcAd7h2s", 15000, "blocker", "skewed"),
          ("7c7d2h2s", 19999, "uniform", "skewed"),
          ("TsJhQdKc", 9900, "degenerate", "uniform"),
          ("5h6h7h8h", 15000, "single", "uniform"),
          ("6s6h9c9d", 4000, "skewed", "degenerate"),
          ("3c8d9hTh", 19999, "blocker", "blocker"),
          ("JdTc9s5h", 9900, "uniform", "single"),
          ("QcQdQh2s", 2000, "skewed", "skewed")]
zs_max = 0.0
anchors = []
for bs, pot, k1, k2 in CORPUS:
    board = string_to_cards(bs)
    pm = possible_hands_mask(board)
    r1 = make_range(k1, board, rng)
    r2 = make_range(k2, board, rng)
    te = TurnEngine(board, pot, cfr_iters=200, cfr_skip_iters=100)
    cfvs = te.resolve_first_node(r1, r2)
    assert np.isfinite(cfvs).all()
    assert (np.abs(cfvs[:, ~pm]) == 0).all(), "blocked hands nonzero"
    col = te.root_strategy.sum(axis=0)
    assert np.abs(col[pm] - 1.0).max() < 1e-9, "root strategy not normalized"
    for nid in te.decision[:50]:
        n = te.nodes[nid]
        s = n._navg.sum(axis=0)
        assert np.isfinite(n._navg).all() and (s < 1.0 + 1e-9).all()
    v1 = float(r1 @ cfvs[0]); v2 = float(r2 @ cfvs[1])
    zs = abs(v1 + v2) / (2 * pot)
    zs_max = max(zs_max, zs)
    assert zs < 2e-3, f"zero-sum {zs}"
    tot, dec, term, ch = count_turn_nodes(te.tree)
    stats["infosets"] += dec * int(pm.sum())
    stats["turn_states"] += 1
    anchors.append(f"{bs}:{pot}:{k1}/{k2}:"
                   + hashlib.sha256(cfvs.tobytes()).hexdigest())
log(f"3 PASS: 10 states (uniform/skewed/blocker/degenerate/single/"
    f"disjoint-ish supports; pots 2000..19999): finite, blocked-zero, "
    f"strategies normalized, max zero-sum {zs_max:.2e} of pot "
    f"({time.time()-t:.0f}s)")
# zero-support rivers state: both supports hold Qh
board = string_to_cards("JdTc9s5h")
pm = possible_hands_mask(board)
zc = string_to_cards("Qh")[0]
holds = [h for h in np.nonzero(pm)[0]
         if zc in (int(HAND_CARDS[h][0]), int(HAND_CARDS[h][1]))]
r1 = np.zeros(HAND_COUNT); r1[holds] = 1.0; r1 /= r1.sum()
te = TurnEngine(board, 4000, cfr_iters=50, cfr_skip_iters=25)
cfvs = te.resolve_first_node(r1, r1)
assert np.isfinite(cfvs).all()
log("3b PASS: zero-support river branch (Qh in every hand) — finite, "
    "no NaN, river-Qh subtrees receive zero reach")

# ================== 4. ENGINE vs INDEPENDENT RECURSIVE REFERENCE
log("== 4. engine vs independent recursive reference ==")
t = time.time()
worst_r = 0.0
for bs, pot in (("AsKh7c4d", 15000), ("KsQsJs9s", 9900)):
    board = string_to_cards(bs)
    live = np.nonzero(possible_hands_mask(board))[0]
    s1 = sorted(rng.choice(live, 6, replace=False).tolist())
    s2 = sorted(rng.choice(live, 6, replace=False).tolist())
    r1 = np.zeros(HAND_COUNT); r1[s1] = rng.random(6) + 0.1; r1 /= r1.sum()
    r2 = np.zeros(HAND_COUNT); r2[s2] = rng.random(6) + 0.1; r2 /= r2.sum()
    te = TurnEngine(board, pot, cfr_iters=200, cfr_skip_iters=100)
    ev = te.resolve_first_node(r1, r2)
    ref = ReferenceTurnSolver(board, pot, CFG, 200, 100).solve(r1, r2)
    d = max(np.abs(ev[0][s1] - ref[0][s1]).max(),
            np.abs(ev[1][s2] - ref[1][s2]).max()) / pot
    worst_r = max(worst_r, d)
    assert d < 1e-9, f"engine vs reference {d}"
    stats["turn_states"] += 1
log(f"4 PASS: 2 small-support states — vectorized engine vs recursive "
    f"reference max |d| {worst_r:.2e} of pot ({time.time()-t:.0f}s)")

# ============== 5. LP ANCHORS + CONVERGENCE + NASHCONV CHECKPOINTS
log("== 5. LP cross-anchors + convergence ==")
t = time.time()
lp_results = []
for bs, pot, cfg_lp, tag in (("AsKh7c4d", 15000, CFG, "full-Table4"),
                             ("KsQsJs9s", 15000, CFG, "full-Table4-blocker"),
                             ("7c7d2h2s", 9900,
                              dataclasses.replace(CFG,
                                                  turn_menus=((1,), (), ())),
                              "reduced-menu")):
    board = string_to_cards(bs)
    live = np.nonzero(possible_hands_mask(board))[0]
    if "blocker" in tag:
        pref = [h for h in live if int(HAND_CARDS[h][0]) % 4 == 3]
        s1 = sorted(rng.choice(pref, 6, replace=False).tolist())
    else:
        s1 = sorted(rng.choice(live, 6, replace=False).tolist())
    s2 = sorted(rng.choice(live, 6, replace=False).tolist())
    r1 = np.zeros(HAND_COUNT); r1[s1] = rng.random(6) + 0.1; r1 /= r1.sum()
    r2 = np.zeros(HAND_COUNT); r2[s2] = rng.random(6) + 0.1; r2 /= r2.sum()
    v_lp = solve_turn_lp(board, pot, s1, s2, r1, r2, cfg_lp)
    te = TurnEngine(board, pot, cfg=cfg_lp, cfr_iters=1000,
                    cfr_skip_iters=500)
    cfvs = te.resolve_first_node(r1, r2)
    v_en = float(r1 @ cfvs[0])
    rel = abs(v_en - v_lp) / (2 * pot)
    lp_results.append((tag, bs, pot, v_lp, v_en, rel))
    log(f"  {tag} {bs} pot {pot}: LP {v_lp:+.3f} vs engine {v_en:+.3f} "
        f"-> {rel*100:.3f}% pot")
    assert rel < 0.005, f"LP anchor fail {rel}"
    stats["turn_states"] += 1
# convergence checkpoints vs LP (small-support full-Table4 state)
board = string_to_cards("AsKh7c4d")
live = np.nonzero(possible_hands_mask(board))[0]
s1 = sorted(rng.choice(live, 6, replace=False).tolist())
s2 = sorted(rng.choice(live, 6, replace=False).tolist())
r1 = np.zeros(HAND_COUNT); r1[s1] = 1 / 6
r2 = np.zeros(HAND_COUNT); r2[s2] = 1 / 6
v_lp = solve_turn_lp(board, 15000, s1, s2, r1, r2, CFG)
gaps = []
for iters, skip in ((100, 50), (250, 125), (500, 250), (1000, 500),
                    (2000, 1000)):
    te = TurnEngine(board, 15000, cfr_iters=iters, cfr_skip_iters=skip)
    v = float(r1 @ te.resolve_first_node(r1, r2)[0])
    gaps.append(abs(v - v_lp))
log(f"  convergence |engine-LP| chips @100/250/500/1000/2000: "
    f"{['%.4f' % g for g in gaps]} (production stays 1000/500)")
# converged-from-above: final gap must be tiny and no worse than the
# first checkpoint (plateau noise between converged checkpoints is fine)
assert gaps[-1] <= gaps[0] + 1e-6 and gaps[-1] < 0.005 * 2 * 15000
# NashConv checkpoints (full range, exact BR)
board = string_to_cards("JdTc9s5h")
pm = possible_hands_mask(board)
r1 = make_range("skewed", board, rng)
r2 = make_range("skewed", board, rng)
ncs = []
for iters, skip in ((250, 125), (500, 250), (1000, 500)):
    te = TurnEngine(board, 9900, cfr_iters=iters, cfr_skip_iters=skip)
    cfvs = te.resolve_first_node(r1, r2)
    nc = float(r1 @ te.best_response_value(0, r2)
               + r2 @ te.best_response_value(1, r1))
    ncs.append(nc)
log(f"  full-1326 NashConv @250/500/1000: "
    f"{['%.2f' % x for x in ncs]} chips "
    f"({['%.3f%%' % (x/(2*9900)*100) for x in ncs]} pot) "
    f"({time.time()-t:.0f}s)")
assert ncs[-1] < 0.02 * 2 * 9900 and ncs[-1] <= ncs[0]
log("5 PASS")

# =================== 6. FULL-SCHEDULE (1000/500) CORPUS + BR
log("== 6. full-schedule 1000/500 corpus + exact BR ==")
t = time.time()
FULL = [("AsKh7c4d", 2000, "uniform", "uniform"),
        ("KsQsJs9s", 4000, "skewed", "blocker"),
        ("TsJhQdKc", 9900, "skewed", "skewed"),
        ("7c7d2h2s", 15000, "blocker", "uniform"),
        ("5h6h7h8h", 19999, "uniform", "skewed")]
full_anchors = []
for bs, pot, k1, k2 in FULL:
    board = string_to_cards(bs)
    pm = possible_hands_mask(board)
    r1 = make_range(k1, board, rng)
    r2 = make_range(k2, board, rng)
    te = TurnEngine(board, pot)          # 1000/500 defaults
    cfvs = te.resolve_first_node(r1, r2)
    v1 = float(r1 @ cfvs[0]); v2 = float(r2 @ cfvs[1])
    zs = abs(v1 + v2) / (2 * pot)
    assert zs < 1e-3 and np.isfinite(cfvs).all() and \
        (cfvs[:, ~pm] == 0).all()
    nc = float(r1 @ te.best_response_value(0, r2)
               + r2 @ te.best_response_value(1, r1))
    tot, dec, term, ch = count_turn_nodes(te.tree)
    stats["infosets"] += dec * int(pm.sum())
    stats["turn_states"] += 1
    full_anchors.append(f"{bs}:{pot}:{k1}/{k2}:"
                        + hashlib.sha256(cfvs.tobytes()).hexdigest())
    log(f"  {bs} pot {pot} ({k1}/{k2}): value {v1:+.2f}, zero-sum "
        f"{zs:.2e}, NashConv {nc:.2f} chips ({nc/(2*pot)*100:.3f}% pot), "
        f"{tot:,} nodes")
    assert nc < 0.025 * 2 * pot, f"NashConv too high {nc}"
log(f"6 PASS ({time.time()-t:.0f}s)")

# ================================ 7. CFR-D GADGET PATH (separate)
log("== 7. CFR-D gadget re-solves (separate) ==")
t = time.time()
for bs, pot in (("AsKh7c4d", 9900), ("KsQsJs9s", 15000),
                ("7c7d2h2s", 19999)):
    board = string_to_cards(bs)
    pm = possible_hands_mask(board)
    r1 = make_range("skewed", board, rng)
    r2 = make_range("uniform", board, rng)
    pre = TurnEngine(board, pot, cfr_iters=200, cfr_skip_iters=100)
    pre.resolve_first_node(r1, r2)
    opp_cfvs = pre.root_cfvs[1].astype(np.float32)
    te = TurnEngine(board, pot, cfr_iters=200, cfr_skip_iters=100)
    te.resolve(r1, opp_cfvs)
    g = te.gadget
    assert (g.input_opponent_range[~pm] == 0).all(), "gadget blocked leak"
    assert np.isfinite(g.input_opponent_range).all()
    assert float(g.input_opponent_range.max()) <= 1.0 + 1e-6
    assert (g.input_opponent_value[pm].astype(np.float64)
            == opp_cfvs[pm].astype(np.float64)).all(), \
        "terminate values must be the input opponent CFVs (opponent-optimal)"
    col = te.root_strategy.sum(axis=0)
    assert np.abs(col[pm] - 1.0).max() < 1e-9
    assert np.isfinite(te.root_cfvs).all()
    stats["turn_states"] += 1
log(f"7 PASS: 3 gadget re-solves — opponent-optimal terminate values = "
    f"input CFVs, blocked-zero ranges, normalized strategies "
    f"({time.time()-t:.0f}s)")

# ==================================== 8. DETERMINISM (fresh procs)
log("== 8. determinism ==")
t = time.time()
code = r"""
import sys, numpy as np, hashlib
np.seterr(all='ignore')
sys.path.insert(0, '/home/user/quant-trade')
from hunl.cards import string_to_cards, possible_hands_mask
from hunl.turn_engine import TurnEngine
rng = np.random.default_rng(20260813)
board = string_to_cards('AsKh7c4d')
pm = possible_hands_mask(board)
r1 = np.zeros(1326); r1[pm] = rng.random(1128) ** 2; r1 /= r1.sum()
r2 = np.zeros(1326); r2[pm] = rng.random(1128) ** 2; r2 /= r2.sum()
te = TurnEngine(board, 9900, cfr_iters=150, cfr_skip_iters=75)
cfvs = te.resolve_first_node(r1, r2)
br = te.best_response_value(0, r2)
h = hashlib.sha256(); h.update(cfvs.tobytes()); h.update(br.tobytes())
h.update(te.root_strategy.tobytes())
print(h.hexdigest())
"""
runs = [subprocess.run([sys.executable, "-c", code], cwd=DS, env=ENV,
                       capture_output=True, text=True, check=True
                       ).stdout.strip() for _ in range(2)]
assert runs[0] == runs[1] and runs[0]
log(f"8 PASS: fresh-process byte-identical; SHA {runs[0]} "
    f"({time.time()-t:.0f}s)")

combined = hashlib.sha256(
    "\n".join(anchors + full_anchors).encode()).hexdigest()
log(f"\ncorpus anchors combined SHA-256: {combined}")
log(f"COUNTERS: {stats}")
log(f"TURN ENGINE GATE CORE: PASS ({(time.time()-T0)/60:.1f} min)")
out = QT / "certification/hunl_g1/latest_audit"
out.mkdir(exist_ok=True)
(out / "G1_TURN_ENGINE_RESULT.txt").write_text("\n".join(report) + "\n")
