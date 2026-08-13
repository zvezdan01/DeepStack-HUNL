"""HUNL turn -> river transition layer (production implementation).

Everything follows the chance-weight algebra documented in hunl/chance.py.
Consumes only certified layers: cards/blockers (G1.1/G1.2), showdown
(G1.3), river resolver (G1.7/G1.8 — frozen, untouched).

Two entry points:
  - all_in_equity: turn all-in runout values (no betting, no CFR) —
    exact expectation over the 44-per-pair river chance, vectorized with
    the G1.3 showdown matrices.
  - TurnTransition.turn_cfvs: full transition — for every river card run
    the FROZEN certified exact river resolver on masked counterfactual
    reach vectors and aggregate CFVs with the single 1/44 factor.

dtype contract: aggregation in float64; per-river resolver inputs/outputs
keep the frozen engine's float32 contract; discrete structures exact.
"""
from __future__ import annotations

import numpy as np

from .cards import HAND_COUNT, possible_hands_mask
from .chance import CHANCE_FACTOR, river_masks
from .showdown import showdown_matrix
from .river_resolver import RiverResolver


def all_in_equity(board4, pot_half: float, r1: np.ndarray,
                  r2: np.ndarray) -> np.ndarray:
    """Exact turn all-in runout values, chips, both players.

    u_p(h) = pot_half * (1/44) * sum_c mask_c(h) * (M_c @ reach_opp^c)(h)
    with M_c the G1.3 showdown matrix (+1 row beats col; illegal pairs 0)
    and reach_opp^c = reach_opp * mask_c. Returns (2, 1326) float64.
    """
    r1 = np.asarray(r1, dtype=np.float64)
    r2 = np.asarray(r2, dtype=np.float64)
    pm4 = possible_hands_mask(board4)
    assert (r1[~pm4] == 0).all() and (r2[~pm4] == 0).all(), \
        "input reach on turn-blocked hands"
    rivers, masks = river_masks(board4)
    out = np.zeros((2, HAND_COUNT), dtype=np.float64)
    board = tuple(int(c) for c in board4)
    for k, c in enumerate(rivers):
        m, _, _ = showdown_matrix(board + (c,))
        md = m.astype(np.float64)
        mc = masks[k]
        out[0] += mc * (md @ (r2 * mc))
        out[1] += mc * ((-md.T) @ (r1 * mc))
    out *= float(pot_half) * CHANCE_FACTOR
    return out


class TurnTransition:
    """Full turn -> river transition through the frozen river resolver."""

    def __init__(self, board4, pot_half: int,
                 cfr_iters: int | None = None,
                 cfr_skip_iters: int | None = None) -> None:
        self.board = tuple(int(c) for c in board4)
        self.pot_half = int(pot_half)
        self.rivers, self.masks = river_masks(self.board)
        self.cfr_iters = cfr_iters
        self.cfr_skip_iters = cfr_skip_iters

    def turn_cfvs(self, r1: np.ndarray, r2: np.ndarray
                  ) -> tuple[np.ndarray, list[str]]:
        """Aggregate turn CFVs for both players (2, 1326) float64 chips,
        plus a per-river log. Reach vectors are masked, never renormalized
        (counterfactual-reach convention); 1/44 applied once at the end."""
        r1 = np.asarray(r1, dtype=np.float64)
        r2 = np.asarray(r2, dtype=np.float64)
        pm4 = possible_hands_mask(self.board)
        assert (r1[~pm4] == 0).all() and (r2[~pm4] == 0).all()
        agg = np.zeros((2, HAND_COUNT), dtype=np.float64)
        log: list[str] = []
        for k, c in enumerate(self.rivers):
            mc = self.masks[k]
            c1 = (r1 * mc)
            c2 = (r2 * mc)
            if c1.sum() == 0.0 and c2.sum() == 0.0:
                log.append(f"river {c}: zero support both sides -> skip")
                continue
            rs = RiverResolver(cfr_iters=self.cfr_iters,
                               cfr_skip_iters=self.cfr_skip_iters)
            rs.resolve_first_node(self.board + (int(c),), self.pot_half,
                                  c1.astype(np.float32),
                                  c2.astype(np.float32))
            both = rs.get_root_cfv_both_players().astype(np.float64)
            agg[0] += mc * both[0]
            agg[1] += mc * both[1]
            log.append(f"river {c}: mass ({c1.sum():.6f},{c2.sum():.6f})")
        agg *= CHANCE_FACTOR
        return agg, log
