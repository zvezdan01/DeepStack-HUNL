#!/usr/bin/env python3
"""Re-verification of the '6/6 checkpoints bit-exact' deterministic
first-action claim against the orphan `continual_lua_trace` export
(export_continual_raise300.lua; no comparator was committed).
Run from the DS repo root with LD_LIBRARY_PATH=$PWD PYTHONPATH=."""
from pathlib import Path

import numpy as np

from deepstack_leduc.acpc import parse_matchstate
from deepstack_leduc.card_tools import normalize_range
from deepstack_leduc.continual_resolving import ContinualResolving
from deepstack_leduc.torch7_tensor import load_float_tensor
from deepstack_leduc.value_model import load_original_value_net

ROOT = Path('continual_lua_trace')
checked = 0
failures = []


def check(name, actual):
    global checked
    expected = load_float_tensor(ROOT / f'{name}.t7')
    actual = np.asarray(actual)
    checked += 1
    if actual.shape != expected.shape:
        failures.append(f'{name}: shape {actual.shape} != {expected.shape}')
    elif not np.array_equal(actual, expected, equal_nan=True):
        aa, bb = actual.astype(np.float64), expected.astype(np.float64)
        mask = ~(np.isnan(aa) & np.isnan(bb))
        failures.append(f'{name}: NOT BIT-EXACT max_abs='
                        f'{float(np.max(np.abs(aa[mask]-bb[mask]))) if mask.any() else 0.0}')


cr = ContinualResolving(value_network=load_original_value_net())
state = parse_matchstate('MATCHSTATE:0:1::As|')
cr.start_new_hand(state)
node = state.to_node()
cr._resolve_node(node, state)

check('before.player_range', cr.current_player_range)
check('before.starting_cfvs_p1', cr.starting_cfvs_p1)

bet = 300
check('action.strategy', cr.resolving.get_action_strategy(bet))
check('action.opponent_cfv', cr.resolving.get_action_cfv(bet))

cr.current_opponent_cfvs_bound = cr.resolving.get_action_cfv(bet).copy()
cr.current_player_range *= cr.resolving.get_action_strategy(bet)
cr.current_player_range = normalize_range(node.board, cr.current_player_range).astype(np.float32)

check('after.player_range', cr.current_player_range)
check('after.opponent_cfvs_bound', cr.current_opponent_cfvs_bound)

print(f'tensors checked={checked} failures={len(failures)}')
for f in failures:
    print('FAIL:', f)
print('RESULT:', '6/6 FIRST-ACTION BIT-EXACT PASS' if not failures and checked == 6 else 'FAIL')
