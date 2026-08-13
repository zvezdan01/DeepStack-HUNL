# HUNL PORT GAP AUDIT — Leduc Certified Baseline → Full HU No-Limit Hold'em

> **v1.1 note (2026-08-13):** the parameter sheet, asset inventory, Gate-G1
> plan and project estimates are superseded by
> **`HUNL_RECONSTRUCTION_SPEC.md`** (adds DeepHoldem/DyypHoldem
> corroborating clones, VERIFIED/INFERRED/UNKNOWN parameter statuses, and
> the M-HUNL-0 milestone). The per-component analysis below remains valid.

Date: 2026-08-13. Scope: **audit only — nothing implemented, nothing modified.**
Baselines frozen: Golden Baseline `2ab6dde…`, certified datagen `7967622…`,
Phase-2B dataset (110k) + manifests.

## 0. Source inventory (what this audit is grounded on)

**Verified, in session (on disk):**
- Certified Python engine `deepstack_leduc/` (3,044 LOC) + `datagen/` (~700 LOC),
  both bit-certified against the released Lua.
- Released author Lua `reference_lua/Source/**` (the DeepStack-Leduc tutorial
  codebase — itself a *reduced instance of the real DeepStack architecture*,
  per its own docs).
- **`reference_lua/ACPCServer/`** — the official ACPC dealer with FULL
  Hold'em support: `game.c/h` (game definition parser, betting legality,
  `rankHand`), **`evalHandTables` (complete 7-card evaluator lookup
  tables)**, `dealer.c`, `rng.c`, and the exact game definition
  `holdem.nolimit.2p.reverse_blinds.game`:
  `numPlayers=2, numRounds=4, stack=20000 20000, blind=100 50,
  firstPlayer=2 1 1 1, numSuits=4, numRanks=13, numHoleCards=2,
  numBoardCards=0 3 1 1`. This is the ACPC HUNL game DeepStack played —
  **exact game settings are therefore in-session, certified provenance.**
- **`third_party/CFR_plus/`** — Tammelin's game-general CFR+ (already used as
  our certified oracle): reads ACPC `.game` files, ships
  `holdem.limit.2p.reverse_blinds.game`, `betting_tools.c`, `card_tools.c`,
  and the same `evalHandTables`. A ready-made *large-game CFR+ oracle*.
- `davis20asupp.pdf` (uploads) — Davis/Schmid/Bowling, MCCFR with
  baseline-corrected values (pseudocode): evaluation-variance-reduction
  reference (AIVAT-family), NOT a source of HUNL game/NN parameters.
- `1809.03057v1.pdf` (uploads) — VR-MCCFR: same category.

**NOT in session (verified unavailable):**
- DeepStack Science paper supplementary materials (arXiv 1701.01724 /
  Science aai1110 supplement) — egress proxy blocks arxiv.org.
- Burch PhD thesis *Time and Space: Why Imperfect Information Games are
  Hard* (2017) — egress blocks poker.cs.ualberta.ca and the ERA repository
  (public URLs exist and were located; download attempts returned proxy 403).
- The real DeepStack HUNL implementation was **never publicly released**;
  no author-side HUNL solver traces or weights exist anywhere.

Consequence: every HUNL-specific *parameter* below that is not in the ACPC
game file (bet-sizing tables used in re-solving, bucket counts, NN layer
sizes, DataGeneration sample counts and pot-sampling ranges, per-street CFR
iteration counts) is currently **model-knowledge only — flagged UNVERIFIED**
and must be re-verified against the actual supplement/thesis PDFs (owner
upload needed) before any implementation is certified against them.

Legend per component: **(1)** current Leduc file/function → **(2)**
game-independent? → **(3)** verdict → **(4)** reason → **(5)** HUNL
dims/structures → **(6)** available original HU oracle/source → **(7)**
certification path → **(8)** main risk.

---

## 1. CFR / CFR+ primitives

1. `deepstack_leduc/lookahead.py` (regret-matching+, 999999 caps,
   `regret_epsilon`, skip-500 averaging; ~200 LOC of pure math),
   `lookahead_recursive_reference.py`; Lua `Lookahead/lookahead.lua`,
   `Tree/tree_cfr.lua`. (`cfr.py` remains QUARANTINED — M1.)
