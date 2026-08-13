# Gate G1 tree layer — HUNL river config + betting tree vs untouched ACPC game.c

Date: 2026-08-13. Result: **PASS — zero divergences.** Spec anchor:
HUNL_RECONSTRUCTION_SPEC v2 freeze `f81d08c` (Table-4 river configuration,
all VERIFIED).

## Deliverables
- `hunl/config.py` — VERIFIED game constants (stack 20,000; blinds 100/50,
  seat0 = BB; firstPlayer 2 1 1 1 → river first actor seat 0) + Table-4
  river menus (depth 0 {F,C,½P,P,2P,A}; depth 1 {F,C,½P,P,2P,A};
  depth ≥2 {F,C,P,A}) + river resolve constants 2000 iters / 1000 omitted
  (recorded, unused by the tree). Chip conversion: pot = 2·max_spent,
  raise-to = max_spent + f·pot (author bet-sizing convention) — with the
  Table-4 fractions every candidate is an exact integer (no rounding
  exists anywhere).
- `hunl/tree.py` — full river betting tree: player ordering,
  check/call/fold semantics, committed chips (`spent` = total per seat),
  max_spent, min-raise-to propagation (`2R − max_spent`, short all-in does
  not raise it), all-in & call-to-all-in, short all-in raise
  (min=max=stack window), terminal fold/showdown contracts,
  depth-indexed Table-4 menus, canonical manifest + SHA.
- `certification/hunl_g1/betting_oracle.c` — stdin driver compiled with
  **verbatim `game.c` + `rng.c`** (`isValidAction`, `raiseIsValid`,
  `doAction`, `initState`, `currentPlayer`, `stateFinished` are the
  authority; our builder only mirrors them).

## Certification corpus — EXHAUSTIVE
- **19,801 river states = every reachable river entry pot-half in HUNL**
  ({100} ∪ [200, 19999]; halves in (100,200) are unreachable — min bet =
  BB — and 20,000 means both all-in with no river betting).
- Each state reached in the oracle through a real hand replay from
  initState (pre-flop call/check → flop raise-to-pot + call (or checks) →
  turn checks), so blind posting, position asymmetry and cross-street
  min-raise propagation are exercised on every case.
- **622,563 tree nodes** (227,322 decision + 395,241 terminal), every one
  replayed and checked in the ACPC state machine.
- **2,318,960 oracle replies, all byte-identical to our predictions:**
  622,563 full state snapshots (finished/round/actor/spent/max_spent/
  minNoLimitRaiseTo/folded), 227,322 `raiseIsValid` windows (valid flag +
  exact [min,max]), **1,469,075 per-action validity comparisons**
  (`isValidAction`, no fixing) — every tree action asserted legal and
  every negative probe asserted illegal.

## Boundary cases exercised (counts from the run)
| Case | Count |
|---|---|
| legal/illegal fold (incl. fold-facing-check illegal) | 39,602 illegal-fold probes; fold-legal at every bet-facing node |
| check vs call semantics (depth-0 check child vs closing call) | all 227,322 decision nodes |
| min raise exact boundary (`r min` legal, `r min−1` illegal) | 113,661 min-raise probes |
| pot / half-pot / 2-pot raises (exact chips) | all menu candidates in 1,469,075 comparisons |
| all-in; raise above stack (`r 20001` illegal) | every raise-capable node |
| short all-in raise (min>stack ⇒ window=[20000,20000]; sub-all-in raises illegal) | 31,088 windows |
| menu candidates dropped for exceeding stack | 88,167 nodes |
| fraction candidate colliding with all-in (dedupe, e.g. 2P=20000 at M=4000) | 8 nodes |
| exact stack exhaustion (raise-to == 20000) + post-all-in no-raise states | 113,661 |
| previous-raise/min-raise propagation over repeated raises | every raise chain (deepest trees 279 nodes at pot 100) |
| asymmetric blind/position replay | every scaffold (SB acts first preflop, BB first postflop) |
| terminal fold/showdown identification (finished flag, folded flags, spent) | 395,241 terminals |

## Anchors & determinism
- game.c SHA-256: `85b5325dd54e043fdb22548d4e1bfe4ed40b820a87f75f252d93875688b5c7cc` (untouched)
- Combined tree-manifest SHA-256 over all 19,801 trees:
  `7e5eb54ca43481b24e3e1b64f7c20881ff2d0f72f41f5cc3c8f6b03a7ceffa50`
  — identical in-process and across 2 fresh subprocess rebuilds.

## Structural tests (all pass, asserted during build/walk)
No negative remaining stack; contributions monotonic per seat; pot
accounting conservative; no illegal action enters the tree (oracle would
abort on any `A` replay of an illegal action — never triggered); every
non-terminal node has ≥1 legal action (call always present); terminal
utility context unambiguous (fold → folder ∈ {0,1}; showdown →
spent[0]==spent[1]); byte-identical manifests across processes.

## First divergence
**NONE** (engine and harness both green on first full exhaustive run;
the earlier 140-pot pilot run also passed with zero divergences).

## Runtime
13 s total on the 4-core container (generation 7 s, oracle 1 s,
comparison <1 s, determinism rebuilds ~4 s).

## Residual risks
1. The scaffold reaches river states through one canonical action
   history per pot; ACPC min-raise-to at river entry depends only on
   (max_spent, BB), which the state snapshot verifies, so alternative
   histories cannot yield a different river entry state — but histories
   with river entry min_raise_to ≠ S+100 (e.g. turn ending in an exact
   call of a raise) are not represented; the river-entry contract is
   FROZEN as min_raise_to = max_spent + BB and must be revisited when the
   full 4-street tree is built. [ACPC doAction always resets to
   maxSpent+BB on round advance — verified in code — so this is a
   documentation note, not an open risk.]
2. CFR integration is intentionally NOT connected yet (per instruction);
   terminal nodes carry context only.
3. Table-4 chip semantics (pot = 2·max_spent) is the author Leduc
   bet-sizing convention applied to VERIFIED fractions; the supplement
   does not spell out the chip formula — recorded as the one INFERRED
   element of this layer (exact-integer, no rounding ambiguity).

Frozen artifacts untouched: Golden Baseline `2ab6dde`, datagen `7967622`,
Phase-2B dataset, G1.1 `23f783f`, G1.2/G1.3 `740f47b`, spec `f81d08c`.
Raw log: `G1_TREE_RESULT.txt`.
