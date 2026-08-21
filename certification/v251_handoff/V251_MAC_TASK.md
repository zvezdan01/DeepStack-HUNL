# V251 MAC TASK — Multi-State CFV Object / Corpus Discrimination

## Objective

Run the current source-audited DeepStack-2017 HUNL river solver/tree path on the **same multi-state corpus used by the prior V106/V107 experiment** (or recover those exact states from the project artifacts), but this time retain raw first-layer CFV tensors so we can test the two source-real Table-S4 reporting candidates correctly:

1. action-conditioned opponent CFVs `v_-i(a)`;
2. true root/parent opponent CFV `v_-i(s)` reconstructed as the sum over **all** first-layer child opponent CFVs, including FULL-only actions.

The task is to determine whether the published Table-S4 crossing fingerprint:

- `P -> 1/2P+P`: `++-`
- `P -> P+2P`: `++-`
- `P+2P -> 1/2P+P+2P`: `--+`

appears after averaging over the recovered multi-state corpus.

This task must **not** introduce new ad-hoc action weights, player weights, nonlinear reductions, or external poker-system semantics.

---

## Scientific context

The following project conclusions are inputs, not things to re-derive:

- V224: V218's action-CFV-only source lock was withdrawn. Both action-conditioned opponent CFVs and true root/parent opponent CFVs are source-real candidates.
- V224: true root error must be:
  `sum_a sparse_v2(a) - sum_a FULL_v2(a)`,
  not merely a sum over common-action pairwise errors.
- V225: the current V95 collection point matches Algorithm-S1 reach/weighting semantics:
  acting-player reach is multiplied by current strategy inside recursion, opponent parent value is the unweighted child sum, and action CFVs are collected before regret update.
- V223: simple both-player aggregation does not rescue the one-state V95 crossing mismatch.
- V250: do not invent progressively richer scheduler Boolean models as historical evidence.
- The current strongest unresolved question is whether the V95 one-state failure is a corpus/state artifact or an upstream tree/solver semantic mismatch.

---

# HARD RULES

1. **Do not import Supremus, CPRG, Leduc, Libratus, Pluribus, Slumbot, etc. as DeepStack facts.**
2. Use only:
   - primary DeepStack supplement semantics already encoded in the current audited path;
   - current project code/artifacts;
   - exact V106/V107 state definitions if recoverable.
3. Do not tune any metric to Table-S4 numbers.
4. Do not choose action subsets or weights after observing the paper fingerprint.
5. Do not silently replace the solver/tree configuration.
6. Every state, menu, seed/config, retained iteration count, and SHA256 must be logged.
7. Preserve raw tensors. Do not save only final norms.
8. If the exact V106/V107 corpus cannot be recovered, STOP and report exactly what artifacts are missing. Do not substitute random states and call the task complete.

---

# PHASE 0 — Recover the exact V106/V107 states

Search the local project recursively for artifacts associated with V106/V107, including:

- state JSON/NPZ/PKL files;
- board/range/pot/stack definitions;
- runner scripts;
- logs;
- seeds;
- hashes;
- any list of the 9 river situations.

Likely search tokens:

`V106`
`V107`
`nine_state`
`9_state`
`Table S4`
`board`
`range`
`pot`
`river`
`state`
`corpus`

Create:

`out/v251_state_inventory.json`

with, for each recovered state:

```json
{
  "state_id": "...",
  "board": "...",
  "pot": 0,
  "stack": 0,
  "range_p1_source": "...",
  "range_p2_source": "...",
  "source_artifact": "...",
  "sha256": "..."
}
```

PASS condition for Phase 0:

- exact prior state set recovered, with at least all states actually used in V106/V107;
- if V106/V107 truly used 9 states, exactly those 9 must be listed.

If exact states are not recoverable:
- produce `V251_BLOCKED.md`;
- list every searched path;
- list missing information;
- STOP.

---

# PHASE 1 — Freeze the solver/tree path

Use the current audited V95 backend as the baseline implementation.

Locate the exact source used for the current V95 full-iteration run, especially:

