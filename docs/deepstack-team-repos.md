# DeepStack — mapa autorů a jejich repozitářů

**Rozsah.** Tento dokument vědomě **ruší** původní scope rule předchozího huntu
(„výhradně Neil Burch, nerozšiřovat na jiné autory"). Pokrývá všech deset autorů
DeepStacku a jejich veřejné repozitáře.
**Companion:** `docs/burch-forensics.md` (ledger, 53 nálezů), `docs/burch-handoff.md`.
**Datum:** 2026-08-15.

---

## 1. Autoři — primární zdroj

Z `arXiv:1701.01724v3`, `paper.tex`, autorský blok:

| # | Autor | Afiliace |
|---|---|---|
| 1 | **Matej Moravčík** † | UAlberta ♠ + Charles University ♥ |
| 2 | **Martin Schmid** † | UAlberta ♠ + Charles University ♥ |
| 3 | **Neil Burch** | UAlberta ♠ |
| 4 | **Viliam Lisý** | UAlberta ♠ + ČVUT FEL ♣ |
| 5 | **Dustin Morrill** | UAlberta ♠ |
| 6 | **Nolan Bard** | UAlberta ♠ |
| 7 | **Trevor Davis** | UAlberta ♠ |
| 8 | **Kevin Waugh** | UAlberta ♠ |
| 9 | **Michael Johanson** | UAlberta ♠ |
| 10 | **Michael Bowling** ∗ | UAlberta ♠ — korespondenční autor, `bowling@cs.ualberta.ca` |

† *„These authors contributed equally to this work and are listed in alphabetical order."*

Doplňkově z Burchovy thesis (preface): DeepStack ethics approval
„Evaluating the skill of state-of-the-art computer poker agents", **No. 67663, 2016-10-24**.
Schmidova disertace (Charles University, 2021): školitel **Milan Hladík**,
konzultant **Michael Bowling**.

---

## 2. Mapa účtů

| Autor | Účet | Repo | Status |
|---|---|---|---|
| Matej Moravčík | **nenalezen** | — | Name search 0 výsledků. Nyní CSO & spoluzakladatel **EquiLibre Technologies**, dříve DeepMind |
| Martin Schmid | **`lifrordi`** | 5 | ✅ potvrzeno bio: *„Research Scientist, co-author of DeepStack"*; web `kam.mff.cuni.cz/agtg/martin` |
| Neil Burch | `NeilBurch` | 2 (jen forky) | ✅ Arctic Code Vault; žádný vlastní commit |
| Neil Burch | `neilburch-sony` | 0 | ✅ prázdný |
| Viliam Lisý | `ViliamLisy` | **0** | ✅ Pro účet, žádné veřejné repo |
| Dustin Morrill | **`dmorrill10`** | **65** | ✅ Edmonton; největší nález |
| Dustin Morrill | `morrill-sony` | 0 | ✅ prázdný |
| Nolan Bard | `nolanbard-sony` | 0 | ✅ prázdný |
| Trevor Davis | **nenalezen** | — | MSc UAlberta 2016; žádný účet nenalezen |
| Kevin Waugh | **`kdub0`** | **7** | ✅ Calgary, `kevinwaugh.com`; **nalezen přes fork lineage, ne jménem** |
| Kevin Waugh | `kwaugh-sony` | 0 | ✅ prázdný |
| Michael Johanson | `mikebjohanson` | **0** | ✅ *„Rogue Game Theorist. Previously: Co-founder Artificial.Agency, RS DeepMind, PhD UAlberta, Poker AI."* |
| Michael Bowling | **`bowlingmh`** | ~3 | ✅ **nalezen přes fork lineage, ne jménem** |

### Dvě pozorování k metodě

**Fork lineage překonává name search.** `kdub0` (Waugh) a `bowlingmh` (Bowling)
GitHub user search podle jména **nenašel**. Objevily se až jako upstream forků
v repozitářích Dustina Morrilla (`acpc_hand_converter` ← `kdub0`,
`seq_predict` ← `bowlingmh`). Kdo hledá jen jménem, mine je.

**Sony AI cluster.** Čtyři z deseti autorů mají prázdné účty ve tvaru `*-sony`:
`neilburch-sony`, `morrill-sony`, `kwaugh-sony`, `nolanbard-sony`. Ukazuje, kam
část týmu odešla; obsahově bezcenné.

---

## 3. Repozitáře podle relevance k DataGeneratoru

### P1 — přímo na cestě k cíli A (range/bucket reprezentace)

**`kdub0/hand-isomorphism`** — C, 74★, 24 forků, poslední změna 2014-08-01
> „A C library for efficiently mapping poker hands to and from a tight set of indices.
> Poker hands are isomorphic with respect to permutations of the suits and ordering
> within a betting round. That is, AsKs, KdAd and KhAh all map to the same index preflop."
>
> author: Kevin Waugh (`waugh@cs.cmu.edu`), 2013-04-07
> Reference: K. Waugh, *A Fast and Optimal Hand Isomorphism Algorithm*, AAAI Computer
> Poker and Imperfect Information Symposium, 2013. API v `src/hand_index.h`.

**Proč P1:** je to přesně ta primitiva, kterou dělá `sortedCardsNumSuitMappings()` a
`cardsToCanonicalCards()` v Burchově `CFR_plus/card_tools.c` (ledger #14, #49), a kterou
DeepStack potřebuje pro mapování 1326 rukou do 1000 bucketů. **First-party artefakt
DeepStack spoluautora, veřejný, kompletní.**

**`lifrordi/DeepStack-Leduc`** — Lua, 949★, 225 forků, poslední změna 2018-01-06
> Reimplementace DeepStacku pro Leduc hold'em. Obsahuje offline komponentu, která
> „solves random **poker situations**".

**Proč P1:** jediná veřejná implementace DeepStack pipeline včetně generování dat.
**Výhrada z původního zadání zůstává v platnosti: není to HUNL oracle.** Leduc má
6 karet a 2 kola; range generator i pot distribuce jsou jiné.

### P2 — ACPC infrastruktura (cíle D/E, genealogicky)

Vše `dmorrill10`, převážně Ruby:

| Repo | Popis |
|---|---|
| `acpc_dealer` | Ruby rozhraní k ACPC dealer programu |
| `acpc_poker_types` | Pokerové typy dle ACPC standardu |
| `acpc_poker_player_proxy` | Proxy komunikující s ACPC dealerem, spravuje stav zápasu |
| `acpc_table` | Standalone verze ACPC Poker GUI Client table |
| `acpc_table_manager` | — |
| `acpc_vagrant` | Vagrant VM pro vývoj ACPC GUI klienta |
| `acpc_hand_converter` | fork z `kdub0/acpc_hand_converter` |

Původní `kdub0/acpc_hand_converter` (Python, BSD-2, 2017-04-02) je nástroj, kterým
vznikly PokerStars-formátované logy v `DeepStack_vs_IFP_pros.zip` (ledger #43).

### P3 — související, ale mimo linii

| Repo | Autor | Poznámka |
|---|---|---|
| `dmorrill10/hr_edl_experiments` | Morrill | „Experiments, data, and results for MAL and general sum game experiments with CFR" |
| `dmorrill10/research2018` | Morrill | výzkumný kód 2018 |
| `dmorrill10/open_spiel` + `open_spiel-project-template` | Morrill | fork DeepMind OpenSpiel |
| `NeilBurch/open_spiel`, `NeilBurch/roshambo` | Burch | forky, žádný vlastní commit |
| `kdub0/kuhn3p` | Waugh | 3-player Kuhn, ACPC 2014 |
| `kdub0/ice` | Waugh | Inverse Correlated Equilibrium, Waugh et al. 2011 |
| `kdub0/subzero`, `kdub0.github.io` | Waugh | `sub-zero.ai` |
| `bowlingmh/seq_predict` | Bowling | Bayesovská predikce sekvencí (KT, SAD, CTW), 2016 |
| `lifrordi/algorithmic_game_theory` | Schmid | kurz NOPT021, Charles University |
| `lifrordi/game_theory_2023`, `game_theory_2024` | Schmid | starší ročníky kurzu |
| `lifrordi/webpage` | Schmid | osobní web |

---

## 4. Schmidův „game theory dokument" — co v něm je

`lifrordi/algorithmic_game_theory` — *Modern Algorithmic Game Theory (NOPT021)*,
Faculty of Mathematics and Physics, Charles University.
Kurzový web: `sites.google.com/view/agtg-101`.

Struktura: `slides/`, `tasks/` (zadání v Markdownu), `templates/` (signatury funkcí),
`tests/` (pytest proti referenčním implementacím), `requirements.txt`.

> **Jména v něm nejsou.** README neuvádí žádného přednášejícího ani přispěvatele —
> kontakt jen přes „course Discord server or the faculty emails". Jediný identifikovatelný
> člověk je vlastník účtu `lifrordi` = Martin Schmid.
>
> Podle vašeho evidence ledgeru v2 obsahuje `tests/` soubor `ref_cfr_plus_kuhn.txt` —
> referenční výstup CFR+ pro Kuhn poker. **Výukový artefakt, ne DeepStack provenance.**

Lepší zdroj jmen je Schmidova **disertace** *Search in Imperfect Information Games*
(Charles University 2021, `arXiv:2111.05884`, dspace `20.500.11956/173905`), jejíž
poděkování by kolaboranty jmenovalo. **Z tohoto prostředí nedostupná** —
`dspace.cuni.cz` i `arxiv.org` jsou blokované egress proxy.

---

## 5. Nenalezeno a nedostupné

| Cíl | Status |
|---|---|
| Matej Moravčík — GitHub | **nenalezen** name searchem. Zkusit přes EquiLibre Technologies org, DeepMind publikace, nebo fork lineage |
| Trevor Davis — GitHub | **nenalezen**. MSc UAlberta 2016 |
| EquiLibre Technologies — GitHub org | **neověřeno**, GitHub search endpoint vrátil 429 (Retry-After 3600) |
| Schmidova disertace, plný text | `dspace.cuni.cz` blokován |
| `kam.mff.cuni.cz/agtg/martin`, `johanson.ca`, `kevinwaugh.com`, `sites.google.com` | všechny **blokované** egress proxy |
| GitHub code search | vyžaduje přihlášení |
| `dmorrill10` — repozitáře 31–65 | seznam useknut na 30; zbytek nevytěžen |

---

## 6. Doporučené další kroky

1. **`kdub0/hand-isomorphism` naklonovat a projít** — jediný P1 artefakt, který je
   veřejný, kompletní a přímo na cestě k cíli A. Porovnat `src/hand_index.h` proti
   `CFR_plus/card_tools.c`; pokud se algoritmy shodují, je to doložená sdílená primitiva
   napříč CPRG.
2. **Dotáhnout `dmorrill10` repozitáře 31–65** — 35 nevytěžených repozitářů člověka,
   který psal ACPC tooling.
3. **Moravčík a Davis** — hledat přes fork lineage a přes EquiLibre Technologies, ne jménem.
4. **Schmidova disertace** — z neblokované sítě; poděkování a případné odkazy na
   interní infrastrukturu.
5. `lifrordi/DeepStack-Leduc` `data_generation` — s výhradou, že Leduc není HUNL oracle.

---

*Připraveno jako rozšíření Burchova huntu po zrušení scope rule. Účty označené ✅ byly
ověřeny z GitHub profilu nebo README; „nenalezen" znamená prohledáno bez výsledku,
„neověřeno" znamená zablokováno.*
