# HUNL_DATAGEN_SOURCE_AUDIT — original HUNL turn DataGeneration algorithm, reconstructed step by step

Date: 2026-08-13. Read-only parallel audit task (no production code touched).
Companion documents: `HUNL_DATAGEN_ORACLE_PLAN.md`,
`HUNL_DATAGEN_FAILURE_MATRIX.md`, `HUNL_DATAGEN_FREEZE_CHECKLIST.md`.

Authority: statuses here follow `HUNL_RECONSTRUCTION_SPEC.md` v2 (spec
freeze `f81d08c`); nothing below contradicts it. Status legend as in the
spec: **VERIFIED** (read from an in-session primary), **INFERRED**
(defensible, not explicit in a primary), **UNKNOWN** (no defensible value),
plus **PROJECT CANONICAL** (a choice this project freezes and documents
because the author artifact never existed publicly — explicitly *not*
author-BIT_EXACT).

## 0. Sources used (all in session)

| Tag | Artifact | Path |
|---|---|---|
| P1 | arXiv 1701.01724v3 main paper + Supplementary Materials (citations use P1 PDF page numbers; extracted text line numbers from `arxiv.txt` given as `L…`) | `/root/.claude/uploads/ab297466-…/0f135c39-1701.01724v3.pdf`; text `…/scratchpad/arxiv.txt` |
| P2 | Science reprint (main article; text identical to P1 pp.1–14) | `…/31a7f364-17science.pdf` |
| P3 | Burch thesis | `…/scratchpad/thesis.txt` |
| L | Author Leduc Lua (the only released author DataGeneration code) | `/workspace/deepstack_leduc_v1.1-bitexact-certified/reference_lua/Source/DataGeneration/{data_generation,range_generator,random_card_generator}.lua`, `Settings/arguments.lua` |
| DG | Bit-exact-certified Python port of L (Phase 2A/2B) | DS repo `datagen/` @ `7967622`; `DS_PHASE2A_CERTIFICATION.md`, `PHASE2B_PRODUCTION_DATASET.md` |
| ACPC | ACPC server + game defs | `/workspace/deepstack_leduc_v1.1-bitexact-certified/reference_lua/ACPCServer/` (`game.c`, `holdem.nolimit.2p.reverse_blinds.game`) |
| DH | DeepHoldem (corroboration only) | `/workspace/happypepper/deepholdem` |
| DY | DyypHoldem (corroboration only) | `/workspace/lucky72s/dyypholdem` |
| DE | DeeperStack (corroboration only; **cloned successfully this session**, `GIT_LFS_SKIP_SMUDGE=1`, depth 1) | `/workspace/godmoves/deeperstack` |

The original **HUNL** DataGeneration code was never released. Every HUNL
datagen statement therefore rests on (a) P1/P2 prose, (b) the author's
released **Leduc** datagen code as the author-code pattern, (c) the
project's bit-exact certification of that pattern (Phase 2A/2B).

---

## 1. The algorithm, step by step (turn network data)

Pipeline per sample: random board → pot → P1 range → P2 range → solve →
root CFVs → normalization → serialized input/target/mask.

