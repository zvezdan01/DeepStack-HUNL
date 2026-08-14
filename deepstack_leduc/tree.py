"""Shim tree constants + loud-fail `Node` — golden engine lost.

`CALL`/`FOLD` are the DeepStack action constants (Lua
`constants.actions`: fold = -2, ccall = -1); they are only compared
against inside `hunl.river_resolver` functions that construct golden
`Node` objects — and `Node` raises here, so no golden-tree path can run
silently. The HUNL turn DATAGEN path never touches this module at
runtime.
"""
from __future__ import annotations

from . import _lost

FOLD = -2
CALL = -1


class Node:
    def __init__(self, *args, **kwargs):
        raise _lost("tree.Node (golden lookahead tree)")
