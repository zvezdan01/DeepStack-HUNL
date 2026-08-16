# ORIGINAL DS WORKSPACE RECOVERED — owner-uploaded archives, fully verified

Date: 2026-08-14 (session claude/generator-dat-pro-huhl-forenzic-rvclmx).
The owner uploaded two zip exports of the DS workspace that died with the
2026-08-14 container reclaim. Both are `git archive` exports whose zip
comment carries the source commit SHA. Everything below was verified in
this session against anchors RECORDED IN THIS REPO before the loss.

## Archives (committed under `certification/leduc_restore/archives/`)

| archive | zip SHA-256 | embedded commit (zip comment) | matches recorded anchor |
|---|---|---|---|
| `deepstack_leduc_v1.1_golden-baseline-v1.0-m2m4_2ab6dde.zip` | `988ac333…d33f` | `2ab6dde943ebad2f5458779dc561ed203f796e39` | Golden Baseline freeze (GOLDEN_BASELINE_v1.0.md, D2 constraint line) |
| `deepstack_leduc_v1.1_phase2-datagen_7967622e.zip` | `7b909c04…ba7c` | `7967622e5b66e35a8e9a17506f97db86c2e6b543` | Phase-2 generator freeze (DS_D2_TORCH7_THREEWAY.md constraint line) |

## Content verification (phase2-datagen export, staged at /workspace/ds_restore/)

| artifact | verification | result |
|---|---|---|
| `libopenblas_sandybridgep-r0.3.0.dev.so` | SHA-256 vs FAILURE_MATRIX F-07 recorded `cd143947…` | **MATCH** |
| `reference_lua/ACPCServer/game.c` | SHA-256 vs G1_TREE_REPORT recorded `85b5325d…` | **MATCH** |
| `reference_lua/ACPCServer/evalHandTables` | SHA-256 vs evaluator `_KNOWN_FILE_SHA256` `9b8bb8e1…` | **MATCH** |
| `reference_lua/Data/Models/PotBet/final_cpu.model` / `.info` | SHA-256 vs DS_PHASE2_CLAIMS `d5fcba44…`/`9ff711ff…` (also == fresh upstream lifrordi clone @ da416f96) | **MATCH** |
| `lua_trace/` frozen corpus | file count vs D2 report (232 byte-identical files) | **232 present** |
| `datagen/th_random.py` (original certified RNG) | byte-stream equivalence vs the in-repo restored port: 6 seeds (0, 1, 42, 6874, master 20260814, shard0 1297610827) × u32(20k)/rand_float(20k)/random_range(5k × 4 ranges) | **BYTE-IDENTICAL 6/6** |
| `deepstack_leduc/` golden engine package | full source present (lookahead, cfrd_gadget, tree, terminal equity, …) | **RECOVERED** |

## Consequences

1. **The running HUNL datagen pilot is unaffected and needs no restart**:
   the restored in-repo `datagen/th_random.py` is byte-stream identical
   to the recovered original, so pilot data equals what the original
   would produce, bit for bit.
2. **Deliberate sequencing**: the recovered workspace stays STAGED
   (`/workspace/ds_restore/`) and is NOT installed into the live DS path
   until the pilot's generation (12 shards + replay0) completes — so
   every shard and the replay run under one identical import
   environment (in-repo modules; provenance uniformity).
3. After the pilot: install the phase2-datagen export into
   `/workspace/deepstack_leduc_v1.1-bitexact-certified`, re-validate
   (Leduc pytest, ds_scripts comparators vs the recovered lua_trace
   corpus, G1.7/G1.8, CFR-D gadget), and drop the corresponding
   NOT_RE_RUNNABLE entries from the forensic report. The re-port plan is
   CANCELLED — the original certified artifact is back.
4. The archives are committed to this repository so no future container
   reclaim can take the golden engine again.

## Addendum — ACPC archives (owner-uploaded, same day)

| archive | embedded commit | finding |
|---|---|---|
| `acpc-python-client_b5079a21.zip` | `b5079a214c66…` | bundled `game.c` == recorded oracle anchor `85b5325d…`; `evalHandTables` == `9b8bb8e1…` — a THIRD independent provenance source for the ACPC oracle |
| `acpc-server_80908609.zip` | `80908609d982…` | 2019 upstream; `lib/game.c` = `ca1f8ac7…` (newer revision, ≠ oracle anchor) — archived for reference, NOT used as an oracle |
