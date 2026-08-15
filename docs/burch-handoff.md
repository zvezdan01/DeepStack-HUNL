# Handoff brief — Neil Burch / DeepStack HUNL DataGenerator provenance

**Purpose.** Self-contained transfer document for another model or analyst continuing this
investigation. No prior conversation context required.
**Companion.** `docs/burch-forensics.md` — the full ledger, 53 findings, 13 waves, with
line numbers, hashes and verbatim quotes. This brief is the executive layer over it.
**Date of investigation.** 2026-08-15.

---

## 1. The question

Neil Burch's 2017 PhD thesis states, in the mandated co-authorship declaration:

> "I was responsible for the theoretical bounds, along with T. Davis. I provided an initial
> experimental framework, and **generated one data set used to train the evaluation function**."

The investigation sought any surviving first-party artifact behind that sentence:

| ID | Target |
|----|--------|
| A | Original HUNL range generator source |
| B | Original DataGenerator / generate_data source or job script |
| C | Original raw HUNL training samples |
| D | Original RNG seed / config / worker seed allocation |
| E | Cluster log, PBS/qsub script, or experiment manifest with exact generation parameters |

**Scope rule enforced throughout:** Neil Burch only. Other authors and projects were
followed only where they appear inside a Burch artifact, commit, directory, paper, job
script or repository.

---

## 2. Answer

**A, B, C, D, E: NOT FOUND.** None exists publicly. The investigation further shows that
none of the examined artifacts contains them or could contain them.

**Three results replace the artifacts:**

1. **Bit-exact reproduction of the original is provably unattainable** — established
   twice, independently, by experiment (§5).
2. **The space of candidate mechanisms is closed** — four seeding idioms, one hand-strength
   engine, all specified bit-exactly from primary sources (§4).
3. **A named, located target for any future search** — the internal CPRG repository (§6).

---

## 3. Sources exhausted

All read line by line. Hashes and full inventory in the ledger, §1.

| Source | Note |
|---|---|
| `CFR_plus.tar.bz2` | 20 files. tar owner `burch/burch`, packed 2014-11-18 20:29. Verified byte-identical against two independent GitHub mirrors |
| Burch PhD thesis (2017) | 7 243 lines, full grep; chapter 6 read entire; DOCX internals |
| `project_acpc_server` v1.0.42 | Original tarball, owner `aaaicpc/pg227652` (uid 10424679, gid 26238) |
| arXiv 1701.01724 v1/v2/v3 | DeepStack. `paper.tex`, `appendix.tex`, all LaTeX comments, version diffs |
| arXiv 1303.4441 v1–v4 | CFR-D, Burch first author |
| arXiv 1612.06915 v1/v2 | AIVAT, Burch first author |
| arXiv 1810.11542 v1/v2 | JAIR alternating updates, Burch first author |
| `vs_LBR.zip` | 628 match logs from Calcul Québec MP2 + the team's aggregation script |
| `DeepStack_vs_IFP_pros.zip` | Human study: 45 037 hands, AIVAT CSVs, ACPC + PokerStars logs |
| NIPS 2012 supplemental | Single `appendix.pdf`, no code |
| GitHub / GitLab / Bitbucket | User, repo and commit search |

**Burch has no public repository containing poker, CFR or DeepStack code.** His University
of Alberta version control was SVN, not git — proven by git-svn UUID author addresses in the
HOG2 migration (`neil.burch@3e291e08-…`, 2008–2009). His two GitHub accounts
(`neilburch-sony`, `NeilBurch`) hold zero original repositories between them.

**Not searchable from the investigation environment** (egress-blocked, must not be recorded
as negative): Wayback Machine, Software Heritage, all ualberta.ca hosts, ERA, arXiv directly,
GitHub authenticated code search, Bitbucket user lookup.

---

## 4. What is established, with mechanism

### 4.1 Chain of custody for the CFR+ solver (the only first-party Burch solver artifact)

Thesis bibliography `[8]` cites `http://poker.cs.ualberta.ca/software/CFR_plus.tar.bz2`;
thesis §4.3.1 names that code as what generated Cepheus; the tarball is UNIX-owned by
`burch`; the packing command is in Burch's own `Makefile:43-46`, which exports from an SVN
`trunk` while stripping `*svn*` metadata; two independent mirrors are byte-identical.

