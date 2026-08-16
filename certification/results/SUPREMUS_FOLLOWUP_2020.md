# DeepStack follow-up / Supremus evidence — arXiv:2007.10442v1

Status: PRIMARY PAPER FOR A LATER INDEPENDENT HUNL REIMPLEMENTATION,
not original DeepStack source code.

## What this paper independently confirms about DeepStack

1. The authors built an HUNL reimplementation that "closely follows" the
   published DeepStack description and retained the same network I/O
   architecture.
2. Original DeepStack's play-time **turn** solve extended to game end and used
   a **bucketed card abstraction for all river actions**. The paper explicitly
   says the details of this bucketing were never presented. Their
   reimplementation therefore stopped at the start of river and used a river
   value network instead.
3. DeepStack/Supremus CFVnet interface: 2x1000 bucket ranges + one pot feature
   = 2001 inputs; 1000 bucket values/player = 2000 outputs; seven fully
   connected 500-unit hidden layers plus external differentiable zero-sum
   enforcement.
4. The follow-up reports that its random training subgames were generated in a
   manner identical to DeepStack. It does not publish the missing private RNG,
   tie ordering, or original bucket artifact.

## Required project interpretation

- `hunl/turn_engine.py` (full 1326-hand, no card abstraction, solve-to-end) is
  retained as the **offline target-generation / mathematical oracle** engine.
  This is consistent with the DeepStack training-target statement that the
  F/C/P/A training games were solved with no card abstraction.
- It must **not** be described as the exact original play-time turn resolver.
  The original play-time resolver had an unpublished river card abstraction.
- Exact original play-time turn reproduction therefore remains blocked by the
  missing river-bucket definition/artifact.

## Supremus improvements (separate optional lineage)

The paper deliberately changes the algorithm after reimplementing DeepStack:
- DCFR+ with delayed average-policy tracking (`d=100`) and simultaneous updates;
- 4,000 iterations per player for generated training subgames;
- a river value network and value functions at the end of every round except
  the final round;
- much more training data: 50M river, 20M turn, 5M flop, 10M auxiliary;
- a larger action abstraction;
- an end-to-end CUDA/GPU implementation.

These are **not** to be silently folded into the forensic DeepStack baseline.
They define a future `SUPREMUS_INSPIRED` performance profile after the
DeepStack reconstruction baseline is frozen.

## Performance anchors reported by the paper

DeepStack-reimplementation validation error reported in the paper is close to
or better than the original reported DeepStack values; Supremus improves the
turn/flop validation losses further. The paper also reports 1,000 flop search
iterations in 0.8 s for its custom GPU implementation, over 6x faster than the
DeepStack implementation under the compared action abstraction.

These are performance/regression targets, not bit-exact oracles.
