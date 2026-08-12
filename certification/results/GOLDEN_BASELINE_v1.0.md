# CERTIFIED GOLDEN BASELINE v1.0 — FREEZE RECORD

Status: FROZEN (pending final source-fidelity verdict — see
DS_SOURCE_FIDELITY_AUDIT.md; this record is valid only together with that
verdict).

## Identity

| Item | Value |
|---|---|
| Repository | `zvezdan01/deepstack_leduc_v1.1-bitexact-certified` |
| Golden commit | **`eb7b21d1cffcccb786093f808721a592f57e21d0`** |
| Certification branch (oracles + comparators + reports) | `zvezdan01/quant-trade` @ `claude/huhl-deepstack-certification-tutg3b` |
| Upstream provenance anchor | `lifrordi/DeepStack-Leduc` @ `da416f9646725def43e668851593de13ead8b607` (`reference_lua/Source` byte-identical; weights byte-identical) |
| Frozen upstream weights | `deepstack_leduc/models/final_cpu.model` SHA-256 `d5fcba4402cec46a9b02cea0f96cb78bda83f284ea36f6d5db84529e83eb59a1` |
| | `deepstack_leduc/models/final_cpu.info` SHA-256 `9ff711ffec93bf7b70ac8e405de9c72b67776ecf0f3f9cb8fba5c64e59fa482e` |

**`final_cpu.model` is immutable**: it remains the upstream baseline for all
future A/B tests. Any newly trained weights must be stored under a NEW file
name; nothing may overwrite these two files (re-verify both SHA-256 values
before every A/B run).

## Environment of record

| Item | Value |
|---|---|
| OS | Linux 6.18.5-fc-v20 x86_64, Ubuntu 24.04 userland |
| CPU | Intel Xeon @ 2.80GHz, x86_64 (bit-exact mode requires x86_64) |
| Python | 3.11.15 |
| numpy | 2.4.6 |
| torch | 2.13.0 (CPU) |
| pytest | 9.1.1 |
| gcc (oracle builds) | 13.3.0 |
| BLAS of record | repo-bundled `torch7_openblas.so.0` + `libopenblas_sandybridgep-r0.3.0.dev.so` + `libgfortran.so.3` via `LD_LIBRARY_PATH=<repo root>` |
| Config of record | `Config`: ante=100, stack=1200, cfr_iters=1000, cfr_skip_iters=500 |

## Complete reproduction command set

All commands from the DS repo root at the golden commit, on x86_64:

```bash
export DS=/path/to/deepstack_leduc_v1.1-bitexact-certified
export CERT=/path/to/quant-trade/certification   # certification branch checkout
cd "$DS"

# 0) identity + weights immutability
git rev-parse HEAD                      # must be eb7b21d1cffcccb786093f808721a592f57e21d0
sha256sum deepstack_leduc/models/final_cpu.model deepstack_leduc/models/final_cpu.info

# 1) full unit/regression suite (36/36)
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 -m pytest -q

# 2) one-iteration CFR trace (232/232)
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 reference_tools/compare_lua_trace.py lua_trace

# 3) street-2 exhaustive stage-by-stage (90 cases, 20340/20340)
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 reference_tools/compare_street2_exhaustive.py

# 4) all first-street chance histories (150 cases, 3720/3720)  [~1 h CPU]
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 reference_tools/compare_all_chance_histories.py

# 5) P2 first-street (36 cases, 744/744)                        [~30 min CPU]
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 reference_tools/compare_p2_all_street1.py

# 6) first-street terminal leaves (18 leaves, 108/108)
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 reference_tools/compare_terminal_all_street1.py

# 7) comparators added by this certification (in $CERT/ds_scripts):
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 "$CERT/ds_scripts/compare_private_boards_480.py"      # 480/480
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 "$CERT/ds_scripts/compare_continual_first_action.py"  # 6/6
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 "$CERT/ds_scripts/compare_nn_root_trace.py"           # NN layers 11/11 (+raw output via corrected path)
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 "$CERT/ds_scripts/compare_nn_boxes.py"                # NN boxes 8/8
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 "$CERT/ds_scripts/regen_tree_manifest.py"             # 653/653
LD_LIBRARY_PATH="$PWD" PYTHONPATH=. python3 "$CERT/ds_scripts/determinism_check.py"               # repeat + hash

# 8) primitive-layer oracles (Tammelin author source), from $CERT:
python3 "$CERT/scripts/cfrplus_replica_kuhn.py"    # KUHN  CFR+ AUTHOR-SOURCE BIT EXACT: PASS
python3 "$CERT/scripts/cfrplus_replica_leduc.py"   # LEDUC CFR+ AUTHOR-SOURCE BIT EXACT: PASS
for c in 10 100 1000 10000; do for s in 0 1 42 6874; do \
  python3 "$CERT/scripts/mt19937_independent.py" $s $c "$CERT/oracles/rng/mt_seed${s}_n${c}.bin"; done; done
sha256sum -c "$CERT/oracles/SHA256SUMS"            # oracle immutability
```

Expected: every command reports full PASS / bit-exact counts exactly as in
DS_FINAL_MATRIX.md; determinism hash for the street-1 root resolve:
`b1e35a1a495bf5b01ece7ef9086f791f32b68a35543996ef22f69353918173c1`.

## Rules going forward (Phase 2: dataset + new weights)

1. The golden commit's mathematical engine is immutable; any change
   invalidates the certificate and requires a re-run of this command set.
2. New training data generators/weights live alongside, never replacing,
   `final_cpu.model`; A/B comparisons always run against the frozen model.
3. Bit-exact claims are valid only on x86_64 with the bundled BLAS.
