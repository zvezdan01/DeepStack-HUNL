# HUNL DataGenerator — owner's forensic provenance notes (2026-08-14)

Verbatim owner-supplied research record (Czech), preserved as primary
provenance input for the datagen certification. An English implication
map for THIS repo's pilot parameterization follows at the end.

---

## Zápis vlastníka (doslovně)

### 1. Co je potvrzené přímo z původních zdrojů
Neil Burch ve své disertaci výslovně uvádí, že pro DeepStack vygeneroval
jeden dataset použitý k trénování evaluation function a podílel se na
počátečním experimentálním frameworku. To z něj dělá přímého provenance
aktéra DataGenerator pipeline. Původní DeepStack HUNL training source
code nebyl veřejně vydán; tým zveřejnil zjednodušený DeepStack-Leduc
demo (Schmid: nejde o stejný kód). Reálné cíle hledání: A. HUNL
range_generator, B. DataGenerator/job script, C. raw training samples,
D. RNG seed/config, E. cluster manifest/log.

### 2.-3. Training situation + počty
Situace = public cards, pot size, range P1, range P2 (bez betting
history); target = CFV obou hráčů / pot. Turn síť: 10 000 000 situací
(6 144 CPU cores, Calcul Québec MP2, >175 core-years). Flop: 1 000 000
(~20 GPU, ~0.5 GPU-year). Auxiliary/preflop: 10 000 000, target
enumerací 22 100 flopů přes flop síť.

### 4. Offline target solver
"1 000 iterations of CFR+" s akcemi F/C/P/A. Schmidova definice CFR+
(disertace): Regret Matching+, ALTERNATING player updates, LINEARLY
weighted average strategy. => offline DataGenerator je nejspíš
standardní CFR+, ne online DeepStack hybrid. Není to bit-exact důkaz,
ale nejlepší first-party interpretace.

### 5. omit_iters NENÍ doložen pro offline
Online continual-resolving používal iterations/omit; offline sekce říká
jen "1000 iterations of CFR+". omit=500 pro offline generator je pouze
HYPOTÉZA, dokud se nenajde source/job config/raw sample.

### 6. Rozpory v online konfiguraci
Science supplement vs Schmidova disertace uvádějí pro preflop jiná
iterations/omit čísla; disertace má i vnitřní rozpor prose vs tabulka.
=> online parametry nejsou spolehlivý základ pro offline rekonstrukci;
DataGenerator rekonstruovat odděleně od continual re-solving konfigurace.

### 7.-8. Range generator R(S,p)
Algoritmus popsán (rekurzivní stick-breaking dle hand strength = P(beat
uniform random hand)). Bit-exact neznámé: pořadí 1326 kombinací,
blocker semantics, maskování, tie-breaking, přesná strength definice,
float precision, RNG, seed, pořadí RNG volání.

### 9.-11. Pot-size generator
Intervaly {[100,100), [200,400), [400,2000), [2000,6000), [6000,19950]};
[100,100) je prázdný interval a JE ve všech verzích (arXiv v1-v3 i
Science) — nikdy neopraveno. Hypotézy: (a) [100,200) — doplní mezeru,
(b) singleton pot=100 špatně zapsaný intervalovou notací. Nesmí se
automaticky měnit na [100,200). Distribuce měla aproximovat pot sizes
starších HUNL programů (Nyx, Hyperborean, CPRG boti) => historické ACPC
logy jsou relevantní.

### 12.-14. ACPC logy, Nyx genealogie, FCPA
2014 archiv 2pn_logs.tar.bz2; moderní archivace "A Dataset of Poker
Hand Histories" obsahuje ACPC 2014: 48 048 000 HUNL hand records (~24M
unikátních). Moravčík+Schmid dělali Nyx (ACPC 2013/14) => genealogie
Nyx/CPRG -> endgame solving -> DeepStack HUNL -> Leduc demo; hledat i
"nyx, endgame, subgame, fullcards, fcpa, nlhe, hunl". FCPA existovalo
už ve starší CPRG HUNL linii.

### 15. DeepStack-Leduc jako architektonický fosil
Naming: DataGeneration, data_generation.lua, range_generator,
random_card_generator, get_root_cfv_both_players, .inputs/.targets/
.mask, cfr_iters, cfr_skip_iters. Pipeline: board -> ranges -> pot ->
Resolving -> root CFVs -> /pot -> serialize. Leduc pot sampler je ale
jednodušší (ne HUNL distribuce).

