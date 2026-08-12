#!/usr/bin/env python3
"""Determinism check: full street-1 root resolve (1000 CFR iterations with
CFR-D machinery + original NN) run twice in-process; SHA-256 over every
result tensor printed so cross-process/restart identity can be compared.
Run from the DS repo root with LD_LIBRARY_PATH=$PWD PYTHONPATH=."""
import hashlib

import numpy as np

from deepstack_leduc.card_tools import uniform_range
from deepstack_leduc.resolving import Resolving
from deepstack_leduc.tree import Node
from deepstack_leduc.value_model import load_original_value_net


def resolve_once(net):
    resolving = Resolving(value_network=net)
    node = Node(1, 0, np.array([100.0, 100.0], dtype=np.float32), ())
    resolving.resolve_first_node(node, uniform_range(()), uniform_range(()))
    r = resolving.resolve_results
    h = hashlib.sha256()
    for name in ('strategy', 'achieved_cfvs', 'children_cfvs'):
        arr = np.ascontiguousarray(np.asarray(getattr(r, name)))
        h.update(name.encode())
        h.update(arr.tobytes())
    return h.hexdigest()


net = load_original_value_net()
h1 = resolve_once(net)
h2 = resolve_once(net)
print('run1', h1)
print('run2', h2)
print('same-process repeat identical:', h1 == h2)
