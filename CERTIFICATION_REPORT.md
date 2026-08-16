# HUHL CERTIFICATION STATUS

Date: 2026-08-12 · Branch `claude/huhl-deepstack-certification-tutg3b` ·
Baseline tag `huhl-baseline-pre-certification`

```
Existing DeepStack regression: NOT_TESTABLE_WITH_AVAILABLE_ORACLE  (repository is EMPTY — no project code exists)
CFR:                           TRACE_EXACT      (official Kuhn trace: 498/500 values exact-to-format, 500/500 within reference precision)
CFR+:                          TRACE_EXACT      (official Kuhn trace: 380/380 lines, 760/760 values exact-to-5-decimals)
Original CFR+ Kuhn:            BIT_EXACT        (independent replica vs author binary: all 6 integer checkpoints byte-equal, incl. iter 1000)
Original CFR+ Leduc:           NOT_TESTABLE_WITH_AVAILABLE_ORACLE  (author-side oracle generated+frozen; no "ours" side exists)
Best Response:                 BIT_EXACT        (AGT raw oracles 28/28 arrays byte-equal; independent BR reproduces author binary digit-for-digit)
NashConv:                      BIT_EXACT        (AGT raw oracles 14/14 arrays byte-equal)
Exploitability:                NUMERIC_MATCH    (13/14 byte-equal, worst |diff| 7.1e-15; BR-chain exploitability exact to author binary's printed precision)
CFR-D Gadget:                  NOT_TESTABLE_WITH_AVAILABLE_ORACLE  (no project code, no Lua/DeepStack oracle uploaded)
Continual Resolving:           NOT_TESTABLE_WITH_AVAILABLE_ORACLE  (no project code)
Value Network:                 NOT_TESTABLE_WITH_AVAILABLE_ORACLE  (no project code, no weights)
End-to-End HUHL:               NOT_TESTABLE_WITH_AVAILABLE_ORACLE  (no project code)

Experimental:
VR-MCCFR:                      NOT_IMPLEMENTED  (reference on file: arXiv 1809.03057 VR-MCCFR paper)
POS:                           NOT_IMPLEMENTED  (reference on file: Davis/Schmid/Bowling ICML 2020 supplement)
Predictive Baseline:           NOT_IMPLEMENTED  (reference on file: same supplement)
AIVAT:                         NOT_IMPLEMENTED  (no oracle uploaded)
DCFR:                          NOT_IMPLEMENTED
```

## THE CRITICAL FINDING

**The repository `zvezdan01/quant-trade` was completely empty at certification
start** — zero commits, zero remote refs, no working tree. There is no HUHL
solver, no CFR loop, no gadget, no training pipeline, no weights, no configs,
no seeds, and no pre-existing test suite ("480/480 tensors exact",
F1/F2/F5 fixes, prior reconstruction fixes: **none of these exist here**).
See `certification/BASELINE.md`. Every plan item that tests "our current
implementation" against an oracle is therefore NOT_TESTABLE: the object
under test is absent. What this certification did instead: **built, froze
and cross-validated the complete reference-oracle infrastructure** so that a
future HUHL implementation can be certified against immutable, hashed,
determinism-proven oracles — and proved the method works by writing
independent certification implementations and driving them to BIT_EXACT /
TRACE_EXACT against the author references.

## 1. Total tests executed

| Suite | Count | Result |
|---|---|---|
| AGT raw .npz oracle harness (their pytest, weeks 1–6) | 256 tests | **256 PASS** |
| — stored oracle arrays, raw byte-level | 515 arrays | 437 byte-equal, 78 numeric-only (≤1.1e-9, LP-solver dependent) |
| game_theory_2023 course tests (hand-computed oracles) | 3 tests | **3 PASS** |
| Original CFR+ RNG oracle (4 seeds × 4 lengths) | 16 comparisons | **16 BIT_EXACT** |
| Original CFR+ Kuhn checkpoints vs Python replica | 6 checkpoints | **6 byte-equal (BIT_EXACT)** |
| Original CFR+ Leduc: untouched-source vs patched build | 6 checkpoints | 6 byte-equal |
| Original CFR+ determinism re-runs (Kuhn + Leduc, iter 1000) | 2 | identical SHA-256 |
| Official Kuhn CFR trace | 250 lines / 500 values | 247 / 498 exact-to-format; 500/500 within format precision |
| Official Kuhn CFR+ trace | 380 lines / 760 values | **all exact** |
| Sequence-form LP oracle vs closed form −1/18 | 1 | |diff| = 2.8e-17 |
| Triangulation: independent BR vs author binary print | 4 values | exact to all printed digits |

