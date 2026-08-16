# HUNL Reconstruction Milestone — 2026-08-16

## Newly closed in this milestone

1. **HUNL value-network interface / flop→turn boundary**
   - 2001 input / 2000 output contract;
   - 7×500 PReLU architecture;
   - source-anchored zero-sum outer correction;
   - 49-turn conditional range/bucket/NN algebra;
   - exact 1/45 chance aggregation;
   - private 1000-bucket artifact remains fail-closed.

2. **Exact flop all-in forced-runout terminal**
   - C(49,2)=1176 global future-board pairs;
   - C(45,2)=990 equiprobable final boards for every fixed disjoint private
     pair;
   - exact int16 antisymmetric numerator matrix;
   - 64/64 independent direct runout recounts exact.

3. **Flop CFR lookahead structural integration**
   - exact fold and exact flop all-in terminals;
   - turn value boundary injected separately;
   - deterministic integration certificates.

4. **Turn DataGenerator source correction V2**
   - current-board hand strength replaces the legacy future-runout metric;
   - first-party `rankCardset` checked on 10,608 six-card hand slots;
   - source-explicit floor split replaces randomized odd split;
   - `[100,100)` now fails closed in AUTHOR_STRICT mode;
   - equal-strength tie ordering and private RNG remain explicitly unresolved.

## Strongest current blockers

### U1 — original HUNL 1000 strategic buckets
Missing exact feature construction/centroids/map/tie/init details.

### U2 — original HUNL turn-network weights
Missing private trained model. Reconstruction weights can later be trained,
but may not be labelled original.

### U3 — generator details not fixed by publication
- equal-strength ordering inside R(S,p);
- original RNG / seed schedule / board sampler;
- intended correction of `[100,100)`;
- exact private HUNL offline CFR target averaging implementation.

Released DeepStack-Leduc provides strong implementation anchors for several of
these concepts but is not promoted over explicit HUNL primary text.

## Rule for next work

Preserve solved raw 1326-hand ranges and 1326-hand CFV targets independently
of neural-network bucketing.  This prevents a future recovered bucket artifact
from forcing the expensive turn games to be re-solved.
