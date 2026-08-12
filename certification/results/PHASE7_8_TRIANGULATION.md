# PHASES 7–8 — CROSS-ORACLE TRIANGULATION + SEQUENCE-FORM LP ORACLE

Scripts: `certification/scripts/kuhn_lp_triangulation.py`,
`certification/scripts/cfrplus_replica_kuhn.py`.

## Phase 6.3 completed here — KUHN CFR+ AUTHOR-SOURCE BIT EXACT: **PASS**

`cfrplus_replica_kuhn.py` is an independent Python replica of the original
Tammelin/CPRG CFR+ built from the line-level source audit (int32 regrets and
accumulated strategy, `lrint(x*16.0)` quantization, `max(R+d, 0)` clipping,
alternating updates player-index-1 first, fold/call/raise child order,
pre-order immIndex layout, inclusion-exclusion 1-card leaf evals).

Result against the compiled original binary's raw trunk checkpoints:

| iters | byte_equal (48 × int32) |
|---|---|
| 1 | **True** |
| 2 | **True** |
| 5 | **True** |
| 10 | **True** |
| 100 | **True** |
| 1000 | **True** |

`original_regrets == replica_regrets` and `original_strategy ==
replica_strategy` raw byte-for-byte at every checkpoint → **BIT_EXACT**.

## Phase 8 — sequence-form LP oracle (independent, scipy HiGHS)

- LP game value: `-0.055555555555555525`
- exact rational −1/18 = `-0.05555555555555555`
- |diff| = **2.8e-17** (≈1 ULP) → NUMERIC_MATCH against the closed-form value.

## Phase 7 — triangulation matrix (Kuhn)

| Quantity | LP oracle | Original CFR+ (decoded trunk, iter 1000) | AGT-style CFR+ (trace impl, 1000 iters) | Status |
|---|---|---|---|---|
| game value (P1, sb/hand) | −0.055555556 | bracket [−0.055703005, −0.055488303] ∋ −1/18 | −0.055555909 | CONSISTENT |
| BR value P1 | −1/18 | **−0.05548830336** (independent BR) vs binary's printed **−0.055488303** | −0.055506130 | EXACT to all printed digits |
| BR value P2 | +1/18 | **+0.05570300533** vs binary's printed **+0.055703005** | +0.055649234 | EXACT to all printed digits |
| exploitability (mSBet/h) | 0 | **0.107350982** (ours) vs **0.107350982** (binary print) | 0.071552166 | EXACT to printed precision |

Independent chain validated end-to-end: trunk int32 layout decode → integer
average normalization → independent best-response evaluator reproduces the
original binary's self-reported BR values digit-for-digit; both CFR+ variants
converge toward the LP equilibrium value; exploitability → 0.

Notes:
- The original CFR+ average strategy and the AGT-course CFR+ average strategy
  are *not* expected to be identical (different quantization — int32
  lrint×16 vs float64 —, different alternation order P2-first vs P1-first,
  different averaging weights). Kuhn equilibria form a one-parameter family;
  both converge into it. This is a legitimate two-external-references
  difference explained by documented algorithmic variant differences
  (plan §7: different update order / averaging / integer quantization).
- Leduc: original-binary oracle series frozen (Phase 6.4) with determinism
  and patched-build byte-equality proofs; a bit-exact Python replica for
  Leduc (suit isomorphism, board enumeration, 2-round hand mapping) was not
  attempted in this pass — marked NOT_TESTABLE for the "ours" side (no
  project implementation exists) with the author-side oracle fully generated.
