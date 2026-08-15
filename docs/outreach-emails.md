# Hotové e-maily k odeslání

Dva kompletní dopisy, k překopírování. Doplňte pole `[…]`.

**Design proti doptávání:**
- každá otázka nese kontext, aby se adresát nemusel ptát, co myslíme,
- sekce „what we already established" brání tomu, aby vysvětlovali, co víme,
- každá otázka má **záložní variantu** („if you don't recall X, does Y ring a bell"),
  takže i mlhavá vzpomínka je použitelná,
- otázky jsou rozdělené na **dvě, na kterých záleží** a **zbytek**, aby krátká odpověď
  pořád měla cenu.

**Před odesláním doplňte:** jméno, jednou větou co stavíte, a — pokud váš projekt míří
do kvantitativního obchodování — větu o tom hned v úvodu (Schmid a Moravčík vedou
EquiLibre Technologies; zamlčené a později zjištěné to zavře dveře natrvalo).

---

## E-mail 1 — Neil Burch

**To:** `nburch@ualberta.ca`
**Subject:** Two implementation details from the DeepStack turn/flop data generation

---

Dear Dr. Burch,

I'm [jméno], and I'm reimplementing the DeepStack counterfactual-value data generation
from the published description, [jednou větou: k čemu — např. "as the training pipeline for
a research project on depth-limited solving"]. [Pokud je relevantní: "I should say up front
that this work sits in [oblast], which overlaps with what some of your former colleagues now
do commercially — I mention it so it doesn't come as a surprise later."]

I'm not asking for code, data, or anything under obligation. Two implementation decisions
are simply not recoverable from the paper or the supplement, and I think you may be the
only person who remembers them — your thesis preface says you provided the initial
experimental framework and generated one of the data sets used to train the evaluation
function.

**What I've already worked out, so you don't have to explain it:** I have the released
CFR+ solver, the ACPC server, and DeepStack-Leduc; I've verified that the public CFR+
release has no counterfactual-value export (`dumpValues()` writes regrets and average
strategy only), that its per-subgame RNG is glibc `random_r` seeded `rngSeed ^ subgameIndex`
rather than your MT19937, and that the `[100,100)` interval appears unchanged in all three
arXiv versions. So I'm not asking what the supplement says — I'm asking what the code did.

**The two that matter most:**

1. **The first pot-size bin.** The supplement lists
   `{[100,100), [200,400), [400,2000), [2000,6000), [6000,19950]}`.
   The first interval is empty as written. Was it a point mass at pot = 100 — the big blind,
   and the smallest possible pot — or a typo for `[100,200)`, or something else entirely?
   *If you don't recall the bracket: do you recall whether pot = 100 situations were
   generated at all?*

2. **Tie-breaking in the range generator.** R(S,p) splits a hand set so that
   `|S₁| = ⌊|S|/2⌋` with hands in `S₁` no stronger than those in `S₂`. On a turn board
   there are only ~40–130 distinct hand-strength values among 1128 hands, so almost every
   split lands inside a group of ties. Was there an explicit tie-break rule, or did the
   assignment fall out of whatever sort the code used?
   *If you don't recall a rule: do you recall whether the hand list was sorted once per
   board and reused, or re-sorted per sample?*

**If you have more time — anything you remember helps, and "I don't recall" is a useful
answer:**

3. Which of the three data sets did you generate — the turn network's ten million
   situations, the flop network's one million, or the auxiliary network's ten million?
4. Was hand strength computed as the supplement describes (probability of beating a
   uniformly random hand), or from a rank-based evaluator like the `rankCardset()` in the
   released CFR+ code?
5. Was the generation seeded at all? If so, which RNG did the seed drive — your MT19937
   from `rng.c`, glibc `random_r`, or something else? *(DeepStack-Leduc doesn't seed at
   all, which is partly why I ask.)*
6. Was the generator a program of its own, or built on the CFR+ codebase? I ask because
   the public CFR+ can't emit counterfactual values, so it can't have been driven directly.
7. What did the "initial experimental framework" consist of — the range generator, the
   solver harness, the job submission, or something else?
8. The supplement says the turn situations were solved with 1,000 iterations of CFR⁺ and
   mentions no discarded iterations, but DeepStack-Leduc uses `cfr_skip_iters = 500` in
   offline generation. Did the HUNL offline generation discard early iterations?
9. How was the work split across the 6,144 MP2 cores — a PBS job array, N independent
   `qsub` submissions, MPI? And how did each worker get its randomness?
10. Does any snapshot of `project_uoapoker/trunk/src/c/` survive — a personal checkout, a
    tarball, a backup? I reconstructed the repository name from paths that appear in the
    released LBR logs, but I have no copy.

A one-line answer to any of these is more than enough; I don't need prose. If it's useful,
I'm happy to send the reconstruction write-up so you can see exactly what I've pieced
together and correct anything I've got wrong.

Thank you for your time.

[jméno]
[kontakt]

---

## E-mail 2 — Martin Schmid

**To:** `schmid@equilibretechnologies.com`
**Subject:** DeepStack-Leduc vs. the HUNL data generation — a few differences

---

Dear Dr. Schmid,

I'm [jméno], and I'm reimplementing the DeepStack counterfactual-value data generation from
the published description, [jednou větou: k čemu]. [Pokud relevantní: věta o překryvu
s EquiLibre.]

I'm not asking for code or data. I've been working from `DeepStack-Leduc`, which is the
only public implementation of the pipeline, and there are several places where it clearly
differs from what the HUNL supplement describes. You're the person who would know whether
those differences are Leduc simplifications or whether the HUNL original did the same thing.

**What I've already established from your repository, so you don't have to restate it:**
`range_generator.lua` samples `p₁` as `mass * torch.rand()` and recurses to size 1;
`data_generation.lua` draws pot sizes from one continuous uniform on `[ante, stack − 0.1)`;
one board is sampled per batch and shared by all ten situations; values come from
`get_root_cfv_both_players()` normalised by pot size; nothing in the data-generation path
seeds the RNG; and `arguments.lua` sets `cfr_iters = 1000` with `cfr_skip_iters = 500`.

**The two that matter most:**

1. **The odd-split randomisation.** Leduc's `_generate_recursion` randomises which side the
   middle element falls on when the set has odd size (`halfSize + torch.random(0,1)`).
   The supplement describes a deterministic `⌊|S|/2⌋`. Was the randomisation in the HUNL
   generator too, or is it something you added for the Leduc release?
   *If you don't recall: was the Leduc range generator a port of the HUNL one, or written
   fresh for the public release?*

2. **Ties in the strength sort.** Leduc sorts hands with `torch.sort()` and leaves ties to
   the sort. In HUNL, a turn board has only ~40–130 distinct strength values among 1128
   hands, so the `⌊|S|/2⌋` split almost always cuts through a tie group. Did the HUNL
   generator have an explicit tie-break, or did it also just take whatever the sort gave?
   *If you don't recall: was the hand list sorted once per board and reused across samples?*

**If you have more time — "I don't recall" is a useful answer:**

3. Leduc uses a single continuous uniform for pot size; HUNL uses five intervals. Why the
   difference — and what was the first HUNL interval `[100,100)` meant to express? It's
   empty as written, and `min_pot = ante = 100` in Leduc makes me suspect it was meant as a
   point mass at the minimum pot.
4. Leduc's data generation doesn't seed the RNG at all. Was the HUNL generation seeded, and
   was it intended to be reproducible?
5. Leduc applies `cfr_skip_iters = 500` in offline data generation, because offline and
   online share one solver there. The supplement describes the HUNL offline solve as plain
   1,000-iteration CFR⁺ with no mention of discarding. Which was it in HUNL?
6. What language and framework was the HUNL generator — Lua/Torch7 like Leduc, or C++?
7. In Leduc one board is shared by a whole batch. Did HUNL share boards within a batch, or
   was every situation drawn independently?
8. Were the 1,000 buckets produced by Kevin Waugh's `hand-isomorphism` library, by the
   isomorphism code in the CPRG solver tree, or by something else?
9. Do any of the ten million turn samples still exist anywhere — even a fragment, even a
   few thousand rows? A handful would let me validate a reimplementation against ground
   truth rather than against a description.
10. Was the HUNL generator part of the internal `project_uoapoker` repository, and does any
    snapshot of it survive?

One line per answer is plenty. If it helps, I can send the reconstruction write-up — it
documents what I've verified from public sources and where the gaps are, and you'd be very
welcome to correct it.

Thank you for your time.

[jméno]
[kontakt]

---

## Poznámky k odeslání

- **Neposílat oba naráz.** Burch první; Schmida až po týdnu, nebo rovnou, ale ne jako
  kopii téhož textu — jsou to různé dopisy a je to vidět.
- **Bowlinga do kopie nedávat.** Až kdyby oba mlčeli tři týdny, pak samostatný mail
  s institucionálními otázkami (viz `outreach-questions.md`, §3).
- **Přílohu neposílat hned.** Nabídnout ji, jak je v textu; kdo bude chtít, řekne si.
  Poslat 70 KB ledgeru nevyžádaně snižuje šanci na odpověď.
- **Když odpoví jen na jednu věc,** ať je to tie-breaking. Je to jediná mezera, kterou
  nelze uzavřít další analýzou veřejných zdrojů, a týká se 99,5–100 % generovaných rukou.
