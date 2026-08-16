# The Supremus line moved out of this repository

Date: 2026-08-16 · New repository: `zvezdan01/Supremus` (private)

## Why

This repository is a **forensic reconstruction of the original 2017 DeepStack**.
Its value is evidentiary: every parameter is traced to a primary source, and any
deviation from the published method counts as a defect.

Supremus (Zarick, Pellegrino, Brown, Banister, arXiv:2007.10442) reimplements
DeepStack and then *deliberately changes the algorithm* — DCFR+ with delayed
average weighting `max(0, t-100)`, a river value network, 4,000 iterations per
player, a larger action abstraction, far more training data. Those changes are
improvements to be measured, not defects to be corrected.

Keeping both in one history would let Supremus choices leak into the forensic
baseline. `CERTIFICATION_REPORT.md` already recorded the rule — *"Supremus/DCFR+
improvements are recorded separately and are not mixed into the forensic
DeepStack baseline"* — and this is that separation made physical.

## What moved

Extracted byte-for-byte at commit `7161f7c4` (engine lineage HUNL Golden
Baseline v1, `34a50560`):

- `hunl/supremus_config.py` — Table-2 action abstraction, explicit chip quantization
- `hunl/river_dcfr_plus.py` — DCFR+ river solver with Numba backend
- `hunl_datagen/river_datagen_v1.py` — Supremus river training-sample generator
- `certification/hunl_river_datagen/` — V1 certificate, LP anchor, 4,000-iteration anchor
- `certification/hunl_river_value/` — 1000-bucket projection and CFVnet V1 (from
  the later `huhlgoldencorerivercfvnetv6` upload, which never landed here)

The Supremus repository also carries a **frozen read-only copy** of the certified
core it depends on (cards, evaluator, blockers, showdown, chance, tree,
turn_tree, river terminals, river_resolver, turn_engine, and the
DeepStack-identical subgame generation). Those files keep their original paths
and bytes; `PROVENANCE.md` there records the SHA-256 of each one, so the copies
stay verifiable against the originals here.

`hunl/turn_engine.py` is the one deliberate borrow: the paper states Supremus
generated its random training subgames "in a manner identical to DeepStack", so
the DeepStack-faithful generator is a *dependency* of Supremus datagen, not a
contamination of it.

## What deliberately stayed

`FORENSICS/` (author testimony, CPRG lineage, AIVAT, evidence tables), the
`hunl_g1` DeepStack certification gates, the AGT/Kuhn/CFR+ oracle
infrastructure, `third_party/CFR_plus`, the turn datagen pilot shards, and
`CERTIFICATION_REPORT.md`. These are evidence about the original DeepStack and
have no bearing on the Supremus line.

## Nothing was lost here

The `huhlgoldencorerivercfvnetv6` snapshot was checked field by field against
this repository. The only DeepStack-side file it touched was
`certification/hunl_river_datagen/HUNL_RIVER_DATAGEN_V1_CERT.json`, and the sole
difference there was wall-clock timing (`seconds`), with every mathematical
field — target hashes, LP anchor gap, zero-sum residuals — identical. The entire
substantive delta of v6 was Supremus-line and is committed there.
