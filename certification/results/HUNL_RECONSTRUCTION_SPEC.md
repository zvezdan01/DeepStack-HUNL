# HUNL_RECONSTRUCTION_SPEC — definitive reconstruction spec for full HU No-Limit Hold'em DeepStack

Date: 2026-08-13. Supersedes the parameter/asset/roadmap sections of
`HUNL_PORT_GAP_AUDIT.md` (v1 stays as the component-analysis record).
Frozen and untouched: Golden Baseline `2ab6dde…`, certified datagen
`7967622…`, Phase-2B 110k dataset + manifests.

## 0. Source status (exact, verified this session)

**Primary sources #1 and #2 remain physically unavailable in-session.**
Retrieval was attempted this session against: arxiv.org (paper+supplement),
era.library.ualberta.ca, poker.cs.ualberta.ca, www.deepstack.ai,
static1.squarespace.com (deepstack.ai CDN), web.archive.org,
pdfs/api.semanticscholar.org, www.science.org, webdocs.cs.ualberta.ca,
www.cs.cmu.edu, huggingface.co, openreview.net — **all refused by the
network egress proxy (CONNECT 403)**. Nothing new appeared in the session
uploads. Consequence: **no parameter can be marked VERIFIED on the
authority of the Science Supplement or the Burch thesis** in this session.

**Newly acquired in-session corroborating sources** (read-only shallow
clones via the git proxy — third-party reimplementations, NOT author
oracles; they can raise a value to INFERRED, never to VERIFIED):
- `happypepper/DeepHoldem` @ `68953137dd9d…` → `/workspace/happypepper/deepholdem`
  (Lua/Torch7 HUNL extension of DeepStack-Leduc; played Slumbot 2017).
- `lucky72s/dyypholdem` @ `0e2dda5224a4…` → `/workspace/lucky72s/dyypholdem`
  (Python/PyTorch port of DeepHoldem).
- `michalp21/coms4995-finalproj` @ shallow clone (ACPC python client only;
  no additional value — recorded for completeness).

**In-session primary sources (author/official provenance):**
- `reference_lua/ACPCServer/` — official ACPC dealer bundled by the
  DeepStack authors: `game.c` (1,793 lines), `evalHandTables` (4,269
  lines), `dealer.c`, `holdem.nolimit.2p.reverse_blinds.game`.
- `reference_lua/Source/**` — author Lua (game-independent math certified
  BIT_EXACT into our Golden Baseline).
- `third_party/CFR_plus/` — Tammelin CFR+ (independent oracle only).

Status legend: **VERIFIED** = value read from an in-session primary
artifact (file:line cited). **INFERRED** = value from model recollection of
the Supplement/thesis and/or third-party code; corroboration cited;
must be re-verified when the Supplement PDF is uploaded. **UNKNOWN** =
no defensible value in-session.

---

## 1. Parameter sheet (Task 1)

### 1.1 Game definition

| # | Parameter | Value | Source | Location | Status |
|---|---|---|---|---|---|
| G1 | Players | 2 | ACPC game def | `holdem.nolimit.2p.reverse_blinds.game:3` | **VERIFIED** |
| G2 | Variant | no-limit | ibid. | line 2 (`nolimit`) | **VERIFIED** |
| G3 | Stacks | 20,000 chips both | ibid. | line 5 (`stack = 20000 20000`) | **VERIFIED** |
| G4 | Blinds | P1 = 100 (big), P2 = 50 (small); "reverse blinds" seat mapping | ibid. | line 6 (`blind = 100 50`) | **VERIFIED** |
| G5 | First player per round | preflop: P2 (SB); flop/turn/river: P1 | ibid. | line 7 (`firstPlayer = 2 1 1 1`) | **VERIFIED** |
| G6 | Betting rounds | 4 | ibid. | line 4 (`numRounds = 4`) | **VERIFIED** |
| G7 | Board schedule | 0 / 3 / 1 / 1 | ibid. | line 11 (`numBoardCards = 0 3 1 1`) | **VERIFIED** |
| G8 | Deck | 52 = 13 ranks × 4 suits | ibid. | lines 8–9 | **VERIFIED** |
| G9 | Hole cards | 2 → 1,326 private hands | ibid. line 10; C(52,2) | **VERIFIED** (count derived) |
| G10 | No-limit legality / min-raise | executable rules: raise size ≥ max(prev raise delta, big blind), reopening, all-in short raises, chip-integer amounts | ACPC `game.c` | `raiseIsValid`:788–, `isValidAction`:846– | **VERIFIED** (as code oracle) |

