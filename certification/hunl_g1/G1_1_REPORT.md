# Gate G1.1 — HUNL card layer + 7-card evaluator: BIT_EXACT certification

Date: 2026-08-13. Result: **PASS — BIT_EXACT, zero divergences.**
First milestone of HUNL Golden Baseline v0 (per `HUNL_RECONSTRUCTION_SPEC.md` §4).

## Deliverables
- `hunl/cards.py` — ACPC-exact 52-card encoding (`card = rank*4 + suit`,
  `game.h:249-251`; chars `cdhs` / `23456789TJQKA`, `game.c:103-104`),
  string I/O, frozen 1326 hole-pair ordering contract (lexicographic
  c0<c1), `possible_hands_mask`.
- `hunl/evaluator.py` — vectorized faithful port of `rankCardset`
  (`evalHandTables:4154-4253`). Lookup tables are **parsed at import from
  an untouched author file** (never retyped); file SHA-256 and canonical
  table digest are pinned and enforced at import.
- `certification/hunl_g1/rank_oracle.c` — C harness that `#include`s the
  untouched `evalHandTables` verbatim (Phase-2A THRandom pattern).

## Oracle provenance
| Copy | SHA-256 |
|---|---|
| `reference_lua/ACPCServer/evalHandTables` (authoritative, contains `rankCardset`) | `9b8bb8e1c73503d55073757d0434380a69c40431713448c3d578f1a8dca7c3e4` |
| `third_party/CFR_plus/evalHandTables` (Tammelin bundle) | `53248e54bafb8fbc67830230baf4ad92abaf1e95425c0326e14e7e7a82ef8425` |

The two copies differ only in surrounding consumer code; all nine numeric
tables are identical (canonical digest `c1f905c09588e32e3fe756a6f1e608cc`,
verified from both) — dual-provenance anchor.

## Certification matrix

| Check | Coverage | Result | Class |
|---|---|---|---|
| B. Full 7-card space | **all C(52,7) = 133,784,560** combinations, lexicographic; uint32 rank stream | SHA-256 `91d8792a3c5f…0466` **identical** C vs Python | **BIT_EXACT** |
| C. Class frequencies | 9 hand classes vs canonical published 7-card counts (23,294,460 / 58,627,800 / 31,433,400 / 6,461,620 / 6,180,020 / 4,047,644 / 3,473,184 / 224,848 / 41,584) | both implementations match exactly | independent math cross-check |
| D. Board API | 25,000 seeded boards (seed 20260813) × 1,326 hands = **33,150,000** entries incl. blocked sentinels | byte-exact vs C oracle `boards` mode | **BIT_EXACT** |
| E. Hand indexing | 1,326 pairs bijective; semantic ordering spot checks (royal > quads > boat; wheel straight flush) | PASS | |

Total evaluated: **133,784,560 + 33,150,000 = 166,934,560** comparisons.
**First divergence: NONE.** Runtime: C 4 s, Python full space 30 s,
board corpus 11 s (this 4-core container).

## Frozen artifacts
Golden Baseline `2ab6dde…`, certified datagen `7967622…`, Phase-2B
dataset/manifests — untouched (no DS-repo write; verified clean).
No tree building, bucketing, NN, training, or bulk generation started.

Raw run log: `G1_1_RESULT.txt`.
