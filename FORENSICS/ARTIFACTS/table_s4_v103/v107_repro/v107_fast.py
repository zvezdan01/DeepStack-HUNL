"""Legal-basis matrix CFR for the V107 protocol (fast path).
Semantics identical to v107_engine (verified); n=|legal| basis, float32
BLAS matvecs for terminals."""
import sys
from pathlib import Path
import numpy as np

QT = Path("/home/user/quant-trade")
sys.path.insert(0, str(QT))
sys.path.insert(0, str(QT / "FORENSICS/ARTIFACTS/table_s4_v103/v99_v102_handoff"))
from reproduce_table_s4_tree_counts import SPARSE, FULL, build  # noqa
from hunl.cards import HAND_CARDS, HAND_COUNT, possible_hands_mask, string_to_cards  # noqa
from hunl.evaluator import rank_board_hands  # noqa

MENU_ORDER = ["2P", "1/2P", "P", "1/2P+P", "P+2P", "1/2P+P+2P"]
PAPER = {"2P": (64.79, 2.672, 0.3445), "1/2P": (58.24, 3.426, 0.7376),
         "P": (25.51, 1.272, 0.3372), "1/2P+P": (41.42, 1.541, 0.2955),
         "P+2P": (27.69, 1.390, 0.2543), "1/2P+P+2P": (20.96, 1.059, 0.2653)}


class Basis:
    def __init__(self, board_str):
        self.board = tuple(string_to_cards(board_str))
        mask = possible_hands_mask(self.board).astype(bool)
        self.legal = np.nonzero(mask)[0]
        self.n = len(self.legal)
        ranks = rank_board_hands(self.board)[self.legal].astype(np.int64)
        cards = HAND_CARDS[self.legal]
        share = ((cards[:, None, 0] == cards[None, :, 0])
                 | (cards[:, None, 0] == cards[None, :, 1])
                 | (cards[:, None, 1] == cards[None, :, 0])
                 | (cards[:, None, 1] == cards[None, :, 1]))
        feas = ~share
        sgn = np.sign(ranks[:, None] - ranks[None, :]).astype(np.float32)
        self.M = (sgn * feas).astype(np.float32)          # showdown
        self.L = feas.astype(np.float32)                  # fold mass
        np.fill_diagonal(self.L, 0.0)


def collect(node, decs):
    if node.terminal is not None:
        return
    decs.append(node)
    for c in node.children:
        collect(c, decs)


class Solver:
    def __init__(self, root, basis):
        self.root, self.b = root, basis
        decs = []
        collect(root, decs)
        n = basis.n
        for d in decs:
            d._reg = np.zeros((len(d.children), n), np.float32)

    def _term(self, nd, reach):
        b = np.float32(min(nd.spent))
        u = np.empty((2, self.b.n), np.float32)
        if nd.terminal == "fold":
            sgn = np.float32(-1.0 if nd.folder == 0 else 1.0)
            u[0] = sgn * b * (self.b.L @ reach[1])
            u[1] = -sgn * b * (self.b.L @ reach[0])
        else:
            u[0] = b * (self.b.M @ reach[1])
            u[1] = -b * (self.b.M @ reach[0])
        return u

    def _cfr(self, nd, reach):
        if nd.terminal is not None:
            return self._term(nd, reach)
        k = len(nd.children)
        pos = nd._reg
        tot = pos.sum(axis=0, keepdims=True)
        strat = np.where(tot > 0, pos / np.where(tot > 0, tot, 1), 1.0 / k)
        p = nd.player
        u = np.zeros((2, self.b.n), np.float32)
        avals = np.empty((k, self.b.n), np.float32)
        for a, c in enumerate(nd.children):
            cr = [reach[0], reach[1]]
            cr[p] = cr[p] * strat[a]
            cu = self._cfr(c, cr)
            avals[a] = cu[p]
            u[p] += strat[a] * cu[p]
            u[1 - p] += cu[1 - p]
        nd._reg = np.maximum(nd._reg + (avals - u[p][None, :]), 0.0)
        if nd is self.root:
            self._root_avals = avals
            self._root_u = u
        return u

    def solve(self, r0, r1, iters, skip):
        k = len(self.root.children)
        acc = np.zeros((k, self.b.n))
        r0 = r0.astype(np.float32); r1 = r1.astype(np.float32)
        for it in range(1, iters + 1):
            self._cfr(self.root, [r0, r1])
            if it > skip:
                acc += self._root_avals
        return acc / (iters - skip)


def norms(v):
    return [float(np.abs(v).sum()), float(np.linalg.norm(v)),
            float(np.abs(v).max())]


def amap(root):
    return {a: i for i, a in enumerate(root.actions)}
