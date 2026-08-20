# DeepStack Table S4 — V104 label-permutation uniqueness

Status: **NEW ROBUSTNESS MILESTONE / THE SIZE-STRUCTURE CORRESPONDENCE IS UNIQUE EVEN WITH FULL ROUNDING FREEDOM**

V102/V103 found the exact nominal-center law:

`Size_center = 3250*D - 4000`.

V104 asks a more adversarial question:

> Could this alignment be a generic accident caused by seven rounded Size numbers and seven reconstructed tree counts?

## Seven-row exhaustive permutation test

Keep the seven reconstructed decision counts fixed:

`16 / 32 / 20 / 40 / 64 / 112 / 172`.

Now arbitrarily reassign the seven published Size values among those rows.

There are:

`7! = 5,040`

possible assignments.

### Exact-center test

Exactly **1 / 5,040** assignments lies on any affine line.

It is the real Table-S4 row assignment.

### Full rounding-bin test

Now give every printed Size value the maximum freedom allowed by nearest-thousand publication:

`[center-500, center+499]`.

Ask whether *any real affine slope and intercept* can place all seven permuted rows inside their bins.

Again:

**1 / 5,040 feasible assignments.**

The unique survivor is the real Table-S4 labeling.

## Sparse-only test

Repeat without FULL.

There are:

`6! = 720`

permutations of the six sparse Size values.

Results:

- exact affine: **1 / 720**
- full nearest-thousand-bin affine feasibility: **1 / 720**

Again the unique survivor is the published row correspondence.

## Meaning

This is much stronger than saying "a line can be fit through the values."

The pairing between each betting menu's reconstructed structural count and its published Size value is
itself uniquely selected by affine compatibility.

Even allowing every printed number to float through its entire ±500 publication uncertainty does not
create a second permuted explanation.

This substantially strengthens the case that the reconstructed structural ordering is detecting a real
Table-S4 invariant rather than a generic rounded-number coincidence.

## Boundary

This is not a calibrated probability that the historical reconstruction is correct.

It still depends on the current forensic decision-node counts, and V99's algebraic ambiguity between
decision nodes, public nodes, and edges remains.

It does not identify the operational private Size counter.

No Supremus, CPRG, Leduc, Libratus, or Pluribus semantics are imported as DeepStack facts.

## Validation

- V104 tests: **6/6 PASS**
- seven-row permutations: **5,040 exhaustively tested**
- seven-row rounded-bin feasible mappings: **1**
- six-sparse permutations: **720 exhaustively tested**
- sparse rounded-bin feasible mappings: **1**
