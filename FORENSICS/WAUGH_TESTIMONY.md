# Kevin Waugh — first-party testimony (private e-mail to owner, 2026-08-15)

Evidence class: **Tier 2 / CONFIRMED (first-party author statement)** —
direct recollection of a DeepStack co-author & CPRG member, obtained by
the owner via private correspondence and supplied to this session.
Caveats: memory-based ("as far as I know", "I don't remember specifics"),
not an artifact; recorded verbatim below in substance.

## Statements (numbered per the owner's questions)

0. **Code separation (headline):** "The DeepStack experiments … did not
   use any of the CPRG's internal code for training or playing the
   DeepStack agent. Experiments involving CPRG agents obviously used
   CPRG code, and **some evaluation (like AIVAT and local best response)
   did use CPRG code**." And: "DeepStack is for the most part its own
   thing written by Martin and Matej."
1. **CFRplus_holdem_nolimit_FCPA:** public CPRG releases were "either a
   complete rewrite or a derivation of internal code with certain
   features removed or modified"; Neil's CFR+ release "relatively close"
   to the internal one, specifics not remembered.
2. **FCPA abstraction:** the raise-to sequence
   **3 BB → 9 BB → 27 BB → 81 BB → all-in** (100 BB stack, integer
   chips) "is exactly the internal representation when stated publicly."
3. **Card representation:** internal no-limit code "100% used canonical
   board indexing"; canonical indexing of PRIVATE cards uncertain;
   possibly solver on all private cards with canonical-hand storage.
4. **RNG:** "All the internal code used MT19937 as far as I know
   (Note: I'm not sure about DeepStack, since it did not use CPRG code
   for the solver)."
5. **project_uoapoker:** the CPRG internal repo; "The DeepStack solver,
   data generation and agent were separate."
6. **SVN:** location/archival unknown; "I don't think it was ever
   converted to git. None of the open source releases are in the repo."
7. **Training data generator:** "It was separate and not in the CPRG
   repo."

## Implications for the open forensic missions

### HUNL DataGenerator hunt (FINDINGS.md)
- **B-artifact localization changed**: the DataGenerator was a private,
  separate program by Schmid/Moravčík — NOT in the CPRG SVN. Hunting
  CPRG archives for it is now LOW-YIELD; the realistic holders are
  Schmid/Moravčík personal/DeepMind-era storage.
- **RNG family evidence REBALANCED**: Waugh's MT19937 statement covers
  CPRG internal code only and explicitly NOT DeepStack. Since
  Schmid/Moravčík wrote the DeepStack stack in Torch7/Lua (and the
  released Leduc datagen literally draws via `torch.rand` /
  `torch.manualSeed` = THRandom MT19937), the **Torch7 THRandom
  hypothesis** — exactly our generator's PROJECT CANONICAL choice —
  gains standing as the most natural DeepStack-side instance, while both
  families remain MT19937 at the core. No change to our pilot; label
  refinement only.
- FCPA integer-chip raise-to chain 3/9/27/81 BB: new CONFIRMED
  fingerprint for CPRG FCPA (useful for validating any recovered
  no-limit solver artifact).
- Canonical-board indexing CONFIRMED for internal no-limit strategy
  storage (supports Waugh hand-isomorphism-family candidates for the
  CPRG side; DeepStack-side 1326-ordering still UNKNOWN).

### AIVAT hunt (AIVAT_FINDINGS.md)
- **L4 (author code) localization**: the AIVAT implementation used for
  the DeepStack evaluation **lived in CPRG internal code**
  (project_uoapoker lineage, unarchived location, never on git). Public
  release likelihood: LOW. The realistic L4 path is a private archive of
  the CPRG tree or the person who maintained the evaluation component.
- The per-hand release (our L3 oracle) remains the strongest available
  artifact; the strategy/ranges BLOCKER stands.
