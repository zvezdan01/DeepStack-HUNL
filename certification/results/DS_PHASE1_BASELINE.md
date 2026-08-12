# DS PHASE 1 — FRESH BASELINE (deepstack_leduc_v1.1-bitexact-certified)

Date: 2026-08-12

## Object under test

- Repo: `zvezdan01/deepstack_leduc_v1.1-bitexact-certified`
- HEAD: `eb7b21d1cffcccb786093f808721a592f57e21d0`
  ("Update Python version to 3.11 for pytest and numpy compatibility")
- Working tree: clean before and after all test runs (verified — no test
  mutates repo state; weights not overwritten by any test)
- 25,957 files, 133 MB; clone location `/workspace/deepstack_leduc_v1.1-bitexact-certified`

## Environment freeze (this certification run)

| Item | Value |
|---|---|
| OS | Linux 6.18.5-fc-v20 x86_64, Ubuntu 24.04 userland |
| CPU | Intel(R) Xeon(R) Processor @ 2.80GHz (4 cores, x86_64) |
| Python | 3.11.15 |
| numpy | 2.4.6 (scipy-openblas64 backend for numpy's own ops) |
| torch | 2.13.0+cu130 (CPU execution only; no GPU present) |
| pytest | 9.1.1 |
| gcc | 13.3.0 |
| Bit-exact BLAS | repo-bundled `torch7_openblas.so.0` / `libopenblas_sandybridgep-r0.3.0.dev.so` / `libgfortran.so.3` loaded via `LD_LIBRARY_PATH=<repo root>` (required; without it the suite cannot even collect) |
| Seeds / config | `Config`: cfr_iters=1000, cfr_skip_iters=500, ante=100, stack=1200; deterministic paths under test use no RNG (RNG excluded from certified scope per the repo's own report — re-confirmed) |

## Full existing test suite — fresh run (no inherited results)

```
LD_LIBRARY_PATH=$PWD PYTHONPATH=. python3 -m pytest -q
36 passed in 33.25s
```

**36/36 PASS** (test_continual_acpc, test_core, test_end_to_end_bitmatch,
test_lookahead, test_original_checkpoint, test_reference_modules).
Matches the repo's release-time claim (36/36), now reproduced in this
environment with torch 2.13 / numpy 2.4 / Python 3.11.15.
