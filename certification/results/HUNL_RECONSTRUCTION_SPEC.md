# HUNL_RECONSTRUCTION_SPEC v2 — definitive reconstruction spec for full HU No-Limit Hold'em DeepStack

Date: 2026-08-13 (v2 — Stage 0 closed: primary sources now IN SESSION).
v1 history preserved in git (`8354516`). Frozen and untouched: Golden
Baseline `2ab6dde…`, certified datagen `7967622…`, Phase-2B dataset,
G1.1 certified code (`23f783f…`), G1.2/G1.3 certified code (`740f47b…`).

## 0. Primary sources (verified in session)

| # | Document | Authors | Pages | SHA-256 | Kind | Local path |
|---|---|---|---|---|---|---|
| P1 | *DeepStack: Expert-Level Artificial Intelligence in Heads-Up No-Limit Poker*, arXiv:1701.01724v3 — **main paper + full Supplementary Materials** | Moravčík, Schmid, Burch, Lisý, Morrill, Bard, Davis, Waugh, Johanson, Bowling | 37 | `603e3975b29edd9034b4fdd6f2c0a70eeb5058259680bb7444f1727315dd3b2d` | main + supplement | `/root/.claude/uploads/ab297466-…/0f135c39-1701.01724v3.pdf` |
| P2 | *DeepStack…* — Science vol. 356 iss. 6337 reprint (main article) | same | 15 | `ef71dea9ebc972a6058815df4878b38a907591ff4b5266bf607fd286f7f5ac64` | main paper | `…/31a7f364-17science.pdf` |
| P3 | *Time and Space: Why Imperfect Information Games are Hard* — PhD thesis, U. of Alberta 2017 (full text, .docx export, 311,835 chars) | Neil Burch | n/a (docx) | `078c9543b8424a06a23e0bf13fc895d282b62e393b7834dfa834884539e7d2ff` | thesis | `…/9b1c2e7d-msf_1000043324.docx` |
| A1 | `vs_LBR.zip` — original LBR evaluation raw outputs (DeepStack, Slumbot, Act1, Hyperborean, Full Cards) | authors | — | `684759179326665cbc3c96adcfb76d804a023908e029fbbfed7eaba376b91925` | evaluation data | `…/96762bc8-vs_LBR.zip` |
| A2 | `DeepStack_vs_IFP_pros_1.zip` — original human-match logs + AIVAT analysis | authors | — | `fb92b4b0821b31a5c8ba18373ae8dc1c99ec098996adb1fc120e8887fdf9431a` | evaluation data | `…/13671c5e-DeepStack_vs_IFP_pros_1.zip` |
| — | `cee607ec-…mht` | — | — | `29a64931…` | **NOT the thesis** — only the ERA repository landing page (catalog HTML); superseded by P3 | `…/cee607ec-…` |

Notes: P1 pages 1–14 = the article (text identical to P2 in every checked
passage); pages 15–37 = Supplementary Materials. Citations below use P1
PDF page numbers. Secondary corroboration only (never a source of
VERIFIED): DeepHoldem `6895313`, DyypHoldem `0e2dda5`. In-session code
primaries unchanged: ACPC `game.c`/`.game` defs, author Leduc Lua.

Status legend: **VERIFIED** = read from an in-session primary artifact
(cited). **INFERRED** = defensible value, not explicit in a primary.
**UNKNOWN** = no defensible value.

---

## 1. Parameter sheet

### 1.1 Game definition (unchanged from v1 — all VERIFIED via ACPC game def)

G1–G10 as v1: 2 players, no-limit, stacks 20,000, blinds 100/50 (P1=BB),
firstPlayer 2 1 1 1, 4 rounds, board 0/3/1/1, 52 cards, 1,326 hands,
min-raise/all-in legality per `game.c:788,846`. P1 p.16 (§Performance
Against Professional Players) confirms 200 big-blind stacks ($50/$100
blinds, $20,000 stacks per hand).

