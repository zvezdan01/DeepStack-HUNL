# HUNL milestone — Schmid testimony + Deep CFV follow-up

Date: 2026-08-16

## New first-party evidence
Martin Schmid directly recalled that skip iterations were always used when
answering the question about CFR+ target-generation iterations.

Verdict:
- skip/burn-in **exists**: AUTHOR-CONFIRMED recollection;
- exact HUNL skip count: still unpublished;
- project value 500: RELEASED-CODE-ANCHORED to Schmid/Moravcik
  DeepStack-Leduc, no longer an unsupported skip-vs-no-skip hypothesis.

## New primary follow-up evidence
Zarick, Pellegrino, Brown, Banister (2020) independently reimplemented
DeepStack in HUNL. The paper provides a high-value architecture cross-check:
- same 2001->7x500->2000 CFVnet architecture;
- original play-time turn solve went to game end with bucketed river actions;
- those river-bucketing details were never published;
- random training subgames were generated in a manner identical to DeepStack.

## Architecture correction
`hunl.turn_engine.TurnEngine` is now explicitly documented as the
full-card exact-to-end **DATAGEN / ORACLE** turn engine. It is not labeled as
the exact original play-time turn implementation.

`hunl.turn_play_contract` is new and fails closed unless an explicit river
bucket provider is supplied. No project reconstruction is silently substituted
for the missing original artifact.

## Regression gates
- Python compileall: PASS
- AUTHOR_RANGE_V2 certification: PASS
- TURN_DATAGEN_V2 certification: PASS; replay byte-exact under project stack
- VALUE_NETWORK contract certification: PASS
- original online-turn missing-bucket fail-closed contract: PASS

No golden numeric solver path was intentionally changed by this milestone.

## Next decision
Keep two lineages separate:
1. `ORIGINAL_DEEPSTACK_FORENSIC`: preserve the source-constrained baseline and
   explicitly expose missing private artifacts.
2. `SUPREMUS_INSPIRED` (future performance branch): DCFR+, river CFVnet,
   4,000-iteration training solves, larger action abstraction, larger datasets,
   GPU kernels. Do not mix these improvements into the original baseline.
