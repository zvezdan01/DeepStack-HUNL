# HUNL Value-Network / Flop→Turn Boundary — Phase 2

## Verdict

This milestone closes the **published architecture and next-round algebra contract** for the HUNL postflop value network without inventing the unreleased 1000-bucket artifact.

It does **not** claim original HUNL weights, original cluster centroids, original bucket ids, or bit identity with the private DeepStack implementation.

### Status

| Component | Status |
|---|---|
| HUNL NN input/output dimensions | AUTHOR-EXPLICIT + RELEASED-CODE-ANCHORED |
| 7 × 500 hidden architecture + PReLU | AUTHOR-EXPLICIT |
| zero-sum outer correction | AUTHOR-EXPLICIT + RELEASED-CODE-EXACT ALGEBRA |
| pot feature / stack normalization | AUTHOR-EXPLICIT + RELEASED-CODE-ANCHORED |
| range→bucket conditional normalization | RELEASED-CODE-ANCHORED |
| opponent-mass restoration | RELEASED-CODE-ANCHORED |
| bucket→hand inverse mapping | RELEASED-CODE-ANCHORED |
| flop→turn chance factor | COMBINATORIAL-EXACT: 1/45 |
| post-skip next-board memory | RELEASED-CODE-ANCHORED |
| original HUNL 1000-bucket map | **MISSING / FAIL-CLOSED** |
| original HUNL weights | **MISSING** |

## Primary-source anchors

Recovered original DeepStack arXiv v3 TeX is used as the HUNL authority.

- `paper.tex` SHA-256 `86a81830f5e83ed35edf49678c67a8ea832de2f664cc2e9e5121cef367e3725e`
  - architecture: two postflop networks, seven FC hidden layers × 500, PReLU;
  - pot fraction + bucketed ranges as input;
  - two-player CFVs as fractions of pot;
  - differentiable zero-sum correction;
  - turn training from 10M solved situations and flop training from 1M situations using the turn network at the depth boundary.
- `appendix.tex` SHA-256 `6056105a7bc3eca582cee26c8ea9051544614b37144d7e5877b10657ad225938`
  - Table 4: flop `1000` CFR iterations, `500` omitted, action menus, `Turn` NN boundary;
  - training details: Adam, average Huber, batch 1000, LR 0.001→0.0001 after 200 epochs, ~350 epochs;
  - bucket description: 1000 clusters, k-means + earth mover distance over hand-strength-like features.
- `figs/dnn.pdf` SHA-256 `f125656fe7be38638c7cb9bd4ca027b4c0a0069a88cff7728bb2155f8d8521b0`
  - depicts 1326-card ranges → 1000 bucket ranges → deep network → 1000 bucket values → inverse mapping to card CFVs.

Released author DeepStack-Leduc is used only to anchor generic implementation semantics:

- `Nn/net_builder.lua` SHA-256 `c1a96384fbc12ea238f9fe0df7028b724a59611ae2d1786c9fbe68d720638716`
- `Nn/next_round_value.lua` SHA-256 `2f8283ab3a030e909f0501fd1b412972e8abb06c0a891d21b1279a94f4410562`
- `Tree/tree_builder.lua` and `Settings/arguments.lua` are recorded in `SOURCE_PROVENANCE.json`.

## Implemented contract

### `hunl/value_network.py`

`DeepStackHUNLValueNet` implements:

- input width = `2×1000 + 1 = 2001`;
- seven hidden `Linear(...,500) + PReLU` stages;
- final `Linear(500,2000)`;
- output order `[P1 1000 CFVs | P2 1000 CFVs]`;
- zero-sum correction

`raw - 0.5 * sum(raw * [range1,range2])`

broadcast to all 2000 output coordinates.

The instantiated architecture has `3,506,007` trainable parameters when using one scalar PReLU slope per hidden layer. The scalar PReLU convention is **released-code-anchored**, not explicitly specified by the HUNL paper.

### `hunl/value_bucketing.py`