### 1.2 Solving (re-solving CFR) — Table 4, P1 p.22 unless noted

| # | Parameter | Value | Source | Status |
|---|---|---|---|---|
| S1 | CFR variant | "hybrid of vanilla CFR and CFR+: **regret-matching+** like CFR+, but **uniform weighting** and **simultaneous updates** like vanilla CFR" | P1 p.22 (Continual Re-Solving); thesis ch.4 corroborates the CFR/CFR+ distinction | **VERIFIED** — exactly the semantics certified in our Leduc engine |
| S2 | Updates | simultaneous | P1 p.22 | **VERIFIED** |
| S3 | Re-solve iterations per round | **pre-flop 1000, flop 1000, turn 1000, river 2000** | P1 p.22, Table 4 | **VERIFIED** |
| S4 | Omitted (burn-in) iterations per round | **pre-flop 980, flop 500, turn 500, river 1000** (included in S3 counts) | P1 p.22, Table 4 | **VERIFIED** |
| S5 | Averaging | uniform average of strategy/CFVs over non-omitted iterations | P1 p.22 | **VERIFIED** |
| S6 | Per-round action menus (bet sizing) | Table 4, P1 p.22 — abbrev. F/C/½P/P/2P/A: |||
|  |  | **Pre-flop**: 1st action {F,C,½P,P,A}; 2nd {F,C,½P,P,2P,A}; remaining {F,C,P,A}; NN = Aux/Flop |||
|  |  | **Flop**: 1st {F,C,½P,P,A}; 2nd {F,C,P,A}; remaining {F,C,P,A}; NN = Turn |||
|  |  | **Turn**: 1st {F,C,½P,P,A}; 2nd {F,C,P,A}; remaining {F,C,P,A}; NN = none (solve to end, river card-bucketed) |||
|  |  | **River**: 1st {F,C,½P,P,2P,A}; 2nd {F,C,½P,P,2P,A}; remaining {F,C,P,A}; NN = none | P1 p.22 Table 4 | **VERIFIED** (closes v1's critical gap S7) |
| S7 | Depth limit | end of current round (flop/pre-flop → value net at next-street start); turn solves to end of game with **bucketed card abstraction on the river**; river solves remainder exactly | P1 pp.22–23 | **VERIFIED** (river-bucket space spec: see U3) |
| S8 | Gadget | modified CFR-D gadget (chosen over max-margin); constraint values = **opponent-optimal values** (max over all actions incl. the one reaching S — more pessimistic than best-response-excluding) | P1 p.22; P3 thesis ch.6 (§continual re-solving refinements) | **VERIFIED** |
| S9 | Pre-flop optimizations | aux net used ONLY during omitted iterations; final (averaged) iterations enumerate all 22,100 flops with the flop net; re-solve results **cached per betting sequence** | P1 p.23 | **VERIFIED** |
| S10 | Iteration-count driver | counts chosen to meet per-round wall-clock (human-speed play on 1 GPU) | P1 p.22; P3 ch.4 note | **VERIFIED** (rationale) |
| S11 | Sparse-tree CFV error reference | Table 5, P1 p.23: ground truth = {F,C,Min,¼P,½P,¾P,P,2P,3P,10P,A} @ 4,000 iters; e.g. {F,C,½P,P,A} → L1 41.42 mbb/g over 100 random river situations | P1 p.23 | **VERIFIED** (G1.8/G1.9 reference protocol) |

### 1.3 DataGeneration — P1 pp.25–26

| # | Parameter | Value | Source | Status |
|---|---|---|---|---|
| D1 | Datagen solver | "1,000 iterations of CFR+" (wording; resolver semantics per S1 — the author Leduc datagen we bit-certified uses RM+/simultaneous/uniform-skip) | P1 p.26 | **VERIFIED** (count) / wording note in §4 |
| D2 | Datagen omitted iterations | not stated in primaries; author Leduc pipeline & DeepHoldem use 500 | — | **INFERRED** (500) |
| D3 | Datagen action set | **{fold, call, pot-sized bet, all-in}, no card abstraction** (turn targets); flop targets: depth-limited solve with turn net at river boundary | P1 p.26 + P2 p.8 | **VERIFIED** |
| D4 | Pot sampling | interval from **{[100,100), [200,400), [400,2000), [2000,6000), [6000,19950]}** uniformly, then **uniform integer** within interval (footnote 2: "designed to approximate observed pot sizes from older HUNL programs") | P1 p.25 fn.2 | **VERIFIED as printed** — `[100,100)` bracket anomaly: see conflict C3 |
| D5 | Range sampling | recursive R(S,p): p1 ~ U(0,p), p2 = p−p1; S1 = ⌊\|S\|/2⌋ **lowest-strength** hands, S2 rest; recurse; hand strength = P(beat uniform random hand at current public state) | P1 p.26 | **VERIFIED** — odd-split detail: conflict C2 |
| D6 | Turn samples | **10,000,000** (post-turn-card situations), solved to game end; 6,144 CPU cores, >175 core-years (Calcul Québec MP2) | P1 p.26 | **VERIFIED** |
| D7 | Flop samples | **1,000,000**, solved depth-limited with turn net; 20 GPUs, ~0.5 GPU-year | P1 p.26 | **VERIFIED** |
| D8 | Aux samples | **10,000,000** pre-flop situations; targets = enumerate all 22,100 flops, average flop-net outputs | P1 p.26 | **VERIFIED** |
| D9 | Train/validation split | not stated (validation set exists — losses reported) | — | **UNKNOWN** |
| D10 | Target definition | per-player CFV vectors, output as fractions of the pot | P1 pp.25–26, P2 p.8 | **VERIFIED** |

### 1.4 Abstraction — P1 p.27

| # | Parameter | Value | Source | Status |
|---|---|---|---|---|
| B1 | Postflop buckets | **1,000 clusters** (flop and turn nets) | P1 p.27, P2 p.8 | **VERIFIED** |
| B2 | Pre-flop | **no bucketing for aux net — 169 strategically distinct hands input directly** | P1 p.27 | **VERIFIED** |
| B3 | Method | **k-means with earth mover's distance over "hand-strength-like features"** (refs 28, 54) | P1 p.27 | **VERIFIED** (method family) |
| B4 | Exact features / init / seeds / iterations | not stated | — | **UNKNOWN** |
| B5 | Author cluster artifacts | never released | — | **UNKNOWN forever** (permanent rider) |

### 1.5 Neural networks — P2 p.8 (Architecture/Training), P1 pp.26–27, Fig. 3 (P1 p.9)

| # | Parameter | Value | Source | Status |
|---|---|---|---|---|
| N1 | Input | pot size **as fraction of total stacks** + both players' ranges as distributions over 1,000 buckets ⇒ 2×1000+1 = 2001 (flop/turn); aux: 2×169+1 = 339 (derived) | P2 p.8; P1 p.27 | **VERIFIED** (structure; exact vector ordering U6) |
| N2 | Output | per-player bucket CFVs, fractions of pot ⇒ 2000 (aux 338), inverse-bucketed to card CFVs | P2 p.8, Fig. 3 | **VERIFIED** |
| N3 | Hidden layers | **7** fully connected (Fig. 5 p.27: validation plateaus ≥5; 7 chosen for accuracy/speed/GPU-memory tradeoff) | P2 p.8; P1 p.27 | **VERIFIED** — conflict C1 resolved |
| N4 | Width | **500** | P2 p.8, Fig. 3 | **VERIFIED** |
| N5 | Activation | **PReLU** ("linear, PReLU" layers); **no BatchNorm in the described architecture** (DeepHoldem's BatchNorm is their own addition) | P2 p.8, Fig. 3 | **VERIFIED** (absence = as-described) |
| N6 | Zero-sum correction | **inside the network graph** (outer network): compute both players' range-weighted value estimates, subtract half of their sum from each side's values; differentiable, trained through | P2 p.8; Fig. 3 | **VERIFIED** |
| N7 | Loss | average **Huber loss** over CFV errors (δ parameter not stated → U4) | P1 p.26 | **VERIFIED** |
| N8 | Optimizer | **Adam** (Torch7 built-ins) | P1 p.26 | **VERIFIED** |
| N9 | Learning rate + schedule | **0.001 → 0.0001 after first 200 epochs** | P1 p.26 | **VERIFIED** |
| N10 | Batch size | **1,000** | P1 p.26 | **VERIFIED** |
| N11 | Epochs / selection | ~**350 epochs** (~2 days, 1 GPU); **epoch with lowest validation loss chosen** | P1 p.26 | **VERIFIED** |
| N12 | Roles | flop net: values at turn-card boundary for preflop/flop resolves; turn net: values at river boundary within flop resolves ... (see S6 NN column, S7, S9); river: no net | P1 pp.22–23, 25–26 | **VERIFIED** |
| N13 | Accuracy anchors (reproduction targets) | Huber loss (fractions of pot): turn 0.016 train / 0.026 val; flop 0.008 / 0.034; aux 0.000053 / 0.000055 | P1 p.27 | **VERIFIED** |

### 1.6 Evaluation

AIVAT (human match ranking; raw data A2) and LBR configurations
(F,C / F,C,P,A / 56bets variants; results Table 6.1 P3 = P1 supplement;
raw data A1) — **VERIFIED with original raw data in session**.

---

## 2. Reuse map — v1 §2 stands with these updates
- "No-limit bet sizing": author menu tables now VERIFIED (S6) → verdict
  stays ADAPT, fidelity blocker removed.
- "CFR core / averaging": supplement confirms the certified Leduc engine's
  exact scheme (RM+, simultaneous, uniform skip-averaging) is the
  DeepStack scheme → reuse confidence upgraded; per-round iteration counts
  become config.
- Gadget: opponent-optimal constraint values (S8) — matches the certified
  Leduc implementation's semantics; no change.
- Everything else unchanged.

## 3. Assets — v1 §3 stands; add A1/A2 evaluation datasets (oracle data
for the future LBR/AIVAT harness).

## 4. Source conflicts (none silently resolved)

| # | Parameter | Main paper (P2) | Supplement (P1) | Thesis (P3) | Secondary | VERDICT |
|---|---|---|---|---|---|---|
| C1 | Hidden layers | 7×500 PReLU | 7 (Fig. 5: ≥5 plateau) | silent | DeepHoldem/Dyyp: 3 + BatchNorm | **7×500 PReLU, no BatchNorm** — primaries unanimous; DeepHoldem is a self-admitted reduction. v1's conflict CLOSED. |
| C2 | R(S,p) odd-split | — | ⌊\|S\|/2⌋ deterministic | silent | author *Leduc released code* (and our bit-exact-certified port + DeepHoldem): randomized floor/ceil via torch.random(0,1) | **Implementation follows the author-code randomized rounding** (proven bit-exact against author-generated Leduc data); supplement prose treated as simplified description. Documented deviation-from-prose, code-anchored. |
| C3 | Pot-sampling first interval | — | "[100, 100)" (degenerate as printed; [100,200) gap) | silent | DeepHoldem: exactly 100; last interval 18,000 vs P1's 19,950 | **As printed in P1**: {100} singleton + [200,400) + [400,2000) + [2000,6000) + [6000,19950]; the bracket anomaly and the missing [100,200) recorded as U5. DeepHoldem's 18,000 rejected (P1 says 19,950). |
| C4 | "CFR+" naming for datagen solves | — | datagen: "1,000 iterations of CFR+" (p.26) vs resolver: hybrid (p.22); canonical CFR+ per thesis = RM+ + linear weights + alternating | thesis defines canonical CFR+ | author Leduc datagen code = hybrid semantics | **Hybrid semantics (S1) with 1,000 iterations** — the author's own released datagen implements it; "CFR+" read as colloquial for RM+-based solver. |

## 5. Remaining INFERRED (3)
1. **D2** datagen omitted iterations = 500 (author Leduc pipeline +
   DeepHoldem; primaries silent).
2. Torch7 f32 numeric conventions for HUNL nets/datagen (P1 says "built-in
   Torch7 libraries"; f32 default — matches everything we certified).
3. Datagen for aux/preflop situations uses the same pot/range sampling
   machinery (P1 describes generation generically; preflop specifics not
   separately spelled out).

## 6. Remaining UNKNOWN (8)
| # | Item | Blocker? |
|---|---|---|
| U1 | Train/valid split sizes (D9) | no — choose & document (deviation note) |
| U2 | Bucketing exact features/init/seed/iters (B4) + author artifacts (B5, permanent) | **yes for author-faithful NN stage** (method known; artifacts irreproducible — permanent rider) |
| U3 | River bucket space used inside turn resolves ("bucketed abstraction for all actions on the river") — presumably the same 1,000-cluster space, not stated | minor — resolvable by experiment vs exactness tradeoff |
| U4 | Huber δ | no — default δ=1 (Torch7 SmoothL1) documented |
| U5 | Intended first pot interval (C3 anomaly) | no — document both readings |
| U6 | Exact NN input vector ordering/layout (bucket order, pot position) | no — freeze our own contract (affects only our reproducibility, not author-fidelity, since weights are lost anyway) |
| U7 | Adam β₁/β₂/ε | no — Torch7 defaults documented |
| U8 | NN weight initialization | no — Torch7 defaults documented |

**Implementation blockers actually remaining: U2 only, and only for the
author-faithful abstraction stage.** The solving/tree/datagen pipeline has
no UNKNOWN blocker left.

## 7. Updated status

- Parameter sheet: **~40 VERIFIED / 3 INFERRED / 8 UNKNOWN** (v1: ~14
  VERIFIED / ~15 INFERRED / ~15 UNKNOWN).
- **% HUNL specification complete: ~87 %** (v1: ~55 %) — everything needed
  for solver + tree + datagen is VERIFIED; residual UNKNOWNs are
  training-stage details with documented defaults, plus the permanent
  abstraction-artifact rider.
- **% full HUNL project complete: ~12 %** (spec closed; G1.1–G1.3 of the
  ~13-step build certified; solver/tree/transitions/abstraction/NN/datagen
  outstanding).
- Reuse of certified Leduc system: **55–60 % unchanged, confidence
  upgraded** — P1 p.22 confirms the resolver is algorithmically identical
  to our certified engine (RM+, simultaneous, uniform skip-averaging,
  CFR-D gadget with opponent-optimal constraints).
- Compute reality check (P1 p.26): authors used **>175 CPU-core-years**
  (turn data) + **0.5 GPU-year** (flop data) — full-scale 10M/1M
  reproduction remains cluster-scale; certified reduced-scale first.

## 8. Gate G1 impact

G1.1 (`23f783f`), G1.2+G1.3 (`740f47b`) — **unchanged and unaffected**
(rule-level, source-independent; nothing in the primaries contradicts
them). Updates to FUTURE gates: river resolve gate uses **2000 iters /
1000 omitted** and Table-4 river menus as config defaults; G1.8/G1.9 gain
an author-defined reference protocol (Table 5: 9-option menu @ 4,000
iterations as ground-truth construction, L1/L2/L∞ in mbb/g over random
river situations); gadget certification must assert opponent-optimal
constraint semantics (S8).
