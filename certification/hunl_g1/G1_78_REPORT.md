# Gates G1.7 + G1.8 — parameterized golden CFR core + exact HUNL river resolver

Date: 2026-08-13. Result: **PASS.** Spec anchor `f81d08c`; builds on
G1.1 `23f783f`, G1.2/G1.3 `740f47b`, tree layer `29832ad`.

## Architecture (no new CFR code)
The solver is the **untouched certified Golden Baseline engine**
(`deepstack_leduc.lookahead.Lookahead` + `cfrd_gadget.CFRDGadget` — both
fully `Config.card_count`-parameterized in the certified source). New
modules only inject the HUNL game layer through documented seams:
- `hunl/river_terminal.py` — terminal-equity object from G1.3/G1.2
  certified matrices in the Leduc orientation convention (call =
  showdown-matrix transpose; fold = legal-pairs mask), byte-verified.
- `hunl/river_resolver.py` — Config(card_count=1326, stack=20000,
  cfr_iters=2000, cfr_skip_iters=1000); lookahead tree = G1-certified
  ACPC river tree converted to golden Nodes with the **author lookahead
  convention** (fold child first at every decision node — Lua
  tree_builder behavior, consistent with Table 4 listing F everywhere;
  non-fold action sets are the ACPC-certified ones, unchanged);
  `InjectedLookahead` replicates two golden orchestration bodies verbatim
  with pluggable terminal-equity factory and gadget board-mask.
Preserved exactly (by running the certified code): RM+, simultaneous
updates, cumulative-regret semantics with [ε, 999999] clamps,
positive-regret strategies, uniform post-omit averaging, CFV propagation,
CFR-D gadget with opponent-optimal constraint values, all certified
f32/dtype semantics.

## 1. Leduc regression (ZERO numerical change)
| Check | Result |
|---|---|
| DS pytest suite (incl. one-iteration & continual/street-2 trace corpora, NN boundary, end-to-end bitmatch) | **36/36 passed** |
| compare_private_boards_480 | **480/480 BIT-EXACT** |
| compare_continual_first_action | 6/6 BIT-EXACT |
| compare_nn_root_trace / compare_nn_boxes | BIT-EXACT |
| compare_root_cfv_both_players (L2) | BIT-EXACT |
| determinism_check / m2_activation_probe / regen_tree_manifest | PASS / clamp never active / PASS |
| **Wrapper equivalence on Leduc** (InjectedLookahead + Leduc components vs golden engine) | **40 plain + 10 gadget resolves BYTE-IDENTICAL** (strategy, achieved/children/both-players CFVs) |

**Golden modules modified: 0.** New game-independent modules: 2
(`river_terminal.py`, `river_resolver.py`) + harness + LP oracle.

## 2. CFR-D gadget @ 1326 (separate)
Two RM+ gadget iterations replicated by hand in exact f32 —
**byte-identical output**; blocked hands never resurrected; terminate
values = input opponent CFVs (opponent-optimal constraint semantics per
thesis ch. 6 / cfrd_gadget.lua); play-probability monotonicity sane.

## 3. HUNL river corpus (plain resolves)
**28 states** — 10 boards (rainbow, monotone, paired, quads-on-board,
board-straight, straight-flush board, broadway, …) × pots
{100, 2000, 9900, 19999} × ranges {uniform, skewed, near-degenerate
(3-hand), blocker-heavy, all-in-heavy trees at 19999}. Full VERIFIED
schedule 2000/1000, RM+/simultaneous/uniform-post-omit, exact
unabstracted 1326-hand ranges, no buckets/NN/approximation.
- **2,084 lookahead-tree nodes; 761,024 solved (decision-node × live-hand)
  infosets**; exact terminal comparisons inherited from G1.3 layer
  (~7.0e9 certified entries) + byte-verified matrix contract in-context.
- Invariants all green: finite everywhere; strategy normalized per live
  hand (max |Σ−1| < 1e−3, f32); blocked hands zero in ranges; **max root
  zero-sum residual |r1·u1 + r2·u2| = 4.69e−06 of pot**.
- Analytic: royal-flush-on-board (premise all-tie verified from certified
  ranks) → game value **+0.00 chips**.