2. Game-independent: all ops are dense tensor algebra over
   (action × parent × grandparent × hand) — the hand dimension is just a size.
3. **REUSE AS-IS** (hand-dim 6 → 1326).
4. Not one line of update math references Leduc; certified semantics
   (f32, clamp order, averaging window) carry over unchanged.
5. Hand dim 1326; per-street lookahead tensor shapes otherwise identical.
6. Tammelin CFR+ (in-session, certified BIT_EXACT twice) is game-general and
   reads Hold'em `.game` files → usable as a *limit-holdem* CFR+ oracle at
   full 52-card scale; Kuhn/Leduc frozen checkpoints remain regression
   anchors.
7. BIT_EXACT: (a) Leduc regression must stay byte-identical after
   dim-parameterization; (b) small-holdem/limit-holdem checkpoint runs vs
   Tammelin `cfr.c` (int-quantized protocol already built in Phase 6).
8. Risk: memory/latency of dense 1326-wide tensors (the real DeepStack ran
   this on GPU). Math untouched, but a performance refactor pressure exists —
   must be resisted or proven byte-neutral.

## 2. CFR-D gadget

1. `deepstack_leduc/cfrd_gadget.py` (66 LOC) = `Lookahead/cfrd_gadget.lua`.
2. Game-independent: pure hand-vector ops (play/terminate regrets, epsilon,
   999999 caps — M2-patched).
3. **REUSE AS-IS** (vector length 1326).
4. Zero game references; certified vs author Lua (F5/F1/F2).
5. Opponent CFV vector length 1326.
6. Burch thesis has the construction + proofs (NOT in session); the author
   Lua gadget (in session) is the operative oracle and already certified.
7. BIT_EXACT: Leduc regression + dim-blind unit properties (gadget output
   invariance under permutation of hand indices).
8. Risk: minimal — smallest, best-certified component.

## 3. Continual resolving

1. `deepstack_leduc/continual_resolving.py` (141 LOC) =
   `Player/continual_resolving.lua`; state carry of own range + opponent
   CFVs across actions.
2. Mixed: the protocol (resolve → store CFVs of chosen action → advance) is
   game-independent; street bookkeeping is Leduc-2-street (`street == 1/2`
   branches, single chance transition).
3. **ADAPT.**
4. Logic transfers; needs 4-street state machine, chance advance over
   flop(3)/turn(1)/river(1), and HUNL blind/position asymmetry
   (`firstPlayer = 2 1 1 1`: SB acts first preflop, BB first postflop —
   Leduc has antes and fixed P1-first on both streets).
5. Per-street resolve contexts; 1326 CFV carry; position-dependent player
   mapping.
6. **No author HUNL oracle exists** (DeepStack HUNL source unreleased).
   Paper §Continual re-solving describes the protocol (UNVERIFIED in
   session).
7. NUMERIC/BEHAVIORAL: self-consistency invariants (CFV monotonicity,
   zero-sum residuals), Leduc regression BIT_EXACT, match-play sanity vs
   ACPC dealer. TRACE_EXACT impossible (no traces exist).
8. Risk: position asymmetry bugs — subtle, no external oracle; needs a
   purpose-built invariant suite.

## 4. Depth-limited resolving

1. `deepstack_leduc/lookahead_builder.py` (295 LOC),
   `resolving.py` (91 LOC), street-2 NN boxes in `lookahead.py`
   (`_construct_transition_boxes`, M4-patched).
2. Mixed: layered-tensor construction is structural; "next street = NN"
   boundary is Leduc-shaped (exactly one transition).
3. **ADAPT** (builder, resolving protocol) + **REPLACE** (transition
   plumbing → per-street value networks).
4. Real DeepStack does the same thing per street (turn boxes call turn NN,
   etc.); the Leduc code is the same architecture with one street removed.
5. Lookahead depth-limited at end of current street; NN boxes per
   next-street board set: flop→turn 49 boards, turn→river 48; preflop aux
   network (paper, UNVERIFIED) short-circuits preflop resolves.
