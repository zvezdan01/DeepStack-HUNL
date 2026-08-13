"""Independent sequence-form LP oracle for restricted-support HUNL river
subgames (Gate G1.8 cross-anchor).

Solves the EXACT zero-sum value of the same lookahead-tree game the
resolver plays (author fold convention included), for ranges supported on
small hand sets, via the standard sequence-form LP:

    max_{x >= 0, Ex = e}  min_{y >= 0, Fy = f}  x^T A y
    <=> LP:  max f^T p  s.t.  A^T x >= F^T p,  Ex = e,  x >= 0

Utilities (player 1 = seat 0, chips, engine convention):
    fold terminal, folder p, node bets b: u1 = -min(b) if p == 0 else +min(b)
    showdown terminal, equal bets b:      u1 = sign(i beats j) * b
Chance weights (range draw) r1[i]*r2[j] are folded into A, with
board-blocked and card-sharing pairs contributing zero — exactly the
blocker semantics of the certified terminal layer.

This is an independent implementation: no CFR, no golden-engine code; only
the G1.1-certified evaluator ranks enter through the showdown sign.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.blockers import blocker_matrix  # noqa: E402
from hunl.cards import possible_hands_mask  # noqa: E402
from hunl.evaluator import rank_board_hands, BLOCKED_SENTINEL  # noqa: E402
from hunl.river_resolver import build_lookahead_tree  # noqa: E402


def solve_lp(board, pot_half, support1, support2, r1, r2):
    """Exact game value (chips, player = seat 0) of the lookahead-tree
    river subgame with ranges r1/r2 supported on the given hand lists."""
    tree = build_lookahead_tree(pot_half, board)
    ranks = rank_board_hands(board)
    pm = possible_hands_mask(board)
    B = blocker_matrix()
    s1 = [h for h in support1 if pm[h]]
    s2 = [h for h in support2 if pm[h]]
    assert s1 and s2

    # enumerate sequences: per player, per hand, per (node, action) on path
    # sequence ids: 0 = empty sequence; then one per (hand, decision edge)
    seqs = [{}, {}]           # (hand, id(node), action_idx) -> seq id
    n_seq = [1, 1]
    infosets = [[], []]       # list of (hand, node, parent_seq)

    def index_sequences(node, parent_seq, hand, player):
        if node.terminal:
            return
        p = node.current_player
        if p == player:
            infosets[player].append((hand, node, parent_seq))
            for ai in range(len(node.children)):
                key = (hand, id(node), ai)
                seqs[player][key] = n_seq[player]
                n_seq[player] += 1
                index_sequences(node.children[ai],
                                seqs[player][key], hand, player)
        else:
            for child in node.children:
                index_sequences(child, parent_seq, hand, player)

    for h in s1:
        index_sequences(tree, 0, h, 0)
    for h in s2:
        index_sequences(tree, 0, h, 1)

    # payoff matrix A[seq1, seq2] accumulated over terminals x hand pairs
    A = lil_matrix((n_seq[0], n_seq[1]))

    def walk(node, seq_by_hand1, seq_by_hand2):
        if node.terminal:
            b = float(np.min(node.bets))
            for i, si in seq_by_hand1.items():
                for j, sj in seq_by_hand2.items():
                    if B[i, j]:
                        continue
                    w = r1[i] * r2[j]
                    if w == 0.0:
                        continue
                    if node.terminal_type == "fold":
                        folder = 1 - node.current_player  # player who acted
                        u1 = -b if folder == 0 else b
                    else:
                        ri, rj = int(ranks[i]), int(ranks[j])
                        assert ri != int(BLOCKED_SENTINEL) and \
                            rj != int(BLOCKED_SENTINEL)
                        u1 = b * ((ri > rj) - (ri < rj))
                    A[si[0] if isinstance(si, tuple) else si,
                      sj[0] if isinstance(sj, tuple) else sj] += w * u1
            return
        p = node.current_player
        for ai, child in enumerate(node.children):
            if p == 0:
                nxt1 = {h: seqs[0].get((h, id(node), ai), s)
                        for h, s in seq_by_hand1.items()}
                walk(child, nxt1, seq_by_hand2)
            else:
                nxt2 = {h: seqs[1].get((h, id(node), ai), s)
                        for h, s in seq_by_hand2.items()}
                walk(child, seq_by_hand1, nxt2)

    walk(tree, {h: 0 for h in s1}, {h: 0 for h in s2})
    A = A.toarray()

    # flow constraints E x = e (player 0), F y = f (player 1)
    def flow(player, supp):
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

    E, e = flow(0, s1)
    F, f = flow(1, s2)

    # LP over (x, p): maximize f^T p  s.t. -A^T x + F^T p <= 0; Ex = e; x>=0
    nx, npv = n_seq[0], F.shape[0]
    c = np.concatenate([np.zeros(nx), -f])              # minimize -f^T p
    A_ub = np.hstack([-A.T, F.T])
    b_ub = np.zeros(A.shape[1])
    A_eq = np.hstack([E, np.zeros((E.shape[0], npv))])
    b_eq = e
    bounds = [(0, None)] * nx + [(None, None)] * npv
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")
    assert res.status == 0, res.message
    return -res.fun          # game value for player seat 0
