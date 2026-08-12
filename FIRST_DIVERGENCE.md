# FIRST DIVERGENCE REPORT

**No test in this certification FAILED.** This report documents, in the
plan's §28 format, the only two divergences observed anywhere — both in the
official Kuhn CFR trace reproduction, both *below the reference's printed
precision*, and neither classified as FAIL.

## Divergence 1 — negative-zero print

1. **Reference source:** `third_party/agt_tests/ref_cfr_kuhn.txt`
   (AGT course official Kuhn vanilla-CFR trace, 5-decimal text format)
2. **Test name:** Phase 4 trace reproduction
   (`certification/scripts/kuhn_cfr_trace.py`)
3. **Seed:** none (deterministic full-traversal CFR)
4. **Iteration:** 3 (also identical artifact at iterations 4 and one later line)
5. **Player:** P2
6. **Infoset:** `('', 'Q', 'Check')`
7. **Action:** Check (cumulative regret)
8. **Expected value:** printed `0.00000`
9. **Actual value:** printed `-0.00000`
10. **Raw bytes:** ours = `-6.938893903907228e-18`
    (IEEE-754 `0xBC80000000000000`, hex float `-0x1.0p-57`);
    reference raw double unknown (only formatted text exists) but is
    ≥ 0 and < 5e-6
11. **ULP difference:** not computable against a text reference; distance
    from exact 0 is 1 × 2⁻⁵⁷
12. **Upstream values immediately before divergence:** cumulative regret
    after iter 2 = `-0.041666666666666664`; iteration-3 delta =
    `+0.041666666666666657...` (differs in last bit from the stored
    magnitude) → residue −2⁻⁵⁷ instead of exact 0
13. **Probable cause:** floating-point summation association order inside
    the unpublished reference solution differs from ours; exact math value
    is 0
14. **Proposed minimal fix:** none proposed — algorithmic equivalence is
    established (all 500 values agree within the reference's 1e-5 print
    precision); do not tune production FP ordering to chase a 2⁻⁵⁷ residue.
    Three alternative association orders were tested (per-deal accumulation,
    per-infoset aggregation, cf-value-difference form); the residue's sign
    is not controllable without the reference's source.

## Divergence 2 — rounding-tie boundary

1. **Reference source:** `ref_cfr_kuhn.txt` line 177
2. **Test name:** Phase 4 trace reproduction
3. **Seed:** none
4. **Iteration:** 8
5. **Player:** P1
6. **Infoset:** `('J', '')`
7. **Action:** Bet / Check (average strategy)
8. **Expected:** `0.23437` / `0.76563`
9. **Actual:** `0.23438` / `0.76562`
10. **Raw bytes:** our average ratio is exactly the dyadic rational
    15/64 = 0.234375 (`0x3FCE000000000000`); Python's correct
    round-half-to-even prints `0.23438`. The reference double sits a
    fraction below the tie (prints `0.23437`).
11. **ULP difference:** ≈1 ULP at the 5th decimal; ≤2⁻⁵² relative at
    double level
12. **Upstream:** cumulative strategy mass Bet = 15, total = 64 in our
    accumulation order (exact); reference accumulated the same quantities
    in a different order, landing epsilon under 0.234375
13. **Probable cause:** identical to Divergence 1 — FP association order
14. **Proposed minimal fix:** none — sub-print-precision artifact.

Both divergences are documented in `certification/results/PHASE4_5_KUHN_TRACES.md`.
The CFR+ trace (stricter test: alternating updates, clipping, weighted
averaging) reproduces **exactly, 760/760 values**, and the original author
CFR+ binary is reproduced **bit-exactly** at integer-state level, so these
two artifacts carry no algorithmic information.