## 4. Independent validation
**LP cross-oracle** (independent sequence-form LP, scipy/HiGHS, no CFR,
no golden code; restricted supports K∈{6,10} incl. blocker-heavy):
**8/8 within 0.5 % pot — worst 0.088 %, best exact to 3 decimals:**
```
AsKh7c4d2s 2000 K6 : |d| 0.131 chips (0.003%)   AsKh7c4d2s 9900 K10: 4.471 (0.023%)
KsQsJs9s2s 2000 K10b: 3.515 (0.088%)            KsQsJs9s2s 9900 K6 : 9.004 (0.045%)
5h6h7h8h9h 2000 K6b : 0.002 (0.000%)            5h6h7h8h9h 9900 K10: 0.003 (0.000%)
AcAdAh2c2d 2000 K10 : 2.833 (0.071%)            TsJsQdKcAh 9900 K6 : 0.000 (0.000%)
```
**Convergence checkpoints** (|engine−LP| chips at 250/500/1000/2000/4000
iters): `13.77 → 10.48 → 2.33 → 0.47 → 0.55` and
`1.65 → 1.82 → 0.19 → 0.17 → 0.28` — converging as required.
**Tammelin CFR+ cross-anchor:** fixed-board river subgames are NOT
representable as ACPC `.game` definitions (games start pre-flop; blinds
cannot encode river-entry min-raise state) — documented as
representation-incompatible; the CFR core remains Tammelin-anchored via
the Phase-6 Kuhn/Leduc byte-exact replicas, and the LP oracle provides
the independent anchor for this game. **Exact BR/NashConv via LP** covers
the BR cross-check on restricted supports.

## 5. Gadget river resolves (separate corpus)
8 CFR-D re-solves (constraints from prior plain solves): opponent ranges
blocked-zero and finite, strategies normalized, all invariants green —
reported separately from plain resolves as required.

## 6. Determinism
4 corpus states × 2 fresh processes → **byte-identical** strategy+CFVs.
Combined corpus anchor (28 plain + 8 gadget SHAs):
`5a354ebe97f1405fb40741c9dc2ec7d3f1ba55f5f711f49cbcfd7947b3b2b05f`
(per-state SHAs in `G1_78_ANCHORS.txt`).

## 7. Classification (exact)
- **BIT_EXACT:** all reused Leduc CFR primitives (regression + 50-resolve
  byte-equivalence), gadget f32 semantics @1326, blocker/evaluator/
  showdown layers (G1.1–G1.3), betting legality (tree layer vs game.c),
  terminal matrix construction, determinism/replay of our own outputs.
- **NUMERIC:** the full HUNL river resolve as a whole (LP anchors ≤0.09 %
  pot; convergence verified). No original DeepStack HUNL trace exists for
  any river state — full-resolve BIT_EXACT against the author is
  impossible in principle and is NOT claimed.
- **BEHAVIORAL:** none needed at this gate.

## 8. First divergence
Engine: **NONE.** One harness-side error caught and fixed before any
pass was recorded (a hand-analysis mistake in the all-tie sanity board:
quads-on-board is NOT universally tying — ace-kicker hands win; replaced
with royal-on-board and the premise is now verified from certified ranks
instead of assumed).

## 9. Runtime
35.5 min total single run (regression 6.5 min; corpus 14 min; LP+
convergence 6 min; gadget corpus 7 min; determinism 2.5 min) on the
4-core container.

## 10. Residual risks
1. Full-resolve fidelity is NUMERIC by nature (no author traces) — the
   LP anchor covers restricted supports; full-1326 anchoring rests on
   component BIT_EXACTness + zero-sum/convergence/determinism evidence.
2. The author fold-first lookahead convention at check-able nodes is an
   architectural inference from the Lua tree builder + Table 4 (F in all
   menus); CFR gives such folds ~0 mass (verified), so value impact is
   nil, but the convention itself has no dedicated author trace.
3. LP oracle scales only to restricted supports; full-1326 exact BR
   remains future work (cheap to add: direct argmax walk — planned with
   the continual-resolving gate).
4. f32 zero-sum residual envelope (≤5e−6 pot) measured, not proven.

Frozen artifacts untouched (DS repo clean; golden `2ab6dde`, datagen
`7967622`, Phase-2B, spec `f81d08c`, prior G1 commits). Turn/flop/
bucketing/NN/training/DataGeneration NOT started.
Raw log: `G1_78_RESULT.txt`; anchors: `G1_78_ANCHORS.txt`.
