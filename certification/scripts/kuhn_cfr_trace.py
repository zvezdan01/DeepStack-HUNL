#!/usr/bin/env python3
"""Reproduce the official AGT Kuhn CFR / CFR+ traces
(third_party/agt_tests/ref_cfr_kuhn.txt, ref_cfr_plus_kuhn.txt)
value-by-value at reference precision (5 decimals).

Certification reference implementation — no production HUHL solver exists in
this repository. Game definition mirrors the trace's infoset naming:
P1 infoset key = (card1, '', *history), P2 = ('', card2, *history);
actions ordered Bet/Check and Call/Fold as printed.
"""
import itertools
import sys

CARDS = ['J', 'Q', 'K']
RANK = {'J': 0, 'Q': 1, 'K': 2}
DEALS = [(a, b) for a, b in itertools.permutations(CARDS, 2)]  # prob 1/6 each

# history: tuple of actions from {'Bet','Check','Call','Fold'}
TERMINAL = {
    ('Bet', 'Call'): 'showdown2',
    ('Bet', 'Fold'): 'p1_wins1',
    ('Check', 'Check'): 'showdown1',
    ('Check', 'Bet', 'Call'): 'showdown2',
    ('Check', 'Bet', 'Fold'): 'p2_wins1',
}


def terminal_utility(deal, history):
    kind = TERMINAL.get(history)
    if kind is None:
        return None
    c1, c2 = deal
    if kind == 'p1_wins1':
        return 1.0
    if kind == 'p2_wins1':
        return -1.0
    amount = 1.0 if kind == 'showdown1' else 2.0
    return amount if RANK[c1] > RANK[c2] else -amount


def acting_player(history):
    return len(history) % 2  # 0 = P1, 1 = P2


def infoset_key(deal, history):
    player = acting_player(history)
    if player == 0:
        return (deal[0], '') + history
    return ('', deal[1]) + history


def legal_actions(history):
    if len(history) == 0 or history == ('Check',):
        return ['Bet', 'Check']
    return ['Call', 'Fold']


ALL_HISTORIES_NONTERMINAL = [(), ('Check',), ('Bet',), ('Check', 'Bet')]


def infoset_order():
    """Infosets in the order the trace prints them (P1 first)."""
    order = []
    for card in CARDS:
        order.append(((card, ''), ['Bet', 'Check']))
    for card in CARDS:
        order.append(((card, '', 'Check', 'Bet'), ['Call', 'Fold']))
    for card in CARDS:
        order.append((('', card, 'Check'), ['Bet', 'Check']))
        order.append((('', card, 'Bet'), ['Call', 'Fold']))
    # reorder P2: trace prints ('', J, Check), ('', J, Bet), ('', Q, Check)...
    return order


def regret_matching(regrets, actions):
    positive = [max(r, 0.0) for r in (regrets[a] for a in actions)]
    total = sum(positive)
    if total > 0:
        return {a: p / total for a, p in zip(actions, positive)}
    return {a: 1.0 / len(actions) for a in actions}


def current_strategy(regret_sum):
    sigma = {}
    for key, regrets in regret_sum.items():
        actions = list(regrets.keys())
        sigma[key] = regret_matching(regrets, actions)
    return sigma


def average_strategy(strategy_sum):
    avg = {}
    for key, sums in strategy_sum.items():
        actions = list(sums.keys())
        total = sum(sums.values())
        if total > 0:
            avg[key] = {a: sums[a] / total for a in actions}
        else:
            avg[key] = {a: 1.0 / len(actions) for a in actions}
    return avg


def expected_value(sigma):
    """Expected utility of P1 under profile sigma (full traversal)."""

    def ev(deal, history):
        u = terminal_utility(deal, history)
        if u is not None:
            return u
        key = infoset_key(deal, history)
        return sum(
            p * ev(deal, history + (a,)) for a, p in sigma[key].items() if p > 0.0
        )

    return sum(ev(deal, ()) for deal in DEALS) / len(DEALS)


def new_tables():
    regret_sum = {}
    strategy_sum = {}
    for key, actions in infoset_order():
        regret_sum[key] = {a: 0.0 for a in actions}
        strategy_sum[key] = {a: 0.0 for a in actions}
    return regret_sum, strategy_sum


def cfr_traverse(deal, history, reach1, reach2, sigma, regret_sum, update_player):
    """Returns utility for P1. Updates update_player's regrets."""
    u = terminal_utility(deal, history)
    if u is not None:
        return u
    player = acting_player(history)
    key = infoset_key(deal, history)
    actions = legal_actions(history)
    strat = sigma[key]

    action_values = {}
    value = 0.0
    for a in actions:
        if player == 0:
            av = cfr_traverse(deal, history + (a,), reach1 * strat[a], reach2,
                              sigma, regret_sum, update_player)
        else:
            av = cfr_traverse(deal, history + (a,), reach1, reach2 * strat[a],
                              sigma, regret_sum, update_player)
        action_values[a] = av
        value += strat[a] * av

    if player == update_player:
        chance = 1.0 / len(DEALS)
        if player == 0:
            cf_reach = chance * reach2
            sign = 1.0
        else:
            cf_reach = chance * reach1
            sign = -1.0
        for a in actions:
            regret_sum[key][a] += cf_reach * sign * (action_values[a] - value)
    return value


