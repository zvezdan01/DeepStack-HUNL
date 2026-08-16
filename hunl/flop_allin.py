"""Exact flop all-in forced-runout terminal equity.

For a fixed three-card flop and a fixed disjoint pair of private hands there
are 45 unseen cards for the turn and 44 for the river, i.e. 1980 ordered
runouts.  Since showdown depends only on the final five-card board, every
unordered pair of future public cards represents exactly two ordered runouts.
Thus each private-hand pair has C(45,2)=990 equiprobable final-board
completions.

We precompute an integer payoff numerator matrix

    N[h0,h1] = sum_{unordered two-card completions} showdown(h0,h1)

where illegal/blocking completions contribute zero through the certified
showdown matrices.  Exact all-in counterfactual values are then

    CFV0 = pot_half / 990 * N @ reach1
    CFV1 = pot_half / 990 * (-N.T) @ reach0.

The matrix is discrete and exact; only the final reach-weighted matvec is
floating point.  This is poker/chance mathematics, not a claim about the
private DeepStack implementation's storage or optimization strategy.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import combinations
import hashlib
import time

import numpy as np

from .cards import CARD_COUNT, HAND_COUNT, possible_hands_mask
from .showdown import showdown_matrix

FLOP_FUTURE_PUBLIC_CARDS = 49
PAIR_AVAILABLE_PUBLIC_CARDS = 45
UNORDERED_RUNOUTS_PER_PRIVATE_PAIR = 990  # C(45,2)
ORDERED_RUNOUTS_PER_PRIVATE_PAIR = 1980   # 45*44


def _validate_board3(board3) -> tuple[int, int, int]:
    b = tuple(int(c) for c in board3)
    if len(b) != 3 or len(set(b)) != 3 or not all(0 <= c < CARD_COUNT for c in b):
        raise ValueError("board3 must contain three distinct 0-based cards")
    return b  # type: ignore[return-value]


@lru_cache(maxsize=2)
def flop_allin_numerator(board3: tuple[int, int, int]) -> np.ndarray:
    """Return exact int16 [1326,1326] showdown numerator for one flop."""
    b = _validate_board3(board3)
    rem = [c for c in range(CARD_COUNT) if c not in b]
    if len(rem) != FLOP_FUTURE_PUBLIC_CARDS:
        raise AssertionError
    acc = np.zeros((HAND_COUNT, HAND_COUNT), dtype=np.int16)
    for c, d in combinations(rem, 2):
        m, _, _ = showdown_matrix(b + (c, d))
        # Every legal pair has only 990 contributing boards, so int16 is safe.
        acc += m.astype(np.int16, copy=False)
    # A zero-sum showdown matrix must remain exactly antisymmetric in integers.
    if not np.array_equal(acc, -acc.T):
        raise AssertionError("flop all-in numerator lost antisymmetry")
    acc.setflags(write=False)
    return acc


def numerator_sha256(board3) -> str:
    n = flop_allin_numerator(_validate_board3(board3))
    return hashlib.sha256(np.ascontiguousarray(n).tobytes()).hexdigest()


class FlopAllInEquity:
    """Production exact all-in terminal provider for one fixed flop."""

    def __init__(self, board3) -> None:
        self.board = _validate_board3(board3)
        t0 = time.perf_counter()
        self.numerator = flop_allin_numerator(self.board)
        self.build_seconds = time.perf_counter() - t0
        self.pm3 = possible_hands_mask(self.board)

    def get_value(self, board3, pot_half, player0_reach, player1_reach) -> np.ndarray:
        if _validate_board3(board3) != self.board:
            raise ValueError("provider was built for a different flop")
        r0 = np.asarray(player0_reach, dtype=np.float64)
        r1 = np.asarray(player1_reach, dtype=np.float64)
        if r0.shape != (HAND_COUNT,) or r1.shape != (HAND_COUNT,):
            raise ValueError("reach vectors must have shape [1326]")
        if np.any(r0[~self.pm3] != 0) or np.any(r1[~self.pm3] != 0):
            raise ValueError("reach on flop-blocked private hands")
        scale = float(pot_half) / float(UNORDERED_RUNOUTS_PER_PRIVATE_PAIR)
        n = self.numerator
        out = np.empty((2, HAND_COUNT), dtype=np.float64)
        out[0] = scale * (n @ r1)
        out[1] = scale * ((-n.T) @ r0)
        return out