Aggregate: **275 discrete tests / 2000+ compared values, 0 FAIL.**
No test was inherited from history — everything above was executed fresh in
this session.

## 2–6. Classification lists

**BIT_EXACT** (raw bytes / integers identical):
- Original CFR+ `rng.c` (MT19937) vs independent Python MT19937 — 16/16 streams.
- Original CFR+ Kuhn solve: int32 regrets + int32 accumulated strategy at
  iterations 1, 2, 5, 10, 100, 1000 — replica vs compiled author binary,
  48 int32 per checkpoint, byte-for-byte (`KUHN CFR+ AUTHOR-SOURCE BIT
  EXACT: PASS`).
- AGT raw oracles: best response (28/28), strictly-dominated actions (28/28),
  iterated removal (56/56), NashConv (14/14), plus 311 further arrays across
  evaluate/verify_support/support_enumeration/CE/regret families.

**TRACE_EXACT** (matches published formatted reference exactly at its precision):
- Official Kuhn CFR+ trace: 380/380 lines, 760/760 values (5 decimals).
- Official Kuhn CFR trace: 498/500 values exact-to-format (2 artifacts below
  print precision, documented in FIRST_DIVERGENCE.md); 500/500 within 1e-5.
- AGT fictitious-play (42/42) and regret-minimization (57/57) snapshots
  (stored rounded to 8 dp by the harness — classified TRACE per plan rule,
  not raw bit-exact).

**NUMERIC_MATCH**:
- Sequence-form LP Kuhn game value vs −1/18: 2.8e-17.
- AGT evaluate/deltas/exploitability last-bit stragglers (≤1.4e-14, FP
  association order).
- LP-solver-dependent AGT families (verify_support, support_enumeration,
  find_nash_equilibrium, correlated equilibrium, double_oracle): worst
  1.1e-9 — "NUMERIC_EQUIVALENT — solver dependent" per plan §3.2/3.4.

**BEHAVIORAL_MATCH**:
- Original CFR+ Kuhn/Leduc exploitability decay (0.107 / 0.551 mSBet/h at
  iter 1000), BR values bracketing known game values (−1/18; ≈−0.0856).
- AGT-style CFR+ convergence (0.0716 mSBet/h @ 1000 iters, value −0.0555559).

## 7. First divergence of each FAIL

**No FAIL occurred.** The only divergences anywhere are the two sub-precision
artifacts in the Kuhn CFR trace (a −7e-18 negative-zero print and one exact
.xxxxx5 rounding tie) — full §28-style analysis in `FIRST_DIVERGENCE.md`.

## 8. Parts still without an external oracle

- HUHL/DeepStack production stack itself (absent) — everything in Phases 1,
  2, 9–15, 24–26.
- CFR-D gadget & continual resolving: no Lua/DeepStack oracle was uploaded.
- Leduc CFR+ "ours" side (author-side oracle IS frozen and ready).
- AIVAT: no reference implementation/oracle on file (paper values only).
- VR-MCCFR/POS/predictive baseline: papers on file, no author code/data.

## 9. Recommendation on training final weights

**HUHL baseline is NOT certified for training final weights — the baseline
does not exist in this repository.** Before any training:
1. Locate/push the actual HUHL project code (it was never pushed to this
   repo, or the wrong repository was attached to this session).
2. Run it against the frozen oracles in this branch, in the plan's priority
   order (the infrastructure is ready: Phase 6 checkpoints + SHA-256,
   RNG oracle, trace reproducers, LP oracle, AGT harness).
3. Only after Phases 1–14 pass on the real code should dataset generation
   and training proceed.

## 10. Engine changes