Defines only the algebraic interface:

- legal hand → bucket id;
- blocked hand → `-1`;
- card-range → bucket-range by summation;
- bucket-value → card-value by inverse scatter;
- explicit `BucketProvider` interface.

`MissingAuthorBucketProvider` intentionally raises at runtime. There is no fake default clustering.

### `hunl/flop_value_boundary.py`

HUNL generalization of released `NextRoundValue` mechanics for a fixed 3-card flop:

1. enumerate all 49 turn cards;
2. mask each player's 1326-hand reach by the candidate turn;
3. map to 1000 buckets;
4. record compatible mass for each player;
5. condition each player's bucket distribution on the turn board;
6. append `pot_half / 20000` as the NN pot feature;
7. evaluate the turn NN;
8. multiply player-0 values by player-1 compatible mass and vice versa;
9. inverse-map 1000 bucket values to 1326 hand values;
10. aggregate chance exactly once with `1/45`;
11. retain post-skip opponent masses and weighted CFVs so an observed turn can later be queried conditionally without the `1/45` average.

Returned values remain **fractions of pot**. The calling lookahead is responsible for the pot multiplier, matching released author Lookahead semantics.

## Deterministic certification

`certification/hunl_value/run_value_contract_cert.py` is deterministic and repeatable. Re-running it twice produces byte-identical JSON.

Certificate SHA-256:

`b0f06cc9a8649da2d0931b96a1315db4a6e92a3b7cda79fcdcac11f94d3d9c07`

Key results:

- architecture: `2001 → 7×500 PReLU → 2000`;
- parameter count: `3,506,007` under scalar-PReLU convention;
- zero-sum invariant: max weighted residual `1.280568540096283e-09` over 19 deterministic cases;
- real 4-card board bucket-conversion algebra tested on all 1326 slots;
- missing author buckets: **FAIL_CLOSED_PASS**;
- flop→turn boundary: 49 turns, `1/45`, batch 3;
- implementation vs independent explicit chance/bucket/normalization loop: **EXACT** for the deterministic synthetic test oracle;
- observed-turn post-skip memory path exercised and hashed.

The synthetic mapping in this certificate is strictly a test fixture. It is not used as a reconstruction bucketizer.

## Regression gates retained

Existing earlier-street gates remain green after adding the value contract:

- preflop/flop ACPC differential oracle: `1711` states, `1673` actions, `0` divergences;
- flop→turn blocker/chance certificate: all `22,100` flops plus `7,627,536` legal ordered hand pairs on representative boards, `0` divergences;
- chance factor remains exactly `1/45`.

## Bucket-artifact search

A focused artifact inventory found no original HUNL 1000-cluster map, centroid file, HUNL network model, or HUNL network weight file in the recovered DeepStack paper artifacts / match artifacts.

The released DeepStack-Leduc tree contains its own toy-game bucketer and `Data/Models/PotBet/final_cpu.model`; these are **not HUNL artifacts** and are not substituted.

See `HUNL_BUCKET_ARTIFACT_SEARCH.json`.

## Remaining blockers before a real flop solve

The architecture is no longer the blocker. The first unresolved numerical dependency is:

**U2 — an explicit HUNL 1000-bucket artifact.**

For an author-exact reconstruction we would need at least one of:

- original feature vectors / histogram specification;
- original centroids;
- board+hand→bucket tables;
- original bucket generator with seed/config.

The paper's cited abstraction literature constrains the method family, but does not uniquely determine DeepStack's private feature construction or centroids. Therefore a replacement can be built as a **versioned reconstruction bucketizer**, but it must never be labelled original/bit-exact.

A second later blocker is the original trained HUNL turn-network weights. The network code can be trained from reconstructed data once U2 is resolved project-canonically, but that produces reconstruction weights, not the 2016 private weights.

## Next engineering step

Build the flop CFR lookahead around this boundary using dependency injection:

