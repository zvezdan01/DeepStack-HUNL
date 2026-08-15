# Neil Burch — forensic ledger v11

**DeepStack HUNL DataGenerator provenance**
Datum: 2026-08-15 · Rozsah: výhradně Neil Burch · 53 nálezů, 14 vln — průchod zdroji ÚPLNÝ · #20 opraven ve vlně 14

---

## 0. Executive summary

Cíle A–E (originální HUNL range generator / DataGenerator / raw training samples / RNG seed config /
cluster manifest) **nebyly nalezeny**. Žádný z nich není veřejně dostupný a analýza ukazuje, že žádný
z prohledaných Burchových artefaktů je neobsahuje ani obsahovat nemůže.

Co bylo místo toho získáno:

1. **Úplný chain of custody** pro Burchův CFR+ solver (P0) — jediný veřejný first-party Burchův
   solver-artefakt, s ověřeným původem od SVN trunku po dnešní mirrory.
2. **Bit-exact specifikace** jediného dochovaného Burchova sampleru pokerových situací.
3. **Tři vyvrácené hypotézy** — nikoli nepodložené, ale prokazatelně nepravdivé pro dané artefakty.
4. **Přímý důkaz o `[100, 100)`** z originálního LaTeX zdroje DeepStack supplementu.
5. **Burchův podepsaný nepublikovaný technický komentář** z ledna 2014.

### Stav A–E

