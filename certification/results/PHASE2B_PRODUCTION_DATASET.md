# PHASE 2B — PRODUCTION TRAINING DATASET: GENERATION REPORT & CERTIFICATION

Date: 2026-08-13. Verdict: **DATASET CERTIFIED FOR TRAINING: YES**
(training itself NOT started, per instruction).

## Provenance pins (verified at start of every generating process)

| Item | Value |
|---|---|
| Engine (Golden Baseline v1.0, READ-ONLY) | `2ab6dde943ebad2f5458779dc561ed203f796e39` |
| Datagen (certified generator, READ-ONLY) | `7967622e5b66e35a8e9a17506f97db86c2e6b543` (verified = DS HEAD, clean tree, parent = engine) |
| Weights `final_cpu.model` (loaded, byte-verified; street-2 resolves never evaluate it) | `d5fcba4402cec46a9b02cea0f96cb78bda83f284ea36f6d5db84529e83eb59a1` |
| Config hash (canonical JSON: seeds, derivation, shard plan, Config(), bounds) | `f0315183c58640812df4cc8560088183b50f7d1abb4544cbdcd71c7defc05c77` |
| Environment | Python 3.11.15, NumPy 2.4.6, bundled OpenBLAS (BIT_EXACT_BACKEND), x86_64 |
| Orchestrator | `certification/phase2b/run_phase2b.py` (no math — certified API only) |
| Oracle truth | released-Lua-equivalent Certified Golden Baseline (D2-proven). The historical 200 TrainSamples were NOT used as target truth. |

## Dataset

- **Total samples: 110,000** — **train 100,000 / valid 10,000** (ratio 10:1)
- **110 shards** × 1,000 samples: shards 00000–00009 = valid, 00010–00109 = train
- **Size: 79.8 MB** (330 Torch7-format `.t7` files: per shard `.inputs`
  (1000×73 f32), `.targets` (1000×72 f32), `.mask` (1000×36 f32))
- Location: `certification/phase2b/shards/` + per-shard JSON manifests +
  master `certification/phase2b/MANIFEST.json`

## Seeding (requirement 1)

- Master seed **20260813** (explicit).
- Per-shard seed = first 4 bytes (big-endian u32) of
  `SHA-256("phase2b:20260813:shard:{idx:05d}")`; all 110 unique (verified).
- Each shard is one independent certified THRandom stream through the
  certified `generate_data_file` (batch size 10, valid/train assignment by
  shard index). Deviation from the original single-stream valid-then-train
  order is deliberate (resumability + parallelism), documented, and
  distribution-preserving — every batch consumes the identical certified
  draw pattern (1 board + 84 range + 10 pot u32 draws).

## Per-shard manifests (requirement 2)

Each `shard_XXXXX.json` records: seed, sample count, SHA-256 of
inputs/targets/mask, config hash, engine SHA, datagen SHA, weights SHA,
QA stats, audited row indices + result, generation seconds. The master
`MANIFEST.json` embeds all 110 plus the aggregate QA and virtual merged
SHAs (concatenation in shard order, for the training consumer):

```
merged valid.inputs   6931f8a481637fe7dc03ebcdff0f908ab9c1665d128246475e558049055a0c01
merged valid.targets  e4a4f1cb3fc82893590fdec1a55c8ac80de610e8451d963c35eccb2e92df50e2
merged valid.mask     84f27a22db969675435849e66420dd52c1918578652e259f51311fa1ee852f11
merged train.inputs   da175b806a5fdde912e718818c1495c38ecee718ccd0fc998653859cd75cbe64
merged train.targets  8dfead54145de5c3151571e40db001decba1e34ba1c000ec11ebdbb12bc60777
merged train.mask     0fd9dc53dd37039202ddcb2285c15a8bda4f57f27fabea48d510546338927439
```

## Runtime / throughput

- Generation: **2.27 h wall** on 4 workers, **8.90 core-hours**;
  per shard min/mean/max = 275/291/316 s → **0.29 s/sample/core**,
  ≈ 13.5 samples/s aggregate. Final QA ≈ 4 min; replay ≈ 25 min (4 procs).

## Failed / retried samples (requirement 3)

