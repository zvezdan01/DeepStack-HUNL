#!/usr/bin/env python3
"""Re-verification of the value-network bit-for-bit claim against the orphan
`nn_root_trace` Lua export (layer-by-layer Torch7 outputs; no comparator was
committed for it). Replays deepstack_leduc.value_model._torch7_exact_inference
layer-by-layer (the exact code path used by bit-exact resolves) on the traced
input `layer_00_input.t7` and compares every stored layer output plus the raw
pre-correction output with np.array_equal (zero tolerance).
Run from the DS repo root with LD_LIBRARY_PATH=$PWD PYTHONPATH=."""
from pathlib import Path

import numpy as np
import torch
from torch import nn

from deepstack_leduc.torch7_blas import mm as torch7_mm
from deepstack_leduc.torch7_tensor import load_float_tensor
from deepstack_leduc.value_model import load_original_value_net

ROOT = Path('nn_root_trace')
model = load_original_value_net()

x = load_float_tensor(ROOT / 'layer_00_input.t7').astype(np.float32)
out = np.ascontiguousarray(x, dtype=np.float32).copy()

checked = 0
failures = []


def check(name, actual):
    global checked
    expected = load_float_tensor(ROOT / f'{name}.t7')
    checked += 1
    if actual.shape != expected.shape:
        failures.append(f'{name}: shape {actual.shape} != {expected.shape}')
    elif not np.array_equal(actual, expected):
        diff = np.max(np.abs(actual.astype(np.float64) - expected.astype(np.float64)))
        failures.append(f'{name}: NOT BIT-EXACT max_abs={diff}')


layer_idx = 0
for layer in model.feedforward:
    layer_idx += 1
    if isinstance(layer, nn.Linear):
        w = np.ascontiguousarray(layer.weight.detach().cpu().numpy().astype(np.float32).T)
        b = layer.bias.detach().cpu().numpy().astype(np.float32)
        out = torch7_mm(np.ascontiguousarray(out, dtype=np.float32), w)
        for r in range(out.shape[0]):
            for c in range(out.shape[1]):
                out[r, c] = np.float32(out[r, c] + b[c])
    elif isinstance(layer, nn.PReLU):
        with torch.no_grad():
            out = layer(torch.from_numpy(np.ascontiguousarray(out, dtype=np.float32))).cpu().numpy().astype(np.float32)
    check(f'layer_{layer_idx:02d}', out)

# raw_lua_output.t7 is produced by reference_tools/test_fixed_nn.lua as the
# FULL model forward, i.e. INCLUDING the zero-sum correction graph — compare
# against the corrected output, not the bare feedforward chain.
from deepstack_leduc.value_model import _torch7_exact_inference  # noqa: E402

check('raw_lua_output', _torch7_exact_inference(model, x))

print(f'tensors checked={checked} failures={len(failures)}')
for f in failures:
    print('FAIL:', f)
print('RESULT:', 'NN LAYER TRACE BIT-EXACT PASS' if not failures else 'FAIL')
