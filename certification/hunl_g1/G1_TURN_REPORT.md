# Gate G1 turn→river transition layer — certification report

Date: 2026-08-13. Result: **PASS.** Builds on HUNL Golden Baseline v0
(`0004cf0`, frozen). No bucketing, NN, training, bulk datagen, flop or
preflop work.

## Deliverables
- `hunl/chance.py` — chance-weight algebra, fully documented per
  operation (numerator/denominator/conditioning/blocker correction/
  normalization/dtype): public prior 1/48 vs **hand-conditional chance
  1/44** (= 52−4−2−2, the game-tree factor; generalization of the Leduc
  `possible_mask/4` and `1/(board_count−2)` author construction) vs
  masked counterfactual-reach propagation (never renormalized) vs
  normalized-conditional helper — never silently interchanged.
- `hunl/turn.py` — production layer: exact all-in runout equity
  (vectorized over G1.3 matrices) and `TurnTransition.turn_cfvs` (per
  river: frozen certified river resolver on masked reach vectors; single
  ×1/44 at aggregation; f64 aggregation, frozen f32 resolver contract).
- `certification/hunl_g1/turn_reference.py` — independent float64
  reference sharing no optimized code (pure per-pair/per-river loops;
  showdown by direct evaluator rank comparison; explicit per-hand
  aggregation loops around the frozen solver).

## Results (per requested items)
1. **Turn boards/states tested:** 270,725 (full turn-board space sweep)
   + 12 representative boards deep + 13 resolve/transition states =
   **270,735+ states** total.
2. **River transitions:** 960 executed through the full resolver path
   (48 per transition state × 20 state-runs incl. reference re-runs);
   12,994,800 board→river links covered structurally (270,725 × 48).
3. **Blocker/chance comparisons:** **21,306,192** (pair-count matrices,
   mask BIT-EXACT cross-path checks, loop recounts).
4. **Probability-mass identities:** **14,009,760 legal pairs — every one
   has exactly 44 mutual rivers** (⇒ Σ P(c|h1,h2)=1 exactly); overlap
   pairs 45, diagonal 46 (structure verified); per-hand legal-river
   count 46 on all 1128 legal hands; bijection cross-foot
   48×1081 == 1128×46 == 51,888 on every board incl. the FULL space;
   reach-mass accounting Σ_c mass_p^c == 46×mass_p exactly.
5. **Full-range vs reduced-support:** all-in — 3 small-support states
   (incl. blocker-heavy) max |prod−ref| **1.09e−15 pot**; full-range
   zero-sum <1e−9 pot + 12 per-hand loop recounts vs full opponent
   range. Transition — 3 small-support states (uniform/blocker/
   degenerate-disjoint) max |prod−ref| **4.55e−15 pot** with per-river
   masks BIT-EXACT between code paths; 2 full-range states (finite,
   blocked-zero, zero-sum <2e−3 pot at 200/100 iters, zero-support
   river skipped exactly once where constructed).
6. **All-in equity oracle:** production vs pure-loop f64 reference
   agrees to 1e−15 pot (no CFR involved — direct exhaustive card
   enumeration), the strongest transition-algebra evidence.
7. **BR/LP:** full-1326 BR audit (item 11 addendum on the frozen river
   baseline): independent f64 solver value vs frozen engine
   **0.003 % / 0.001 % pot**; full-1326 NashConv of audit profile
   **0.517 % / 0.123 % pot** at 1000/500. (River LP anchors from G1.8
   re-confirmed in the regression battery.) No solver change made.
8. **Suit isomorphism:** NO reduction used in the Golden path (full card
   space). Verification-only: h↔s permutation preserves multiplicities,
   blocker counts, chance counts exactly; all-in equities permute to
   1.82e−12; documented as not-certified-for-use.
9. **Zero-sum residuals:** all-in <1e−9 pot; transitions <2e−3 pot
   (200/100 iters — dominated by CFR convergence, not the transition);
   board-permutation of full transition **BYTE-EXACT**.
10. **Frozen regressions (ZERO CHANGE):** Leduc pytest 36/36 + all 8
    frozen comparators (480/480 etc.) green; G1.1 full space PASS;
    G1.2/G1.3 (incl. exhaustive 2,598,960-river audit) PASS; ACPC tree
    exhaustive PASS; **G1.7/G1.8 full corpus re-run — regenerated
    anchors byte-identical to the committed frozen version.**
11. **Determinism SHA:**
    `4c26a18f04d73e50c76a1a76976693b67c1c4795bf688a200f37ccd83bbd4fda`
    (all-in + transition, 2 fresh processes byte-identical).
12. **First divergence:** engine **NONE**. One harness-side comparison
    error caught before any pass (reference fills support entries only;
    production correctly computes full counterfactual vectors — 
    comparison domain fixed to the reference's support; single-pair
    values agreed to 3e−13 throughout).
13. **Classification:** BIT_EXACT — all discrete structure (river
    enumeration, masks cross-path, blocker/chance counts, mass
    identities, board-permutation byte-equality, determinism), and the
    frozen underlying layers. NUMERIC — all-in equity vs reference
    (f64 ordering, ≤1e−15 pot), transition aggregation vs reference
    (≤4.5e−15 pot), CFV convergence-level residuals, BR/value
    cross-checks. BEHAVIORAL — none claimed. **The full turn system is
    NOT author-BIT_EXACT** (no original DeepStack HUNL traces exist).
14. **Residual risks:** (a) full-range transition zero-sum measured at
    reduced iteration counts (production full-schedule 2000/1000 runs
    ≈40 min/state — economics, not correctness; small-support full
    fidelity shown at 500/250); (b) suit-isomorphic reduction remains
    uncertified and unused; (c) transition reference shares the frozen
    river solver by design (the solver itself is the certified
    component; transition algebra is what the reference independently
    checks — the all-in oracle is fully solver-free); (d) f64 1/44 is a
    rounded constant (non-dyadic) — identical in both paths, error
    ~1e−17/river.
15. **Runtime:** turn gate core 34.8 min; frozen-regression battery
    ~64 min; total ≈ 99 min on the 4-core container.
16. Commit: see repository (this file committed with the gate).

Frozen artifacts untouched: Leduc Golden `2ab6dde`, datagen `7967622`,
Phase-2B, spec `f81d08c`, G1 commits (`23f783f`, `740f47b`, `29832ad`,
`0004cf0`). Raw logs: `G1_TURN_RESULT.txt`, `G1_TURN_REGRESSION.txt`.
