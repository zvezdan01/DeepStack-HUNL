"""HUNL TURN DATAGENERATOR (pilot certification build).

Every parameter is anchored to HUNL_RECONSTRUCTION_SPEC.md v2 (freeze
f81d08c); targets are produced EXCLUSIVELY by the frozen HUNL Golden
Baseline v1 exact turn engine (34a50560…) — this module contains no
solver math of its own.

Parameter provenance (explicit, per instruction):
  VERIFIED  - datagen action set {F,C,P,A} (supplement p.26; config
              turn_menus=pot-only + all-in at every depth);
            - 1000 solver iterations (p.26); no NN; no card abstraction;
            - pot sampling: interval uniformly from {[100,100), [200,400),
              [400,2000), [2000,6000), [6000,19950]} then uniform integer
              (p.25 fn.2; "[100,100)" anomaly read as {100} per spec C3);
            - R(S,p) range procedure (p.26): p1 ~ U(0,p), split into
              lower-strength half S1 and rest, recurse; hand strength =
              P(beat uniform random hand at current public state);
            - target = root CFVs as fractions of the pot (p.25-26).
  INFERRED  - 500 omitted iterations (datagen omission not stated in the
              primaries; author Leduc pipeline + DeepHoldem use half);
            - batch structure: 10 samples per sampled board (author Leduc
              data_generation.lua gen_batch_size=10; HUNL batching not
              stated);
            - odd-split randomized rounding in R(S,p) (spec C2 verdict:
              author released code randomizes; supplement prose floors);
            - pot divisor = per-player committed chips (pot_half), the
              author Leduc values:mul(1/pot_size) convention.
  PROJECT CANONICAL (author artifact never published):
            - strength metric implementation: expected showdown sign vs
              the uniform-random opponent hand including the river runout
              (computed with the certified all-in-equity layer; any
              strictly monotone transform yields the same sort);
            - board sampler: rejection sampling with the certified
              THRandom (author Leduc random_card_generator.lua pattern;
              the HUNL supplement is silent on the sampler);
            - pot RNG mapping: category = random_range(0,4), value =
              random_range(lo,hi) — 2 draws per sample, always;
            - serialization schema HUNL_TURN_DATASET_V1 (below); the
              original HUNL byte layout was never released.

Serialization schema HUNL_TURN_DATASET_V1 (PROJECT CANONICAL, not
author-BIT_EXACT): per shard, little-endian .npy arrays over the FROZEN
1326 lexicographic hand ordering (hunl/cards.py contract):
  boards  (N, 4)      uint8   turn cards, ascending
  pots    (N,)        int32   per-player committed chips (pot_half)
  ranges  (N, 2, 1326) float32 sampled ranges (blocked hands exactly 0)
  targets (N, 2, 1326) float32 root CFVs / pot_half (both players,
                               engine f64 result cast to f32)
  masks   (N, 1326)   uint8   possible_hands_mask(board)
plus shard_XXXXX.json manifest (seed, counts, SHA-256 of every array
file, config/engine/generator/spec identifiers, RNG draw ledger).

RNG: certified THRandom (frozen DS datagen package, byte-certified vs
untouched THRandom.c). Master seed 20260814; per-shard seed = first 4
bytes (big-endian) of SHA-256("hunl-turn-datagen:{master}:shard:{idx:05d}").
Draw ledger per batch of 10 samples:
  board: 4 accepted + R rejection draws (R recorded; rejections VERIFIED
         author-code pattern), each draw = 1 u32 (random_range(1,52));
  ranges: per player, one rand_float(10) per internal stick-breaking node
         (1127 nodes over the 1128 live hands => 11,270 u32) plus one
         random_range(0,1) per odd-sized internal subset (K_ODD, a fixed
         constant of the 1128-subdivision, computed below) => 2 players;
  pots: 2 u32 per sample (category + value) => 20 per batch.
Sorting consumes NO RNG (deterministic stable argsort).
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

QT = Path("/home/user/quant-trade")
DS = Path("/workspace/deepstack_leduc_v1.1-bitexact-certified")
for p in (str(QT), str(DS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from datagen.th_random import THRandom  # frozen certified RNG  # noqa: E402
from hunl.cards import HAND_COUNT, possible_hands_mask  # noqa: E402
from hunl.config import DEFAULT_CONFIG  # noqa: E402
from hunl.turn import all_in_equity  # noqa: E402
from hunl.turn_engine import TurnEngine  # noqa: E402

SCHEMA_VERSION = "HUNL_TURN_DATASET_V1"
MASTER_SEED = 20260814
BATCH = 10                       # INFERRED (author Leduc gen_batch_size)
ENGINE_SHA = "34a50560a30cbff156e979b59af6c00e39f7f1a9"
SPEC_SHA = "f81d08c"
CFR_ITERS = 1000                 # VERIFIED
CFR_OMIT = 500                   # INFERRED
POT_INTERVALS = ((100, 100), (200, 399), (400, 1999),
                 (2000, 5999), (6000, 19950))   # VERIFIED (C3 reading)

DGCFG = dataclasses.replace(
    DEFAULT_CONFIG,
    turn_menus=((Fraction(1),), (Fraction(1),), (Fraction(1),)),
    turn_allin=True, turn_cfr_iters=CFR_ITERS, turn_cfr_omit=CFR_OMIT)

CONFIG_CANON = {
    "schema": SCHEMA_VERSION, "master_seed": MASTER_SEED, "batch": BATCH,
    "action_set": "{F,C,P,A} all depths (VERIFIED)",
    "cfr_iters": CFR_ITERS, "cfr_omit": f"{CFR_OMIT} (INFERRED)",
    "pot_intervals": POT_INTERVALS,
    "target_scaling": "root_cfvs / pot_half (pot divisor INFERRED)",
    "strength_metric": "all-in-equity vs uniform (PROJECT CANONICAL)",
    "board_sampler": "THRandom rejection (PROJECT CANONICAL)",
    "pot_rng": "cat=random_range(0,4), val=random_range(lo,hi) "
               "(PROJECT CANONICAL)",
    "odd_split": "randomized (spec C2 author-code verdict)",
    "engine_sha": ENGINE_SHA, "spec": SPEC_SHA,
    "hand_ordering": "frozen 1326 lex (hunl/cards.py)",
}
CONFIG_SHA = hashlib.sha256(
    json.dumps(CONFIG_CANON, sort_keys=True).encode()).hexdigest()


def shard_seed(idx: int) -> int:
    h = hashlib.sha256(
        f"hunl-turn-datagen:{MASTER_SEED}:shard:{idx:05d}".encode())
    return int.from_bytes(h.digest()[:4], "big")


class CountingTHRandom(THRandom):
    def __init__(self, seed: int):
        super().__init__(seed)
        self.draws = 0

    def random_u32(self):
        self.draws += 1
        return super().random_u32()


def sample_board(rng: THRandom) -> tuple[tuple[int, ...], int]:
    """Rejection sampler (author-code pattern), 0-based cards; returns
    (sorted board, number of rejected draws)."""
    used = [0] * 52
    out = []
    rejects = 0
    while len(out) < 4:
        c = rng.random_range(1, 52) - 1
        if used[c]:
            rejects += 1
            continue
        used[c] = 1
        out.append(c)
    return tuple(sorted(out)), rejects


class HunlTurnRangeGenerator:
    """R(S,p) stick-breaking over the 1128 live hands (f32, author Leduc
    recursion semantics incl. randomized odd split)."""

    def set_board(self, board4) -> None:
        self.board = tuple(int(c) for c in board4)
        self.mask = possible_hands_mask(self.board)
        self.live = np.nonzero(self.mask)[0]
        uni = np.zeros(HAND_COUNT)
        uni[self.mask] = 1.0 / len(self.live)
        strength = all_in_equity(self.board, 1.0, uni, uni)[0][self.live]
        order = np.argsort(strength, kind="stable")
        self.reverse = np.argsort(order, kind="stable")

    def _recurse(self, cards: np.ndarray, mass: np.ndarray,
                 rng: THRandom) -> None:
        batch, n = cards.shape
        if n == 1:
            cards[:, 0] = mass
            return
        rand = rng.rand_float(batch)
        m1 = (mass * rand).astype(np.float32, copy=False)
        m2 = (mass - m1).astype(np.float32, copy=False)
        half = n / 2
        if half % 1 != 0:
            half = (half - 0.5) + rng.random_range(0, 1)
        half = int(half)
        self._recurse(cards[:, :half], m1, rng)
        self._recurse(cards[:, half:], m2, rng)

    def generate(self, batch: int, rng: THRandom) -> np.ndarray:
        sorted_r = np.empty((batch, len(self.live)), dtype=np.float32)
        self._recurse(sorted_r, np.ones(batch, dtype=np.float32), rng)
        out = np.zeros((batch, HAND_COUNT), dtype=np.float32)
        out[:, self.live] = sorted_r[:, self.reverse]
        return out


def sample_pot(rng: THRandom) -> int:
    cat = rng.random_range(0, 4)
    lo, hi = POT_INTERVALS[cat]
    return rng.random_range(lo, hi)


def generate_shard(shard_idx: int, n_samples: int, out_dir: Path) -> dict:
    assert n_samples % BATCH == 0
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / f"shard_{shard_idx:05d}"
    manifest_path = Path(str(prefix) + ".json")
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())

    seed = shard_seed(shard_idx)
    rng = CountingTHRandom(seed)
    gen = HunlTurnRangeGenerator()
    boards = np.zeros((n_samples, 4), dtype=np.uint8)
    pots = np.zeros(n_samples, dtype=np.int32)
    ranges = np.zeros((n_samples, 2, HAND_COUNT), dtype=np.float32)
    targets = np.zeros((n_samples, 2, HAND_COUNT), dtype=np.float32)
    masks = np.zeros((n_samples, HAND_COUNT), dtype=np.uint8)
    ledger = {"board_draws": 0, "board_rejects": 0, "range_draws": 0,
              "pot_draws": 0}
    t0 = time.time()
    for b in range(n_samples // BATCH):
        d0 = rng.draws
        board, rej = sample_board(rng)
        ledger["board_draws"] += rng.draws - d0
        ledger["board_rejects"] += rej
        gen.set_board(board)
        d0 = rng.draws
        r1 = gen.generate(BATCH, rng)
        r2 = gen.generate(BATCH, rng)
        ledger["range_draws"] += rng.draws - d0
        pmask = possible_hands_mask(board)
        for i in range(BATCH):
            d0 = rng.draws
            pot = sample_pot(rng)
            ledger["pot_draws"] += rng.draws - d0
            assert ledger["pot_draws"] % 2 == 0
            row = b * BATCH + i
            te = TurnEngine(board, pot, cfg=DGCFG)
            cfvs = te.resolve_first_node(r1[i].astype(np.float64),
                                         r2[i].astype(np.float64))
            del te
            import gc
            gc.collect()   # bound worker RSS (OOM guard; numerics untouched)
            tgt = (cfvs / float(pot)).astype(np.float32)
            assert np.isfinite(tgt).all()
            assert (np.abs(tgt) <= DGCFG.stack / pot + 1e-6).all()
            assert (tgt[:, ~pmask] == 0).all()
            boards[row] = board
            pots[row] = pot
            ranges[row, 0] = r1[i]
            ranges[row, 1] = r2[i]
            targets[row] = tgt
            masks[row] = pmask.astype(np.uint8)
            print(f"shard {shard_idx} sample {row + 1}/{n_samples} "
                  f"pot {pot} board {board} "
                  f"[{(time.time()-t0)/60:.1f} min]", flush=True)

    shas = {}
    for name, arr in (("boards", boards), ("pots", pots),
                      ("ranges", ranges), ("targets", targets),
                      ("masks", masks)):
        path = Path(f"{prefix}.{name}.npy")
        tmp = Path(f"{prefix}.{name}.tmp.npy")
        np.save(tmp, arr)
        os.rename(tmp, path)
        shas[name] = hashlib.sha256(path.read_bytes()).hexdigest()

    gen_sha = os.popen(f"git -C {QT} rev-parse HEAD").read().strip()
    manifest = {
        "schema": SCHEMA_VERSION, "shard": shard_idx, "seed": seed,
        "samples": n_samples, "sha256": shas, "config_sha": CONFIG_SHA,
        "config": CONFIG_CANON, "engine_sha": ENGINE_SHA,
        "generator_sha": gen_sha, "spec": SPEC_SHA,
        "rng_ledger": ledger, "total_draws": rng.draws,
        "gen_minutes": round((time.time() - t0) / 60, 1),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    np.seterr(all="ignore")
    idx = int(sys.argv[1])
    n = int(sys.argv[2])
    out = Path(sys.argv[3])
    m = generate_shard(idx, n, out)
    print(json.dumps({k: m[k] for k in
                      ("shard", "seed", "samples", "gen_minutes")}))
