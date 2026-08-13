# HUNL_DATAGEN_ORACLE_PLAN — independent oracle matrix + adversarial test corpus for the HUNL turn DataGenerator

Date: 2026-08-13. Read-only parallel audit task. Companion:
`HUNL_DATAGEN_SOURCE_AUDIT.md` (algorithm + citations),
`HUNL_DATAGEN_FAILURE_MATRIX.md`, `HUNL_DATAGEN_FREEZE_CHECKLIST.md`.

Principle (inherited from the Leduc certification): every oracle below
shares **no optimized code path** with the production generator/engine and,
where possible, no solver at all. Accuracy classes: **BYTE_EXACT**
(identical bytes), **BIT_EXACT** (identical values/discrete structure),
**NUMERIC** (agreement within a stated, measured tolerance). All measured
numbers below are quoted from frozen G1 artifacts — nothing was re-run in
this task.

## 1. Oracle matrix

| # | Sample regime | Oracle | Exists? Harness pointers | Expected accuracy class | Evidence already on file |
|---|---|---|---|---|---|
| A | **All-in at the root** (both players committed = stack; no betting remains) | Solver-free exhaustive runout: u_p(h) = pot_half · (1/44) · Σ_c mask_c(h)·(M_c reach_opp^c)(h), direct enumeration of all 44 rivers per pair via G1.3 showdown matrices; independent pure-loop f64 recount | **YES** — production `hunl/turn.py::all_in_equity` (line 28) vs independent `certification/hunl_g1/turn_reference.py::reference_all_in_equity` (line 32; per-pair/per-river loops, showdown by direct evaluator rank comparison) | Discrete parts (river sets, masks, blocker counts) **BIT_EXACT**; values **NUMERIC ≈ 1e−15 of pot** (f64 summation-order only) | G1 transition gate (`43020db`): max \|prod−ref\| **1.09e−15 pot** on small-support incl. blocker-heavy; full-range zero-sum <1e−9 pot; G1_TURN_REPORT.md items 5–6 |
| B | **Forced-check** (menu emptied to check-down; equivalent to no betting) | Chance+terminal oracle: forced-check engine config must equal the class-A all-in oracle at the same pot | **YES** — `certification/hunl_g1/run_g1_turn_engine.py` forced-check anchors; oracle = `turn.py::all_in_equity` | **NUMERIC ≈ 1e−15 of pot** | HUNL_GOLDEN_BASELINE_V1 item 6: 8 forced-check full-pipeline states, **max 9.10e−16 of pot** |
| C | **Small-support ranges** (≤ ~6 hands/side) | Independent sequence-form **LP** over the FULL turn+chance+river game (chance-weighted; no CFR/engine code) + independent recursive reference solver | **YES** — `certification/hunl_g1/turn_oracles.py::solve_turn_lp` (line 30) and `TurnRecursiveCFR` reference (line 141); `turn_reference.py::reference_turn_cfvs` (line 66) | Game value **NUMERIC ≤ 0.002 % of pot** at production 1000/500; exact-BR NashConv bound | HUNL_GOLDEN_BASELINE_V1 item 7: LP anchors 0.000 % / **0.002 %** / 0.000 % pot; engine vs recursive reference **7.35e−16 pot**; convergence \|engine−LP\| = 0 chips from 250 iters (item 8) |
| D | **Normal full-range samples** | Frozen-engine replay: regenerate the identical sample from the recorded shard seed in a fresh process; compare serialized bytes | **YES** — the Phase-2B pattern: `certification/phase2b/run_phase2b.py` replay (:409-423) + per-shard audit resolves (:320-333 inversion, fresh resolve); HUNL analogue must call the frozen turn engine (`hunl/turn_engine.py`) under `HunlConfig` | **BYTE_EXACT** under the deterministic stack (x86_64, pinned BLAS; HUNL v1 determinism SHA `c6c4eb4e9b6b…`) | Phase-2B: 39/39 replay SHAs identical, 220/220 audit target rows byte-identical; HUNL_GOLDEN_BASELINE_V1 item 12: 2 fresh processes byte-identical |
| E | **Blocker-heavy states** (board pairs/suits removing large hand classes) | Combinatorial mask oracle: recount possible-hand masks, pair-exclusion counts, 44-river mutual-legality identities by direct loops (G1.2 layer) | **YES** — G1.2 certified layer (`hunl/blockers.py`, gate `740f47b`, exhaustive incl. all 2,598,960 rivers); chance identities in G1 transition gate (14,009,760 pairs × 44 mutual rivers) | **BIT_EXACT** (counting, no floats) | G1_2_3_REPORT.md; G1_TURN_REPORT.md item 4 (mass identities exact) |
| F | **Degenerate / single-hand / analytic** | Closed-form EV where derivable: (i) board plays for both (e.g. royal-flush-equivalent board where every legal holding ties) ⇒ every root CFV = 0 exactly up to the fold-branch structure — in the all-in/check-down regimes exactly **0**; (ii) nuts-vs-air: nut hand vs range with zero equity ⇒ value = +pot_half (check-down) and bounded by +stack (with betting); (iii) single-hand vs single-hand ⇒ 2×2-payoff hand calculation by hand | **PARTIAL** — class-A/B oracles already realize (i)/(ii) for no-betting regimes (`turn_reference.py` loops); with betting, analytic bounds only (LP of class C is the exact check) | (i)/(ii) no-betting: **BIT_EXACT** (exact zeros/± pot_half); with betting: bound assertions + class-C LP **NUMERIC** | G1 turn corpus includes degenerate/single/disjoint supports (HUNL_GOLDEN_BASELINE_V1 item 1); quads/straight-flush boards in corpus |

