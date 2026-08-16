from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.cards import HAND_CARDS, HAND_COUNT, possible_hands_mask
from hunl.blockers import legal_pairs_mask
from hunl.evaluator import rank7
from hunl.flop_allin import (
    FlopAllInEquity,
    UNORDERED_RUNOUTS_PER_PRIVATE_PAIR,
    ORDERED_RUNOUTS_PER_PRIVATE_PAIR,
    numerator_sha256,
)


def direct_pair_numerator(board3, h0, h1) -> tuple[int, int]:
    bset = set(map(int, board3))
    a, b = map(int, HAND_CARDS[h0])
    c, d = map(int, HAND_CARDS[h1])
    if any(x in bset for x in (a,b,c,d)) or len({a,b,c,d}) < 4:
        return 0, 0
    rem = [x for x in range(52) if x not in bset and x not in {a,b,c,d}]
    assert len(rem) == 45
    pairs = np.asarray(list(itertools.combinations(rem, 2)), dtype=np.int8)
    assert pairs.shape == (990, 2)
    c0 = np.empty((990, 7), dtype=np.int8)
    c1 = np.empty((990, 7), dtype=np.int8)
    c0[:, 0] = a; c0[:, 1] = b
    c1[:, 0] = c; c1[:, 1] = d
    c0[:, 2:5] = np.asarray(board3, dtype=np.int8)
    c1[:, 2:5] = np.asarray(board3, dtype=np.int8)
    c0[:, 5:] = pairs; c1[:, 5:] = pairs
    r0, r1 = rank7(c0), rank7(c1)
    s = np.sign(r0.astype(np.int64) - r1.astype(np.int64))
    return int(s.sum()), int(s.size)


def sha(a): return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def main():
    board = (0, 5, 10)
    t0 = time.perf_counter()
    eq = FlopAllInEquity(board)
    elapsed = time.perf_counter() - t0
    n = eq.numerator
    assert n.dtype == np.int16 and n.shape == (HAND_COUNT, HAND_COUNT)
    assert np.array_equal(n, -n.T)
    assert np.all(np.diag(n) == 0)
    assert int(np.max(np.abs(n))) <= UNORDERED_RUNOUTS_PER_PRIVATE_PAIR
    legal_pair = legal_pairs_mask(board)
    illegal_nonzero = int(np.count_nonzero(n[~legal_pair]))
    assert illegal_nonzero == 0

    legal = possible_hands_mask(board)
    hands = np.flatnonzero(legal)
    rng = np.random.default_rng(170101724)
    pair_checks = []
    while len(pair_checks) < 64:
        h0, h1 = map(int, rng.choice(hands, size=2, replace=False))
        if len(set(map(int, HAND_CARDS[h0])) | set(map(int, HAND_CARDS[h1]))) != 4:
            continue
        ref, cnt = direct_pair_numerator(board, h0, h1)
        assert cnt == 990
        got = int(n[h0, h1])
        assert got == ref, (h0, h1, got, ref)
        pair_checks.append((h0, h1, got))

    # Independent small-support CFV recount from pair numerators.
    # Use unique supports and then iterate the actual non-zero range indices.
    # This avoids a false mismatch if a hand id appears more than once in the
    # random pair-check list (numpy assignment would overwrite duplicates).
    support0 = []
    support1 = []
    for h0, h1, _ in pair_checks:
        if h0 not in support0 and len(support0) < 12:
            support0.append(h0)
        if h1 not in support1 and len(support1) < 12:
            support1.append(h1)
        if len(support0) == 12 and len(support1) == 12:
            break
    assert len(support0) == 12 and len(support1) == 12
    r0 = np.zeros(HAND_COUNT, dtype=np.float64)
    r1 = np.zeros(HAND_COUNT, dtype=np.float64)
    z0 = rng.random(len(support0)); z0 /= z0.sum()
    z1 = rng.random(len(support1)); z1 /= z1.sum()
    r0[np.asarray(support0, dtype=np.int64)] = z0
    r1[np.asarray(support1, dtype=np.int64)] = z1
    pot = 20000
    got = eq.get_value(board, pot, r0, r1)
    ref = np.zeros_like(got)
    nz0 = np.flatnonzero(r0)
    nz1 = np.flatnonzero(r1)
    for h0 in nz0:
        for h1 in nz1:
            if len(set(map(int, HAND_CARDS[h0])) | set(map(int, HAND_CARDS[h1]))) != 4:
                continue
            num, cnt = direct_pair_numerator(board, int(h0), int(h1))
            assert cnt == 990
            v = pot * (num / 990.0)
            ref[0, h0] += r1[h1] * v
            ref[1, h1] += r0[h0] * (-v)
    # CFVs are defined for every possible own private hand, including hands
    # with zero own reach.  The independent recount above intentionally only
    # computes rows/columns for the chosen own-hand supports, so compare those
    # entries rather than the untouched zero reference entries elsewhere.
    err0 = float(np.max(np.abs(got[0, nz0] - ref[0, nz0])))
    err1 = float(np.max(np.abs(got[1, nz1] - ref[1, nz1])))
    err = max(err0, err1)
    assert err < 2e-12, (err0, err1)
    zero = float(np.dot(r0, got[0]) + np.dot(r1, got[1]))
    assert abs(zero) < 2e-10, zero

    result = {
      'schema':'HUNL_FLOP_ALLIN_CERT_V1',
      'board3':list(board),
      'future_public_cards':49,
      'ordered_runouts_per_disjoint_private_pair':ORDERED_RUNOUTS_PER_PRIVATE_PAIR,
      'unordered_final_boards_per_disjoint_private_pair':UNORDERED_RUNOUTS_PER_PRIVATE_PAIR,
      'global_unordered_board_completions_enumerated':1176,
      'numerator_dtype':'int16',
      'numerator_sha256':numerator_sha256(board),
      'antisymmetry_exact':True,
      'direct_private_pair_recounts':len(pair_checks),
      'direct_pair_mismatches':0,
      'small_support_cfv_max_abs_error_chips':err,
      'small_support_zero_sum_residual_chips':zero,
      'illegal_pair_nonzero_entries': illegal_nonzero,
      'cfv_sha256':sha(got),
      'status':'COMBINATORIAL/EVALUATOR-EXACT; no private DeepStack implementation claim'
    }
    out=Path(__file__).with_name('HUNL_FLOP_ALLIN_CERT.json')
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
    print(f'matrix_build_wall_seconds_this_run={elapsed:.6f}', file=sys.stderr)

if __name__=='__main__': main()