6. Paper/supplement pseudocode (NOT in session). Our own certified Leduc
   trace corpus anchors the shared machinery.
7. Leduc regression BIT_EXACT for shared code; HUNL construction NUMERIC
   (exact river resolve with no NN is fully checkable — see §Roadmap gate).
8. Risk: correctness of value-box normalization across 49/48-board batches
   (Leduc's `/(board_count-2)` style constants must be re-derived, not
   copied).

## 5. Public tree builder

1. `deepstack_leduc/tree.py::PokerTreeBuilder` (116 LOC) =
   `Tree/tree_builder.lua` (241 LOC); datagen `LuaF32TreeBuilder` overlay.
2. Mixed: recursion + fold/call/raise skeleton game-independent; chance
   expansion `for b in range(6)`, 2 streets, ante model Leduc-specific.
3. **ADAPT.**
4. Same recursion; needs 4 rounds, blind posting, per-street first-player,
   chance nodes dealing 3/1/1 cards, raise-cap/all-in rules.
5. Public tree keyed by betting sequence + board; chance branching 
   flop C(50,3)=19,600 / turn 49 / river 48 (within a resolve: 49/48 only —
   full flop enumeration never sits in one tree).
6. **ACPC `game.c` in session** encodes exact betting legality (min-raise,
   all-in, firstPlayer) — an executable oracle.
7. **BIT_EXACT vs ACPC dealer**: enumerate our tree's legal action sets vs
   `game.c` (`raiseIsValid`, `numActions`) state-by-state; Leduc regression
   stays BIT_EXACT.
8. Risk: min-raise edge cases (partial raise all-in reopening betting) —
   classic NL bug nest; mitigated by the dealer oracle.

## 6. Private-hand representation

1. `deepstack_leduc/cards.py` (60 LOC): card = one of 6 ints; hand = card.
2. Leduc-specific by definition.
3. **REPLACE.**
4. HUNL private hand = unordered pair of 52 cards → 1326 combos; needs
   canonical hand indexing, hand↔cards maps, per-board possibility masks.
5. `hand_index(c1,c2)` (1326), `hand_cards[1326,2]`, board-blocking masks;
   (optional later: suit-isomorphism canonicalization — NOT needed for
   correctness, only for efficiency; original DeepStack did not bucket by
   isomorphism at the range representation level per paper — UNVERIFIED).
6. ACPC `card_tools.c` + `game.h` card encoding (rank×4+suit) in session.
7. BIT_EXACT: exhaustive combinatorial self-checks (counts, bijectivity),
   cross-check card encoding vs ACPC.
8. Risk: index-order conventions leaking into NN input ordering — freeze the
   ordering contract first, document, test exhaustively.

## 7. Ranges

1. `deepstack_leduc/card_tools.py` (uniform_range, is_valid_range,
   normalize_range, possible_hand_indexes).
2. Game-independent *given* a possible-hands primitive.
3. **REUSE AS-IS** (API), **ADAPT** (possible-hands = combos disjoint from
   board).
4. All range ops are mask+normalize over the hand vector.
5. f64 range vectors of 1326 (engine boundary f32 where certified so).
6. Author Lua `Game/card_tools.lua` (in session) for semantics.
7. BIT_EXACT: property tests + Leduc regression.
8. Risk: low.

## 8. Chance nodes

1. `tree.py` chance expansion; `terminal.py::_call_matrix` street-1
   averaging (`sum/4.0`); lookahead chance layers.
2. Leduc-specific numerics (6 boards, /4 normalization = per-hand possible
   continuations).
3. **REPLACE** (weights/enumeration), **ADAPT** (structure).
4. HUNL chance weights are card-removal-dependent: P(next card | hands) —
   the 1/(board_count-2)-style constants become 1/45-style per-street
   constants (2 hole cards block 2 of remaining deck: river weight
   1/(52-2·2-4)=1/44 per hand pair… must be *derived*, not assumed —
   the Leduc code derives them implicitly via masks).
5. Board enumeration per transition (49/48), chance-weight tensors
   consistent with blocking.
6. No direct oracle; ACPC dealer deals uniformly (statistical check);
   algebraic identities (chance weights row-sum 1 under masks).
