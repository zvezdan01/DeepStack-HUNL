# AIVAT — forensic reconstruction & oracle status

Mission date: 2026-08-15. Session `claude/generator-dat-pro-huhl-forenzic-rvclmx`.

## *** FORENSIC BREAKTHROUGH ***

Owner-uploaded `DeepStack_vs_IFP_pros.zip` (SHA-256
`fb92b4b0821b31a5c8ba18373ae8dc1c99ec098996adb1fc120e8887fdf9431a`,
archived at `certification/leduc_restore/archives/DeepStack_vs_IFP_pros_fb92b4b0.zip`)
is the **original authors' release of the DeepStack pro-match study**,
containing `AIVAT_analysis/` — **per-hand AIVAT outputs** (33 CSV files,
one per participant, dated 2017-02-08) plus the official ACPC match logs
(`DeepStack_logs/ACPC/`) and three PokerStars-format views. This is a
CONFIRMED original experimental artifact (mission category E — intermediate
AIVAT outputs per hand; plus C — original match logs).

### Contents verified (all CONFIRMED, computed this session)

Per-hand fields: `AIVAT, Chips, All Hands Chips, Chance Correction,
Action Correction, Your Hand, DeepStack Hand, Flop/Turn/River, Position,
per-street betting, timing, start time, notes`.

1. **Decomposition identity** (stated in the release README):
   `AIVAT = All Hands Chips − Chance Correction − Action Correction`
   (participant's point of view). **Holds on ALL 45,037 hands** across
   all 33 files, worst |residual| = 1.0e-6 (= CSV rounding at 5–6
   decimals). 0 violations.
2. **Study-population filter reconstructed**: the release holds 45,037
   hands; the paper reports 44,852. The difference (185) equals EXACTLY
   the sum of per-player overflow beyond 3,000 hands
   (122+26+10+7+6+4+3+3+2+1+1 over the 11 players who exceeded 3,000).
   ⇒ the published population = **first 3,000 hands per participant**.
3. **NUMERIC-EXACT reproduction of the published Science results** from
   the original per-hand data under that filter:
   | metric | published | reproduced here |
   |---|---|---|
   | games | 44,852 | 44,852 (exact) |
   | DeepStack raw chips | 492 mbb/g, >4σ | **491.50 mbb/g, 4.4σ** |
   | DeepStack AIVAT | 486 mbb/g, >20σ | **485.74 mbb/g, 23.6σ** |
   | players / completed 3000 | 33 / 11 | 33 / 11 (exact) |
4. Disconnect incidents: 8 hands carry the disconnect note (7×
   qin.youwei, 1× takeda.tsuneaki) and have empty timestamps —
   consistent with the README's "nine hands" wording (one further hand
   presumably in the logs without a note; to be reconciled against the
   ACPC logs).

## Oracle hierarchy — current status

| level | definition | status |
|---|---|---|
| L0 paper-equation | AIVAT equations spec | **DONE** — plná transkripce z prvoautorského vat.tex (owner-uploaded arXiv v2 tarball) do `FORENSICS/AIVAT_L0_SPEC.md`: partition 𝓗 (3 vlastnosti), k_H(z), partition 𝓦 + base value, eqn:vat, u_h(a)=−w_H(a) z MCCFR self-play, 8M-infoset HUNL abstrakce, poziční 50/50 korekce, důkaz nestrannosti; ⚠ OPEN jen produkční parametry (abstrakce, MCCFR seed) |
| L1 synthetic deterministic hand | build-your-own fixture | AVAILABLE (given L0 spec) — not yet built |
| L2 original-paper numeric | published aggregates | **ACHIEVED** — 44,852 / 491.50→"492" / 485.74→"486" / σ levels, from original data |
| L3 original hand/log | per-hand original values + official ACPC logs | **ACHIEVED (artifact in hand)** — 45,037 per-hand AIVAT/corrections + official ACPC logs; CSV↔ACPC-log linkage check pending |
| L4 original author code | AIVAT source | NOT FOUND (hunt continues) |
| L5 bit-exact original | byte-level oracle | NOT AVAILABLE — CSVs are rounded to 5–6 decimals ⇒ numeric (≤1e-6) not bit oracle |

