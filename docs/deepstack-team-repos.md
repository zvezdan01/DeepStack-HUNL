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

## 5b. Vytěženo — druhé kolo

### ⭐ Nález T1 (P1) — Waughova `hand-isomorphism` vs Burchův `card_tools.c`: **dvě nezávislé implementace**

Staženy zdrojáky `kdub0/hand-isomorphism` (`src/hand_index.h`, `hand_index.c` 20 457 B,
`hand_index-impl.h`, `deck.c/h`) a porovnány s Burchovým `CFR_plus/card_tools.c`.

**Křížová kontrola:** `grep -rn "hand_index\|hand_indexer\|isomorph"` přes celý CFR+ →
jediné zásahy jsou dva **komentáře** (`card_tools.c:559`, `:648`,
*„Have we found a new suit that is isomorphic…"*). **Žádná reference na Waughovu knihovnu.**

| | Burch — `card_tools.c` | Waugh — `hand-isomorphism` |
|---|---|---|
| Přístup | enumerate-and-weight | index-and-invert |
| Výstup | násobnost ekvivalentních suit mapování, `0` = nekanonické | hustý bijektivní index + inverze (`hand_unindex`) |
| Tabulky | žádné, počítá se za běhu | předpočítané v `__attribute__((constructor))`: `equal[]`, `nth_unset[]`, `nCr_ranks[][]`, `nCr_groups[][]`, `rank_set_to_index[]`, `index_to_rank_set[][]`, `suit_permutations[][]` |
| Stav suit-grup | `uint32_t suitGroups`, jeden bajt na barvu, inkrementálně `updateSuitGroups()` | `hand_indexer_state_t`, per-round |
| Vícekolovost | implicitní přes `suitGroups` | explicitní `cards_per_round[]`, `hand_index_next_round()` |
| API | `sortedCardsNumSuitMappings`, `cardsToCanonicalCards(Extended)` | `hand_indexer_init/size/state_init`, `hand_index_all/last/next_round`, `hand_unindex` |
| Autor, datum | Neil Burch, ≤2014 | Kevin Waugh (`waugh@cs.cmu.edu`), 2013-04-13 |

> **Závěr:** CPRG mělo **dvě nezávislé implementace suit izomorfismu** — Burchovu uvnitř
> solveru a Waughovu jako samostatnou knihovnu. Nejsou to varianty téhož kódu.
>
> **Které z nich by použil DataGenerator?** Supplement říká, že buckety vznikly k-means
> clusteringem s earth mover's distance nad hand-strength featurami
> (`Johanson13:Abstraction`, `Ganzfried14:EMD`). Abstrakční pipeline tohoto typu potřebuje
> **indexer**, ne weight-based enumeraci — tedy spíš Waughova knihovna. **Hypotéza, ne důkaz.**

### Nález T2 (P2, cíl E) — PBS/TORQUE nástroje Dustina Morrilla jsou stuby

Dva repozitáře vypadaly jako přímý zásah na cíl E. Nejsou.

| Repo | Obsah | Verdikt |
|---|---|---|
| `dmorrill10/science-environment` | *„Scripts and environment additions to make scientific computing on TORQUE (PBS)/MOAB clusters easier."* MIT, © 2013 Dustin Morrill | **3 soubory**: `defs` (2 řádky — jen `SCIENCE_ENVIRONMENT=$HOME/.science-environment`), `bin/link_bin`, `bin/executables/monitor_files`. Autor sám píše *„This is a work in progress"* |
| `dmorrill10/pbs_job` | Ruby gem | README je nevyplněná šablona: *„TODO: Write a gem description"*, *„TODO: Write usage instructions here"* |

> **NEGATIVE pro cíl E co do obsahu.** Žádné `qsub` volání, žádné `#PBS` direktivy,
> žádné `nodes=`/`ppn=`/`walltime`, žádná alokace seedů. Potvrzuje jen, že tým na
> TORQUE/PBS clusterech pracoval — což už víme z `.mp2.m.out` logů (ledger #30).

### Nález T3 (P2) — další ACPC repozitáře Morrilla (strana 2)

| Repo | Popis | Poznámka |
|---|---|---|
| `acpc_poker_gui_client` | Rails aplikace, kterou lidé hrají poker proti ACPC dealeru přes web GUI | **Pravděpodobně** software použitý pro human study — IFP README zmiňuje *„delay from the browser interface"*. **Neprokázáno** |
| `acpc_match_log` | ACPC match log parsing, C++ | |
| `project_acpc_server` | fork ACPC serveru | |
| `acpc_poker_basic_proxy`, `acpc_poker_match_state` | Ruby | |
| `hand-isomorphism` | **fork z `kdub0`** | potvrzuje, že Morrill Waughovu knihovnu používal |
| `tree_and_history_traversal` | C++ header-only, průchod stromy se stavovou historií | |
| `cpp_utilities` | ladicí a paměťové utility C++ | |

---

## 5c. Commit forensics — třetí kolo

### Nález T4 — kanál se otevřel

GitHub `/search` byl na hodinu `429`, ale **git proxy této session obsluhuje anonymní
čtení libovolného veřejného GitHub repozitáře** (`git clone`/`fetch`, bez přihlášení,
mimo rate limit vyhledávání). Tím se poprvé v celém huntu otevřela **commit forensics
nad cizími repozitáři** — sekce původního zadání, na kterou dosud nebylo dosaženo.

### Nález T5 (P1) — `lifrordi/DeepStack-Leduc` nemá vývojovou historii

```
da416f9  2017-04-05  Martin Schmid <lifrordi@gmail.com>  -fixed cutorch version in the readme.md …
bd344ca  2017-04-05  Martin Schmid <lifrordi@gmail.com>  Initial commit
```

**2 commity, jeden autor, jeden den.** Větve: pouze `master`. Tagy: 0.

> Jediná veřejná implementace DeepStack pipeline byla publikována jako **hotový dump**,
> ne jako vyvíjený projekt. Vývoj proběhl jinde a jeho historie do veřejného repozitáře
> nikdy nešla.
>
> **Moravčík do něj nikdy nepřispěl** — DeepStack-Leduc je Schmidovo vydání.
> Zároveň definitivně potvrzuje identitu `lifrordi` = Martin Schmid (`lifrordi@gmail.com`).

### Nález T6 (P2) — `kdub0/hand-isomorphism`: obnoveny smazané větve i soubory

83 commitů, **2013-04-07 → 2014-07-31**.

| Autor | Commitů |
|---|---|
| Kevin Waugh `<kevin.waugh@gmail.com>` (jako „Kevin" i „Kevin Waugh") | 82 |
| Dustin Morrill `<dmorrill10@gmail.com>` | 1 — PR #1, *„Added math library flag for linking on Linux"* |

**Smazané topic větve rekonstruované z merge zpráv** (samotné větve už neexistují):
`dev`, `set`, `rank_set`, `group_index`, `tabulate`, `test`.

**Obnoveno 13 smazaných souborů** z rodičovských commitů:

| Soubor | Velikost | Verdikt |
|---|---|---|
| `src/index_flop-main.c` | **49 B** | prázdný stub `int main(){return 0;}` — **NEGATIVE** |
| `src/unindex_flop-main.c` | **49 B** | totéž — **NEGATIVE** |
| `src/rank_set.h` | 8 468 B | pre-refactor API, později složeno do `hand_index.c` |
| `src/group_index.h` | 1 911 B | pre-refactor API |
| `src/card_set.*`, `rank_set.c`, `group_index.c`, `test.*`, `*-test.c` | — | vývojové mezistupně |

> Názvy `index_flop-main.c` / `unindex_flop-main.c` sliboval samostatné nástroje pro
> indexování flopových rukou — což by DeepStack flop network potřeboval.
> **Jsou to prázdné stuby.** Zaznamenáno jako negativní, aby po nich nikdo nešel znovu.
>
> `git fsck --lost-found`: **žádné dangling objekty.**

### Nález T7 (P2, NEGATIVE) — Morrillovy ACPC repozitáře nenesou CPRG SVN historii

| Repo | Commitů | Rozsah |
|---|---|---|
| `dmorrill10/project_acpc_server` | 80 | 2012-06-29 → 2017-01-06 |
| `dmorrill10/acpc_dealer` | 82 | 2012-06-29 → 2020-04-04 |

Autoři obou: Dustin Morrill (`dmorrill10@gmail.com`, `morrill@ualberta.ca`) a
Jesse Rosenstock (2 commity).

Nejstarší commit: *„Initial commit with dealer, hand evaluator extension, and rake task
to compile both."* (2012-06-29).

Grep přes všechny commit zprávy a těla na `svn|trunk|uoapoker|cprg|internal`: **prázdno.**
`git fsck --lost-found`: **žádné dangling objekty.**

> Přestože je `project_acpc_server` označen jako „fork", **nenese historii CPRG SVN.**
> Vznikl z **uvolněných tarballů**, stejně jako `jblespiau/project_acpc_server` (ledger #3).
> Cesta k `project_uoapoker` přes veřejné forky tedy **nevede**.

### Potvrzené e-mailové identity

| Osoba | E-mail | Zdroj |
|---|---|---|
| Martin Schmid | `lifrordi@gmail.com` | commity DeepStack-Leduc |
| Kevin Waugh | `kevin.waugh@gmail.com`, `waugh@cs.cmu.edu` | commity + README hand-isomorphism |
| Dustin Morrill | `dmorrill10@gmail.com`, **`morrill@ualberta.ca`** | commity ACPC repozitářů |
| Michael Bowling | `mbowling@ualberta.ca`, `bowling@cs.ualberta.ca` | `seq_predict` LICENSE, DeepStack `paper.tex` |
| Neil Burch | `burchn@google.com` | JAIR `burch19a.tex` (ledger) |

---

### ⭐ Nález T8 (P1) — `acpc_poker_gui_client` a human study: silná shoda funkcí

614 commitů, **2011-10-13 → 2016-12-01**, autor Dustin Morrill
(`dmorrill10@gmail.com` + `morrill@ualberta.ca`). **26 remote větví** včetně
`exhibition`, `exhibitionOnlyPolling`, `humanVsHuman`, `websockets`, `sidekiq`,
`v0.0`, `v1.0`, `v1.2`, `webpack`.

**Vývoj v srpnu 2016 — tři měsíce před studií** (studie: 2016-11-07 → 2016-12-16, ledger #35):

| Datum | Commit |
|---|---|
| 2016-08-22 | Allow other matches to be **hidden from users** with a configuration option |
| 2016-08-21 | Escape user and match names properly |
| **2016-08-18** | **Allow a configuration option to fold or check after a timeout instead of leaving the match** |
| 2016-08-15 | Allow **pauses between hands** with a configuration option |
| 2016-08-13 | Replace god with daemon-overlord |

Porovnej s `DeepStack_vs_IFP_pros/.../README.txt`:

> *„DeepStack **disconnected on nine hands** against two participants, **causing it to
> check/fold** against them for the rest of the hand."*

> **To je přesně ta funkce z 2016-08-18.** Dále sedí: skrývání ostatních zápasů před
> účastníky (hráli izolovaně), escapování jmen (účastníci měli jména typu
> `bachmann.juergen.1`), pauzy mezi rukama, a `timer` komponenta odpovídající poli
> *„Seconds to Act … includes any network lag, and delay from the browser interface"*.

**Commity během studie samotné** (2016-11-30, 2016-12-01) jsou naopak Webpack refactoring,
který aplikaci **rozbil** — *„Welcome page shows but does not work properly"*,
*„Still broken though"*.

> **Čtení:** studie běžela na **srpnovém stavu** (poslední stabilní před 2016-11-07),
> zatímco Morrill mezitím na masteru refaktoroval. Nikdo si uprostřed sběru dat
> nerozbije produkci.
>
> **Klasifikace:** funkční shoda je silná a časově konzistentní, ale **není to důkaz**,
> že tento konkrétní repozitář byl nasazený deployment. Studie mohla běžet z jiné větve,
> forku nebo interní kopie. Posouvám T3 z „pravděpodobně" na **„silně podloženo,
> neprokázáno"**.

---

### ⭐ Nález T9 — jména v Schmidově „game theory dokumentu" (přes commit historii)

README kurzu nejmenuje nikoho (§4). **Commit historie ano.** Naklonováno přes git proxy:

| Repo | Commitů | Rozsah |
|---|---|---|
| `lifrordi/algorithmic_game_theory` | 65 | 2025-09-15 → 2026-02-11 |
| `lifrordi/game_theory_2024` | 39 | 2024-10-15 → 2024-12-30 |
| `lifrordi/game_theory_2023` | 12 | 2023-10-07 → 2024-02-03 |

**Autoři:**

| Osoba | E-mail | Commitů | Role |
|---|---|---|---|
| **Radovan Haluška** | `radovan.haluska1@gmail.com` | **94** | hlavní autor materiálů; PhD student na UK, jeho diplomku *„Analyzing the State-of-the-Art AI in the Game of Hearthstone"* vedl **Mgr. Martin Schmid, Ph.D.** |
| **`schmid-equilibre`** | **`schmid@equilibretechnologies.com`** | 7 | **druhý účet Martina Schmida**, vázaný na EquiLibre Technologies |
| Martin Schmid | `lifrordi@gmail.com` | 1 | osobní účet |
| **Dominik Farhan** | `nikousf@seznam.cz` | 1 | |
| **Matej Straka** | `strakammm@gmail.com` | 1 | |

> **Odpověď na otázku „kdo se podílel na tom dokumentu":** materiály píše převážně
> **Radovan Haluška**, Schmidův doktorand, ne Schmid sám. Schmid přispívá z účtu
> `schmid-equilibre` firemním e-mailem.
>
> **Nový lead:** `schmid@equilibretechnologies.com` je firemní doména EquiLibre Technologies —
> firmy, kde je **Moravčík CSO**. Veřejná GitHub organizace `equilibretechnologies` se ale
> nenašla (`equilibre-finance` je jiná, DeFi firma).

### Nález T10 (NEGATIVE) — Moravčík a Davis nemají dohledatelnou veřejnou GitHub stopu

**Matej Moravčík** — vyzkoušeno pět strategií, všechny bez výsledku:

| Strategie | Výsledek |
|---|---|
| GitHub user search `fullname:"Matej Moravcik"` | 0 |
| WebSearch na handle (`moravcikm`, `Moravcik`, s diakritikou) | 0 |
| Commit historie `lifrordi/DeepStack-Leduc` | nikdy nepřispěl (T5) |
| Commit autoři `google-deepmind/open_spiel` (5 674 commitů) | nepřítomen |
| EquiLibre Technologies GitHub org | veřejná organizace nenalezena |

**Trevor Davis** — GitHub user search vrací **34 jmenovců**, žádný neodpovídá profilu
(UAlberta, MSc 2016, game theory). Filtr `location:Alberta` se nepodařilo dokončit
kvůli 503.

> **Poctivý závěr:** oba pravděpodobně **nemají veřejnou GitHub přítomnost**.
> Není to selhání hledání — u výzkumníků je to běžné. Vedeno jako NEGATIVE
> s výhradou u Davise (běžné jméno, filtr nedokončen).

### Nález T11 — OpenSpiel: interní export anonymizuje autory

`google-deepmind/open_spiel`, 5 674 commitů. Z DeepStack týmu je přítomen **jen
Dustin Morrill** (10 commitů, 2019-11 → 2024-08).

Top autoři obsahují **`DeepMind Technologies Ltd` (765 commitů)** a
**`open_spiel@google.com` (265)** — to je interní exportní cesta (copybara-style).

> **Důsledek:** příspěvky lidí uvnitř DeepMindu se v historii jako jednotlivci
> **neobjeví**. Přes OpenSpiel tedy Schmida ani Moravčíka identifikovat nelze,
> a jejich nepřítomnost v seznamu autorů **není důkazem**, že nepřispěli.

---

### ⭐⭐ Nález T12 (P0) — Morrill sám potvrzuje autorství match interface (povyšuje T8)

`dmorrill10/dmorrill10.github.io` (261 commitů, 2011-12-30 → 2026-08-13; ostatní autoři
v historii jsou tvůrci Jekyll šablony, ne spolupracovníci). Z `index.md`, doslova:

> *„I'm a coauthor of [DeepStack], **I created the match interface** you can see in
> [these exhibition match videos](https://www.youtube.com/@deepstackai1330), and before
> DeepStack, I created [Cepheus]'s [public match interface](http://poker-play.srv.ualberta.ca/)
> as well."*
>
> *„As an undergraduate, I worked with the Computer Poker Research Group to create an
> [**open-source web interface to play against poker bots**](https://github.com/dmorrill10/acpc_poker_gui_client)
> and to develop the 1st-place 3-player Kuhn poker entry in the 2014 Annual Computer
> Poker Competition."*

> **T8 povýšen z „silně podloženo, neprokázáno" na POTVRZENO first-party výrokem.**
> Morrill uvádí, že vytvořil match interface DeepStacku, a jako open-source webové
> rozhraní pro hru proti botům explicitně odkazuje **právě `acpc_poker_gui_client`**.
> Funkční shoda z T8 (fold/check po timeoutu ↔ devět rukou, kdy se DeepStack odpojil)
> tím dostává autorské potvrzení.

**Nové UAlberta hostnames** — dosud v huntu neznámé, odlišné od `poker.cs.ualberta.ca`:

| Host | Účel |
|---|---|
| `poker.srv.ualberta.ca` | Cepheus |
| `poker-play.srv.ualberta.ca` | **veřejné match interface Cephea** (Morrillovo dílo) |

> Pro Wayback enumeraci z neblokované sítě jsou to **dva nové cíle** vedle
> `poker.cs.ualberta.ca` a `webdocs.cs.ualberta.ca/~burch/`.
> Dále: `youtube.com/@deepstackai1330` — exhibition match videa.

**Morrillova akademická časová osa** (relevantní pro dataci ACPC infrastruktury):

| Období | |
|---|---|
| 2008–2013 | B.Sc. UAlberta — **jako student vytvořil ACPC web interface** |
| 2014–2016 | M.Sc., školitel Bowling — *„Using Regret Estimation to Solve Games Compactly"* |
| 2016–2022 | Ph.D., školitelé **Michael Bowling** + **Amy Greenwald** (Brown University) |
| dnes | senior research scientist, Sony AI (GT Sophy) |

**Nová jména** z jeho publikací (mimo DeepStack tým): Amy Greenwald (Brown),
Montaser Mohammedalamen, Alexander Sieusahai, Yash Satsangi, Thomas J. Walsh,
Daniel Hernandez, Peter R. Wurman, Peter Stone (Sony AI).

`lifrordi/webpage` — 2 commity, 2026-03-30/31, jen Schmid. Nový, bez historie.

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
