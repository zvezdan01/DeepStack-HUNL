# HUNL Turn DataGenerator — Source Correction V2

## Why this correction exists

The historical project pilot is preserved for reproducibility, but it mixed
some released-Leduc reconstruction choices into the HUNL generator.  Re-reading
the recovered original DeepStack v1/v2/v3 TeX shows that two of those choices
must not be treated as HUNL-source semantics.

This V2 work does **not** regenerate the expensive solved dataset.  It first
freezes the state/range-generation contract so that future compute is not spent
on a source-inconsistent sampler.

## Primary HUNL statements

The recovered DeepStack supplement states that a training situation is defined
by pot size, both player ranges, and public cards; targets are CFVs as fractions
of pot.  For turn training it states:

- 10,000,000 random turn situations;
- 1,000 iterations of CFR+;
- action set fold / call / pot-sized bet / all-in;
- no card abstraction;
- 6,144 CPU cores and over 175 core-years;
- ranges generated recursively by `R(S,p)`;
- at every non-leaf recursion `|S1| = floor(|S|/2)`;
- hand strength = probability that a hand beats a uniformly selected random
  hand from the **current public state**.

All v1/v2/v3 supplement sources retain the same anomalous first pot interval
`[100,100)`.

## Correction 1 — hand-strength metric

The legacy V1 pilot sorted hands using future-runout all-in equity on the turn.
That is no longer used for new work.

V2 implements the literal current-public-state definition:

1. evaluate each legal 2-private + 4-public six-card holding with the certified
   ACPC `rankCardset` semantics;
2. for a fixed private hand, enumerate the 1,035 legal disjoint opponent hands;
3. hand strength is `strict_wins / 1035`; ties are not wins.

A new first-party C harness calls the untouched author `rankCardset` on six-card
holdings.  Across 8 deterministic turn boards:

- 10,608 hand slots checked;
- Python evaluator vs author C: 0 mismatches.

For board `(5,22,34,39)`, 64 independent hand-strength recounts match exactly.

Most importantly, the old and new sorting metrics are **not** monotone
equivalents on that board: there are 58,714 pairwise ordering-sign differences.
Therefore retaining the old metric would materially change `R(S,p)`.

## Correction 2 — recursive split

The HUNL supplement explicitly says:

`|S1| = floor(|S|/2)`.

V2 therefore does **not** randomize the middle hand of odd-size subsets.  The
released DeepStack-Leduc `range_generator.lua` does randomize that middle hand,
but HUNL primary text has precedence for HUNL reconstruction.

For a turn board with 1,128 legal hands, one range requires exactly 1,127
continuous mass-split draws.  A batch of four uses 4,508 scalar U(0,1) draws.

## Still unresolved — equal-strength ties

The source constrains every hand in `S1` to have strength no greater than every
hand in `S2`, but it does not specify ordering inside an equal-strength class.
On the representative turn board, **1,039 of 1,127 recursive split boundaries**
have an equal-strength tie crossing the split point.

Thus tie handling is not cosmetic.  V2 uses frozen hand id only as an explicit
`PROJECT_CANONICAL` tie-break and records that status.  It is not called
original/bit-exact.

## Still unresolved — pot interval

Under standard interval notation `[100,100)` is empty.  The same text survives
all three recovered arXiv source versions.  `AUTHOR_STRICT` therefore raises
instead of silently converting it to `{100}`.

The old `{100}` interpretation remains available only as
`RECONSTRUCTION_V1 / PROJECT_CANONICAL_NOT_AUTHOR_CONFIRMED`.

Literal integer counts for the other published intervals are:

- `[200,400)` → 200;
- `[400,2000)` → 1,600;
- `[2000,6000)` → 4,000;
- `[6000,19950]` → 13,951.

## RNG and board sampling

The original HUNL RNG implementation, seed schedule and exact public-board
sampling implementation remain unrecovered.  V2 therefore injects the uniform
random source and does not claim CPRG MT19937 inheritance.  Kevin Waugh's
email explicitly separates DeepStack from CPRG solver code.

## Offline CFR averaging status

The HUNL supplement explicitly says the target situations were approximately
solved using 1,000 iterations of CFR+ but does not explicitly state the target
averaging/skip convention in the data-generation paragraph.

The released Schmid/Moravčík DeepStack-Leduc `DataGeneration/data_generation.lua`
uses `Resolving:resolve_first_node`, and its released global settings are
`cfr_iters=1000`, `cfr_skip_iters=500`; `Lookahead` accumulates root CFVs only
after the skip.  This is strong **RELEASED-CODE-ANCHORED** reconstruction
evidence, but it is not promoted to HUNL author-explicit fact.

## Certification

`HUNL_AUTHOR_RANGE_V2_CERT.json` SHA-256:

`cbf891303c0550fa679428586f190ef5b46e43f5ca5c6f59a99c8c31ee5f7e35`

Key results:

- six-card author `rankCardset` oracle: 10,608/10,608 exact;
- legal turn hands: 1,128;
- legal uniform opponents per fixed hand: 1,035;
- 64/64 independent hand-strength recounts exact;
- legacy/new pair ordering-sign differences: 58,714;
- R(S,1) range sums: max error `2.220446049250313e-16`;
- blocked mass: exact zero;
- literal `[100,100)` sampling: FAIL-CLOSED;
- repeated certificate runs: byte-identical.

## Policy going forward

Do not create further expensive HUNL turn targets with `turn_datagen.py` V1.
It remains only to reproduce the historical pilot.

New generator work must build on `author_range_v2.py` and
`source_contract_v2.py`, preserving raw 1326-hand ranges and raw 1326-hand CFV
targets.  This keeps future recovered bucket maps/centroids applicable without
re-solving the poker states.
