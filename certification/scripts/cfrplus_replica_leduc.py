#!/usr/bin/env python3
"""Bit-exact Python replica of the original Tammelin/CPRG CFR+ solver for
leduc.game (2 rounds, suit isomorphism, board chance nodes), written from a
line-level source audit of third_party/CFR_plus/cfr.c — NOT from memory.

All structural tables (betting tree with immIndex/leaf values, canonical
boards with weights, per-board rank-sorted hand lists with weights and
canonical indexes) are read from certification/oracles/leduc_structure_dump.txt,
which was dumped by the original C code itself (cfr_dump harness in
certification/scripts/CFR_plus_patched/), so no card-isomorphism logic is
re-derived by hand.

Replicated cfr.c semantics (line references into third_party/CFR_plus/cfr.c):
- chance node: firstNewBoard/nextNewBoard board loop, handMapping raw->parent
  (weight-0 raw indexes map to canonical parent, cfr.c:1240-1266 firstNewBoard),
  per-board pointer advance by numHands (1585-1595), board-weight accumulation
  (1570-1583), final pointer jump bts*numBoards*numHands (1625-1641),
  vals /= boardFactor*weight epilogue + weight-0 canonical copy (1643-1664),
  RIVER_CUTOFFS skip on zero opponent reach in final round (1539-1568)
- player node regret update d = lrint((v(a)-v)*16.0), R = max(R+d, 0)
  (1793-1811); opponent node avg update A += lrint(sigma*pi_opp*weight)
  (1850-1867); regret matching with 2- and 3-action cases (regretsToPolicy)
- leaf evals evalShowdown_1c / evalFold_1c (card_tools.c:180-246)
- alternating updates, player index 1 first (2003); weight (iter+1)*16 float
"""
import re
import struct
import sys

import numpy as np


def lrint(x):
    return int(np.rint(np.float64(x)))


REGRET_SCALING = 16.0


class Choice:
    __slots__ = ('round', 'player', 'imm', 'children')

    def __init__(self, rnd, player, imm):
        self.round = rnd
        self.player = player
        self.imm = imm
        self.children = []


class Leaf:
    __slots__ = ('showdown', 'v0', 'v1')

    def __init__(self, sd, v0, v1):
        self.showdown = sd
        self.v0 = v0
        self.v1 = v1


class Chance:
    __slots__ = ('round', 'bts', 'child')

    def __init__(self, rnd, bts):
        self.round = rnd
        self.bts = bts
        self.child = None


class Hand:
    __slots__ = ('raw', 'rank', 'weight', 'canon')

    def __init__(self, raw, rank, weight, canon):
        self.raw = raw
        self.rank = rank
        self.weight = weight
        self.canon = canon


def parse_structure(path):
    lines = open(path).read().splitlines()
    meta = {}
    rounds = {}
    boards = {0: [], 1: []}
    r0hands = []
    bhands = {}
    tree_lines = []
    in_tree = False
    for ln in lines:
        if ln == 'TREE':
            in_tree = True
            continue
        if in_tree:
            tree_lines.append(ln)
            continue
        if ln.startswith('numRounds'):
            meta.update(dict(kv.split('=') for kv in ln.split()))
        elif ln.startswith('round='):
            d = dict(kv.split('=') for kv in ln.split())
            rounds[int(d['round'])] = d
        elif ln.startswith('board '):
            d = dict(kv.split('=') for kv in ln.split()[1:])
            boards[int(d['r'])].append(d)
        elif ln.startswith('hand '):
            d = dict(kv.split('=') for kv in ln.split()[1:])
            r0hands.append(Hand(int(d['raw']), int(d['rank']),
                                int(d['weight']), int(d['canon'])))
        elif ln.startswith('bhand '):
            d = dict(kv.split('=') for kv in ln.split()[1:])
            bhands.setdefault(int(d['b']), []).append(
                Hand(int(d['raw']), int(d['rank']), int(d['weight']), int(d['canon'])))

    # parse tree by indentation
    def parse_node(idx, depth):
        ln = tree_lines[idx]
        ind = (len(ln) - len(ln.lstrip())) // 2
        assert ind == depth, (ln, depth)
        t = ln.split()
        if t[0] == 'LEAF':
            d = dict(kv.split('=') for kv in t[1:])
            return Leaf(int(d['sd']), int(d['v0']), int(d['v1'])), idx + 1
        if t[0] == 'CHANCE':
            d = dict(kv.split('=') for kv in t[1:])
            node = Chance(int(d['round']), int(d['bts0']))
            child, nxt = parse_node(idx + 1, depth + 1)
            node.child = child
            return node, nxt
        d = dict(kv.split('=') for kv in t[1:])
        node = Choice(int(d['round']), int(d['player']), int(d['imm']))
        nxt = idx + 1
        while nxt < len(tree_lines):
            nind = (len(tree_lines[nxt]) - len(tree_lines[nxt].lstrip())) // 2
            if nind <= depth:
                break
            child, nxt = parse_node(nxt, depth + 1)
            node.children.append(child)
        return node, nxt

    tree, _ = parse_node(0, 0)
    return meta, rounds, boards, r0hands, bhands, tree