### 1.2 Solving (re-solving CFR)

| # | Parameter | Value | Source | Location | Status |
|---|---|---|---|---|---|
| S1 | CFR variant in lookahead | vectorized CFR+ (regret-matching+, per-iteration clamp [ε,999999]) | author Lua (game-independent) | `Lookahead/lookahead.lua` (certified port `lookahead.py`) | **VERIFIED** (algorithm) |
| S2 | Updates | simultaneous (both players each iteration; not alternating) | author Lua | `lookahead.lua` update loop (certified) | **VERIFIED** (algorithm) |
| S3 | Resolving iterations | 1000 | model recollection of Supplement; DeepHoldem `arguments.lua:30`; DyypHoldem `arguments.py:41`; = certified Leduc default | | **INFERRED** (strong) |
| S4 | Omitted/burn-in iterations | first 500 excluded from averages (included in the 1000) | same three sources (`:31-32`, `:42-43`) | | **INFERRED** (strong) |
| S5 | Averaging semantics | uniform average of strategy/CFVs over iterations 501–1000; both players; as certified in Leduc engine | author Lua (game-independent) | `lookahead.lua` / `cfrd_gadget.lua` (certified) | **VERIFIED** (algorithm) |
| S6 | Per-street iteration overrides (if any in original play) | unknown whether turn/river/preflop used different counts | — | — | **UNKNOWN** |
| S7 | Re-solve bet-sizing sets per street & action depth | **exact author table UNKNOWN.** Recollection: richer first-action set (incl. fractions of pot + all-in), reduced later; DeepHoldem uses pot-only `{{1},{1},{1}}` (self-admitted reduction, `arguments.lua:14`) | Supplement needed | — | **UNKNOWN** (critical gap) |
| S8 | Gadget | CFR-D re-solving gadget, play/terminate regrets, as certified | author Lua + Burch thesis (construction) | `cfrd_gadget.lua` (certified) | **VERIFIED** (algorithm) |

### 1.3 DataGeneration

| # | Parameter | Value | Source | Location | Status |
|---|---|---|---|---|---|
| D1 | CFR schedule for datagen solves | 1000 / skip 500 | as S3/S4 | | **INFERRED** (strong) |
| D2 | Datagen action set | DeepHoldem: pot-only bets; author set unknown (likely restricted) | DeepHoldem `arguments.lua:14` | | **UNKNOWN** (author) |
| D3 | Pot sampling (NL) | uniform over 5 intervals, then uniform integer in interval, floored: min {100,200,400,2000,6000}, max {100,400,2000,6000,18000}; feature = pot/stack | DeepHoldem `data_generation.lua:69–99`; consistent with Supplement recollection | | **INFERRED** (strong) |
| D4 | Range sampling | strength-sorted recursive stick-breaking over the 1326-simplex (identical algorithm to certified Leduc `range_generator.lua`, hand-strength sorted per board) | author Lua algorithm + DeepHoldem `range_generator.lua` | | **VERIFIED** (algorithm; author file is the Leduc original, extended dims) |
| D5 | Turn samples | 10,000,000 | recollection of Supplement | uncorroborated in-session (DeepHoldem used 150k+150k of its own, `arguments.lua:50-52`) | **INFERRED** (weak) |
| D6 | Flop samples | 1,000,000 | recollection of Supplement | uncorroborated in-session | **INFERRED** (weak) |
| D7 | Preflop/aux samples | 10,000,000 (recollection) | uncorroborated | | **INFERRED** (weak) |
| D8 | Train/validation split | not known for author HUNL | — | — | **UNKNOWN** |
| D9 | Datagen target definition | root CFVs of both players from re-solve, normalized by pot | author Leduc pipeline (certified) + DeepHoldem same | `data_generation.lua` both repos | **VERIFIED** (algorithm) |

### 1.4 Abstraction (bucketing)

