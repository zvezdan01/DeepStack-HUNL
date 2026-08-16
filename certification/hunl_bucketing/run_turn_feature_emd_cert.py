#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.bucket_features import (
    DEFAULT_EQUITY_BINS,
    emd_1d,
    emd_1d_integer_counts,
    turn_final_equity_histogram,
)
from hunl.cards import HAND_CARDS, HAND_COUNT, make_card, possible_hands_mask
from hunl.evaluator import rank_board_hands
from hunl.blockers import blocker_matrix


def permute_suits(cards, perm):
    return tuple((int(c) // 4) * 4 + int(perm[int(c) % 4]) for c in cards)


def hand_id_from_cards(c0, c1):
    lo, hi = sorted((int(c0), int(c1)))
    # frozen lexicographic HAND_CARDS; binary lookup is unnecessary for cert size
    matches = np.flatnonzero((HAND_CARDS[:, 0] == lo) & (HAND_CARDS[:, 1] == hi))
    assert len(matches) == 1
    return int(matches[0])


def slow_river_equity(board4, hand_id, river):
    """Independent scalar-style recount using rank_board_hands but explicit opponent loop."""
    board5 = tuple(board4) + (int(river),)
    ranks = rank_board_hands(board5)
    hero = int(ranks[hand_id])
    hc = {int(HAND_CARDS[hand_id, 0]), int(HAND_CARDS[hand_id, 1])}
    wins = ties = n = 0
    for oid in range(HAND_COUNT):
        oc0, oc1 = map(int, HAND_CARDS[oid])
        if oc0 in board5 or oc1 in board5 or oc0 in hc or oc1 in hc:
            continue
        n += 1
        opp = int(ranks[oid])
        if hero > opp:
            wins += 1
        elif hero == opp:
            ties += 1
    assert n == 990
    return 2 * wins + ties, 1980


def greedy_emd_counts(a, b):
    """Independent transport implementation (not cumulative-formula code)."""
    supply = [[i, int(v)] for i, v in enumerate(a) if v]
    demand = [[j, int(v)] for j, v in enumerate(b) if v]
    i = j = 0
    cost = 0
    while i < len(supply) and j < len(demand):
        moved = min(supply[i][1], demand[j][1])
        cost += moved * abs(supply[i][0] - demand[j][0])
        supply[i][1] -= moved
        demand[j][1] -= moved
        if supply[i][1] == 0:
            i += 1
        if demand[j][1] == 0:
            j += 1
    assert i == len(supply) and j == len(demand)
    return cost


def main():
    # Four deliberately varied legal turn states.
    examples = [
        ((0, 5, 10, 15), (20, 25)),
        ((3, 18, 32, 49), (7, 44)),
        ((4, 21, 34, 47), (1, 51)),
        ((8, 13, 38, 43), (17, 30)),
    ]
    feature_records = []
    suit_checks = 0
    slow_checks = 0
    stream = hashlib.sha256()

    for board, hero_cards in examples:
        hid = hand_id_from_cards(*hero_cards)
        f = turn_final_equity_histogram(board, hid)
        assert f.bins == DEFAULT_EQUITY_BINS == 50
        assert int(f.counts.sum()) == 46
        assert abs(float(f.probabilities.sum()) - 1.0) < 1e-15
        assert np.all((f.equity_numerators >= 0) & (f.equity_numerators <= f.equity_denominator))

        # Independent scalar recount for 8 fixed river positions per feature.
        positions = [0, 1, 5, 11, 19, 27, 35, 45]
        for pos in positions:
            num, den = slow_river_equity(board, hid, int(f.river_cards[pos]))
            assert den == f.equity_denominator
            assert num == int(f.equity_numerators[pos])
            slow_checks += 1

        # Global suit relabeling must preserve the exact histogram and sorted exact equities.
        for perm in itertools.permutations(range(4)):
            pb = permute_suits(board, perm)
            ph = permute_suits(hero_cards, perm)
            phid = hand_id_from_cards(*ph)
            pf = turn_final_equity_histogram(pb, phid)
            assert np.array_equal(pf.counts, f.counts)
            assert np.array_equal(np.sort(pf.equity_numerators), np.sort(f.equity_numerators))
            suit_checks += 1

        stream.update(np.asarray(board, dtype='<i2').tobytes())
        stream.update(np.asarray([hid], dtype='<i4').tobytes())
        stream.update(f.equity_numerators.astype('<i4').tobytes())
        stream.update(f.counts.astype('<i2').tobytes())
        feature_records.append({
            'board': list(board),
            'hand_cards': list(hero_cards),
            'hand_id': hid,
            'counts': f.counts.astype(int).tolist(),
            'equity_numerator_min': int(f.equity_numerators.min()),
            'equity_numerator_max': int(f.equity_numerators.max()),
            'mean_equity': float(f.equities.mean()),
        })

    # EMD exact tests.
    delta0 = np.zeros(50, dtype=np.int64); delta0[0] = 46
    delta49 = np.zeros(50, dtype=np.int64); delta49[49] = 46
    assert emd_1d_integer_counts(delta0, delta49) == 46 * 49
    assert emd_1d(delta0 / 46.0, delta49 / 46.0) == 49.0

    rng = np.random.default_rng(20260816)
    emd_random_checks = 0
    triangle_checks = 0
    for _ in range(500):
        # Multinomial gives equal total count 46, exactly like turn features.
        a = rng.multinomial(46, np.full(50, 1.0 / 50.0)).astype(np.int64)
        b = rng.multinomial(46, np.full(50, 1.0 / 50.0)).astype(np.int64)
        c = rng.multinomial(46, np.full(50, 1.0 / 50.0)).astype(np.int64)
        fast = emd_1d_integer_counts(a, b)
        slow = greedy_emd_counts(a.tolist(), b.tolist())
        assert fast == slow
        # Probability form is exactly count cost / 46 up to FP rounding.
        assert abs(emd_1d(a / 46.0, b / 46.0) - fast / 46.0) < 1e-12
        assert fast == emd_1d_integer_counts(b, a)
        ac = emd_1d_integer_counts(a, c)
        bc = emd_1d_integer_counts(b, c)
        assert fast <= ac + bc
        emd_random_checks += 1
        triangle_checks += 1

    result = {
        'schema': 'hunl-turn-equity-histogram-emd-cert-v1',
        'status': 'PASS',
        'provenance': {
            'deepstack_explicit': 'k-means with earth mover distance over hand-strength-like features; 1000 turn clusters',
            'cited_primary_method': 'final-round equity/hand-strength histogram, k-means, 1D EMD',
            'bins_50': 'CITED-METHOD RECONSTRUCTION DEFAULT; not published as a private DeepStack parameter',
            'equity': 'win + 1/2 tie vs uniform legal opponent, uniform public rollout',
        },
        'turn_feature_contract': {
            'future_river_cards_per_fixed_turn_hand': 46,
            'opponent_hands_per_river': 990,
            'equity_denominator': 1980,
            'histogram_bins': 50,
            'bin_width': 0.02,
        },
        'checks': {
            'features': len(feature_records),
            'independent_river_equity_recounts': slow_checks,
            'global_suit_permutations': suit_checks,
            'emd_fast_vs_independent_greedy': emd_random_checks,
            'emd_triangle_checks': triangle_checks,
            'max_delta_emd_bin_units': 49.0,
        },
        'feature_stream_sha256': stream.hexdigest(),
        'features': feature_records,
    }
    out = Path(__file__).with_name('HUNL_TURN_BUCKET_FEATURE_EMD_CERT.json')
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('status','checks','feature_stream_sha256')}, indent=2))


if __name__ == '__main__':
    main()
