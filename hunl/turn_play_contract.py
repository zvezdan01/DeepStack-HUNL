"""Fail-closed contract for the ORIGINAL DeepStack play-time turn resolver.

Zarick et al. (2020), in their DeepStack reimplementation, explicitly report
that original DeepStack solved turn situations to the end of the game using a
*bucketed abstraction for all river actions* and that the details of that
bucketing were never presented.

Accordingly, this module contains no guessed default mapping.  The existing
``TurnEngine`` remains the full-card exact-to-end DATAGEN / oracle engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class RiverActionBucketProvider(Protocol):
    """Unpublished dependency required by the original play-time turn solve."""
    def bucket_ids(self, board5: tuple[int, int, int, int, int]) -> np.ndarray:
        """Return one river abstraction id per private-hand slot."""
        ...


class MissingOriginalRiverBucketing(RuntimeError):
    pass


@dataclass(frozen=True)
class OriginalTurnPlayStatus:
    solves_to_game_end: bool = True
    river_actions_bucketed: bool = True
    river_bucket_details_published: bool = False
    replacement_with_full_card_engine_allowed: bool = False


def require_original_river_bucketing(provider: RiverActionBucketProvider | None):
    if provider is None:
        raise MissingOriginalRiverBucketing(
            "Original DeepStack play-time turn resolving requires the unpublished "
            "river card abstraction. The full-card TurnEngine is a datagen/oracle "
            "engine and is not silently substituted here."
        )
    return provider


__all__ = [
    "RiverActionBucketProvider",
    "MissingOriginalRiverBucketing",
    "OriginalTurnPlayStatus",
    "require_original_river_bucketing",
]