### 4.2 Four CPRG seeding idioms — complete catalogue

| # | Idiom | Location | Deterministic |
|---|---|---|---|
| 1 | `rngSeed ^ subgameIndex` → glibc `random_r`, state length **32** (TYPE_1, degree 7) | `CFR_plus/storage.c:1001` | yes |
| 2 | `genrand_int32(&match->rng)` drawn from an MT19937 stream seeded by a master seed | `bm_server.c:1358` | yes |
| 3 | plain sequential worker index 0…49 passed directly | LBR submit loop on MP2 | yes |
| 4 | `init_genrand(tv.tv_usec)` | `example_player.c:52` | **no** |

Shared across all four: reduction by `% n`, modulo bias never corrected.

Idiom 1 is the one matching the `rngSeed ^ index` pattern often assumed for DeepStack. It is
**glibc `random_r`, not MT19937**, and it samples boards inside the HULHE solver.

### 4.3 Hand strength engine

`rankCardset()` in `CFR_plus/game.c:107-224` — a seven-card evaluator absent from the ACPC
build. Returns a value in `[0, 12116)` over nine classes:

| class | count | offset |
|---|---|---|
| high card | 1 287 | 0 |
| pair | 3 718 | 1 287 |
| two pair | 3 601 | 5 005 |
| trips | 1 014 | 8 606 |
| straight | 13 | 9 620 |
| flush | 1 287 | 9 633 |
| full house | 1 014 | 10 920 |
| quads | 169 | 11 934 |
| straight flush | 13 | 12 103 |

This is the only hand-strength engine anywhere in Burch's released code. If he wrote the
range generator, this was its primitive. **Candidate, not proof.**

### 4.4 Burch's only surviving situation sampler

`CFR_plus/storage.c:865-902`: enumerate suit-isomorphic canonical boards keeping `weight` =
number of suit mappings, then partial Fisher–Yates with `random_r`, `t %= (num - i)`, weight
copied verbatim and renormalised only downstream via `weightSum` and `boardFactor`.
Seeded per subgame by idiom 1. Full bit-exact recipe in ledger appendix A.

### 4.5 Hard negatives (disproved, not merely unsupported)

- **MT19937 is unreachable dead code in the CFR+ solver.** `dealCards()` has zero call
  sites; `cfr.c`, `recompress.c`, `storage.c` and the rest contain no reference to
  `genrand*`. The `rngseed=` CLI option reaches only glibc `random_r`.
- **CFR+ has no counterfactual-value export.** `dumpValues()` writes regrets and average
  strategy only. The DataGenerator cannot have been a wrapper around this binary.
- **The omitted CPRG file `cfr_player.c` is a player, not a generator.** Its only source-level
  effect, `PLAYER_OBJECT` in `betting_tools.h:23-25`, adds a `parent` pointer for upward tree
  traversal — the signature of strategy lookup. Confirmed by the `.so` plugin architecture
  visible in the LBR logs.
- **The thesis contains no DeepStack data-generation information.** Zero hits for cluster,
  seed, RNG, MP2, Calcul Québec, 6144, core-years or pot sizes. The dataset sentence appears
  exactly once, in the preface; chapter 6's own narrative claims only "coordination and
  infrastructure".

---

## 5. Why reconstruction is impossible — two independent proofs

### 5.1 Knowing the seed is not sufficient (experiment)

The LBR logs pair a printed seed with the cards actually dealt on MP2. A faithful
reimplementation of the released chain — `init_genrand`, `genrand_int32`, `dealCard`,
`dealCards`, `makeCard`, the card character tables — diverges from the first card.

**372 combinations** were then tested: both RNG families, six glibc state lengths, both deck
construction orders, both card encodings, three draw reductions, both swap policies, three
deal orders, three stream offsets, incremental versus full-shuffle. **Zero matches.**

Every input that should suffice was known — seed, game definition, RNG source, and ground
truth to check against — and reproduction still failed. The generator lives in unreleased
code.

### 5.2 Having the source would not be sufficient either (measurement)

