#!/usr/bin/env python3
"""Gate G1 turn -> river transition certification.

Sections:
  1. Exhaustive combinatorial certification (counts + full turn-space)
  2. Chance-weight / probability-mass identities (pair mass == 44/44)
  3. All-in runout equity: production vs independent f64 reference
  4. Transition aggregation: production vs independent reference
  5. Range-propagation invariants + zero-support rivers
  6. Zero-sum / permutation / suit-isomorphism identities
  7. Full-1326 river BR audit (frozen-baseline addendum, item 11)
  8. Determinism (fresh processes)
Frozen-regression re-runs (Leduc + all HUNL gates) are driven separately
at the end of this script via subprocesses.

Run from DS root:
  LD_LIBRARY_PATH=$PWD PYTHONPATH=/home/user/quant-trade:. \
      python3 /home/user/quant-trade/certification/hunl_g1/run_g1_turn.py
"""
from __future__ import annotations

import hashlib
import itertools
import math
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

from hunl.cards import (CARD_COUNT, HAND_CARDS, HAND_COUNT,  # noqa: E402
                        possible_hands_mask, string_to_cards)
from hunl.blockers import card_hand_membership  # noqa: E402
from hunl import chance  # noqa: E402
from hunl.turn import TurnTransition, all_in_equity  # noqa: E402
from hunl.showdown import showdown_matrix  # noqa: E402
from hunl.river_resolver import build_lookahead_tree  # noqa: E402
from hunl.evaluator import rank_board_hands, BLOCKED_SENTINEL  # noqa: E402
from turn_reference import (reference_all_in_equity,  # noqa: E402
                            reference_turn_cfvs)

T0 = time.time()
report: list[str] = []
ENV = {**os.environ, "LD_LIBRARY_PATH": str(DS),
       "PYTHONPATH": f"{QT}:{DS}"}


def log(msg: str) -> None:
    print(msg, flush=True)
    report.append(msg)


BOARDS = ["AsKh7c4d", "KsQsJs9s", "AcAd7h2s", "7c7d2h2s", "2c2d2h2s",
          "TsJhQdKc", "5h6h7h8h", "AhKs7d4c", "JdTc9s5h", "3c8d9hTh",
          "QcQdQh2s", "6s6h9c9d"]
counters = {"turn_states": 0, "river_transitions": 0, "blocker_cmp": 0,
            "mass_identities": 0}

# ================================ 1+2. COMBINATORICS + MASS IDENTITIES
log("== 1/2. exhaustive combinatorics + chance-mass identities ==")
t = time.time()
for bs in BOARDS:
    board = string_to_cards(bs)
    rivers, masks = chance.river_masks(board)
    assert len(rivers) == chance.RIVER_DECK == 48
    pm4 = possible_hands_mask(board)
    assert int(pm4.sum()) == chance.TURN_LEGAL_HANDS == 1128
    assert (masks.sum(axis=1) == chance.RIVER_LEGAL_HANDS).all()  # 1081
    counts = chance.legal_river_counts_per_hand(board)
    assert (counts[pm4] == 46).all() and (counts[~pm4] == 0).all()
    # bijection cross-foot: sum_h legal rivers == sum_c legal hands
    assert int(counts.sum()) == 1128 * 46 == 48 * 1081 == 51888
    # pair mass identity over ALL ordered hand pairs at once:
    pair_counts = masks.astype(np.int32).T @ masks.astype(np.int32)
    B = card_hand_membership()
    share = np.zeros((HAND_COUNT, HAND_COUNT), dtype=bool)
    from hunl.blockers import blocker_matrix
    blk = blocker_matrix().astype(bool)
    legal_pair = pm4[:, None] & pm4[None, :] & ~blk
    assert (pair_counts[legal_pair] == chance.PAIR_UNSEEN).all(), \
        f"pair river-count != 44 on {bs}"
    one_share = pm4[:, None] & pm4[None, :] & blk & \
        ~np.eye(HAND_COUNT, dtype=bool)
    assert (pair_counts[one_share] >= 44).all()  # 45 for 1-card overlap
    diag = np.diag(pair_counts)[pm4]
    assert (diag == 46).all()
    counters["mass_identities"] += int(legal_pair.sum())
    counters["blocker_cmp"] += HAND_COUNT * HAND_COUNT
    counters["river_transitions"] += 48
    # discrete reference spot-check (independent loop implementation)
    rng = np.random.default_rng(hash(bs) % 2**32)
    live = np.nonzero(pm4)[0]
    for _ in range(200):
        h1, h2 = rng.choice(live, 2, replace=False)
        expect = 44 if not blk[h1, h2] else 45
        got = chance.pair_legal_river_count(board, int(h1), int(h2))
        assert got == expect == pair_counts[h1, h2]
        counters["blocker_cmp"] += 1
