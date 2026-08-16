#!/usr/bin/env python3
"""Exhaustive/discrete certification of hunl.flop_chance."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

from hunl.blockers import blocker_matrix, card_hand_membership
from hunl.cards import CARD_COUNT, HAND_COUNT, possible_hands_mask
from hunl.flop_chance import (
    FLOP_LEGAL_HANDS, HAND_LEGAL_TURNS, PAIR_UNSEEN, TURN_DECK,
    TURN_LEGAL_HANDS, legal_turn_counts_per_hand, pair_legal_turn_count,
    turn_masks,
)

HERE = Path(__file__).resolve().parent


def main():
    # Representative full pair-matrix identities.  These test all legal
    # ordered private-hand pairs on each selected flop simultaneously.
    reps = [(0, 1, 2), (0, 17, 51), (7, 23, 39), (4, 8, 12),
            (3, 19, 35), (10, 11, 50)]
    blk = blocker_matrix().astype(bool)
    pair_checks = 0
    for board in reps:
        turns, masks = turn_masks(board)
        assert len(turns) == TURN_DECK == 49
        pm3 = possible_hands_mask(board)
        assert int(pm3.sum()) == FLOP_LEGAL_HANDS == 1176
        assert (masks.sum(axis=1) == TURN_LEGAL_HANDS).all()
        counts = legal_turn_counts_per_hand(board)
        assert (counts[pm3] == HAND_LEGAL_TURNS).all()
        assert (counts[~pm3] == 0).all()
        # Cross-foot identity: 1176*47 == 49*1128.
        assert int(counts.sum()) == FLOP_LEGAL_HANDS * HAND_LEGAL_TURNS
        assert int(counts.sum()) == TURN_DECK * TURN_LEGAL_HANDS
        pair_counts = masks.astype(np.int16).T @ masks.astype(np.int16)
        legal_pair = pm3[:, None] & pm3[None, :] & ~blk
        assert (pair_counts[legal_pair] == PAIR_UNSEEN).all()
        pair_checks += int(legal_pair.sum())

    # Exhaust every possible flop board for the load-bearing hand-count and
    # cross-foot identities.  C(52,3)=22,100 is small enough to do fully.
    ch = card_hand_membership()
    nboards = 0
    for chunk_start in range(0, math.comb(52, 3), 2048):
        # Generate only this chunk to keep memory bounded.
        chunk_len = min(2048, math.comb(52, 3) - chunk_start)
        boards = np.asarray(list(itertools.islice(
            itertools.combinations(range(CARD_COUNT), 3),
            chunk_start, chunk_start + chunk_len)), dtype=np.int8)
        if len(boards) == 0:
            break
        blocked = ch[boards[:, 0]] | ch[boards[:, 1]] | ch[boards[:, 2]]
        live = HAND_COUNT - blocked.sum(axis=1)
        assert (live == FLOP_LEGAL_HANDS).all()
        nboards += len(boards)
    assert nboards == math.comb(52, 3) == 22100

    # Independent scalar recounts on deterministic hand pairs, separated
    # from the vectorized mask-matrix calculation above.
    scalar = 0
    for board in reps:
        live = np.nonzero(possible_hands_mask(board))[0]
        for i in range(0, min(100, len(live)-1), 2):
            h1 = int(live[i])
            # choose first disjoint later hand
            h2 = next(int(h) for h in live[i+1:] if not blk[h1, h])
            assert pair_legal_turn_count(board, h1, h2) == PAIR_UNSEEN
            scalar += 1

    manifest = {
        "schema": "HUNL_FLOP_CHANCE_CERT_V1",
        "flop_boards_exhausted": nboards,
        "representative_flops_full_pair_matrix": len(reps),
        "legal_ordered_pairs_checked": pair_checks,
        "scalar_pair_recounts": scalar,
        "constants": {
            "turn_public_candidates": TURN_DECK,
            "flop_legal_hands": FLOP_LEGAL_HANDS,
            "turn_legal_hands": TURN_LEGAL_HANDS,
            "legal_turns_per_hand": HAND_LEGAL_TURNS,
            "legal_turns_per_disjoint_pair": PAIR_UNSEEN,
            "chance_factor": "1/45",
        },
        "identities": ["1176*47=49*1128=55272", "pair mass=45/45"],
        "divergences": 0,
        "status": "COMBINATORIAL_EXACT (not private-source bit-exact)",
    }
    raw = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    manifest["fingerprint_sha256"] = hashlib.sha256(raw).hexdigest()
    (HERE / "FLOP_CHANCE_CERT.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
