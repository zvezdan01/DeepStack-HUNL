# DS PHASE 5 — CFR-D GADGET (F5 math, F1 loop integration, F2 CFV averaging)

The repo carries no "F1/F2/F5" labels; per the certification instructions the
mapping used is: **F5** = gadget mathematics itself, **F1** = gadget
integration inside the CFR loop, **F2** = averaged CFVs / normalization
scaler.

## F5 — gadget math (`deepstack_leduc/cfrd_gadget.py` vs `reference_lua/Source/Lookahead/cfrd_gadget.lua`)

Line-level audit (both files read side-by-side, float32 throughout):

| Step | Lua | Python | Match |
|---|---|---|---|
| total values | `cmul(play,ps); cmul(term,ts); add` | `(play*ps) + (term*ts)` — same association order | ✓ |
| current regrets | `copy(values); csub(total)` | `values − total` | ✓ |
| cumulate | `add` | `+=` | ✓ |
| CFR+ clamp | `clamp(1e-8, max_number)` **on both play and terminate regrets** | `np.maximum(x, 1e-8)` in place | ✓ (upper clamp irrelevant at these magnitudes) |
| regret matching | copy + add + cdiv | `r / (play+term)` | ✓ |
| range mask | `cmul(range_mask)` after matching | `*= range_mask` | ✓ |
| output | play strategy copy | `.copy()` | ✓ |
| `iteration` arg unused | ✓ | ✓ (kept for API parity) | ✓ |

## F1 — integration in the CFR loop (`lookahead.py:_compute` vs `lookahead.lua:_compute`)

Iteration body order identical to the Lua reference:
`_set_opponent_starting_range → _compute_current_strategies →
_compute_ranges → _compute_update_average_strategies →
_compute_terminal_equities → _compute_cfvs → _compute_regrets →
_compute_cumulate_average_cfvs`, then `_compute_normalize_average_strategies`
+ `_compute_normalize_average_cfvs`. The gadget is consulted at the start of
every iteration during re-solves (`_set_opponent_starting_range` reads
`cfvs_data[1]` player-1 slice → `compute_opponent_range` → writes
`ranges_data[1]` player-2 slice), exactly as in Lua.

## F2 — averaged CFVs / scaler

- accumulation only for `iteration > cfr_skip_iters` (500), unnormalized
  (`average_cfvs_data[1] += cfvs_data[1]`, layers 1 and 2) — matches Lua
  `_compute_cumulate_average_cfvs`;
- final scaler `average_cfvs_data[1] /= float32(cfr_iters − cfr_skip_iters)`;
- average strategy normalization reproduces the exact Lua NaN fallback
  (first action ← 1, remaining NaN ← 0).

## Empirical certification (not just final CFVs)

- **Stage-level intermediates:** the street-2 exhaustive re-run compares
  every internal stage of a CFR iteration (ranges, current strategy, average
  strategy, terminal CFVs, current CFVs, regrets, positive regrets, average
  CFVs) tensor-by-tensor — see DS_PHASE6 results.
- **Gadget-in-loop, 1000 iterations:** every street-2 re-solve in the
  480-case and 3720-tensor chance-histories certifications runs the gadget
  inside the full 1000-iteration loop; final averaged strategies/achieved
  CFVs/children CFVs are byte-equal to the Lua traces. float32 state cannot
  re-converge after a divergence, so in-loop bit-equality of the averaged
  outputs certifies every intermediate gadget iteration on those paths.
- **Standalone gadget-vs-Lua unit trace:** NOT_TESTABLE — no gadget-only Lua
  export exists and no Torch7 runtime is available to create one; covered by
  the line audit + in-loop bit-exactness above.