7. NUMERIC + exhaustive algebraic identity tests; Leduc regression
   BIT_EXACT.
8. Risk: **highest correctness risk of the tree layer** — silent
   mis-weighting distorts every CFV downstream and no author trace can
   catch it.

## 9. Card evaluator

1. `deepstack_leduc/cards.py::hand_strength` (pair/high-card over 3 ranks)
   = `Game/Evaluation/evaluator.lua`.
2. Leduc-specific.
3. **REPLACE.**
4. HUNL needs best-5-of-7 ranking.
5. `evaluate7(2 hole + 5 board) -> int rank` for all 1326 hands per river
   board.
6. **`evalHandTables` + `game.c::rankHand` in session (two identical copies:
   ACPCServer and CFR_plus)** — the official ACPC evaluator, C, certifiable
   provenance (used by the real dealer DeepStack played against).
7. **BIT_EXACT**: bind/port and compare vs compiled original over exhaustive
   enumerations (all 1326 hands × sampled boards; full exhaustion feasible
   offline: ~2.8M ranks/board set) — same untouched-C-oracle pattern as
   Phase 2A THRandom.
8. Risk: low — perfect oracle available; only binding bugs possible.

## 10. Card blocking

1. Implicit in `terminal.py` (fold matrix = 1−I masked) and
   `possible_mask` — trivial in Leduc (hands collide iff same card).
2. Leduc-specific instance of a general concept.
3. **REPLACE.**
4. HUNL: hands block each other iff they share ≥1 card → 1326×1326
   crosstalk matrix (≈7 MB f32, dense is fine); board-blocking masks per
   street.
5. `blocker_matrix[1326,1326]`, per-board `possible_hands` masks.
6. Combinatorics (self-oracle) + ACPC card encoding.
7. BIT_EXACT via exhaustive recount (each entry independently derivable).
8. Risk: low but load-bearing — feeds terminal equity and chance weights;
   certify before anything that consumes it.

## 11. Flop/turn/river transitions

1. `deepstack_leduc/next_round_value.py` (195 LOC) =
   `Nn/next_round_value.lua`: batch all next boards, bucketize, NN, un-bucketize,
   normalize.
2. Structure general; constants and single-transition shape Leduc-specific.
3. **ADAPT** (structure) + **REPLACE** (constants, per-street instances).
4. Same pipeline exists per HUNL transition with per-street nets and
   1000-bucket spaces (bucket count UNVERIFIED).
5. Three instances: preflop→flop (aux net path), flop→turn (49 boards),
   turn→river (48); range/value scatter matrices per board batch.
6. Paper/supplement (NOT in session); no traces.
7. NUMERIC: algebraic round-trip identities (bucketize∘unbucketize on
   possible sets), zero-sum preservation; Leduc regression BIT_EXACT for the
   shared skeleton.
8. Risk: normalization constants (see §8) and bucket-scatter correctness at
   1000 buckets.

## 12. No-limit betting / bet sizing

1. `deepstack_leduc/tree.py::BetSizing` = `Game/bet_sizing.lua` (63 LOC):
   pot-fraction bets `cfg.bet_fractions=(1.0,)` + all-in.
2. Game-independent mechanism; Leduc uses one fraction.
3. **ADAPT.**
4. Real DeepStack restricted re-solve actions to a per-round,
   per-action-depth fraction table (e.g. first action {F,C,½P,P,2P,A}, later
   fewer — exact table in supplement, **UNVERIFIED in session**); mechanism
   = same possible_bets loop + ACPC min-raise/all-in legality.
5. Fraction table keyed by (street, action-depth); min-raise state
   (raise-to amounts, reopening rules); chip integer granularity (ACPC
   chips are ints — Leduc engine uses f32/f64 pots; decide and freeze).
6. ACPC `game.c` (legality, in session); supplement (fraction table, NOT in
   session).
7. Legality BIT_EXACT vs ACPC; fraction-table fidelity blocked on
   supplement.
8. Risk: fraction table unknown-in-session → any implementation now would
   encode guesses. **Blocker for paper-faithful reconstruction.**

## 13. Stacks / pots

1. `deepstack_leduc/config.py` (ante=100, stack=1200); pots as f32 chains
   (certified in datagen).
