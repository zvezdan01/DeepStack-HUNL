"""Flop -> turn DeepStack value-network boundary.

This is the HUNL generalization of the released author
``Nn/next_round_value.lua`` mechanics, using the certified flop chance algebra:

  * evaluate all 49 possible turn cards for a fixed flop;
  * mask card ranges by each turn board;
  * bucket and CONDITION each player's range on that board;
  * call the turn value network on [P1 buckets | P2 buckets | pot/stack];
  * multiply each player's output by the OPPONENT'S compatible range mass;
  * inverse-bucket values to the frozen 1326-hand card space;
  * aggregate turn chance exactly once with factor 1/45.

Network outputs remain in fractions-of-pot units.  The caller applies the chip
pot multiplier, mirroring the released DeepStack-Leduc Lookahead code.

The original HUNL 1000-bucket artifact is an explicit dependency.  No fallback
or guessed clustering exists here.
"""
from __future__ import annotations

from typing import Protocol

import numpy as np

from .cards import HAND_COUNT
from .config import DEFAULT_CONFIG, HunlConfig
from .flop_chance import CHANCE_FACTOR, turn_cards
from .value_bucketing import BucketProvider, POSTFLOP_BUCKET_COUNT


class ValueNetwork(Protocol):
    def get_value(self, inputs: np.ndarray) -> np.ndarray: ...


class TorchValueNetworkAdapter:
    """Adapter for ``DeepStackHUNLValueNet`` or compatible torch modules."""

    def __init__(self, model) -> None:
        self.model = model

    def get_value(self, inputs: np.ndarray) -> np.ndarray:
        import torch
        x = torch.from_numpy(np.asarray(inputs, dtype=np.float32))
        with torch.no_grad():
            y = self.model(x).cpu().numpy()
        return np.asarray(y, dtype=np.float32)


class FlopTurnValueBoundary:
    def __init__(
        self,
        board3,
        nn: ValueNetwork,
        bucket_provider: BucketProvider,
        cfg: HunlConfig = DEFAULT_CONFIG,
        cfr_iters: int | None = None,
        cfr_skip_iters: int | None = None,
    ) -> None:
        self.board3 = tuple(int(c) for c in board3)
        if len(set(self.board3)) != 3:
            raise ValueError("board3 must contain three distinct cards")
        self.nn = nn
        self.bucket_provider = bucket_provider
        if int(bucket_provider.bucket_count) != POSTFLOP_BUCKET_COUNT:
            raise ValueError("DeepStack HUNL postflop contract requires 1000 buckets")
        self.cfg = cfg
        self.turns = turn_cards(self.board3)
        self.turn_boards = [self.board3 + (c,) for c in self.turns]
        self.maps = [bucket_provider.for_board(b) for b in self.turn_boards]
        self.iters_required = int(cfr_iters if cfr_iters is not None else cfg.flop_cfr_iters)
        self.skip = int(cfr_skip_iters if cfr_skip_iters is not None else cfg.flop_cfr_omit)
        self.iter = 0
        self._prepared = False

    def start_computation(self, pot_halves: np.ndarray) -> None:
        p = np.asarray(pot_halves, dtype=np.float32).reshape(-1)
        if p.size == 0:
            raise ValueError("pot_halves must be non-empty")
        self.pot_halves = p.copy()
        self.batch_size = int(p.size)
        self.iter = 0
        self._prepared = False
        self._opp_mass_memory = None
        self._cfv_memory = None

    def _build_inputs(self, ranges: np.ndarray):
        ranges = np.asarray(ranges, dtype=np.float32)
        expected = (self.batch_size, 2, HAND_COUNT)
        if ranges.shape != expected:
            raise ValueError(f"ranges must have shape {expected}, got {ranges.shape}")

        inputs = np.zeros((self.batch_size, len(self.turns), 2001), dtype=np.float32)
        own_mass = np.zeros((self.batch_size, 2, len(self.turns)), dtype=np.float32)

        for t, bmap in enumerate(self.maps):
            for p in range(2):
                bucket_reach = bmap.range_to_buckets(ranges[:, p, :])
                mass = bucket_reach.sum(axis=1, dtype=np.float64).astype(np.float32)
                own_mass[:, p, t] = mass
                safe = mass.copy()
                safe[safe == 0] = np.float32(1.0)
                bucket_prob = bucket_reach / safe[:, None]
                lo = p * POSTFLOP_BUCKET_COUNT
                hi = lo + POSTFLOP_BUCKET_COUNT
                inputs[:, t, lo:hi] = bucket_prob

        # Project frozen reading, inherited from author Leduc code and the
        # HUNL pot distribution: per-player committed pot / 20,000 stack.
        inputs[:, :, -1] = (self.pot_halves / np.float32(self.cfg.stack))[:, None]
        return inputs, own_mass

    def get_value(self, ranges: np.ndarray) -> np.ndarray:
        if not hasattr(self, "batch_size"):
            raise RuntimeError("start_computation() must be called first")
        self.iter += 1
        inputs, own_mass = self._build_inputs(ranges)
        flat = inputs.reshape(self.batch_size * len(self.turns), -1)
        out = np.asarray(self.nn.get_value(flat), dtype=np.float32)
        if out.shape != (flat.shape[0], 2000):
            raise ValueError(f"network returned {out.shape}, expected {(flat.shape[0], 2000)}")
        bucket_cfvs = out.reshape(self.batch_size, len(self.turns), 2, POSTFLOP_BUCKET_COUNT)

        # Restore opponent counterfactual reach after conditioning the network
        # input ranges.  Player 0 values use player 1 compatible mass and vice versa.
        opp_mass = own_mass[:, ::-1, :].copy()  # [B,player,turn]
        weighted = bucket_cfvs.transpose(0, 2, 1, 3) * opp_mass[..., None]

        if self.iter > self.skip:
            if self._opp_mass_memory is None:
                self._opp_mass_memory = np.zeros_like(opp_mass, dtype=np.float64)
                self._cfv_memory = np.zeros_like(weighted, dtype=np.float64)
            self._opp_mass_memory += opp_mass.astype(np.float64)
            self._cfv_memory += weighted.astype(np.float64)

        card_values = np.zeros((self.batch_size, 2, HAND_COUNT), dtype=np.float64)
        for t, bmap in enumerate(self.maps):
            hand_vals = bmap.bucket_values_to_hands(weighted[:, :, t, :])
            card_values += hand_vals.astype(np.float64)
        card_values *= CHANCE_FACTOR  # exactly once: 1/45 per private-hand pair
        return card_values.astype(np.float32)

    def _prepare_memory(self) -> None:
        if self.iter != self.iters_required:
            raise RuntimeError(f"expected {self.iters_required} calls, got {self.iter}")
        if self._prepared:
            return
        if self._opp_mass_memory is None or self._cfv_memory is None:
            raise RuntimeError("no post-skip values accumulated")
        safe = self._opp_mass_memory.copy()
        safe[safe == 0] = 1.0
        self._cfv_memory /= safe[..., None]
        self._prepared = True

    def get_value_on_turn(self, board4) -> np.ndarray:
        """Average post-omit conditional CFVs for the observed turn board.

        Returns fractions-of-pot in card space; no 1/45 factor is applied
        because the turn card is now observed rather than averaged over.
        """
        self._prepare_memory()
        board = tuple(int(c) for c in board4)
        try:
            t = self.turn_boards.index(board)
        except ValueError as exc:
            raise ValueError("board4 is not a one-card extension of this flop") from exc
        assert self._cfv_memory is not None
        return self.maps[t].bucket_values_to_hands(
            self._cfv_memory[:, :, t, :].astype(np.float32)
        )
