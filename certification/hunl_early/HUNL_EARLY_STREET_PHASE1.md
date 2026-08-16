# HUNL Early-Street Phase 1 — preflop/flop betting skeleton + flop chance

Date: 2026-08-16
Base: owner-supplied `huhl-golden-core-aa04c5a.zip`.

## Scope

This milestone deliberately stops before value networks and bucketing.
It adds only pieces that can be grounded without guessing private DeepStack
implementation details:

1. Table-4 pre-flop and flop sparse action menus in `hunl/config.py`.
2. `hunl/early_street_tree.py`: preflop/flop betting trees ending at a
   next-street value boundary, with all-in runout distinguished explicitly.
3. `hunl/preflop_tree.py` and `hunl/flop_tree.py` wrappers.
4. `hunl/flop_chance.py`: flop->turn blocker/chance algebra (1/45 pair chance).
5. First-party `count_nl_infosets` source vendored as a separate rule oracle.

## Gate A — sparse betting differential oracle

Authority for legality/state transitions: untouched CPRG/ACPC `game.c`.
Sparse action-menu authority: DeepStack supplementary Table 4.

Result (`EARLY_STREET_ORACLE.json`):

- Preflop tree: 226 nodes, 76 decisions, 225 actions.
- 37 non-all-in preflop boundaries; 21 distinct flop entry pot-halves.
- Preflop + every flop tree reached through those boundary paths:
  **1,711 states checked**.
- **1,673 emitted sparse actions checked** through `isValidAction`.
- State fields checked: round, current player, spent[2], maxSpent,
  minNoLimitRaiseTo, finished/fold state.
- Divergences: **0**.
- Fingerprint: `32188d0c5d70dd0d87e5c74d261236265a35843f514fb578e2b266d7605e7eae`.

Important: this proves our sparse actions are legal and their state transitions
match the public game oracle.  It does **not** prove byte identity with the
private DeepStack tree-builder implementation.

## Gate B — flop->turn chance algebra

Result (`FLOP_CHANCE_CERT.json`):

- all C(52,3) = **22,100 flop boards** exhausted for legal-hand counts;
- 1,176 legal hands per flop = C(49,2);
- 49 candidate public turn cards;
- 1,128 legal hands after each turn = C(48,2);
- 47 legal turn cards per fixed legal private hand;
- every legal disjoint hand pair has exactly **45** unseen turn cards;
- six representative flops checked by full 1326x1326 pair-count matrices:
  **7,627,536 legal ordered pairs**;
- 300 additional independent scalar recounts;
- divergences: **0**;
- fingerprint: `29e80b4f0e45309abd4dc03a1982936cf6e4d67652df7269792201d7bab69ca5`.

Status: COMBINATORIAL_EXACT.  This is the derived game chance algebra, not a
private-source bit-exact claim.

## Frozen-core regression

The only existing HUNL code file intentionally modified is `hunl/config.py`
(additive preflop/flop constants + generic menu accessor).  Existing river
behavior uses the backwards-compatible `menu_for_depth()` wrapper.

Representative regression old golden vs this branch:

- River manifest SHA values identical for pot-halves
  100, 200, 300, 900, 2700, 8100, 19999.
- Turn `(board=(0,5,10,15), pot_half=2000)` node count identical:
  `(6333, 2320, 3998, 15)`.
- Turn manifest SHA identical:
  `cdb302a45f60440c3f14a35d8ded584395ad9dbbdad7d9be92b182053d44e5e1`.

## What remains before a flop solver

Do **not** invent a turn value network.  The next dependency is the actual
turn value-function layer: bucket mapping + network/training contract.  The
flop betting/chance skeleton is now ready to consume that boundary once its
artifacts are reconstructed and certified.
