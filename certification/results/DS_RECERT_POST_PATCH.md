# RE-CERTIFICATION AFTER M2+M4 FIDELITY PATCH

Patched commit: **`2ab6dde`** (branch `golden-baseline-v1.0-m2m4`,
parent `eb7b21d`). Diff: 2 files, +19/−6 lines, all in
`deepstack_leduc/lookahead.py` + `deepstack_leduc/cfrd_gadget.py`:
- **M2**: `np.clip(..., regret_epsilon|0.0, 999999.0)` restored at the three
  Lua clamp sites (`lookahead.lua:91`, `:381`, `cfrd_gadget.lua:76-77`;
  `tools.lua:29-31 max_number() = 999999`). Elementwise comparison only — no
  FP-arithmetic change, dtype float32 preserved, op order unchanged.
- **M4**: implicit `MockNNTerminal` default removed; `value_network=None`
  now lazily loads the original checkpoint at exactly the Lua default point
  (`lookahead_builder.lua:35 neural_net or ValueNn()` ⇒ Python
  `_construct_transition_boxes`, street-1 trees only; street-2 trees need no
  net, as in Lua). `MockNNTerminal` remains available explicitly.

Weights untouched: `final_cpu.model` SHA-256
`d5fcba4402cec46a9b02cea0f96cb78bda83f284ea36f6d5db84529e83eb59a1`,
`final_cpu.info` `9ff711ffec93bf7b70ac8e405de9c72b67776ecf0f3f9cb8fba5c64e59fa482e`
(identical before/after; nothing writes them).

## Full matrix re-run at `2ab6dde` — zero tolerance, nothing inherited

| Check | Result |
|---|---|
| Full pytest suite | **36/36 PASS** (42.3 s) |
| One-iteration CFR trace | **232/232 bit-exact** |
| Street-2 exhaustive (90 cases) | **20340/20340 bit-exact** |
| First-street terminals (18 leaves) | **108/108 bit-exact** |
| r300→call all private/board (30 cases) | **480/480 bit-exact** |
| Deterministic first action | **6/6 bit-exact** |
| NN layer trace + corrected output | **12/12 bit-exact** (comparator semantics fixed: `raw_lua_output` = post-correction output per `test_fixed_nn.lua`) |
| NN next-street boxes | **8/8 bit-exact** |
| Tree manifest | **653/653 exact** |
| Determinism (full 1000-iter resolve) | SHA-256 `b1e35a1a…` — **identical to the pre-patch hash**, 2×/process ×2 processes |
| P2 first-street (36 cases) | PENDING-P2 |
| All chance histories (150 cases) | PENDING-CH |
| `get_root_cfv_both_players` (L2 closure, new comparator) | **PASS** — swap structure vs raw root CFVs, row 0 == `get_root_cfv` == frozen `starting_cfvs_p1.t7`, row 1 == certified `achieved_cfvs`, API result consistency |
| Kuhn CFR+ author-source replica | **PASS** (6/6 checkpoints) |
| Leduc CFR+ author-source replica | **PASS** (6/6 checkpoints) |
| MT19937 RNG oracle | **16/16 BIT_EXACT** |
| Oracle immutability manifest | **52/52 SHA-256 OK** |

## Did the M2 clamp ever activate on the certification corpus?

**No — two independent proofs:**
1. **Bit-equality proof (conclusive):** the entire post-patch matrix is
   byte-identical to the frozen Lua traces and to pre-patch outputs
   (including the determinism hash `b1e35a1a…` being unchanged). If any
   regret had exceeded 999999 anywhere in any certified run, the clamp would
   have altered subsequent float32 state and at least one of the ~25k
   compared tensors would differ. None does ⇒ the clamp is a no-op over the
   full corpus.
2. **Magnitude probe** (`ds_scripts/m2_activation_probe.py`, production
   trace hook, no engine change): worst observed values across a full
   street-1 root resolve, a P2-history street-2 gadget resolve, and an
   adversarially skewed pot-900 street-2 resolve —
   max cumulative regret **266,290.6**, max positive regret 2,826.9,
   max gadget regret 457.1, vs bound 999,999. Headroom ≈ 3.8× at the
   adversarial extreme ⇒ M2 was a genuine latent risk (the bound is in
   reachable territory), and it provably never fired in certification.

## Explained non-engine issues during re-certification
- The L2 comparator's first draft asserted the row order of
  `get_root_cfv_both_players` backwards; frozen-first analysis showed
  checks 1/3/5 (swap structure, frozen-trace anchor, API consistency)
  passing — the engine's swap semantics match Lua (`lookahead.lua:419-424`);
  comparator indices fixed, 5/5 PASS. No engine involvement.
- `compare_nn_root_trace.py` previously compared `raw_lua_output.t7`
  against the pre-correction feedforward; per `test_fixed_nn.lua` it is the
  full corrected output. Comparator now self-contained, 12/12.