def collect_deltas(deal, history, reach1, reach2, sigma, deltas, update_player):
    """Like cfr_traverse but accumulates raw regret deltas into `deltas`
    instead of writing to the cumulative table."""
    u = terminal_utility(deal, history)
    if u is not None:
        return u
    player = acting_player(history)
    key = infoset_key(deal, history)
    actions = legal_actions(history)
    strat = sigma[key]

    action_values = {}
    value = 0.0
    for a in actions:
        if player == 0:
            av = collect_deltas(deal, history + (a,), reach1 * strat[a], reach2,
                                sigma, deltas, update_player)
        else:
            av = collect_deltas(deal, history + (a,), reach1, reach2 * strat[a],
                                sigma, deltas, update_player)
        action_values[a] = av
        value += strat[a] * av

    if player == update_player:
        chance = 1.0 / len(DEALS)
        if player == 0:
            cf_reach = chance * reach2
            sign = 1.0
        else:
            cf_reach = chance * reach1
            sign = -1.0
        for a in actions:
            deltas[key][a] += cf_reach * sign * (action_values[a] - value)
    return value


def accumulate_strategy(deal, history, reach_own, sigma, strategy_sum, player, weight):
    """Accumulate player's current strategy weighted by own reach."""
    u = terminal_utility(deal, history)
    if u is not None:
        return
    acting = acting_player(history)
    key = infoset_key(deal, history)
    strat = sigma[key]
    if acting == player:
        for a, p in strat.items():
            strategy_sum[key][a] += weight * reach_own * p
        for a, p in strat.items():
            accumulate_strategy(deal, history + (a,), reach_own * p, sigma,
                                strategy_sum, player, weight)
    else:
        for a in strat:
            accumulate_strategy(deal, history + (a,), reach_own, sigma,
                                strategy_sum, player, weight)


def accumulate_player(sigma, strategy_sum, player, weight):
    """Accumulate `player`'s current strategy once per infoset, weighted by
    the player's own reach probability pi_p(I)."""
    if player == 0:
        for card in CARDS:
            root = (card, '')
            for a, p in sigma[root].items():
                strategy_sum[root][a] += weight * p
            deep = (card, '', 'Check', 'Bet')
            own_reach = sigma[root]['Check']
            for a, p in sigma[deep].items():
                strategy_sum[deep][a] += weight * own_reach * p
    else:
        for card in CARDS:
            for hist in (('Check',), ('Bet',)):
                key = ('', card) + hist
                for a, p in sigma[key].items():
                    strategy_sum[key][a] += weight * p


def fmt_line(prefix, kind, player, key, values):
    parts = ', '.join(f'{a}: {p:.5f}' for a, p in values)
    return f'{prefix}: {kind} of P{player} at {key}: {parts}'


def emit_state(prefix, regret_sum, strategy_sum, sigma_for_util, lines):
    util = expected_value(average_strategy(strategy_sum))
    lines.append(f'{prefix}: Utility of avg. strategies: {util:.5f}, {-util:.5f}')
    avg = average_strategy(strategy_sum)
    for key, actions in infoset_order():
        player = 2 if key[0] == '' else 1
        lines.append(fmt_line(prefix, 'Avg. strategy', player, key,
                              [(a, avg[key][a]) for a in actions]))
    return lines


def emit_regrets(prefix, regret_sum, players, lines):
    for key, actions in infoset_order():
        player = 2 if key[0] == '' else 1
        if player not in players:
            continue
        lines.append(fmt_line(prefix, 'Cumulative regrets', player, key,
                              [(a, regret_sum[key][a]) for a in actions]))
    return lines


def run_cfr(num_iters=10):
    """Vanilla CFR, simultaneous updates."""
    regret_sum, strategy_sum = new_tables()
    lines = []
    for it in range(1, num_iters + 1):
        sigma = current_strategy(regret_sum)
        # accumulate average strategy (reach-weighted, weight 1)
        for deal in DEALS:
            for p in (0, 1):
                accumulate_strategy(deal, (), 1.0, sigma, strategy_sum, p, 1.0)
        # regret updates for both players from the same sigma:
        # aggregate deltas across all deals, then add once per infoset
        deltas = {key: {a: 0.0 for a in actions} for key, actions in infoset_order()}
        for deal in DEALS:
            for p in (0, 1):
                collect_deltas(deal, (), 1.0, 1.0, sigma, deltas, p)
        for key in regret_sum:
            for a in regret_sum[key]:
                regret_sum[key][a] += deltas[key][a]
        prefix = f'Iter {it}'
        emit_state(prefix, regret_sum, strategy_sum, None, lines)
        emit_regrets(prefix, regret_sum, (1, 2), lines)
    return lines


