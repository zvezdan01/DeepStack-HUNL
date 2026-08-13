# HUNL GOLDEN BASELINE v1 — EXACT TURN→RIVER SOLVER CERTIFIED

Date: 2026-08-13. Result: **PASS — milestone frozen.** Foundation for the
next (separately gated) milestone: HUNL TURN DATAGENERATOR CERTIFICATION.
Builds on: v0 exact river solver `0004cf0` (frozen), transition gate
`43020db` (frozen), spec freeze `f81d08c`.

## Deliverables
- `hunl/turn_tree.py` — full turn game tree (turn betting → river chance
  → river betting → terminals) with VERIFIED Table-4 turn menus indexed
  by lookahead-global depth (first {F,C,½P,P,A}; second/remaining
  {F,C,P,A} — governing river betting inside the turn resolve, which is
  solved to the end of the game); ACPC rules via the certified river-tree
  rule mirror (composition, unchanged); ACPC-legal folds only
  (documented, value-inert deviation from the golden layered engine's
  structural fold-first convention).
- `hunl/turn_engine.py` — vectorized f64 full-game CFR: RM+ with
  [ε,999999] clamps, simultaneous updates, uniform post-omit averaging
  (1000/500 VERIFIED turn schedule), certified chance algebra (masked
  reach + single 1/44), certified G1.2/G1.3 terminal matrices, golden
  `CFRDGadget` imported unchanged for CFR-D re-solves, full average
  profile retained, exact vectorized best response.
- `certification/hunl_g1/turn_oracles.py` — independent sequence-form LP
  over the full turn game (chance-weighted, no CFR/engine code) +
  independent recursive reference solver.
- Config: Table-4 turn menus + 1000/500 added to `HunlConfig`
  (river defaults untouched — tree-gate manifests re-verified ZERO CHANGE).
- Golden path = exact river throughout: 1326 hands, full blockers, all
  legal river cards, exact river trees, exact showdown. **No bucketing,
  no NN, no suit-isomorphism reduction.** (The supplement's card-bucketed
  river inside turn re-solves — S7/U3 — remains documented in the spec as
  the author's production-efficiency variant; deliberately NOT in this
  Golden baseline.)

## Final report (17 items)
1. **Turn states:** 74 solved/certified states + 43 pots tree-replayed
   (uniform/skewed/blocker/degenerate/single/disjoint supports; paired,
   monotone, two-tone, rainbow, quads, straight-flush boards; pots
   100→19999 incl. short-stack & all-in-heavy).
2. **Turn trees/nodes:** 43 trees, **154,041 nodes**, deepest 21,831
   (pot 100); solve trees up to 6,333 nodes.
3. **ACPC comparisons:** **14,199 oracle replies identical** (8,752
   action-validity probes + state snapshots + raise windows), including
   round transition, cross-street min-raise reset (max_spent+BB) and the
   all-in-call path that finishes WITHOUT the reset (doAction
   "not-enough-players" branch); 355 chance transitions with 48-way
   river-subtree betting-identity asserted.
4. **Chance transitions:** 355 in-tree (× 48 rivers each = 17,040 river
   subgames inside solved trees).
5. **Solved infosets:** **11,602,608** (decision-node × live-hand).
6. **All-in oracle error:** forced-check full-pipeline anchors (8 states)
   vs certified solver-free all-in oracle: **max 9.10e−16 of pot**.
7. **LP/BR/NashConv:** LP cross-anchors (independent sequence-form over
   the FULL turn+chance+river game): full-Table4 **0.000 %**,
   full-Table4-blocker **0.002 %**, reduced-menu **0.000 %** of pot.
   Engine vs independent recursive reference: **7.35e−16 pot**.
   Full-schedule 1000/500 corpus NashConv (exact full-1326 BR): 0.691 %,
   0.408 %, 0.034 %, 0.000 %, 0.000 % of pot.
8. **Convergence checkpoints:** |engine−LP| @100/250/500/1000/2000 =
   2.35 → 0.000 → 0.000 → 0.000 → 0.000 chips; NashConv @250/500/1000 =
   0.204 % → 0.097 % → 0.021 % pot. Production stays 1000/500.
9. **Zero-sum residual:** ≤ **8.19e−16** of pot (invariant corpus);
   ≤ 1.73e−16 on the full-schedule corpus.
10. **CFR-D:** 3 gadget re-solves, separate: terminate values ==
    input opponent CFVs exactly (opponent-optimal semantics), ranges
    blocked-zero/finite/≤1, strategies normalized. Golden gadget class
    unchanged.
11. **Frozen regression:** ZERO CHANGE — Leduc pytest 36/36 + all 8
    comparators; G1.1; G1.2/G1.3 (incl. exhaustive river audit); ACPC
    tree; G1.7/G1.8 full corpus **anchors byte-identical**; transition
    gate full re-run. Frozen RESULT files restored (regenerated logs in
    `latest_audit/`, not overwriting frozen artifacts).
12. **Determinism SHA:**
    `c6c4eb4e9b6b78898c176c2d9e996c159f71e15d09ba4210ca5d07a9255918f7`
    (2 fresh processes byte-identical: CFVs + BR + strategy). Corpus
    anchors combined:
    `78958278e61db0f1649ef24aa0c5de2a5669294423c7f91b2d841595b6f4f8f9`.
13. **First divergence:** engine **NONE**. Two harness-side calibration
    fixes before any recorded pass: (a) all-in-call minNoLimitRaiseTo
    prediction (ACPC finishes without round-advance reset — prediction
    corrected, oracle authoritative); (b) a brittle convergence assert
    (engine had converged EXACTLY to LP from 250 iterations, making
    "min of first two" smaller than plateau noise).
14. **Classification:** **BIT_EXACT** — tree/legality vs game.c, chance/
    blocker discrete structure, terminal matrices, gadget f32 semantics,
    determinism/replay, frozen underlying gates. **NUMERIC** — the full
    turn solve (LP ≤0.002 % pot, reference 7e−16, forced-check 9e−16,
    NashConv ≤0.7 % at production schedule). **BEHAVIORAL** — none
    claimed. **NOT author-BIT_EXACT** (no original DeepStack HUNL trace
    exists; never claimed).
15. **Residual risks:** (a) full-schedule pot-100/200 deep trees not in
    the solve corpus (tree layer ACPC-certified; solve cost ~1 h/state —
    economics only); (b) engine is f64 while the author stack was f32
    Torch7 (documented; v0 river baseline remains the f32-certified
    path); (c) suit-isomorphism unused/uncertified; (d) LP anchors on
    restricted supports (full-range anchored via forced-check exact
    pipeline anchor + exact BR); (e) turn-menu depth-indexing
    ("remaining" = global lookahead depth incl. river) is the documented
    Table-4 reading — no author trace can confirm it (INFERRED
    interpretation, flagged in spec).
16. **Runtime:** gate core 60.3 min + frozen-regression battery 76 min ≈
    **2.3 h** on the 4-core container.
17. **Commit SHA:** this commit (see git).

**FROZEN:** this milestone is HUNL GOLDEN BASELINE v1. Next milestone
(NOT started): HUNL TURN DATAGENERATOR CERTIFICATION.
Raw logs: `latest_audit/G1_TURN_ENGINE_RESULT.txt`,
`latest_audit/TURN_ENGINE_REGRESSION.txt`.