2. Config-level; ante model Leduc-specific.
3. **ADAPT.**
4. HUNL: blinds 50/100, stacks 20000 (in-session ACPC file, VERIFIED);
   position swap per hand; pot normalization by stack (paper normalizes by
   pot — Leduc datagen divides CFVs by pot; same pattern).
5. `Config(blinds=(50,100), stack=20000, rounds=4, …)`.
6. `holdem.nolimit.2p.reverse_blinds.game` (in session).
7. BIT_EXACT (trivially checkable constants; dealer agreement).
8. Risk: low; watch the reverse_blinds convention (blind = "100 50" with
   firstPlayer 2 — seat→blind mapping must match dealer exactly).

## 14. Terminal utilities

1. `deepstack_leduc/terminal.py` (49 LOC) = `TerminalEquity/*` (160 LOC Lua).
2. Mechanism general; matrices Leduc 6×6.
3. **ADAPT** (fold path) + **REPLACE** (call path).
4. Fold matrix → blocker-normalized mass exclusion (needs card-removal
   normalization 1/C(48,2)-style row weights — in Leduc this is uniform);
   call matrix at river → sign(rank_i − rank_j) masked by blockers, per
   board; all-in pre-river → expectation over runouts (real DeepStack
   computed this by enumeration or NN — supplement detail, UNVERIFIED).
5. Per-river-board 1326×1326 win/lose/tie matrices (constructed on demand;
   7 MB each, cacheable); fold matrices per street.
6. Evaluator oracle (in session) makes showdown matrices independently
   derivable; Lua `terminal_equity.lua` for structure.
7. **BIT_EXACT** achievable: matrices are deterministic functions of the
   certified evaluator; verify by independent recount + symmetry/zero-sum
   identities.
8. Risk: all-in runout handling (design decision with math consequences,
   needs supplement).

## 15. Bucketing / abstraction

1. `deepstack_leduc/bucketing.py` (65 LOC): **identity** bucketing
   (36 = board×card) — no abstraction at all.
2. Leduc-trivial.
3. **REPLACE ENTIRELY.**
4. HUNL value nets require lossy card abstraction: paper used
   1,000 buckets per player per street via clustering on hand-strength
   distribution features (PE-style; exact features/algorithm/counts in
   supplement — **UNVERIFIED in session**).
5. Per-street bucket maps hand×board→bucket; cluster model artifacts
   (must be versioned + hashed like weights).
6. **None in session; none ever released** (the author cluster centroids do
   not exist publicly). Supplement describes method only.
7. NOT certifiable against author: at best **deterministic-reproducible**
   (seeded clustering, hashed artifacts, our own manifests) + BEHAVIORAL
   (abstraction quality metrics). This is a *permanent* rider item for any
   HUNL build.
8. Risk: **the single largest fidelity gap** — bucketing shapes everything
   the NN learns; author-matching is impossible in principle.

## 16. NN input representation

1. Datagen inputs 73 = [P1 36 buckets | P2 36 buckets | pot/1200]
   (`datagen/generator.py::generate_data_file`, certified).
2. Layout general, dims Leduc.
3. **ADAPT** (dims; per-street nets), pending supplement for exact HUNL
   layout (2×1000+1 = 2001 believed, **UNVERIFIED**).
4. Same construction: bucketized ranges + normalized pot.
5. Input vectors per street net; bucket scatter from §15.
6. Supplement (NOT in session).
7. Structure certifiable vs our own spec (BIT_EXACT construction); fidelity
   to author's layout blocked on supplement.
8. Risk: silent layout mismatch vs paper → wrong reconstruction claims.

## 17. NN output / CFVs

1. Targets 72 = 2×36 bucket CFVs, pot-normalized; zero-sum handling in
   `next_round_value.py` / `resolving.get_root_cfv_both_players` (L2-certified).
2. General mechanism.
3. **ADAPT** (dims 2×1000 believed, UNVERIFIED).
4. Identical math: bucket CFVs, /pot normalization, zero-sum correction.
5. Output vectors + inverse bucket scatter.
6. Supplement (NOT in session).
7. Same as §16.
8. Risk: as §16.