Datagen-level use: a pilot subset of every bulk run must route samples of
regimes A/B/C (constructed adversarially, below) through these oracles,
plus D on full shards and E structurally on every sample (mask QA). This
is the acceptance bar wired into `HUNL_DATAGEN_FREEZE_CHECKLIST.md`.

Position-asymmetry warning (applies to corpus items 41-44, 56): a turn
state with **identical ranges for both players is NOT value-symmetric** —
seat0 (BB) acts first postflop, and first-actor (dis)advantage makes even
symmetric-range values nonzero. Symmetry assertions are only exact for
regimes with no betting (A/B: check-down/all-in values under mirrored
ranges obey u1(h) = −u2(h) pairwise and Σ r·u = 0), or as an
*approximate* sanity band with betting. Never assert "symmetric ranges ⇒
value 0" on the full tree.

## 2. Datagen adversarial test corpus (numbered)

Each item = a concrete sample type to be constructed (board, pot, ranges),
run through the production datagen path, and checked against the named
oracle class(es). Pots are per-player-committed chips (SOURCE_AUDIT §2.7).

Range-shape family (oracle C/D; A/B variants at all-in/check-down):
1. Near-zero range mass on one hand: r1 = 1−ε on best hand, ε=1e−7 spread over rest (f32 stick-breaking floor).
2. Near-zero TOTAL mass survivor: recursive splits driving one subset's mass to f32 underflow (denormal/zero entries) — assert no NaN, blocked-zero preserved.
3. Single-hand support vs single-hand support, non-overlapping cards (oracle F(iii) + C).
4. Single-hand support vs single-hand support, card-overlapping (blocked pair) — the joint reach is impossible; assert defined, finite outputs (engine convention documented).
5. Single-hand vs full 1128-hand range (oracle C bound + A at all-in).
6. Overlapping supports: both players' support = same 4 hands sharing cards (blocker-coupled equity; oracle C + E recounts).
7. Disjoint supports: P1 top-100 strength hands, P2 bottom-100 (dominated direction check: P1 value ≥ check-down bound).
8. Dominated ranges: P2 support strictly card-dominated (every P2 hand loses every runout to every P1 hand — quads-on-board kicker construction); check-down value exactly ±pot_half (oracle F/A).
9. Uniform-over-possible ranges both sides (the "cleanest" full-range state; oracle A at all-in, D replay).
10. Author-shaped R(S,p) draw with forced extreme first break (p1 ≈ 1−2^−23): virtually all mass in the low-strength half.
11. Mirror of 10 (p1 ≈ 2^−126): mass forced into the high half; assert f32 sum still within [0.999, 1.001] envelope (Phase-2B QA bound).
12. Range with exactly one odd-split path flipped: two samples differing ONLY in one `random_range(0,1)` outcome — assert middle-hand mass moves subsets and nothing else changes (RNG ledger line-5 semantics).
13. Zero-support river branch: supports chosen so some river card kills ALL of one player's remaining hands (skip-exactly-once semantics; G1 turn report item 5 pattern).
14. Zero-support BOTH players on a river: assert branch handled without renormalization-by-zero (NaN guard).
15. Ranges concentrated on hands blocked by the TURN board (must be impossible: generator asserts blocked-zero at source; negative test — inject and expect fail-fast).

