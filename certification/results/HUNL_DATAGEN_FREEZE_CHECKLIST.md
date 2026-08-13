# HUNL_DATAGEN_FREEZE_CHECKLIST — gate for "HUNL TURN DATAGEN CERTIFIED FOR BULK GENERATION: YES"

Date: 2026-08-13. Read-only parallel audit task. Companion:
`HUNL_DATAGEN_SOURCE_AUDIT.md` (citations), `HUNL_DATAGEN_ORACLE_PLAN.md`
(oracles + corpus), `HUNL_DATAGEN_FAILURE_MATRIX.md` (F-xx references).

The verdict line may be written ONLY when every box below is checked with
evidence (file + measured number + SHA where applicable). Any unchecked
box ⇒ verdict is NO. This checklist gates the generator built by the main
session; this document itself changes nothing.

## 1. Parameter lock

- [ ] Every **VERIFIED** datagen parameter locked in the generator config
      with its citation: pot intervals as printed (P1 p.25 fn.2), R(S,p)
      + hand-strength sort (P1 p.26), {F,C,P,A} datagen tree with no card
      abstraction solved to game end (P1 p.26 + P2/P1 p.8), 1,000
      iterations (P1 p.26), resolver semantics RM+/simultaneous/uniform
      skip (P1 p.22, spec S1/C4), fractions-of-pot targets (P1 pp.25-26),
      zero-sum correction EXCLUDED from targets (P2/P1 p.8, network-side),
      card-space product (bucketing training-side, P1 p.27), root actor =
      seat0 = BB (ACPC `firstPlayer 2 1 1 1`), turn samples goal (P1 p.26).
- [ ] Every **INFERRED** value explicitly listed in the generator's
      manifest with status tag: omit=500 (spec D2); pot = per-player
      committed (bets value and normalizer); pot feature = committed/20000;
      rejection sampler for 4-of-52.
- [ ] Every **UNKNOWN / PROJECT CANONICAL** choice listed in the manifest
      with status tag: THRandom draw mapping + order (board → P1 → P2 →
      pots), pot draw realization (category `random_range(0,4)` + inclusive
      integer `random_range(lo,hi)`), batch=10 shared board, f64 engine
      deviation (author f32), `[100,100)`/gap reading (spec U5), schema
      HUNL_TURN_DATASET_V1. Nothing UNKNOWN may be silently defaulted.
- [ ] Odd-split behavior = author-code randomized rounding (spec C2
      code-anchored verdict) — asserted by a unit test against the ledger
      (376 odd-split draws per range on any 4-card board).

## 2. Determinism

- [ ] RNG determinism: two fresh processes generate byte-identical output
      for every pilot shard (same derived seed) — Phase-2B pattern
      (39/39); record the combined determinism SHA.
- [ ] Draw-ledger reconciliation on instrumented pilot batches: observed
      draw counts == 4+G board, 2×(11,270 f32 + 376 u32) range, 20 pot
      per batch (SOURCE_AUDIT §3), G logged per batch (F-01).
- [ ] Thread/BLAS invariance or pinning proven (F-07; corpus item 53);
      environment recorded (python, numpy, BLAS SHA, arch).
