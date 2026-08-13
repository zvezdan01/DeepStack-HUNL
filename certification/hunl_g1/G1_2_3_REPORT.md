# Gates G1.2 + G1.3 — blockers/indexing + exact river showdown

Date: 2026-08-13. Result: **PASS — zero divergences.** Built strictly on
G1.1-certified `hunl/evaluator.py` (`23f783f…`).

## Deliverables
- `hunl/blockers.py` — 1326×1326 blocker/compatibility layer over the
  frozen hand-ordering contract; per-board possible masks; legal-pair
  masks; SHA anchor.
- `hunl/showdown.py` — exact river showdown matrices + reference terminal
  values (`river_call_values`) for the CFV identity.

## dtype / layout contracts (FROZEN)
- Blocker `B`: uint8 (1326,1326) row-major; `B[i,j]=1` iff hands share a
  card; diagonal = 1 (self-overlap); symmetric; every row sum = 101
  (= 51+51−1, self included).
- Showdown `M`: int8 (1326,1326) row-major; legal pair → `M[i,j] ∈
  {+1,0,−1}` = sign(rank_i − rank_j); **every illegal entry exactly 0**;
  legality carried by separate uint8 `legal` mask (a legal tie is also 0 —
  consumers must mask, never infer legality from `M`); exact antisymmetry
  `M == −Mᵀ` over the whole matrix.
- Ranks: uint32, blocked hands = sentinel `0xFFFFFFFF`.
- Terminal reference: `u1 = M @ r2`, `u2 = (−Mᵀ) @ r1`; f64 reference +
  f32 (future CFR dtype) both exercised.

## G1.2 results
| Check | Coverage | Result |
|---|---|---|
| Independent recount (pure-python sets) | all **1,758,276** ordered pairs | match |
| Structure | symmetric, diag=1, row sums 101 | PASS |
| Case tests | self-overlap, one-card overlap, disjoint, hand-vs-board | PASS |
| Exhaustive per-board possible-hand counts | **all** boards: 22,100 flops → C(49,2)=1176; 270,725 turns → C(48,2)=1128; 2,598,960 rivers → C(47,2)=1081; preflop 1326 | PASS (2,891,785 boards) |
| API-path sample | 10,000 boards × {3,4,5} via `possible_hands_mask` | PASS |
| Determinism anchor | in-process rebuild + fresh subprocess | **SHA-256 `8c7f9f9e68187a60615fe085e9ca29b22aefb63cbd81c18ea9ec6926451cd494`** |

## G1.3 results
| Check | Coverage | Result |
|---|---|---|
| Corpus (seed 20260813) | **2,000 rivers × 1326² = 3,516,552,000 entries** (2,140,380,000 legal; 1081×990 legal ordered pairs per board) | PASS |
| Ranks vs certified evaluator | independent sign-construction per board + **12,000** slow per-row win/tie/loss recounts | match |
| Legality vs G1.2 | `legal == legal_pairs_mask`, diag illegal, illegal entries exactly 0 | PASS |
| Antisymmetry | `M == −Mᵀ` exact, all corpus boards | PASS |
| Tie symmetry | ties symmetric AND exactly rank-equality on legal pairs | PASS |
| Win/loss balance | global wins == losses each board | PASS |
| Permutation invariance | 50 boards, shuffled board order → byte-identical (M, legal, ranks) | PASS |
| Determinism | repeated builds SHA-identical | PASS |
| Corpus anchor | SHA-256 `34af9da10c5edde3571e8059b0baaa9dcce4f54b8539380b27855c2278822ac4` | |
| Terminal CFV identity | 1,000 range pairs on 200 boards: max \|r1·u1 + r2·u2\| **f64 2.31e−16** (<1e−12), **f32 9.97e−08** (<1e−4) | PASS |
| **Exhaustive river structural audit** | **all 2,598,960 rivers × 1326 = 3,446,220,960 rank entries**; every board exactly 1081 live hands; hand-class cross-foot == **21 × canonical 7-card frequencies** (exact, ties the entire river space back to the G1.1-certified space) | PASS |
| Full-river anchor | rank-stream SHA-256 `4bb00373c775b20141a24845cd2a02d16e9b516fddef9005769db27415e83ef6` (lexicographic boards) | |

## Divergences
One harness-side expectation bug caught before any pass was recorded
(row-sum constant miscounted as 102 by double-counting self; matrix itself
verified correct by the full recount; fixed in harness, engine untouched).
**Engine-side first divergence: NONE.**

## Runtime
Total 801 s single-process on the 4-core container (recount 0 s, cardinality
sweeps 11 s, corpus 63 s, CFV identity 7 s, exhaustive river audit 719 s).

## Residual risks
1. Showdown matrices are certified against the same evaluator they consume
   (plus independent constructions/recounts); their ultimate anchor is the
   G1.1 BIT_EXACT tie to the untouched author oracle — inherited, not
   re-derived here.
2. f32 zero-sum residual (≤1e−7 on unit-mass ranges) is a *measured
   envelope*, not a proof; the future CFR terminal path must re-measure it
   at real pot scales (G1.8).
3. Dense int8 matrices (1.76 MB/board) are fine for river work; memory
   strategy for many-board caching is deliberately not frozen yet.

Frozen baselines untouched (DS repo clean at `7967622`, golden parent
`2ab6dde`); no tree/ACPC-binding/CFR/bucketing/NN/training/datagen started.
Raw log: `G1_2_3_RESULT.txt`.
