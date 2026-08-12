#!/usr/bin/env python3
"""Re-verification of the '480/480 tensors bit-exact' claim
(CERTIFICATION_REPORT.md §'Continual resolving — all legal private-card /
board combinations for r300 -> call').

The claim's trace directory `continual_all_private_boards_lua_trace` ships
with its Lua exporter but NO committed comparator; this script provides the
missing comparison, mirroring the flow of the bundled
reference_tools/compare_all_chance_histories.py and the exporter
reference_tools/export_continual_all_private_boards.lua:
  per private card: resolve street-1 root, take r300 (strategy/cfv bound,
  range update); per legal board: restore state, update invariant, fresh
  street-2 resolve; compare all 16 stored tensors with np.array_equal
  (zero tolerance).

Run from the DS repo root with LD_LIBRARY_PATH=$PWD PYTHONPATH=.
"""
from pathlib import Path

import numpy as np

from deepstack_leduc.acpc import parse_matchstate
from deepstack_leduc.card_tools import normalize_range
from deepstack_leduc.continual_resolving import ContinualResolving
from deepstack_leduc.resolving import Resolving
from deepstack_leduc.torch7_tensor import load_float_tensor
from deepstack_leduc.value_model import load_original_value_net

ROOT = Path("continual_all_private_boards_lua_trace")
CARDS = ["As", "Ah", "Ks", "Kh", "Qs", "Qh"]

VALUE_NET = load_original_value_net()

checked = 0
failures = []


def check(case_dir, name, actual):
    global checked
    expected = load_float_tensor(case_dir / f"{name}.t7")
    actual = np.asarray(actual)
    checked += 1
    if actual.shape != expected.shape:
        failures.append(f"{case_dir}: {name}: shape {actual.shape} != {expected.shape}")
        return
    if not np.array_equal(actual, expected, equal_nan=True):
        aa = actual.astype(np.float64)
        bb = expected.astype(np.float64)
        mask = ~(np.isnan(aa) & np.isnan(bb))
        maxerr = float(np.max(np.abs(aa[mask] - bb[mask]))) if np.any(mask) else 0.0
        neq = int(np.sum(~((actual == expected) | (np.isnan(actual) & np.isnan(expected)))))
        failures.append(
            f"{case_dir}: {name}: NOT BIT-EXACT; different_elements={neq}, "
            f"max_abs_error={maxerr}"
        )


cases = 0
for private_id, private_card in enumerate(CARDS):
    cr = ContinualResolving(value_network=VALUE_NET)
    root_state = parse_matchstate(f"MATCHSTATE:0:1::{private_card}|")
    cr.start_new_hand(root_state)

    state1 = parse_matchstate(f"MATCHSTATE:0:1::{private_card}|")
    node1 = state1.to_node()
    cr._resolve_node(node1, state1)

    bet = 300
    strategy = cr.resolving.get_action_strategy(bet)
    cr.current_opponent_cfvs_bound = cr.resolving.get_action_cfv(bet).copy()
    cr.current_player_range *= strategy
    cr.current_player_range = normalize_range(node1.board, cr.current_player_range).astype(
        np.float32
    )
    cr.decision_id += 1
    cr.last_bet = bet
    cr.last_node = node1

    base_range = cr.current_player_range.copy()
    base_cfvs = cr.current_opponent_cfvs_bound.copy()
    first_resolving = cr.resolving  # exporter restores this before each board

    for board_id, board_card in enumerate(CARDS):
        if board_id == private_id:
            continue
        cases += 1
        case_dir = ROOT / f"private_{private_id + 1}_board_{board_id + 1}"

        cr.current_player_range = base_range.copy()
        cr.current_opponent_cfvs_bound = base_cfvs.copy()
        cr.resolving = first_resolving
        cr.last_bet = bet
        cr.last_node = node1

        check(case_dir, "street1.after_action.player_range", cr.current_player_range)
        check(case_dir, "street1.after_action.opponent_cfvs", cr.current_opponent_cfvs_bound)

        state2 = parse_matchstate(f"MATCHSTATE:0:1:r300c/:{private_card}|/{board_card}")
        node2 = state2.to_node()
        cr._update_invariant(node2, state2)

        check(case_dir, "street2.invariant.player_range", cr.current_player_range)
        check(case_dir, "street2.invariant.opponent_cfvs", cr.current_opponent_cfvs_bound)

        cr.resolving = Resolving(cr.cfg, cr.value_network)
        cr.resolving.resolve(node2, cr.current_player_range, cr.current_opponent_cfvs_bound)
        r = cr.resolving

        check(case_dir, "street2.achieved_cfvs", r.resolve_results.achieved_cfvs)
        check(case_dir, "street2.strategy_all", r.resolve_results.strategy)
        check(case_dir, "street2.children_cfvs_all", r.resolve_results.children_cfvs)
        possible = r.get_possible_actions()
        check(case_dir, "street2.possible_actions", possible)
        for action in [int(a) for a in np.asarray(possible).ravel()]:
            check(case_dir, f"street2.strategy_{action}", r.get_action_strategy(action))
            check(case_dir, f"street2.cfv_{action}", r.get_action_cfv(action))

print(f"cases={cases} tensors_checked={checked} failures={len(failures)}")
for f in failures[:50]:
    print("FAIL:", f)
print("RESULT:", "480/480 BIT-EXACT PASS" if (not failures and checked == 480) else "FAIL")
