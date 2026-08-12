#!/usr/bin/env python3
"""Re-verification of the tensor/network boundary against the orphan
`nn_root_trace` inputs_N/values_N export (export_nn_root.lua: root
resolve_first_node with uniform ranges; next_street_boxes' NN input tensors
and value tensors per lookahead depth). Zero-tolerance comparison.
Run from the DS repo root with LD_LIBRARY_PATH=$PWD PYTHONPATH=."""
from pathlib import Path

import numpy as np

from deepstack_leduc.card_tools import uniform_range
from deepstack_leduc.resolving import Resolving
from deepstack_leduc.tree import Node
from deepstack_leduc.torch7_tensor import load_float_tensor
from deepstack_leduc.value_model import load_original_value_net

ROOT = Path('nn_root_trace')

net = load_original_value_net()
resolving = Resolving(value_network=net)
node = Node(1, 0, np.array([100.0, 100.0], dtype=np.float32), ())
player_range = uniform_range(())
opponent_range = uniform_range(())
resolving.resolve_first_node(node, player_range, opponent_range)

look = resolving.lookahead
checked = 0
failures = []
for d in sorted(look.next_street_boxes_inputs):
    box = look.next_street_boxes[d]
    for kind, actual in (
        ('inputs', box.next_round_inputs),
        ('values', box.next_round_values),
    ):
        path = ROOT / f'{kind}_{d}.t7'
        if not path.exists():
            failures.append(f'{kind}_{d}: no reference file')
            continue
        expected = load_float_tensor(path)
        checked += 1
        actual = np.asarray(actual)
        if actual.shape != expected.shape:
            failures.append(f'{kind}_{d}: shape {actual.shape} != {expected.shape}')
        elif not np.array_equal(actual, expected):
            diff = float(np.max(np.abs(actual.astype(np.float64) - expected.astype(np.float64))))
            neq = int(np.sum(actual != expected))
            failures.append(f'{kind}_{d}: NOT BIT-EXACT diff_elems={neq} max_abs={diff}')

print(f'tensors checked={checked} failures={len(failures)}')
for f in failures:
    print('FAIL:', f)
print('RESULT:', 'NN BOX TENSORS BIT-EXACT PASS' if not failures and checked == 8 else 'FAIL')
