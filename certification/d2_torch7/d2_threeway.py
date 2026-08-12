#!/usr/bin/env python3
"""D2 three-way classification: bundled historical target vs released-Lua
fresh vs Python Golden Baseline fresh, per row, zero tolerance.
Run from the DS repo root with LD_LIBRARY_PATH=$PWD PYTHONPATH=."""
import numpy as np

from datagen.generator import BucketConversionF32
from deepstack_leduc.torch7_tensor import load_float_tensor

S = '/tmp/claude-0/-home-user-quant-trade/ab297466-f300-5fe2-aeba-419112c121c8/scratchpad'
boards = load_float_tensor(f'{S}/d2_boards.t7')
lua = load_float_tensor(f'{S}/d2_lua_fresh.t7')          # (200,2,6) card space
py = np.load(f'{S}/d2_python_fresh.npy')                  # (200,2,6) card space

hist = np.zeros((200, 72), dtype=np.float32)
i = 0
for split in ('train', 'valid'):
    t = load_float_tensor(f'reference_lua/Data/TrainSamples/PotBet/{split}.targets')
    hist[i:i+100] = t
    i += 100

counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'LuaHist_only': 0}
rows_by_class = {'C': [], 'D': [], 'LuaHist_only': []}
for r in range(200):
    board = int(boards[r]) - 1
    conv = BucketConversionF32()
    conv.set_board(board)
    lua_b = conv.card_range_to_bucket_range(lua[r]).reshape(-1)
    py_b = conv.card_range_to_bucket_range(py[r]).reshape(-1)
    h = hist[r]
    lp = np.array_equal(lua_b, py_b)
    lh = np.array_equal(lua_b, h)
    ph = np.array_equal(py_b, h)
    if lp and lh:
        counts['A'] += 1
    elif lp and not lh:
        counts['B'] += 1
    elif lh and not lp:
        counts['C'] += 1
        rows_by_class['C'].append(r)
    elif ph and not lp:
        counts['LuaHist_only'] += 1  # python==hist but lua differs (anomaly)
        rows_by_class['LuaHist_only'].append(r)
    else:
        counts['D'] += 1
        rows_by_class['D'].append(r)

print('A (Lua==Py==Hist)        :', counts['A'])
print('B (Lua==Py != Hist)      :', counts['B'])
print('C (Lua==Hist != Py)      :', counts['C'], rows_by_class['C'][:10])
print('D (all differ)           :', counts['D'], rows_by_class['D'][:10])
print('anomaly (Py==Hist!=Lua)  :', counts['LuaHist_only'], rows_by_class['LuaHist_only'][:10])

# Frozen case: valid row 1 = global row 101, target idx 20
r = 101
board = int(boards[r]) - 1
conv = BucketConversionF32(); conv.set_board(board)
lua_b = conv.card_range_to_bucket_range(lua[r]).reshape(-1)
py_b = conv.card_range_to_bucket_range(py[r]).reshape(-1)
print('\nFrozen case valid row 1, target idx 20:')
print('  historical:', hex(int.from_bytes(hist[r][20].tobytes(), "little")), float(hist[r][20]))
print('  Lua fresh :', hex(int.from_bytes(lua_b[20].tobytes(), "little")), float(lua_b[20]))
print('  Py fresh  :', hex(int.from_bytes(py_b[20].tobytes(), "little")), float(py_b[20]))
