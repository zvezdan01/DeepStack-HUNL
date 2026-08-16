"""Versioned RECONSTRUCTION (not original DeepStack) of 1000 turn buckets.

What primary DeepStack/poker-abstraction sources constrain:
  * turn network uses 1000 clusters;
  * clustering family is k-means;
  * distance is earth mover's distance over hand-strength-like features;
  * cited abstraction literature describes one-dimensional final-equity
    histograms and k-means++/multiple restarts.

What the private DeepStack artifact does NOT publish:
  * exact histogram resolution used by DeepStack;
  * exact state weighting / canonical-state sampling;
  * RNG seed and restart count;
  * exact centroid-update implementation when EMD is the assignment metric;
  * serialized centroids and their bucket ordering.

This module therefore creates an explicitly PROJECT_RECONSTRUCTION artifact.
It is useful for training a reproducible replacement value network and for
end-to-end engineering, but it must never be labelled the original buckets.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cdist

from .bucket_features import DEFAULT_EQUITY_BINS, turn_board_final_equity_histograms
from .cards import CARD_COUNT, HAND_COUNT, possible_hands_mask
from .value_bucketing import BoardBucketMap, POSTFLOP_BUCKET_COUNT


def hist_to_emd_coordinates(hist: np.ndarray) -> np.ndarray:
    """Map normalized histograms to 1-D EMD coordinates.

    For equal-width 1-D histograms, EMD in bin units is L1 distance between
    cumulative masses across the 49 internal boundaries.  The final cumulative
    value (1) is omitted because it is constant.
    """
    x = np.asarray(hist, dtype=np.float32)
    if x.shape[-1] < 2:
        raise ValueError("histogram needs at least two bins")
    return np.cumsum(x, axis=-1, dtype=np.float32)[..., :-1]


def _assign_emd(xcdf: np.ndarray, ccdf: np.ndarray, chunk: int = 1024):
    n = xcdf.shape[0]
    labels = np.empty(n, dtype=np.int32)
    dmin = np.empty(n, dtype=np.float32)
    for lo in range(0, n, chunk):
        hi = min(n, lo + chunk)
        # scipy cityblock is the exact 1-D EMD coordinate L1 metric here.
        d = cdist(xcdf[lo:hi], ccdf, metric="cityblock")
        lab = np.argmin(d, axis=1)
        labels[lo:hi] = lab.astype(np.int32)
        dmin[lo:hi] = d[np.arange(hi - lo), lab].astype(np.float32)
    return labels, dmin


def _kmeanspp_emd(hist: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    """Standard D^2 k-means++ initialization under 1-D EMD distance."""
    n = hist.shape[0]
    if k > n:
        raise ValueError("k cannot exceed number of training features")
    xcdf = hist_to_emd_coordinates(hist)
    chosen = np.empty(k, dtype=np.int32)
    first = int(rng.integers(0, n))
    chosen[0] = first
    min_d = np.abs(xcdf - xcdf[first]).sum(axis=1, dtype=np.float32)
    min_d[first] = 0.0
    used = np.zeros(n, dtype=bool); used[first] = True
    for i in range(1, k):
        w = min_d.astype(np.float64) ** 2
        w[used] = 0.0
        total = float(w.sum())
        if total <= 0.0:
            # Degenerate duplicate feature set: deterministic first unused.
            idx = int(np.flatnonzero(~used)[0])
        else:
            t = float(rng.random()) * total
            idx = int(np.searchsorted(np.cumsum(w), t, side="right"))
            if idx >= n or used[idx]:
                cand = np.flatnonzero(~used)
                idx = int(cand[0])
        chosen[i] = idx; used[idx] = True
        d = np.abs(xcdf - xcdf[idx]).sum(axis=1, dtype=np.float32)
        np.minimum(min_d, d, out=min_d)
    return hist[chosen].copy()


@dataclass(frozen=True)
class ReconstructionArtifact:
    centroids: np.ndarray  # [1000,50], normalized probability histograms
    manifest: dict

    def save(self, path: str | Path) -> None:
        p = Path(path)
        m = json.dumps(self.manifest, sort_keys=True, separators=(",", ":"))
        np.savez_compressed(p, centroids=self.centroids.astype(np.float32),
                            manifest_json=np.asarray(m))

    @classmethod
    def load(cls, path: str | Path) -> "ReconstructionArtifact":
        z = np.load(path, allow_pickle=False)
        cent = np.asarray(z["centroids"], dtype=np.float32)
        manifest = json.loads(str(z["manifest_json"].item()))
        return cls(cent, manifest)


def sample_turn_features(
    *,
    seed: int,
    boards: int,
    hands_per_board: int,
    bins: int = DEFAULT_EQUITY_BINS,
) -> tuple[np.ndarray, dict]:
    """PROJECT sampling scheme: uniform raw turn boards, uniform legal hands."""
    rng = np.random.default_rng(int(seed))
    feats = []
    board_log = []
    for _ in range(int(boards)):
        board = tuple(int(x) for x in rng.choice(CARD_COUNT, size=4, replace=False))
        bulk = turn_board_final_equity_histograms(board, bins=bins)
        ids = np.flatnonzero(possible_hands_mask(board))
        take = min(int(hands_per_board), len(ids))
        pick = rng.choice(ids, size=take, replace=False)
        feats.append(bulk[pick].astype(np.float32) / np.float32(46.0))
        board_log.append(board)
    x = np.concatenate(feats, axis=0)
    meta = {
        "seed": int(seed),
        "boards": int(boards),
        "hands_per_board": int(hands_per_board),
        "samples": int(x.shape[0]),
        "bins": int(bins),
        "board_stream_sha256": hashlib.sha256(
            np.asarray(board_log, dtype='<i2').tobytes()).hexdigest(),
    }
    return x, meta


def fit_reconstruction_v1(
    hist: np.ndarray,
    *,
    k: int = POSTFLOP_BUCKET_COUNT,
    seed: int = 20260816,
    iterations: int = 5,
) -> ReconstructionArtifact:
    """Deterministic Lloyd-style replacement clustering.

    Assignment: nearest centroid under 1-D EMD.
    Update: arithmetic mean histogram of assigned samples.

    The arithmetic-mean update is an explicit PROJECT choice because the
    private implementation's centroid update under EMD is unpublished.
    """
    x = np.asarray(hist, dtype=np.float32)
    if x.ndim != 2 or x.shape[1] != DEFAULT_EQUITY_BINS:
        raise ValueError(f"expected [N,{DEFAULT_EQUITY_BINS}] normalized histograms")
    if np.max(np.abs(x.sum(axis=1) - 1.0)) > 2e-6:
        raise ValueError("training histograms must have unit mass")
    rng = np.random.default_rng(int(seed))
    cent = _kmeanspp_emd(x, int(k), rng)
    objectives = []
    populations = None
    for _ in range(int(iterations)):
        xc = hist_to_emd_coordinates(x)
        cc = hist_to_emd_coordinates(cent)
        labels, dmin = _assign_emd(xc, cc)
        objectives.append(float(dmin.sum(dtype=np.float64)))
        sums = np.zeros_like(cent, dtype=np.float64)
        populations = np.bincount(labels, minlength=k).astype(np.int32)
        np.add.at(sums, labels, x.astype(np.float64))
        nonempty = populations > 0
        cent[nonempty] = (sums[nonempty] / populations[nonempty, None]).astype(np.float32)
        # Keep prior centroid for empty clusters, deterministic and explicit.
        cent /= cent.sum(axis=1, keepdims=True, dtype=np.float32)
    # Final assignment/objective after last update.
    labels, dmin = _assign_emd(hist_to_emd_coordinates(x), hist_to_emd_coordinates(cent))
    populations = np.bincount(labels, minlength=k).astype(np.int32)
    objectives.append(float(dmin.sum(dtype=np.float64)))
    h = hashlib.sha256(cent.astype('<f4').tobytes()).hexdigest()
    manifest = {
        "schema": "HUNL_TURN_BUCKET_RECONSTRUCTION_V1",
        "status": "PROJECT_RECONSTRUCTION_NOT_ORIGINAL",
        "bucket_count": int(k),
        "feature": "50-bin final-river equity histogram; win+0.5*tie vs uniform opponent",
        "distance": "1D EMD = L1 distance of cumulative histogram",
        "initialization": "standard k-means++ D^2 under EMD",
        "centroid_update": "arithmetic mean histogram (PROJECT choice; private DeepStack detail unpublished)",
        "restarts": 1,
        "iterations": int(iterations),
        "seed": int(seed),
        "objective_history_bin_units": objectives,
        "empty_clusters_final": int(np.count_nonzero(populations == 0)),
        "min_cluster_population": int(populations.min()),
        "max_cluster_population": int(populations.max()),
        "centroid_sha256": h,
    }
    return ReconstructionArtifact(cent.astype(np.float32), manifest)


class ReconstructedTurnBucketProvider:
    """Board-specific 1326->1000 assignment from a versioned centroid file."""
    bucket_count = POSTFLOP_BUCKET_COUNT

    def __init__(self, artifact: ReconstructionArtifact):
        c = np.asarray(artifact.centroids, dtype=np.float32)
        if c.shape != (POSTFLOP_BUCKET_COUNT, DEFAULT_EQUITY_BINS):
            raise ValueError("turn centroid artifact must be [1000,50]")
        self.artifact = artifact
        self.centroids = c
        self.centroid_cdf = hist_to_emd_coordinates(c)

    @classmethod
    def from_file(cls, path: str | Path):
        return cls(ReconstructionArtifact.load(path))

    def for_board(self, board: tuple[int, ...]) -> BoardBucketMap:
        b = tuple(int(c) for c in board)
        if len(b) != 4:
            raise ValueError("turn bucket provider requires a 4-card public board")
        counts = turn_board_final_equity_histograms(b)
        legal = possible_hands_mask(b)
        ids = np.flatnonzero(legal)
        h = counts[ids].astype(np.float32) / np.float32(46.0)
        labels, _ = _assign_emd(hist_to_emd_coordinates(h), self.centroid_cdf, chunk=512)
        mapping = np.full(HAND_COUNT, -1, dtype=np.int16)
        mapping[ids] = labels.astype(np.int16)
        return BoardBucketMap(b, mapping, POSTFLOP_BUCKET_COUNT)


__all__ = [
    "hist_to_emd_coordinates", "ReconstructionArtifact",
    "sample_turn_features", "fit_reconstruction_v1",
    "ReconstructedTurnBucketProvider",
]