| Cíl | Stav | Poznámka |
|-----|------|----------|
| **A** HUNL range generator | **NOT FOUND** (zdrojový kód) | Specifikace R(S,p) plně vytěžena vč. verzní historie; bit-exact rekonstrukce **prokazatelně nemožná** — viz #17 |
| **B** DataGenerator / job script | **NOT FOUND** | Doloženo, že to nebyl wrapper nad CFR+ (#6) ani `cfr_player.c` (#10) |
| **C** raw HUNL training samples | **NOT FOUND** | Žádná stopa v žádném z 11 analyzovaných artefaktů |
| **D** RNG seed / config | **NOT FOUND** pro DeepStack | Precursor bit-exact specifikován (#13, #14); MT19937 hypotéza **vyvrácena** (#9) |
| **E** cluster log / manifest | **NOT FOUND** | Spec z originálního LaTeXu; okno zúženo na 2015 – Q3 2016 (#15, #23) |

---

## 1. Analyzované zdroje

### 1.1 Primární artefakty (lokálně, plná analýza)

| Artefakt | Identifikace | Rozsah analýzy |
|---|---|---|
| `CFR_plus.tar.bz2` | SHA256 `177fb8ac00bbf66abfb372c9d6e1465c334fada40ef0d305b5c80f00a8b10f0f`, tar owner/group `burch/burch`, mtime 2014-11-18 20:29 *(údaje z user evidence ledger; nezávisle ověřeno přes 2 mirrory)* | 20 souborů, řádek po řádku |
| Burch PhD thesis | `Burch_Neil_E_201712_PhD.pdf` → txt, 7 243 řádků | úplný grep + kapitola 6 přečtena celá |
| Thesis DOCX | SolidFramework v10.0.19910.1 konverze | docProps, 60 souborů, 45 PNG |
| arXiv 1701.01724 v1 | SHA256 `061e2dbc97539a026b3cbde080c0634a1222b2a4002b39434dc06f894db11e2f` | `paper.tex`, `appendix.tex`, komentáře, tar mtime |
| arXiv 1701.01724 v2 | SHA256 `9781a9ca66bfefbcfbd5fba12a27a869f468ff735559592f7a40d5e13a1b695f` | idem + diff proti v1 |
| arXiv 1701.01724 v3 | SHA256 `8efb295b56647c6032d553847cc7a693166fc41ca32ea882250ac113049a2ebf` | idem + diff proti v2 |
| arXiv 1612.06915 v1 (AIVAT) | SHA256 `a0fdd437c4dbdf7059b810ecf913f35ae5362a2879ad15223cc6744a254530e0` | `vat.tex` úplně |
| arXiv 1612.06915 v2 (AIVAT) | SHA256 `8edb39b26cbce874b6196b7289f71a9a3bdd950c73e0772bd6ce78374085007c` | idem + diff |
| arXiv 1303.4441 v1 (CFR-D) | SHA256 `8b31c522b17643d48abb20728ae86ea6f1d7b17793f95cb6bcbe416d83760462` | `cfrd.tex` úplně |
| arXiv 1303.4441 v2 (CFR-D) | SHA256 `4cccc76c8171a36cb9c25f29741daf4d19d3fc7e4c83715a137fd57438c89f98` | idem + diff |
| arXiv 1303.4441 v3 (CFR-D) | SHA256 `f25ed0e5204cc8245e849f9586ccfa05e1676195f12f2afc455a0bfedf5847c6` | idem + diff + `\comment{}` bloky |

### 1.2 Mirrory ověřené online

| Mirror | Ověření |
|---|---|
| `github.com/godmoves/cfr_plus` | 20 souborů staženo přes `raw.githubusercontent.com` |
| `github.com/strikles/cfr_plus` | 20 souborů staženo; `diff -rq` proti godmoves = **byte-identické 20/20** |
| `github.com/jblespiau/project_acpc_server` | `rng.h`, `rng.cc`, `game.h`, `dealer.c`, `README` |

Manifest hash CFR+ (sha256 všech 20 souborů, seřazeno, pak sha256):
`d5d92d0497a4f9e8429f7b2ee40bcbfa35952a92de4ce58fe27f1390a68ff88e`

Jednotlivé soubory:
```
0e4a4d7ac3d310500f1dbd40e5d0d268d31d1dfecf5183314b99abf3aa646661  rng.c
d16535446b4ce8e360f0125b0124a1e7a1c02abaf0b333460be24142db5b0f17  rng.h
a2556e455259741bcd9d6fc5d269d93ce42da7c4c40b6c77aab388ec52045c23  storage.c
8c1e6ea33d32c020774823904d50206afdac49300018f4006e40bb181345d799  args.c
7c51944f285a365a3d7c092fece21edcacc1b6019fda775a08e33740cdca6fb7  cfr.c
89fea891d8d6e031b803c96761c9b939cd372799a26c4eec82536f549c923d84  game.c
4352b66e17678c63218766303707d38e8dc5f9275c1e95ed1df60469e38f6796  dealer.c        (ACPC)
81a7bff1c7a62791bba0c43d4b5041bc060b682935604dd4da6b5fff7420a2b3  game.cc         (ACPC)
```

### 1.3 Omezení prostředí

Egress proxy sandboxu propouštěla **výhradně**: `github.com` (HTML přes WebFetch),
`raw.githubusercontent.com`, `gitlab.com`, `bitbucket.org`, `launchpad.net`, `pypi.org`,
`registry.npmjs.org`.

Blokované (403 CONNECT / EGRESS_BLOCKED), ověřeno opakovaným probingem:
`poker.cs.ualberta.ca`, `webdocs.cs.ualberta.ca`, `cs.ualberta.ca`, `era.library.ualberta.ca`,
`ualberta.scholaris.ca`, `apps.ualberta.ca`, `web.archive.org`, `archive.org`,
`archive.softwareheritage.org`, `arxiv.org`, `export.arxiv.org`, `xxx.lanl.gov`,
`semanticscholar.org`, `zenodo.org`, `figshare.com`, `sourcegraph.com`, `grep.app`,
`searchcode.com`, `codesearch.debian.net`, `sources.debian.org`, `salsa.debian.org`,
`snapshot.debian.org`, `codeberg.org`, `gitee.com`, `git.sr.ht`, `repo.or.cz`, `svn.gna.org`,
`groups.google.com`, `forumserver.twoplustwo.com`, `computerpokercompetition.org`,
`google.com`, `duckduckgo.com`.

Navíc `api.github.com` a `git clone`/`codeload` byly proxy omezeny na repozitáře session
(`"sessions are bound to their configured repositories"`), a GitHub code search vyžaduje login.

**Důsledek:** větev „university home directory / Wayback / Software Heritage / ERA attachments"
je **neprovedená, ne negativní**. Nesmí být uzavřena jako NEGATIVE.

---

## 2. P0 — Chain of custody: CFR_plus jako first-party Burchův artefakt

**Nález #1.** Řetěz uzavřen, každý článek z primárního zdroje.

1. **Thesis cituje přesnou URL** — `thesis.txt:5665-5666`:
   ```
    [8] Michael Bowling, Neil Burch, Michael Johanson, and Oskari Tammelin.
        CFR+ . http://poker.cs.ualberta.ca/software/CFR_plus.tar.bz2.
   ```
2. **Thesis označuje tento kód za kód Cephea** — `thesis.txt:2594-2595`, §4.3.1:
   > "Figure 4.1 describes the performance of CFR+ in HULHE as used in the generation of Cepheus.
   > The strategy was generated using publicly released code [8], set up so that the average
   > strategy discarded the current strategy for the first 200 iterations."
3. **Abstrakt** — `thesis.txt:52`:
   > "We wrote and released an efficient, distributed implementation of CFR+ to solve heads-up
   > limit Texas hold'em."
4. **Tar nese UNIX vlastnictví `burch/burch`**, mtime 2014-11-18 20:29.
5. **Balicí příkaz je v Burchově vlastním Makefile** — `Makefile:43-46`:
   ```make
   # should only be run on a freshly-checked out repository
   # don't include faste/FSE compressor, not used for Science result
   CFR_plus.tar.bz2:
   	cd ..; mkdir CFR_plus; cp -r trunk/* CFR_plus; rm -f CFR_plus/compressor/fse*; \
   	rm -f CFR_plus/compressor/fast*; tar cvjf CFR_plus.tar.bz2 CFR_plus --exclude=*svn*; rm -rf CFR_plus
   ```
6. **Dva nezávislé mirrory byte-identické** (viz 1.2).

**Vztah k A–E:** B (solver, ne generátor) + D (seed schéma) + E (README = de-facto job manifest)
**First-party:** ANO · **Bit-exact:** viz příloha A

---

## 3. P0 — Tvrdé negativní důkazy

### Nález #6 — CFR+ nemá export counterfactual values

`cfr.c:2661` `dumpValues()` navzdory jménu dumpuje **regrety a average strategy**:
```c
snprintf( filename, 1000, "%s/%d.p%d.%c", dirname, subgame, p, type[i] );  // type = "ra"
dumpCompressedStorage( file, &storage->arrays->compressedRegrets[ r ][ p ] );
dumpCompressedStorage( file, &storage->arrays->compressedAvgStrategy[ r ][ p ] );
```
Volána 2× (`cfr.c:4107`, `cfr.c:4129`), checkpoint/finish. Jediná další hodnotová cesta je
`computeBR()` (`cfr.c:2587`) → **skalární** best-response value, normalizovaná
`factor = C(deckSize,2) × C(deckSize−2,2)`; ne per-hand CFV vektor.

> **Důsledek:** DataGenerator nemohl být skript nad touto binárkou. Byl to jiný program.

### Nález #9 — MT19937 je v CFR+ nedosažitelný mrtvý kód

| Symbol | Volající | Počet |
|---|---|---|
| `genrand_int32()` | `dealCard()` — `game.c:767` | 1 |
| `dealCard()` | `dealCards()` — `game.c:793`, `:803` | 2 |
| `dealCards()` | pouze deklarace `game.h:164` | **0** |
| `genrand*` / `rng_state_t` / `init_by_array` v `cfr.c`, `recompress.c`, `storage.c`, `card_tools.c`, `betting_tools.c`, `util.c`, `args.c` | — | **0** |

`game.c` je sdílený CPRG soubor přenesený z ACPC knihovny; rozdávací větev binárky `cfr`
ani `recompress` nikdy nespustí.

> **Důsledek:** CLI parametr `rngseed=` vede **výhradně** do glibc `random_r`. Hypotéza
> „DeepStack DataGenerator zdědil CPRG MT19937 přes CFR+" je pro tento artefakt vyvrácena.

### Nález #10 — chybějící `cfr_player.c` je hráč, ne generátor

`Makefile:37-41`:
```make
# CPRG-specific code used to link to the CPRG codebase for validation
# This target will not compile, as it requires the CPRG code.
cfr_player.so: ... cfr_player.c ...
	$(CC) $(CFLAGS) -shared -Wl,--export-dynamic -DPLAYER_OBJECT -o $@ ... cfr_player.c ...
```

Jediný efekt `PLAYER_OBJECT` ve zdrojáku — `betting_tools.h:23-25`:
```c
#ifdef PLAYER_OBJECT
  struct BettingNodeStruct *parent;
#endif
```

`parent` pointer = průchod betting tree **nahoru** = strategy lookup pro hrajícího agenta.
Generátor sestupuje, `parent` nepotřebuje.

> **Důsledek:** absence `cfr_player.c` **neskrývá** hledaný DataGenerator.

### Nález #11 — thesis: tvrzení o datasetu je izolované

**Preface** (`thesis.txt:103-108`) — povinná deklarace spoluautorství:
> "I was responsible for the theoretical bounds, along with T. Davis. **I provided an initial
> experimental framework, and generated one data set used to train the evaluation function.**
> M. Bowling led the research project…"

**Kapitola 6** (`thesis.txt:5241-5247`) — Burchovo vlastní vyprávění:
> "My main contribution is a theoretical analysis of the final algorithm done in cooperation with
> Trevor Davis. **I also worked on coordination and infrastructure**, and participated in general
> discussion throughout the project."

Grep celé thesis: `data set` → **1 hit** (řádek 106). `training` → **1 hit** (řádek 5240, a to
ve větě *"Martin Schmid and Matej Moravčík suggested the use of deep neural networks to build an
evaluation function from training data"*).

Kapitola 6 (str. 112–122) obsahuje §6.1 continual re-solving, §6.1.1 tvar I/O evaluation function,
§6.1.2 constraint values, §6.2 teorii, §6.3 výsledky (Table 6.1 LBR, Table 6.2 human study).
**Nula obrázků, nula popisu generování dat.**

> **Důsledek:** věta o datasetu je formalita atribuce autorství, ne technický záznam.
> Thesis není zdrojem pro DataGenerator.

### Nález #13 — determinism audit CFR+

| Konstrukce | Výskyty | Status |
|---|---|---|
| `random_r` / `initstate_r` | `storage.c:893`, `storage.c:1001` | **jediný živý RNG** |
| `genrand_int32` (MT19937) | `game.c:767` | mrtvý kód (#9) |
| `gettimeofday` | `args.c:340` (jen `rngseed=TIME`), 11× profiling | není zdroj náhody |
| `rand()`, `srand()`, `drand48`, `lrand48`, `arc4random`, `/dev/urandom`, `getpid()` | **0** | neexistují |

> CFR+ solver je plně deterministický při daném `rngseed` a daném rozdělení na subgames.

### Nález #16 — `[100, 100)` je v originálním LaTeXu a nikdy nebylo opraveno

`ds_v1/appendix.tex:259`:
```latex
\footnote{The fixed distribution selects an interval from the set of intervals
$\{[100, 100),$ $[200,400),$ $[400, 2000),$ $[2000, 6000),$ $[6000, 19950]\}$
with uniform probability, followed by uniformly selecting an integer from
within the chosen interval.}
```

| verze | mtime `appendix.tex` | footnote |
|---|---|---|
| v1 | 2017-01-06 14:26 | `[100, 100)` |
| v2 | 2017-01-10 02:29 | `[100, 100)` — `diff v1 v2` **prázdný** |
| v3 | 2017-02-13 04:40 (post-review) | `[100, 100)` — **nezměněno** |

> **PŘÍMÝ DŮKAZ:** není to artefakt extrakce z PDF, není to transkripční chyba, nebylo to
> nikdy zamýšleno jako `[100, 200)`. Překlep přežil dvě arXiv revize i peer review v Science,
> a to přesto, že autoři na tomtéž místě mezi v2 a v3 aktivně editovali (#17).

### Nález #17 — tie-breaking oprava v R(S,p) mezi v2 a v3

```
v1/v2:  all of the hands in $S_1$ have a lower hand strength than hands in $S_2$
v3:     all of the hands in $S_1$ have a hand strength no greater than hands in $S_2$
```

Ostrá → neostrá nerovnost. Původní formulace je nesplnitelná: hand strength má remízy, takže
rozdělit `|S₁| = ⌊|S|/2⌋` tak, aby *všechny* ruce v S₁ byly *striktně* slabší, obecně nelze.

> **Kritická výhrada:** opravený text je **nutný, ne dostačující**. „No greater than" připouští
> remízové ruce na obou stranách řezu, ale **neříká, které z nich jdou do S₁**. Deterministické
> tie-breaking pravidlo není v žádné ze tří verzí. **Bit-exact rekonstrukce R(S,p) z tohoto
> zdroje není možná ani po opravě.**

### Nález #20 — separace offline generátoru a online solveru

**OFFLINE — generování trénovacích dat** (`ds_v3/appendix.tex:397`):
> "the situations were approximately solved using **1,000 iterations of CFR⁺** with only betting
> actions fold, call, a pot-sized bet, and all-in."

Čisté CFR⁺. Žádná zmínka o vynechávání iterací.

**ONLINE — continual re-solving** (`ds_v3/appendix.tex:265` + Table `tab-lookahead`):
> "a **hybrid of vanilla CFR and CFR⁺**, which uses regret matching⁺ like CFR⁺, but does uniform
> weighting and simultaneous updates like vanilla CFR. When computing the final average strategy
> and average counterfactual values, **we omit the early iterations** of CFR in the averages."

| Round | CFR Iterations | Omitted Iterations | NN Eval |
|---|---|---|---|
| Pre-flop | 1000 | 980 | Aux/Flop |
| Flop | 1000 | 500 | Turn |
| Turn | 1000 | 500 | — |
| River | 2000 | 1000 | — |

> **Důsledek:** `omit_iters` patří výhradně online solveru a je per-round.
>
> ⚠️ **OPRAVENO VE VLNĚ 14 — viz `docs/deepstack-leduc-reference.md`, nález L2.**
> Referenční implementace `lifrordi/DeepStack-Leduc` (Martin Schmid, 2017) má
> `cfr_iters = 1000` a `cfr_skip_iters = 500`, a **tytéž parametry používá i v offline
> generování dat** — offline i online tam sdílí jeden solver. Text HUNL supplementu se
> nemění, ale jediná dochovaná referenční implementace mu odporuje. Tvrzení klesá
> z „potvrzeno z primárního zdroje" na **„platí pro text supplementu, referenční
> implementace dělá opak"**.

---

## 4. P1 — First-party Burchovy artefakty

### Nález #2 — Burchův MT19937 fork (2005-09-07)

`rng.c:52` a `rng.h:15`:
```c
/* NOTE changes made on 2005/9/7 by Neil Burch - if you have problems
   with this code, DON'T complain to Makoto Matsumoto... */
```

Burchova změna = reentrantní `rng_state_t { uint32_t mt[624]; int mti; }` místo globálního stavu.
API: `init_genrand`, `init_by_array`, `genrand_int32`, makra `genrand_int31/real1/real2/real3/res53`.

Přítomno **identicky** v CFR+ i v ACPC serveru → sdílená RNG vrstva CPRG infrastruktury 2005–2015.
Nejstarší datovaný Burchův kódový artefakt, který byl nalezen.

**Vztah:** D · **First-party:** ANO (jmenná atribuce v hlavičce) · **Bit-exact:** ANO (standardní MT19937)

### Nález #7 — ACPC dealer seed pipeline

```
dealer.c:60    "usage: dealer matchName gameDefFile #Hands rngSeed p1name p2name ... [options]"
dealer.c:1139  if( sscanf( argv[ optind + 3 ], "%"SCNu32, &seed ) < 1 ) {
dealer.c:1145  init_genrand( &rng, seed );
dealer.c:1146  srandom( seed ); /* used for random port selection */
dealer.c:621   "# name/game/hands/seed %s %s %"PRIu32" %"PRIu32"\n..."
```

Seed je povinný poziční argument, jde do MT19937 a **zapisuje se do hlavičky match logu**.
Stejný dvojitý vzorec jako v CFR+ (MT19937 na karty + libc na infrastrukturu).

**Vztah:** D · **First-party:** ANO · **Bit-exact:** ANO

### Nález #14 — Burchův sampler pokerových situací (viz příloha A)

### ⭐ Nález #18 — Burchův podepsaný nepublikovaný technický komentář

`cfrd_v3/cfrd.tex:214-235`, mtime **2014-01-09 19:45**. Přítomno **pouze ve v3**
(v1 2013-03-18, v2 2013-03-30 ho nemají). Odpověď na `% TODO:` blok spoluautora:

```latex
% NB: Time estimate was from canonical game.  Using an estimate of 1
% second per subgame was something like 500 core years for a real game
% best response.  1 second might actually be reasonable, but we need
% to solve the subgame twice.  10,000 trunk iterations might be enough
% for a reasonable first attempt.  While solving, using roughly
% 1/100th the re-solve iterations has been okay.  500 core years * 2 *
% 10000 / 100 = 100,000 core years.  It certainly might be an
% underestimate, but it's enough that personally, I would be
% interested to see the result.
%
% I did not use the canonical chance events because I thought the
% numbers become much easier to verify, mostly for the size of the
% subgames for re-solving and CFR-D.  For the numbers now, I've used
% canonical groupings in the trunk, and non-canonical groupings in the
% subgames (49*48/2*turn_betting*47+49*48/2*river_betting*47*46).
% ((21*169+182*1286792)*3+(1176*28*47+1176*234*47*46)*2)*8/1024/1024/1024
%
% I agree that the time and space cases should match.  I was thinking
% (or possibly not thinking...) that the canonical indexing was a
% space-only issue, so it didn't matter. It's definitely also a
% time-required issue, which would affect the numbers.
```

Použitelný obsah:
1. **Iterační pravidlo:** re-solve : subgame-solve ≈ 100 : 1 (interpretace viz #25)
2. **Nákladová aritmetika:** 1 s/subgame, ×2 (subgame se řeší dvakrát), `500 × 2 × 10000/100 = 100 000 core years`
3. **Izomorfismová politika:** kanonická grupování v trunku, nekanonická v subgames

> **Cross-artifact shoda:** bod 3 je přesně politika implementovaná v CFR+ —
> `sortedCardsNumSuitMappings()` filtruje na kanonické třídy a nese `weight`.
> Dva nezávislé Burchovy artefakty, stejný způsob uvažování.

**Vztah:** D/E (genealogie) · **First-party:** ANO, doslovný Burch, nepublikováno · **Bit-exact:** NE

### Nález #25 — `% NB:` komentář je interpretovatelný

Ověření proti Burchovým vlastním publikovaným číslům ze stejného souboru
(`cfrd_v3/cfrd.tex:857-865`):

```
recovery (re-solve) iterations                    = 200 000
200 000 / 100                                     = 2 000
publikovaný rozsah subgame iterací během solvingu = 100 … 12 800
                                                    → 2 000 leží uvnitř
```

> Poměr 1/100 platí mezi **iteracemi subgame solvingu za běhu** a **iteracemi finálního
> re-solve/recovery** — ne mezi trunk a subgame. Aritmetika `500 × 2 × 10000/100` sedí.

Je to jediné dochované Burchovo kvantitativní pravidlo pro iterační rozpočet.

### Nález #22 — potlačený `\comment{}` blok v CFR-D

`cfrd_v3/cfrd.tex:24` definuje `\newcommand{\comment}[1]{}` (obsah se zahodí).
Věcné použití na `:845-855`:

> "While it would definitely be interesting to test CFR-D performance in a much larger game like
> limit Texas Hold'em, there is a serious issue with evaluation. […] can be a computation that
> requires on the order of **CPU-months** […] the evaluation is **completely beyond current
> computational resources**."

Burchovo vlastní odůvodnění, proč CFR-D neškáloval na HULHE — **výpočetní, ne algoritmické**.

### Nález #23 — CFR-D nemělo cluster funding

`cfrd_v3/cfrd.tex:1116` (potlačeno přes `\comment{}`):
```latex
\comment{\section{Acknowledgements}
This research was supported by the Natural Sciences and Engineering
Research Council (NSERC) and Alberta Innovates Technology Futures (AITF).}
```

Srovnej DeepStack `ds_v3/paper.tex:380`:
> "This work was only possible thanks to computing resources provided by Compute Canada and
> Calcul Québec."

> **Důsledek:** Burchův vztah k Compute Canada / Calcul Québec v lednu 2014 ještě neexistoval.
> Pátrání po jeho MP2 job artefaktech nemá smysl posouvat před ~2015.

### Nález #24 — Burchova hardwarová a experimentální konfigurace

`cfrd_v3/cfrd.tex:780`:
> "All timing results were generated on a **2.67GHz Intel Xeon X5650** based machine running **Linux**."

X5650 = 6-core Westmere-EP (2010). Konzistentní s `-xHost` v CFR+ Makefile a `threads=24` v README.

`cfrd_v3/cfrd.tex:857-890`:

| Parametr | Hodnota |
|---|---|
| Trunk iterations | 500 / 2 000 / 8 000 / 32 000 |
| Subgame iterations | 100 … 12 800 |
| Recovery game iterations | 200 000 (~0,8 s/subgame) |
| Nejlepší výsledek | 0,0075 chips/hand, ~114 min na **jednom** CPU jádru |
| Po 6 400 000 recovery iterací | 0,0028 chips/hand |
| Srovnání: plné CFR | 0,0028 chips/hand za 23 s |

---

## 5. P1 — CFR+ cluster manifest (cíl E, precursor)

`README:23-35` — doložený reálný běh Cephea:

```
mpiexec -n 200 ./cfr game=holdem.limit.2p.reverse_blinds.game split=2 threads=24 \
  scratch=/ltmp/yourname/ scratchpool=36 regretscaling=3,0.5 regretscaling=4,0.5 \
  avgscaling=3,1 avgscaling=4,1 mpi iters=2000 warmup=100 networkcopies=42 \
  maxtime=4:16:00:00 dump=/home/yourname/cfrplus_scratch/ \
  resume=/home/yourname/cfrplus_scratch/cfr.split-2.iter-1381.warm-100
```

200 nodes × 24 threads = **4 800 CPU** (publikováno pro Cepheus: „4800 CPUs, 68 days").
Checkpoint adresáře `cfr.split-2.iter-1381.warm-100`.
Makefile: `icc -Ofast -xHost -fp-model fast=2`, `mpicc -DUSE_MPI`, mpich2.

> **NENÍ to DeepStack 6 144-core běh na MP2.** Jiný počet jader, jiná hra, jiný účel.

---

## 6. P2 — genealogie a lokátory

| # | Nález | Detail |
|---|---|---|
| #3 | ACPC server / dealer | `github.com/jblespiau/project_acpc_server`, pristine kopie z oficiálních ACPC downloads, copyright CPRG 2011; Burch primární autor dealer stacku |
| #12 | Burchovo build prostředí | `docProps/custom.xml`: `PTEX.Fullbanner = "This is pdfTeX, Version 3.14159265-2.6-1.40.17 (TeX Live 2016/Cygwin) kpathsea version 6.2.2"`, `Created = 2017-12-17`, `Producer = pdfTeX`, `GTS_PDFA1Version = PDF/A-1b:2005` → thesis sázena na **Windows přes Cygwin**; TeX source existoval na jeho osobním stroji |
| #15 | Časové ohraničení DataGeneration | `thesis.txt:76-79`: ethics approval „Evaluating the skill of state-of-the-art computer poker agents", **No. 67663, October 24 2016**. S #23 → okno **2015 – Q3 2016** |
| #19 | `\NBTODO` v DeepStack preambuli | `ds_v{1,2,3}/paper.tex:21-23` definuje `\MBTODO` (blue), `\MJTODO` (orange), `\NBTODO` (green!40). Přesně tři autoři z deseti mají anotační makro. **Ale žádné volání `\NBTODO{...}` nepřežilo** — jen `\MBTODO` jednou (`appendix.tex:96` v v1/v2, ve v3 odstraněno). Definice makra je provisioning, **ne autorství komentáře** → DeepStack arXiv source **zůstává paper-level zdroj, ne Burchův artefakt** |
| #21 | Nepublikovaná nezaokrouhlená data | `ds_v1/appendix.tex:127-148` — zakomentovaná tabulka výsledků hráčů v plné přesnosti (`$1500.00386455556$` vs publikované `$1500$`), s metodickou poznámkou „Values rounded to nearest mbb, using /sqrt(n-1) and 2-sided t0.95 n-1 freedom". **Match data, ne training data → není to cíl C** |

### Burchovy identity a kód-hostingové účty (#4, #5, nález z 1. vlny)

| Identita | Zdroj | Verdikt |
|---|---|---|
| `github.com/neilburch-sony` | GitHub user search `fullname:"Neil Burch"` — 1 výsledek | Neil Burch (Sony AI), **0 public repos** |
| `github.com/NeilBurch` | commit search | 2 forky (`roshambo`, `open_spiel`), **žádný vlastní commit** v roshambo; Arctic Code Vault |
| `neil.burch` | `WeikangChen/hog2` commit `90176d4.patch` → `From: "neil.burch" <neil.burch@3e291e08-dd2d-0410-9de5-7df0620fb8d4>`, 2009-01-08 | git-svn UUID → HOG2 migrováno ze SVN. **Burch na UAlbertě pracoval v SVN, ne v gitu** |
| `nburch` v pokersource/poker-eval | `dooglus/pokereval` commit `a403e2c.patch`, 2006-04-14, `git-svn-id: http://svn.gna.org/svn/pokersource/trunk@998` | **IDENTITA NEPOTVRZENA** — stejný handle používá Nick Burch (Apache POI/Tika), jehož commity jsou ve stejném search resultu. Bez skutečné e-mailové adresy nerozlišitelné. **Neopírat o to nic** |

---

## 7. NEGATIVE — prohledáno, nic

| Zdroj | Výsledek |
|---|---|
| GitHub user search `fullname:"Neil Burch"` | 1 výsledek (prázdný účet) |
| GitHub repo search `"Neil Burch"` | **0 repozitářů** |
| GitHub commit search `author-name:"Neil Burch"` | 149 výsledků = duplikáty napříč forky HOG2 (2008-09, RoboticArm) a hanabi (2019-20, DeepMind). **Žádný poker/CFR/DeepStack commit** |
| GitHub commit search `author-name:"Neil Burch" poker OR cfr OR deepstack OR range OR data` | **0** |
| GitHub commit search `author-email:nburch@ualberta.ca` | **0** |
| GitLab project search: `deepstack`, `cfr_plus`, `cfrplus`, `acpc_server`, `computer poker`, `burch` | **NEGATIVE definitivně** |
| Bitbucket `users/{nburch,neilburch,burch}` | API pro username lookup zrušen → **unsearched, ne negative** |
| `godmoves/cfr_plus` forks | **0 forků** — nikdo Burchův CFR+ veřejně nerozšířil |
| CFR+ balík: `19950\|6144\|MP2\|qsub\|PBS\|potBins\|range_generator\|handStrength\|root_cfv\|generate_data\|torch\|\.t7` | **0 hitů** |
| Thesis: `DataGenerat`, `generate_data`, `range generator`, `rngseed`, `init_genrand`, `MT19937`, `qsub`, `PBS`, `Torch`, `19950`, `6144`, `Mammouth`, `Compute Canada`, `WestGrid`, `core-year`, `pot size`, `sampled board`, `worker`, `10,000,000`, `ten million` | **0** |
| Thesis: `MP2` (1), `Calcul` (2), `cluster` (1) | **všechno false positives**: `Mp2` matematický symbol (`:2082`), „to **calcul**ate" / „best response **calcul**ation" (`:2005`, `:5810`), „large **cluster**s of machines" (`:5631`) |
| AIVAT `vat.tex` v1 vs v2 | **byte-identické**; pouze 2 komentáře, oba boilerplate; **0 zmínek** o DeepStack / data generation / clusteru / seedu |
| CFR-D `proof_techreport` | `cfrd_v3:591-592` zakomentovaný `\cite{proof_techreport}`. **Není v žádném `.bbl`** → plán zrušen, důkazy vloženy inline. **Nikdy nevznikl, není to nedohledaný artefakt** |
| CFR-D `diff v1 v2` | 2 hunky, obojí přepis definice perfect recall. Nula změn v experimentální části, nula komentářů |

---

## 8. FAKTA vs HYPOTÉZY

### Fakta (ověřená z primárního zdroje, s odkazy na řádky)

1. Burch napsal modifikaci MT19937 datovanou 2005-09-07; je sdílená CFR+ i ACPC serverem.
2. CFR+ má `rngseed=` (default `1`) a `initstate_r( params->rngSeed ^ subgameIndex, buf, 32, state )`.
3. Ta konstrukce používá **glibc `random_r`, ne MT19937**, a slouží výhradně k samplování boardů.
4. MT19937 je v CFR+ **nedosažitelný mrtvý kód**.
5. CFR+ neobsahuje žádný data-generation, range-generation ani pot-size kód a **nemá CFV export**.
6. CFR+ je plně deterministický při daném `rngseed`.
7. Public CFR+ archiv byl exportován z SVN `trunk` se stripnutými SVN metadaty a vynechaným `cfr_player.c`.
8. `cfr_player.c` je (dle jediného efektu `PLAYER_OBJECT`) strategy-lookup hráč, ne generátor.
9. Burchova thesis zmiňuje dataset **jednou**, v preface; kapitola 6 ho neopakuje.
10. Thesis neobsahuje jedinou zmínku o clusteru, seedu, RNG ani parametrech generování dat pro DeepStack.
11. `[100, 100)` je v originálním LaTeXu ve všech třech arXiv verzích, včetně post-review v3.
12. Tie-breaking v R(S,p) byl mezi v2 a v3 opraven z ostré na neostrou nerovnost; zůstává nedourčený.
13. `omit_iters` je vlastnost online solveru (per-round); HUNL supplement popisuje offline generátor jako čisté CFR⁺ / 1 000 iterací. ⚠️ **Referenční Leduc implementace ale skip iterace v offline generování používá — viz L2.**
14. Burch má první podepsaný technický komentář (`% NB:`) v CFR-D v3, 2014-01-09.
15. CFR-D nemělo cluster funding; Compute Canada / Calcul Québec se objevuje až u DeepStacku.
16. Burch nemá veřejný git repozitář s pokerovým kódem; jeho UAlberta VCS byl SVN.

### Hypotézy — NEPROKÁZANÉ

- Chybějící DeepStack DataGenerator žil pravděpodobně v dlouhodobě udržovaném interním
  CPRG source/experimental frameworku, ne ve veřejném repozitáři jménem „DeepStack".
  Nálezy #1 (SVN trunk export), #6 (chybějící CFV export), #10 (chybějící CPRG bridge)
  a thesis §4.3.1 („validating results with an **independent codebase**", `thesis.txt:2598-2599`)
  tento směr podporují. **Nedokazují** ale reuse kódu, reuse RNG ani identitu repozitáře.

### NESMÍ SE ODVOZOVAT

- ~~DeepStack RNG == `rngSeed ^ subgameIndex`~~
- ~~DeepStack RNG == MT19937~~ (pro linii přes CFR+ **vyvráceno**, #9)
- ~~`[100,100)` se má tiše změnit na `[100,200)`~~ (#16 — zdroj to má takhle, oprava je vaše rozhodnutí, ne rekonstrukce)
- ~~online `omit_iters` platí pro offline generátor~~ (#20 — vyvráceno *pro text supplementu*; ⚠️ referenční implementace dělá opak, viz L2)
- ~~CFR+ solver options implikují offline DataGeneration options~~
- ~~DeepStack-Leduc nebo pozdější mirrory jsou HUNL oracle~~
- ~~`\NBTODO` definice dělá z DeepStack arXiv source Burchův artefakt~~ (#19)

---

## 9. Zbývající cíle, seřazené

Vše níže je z prostředí této analýzy **nedostupné** (viz 1.3) a vyžaduje jinou síť.

1. **Interní CPRG SVN** — `trunk`, branches, tags, `cfr_player.c`, independent validation codebase.
   Jediné místo, kde A/B/C/D/E reálně mohou existovat.
2. **Wayback CDX enumerace** `webdocs.cs.ualberta.ca/~burch/*` a `poker.cs.ualberta.ca/*`,
   filtr na `.tar.gz|.tar.bz2|.zip|.sh|.pbs|.job|.log|.t7`.
   *Pozor: správný prefix je `~burch`, ne `~nburch` — doloženo lokátorem
   `webdocs.cs.ualberta.ca/~burch/two_plus_two.html`.*
3. **Software Heritage** origin search na `nburch`, `burch`, `ualberta`, `pokersource`
   (archivuje smazané repo i SVN).
4. **GitHub code search s přihlášením** na `changes made on 2005/9/7 by Neil Burch` →
   najde všechny repozitáře nesoucí Burchův kód.
5. **ERA backend / original-deposit bitstream manifest** pro item
   `db44409f-b373-427d-be83-cace67d33c41` (PDF bitstream `bcb00dca-39e6-4c43-9ec2-65026a50135e`).
6. **Calcul Québec / Compute Canada** historická accounting/job metadata vázaná na Burche/CPRG 2015-2016.
7. **Přímý dotaz Burchovi** (`nburch@ualberta.ca`). Po šesti vlnách je formulovatelná otázka,
   na kterou umí odpovědět jednou větou:

   > Ve všech třech verzích DeepStack supplementu je pot bin `[100, 100)` a mezi v2 a v3 se
   > opravovalo tie-breaking v R(S,p) (`lower than` → `no greater than`). Co ten první bin
   > v implementaci skutečně dělal, a jak se rozdělovaly ruce se stejnou hand strength?
   > A byl generátor, který jsi psal, ten pro turn, flop, nebo aux síť?

---

## Příloha A — Burchův sampler pokerových situací, bit-exact

Jediný dochovaný kus first-party Burchova kódu, který náhodně vybírá pokerové situace.

### Krok 1 — enumerace kanonických boardů (`storage.c:865-885`)

```c
firstCardset( params->deckSize, numBoardCards, board, bc ); do {
  weight = sortedCardsNumSuitMappings( bc, numBoardCards, suitGroups, numSuits );
  if( !weight ) { continue; }                    /* nekanonický -> zahodit */
  tempBoards[ num ].board      = *board;
  tempBoards[ num ].suitGroups = updateSuitGroups( bc, numBoardCards, suitGroups, numSuits );
  tempBoards[ num ].weight     = weight;         /* int8_t, storage.h:34 */
  ++num;
} while( nextCardset( params->deckSize, numBoardCards, board, bc ) );
```

Enumeruje **suit-izomorfní třídy**, ne surové boardy. `weight` = počet suit mappingů třídy.

### Krok 2 — částečný Fisher–Yates (`storage.c:886-902`)

```c
if( params->numSampledBoards[ r ] && num > params->numSampledBoards[ r ] ) {
  int t;
  for( i = 0; i < params->numSampledBoards[ r ]; ++i ) {
    random_r( rngState, &t );
    t %= ( num - i );
    boards[ r ][ *idx + i ] = tempBoards[ i + t ];
    if( t ) { tempBoards[ i + t ] = tempBoards[ i ]; }
  }
  num = params->numSampledBoards[ r ];
}
```

### Krok 3 — počítací cesta se ořízne identicky (`storage.c:742-746`)

```c
/* cap count by random sample count */
if( params->numSampledBoards[ r ] && num > params->numSampledBoards[ r ] ) {
  num = params->numSampledBoards[ r ];
}
```

### Seedování (`storage.c:998-1002`, `cfr.h:14`)

```c
memset( &storage->rngState, 0, sizeof( storage->rngState ) );
initstate_r( params->rngSeed ^ subgameIndex,
             storage->rngBuf,
             RNG_STATELEN,          /* cfr.h:14  #define RNG_STATELEN 32 */
             &storage->rngState );
```

**`RNG_STATELEN 32` → glibc TYPE_1**, degree 7, separation 3, rekurence `x[i] = x[i-3] + x[i-7]`.
**Není to 128bajtový TYPE_3, který je glibc default.** Nedefaultní, paměťově úsporná volba
(`rngBuf[32]` sedí v každém `VanillaStorage`, `storage.h:101`, a těch jsou miliony).

> **Fingerprint:** kdyby se objevil DataGenerator s `initstate_r(seed, buf, 32, state)`,
> byla by to silná shoda idiomu.

### CLI (`args.c:51`, `:314-334`, `:54`, `:65`)

```
sampleboards=<round>,<num>   round 1-based → --r na 0-based; num < 0 → 0; default 0 = bez samplování
rngseed=<integer>            default 1; "TIME" → tv_sec*1000 + tv_usec/1000
```

### Reprodukční recept

```
seed_subgame = rngSeed ^ subgameIndex
initstate_r(seed_subgame, buf, 32, &state)        // glibc TYPE_1, deg 7, sep 3
for i in 0 .. numSampledBoards[r]-1:
    random_r(&state, &t)                          // t ∈ [0, 2^31-1]
    t %= (num - i)
    vybraný = tempBoards[i + t]
    if t: tempBoards[i + t] = tempBoards[i]
```

Pořadí volání `random_r` je dané rekurzí `setUpBoards` → `countBoardsOnRound` →
`setUpBoardsOnRound` přes kola `startRound..endRound`.
Indexace: `bettingIndexOfSubgame = subgameIndex % numBettingSubgames`,
`boardIndexOfSubgame = subgameIndex / numBettingSubgames` (`storage.h:180-181`).

### Dvě vlastnosti, které je nutné znát

1. **Váha se při samplování nerenormalizuje.** `tempBoards[i+t]` se kopíruje včetně `weight`.
   Normalizace probíhá až downstream v `cfr.c:1571-1581` a `:2396-2405` přes `weightSum`
   (součet vah skutečně přítomných boardů) a `params->boardFactor[round]` v `cfr.c:1648-1650`.
   Sampler vzorkuje **uniformně přes kanonické třídy**, korekci nechává na solveru.
2. **Modulo bias je přítomný.** `t %= (num - i)` na hodnotě z `[0, 2^31-1]`; pro `num` řádu tisíců
   je bias ~10⁻⁶ — zanedbatelný, ale **deterministický a nenulový**. Burch ho neřešil.

---

## Příloha B — Časová osa z tar mtime

| Datum | Soubor | Význam |
|---|---|---|
| 2005-09-07 | `rng.c` / `rng.h` (datum v komentáři) | nejstarší datovaný Burchův kód |
| 2013-02-07 | `subgame.pdf`, `recovery_game.pdf` | nejstarší CFR-D obrázky |
| 2013-03-18 / 03-30 | `cfrd.tex` v1 / v2 | bez Burchova komentáře |
| **2014-01-09 19:45** | `cfrd.tex` v3 | **`% NB:` blok vzniká zde** (#18) |
| **2014-11-18 20:29** | `CFR_plus.tar.bz2` | **zabaleno uživatelem `burch`** (#1) |
| 2016-10-24 | ethics approval No. 67663 | horní mez pro dokončení DataGeneration (#15) |
| 2016-12-14 02:58 | `scicite.sty`, `Science.bst` | DeepStack rukopis zakládán, 2 dny po konci human study |
| 2016-12-20 23:00 | `vat.tex` | AIVAT |
| 2017-01-06 14:26 | `appendix.tex` v1 | `[100,100)` + „lower hand strength than" |
| 2017-01-10 02:29 | `appendix.tex` v2 | obsahově beze změny |
| **2017-02-13 04:40** | `appendix.tex` v3 | **tie-breaking oprava**; `[100,100)` ponecháno (#16, #17) |
| 2017-03-03 14:30 | `paper.tex` v3 | finální arXiv verze |
| 2017-12-17 | thesis PDF | pdfTeX / TeX Live 2016 / **Cygwin** (#12) |

---

## Příloha D — Vlna 7: cluster artefakty a interní repozitář

Nové zdroje: originální `project_acpc_server_v1.0.42.tar.bz2`, `vs_LBR.zip`,
`DeepStack_vs_IFP_pros.zip`, arXiv 1303.4441 **v4**, arXiv 1810.11542 v1/v2 (JAIR, Burch 1. autor),
NIPS 2012 supplemental.

### ⭐ Nález #29 (P0) — interní CPRG repozitář má JMÉNO: `project_uoapoker`

Ve více než 400 hlavičkách LBR logů (`vs_LBR/hyperborean14/*.out`, `full_cards/*.out`):

```
Player args: /home/viliam/cprg/project_uoapoker/trunk/src/c/meta_player.so \
             /home/viliam/cprg/project_uoapoker/trunk/src/c/acpc14.map
```

Layout `project_uoapoker/trunk/src/c/` odpovídá `Makefile:45-46` v CFR+ (`cp -r trunk/*`,
`--exclude=*svn*`).

> Cíl č. 1 ze seznamu zbývajících cílů (§9) má nyní **konkrétní jméno a cestu**.
> **Atribuce:** `/home/viliam/` je home adresář Viliama Lisého (autor LBR), ne Burchův.
> Repozitář `project_uoapoker` je ale CPRG-wide, a je to tentýž `trunk`, ze kterého Burch
> exportoval CFR+. Nezaměňovat operátora běhu s vlastníkem repozitáře.

### ⭐ Nález #30 (P0) — první skutečné MP2 cluster artefakty: PBS job ID + alokace seedů

400 souborů ve tvaru `lbr_<betting>_Hyp14_<r|s><SEED>_<JOBID>.mp2.m.out`.

`vs_LBR/README.txt`:
> "In all file names the **sSEED or rSEED indicate the SEED used for generating cards** where
> the 'r' or 's' indicate the side of the cards played by the player."

A každý log to potvrzuje ve své hlavičce: `Using seed 22.` ↔ soubor `..._s22_288772.mp2.m.out`.

| Betting setting | Seedy | Job ID rozsah | Jobů | Seedů/job |
|---|---|---|---|---|
| `fcpa` | 0–49 (50) | 288761–288785 | 25 | 2 |
| `56bets` | 0–49 (50) | 291695–291719 | 25 | 2 |
| `fc4` | 0–49 (50) | 295063–295087 | 25 | 2 |
| `2r56bets` | 0–49 (50) | 502916–502940 | 25 | 2 |

Odvozené pravidlo: `jobid = base + ⌊seed / 2⌋`, tedy **2 seedy × 2 strany = 4 zápasy na job**,
25 sekvenčních `qsub` jobů na nastavení. Job ID jsou prostá sekvenční čísla (ne `NNN[i]`),
takže **nešlo o PBS job array**, ale o 25 samostatných submitů.

**Alokace seedů: 0…49 sekvenčně — prostý index workeru.** Žádný hash, žádný XOR, žádné
`seed ^ jobid`.

> **Vztah k A–E:** je to **E-třídní materiál z téhož clusteru** (Calcul Québec MP2), jaký použil
> turn dataset. **ALE je to LBR evaluace, ne generování dat.** Nesmí se zaměňovat.
> Hodnota: ukazuje, jaký seed/job idiom tým na MP2 skutečně používal.

### Nález #31 (P1) — DeepStack běhy přes MP2 nešly

Soubory v `deepstack/` a `full_cards/` **nemají** `_<jobid>.mp2.m` sufix a seedy jsou
**1-based** (1…10, 1…20, 1…30), ne 0-based.

> Dvě různé konvence seedů v jednom projektu: **0-based pro CPU běhy na MP2**,
> **1-based pro lokální GPU běhy**. DeepStack potřeboval GPU, MP2 je CPU cluster.

### Nález #32 (P1) — `.so` plugin architektura potvrzuje nález #10

Hlavičky logů:
```
Loading player: rgbr_nl_cprg.so
Player args: .../meta_player.so  .../acpc14.map
Player args: translation_player.so  translation_player.args.CFRplus_holdem_nolimit_FCPA
```

Tentýž vzorec jako `cfr_player.so` v CFR+ Makefile (`-shared -Wl,--export-dynamic`).

> Potvrzuje #10: `cfr_player.c` byl **plugin hráče** pro tuto evaluační harness, ne generátor.

### Nález #33 (P1) — existoval interní NO-LIMIT CFR+

`translation_player.args.**CFRplus_holdem_nolimit_FCPA**` — agent „Full Cards" (thesis Table 6.1,
~2 TB, ~14 CPU-let) byl vyroben **no-limit CFR+**.

Veřejný Burchův CFR+ release je v praxi limit-only (`holdem.limit.2p.reverse_blinds.game`),
byť `game.c` `bettingType` no-limit zná.

> **Nejsilnější nová stopa:** v `project_uoapoker/trunk` existovala **no-limit varianta CFR+**.
> To je nejbližší známý příbuzný solveru z doby DeepStacku. Hypotéza, nikoli důkaz o DataGeneratoru.

### Nález #28 (P0) — Burchův `rng.c` je byte-identický napříč dvěma nezávislými releasy

| Zdroj | tar owner | zabaleno | `rng.c` mtime |
|---|---|---|---|
| `CFR_plus.tar.bz2` | `burch/burch` | 2014-11-18 20:29 | — |
| `project_acpc_server_v1.0.42` | `aaaicpc/pg227652` | 2017-07-28 22:03 | 2013-01-26 00:07 |

```
0e4a4d7ac3d310500f1dbd40e5d0d268d31d1dfecf5183314b99abf3aa646661  rng.c   (obojí)
d16535446b4ce8e360f0125b0124a1e7a1c02abaf0b333460be24142db5b0f17  rng.h   (obojí)
4352b66e17678c63218766303707d38e8dc5f9275c1e95ed1df60469e38f6796  dealer.c (originál == jblespiau mirror)
```

> Burchův MT19937 je **zmrazená, neměnná CPRG-wide komponenta**, distribuovaná dvěma nezávislými
> kanály. Mirror `jblespiau/project_acpc_server` je věrný. **Bit-exact: ANO.**

### Nález #34 (P2) — sada `56bets` plně rekonstruována

Z hlaviček logů: `F, C,` pak 56 potových zlomků `0.05 × 1.15^k` pro k = 0…55
(0.05, 0.0575, 0.066125, … 82.40537557, 94.76618191), pak `A`.
Geometrická řada s kvocientem **1.15**.

### Nález #35 (P2) — nezávislé ověření Burchova veřejného tvrzení

`DeepStack_vs_IFP_pros/DeepStack_logs/ACPC/*.log`: **90 074** časově razítkovaných `STATE:` záznamů
= **45 037 rukou × 2**. Přesně odpovídá Burchovu veřejnému vyjádření z 2017-03-04, že napočítal
45 037 rukou (ledger v2, položka P2/P3).

Časové okno z unixových razítek: **2016-11-07 12:03:43 UTC → 2016-12-16 22:49:21 UTC**.

### Nález #36 (P3) — CFR-D v4 odstranil `% NB:` blok

`cfrd.tex` v4 (2014-04-21, 49 541 B) vs v3 (2014-01-09, 61 154 B): 1 427 změněných řádků,
Burchův komentářový blok **pryč**.

> **Provenance:** `% NB:` komentář (#18) existuje **výhradně v arXiv v3** 1303.4441.
> Kdo pracuje jen s v4 nebo s publikovanou verzí, nedostane ho.

### NEGATIVE — vlna 7

| Zdroj | Výsledek |
|---|---|
| arXiv **1810.11542** v1/v2 (`burch19a.tex`, „Revisiting CFR⁺ and Alternating Updates", JAIR, **Burch 1. autor**, e-mail `burchn@google.com`) | v1 má **1** boilerplate komentář, v2 **nula**. Žádné seedy, cluster, implementační infrastruktura. v1→v2 = 542 řádků, čistě editorial/teoretické. **NEGATIVE** |
| NIPS 2012 supplemental (Gibson, **Burch**, Lanctot, Szafron) | jediný soubor `appendix.pdf`, **žádný kód**. **NEGATIVE** |
| `DeepStack_vs_IFP_pros` ACPC logy | **žádné `# name/game/hands/seed` hlavičky** — human study se rozdávala živě přes web, ne ACPC dealerem. Match data, ne training data → **není to cíl C** |
| `project_acpc_server` v1.0.42 — hledání data-generation | nic nad rámec už známého dealer/game/rng stacku |

### Dopad vlny 7 na stav A–E

| Cíl | Před vlnou 7 | Po vlně 7 |
|---|---|---|
| **A** | NOT FOUND | beze změny |
| **B** | NOT FOUND | beze změny; #33 přidává stopu na interní no-limit CFR+ |
| **C** | NOT FOUND | beze změny (IFP data jsou match, ne training) |
| **D** | NOT FOUND | **první doložené reálné seedy týmu na MP2**: 0…49 sekvenčně, prostý index workeru (#30). Pro LBR evaluaci, ne pro DataGeneration |
| **E** | NOT FOUND | **první skutečné MP2 cluster artefakty** (#30): 25 `qsub` jobů/nastavení, 2 seedy/job, sekvenční job ID. Pro LBR evaluaci, ne pro DataGeneration |

### Aktualizace §9 — zbývající cíle

Cíl č. 1 se zpřesňuje na:

> **`project_uoapoker` — interní CPRG SVN repozitář, layout `trunk/src/c/`.**
> Obsahuje (doloženo z cest a názvů artefaktů): `meta_player.so`, `rgbr_nl_cprg.so`,
> `translation_player.so`, `acpc14.map`, `cfr_player.c`, a **no-limit CFR+ variantu**
> (`CFRplus_holdem_nolimit_FCPA`). Toto je jediné místo, kde A/B/C/D/E reálně mohou být.

---

## Příloha E — Vlna 8: reprodukce publikované LBR tabulky z raw dat

Archiv `vs_LBR.zip` obsahuje kromě 628 logů i **agregační skript týmu** — `vs_LBR/aggregate3.sh`
(406 B, mtime 2017-02-09). To umožnilo publikovaná čísla nezávisle přepočítat.

### ⭐ Nález #37 (P0) — celá publikovaná LBR tabulka se reprodukuje z uvolněných dat

Spuštěn původní `aggregate3.sh` (párování `_s`/`_r` = duplicate poker, průměr dvojice,
pak `mean ± 1.96·SE`) nad raw logy. Převod jednotek ověřen: **×10** pro hru se stackem
20 000 / BB 100, **×500** pro `full_cards` (stack 100 BB / BB 2).

| Agent | Setting | Přepočet z raw | Publikováno (`tab-localbr`) | Shoda |
|---|---|---|---|---|
| Hyperborean 2014 | `fc4` | 720.58 ± 55.53 | 721 ± 56 | ✓ |
| Hyperborean 2014 | `fcpa` | 3851.51 ± 140.77 | 3852 ± 141 | ✓ |
| Hyperborean 2014 | `56bets` | 4675.29 ± 152.36 | 4675 ± 152 | ✓ |
| Hyperborean 2014 | `2r56bets` | 983.37 ± 94.95 | 983 ± 95 | ✓ |
| DeepStack | `fc4` | −427.77 ± 87.21 | −428 ± 87 | ✓ |
| DeepStack | `fcpa` | −382.89 ± 219.12 | −383 ± 219 | ✓ |
| DeepStack | `56bets` | −775.17 ± 255.40 | −775 ± 255 | ✓ |
| DeepStack | `2r56bets` | −602.08 ± 214.79 | −602 ± 214 | ~ (viz #39) |
| Full Cards [100BB] | `fc4` | −424.00 ± 37.00 | −424 ± 37 | ✓ |
| Full Cards [100BB] | `fcpa` | −536.00 ± 87.00 | −536 ± 87 | ✓ |
| Full Cards [100BB] | `56bets` | 2402.50 ± 86.50 | 2403 ± 87 | ✓ |
| Full Cards [100BB] | `2r56bets` | 1008.00 ± 68.00 | 1008 ± 68 | ✓ |
| DeepStack | `dsMORE` | −405.86 ± 218.13 | −406 ± 218 (Table „first level actions") | ✓ |

> **Toto je první bit-reprodukovatelná verifikace publikovaného DeepStack výsledku v celém huntu.**
> Uvolněná primární data jsou úplná a autentická; metodika agregace je přesně ta publikovaná.

### ⭐ Nález #38 (P0) — uvolněný archiv obsahuje VÍC dat, než bylo publikováno

Varianta `dsFCPA` má v archivu **30 seedů**, ale publikovaná hodnota odpovídá **seedům 1–20**:

| Podmnožina | N | Přepočet ×10 | Publikováno |
|---|---|---|---|
| seedy 1–10 | 5 000 | −507.25 ± 292.88 | — |
| **seedy 1–20** | **10 000** | **−478.69 ± 215.99** | **−479 ± 216** ✓ |
| seedy 1–30 (vše) | 15 000 | −467.19 ± 178.76 | — |

> Shoda na desetinu mbb potvrzuje, že paper použil prvních 20 seedů. Archiv obsahuje
> **10 seedů navíc**, dogenerovaných po odeslání. Užší CI (178.76 vs 216) znamená, že
> plná data dávají o něco **méně** záporný odhad než publikovaná hodnota.

### Nález #39 (P2) — jediná nesrovnalost v celé tabulce

`DeepStack / 2r56bets`: střední hodnota sedí přesně (−602.08 → −602), ale **CI vychází 214.79,
publikováno 214** — zaokrouhlení nahoru by dalo 215. Ostatních 12 buněk sedí na zaokrouhlení
bez výjimky.

Kontext: v arXiv **v2** byla tato buňka v zakomentované tabulce ještě
`-615 $\pm$ 210`; ve v3 je `-602 $\pm$ 214`. Cela tedy byla mezi verzemi přepočítána.
Rozdíl 0,79 mbb je pravděpodobně stopa po mírně jiném datovém řezu, ne chyba.
**Zaznamenáno jako pozorování, ne jako obvinění.**

### Nález #40 (P1) — formát RESULTS footeru a rozsahy zápasů

```
RAW BR STATS: n=1000, sum=371187.000000, sum_sq=10898118463.000000,
              vr_sum=331003.806414, vr_sum_sq=7810334116.799194
BR STATS: 371.187000(203.314823), 331.003806(171.997908)
RESULTS
1)Player: -371187
2)BR: 371187
```

Distribuce délek souborů → rozsahy zápasů:

| Řádků | Souborů | Zápas | Kdo |
|---|---|---|---|
| 50 013 | 8 | **50 000 rukou** | `full_cards` (levný table lookup) |
| 1 013 | 400 | 1 000 rukou | Hyperborean14 na MP2 |
| 1 011 | 32 | 1 000 rukou | `deepstack` (fc4, fcpa seedy 5–10) |
| 1 006 | 8 | 1 000 rukou, **bez RESULTS footeru** | `lbr_fcpa_ds_{r,s}{1..4}` |
| 511 | 180 | 500 rukou | `deepstack` (drahé settingy) |

### Nález #41 (P3) — osm běhů bez RESULTS footeru

`deepstack/lbr_fcpa_ds_{r,s}{1,2,3,4}.out` — přesně 1 006 řádků, 1 000 rukou, ale **chybí
`RAW BR STATS` / `BR STATS` / `RESULTS` blok**, který mají ostatní. Seedy 5–10 téhož nastavení
footer mají (1 011 řádků).

> Prvních 8 běhů `fcpa_ds` proběhlo jinou verzí harness nebo bylo useknuto. Agregační skript
> footer nepoužívá (čte jen řádky rukou), takže to výsledky neovlivnilo — což reprodukce #37
> potvrzuje.

### NEGATIVE — vlna 8

| Cíl | Výsledek |
|---|---|
| `project_uoapoker` / `uoapoker` / `rgbr_nl_cprg` — WebSearch | **žádná veřejná stopa** |
| `project_uoapoker` — GitHub code search | vyžaduje přihlášení, z tohoto prostředí nedostupné → **unsearched** |
| LBR logy — hledání dalších cest, hostnames, PBS proměnných, verzí, chybových výpisů | mimo `/home/viliam/cprg/project_uoapoker/trunk/src/c/` (400×) a tři `.so` **nic dalšího** |

---

## Příloha F — Vlna 9: CPRG schéma odvození seedů (master → worker)

### ⭐⭐ Nález #42 (P0, cíl D) — kanonické CPRG odvození per-match seedů z master seedu

Nalezeno v `project_acpc_server/bm_server.c` (benchmark server, copyright CPRG 2011),
dosud neanalyzovaném souboru originálního ACPC balíku.

**Deklarace** — `bm_server.c:103-106`:
```c
  rng_state_t rng;
  uint32_t rngSeed;
  int useRngForSeed; /* 0: use rngSeed as seed for each dealer run
			1: use genrand_int32( match->rng ) */
```

**Inicializace** — `bm_server.c:775-789`:
```c
  match->rngSeed = rngSeed;
  if( rngSeed ) {
    init_genrand( &match->rng, rngSeed );
    if( match->numRuns == 1 ) {
      match->useRngForSeed = 0;
    } else {
      match->useRngForSeed = 1;
    }
  } else {
    init_genrand( &match->rng, genrand_int32( &serv->rng ) );
  }
```

**Odvození seedu pro každý běh dealera** — `bm_server.c:1356-1359`:
```c
  job = runMatchJob( conf, serv, best,
		     bestMatch->useRngForSeed
		     ? genrand_int32( &bestMatch->rng )
		     : bestMatch->rngSeed );
```

**Master seed serveru** — `bm_server.c:1399`: `init_genrand( &serv->rng, time( NULL ) );`

**Předání dealeru** — `bm_server.c:1016`: `snprintf( rngString, ..., "%"PRIu32, rngSeed )`
→ pozičně do `dealer.c:1139` → `init_genrand( &rng, seed )` → `dealCard()`.

**Dokumentace v `bm_run_matches.c:53-60`:**
> "`<seed>` is a seed used to **generate the random seeds** that determine the cards in each match"
>
> "To run N duplicate heads-up matches, do one run of N matches with a given seed, then run
> a second set of N matches with the **same seed but the order of the players reversed**"

### Rekonstruovaný řetěz

```
serv->rng     ← init_genrand( time(NULL) )                     // nedeterministický fallback
match->rng    ← init_genrand( rngSeed )                        // uživatelský master seed
                nebo init_genrand( genrand_int32(&serv->rng) ) // když rngSeed == 0

useRngForSeed = (numRuns == 1) ? 0 : 1

seed_běhu     = useRngForSeed ? genrand_int32( &match->rng )    // TAH Z MT19937 STREAMU
                              : match->rngSeed                 // konstanta (duplicate režim)

→ dealer argv[optind+3] → init_genrand( &rng, seed ) → dealCard()
```

> **Odpověď na otázku „CPRG worker seed allocation":** je to **postupný tah z MT19937 streamu**
> seedovaného master seedem — **ne** `seed ^ index`, **ne** `seed + index`, **ne** sekvenční index.
>
> Režim `useRngForSeed == 0` (jeden běh) dává duplicate poker: tentýž seed, prohozená sedadla —
> **přesně vzorec `_s`/`_r` v LBR lozích (#30)**.

### Tři doložené CPRG seed idiomy — úplný výčet z primárních zdrojů

| # | Idiom | Kde | RNG | Účel |
|---|---|---|---|---|
| 1 | `rngSeed ^ subgameIndex` | `CFR_plus/storage.c:1001` | glibc `random_r`, `RNG_STATELEN 32` (TYPE_1) | vzorkování boardů per subgame |
| 2 | `genrand_int32( &match->rng )` z master streamu | `project_acpc_server/bm_server.c:1358` | MT19937 (Burchův `rng.c`) | seed per zápas |
| 3 | prostý sekvenční index 0…49 předaný přímo | `vs_LBR/*.out`, MP2 | MT19937 v dealeru | LBR evaluace, submit smyčka |

> **Tohle je uzavřený výčet.** Prostor Burchových/CPRG seedovacích idiomů je nyní vytěžen
> z primárních zdrojů a každý je bit-exactly specifikovaný.
> **Žádný z nich není prokázán pro DeepStack DataGenerator** — ale otázka se posunula
> z „nevíme" na „je to jeden z těchto tří, a tady je každý přesně".

### Nález #43 (NEGATIVE) — IFP PokerStars logy neobsahují interní data DeepStacku

`DeepStack_logs/PokerStars/{full_info,DeepStack_view,participant_view}` + `ACPC/` —
pouze přeformátovaná historie rukou. **Žádné ranges, žádné counterfactual values,
žádné seedy.** README potvrzuje, že PokerStars formát je syntetický převod, čísla rukou
generovaná 1…N.

Potvrzena konfigurace hry: stack **$20 000**, blindy **$50/$100** — souhlasí s thesis §6.1.1
(„HUNL with 20 000 chip stacks with a 100 chip big blind").

> **Není to cíl C.** Human study data neobsahují nic z trénovacího řetězce.

---

## Příloha G — Vlna 10: exekuční test Burchova RNG řetězce proti reálným datům

LBR logy obsahují **skutečné karty rozdané se známým seedem** na MP2. To umožnilo poprvé
v celém huntu spustit rekonstrukci Burchova RNG a porovnat ji s produkčními daty.

### Nález #44a (P1) — stejný seed dává identické karty napříč nastaveními

| Seed | `fcpa` | `56bets` | `fc4` | `2r56bets` |
|---|---|---|---|---|
| 0 | `2s4d,2h5h\|/7sThQc/2c/As` | `…/7sThQc/2c` | `…/7sThQc/2c/As` | `…/7sThQc` |
| 22 | `JcQs,6hTd\|/4c5sQd/Ks/Kh` | `…/4c5sQd/Ks` | `…/4c5sQd/Ks/Kh` | `…/4c5sQd/Ks` |

Karty jsou identické, liší se jen kolik jich betting stihl odhalit.

> Potvrzuje: karty se předrozdají ze seedu **před** hrou a nezávisí na betting konfiguraci —
> stejná struktura jako `dealCards()` v `game.c:656-690`.

### ⭐ Nález #44b (P0, NEGATIVNÍ) — uvolněný kód tyto karty nereprodukuje

Implementoval jsem Burchův řetěz přesně podle zdroje — `rng.c:57` `init_genrand`,
`rng.c:106` `genrand_int32`, `game.c:644-654` `dealCard`, `game.c:656-690` `dealCards`,
`game.h:251` `makeCard(r,s) = r*MAX_SUITS+s`, `game.c:103-104` `suitChars="cdhs"`,
`rankChars="23456789TJQKA"` — a spustil proti seedům 0 a 22.

```
seed  0   očekáváno  2s4d,2h5h|/7sThQc/2c/As
          spočteno   5d5c,9hQd|/8dAs8s/4h/6d      NESHODA
seed 22   očekáváno  JcQs,6hTd|/4c5sQd/Ks/Kh
          spočteno   Ad6s,9s2c|/6c4cTh/3c/Ac      NESHODA
```

Následně otestováno **372 kombinací** napříč všemi rozměry, které uvolněný kód a jeho
přirozené varianty připouštějí:

| Rozměr | Testované hodnoty |
|---|---|
| RNG rodina | Burchův MT19937; glibc `srandom/random`; glibc `initstate_r/random_r` se stavem 8/32/64/128/256 B |
| Stavba balíčku | `s` vnější / `r` vnější |
| Kódování karty | `r*4+s` / `s*13+r` |
| Redukce tahu | `% n`, `genrand_int31`, `real2 × n` |
| Politika výběru | ACPC `deck[i]=deck[n-1]` / skutečný swap |
| Pořadí rozdání | blokové (p0p0 p1p1), střídavé (p0 p1 p0 p1), board první |
| Offset streamu | 0, 1, 2 tahy |
| Režim | inkrementální rozdávání / plné promíchání 52 karet |

**Shod: 0.**

> **PŘÍMÝ NEGATIVNÍ DŮKAZ:** generátor karet, kterým tým na MP2 vyráběl LBR zápasy,
> **není žádnou cestou přes uvolněný CPRG kód**. Žije v neuvolněném stromě
> `project_uoapoker/trunk/src/c/` (#29), spolu s `rgbr_nl_cprg.so`.
>
> Test není vyčerpávající přes všechny myslitelné implementace — je vyčerpávající přes
> **uvolněné kódové cesty a jejich přirozené varianty**. To stačí k závěru.

### Proč je to důležité pro cíl D a pro váš DataGenerator

Máme tu doložený případ, kdy jsou známy **všechny** vstupy, které by měly stačit:

- seed (0…49, vytištěný v logu i v názvu souboru),
- herní definice (stack 20 000, blindy 100/50, 4 kola, 2 hole karty, board 0/3/1/1),
- Burchův RNG zdrojový kód,
- reálný výstup k porovnání,

**a přesto data reprodukovat nelze.**

> **Závěr přenositelný na DataGenerator:** i kdyby se našel původní `rngseed` DeepStack
> DataGeneratoru, **sám o sobě by k bit-exact rekonstrukci nestačil**. CPRG kód z té doby
> obsahuje generátory, které nejsou odvoditelné z veřejných releasů.
> „Známe seed" ≠ „umíme reprodukovat data" — a tady je to dokázáno experimentem, ne argumentem.

Skript je v `docs/` neuložen (běžel v scratchpadu); reprodukovatelný z popisu výše.

---

## Příloha H — Vlna 11: hand evaluator, `game.c` diff a CPRG identifikátory

### ⭐ Nález #45 (P1, relevantní k cíli A) — CPRG hand evaluator a prostor síly ruky

`game.c` existuje ve dvou verzích. Diff ACPC (39 850 B, mtime 2013-08-01) vs CFR+ (42 898 B)
= 212 řádků a odhaluje, co Burch pro solver přidal:

**1. `rankCardset()`** — kompletní 7-card evaluator, `cfrplus/game.c:107-224`. V ACPC verzi
**chybí**. Používá tabulky `oneSuitVal[8192]`, `anySuitVal[8192]`, `topBit[8192]`,
`quadsVal[13]`, `tripsVal[13]`, `pairsVal[13]`, `twoPairOtherVal[13]`, `tripsOtherVal[8192]`,
`pairOtherVal[8192]`.

**2. Parametrizace kódování karty:** `makeCard(r,s)` → `makeCard(r,s,game->numSuits)`,
totéž `rankOfCard`/`suitOfCard`. ACPC verze má natvrdo `MAX_SUITS`, CFR+ podle hry
(kvůli Leduc/Kuhn/Rhode Island/royal). **Pro plný holdem jsou identické** (numSuits = 4).

**Prostor síly ruky** — z hlavičky `evalHandTables`:

| Třída | Počet | Offset |
|---|---|---|
| high card | 1 287 | 0 |
| pair | 3 718 | 1 287 |
| two pair | 3 601 | 5 005 |
| trips | 1 014 | 8 606 |
| straight | 13 | 9 620 |
| flush | 1 287 | 9 633 |
| full house | 1 014 | 10 920 |
| quads | 169 | 11 934 |
| straight flush | 13 | 12 103 |

Celkem **12 116 rozlišitelných hodnot ruky**; `rankCardset()` vrací hodnotu v `[0, 12116)`.
Konstanty `HANDCLASS_SINGLE_CARD 0`, `HANDCLASS_PAIR 1287`, `HANDCLASS_TWO_PAIR 5005`,
`HANDCLASS_TRIPS 8606`, `HANDCLASS_STRAIGHT 9620`, `HANDCLASS_FLUSH 9633`,
`HANDCLASS_FULL_HOUSE 10920`.

> **Vztah k cíli A:** DeepStack range generator R(S,p) dělí ruce podle *hand strength*
> („probability of a hand beating a uniformly selected random hand from the current public
> state"). Kdyby ho psal Burch, primitivem by byl **tenhle** evaluator — je to jediný
> hand-strength stroj, který ve svém uvolněném kódu má.
> **Není to důkaz**, že ho DataGenerator použil. Je to jediný doložený kandidát.

### Nález #46 (P2) — Burchův CPRG username a konvence home adresářů

`bm_server.config` (v tarballu od 2012-02-16), poslední řádek:
```
# Users authorized to run jobs on the benchmark (user name pass)
user neil test
```

Kombinace s cestami z LBR logů (`/home/viliam/cprg/project_uoapoker/trunk/...`, #29) ukazuje,
že **CPRG home adresáře používaly křestní jména**.

| Identifikátor | Kontext |
|---|---|
| `neil` | benchmark server login (`bm_server.config`) |
| `burch` | UNIX owner tarballu `CFR_plus.tar.bz2` |
| `viliam` | home adresář v LBR cestách |
| `aaaicpc` (uid **10424679**, gid `pg227652` = **26238**) | účet, který balil ACPC v1.0.42 |

> **Oprava směru pátrání:** pro `project_uoapoker` je pravděpodobná historická cesta
> `/home/neil/cprg/project_uoapoker/trunk/…`, ne `/home/nburch/` ani `/home/burch/`.
> Pro webové home adresáře zůstává doložený prefix `~burch` (ledger v2).

### Nález #47 (P2) — provozní parametry CPRG benchmark serveru

`bm_server.config`, plná konfigurace:

| Parametr | Hodnota |
|---|---|
| `port` | 54000 |
| `startupTimeoutSecs` | 100 |
| `responseTimeoutSecs` | 600 |
| `handTimeoutSecs` | 21000 |
| `avgHandTimeSecs` | **7** |
| `maxMatchRuns` | 10 |
| `maxRunningJobs` | 1 |
| `matchHands` | **5000** |
| Hry | `holdem.limit.2p.reverse_blinds`, `holdem.nolimit.2p.reverse_blinds`, `holdem.limit.3p` |

> `matchHands 5000` a `avgHandTimeSecs 7` jsou reálné ACPC provozní hodnoty. Pro srovnání:
> LBR běhy na MP2 měly 1 000 rukou/zápas, `full_cards` 50 000 (#40).

### Nález #48 (P3) — `evalHandTables` má dvě generace

| Balík | Velikost | SHA256 |
|---|---|---|
| ACPC v1.0.42 | 217 644 B | `9b8bb8e1c73503d55073757d0434380a69c40431713448c3d578f1a8dca7c3e4` |
| CFR+ | 214 384 B | `53248e54bafb8fbc67830230baf4ad92abaf1e95425c0326e14e7e7a82ef8425` |

**Nejsou identické.** ACPC verze začíná komentářem s offsety tříd a obsahuje navíc
`bySuit[]`; CFR+ verze začíná rovnou `static const uint16_t oneSuitVal[8192]` a přidává
`topBit[8192]`, `tripsOtherVal[8192]`, `twoPairOtherVal[13]`.

> Na rozdíl od `rng.c`/`rng.h` (#28, byte-identické napříč balíky) je **hand evaluator
> ve dvou generacích**. Kdo staví Burch-faithful hand strength, musí vybrat správnou —
> pro solver/CFR+ linii je to CFR+ verze.

---

## Příloha I — Vlna 12: úplný průchod, `card_tools.c` a mechanismus nereprodukovatelnosti R(S,p)

Prošlo se **všech 65** lokálních zdrojových/textových souborů. Plošný sken fingerprintů
(`DataGenerat`, `range_generat`, `hand_strength`, `root_cfv`, `19950`, `6144`, `MP2`, `qsub`,
`#PBS`, `walltime`, `ppn=`, `uoapoker`, …) vrátil jen zásahy v už analyzovaných souborech
plus tři false positives: `qsub` = LaTeX `\sqsubset`, `inputs`/`mask` = komentář k hash funkci
v `util.c:241-433`, `random` ve `validate_submission.pl:509` = prozaická zmínka.

### ⭐⭐ Nález #49 (P0, cíl A) — `getHandList()` a mechanismus, proč R(S,p) nelze bit-exact zrekonstruovat

`card_tools.h` definuje strukturu, kterou range generator přesně potřebuje:

```c
typedef struct {
  int rawIndex;      /* ( card[0] * deckSize + card[1] ) * deckSize ... */
  int canonIndex;    /* raw index of canonical version of hand */
  int rank;
  int8_t weight;
  uint8_t cards[ MAX_HOLE_CARDS ];
} Hand;
```

`card_tools.c:117-171` `getHandList()` — *„given the current board cards, generate all possible
hole cards, **sorts the hands by rank**"*:

1. enumeruje všechny hole-card kombinace přes `firstCardset`/`nextCardset`
2. `rank = rankCardset( hand )` — síla ruky v `[0, 12116)` (#45)
3. `weight = sortedCardsNumSuitMappings(...)` — suit-izomorfní násobnost, `0` = nekanonická
4. `canonIndex` z `cardsToCanonicalCards(...)`
5. **`qsort( hands, numHands, sizeof( hands[0] ), compareHandByRank )`**

A komparátor — `card_tools.c:112-115`:
```c
static int compareHandByRank( const void *a, const void *b )
{
  return ( (Hand *)a )->rank - ( (Hand *)b )->rank;
}
```

**Čistý rozdíl ranků. Žádné sekundární kritérium, žádný tie-break.**

#### Proč to uzavírá nález #17

DeepStack R(S,p) dělí `S` na `S₁`, `S₂` s `|S₁| = ⌊|S|/2⌋` tak, aby ruce v `S₁` měly
*hand strength no greater than* ruce v `S₂` (#17). Při remízách řez **prochází skupinou
stejně silných rukou** — a která z nich padne nalevo, určuje pořadí po `qsort`.

Jenže `compareHandByRank` remízy nerozlišuje, takže pořadí uvnitř remízové skupiny
**není v kódu určeno**. `qsort()` navíc není standardem C garantován jako stabilní; glibc
používá merge sort (stabilní), když dokáže alokovat pomocný buffer, a quicksort (nestabilní),
když ne.

> **Mechanistické vysvětlení nereprodukovatelnosti:** i s originálním zdrojovým kódem by
> pořadí remízových rukou záviselo na implementaci a verzi libc na strojích, které data
> generovala, případně na tom, zda `qsort` v daném běhu sáhl po mergesortu nebo po
> quicksortu. **Ze zdroje samotného ho odvodit nelze.**
>
> Tím se nález #17 posouvá z „specifikace je nedourčená" na
> **„nedourčená je i implementace, a to ze strukturálního důvodu"**.

#### Ostrý kontrast v témže souboru

`evalShowdown_2c` remízy řeší **korektně a pořadí-nezávisle** — `card_tools.c:307-310`:
```c
    /* hand i is first in a group of ties; find the last hand in the group */
    for( j = i + 1;
	 ( j < numHands ) && ( hands[ j ].rank == hands[ i ].rank );
	 j++ );
```
Seskupuje podle **rovnosti ranku**, ne podle indexu. Výsledek je tedy na pořadí uvnitř
remízové skupiny imunní.

> Burchův vlastní kód tedy remízy ošetřuje tam, kde na nich záleží (showdown), a nechává je
> neurčené tam, kde by na nich záležel až split na půlky (`getHandList`). To je konzistentní —
> `getHandList` nebyl psán pro dělení na poloviny.

### Nález #50 (P1, cíl A/C) — per-hand CFV primitiva v terminálních uzlech

`card_tools.c` obsahuje čtyři funkce, které berou **range soupeře** a vracejí **vektor hodnot
po rukou**:

| Funkce | Řádek | Význam |
|---|---|---|
| `evalFold_1c` / `evalFold_2c` | 175 / 247 | hodnoty při foldu; `foldValue = -spent[p]` nebo `spent[p^1]` |
| `evalShowdown_1c` / `evalShowdown_2c` | 199 / 283 | hodnoty při showdownu; `sdValue = spent[p] == spent[p^1]` |

`evalShowdown_2c` implementuje O(n) rozklad výhra/remíza/prohra s korekcí na blokery
(`sumIncludingCard[]` po kartách), vstup `oppProbs[numHands]`, výstup `retVal[numHands]`.

> **To je tvarem přesně to, co DeepStack potřebuje jako trénovací cíl** — jenže
> **v terminálních uzlech**, ne v kořenech subgames. Nález #6 (žádný CFV export
> v kořenech subgames) tím zůstává v platnosti; tohle je vnitřní primitiva solveru,
> ne exportní rozhraní.

### Nález #51 (P2, cíl D) — čtvrtý seedovací idiom a společná redukce

`example_player.c:50-52`:
```c
  /* Initialize the player's random number state using time */
  gettimeofday( &tv, NULL );
  init_genrand( &rng, tv.tv_usec );
```
a použití — `:165` `p = genrand_real2( &rng );`, `:177`
`action.size = min + genrand_int32( &rng ) % ( max - min + 1 );`

**Úplný katalog CPRG seedovacích idiomů** (rozšíření #42):

| # | Idiom | Kde | Determinismus |
|---|---|---|---|
| 1 | `rngSeed ^ subgameIndex` → glibc `random_r`, stav 32 B | `CFR_plus/storage.c:1001` | ano |
| 2 | `genrand_int32( &match->rng )` z MT19937 streamu | `bm_server.c:1358` | ano |
| 3 | sekvenční index 0…49 předaný přímo | LBR na MP2 | ano |
| 4 | `init_genrand( tv.tv_usec )` | `example_player.c:52` | **ne** |

Společná redukce napříč **všemi**: `% n` — modulo bias, nikde neošetřený
(`game.c:767`, `storage.c:893`, `example_player.c:177`).

### Nález #52 (NEGATIVE) — zbytek balíků neobsahuje nic k A–E

| Soubor | Velikost | Obsah |
|---|---|---|
| `validate_submission.pl` | 19 005 B | validace ACPC submission; jediný „random" je prozaická zmínka na `:509` |
| `all_in_expectation.c` | 5 082 B | výpočet all-in EV z match logu; bez RNG |
| `bm_widget.c` | 5 176 B | UI widget benchmark serveru |
| `net.c` / `net.h` | 4 539 / 1 690 B | socket I/O |
| `example_player.c` | 4 842 B | ukázkový hráč (viz #51) |
| `sum_values.pl` | 706 B | sčítání hodnot z logů |
| `betting_tools.c` | 9 252 B | konstrukce betting tree; bez RNG |
| `util.c` | 18 108 B | hash + časovače; „pseudorandom" jen v komentáři |
| `recompress.c` | 20 657 B | přeuspořádání komprimovaných dat pro random access; bez RNG |

> **Průchod je úplný.** Všech 65 lokálních zdrojových souborů přečteno. Mimo už zaznamenané
> nálezy neobsahují nic relevantního k A–E.

---

## Příloha J — Vlna 13: kvantifikace nálezu #49

Nález #49 ukázal *mechanismus*, proč je R(S,p) nedourčené. Tato vlna měří **rozsah**.

### Metoda

Pro náhodně vybrané turn boardy (4 veřejné karty) enumerováno všech
`C(48,2) = 1128` hole-card kombinací, spočtena síla ruky, pole seřazeno a odsimulována
rekurze R(S,p) — na každé úrovni řez v `⌊|S|/2⌋`. Označena každá ruka, která leží
v remízové skupině, kterou nějaký řez protíná; její zařazení do `S₁`/`S₂` tedy
**není zdrojovým kódem určeno**.

Měřeno dvěma metrikami síly ruky:
1. **`rank`** — pořadí kombinace, ekvivalent `rankCardset()` (#45)
2. **hand strength dle supplementu** — *„probability of a hand beating a uniformly selected
   random hand from the current public state"*, počítáno přesně (racionální aritmetika),
   s vyloučením blokovaných rukou a remízou za ½

### ⭐⭐ Nález #53 (P0, cíl A) — nedourčeno je prakticky celé generované range

| Board | Ruk | Různých `rank` | Nedourčeno (rank) | Různých HS | Nedourčeno (HS) |
|---|---|---|---|---|---|
| `2h9s2cAs` | 1128 | 42 | 1127 | 43 | 1127 |
| `8dQdAc6d` | 1128 | 105 | 1083 | 133 | 1127 |
| `Qh3hQcQd` | 1128 | 78 | 1128 | 70 | 1128 |
| `9c3h5dJh` | 1128 | 90 | 1128 | 91 | 1128 |
| `3sKc2sJh` | 1128 | 91 | 1128 | 91 | 1128 |
| `KcJdTs9s` | 1128 | 36 | 1128 | 42 | 1128 |
| `7c9hTs2h` | 1128 | 88 | 1128 | 89 | 1128 |
| `Kh8hQcJc` | 1128 | 44 | 1128 | 46 | 1128 |
| **celkem** | **9 024** | — | **8 978 (99,5 %)** | — | **9 022 (100,0 %)** |

Doplňkově přes 30 turn boardů (metrika `rank`): **99,2 %** nedourčených, medián
**1128 z 1128**; top-level řez padne dovnitř remízové skupiny v **90 %** případů.

### Proč to vychází takto

Na turn boardu existuje mezi 1128 rukama jen **36–133 různých hodnot síly ruky**.
Průměrná remízová skupina má tedy ~12 rukou. Rekurze R(S,p) sestupuje ~10 úrovní
(2¹⁰ = 1024 ≈ 1128), takže na hlubších úrovních jsou skupiny menší než průměrná
remízová skupina a **prakticky každý řez padne dovnitř remízy**.

Blokery to nezachrání: definice ze supplementu dává jen o pár hodnot víc
(42→43, 90→91, 44→46) a v jednom případě dokonce **méně** (78→70).

> **Závěr:** pravděpodobnost, kterou R(S,p) přiřadí prakticky **každé** ruce, závisí
> na pořadí uvnitř remízové skupiny — tedy na chování `qsort` v konkrétní libc (#49),
> které zdrojový kód nespecifikuje.
>
> Nález #17 → #49 → #53 tvoří uzavřený řetěz:
> **spec je nedourčená → implementace je nedourčená → nedourčenost se týká celého výstupu**,
> ne okrajového případu.

### Výhrada — jediné čtení, které by to zachránilo

Měření předpokládá, že R(S,p) pracuje **nad seřazeným polem a řeže na pozici**
`⌊|S|/2⌋` — což je doslovné čtení supplementu (`$|S_1| = \left\lfloor|S|/2\right\rfloor$`).

Kdyby implementace místo toho seskupovala podle **různých hodnot síly** a řezala na
nejbližší hranici skupiny, byla by deterministická — ale porušila by podmínku
`|S₁| = ⌊|S|/2⌋` přesně tak, jak je napsaná. **Který z těch dvou zápisů odpovídá
skutečnému kódu, se z dostupných zdrojů rozhodnout nedá.**

### Dopad na cíl A a na rekonstrukci

Toto je nezávislé posílení nálezu #44 (experiment se seedem):

| | Co by bylo potřeba navíc |
|---|---|
| Znát `rngseed` | nestačí (#44 — ani u známého seedu se karty nereprodukovaly) |
| Získat originální zdroják R(S,p) | **stále nestačí** (#53 — tie ordering ve zdroji není) |
| Reprodukovat bit-exact | nutná i shodná libc a její `qsort` režim na generujících strojích |

> Pro váš DataGenerator to znamená: **bit-exact shoda s originálem není dosažitelný cíl**,
> a to prokazatelně, ne z opatrnosti. Rozumný cíl je distribuční ekvivalence —
> stejná specifikace, vlastní deterministické a zdokumentované tie-breaking pravidlo.

---

## Příloha C — Dopad na implementaci DataGeneratoru

Tento ledger **neopravňuje k žádné změně** existujícího DataGeneratoru ani Golden testů.

Tři existující pravidla jsou nyní doložená z primárního zdroje:

| Pravidlo | Doklad |
|---|---|
| `[100,100)` neopravovat na `[100,200)` | #16 — zdroj to má takhle ve všech třech verzích včetně post-review |
| `omit_iters` nepřenášet do offline generátoru | #20 — platí pro text supplementu. ⚠️ **Oslabeno:** referenční Leduc implementace skip iterace v offline generování používá (L2). Rozhodněte vědomě, kterému zdroji dáte přednost |
| R(S,p) nelze reprodukovat bit-exact | #17 — ani opravená v3 formulace neurčuje tie-breaking mezi remízovými ruce |

Fingerprint sada pro testování budoucích kandidátů na Burchův DataGenerator:

- `initstate_r(seed, buf, **32**, state)` — nedefaultní glibc TYPE_1
- `seed ^ index` odvození per-worker/per-subgame
- kanonické izomorfní třídy + `weight`, renormalizace až downstream
- partial Fisher–Yates s `t %= (num - i)`
- kanonická grupování v trunku, nekanonická v subgames (#18)