| # | Step | Exact formula / pseudocode | Primary source | dtype | RNG draws | Status |
|---|---|---|---|---|---|---|
| 1 | Board sampling | Rejection sampler: `while n<4: c=random(1,52); if unused[c]: keep` — uniform over 4-subsets, order retained as drawn (project sorts ascending at serialization only) | P1 silent on the sampler; author-code pattern `random_card_generator.lua:16-32` (Leduc); certified port `datagen/generator.py:60-67` | int card ids | 4 accepted u32 + geometric rejections (§3) | Pattern **VERIFIED** (author Leduc code); use for 4-card HUNL **INFERRED / PROJECT CANONICAL** |
| 2 | Hand strength + sort order | strength(h) = P(beat uniform random hand at current public state); sort possible hands ascending by strength; keep `reverse_order` to unsort | P1 p.26 (quote §2.1); `range_generator.lua:60-76` (`batch_eval`, `sort`, double-argsort) | f32 strengths, long indices | **0** (deterministic stable argsort) | **VERIFIED** (both prose and author code) |
| 3 | Pot sampling | Pick interval uniformly from {[100,100), [200,400), [400,2000), [2000,6000), [6000,19950]}, then uniform **integer** within it | P1 p.25 footnote 2 (quote §2.3) | int chips | project scheme: 1 category + 1 integer u32 per sample; author draw mapping **UNKNOWN** | Distribution **VERIFIED as printed** (with the `[100,100)` anomaly, spec C3/U5); RNG mapping **PROJECT CANONICAL** |
| 4 | P1 range | `R(S,1)` stick-breaking over the 1128 strength-sorted possible hands; unsort; scatter into 1326-vector, blocked hands = 0 | P1 p.26 (quote §2.1); `range_generator.lua:18-52,88-102` | f32 (Torch7 default, `arguments.lua:6`) | 1127×batch f32 + 376 u32 (§3) | Procedure **VERIFIED**; odd-split detail per author code (§2.2) |
| 5 | P2 range | identical, independent draw | same | f32 | same | **VERIFIED** |
| 6 | Solve tree | Betting restricted to **{fold, call, pot-sized bet, all-in}**, no card abstraction; turn situations solved **to the end of the game** (turn betting → river chance → river betting with the same menu → showdown/fold terminals); root = start of turn betting, `bets=(pot,pot)`, first-to-act = seat0 (BB) per ACPC `firstPlayer 2 1 1 1` | P1 p.26 + P2/P1 p.8 (quotes §2.5); ACPC game def; Leduc root construction `data_generation.lua:100-109` | tree ints/f32 | 0 | **VERIFIED** (menu, no-abstraction, solve-to-end); root-player convention §2.9 |
| 7 | Solve | 1,000 iterations "CFR+" = RM+ regrets, simultaneous updates, uniform averaging over non-omitted iterations (hybrid, spec S1/C4); omitted count for datagen NOT stated → 500 | P1 p.26 (count); P1 p.22 (resolver semantics); `arguments.lua` `cfr_iters=1000, cfr_skip_iters=500` | f32 (author) / project turn engine f64 (documented deviation, HUNL_GOLDEN_BASELINE_V1 §15b) | 0 | Count **VERIFIED**; semantics **VERIFIED** (C4 verdict); omitted=500 **INFERRED** (spec D2) |
| 8 | Root CFVs | Average CFVs of both players at the root over non-omitted iterations (`get_root_cfv_both_players` pattern) | `data_generation.lua:110`; P1 p.26 targets | f32 (author) | 0 | **VERIFIED** (pattern) |
| 9 | Normalization | `values :mul(1/pot_size)` — divide by the **per-player committed** pot (the same number used for `bets={pot,pot}`), i.e. half the total pot | P1 pp.25-26 + P2/P1 p.8 ("fractions of the pot size"); the per-player-committed convention from `data_generation.lua:105-111` | f32; `1/pot` computed in double, applied as f32 mul (certified port `generator.py:148`) | 0 | "fractions of pot" **VERIFIED**; pot = per-player-committed **INFERRED** (author Leduc code values:mul(1/pot_size), spec §1.3 D10 note) |
| 10 | Serialization | inputs = [ranges, pot feature = pot/stack], targets = normalized CFVs, mask = possible-hand mask; f32 files | `data_generation.lua:76-127`; P2/P1 p.8 pot feature "fraction of the players' total stacks" | f32 | 0 | Structure **VERIFIED** (Leduc); HUNL byte layout **UNKNOWN forever** → **PROJECT CANONICAL** schema (freeze checklist §5) |

Batching: author Leduc generates in batches of `gen_batch_size=10`
(`arguments.lua`), one board per batch shared by 10 samples, ranges drawn
batched, pots per sample (Leduc `torch.rand(gen_batch_size,1)`).
P1 is silent on batching → batch=10 with shared board is **the author-code
pattern**, adopted **PROJECT CANONICAL** for HUNL (spec-consistent; also
used by DH/DY/DE, see §4 — though those draw only ONE pot per batch, a
deviation from the author Leduc per-sample pots; see conflict X4).