The DeepStack supplement's range generator splits a hand set at `|S₁| = ⌊|S|/2⌋` so that
hands in `S₁` have strength no greater than those in `S₂`. The wording was **corrected
between arXiv v2 and v3** from "lower hand strength than" to "hand strength no greater
than" — an acknowledgement that ties exist — but no tie-breaking rule was ever specified.

In Burch's code the corresponding array comes from `getHandList()`
(`card_tools.c:117-171`), sorted by

```c
static int compareHandByRank( const void *a, const void *b )
{ return ( (Hand *)a )->rank - ( (Hand *)b )->rank; }
```

A bare rank difference, no secondary key, passed to `qsort` — which the C standard does not
require to be stable, and which glibc implements as merge sort or quicksort depending on
whether it can allocate a buffer.

**Measured extent.** On turn boards, all 1128 hole-card combinations enumerated, the
recursion simulated, every hand in a tie group crossed by a cut marked:

| metric | undetermined |
|---|---|
| by combination rank | 8 978 / 9 024 = **99.5 %** |
| by the supplement's own hand-strength definition | 9 022 / 9 024 = **100.0 %** |

Cause: a turn board admits only **36–133 distinct strength values** among 1128 hands, so the
roughly ten-level recursion exhausts distinct values long before it exhausts levels. Blockers
do not help; under the supplement's definition the count is sometimes *lower*.

**One reading would avoid this:** grouping by distinct strength value and cutting at the
nearest group boundary. That would be deterministic but would violate `|S₁| = ⌊|S|/2⌋` as
written. Available sources cannot decide between the two readings.

### 5.3 Consequence

| Would it suffice for bit-exact reproduction? | |
|---|---|
| Recovering the original `rngseed` | No — §5.1 |
| Recovering the original R(S,p) source | No — §5.2 |
| Both, plus identical libc and its `qsort` mode on the generating machines | Only then |

**Bit-exact equivalence with the original is not an attainable goal.** The attainable goal is
distributional equivalence: the published specification plus an explicit, deterministic,
documented tie-breaking rule of one's own.

---

## 6. The one open branch

**`project_uoapoker`** — the internal CPRG Subversion repository, leaked in over 400 LBR log
headers as

```
/home/viliam/cprg/project_uoapoker/trunk/src/c/meta_player.so
/home/viliam/cprg/project_uoapoker/trunk/src/c/acpc14.map
```

matching the `trunk` layout the CFR+ `Makefile` exports from. Documented contents:
`meta_player.so`, `rgbr_nl_cprg.so`, `translation_player.so`, `acpc14.map`, `cfr_player.c`,
and — from `translation_player.args.CFRplus_holdem_nolimit_FCPA` — an internal **no-limit
CFR+** variant, the closest known relative of the DeepStack-era HUNL solver.

**Path correction for any archive search:** CPRG home directories used first names.
`bm_server.config` authorises `user neil`; the LBR paths show `/home/viliam/`. The likely
historical path is therefore `/home/neil/cprg/project_uoapoker/trunk/`, **not**
`/home/nburch/` or `/home/burch/`. The documented personal web prefix is `~burch`.

**Ranked remaining targets**, all outside the investigation environment:

1. The CPRG SVN repository or a server backup of it
2. Wayback CDX enumeration of `webdocs.cs.ualberta.ca/~burch/*` and `poker.cs.ualberta.ca/*`,
   filtered to `.tar.gz|.tar.bz2|.zip|.sh|.pbs|.job|.log|.t7`
3. Software Heritage origin search for `nburch`, `burch`, `ualberta`, `pokersource`
4. Authenticated GitHub code search for `changes made on 2005/9/7 by Neil Burch`
5. ERA deposit manifest for item `db44409f-b373-427d-be83-cace67d33c41`
6. Calcul Québec / Compute Canada allocation records for CPRG, 2015–2016
7. **Asking Burch.** A question he could answer in one sentence:
   *"All three versions of the DeepStack supplement carry the pot bin `[100, 100)`, and the
   R(S,p) tie-breaking wording was revised between v2 and v3. What did that first bin
   actually do in the implementation, how were equal-strength hands split, and was the
   data set you generated the turn, flop, or auxiliary one?"*

---

