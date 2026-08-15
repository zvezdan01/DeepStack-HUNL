# Outreach kit — konkrétní otázky pro autory DeepStacku

**Účel.** Uzavřít mezery, které z veřejných zdrojů uzavřít nelze. Otázky jsou psané tak,
aby se nemuselo doptávat — každá je zodpověditelná jednou až třemi větami z paměti,
bez dohledávání kódu.

**Podklad:** `docs/burch-forensics.md` (ledger), `docs/burch-handoff.md` (shrnutí),
`docs/deepstack-leduc-reference.md` (rozbor referenční implementace).

---

## Jak to poslat

1. **Neposílat hromadně.** Každému jeho vlastní mail, s otázkami jen z jeho okruhu.
   Hromadný mail deseti lidem, z nichž sedm s generováním dat nemělo nic společného,
   skončí bez odpovědi.
2. **Pořadí:** Burch → Schmid. Bowling jen pokud oba mlčí (je PI, ne implementátor).
   Ostatní až podle toho, co vyjde.
3. **Rámování.** Otevřít tím, co jsme *zrekonstruovali*, ne tím, co jsme *našli za chyby*.
   Nález o nesrovnalosti v publikovaném konfidenčním intervalu (#39) a o tom, že archiv
   obsahuje víc dat než paper (#38), do prvního mailu **nepatří** — vypadalo by to jako audit.
4. **Být konkrétní v tom, co nechceme.** Nežádáme kód, data ani nic pod NDA. Žádáme
   vzpomínku na dvě až tři implementační rozhodnutí.
5. **Konflikt zájmů.** Schmid a Moravčík vedou EquiLibre Technologies (kvantitativní
   obchodování). Pokud váš projekt míří do příbuzné oblasti, řekněte to v mailu rovnou —
   zamlčené a později zjištěné to zavře dveře natrvalo.
6. **Délka.** Mail do 200 slov, otázky jako číslovaný seznam, odkaz na ledger jako přílohu
   nebo link. Nikdo nebude číst esej.

---

## 1. Neil Burch — **hlavní adresát**

`nburch@ualberta.ca` · Amii / Sony AI · dříve DeepMind (`burchn@google.com`, pravděpodobně stálý)

**Proč on:** jeho vlastní disertace (preface) říká: *„I provided an initial experimental
framework, and generated one data set used to train the evaluation function."* Naše dvě
hlavní otázky jsou přesně o jeho části. Kapitola 6 té disertace to už nerozvádí.

### Otázky

1. **Which of the three data sets did you generate** — the turn network's ten million
   situations, the flop network's one million, or the auxiliary network's ten million?
2. The supplement's pot distribution lists the intervals
   `[100,100)`, `[200,400)`, `[400,2000)`, `[2000,6000)`, `[6000,19950]`.
   The first is empty as written. **What did that first bin actually do in the code** —
   was it a point mass at pot = 100 (the big blind), a typo for `[100,200)`, or something
   else? It survived unchanged through all three arXiv versions and peer review.
3. The range generator R(S,p) splits a hand set so that `|S₁| = ⌊|S|/2⌋` with hands in `S₁`
   no stronger than those in `S₂`. **How were hands of equal strength assigned** when the
   split fell inside a group of ties? Was there an explicit tie-break rule, or did it fall
   out of whatever sort was used?
4. Was **hand strength** computed as the supplement describes — probability of beating a
   uniformly random hand — or from a rank-based evaluator like `rankCardset()` in the
   released CFR+ code?
5. **Was the generation seeded?** Was there an `rngseed`-style parameter, and if so which
   RNG did it drive — the CPRG MT19937 from your `rng.c`, glibc `random_r` as in
   `CFR_plus/storage.c`, or something else?
6. Was the generator **a program of its own, or built on the CFR+ codebase?** We verified
   the public CFR+ release has no counterfactual-value export — `dumpValues()` writes
   regrets and average strategy only — so it could not have been driven directly.
7. What did the **"initial experimental framework"** consist of? Was it the range
   generator, the solver harness, the job submission, or something else?
8. The supplement says the turn situations were solved with **1,000 iterations of CFR⁺**
   and mentions no discarded iterations, but the Leduc reference implementation uses
   `cfr_skip_iters = 500` in offline generation. **Did the HUNL offline generation discard
   early iterations?**
9. **How was the work split across the 6,144 MP2 cores** — a PBS job array, N independent
   `qsub` submissions, MPI? How many situations per worker, and how did each worker get
   its randomness?
10. Does any snapshot of **`project_uoapoker/trunk/src/c/`** survive — a personal checkout,
    a tarball, a backup? We have the repository name from paths leaked in the released
    LBR logs, but no copy.

---

## 2. Martin Schmid — **druhý adresát**

`schmid@equilibretechnologies.com` · EquiLibre Technologies · dříve DeepMind
(osobní `lifrordi@gmail.com` — použít jen pokud firemní mlčí)

**Proč on:** spolu-první autor, a autor `DeepStack-Leduc` — jediné veřejné implementace
pipeline. Ví, jak se Leduc verze liší od HUNL.

### Otázky

1. **Is DeepStack-Leduc's `range_generator.lua` a faithful port of the HUNL one**, or was
   it rewritten/simplified for the public release?
2. The Leduc version randomises which side the middle element falls on for odd-sized
   splits (`halfSize + torch.random(0,1)`). **Was that in the HUNL generator too?**
   The supplement's `⌊|S|/2⌋` describes something deterministic.
3. Leduc samples pot sizes from a **single continuous uniform** on `[ante, stack − 0.1)`,
   while HUNL uses five intervals. **Why the difference**, and what was the first HUNL
   interval `[100,100)` meant to express?
4. Leduc's data generation **does not seed** — no seed parameter exists and the global
   Torch RNG is left uninitialised. **Was HUNL generation seeded?**
5. Leduc uses `cfr_iters = 1000` with `cfr_skip_iters = 500`, and applies both in offline
   data generation. **Did the HUNL offline generation also discard early iterations,** or
   was it the plain 1,000-iteration CFR⁺ the supplement describes?
6. In Leduc, hands are sorted by strength with `torch.sort()` and ties are left to the sort.
   **Was the HUNL sort stable, or was there an explicit tie-break?**
7. **What language and framework was the HUNL generator** — Lua/Torch7 like Leduc, or C++?
8. In Leduc, one board is sampled per batch and all ten situations in the batch share it.
   **Did HUNL share boards within a batch,** or was every situation independent?
9. **Do the ten million turn samples still exist anywhere** — even a fragment, even a few
   thousand rows? A handful would let us validate a reimplementation.
10. Were the **1,000 buckets** produced by Kevin Waugh's `hand-isomorphism` library,
    by the isomorphism code in Burch's `card_tools.c`, or by something else?

---

## 3. Michael Bowling — **jen když první dva mlčí**

`bowling@cs.ualberta.ca` · UAlberta, vedoucí CPRG, korespondenční autor DeepStacku

**Proč on:** institucionální otázky, ne implementační. Je to PI — na detaily generátoru
se ptát nemá smysl, na osud repozitáře ano.

### Otázky

1. **Does the CPRG Subversion repository `project_uoapoker` still exist** — on a server,
   in a backup, in an archive? We reconstructed its name and layout from paths in the
   released LBR logs (`/home/<user>/cprg/project_uoapoker/trunk/src/c/`).
2. If it survives, **is any part of it shareable** — specifically the DeepStack-era data
   generation code, or a manifest of what it contained?
3. **Were the DeepStack training sets archived** anywhere after the paper, or were they
   discarded once the networks were trained?
4. Is there an institutional contact — department IT, library, Amii — who would know what
   happened to CPRG's internal infrastructure after the group wound down?

---

## 4. Kevin Waugh — úzká, ale rozhodnutelná otázka

`kevin.waugh@gmail.com` · `kdub0` · dříve CMU/UAlberta, ACPC competition chair

**Proč on:** autor `hand-isomorphism`. Ověřili jsme, že Burchův CFR+ jeho knihovnu
**nepoužívá** — CPRG mělo dvě nezávislé implementace izomorfismu. Otázka je, která
z nich stála pod DeepStack abstrakcí.

### Otázky

1. **Was `hand-isomorphism` used in DeepStack's bucketing pipeline** (the 1,000 clusters
   over hand-strength features), or was that built on the isomorphism code inside the
   CPRG solver tree?
2. We found two independent isomorphism implementations in CPRG code — yours
   (index-and-invert, precomputed tables) and Burch's in `card_tools.c`
   (enumerate-and-weight, no tables). **Was that deliberate, and which was considered
   canonical** for new work around 2015–2016?
3. Your repository's history shows deleted topic branches and files including
   `index_flop-main.c` and `unindex_flop-main.c`, both empty stubs.
   **Was there ever a working flop-specific indexing tool?**

---

## 5. Michael Johanson — abstrakce a buckety

`mikebjohanson` na GitHubu · web `johanson.ca` · Amii / dříve DeepMind
*(e-mail nedohledán — kontakt přes web nebo LinkedIn)*

**Proč on:** supplement cituje `Johanson13:Abstraction` jako zdroj bucketovací metody.

### Otázky

1. The supplement says the 1,000 buckets came from **k-means clustering with earth
   mover's distance over hand-strength features**, citing your 2013 abstraction work.
   **Does the implementation that produced DeepStack's buckets survive** anywhere?
2. **Were the flop and turn networks' bucketings computed once and reused,** or regenerated
   per training run? If reused, do the cluster definitions still exist?
3. Was the bucketing deterministic — **was k-means seeded**, and would rerunning it
   reproduce the same 1,000 clusters?

---

## 6. Dustin Morrill — nízká priorita, ale nejaktivnější

`dmorrill10@gmail.com` · Sony AI · GitHub `dmorrill10` (aktivní 2026)

**Proč on:** na svém webu píše, že vytvořil match interface DeepStacku. K generování dat
se nevyjadřuje, ale je z týmu prokazatelně nejdostupnější a může nasměrovat.

### Otázky

1. You write that you created DeepStack's match interface. **Was the study deployment the
   `acpc_poker_gui_client` repository**, and if so which branch or commit? The August 2016
   commits — timeout-fold/check, pauses between hands, hiding other matches — line up with
   how the study is documented to have behaved.
2. **Do you know what became of the CPRG Subversion server** after the group wound down?
3. Were you involved in the **turn/flop data generation** in any capacity, or was that
   entirely Burch, Moravčík and Schmid?

---

## 7. Matej Moravčík / Trevor Davis — kontakt nedohledán

Ani jeden nemá veřejnou GitHub přítomnost (ověřeno sedmi, resp. dvěma strategiemi).

- **Moravčík** — CSO EquiLibre Technologies. Cesta: přes Schmida, nebo přes firemní kontakt
  `equilibre.ai`. Otázky by byly stejné jako Schmidovy, plus: *kdo vlastnil kterou
  komponentu pipeline?*
- **Davis** — spolupracoval s Burchem na teoretických mezích, s generováním dat
  pravděpodobně nesouvisel. **Nízká priorita**, kontakt neznámý.

---

## Co dělat s odpověďmi

Každá odpověď na otázky **Burch 2, Burch 3, Schmid 2, Schmid 6** přímo mění, co má váš
generátor dělat. Ostatní jsou kontext.

Pokud přijde odpověď jen na jednu věc, ať je to **tie-breaking v R(S,p)** — je to jediná
mezera, kterou nelze uzavřít žádnou další analýzou veřejných zdrojů, a týká se
99,5–100 % generovaných rukou.
