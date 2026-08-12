#!/usr/bin/env python3
"""L2 closure: reproducible comparator for Resolving.get_root_cfv_both_players
(resolving.py:69-72 / lookahead.py get_results root swap — Lua
resolving.lua:119-121 + lookahead.lua:419-424 clone + player-row swap).

Oracle anchoring (all zero tolerance):
  row asserted against get_root_cfv() — itself certified bit-exact against
  the frozen `continual_lua_trace/before.starting_cfvs_p1.t7` — plus the
  swap-structure assertions: both_players[[1,0]] must equal the raw root
  average-CFV tensor, and the P1 row must equal resolve_results.achieved_cfvs
  (certified in every d1.achieved_cfvs trace tensor).
Run from the DS repo root with LD_LIBRARY_PATH=$PWD PYTHONPATH=."""
from pathlib import Path

import numpy as np

from deepstack_leduc.card_tools import uniform_range
from deepstack_leduc.resolving import Resolving
from deepstack_leduc.tree import Node
from deepstack_leduc.torch7_tensor import load_float_tensor
from deepstack_leduc.value_model import load_original_value_net

failures = []

net = load_original_value_net()
r = Resolving(value_network=net)
node = Node(1, 0, np.array([100.0, 100.0], dtype=np.float32), ())
u = uniform_range(())
res = r.resolve_first_node(node, u, u)

both = r.get_root_cfv_both_players()
root_cfv = r.get_root_cfv()
raw_root = r.lookahead.average_cfvs_data[1].reshape(2, 6)

# 1) shape and swap structure: both == raw_root with player rows swapped
if both.shape != (2, 6):
    failures.append(f'shape {both.shape}')
if not np.array_equal(both[[1, 0]], raw_root):
    failures.append('both_players[[1,0]] != raw root average CFVs (swap broken)')
# 2) row 0 equals certified get_root_cfv() (Lua swap puts opponent slot first;
#    lookahead.lua:419-424 / lookahead.py get_results both = root[[1,0]])
if not np.array_equal(both[0], root_cfv):
    failures.append('both[0] != get_root_cfv()')
# 3) get_root_cfv equals the frozen Lua trace tensor (external anchor)
expected = load_float_tensor(Path('continual_lua_trace/before.starting_cfvs_p1.t7'))
if not np.array_equal(root_cfv, expected):
    failures.append('get_root_cfv != frozen starting_cfvs_p1 trace')
# 4) row 1 equals certified achieved_cfvs (= root slot 0)
if not np.array_equal(both[1], res.achieved_cfvs):
    failures.append('both[1] != resolve_results.achieved_cfvs')
# 5) results object consistency (root_cfvs_both_players on first-node resolve)
if res.root_cfvs_both_players is not None and not np.array_equal(res.root_cfvs_both_players, both):
    failures.append('results.root_cfvs_both_players != get_root_cfv_both_players()')

print(f'failures={len(failures)}')
for f in failures:
    print('FAIL:', f)
print('RESULT:', 'ROOT CFV BOTH PLAYERS BIT-EXACT PASS' if not failures else 'FAIL')