## What this enables as a certification test TODAY

Strongest available test (no author code needed):
- Parse the official ACPC logs; recompute `Chips` per hand (raw payoff)
  — must match CSV exactly (integers/halves).
- Verify the decomposition identity per hand (done: 45,037/45,037).
- Reproduce the published aggregates under the reconstructed
  first-3000 filter (done: NUMERIC-EXACT).
- Once our engine can compute DeepStack-side ranges/strategies for these
  situations, the `All Hands Chips` column is a per-hand oracle for the
  "imaginary observations" expectation, and the correction columns for
  the chance/action baselines.

## Blockers for full AIVAT recomputation (per-hand corrections)

- **BLOCKER: DeepStack's strategy/ranges** for each decision point of the
  study — required to recompute `All Hands Chips`, `Chance Correction`
  and `Action Correction`. Not in the release (only their VALUES are).
- **BLOCKER (bit-level): CSV rounding** — 5–6 decimals ⇒ ceiling is
  numeric equivalence ≤ ~1e-6, not bit-exactness.
- NON-BLOCKER: RNG/seeds — AIVAT evaluation of a FIXED log is
  deterministic given strategy + baseline; no sampling involved at
  evaluation time.
- To determine: baseline function used by the authors (paper specifies
  it; transcribe equations), float precision, summation order (only
  matters below ~1e-6).

## Answers to the mission's final questions (interim)

1. Public original AIVAT source? — NOT FOUND yet (hunt continuing:
   CPRG/author repos swept for DataGenerator mission already; AIVAT-
   specific fingerprint sweep pending).
2. Original AIVAT experimental artifacts? — **YES: this release** (per-
   hand outputs + official logs), CONFIRMED.
3. At least one original hand-level oracle? — **YES: 45,037 of them.**
4. Numeric reproduction vs authors' results? — **YES, achieved** for the
   aggregates + per-hand identity; per-hand corrections need our own
   AIVAT implementation + DeepStack strategy (blocked).
5. Bit-exact reproduction? — NO (CSV rounding ceiling; no author code).
6. Missing for bit-exact: author code (L4/L5), unrounded outputs,
   strategy artifacts.
7. Strongest test today: L2+L3 combo above (identity + filter +
   aggregates + ACPC payoff cross-check).
8. Next artifacts to hunt: aivat source fingerprints (aivat.py/.cpp,
   "imaginary observations", MIVAT/DIVAT code by Zinkevich/White/Bowling
   lineage), Burch/White repos, ualberta hand-values baselines, the
   AIVAT arXiv (1612.06915) TeX for exact equations, and the 9th
   disconnect hand reconciliation.

---

## UPDATE 2026-08-15 večer — supplement + vs_LBR artefakty (owner-uploaded)

### Nové artefakty (CONFIRMED, archived)
- `17science-supplementary_b60b8865.pdf` — oficiální Science supplement
  (dosud egress-blokovaný), nyní čtený přímo, vč. vizuálního čtení
  rovnic (Lemmas S1–S3, gadget; stránky rasterizovány).
- `vs_LBR_68475917.zip` — **originální LBR experiment outputy z MP2**
  (`*.mp2.m.out`, PBS job ID v názvech). Obsahuje: config hlavičky
  (GAME_DEF, ACTIONS_R0..R3), `Loading player: rgbr_nl_cprg.so`,
  `Player args: /home/viliam/cprg/project_uoapoker/trunk/src/c/
  meta_player.so … acpc14.map` (přesné cesty CPRG SVN stromu!),
  **explicitní `Using seed N.`** + sSEED/rSEED v názvech souborů,
  per-hand variance-reduced hodnoty (imaginary observations) a
  **originální autorský agregační skript `aggregate3.sh`** (kategorie
  B/I pro LBR evaluaci).