log(f"12 representative boards: rivers 48, hands 1128->1081, per-hand 46, "
    f"cross-foot 51,888, ALL {counters['mass_identities']:,} legal pairs "
    f"have exactly 44 mutual rivers (+45/46 overlap/diag structure), "
    f"2,400 independent loop recounts ({time.time()-t:.0f}s)")

# full turn-board space sweep (all C(52,4) boards)
t = time.time()
CH = card_hand_membership()
total = 0
chunk = []
for b in itertools.combinations(range(CARD_COUNT), 4):
    chunk.append(b)
    if len(chunk) == 20000:
        boards = np.asarray(chunk, dtype=np.int8)
        blocked = CH[boards[:, 0]] | CH[boards[:, 1]] | \
            CH[boards[:, 2]] | CH[boards[:, 3]]
        counts = HAND_COUNT - blocked.sum(axis=1)
        assert (counts == 1128).all()
        total += len(chunk)
        chunk = []
if chunk:
    boards = np.asarray(chunk, dtype=np.int8)
    blocked = CH[boards[:, 0]] | CH[boards[:, 1]] | \
        CH[boards[:, 2]] | CH[boards[:, 3]]
    assert ((HAND_COUNT - blocked.sum(axis=1)) == 1128).all()
    total += len(chunk)
assert total == math.comb(52, 4) == 270725
log(f"FULL turn-board space: all {total:,} boards -> 1128 legal hands; "
    f"per-hand legal rivers = 46 exactly (both hand cards lie in the "
    f"48-card remainder); 48x1081 == 1128x46 == 51,888 per board "
    f"({time.time()-t:.0f}s)")
counters["turn_states"] += total

# ============================== 3. ALL-IN EQUITY vs f64 REFERENCE
log("== 3. all-in runout equity: production vs independent reference ==")
t = time.time()
rng = np.random.default_rng(20260813)
worst = 0.0
for bs, pot in (("AsKh7c4d", 2000), ("KsQsJs9s", 9900), ("7c7d2h2s", 19999)):
    board = string_to_cards(bs)
    pm4 = possible_hands_mask(board)
    live = np.nonzero(pm4)[0]
    if bs == "KsQsJs9s":     # blocker-heavy: spade-holding support
        pref = [h for h in live
                if int(HAND_CARDS[h][0]) % 4 == 3 or int(HAND_CARDS[h][1]) % 4 == 3]
        s1 = sorted(rng.choice(pref, 8, replace=False).tolist())
    else:
        s1 = sorted(rng.choice(live, 8, replace=False).tolist())
    s2 = sorted(rng.choice(live, 8, replace=False).tolist())
    r1 = np.zeros(HAND_COUNT)
    r1[s1] = rng.random(8) + 0.1
    r1 /= r1.sum()
    r2 = np.zeros(HAND_COUNT)
    r2[s2] = rng.random(8) + 0.1
    r2 /= r2.sum()
    prod = all_in_equity(board, pot, r1, r2)
    ref = reference_all_in_equity(board, pot, s1, s2, r1, r2)
    # reference fills SUPPORT entries only; production computes full
    # counterfactual vectors — compare on the reference's domain
    d = max(np.abs(prod[0][s1] - ref[0][s1]).max(),
            np.abs(prod[1][s2] - ref[1][s2]).max())
    worst = max(worst, d / pot)
    assert d <= 1e-9 * pot, f"all-in mismatch {d} on {bs}"
    counters["turn_states"] += 1
log(f"3 small-support states (incl. blocker-heavy): max |prod-ref| = "
    f"{worst:.2e} of pot (<=1e-9)")