class Solver:
    def __init__(self, structure_path):
        (self.meta, self.rounds, self.boards, self.r0hands, self.bhands,
         self.tree) = parse_structure(structure_path)
        self.num_rounds = int(self.meta['numRounds'])
        self.num_hands = {r: int(self.rounds[r]['numHands']) for r in self.rounds}
        self.num_boards = {r: int(self.rounds[r]['numBoards']) for r in self.rounds}
        self.board_factor = {r: float(self.rounds[r]['boardFactor']) for r in self.rounds}
        self.strategy_size = {
            r: int(self.rounds[r]['strategySize0']) for r in self.rounds
        }
        self.board_weight = {
            r: [int(b['weight']) for b in self.boards[r]] for r in self.boards
        }
        # regrets/avg: [player][round] flat int lists
        self.regrets = [{r: [0] * self.strategy_size[r] for r in self.rounds}
                        for _ in range(2)]
        self.avg = [{r: [0] * self.strategy_size[r] for r in self.rounds}
                    for _ in range(2)]

    # --- leaf evals (card_tools.c) ---
    @staticmethod
    def eval_showdown(sd_value, hands, opp_probs):
        n = len(hands)
        vals = [0.0] * n
        s = 0.0
        for k in range(n):
            s -= opp_probs[k]
        i = 0
        while i < n:
            j = i + 1
            while j < n and hands[j].rank == hands[i].rank:
                j += 1
            for k in range(i, j):
                s += opp_probs[k]
            for k in range(i, j):
                vals[k] = sd_value * s
            for k in range(i, j):
                s += opp_probs[k]
            i = j
        return vals

    @staticmethod
    def eval_fold(fold_value, hands, opp_probs):
        n = len(hands)
        s = 0.0
        for k in range(n):
            s += opp_probs[k]
        return [float(fold_value) * (s - opp_probs[k]) for k in range(n)]

    def regrets_to_policy(self, regs, base, chance_mult, num_hands, num_choices):
        probs = [0.0] * (num_choices * num_hands)
        for hand in range(num_hands):
            rs = [regs[base + c * chance_mult + hand] for c in range(num_choices)]
            ssum = float(sum(rs))
            if ssum > 0:
                for c in range(num_choices):
                    probs[c * num_hands + hand] = float(rs[c]) / ssum
            else:
                for c in range(num_choices):
                    probs[c * num_hands + hand] = 1.0 / num_choices
        return probs

    def vanilla_r(self, node, player, hands, opp_probs, offsets, update_weight):
        """offsets: dict round -> [offset_p0, offset_p1] (mutable)."""
        num_hands = len(hands)
        if isinstance(node, Leaf):
            value = node.v0 if player == 0 else node.v1
            if node.showdown:
                return self.eval_showdown(value, hands, opp_probs)
            return self.eval_fold(value, hands, opp_probs)

        if isinstance(node, Chance):
            r = node.round
            nb = self.num_boards[r]
            nh = self.num_hands[r]
            # handMapping: raw -> parent index (canonical for weight 0)
            mapping = {}
            for i, h in enumerate(hands):
                if h.weight:
                    mapping[h.raw] = i
            for i, h in enumerate(hands):
                if not h.weight:
                    mapping[h.raw] = mapping[h.canon]

            vals = [0.0] * num_hands
            old = {p: offsets[r][p] for p in (0, 1)}
            child_lists = self.bhands if r == 1 else {0: self.r0hands}
            for b in range(nb):
                child_hands = child_lists[b]
                child_opp = [opp_probs[mapping[h.raw]] for h in child_hands]
                s = 0.0
                for x in child_opp:
                    s += x
                if r == self.num_rounds - 1 and s <= 0:
                    child_vals = [0.0] * len(child_hands)
                else:
                    child_vals = self.vanilla_r(node.child, player, child_hands,
                                                child_opp, offsets, update_weight)
                w = self.board_weight[r][b]
                for i, h in enumerate(child_hands):
                    vals[mapping[h.raw]] += child_vals[i] * w
                for p in (0, 1):
                    offsets[r][p] += nh
            for p in (0, 1):
                offsets[r][p] = old[p] + node.bts * nb * nh

            for i, h in enumerate(hands):
                if h.weight:
                    vals[i] /= self.board_factor[r] * h.weight
            for i, h in enumerate(hands):
                if not h.weight:
                    vals[i] = vals[mapping[h.canon]]
            return vals

        # Choice node
        r = node.round
        chance_mult = self.num_boards[r] * self.num_hands[r]
        nc = len(node.children)
        if node.player == player:
            regs = self.regrets[player][r]
            base = offsets[r][player] + node.imm * chance_mult
            a_probs = self.regrets_to_policy(regs, base, chance_mult, num_hands, nc)
            vals = [0.0] * num_hands
            a_vals = [0.0] * (nc * num_hands)
            for c, child in enumerate(node.children):
                child_vals = self.vanilla_r(child, player, hands, opp_probs,
                                            offsets, update_weight)
                for i in range(num_hands):
                    a_vals[c * num_hands + i] = child_vals[i]
                    vals[i] += child_vals[i] * a_probs[c * num_hands + i]
            for i in range(num_hands):
                for c in range(nc):
                    d = lrint((a_vals[c * num_hands + i] - vals[i]) * REGRET_SCALING)
                    nr = regs[base + c * chance_mult + i] + d
                    regs[base + c * chance_mult + i] = nr if nr > 0 else 0
            return vals

        opp = player ^ 1
        regs = self.regrets[opp][r]
        avg = self.avg[opp][r]
        base = offsets[r][opp] + node.imm * chance_mult
        a_probs = self.regrets_to_policy(regs, base, chance_mult, num_hands, nc)
        for c in range(nc):
            for i in range(num_hands):
                avg[base + c * chance_mult + i] += lrint(
                    a_probs[c * num_hands + i] * opp_probs[i] * update_weight
                )
        vals = [0.0] * num_hands
        for c, child in enumerate(node.children):
            child_probs = [0.0] * num_hands
            opp_sum = 0.0
            for i in range(num_hands):
                child_probs[i] = opp_probs[i] * a_probs[c * num_hands + i]
                opp_sum += child_probs[i]
            if r == self.num_rounds - 1 and opp_sum <= 0:
                child_vals = [0.0] * num_hands
            else:
                child_vals = self.vanilla_r(child, player, hands, child_probs,
                                            offsets, update_weight)
            for i in range(num_hands):
                vals[i] += child_vals[i]
        return vals

    iteration = 0

    def run(self, num_iters, warmup=0):
        for _ in range(num_iters):
            it = self.iteration
            self.iteration += 1
            if it + 1 > warmup:
                w = float(np.float32(it + 1 - warmup) * np.float32(16.0))
            else:
                w = 0.0
            for p in (1, 0):
                opp_probs = [1.0] * len(self.r0hands)
                offsets = {r: [0, 0] for r in self.rounds}
                self.vanilla_r(self.tree, p, self.r0hands, opp_probs, offsets, w)

    def serialize(self):
        out = b''
        for r in sorted(self.rounds):
            for p in (0, 1):
                out += struct.pack(f'<{self.strategy_size[r]}i', *self.regrets[p][r])
                out += struct.pack(f'<{self.strategy_size[r]}i', *self.avg[p][r])
        return out