- [ ] One fresh THRandom per shard; seeds derived
      `sha256("hunl_datagen:{master}:shard:{idx:05d}")[:4]` (or the
      generator's documented equivalent), all-unique asserted (F-08/F-15).

## 3. Serialization & provenance

- [ ] Schema versioned **HUNL_TURN_DATASET_V1** (§5) — schema_version
      field present in every manifest; any layout change bumps it.
- [ ] Per-shard JSON manifest: seed, sample_count, SHA-256 of every array
      file, engine SHA **`34a50560a30cbff156e979b59af6c00e39f7f1a9`**,
      generator SHA, config hash (canonical JSON of the live config,
      F-23), spec identifier (HUNL_RECONSTRUCTION_SPEC v2 @ `f81d08c`),
      QA stats, audited rows + result. Master manifest embeds all shards
      + merged SHAs (run_phase2b.py pattern).
- [ ] Clean-tree + pinned-SHA assert at the start of every generating
      process (F-09); atomic tmp-then-rename writes only (F-10/F-18).

## 4. Verification runs (all must be green BEFORE bulk)

- [ ] **Row-level inversion audit**: sampled rows inverted from the
      written files (board ← boards array, ranges, pot ← exact f32 cast
      chain) and fresh-resolved: target rows byte-exact (Phase-2B 220/220
      pattern; F-03/F-05/F-22).
- [ ] **Independent oracles A/B/C at minimum** green on the pilot subset
      (ORACLE_PLAN §1): A all-in ≤ ~1e−15 pot; B forced-check ≤ ~1e−15
      pot (measured 9.10e−16 on the frozen anchors); C LP ≤ 0.002 % pot
      at 1000/500 (frozen G1 anchors). E mask recounts BIT_EXACT on every
      pilot sample; F analytic zeros/bounds where constructed.
- [ ] **Statistical QA** (fail-fast, per shard + cross-shard): board
      uniformity χ² vs 270,725 4-subsets (or per-card marginals at pilot
      scale); pot histogram exactly inside the frozen intervals incl.
      negative bands 101-199 and >19950 (F-21); range sums within the f32
      stick-breaking envelope [0.999, 1.001]; blocked-zero exact (ranges,
      targets, mask — F-04); per-sample target bound |t| ≤ stack/pot_half
      (F-05); zero-sum residual distribution measured and banded (recorded
      as statistic, never corrected); duplicates = 0 over all rows incl.
      across train/valid (F-11); RNG ledger reconciles (§2).
- [ ] **Full-shard replay** byte-identical for a representative shard
      subset (≥10 % of pilot; Phase-2B: 13/110 = 11.8 %).
- [ ] **Adversarial corpus subset executed**: at least one item from each
      ORACLE_PLAN corpus family (ranges 1-15, boards 16-26, pots 27-36,
      targets 37-46, pipeline 47-56), results recorded.

## 5. Frozen-regression battery — ZERO CHANGE

- [ ] Leduc: pytest 36/36 + all 8 frozen comparators; Phase-2A pilot
      SHAs re-anchor (seed 20260812, 6/6); Phase-2B manifests untouched.
- [ ] HUNL gates: G1.1, G1.2/G1.3, ACPC tree gate, G1.7/G1.8 anchors
      byte-identical, transition gate, turn-engine gate — including the
      HUNL v1 determinism SHA
      **`c6c4eb4e9b6b78898c176c2d9e996c159f71e15d09ba4210ca5d07a9255918f7`**
      reproduced by two fresh processes.
- [ ] **No frozen RESULT file overwritten** — regenerated logs go to
      `certification/hunl_g1/latest_audit/` (established convention);
      `git status` proves frozen artifacts untouched.
- [ ] READ-ONLY repos untouched: DS repo branches `2ab6dde` /
      `7967622` unchanged.

## 6. Verdict

- [ ] All boxes above checked with evidence links. Only then write:
      **HUNL TURN DATAGEN CERTIFIED FOR BULK GENERATION: YES** (new
      result file; never edit a frozen one).

---

## 5'. Proposed serialization schema — HUNL_TURN_DATASET_V1 (design only)

Status: **PROJECT CANONICAL, explicitly NOT author-BIT_EXACT** — the
original HUNL byte layout was never released (SOURCE_AUDIT §4, "Datagen
output files": UNKNOWN forever). Design goals: flat, dtype-explicit,
mmap-able, invertible (every QA/inversion check above is O(1) per row).

Per shard, flat binary arrays (`.npy`, C-order):

| File | Shape | dtype | Contents / contract |
|---|---|---|---|
| `boards.npy` | (N, 4) | uint8 | card ids 0-51, **ascending** (canonical storage order; draw order lives only in the RNG stream — F-13) |
| `pots.npy` | (N,) | int32 | pot in chips, **per-player committed** (SOURCE_AUDIT §2.7); ∈ frozen intervals |
| `ranges.npy` | (N, 2, 1326) | float32 | player 0 = seat0 = BB = root actor, player 1 = seat1 (SOURCE_AUDIT §2.10); frozen 1326 lex hand order (`hunl/cards.py` (c0<c1) contract); exact f32 values as drawn (no renormalization) |
| `targets.npy` | (N, 2, 1326) | float32 | root CFVs / pot_half (fractions of per-player committed pot); same player/hand order as ranges; exactly 0 on blocked hands |
| `masks.npy` | (N, 1326) | uint8 | possible-hand mask for the board (1=legal); redundant with boards by construction — kept precisely so QA can cross-check (F-04) |

Per shard JSON manifest (`shard_XXXXX.json`): `schema_version:
"HUNL_TURN_DATASET_V1"`, master seed + derived shard seed + derivation
string, sample_count, per-file SHA-256, engine SHA
`34a50560a30cbff156e979b59af6c00e39f7f1a9`, generator SHA, config hash,
spec identifier (`HUNL_RECONSTRUCTION_SPEC.md` v2 @ `f81d08c`), status
tags for every INFERRED/UNKNOWN/PROJECT-CANONICAL parameter (§1), QA
stats, audited row indices + results, environment pins, generation
seconds. Master `MANIFEST.json` embeds all shard manifests + merged
concatenation SHAs in shard order (Phase-2B pattern).

Notes:
- Pot feature (pot/20000) and any bucket-space views are DERIVED at
  training time, never stored — keeps the dataset independent of U6
  (input-vector layout) and of the abstraction stage (U2/B4).
- `.npy` (not `.t7`) is deliberate: the author HUNL container is unknown
  anyway, and `.npy` removes the Torch7 writer from the trust chain; the
  certified `.t7` writer remains available if a Torch7-format export is
  ever needed for cross-checks.
- 16-byte-aligned flat arrays make the duplicate scan (F-11) and row
  hashing trivially reproducible: row hash = SHA-256 of the concatenated
  raw bytes of (board row ‖ pot ‖ range rows).
