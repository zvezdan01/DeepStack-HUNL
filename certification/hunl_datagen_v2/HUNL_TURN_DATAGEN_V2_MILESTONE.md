# HUNL Turn DataGenerator V2 — source-constrained milestone

## Purpose

Replace the legacy V1 pilot's now-known nonliteral choices without claiming
access to the private 2016 HUNL generator.

## Author-explicit HUNL contract

From the original DeepStack supplementary TeX:

- sample a pot category uniformly, then an integer uniformly within it;
- generate ranges with recursive `R(S,p)`;
- split `|S1| = floor(|S|/2)`;
- hand strength = probability of beating a uniformly selected compatible hand
  in the **current public state**;
- turn targets: 10,000,000 random turn situations;
- solve each with 1,000 iterations of CFR+;
- actions are only F/C/P/A;
- no card abstraction in the target solve;
- original run used 6,144 CPU cores and >175 core-years.

## Same-author released-code anchors

The released DeepStack-Leduc code provides a concrete implementation family:

- Torch7 FloatTensor default;
- `torch.random` rejection board sampler without replacement;
- `gen_batch_size = 10`;
- full P1 range batch, then full P2 range batch;
- `Resolving:resolve_first_node` and `get_root_cfv_both_players` for datagen;
- `cfr_iters = 1000`, `cfr_skip_iters = 500`;
- RM+ regrets, simultaneous updates, uniform post-skip averaging;
- returned root values divided by the equal committed amount used in
  `node.bets`.

These anchors are not represented as proof that the private HUNL generator was
byte-identical to the released Leduc implementation.

## V2 correction relative to legacy V1

V1 used future-river all-in equity to sort turn hands and randomized odd splits.
V2 instead uses the literal HUNL source contract:

1. evaluate strength on the current four-card public board;
2. use `floor(n/2)` at every recursive split;
3. keep blocked hands at exactly zero.

Equal-strength ordering is unpublished. V2 uses frozen hand id only as an
explicit `PROJECT_CANONICAL` tie-break.

## Two execution modes

### `AUTHOR_STRICT`

Fail-closed. It refuses to emit samples while any private-source choice needed
for bit identity remains unresolved, including the printed `[100,100)` interval,
tie order, HUNL RNG/seed schedule, and original serialization ordering.

### `RELEASED_CODE_ANCHORED`

Operational reconstruction. It uses exact THRandom/Torch7 behavior and the
released-code conventions listed above, plus explicit project-canonical choices
where the private source is unavailable.

## Certification

`HUNL_TURN_DATAGEN_V2_CERT.json` records:

- AUTHOR_STRICT fail-closed behavior;
- deterministic input replay;
- blocked range mass exactly zero;
- float32 range sum error below 2e-6;
- exact RNG draw ledger;
- legal support for 10,000 sampled reconstructed pot values;
- deterministic full HUNL first-node solver smoke (20 iterations / omit 10);
- weighted expected-utility zero-sum residual below 1e-5 chips.

A 1000/500 production-shape solve was attempted in the sandbox but exceeded the
600-second execution ceiling. This is a performance limitation of the current
Python full-hand solver path, not a failed correctness gate. No solver semantics
were changed to make the test faster.

## Remaining private-source unknowns

1. intended correction/semantics of `[100,100)`;
2. equal-strength tie ordering;
3. exact HUNL RNG instance, master seed, worker seed derivation and draw order;
4. original 1326 serialization order / sample file format;
5. exact private HUNL offline implementation details beyond the strong
   released-code anchors;
6. original 1000-bucket centroids/mapping and trained network weights.