- **0 failed, 0 retried, 0 dropped.** No retry logic exists in the runner;
  every anomaly is a fail-fast abort. The only rejection loop anywhere is
  the board sampler inside the certified generator (part of the original
  algorithm; its draws are part of the certified stream). No fail-fast ever
  triggered; `FREEZE_DIVERGENCE.json` was never written.

## QA results (requirements 4, 6)

Per-shard (all 110 pass, enforced fail-fast): finite values everywhere;
mask rows each equal one of the 6 legal board masks; board constant within
each generation batch of 10; range blocks non-negative, zero on impossible
buckets, per-row sums within f32 stick-breaking envelope (0.999, 1.001);
pot features inside the exact f32-chain bounds of the certified pipeline;
targets zero on impossible buckets; |target| ≤ 12.5 bound.

Cross-shard (master QA):

| Check | Result |
|---|---|
| Board counts (χ², df 5, crit@0.001 = 20.5) | [18600, 18210, 18100, 17820, 18530, 18740], **χ² = 3.32** — PASS |
| Pot distribution | min 100.019, max 1199.896, mean **649.68** (expected 649.95) — PASS |
| Duplicate/collision check (SHA-256 of every input row, 110,000 rows) | **0 duplicates** — PASS |
| Target magnitude | max abs **10.6536** (bound 12.5; theory cap stack/min-pot = 12) — PASS |
| Mask coverage | all 6 boards present; every mask row a legal board mask — PASS |
| Certified-pilot re-anchor | pilot seed 20260812 regenerated in this run: **6/6 SHA-256 identical** to Phase-2A certified appendix — PASS |
| Distribution drift vs pilot (nonzero-target quantiles P1–P99) | pilot [-0.999, -0.981, -0.644, 0.018, 0.719, 1.354, 2.280] vs bulk [-0.997, -0.968, -0.609, 0.000, 0.703, 1.388, 2.213] — consistent (pilot n=14.4k values vs bulk sample n=936k) — PASS |

Certified sampling distributions, 1000/500 CFR schedule, f32 dtypes,
`mul(1/pot)` normalization and Torch7 serialization are inherited by
construction: the runner calls only the certified `generate_data_file` /
`resolve_targets` with the default certified `Config()`.

## Determinism verification (requirements 7, 8)

- **Audit resolves (every shard):** 2 rows per shard selected by a
  deterministic audit RNG (outside the certified stream), inverted from the
  *written files* (board ← mask, ranges ← bucket blocks, pot ← feature
  round-trip) and re-resolved fresh through the certified path:
  **220/220 full 72-value target rows byte-identical.**
- **Independent replay:** 13 representative shards (00000, 00009 valid;
  00010, 00020, …, 00100, 00109 train = 13,000 samples, 11.8 % of the
  dataset) regenerated from the same seeds in 4 fresh processes:
  **39/39 file SHA-256 identical** to the shard manifests.

## Residual risks (explicit)

1. **Sampled, not exhaustive, determinism audit:** 220 rows fresh-resolved +
   13/110 shards (11.8 %) fully regenerated. The remaining shards are
   covered by the same code path, per-shard QA, and manifest SHAs, but were
   not re-resolved twice. (Exhaustive replay would double compute; can be
   run later from the manifests without touching the data.)
2. **Environment-pinned reproducibility:** byte-reproducibility is
   certified for this stack (x86_64, bundled OpenBLAS `cd143947…`,
   Python 3.11.15, NumPy 2.4.6). On other stacks the Golden Baseline rider
   (non-x86_64 fallback) applies.
3. **Sharded seeding deviates from the original single-stream order**
   (documented above; per-batch draw pattern and distributions identical;
   affects only which concrete samples are drawn, which is what a new
   seeded dataset is by definition).
4. **Golden Baseline rider items unchanged** (M3 P2-street-2 oracle hole;
   RNG action-sampling path — not exercised by data generation; Torch7
   runtime items closed by the D2 experiment).
5. **Historical 200 TrainSamples remain a mixed oracle** (D2 PROVEN
   pre-release provenance) — intentionally not used as truth for this
   dataset (requirement 9).

## Verdict

All requirements 1–9 satisfied; zero unexplained anomalies; determinism
demonstrated at three levels (per-shard audit resolves, independent
replay, pilot re-anchor).

**DATASET CERTIFIED FOR TRAINING: YES.**
Training awaits explicit owner instruction.
