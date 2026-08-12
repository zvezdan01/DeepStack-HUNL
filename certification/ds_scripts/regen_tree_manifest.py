#!/usr/bin/env python3
"""Regenerate the Python public-tree manifest fresh from current code and
diff it against the bundled Lua manifest (lua_tree_manifest.tsv), mirroring
reference_tools/export_tree_manifest.lua's row format exactly.
Run from the DS repo root with PYTHONPATH=."""
import sys

import numpy as np

from deepstack_leduc.config import Config
from deepstack_leduc.tree import Node, PokerTreeBuilder

cfg = Config()
builder = PokerTreeBuilder(cfg)
root = Node(1, 0, np.array([float(cfg.ante), float(cfg.ante)], dtype=np.float32), ())
tree = builder.build_tree(root, limit_to_street=False)

rows = []
idx = 0


def board_str(node):
    if not node.board:
        return '-'
    return ','.join(str(int(b)) for b in node.board)


def actions_str(node):
    if node.current_player == -1:
        return 'chance'
    if not node.actions:
        return '-'
    return ','.join(str(int(a)) for a in node.actions)


def fmt_bet(x):
    v = float(x)
    return str(int(v)) if v == int(v) else str(v)


def walk(node, path):
    global idx
    idx += 1
    term = 1 if node.terminal else 0
    rows.append(
        f"{idx}\t{path}\t{node.street}\t{node.current_player}\t"
        f"{fmt_bet(node.bets[0])},{fmt_bet(node.bets[1])}\t{board_str(node)}\t"
        f"{term}\t{len(node.children)}\t{actions_str(node)}"
    )
    for i, child in enumerate(node.children):
        walk(child, f"{path}.{i}")


walk(tree, 'R')

lua_rows = [l.rstrip('\n') for l in open('lua_tree_manifest.tsv') if l.strip()]
print(f"python nodes: {len(rows)}, lua nodes: {len(lua_rows)}")
mismatches = 0
for i, (a, b) in enumerate(zip(rows, lua_rows)):
    if a != b:
        mismatches += 1
        if mismatches <= 5:
            print(f"MISMATCH row {i+1}:\n  lua: {b}\n  py : {a}")
mismatches += abs(len(rows) - len(lua_rows))
print(f"tree manifest: {len(lua_rows) - mismatches} / {len(lua_rows)} rows exact")
print("RESULT:", "PASS" if mismatches == 0 else "FAIL")
sys.exit(0 if mismatches == 0 else 1)