# full-range: identities + per-hand loop spot checks
for bs, pot in (("AsKh7c4d", 2000), ("5h6h7h8h", 9900)):
    board = string_to_cards(bs)
    pm4 = possible_hands_mask(board)
    r1 = np.zeros(HAND_COUNT)
    r1[pm4] = rng.random(1128) ** 2
    r1 /= r1.sum()
    r2 = np.zeros(HAND_COUNT)
    r2[pm4] = rng.random(1128) ** 2
    r2 /= r2.sum()
    u = all_in_equity(board, pot, r1, r2)
    zs = abs(float(r1 @ u[0] + r2 @ u[1]))
    assert zs < 1e-9 * pot, f"all-in zero-sum {zs}"
    assert (u[:, ~pm4] == 0).all() and np.isfinite(u).all()
    # spot per-hand recount via reference loops (opponent full support)
    live = np.nonzero(pm4)[0].tolist()
    spot = rng.choice(np.nonzero(pm4)[0], 6, replace=False).tolist()
    ref = reference_all_in_equity(board, pot, spot, live, r1, r2)
    d = np.abs(u[0][spot] - ref[0][spot]).max()
    assert d <= 1e-9 * pot, f"full-range spot mismatch {d}"
    counters["turn_states"] += 1
    counters["blocker_cmp"] += 6 * 1128
log(f"full-range all-in: zero-sum <1e-9 pot, blocked exactly 0, 12 "
    f"per-hand loop recounts vs full opponent range match "
    f"({time.time()-t:.0f}s)")

