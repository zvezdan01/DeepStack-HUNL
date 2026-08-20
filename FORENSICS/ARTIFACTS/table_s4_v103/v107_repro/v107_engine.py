"""V107+ value-experiment engine (this session's independent implementation).

Tree family: verbatim import of the V99-V102 handoff reproducer (frozen
semantics — NOT modified, per tasking).  Solver: CFR+ with RM+ regrets,
simultaneous updates, uniform averaging of root per-action CFVs after the
skip window — the same conventions as the certified turn datagen pipeline.
River showdown/fold terminals use O(n) rank-prefix + inclusion-exclusion
blocker accounting, verified against the certified dense showdown matrix.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

QT = Path("/home/user/quant-trade")
sys.path.insert(0, str(QT))
sys.path.insert(0, str(QT / "FORENSICS/ARTIFACTS/table_s4_v103/v99_v102_handoff"))

from reproduce_table_s4_tree_counts import SPARSE, FULL, build  # noqa: E402
from hunl.cards import (CARD_COUNT, HAND_CARDS, HAND_COUNT,  # noqa: E402
                        possible_hands_mask, string_to_cards)
from hunl.evaluator import BLOCKED_SENTINEL, rank_board_hands  # noqa: E402

MENU_ORDER = ["2P", "1/2P", "P", "1/2P+P", "P+2P", "1/2P+P+2P"]
PAPER = {  # L1, L2, Linf from first-party tab:cfvs (= Table S4)
    "2P": (64.79, 2.672, 0.3445),
    "1/2P": (58.24, 3.426, 0.7376),
    "P": (25.51, 1.272, 0.3372),
    "1/2P+P": (41.42, 1.541, 0.2955),
    "P+2P": (27.69, 1.390, 0.2543),
    "1/2P+P+2P": (20.96, 1.059, 0.2653),
}


class RiverEval:
    """Fast river terminal CFVs on the 1326-hand basis."""

    def __init__(self, board5: tuple[int, ...]):
        self.mask = possible_hands_mask(board5).astype(bool)
        ranks = rank_board_hands(board5)
        self.legal = np.nonzero(self.mask)[0]
        r = ranks[self.legal].astype(np.int64)
        order = np.argsort(r, kind="stable")
        self.ord_idx = self.legal[order]
        self.ord_rank = r[order]
        # group boundaries of equal ranks in the sorted order
        self.grp_start = np.concatenate(
            ([0], np.nonzero(np.diff(self.ord_rank))[0] + 1))
        self.grp_end = np.concatenate((self.grp_start[1:],
                                       [len(self.ord_rank)]))
        self.cards = HAND_CARDS  # (1326, 2)

    def showdown(self, w: np.ndarray) -> np.ndarray:
        """v_i = sum_j feasible w_j * sign(rank_i - rank_j) for legal i."""
        out = np.zeros(HAND_COUNT)
        oi = self.ord_idx
        wo = w[oi]
        ca, cb = self.cards[oi, 0], self.cards[oi, 1]
        n = len(oi)
        # ascending pass: wins (strictly worse-ranked opponent mass)
        wins = np.empty(n)
        cumW = 0.0
        cumC = np.zeros(CARD_COUNT)
        for s, e in zip(self.grp_start, self.grp_end):
            wins[s:e] = cumW - cumC[ca[s:e]] - cumC[cb[s:e]]
            cumW += wo[s:e].sum()
            np.add.at(cumC, ca[s:e], wo[s:e])
            np.add.at(cumC, cb[s:e], wo[s:e])
        # descending pass: losses
        losses = np.empty(n)
        cumW = 0.0
        cumC = np.zeros(CARD_COUNT)
        for s, e in zip(self.grp_start[::-1], self.grp_end[::-1]):
            losses[s:e] = cumW - cumC[ca[s:e]] - cumC[cb[s:e]]
            cumW += wo[s:e].sum()
            np.add.at(cumC, ca[s:e], wo[s:e])
            np.add.at(cumC, cb[s:e], wo[s:e])
        out[oi] = wins - losses
        return out

    def fold_mass(self, w: np.ndarray) -> np.ndarray:
        """m_i = sum_j feasible w_j  (opponent mass not blocked by i)."""
        out = np.zeros(HAND_COUNT)
        li = self.legal
        tot = w[li].sum()
        percard = np.zeros(CARD_COUNT)
        np.add.at(percard, self.cards[li, 0], w[li])
        np.add.at(percard, self.cards[li, 1], w[li])
        out[li] = tot - percard[self.cards[li, 0]] \
            - percard[self.cards[li, 1]] + w[li]
        return out


def collect(node, decs, terms):
    if node.terminal is not None:
        terms.append(node)
        return
    decs.append(node)
    for c in node.children:
        collect(c, decs, terms)


class CfrSolver:
    """CFR+ (RM+, simultaneous updates), uniform average after skip."""

    def __init__(self, root, ev: RiverEval):
        self.root, self.ev = root, ev
        decs, _ = [], []
        collect(root, decs, _)
        for d in decs:
            k = len(d.children)
            d._reg = np.zeros((k, HAND_COUNT))

    def _terminal(self, n, reach):
        b = float(min(n.spent))
        u = np.zeros((2, HAND_COUNT))
        if n.terminal == "fold":
            sgn = -1.0 if n.folder == 0 else 1.0
            u[0] = sgn * b * self.ev.fold_mass(reach[1])
            u[1] = -sgn * b * self.ev.fold_mass(reach[0])
        else:
            u[0] = b * self.ev.showdown(reach[1])
            u[1] = -b * self.ev.showdown(reach[0])
        return u

    def _cfr(self, n, reach):
        if n.terminal is not None:
            return self._terminal(n, reach)
        k = len(n.children)
        pos = np.maximum(n._reg, 0.0)
        tot = pos.sum(axis=0, keepdims=True)
        strat = np.where(tot > 0, pos / np.where(tot > 0, tot, 1.0), 1.0 / k)
        p = n.player
        u = np.zeros((2, HAND_COUNT))
        avals = np.empty((k, HAND_COUNT))
        for a, c in enumerate(n.children):
            cr = [reach[0], reach[1]]
            cr[p] = cr[p] * strat[a]
            cu = self._cfr(c, cr)
            avals[a] = cu[p]
            u[p] += strat[a] * cu[p]
            u[1 - p] += cu[1 - p]
        n._reg += avals - u[p][None, :]
        np.maximum(n._reg, 0.0, out=n._reg)   # RM+
        if n is self.root:
            self._root_avals = avals
        return u

    def solve(self, r0, r1, iters, skip):
        k = len(self.root.children)
        acc = np.zeros((k, HAND_COUNT))
        for it in range(1, iters + 1):
            self._cfr(self.root, [np.asarray(r0, float),
                                  np.asarray(r1, float)])
            if it > skip:
                acc += self._root_avals
        return acc / (iters - skip)


def board_from_string(s: str) -> tuple[int, ...]:
    return tuple(string_to_cards(s))


def norms(vec, legal_mask):
    v = vec[legal_mask]
    return [float(np.abs(v).sum()), float(np.linalg.norm(v)),
            float(np.abs(v).max())]


def root_action_map(root):
    """action label -> child index; raises keyed by raise-to amount."""
    m = {}
    for i, (kind, amt) in enumerate(root.actions):
        m[(kind, amt)] = i
    return m


def state_rows(board_str, r0, r1, sparse_iters=100, sparse_skip=50,
               full_iters=400, full_skip=200):
    board = board_from_string(board_str)
    ev = RiverEval(board)
    full_root = build(FULL)
    full_cfv = CfrSolver(full_root, ev).solve(r0, r1, full_iters, full_skip)
    fmap = root_action_map(full_root)
    rows = {}
    for menu in MENU_ORDER:
        sroot = build(SPARSE[menu])
        scfv = CfrSolver(sroot, ev).solve(r0, r1, sparse_iters, sparse_skip)
        smap = root_action_map(sroot)
        # common root actions (call, matching raise-to sizes incl. all-in)
        common = [(k, smap[k], fmap[k]) for k in smap if k in fmap]
        errs = {k: scfv[si] - full_cfv[fi] for k, si, fi in common}
        lay = {}
        lm = ev.mask
        call_err = errs[("call", 0)]
        lay["call_only"] = norms(call_err, lm)
        bet_keys = [k for k in errs if k[0] == "raise"]
        allin = max(bet_keys, key=lambda k: k[1]) if bet_keys else None
        nonallin = [k for k in bet_keys if k != allin]
        per_action = {k: norms(errs[k], lm) for k in errs}
        acts = list(errs)
        lay["mean_action_norms"] = list(np.mean(
            [per_action[k] for k in acts], axis=0))
        lay["max_action_norms"] = list(np.max(
            [per_action[k] for k in acts], axis=0))
        stack_all = np.concatenate([errs[k][lm] for k in acts])
        lay["concat"] = [float(np.abs(stack_all).sum()),
                         float(np.linalg.norm(stack_all)),
                         float(np.abs(stack_all).max())]
        if bet_keys:
            stack_b = np.concatenate([errs[k][lm] for k in bet_keys])
            lay["bets_concat"] = [float(np.abs(stack_b).sum()),
                                  float(np.linalg.norm(stack_b)),
                                  float(np.abs(stack_b).max())]
        na_keys = [("call", 0)] + nonallin
        stack_na = np.concatenate([errs[k][lm] for k in na_keys])
        lay["nonallin_concat"] = [float(np.abs(stack_na).sum()),
                                  float(np.linalg.norm(stack_na)),
                                  float(np.abs(stack_na).max())]
        mean_vec = np.mean([errs[k] for k in acts], axis=0)
        sum_vec = np.sum([errs[k] for k in acts], axis=0)
        lay["mean_vector"] = norms(mean_vec, lm)
        lay["sum_vector"] = norms(sum_vec, lm)
        rows[menu] = lay
    return rows


def aggregate_mare(states_rows, layouts=None):
    """mean per-state norms -> ratios -> MARE vs paper, per layout."""
    if layouts is None:
        layouts = ["call_only", "mean_action_norms", "max_action_norms",
                   "mean_vector", "sum_vector", "concat", "bets_concat",
                   "nonallin_concat"]
    out = {}
    for lay in layouts:
        mares = []
        for menu in MENU_ORDER:
            arr = np.array([sr[menu][lay] for sr in states_rows])
            m = arr.mean(axis=0)
            ratios = [m[0] / m[1], m[1] / m[2]]
            p1, p2, pinf = PAPER[menu]
            pr = [p1 / p2, p2 / pinf]
            mares.append(np.mean([abs(ratios[0] - pr[0]) / pr[0],
                                  abs(ratios[1] - pr[1]) / pr[1]]))
        out[lay] = float(np.mean(mares))
    return out
