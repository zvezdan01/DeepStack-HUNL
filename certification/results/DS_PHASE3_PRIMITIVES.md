# DS PHASE 3 — CFR/CFR+ PRIMITIVE LAYER vs FROZEN TAMMELIN ORACLES

## Applicability finding

The DeepStack-Leduc engine defines only the extended-Leduc game (ante 100,
stack 1200, pot-fraction bets); it contains no Kuhn game and cannot consume
ACPC `kuhn.game`/`leduc.game` definitions. Its CFR variant (float32, epsilon
regret floor 1e-9…, skip-iteration averaging, CFR-D gadget) is a **different
algorithm family** from Tammelin's int32 lrint-quantized CFR+, so a direct
bit comparison between the two engines is mathematically undefined — this is
a "different dtype/scaling/update order" case under the plan's rule 7, not a
FAIL.

The primitive layer is therefore certified by triangulated pairs, each
against its own author-side oracle:

| Pair | Result |
|---|---|
| Tammelin CFR+ (Kuhn) vs independent replica | **BIT_EXACT** — 6/6 integer checkpoints (quant-trade Phase 6.3) |
| Tammelin CFR+ (Leduc, suit isomorphism, 2 rounds) vs independent replica | **BIT_EXACT** — 6/6 integer checkpoints (this run; `cfrplus_replica_leduc.py`, structural tables dumped by the original C itself) |
| MT19937 RNG (rng.c) vs independent implementation | **BIT_EXACT** — 16/16 streams |
| Official course CFR/CFR+ Kuhn traces vs independent implementation | **TRACE_EXACT** — 760/760 (CFR+), 498/500 exact-to-format (CFR, 2 sub-precision artifacts) |
| DeepStack-Leduc CFR core vs its own Lua/Torch7 author reference | **BIT_EXACT** — 232/232 one-iteration tensors + stage-level street-2 exhaustive (see DS_PHASE6) |
| All CFR+ variants + LP oracle | game values consistent (quant-trade Phase 7/8 triangulation) |

Note on the Leduc replica first-run FAIL (documented per freeze-first rule):
the initial run reported divergence at iteration 2 (int32[42], avg strategy).
Frozen and analyzed before any change: the replica's math was correct — the
test *driver* restarted the iteration counter between incremental checkpoint
runs, resetting the linear averaging weight (w = t·16) to t=1. A fresh
2-iteration run showed 0/2268 diffs. Driver fixed (persistent iteration
counter); engine untouched; all 6 checkpoints then byte-equal. This was a
divergence in new certification tooling, not in any engine under test.
