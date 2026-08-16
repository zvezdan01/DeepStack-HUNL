# DeepStack / CPRG lineage correction — 2026-08-16

Evidence basis: first-party e-mails supplied by the owner from Kevin Waugh
(2026-08-15) and Michael Johanson (2026-08-16).  This note changes provenance
claims, not already-certified poker mathematics.

## Confirmed separation

- `project_uoapoker` was an internal CPRG repository.
- Waugh: DeepStack training, DeepStack solver and the playing agent did **not**
  use CPRG internal code; they were separate, predominantly Martin Schmid /
  Matej Moravčík work.
- Johanson independently recalls DeepStack being built from scratch in a new
  repository and not based on the old internal repository.
- CPRG code did participate in experiments involving CPRG opponents and in
  some evaluation tooling (AIVAT / local best response).
- The DeepStack HUNL DataGenerator was separate from `project_uoapoker`.

## Project rule from this point

Evidence must be labeled by lineage:

1. **DeepStack-primary** — paper/supplement, author Leduc code, Schmid /
   Moravčík / Burch artifacts or testimony.  May support claims about the
   DeepStack implementation.
2. **Poker-rule oracle** — ACPC `game.c`, Johanson `count_nl_infosets`, card
   evaluator, combinatorics.  May certify game semantics but does not prove
   DeepStack source lineage.
3. **CPRG historical cross-check** — internal/public CFR+, FCPA, Waugh
   indexing, AIVAT/LBR.  Useful as an independent implementation oracle or
   historical fingerprint; must not be called DeepStack source code.
4. **PROJECT CANONICAL / INFERRED** — deterministic choices where no original
   DeepStack artifact exists (e.g. exact RNG instance/seed, 1326 ordering,
   datagen omit=500 unless later author evidence resolves it).

## Specific reclassifications

- CPRG MT19937 evidence no longer supports inheritance into DeepStack.  The
  project's THRandom choice is supported on the DeepStack side by the released
  Torch7/Leduc family and remains PROJECT CANONICAL for unreleased HUNL data.
- Waugh `hand-isomorphism` is an author-certified CPRG indexing candidate and
  a bit-exact oracle; it is **not** evidence that private DeepStack HUNL used
  that exact indexer.
- CPRG FCPA = fold/call/pot/all-in with integer chips is first-party confirmed
  (Waugh + Johanson).  It is a cross-check for the DeepStack supplement's
  F/C/P/A datagen action set, not evidence of code reuse.
- `CFRPLUS_HOLDEM_NOLIMIT_FCPA` is best classified as a likely strategy-file
  name (Johanson recollection), not as a known special solver executable.
- Searching `project_uoapoker` remains useful for Full Cards / CPRG evaluation
  genealogy, but is low priority for recovering the DeepStack DataGenerator.