## 7. Facts, hypotheses, and prohibitions

### Facts — each verified against a primary source with line references in the ledger

1. Burch authored the CPRG MT19937 wrapper, dated 2005-09-07; byte-identical across the
   CFR+ and ACPC releases.
2. CFR+ exposes `rngseed=` (default 1) and derives per-subgame state as
   `initstate_r(rngSeed ^ subgameIndex, buf, 32, state)`.
3. That path is glibc `random_r`, not MT19937, and samples boards only.
4. MT19937 is unreachable dead code in the CFR+ solver.
5. CFR+ contains no data-generation, range-generation or pot-size code, and no CFV export.
6. CFR+ is fully deterministic given `rngseed`; no `rand()`, `/dev/urandom`, or pid entropy.
7. The public archive was exported from an SVN `trunk` with metadata stripped and
   `cfr_player.c` omitted.
8. The thesis mentions the data set once, in the preface; chapter 6 does not repeat it.
9. `[100, 100)` — a mathematically empty interval — appears in the original LaTeX of all
   three arXiv versions and survived peer review unchanged.
10. The R(S,p) tie wording was corrected between v2 and v3 and remains underdetermined.
11. `omit_iters` is a property of the online solver only, per-round; the offline generator is
    described as plain CFR⁺ at 1 000 iterations.
12. The published LBR table reproduces from the released raw logs using the team's own
    aggregation script, in 12 of 13 cells, once units are pinned (×10 for the 20 000-stack
    game, ×500 for the 100BB game).
13. The released archive holds more data than was published: `dsFCPA` has 30 seeds on disk,
    the printed figure matches seeds 1–20 to a tenth of a milli-big-blind.
14. Burch's own signed, unpublished technical comment survives only in arXiv v3 of 1303.4441.
15. CFR-D had no cluster funding; the Compute Canada / Calcul Québec relationship appears
    first with DeepStack, bounding data generation to roughly 2015 – Q3 2016.
16. Burch has no public git repository containing poker code.

### Hypothesis — unproven

The missing DataGenerator most likely lived in `project_uoapoker`, alongside the internal
no-limit CFR+ variant. Supported by the SVN export, the missing CFV export, the omitted CPRG
bridge, and the thesis's reference to validating against "an independent codebase". **Does
not prove code reuse, RNG reuse, or repository identity.**

### Must not be inferred

- DeepStack RNG equals `rngSeed ^ subgameIndex`
- DeepStack RNG equals MT19937 — **disproved for the CFR+ lineage**
- `[100, 100)` should be silently corrected to `[100, 200)` — the source says otherwise in
  all three versions; any correction is an engineering decision, not a reconstruction
- Online `omit_iters` applies to the offline generator — **disproved**
- CFR+ solver options imply offline data-generation options
- DeepStack-Leduc or later mirrors are a HUNL oracle
- The `\NBTODO` macro defined in the DeepStack preamble makes that source a Burch artifact —
  the macro is provisioning; no `\NBTODO{…}` invocation survives

---

## 8. Actionable conclusions for a DataGenerator implementation

Nothing in this investigation authorises changing an existing generator or its golden tests.
Three commonly debated rules are now settled by primary evidence:

| Rule | Basis |
|---|---|
| Do not "fix" `[100, 100)` to `[100, 200)` | Present in all three source versions including post-review; the authors edited the same passage between v2 and v3 and left this bin alone |
| Do not carry `omit_iters` into the offline generator | Two different solvers; omission is a per-round property of the online CFR hybrid |
| Do not aim for bit-exact parity with the original | §5 — proved twice, independently |

**Fingerprint set** for testing any future candidate claiming to be Burch's generator:

- `initstate_r(seed, buf, **32**, state)` — non-default glibc TYPE_1
- `seed ^ index` derivation per worker or subgame
- canonical suit-isomorphism classes carrying `weight`, renormalised only downstream
- partial Fisher–Yates with `t %= (num - i)`
- canonical groupings in the trunk, non-canonical in subgames — stated in Burch's own
  unpublished comment and matching his implementation

---

*Prepared as a handoff. Every claim above is traceable to a line reference, file hash or
reproducible computation in `docs/burch-forensics.md`.*
