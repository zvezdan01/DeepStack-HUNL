"""Thin pre-flop wrapper around the source-constrained early-street tree."""
from .config import DEFAULT_CONFIG, HunlConfig
from .early_street_tree import EarlyStreetTreeBuilder, EarlyStreetNode


def build_preflop_tree(cfg: HunlConfig = DEFAULT_CONFIG) -> EarlyStreetNode:
    return EarlyStreetTreeBuilder("preflop", cfg).build_preflop()
