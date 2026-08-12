# PHASE-2 SOURCE-FAITHFUL DATA-GENERATION PIPELINE — PLAN

Basis: complete line-level map of the original Lua pipeline
(`Source/DataGeneration/*`, `Source/Training/*`) — full specification with
file:line citations archived from the mapping pass; key facts below.
`cfr.py`/`evaluate.py` are **quarantined** (audit M1/L8) and appear nowhere
in this plan.

## What the original actually does (verified spec, abbreviated)

- Entry `main_data_generation.lua:7` → `generate_data(train=100, valid=100)`;
  valid generated FIRST, then train — two independent pools, no split.
- Per batch of `gen_batch_size=10` samples (one board per batch):
  1. board: one `torch.random(1,6)` (global Torch7 MT, unseeded!);
  2. ranges per player: recursive stick-breaking over strength-sorted
     possible hands (`range_generator.lua:18-42`): `torch.rand(batch)` per
     internal node, `torch.random(0,1)` per odd split, left-first DFS;
     f32 mass arithmetic; un-sort via gather + maskedCopy; board card = 0;
  3. pots: `100 + U[0,1)·1099.9` f32 (`torch.rand(10,1)`), pot feature =
     `pot·f32(1/1200)`, and the solver pot is **recomputed from the f32
     feature** (`pot_feature·1200` in double, cast back to f32 — a
     round-trip the port must reproduce, `data_generation.lua:84,105`);
  4. targets: per sample a fresh `Resolving():resolve_first_node` on
     street-2 node {board, P1, bets=(pot,pot)}, cfr_iters=1000/skip=500,
     read `get_root_cfv_both_players()` (P1 row first), divide by the
     per-player pot commitment (chips), bucketize to 36-bucket blocks;
  5. serialize `{valid|train}.{inputs(100×73), targets(100×72), mask(100×36)}`
     as Torch7 f32 — layout `[P1 buckets | P2 buckets | pot]`.
- Bundled TrainSamples provably came from the standard variant, not
  `data_generation_call` (pot column spans [0.0886, 0.9994] = ante/stack
  scaling; |targets| up to 8.4 ⇒ solver CFVs, not call equity). The
  doc-comments claiming otherwise are stale.
- Bundled `final_cpu.model` was trained by an **earlier code version** on a
  much larger non-bundled dataset (info: epoch 9849, no `gpu` field) —
  the bundled 100+100 samples are a format specimen, not the training set.
- RNG: everything draws from the **unseeded global Torch7 MT19937**
  (board, range recursion, pots, weight init, epoch shuffle). The original
  dataset is therefore unrecoverable bit-for-bit — only the deterministic
  tail (bucketing → resolve → normalization → serialization) is exactly
  reproducible.
- Quirks that MUST be replicated, not fixed: the masked-Huber
  `loss_multiplier = 72/62` (mask-polarity bug, constant factor,
  `masked_huber_loss.lua:57-66`); in-place masking that mutates loaded
  targets; pot f32/double round-trip; `torch7` sort tie-breaking in the
  strength ordering; left-first recursion RNG call order.

## Port plan (ordered, each step gated by its own oracle)

**Step 0 — freeze the spec** (done): the mapping above + Golden Baseline
`2ab6dde` as the only allowed resolver.

**Step 1 — THRandom-exact RNG layer** (new module `datagen/th_random.py`):
MT19937 with Torch7 semantics — `rand` (uniform double → f32 store),
`random(a,b)` (modulo mapping), `randperm` (Torch7 swap order), explicit
seed. Oracle: byte streams vs a tiny C harness compiled from Torch7's
`THRandom.c` (same pattern as the certified Tammelin `rng.c` oracle — we
already have the method and toolchain).

**Step 2 — samplers**: `random_card_generator` (rejection loop),
`RangeGenerator` (sort/reverse-order incl. tie behavior, stick-breaking with
exact call order, gather/maskedCopy), pot sampler (incl. the f32 round-trip).
Oracle: (a) RNG-stream accounting tests (exact draw counts per batch);
(b) distributional tests (range-mass simplex uniformity per sorted axis,
pot uniformity); (c) fixed-seed self-reproducibility, two processes.

**Step 3 — deterministic target path** (already-certified components only:
`Bucketer`/`BucketConversion`, `card_tools`, `Resolving.resolve_first_node`,
`get_root_cfv_both_players` — L2 comparator now exists and passes).
**Strongest oracle, already available:** every bundled TrainSamples row is
invertible (board ← mask block, card ranges ← input bucket blocks — lossless
since bucketing is a permutation-scatter of the 5 possible cards, pot ←
feature·1200). Re-run the resolver on all 200 bundled rows and demand the
recomputed, pot-normalized, bucketized CFVs equal the stored `.targets`
**bit-for-bit**. This certifies the entire deterministic generator tail
end-to-end against author-produced data, with zero RNG dependence.

**Step 4 — assembly + serialization**: `generate_data_file` batch layout,
valid-then-train order, Torch7 f32 writer (round-trip oracle over the six
bundled files byte-for-byte).

**Step 5 — training loop** (only after generator certified): DataStream
(per-epoch `randperm`, batch views), MaskedHuberLoss replicated bug-for-bug
(72/62 multiplier, in-place masking), Adam lr=0.001 defaults, checkpoint
`epoch_N_cpu.model` naming. Oracles: loss-plumbing check = forward
`final_cpu.model` over bundled `valid.inputs` and compare the masked-Huber
value against an independent hand computation; fixed-seed training
self-reproducibility; **never** expect to reproduce `final_cpu.info`'s
0.00034992 (different data, different era of the code).

**Step 6 — scale-up runs**: new datasets under NEW file names
(`Data/TrainSamples/PotBet-v2/...`), seeds recorded in the run manifest,
SHA-256 per file; `final_cpu.model` never overwritten (A/B anchor).

## Certification plan for the new generator (summary)

| Layer | Oracle | Class |
|---|---|---|
| THRandom port | C harness byte streams (seeded) | BIT_EXACT |
| Samplers | draw-count accounting + distribution tests + fixed-seed replay | BEHAVIORAL + deterministic replay |
| Target path | inversion of 200 bundled rows → resolve → compare `.targets` | **BIT_EXACT vs author data** |
| Serialization | byte round-trip of 6 bundled files | BIT_EXACT |
| Loss/training plumbing | masked-Huber vs hand computation on bundled valid set; fixed-seed replay | NUMERIC + replay |
| Full runs | per-file SHA-256 manifest, seed ledger | reproducibility |

Non-closable by construction: bit-reproduction of the ORIGINAL bundled
sample draws and of `final_cpu.model` training (unseeded global RNG,
lost dataset) — recorded as an oracle limitation alongside M3/RNG.
