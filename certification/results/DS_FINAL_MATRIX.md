# HUHL CERTIFICATION MATRIX

Object under test: `zvezdan01/deepstack_leduc_v1.1-bitexact-certified` @ `eb7b21d`
(Python port; author-side oracle = original Lua/Torch7 DeepStack-Leduc,
byte-identical to public upstream `lifrordi/DeepStack-Leduc` @ `da416f96`).
Primitive-layer oracles: original Tammelin/CPRG CFR+ author source (frozen
integer checkpoints, `certification/oracles/`, SHA-256 manifest).
All results below were produced fresh in this run; no historical PASS was
inherited.

```
CFR core              BIT_EXACT       PASS   (232/232 one-iteration tensors; 20340/20340 street-2 exhaustive, stage-by-stage)
RNG                   BIT_EXACT       PASS   (MT19937 vs rng.c: 16/16 streams; DS certified paths call no RNG — excluded scope re-confirmed)
Kuhn CFR+             BIT_EXACT       PASS   (independent replica vs Tammelin binary: 6/6 integer checkpoints incl. iter 1000)
Leduc CFR+            BIT_EXACT       PASS   (independent replica vs Tammelin binary: 6/6 integer checkpoints incl. iter 1000; suit isomorphism + boards)
CFR-D gadget          BIT_EXACT       PASS   (line-audit vs cfrd_gadget.lua + gadget-in-loop 1000-iteration resolves byte-equal in 480/744/3720 traces)
Continual resolving   BIT_EXACT       PASS   (6/6 first action; 480/480 r300->call; 744/744 P2; 108/108 terminals; e2e hand; 150/150 chance histories, 3720/3720 tensors)
CFV averaging         BIT_EXACT       PASS   (skip-500 accumulation + float32 scaler audited vs Lua; average_strategies/average_cfvs stages in 20340-tensor set byte-equal)
Tensor construction   BIT_EXACT       PASS   (NN boxes 8/8: bucketing, range normalization, pot feature, layout; NN layers 11/11 + corrected output byte-equal)
Original weights      BIT_EXACT       PASS   (SHA-256 d5fcba44… == reference_lua copy == public upstream; runtime loads bundled copy; nothing overwrites it)
Full resolve trace    BIT_EXACT       PASS   (street-2 exhaustive 90/90 cases; every internal stage of the CFR iteration compared with np.array_equal, zero tolerance)
Determinism           BIT_EXACT       PASS   (full 1000-iter resolve: identical SHA-256 across 4 runs / 2 processes; full suite 36/36 twice: 33.25 s / 34.28 s)

FIRST UNEXPLAINED DIVERGENCE:
NONE
```

## Explained (non-engine) divergences encountered during this run
1. Leduc replica driver reset the averaging-weight iteration counter between
   incremental checkpoint runs (tooling bug, engine untouched; fixed,
   then 6/6 byte-equal). `DS_PHASE3_PRIMITIVES.md`.
2. `raw_lua_output.t7` initially compared against the pre-correction
   feedforward output; it is the post-zero-sum-correction output
   (test_fixed_nn.lua). With correct semantics: byte-equal.
3. My 480-comparator omitted the exporter's `cr.resolving = first_resolving`
   restore before per-board invariant updates (comparator bug; fixed →
   480/480 byte-equal).
4. quant-trade phase: Kuhn CFR text trace, 2 sub-print-precision artifacts
   (−2⁻⁵⁷ negative-zero print; one .xxxxx5 rounding tie) — documented in
   FIRST_DIVERGENCE.md; CFR+ trace 760/760 exact.

None of these is an unexplained divergence and none required touching any
engine under test.

## Scope boundaries (unchanged from the repo's own report, re-confirmed)
- The Lua side is certified against **frozen** `.t7` author exports; no
  Lua/Torch7 runtime exists here to re-execute the exporters. Provenance:
  reference source byte-identical to public upstream + committed exporters.
- Bit-exactness requires the bundled legacy x86_64 OpenBLAS
  (`LD_LIBRARY_PATH=<repo root>`); non-x86_64 uses a portable fallback,
  explicitly not bit-exact.
- Random action sampling remains outside the deterministic certified scope.
- This is the public Leduc DeepStack, not the HUNL system from the paper.