- `v95_table_s4_hybrid.py`
- chunk/runner script
- action-menu definitions
- skip/omission logic

Record SHA256 for every code file used.

Create:

`out/v251_code_manifest.json`

Required fields:

```json
{
  "solver_files": [
    {"path":"...", "sha256":"..."}
  ],
  "sparse_iterations": 1000,
  "sparse_skip": 500,
  "full_iterations": 4000,
  "full_skip": 2000,
  "float_dtype": "...",
  "device": "...",
  "python": "...",
  "numpy": "..."
}
```

Do not change solver semantics unless required only to emit raw tensors.

Instrumentation-only changes must be clearly separated and diffed.

---

# PHASE 2 — Run all Table-S4 sparse menus + FULL on every recovered state

Menus to solve:

- `2P`
- `1/2P`
- `P`
- `1/2P+P`
- `P+2P`
- `1/2P+P+2P`
- `FULL`

Use the same menu encoding currently used by V95/V106/V107.

For every `(state, menu)` save raw NPZ:

`raw/<state_id>/<menu>.npz`

Minimum required arrays:

- `opp_action_cfvs`
  - retained-iteration average or raw accumulator + retained count
  - shape `[n_first_actions, hand_axis]`
- `own_action_cfvs` if already available in the backend
- `pm` or exact legal-private-hand mask
- action identifiers in a sidecar JSON if NPZ cannot store them safely
- retained iteration count
- any state metadata required to reconstruct units

If the backend internally stores unnormalized sums:
save the sums **and** retained count.

Expected private-hand axis:
- raw 1326 possible unordered hole-card combinations may exist internally;
- exact river legal-hand mask should leave `1081` coordinates.

Verify and log:
`pm.sum() == 1081`

for every state.

---

# PHASE 3 — Compute source-real candidate A: TRUE ROOT/PARENT opponent CFV

For each state and menu:

```python
root_opp(menu) = sum_over_ALL_first_layer_actions(opp_action_cfvs[menu])
```

FULL root must include **all FULL first-layer actions**, including actions absent from sparse menus.

Then:

```python
error_root(menu) = root_opp_sparse(menu) - root_opp_FULL
```

restricted to the 1081 legal river hands.

For each state/menu compute ordinary:

- `L1 = sum(abs(error))`
- `L2 = sqrt(sum(error^2))`
- `Linf = max(abs(error))`

Then average the **norms over states**, because Table S4 reports per-state errors averaged over situations.

Do NOT concatenate state vectors and norm afterward.

Create:

`out/v251_true_root_metrics.json`

with:
- per-state triples;
- mean triples across corpus;
- crossing signatures.

Crossing signature order is `(L1,L2,Linf)`.

Required paper target:

```text
P -> 1/2P+P          ++-
P -> P+2P            ++-
P+2P -> triple       --+
```

---

# PHASE 4 — Candidate B: action-conditioned opponent CFVs

Do NOT invent a new weighted reduction.

Compute only the following pre-declared source-neutral diagnostics:

### B1. Common physical action primitive metrics

For actions physically common between sparse row and FULL:

- call/check
- matching sparse bet sizes
- all-in if represented and nonzero

For each action separately:

```python
error_a = v_sparse(a) - v_FULL(a)
```

over 1081 legal hands.

Store per-state and mean norm triples.

### B2. Full sparse-row action-block concatenation

For each sparse menu, concatenate its own first-layer action-error blocks against matching FULL actions in a deterministic declared action order.

This is diagnostic only; V220/V222 already constrain this family.

### B3. Sum over matched/common action errors

Store separately from true root:
```python
sum_common_errors = sum_{a common} [v_sparse(a)-v_full(a)]
```

This must NOT be mislabeled as root error.

Create:

`out/v251_action_conditioned_metrics.json`.

---

# PHASE 5 — Optional player-axis audit

Only if the raw backend exposes both player channels without changing solve semantics.

Compute:

- player-0 root error
- player-1 root error
- both-player concatenation

per state and corpus mean.

This phase is optional and must not block the main task.

---