## 18. Value network architecture

1. `deepstack_leduc/value_model.py` (73→50×5 PReLU→72; loads original
   `final_cpu.model` byte-verified), `torch7_model.py` (Torch7 deserializer).
2. General code; dims/depth Leduc.
3. **ADAPT** code, **REPLACE** capacity (believed 7×500 PReLU, 2001→2000,
   **UNVERIFIED**); train from scratch — no author HUNL weights exist.
4. Architecture is a hyperparameter; loader/verification infra reusable.
5. Per-street nets + preflop auxiliary net; GPU training.
6. Supplement (architecture; NOT in session). No weights oracle, ever.
7. Architecture NUMERIC (spec match once supplement available); training
   run itself at best seeded-reproducible (GPU nondeterminism ⇒ NUMERIC,
   not BIT_EXACT, unless CPU-deterministic training is accepted at huge
   cost).
8. Risk: compute scale; determinism-vs-throughput tradeoff must be decided
   explicitly.

## 19. DataGeneration

1. `datagen/` package (certified Phase 2A/2B): board sampler, stick-breaking
   `RangeGenerator`, pot sampling f32 chain, resolve targets, shard
   orchestration (`certification/phase2b/run_phase2b.py`).
2. Algorithm general (the stick-breaking recursive range split IS the
   documented DeepStack method per supplement — believed, UNVERIFIED); dims
   and pot ranges Leduc.
3. **ADAPT.**
4. Same pipeline per street: sample board+ranges+pot → resolve → bucket
   CFV targets. HUNL adds: per-street pot-range tables, random betting
   history irrelevant (paper samples pot directly — as Leduc does), river
   solves feed turn net, turn net feeds flop datagen (bootstrapped
   cascade), counts believed 10M turn / 1M flop (UNVERIFIED).
5. Per-street generators + the Phase-2B shard/manifest/audit pattern
   unchanged.
6. `range_generator.lua` (in session, author code, certified port) — this
   part IS author-anchored; counts/pot ranges need supplement.
7. RNG/serialization/shard determinism BIT_EXACT (proven pattern);
   target fidelity NUMERIC vs our own certified solver (no author data).
8. Risk: compute (HUNL resolve ≫ Leduc resolve; 10M × minutes-scale =
   cluster budget, not a container job).

## 20. Sampling / RNG

1. `datagen/th_random.py` (THRandom MT19937, certified vs untouched C),
   Phase-2B seed derivation.
2. Fully game-independent.
3. **REUSE AS-IS.**
4. Certified byte-exact twice (C oracle + Tammelin cross-anchor).
5. None new.
6. torch7 THRandom.c (in session).
7. Already BIT_EXACT.
8. Risk: none.

## 21. Serialization

1. `deepstack_leduc/torch7_tensor.py` + `datagen/t7_writer.py`
   (round-trip 6/6 byte-certified), shard manifest scheme.
2. Game-independent.
3. **REUSE AS-IS** (dims free).
4. Certified; HUNL only changes tensor sizes.
5. Larger tensors; consider sharding sizes (manifest pattern scales).
6. Torch7 format (in session).
7. Already BIT_EXACT.
8. Risk: none (file sizes only).

## 22. Training pipeline

1. `deepstack_leduc/data_stream.py`, `masked_huber.py` (port of
   `Nn/masked_huber_loss.lua`), Lua `Training/train.lua` (optim.adam,
   lr=0.001) — Python training loop itself not yet built/certified (we
   never trained; Leduc training is Phase 3 pending).
2. General.
3. **ADAPT** (dims; PyTorch loop to be written for Leduc Phase 3 anyway —
   same loop then scales to HUNL).
4. Loss/masking semantics certified at module level; optimizer parity
   (Torch7 optim.adam vs PyTorch Adam — epsilon/bias-correction details)
   must be audited when training starts (applies to Leduc Phase 3 first).
5. Street-specific datasets, GPU batching, masked huber over 2000 outputs.
6. `train.lua` (in session) for semantics; no author training logs.
7. Loss NUMERIC/BIT_EXACT at module level (CPU); full training run
   seeded-NUMERIC.
