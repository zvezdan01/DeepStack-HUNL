# FINDINGS — DeepStack HUNL DataGenerator forensic hunt

Session: `claude/generator-dat-pro-huhl-forenzic-rvclmx`, 2026-08-14/15.
Status: **IN PROGRESS** (live document; every claim carries an evidence tier).

## 1. Executive summary

No Tier-1 original artifact (A–E) found yet. The fork network of the
official DeepStack-Leduc release contains NO hidden original material
(exhaustively enumerated, 223 forks, 6 with own commits, all
community-side). Strong Tier-3 genealogy evidence was recovered for the
RNG/seed/job-culture components: the CPRG lineage uses one specific
MT19937 implementation file (byte-identical `rng.c` across the ACPC
server, Gibson's open-pure-cfr, and the DeepStack-Leduc reference tree),
explicit CLI seeds recorded into output artifacts, deterministic
per-worker seed derivation, and PBS/qsub batch conventions carried into
the closest descendant project (TensorCFR/beyond-deepstack).

Network constraints of this container (see SEARCH_LOG capability map):
arxiv.org, zenodo.org, poker.cs.ualberta.ca and web.archive.org are
egress-blocked; GitHub (git + HTML) and WebSearch work. Raw mirroring of
arXiv/Zenodo/ualberta artifacts is impossible from here — those leads
are pursued via search snippets and GitHub mirrors, and remain OPEN, not
exhausted.

## 2. New artifacts toward A–E

### D (RNG seed/config) — Tier 3 progress, no Tier 1 yet
- **`rng.c` monoculture proven**: SHA-256 `0e4a4d7ac3d31050…` is
  byte-identical in (a) `third_party/CFR_plus/rng.c` (Tammelin),
  (b) DS workspace `reference_lua/ACPCServer/rng.c`, (c) the public
  `project_acpc_server` mirror, (d) `open-pure-cfr/acpc_server_code/rng.c`
  (Gibson, with Burch/Johanson contributions). MT19937 with
  `init_genrand`/`init_by_array`/`genrand_int32`. The entire CPRG
  ecosystem shares ONE RNG file. [Tier 3]
- **open-pure-cfr seed conventions** (`parameters.cpp`, `pure_cfr.cpp`):
  default 4-seed vector `{6,12,1983,28}`; CLI `--rng=<s1:s2:s3:s4|TIME>`;
  per-thread derivation `seeds[i] = base[i] + 1234 + 4*thread_num + i`
  then `init_by_array`; seeds dumped into result files
  (`RNG_SEEDS %u %u %u %u`). Concrete CPRG worker-seed-derivation
  fingerprint + "seeds live in output artifacts" culture. [Tier 3]
- **TensorCFR (beyond-deepstack, Lisý/Rudolf/Ha)**: explicit
  `--seed`/`--size` CLI on `generate_data*` scripts, wave derivation
  `seed = seed_offset + generation * size_of_generation`, datasets
  organized as per-seed files, Metacentrum `#PBS` job scripts for both
  generation and training. GitHub mirror `mathemage/TensorCFR` (full
  2886-commit history; GitLab origin egress-blocked/403). [Tier 3]

### E (cluster/job) — Tier 3 conventions only
- TensorCFR `#PBS -N …` batch scripts (generation + training) confirm
  the PBS/qsub convention in the immediate descendant lineage;
  consistent with (but not proof of) the MP2 Torque/PBS inference for
  the original 6,144-core run. [Tier 3 / Tier 5 for MP2 details]

### A/B/C (range generator / DataGenerator / raw samples) — nothing new
- DeepStack-Leduc fork network (223 forks): **exhaustive `git ls-remote`
  sweep**; only 6 forks carry own commits (andreayres: unrelated
  notebook; hmate9: `from_turn.game` + debug print; sjtuwy: community
  NLHE-HU adaptation of the Leduc code [Tier 4 fossil]; snarb: caching;
  xiaoyjy: run scripts; mathemage: two small `tree_builder.lua` patch
  branches). **No original HUNL material anywhere in the network.**
  [exhaustive NEG]
- Upstream `lifrordi/DeepStack-Leduc`: full clone confirms only 2
  commits (2017-04-05, Martin Schmid), code imported in a single
  "Initial commit" — no development history to mine. [NEG]
- Martin Schmid's GitHub account has only 5 repos (webpage, 3 course
  repos, DeepStack-Leduc) — no hidden research code. [NEG]

### Corroborations of published facts (Tier 2)
- Search-snippet confirmation of supplementary wording: "pot sizes
  selected from the intervals … [2000,6000) or [6000,19950] with uniform
  probability, followed by uniformly selecting an integer from within
  the chosen interval" (poker.cs.ualberta.ca supplementary PDF, blocked
  for direct fetch).
- Burch PhD thesis located: `Burch_Neil_E_201712_PhD.pdf` ("Time and
  Space: Why Imperfect Information Games are Hard"); search snippet
  confirms the "generated one data set used to train the evaluation
  function" statement. Direct PDF fetch egress-blocked. [Tier 2]

## 3. Bit-exact implications so far

- RNG family choice (MT19937 of the ACPC `rng.c` line) is now supported
  by a THREE-repo byte-identity plus the descendant projects' habits —
  it remains PROJECT CANONICAL for our generator but is the only
  RNG family with positive genealogical evidence.
- Seed-in-artifact culture (open-pure-cfr dumps, ACPC log headers,
  TensorCFR per-seed files) supports the hunt for E-artifacts: if any
  original DeepStack job log survives, it likely CONTAINS its seeds.
- ACPC dealing inheritance is REAL in the CPRG line: open-pure-cfr calls
  the ACPC `dealCards` directly for hand generation — precedent for the
  rejection/modulo card sampler family in offline solvers.

## 4. Confidence / evidence tiers

See EVIDENCE_TABLE.csv. Nothing above Tier 2 for first-party facts;
Tier 3 for all genealogy conventions; Tier 4 fossils recorded as such.

## 5. What remains unknown

See UNRESOLVED.md (unchanged core unknowns; [100,100), offline CFR+
semantics, master seed, serialization all still open).