# PHASE 6 — Crossing-fingerprint decision

Produce one machine-readable summary:

`out/v251_crossing_summary.json`

Schema:

```json
{
  "states": 9,
  "true_root": {
    "mean_norms": {
      "P": [0,0,0],
      "1/2P+P": [0,0,0],
      "P+2P": [0,0,0],
      "1/2P+P+2P": [0,0,0]
    },
    "crossings": ["...", "...", "..."],
    "paper_match_edges": 0,
    "full_match": false
  },
  "action_diagnostics": {},
  "paper_target": ["++-","++-","--+"]
}
```

Also report per-state crossing signatures to show whether the mean is caused by a stable pattern or state cancellation.

---

# PHASE 7 — Required interpretation

Use exactly one of these result classes.

## CLASS A — Genuine multi-state root-CFV match

If true-root corpus mean gives exactly:

`["++-","++-","--+"]`

then this is a genuine milestone.

Report:
- exact mean norm triples;
- state count;
- per-state signatures;
- raw artifact hashes;
- whether result survives all recovered states or arises from cancellation.

Do NOT claim bit-exact Table-S4 reproduction unless the absolute L1/L2/Linf values also match the paper within publication precision.

## CLASS B — Crossing improvement but not full match

If root candidate moves materially toward the paper fingerprint versus V95 one-state but is not exact:
- report exact edge/component score;
- no historical claim;
- identify which crossing components remain wrong.

## CLASS C — Multi-state root candidate still fails strongly

If true-root corpus mean still gives 0/3 or similarly strong mismatch:
- state explicitly that reporting-object/corpus averaging is unlikely to explain the V95 failure;
- raise priority of upstream continuation-tree / historical corpus-generation semantics.

## CLASS D — Blocked exact-state recovery

If exact V106/V107 states are unrecoverable:
- stop;
- do not replace them with random states.

---

# REQUIRED OUTPUT DIRECTORY

Produce exactly:

```text
V251_MAC_RESULT/
  V251_RESULT.md
  v251_state_inventory.json
  v251_code_manifest.json
  v251_crossing_summary.json
  v251_true_root_metrics.json
  v251_action_conditioned_metrics.json
  raw/
    <state_id>/
      2P.npz
      HP.npz
      P.npz
      HP_P.npz
      P_2P.npz
      HP_P_2P.npz
      FULL.npz
      actions.json
  logs/
  tests/
  SHA256SUMS.txt
```

If blocked, replace result directory with:

```text
V251_MAC_RESULT/
  V251_BLOCKED.md
  v251_state_inventory_partial.json
  searched_paths.txt
```

---

# TESTS THAT MUST PASS

At minimum:

1. `pm.sum()==1081` for every state/menu.
2. retained iteration counts exactly equal configured values.
3. true root uses ALL actions of sparse and ALL actions of FULL independently.
4. common-action sum is not confused with root error.
5. averaging order is:
   `norm per state -> average norms`.
6. sparse and FULL state metadata are identical within each state.
7. action IDs are deterministic and physically matched correctly.
8. raw NPZ tensors are finite.
9. SHA256 manifest covers every raw NPZ and source file used.
10. paper crossings are computed from corpus-mean norm triples without any fitted rescaling.

Run:
`pytest -q`

and preserve the full log.

---

# DO NOT DO

- no action-weight optimization;
- no player-weight optimization;
- no menu-dependent metric selection;
- no scale fit to paper L1/L2/Linf;
- no cherry-picking states;
- no random replacement corpus;
- no use of Supremus/CPRG/Leduc semantics as DeepStack facts;
- no claim of reproduction from crossing signs alone.

---

# FINAL MESSAGE BACK TO ADAM

Return only:

1. status: PASS / FAIL / BLOCKED;
2. exact state count;
3. true-root mean norm table;
4. three crossing signatures;
5. paper edge-match count;
6. absolute paper metric comparison if available;
7. test count;
8. path to ZIP containing `V251_MAC_RESULT`;
9. one paragraph stating the strongest justified conclusion and nothing stronger.
