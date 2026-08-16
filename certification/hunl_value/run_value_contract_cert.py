from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.cards import HAND_COUNT, possible_hands_mask
from hunl.flop_chance import CHANCE_FACTOR, turn_cards
from hunl.flop_value_boundary import FlopTurnValueBoundary
from hunl.value_bucketing import BoardBucketMap, MissingAuthorBucketProvider, POSTFLOP_BUCKET_COUNT
from hunl.value_network import DeepStackHUNLValueNet, HUNLValueNetworkSpec


class SyntheticProvider:
    """Deterministic test-only mapping; NEVER an author/reconstruction bucketizer."""
    bucket_count = POSTFLOP_BUCKET_COUNT

    def __init__(self):
        self.cache = {}

    def for_board(self, board):
        board = tuple(int(c) for c in board)
        if board not in self.cache:
            legal = possible_hands_mask(board)
            mapping = np.full(HAND_COUNT, -1, dtype=np.int16)
            # A deterministic surjection-ish mapping of legal hand positions to 1000 ids.
            # It exists solely to exercise the conversion algebra.
            positions = np.flatnonzero(legal)
            mapping[positions] = (np.arange(positions.size, dtype=np.int64) % self.bucket_count).astype(np.int16)
            self.cache[board] = BoardBucketMap(board, mapping)
        return self.cache[board]


class DeterministicNet:
    def get_value(self, inputs: np.ndarray) -> np.ndarray:
        x = np.asarray(inputs, dtype=np.float32)
        # Deliberately non-zero, player-asymmetric but deterministic.
        p1 = x[:, :1000]
        p2 = x[:, 1000:2000]
        pot = x[:, 2000:2001]
        ids = np.arange(1000, dtype=np.float32)[None, :]
        y1 = np.float32(0.25) * p1 - np.float32(0.10) * p2 + pot + ids * np.float32(1e-5)
        y2 = -np.float32(0.15) * p1 + np.float32(0.35) * p2 - pot - ids * np.float32(7e-6)
        return np.concatenate([y1, y2], axis=1).astype(np.float32)


