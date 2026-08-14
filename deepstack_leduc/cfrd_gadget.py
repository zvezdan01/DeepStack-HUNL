"""Shim `CFRDGadget` — loud-fail: golden gadget lost with the container.

Instantiating the gadget (the CFR-D re-solve path, `TurnEngine.resolve`)
requires the certified golden implementation; it must not be silently
re-implemented. The HUNL turn DATAGEN path never constructs it
(datagen uses `TurnEngine.resolve_first_node` exclusively).
"""
from __future__ import annotations

from . import _lost


class CFRDGadget:
    def __init__(self, *args, **kwargs):
        raise _lost("CFRDGadget (CFR-D re-solve)")
