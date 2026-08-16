"""Source-constrained HUNL card-abstraction features.

This module intentionally separates what the cited abstraction literature fixes
from what the private DeepStack bucket-generation implementation did not
publish.

DeepStack supplementary material says its flop/turn buckets were produced by
k-means with earth mover's distance over "hand-strength-like features", citing
Johanson et al. (AAMAS 2013) and Ganzfried & Sandholm (AAAI 2014).
Those primary sources describe the leading distribution-aware Hold'em
abstraction as:

  * roll out the remaining public cards,
  * compute final-round equity/hand-strength against a uniformly random legal
    opponent hand,
  * represent the resulting distribution as a one-dimensional histogram,
  * compare histograms with earth mover's distance (EMD),
  * cluster with k-means.

Ganzfried & Sandholm note that prior/strong poker agents use 50 equal-width
intervals of width 0.02.  DeepStack itself does NOT publish its exact histogram
bin count, centroid initialization, restart count, or serialized centroids.
Therefore ``bins=50`` is a CITED-METHOD reconstruction default, not an
ORIGINAL-DEEPSTACK claim.

For a TURN state, only the river remains.  The feature below is therefore the
final-round equity distribution induced by the 46 legal river cards for a
fixed legal private hand.  Equity is win + 1/2 tie, following the explicit
Ganzfried/Sandholm definition.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from hunl.blockers import blocker_matrix
from hunl.cards import CARD_COUNT, HAND_CARDS, HAND_COUNT, possible_hands_mask
from hunl.evaluator import rank_board_hands


DEFAULT_EQUITY_BINS = 50


@dataclass(frozen=True)
class TurnEquityHistogram:
    board: tuple[int, int, int, int]
    hand_id: int
    bins: int
    river_cards: np.ndarray          # [46] int16
    equity_numerators: np.ndarray    # [46] int32, denominator = 2*990
    equity_denominator: int
    counts: np.ndarray               # [bins] int16, sums to 46
    probabilities: np.ndarray        # [bins] float64, sums to 1

    @property
    def equities(self) -> np.ndarray:
        return self.equity_numerators.astype(np.float64) / float(self.equity_denominator)


def _validate_turn_hand(board: Iterable[int], hand_id: int) -> tuple[tuple[int, int, int, int], int]:
    b = tuple(int(c) for c in board)
    if len(b) != 4 or len(set(b)) != 4 or any(c < 0 or c >= CARD_COUNT for c in b):
        raise ValueError("turn board must contain four distinct ACPC card ids")
    h = int(hand_id)
    if h < 0 or h >= HAND_COUNT:
        raise ValueError("hand_id out of range")
    hc = HAND_CARDS[h]
    if int(hc[0]) in b or int(hc[1]) in b:
        raise ValueError("private hand collides with turn board")
    return b, h


def _equity_bin_indices(numerators: np.ndarray, denominator: int, bins: int) -> np.ndarray:
    """Map exact rational equities into equal-width bins on [0,1].

    We avoid floating-point boundary ambiguity.  For e < 1, floor(e*bins).
    Exact equity 1 is placed in the final bin.
    """
    nums = np.asarray(numerators, dtype=np.int64)
    idx = (nums * int(bins)) // int(denominator)
    return np.minimum(idx, int(bins) - 1).astype(np.int32)


def turn_final_equity_histogram(
    board: Iterable[int],
    hand_id: int,
    *,
    bins: int = DEFAULT_EQUITY_BINS,
) -> TurnEquityHistogram:
    """Exact final-round equity histogram for one turn hand.

    For each of the 46 river cards not in the turn board or hero's private
    hand, evaluate hero versus every uniformly possible opponent private hand
    on the resulting five-card board.  There are C(45,2)=990 such opponent
    hands for every fixed river.  Store equity exactly as the integer numerator
    ``2*wins + ties`` over denominator ``2*990``.
    """
    b, h = _validate_turn_hand(board, hand_id)
    if bins <= 0:
        raise ValueError("bins must be positive")

    hero_cards = {int(HAND_CARDS[h, 0]), int(HAND_CARDS[h, 1])}
    used = set(b) | hero_cards
    rivers = np.asarray([c for c in range(CARD_COUNT) if c not in used], dtype=np.int16)
    if rivers.shape != (46,):
        raise AssertionError("turn+hero must leave exactly 46 river cards")

    hand_compat = blocker_matrix()[h] == 0
    numerators = np.empty(46, dtype=np.int32)
    expected_opp = 45 * 44 // 2  # C(45,2) = 990

    for i, river in enumerate(rivers.tolist()):
        board5 = b + (int(river),)
        ranks = rank_board_hands(board5)
        possible = possible_hands_mask(board5)
        opp = possible & hand_compat
        opp[h] = False
        nopp = int(opp.sum())
        if nopp != expected_opp:
            raise AssertionError(f"river {river}: expected {expected_opp} opponent hands, got {nopp}")
        hero_rank = ranks[h]
        opp_ranks = ranks[opp]
        wins = int(np.count_nonzero(hero_rank > opp_ranks))
        ties = int(np.count_nonzero(hero_rank == opp_ranks))
        numerators[i] = 2 * wins + ties

    denominator = 2 * expected_opp
    idx = _equity_bin_indices(numerators, denominator, int(bins))
    counts = np.bincount(idx, minlength=int(bins)).astype(np.int16)
    if int(counts.sum()) != 46:
        raise AssertionError("histogram does not contain all 46 river outcomes")
    probs = counts.astype(np.float64) / 46.0
    return TurnEquityHistogram(
        board=b,
        hand_id=h,
        bins=int(bins),
        river_cards=rivers,
        equity_numerators=numerators,
        equity_denominator=denominator,
        counts=counts,
        probabilities=probs,
    )


def emd_1d(a: np.ndarray, b: np.ndarray, *, bin_width: float = 1.0) -> float:
    """Exact 1-D EMD formula for equal-spaced, equal-mass histograms.

    For adjacent-bin ground cost ``bin_width``, EMD is the sum of the absolute
    cumulative mass imbalance across every boundary.  With ``bin_width=1`` the
    result is measured in histogram-bin units, matching the units used in the
    cited poker abstraction examples.  A constant bin-width rescaling does not
    change k-means assignments.
    """
    x = np.asarray(a, dtype=np.float64)
    y = np.asarray(b, dtype=np.float64)
    if x.ndim != 1 or y.ndim != 1 or x.shape != y.shape or x.size == 0:
        raise ValueError("histograms must be nonempty one-dimensional arrays of equal shape")
    if np.any(x < 0) or np.any(y < 0):
        raise ValueError("histograms must be nonnegative")
    sx = float(x.sum())
    sy = float(y.sum())
    if not np.isclose(sx, sy, rtol=0.0, atol=1e-12):
        raise ValueError("EMD requires equal total mass")
    # Last cumulative sum is zero (up to rounding), so only boundaries between
    # bins contribute transport cost.
    imbalance = np.cumsum(x - y)[:-1]
    return float(np.abs(imbalance).sum() * float(bin_width))


def emd_1d_integer_counts(a: np.ndarray, b: np.ndarray) -> int:
    """Integer EMD in bin units for histograms with equal integer mass."""
    x = np.asarray(a, dtype=np.int64)
    y = np.asarray(b, dtype=np.int64)
    if x.ndim != 1 or y.ndim != 1 or x.shape != y.shape or x.size == 0:
        raise ValueError("histograms must be nonempty one-dimensional arrays of equal shape")
    if np.any(x < 0) or np.any(y < 0) or int(x.sum()) != int(y.sum()):
        raise ValueError("integer histograms must be nonnegative with equal mass")
    return int(np.abs(np.cumsum(x - y)[:-1]).sum())


__all__ = [
    "DEFAULT_EQUITY_BINS",
    "TurnEquityHistogram",
    "turn_final_equity_histogram",
    "emd_1d",
    "emd_1d_integer_counts",
]


def turn_board_final_equity_histograms(
    board: Iterable[int],
    *,
    bins: int = DEFAULT_EQUITY_BINS,
) -> np.ndarray:
    """Bulk exact turn features for every 1326 private hand.

    Returns integer histogram counts of shape ``(1326,bins)``.  Every hand
    legal on the four-card turn board sums to exactly 46 (one observation for
    every river card not colliding with that hand); board-blocked hands are
    all-zero.

    This is mathematically identical to calling ``turn_final_equity_histogram``
    for each legal hand, but exploits the fact that one river board provides
    final equity for *all* 1081 private hands legal on that river.  For a fixed
    final board, uniform-opponent equity follows from the showdown margin:

        equity = 1/2 + (wins - losses)/(2 * 990)

    because wins + losses + ties = 990 for every legal hero hand.
    """
    from .river_terminal_fast import (
        RiverTerminalFastKernel, _native_arrays, _numba_showdown_batch,
        NUMBA_AVAILABLE,
    )
    b = tuple(int(c) for c in board)
    if len(b) != 4 or len(set(b)) != 4:
        raise ValueError("turn board must have four distinct cards")
    if bins <= 0:
        raise ValueError("bins must be positive")
    if not NUMBA_AVAILABLE:
        raise RuntimeError("bulk turn histogram extraction currently requires numba")

    turn_legal = possible_hands_mask(b)
    counts = np.zeros((HAND_COUNT, int(bins)), dtype=np.int16)
    # Without fixing hero, 48 cards remain after a four-card public board.
    rivers = [c for c in range(CARD_COUNT) if c not in b]
    if len(rivers) != 48:
        raise AssertionError("turn board must leave 48 candidate river cards")
    uniform = np.ones((1, HAND_COUNT), dtype=np.float64)
    denom = 2 * 990
    for river in rivers:
        board5 = b + (river,)
        kernel = RiverTerminalFastKernel.build(board5)
        ranks, gids, offsets, ids = _native_arrays(kernel)
        margin = _numba_showdown_batch(
            uniform, ranks, gids, offsets, ids,
            kernel.legal_mask.astype(np.bool_),
        )[0]
        # 2*wins+ties = 990 + (wins-losses).
        nums = (990.0 + margin[kernel.legal_ids]).astype(np.int32)
        # margin is an exact integer here despite float64 representation.
        if not np.allclose(margin[kernel.legal_ids], np.rint(margin[kernel.legal_ids]),
                           rtol=0.0, atol=0.0):
            raise AssertionError("uniform showdown margins should be exact integers")
        idx = _equity_bin_indices(nums, denom, int(bins))
        counts[kernel.legal_ids, idx] += 1

    sums = counts.sum(axis=1)
    if not np.all(sums[turn_legal] == 46):
        raise AssertionError("every turn-legal hand must have 46 river observations")
    if not np.all(sums[~turn_legal] == 0):
        raise AssertionError("turn-blocked hands must have zero histogram mass")
    return counts


__all__ += ["turn_board_final_equity_histograms"]
