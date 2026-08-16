"""Depth-limited HUNL flop CFR lookahead.

This module connects three already-separated contracts:

* the source-constrained DeepStack flop sparse betting tree (Table 4);
* exact flop card/blocker/fold semantics in the frozen 1326-hand space;
* ``FlopTurnValueBoundary``, the HUNL generalization of the released
  DeepStack ``NextRoundValue`` mechanics.

The private HUNL 1000-bucket artifact and original turn-network weights are
NOT embedded here.  They are explicit dependencies supplied through the
boundary object.  Flop all-in runout values are likewise an explicit terminal
oracle dependency, because that exact multi-card terminal-equity layer is a
separate component and must not be approximated silently.

The implemented CFR schedule is the *play-time flop re-solving* schedule from
DeepStack supplementary Table 4: 1000 iterations, first 500 omitted from the
root average.  This must not be confused with the still-unresolved omitted
iteration convention used by the offline HUNL DataGenerator targets.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from .blockers import legal_pairs_mask
from .cards import HAND_COUNT, possible_hands_mask
from .config import DEFAULT_CONFIG, HunlConfig
from .flop_tree import build_flop_tree
from .flop_value_boundary import FlopTurnValueBoundary
from .early_street_tree import EarlyStreetNode

EPS = 1e-9
CAP = 999999.0


class FlopAllInValueProvider(Protocol):
    """Exact terminal CFV provider for a flop all-in forced runout.

    Inputs are *counterfactual reach* vectors at the terminal node.  Returned
    values are chip-denominated CFVs with shape ``[2,1326]``.
    """

    def get_value(
        self,
        board3: tuple[int, int, int],
        pot_half: int,
        player0_reach: np.ndarray,
        player1_reach: np.ndarray,
    ) -> np.ndarray: ...


class MissingFlopAllInValueProvider:
    """Fail-closed placeholder; never substitutes an approximate rollout."""

    def get_value(self, board3, pot_half, player0_reach, player1_reach):
        raise RuntimeError(
            "Exact flop all-in runout terminal equity provider is required; "
            "no approximate/default rollout is used."
        )


@dataclass(frozen=True)
class FlopBoundaryInfo:
    node_id: int
    pot_half: int
    path: tuple[tuple[str, int], ...]


class FlopLookaheadEngine:
    """First-node depth-limited flop solver in the full 1326-hand card space.

    This class intentionally implements ``resolve_first_node`` only.  That is
    the root operation needed for random flop training situations.  Continual
    re-solving with a CFR-D opponent-CFV gadget is a later gate and will reuse
    the already-certified gadget once this first-node boundary integration is
    frozen.
    """

    def __init__(
        self,
        board3,
        pot_half: int,
        next_round: FlopTurnValueBoundary,
        allin_values: FlopAllInValueProvider,
        cfg: HunlConfig = DEFAULT_CONFIG,
        cfr_iters: int | None = None,
        cfr_skip_iters: int | None = None,
    ) -> None:
        self.cfg = cfg
        self.board = tuple(int(c) for c in board3)
        if len(self.board) != 3 or len(set(self.board)) != 3:
            raise ValueError("board3 must contain three distinct cards")
        self.pot_half = int(pot_half)
        self.iters = int(cfr_iters if cfr_iters is not None else cfg.flop_cfr_iters)
        self.skip = int(cfr_skip_iters if cfr_skip_iters is not None else cfg.flop_cfr_omit)
        if not (0 <= self.skip < self.iters):
            raise ValueError("require 0 <= cfr_skip_iters < cfr_iters")
        self.next_round = next_round
        self.allin_values = allin_values
        self.tree = build_flop_tree(self.board, self.pot_half, cfg)
        self.pm3 = possible_hands_mask(self.board)
        self.legal_pairs = legal_pairs_mask(self.board).astype(np.float64)
        self._index()

        # The released NextRoundValue contract is stateful across all CFR
        # iterations.  Start it once with one matched pot per depth boundary.
        self.boundary_pots = np.asarray(
            [b.pot_half for b in self.boundaries], dtype=np.float32
        )
        if self.boundary_pots.size:
            self.next_round.start_computation(self.boundary_pots)

    # --------------------------------------------------------- tree index --
    def _index(self) -> None:
        self.nodes: list[EarlyStreetNode] = []
        self.parent: list[int] = []
        self.paths: list[tuple[tuple[str, int], ...]] = []
        self.decision: list[int] = []
        self.fold_terminals: list[int] = []
        self.allin_terminals: list[int] = []
        self.boundaries: list[FlopBoundaryInfo] = []

        def walk(n: EarlyStreetNode, parent: int, path: tuple[tuple[str, int], ...]):
            nid = len(self.nodes)
            self.nodes.append(n)
            self.parent.append(parent)
            self.paths.append(path)
            n._id = nid  # type: ignore[attr-defined]
            if n.terminal == "fold":
                self.fold_terminals.append(nid)
                return
            if n.terminal == "allin_runout":
                self.allin_terminals.append(nid)
                return
            if n.is_boundary:
                # A closed non-all-in round has equal committed chips.
                if n.spent[0] != n.spent[1]:
                    raise AssertionError("next-street boundary must have matched bets")
                self.boundaries.append(
                    FlopBoundaryInfo(nid, int(min(n.spent)), path)
                )
                return

            self.decision.append(nid)
            k = len(n.children)
            if k == 0:
                raise AssertionError("decision node with no children")
            n._reg = np.zeros((k, HAND_COUNT), dtype=np.float64)  # type: ignore[attr-defined]
            n._avg = np.zeros((k, HAND_COUNT), dtype=np.float64)  # type: ignore[attr-defined]
            n._strat = np.full((k, HAND_COUNT), 1.0 / k, dtype=np.float64)  # type: ignore[attr-defined]
            for action, c in zip(n.actions, n.children):
                walk(c, nid, path + (tuple(action),))

        walk(self.tree, -1, ())
        n = len(self.nodes)
        self.reach = np.zeros((n, 2, HAND_COUNT), dtype=np.float64)
        self.value = np.zeros((n, 2, HAND_COUNT), dtype=np.float64)

    # ------------------------------------------------------------ terminals --
    def _fold_values(self) -> None:
        for nid in self.fold_terminals:
            n = self.nodes[nid]
            assert n.folder in (0, 1)
            r0 = self.reach[nid, 0]
            r1 = self.reach[nid, 1]
            # Matrix orientation matches the certified turn/river engines.
            u0 = r1 @ self.legal_pairs
            u1 = r0 @ self.legal_pairs
            b = float(min(n.spent))
            sgn = -1.0 if n.folder == 0 else 1.0
            self.value[nid, 0] = sgn * b * u0
            self.value[nid, 1] = -sgn * b * u1

    def _allin_runout_values(self) -> None:
        for nid in self.allin_terminals:
            n = self.nodes[nid]
            if n.spent[0] != n.spent[1]:
                raise AssertionError("all-in runout terminal must have matched bets")
            got = np.asarray(
                self.allin_values.get_value(
                    self.board,
                    int(min(n.spent)),
                    self.reach[nid, 0],
                    self.reach[nid, 1],
                ),
                dtype=np.float64,
            )
            if got.shape != (2, HAND_COUNT):
                raise ValueError("all-in provider must return [2,1326]")
            self.value[nid] = got

    def _next_round_values(self) -> None:
        if not self.boundaries:
            return
        rr = np.stack([self.reach[b.node_id] for b in self.boundaries], axis=0)
        # Author next-round machinery is float Tensor based; retain that seam.
        frac = np.asarray(self.next_round.get_value(rr.astype(np.float32)), dtype=np.float64)
        expected = (len(self.boundaries), 2, HAND_COUNT)
        if frac.shape != expected:
            raise ValueError(f"next-round box returned {frac.shape}, expected {expected}")
        chips = frac * self.boundary_pots.astype(np.float64)[:, None, None]
        for i, b in enumerate(self.boundaries):
            self.value[b.node_id] = chips[i]

    # --------------------------------------------------------------- solver --
    def resolve_first_node(self, player0_range: np.ndarray, player1_range: np.ndarray):
        r0 = np.asarray(player0_range, dtype=np.float64)
        r1 = np.asarray(player1_range, dtype=np.float64)
        if r0.shape != (HAND_COUNT,) or r1.shape != (HAND_COUNT,):
            raise ValueError("ranges must have shape [1326]")
        if np.any(r0 < 0) or np.any(r1 < 0):
            raise ValueError("ranges must be nonnegative")
        if np.any(r0[~self.pm3] != 0) or np.any(r1[~self.pm3] != 0):
            raise ValueError("input reach on flop-blocked hands")

        self.root_avg = np.zeros((2, HAND_COUNT), dtype=np.float64)
        for it in range(1, self.iters + 1):
            self.reach.fill(0.0)
            self.value.fill(0.0)
            self.reach[0, 0] = r0
            self.reach[0, 1] = r1

            # top-down counterfactual reach propagation
            for nid, n in enumerate(self.nodes):
                if n.terminal is not None or n.is_boundary:
                    continue
                p = n.player
                st = n._strat  # type: ignore[attr-defined]
                for a, c in enumerate(n.children):
                    cid = c._id  # type: ignore[attr-defined]
                    self.reach[cid] = self.reach[nid]
                    self.reach[cid, p] = self.reach[nid, p] * st[a]

            self._fold_values()
            self._allin_runout_values()
            self._next_round_values()

            # bottom-up CFVs and regret matching+
            for nid in range(len(self.nodes) - 1, -1, -1):
                n = self.nodes[nid]
                if n.terminal is not None or n.is_boundary:
                    continue
                p = n.player
                st = n._strat  # type: ignore[attr-defined]
                k = len(n.children)
                avals = np.empty((k, HAND_COUNT), dtype=np.float64)
                u = np.zeros((2, HAND_COUNT), dtype=np.float64)
                for a, c in enumerate(n.children):
                    cv = self.value[c._id]  # type: ignore[attr-defined]
                    avals[a] = cv[p]
                    u[p] += st[a] * cv[p]
                    # Opponent CFV already contains acting-player reach in child.
                    u[1 - p] += cv[1 - p]
                self.value[nid] = u
                reg = n._reg  # type: ignore[attr-defined]
                reg += avals - u[p][None, :]
                np.clip(reg, 0.0, CAP, out=reg)

            for nid in self.decision:
                n = self.nodes[nid]
                pos = np.clip(n._reg, EPS, CAP)  # type: ignore[attr-defined]
                n._strat = pos / pos.sum(axis=0, keepdims=True)  # type: ignore[attr-defined]
                if it > self.skip:
                    n._avg += n._strat  # type: ignore[attr-defined]
            if it > self.skip:
                self.root_avg += self.value[0]

        denom = self.iters - self.skip
        self.root_cfvs = self.root_avg / float(denom)
        for nid in self.decision:
            n = self.nodes[nid]
            s = n._avg.sum(axis=0, keepdims=True)  # type: ignore[attr-defined]
            with np.errstate(divide="ignore", invalid="ignore"):
                n._navg = np.where(  # type: ignore[attr-defined]
                    s > 0, n._avg / s, 1.0 / len(n.children)
                )
        self.root_strategy = self.tree._navg.copy()  # type: ignore[attr-defined]
        return self.root_cfvs.copy()

    # -------------------------------------------------------- public results --
    def get_root_strategy(self) -> np.ndarray:
        if not hasattr(self, "root_strategy"):
            raise RuntimeError("solve first")
        return self.root_strategy.copy()

    def get_root_cfv_both_players(self) -> np.ndarray:
        if not hasattr(self, "root_cfvs"):
            raise RuntimeError("solve first")
        return self.root_cfvs.copy()

    def get_boundary_values_on_turn(self, board4) -> np.ndarray:
        """Post-skip conditional next-round CFVs for every boundary, in chips.

        Shape ``[boundary_count,2,1326]``.  No chance factor is applied here
        because the turn card is observed, matching released get_value_on_board.
        """
        frac = np.asarray(self.next_round.get_value_on_turn(board4), dtype=np.float64)
        expected = (len(self.boundaries), 2, HAND_COUNT)
        if frac.shape != expected:
            raise ValueError(f"next-round memory returned {frac.shape}, expected {expected}")
        return frac * self.boundary_pots.astype(np.float64)[:, None, None]