Board-structure family (oracle A/B/E; C on restricted supports):
16. Paired board (e.g. Ks Kh 7d 2c): trips/full-house showdown ordering stress.
17. Double-paired board (Ks Kh 7d 7c): boats over boats; kicker irrelevance classes.
18. Monotone board (4 same-suit cards): flush blockers dominate — E recounts of flush-hand masks.
19. Quads on board (9s 9h 9d 9c): all hands play the board quads + kicker; near-universal ties (oracle F(i) variant with kicker exceptions).
20. Straight-flush board segment (Ts Js Qs Ks): royal/straight-flush draws; As blocker singleton nuts.
21. Exact-tie board: broadway-on-board (Ts Jh Qd Kc + any river A completes for many holdings) — tie-class explosion, showdown matrix zero-diagonal blocks (E + A).
22. Wheel-steel board (As 2s 3s 4s): dual straight/flush/straight-flush classes.
23. Rainbow disconnected board (2c 7d Th Ks... 4 suits): minimal draw interaction — baseline board.
24. Board with three-to-straight-flush + pair (6h 7h 8h 8s): redraw-rich showdown table.
25. Suit-permutation invariance: same state under a global suit permutation (h↔s) — all values must permute exactly with the hand relabeling (measured 1.82e−12 in G1 turn report item 8; assert ≤1e−9 pot band, discrete structure BIT_EXACT).
26. Board-order invariance: same 4 cards presented in different input order — serialized sample must be identical after canonical ascending sort (BYTE_EXACT; FAILURE_MATRIX F-13).

Pot-boundary family (oracle A/B/C at the stated pots; D replay):
27. Pot exactly 100 (the "[100,100)" singleton category; deepest {F,C,P,A} tree — cost sentinel).
28. Pot 101 and 199 — NEVER generated per the printed intervals (negative test: assert the generator cannot emit them; presence in a shard = fail).
29. Pot 200 (lowest of interval 2) and 399/400 (upper boundary semantics: 399 in, 400 in next interval).
30. Pots 1999/2000 and 5999/6000 (remaining interval boundaries).
31. Pot 19949 and 19950 (upper end; 19950 must be reachable — closed bracket `]` in P1 fn.2).
32. Pot 19951 and 20000 — never generated (negative test); 20000 = all-in root is NOT a datagen state.
33. Pot 19950 solve: remaining stack 50 < pot-bet ⇒ menu degenerates toward {F,C,A}-like (pot-bet clamps to all-in per ACPC raise window); assert tree matches ACPC oracle exactly (G1 tree layer pattern).
34. Short-stack ladder: pots 18000, 19000, 19900 — progressive menu degeneration; monotone tree-size decrease sanity.
35. Forced all-in sample: pot such that any bet ≥ remaining stack (all-in-call path finishing WITHOUT min-raise reset — the certified ACPC "not-enough-players" branch, HUNL_GOLDEN_BASELINE_V1 item 3).
36. Forced check-down config (class B): betting disabled — must equal all_in_equity to ≤1e−15 pot (measured 9.10e−16).

