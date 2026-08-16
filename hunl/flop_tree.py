"""Thin flop wrapper around the source-constrained early-street tree."""
from .config import DEFAULT_CONFIG, HunlConfig
from .early_street_tree import EarlyStreetTreeBuilder, EarlyStreetNode


def build_flop_tree(board3, pot_half: int,
                    cfg: HunlConfig = DEFAULT_CONFIG) -> EarlyStreetNode:
    return EarlyStreetTreeBuilder("flop", cfg).build_flop(board3, pot_half)
