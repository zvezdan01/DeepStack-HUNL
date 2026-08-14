"""Shim `Lookahead`/`LookaheadResults` — loud-fail: golden engine lost.

`hunl.river_resolver.RiverResolver` (turn→river transition path) needs
the certified golden lookahead; it is not runnable in this container.
The HUNL turn DATAGEN path never constructs either class.
"""
from __future__ import annotations

from . import _lost


class Lookahead:
    def __init__(self, *args, **kwargs):
        raise _lost("Lookahead (golden river solver)")


class LookaheadResults:
    def __init__(self, *args, **kwargs):
        raise _lost("LookaheadResults")