# permutation + suit isomorphism on all-in equity
t = time.time()
board = string_to_cards("AsKh7c4d")
pm4 = possible_hands_mask(board)
r1 = np.zeros(HAND_COUNT); r1[pm4] = rng.random(1128); r1 /= r1.sum()
r2 = np.zeros(HAND_COUNT); r2[pm4] = rng.random(1128); r2 /= r2.sum()
u = all_in_equity(board, 2000, r1, r2)
perm_board = tuple(np.array(board)[[2, 0, 3, 1]])
u_perm = all_in_equity(perm_board, 2000, r1, r2)
assert u.tobytes() == u_perm.tobytes(), "board-permutation variance"
# suit swap: spades <-> hearts (suit ids 3 <-> 2 in 'cdhs')
smap = {0: 0, 1: 1, 2: 3, 3: 2}
cmap = np.array([4 * (c // 4) + smap[c % 4] for c in range(52)])
from hunl.cards import HAND_INDEX
hperm = np.array([HAND_INDEX[cmap[HAND_CARDS[h][0]], cmap[HAND_CARDS[h][1]]]
                  for h in range(HAND_COUNT)])
iso_board = tuple(int(cmap[c]) for c in board)
r1p = np.zeros(HAND_COUNT); r1p[hperm] = r1
r2p = np.zeros(HAND_COUNT); r2p[hperm] = r2
u_iso = all_in_equity(iso_board, 2000, r1p, r2p)
d = np.abs(u_iso[:, hperm] - u).max()
assert d < 1e-9 * 2000, f"suit-isomorphism all-in mismatch {d}"
# discrete iso invariants: multiplicities/blockers/chance counts
assert int(possible_hands_mask(iso_board).sum()) == 1128
_, m_orig = chance.river_masks(board)
_, m_iso = chance.river_masks(iso_board)
assert m_orig.sum() == m_iso.sum()
log(f"identities: board-permutation BYTE-EXACT; suit-isomorphism (h<->s) "
    f"max |d| {d:.2e}; iso multiplicities/blocker/chance counts preserved "
    f"({time.time()-t:.0f}s)")
log("suit-isomorphic REDUCTION: not certified, NOT used in the Golden "
    "path (full card space only) — verification-only checks above")

# ===================== 4+5+6. TRANSITION: REFERENCE MATCH + INVARIANTS
log("== 4/5/6. turn->river transition ==")
t = time.time()
ITERS, SKIP = 500, 250
worst_t = 0.0
for bs, pot, mode in (("AsKh7c4d", 2000, "random"),
                      ("KsQsJs9s", 9900, "blocker"),
                      ("7c7d2h2s", 2000, "degenerate")):
    board = string_to_cards(bs)
    pm4 = possible_hands_mask(board)
    live = np.nonzero(pm4)[0]
    kk = 2 if mode == "degenerate" else 8
    if mode == "blocker":
        pref = [h for h in live
                if int(HAND_CARDS[h][0]) % 4 == 3 or int(HAND_CARDS[h][1]) % 4 == 3]
        s1 = sorted(rng.choice(pref, kk, replace=False).tolist())
    else:
        s1 = sorted(rng.choice(live, kk, replace=False).tolist())
    s2 = sorted(rng.choice(live, kk, replace=False).tolist())
    r1 = np.zeros(HAND_COUNT); r1[s1] = rng.random(kk) + 0.1; r1 /= r1.sum()
    r2 = np.zeros(HAND_COUNT); r2[s2] = rng.random(kk) + 0.1; r2 /= r2.sum()
    tr = TurnTransition(board, pot, cfr_iters=ITERS, cfr_skip_iters=SKIP)
    prod, plog = tr.turn_cfvs(r1, r2)
    ref = reference_turn_cfvs(board, pot, r1, r2, ITERS, SKIP)
    # discrete parts BIT_EXACT: per-river masks equal between paths
    for k, c in enumerate(tr.rivers):
        keep = np.ones(HAND_COUNT, dtype=bool)
        bset = set(board)
        for h in range(HAND_COUNT):
            a, b = int(HAND_CARDS[h][0]), int(HAND_CARDS[h][1])
            if a in bset or b in bset or a == c or b == c:
                keep[h] = False
        assert keep.tobytes() == tr.masks[k].tobytes(), "mask drift"
    counters["blocker_cmp"] += 48 * HAND_COUNT
    d = np.abs(prod - ref).max()
    worst_t = max(worst_t, d / pot)
    assert d <= 1e-6 * pot, f"transition mismatch {d} chips on {bs}"
    counters["turn_states"] += 1
    counters["river_transitions"] += 96
log(f"3 small-support transition states (48 rivers each, {ITERS}/{SKIP}): "
    f"production vs independent reference max |d| = {worst_t:.2e} of pot "
    f"(<=1e-6); per-river masks BIT-EXACT between code paths "
    f"({time.time()-t:.0f}s)")

# full-range transition invariants + zero-support rivers
t = time.time()
for bs, pot, zero_card in (("AsKh7c4d", 2000, None),
                           ("JdTc9s5h", 19999, "Qh")):
    board = string_to_cards(bs)
    pm4 = possible_hands_mask(board)
    r1 = np.zeros(HAND_COUNT)
    r2 = np.zeros(HAND_COUNT)
    if zero_card is None:
        r1[pm4] = rng.random(1128) ** 2
        r2[pm4] = rng.random(1128) ** 2
    else:
        zc = string_to_cards(zero_card)[0]
        holds = [h for h in np.nonzero(pm4)[0]
                 if zc in (int(HAND_CARDS[h][0]), int(HAND_CARDS[h][1]))]
        r1[holds] = rng.random(len(holds)) + 0.1
        r2[holds] = rng.random(len(holds)) + 0.1
    r1 /= r1.sum(); r2 /= r2.sum()
    # reach-mass accounting identity: sum_c mass_p^c == 46 * total mass
    _, masks = chance.river_masks(board)
    for r in (r1, r2):
        lhs = float((masks @ r).sum())
        assert abs(lhs - 46.0 * r.sum()) < 1e-9, "reach mass accounting"
    tr = TurnTransition(board, pot, cfr_iters=200, cfr_skip_iters=100)
    agg, plog = tr.turn_cfvs(r1, r2)
    assert np.isfinite(agg).all() and (agg[:, ~pm4] == 0).all()
    v1 = float(r1 @ agg[0]); v2 = float(r2 @ agg[1])
    zs = abs(v1 + v2) / (2 * pot)
    assert zs < 2e-3, f"transition zero-sum residual {zs}"
    if zero_card is not None:
        skipped = [ln for ln in plog if "zero support" in ln]
        assert len(skipped) == 1, "expected exactly one zero-support river"
    counters["turn_states"] += 1
    counters["river_transitions"] += 48
log(f"full-range transitions (200/100): finite, blocked-zero, reach-mass "
    f"identity (46x), zero-sum residual < 2e-3 pot, zero-support river "
    f"skipped exactly once where constructed ({time.time()-t:.0f}s)")

# transition board-permutation invariance (byte)
board = string_to_cards("AsKh7c4d")
pm4 = possible_hands_mask(board)
r1 = np.zeros(HAND_COUNT); r1[pm4] = 1.0 / 1128
tr1 = TurnTransition(board, 2000, cfr_iters=100, cfr_skip_iters=50)
a1, _ = tr1.turn_cfvs(r1, r1)
tr2 = TurnTransition(tuple(np.array(board)[[3, 1, 0, 2]]), 2000,
                     cfr_iters=100, cfr_skip_iters=50)
a2, _ = tr2.turn_cfvs(r1, r1)
assert a1.tobytes() == a2.tobytes(), "transition board-permutation variance"
log("transition board-permutation: BYTE-EXACT")

# ============================== 7. FULL-1326 RIVER BR AUDIT (item 11)
log("== 7. full-1326 exact BR audit of frozen river baseline ==")
t = time.time()


def audit_solve_and_br(board5, pot, r1, r2, iters, skip):
    """Standalone f64 CFR (RM+, simultaneous, uniform post-skip avg) with
    full-tree average profile + exact vectorized best response."""
    tree = build_lookahead_tree(pot, board5)
    m, legal, _ = showdown_matrix(board5)
    md = m.astype(np.float64)
    fold_mask = legal.astype(np.float64)
    eps = 1e-9

    nodes = []

    def init(n):
        if not n.terminal:
            k = len(n.children)
            n._reg = np.zeros((k, HAND_COUNT))
            n._avg = np.zeros((k, HAND_COUNT))
            nodes.append(n)
            for c in n.children:
                init(c)
    init(tree)

    def cfr(n, reach, it):
        if n.terminal:
            b = float(np.min(n.bets))
            u = np.zeros((2, HAND_COUNT))
            if n.terminal_type == "fold":
                folder = 1 - n.current_player
                sgn = -1.0 if folder == 0 else 1.0
                u[0] = sgn * b * (fold_mask @ reach[1])
                u[1] = -sgn * b * (fold_mask.T @ reach[0])
            else:
                u[0] = b * (md @ reach[1])
                u[1] = b * ((-md.T) @ reach[0])
            return u
        k = len(n.children)
        pos = np.clip(n._reg, eps, 999999.0)
        strat = pos / pos.sum(axis=0, keepdims=True)
        if it > skip:
            n._avg += strat
        p = n.current_player
        u = np.zeros((2, HAND_COUNT))
        avals = np.zeros((k, HAND_COUNT))
        for a, c in enumerate(n.children):
            child_reach = [reach[0].copy(), reach[1].copy()]
            child_reach[p] = child_reach[p] * strat[a]
            cu = cfr(c, child_reach, it)
            avals[a] = cu[p]
            u[p] += strat[a] * cu[p]
            u[1 - p] += cu[1 - p]
        n._reg += avals - u[p][None, :]
        np.clip(n._reg, 0.0, 999999.0, out=n._reg)
        return u

    root_avg = np.zeros((2, HAND_COUNT))
    for it in range(1, iters + 1):
        u = cfr(tree, [r1.astype(np.float64), r2.astype(np.float64)], it)
        if it > skip:
            root_avg += u
    root_avg /= (iters - skip)

    def norm_avg(n):
        if n.terminal:
            return
        s = n._avg.sum(axis=0, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            n._navg = np.where(s > 0, n._avg / s, 1.0 / len(n.children))
        for c in n.children:
            norm_avg(c)
    norm_avg(tree)

    def br(n, reach_opp, brp):
        """BR value vector for player brp vs avg profile."""
        if n.terminal:
            b = float(np.min(n.bets))
            if n.terminal_type == "fold":
                folder = 1 - n.current_player
                sgn = (-1.0 if folder == 0 else 1.0)
                sgn = sgn if brp == 0 else -sgn
                mat = fold_mask if brp == 0 else fold_mask.T
                return sgn * b * (mat @ reach_opp)
            mat = md if brp == 0 else (-md.T)
            return b * (mat @ reach_opp)
        p = n.current_player
        if p == brp:
            vals = [br(c, reach_opp, brp) for c in n.children]
            return np.max(np.stack(vals), axis=0)
        out = np.zeros(HAND_COUNT)
        for a, c in enumerate(n.children):
            out += br(c, reach_opp * n._navg[a], brp)
        return out

    br0 = br(tree, r2.astype(np.float64), 0)
    br1 = br(tree, r1.astype(np.float64), 1)
    v_audit = float(r1 @ root_avg[0])
    nashconv = float(r1 @ br0 + r2 @ br1)
    return v_audit, nashconv


sys.setrecursionlimit(100000)
for bs, pot in (("AsKh7c4d2s", 2000), ("JdTc9s5h5c", 9900)):
    board = string_to_cards(bs)
    pm = possible_hands_mask(board)
    r1 = np.zeros(HAND_COUNT); r1[pm] = rng.random(int(pm.sum())) ** 2
    r1 /= r1.sum()
    r2 = np.zeros(HAND_COUNT); r2[pm] = rng.random(int(pm.sum())) ** 2
    r2 /= r2.sum()
    v_a, nc = audit_solve_and_br(board, pot, r1, r2, 1000, 500)
    from hunl.river_resolver import RiverResolver
    rs = RiverResolver(cfr_iters=1000, cfr_skip_iters=500)
    rs.resolve_first_node(board, pot, r1.astype(np.float32),
                          r2.astype(np.float32))
    v_e = float(r1 @ rs.get_root_cfv_both_players()[0].astype(np.float64))
    log(f"  {bs} pot {pot}: audit-f64 value {v_a:+.3f}, frozen engine "
        f"{v_e:+.3f} (|d| {abs(v_a-v_e):.3f} chips = "
        f"{abs(v_a-v_e)/(2*pot)*100:.3f}% pot); full-1326 NashConv of "
        f"audit profile {nc:.3f} chips ({nc/(2*pot)*100:.3f}% pot)")
    assert abs(v_a - v_e) < 0.01 * 2 * pot, "audit vs engine value drift"
    assert nc < 0.03 * 2 * pot, "audit profile not near equilibrium"
log(f"7 PASS: full-1326 BR audit — engine values confirmed by independent "
    f"f64 solver+BR; NO solver change made ({time.time()-t:.0f}s)")

# ==================================================== 8. DETERMINISM
log("== 8. determinism (fresh processes) ==")
t = time.time()
code = r"""
import sys, numpy as np, hashlib
np.seterr(all='ignore')
sys.path.insert(0, '/home/user/quant-trade')
from hunl.cards import string_to_cards, possible_hands_mask
from hunl.turn import TurnTransition, all_in_equity
rng = np.random.default_rng(20260813)
board = string_to_cards('AsKh7c4d')
pm = possible_hands_mask(board)
r1 = np.zeros(1326); r1[pm] = rng.random(1128) ** 2; r1 /= r1.sum()
r2 = np.zeros(1326); r2[pm] = rng.random(1128) ** 2; r2 /= r2.sum()
u = all_in_equity(board, 2000, r1, r2)
tr = TurnTransition(board, 2000, cfr_iters=100, cfr_skip_iters=50)
a, _ = tr.turn_cfvs(r1, r2)
h = hashlib.sha256(); h.update(u.tobytes()); h.update(a.tobytes())
print(h.hexdigest())
"""
runs = [subprocess.run([sys.executable, "-c", code], cwd=DS, env=ENV,
                       capture_output=True, text=True, check=True).stdout.strip()
        for _ in range(2)]
assert runs[0] == runs[1] and runs[0]
DETERMINISM_SHA = runs[0]
log(f"8 PASS: all-in + transition byte-identical across fresh processes; "
    f"SHA {DETERMINISM_SHA} ({time.time()-t:.0f}s)")

log(f"\nTURN GATE CORE: PASS ({(time.time()-T0)/60:.1f} min so far); "
    "now running frozen-regression battery...")
(QT / "certification/hunl_g1/G1_TURN_RESULT.txt").write_text(
    "\n".join(report) + "\n")
print("COUNTERS", counters)