- Druhá kopie `DeepStack_vs_IFP_pros.zip` — **BYTE-IDENTICKÁ**
  (SHA fb92b4b0…) s dříve archivovanou ⇒ bitová verifikace artefaktu.

### NUMERIC-EXACT verifikace dokončené tímto materiálem
1. **Table S2 (LBR) 12/12 hodnot** reprodukováno autorským
   aggregate3.sh na originálních lozích, včetně CI: DeepStack
   −428±87 / −383±219 / −775±255 / −602±214; Hyperborean14
   721±56 / 3852±141 / 4675±152 / 983±95; FullCards (blindy 1/2 chip)
   −424±37 / −536±87 / 2403±87 / 1008±68.
2. **Table S1 (per-player AIVAT) 33/33 řádků** (3 hraniční případy
   zaokrouhlení ±0.5 mbb/g): vzorec rekonstruován PŘESNĚ —
   mean ± t_{0.975,n−1}·s_{n−1}/√n, first-3000 cap.
3. `[100,100)` potvrzeno doslova v oficiálním supplementu (p.10 fn.1);
   offline datagen: "1,000 iterations of CFR+" BEZ zmínky omitu ⇒
   omit=500 zůstává hypotéza.
4. **Vidlička R-1 VÝZNAMNĚ OSLABENA**: supplement (p.7) definuje
   DeepStack "CFR+" jako hybrid (RM+ + simultánní updaty + uniformní
   vážení + omit raných iterací) — tj. papírová terminologie „CFR+"
   označuje přesně sémantiku našeho enginu; offline věta „CFR+"
   pravděpodobně míní týž hybrid. Table S3 dává online konfigurace:
   preflop 1000/980, flop 1000/500, turn 1000/500, river 2000/1000.
5. NN přesnosti (p.12): turn train/valid 0.016/0.026 pot, flop
   0.008/0.034, aux 0.000053/0.000055 — statistické oracle hodnoty.

### Nová kategorie D/E fakta (LBR runy)
- seedy 1..30 (fcpa_dsFCPA), 1..20/1..10 dle konfigurace; s/r = strana
  karet (duplicate matches). N=50k rukou u CPRG agentů, 10-15k u DS.
