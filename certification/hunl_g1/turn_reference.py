"""Independent float64 reference implementations for the turn -> river
transition (Gate G1 transition milestone).

Shares NO optimized code with hunl/turn.py:
  - all-in equity: pure per-hand-pair, per-river Python loops; showdown
    decided by direct evaluator rank comparison (no matrices, no
    vectorized masks); chance factor 1/44 applied per pair.
  - transition reference: enumerate legal rivers per state, build masked
    reach vectors by explicit per-hand loops, call the FROZEN certified
    river solver (the solver itself is the shared certified component by
    design), aggregate with explicit per-hand conditional sums.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.cards import HAND_CARDS, HAND_COUNT  # noqa: E402
from hunl.evaluator import rank_board_hands, BLOCKED_SENTINEL  # noqa: E402
from hunl.river_resolver import RiverResolver  # noqa: E402


def _cards_of(h: int) -> tuple[int, int]:
    return int(HAND_CARDS[h][0]), int(HAND_CARDS[h][1])


def reference_all_in_equity(board4, pot_half, support1, support2,
                            r1, r2) -> np.ndarray:
    """(2, 1326) float64 — brute force, small supports only."""
    board = [int(c) for c in board4]
    bset = set(board)
    out = np.zeros((2, HAND_COUNT), dtype=np.float64)
    rivers = [c for c in range(52) if c not in bset]
    ranks_by_river = {c: rank_board_hands(tuple(board) + (c,))
                      for c in rivers}
    for h1 in support1:
        a, b = _cards_of(h1)
        if a in bset or b in bset:
            continue
        for h2 in support2:
            x, y = _cards_of(h2)
            if x in bset or y in bset or len({a, b, x, y}) < 4:
                continue
            acc = 0.0
            n_legal = 0
            for c in rivers:
                if c in (a, b, x, y):
                    continue
                n_legal += 1
                rk = ranks_by_river[c]
                q1, q2 = int(rk[h1]), int(rk[h2])
                assert q1 != int(BLOCKED_SENTINEL) and \
                    q2 != int(BLOCKED_SENTINEL)
                acc += (1.0 / 44.0) * ((q1 > q2) - (q1 < q2))
            assert n_legal == 44, f"pair river count {n_legal}"
            out[0][h1] += float(pot_half) * r2[h2] * acc
            out[1][h2] += float(pot_half) * r1[h1] * (-acc)
    return out


def reference_turn_cfvs(board4, pot_half, r1, r2, cfr_iters,
                        cfr_skip_iters) -> np.ndarray:
    """(2, 1326) float64 — independent transition/aggregation code path
    around the frozen certified river solver."""
    board = [int(c) for c in board4]
    bset = set(board)
    rivers = sorted(c for c in range(52) if c not in bset)
    agg = np.zeros((2, HAND_COUNT), dtype=np.float64)
    for c in rivers:
        keep = np.ones(HAND_COUNT, dtype=bool)
        for h in range(HAND_COUNT):
            a, b = _cards_of(h)
            if a in bset or b in bset or a == c or b == c:
                keep[h] = False
        c1 = np.where(keep, np.asarray(r1, dtype=np.float64), 0.0)
        c2 = np.where(keep, np.asarray(r2, dtype=np.float64), 0.0)
        if float(c1.sum()) == 0.0 and float(c2.sum()) == 0.0:
            continue
        rs = RiverResolver(cfr_iters=cfr_iters,
                           cfr_skip_iters=cfr_skip_iters)
        rs.resolve_first_node(tuple(board) + (c,), int(pot_half),
                              c1.astype(np.float32), c2.astype(np.float32))
        both = rs.get_root_cfv_both_players().astype(np.float64)
        for p in (0, 1):
            for h in range(HAND_COUNT):
                if keep[h]:
                    agg[p][h] += both[p][h] / 44.0
    return agg