| # | Parameter | Value | Source | Location | Status |
|---|---|---|---|---|---|
| B1 | Bucket counts postflop | 1,000 per player per street (flop/turn/river spaces) | recollection of Supplement + DeepHoldem `bucketer.lua:102-110` | | **INFERRED** (strong) |
| B2 | Preflop buckets | 169 (canonical preflop hand classes) | DeepHoldem `bucketer.lua:108-110` + recollection | | **INFERRED** (strong) |
| B3 | Bucket construction | clustering of hand-strength(-distribution) features; DeepHoldem: improved-hand-strength (win,tie) histogram pairs + EMD distance (`bucketer.lua:43,119-127`); author's exact features/algorithm/seeds | Supplement needed | | **INFERRED** (method family) / **UNKNOWN** (exact author procedure) |
| B4 | Author bucket artifacts (centroids/assignments) | never released; irreproducible exactly | — | — | **UNKNOWN forever** (permanent rider) |

### 1.5 Neural networks

| # | Parameter | Value | Source | Location | Status |
|---|---|---|---|---|---|
| N1 | Input dim (flop/turn nets) | 2×1000 bucketed ranges + 1 pot (normalized) = 2001 | recollection + B1 | | **INFERRED** |
| N2 | Output dim | 2×1000 bucketed CFVs = 2000 | recollection + B1 | | **INFERRED** |
| N3 | Hidden layers | **CONFLICT: recollection of Supplement = 7 hidden layers; DeepHoldem/DyypHoldem use 3** (`arguments.lua:44`; `net_builder.py:46-53`) | | | **UNKNOWN** (pending Supplement) |
| N4 | Width | 500 | recollection + both ports | | **INFERRED** (strong) |
| N5 | Activation | PReLU (both ports add BatchNorm — author use of BatchNorm UNKNOWN; certified Leduc author net has NO BatchNorm) | ports + our `final_cpu.model` structure | `value_model.py:72-84` | **INFERRED** (PReLU strong; BatchNorm UNKNOWN) |
| N6 | Zero-sum correction | subtract per-player weighted residual; mechanism certified in Leduc engine; DeepHoldem builds it into the net graph (DotProduct → MulConstant(−0.5)) | author Leduc + DeepHoldem `net_builder.lua:52-78` | | **VERIFIED** (mechanism) / **INFERRED** (in-net placement) |
| N7 | Loss | masked Huber over possible buckets | author Lua `masked_huber_loss.lua` (certified port exists) | | **VERIFIED** (algorithm) |
| N8 | Optimizer | Adam | author Lua `train.lua:80` (Leduc); assumed same for HUNL | | **VERIFIED** (Leduc) / **INFERRED** (HUNL) |
| N9 | Learning rate | 0.001 | `arguments.lua:54` (both Leduc author and DeepHoldem) | | **INFERRED** (HUNL) |
| N10 | Batch size | DeepHoldem 1000 (`arguments.lua:36`); author Leduc 100; author HUNL | — | | **UNKNOWN** |
| N11 | LR schedule | none known | — | — | **UNKNOWN** |
| N12 | Epochs / model selection | author HUNL unknown (Leduc author: best-validation-epoch checkpointing, `train.lua`) | | | **UNKNOWN** |
| N13 | Network roles | river: solved exactly (no net); turn net: values at river boundary for flop/turn lookaheads; flop net: values at turn boundary; auxiliary preflop net: averages over flops to avoid enumerating all flops in preflop re-solves | recollection; structure mirrored by DeepHoldem `next_round_value_pre.lua` (aux) | | **INFERRED** (strong, structural) |

---

## 2. Updated reuse map Leduc → HUNL (Task 2)

Verdicts: **RBU** = REUSE BYTE-UNTOUCHED, **RP** = REUSE PARAMETRIZED
(dims/config only, math unchanged, Leduc byte-regression required),
**AD** = ADAPT, **RE** = REPLACE, **NEW** = new code.
Columns: Leduc impl → HUNL target | math preserved? | author oracle? |
certification | residual risk.