8. Risk: silent optimizer-semantics drift — audit before Leduc training,
   inherit for HUNL.

## 23. Evaluation / exploitability / AIVAT hooks

1. `deepstack_leduc/evaluate.py` + `differential.py` (trace comparators);
   Lua `Tree/tree_values.lua`, `tree_strategy_filling.lua` (full-tree
   exploitability — Leduc-scale only); `davis20asupp.pdf` +
   `1809.03057v1.pdf` (variance-reduced evaluation math, in session).
2. Full-tree exploitability is smallgame-only by nature.
3. **REUSE** (Leduc-side regression tooling) + **REPLACE** (HUNL evaluation
   = LBR-style local best response and/or AIVAT match evaluation — new
   code).
4. HUNL best response is intractable exactly; the field's standards are
   LBR and AIVAT (AIVAT paper itself NOT in session; davis20a baselines
   are in-session cousins).
5. LBR agent vs ACPC dealer harness; AIVAT value-function plumbing.
6. ACPC dealer (in session) for match infrastructure; davis20asupp
   pseudocode (in session) for baseline-corrected estimators.
7. BEHAVIORAL/statistical only (confidence intervals) — by nature.
8. Risk: none to engine correctness; only to strength claims.

---

## Special findings

**S1 — Unused HUNL assets already in our sources (verified):**
`evalHandTables` 7-card evaluator (×2 copies), ACPC `game.c/h` betting
legality + game parser, `dealer.c` match infra, HUNL game definitions
(no-limit AND limit, 2p/3p), Tammelin CFR+ as game-general large-scale CFR+
oracle (reads Hold'em game files), `rng.c` (dealer RNG), and
`protocol_to_node.lua`/`acpc.py` ACPC protocol layer (Leduc-trimmed but
protocol-general in structure). Nothing else HUNL-specific exists in the
repos (no hidden holdem Lua).

**S2 — Supplement/thesis availability:** neither is in session; egress
blocks arxiv.org and poker.cs.ualberta.ca (attempted; 403 via proxy). Public
URLs located: arXiv 1701.01724 (paper+supplement), ERA/poker.cs thesis PDF.
**They are believed to contain exactly the missing numbers** (bet-sizing
table, 1000-bucket abstraction description, 7×500 PReLU dims, 10M/1M sample
counts, pot sampling ranges, per-street CFR iteration/skip counts) — but per
this project's rules those stay UNVERIFIED until the PDFs are uploaded into
the session. **Owner action: upload the two PDFs** (and ideally the Science
SOM aai1110 supplement) — then §12/15/16/17/18/19 unknowns collapse to
verified constants.

**S3 — 1:1 transferable without touching math (certified-to-certified):**
CFR+ update core, gadget, resolving protocol, range ops API, torch7 BLAS
wrapper (sgemm is dim-free), THRandom, t7 reader/writer, masked-huber
module, zero-sum correction scheme, stick-breaking range generator
algorithm, the whole Phase-2B shard/manifest/audit/replay methodology, and
the certification culture artifacts (freeze-first, oracle manifests).

**S4 — Genuinely new poker-specific layer:** 1326-hand indexing + blocking,
7-card evaluator binding, river showdown matrices, chance-weight algebra,
multi-street transitions, HUNL bet-sizing tables + blind/position
asymmetry, clustering abstraction, per-street + auxiliary nets, all-in
runout equity, LBR/AIVAT evaluation, distributed datagen orchestration.

---

## Conclusions

**A. Reuse of the certified engine:** ≈ **55–60 %** of engine+datagen LOC
carries over with math unchanged — of that, ≈ **30 % byte-untouched**
(gadget, CFR core, RNG, serialization, BLAS wrapper, loss, range API,
orchestration) and the rest mechanical dim-parameterization under Leduc
byte-regression. Certification infrastructure reuse ≈ **85 %**.

**B. New HUNL code:** ≈ **40–45 %** of the future engine by LOC — but
concentrated in the highest-risk strata: abstraction (§15), chance/terminal
algebra (§8/§14), betting legality (§12), evaluation (§23), plus NN scale.

**C. Minimal implementation order** (each step gated by its certification):
1. Card layer: encoding, 1326 indexing, blocking (§6/§10) — exhaustive BIT_EXACT.
2. Evaluator binding vs `evalHandTables` (§9) — BIT_EXACT.
3. River terminal equity matrices (§14) — BIT_EXACT recount.
4. Tree builder + betting legality vs ACPC `game.c` (§5/§12/§13) — BIT_EXACT
   legality (fraction table pending supplement).
5. Dim-parameterized CFR core + gadget with Leduc byte-regression (§1/§2).
6. **Gate G1: exact river re-solve** (no NN, no abstraction) — full
   self-consistent solve, verifiable against Tammelin CFR+ on a reduced
   river game BIT_EXACT.
7. Chance weights + turn→river transition, exact (no NN) turn solves at
   reduced scale (§8/§11) — NUMERIC + identities.
8. Bucketing (§15) — deterministic-reproducible, hashed artifacts.
9. Turn datagen from river solves (Phase-2B pattern) (§19).
10. Turn net training (§18/§22, after Leduc Phase-3 training certifies the
    loop) → turn boxes (§4).
11. Flop datagen (uses turn net) + flop net; preflop auxiliary net.
12. Continual resolving full stack (§3) + ACPC agent (§23 infra).
13. LBR/AIVAT evaluation harness (§23).

**D. BIT_EXACT-certifiable:** card layer, evaluator, blocking, river/showdown
matrices, betting legality (vs ACPC C), CFR core + gadget (Leduc regression +
Tammelin cross-anchors incl. limit-holdem instances), RNG, serialization,
datagen determinism/shard replay, NN input/target construction (vs our own
frozen spec), G1 exact river solves.

**E. TRACE/NUMERIC/BEHAVIORAL only:** bucketing (deterministic-reproducible
+ BEHAVIORAL; author-matching impossible in principle), value-net training
(NUMERIC seeded), continual resolving end-to-end (NUMERIC invariants +
BEHAVIORAL match play; no author traces exist for HUNL), transitions'
value-box math beyond identities (NUMERIC), evaluation/strength claims
(statistical/BEHAVIORAL), fidelity of bet-sizing/bucket/net/datagen
*parameters* to the paper (blocked on S2 upload; until then BEHAVIORAL at
best).

**F. Enough podkladů for a full HUNL DataGenerator?** **NOT YET.** We have:
the algorithm (author range generator + certified pipeline), the RNG, the
orchestration, the exact game definition, and (after C.1–C.7) we would have
the solver. We do NOT have in-session: re-solve bet-sizing table, bucket
counts/method, per-street CFR iteration counts, pot-sampling ranges, sample
counts, NN dims — i.e., the *parameters*. One owner action (upload S2 PDFs)
plus the compute-budget decision closes the spec gap.

**G. Roadmap** (Leduc GB → HUNL GB → HUNL DataGen → HUNL training):
- **Stage 0 (now):** owner uploads DeepStack supplement + Burch thesis →
  re-audit §12/15/16/17/18/19 against them; freeze "HUNL Paper Parameter
  Sheet" with quotes + hashes.
- **Stage 1 — HUNL Card&Rules Baseline:** C.1–C.4 (everything BIT_EXACT vs
  in-session C oracles). Deliverable: certified card/rules layer + matrix
  corpus with manifests.
- **Stage 2 — HUNL Solver Baseline:** C.5–C.7; Gate G1 river-exact; freeze
  **HUNL Golden Baseline v0** (solver without abstraction/NN, river+turn
  exact at reduced scale, Leduc regression green throughout).
- **Stage 3 — Abstraction + Value Nets:** C.8–C.11; every artifact hashed;
  training loop first certified on Leduc Phase-3 (already owner-gated).
- **Stage 4 — HUNL DataGenerator:** Phase-2B pattern at HUNL dims; pilot
  (10³-scale) fully audited before any bulk; bulk requires an explicit
  compute plan (cluster/GPU — this container is 4 CPU cores; 10M-scale turn
  solving is out of its reach by orders of magnitude).
- **Stage 5 — HUNL training + continual resolving + ACPC/LBR evaluation**,
  each gated like Leduc phases were.

**Nothing was modified by this audit.** Frozen artifacts remain frozen.
