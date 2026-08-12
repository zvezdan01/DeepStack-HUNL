#!/usr/bin/env python3
"""Phase 8: independent sequence-form LP equilibrium oracle for Kuhn poker
(scipy linprog / HiGHS) + Phase 7 cross-oracle triangulation:

  1. sequence-form LP game value  vs  exact rational -1/18
  2. decoded original CFR+ integer average strategy (trunk checkpoint)
     -> independent best-response exploitability  vs  the original binary's
     self-reported BR values
  3. AGT-trace CFR+ implementation (kuhn_cfr_trace.py) average strategy at
     1000 iterations -> exploitability
"""
import struct
import sys
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, '/home/user/quant-trade/certification/scripts')
import kuhn_cfr_trace as K

CARDS = ['J', 'Q', 'K']
RANK = {'J': 0, 'Q': 1, 'K': 2}


def sign(c, d):
    return 1.0 if RANK[c] > RANK[d] else -1.0


def solve_sequence_form_lp():
    # P1 sequence variables per card: B, C, CC, CF (4 per card, 12 total)
    x_index = {}
    for ci, c in enumerate(CARDS):
        for si, s in enumerate(('B', 'C', 'CC', 'CF')):
            x_index[(c, s)] = ci * 4 + si
    nx = 12
    # P2 sequence columns per card: Call, Fold (facing bet), Bet, Check (after check)
    y_index = {}
    for di, d in enumerate(CARDS):
        for si, s in enumerate(('Call', 'Fold', 'Bet', 'Check')):
            y_index[(d, s)] = di * 4 + si
    ny = 12

    w = 1.0 / 6.0
    A = np.zeros((nx, ny))
    for c in CARDS:
        for d in CARDS:
            if c == d:
                continue
            A[x_index[(c, 'B')], y_index[(d, 'Call')]] += w * 2 * sign(c, d)
            A[x_index[(c, 'B')], y_index[(d, 'Fold')]] += w * 1
            A[x_index[(c, 'CC')], y_index[(d, 'Bet')]] += w * 2 * sign(c, d)
            A[x_index[(c, 'CF')], y_index[(d, 'Bet')]] += w * -1
            A[x_index[(c, 'C')], y_index[(d, 'Check')]] += w * sign(c, d)

    # P1 constraints Ex = e
    E = np.zeros((6, nx))
    e = np.ones(6)
    for ci, c in enumerate(CARDS):
        E[ci * 2, x_index[(c, 'B')]] = 1
        E[ci * 2, x_index[(c, 'C')]] = 1
        E[ci * 2 + 1, x_index[(c, 'CC')]] = 1
        E[ci * 2 + 1, x_index[(c, 'CF')]] = 1
        E[ci * 2 + 1, x_index[(c, 'C')]] = -1
        e[ci * 2 + 1] = 0
    # P2 constraints F y = f  (6 infoset rows)
    F = np.zeros((6, ny))
    for di, d in enumerate(CARDS):
        F[di * 2, y_index[(d, 'Call')]] = 1
        F[di * 2, y_index[(d, 'Fold')]] = 1
        F[di * 2 + 1, y_index[(d, 'Bet')]] = 1
        F[di * 2 + 1, y_index[(d, 'Check')]] = 1
    f = np.ones(6)

    # variables z = [x (12), v (6)]; maximize f'v
    # s.t. F'v - A'x <= 0 ; E x = e ; x >= 0, v free
    c_obj = np.concatenate([np.zeros(nx), -f])
    A_ub = np.hstack([-A.T, F.T])
    b_ub = np.zeros(ny)
    A_eq = np.hstack([E, np.zeros((6, 6))])
    bounds = [(0, None)] * nx + [(None, None)] * 6
    res = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=e,
                  bounds=bounds, method='highs')
    assert res.success
    value = -res.fun
    x = res.x[:nx]
    return value, x, x_index


def strategy_from_ints(avg_ints):
    """Decode the original trunk int32 accumulated strategy into a strategy
    dict in kuhn_cfr_trace format. Layout (audited): per player 12 ints,
    node-major: P1: root(call@0-2, raise@3-5), node-B after check-bet
    (fold@6-8, call@9-11); P2: node-A after check (call@0-2, raise@3-5),
    node-C facing bet (fold@6-8, call@9-11); hands J,Q,K ascending.
    ACPC 'call' = check/call, 'raise' = bet."""
    p1, p2 = avg_ints
    sigma = {}
    for hi, card in enumerate(CARDS):
        def norm(a, b):
            t = a + b
            if t <= 0:
                return 0.5, 0.5
            return a / t, b / t
        # P1 root: trace actions (Bet, Check) = (raise, call)
        bet, check = norm(p1[3 + hi], p1[0 + hi])
        sigma[(card, '')] = {'Bet': bet, 'Check': check}
        # P1 after Check-Bet: (Call, Fold) = (call, fold)
        call, fold = norm(p1[9 + hi], p1[6 + hi])
        sigma[(card, '', 'Check', 'Bet')] = {'Call': call, 'Fold': fold}
        # P2 after check: (Bet, Check) = (raise, call)
        bet, check = norm(p2[3 + hi], p2[0 + hi])
        sigma[('', card, 'Check')] = {'Bet': bet, 'Check': check}
        # P2 facing bet: (Call, Fold)
        call, fold = norm(p2[9 + hi], p2[6 + hi])
        sigma[('', card, 'Bet')] = {'Call': call, 'Fold': fold}
    return sigma


