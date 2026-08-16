from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.blockers import legal_pairs_mask
from hunl.cards import HAND_COUNT, possible_hands_mask
from hunl.flop_engine import FlopLookaheadEngine, MissingFlopAllInValueProvider
from hunl.flop_value_boundary import FlopTurnValueBoundary
from hunl.value_bucketing import BoardBucketMap, POSTFLOP_BUCKET_COUNT


def sha(a) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


class SyntheticProvider:
    """Deterministic integration fixture, not a reconstruction bucketizer."""
    bucket_count = POSTFLOP_BUCKET_COUNT

    def __init__(self):
        self.cache = {}

    def for_board(self, board):
        board = tuple(int(c) for c in board)
        if board not in self.cache:
            legal = possible_hands_mask(board)
            ids = np.full(HAND_COUNT, -1, dtype=np.int16)
            pos = np.flatnonzero(legal)
            # Board-dependent permutation to exercise per-board maps.
            shift = sum((i + 1) * c for i, c in enumerate(board)) % self.bucket_count
            ids[pos] = ((np.arange(pos.size, dtype=np.int64) * 37 + shift) % self.bucket_count).astype(np.int16)
            self.cache[board] = BoardBucketMap(board, ids)
        return self.cache[board]


class ZeroSumSyntheticNet:
    """Deterministic NN-like map with the exact outer zero-sum algebra."""
    def get_value(self, inputs: np.ndarray) -> np.ndarray:
        x = np.asarray(inputs, dtype=np.float32)
        r1, r2, pot = x[:, :1000], x[:, 1000:2000], x[:, 2000:2001]
        idx = np.arange(1000, dtype=np.float32)[None, :]
        raw1 = np.float32(0.31) * r1 - np.float32(0.17) * r2 + pot + idx * np.float32(1e-6)
        raw2 = np.float32(0.23) * r2 - np.float32(0.11) * r1 - pot - idx * np.float32(2e-6)
        raw = np.concatenate([raw1, raw2], axis=1).astype(np.float32)
        ranges = x[:, :2000]
        err = np.sum(raw * ranges, axis=1, keepdims=True, dtype=np.float64).astype(np.float32)
        return (raw - np.float32(0.5) * err).astype(np.float32)


class SyntheticAllIn:
    """Linear antisymmetric terminal oracle used only for integration testing."""
    def __init__(self, board3):
        legal = legal_pairs_mask(board3)
        i = np.arange(HAND_COUNT, dtype=np.int32)
        a = np.sign(i[:, None] - i[None, :]).astype(np.float64)
        a *= legal.astype(np.float64)
        self.a = a
        self.calls = 0

    def get_value(self, board3, pot_half, player0_reach, player1_reach):
        self.calls += 1
        r0 = np.asarray(player0_reach, dtype=np.float64)
        r1 = np.asarray(player1_reach, dtype=np.float64)
        out = np.empty((2, HAND_COUNT), dtype=np.float64)
        out[0] = float(pot_half) * (self.a @ r1)
        out[1] = float(pot_half) * (-(self.a.T @ r0))
        return out


def make_ranges(board3):
    legal = possible_hands_mask(board3)
    rng = np.random.default_rng(20260816)
    out = []
    for _ in range(2):
        r = np.zeros(HAND_COUNT, dtype=np.float64)
        z = rng.random(int(legal.sum()))
        z /= z.sum()
        r[legal] = z
        out.append(r)
    return out


def run_once():
    board3 = (0, 5, 10)
    pot_half = 9000
    iters, skip = 4, 2
    provider = SyntheticProvider()
    nn = ZeroSumSyntheticNet()
    box = FlopTurnValueBoundary(
        board3, nn, provider, cfr_iters=iters, cfr_skip_iters=skip
    )
    allin = SyntheticAllIn(board3)
    eng = FlopLookaheadEngine(
        board3, pot_half, box, allin, cfr_iters=iters, cfr_skip_iters=skip
    )
    r0, r1 = make_ranges(board3)
    cfv = eng.resolve_first_node(r0, r1)
    strat = eng.get_root_strategy()
    boundary_turn = eng.get_boundary_values_on_turn(board3 + (11,))

    assert cfv.shape == (2, HAND_COUNT)
    assert strat.shape[1] == HAND_COUNT
    assert boundary_turn.shape == (len(eng.boundaries), 2, HAND_COUNT)
    assert np.max(np.abs(strat.sum(axis=0) - 1.0)) < 3e-15
    assert np.all(boundary_turn[:, :, ~possible_hands_mask(board3 + (11,))] == 0)
    # Joint expected utilities from counterfactual root values must cancel.
    game_sum = float(np.dot(r0, cfv[0]) + np.dot(r1, cfv[1]))
    assert abs(game_sum) < 2e-3, game_sum

    return {
        'board3': list(board3),
        'pot_half': pot_half,
        'iters': iters,
        'skip': skip,
        'nodes': len(eng.nodes),
        'decision_nodes': len(eng.decision),
        'fold_terminals': len(eng.fold_terminals),
        'allin_terminals': len(eng.allin_terminals),
        'turn_boundaries': len(eng.boundaries),
        'boundary_pots': [int(x) for x in eng.boundary_pots],
        'allin_provider_calls': allin.calls,
        'root_cfv_sha256': sha(cfv),
        'root_strategy_sha256': sha(strat),
        'observed_turn_boundary_sha256': sha(boundary_turn),
        'weighted_zero_sum_residual_chips': game_sum,
    }


def main():
    # Missing terminal equity must fail closed when actually used.
    missing = MissingFlopAllInValueProvider()
    try:
        missing.get_value((0, 5, 10), 20000, np.zeros(HAND_COUNT), np.zeros(HAND_COUNT))
    except RuntimeError:
        fail_closed = 'PASS'
    else:
        raise AssertionError('missing all-in provider did not fail closed')

    a = run_once()
    b = run_once()
    assert a == b, (a, b)
    result = {
        'schema': 'HUNL_FLOP_ENGINE_CONTRACT_V1',
        'synthetic_dependencies': 'TEST_ONLY_NOT_RECONSTRUCTION',
        'repeat_run_exact': True,
        'missing_allin_provider_fail_closed': fail_closed,
        'run': a,
        'status': 'STRUCTURAL_INTEGRATION_CERT; original HUNL buckets/weights/all-in implementation not claimed',
    }
    out = Path(__file__).with_name('HUNL_FLOP_ENGINE_CONTRACT_CERT.json')
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