def sha(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()


def explicit_boundary(board3, ranges, pot_halves, provider, net):
    turns = turn_cards(board3)
    out = np.zeros((ranges.shape[0], 2, HAND_COUNT), dtype=np.float64)
    for c in turns:
        b = tuple(board3) + (c,)
        bm = provider.for_board(b)
        x = np.zeros((ranges.shape[0], 2001), dtype=np.float32)
        masses = np.zeros((ranges.shape[0], 2), dtype=np.float32)
        for p in range(2):
            br = bm.range_to_buckets(ranges[:, p, :])
            m = br.sum(axis=1, dtype=np.float64).astype(np.float32)
            masses[:, p] = m
            safe = m.copy(); safe[safe == 0] = 1
            x[:, p*1000:(p+1)*1000] = br / safe[:, None]
        x[:, -1] = pot_halves / np.float32(20000)
        y = net.get_value(x).reshape(ranges.shape[0], 2, 1000)
        y[:, 0] *= masses[:, 1, None]
        y[:, 1] *= masses[:, 0, None]
        out += bm.bucket_values_to_hands(y).astype(np.float64)
    return (out * CHANCE_FACTOR).astype(np.float32)


def main():
    # Freeze all test randomness before model construction so the certificate
    # itself is reproducible across repeated runs.
    torch.manual_seed(7)
    result = {}
    spec = HUNLValueNetworkSpec()
    assert spec.input_size == 2001 and spec.output_size == 2000
    model = DeepStackHUNLValueNet(spec)
    linears = [m for m in model.feedforward if isinstance(m, torch.nn.Linear)]
    prelus = [m for m in model.feedforward if isinstance(m, torch.nn.PReLU)]
    assert len(linears) == 8 and len(prelus) == 7
    assert [tuple(m.weight.shape) for m in linears] == [
        (500, 2001), (500, 500), (500, 500), (500, 500),
        (500, 500), (500, 500), (500, 500), (2000, 500)
    ]
    assert model.architecture_parameter_count == 3_506_007
    result['architecture'] = {
        'input': 2001, 'output': 2000, 'hidden_layers': 7, 'width': 500,
        'linear_layers': 8, 'prelu_layers': 7,
        'parameter_count_including_7_scalar_prelu': model.architecture_parameter_count,
    }

    # Zero-sum outer network invariant independent of learned weights.
    with torch.no_grad():
        p1 = torch.rand(19, 1000, dtype=torch.float32); p1 /= p1.sum(1, keepdim=True)
        p2 = torch.rand(19, 1000, dtype=torch.float32); p2 /= p2.sum(1, keepdim=True)
        pot = torch.linspace(0.005, 0.9975, 19, dtype=torch.float32)[:, None]
        x = torch.cat([p1, p2, pot], 1)
        raw = model.raw_values(x)
        y = model.zero_sum_correct(raw, x)
        game_sum = (y[:, :1000] * p1).sum(1) + (y[:, 1000:] * p2).sum(1)
        max_abs = float(game_sum.abs().max())
        assert max_abs < 2e-6, max_abs
        shift = y - raw
        # Every output coordinate receives the same -0.5*total_error shift.
        assert float((shift - shift[:, :1]).abs().max()) < 1e-7
    result['zero_sum'] = {'cases': 19, 'max_abs_weighted_game_sum': max_abs}

    # Bucket conversion invariants on a real 4-card board with synthetic mapping.
    provider = SyntheticProvider()
    board4 = (0, 5, 10, 15)
    bm = provider.for_board(board4)
    legal = possible_hands_mask(board4)
    rng = np.random.default_rng(11)
    r = np.zeros((13, HAND_COUNT), dtype=np.float32)
    r[:, legal] = rng.random((13, int(legal.sum())), dtype=np.float32)
    r /= r.sum(axis=1, keepdims=True)
    br = bm.range_to_buckets(r)
    assert np.allclose(br.sum(axis=1), 1.0, atol=2e-6)
    vals = rng.standard_normal((13, 1000)).astype(np.float32)
    hv = bm.bucket_values_to_hands(vals)
    assert np.all(hv[:, ~legal] == 0)
    assert np.array_equal(hv[:, legal], vals[:, bm.hand_to_bucket[legal]])
    result['bucket_contract'] = {
        'board': list(board4), 'legal_hands': int(legal.sum()),
        'range_mass_max_error': float(np.max(np.abs(br.sum(1) - 1))),
        'range_sha256': sha(br), 'inverse_value_sha256': sha(hv)
    }

    # Missing author artifact must fail closed.
    try:
        MissingAuthorBucketProvider().for_board(board4)
    except RuntimeError:
        result['missing_author_bucket_provider'] = 'FAIL_CLOSED_PASS'
    else:
        raise AssertionError('missing bucket provider did not fail closed')

    # Stateful flop->turn boundary compared to an independent explicit loop.
    board3 = (0, 5, 10)
    flop_legal = possible_hands_mask(board3)
    rr = np.zeros((3, 2, HAND_COUNT), dtype=np.float32)
    for b in range(3):
        for p in range(2):
            z = rng.random(int(flop_legal.sum()), dtype=np.float32)
            z /= np.float32(z.sum(dtype=np.float64))
            rr[b, p, flop_legal] = z
    pots = np.asarray([100, 2000, 19950], dtype=np.float32)
    net = DeterministicNet()
    box = FlopTurnValueBoundary(board3, net, provider, cfr_iters=3, cfr_skip_iters=1)
    box.start_computation(pots)
    got1 = box.get_value(rr)
    ref1 = explicit_boundary(board3, rr, pots, provider, net)
    assert np.array_equal(got1, ref1), float(np.max(np.abs(got1-ref1)))
    # Two more iterations, with changed ranges, to exercise post-skip memory.
    rr2 = rr.copy(); rr2[:, :, flop_legal] *= np.float32(0.9); rr2[:, :, flop_legal] /= rr2.sum(axis=2, keepdims=True)
    box.get_value(rr2)
    rr3 = rr.copy(); rr3[:, :, flop_legal] *= np.float32(1.1); rr3[:, :, flop_legal] /= rr3.sum(axis=2, keepdims=True)
    box.get_value(rr3)
    observed_turn = board3 + (11,)
    on_turn = box.get_value_on_turn(observed_turn)
    assert on_turn.shape == (3, 2, HAND_COUNT)
    assert np.all(on_turn[:, :, ~possible_hands_mask(observed_turn)] == 0)
    result['flop_turn_boundary'] = {
        'board3': list(board3), 'turn_count': 49, 'chance_factor': CHANCE_FACTOR,
        'batch': 3, 'single_iter_reference_exact': True,
        'expected_calls': 3, 'skip': 1,
        'expected_value_sha256': sha(got1),
        'observed_turn_card_values_sha256': sha(on_turn),
    }

    out = Path(__file__).with_name('HUNL_VALUE_CONTRACT_CERT.json')
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