### 16.-18. RNG genealogie
CPRG RNG (Burch od 2005): MT19937, init_genrand()/genrand_int32(),
explicitní rngseed; per-subgame seed ~ rngSeed ^ subgameIndex. ACPC
dealing: deterministický deck v suit/rank pořadí, výběr
genrand_int32 % numCards, swap s poslední kartou, hole cards před
boardem. ACPC match seed explicitní v argumentu i log headeru =>
kultura reprodukovatelných game+hands+seed experimentů. Nepotvrzeno, že
DeepStack DataGenerator tyto přímo používal — fingerprint pro D/E.

### 19. Cluster
MP2/Mammouth-MP2, Torque/PBS (qsub, #PBS), AMD Opteron ~24 cores/node
=> 6144/24 = 256 nodes (inference z HW, ne nalezený manifest).

### 20.-21. Následnické projekty
TensorCFR (beyond-deepstack): seed loops, generate_data.py, TFRecord,
cluster konvence — dobrý pro naming/job conventions, není originál.
PyStack (problémy s reprodukcí accuracy) a DeeperStack (záměrné
odchylky; tvrzení o 1/2-pot akci při trainingu nepodloženo primárem —
originál říká F/C/P/A) = jen stopy, ne ground truth.

### 22.-23. Training NN + bucketing
Torch7, Adam, Huber, minibatch 1000, lr 0.001 -> 0.0001 po 200
epochách, ~350 epoch, ~2 dny 1 GPU, checkpoint dle validation loss.
Validation losses: Turn 0.026, Flop 0.034, Auxiliary 0.000055 pot
(statistický oracle). Bucketing: 1000 buckets, k-means nad
hand-strength features s EMD; auxiliary 169 preflop tříd; pro plnou
reprodukci NN inputu budou potřeba originální centroidy/mapping.

### 24.-26. Souhrn
Algorithm-exact skeleton je rekonstruovatelný už teď (sample state/pot/
ranges -> ~1000 CFR+ F/C/P/A -> root CFVs/pot -> serialize). Bit-exact
blokují: RNG, master seed, worker seed derivation, RNG call ordering,
board sampler, 1326 ordering, tie-breaking, blocker semantics, strength
výpočet, pot first-bin, offline averaging/omit semantics, float
precision, parallel reduction order, serializace, worker assignment,
bucket mapping. Artefakty A-E: vše zatím nenalezeno (D/E mají silnou
CPRG genealogii). Jediný původní job script/raw sample/seed config by
vyřešil několik neznámých najednou.

---

## Implication map for THIS repo's pilot (English, maintainer-added)

The pilot parameterization (CONFIG_CANON in hunl_datagen/turn_datagen.py,
schema HUNL_TURN_DATASET_V1) stays FROZEN for the running pilot — the
certification certifies the documented parameterization, not a claim of
author-bit-exactness (never claimed; the original HUNL byte layout and
configs were never released). These notes change the LABELS and the
report's risk register:

1. `cfr_omit = 500 (INFERRED)` — DOWNGRADED to **HYPOTHESIS**: offline
   omission is not documented anywhere first-party (§5), and online
   configs are self-contradictory (§6). The report must carry this as an
   open fork, not a corroborated inference.
2. **Solver update semantics fork (NEW, material)**: Schmid's own CFR+
   definition is RM+ + alternating updates + linear averaging (§4); our
   frozen engine runs simultaneous updates + uniform post-omit
   averaging (the released-Leduc-code anchoring). Both readings are
   defensible; they are NOT numerically equivalent. Recorded as
   parameter-risk fork R-1; a post-pilot sensitivity experiment
   (alternating/linear-weight 1000-iter full-average variant vs the
   pilot config on identical inputs, target delta in pot fractions) is
   the planned quantification.
3. Pot first bin: the pilot's `{100}` singleton reading (spec C3) keeps
   corroboration (3 secondary codebases use constant 100); the
   `[100,200)` gap-filling hypothesis (§10) joins the risk register as
   the alternative — NOT silently adopted.
4. RNG/seed layer remains PROJECT CANONICAL (never released); the CPRG
   MT19937 genealogy (§16-17) strengthens the plausibility of our
   MT19937-family choice (THRandom == same core generator family as
   CPRG init_genrand/genrand_int32 — bit-identical streams verified in
   this repo) without proving author identity.
5. Statistical oracles for any future NN phase: validation losses
   (Turn 0.026 pot) and bucketing parameters (§22-23) recorded.
