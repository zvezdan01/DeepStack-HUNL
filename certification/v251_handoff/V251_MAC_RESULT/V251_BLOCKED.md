# V251 — BLOCKED (CLASS D: exact V106/V107 state corpus not recoverable)

Date: 2026-08-21. Environment: Claude Code remote container, project
`/home/user/quant-trade` (branch `claude/huhl-deepstack-certification-tutg3b`).
Handoff pack SHAs:
- `DEEPSTACK_V251_MAC_MULTISTATE_CFV_DISCRIMINATION_TASK.zip`
  `520c5d34b1d7e32444f830592fadc02c2c6b3faa4f35374d79ab4fdd5ecda2c`
- `DEEPSTACK_V251_MAC_ADDENDUM_V253.zip`
  `c3c615350a2bec98fdda98a1c08a912eaaa55543c4c1deb25639eeb98ee2ec15`

## Verdict

**BLOCKED.** Phase 0 (recover the exact V106/V107 multi-state corpus) FAILED:
no artifact, file, log, commit, or upload in this environment contains any
V106/V107 state definition, nor any file of the V-numbered project lineage the
task references (V95, V106/V107, V218–V225, V250, `v95_table_s4_hybrid.py`).

Per HARD RULE 8 and result CLASS D of `V251_MAC_TASK.md`, no solver runs were
performed and **no substitute corpus was generated**. Zero CFR iterations were
executed for this task.

## Why this environment cannot contain the corpus

This machine hosts a *different* DeepStack reconstruction lineage than the one
the handoff addresses. The local project's milestone history is: Leduc
bit-exact certification → Phase 2A/2B Leduc datagen → HUNL gates G1.1–G1.8 →
HUNL Golden Baseline v0/v1 (exact river resolver + exact turn engine) → turn
datagen pilot (currently running). It has never had V-numbered milestones, a
`v95_table_s4_hybrid.py` backend, or a V106/V107 nine-state experiment. The
handoff README says the pack "is intended to be handed directly to Claude/Codex
on the Mac that contains the active DeepStack reconstruction project" — this
container is not that Mac and has no filesystem access to it.

## Search evidence (exhaustive, all negative)

See `searched_paths.txt` for the full list. Summary:

1. **Working tree** `/home/user/quant-trade` — recursive case-insensitive
   content grep for `v106`, `v107`, `v95_`, `nine_state`, `9_state`,
   `table s4`/`table_s4`: 0 hits.
2. **Full git history (all refs)** — commit-message grep and content pickaxe
   (`git log --all -S`) for `V106`, `V107`, `v95_table_s4`, `nine_state`:
   0 hits.
3. **Filename sweep** over `/home`, `/root`, `/workspace`, `/tmp` for
   `*v106*`, `*v107*`, `*v95*`, `*nine_state*`, `*9_state*`, `*s4*`,
   `*corpus*`: only unrelated matches (AGT course test fixtures
   `...deltas4.npz` etc.).
4. **/workspace reference clones** (deepstack_leduc_v1.1-bitexact-certified,
   deepholdem, dyypholdem, deeperstack, coms4995-finalproj) — content grep:
   0 hits.
5. **All 14 session uploads** in `/root/.claude/uploads/...` — filenames and
   ZIP listings scanned: the only V251-related files are the two handoff ZIPs
   themselves (which contain no state data).
6. **/tmp scratchpads** — 0 hits.

## Missing information (what the Mac must provide)

To unblock, the handoff needs to include (any one of these forms):

- the V106/V107 state artifacts themselves: per-state board cards, pot, stack,
  and both players' range vectors (JSON/NPZ/PKL), with their SHA256s; **or**
- the V106/V107 runner scripts + seeds + the RNG/code that generated the
  states, sufficient to regenerate them deterministically; **and in both cases**
- `v95_table_s4_hybrid.py` plus its chunk/runner scripts, menu encodings and
  skip/omission logic (Phase 1 requires SHA-anchoring this exact backend, and
  Phases 2–6 require running *it*, not a re-implementation);
- V106/V107 logs/manifests confirming the exact state count (9 or otherwise).

## Primary-source context (input, not a substitute)

The verified supplement (arXiv 1701.01724v3, p.22–23) presents this ablation
as **Table 5**: L1/L2/L∞ errors in mbb/g of counterfactual values from 1,000
CFR iterations on sparse trees, **averaged over 100 random river situations**,
with ground truth = the 9-betting-option tree at 4,000 iterations. The paper
does not publish the situations themselves, and the omitted-iteration counts
are not stated (consistent with Addendum V253: totals 1000/4000 are
source-locked; S4 omission counts are not). None of this licenses substituting
new random states for the exact V106/V107 corpus, so it does not unblock
Phase 0.

## What is available here (for planning only)

This environment does contain an independently certified exact HUNL river
stack of its own lineage (1326-hand exact river resolver, ACPC-oracle betting
trees, RM+/simultaneous/uniform-post-omit hybrid solver, frozen as HUNL Golden
Baseline v1 at `34a50560...`). If Adam ever *wants* a fresh-corpus Table-5
style experiment on this stack, that would be a new task with its own
protocol — it would not be V251, whose decision question is specifically about
the *prior* V106/V107 corpus under the *V95* backend.

## Required final answers (per task §FINAL MESSAGE)

1. status: **BLOCKED**
2. exact state count: **0 recovered** (required: exact V106/V107 set)
3. true-root mean norm table: not computed (blocked at Phase 0)
4. crossing signatures: not computed
5. paper edge-match count: n/a
6. absolute paper metric comparison: n/a
7. tests: no solver tests run (nothing to test; fail-closed stop)
8. result ZIP: `V251_MAC_RESULT.zip` (this directory: BLOCKED variant)
9. strongest justified conclusion: the V106/V107 corpus and the V95 backend
   exist only on the originating Mac; this container's project is a disjoint
   reconstruction lineage, so V251 cannot be executed here without the Mac
   artifacts listed above — and running it on substitute states would answer a
   different question than the one V251 poses.
