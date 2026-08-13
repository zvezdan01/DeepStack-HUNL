"""Independent oracles for the exact turn engine gate.

- solve_turn_lp: sequence-form LP over the FULL turn game tree (turn
  betting + river chance with exact 1/44 weights + river betting),
  restricted supports. Independent implementation: no CFR, no engine
  code; showdown by direct evaluator ranks.
- ReferenceTurnSolver: recursive per-node f64 CFR + exact BR sharing no
  vectorized engine code (independent structure, same certified math).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.blockers import blocker_matrix, legal_pairs_mask  # noqa: E402
from hunl.cards import HAND_CARDS, HAND_COUNT  # noqa: E402
from hunl.evaluator import BLOCKED_SENTINEL, rank_board_hands  # noqa: E402
from hunl.showdown import showdown_matrix  # noqa: E402
from hunl.turn_tree import TurnGameTreeBuilder, TurnNode  # noqa: E402
from hunl.chance import CHANCE_FACTOR  # noqa: E402


def solve_turn_lp(board4, pot_half, support1, support2, r1, r2, cfg):
    tree = TurnGameTreeBuilder(cfg).build(board4, pot_half)
    B = blocker_matrix()
    ranks_cache: dict[tuple, np.ndarray] = {}

    seqs = [{}, {}]
    n_seq = [1, 1]
    infosets = [[], []]

    def index(node, parent_seq, hand, player):
        if node.terminal is not None:
            return
        if node.street == "chance":
            a, b = int(HAND_CARDS[hand][0]), int(HAND_CARDS[hand][1])
            for c in node.children:
                if c.river_card in (a, b):
                    continue
                index(c, parent_seq, hand, player)
            return
        if node.player == player:
            infosets[player].append((hand, node, parent_seq))
            for ai in range(len(node.children)):
                key = (hand, id(node), ai)
                seqs[player][key] = n_seq[player]
                n_seq[player] += 1
                index(node.children[ai], seqs[player][key], hand, player)
        else:
            for c in node.children:
                index(c, parent_seq, hand, player)

    for h in support1:
        index(tree, 0, h, 0)
    for h in support2:
        index(tree, 0, h, 1)

    A = lil_matrix((n_seq[0], n_seq[1]))

    def payoff(node, i, j):
        b = float(min(node.spent))
        if node.terminal == "fold":
            folder = 1 - node.player
            return -b if folder == 0 else b
        rk = ranks_cache.setdefault(node.board, rank_board_hands(node.board))
        qi, qj = int(rk[i]), int(rk[j])
        assert qi != int(BLOCKED_SENTINEL) and qj != int(BLOCKED_SENTINEL)
        return b * ((qi > qj) - (qi < qj))

    def walk(node, s1_by_hand, s2_by_hand, w):
        if node.terminal is not None:
            for i, si in s1_by_hand.items():
                for j, sj in s2_by_hand.items():
                    if B[i, j]:
                        continue
                    ww = w * r1[i] * r2[j]
                    if ww != 0.0:
                        A[si, sj] += ww * payoff(node, i, j)
            return
        if node.street == "chance":
            for c in node.children:
                rc = c.river_card
                n1 = {h: s for h, s in s1_by_hand.items()
                      if rc not in (int(HAND_CARDS[h][0]),
                                    int(HAND_CARDS[h][1]))}
                n2 = {h: s for h, s in s2_by_hand.items()
                      if rc not in (int(HAND_CARDS[h][0]),
                                    int(HAND_CARDS[h][1]))}
                if n1 or n2:
                    walk(c, n1, n2, w * CHANCE_FACTOR)
            return
        p = node.player
        for ai, c in enumerate(node.children):
            if p == 0:
                nxt = {h: seqs[0].get((h, id(node), ai), s)
                       for h, s in s1_by_hand.items()}
                walk(c, nxt, s2_by_hand, w)
            else:
                nxt = {h: seqs[1].get((h, id(node), ai), s)
                       for h, s in s2_by_hand.items()}
                walk(c, s1_by_hand, nxt, w)

    walk(tree, {h: 0 for h in support1}, {h: 0 for h in support2}, 1.0)
    A = A.toarray()

    def flow(player):
        rows = 1 + len(infosets[player])
        E = np.zeros((rows, n_seq[player]))
        e = np.zeros(rows)
        E[0, 0] = 1.0
        e[0] = 1.0
        for k, (hand, node, parent_seq) in enumerate(infosets[player]):
            E[1 + k, parent_seq] = -1.0
            for ai in range(len(node.children)):
                E[1 + k, seqs[player][(hand, id(node), ai)]] = 1.0
        return E, e

    E, e = flow(0)
    F, f = flow(1)
    nx, npv = n_seq[0], F.shape[0]
    c = np.concatenate([np.zeros(nx), -f])
    res = linprog(c, A_ub=np.hstack([-A.T, F.T]), b_ub=np.zeros(A.shape[1]),
                  A_eq=np.hstack([E, np.zeros((E.shape[0], npv))]), b_eq=e,
                  bounds=[(0, None)] * nx + [(None, None)] * npv,
                  method="highs")
    assert res.status == 0, res.message
    return -res.fun


class ReferenceTurnSolver:
    """Recursive per-node f64 CFR — independent structure from the
    vectorized engine (per-node dict state, recursive passes)."""

    def __init__(self, board4, pot_half, cfg, iters, skip):
        self.tree = TurnGameTreeBuilder(cfg).build(board4, pot_half)
        self.iters, self.skip = iters, skip
        self.mats = {}

        def init(n):
            if n.terminal is not None:
                if n.board not in self.mats:
                    if len(n.board) == 5:
                        m, legal, _ = showdown_matrix(n.board)
                        self.mats[n.board] = (m.astype(np.float64),
                                              legal.astype(np.float64))
                    else:
                        self.mats[n.board] = (
                            None, legal_pairs_mask(n.board).astype(np.float64))
                return
            if n.street != "chance":
                k = len(n.children)
                n._reg = np.zeros((k, HAND_COUNT))
                n._avg = np.zeros((k, HAND_COUNT))
            for c in n.children:
                init(c)
        import sys
        sys.setrecursionlimit(200000)
        init(self.tree)

    def _terminal(self, n, reach):
        m, fmask = self.mats[n.board]
        b = float(min(n.spent))
        u = np.zeros((2, HAND_COUNT))
        if n.terminal == "fold":
            sgn = -1.0 if n.folder == 0 else 1.0
            u[0] = sgn * b * (fmask @ reach[1])
            u[1] = -sgn * b * (fmask.T @ reach[0])
        else:
            u[0] = b * (m @ reach[1])
            u[1] = b * ((-m.T) @ reach[0])
        return u

    def _cfr(self, n, reach, it):
        if n.terminal is not None:
            return self._terminal(n, reach)
        if n.street == "chance":
            acc = np.zeros((2, HAND_COUNT))
            for k, c in enumerate(n.children):
                mk = n.chance_masks[k]
                acc += mk * self._cfr(c, [reach[0] * mk, reach[1] * mk], it)
            return CHANCE_FACTOR * acc
        k = len(n.children)
        pos = np.clip(n._reg, 1e-9, 999999.0)
        strat = pos / pos.sum(axis=0, keepdims=True)
        if it > self.skip:
            n._avg += strat
        p = n.current_player if hasattr(n, "current_player") else n.player
        u = np.zeros((2, HAND_COUNT))
        avals = np.zeros((k, HAND_COUNT))
        for a, c in enumerate(n.children):
            cr = [reach[0].copy(), reach[1].copy()]
            cr[p] = cr[p] * strat[a]
            cu = self._cfr(c, cr, it)
            avals[a] = cu[p]
            u[p] += strat[a] * cu[p]
            u[1 - p] += cu[1 - p]
        n._reg += avals - u[p][None, :]
        np.clip(n._reg, 0.0, 999999.0, out=n._reg)
        return u

    def solve(self, r1, r2):
        root_avg = np.zeros((2, HAND_COUNT))
        for it in range(1, self.iters + 1):
            u = self._cfr(self.tree,
                          [np.asarray(r1, float), np.asarray(r2, float)], it)
            if it > self.skip:
                root_avg += u
        return root_avg / (self.iters - self.skip)
