# V251 MAC ADDENDUM — V253 Source-Precedence + Omission-Sensitivity Rules

This addendum is MANDATORY and supersedes any conflicting wording in the original V251 task.

## 1. Do not change the Table-S4 total iteration counts

For reproducing Table S4:

- sparse rows: **1000 total CFR iterations**
- FULL ground truth: **4000 total CFR iterations**

Do **not** replace sparse=1000 by the production DeepStack river count of 2000.

The production river protocol is a different source fact:

- production river: 2000 total / omit 1000

That protocol is relevant to historical DeepStack play, not to the Table-S4 ablation totals.

## 2. Treat omission counts as an uncertainty, not a locked Table-S4 fact

The Table-S4 caption gives the 1000 sparse and 4000 FULL totals, but does not explicitly state the
omitted-iteration counts.

Therefore:

- sparse skip=500 is a current hypothesis;
- FULL skip=2000 is a current hypothesis.

Do not hard-code the final analysis so that only those suffix averages can be recovered.

## 3. Required instrumentation change

For every `(state, menu)`, preserve enough iteration information to recompute CFV averages for multiple
omission hypotheses **without re-solving**.

Preferred implementation, in order:

### Option A — raw retained per-iteration first-layer tensors

Save per iteration after each value pass:

`opp_action_cfvs_by_iter[t, action, hand]`

for all iterations.

If memory is too large, use Option B.

### Option B — prefix cumulative sums at declared checkpoints

Save cumulative first-layer opponent-CFV sums at least at:

Sparse 1000 run:
- t=0
- 100
- 250
- 400
- 500
- 600
- 750
- 900
- 1000

FULL 4000 run:
- t=0
- 500
- 1000
- 1500
- 2000
- 2500
- 3000
- 3500
- 4000

This must allow suffix means such as:

- sparse omit 0 / 250 / 500 / 750
- FULL omit 0 / 1000 / 2000 / 3000

without rerunning CFR.

### Option C — if neither A nor B is feasible

At minimum save parallel accumulators for:

Sparse:
- omit 0
- omit 250
- omit 500
- omit 750

FULL:
- omit 0
- omit 1000
- omit 2000
- omit 3000

Do not silently fall back to a single 500/2000 accumulator.

## 4. Mandatory omission-sensitivity analysis

For the TRUE root/parent opponent-CFV candidate, compute the paper crossing fingerprint for at least:

Sparse skip candidates:
`0, 250, 500, 750`

crossed with FULL skip candidates:
`0, 1000, 2000, 3000`

where feasible from the saved accumulators.

That gives up to 16 omission-pair analyses.

For each pair report:

- mean L1/L2/Linf for P
- mean L1/L2/Linf for 1/2P+P
- mean L1/L2/Linf for P+2P
- mean L1/L2/Linf for triple
- crossings
- paper edge match count 0..3

Output:

`out/v251_omission_sensitivity.json`

Schema:

```json
{
  "analyses": [
    {
      "sparse_skip": 500,
      "full_skip": 2000,
      "crossings": ["...", "...", "..."],
      "paper_edge_matches": 0,
      "mean_norms": {}
    }
  ],
  "best_match": {},
  "nominal_500_2000": {}
}
```

## 5. Interpretation rule

If a different omission pair improves the crossing fingerprint, do NOT call it recovered historical
semantics.

Report only:

`Table-S4 results are omission-sensitive under the current solver path.`

The historical omitted-iteration count remains unresolved unless primary evidence is found.

If the fingerprint is stable across all tested omission pairs, that is stronger evidence that omission
policy is not the main source of the V95/V251 mismatch.

## 6. Preserve Algorithm-S1 collection parity

Instrumentation must not move the collection point.

Continue to collect child opponent CFVs:

- after the recursive value pass;
- before the simultaneous regret update;
- with acting-player reach already multiplied by current strategy.

Do not renormalize the acting player's range inside `VALUES`.

## 7. Do not confuse three distinct protocols

Keep these labels separate in every log:

`PRODUCTION_RIVER`
- 2000 total / 1000 omitted

`TABLE_S4_SPARSE`
- 1000 total
- omission unresolved

`TABLE_S4_FULL_GROUND_TRUTH`
- 4000 total
- omission unresolved

## 8. New tests that must pass

Add tests for:

1. all declared cumulative checkpoints exist;
2. suffix mean reconstructed from cumulative sums equals direct accumulator on a small test run;
3. changing skip changes only averaging window, never regrets/strategies during solve;
4. nominal 500/2000 result is still reproducible;
5. omission-sensitivity JSON covers every feasible declared skip pair;
6. source manifest labels omission counts as hypotheses, not primary facts.

## 9. Final Mac report addition

In the final response to Adam include:

- nominal 500/2000 crossing result;
- best crossing result over omission sensitivity scan;
- whether crossing fingerprint is stable or omission-sensitive;
- explicit sentence:
  `1000 sparse / 4000 FULL totals are source-locked; S4 omission counts are not.`

Do not make any stronger claim.
