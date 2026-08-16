# Michael Johanson (CPRG) — first-party svědectví (e-mail vlastníkovi, 2026-08-16)

Evidence class: **Tier 2 / CONFIRMED (first-party recollection)**. Autor: **Michael Johanson** — identita potvrzena vlastníkem (adresát
korespondence), 2026-08-16. Paměťové výroky („nejsem si jistý",
„nevím") značeny.

## Výroky

1. **project_uoapoker**: interní repozitář CPRG, není a nebude veřejný.
   Veřejná vydání (Cepheus, DeepStack-Leduc…) byla přepsána zvlášť.
2. **DeepStack postaven OD NULY v novém repozitáři** — ne nad interním
   repem („dostatečně se lišil od dřívějšího přístupu"). Autor u toho
   už nekódoval. → **Druhé nezávislé potvrzení Waughova svědectví.**
3. **Starý CPRG workflow**: (gamedef textový soubor) → (solver
   executable) → (strategy file); hraní přes „dealer" + hráčská `.so`
   rozhraní s parametry (např. strategy file). → přesně odpovídá
   struktuře vs_LBR logů (`meta_player.so` + args + `.map`).
4. **Indexování karet**: obecné (nic NL-specifického); interně DVA
   systémy — (a) Waughova open-source **kdub0/hand-isomorphism**
   (optimální), (b) starší indexace z éry prvního CFR článku (mírně
   větší než optimální). Který byl použit kde, si nepamatuje.
5. **FCPA**: fold/call/pot/all-in s celočíselnými žetony — potvrzeno
   (shodné s Waughem).
6. **CFRPLUS_HOLDEM_NOLIMIT_FCPA**: zní jako **jméno STRATEGY FILE**
   (solver byl na abstrakci/limit-nolimit agnostický — vše definoval
   gamedef; jen strategy file kombinuje tyto termíny v jednom řetězci).
7. **DataGenerator**: neví; ani project_uoapoker, ani deepstack repo
   nejsou veřejné.
8. **Koho se ptát**: Dr. Bowling (poslední z týmu na univerzitě);
   očekávaná odpověď: kód je proprietární.

## Důsledky pro mise

- **B-artefakt (DataGenerator)**: druhé nezávislé potvrzení, že žil v
  samostatném, neveřejném DeepStack repu → naděje na veřejný nález
  minimální; formální cesta = dotaz na Dr. Bowlinga (očekávané
  „proprietární").
- **Hand indexing (CPRG strana)**: kandidáti zúženi na 2 konkrétní
  systémy; kdub0/hand-isomorphism už máme klonovaný (Tier 3 → Tier 2
  jako doložený kandidát). POZOR: DeepStack byl od nuly — jeho 1326
  ordering tím DOLOŽEN NENÍ (zůstává UNKNOWN).
- **vs_LBR logy**: workflow popis křížově validuje jejich strukturu
  (dealer/.so/args) — posiluje čtení kategorie E artefaktů.
- **CFRPLUS_HOLDEM_NOLIMIT_FCPA** v Adamově dotazu = pravděpodobně
  strategy-file jméno (odpovídá i „Full Cards" agentovi ze Science
  Table S2 — FCPA strategie bez karetní abstrakce, ~2 TB, ~14 CPU-let).

---

## Bitové testy svědectví (2026-08-16, provedeno v této session)

### FCPA řetěz (Waugh) — PASS 3/3
`FORENSICS/SCRIPTS/fcpa_chain_test.py` (log latest_audit/FCPA_CHAIN_TESTIMONY_TEST.txt):
1. Certifikovaný turn tree (pot 1 BB): max-raise řetěz = **300/900/2700/8100/20000**
   celočíselně — 3/9/27/81 BB + all-in cap ✓
2. Nedotčené ACPC game.c: všech 5 raise akcí legální (replay verbatim) ✓
3. Uzavřená forma raise-to_{k+1}=3·raise-to_k; při 100BB stacku další krok
   přesahuje stack ⇒ all-in — přesně Waughův řetěz ✓
Svědectví povýšeno: recollection → implementation+oracle-verified.

### hand-isomorphism (Johanson: kandidát č. 1) — VERIFIED
- Knihovna kdub0/hand-isomorphism zkompilována; vlastní check-suite
  (full preflop, full flop, random turn/river) prošla.
- Velikosti kanonických tříd spočtené knihovnou:
  preflop **169**, board{3} **1 755**, board{4} **16 432**, board{5}
  **134 459**; hand-indexy: flop 1 286 792, turn 55 190 538, river
  2 428 287 420 — shodné s publikovanou tabulkou Waughova paperu
  (AAAI-13 workshop; přímý PDF egress-blokován, hodnoty koroborovány
  search snippetem + interním self-testem).
- **Cross-anchor na DeepStack**: 169 preflop tříd = přesně dimenze aux
  sítě ze Science supplementu („169 strategically distinct hands
  pre-flop") — knihovna reprodukuje first-party číslo.

### Dohledávání chybějících informací
- Starší CFR-éra indexace: Johansonova MSc thesis (2007, „Robust
  Strategies…") lokalizována (poker.cs.ualberta.ca + scholaris —
  OBĚ egress-blokovány; URL zaznamenány pro stroj bez omezení).
- johanson.ca + cs.cmu.edu PDF — egress-blokovány (zaznamenáno).

## count_nl_infosets — autorský orákulum-nástroj (Tier 1, owner-verified round 1)

Vlastník dodal report z externího ověření Johansonova nástroje `count_nl_infosets.tar`
(hlavička zdrojáku: „Mike Johanson, Feb 1, 02013"; tar owner johanson/johanson;
tar SHA-256 6fcf5fa41387ed71f720c9c850c47b7b111830b68f979853a8c3f998365ac0c8).
Vendorováno: `FORENSICS/ARTIFACTS/count_nl_infosets/` (JSON oracle + MD report;
samotný tar v této session nemáme).

Co je bitově potvrzeno (externí běhy vlastníka, GCC==Clang byte-identical po
normalizaci elapsed-time řádku):

- Royal hold'em [2-$20] $1-$2: 12/12 polí Table 7 EXACT.
- ACPC 2009 ($1/$2, stack 400): čerstvý běh byte-identical s autorovým `acpc-2009.txt`.
- ACPC 2007–2008 ($1/$2, stack 1000): byte-identical s autorovým výstupem.
- ACPC 2010–2013 ($50/$100, stack 20000 = naše HUHL konfigurace): autorův přesný
  výstup zachován jako reference (SHA-256 117b69f8…), čerstvý re-run neproveden
  (alokace 6,4 GB + ~2 dny CPU).

První-osobní sémantika betting pravidel z autorova zdrojáku:
fold legální ⇔ faced>0; check/call vždy; min_bet = max(bigblind, faced);
short all-in výjimka (stack−faced < min_bet ⇒ all-in legální); všechny celočíselné
částky min_bet…stack−faced legální (neabstrahované); call přechází do dalšího kola.

Hranice: NENÍ to FCPA orákulum ani DataGenerator — certifikuje jen bazální NL
legalitu/přechody.

### Diferenciální test: autorská pravidla vs nedotčené ACPC game.c — PASS

`FORENSICS/SCRIPTS/johanson_rules_diff.py` (dávkový design; první interaktivní
verze deadlockovala na blokové bufferaci stdout orákula). Python model počítá
okna raise VÝHRADNĚ z autorových formulí reportu (min increment = max(BB, faced
increment); short all-in výjimka; max raise-to = stack; fold ⇔ faced>0; call
vždy) a na náhodných legálních HUNL sekvencích (50/100, stack 20000, reverse
blinds, seed 20260816) je konfrontuje s `betting_oracle.c` nad nedotčeným
restaurovaným `game.c`:

- 600 her, 2 646 rozhodovacích stavů, 16 971 kontrol (R okna + Q sondy
  f/c/hranice min−1/min/max/max+1), 0 neshod, 0 sync neshod.
- **Závěr: Johansonova betting sémantika z count_nl_infosets je na vzorkovaném
  prostoru IDENTICKÁ s DS-era ACPC game.c (anchor 85b5325d)** — včetně short
  all-in výjimky, resetu min-raise na maxSpent+BB po přechodu kola a inicializace
  min-raise-to = 2×BB. Bazální NL legalita našeho enginu je tak kryta dvěma
  nezávislými prvoautorskými orákuly současně.