def best_response_value(sigma, br_player):
    """Exact BR value for br_player against sigma (utility for br_player)."""

    def walk(deal, history, opp_reach):
        """Returns dict card->cf value not needed; recursive expectimax with
        opponent modeled by sigma, weighted by opp reach and chance."""
        u = K.terminal_utility(deal, history)
        if u is not None:
            return u if br_player == 0 else -u
        player = K.acting_player(history)
        key = K.infoset_key(deal, history)
        if player != br_player:
            return sum(p * walk(deal, history + (a,), opp_reach)
                       for a, p in sigma[key].items() if p > 0.0)
        # br player: handled at infoset level below
        raise RuntimeError

    # infoset-level BR via recursive computation over infosets
    from functools import lru_cache

    def br_value(deal, history):
        u = K.terminal_utility(deal, history)
        if u is not None:
            return {(): u}
        raise RuntimeError

    # simpler: enumerate BR pure strategies is small (each player: 4 infosets
    # x 2 actions = 16 pure strategies over reachable infosets)
    import itertools
    if br_player == 0:
        infosets = [(c, '') for c in CARDS] + [(c, '', 'Check', 'Bet') for c in CARDS]
    else:
        infosets = [('', c, 'Check') for c in CARDS] + [('', c, 'Bet') for c in CARDS]
    actions = {I: (['Bet', 'Check'] if len(I) == 2 or I[2:] == ('Check',)
                   else ['Call', 'Fold']) for I in infosets}
    # careful: root P1 key length 2; P2 keys length 3
    best = -np.inf
    best_pure = None
    for choice in itertools.product(*[actions[I] for I in infosets]):
        pure = dict(zip(infosets, choice))
        full = dict(sigma)
        for I, a in pure.items():
            full[I] = {a: 1.0}
        ev = K.expected_value({k: (v if isinstance(v, dict) else v)
                               for k, v in full.items()})
        ev = ev if br_player == 0 else -ev
        if ev > best:
            best = ev
            best_pure = pure
    return best, best_pure


def exploitability(sigma):
    b0, _ = best_response_value(sigma, 0)
    b1, _ = best_response_value(sigma, 1)
    return b0, b1, (b0 + b1) / 2.0


def main():
    print('=== Sequence-form LP oracle (scipy HiGHS) ===')
    value, x, x_index = solve_sequence_form_lp()
    exact = Fraction(-1, 18)
    print(f'LP game value       : {value!r}')
    print(f'exact -1/18         : {float(exact)!r}')
    print(f'abs diff            : {abs(value - float(exact)):.3e}')

    print()
    print('=== Original CFR+ trunk decode (iter 1000) -> independent BR ===')
    trunk = open('/home/user/quant-trade/certification/oracles/cfrplus_runs/'
                 'kuhn_i1000/cfr.split--1.iter-1000.warm-0/trunk', 'rb').read()
    ints = struct.unpack('<48i', trunk)
    p1_avg = ints[12:24]
    p2_avg = ints[36:48]
    sigma = strategy_from_ints((p1_avg, p2_avg))
    b0, b1, expl = exploitability(sigma)
    print(f'BR value P1 (ours)  : {b0!r}')
    print(f'BR value P2 (ours)  : {b1!r}')
    print(f'original binary said: -0.055488303, 0.055703005 '
          f'(0.935252988 mSBet/h ... at 166; 0.107350982 mSBet/h at 1000)')
    print(f'exploitability      : {expl!r} ({expl*1000:.9f} mSBet/h)')
    print(f'game value bracket  : [{-b1!r}, {b0!r}]  contains -1/18: '
          f'{-b1 <= float(exact) <= b0}')

    print()
    print('=== AGT-trace CFR+ implementation, 1000 iterations ===')
    lines = K.run_cfr_plus(1000)
    # rebuild final average from the run by re-running state (cheap)
    # re-run to capture final strategy_sum
    regret_sum, strategy_sum = K.new_tables()
    uniform_sigma = K.current_strategy(regret_sum)
    K.accumulate_player(uniform_sigma, strategy_sum, 0, 1.0)
    K.accumulate_player(uniform_sigma, strategy_sum, 1, 1.0)
    weights = {0: 1, 1: 1}
    first_half = True
    for it in range(1000):
        for half, update_player in ((1, 0), (2, 1)):
            sigma_t = K.current_strategy(regret_sum)
            if not first_half:
                prev = 1 - update_player
                weights[prev] += 1
                K.accumulate_player(sigma_t, strategy_sum, prev, float(weights[prev]))
            first_half = False
            deltas = {key: {a: 0.0 for a in acts} for key, acts in K.infoset_order()}
            for deal in K.DEALS:
                K.collect_deltas(deal, (), 1.0, 1.0, sigma_t, deltas, update_player)
            for key in regret_sum:
                for a in regret_sum[key]:
                    r = regret_sum[key][a] + deltas[key][a]
                    regret_sum[key][a] = r if r > 0.0 else 0.0
    avg = K.average_strategy(strategy_sum)
    b0t, b1t, explt = exploitability(avg)
    evt = K.expected_value(avg)
    print(f'avg strategy value  : {evt!r}')
    print(f'BR values           : {b0t!r}, {b1t!r}')
    print(f'exploitability      : {explt!r} ({explt*1000:.9f} mSBet/h)')

    print()
    print('=== Triangulation matrix ===')
    print(f'{"Quantity":28s} {"LP oracle":>14s} {"Orig CFR+ (decoded)":>20s} {"AGT-style CFR+":>16s}')
    print(f'{"game value (P1, sb/hand)":28s} {value:14.9f} '
          f'{(b0 - expl):20.9f} {evt:16.9f}')
    print(f'{"exploitability (sb/hand)":28s} {0.0:14.9f} {expl:20.9f} {explt:16.9f}')


if __name__ == '__main__':
    main()
