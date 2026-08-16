# HUNL Flop Lookahead — Phase 3 Certification

## Scope

This milestone connects the already-certified early-street betting skeleton to
an exact flop all-in terminal and the source-anchored flop→turn value-network
boundary.  It deliberately does **not** create replacement private HUNL bucket
centroids or claim original network weights.

## Green gates

| Gate | Result |
|---|---|
| Preflop/flop sparse ACPC differential | 1711 states / 1673 emitted actions / 0 divergences |
| Flop→turn chance/blocker algebra | all 22,100 flops; 1/45 pair-conditioned chance; 0 divergences |
| HUNL NN architecture / zero-sum contract | deterministic PASS |
| Flop→turn NextRoundValue-style contract | deterministic explicit-loop PASS |
| Exact flop forced-runout terminal | 64/64 independent pair recounts; exact antisymmetry |
| Flop CFR skeleton integration | deterministic PASS |
| Flop CFR with exact all-in terminal | deterministic PASS |
| Missing private bucket artifact | FAIL-CLOSED |

## Exact flop all-in oracle

Representative certified flop: card ids `(0,5,10)`.

- global two-card future-board pairs enumerated: `C(49,2)=1176`;
- for every fixed disjoint private-hand pair: `C(45,2)=990` equiprobable final boards;
- equivalent ordered runouts: `45×44=1980`;
- exact numerator matrix dtype: `int16`;
- illegal-pair nonzero entries: `0`;
- numerator SHA-256:
  `35f8f8a2cba78cdfc20f78fdd0b628016077834b9a4918af683868db5844633b`.

`HUNL_FLOP_ALLIN_CERT.json` SHA-256:
`a7be4baec063cddc1b2c7e5d2ea4931866c450a58dc646a9bd711ca5f845594a`.

## Flop engine exact-terminal integration

The production `FlopAllInEquity` is now used inside `FlopLookaheadEngine`.
The certification fixture intentionally keeps only the turn-boundary bucket map
and turn NN synthetic, because the original HUNL bucket artifact and weights
have not been recovered.

Representative test:

- board `(0,5,10)`;
- `pot_half=9000`;
- 4 CFR iterations / 2 skipped (small deterministic integration fixture, not
  a claim about the published production schedule);
- 15 nodes;
- 6 decision nodes;
- 4 fold terminals;
- 3 exact all-in terminals;
- 2 turn-value boundaries (`pot_half` 9000 and 18000);
- root CFV SHA-256:
  `b1425206023359e74b71ae7c888651c12ee751a6d8d447054bde4176abfe1617`;
- root strategy SHA-256:
  `2be1b0a9c89fc2d6a868317084218a506c91577e8c47c0ea96e4127b3e9134e4`.

`HUNL_FLOP_ENGINE_EXACT_TERMINAL_CERT.json` SHA-256:
`3b7651a0ef6456e16002ab0f5ae5d7924a0697149cf0cb22a94c3026fa60de8a`.

## Evidence boundary

This milestone establishes a working and certified **structural flop
lookahead**.  It does not establish bit identity with the private HUNL
DeepStack executable.  Exact original numerical reproduction remains blocked
by the missing strategic bucket artifact and original learned weights.

No Waugh/CPRG card indexer is substituted for the 1000 strategic buckets.
No inferred clustering is silently introduced.

## Next best work item

Continue upstream on the **turn raw DataGenerator**, which does not require the
turn value network at solve time.  Split every generator choice into:

- author-explicit;
- released-code-anchored;
- unresolved ambiguity;
- project-canonical reconstruction.

In particular, do not silently resolve the published `[100,100)` pot interval,
the exact `R(S,p)` equal-strength/tie convention, or the offline CFR averaging
convention.  Preserve raw full-hand CFV targets so a future recovered 1000-
bucket artifact can be applied without regenerating solved poker situations.
