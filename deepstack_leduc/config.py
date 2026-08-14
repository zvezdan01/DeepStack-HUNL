"""Shim `Config` — kwarg-compatible container, no engine semantics.

`hunl.river_resolver.hunl_river_config` constructs
`Config(ante=…, stack=…, bet_fractions=(), cfr_iters=…,
cfr_skip_iters=…, card_count=…)`. In the datagen runtime path the
resulting object is only ever passed onward to `CFRDGadget` (which in
this shim raises before reading it), so a plain attribute container is
sufficient and cannot alter any computed value.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Config:
    ante: float
    stack: float
    bet_fractions: tuple = field(default_factory=tuple)
    cfr_iters: int = 1000
    cfr_skip_iters: int = 500
    card_count: int = 6