**No mathematical engine was modified** — none exists. The immutable
references in `third_party/` were not altered (the one-line memset overflow
fix needed to satisfy modern glibc fortification lives in a clearly separated
patched *copy*, `certification/scripts/CFR_plus_patched/`, and is proven
byte-neutral on all Leduc checkpoints; the oracle binary of record is
compiled from untouched source with fortification disabled).

---

## Oracle inventory (immutable, SHA-256 in `certification/oracles/SHA256SUMS`)

| Oracle | Location | Proven properties |
|---|---|---|
| Original CFR+ source | `third_party/CFR_plus/` | audited (dtypes, lrint, scaling, ordering — `certification/results/PHASE6_ORIGINAL_CFRPLUS.md`) |
| Kuhn CFR+ integer checkpoints ×6 | `certification/oracles/cfrplus_runs/kuhn_i*/` | deterministic, replica-bit-exact |
| Leduc CFR+ integer checkpoints ×6 | `certification/oracles/cfrplus_runs/leduc_i*/` | deterministic, patched-build byte-equal |
| MT19937 RNG streams ×16 | `certification/oracles/rng/` | bit-exact vs independent implementation |
| AGT .npz raw oracles (515 arrays) | `third_party/agt_tests/` | 437 byte-reproduced |
| Official Kuhn CFR/CFR+ traces | `third_party/agt_tests/ref_cfr*.txt` | fully decoded & reproduced |
| Uploaded archives (4) + papers (2) | hashes in `certification/BASELINE.md` + below | frozen |

`1809.03057v1.pdf` (VR-MCCFR): SHA-256
`a3b07d9b15a99be0612e7f3df7db9e0357fed4abbf9ddcc80f6f76f3fb4361f2`.

Per-phase detail: `certification/results/PHASE3_AGT_RAW_ORACLES.md`,
`PHASE4_5_KUHN_TRACES.md`, `PHASE6_ORIGINAL_CFRPLUS.md`,
`PHASE7_8_TRIANGULATION.md`; environment freeze in `certification/BASELINE.md`.

---

# 2026-08-16 Addendum — HUNL reconstruction now present

The historical report above predates the later HUNL reconstruction work and
its statement that the HUNL implementation is absent is no longer current.
The preserved original report is not rewritten; this addendum records the
newer certified state.

Current HUNL layers include certified cards/evaluator/blockers/showdown,
river, turn→river, sparse preflop/flop betting, flop→turn chance algebra,
and a structural flop lookahead.  See:

- `certification/hunl_early/HUNL_EARLY_STREET_PHASE1.md`
- `certification/hunl_value/HUNL_VALUE_NETWORK_PHASE2.md`
- `certification/hunl_value/HUNL_FLOP_LOOKAHEAD_PHASE3.md`
- `certification/hunl_datagen_v2/HUNL_DATAGEN_SOURCE_CORRECTION_V2.md`

The exact private HUNL 1000-bucket artifact and original trained HUNL network
weights remain unresolved.  The value-network path fails closed instead of
inventing them.

A source audit of the turn generator also corrected the future work path:
new data must not be produced from the legacy V1 pilot sampler.  V2 follows
the HUNL supplement's current-public-state hand-strength definition and
`floor(|S|/2)` recursion, while explicitly recording unresolved equal-strength
tie ordering, private RNG, the `[100,100)` pot anomaly, and exact HUNL offline
CFR averaging implementation.

## 2026-08-16 — Schmid testimony + Supremus follow-up evidence
- Offline HUNL target generation used a skip/burn-in window: **AUTHOR-CONFIRMED
  recollection (Martin Schmid)**. Exact count remains unpublished; `500` stays
  RELEASED-CODE-ANCHORED to DeepStack-Leduc.
- Original DeepStack play-time turn solving used an unpublished river card
  abstraction. Full-card `hunl.turn_engine.TurnEngine` is therefore frozen as
  **DATAGEN / mathematical oracle**, not labeled original online-turn code.
- `hunl.turn_play_contract` now fails closed unless an explicit original-river
  bucket provider is supplied.
- Supremus/DCFR+ improvements are recorded separately and are not mixed into
  the forensic DeepStack baseline.