---

## 2. Focused audits (with quotes)

### 2.1 R(S,p) stick-breaking — P1 p.26 (arxiv.txt L1319-1332), quoted verbatim

> "the player ranges for the training situations need to cover the space of
> possible ranges that CFR might encounter during re-solving, not just
> ranges that are likely part of a solution. So we generated pseudo-random
> ranges that attempt to cover the space of possible ranges. We used a
> recursive procedure R(S, p), that assigns probabilities to the hands in
> the set S that sum to probability p, according to the following procedure.
> 1. If |S| = 1, then Pr(s) = p.
> 2. Otherwise,
> (a) Choose p1 uniformly at random from the interval (0, p), and let p2 = p − p1.
> (b) Let S1 ⊂ S and S2 = S \ S1 such that |S1| = ⌊|S|/2⌋ and all of the
> hands in S1 have a hand strength no greater than hands in S2. Hand
> strength is the probability of a hand beating a uniformly selected random
> hand from the current public state.
> (c) Use R(S1, p1) and R(S2, p2) to assign probabilities to hands in S = S1 ∪ S2.
> Generating a range involves invoking R(all hands, 1)."

Author-code realization (`range_generator.lua:26-40`): `p1 = p *
torch.rand(batch)` (note: `torch.rand` can return 0.0, so the code
implements U[0,p) rather than the prose's open interval (0,p) — measure-
zero difference, recorded), split, recurse; low half gets `mass1`, high
half `mass2`.

### 2.2 Odd-split behavior — DOCUMENTED CONFLICT (spec §4 C2)

