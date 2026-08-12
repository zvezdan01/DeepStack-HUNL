#!/usr/bin/env python3
"""Bit-exact Python replica of the original Tammelin/CPRG CFR+ solver
(third_party/CFR_plus) for kuhn.game, written from a line-level source audit
— NOT from memory of the algorithm. Compared byte-for-byte against the
integer trunk checkpoints produced by the compiled original binary.

Source facts replicated (see certification/results/PHASE6_ORIGINAL_CFRPLUS.md):
- Regret, StrategyEntry = int32 (INTEGER_REGRETS / INTEGER_AVERAGE, cfr.h:8-9)
- regret update: d = lrint((v(I,a) - v(I)) * 16.0); R = max(R + d, 0)  (cfr.c:1793-1810)
- avg update at opponent nodes: A += lrint(sigma_opp(a) * pi_opp * weight)  (cfr.c:1850-1861)
- weight = (iter+1 - warmup) * 16.0 for iter+1 > warmup  (cfr.c:3818-3828)
- alternating updates, player index 1 traversed first  (cfr.c:2003)
- regret matching: p = R>0 ? R/sum : uniform, sum over int regrets  (regretsToPolicy)
- action order fold, call, raise  (betting_tools.c:133-215)
- immIndex assigned pre-order per player  (betting_tools.c:125,145)
- leaf eval: evalShowdown_1c / evalFold_1c inclusion-exclusion over opponent
  range with card removal  (card_tools.c:180-246)
- trunk dump: for round, for player: int32 regrets then int32 avg  (storage.c:1113-1186)
"""
import struct
import sys

import numpy as np


def lrint(x):
    return int(np.rint(np.float64(x)))


NUM_HANDS = 3  # J, Q, K ascending (getHandList enumerates cards ascending)
REGRET_SCALING = 16.0
AVG_SCALING = 16.0

# Kuhn betting tree (kuhn.game: blind 1 1, raiseSize 1, maxRaises 1,
# firstPlayer = 1 -> player index 0 acts first).
# Node = ('choice', player, immIndex, [(action, child), ...])
#      | ('leaf', is_showdown, value_p0, value_p1)
# leaf values from betting_tools.c:95-113:
#   folded[0]: value = (-spent0, +spent0); folded[1]: (+spent1, -spent1)
#   showdown: (spent, spent)

LEAF_SD1 = ('leaf', True, 1, 1)     # check-check showdown, spent 1
LEAF_SD2 = ('leaf', True, 2, 2)     # call after raise, spent 2
LEAF_P0_FOLDS = ('leaf', False, -1, 1)   # spent[0]=1
LEAF_P1_FOLDS = ('leaf', False, 1, -1)   # spent[1]=1

NODE_B = ('choice', 0, 2, [('fold', LEAF_P0_FOLDS), ('call', LEAF_SD2)])
NODE_A = ('choice', 1, 0, [('call', LEAF_SD1), ('raise', NODE_B)])
NODE_C = ('choice', 1, 2, [('fold', LEAF_P1_FOLDS), ('call', LEAF_SD2)])
ROOT = ('choice', 0, 0, [('call', NODE_A), ('raise', NODE_C)])

STRATEGY_SIZE = 4 * NUM_HANDS  # per player: 2 nodes x 2 actions x 3 hands


def eval_showdown_1c(sd_value, opp_probs):
    vals = [0.0] * NUM_HANDS
    s = 0.0
    for k in range(NUM_HANDS):
        s -= opp_probs[k]
    i = 0
    while i < NUM_HANDS:
        j = i + 1  # all ranks distinct in Kuhn
        for k in range(i, j):
            s += opp_probs[k]
        for k in range(i, j):
            vals[k] = sd_value * s
        for k in range(i, j):
            s += opp_probs[k]
        i = j
    return vals


def eval_fold_1c(fold_value, opp_probs):
    s = 0.0
    for k in range(NUM_HANDS):
        s += opp_probs[k]
    return [float(fold_value) * (s - opp_probs[k]) for k in range(NUM_HANDS)]


def regrets_to_policy(regrets, base):
    """case 2 of regretsToPolicy: two actions at offsets base, base+NUM_HANDS
    in the per-node layout (chanceMult = NUM_HANDS)."""
    probs = [0.0] * (2 * NUM_HANDS)
    for hand in range(NUM_HANDS):
        r0 = regrets[base + hand]
        r1 = regrets[base + NUM_HANDS + hand]
        ssum = float(r0 + r1)
        if ssum > 0:
            probs[hand] = float(r0) / ssum
            probs[NUM_HANDS + hand] = float(r1) / ssum
        else:
            probs[hand] = 0.5
            probs[NUM_HANDS + hand] = 0.5
    return probs


