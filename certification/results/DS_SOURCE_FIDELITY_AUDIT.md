# SOURCE-FIDELITY AUDIT — deepstack_leduc_v1.1-bitexact-certified @ eb7b21d

Purpose: find components where results are BIT_EXACT on available oracles but
implementation structure could behave differently from the original
Lua/Torch7 DeepStack-Leduc in a future, not-yet-exercised state. No engine
code was modified; every finding is documentation-only. Method: four
independent paired line-level audit passes over ~4,500 lines
(lookahead+builder; resolving+continual+gadget+ACPC; NN boundary;
game layer+config), followed by lead-auditor re-verification of every
MATERIAL claim directly in source (and numerically where applicable:
999999-cap sites, pot-feature 1-ulp table, mock-default inversion,
NN layer re-run 11/11 bit-exact during audit).

## VERDICT

**Not clean SOURCE-FAITHFUL.** The certified runtime resolve path
(builder → lookahead CFR loop → gadget → NN boundary → terminals →
continual invariants) is line-faithful, dtype-faithful (including the subtle
Torch7 dual-sum semantics: float32 accumulation for dim-1 sums, double
accreal for last-dim sums) and fully oracle-backed **within the certified
envelope** — but the audit identified the following places with a real
possibility of future divergence vs the original DeepStack:

### MATERIAL — disposition after owner decision (2026-08-12)

M2 and M4 were fixed source-faithfully in DS-repo commit `2ab6dde`
(branch `golden-baseline-v1.0-m2m4`) and the full certification matrix was
re-run at zero tolerance — see DS_RECERT_POST_PATCH.md. M3 is reclassified
as an explicit **residual oracle limitation** (not a verified BIT_EXACT, not
a known divergence): the P2 street-2 continual path has no original Torch7
trace and none can be generated without a Torch7 runtime. M1 remains open by
design — `cfr.py` stays quarantined from Phase-2 data generation; the
source-faithful DataGeneration plan is in PHASE2_DATAGEN_PLAN.md.


**M1 — `cfr.py` (TreeCFR utility): zero oracle coverage + not dtype-faithful.**
`cfr.py:7-74` vs `Source/Tree/tree_cfr.lua:18-199`. Algorithm structurally
matches, but runs float64 against Lua's all-float32 pipeline, and
`cfr.py:68` clamps averaging-weight contributions in (0, 1e-9) that
`tree_cfr.lua:171` leaves untouched (reachable: reach probs < 1e-9). Only a
4-iteration finiteness smoke test exists. **A Phase-2 data generator built
on cfr.py would not reproduce Lua-generated data bit-for-bit.** The
certified runtime never calls it.

**M2 — Missing 999999 upper regret cap (`tools:max_number()`), 3 sites.**
Lua: `lookahead.lua:91` (positive regrets, clamp(ε, 999999)),
`lookahead.lua:381` (cumulative regrets, clamp(0, 999999)),
`cfrd_gadget.lua:76-77` (gadget regrets). Python: `lookahead.py:127`
(float32-max), `lookahead.py:278` (no upper bound), `cfrd_gadget.py:54-55`
(no upper bound). Per-iteration regret increment is bounded by ~2·pot ≤ 2400
⇒ 1000 iterations can theoretically reach 2.4e6 > 999999, so the Lua
saturation is a reachable regime. Bit-exactness of every certified
1000-iteration run proves it never bound in any tested configuration —
"different code with an unverified regime". The only genuine behavioral
divergence found in the core lookahead files.

**M3 — P2-position street-2 continuation exercised by no oracle.**
`continual_resolving.py:73-82` → `get_chance_action_cfv`
(`lookahead.py:317-340`) with a P2-rooted resolving → P2 street-2 resolve.
Every continual street-2 trace (6/6, 480, 3720, e2e) is P1-position; the 744
set covers P2 only on street 1. Mitigation already in evidence: the
*internal* P2 no-swap branch of the next-street box path IS certified
through the 744 endpoints, and the code is position-agnostic; but the
specific P2 chance-CFV query + street-2 resolve combination is formally
unverified despite being routine in play. Closable only with a Torch7
runtime (new Lua export) or a weaker symmetry test.

**M4 — `MockNNTerminal` default inversion + float64.**
`lookahead.py:36` defaults `value_network=None` → `MockNNTerminal()`
(float64, numpy matmul, zero oracle coverage), whereas Lua defaults to the
**real** net (`lookahead_builder.lua:35` `neural_net or ValueNn()`).
The certified runtime always passes the real net explicitly (`agent.py`),
but any future caller of `Resolving(cfg)` without a net silently gets
non-faithful float64 values where Lua would load `final_cpu.model`.

### LOW (documented, inert or provably equivalent today)

- **L1** `_sample_bet` (`continual_resolving.py:108-131`): PCG64 vs Torch7
  MT `torch.uniform`, float64 cumsum vs float32, silent clamp-to-last-action
  where Lua errors. Realized action draws can never match Lua; the sampled
  *distribution* is bit-certified. Already excluded from certified scope.
