#!/usr/bin/env python3
"""Gates G1.7 + G1.8 — parameterized (injected) golden CFR core + exact
HUNL river resolver certification.

Stages:
  A. Leduc regression gate (ZERO numerical change):
     A1 full DS pytest suite; A2 all frozen ds_scripts comparators;
     A3 injection-wrapper byte-equivalence vs golden engine on Leduc
        (plain + gadget resolves).
  B. CFR-D gadget at 1326 dims — separate unit certification
     (exact f32 hand-replication of two RM+ iterations, mask zeroing,
     opponent-optimal terminate-value semantics).
  C. HUNL river corpus — plain resolves: invariants + anchors.
  D. Independent LP cross-oracle (restricted supports) + convergence
     checkpoints.
  E. Gadget (CFR-D) river resolves — separate corpus + invariants.
  F. Determinism across fresh processes.

Run from DS repo root:
  LD_LIBRARY_PATH=$PWD PYTHONPATH=/home/user/quant-trade:. \
      python3 /home/user/quant-trade/certification/hunl_g1/run_g1_78.py
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

np.seterr(all="ignore")  # golden engine relies on IEEE inf/nan semantics

QT = Path("/home/user/quant-trade")
DS = Path("/workspace/deepstack_leduc_v1.1-bitexact-certified")
sys.path.insert(0, str(QT))
sys.path.insert(0, str(QT / "certification/hunl_g1"))

from hunl.cards import (HAND_COUNT, possible_hands_mask,  # noqa: E402
                        string_to_cards)
from hunl.river_resolver import (InjectedLookahead, RiverResolver,  # noqa: E402
                                 build_lookahead_tree, hunl_river_config)
from hunl.river_terminal import HunlRiverTerminalEquity  # noqa: E402
from hunl.showdown import showdown_matrix  # noqa: E402
from hunl.blockers import legal_pairs_mask  # noqa: E402
from lp_river_oracle import solve_lp  # noqa: E402

from deepstack_leduc.config import Config as LeducConfig  # noqa: E402
from deepstack_leduc.resolving import Resolving  # noqa: E402
from deepstack_leduc.terminal import TerminalEquity as LeducTerminal  # noqa: E402
from deepstack_leduc.tree import Node as GoldenNode, PokerTreeBuilder  # noqa: E402
from deepstack_leduc.cfrd_gadget import CFRDGadget  # noqa: E402
from deepstack_leduc.card_tools import possible_hand_indexes  # noqa: E402

T0 = time.time()
report: list[str] = []
ENV = {**os.environ, "LD_LIBRARY_PATH": str(DS), "PYTHONPATH": str(DS)}


def log(msg: str) -> None:
    print(msg, flush=True)
    report.append(msg)


def sha(*arrays) -> str:
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


# ================================================= A. LEDUC REGRESSION
log("== A. Leduc regression gate ==")
t = time.time()
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"],
                   cwd=DS, env=ENV, capture_output=True, text=True)
tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
assert r.returncode == 0, f"DS pytest suite FAILED: {tail}"
log(f"A1 DS pytest suite: {tail} ({time.time()-t:.0f}s)")

for script in ("compare_private_boards_480.py", "compare_continual_first_action.py",
               "compare_nn_root_trace.py", "compare_nn_boxes.py",
               "compare_root_cfv_both_players.py", "determinism_check.py",
               "m2_activation_probe.py", "regen_tree_manifest.py"):
    t = time.time()
    r = subprocess.run([sys.executable,
                        str(QT / "certification/ds_scripts" / script)],
                       cwd=DS, env=ENV, capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or ["<no output>"])[-1]
    assert r.returncode == 0, f"{script} FAILED: {r.stdout[-400:]}{r.stderr[-400:]}"
    log(f"A2 {script}: {last} ({time.time()-t:.0f}s)")

# A3: injected wrapper == golden engine, byte-for-byte, on Leduc
log("A3 wrapper byte-equivalence on Leduc (40 plain + 10 gadget resolves)...")
t = time.time()
lcfg = LeducConfig()
rng = np.random.default_rng(20260813)
plain_ok = gadget_ok = 0
for k in range(50):
    board = (int(rng.integers(0, 6)),)
    from deepstack_leduc.cards import possible_mask as leduc_possible
    pmask = leduc_possible(board)
    r1 = (rng.random(6) ** 2) * pmask
    r1 /= r1.sum()
    r2 = (rng.random(6) ** 2) * pmask
    r2 /= r2.sum()
    pot = float(rng.integers(100, 1199))
    node = GoldenNode(street=2, current_player=0,
                      bets=np.array([pot, pot]), board=board)
    golden = Resolving(lcfg)
    inj_tree_root = GoldenNode(street=2, current_player=0,
                               bets=np.array([pot, pot]), board=board)
    inj_tree = PokerTreeBuilder(lcfg).build_tree(inj_tree_root,
                                                 limit_to_street=True)
    inj = InjectedLookahead(lcfg, LeducTerminal, range_mask=None)
    inj.build_lookahead(inj_tree)
    if k < 40:
        gres = golden.resolve_first_node(node, r1, r2)
        inj.resolve_first_node(r1, r2)
    else:
        pre = Resolving(lcfg)
        pre.resolve_first_node(node, r1, r2)
        cfvs = pre.get_root_cfv()
        gres = golden.resolve(node, r1, cfvs)
        inj.resolve(r1, cfvs)
    ires = inj.get_results()
    same = (gres.strategy.tobytes() == ires.strategy.tobytes()
            and gres.achieved_cfvs.tobytes() == ires.achieved_cfvs.tobytes()
            and gres.children_cfvs.tobytes() == ires.children_cfvs.tobytes())
    if gres.root_cfvs_both_players is not None:
        same = same and (gres.root_cfvs_both_players.tobytes()
                         == ires.root_cfvs_both_players.tobytes())
    if not same:
        log(f"FIRST DIVERGENCE A3 resolve {k}: wrapper != golden")
        raise SystemExit(1)
    if k < 40:
        plain_ok += 1
    else:
        gadget_ok += 1
log(f"A3 PASS: {plain_ok} plain + {gadget_ok} gadget Leduc resolves "
    f"BYTE-IDENTICAL wrapper vs golden ({time.time()-t:.0f}s)")
log("A PASS: ZERO numerical change to Golden Leduc behavior "
    "(0 golden modules modified; new modules: hunl/river_terminal.py, "
    "hunl/river_resolver.py + harness)")

# ============================================ B. GADGET 1326 UNIT TESTS
log("== B. CFR-D gadget @ 1326 dims (separate unit certification) ==")
board = string_to_cards("AsKh7c4d2s")
mask = possible_hands_mask(board).astype(np.float32)
K = HAND_COUNT
rng = np.random.default_rng(42)
r1 = (rng.random(K).astype(np.float32) * mask)
r1 /= r1.sum()
opp_cfvs = (rng.standard_normal(K).astype(np.float32) * 100 * mask)
g = CFRDGadget(board, r1, opp_cfvs, hunl_river_config())
g.range_mask = mask
# exact f32 replication of two RM+ gadget iterations
play_vals1 = (rng.standard_normal(K).astype(np.float32) * 120 * mask)
play_vals2 = (rng.standard_normal(K).astype(np.float32) * 80 * mask)
ps = np.zeros(K, np.float32)
ts = np.ones(K, np.float32)
pr = np.zeros(K, np.float32)
tr = np.zeros(K, np.float32)
eps = np.float32(1.0 / 100_000_000.0)
for pv in (play_vals1, play_vals2):
    tot = pv * ps + opp_cfvs * ts
    pr = pr + (pv - tot)
    tr = tr + (opp_cfvs - tot)
    pr = np.clip(pr, eps, np.float32(999999.0))
    tr = np.clip(tr, eps, np.float32(999999.0))
    s = pr + tr
    ps = (pr / s) * mask
    ts = (tr / s) * mask
out1 = g.compute_opponent_range(play_vals1, 1)
out2 = g.compute_opponent_range(play_vals2, 2)
assert out2.tobytes() == ps.astype(np.float32).tobytes(), \
    "gadget f32 hand-replication mismatch"
assert (out1[mask == 0] == 0).all() and (out2[mask == 0] == 0).all(), \
    "gadget resurrected blocked hands"
assert np.isfinite(out1).all() and np.isfinite(out2).all()
# opponent-optimal terminate semantics: terminate value IS the input CFV
# vector (thesis ch.6 / cfrd_gadget.lua): where play_values << input cfvs,
# play probability must shrink
worse = (play_vals1 < opp_cfvs - 50) & (mask == 1)
assert out1[worse].mean() <= out1[(mask == 1)].mean()
log("B PASS: two-iteration exact f32 replication byte-identical; blocked "
    "hands stay zero; terminate values = input opponent CFVs "
    "(opponent-optimal constraint semantics); play-prob monotonicity sane")

# ==================================================== C. RIVER CORPUS
log("== C. HUNL river corpus — plain resolves ==")
BOARDS = ["AsKh7c4d2s", "KsQsJs9s2s", "AcAdAh2c2d", "TsJsQdKcAh",
          "7c7d2h2s3c", "5h6h7h8h9h", "2c2d2h2sKc", "AhKs7d4c4h",
          "JdTc9s5h5c", "3c8d9hThJc"]
rng = np.random.default_rng(20260813)


def make_range(kind: str, board, seed_rng) -> np.ndarray:
    pm = possible_hands_mask(board)
    r = np.zeros(HAND_COUNT)
    if kind == "uniform":
        r[pm] = 1.0
    elif kind == "skewed":
        r[pm] = seed_rng.random(int(pm.sum())) ** 4
    elif kind == "degenerate":
        live = np.nonzero(pm)[0]
        r[seed_rng.choice(live, 3, replace=False)] = seed_rng.random(3) + 0.1
    elif kind == "blocker":
        from hunl.cards import HAND_CARDS
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
    return r.astype(np.float32)


STATES = []
for b in BOARDS:
    STATES.append((b, 2000, "uniform", "uniform"))
STATES += [(BOARDS[0], 2000, "skewed", "skewed"),
           (BOARDS[1], 9900, "skewed", "uniform"),
           (BOARDS[3], 9900, "skewed", "skewed"),
           (BOARDS[4], 2000, "uniform", "skewed"),
           (BOARDS[5], 9900, "skewed", "skewed"),
           (BOARDS[0], 2000, "degenerate", "uniform"),
           (BOARDS[2], 9900, "degenerate", "degenerate"),
           (BOARDS[6], 2000, "uniform", "degenerate"),
           (BOARDS[1], 2000, "blocker", "uniform"),
           (BOARDS[5], 9900, "blocker", "blocker"),
           (BOARDS[6], 2000, "blocker", "skewed"),
           (BOARDS[7], 19999, "uniform", "uniform"),
           (BOARDS[8], 19999, "skewed", "skewed"),
           (BOARDS[9], 19999, "blocker", "uniform"),
           (BOARDS[8], 9900, "uniform", "uniform"),
           (BOARDS[9], 9900, "degenerate", "skewed"),
           (BOARDS[0], 100, "uniform", "uniform"),
           (BOARDS[3], 100, "skewed", "skewed")]

anchors = []
tot_nodes = tot_infosets = 0
zs_max_rel = 0.0
t = time.time()
for si, (bs, pot, k1, k2) in enumerate(STATES):
    board = string_to_cards(bs)
    r1 = make_range(k1, board, rng)
    r2 = make_range(k2, board, rng)
    rs = RiverResolver()
    res = rs.resolve_first_node(board, pot, r1, r2)
    both = rs.get_root_cfv_both_players()
    strat = res.strategy
    pm = possible_hands_mask(board)
    # invariants
    assert np.isfinite(both).all() and np.isfinite(strat).all(), (si, bs)
    col = strat.sum(axis=0)
    assert np.abs(col[pm] - 1.0).max() < 1e-3, f"strategy not normalized {si}"
    assert (strat >= 0).all() and (strat <= 1.0 + 1e-6).all()
    v1 = float(r1 @ both[0].astype(np.float64))
    v2 = float(r2 @ both[1].astype(np.float64))
    zs = abs(v1 + v2) / (2 * pot)
    zs_max_rel = max(zs_max_rel, zs)
    assert zs < 1e-3, f"zero-sum residual {zs} state {si}"
    def _count(n):
        return (1 if n.terminal else 1) + sum(_count(c) for c in n.children)

    def _decisions(n):
        return (0 if n.terminal else 1) + sum(_decisions(c) for c in n.children)

    nodes = _count(rs.lookahead_tree)
    tot_nodes += nodes
    tot_infosets += _decisions(rs.lookahead_tree) * int(pm.sum())
    anchors.append(f"{si}:{bs}:{pot}:{k1}/{k2}:{sha(strat, both)}")
log(f"C PASS: {len(STATES)} plain resolves (2000/1000, RM+/simultaneous/"
    f"uniform-post-omit); {tot_nodes:,} lookahead-tree nodes, "
    f"{tot_infosets:,} solved (node x live-hand) infosets; max zero-sum "
    f"residual {zs_max_rel:.2e} of pot ({time.time()-t:.0f}s)")
# all-tie analytic sanity: royal flush ON BOARD — nothing can beat the
# board, so every live matchup ties exactly. Premise verified from the
# certified ranks, not assumed.
board = string_to_cards("AsKsQsJsTs")
from hunl.evaluator import rank_board_hands, BLOCKED_SENTINEL
rr = rank_board_hands(board)
live_ranks = rr[rr != BLOCKED_SENTINEL]
assert (live_ranks == live_ranks[0]).all(), "royal board must be all-tie"
r1 = make_range("uniform", board, rng)
rs = RiverResolver()
rs.resolve_first_node(board, 2000, r1, r1)
both = rs.get_root_cfv_both_players()
v = float(r1 @ both[0].astype(np.float64))
assert abs(v) < 2000 * 0.02, f"all-tie board value should be ~0, got {v}"
log(f"C analytic: royal-on-board (verified universal tie) game value "
    f"{v:+.2f} chips ~ 0 as required")

# ======================================= D. LP CROSS-ORACLE + CONVERGENCE
log("== D. Independent LP cross-oracle (restricted supports) ==")
lp_rows = []
t = time.time()
lp_rng = np.random.default_rng(99)
LP_CASES = [("AsKh7c4d2s", 2000, 6, "random"), ("AsKh7c4d2s", 9900, 10, "random"),
            ("KsQsJs9s2s", 2000, 10, "blocker"), ("KsQsJs9s2s", 9900, 6, "random"),
            ("5h6h7h8h9h", 2000, 6, "blocker"), ("5h6h7h8h9h", 9900, 10, "random"),
            ("AcAdAh2c2d", 2000, 10, "random"), ("TsJsQdKcAh", 9900, 6, "random")]
worst_rel = 0.0
for bs, pot, kk, mode in LP_CASES:
    board = string_to_cards(bs)
    pm = possible_hands_mask(board)
    live = np.nonzero(pm)[0]
    if mode == "blocker":
        from hunl.cards import HAND_CARDS
        suits = {c % 4 for c in board}
        pref = [h for h in live if int(HAND_CARDS[h][0]) % 4 in suits]
        s1 = sorted(lp_rng.choice(pref, kk, replace=False).tolist())
    else:
        s1 = sorted(lp_rng.choice(live, kk, replace=False).tolist())
    s2 = sorted(lp_rng.choice(live, kk, replace=False).tolist())
    r1 = np.zeros(HAND_COUNT)
    r1[s1] = lp_rng.random(kk) + 0.05
    r1 /= r1.sum()
    r2 = np.zeros(HAND_COUNT)
    r2[s2] = lp_rng.random(kk) + 0.05
    r2 /= r2.sum()
    v_lp = solve_lp(board, pot, s1, s2, r1, r2)
    rs = RiverResolver()
    rs.resolve_first_node(board, pot, r1.astype(np.float32),
                          r2.astype(np.float32))
    both = rs.get_root_cfv_both_players()
    v_en = float(r1 @ both[0].astype(np.float64))
    rel = abs(v_en - v_lp) / (2 * pot)
    worst_rel = max(worst_rel, rel)
    lp_rows.append(f"  {bs} pot {pot} K={kk} {mode}: LP {v_lp:+.3f} vs "
                   f"engine {v_en:+.3f} -> |d|={abs(v_en-v_lp):.3f} chips "
                   f"({rel*100:.3f}% pot)")
    assert rel < 0.005, f"LP mismatch {rel} at {bs}/{pot}"
for row in lp_rows:
    log(row)
log(f"D PASS: 8/8 LP cross-anchors within 0.5% pot (worst {worst_rel*100:.3f}%) "
    f"({time.time()-t:.0f}s)")

log("D convergence checkpoints (|engine - LP| in chips):")
t = time.time()
for bs, pot, kk, mode in (LP_CASES[0], LP_CASES[2]):
    board = string_to_cards(bs)
    pm = possible_hands_mask(board)
    live = np.nonzero(pm)[0]
    s1 = sorted(lp_rng.choice(live, kk, replace=False).tolist())
    s2 = sorted(lp_rng.choice(live, kk, replace=False).tolist())
    r1 = np.zeros(HAND_COUNT)
    r1[s1] = 1.0 / kk
    r2 = np.zeros(HAND_COUNT)
    r2[s2] = 1.0 / kk
    v_lp = solve_lp(board, pot, s1, s2, r1, r2)
    gaps = []
    for iters, skip in ((250, 125), (500, 250), (1000, 500), (2000, 1000),
                        (4000, 2000)):
        rs = RiverResolver(cfr_iters=iters, cfr_skip_iters=skip)
        rs.resolve_first_node(board, pot, r1.astype(np.float32),
                              r2.astype(np.float32))
        v = float(r1 @ rs.get_root_cfv_both_players()[0].astype(np.float64))
        gaps.append(abs(v - v_lp))
    log(f"  {bs} pot {pot}: gaps {['%.3f' % g for g in gaps]}")
    assert min(gaps[-2:]) <= min(gaps[:2]) + 1e-9, "no convergence trend"
log(f"D convergence PASS ({time.time()-t:.0f}s)")

# ========================================= E. GADGET RIVER RESOLVES
log("== E. CFR-D gadget river resolves (separate corpus) ==")
t = time.time()
gadget_anchors = []
for si, (bs, pot, k1, k2) in enumerate(STATES[:8]):
    board = string_to_cards(bs)
    r1 = make_range(k1, board, rng)
    r2 = make_range(k2, board, rng)
    pre = RiverResolver()
    pre.resolve_first_node(board, pot, r1, r2)
    opp_cfvs = pre.results.root_cfvs.copy()
    rs = RiverResolver()
    rs.resolve(board, pot, r1, opp_cfvs)
    res = rs.results
    pm = possible_hands_mask(board)
    strat = res.strategy
    assert np.isfinite(strat).all()
    assert np.abs(strat.sum(axis=0)[pm] - 1.0).max() < 1e-3
    gadget = rs.lookahead.reconstruction_gadget
    orange = gadget.input_opponent_range
    assert (orange[~pm] == 0).all(), "gadget range resurrects blocked hands"
    assert np.isfinite(orange).all() and float(orange.max()) <= 1.0 + 1e-6
    gadget_anchors.append(f"g{si}:{sha(strat, res.achieved_cfvs)}")
log(f"E PASS: 8 gadget re-solves; opponent ranges blocked-zero, finite, "
    f"strategies normalized ({time.time()-t:.0f}s)")

# ==================================================== F. DETERMINISM
log("== F. determinism across fresh processes ==")
t = time.time()
code = r"""
import sys, numpy as np, hashlib
np.seterr(all='ignore')
sys.path.insert(0, '/home/user/quant-trade')
from hunl.cards import string_to_cards, possible_hands_mask
from hunl.river_resolver import RiverResolver
rng = np.random.default_rng(20260813)
out = []
for bs, pot in (("AsKh7c4d2s", 2000), ("KsQsJs9s2s", 9900),
                ("2c2d2h2sKc", 19999), ("5h6h7h8h9h", 2000)):
    board = string_to_cards(bs)
    pm = possible_hands_mask(board)
    r1 = np.zeros(1326); r1[pm] = rng.random(int(pm.sum())) ** 2; r1 /= r1.sum()
    r2 = np.zeros(1326); r2[pm] = rng.random(int(pm.sum())) ** 2; r2 /= r2.sum()
    rs = RiverResolver()
    res = rs.resolve_first_node(board, pot, r1.astype(np.float32), r2.astype(np.float32))
    h = hashlib.sha256()
    h.update(res.strategy.tobytes()); h.update(rs.get_root_cfv_both_players().tobytes())
    out.append(h.hexdigest())
