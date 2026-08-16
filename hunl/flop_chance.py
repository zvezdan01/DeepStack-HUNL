"""HUNL flop -> turn chance/blocker algebra.

For a fixed 3-card flop B3:
  * 49 public turn cards remain.
  * 1,176 private hands are legal on B3: C(49,2).
  * 1,128 private hands are legal on B3+c: C(48,2).
  * for a fixed legal DISJOINT pair (h1,h2), exactly 45 turn cards are
    unseen by both players: 52 - 3 - 2 - 2 = 45.

Counterfactual reach therefore propagates by masking (not renormalizing)
and the value aggregation factor is exactly one 1/45 per pair, the direct
flop analogue of hunl.chance's certified turn->river 1/44 construction.

This module is a combinatorial reconstruction, not a claim of byte identity
with the private DeepStack source.  Its discrete identities are exhaustively
certified by certification/hunl_early/run_flop_chance_cert.py.
"""
from __future__ import annotations

import numpy as np

from .cards import CARD_COUNT, HAND_COUNT, possible_hands_mask
from .blockers import card_hand_membership

TURN_DECK = 49
PAIR_UNSEEN = 45
FLOP_LEGAL_HANDS = 1176       # C(49,2)
TURN_LEGAL_HANDS = 1128       # C(48,2)
HAND_LEGAL_TURNS = 47         # 49 - 2 private cards
CHANCE_FACTOR = 1.0 / PAIR_UNSEEN


def turn_cards(board3) -> list[int]:
    board = {int(c) for c in board3}
    if len(board) != 3 or not all(0 <= c < CARD_COUNT for c in board):
        raise ValueError("flop board must contain three distinct 0-based cards")
    return [c for c in range(CARD_COUNT) if c not in board]


def turn_masks(board3) -> tuple[list[int], np.ndarray]:
    """(turn cards, masks[49,1326]) for private-hand legality on B3+c."""
    turns = turn_cards(board3)
    board = tuple(int(c) for c in board3)
    masks = np.zeros((len(turns), HAND_COUNT), dtype=bool)
    for k, c in enumerate(turns):
        masks[k] = possible_hands_mask(board + (c,))
    return turns, masks


def legal_turn_counts_per_hand(board3) -> np.ndarray:
    """47 for every hand legal on the flop, zero for flop-blocked hands."""
    _, masks = turn_masks(board3)
    counts = masks.sum(axis=0).astype(np.int64)
    counts[~possible_hands_mask(board3)] = 0
    return counts


def pair_legal_turn_count(board3, h1: int, h2: int) -> int:
    """Exact discrete count of turn cards unseen by board+h1+h2."""
    ch = card_hand_membership()
    return sum(1 for c in turn_cards(board3)
               if not (ch[c, int(h1)] or ch[c, int(h2)]))
