# PHASE 3 — ALGORITHMIC GAME THEORY RAW .NPZ ORACLES

Reference: `algorithmic_game_theory-main/tests` (upload SHA-256
`7ebd91f4c41c1c01b720ef42b4ad17a5af243e68a065f889c92d0106b479afc2`),
immutable copy `third_party/agt_tests/`. The AGT repo ships NO solution
implementations (templates are `NotImplementedError` stubs); the `.npz`
snapshots are the raw oracle. Inputs are regenerated deterministically by the
harness itself (md5-of-test-name seeded `np.random.default_rng`, classic +
random game generators in `tests/utils.py`) — the real inputs were used, not
reimplemented from memory.

"Ours" side: freshly written certification implementations in
`certification/agt_solutions/` (weeks 1–6), run through the AGT repo's own
pytest + pytest-regressions harness unchanged (`certification/agt_run/`,
symlinks only; `conftest.py` adds passive raw byte-level recording without
altering pass/fail semantics).

## Harness result (their tolerance, np.isclose rtol=1e-5, atol=1e-8)

**256 / 256 tests PASSED** across
week01 (105), week02 (38), week03 (56), week04 (26), week05 (12), week06 (19).

## Raw byte-level classification (obtained.tobytes() == stored.tobytes())

515 stored oracle arrays total → **437 byte-exact (BIT_EXACT)**, 78
numeric-only. Per test family (arrays byte-exact/total, max abs diff of any
non-exact array):

| Family | byte-exact | max_abs_diff | Classification |
|---|---|---|---|
| best_response row/col (3.1) | 28/28 | 0 | **BIT_EXACT** |
| find_strictly_dominated_actions (3.1) | 28/28 | 0 | **BIT_EXACT** |
| iterated_removal_of_dominated_strategies (3.1) | 56/56 | 0 | **BIT_EXACT** |
| compute_nash_conv (3.3) | 14/14 | 0 | **BIT_EXACT** |
| evaluate_general_sum (3.1) | 23/28 | 7.1e-15 | NUMERIC_EQUIVALENT (FP association order) |
| evaluate_zero_sum (3.1) | 10/14 | 1.4e-14 | NUMERIC_EQUIVALENT |
| evaluate_{row,col}_against_best_response (3.1) | 26/28 | 7.1e-15 | NUMERIC_EQUIVALENT |
| compute_deltas (3.3) | 21/28 | 1.4e-14 | NUMERIC_EQUIVALENT |
| compute_exploitability (3.3) | 13/14 | 7.1e-15 | NUMERIC_EQUIVALENT |
| fictitious_play (+naive) (3.3) | 42/42 | 0 | **TRACE_EXACT** (snapshots stored rounded to 8 dp per harness; byte-equal post-round; NOT claimed raw bit-exact per plan rule) |
| verify_support (3.2) | 37/38 | 5.0e-17 | NUMERIC_EQUIVALENT — solver dependent (HiGHS LP) |
| support_enumeration (3.2) | 41/47 | 2.2e-16 | NUMERIC_EQUIVALENT — solver dependent |
| find_nash_equilibrium (3.4) | 2/14 | 4.0e-15 | NUMERIC_EQUIVALENT — solver dependent (LP duals) |
| find_correlated_equilibrium (3.4) | 12/19 | 3.6e-15 | NUMERIC_EQUIVALENT — solver dependent (degenerate LP vertex selection; requires bounds=(0,1) formulation to land on the reference vertex) |
| double_oracle (3.5) | 27/60 | 1.1e-9 | NUMERIC_EQUIVALENT — solver dependent (restricted-game LP; supports/insertion order reproduced exactly, final strategies within 1.1e-9) |
| regret_minimization (3.6) | 57/57 | 0 | **TRACE_EXACT** (stored rounded to 8 dp; byte-equal post-round) |

Environment note: scipy 1.17.1 / HiGHS; the reference snapshots were
generated with an unknown scipy version, so LP-dependent last-bit agreement
beyond this level is not expected and is classified per plan §3.2/3.4.

Notable reproduction detail (documented, needed for oracle agreement):
- Double Oracle: initial restricted game = one `rng.integers` pure action per
  player (row first), support arrays kept in **insertion order** (not sorted).
- Fictitious play / regret minimization: uniform initial average, moving
  average `avg += (new − avg)/(t+1)`, BR ties broken by `np.argmax` first-max.
- Correlated equilibrium LP: zero objective, row-then-col incentive
  constraints, variable bounds (0,1).