- Supplement prose (above): |S1| = ⌊|S|/2⌋ — deterministic floor.
- Author released Leduc code `range_generator.lua:33-38` (comment at
  :33-34: "if the tensor contains an odd number of cards, randomize which
  way the middle card goes"):

  ```lua
  local halfSize = card_count/2
  if halfSize % 1 ~= 0 then
    halfSize = halfSize - 0.5
    halfSize = halfSize + torch.random(0,1)
  end
  ```

  i.e. |S1| ∈ {⌊|S|/2⌋, ⌈|S|/2⌉} chosen by one u32 draw **per odd node per
  call** (NOT per batch member — the draw is shared across the batch).
- Corroboration: DH `range_generator.lua:36-44`, DE
  `range_generator.lua:34-42`, DY `range_generator.py:44-49` all randomize.
- **Project verdict (code-anchored, spec C2, unchanged here):** implement
  the author-code randomized rounding; the supplement prose is treated as a
  simplified description. This is the behavior the project bit-certified
  against author-generated Leduc data (Phase 2A: 12/12 RNG streams
  byte-equal; range draw accounting verified over 3,000 batches).

Note the size-multiset invariance: whichever way the middle hand goes, the
child sizes are always {⌊n/2⌋, ⌈n/2⌉}; therefore the recursion's node-size
multiset — and hence the RNG draw COUNT — is deterministic (§3).

### 2.3 Pot distribution — P1 p.25 footnote 2 (arxiv.txt L1315-1318 + L1355-1356), quoted verbatim

> "The training situations were generated by first sampling a pot size from
> a fixed distribution which was designed to approximate observed pot sizes
> from older HUNL programs.²"
> Footnote 2: "The fixed distribution selects an interval from the set of
> intervals {[100, 100), [200, 400), [400, 2000), [2000, 6000),
> [6000, 19950]} with uniform probability, followed by uniformly selecting
> an integer from within the chosen interval."

Anomalies recorded exactly as in spec C3/U5, not resolved silently:
- **"[100, 100)"** is degenerate as printed (empty as a half-open
  interval). Project reading (spec C3): {100} singleton — corroborated by
  DH/DY/DE, all of which realize category 1 as constant 100.
- **[100, 200) gap**: no interval covers 101–199. As printed, pots
  101–199 are never generated.
- Half-open vs closed: the first four intervals print `)`, the last prints
  `]` — the last interval includes 19950.
- **19950 vs reachable range**: with stack 20000 and pot = per-player
  committed (§2.8), the maximum reachable committed value is 20000
  (all-in). 19950 = 20000 − 50 (one small blind short of all-in); at pot
  19950 a further all-in bet of 50 per player is still legal, so the
  datagen root is never itself an all-in. The supplement gives no
  rationale; recorded as-printed. Boundary pots 19949/19950 (and the
  never-generated 19951..20000 band) are adversarial-corpus items
  (ORACLE_PLAN corpus #31-33).

Author RNG mapping of the two-stage draw (which primitive, what order) is
**UNKNOWN** (HUNL code never released; the released Leduc code uses a
*different* pot law entirely — uniform f32 on [ante, stack−0.1],
`data_generation.lua:76-81`, certified in Phase 2A/2B for Leduc). The
project scheme (category draw + integer draw per sample via THRandom
`random_range`) is **PROJECT CANONICAL**.

### 2.4 Board sampling

P1/P2 are **silent** on how boards were sampled (only "randomly generated
… public cards", P2/P1 p.8 L332-334, and "ten million poker turn
situations (from after the turn card is dealt)", P1 p.26 L1335). The
author-code pattern is the Leduc rejection sampler
(`random_card_generator.lua:16-32`): draw `torch.random(1, card_count)`,
reject already-used cards, until `count` accepted — uniform over subsets.
Docstring (":10-12"): "Each subset of the deck of the correct size is
sampled with uniform probability." Status: sampler **VERIFIED as the
author-code pattern (Leduc)**, its use for 4-of-52 **INFERRED / PROJECT
CANONICAL**. DH/DY/DE reuse the identical sampler for HUNL boards.

### 2.5 The {F,C,P,A} datagen tree — P1 p.26 (L1332-1335) + P2/P1 p.8 (L334-336), quoted

> "the situations were approximately solved using 1,000 iterations of CFR+
> with only betting actions fold, call, a pot-sized bet, and all-in." (P1 p.26)

> "The target counterfactual values for each training game were generated
> by solving the game with players' actions restricted to fold, call, a
> pot-sized bet, and an all-in bet, but **no card abstraction**." (P2/P1 p.8)

So the DATAGEN tree menu is {F,C,P,A} at **every** decision point — it is
NOT the richer Table-4 play-time turn menu (which has ½P at the first
action). Turn situations are solved to the end of the game (P1 p.26
L1335-1337: "ten million poker turn situations … were generated and
solved", with the flop paragraph explicitly contrasting the depth-limited
flop solves). **VERIFIED.**

### 2.6 1,000 CFR iterations; omitted iterations

- 1,000 iterations: **VERIFIED**, P1 p.26 (quote above). "CFR+" wording is
  read per spec conflict C4 as the hybrid resolver (RM+, simultaneous,
  uniform skip-averaging) — the author's own released Leduc datagen
  implements exactly that, and it is what this project bit-certified.
- Omitted (burn-in) iterations for DATAGEN solves: Martin Schmid stated in
  direct email (2026-08-16) that he thinks **skip iterations were always used**.
  This closes the former skip-vs-no-skip fork. The email does **not** state the
  exact count. `arguments.lua` ships `cfr_skip_iters = 500` and the author
  Leduc datagen path uses it; DH/DY/DE also use 1000/500. Status:
  **AUTHOR-CONFIRMED skip existence; exact count 500 RELEASED-CODE-ANCHORED**
  (spec D2).

### 2.7 Target scaling — fractions of pot

P1 p.25-26 (L1312-1314): "The output of the network are vectors of
counterfactual values, one for each player. The output values are
interpreted as fractions of the pot size to improve generalization across
poker situations." P2/P1 p.8 (L329-330) agrees. **VERIFIED.**

Which "pot" divides the CFVs is not spelled out in the primaries. The
author Leduc code (`data_generation.lua:105-111`) sets
`current_node.bets = {pot_size, pot_size}` and then
`root_values:mul(1/pot_size)` — i.e. the normalizer is the **per-player
committed** amount (= half the total pot). **INFERRED** for HUNL (spec
D10 note); adopted by the certified Leduc port (`generator.py:148`, with
the exact double→f32 cast chain preserved) and by DH/DY/DE identically.

### 2.8 Zero-sum correction — NOT part of datagen targets

P2/P1 p.8 (L319-325): the zero-sum enforcement is an **outer network**
("This architecture is embedded in an outer network that forces the
counterfactual values to satisfy the zero-sum property … Half the actual
sum is then subtracted …. This entire computation is differentiable and
can be trained with gradient descent."). It is a network-graph component,
applied at training/inference time — the datagen TARGETS are the raw
(normalized) root CFVs and are NOT zero-sum-corrected. Phase-2A D2
elimination experiment #6 confirmed empirically that the author's bundled
Leduc targets carry no correction signature. **VERIFIED** (placement).
Consequence: the measured zero-sum residual of stored targets is a QA
*statistic with a tolerance*, never an exactness assertion
(FAILURE_MATRIX F-05, FREEZE_CHECKLIST QA row).

### 2.9 Mask / bucket semantics — bucketing is training-side for HUNL

- Datagen solves: "no card abstraction" (P2/P1 p.8, quote §2.5) —
  **VERIFIED**.
- Bucketing (1,000 clusters): "map the original ranges into distributions
  over these clusters **as the first layer of the neural network** (see
  Figure 3 of the main article)" — P1 p.27 (L1379-1382), Fig. 3 p.9.
  For HUNL, bucketing lives INSIDE the network graph; the datagen product
  is card-space. **VERIFIED.**
- Contrast with the released Leduc pipeline, which buckets at datagen
  serialization time (`data_generation.lua:57-64,86-123`: inputs/targets
  are bucket-space, mask = possible-BUCKET mask) — a Leduc-specific
  training-code choice, certified for Leduc in Phase 2A/2B, and NOT the
  HUNL description. The project HUNL dataset therefore stores 1326
  card-space ranges/targets + card-space possible-hand mask
  (**PROJECT CANONICAL** schema, FREEZE_CHECKLIST §5); DH/DY/DE also store
  card-space (1326) at datagen.

### 2.10 Player-order conventions

ACPC game def `holdem.nolimit.2p.reverse_blinds.game`: `blind = 100 50`,
`firstPlayer = 2 1 1 1` (1-based) — seat0 posts the big blind and acts
FIRST on every postflop round; seat1 (SB/dealer) acts first preflop only.
**VERIFIED** (ACPC primary; `game.c` parses/enforces it; certified into
`hunl/config.py` `first_player=(1,0,0,0)` and 14,199 identical ACPC oracle
replies, HUNL_GOLDEN_BASELINE_V1 item 3).

Datagen root for a turn sample: current player = first-to-act on the turn
= seat0 = BB. Author Leduc pattern (`data_generation.lua:104`):
`current_node.current_player = constants.players.P1` with ranges tensor
index 1 = P1 = the root actor, targets = [P1 block | P2 block]. Project
convention: block 1 = seat0 = BB = root actor. **The P1-block/seat/actor
triple must be asserted, not assumed** — DeepHoldem demonstrably permutes
it (its postflop datagen root is `constants.players.P2`,
`data_generation.lua:124`; conflict X8 in §4). A silent swap produces
valid-looking data with players' targets exchanged (FAILURE_MATRIX F-02).

---

## 3. RNG draw ledger — one HUNL turn batch under the certified THRandom scheme

Scheme: the Phase-2A certified THRandom stream (bit-exact vs untouched
`THRandom.c`, 12/12 streams; `datagen/th_random.py`: `random_u32`,
`rand_float(n)` = n uniform f32 draws, `random_range(a,b)` = 1 u32 draw).
Batch = 10 samples sharing one board (author-code pattern, §1). Every
uniform float and every `random_range` consumes exactly one Mersenne
Twister u32 state draw.

Turn board: 4 cards ⇒ possible hands = C(48,2) = **1128**.
Stick-breaking recursion over 1128 leaves ⇒ **1127 internal nodes**
(any full binary recursion over n leaves has n−1 internal nodes).
Odd-sized internal nodes under recursive halving of 1128: **376**
(computed by direct recursion; deterministic because child sizes are
always {⌊n/2⌋, ⌈n/2⌉} regardless of the randomized middle-card direction,
§2.2). Cross-check of the counting method on Leduc (5 hands): 4 internal
nodes, 2 odd ⇒ per batch 2×(4×10+2) = 84 range draws — exactly the
certified Phase-2A accounting "1 board + 84 range + 10 pot u32 draws".

| Ledger line | Draws per batch of 10 | Primitive | Status |
|---|---|---|---|
| 1. Board: accepted draws | 4 | `random_range(1,52)` ×4 | Sampler semantics **VERIFIED** (author Leduc code); 4-card use **INFERRED / PROJECT CANONICAL** |
| 2. Board: rejections | G ≥ 0, variable; E[G] = 52/51+52/50+52/49 − 3 = **0.120832…** (E[total draws] = Σ_{k=0..3} 52/(52−k) = 4.120832…); unbounded with geometric tail | `random_range(1,52)` | Count law **VERIFIED** (follows from the sampler); conditional-draw hazard: G couples the stream to board content (FAILURE_MATRIX F-01) |
| 3. Sort by hand strength | **0** — deterministic stable argsort, no RNG | — | **VERIFIED** (`range_generator.lua:70-73`) |
| 4. P1 range: stick-breaking floats | 1127 internal nodes × 10 batch members = **11,270** f32 draws (one `rand_float(10)` call per internal node, batched exactly as `torch.rand(batch_size)` at `range_generator.lua:26`) | `rand_float(10)` ×1127 | Pattern **VERIFIED** (author code semantics, bit-certified for Leduc); node count 1127 computed for 1128 hands |
| 5. P1 range: odd-split draws | **376** (one per odd-sized internal node, shared across the batch — NOT per member) | `random_range(0,1)` ×376 | Pattern **VERIFIED** (author code `range_generator.lua:37`); count 376 computed, deterministic (§2.2) |
| 6. P2 range: floats | **11,270** | as line 4 | as line 4 |
| 7. P2 range: odd-split | **376** | as line 5 | as line 5 |
| 8. Pots | 10 × (1 category + 1 in-interval integer) = **20** | `random_range` ×2 per sample | **PROJECT CANONICAL** (distribution VERIFIED per §2.3; author primitive mapping **UNKNOWN**; author Leduc pot law differs and used 10 `rand_float` draws/batch) |
| 9. Solve / CFVs / normalization / serialization | **0** — fully deterministic | — | **VERIFIED** (no RNG anywhere downstream of sampling; Phase-2A/2B replay evidence) |
| **Total u32 state draws per batch** | **23,316 + G** (= 4+G board + 2×11,270 float + 2×376 odd + 20 pot) | | |
| **Amortized per sample** | 2,331.6 + G/10 | | |

Draw ORDER within a batch (author Leduc order, `data_generation.lua:66-81`,
adopted PROJECT CANONICAL): board → P1 range → P2 range → pots. NOTE the
author Leduc code draws pots AFTER ranges even though the supplement prose
describes pot "first" (P1 p.25 L1315) — prose order is narrative, code
order is normative for stream reproduction; any reordering changes every
downstream sample (FAILURE_MATRIX F-01).

Conditional draws: ONLY ledger line 2 is conditional (board rejections).
Lines 4-7 are unconditional in count for a fixed board size; line 5/7
counts would change only if the possible-hand count changed (it cannot on
a legal 4-card board: always 1128).

---

## 4. Cross-project comparison table (every extractable DataGeneration detail)

Primary = P1/P2 prose (+ author Leduc code where the primaries are
silent). File anchors: DH `Source/DataGeneration/data_generation.lua`
(pot table at :69-99, root at :118-131), DE
`Source/DataGeneration/data_generation.lua` + `Source/tools.lua:64-85`,
DY `src/data_generation/data_generation.py`. Every conflict is reported;
none is silently unified.

| Parameter | PRIMARY DEEPSTACK | DEEPHOLDEM | DYYP | DEEPERSTACK | VERDICT |
|---|---|---|---|---|---|
| Pot intervals | {[100,100), [200,400), [400,2000), [2000,6000), **[6000,19950]**} (P1 p.25 fn.2) | min {100,200,400,2000,6000} / max {100,400,2000,6000,**18000**} (`data_generation.lua:73-74`) | same as DH, max **18000** (`data_generation.py:85-86`) | same as DH, max **18000** (`tools.lua:69-70`) | **Primary: 19950** (spec C3 verdict). All three secondaries share DH's 18000 (common descent from DH); rejected. **Conflict X1.** |
| First interval realization | "[100,100)" as printed (degenerate) | constant 100 (pot_range=0) | constant 100 | constant 100 | {100} singleton reading corroborated 3× ; anomaly stays recorded (U5). |
| Integer pot | "uniformly selecting an integer from within the chosen interval" | `math.floor(lo + U[0,1)*(hi−lo))` ⇒ ints lo..hi−1 (18000 never hit) | same | same | **Primary wording**; project realizes it as `random_range(lo,hi)` inclusive (PROJECT CANONICAL). Secondaries' floor-of-float is a distributionally different endpoint treatment. **Conflict X2 (minor).** |
| Pot draw granularity | "first sampling a pot size" per situation (prose, per-situation reading); author Leduc: **per-sample** pots within a batch (`torch.rand(gen_batch_size,1)`, `data_generation.lua:81`) | **ONE pot per batch of 10** (`:92-99` scalar, `inputs :fill`) | one per batch (`:88-92`) | one per batch (`:86-91`) | **Per-sample pots** (author-code pattern + prose). Secondaries' shared pot halves sample diversity per batch. **Conflict X4.** |
| Board sampler | silent; author Leduc rejection sampler | identical rejection sampler | identical (port) | identical | Rejection sampler, uniform subsets (INFERRED for HUNL, unanimous). |
| Range generator R(S,p) | P1 p.26 prose (⌊|S|/2⌋) | author code with randomized odd split | same (port) | same | Randomized odd split — **spec C2 code-anchored verdict**, all code unanimous vs prose. **Conflict X3 (prose vs code, documented).** |
| Range space | card-space solves, "no card abstraction"; HUNL bucketing NN-side (P1 p.27) | 1326 card-space inputs/targets at datagen | same | same | Card-space datagen product. (Author LEDUC datagen bucketed at write time — Leduc-specific, §2.9.) |
| Batch size | silent (author Leduc `gen_batch_size=10`) | 10 | 10 | 10 | **10** — author-code pattern, unanimous; PROJECT CANONICAL for HUNL. |
| Turn sample count | **10,000,000** (P1 p.26) | `train_data_count=150000` (self-admitted reduction) | configurable | `train_data_count=1500000` | Primary 10M. Secondaries are scale reductions, not conflicts of record. |
| Flop samples | 1,000,000, depth-limited with turn net (P1 p.26) | reduced, same structure | same structure | same structure | Primary. |
| Aux/preflop samples | 10,000,000; targets = average flop-net over all 22,100 flops (P1 p.26) | `aux_data_generation` variant | port of DH | variant present | Primary. |
| Solver iterations | 1,000 (P1 p.26); omitted **not stated** | 1000 / skip 500 (`arguments.lua:30,32`) | 1000/500 (`arguments.py:41-43`) | 1000/500 (`arguments.lua:31,33`) | 1000 VERIFIED; **skip existence AUTHOR-CONFIRMED (Schmid 2026-08-16); exact 500 RELEASED-CODE-ANCHORED (D2)**. |
| Action set | {F, C, P, A}, no card abstraction (P1 p.26, P2 p.8) | `bet_sizing={1}` ⇒ {F,C,P,A} | same | same | **{F,C,P,A}** unanimous. |
| Normalization | "fractions of the pot size" | `root_values:mul(1/pot_size)` with `bets={pot,pot}` | same | same | Divide by per-player committed pot (INFERRED convention, unanimous in code). |
| Root player (turn) | first-to-act postflop = BB = seat0 (ACPC `firstPlayer 2 1 1 1`) | postflop root `current_player = constants.players.P2` (`:124`) — the block-1/actor pairing is permuted relative to the author Leduc pattern (root actor = P1 = block 1) | same as DH (`:118`) | same as DH (`:118`) | Project: root actor = seat0 = BB = **block 1** (ACPC-anchored, G1-certified). DH-family labeling differs — **Conflict X8: do not import any DH-family player-indexing code or data without an explicit seat-mapping audit.** |
| Solver dtype | Torch7 f32 (P1 p.26 "built-in Torch7 libraries"; INFERRED f32 default, spec §5.2) | f32 (+ GPU) | f32/f64 torch | f32 | f32 author-side; project turn engine is f64 (documented deviation, HUNL_GOLDEN_BASELINE_V1 §15b). |
| Datagen output files | never released (HUNL) | `.inputs`/`.targets` per batch, **no mask file saved** (mask computed, unsaved) | `.inputs`/`.targets`, timestamped names | `.inputs`/`.targets` per batch | HUNL byte layout **UNKNOWN forever** → PROJECT CANONICAL schema HUNL_TURN_DATASET_V1. Timestamped filenames (DY) are a reproducibility anti-pattern (FAILURE_MATRIX F-14). |
| Pot feature | "pot size as a fraction of the players' total stacks" (P2/P1 p.8) | `pot/stack`, stack=20000 | same | same | committed/20000 (INFERRED reading, unanimous). |

Corroboration caveat (unchanged from spec): DH/DY/DE are secondary and
share ancestry (DY and DE are DH derivatives — DY is a Python port, DE a
fork); their agreement is ONE independent data point, not three.

---

## 5. Status tally for the turn-datagen algorithm (this audit's scope)

- **VERIFIED (from primaries / author code / ACPC):** 14 — R(S,p)
  procedure; hand-strength definition + sort determinism; pot distribution
  as printed; {F,C,P,A} menu; no card abstraction; solve-to-end for turn;
  1,000 iterations; resolver semantics (S1/C4); root-CFV targets;
  fractions-of-pot scaling; zero-sum correction network-side (not in
  targets); bucketing training-side for HUNL; player order (ACPC);
  10M/1M/10M sample counts.
- **PARTIAL-AUTHOR / RELEASED-CODE (D2):** skip iterations exist (Schmid 2026-08-16); exact count = 500 remains released-code-anchored.
- **INFERRED (3):** pot = per-player
  committed as the normalizer and bets value; pot feature = committed /
  20000; board rejection-sampler applied to 4-of-52 (+ Torch7 f32
  conventions, spec §5.2, counted with the spec not here).
- **UNKNOWN (4):** author RNG primitive mapping/order for the two-stage
  pot draw; intended reading of "[100,100)" and the [100,200) gap (U5);
  original HUNL datagen serialization/byte layout (permanent); author
  batch/parallelization layout on the 6,144-core run (affects nothing
  reproducible).
- **PROJECT CANONICAL (5):** THRandom stream + draw order (board → P1 →
  P2 → pots); pot draw realization (`random_range` category + inclusive
  integer); batch=10 shared board; f64 solve engine (vs author f32);
  HUNL_TURN_DATASET_V1 schema.

No status here contradicts HUNL_RECONSTRUCTION_SPEC v2; lines D1-D10 and
conflicts C2/C3/C4 are restated with their original verdicts.