- **L2** `get_root_cfv_both_players` (`resolving.py:69-72`): trivial row
  swap of a certified tensor, but no oracle calls it — and it is exactly the
  API a data generator consumes. Add a comparator before Phase 2 uses it.
- **L3** ACPC parser (`acpc.py`): deliberate rewrite (forward commitment
  replay vs Lua last-two-actions+seat-swap). Case-analysis equivalent on all
  reachable state classes; only 3 matchstates under bit-exact oracle.
  Closable by enumerating all legal Leduc ACPC strings.
- **L4** Pot feature formula: `pot/stack` (`next_round_value.py:104`) vs Lua
  `pot×(1/stack)` (`next_round_value.lua:135`) — measured 1-ulp difference
  for pots {500,700,1000,...} which are unreachable in this config;
  bit-equal on the entire reachable pot set {100,300,900,1200}. Becomes
  material only if ante/stack/bet fractions change.
- **L5** `BetSizing` `seen` dedup (`tree.py:54-58`): no Lua counterpart;
  divergent only for duplicate/colliding `bet_fractions`; inert for `(1.0,)`.
- **L6** Hardcodes exact-for-Leduc-only: `tree.py:108` `/4.0` (Lua
  `1/(card_count−2)`), `cards.py` rank multipliers 3/9, `streets_count`
  implicit. Silently wrong for extended variants; correct for this game.
- **L7** Dropped Lua asserts (input `is_valid_range` `resolving.lua:60`;
  `bet_sizing.lua:32`; assert-vs-ValueError refusal paths) — behavioral only,
  never value-bearing.
- **L8** `evaluate.py` (StrategyEvaluator): dead code, float64, zero
  coverage, no BR support — certify or remove before anyone builds on it.
- **L9** `cards.py:normalize_range` — unused float64 duplicate of the
  certified `card_tools.normalize_range`; a foot-gun for future callers.
- **L10** `torch7_blas.py:55-56` numpy fallback: intentionally
  non-bit-exact, never certified (all certified runs used the bundled
  sgemm); flagged via `BIT_EXACT_BACKEND`.
- **L11** Training-side modules (`masked_huber.py` f32 multiplier vs Lua
  double, PyTorch smooth-l1 reduction ≠ THNN; `bucketing.BucketConversion`
  float64) — formula-tested only, no Lua trace, not in any inference path.
  **Relevant to Phase 2 training fidelity.**
- **L12** Street-1 per-stage internals are certified only through
  1000-iteration bit-exact endpoints (per-stage traces are street-2 only);
  an internal divergence surviving 1000 float32 iterations bit-exactly is
  implausible but not logically excluded.
- **L13** `DeepStackValueNet.forward` (PyTorch path, tolerance-only):
  verified absent from every runtime path; material only if wired in later.
- **L14** NaN fallback rows in average-strategy normalization: textually
  identical to Lua and IEEE-deterministic; never numerically triggered on
  either side — provably equivalent, listed for completeness.

### Positive findings (verified equivalences worth recording)
- Torch7 `torch.sum` dual semantics correctly reproduced (float32 dim-1
  sums at `lookahead.py:129/230/245`; double-accreal last-dim sums at
  `lookahead.py:305-310`, `card_tools.py:110-125`, zero-sum correction in
  `value_model.py:57-61`) — all pinned by bit-exact oracles.
- The shared `regrets_sum` buffer rank-resize dance (`torch.sum` output
  resizing) is reproduced exactly (`lookahead.py:132/231/246`).
- `starting_cfvs_p1` provenance identical: computed at construction by a
  full 1000-iteration resolve, both sides; no hidden constants.
- Card indexing: uniform Lua-1-based ↔ Python-0-based shift verified at
  every boundary (boards, chance children, board_index, evaluator rank+1).
- Zero-mass range normalization (`==0→1` substitution) elementwise-identical
  → no NaN path divergence.
- Fold/call matrices, pot scaling, evaluator 1-based-rank arithmetic:
  certified per board including both fold directions and all-in pots.

Full per-component tables from the four audit passes are archived in the
audit transcripts; the material rows are reproduced above with exact
file:line references on both sides.

## Consequences for Phase 2 (dataset generation + new weights)

1. **Do not generate training data with `cfr.py` or `evaluate.py`** (M1,
   L8). Generate via the certified `Resolving`/lookahead path, or first
   build a differential oracle for TreeCFR.
2. **Always pass the real value network explicitly** (M4); never rely on
   the default. Assert `torch7_blas.BIT_EXACT_BACKEND` at generator start
   (L10).
3. The Lua data-generation stack (`Source/DataGeneration/*`,
   `Source/Training/*`) **has no Python port at all** — a Phase-2 generator
   is new code and needs its own certification plan (range_generator RNG
   will never be Lua-seed-compatible, per L1-class limitation; use
   distributional validation + fixed-seed reproducibility instead).
4. `get_root_cfv_both_players` needs a one-case comparator before use (L2).
5. Any config change (ante/stack/fractions) leaves the certified envelope
   (L4, L5, L6) and voids bit-exact claims until traces are regenerated.
6. M2/M3 remain open watch-items on the runtime itself; a Torch7 runtime
   (or a maintainer with one) is the only way to close them bit-exactly.