def main():
    base = '/home/user/quant-trade/certification/oracles/cfrplus_runs'
    struct_path = '/home/user/quant-trade/certification/oracles/leduc_structure_dump.txt'
    all_ok = True
    prev_iters = 0
    solver = Solver(struct_path)
    for iters in (1, 2, 5, 10, 100, 1000):
        solver.run(iters - prev_iters)
        prev_iters = iters
        oracle_path = (f'{base}/leduc_i{iters}/'
                       f'cfr.split--1.iter-{iters}.warm-0/trunk')
        oracle = open(oracle_path, 'rb').read()
        ours = solver.serialize()
        ok = ours == oracle
        all_ok &= ok
        print(f'iters={iters:5d}: byte_equal={ok} '
              f'(ours {len(ours)} B, oracle {len(oracle)} B)')
        if not ok:
            oi = struct.unpack(f'<{len(oracle)//4}i', oracle)
            ui = struct.unpack(f'<{len(ours)//4}i', ours)
            for idx, (a, b) in enumerate(zip(ui, oi)):
                if a != b:
                    print(f'  first divergence int32[{idx}]: ours={a} oracle={b}')
                    break
            break
    print('LEDUC CFR+ AUTHOR-SOURCE BIT EXACT (replica vs original binary):',
          'PASS' if all_ok else 'FAIL')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