- certified flop sparse betting tree;
- exact fold/ACPC terminal semantics;
- an explicit all-in-runout terminal-equity provider;
- `FlopTurnValueBoundary` for non-all-in turn boundaries;
- no silent bucket fallback.

This isolates the private/reconstructed bucket artifact behind one interface and keeps the already-certified turn/river core untouched.

---

## Phase 3 addendum — exact flop all-in terminal + lookahead integration

After the value-boundary contract was frozen, the remaining public-math
terminal dependency at a flop all-in was implemented without using a learned
model or private DeepStack artifact.

### `hunl/flop_allin.py`

For a fixed three-card flop and fixed disjoint private hands:

- 45 cards remain after removing the flop and four private cards;
- ordered turn/river runouts = `45 × 44 = 1980`;
- showdown depends only on the final five-card board, so the two orders of a
  two-card completion are equivalent;
- exact unordered final-board completions = `C(45,2) = 990`.

The implementation precomputes the exact integer payoff numerator matrix

`N[h0,h1] = Σ showdown(h0,h1 | flop + future_pair)`

over all `C(49,2)=1176` global two-card board completions.  Blocked private
pairs or board completions contribute zero through the already-certified
showdown matrix.  The final counterfactual-value matvec is

- `CFV0 = pot_half/990 * N @ reach1`
- `CFV1 = pot_half/990 * (-N.T) @ reach0`.

This is an exact poker/chance terminal computation; it is **not** claimed to
reproduce the private DeepStack implementation's optimization/storage layout.

Certificate `HUNL_FLOP_ALLIN_CERT.json`:

- exact integer antisymmetry: PASS;
- illegal private-pair nonzero entries: 0;
- 64 independently re-enumerated private-hand pairs: 64/64 exact;
- each independent pair: 990 final boards;
- small-support CFVs vs independent direct evaluator: max error
  `1.8189894035458565e-12` chips;
- weighted zero-sum residual: exactly `0.0` in the certified fixture;
- numerator SHA-256:
  `35f8f8a2cba78cdfc20f78fdd0b628016077834b9a4918af683868db5844633b`;
- certificate SHA-256:
  `a7be4baec063cddc1b2c7e5d2ea4931866c450a58dc646a9bd711ca5f845594a`.

### `hunl/flop_engine.py`

A first-node flop depth-limited CFR lookahead now integrates:

- source-constrained sparse flop betting tree;
- exact fold terminal values;
- exact `FlopAllInEquity` forced-runout values;
- `FlopTurnValueBoundary` at non-all-in turn boundaries;
- RM+ style regret update / post-skip averaging as the currently reconstructed
  play-time lookahead contract.

The exact-terminal integration certificate uses the production all-in terminal,
but still injects deterministic **synthetic test-only** 1000-bucket maps and a
synthetic zero-sum turn network.  Therefore it certifies integration and exact
public terminals, not the original HUNL numerical solution.

Certificate `HUNL_FLOP_ENGINE_EXACT_TERMINAL_CERT.json`:

- deterministic repeat run: EXACT;
- 15 nodes, 6 decision nodes, 4 fold terminals, 3 all-in terminals,
  2 turn boundaries for the representative test tree;
- exact all-in numerator hash matches the standalone terminal certificate;
- weighted root zero-sum residual: `-3.838408701994922e-09` chips;
- certificate SHA-256:
  `3b7651a0ef6456e16002ab0f5ae5d7924a0697149cf0cb22a94c3026fa60de8a`.

### Remaining numerical blockers

At this point, the flop lookahead no longer lacks public poker/chance
mechanics.  The unresolved dependencies needed for an **original-numerical**
DeepStack flop solve are now isolated to private/unreleased artifacts:

1. the exact HUNL 1000-bucket construction / maps / centroids;
2. the original trained HUNL turn-network weights.

The code remains fail-closed for (1).  Synthetic bucket/network fixtures exist
only inside certification tests and are labelled `TEST_ONLY_NOT_RECONSTRUCTION`.
