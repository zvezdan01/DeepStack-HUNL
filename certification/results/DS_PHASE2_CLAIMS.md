# DS PHASE 2 — RE-VERIFICATION OF EXISTING CLAIMS (no inherited results)

Every claim from CERTIFICATION_REPORT.md / RELEASE_NOTES.md / audits was
re-executed fresh at HEAD eb7b21d in this session's environment
(Python 3.11.15, numpy 2.4.6, torch 2.13.0-cpu, bundled Torch7 OpenBLAS).
Comparators written for this audit live in `certification/ds_scripts/`
(the DS repo itself was not modified).

| # | Claim (source) | Re-run method | Fresh result | Classification |
|---|---|---|---|---|
| 1 | Public tree 653/653 nodes structural (CERT §tree) | `regen_tree_manifest.py` — Python manifest regenerated from current code, diffed vs bundled Lua manifest | **653/653 rows exact** | TRACE_EXACT (structural) |
| 2 | One complete CFR iteration 232/232 tensors, zero tolerance (CERT §one-iteration) | bundled `compare_lua_trace.py lua_trace` | **PASS: 232 tensors** | BIT_EXACT vs frozen Lua trace |
| 3 | 480/480 tensors r300→call all private/board combos (CERT) | **claim had no committed comparator** — written fresh (`compare_private_boards_480.py`) mirroring the bundled exporter | **480/480 BIT-EXACT PASS** (30 cases × 16 tensors) | BIT_EXACT |
| 4 | 3720/3720 all 5 first-street chance histories × 30 combos (CERT) | bundled `compare_all_chance_histories.py` | see DS_PHASE6 (long run) | — |
| 5 | 744/744 P2 first-street (CERT) | bundled `compare_p2_all_street1.py` | see DS_PHASE6 | — |
| 6 | 108/108 first-street terminal leaves (CERT) | bundled `compare_terminal_all_street1.py` | see DS_PHASE6 | — |
| 7 | 20340/20340 street-2 exhaustive stage-by-stage (CERT) | bundled `compare_street2_exhaustive.py` | see DS_PHASE6 | — |
| 8 | NN feed-forward + zero-sum correction bit-for-bit (CERT §value net) | **orphan traces without comparators** — written fresh: `compare_nn_root_trace.py` (11 layer outputs + full corrected output vs `nn_root_trace`), `compare_nn_boxes.py` (8 next-street box input/value tensors) | **11/11 + 1/1 + 8/8 all byte-equal** | BIT_EXACT |
| 9 | PyTorch layers vs Torch7 checkpoint caches < 1e-4 (WEIGHTS_AUDIT) | in `pytest` suite (test_original_checkpoint) | PASS | NUMERIC_MATCH (explicitly tolerance-based — different BLAS; NOT a bit-exact path; the bit-exact resolve path uses `_torch7_exact_inference`, row 8) |
| 10 | Deterministic e2e hand regression (CERT/RELEASE) | in `pytest` suite (test_end_to_end_bitmatch: 6/6 + 16/16 checkpoints + 3/3 terminal tensors via continual_street2_lua_trace) | PASS | BIT_EXACT vs frozen Lua trace |
| 11 | Full suite 36/36 (CERT) | fresh `pytest -q` | **36/36 in 33.25 s** | PASS |
| 12 | Original weights byte-for-byte from original archive (WEIGHTS_AUDIT) | SHA-256 chain: bundled model == reference_lua copy == **public upstream lifrordi/DeepStack-Leduc @ da416f96** (`d5fcba44…`, info `9ff711ff…`) | identical | BIT_EXACT provenance |
| 13 | reference_lua is the canonical original implementation (README) | `diff -rq` vs freshly cloned public upstream `Source/` | **byte-identical** (Data differs only by absent GPU model + Dot/) | BIT_EXACT provenance |
| 14 | `final_cpu.info` valid_loss reproducibility (WEIGHTS_AUDIT) | not re-run — the repo's own audit already documents the archived sample set does not reproduce the recorded loss; info value is not used as acceptance | NOT_TESTABLE (as documented) |

## Known scope boundaries confirmed
- The Lua traces are frozen `.t7` (genuine Torch7 serialization) exports; no
  Lua/Torch7 runtime exists in this container (or in the repo author's, per
  ITERATION_AUDIT.md), so the Lua side cannot be re-executed here. Its source
  is byte-identical to public upstream (row 13), the exporters are committed
  and reviewed, and the trace formats are Torch7-native. Classification of
  rows 2–8, 10 is therefore "bit-exact against the frozen author-side Lua
  trace", with trace provenance = authentic-source + committed exporters.
- Random action sampling (RNG) is excluded from the certified scope by the
  repo's own report; deterministic paths only. Re-confirmed: certified paths
  call no RNG.