| Component | V | Detail |
|---|---|---|
| CFR core (lookahead solve loop) | **RP** | `lookahead.py` → hand-dim 1326, street count 4. Math preserved: YES. Oracle: author Lua (algorithm) + Tammelin cross-anchor. Cert: Leduc byte-regression + G1. Risk: dense-tensor memory pressure → perf refactor temptation. |
| CFR+ / regret-matching+ | **RBU** | clamp/eps semantics as certified (M2 sites). Math: YES. Oracle: Tammelin (BIT_EXACT twice). Cert: regression. Risk: none. |
| Averaging (skip-500, uniform) | **RBU** | `lookahead.py` averaging + `get_root_cfv_both_players` (L2-certified). Math: YES. Oracle: author Lua. Cert: regression. Risk: none. |
| CFR-D gadget | **RBU** | `cfrd_gadget.py` vector length is the only change → RP boundary; zero math edits. Oracle: author Lua (F5/F1/F2 certified). Cert: regression + permutation properties. Risk: none. |
| Continual resolving | **AD** | `continual_resolving.py` → 4-street state machine + position asymmetry (G5). Math: YES (protocol). Oracle: NONE (HUNL author traces don't exist). Cert: NUMERIC invariants + ACPC match behavior. Risk: position/blind mapping bugs. |
| Depth-limited resolving | **AD** | `resolving.py`/`lookahead_builder.py` → per-street NN boundary. Math: YES. Oracle: none. Cert: G1 river-exact first; NUMERIC identities beyond. Risk: boundary normalization. |
| Range API | **RP** | `card_tools.py` over 1326 with per-board possible-hand masks. Math: YES. Oracle: author Lua semantics. Cert: property tests + regression. Risk: low. |
| Tree representation | **AD** | `tree.py` Node/recursion kept; chance/blind/4-street changes. Math: YES (structure). Oracle: ACPC `game.c` for legality. Cert: BIT_EXACT action-set equivalence vs `game.c`. Risk: min-raise edges. |
| Card representation | **RE** | `cards.py` → 52-card encode (ACPC rank×4+suit), string I/O. Oracle: ACPC `game.c`/`card_tools.c`. Cert: BIT_EXACT vs ACPC encode/decode. Risk: none. |
| 1326-combo indexing | **NEW** | canonical pair index, hand↔cards tables. Oracle: combinatorial self-oracle. Cert: exhaustive bijectivity BIT_EXACT. Risk: ordering-contract discipline. |
| Blockers | **NEW** | 1326×1326 shared-card matrix + per-board masks. Oracle: recount. Cert: exhaustive BIT_EXACT. Risk: low, load-bearing. |
| Evaluator | **RE** | Leduc `hand_strength` → 7-card ranking. Oracle: **`evalHandTables` (in session, author-bundled)**. Cert: BIT_EXACT exhaustive vs compiled original. Risk: none (binding only). |
| Showdown utilities | **RE** | river win/lose/tie matrices from evaluator per board. Oracle: derived from certified evaluator. Cert: BIT_EXACT recount + antisymmetry/zero-sum identities. Risk: low. |
| All-in equity / runout | **NEW** | pre-river all-in → expectation over remaining boards (structure = Leduc street-1 call matrix generalized). Math: derivable. Oracle: none direct; `all_in_expectation.c` (ACPCServer) as cross-check. Cert: NUMERIC identities + small-deck exhaustion. Risk: **high** (weighting algebra). |
| Chance nodes | **AD** | tree chance expansion → 49/48-card deals (in-resolve), flop enumeration only via aux/flop nets. Cert: structural + counts. Risk: medium. |
| Chance weighting | **NEW** | card-removal-consistent weights (Leduc's implicit /4-style constants re-derived). Oracle: algebraic identities (masked row-sums 1). Cert: NUMERIC exhaustive identities. Risk: **highest silent-error risk**. |
| Street transitions | **AD** | `next_round_value.py` pattern ×3 (+aux). Oracle: none; DeepHoldem `next_round_value_pre.lua` as structural reference. Cert: round-trip identities + zero-sum preservation. Risk: medium. |
| ACPC betting legality | **NEW** (binding) | port/bind `game.c` rules. Oracle: `game.c` itself. Cert: BIT_EXACT state-enumeration equivalence. Risk: none if oracle-driven. |
| No-limit bet sizing (re-solve action set) | **AD** | `BetSizing` fraction sets per street/depth. Math: YES (mechanism). Oracle: **author table UNKNOWN (S7)**. Cert: legality BIT_EXACT; table fidelity blocked on Supplement. Risk: fidelity, not correctness. |
| Stack/pot accounting | **AD** | Config → blinds/positions/integer chips. Oracle: ACPC game def (VERIFIED). Cert: dealer agreement on pot/stack evolution BIT_EXACT. Risk: low. |
| Terminal utilities | **AD/RE** | `terminal.py` fold path adapt (blocker-normalized), call path replace (showdown matrices). Cert: BIT_EXACT construction + identities. Risk: low-medium. |
| Bucketing | **NEW** | identity 36 → 1000/street clustering + 169 preflop. Oracle: **none, permanently** (B4). Cert: deterministic-reproducible (seeded, hashed artifacts) + BEHAVIORAL quality metrics. Risk: permanent fidelity rider. |
| NN boundary (bucketize/unbucketize, zero-sum corr.) | **RP/AD** | scatter matmuls generalize; correction mechanism certified. Cert: BIT_EXACT round-trip on possible sets. Risk: low. |
| DataGeneration | **AD** | certified `datagen/` + Phase-2B orchestration → per-street generators, pot intervals (D3), 1326 ranges. Math: YES. Oracle: author Leduc algorithm + D3 corroboration. Cert: RNG/serialization/determinism BIT_EXACT; targets vs own certified solver. Risk: compute scale. |
| RNG | **RBU** | `th_random.py` + seed derivation. Cert: done. Risk: none. |
| Serialization | **RBU** | t7 reader/writer + manifests. Cert: done. Risk: none. |
| Training | **AD** | masked-huber (certified module) + Adam loop (to be built for Leduc Phase 3 first). Oracle: author `train.lua` semantics; HUNL hyperparams partly UNKNOWN (N10-N12). Cert: loss module BIT_EXACT; runs seeded-NUMERIC. Risk: optimizer-semantics parity. |
| Evaluation / LBR / AIVAT hooks | **NEW** | LBR agent + variance-reduced match eval; `davis20asupp.pdf` + `1809.03057v1.pdf` in-session for estimator math; ACPC dealer for matches. Cert: BEHAVIORAL/statistical. Risk: none to engine. |

---

## 3. HUNL assets physically in hand (Task 3)

| Asset | Location(s) | Use |
|---|---|---|
| `evalHandTables` (7-card evaluator tables + inline eval fns, 4,269 lines) | `reference_lua/ACPCServer/`, `third_party/CFR_plus/`, both clones' ACPC dirs | **oracle** (compile untouched, exhaustive compare) AND **binding** (wrap for production evaluator) |
| `game.c/game.h` (game parser, betting legality, `rankHand`) | same 4 locations | **oracle** for legality/state-machine; optionally **binding** for match play |
| `holdem.nolimit.2p.reverse_blinds.game` (+ limit & 3p variants) | `reference_lua/ACPCServer/` | **use directly** (canonical game constants, G1–G10) |
| ACPC `dealer.c` + match infra (`play_match.pl`, `bm_*`) | `reference_lua/ACPCServer/` | **use directly** (evaluation matches, LBR harness substrate) |
| `all_in_expectation.c` | `reference_lua/ACPCServer/` | **oracle/cross-check** for all-in runout equity |
| ACPC `rng.c` (dealer RNG) | `reference_lua/ACPCServer/` | **use directly** for reproducible dealt matches |
| Tammelin `cfr.c` + `betting_tools.c` + `card_tools.c` + holdem `.game` defs | `third_party/CFR_plus/` | **oracle** (game-general CFR+ cross-anchor on holdem subgames; already certified twice) |
| ACPC protocol layer | `acpc.py` (Leduc-trimmed), `protocol_to_node.lua`, `protocol.pdf`, michalp21 python client | **adapt** for HUNL protocol strings (multi-card boards) |
| DeepHoldem @ `6895313` (full HUNL Lua: bucketer w/ EMD, next_round_value_pre aux, pot intervals, 1326 pipelines) | `/workspace/happypepper/deepholdem` | **reference/corroboration only** — third-party; never an author oracle; do not copy uncertified math |
| DyypHoldem @ `0e2dda5` (Python port of the above) | `/workspace/lucky72s/dyypholdem` | **reference/corroboration only** |
| Our certified Leduc engine + datagen + Phase-2B harness | DS repo + quant-trade | **use directly** (per §2) |

No other HUNL-specific assets exist anywhere in the session sources
(searched: both repos, third_party, uploads, all clones).

---

## 4. Milestone M-HUNL-0: **HUNL Golden Baseline v0 — exact river solver** (Task 4)

No bucketing, no NN, no turn/flop — river subgame solved exactly with the
certified CFR/CFR-D core. Minimal implementation (new package `hunl/`,
Golden Baseline untouched; ~10 modules):

1. `hunl/cards.py` — 52-card encode/decode (ACPC convention), string I/O.
2. `hunl/hands.py` — 1326 canonical pair indexing, hand↔cards tables.
3. `hunl/blockers.py` — 1326×1326 blocker matrix + per-board masks (river:
   5 board cards ⇒ 1,081 live hands).
4. `hunl/evaluator.py` — binding to `evalHandTables` logic (port +
   compiled-original harness kept as oracle, Phase-2A THRandom pattern).
5. `hunl/showdown.py` — per-river-board win/lose/tie matrix construction.
6. `hunl/terminal.py` — fold + call values (blocker-normalized), river-only.
7. `hunl/tree.py` — river betting tree: blinds/stacks/min-raise per ACPC
   rules; bet-fraction sets configurable (S7 pending ⇒ config, not constants).
8. `hunl/config.py` — G1–G10 constants read from the `.game` file (single
   source of truth).
9. CFR/CFR-D: **the certified Leduc modules imported with dims injected**
   (lookahead + gadget parametrization; Leduc byte-regression suite runs in
   CI of the new package).
10. `hunl/resolve_river.py` — exact river re-solve: ranges+pot in → 1326
    CFVs out (the future datagen target path for the turn net).

### Gate G1 (must fully pass before ANY turn/flop/abstraction/NN work)

| # | Check | Class |
|---|---|---|
| G1.1 | Evaluator: exhaustive equality vs compiled untouched `evalHandTables`/`rankHand` — all 1,326 hands × sampled boards ≥10⁴ + full enumeration of all C(48,5)? no: full enumeration per fixed sampled boards + all 7-card ranks via ACPC's own iteration (`rankAllHands`-style sweep) | **BIT_EXACT** |
| G1.2 | Betting legality: for exhaustively enumerated betting states (bounded raise grid + all-in edges), our tree's legal-action sets == `game.c` `isValidAction`/`raiseIsValid` | **BIT_EXACT** |
| G1.3 | Legal action sets under the configured bet-fraction menu are a subset of G1.2 legality; chip integrality respected | **BIT_EXACT** |
| G1.4 | Terminal matrices: independent recount of showdown/fold matrices; antisymmetry, blocker-zeroing, zero-sum identities | **BIT_EXACT** |
| G1.5 | Blockers/indexing: bijectivity, counts (1326; 1,081 live on river), mask consistency | **BIT_EXACT** |
| G1.6 | Chance/card indexing: board enumeration counts and canonical ordering frozen + hashed | **BIT_EXACT** (self-spec) |
| G1.7 | CFR primitive regression: Leduc suite (Kuhn/Leduc Tammelin checkpoints, gadget F5/F1/F2, 480/480, continual traces) re-run on the parametrized modules — **all still byte-identical** | **BIT_EXACT** |
| G1.8 | River game-value sanity: our exact river solve vs an independent best-response computation on the same river subgame (exploitability of the average strategy ↓ with iterations; BR gap ≤ known CFR+ bound shape) | NUMERIC |
| G1.9 | Tammelin cross-anchor: define a river-only holdem subgame as an ACPC `.game`-style instance solvable by `cfr.c` (fixed board, restricted bets to match); compare converged game values within f32/int-quantization tolerance; where the int-lrint protocol from Phase 6 applies, byte-level checkpoint comparison | NUMERIC (target BIT_EXACT on the int protocol where representable) |

Deliverable: `HUNL_GOLDEN_BASELINE_V0.md` with the full G1 matrix, hashes,
and freeze — the same discipline as the Leduc Golden Baseline.

---

## 5. Updated project estimates (Task 5)

**A. Certified code reusable for HUNL:** ≈ **55–60 %** math-preserving
(≈ 30 % byte-untouched: CFR+/averaging/gadget/RNG/serialization/loss/
BLAS/orchestration; the rest parametrized under byte-regression).

**B. New HUNL-specific code:** ≈ **40–45 %** (indexing, blockers,
evaluator binding, showdown/all-in, chance weighting, transitions,
bucketing, LBR; plus per-street net plumbing).

**C. HUNL Golden Baseline v0 already in hand before writing it:** ≈
**60 %** — CFR core, gadget, resolve protocol, averaging, RNG, config,
serialization and the whole certification harness exist certified; the v0
gap is exactly modules 1–8 + G1 harness (≈ 2,000–2,500 new LOC, every one
of them against an in-session BIT_EXACT oracle).

**D. BIT_EXACT-certifiable (in-session oracles exist):** evaluator,
legality, action sets, terminal/showdown matrices, blockers/indexing,
chance indexing, CFR core + gadget (regression + Tammelin), RNG,
serialization, datagen determinism, NN input/target construction, G1.

**E. Never author-BIT_EXACT (missing original artifacts, permanent):**
author bucket centroids/assignments (never released), HUNL network weights
(never released), HUNL solver traces (never released), the author's exact
10M/1M sample draws (unseeded, lost), GPU-trained weight bit-patterns.
These cap at deterministic-reproducible-on-our-side + NUMERIC/BEHAVIORAL.

**F. Still missing for the HUNL DataGenerator:**
1. Supplement-verified S7 bet-sizing table and D2 datagen action set
   (**the only hard spec blockers** — everything else has a defensible
   INFERRED value);
2. Supplement verification of D5–D7 counts, N3 depth, N10–N12 training
   params (currently INFERRED/UNKNOWN);
3. implemented+certified M-HUNL-0 → then turn-solver (river-exact
   lookahead from turn) as the target engine;
4. bucketing implementation (for the NN spaces; datagen targets themselves
   don't need it — targets are card-space CFVs bucketized at the end);
5. a compute plan (below).
**Owner action that unblocks (1)+(2): obtain
`DeepStackSupplement.pdf` outside this container** (any of the located
URLs) **and upload it into the session.**

**G. Compute estimates** (order-of-magnitude; measured anchor: certified
Leduc resolve = 0.29 s/sample/core, 1,000 iters, 6-dim; HUNL river tree
similar node count but 1,326-dim vectors and 1326² terminal matmuls;
scaling measured on this 4-core box will refine these by ×3 either way):
- **Exact river resolve (v0):** est. 10–60 s/situation/core (CPU, f32
  BLAS). G1 corpus (~10³ resolves): ~1–7 core-days → feasible here.
- **Pilot HUNL turn dataset (10⁴ samples, turn→river-exact lookahead):**
  ~1–5 min/sample/core → 70–350 core-days → **not feasible in this 4-core
  container; needs ~32–128 cores or GPU port** (GPU lookahead ≈ 1–10
  s/sample → 1–12 GPU-days).
- **1M flop situations:** requires trained turn net first; ≈ 100× pilot →
  ~30–300 GPU-days (or thousands of CPU-core-months) → cluster-scale.
- **10M turn situations:** ≈ 1,000× pilot → **~1–4 GPU-years worth of
  solving** (authors used a large cluster); the single most expensive step
  of the whole reconstruction. A reduced-scale certified variant (e.g.
  10⁵–10⁶ samples) is the realistic first production target.
- **Network training (2001→(3–7)×500→2000, 10M rows):** hours–days on one
  modern GPU; CPU-deterministic training of the same at ~10–50× slower —
  a deliberate determinism-vs-cost decision like Leduc Phase 3.

## 6. Recommended first coding task

**`hunl/evaluator.py` + `hunl/cards.py` + the G1.1 harness**: compile the
untouched `evalHandTables`/`game.c` `rankHand` as a C oracle (exact
Phase-2A THRandom pattern), implement the 52-card layer + 7-card evaluator
port, and drive exhaustive BIT_EXACT comparison. Zero risk to frozen
baselines (new package + quant-trade harness only), fully oracled, and
every later component depends on it.
