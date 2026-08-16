from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.cards import HAND_COUNT, possible_hands_mask
from hunl.flop_allin import FlopAllInEquity, numerator_sha256
from hunl.flop_engine import FlopLookaheadEngine
from hunl.flop_value_boundary import FlopTurnValueBoundary
from hunl.value_bucketing import BoardBucketMap, POSTFLOP_BUCKET_COUNT


def sha(a) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


class SyntheticProvider:
    """Deterministic boundary fixture ONLY; not a reconstruction bucketizer."""
    bucket_count = POSTFLOP_BUCKET_COUNT

    def __init__(self):
        self.cache = {}

    def for_board(self, board):
        board = tuple(int(c) for c in board)
        if board not in self.cache:
            legal = possible_hands_mask(board)
            ids = np.full(HAND_COUNT, -1, dtype=np.int16)
            pos = np.flatnonzero(legal)
            shift = sum((i + 1) * c for i, c in enumerate(board)) % self.bucket_count
            ids[pos] = ((np.arange(pos.size, dtype=np.int64) * 37 + shift) % self.bucket_count).astype(np.int16)
            self.cache[board] = BoardBucketMap(board, ids)
        return self.cache[board]


class ZeroSumSyntheticNet:
    """Deterministic boundary fixture with the released zero-sum outer algebra."""
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
    box = FlopTurnValueBoundary(board3, nn, provider, cfr_iters=iters, cfr_skip_iters=skip)
    allin = FlopAllInEquity(board3)
    eng = FlopLookaheadEngine(board3, pot_half, box, allin, cfr_iters=iters, cfr_skip_iters=skip)
    r0, r1 = make_ranges(board3)
    cfv = eng.resolve_first_node(r0, r1)
    strat = eng.get_root_strategy()
    boundary_turn = eng.get_boundary_values_on_turn(board3 + (11,))

    assert cfv.shape == (2, HAND_COUNT)
    assert np.max(np.abs(strat.sum(axis=0) - 1.0)) < 3e-15
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
        'exact_allin_numerator_sha256': numerator_sha256(board3),
        'root_cfv_sha256': sha(cfv),
        'root_strategy_sha256': sha(strat),
        'observed_turn_boundary_sha256': sha(boundary_turn),
        'weighted_zero_sum_residual_chips': game_sum,
    }


def main():
    a = run_once()
    b = run_once()
    assert a == b, (a, b)
    result = {
        'schema': 'HUNL_FLOP_ENGINE_EXACT_TERMINAL_CERT_V1',
        'repeat_run_exact': True,
        'allin_terminal_dependency': 'EXACT_FLOP_FORCED_RUNOUT_EQUITY',
        'turn_boundary_dependencies': 'SYNTHETIC_BUCKETS_AND_NN_TEST_ONLY',
        'run': a,
        'status': (
            'STRUCTURAL_INTEGRATION + EXACT FOLD/ALL-IN TERMINALS; '
            'original HUNL 1000-bucket artifact and turn-network weights remain unresolved'
        ),
    }
    out = Path(__file__).with_name('HUNL_FLOP_ENGINE_EXACT_TERMINAL_CERT.json')
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