- LBR configy: ACTIONS_R2/R3 = F,C,1,A (pot=„1"); preflop/flop C.

---

## UPDATE 2026-08-16 — arXiv TeX zdrojáky (owner-uploaded, Priorita 1)

### Artefakty (archivovány v certification/leduc_restore/archives/)
DeepStack v1/v2/v3 e-printy + AIVAT 1612.06915v2 e-print (TeX zdroje).

### Nálezy
1. **`[100,100)` je VERBATIM autorský TeX** ve všech třech verzích
   (`$\{[100, 100),$ …`) — není to sazební artefakt; hypotéza H3
   (přepis z interního configu) zůstává nejpravděpodobnější; nikdy
   neopraveno.
2. **appendix.tex v1 == v2 BYTE-IDENTICKÝ (diff 0 řádků)**; v2→v3 =
   476 řádků diffu (Science revize). Table S3 (resolving config,
   preflop 1000/980) **identická v1 i v3** — arXiv i Science se
   shodují; outlier s jinými čísly je tedy Schmidova disertace
   (viz PROVENANCE_NOTES §6).
3. **Zakomentovaná full-precision per-player tabulka v TeX** (31 řádků,
   12+ platných číslic): naše rekonstrukce z originálních CSV sedí na
   **26/29 hráčů s |d|<5e-9** při z-CI formuli (1.96·pstdev/√n) —
   drafty používaly z-CI, publikovaná tabulka t-CI (obě formule jsme
   rekonstruovali přesně). 3 odchylky = draft-éra artefakty: Qin/Takeda
   (disconnect handy — draft měl zjevně starší per-hand hodnoty těchto
   rukou; finální release == CSV přesně) + 1 parsovací kandidát
   (Schwab CI sloupec).
4. **AIVAT vat.tex = kompletní rovnice** (k_H(z) korekce, base values,
   chance/action termy) → L0 paper-equation oracle ODEMČEN; plná
   transkripce do implementační specifikace = další krok.

## UPDATE 2026-08-16b — Priorita 2 dokumenty (owner-uploaded)

1. **isomorphism13.pdf (Waugh)**: Table 1 potvrzuje first-party naše
   vypočtené velikosti — Perfect: flop 1,286,792 / turn 55,190,538 /
   river 2,428,287,420 ✓ (anchor povýšen ze search-snippet na dokument
   v držení).
2. **Refining Subgames (AAAI-16, Moravčík et al.)**: Nyx = 2. místo
   ACPC 2014; endgame experimenty 10,000 iterací CFR+; max-margin
   101.49±7.09 vs re-solving 8.79±… (exploitability zlepšení) — Tier-2
   kontext Nyx→DeepStack re-solving linie.
3. **Johanson PhD 2016**: PŘESNÁ AIVAT GENEALOGIE — Imaginary
   Observations (kap. 7; idea Bowling, formalizace ICML-08 linie);
   „All Cards" estimátor = předchůdce sloupce **All Hands Chips**
   z AIVAT release; IO-DIVAT kombinace (kap. 8: per-match Mean/StdDev
   tabulky 2007/2008 Man-vs-Machine — desítky numerických oracle bodů);
   kombinace AC+EF+BC-DIVAT. Autorské příspěvky explicitně rozděleny.
   => L0 řetěz AIVAT je nyní kompletně dokumentován first-party:
   IO (2008) + DIVAT (Billings&Kan 2006) → AIVAT (2016, vat.tex rovnice).

## *** PRŮLOM #4 (2026-08-16) — open_pvat: originální kus project_uoapoker ***

Owner-uploaded `open_pvat.tgz` + `hand_strength.tgz` +
`preflopPotEquityTable.table.tgz` (archivováno, SHA ed746605/dd7e040c/
8fb90ea4).

### Provenience (CONFIRMED z SVN metadat v archivu)
- `.svn/entries` (graphs/): URL **svn+ssh://games.cs.ualberta.ca/usr/
  svnroot/project_uoapoker/open_source/open_pvat/graphs**, revize
  **r6077**, 2009-10-02T20:27:35Z, autor **jdavidso**.
- => POTVRZENÝ server + cesta + struktura interního repa (podstrom
  `open_source/`), revizní číslování ~6077 k říjnu 2009.

### Obsah
- OPEN PVAT: implementace **DIVAT algoritmu Morgana Kana** (README:
  "based on Morgan Kahns DIVAT algorithm") — přímý algoritmický předek
  AIVAT, z LINIE INTERNÍHO REPA. C zdroje (game_state, hand_strength
  wrapper pro poker-eval, pvat tables/utils/defines), preflop pot
  equity tabulka (1 624 350 řádků), příkladová data.
- Formát hand history dokumentován v README (HandNumber:P1,P2:...).

### Rekonstrukce a GOLDEN TEST — PASS BYTE-IDENTICAL
- Nástroj ZNOVU POSTAVEN v této session (poker-eval z GitHub mirroru;
  jediný zásah: link `-Wl,-z,muldefs` kvůli GCC≥10 -fno-common —
  tentative-definition bug v původním open_pvat_reader.c:15; ŽÁDNÁ
  změna zdrojáků).
- Běh na README příkladové handě reprodukuje bundlované
  `graphs/Chump{1,2}.graph` **bajt po bajtu** (MONEY ±5.000, per-round
  DIVAT sloupce) — mise-item **H (golden test) DOSAŽEN** s originálním
  autorským kódem.

### Dopad na oracle hierarchii AIVAT
- **L4 (author code) DOSAŽEN pro DIVAT/PVAT rodinu** — ne AIVAT sám,
  ale jeho přímý předek ze stejné interní linie; běžící, bajtově
  ověřený.
- Řetěz: DIVAT (Billings&Kan 2006; kód ZDE) + Imaginary Observations
  (Johanson PhD kap. 7) → AIVAT (rovnice vat.tex) — všechna tři patra
  nyní držíme first-party.
