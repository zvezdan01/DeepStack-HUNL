# PHASES 4–5 — OFFICIAL KUHN CFR / CFR+ TRACES

Reference: `third_party/agt_tests/ref_cfr_kuhn.txt` (250 lines, 10 iterations,
500 printed values) and `ref_cfr_plus_kuhn.txt` (380 lines, 10 iterations ×
2 half-updates, 760 printed values). These are formatted text references
(5 decimals) — per plan rules the result is a TRACE claim, **not** an
author-raw-bit claim.

"Ours": `certification/scripts/kuhn_cfr_trace.py` — certification reference
implementation written for this audit (no production HUHL solver exists in
the repository). Compares current strategy, average strategy, cumulative
regrets and utility for every infoset, action and iteration, formatted to
exactly the reference precision. Our produced traces are stored at
`certification/results/trace_cfr_kuhn_ours.txt` / `trace_cfr_plus_kuhn_ours.txt`.

## Phase 5 result — CFR+

**CFR+ official trace: 380 / 380 lines and 760 / 760 values
exact-to-5-decimal-reference.  CFR+ OFFICIAL TRACE CERTIFIED (TRACE_EXACT).**

Verified properties (all required by plan §5):
- alternating updates, P1 half then P2 half, separately checked per half;
- CFR+ clipping `R+_{t+1}(I,a) = max(0, R+_t(I,a) + r_t(I,a))` applied to the
  cumulative regret **after** summing the half-update's regret across all
  deals (clip-per-deal provably diverges from the reference at
  Iter 1/P1/('Q','','Check','Bet')/Fold: 0.04167 vs 0.00000);
- iteration-weighted average strategy. Exact scheme decoded from the trace
  and verified over all 760 values:
  * the average is seeded with the **uniform strategy accumulated
    reach-weighted with weight 1** (uniform realization plan — deep infosets
    start at 0.25/action, roots at 0.5/action);
  * player p's current strategy is accumulated (reach-weighted, once per
    infoset) at the start of the half-update **following p's own regret
    update**, with p's accumulation counter as weight (2, 3, 4, ...);
  * printed utility is the expected value of the resulting average profile.

## Phase 4 result — CFR

**CFR official trace: 247 / 250 lines exact-to-reference-format;
498 / 500 values exact at 5-decimal reference precision; 500 / 500 values
agree within 1e-5 (the reference's printed precision).**

Simultaneous updates; regrets aggregated across deals per iteration before
adding to the cumulative table; reach-weighted average, weight 1/iteration.

First divergence (plan §28-style detail):
1. reference: `ref_cfr_kuhn.txt` line 72 (Iter 3)
2. infoset P2 ('', 'Q', 'Check'), action Check, cumulative regret
3. expected (printed) `0.00000`, ours prints `-0.00000`
4. our raw value: `-6.938893903907228e-18` (hex `-0x1.0p-57`); exact math
   value is 0; the sign of a 2^-57 summation residue differs from the
   reference's (unknown) inner summation order. |diff| ≤ 1.4e-17.
5. second (and last) divergence: line 177 (Iter 8, P1 ('J',''), avg
   strategy): ours `0.23438` (cum ratio lands exactly on dyadic 15/64 =
   0.234375, ties-to-even → 8), reference `0.23437` (their double a
   fraction below the tie). |diff| at double level ≲ 1 ULP of the 5th
   decimal.
6. probable cause for both: floating-point association order inside the
   (unpublished) reference solution; not an algorithmic divergence. No fix
   proposed — algorithm verified equivalent at reference precision.
7. Alternative association orders tested (per-deal vs per-infoset regret
   aggregation, cf-value-difference form, per-infoset average accumulation):
   artifacts persist in all natural orders; the remaining freedom is
   sub-print-precision.

Classification: **TRACE_EXACT** (CFR+ strictly; CFR trace-exact at value
level with 2 sub-precision formatting boundary artifacts, both documented
above). Neither is claimed as author raw-bit exact — the references are
formatted text.