def vanilla_r(node, player, opp_probs, regrets, avg, update_weight):
    """Returns vals[3] for `player`. Mirrors cfr.c vanilla_r FP order."""
    if node[0] == 'leaf':
        _, is_showdown, v0, v1 = node
        value = v0 if player == 0 else v1
        if is_showdown:
            return eval_showdown_1c(value, opp_probs)
        return eval_fold_1c(value, opp_probs)

    _, acting, imm_index, children = node
    base = imm_index * NUM_HANDS

    if acting == player:
        cur_regrets = regrets[player]
        a_probs = regrets_to_policy(cur_regrets, base)
        vals = [0.0] * NUM_HANDS
        a_vals = [0.0] * (2 * NUM_HANDS)
        for c, (_, child) in enumerate(children):
            child_vals = vanilla_r(child, player, opp_probs, regrets, avg,
                                   update_weight)
            for i in range(NUM_HANDS):
                a_vals[c * NUM_HANDS + i] = child_vals[i]
                vals[i] += child_vals[i] * a_probs[c * NUM_HANDS + i]
        # finish updating regrets (i outer, c inner — cfr.c:1794-1811)
        for i in range(NUM_HANDS):
            for c in range(len(children)):
                d = lrint((a_vals[c * NUM_HANDS + i] - vals[i]) * REGRET_SCALING)
                nr = cur_regrets[base + c * NUM_HANDS + i] + d
                cur_regrets[base + c * NUM_HANDS + i] = nr if nr > 0 else 0
        return vals

    # opponent node
    opp = player ^ 1
    cur_regrets = regrets[opp]
    cur_avg = avg[opp]
    a_probs = regrets_to_policy(cur_regrets, base)
    # update average strategy (c outer, i inner — cfr.c:1851-1867)
    for c in range(len(children)):
        for i in range(NUM_HANDS):
            cur_avg[base + c * NUM_HANDS + i] += lrint(
                a_probs[c * NUM_HANDS + i] * opp_probs[i] * update_weight
            )
    vals = [0.0] * NUM_HANDS
    for c, (_, child) in enumerate(children):
        child_probs = [0.0] * NUM_HANDS
        opp_sum = 0.0
        for i in range(NUM_HANDS):
            child_probs[i] = opp_probs[i] * a_probs[c * NUM_HANDS + i]
            opp_sum += child_probs[i]
        # RIVER_CUTOFFS (round == numRounds-1 == 0 for Kuhn)
        if opp_sum <= 0:
            child_vals = [0.0] * NUM_HANDS
        else:
            child_vals = vanilla_r(child, player, child_probs, regrets, avg,
                                   update_weight)
        for i in range(NUM_HANDS):
            vals[i] += child_vals[i]
    return vals


def run(num_iters, warmup=0):
    regrets = [[0] * STRATEGY_SIZE, [0] * STRATEGY_SIZE]
    avg = [[0] * STRATEGY_SIZE, [0] * STRATEGY_SIZE]
    for it in range(num_iters):
        w = float(np.float32((it + 1 - warmup)) * np.float32(AVG_SCALING)) \
            if it + 1 > warmup else 0.0
        for p in (1, 0):  # cfr.c:2003 — player index 1 first
            opp_probs = [1.0] * NUM_HANDS
            vanilla_r(ROOT, p, opp_probs, regrets, avg, w)
    return regrets, avg


def serialize(regrets, avg):
    out = b''
    for p in (0, 1):
        out += struct.pack('<12i', *regrets[p])
        out += struct.pack('<12i', *avg[p])
    return out


def main():
    base = '/home/user/quant-trade/certification/oracles/cfrplus_runs'
    all_ok = True
    for iters in (1, 2, 5, 10, 100, 1000):
        oracle_path = (f'{base}/kuhn_i{iters}/'
                       f'cfr.split--1.iter-{iters}.warm-0/trunk')
        oracle = open(oracle_path, 'rb').read()
        regrets, avg = run(iters)
        ours = serialize(regrets, avg)
        ok = ours == oracle
        all_ok &= ok
        print(f'iters={iters:5d}: byte_equal={ok}')
        if not ok:
            oi = struct.unpack(f'<{len(oracle)//4}i', oracle)
            ui = struct.unpack(f'<{len(ours)//4}i', ours)
            for idx, (a, b) in enumerate(zip(ui, oi)):
                if a != b:
                    print(f'  first divergence int32[{idx}]: ours={a} oracle={b}')
                    break
    print('KUHN CFR+ AUTHOR-SOURCE BIT EXACT (replica vs original binary):',
          'PASS' if all_ok else 'FAIL')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