def cfr_plus_traverse(deal, history, reach1, reach2, sigma, regret_sum, update_player):
    """CFR+ half update: regrets clipped at zero on accumulation."""
    u = terminal_utility(deal, history)
    if u is not None:
        return u
    player = acting_player(history)
    key = infoset_key(deal, history)
    actions = legal_actions(history)
    strat = sigma[key]

    action_values = {}
    value = 0.0
    for a in actions:
        if player == 0:
            av = cfr_plus_traverse(deal, history + (a,), reach1 * strat[a], reach2,
                                   sigma, regret_sum, update_player)
        else:
            av = cfr_plus_traverse(deal, history + (a,), reach1, reach2 * strat[a],
                                   sigma, regret_sum, update_player)
        action_values[a] = av
        value += strat[a] * av

    if player == update_player:
        chance = 1.0 / len(DEALS)
        if player == 0:
            cf_reach = chance * reach2
            sign = 1.0
        else:
            cf_reach = chance * reach1
            sign = -1.0
        for a in actions:
            r = regret_sum[key][a] + cf_reach * sign * (action_values[a] - value)
            regret_sum[key][a] = r if r > 0.0 else 0.0
    return value


def run_cfr_plus(num_iters=10):
    """CFR+ with alternating updates.

    Derived accumulation scheme (verified against the official trace):
    at the start of each half-update (P1's half then P2's half), BOTH
    players' current strategies are accumulated into the average with
    weight = global half-update counter (1, 2, 3, ...), reach-weighted;
    then the half's player regrets are updated with CFR+ clipping.
    """
    regret_sum, strategy_sum = new_tables()
    # initialization: the uniform strategy is itself the first accumulation
    # event (weight 1), reach-weighted like every later accumulation
    uniform_sigma = current_strategy(regret_sum)
    accumulate_player(uniform_sigma, strategy_sum, 0, 1.0)
    accumulate_player(uniform_sigma, strategy_sum, 1, 1.0)
    lines = []
    weights = {0: 1, 1: 1}
    first_half = True
    for it in range(1, num_iters + 1):
        for half, update_player in ((1, 0), (2, 1)):
            sigma = current_strategy(regret_sum)
            if not first_half:
                prev_player = 1 - update_player
                weights[prev_player] += 1
                accumulate_player(sigma, strategy_sum, prev_player,
                                  float(weights[prev_player]))
            first_half = False
            deltas = {key: {a: 0.0 for a in actions} for key, actions in infoset_order()}
            for deal in DEALS:
                collect_deltas(deal, (), 1.0, 1.0, sigma, deltas, update_player)
            for key in regret_sum:
                for a in regret_sum[key]:
                    r = regret_sum[key][a] + deltas[key][a]
                    regret_sum[key][a] = r if r > 0.0 else 0.0
            prefix = f'Iter {it}, Update of P{half}'
            emit_state(prefix, regret_sum, strategy_sum, None, lines)
            emit_regrets(prefix, regret_sum, (half,), lines)
    return lines


import re

_NUM = re.compile(r'-?\d+\.\d{5}')


def _values(line):
    return [float(x) for x in _NUM.findall(line)]


def compare(produced, reference_path):
    ref_lines = [l.rstrip('\n') for l in open(reference_path) if l.strip()]
    match = 0
    value_match = 0
    n_values = 0
    first_divergence = None
    for i, (ours, ref) in enumerate(zip(produced, ref_lines)):
        if ours == ref:
            match += 1
        elif first_divergence is None:
            first_divergence = (i, ref, ours)
        ov, rv = _values(ours), _values(ref)
        n_values += len(rv)
        if len(ov) == len(rv):
            value_match += sum(1 for a, b in zip(ov, rv) if abs(a - b) < 1e-12 or abs(a - b) <= 5e-6)
    return match, len(ref_lines), len(produced), first_divergence, value_match, n_values


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else '/home/user/quant-trade/third_party/agt_tests'

    lines = run_cfr(10)
    m, n, np_, div, vm, nv = compare(lines, f'{base}/ref_cfr_kuhn.txt')
    print(f'CFR official trace: {m} / {n} lines exact-to-reference-format (produced {np_})')
    print(f'CFR official trace: {vm} / {nv} values exact at 5-decimal reference precision')
    if div:
        print(f'  first divergence line {div[0]+1}:\n    ref : {div[1]}\n    ours: {div[2]}')
    open('/home/user/quant-trade/certification/results/trace_cfr_kuhn_ours.txt', 'w').write('\n'.join(lines) + '\n')

    lines = run_cfr_plus(10)
    m, n, np_, div, vm, nv = compare(lines, f'{base}/ref_cfr_plus_kuhn.txt')
    print(f'CFR+ official trace: {m} / {n} lines exact-to-reference-format (produced {np_})')
    print(f'CFR+ official trace: {vm} / {nv} values exact at 5-decimal reference precision')
    if div:
        print(f'  first divergence line {div[0]+1}:\n    ref : {div[1]}\n    ours: {div[2]}')
    open('/home/user/quant-trade/certification/results/trace_cfr_plus_kuhn_ours.txt', 'w').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