Value/target-property family:
37. Target bound: every |target| ≤ stack/pot_half for its own pot (Phase-2B analogue bound; theory cap stack/min-committed = 20000/100 = 200 pot-fractions at pot 100 — assert the PER-SAMPLE bound, not a global constant; a global bound of 200 is vacuous for large pots, so QA uses per-sample stack/pot_half).
38. Zero-sum residual of stored targets: Σ r1·u1 + Σ r2·u2 measured per sample; band from pilot distribution (f32; solver-convergence dominated) — recorded, NOT corrected (SOURCE_AUDIT §2.8).
39. Blocked-zero targets: every target entry on a board-blocked hand is exactly 0 (BIT_EXACT mask check, oracle E).
40. Monotonicity spot-check: at fixed board/pot with nested supports, adding a strictly dominated hand to the opponent cannot lower the hero's root value below the class-C LP of the smaller game (weak-dominance sanity, tolerance from C).
41. Symmetric ranges, check-down: identical ranges both sides, betting off — per-hand u1(h) = −u2(h) and Σ r·u = 0 to 1e−12 pot (oracle A; position removed).
42. Symmetric ranges, FULL tree: identical ranges with betting — values need NOT vanish (first-actor asymmetry; see §1 warning). Assert only the class-C/LP cross-check and record the measured asymmetry as a corpus statistic.
43. Position swap: exchange the two range vectors; targets must equal the swapped-and-relabeled solve of the mirrored state ONLY when the actor role is also swapped — negative control for the F-02 player-swap failure mode.
44. Reflection consistency: state S=(r1,r2) and S'=(r2,r1) at all-in — u_1(S) = −u_2(S') pairwise (oracle A; exact in f64 loops).
45. Extreme skew: P1 = 0.999999 on nut hand + dust elsewhere vs P2 uniform — value ≈ +pot_half·(2·equity−1) band at check-down; with betting, ≥ check-down value − ε (fold option bound).
46. All mass on air vs all mass on nuts with betting: exploitee cannot lose more than stack; assert −stack ≤ value and LP agreement.

Pipeline/RNG family (oracle D + ledger):
47. Rejection-sampler stress: seed chosen (by search over seeds, offline) to produce ≥3 board rejections in one batch — assert downstream draws shift exactly per ledger (SOURCE_AUDIT §3 line 2) and replay is byte-identical.
48. Batch-boundary independence: samples i=9,10,11 spanning a batch boundary — board changes exactly at the boundary, pots per-sample, ranges fresh (draw-order audit).
49. Shard-boundary independence: last sample of shard k and first of shard k+1 under the per-shard seed derivation — no stream continuation across shards (FAILURE_MATRIX F-08/F-15).
50. Duplicate-seed negative test: two shards forced to the same seed must produce identical bytes (proves seed→stream determinism) AND the production seed-derivation must be shown collision-free over the shard set (Phase-2B: all 110 unique).
51. Full-shard replay: one pilot shard regenerated in two fresh processes — 3/3 files byte-identical (class D; Phase-2B pattern 39/39).
52. Row inversion audit: for sampled rows, invert the serialized files (board ← mask, ranges ← blocks, pot ← feature round-trip incl. the exact f32 cast chain) and fresh-resolve: target row byte-identical (Phase-2B 220/220 pattern).
53. Thread-count invariance: same shard generated with BLAS threads 1 vs 4 — byte-identical, else pin threads=1 (FAILURE_MATRIX F-07).
54. dtype drift probe: assert serialized arrays are exactly f32 (and uint8/int32 for cards/pots per schema); any f64 leakage into files = fail (FAILURE_MATRIX F-12).
55. Mid-shard crash + resume: kill the worker after n samples; resume must either regenerate the whole shard from seed or verify the manifest — never append (Phase-2B manifest-check pattern, run_phase2b.py:241-247; FAILURE_MATRIX F-16).
56. Golden-anchor pin: one fixed (board, pot, ranges) state stored with its full 2×1326 f64 engine output and f32 serialized row; every future engine/generator change must reproduce it byte-identically (regression tripwire, analogous to the Leduc frozen comparators).

Corpus execution policy: items 1-46 are state-level (oracle A/B/C/E/F);
items 47-56 are pipeline-level (oracle D + ledger). The freeze checklist
requires a subset covering every family before the bulk verdict.