print('|'.join(out))
"""
runs = [subprocess.run([sys.executable, "-c", code], cwd=DS, env=ENV,
                       capture_output=True, text=True, check=True).stdout.strip()
        for _ in range(2)]
assert runs[0] == runs[1] and runs[0], f"determinism drift: {runs}"
log(f"F PASS: 4 states x 2 fresh processes byte-identical "
    f"({time.time()-t:.0f}s); SHAs: {runs[0][:64]}...")

# terminal-matrix contract re-assert inside resolver context
board = string_to_cards("AsKh7c4d2s")
te = HunlRiverTerminalEquity(board)
m, legal, ranks = showdown_matrix(board)
assert te.call_matrix.tobytes() == np.ascontiguousarray(
    m.T, dtype=np.float32).tobytes()
assert te.fold_matrix.tobytes() == np.ascontiguousarray(
    legal_pairs_mask(board), dtype=np.float32).tobytes()
log("terminal contract: call = G1.3 showdown transpose, fold = G1.2 legal "
    "mask — byte-verified in resolver context")

log(f"\nCORPUS ANCHORS ({len(anchors)} plain + {len(gadget_anchors)} gadget):")
combined = hashlib.sha256(("\n".join(anchors + gadget_anchors)).encode()).hexdigest()
log(f"combined corpus SHA-256: {combined}")

log(f"\nG1.7+G1.8 RESULT: PASS (total {(time.time()-T0)/60:.1f} min)")
(QT / "certification/hunl_g1/G1_78_RESULT.txt").write_text(
    "\n".join(report) + "\n")
(QT / "certification/hunl_g1/G1_78_ANCHORS.txt").write_text(
    "\n".join(anchors + gadget_anchors) + "\n")
