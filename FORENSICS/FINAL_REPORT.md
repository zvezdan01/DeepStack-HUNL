# Závěrečná forenzní zpráva — HUHL data generátor + DeepStack forenzní mise

Datum: 2026-08-16 · Větev: `claude/generator-dat-pro-huhl-forenzic-rvclmx`
Stav: certifikační harness dobíhá (sekce 3/5); tato zpráva se po doběhu
finalizuje doplněním výsledků sekcí 3–5.

## 1. Shrnutí

1. **Pilot HUNL turn data generátoru je DOKONČEN a deterministický**:
   12 shardů × 20 vzorků (240/240) + plný replay shardu 0 v čerstvém
   procesu — všech pět polí byte-identical. Kombinovaný dataset anchor
   SHA-256 `274188d4…`.
2. **Certifikace**: sekce 1 (manifesty + RNG ledger) a 2 (replay
   byte-identity) PASS; sekce 3 (row-level inversion audit, 8 náhodných
   řádků) průběžně 5/8 BYTE-IDENTICAL, běží; sekce 4 (nezávislá orákula)
   a 5 (statistická QA) následují.
3. **Bit-exact rekonstrukce ORIGINÁLNÍHO DeepStack HUNL DataGenerátoru:
   NE. Algorithm-exact: ANO (~90–95 % funkční věrnosti po komponentách)**
   — detailní rozpad v `GENERATOR_READINESS.md`, zdůvodnění v
   `FINDINGS.md` (BIT-EXACT READINESS verdikt).
4. **AIVAT**: L0 spec kompletní (`AIVAT_L0_SPEC.md`), L2+L3 numericky
   ověřeno na publikovaných datech, L4 dosaženo pro DIVAT/PVAT
   předchůdcovskou rodinu (open_pvat golden test byte-identical).
5. **Bazální NL betting legalita je krytá dvěma nezávislými
   prvoautorskými orákuly**: nedotčený ACPC `game.c` (anchor 85b5325d)
   a Johansonův `count_nl_infosets` — diferenciální test 600 her /
   16 971 kontrol, 0 neshod (`SCRIPTS/johanson_rules_diff.py`).

## 2. Golden referenční stav

Commit této větve = referenční stav („golden"): certifikovaný `hunl/`
engine (Golden Baseline 34a5056, SHA256SUMS 52/52), certifikovaný
Torch7 MT19937 (`datagen/th_random.py`, bajtová shoda s originálem
6/6 seedů), generátor `hunl_datagen/turn_datagen.py` v1.1.1
(per-sample checkpointing s RNG stavem, atomic tmp+rename, gc
hardening), plná regresní baterie PASS (pytest 36/36, komparátory 8/8
BIT-EXACT, G1.7+G1.8 ZERO CHANGE). Owner-uploaded originály jsou
vendorované v `certification/leduc_restore/archives/`; DS Leduc
workspace se z nich instaluje do
`/workspace/deepstack_leduc_v1.1-bitexact-certified` (vyžaduje
`LD_LIBRARY_PATH` na libgfortran.so.3 + bundled OpenBLAS cd143947).
Golden export: `huhl-golden-reference-aa04c5a.zip`, SHA-256
`3b5cccad…`; core export (17 MB) `07118bb0…`.

## 3. Certifikace generátoru (stav k okamžiku zápisu)

| Sekce | Obsah | Výsledek |
|---|---|---|
| 1 | manifesty 12 shardů, SHA ověření, RNG ledger reconciliace (4+rej board, 22 540+752 range, 40 pot draws/shard) | **PASS** |
| 2 | plný replay shardu 0 v čerstvém procesu | **PASS (BYTE_EXACT)** |
| 3 | inversion audit 8 náhodných řádků — nezávislé přehrání targetu | běží, 5/8 BYTE-IDENTICAL |
| 4 | nezávislá orákula: forced-check/all-in + LP cross-check | čeká |
| 5 | statistická QA (chi² board karet, pot korelace, unikátnost řádků) | čeká |

Navíc certifikováno: checkpoint-resume (případy A–E: kill po 3./7.
vzorku, korupce ckpt → self-heal, skip hotového shardu — vše
byte-identical, `run_datagen_ckpt_test.py`), determinismus napříč
kontejnery (re-anchor baterie po každém restartu).

## 4. Provozní incident log

Session přežila ~5 recyklací kontejneru (idle 30–60 min) a další
incidenty; žádný nevedl ke ztrátě dat ani nedeterminismu:

1. Recyklace kontejneru → řešeno per-sample checkpointingem + hodinovým
   cron babysitem (`pilot-babysit-hourly`); noční výpadek one-shot
   send_later řetězu (~8 h) byl důvodem přechodu na cron.
2. OOM kill workera (4×4,4 GB) → gc fix v generátoru v1.1.1 + driver
   v2.1 s wave-completeness respawnem; OOM kill cert harnessu (13,6 GB)
   → gc fix v sekci 3.
3. Výpadek git proxy po nočním restartu → kritické soubory pushnuty
   přes GitHub API (commit a2a8e49), poté normální režim.
4. Neúplná obnova ACPCServer (chybějící hlavičky) → kompletní re-copy
   originálu; následná plná baterie PASS.
5. PYTHONPATH shim stínící skutečný balík → odstraněn z repa.

## 5. Forenzní mise: DataGenerator hunt (artefakty A–E)

Původní artefakty A–E (range generator source, DataGenerator skripty,
raw samples, RNG seed/config, cluster manifesty) se **nedochovaly
nikde ve veřejném prostoru** — vyčerpávající negativní výsledky:
223 forků DeepStack-Leduc, CPRG rng.c monokultura, upstream historie
2 commity, egress-blokované zdroje dokumentovány (13 URL,
`BLOCKED_LINKS.md`). Pozitivní průlomy:

- **#1–2**: supplement + vs_LBR + IFP data (owner-uploaded) — numerické
  verifikace publikovaných agregátů; 56-frakční LBR seznam; draft z-CI
  vs published t-CI formule.
- **#3**: arXiv TeX zdrojáky ds_v1/v2/v3 + aivat_v2 — first-party
  rovnice, pot intervaly `{[100,100),[200,400),[400,2000),[2000,6000),
  [6000,19950]}` potvrzeny napříč verzemi.
- **#4**: open_pvat = originální kus project_uoapoker (SVN r6077,
  jdavidso) — REBUILT, golden test byte-identical.
- Svědectví: Waugh (hand-isomorphism, `WAUGH_TESTIMONY.md`), Johanson
  (`JOHANSON_TESTIMONY.md` — gamedef→solver→strategy pipeline, FCPA,
  dva card-indexing systémy, project_uoapoker; bit-testy: FCPA chain
  [300,900,2700,8100,20000] PASS 3/3; count_nl_infosets Tier 1 orákulum
  + diferenciální test PASS).

Verdikt: **bitová rovina je mrtvá pro kohokoli** (ztracené seedy,
cluster konfigurace a Torch verze; detailně `FINDINGS.md`); funkční
rovina je uzavřená na ~90–95 % s kotvami na prvoautorské artefakty.

## 6. AIVAT mise

- L0 rovnice: **kompletní transkripce** z vat.tex → `AIVAT_L0_SPEC.md`
  (partition 𝓗/𝓦, k_H, base value, u=−w z MCCFR, poziční korekce,
  nestrannost).
- L2+L3: per-hand identita `chips = aivat + Σ korekce` ≤ 5e-5 na
  publikovaných IFP CSV; agregáty 491.50/485.74 mbb/g, σ 4.4/23.6
  (`SCRIPTS/aivat_verify.py`, opakovatelné).
- L4: dosaženo pro DIVAT/PVAT rodinu (open_pvat byte-identical).
- L5 (produkční CPRG AIVAT binárka): nedochováno — viz `UNRESOLVED.md`.
- Odpovědi na 8 závěrečných otázek mise: `AIVAT_FINDINGS.md` §Answers.

## 7. Co zbývá / doporučení

1. Doběh cert sekcí 3–5 → zápis `TURN_DATAGEN_CERT_RESULT.txt` +
   finalizace této zprávy; poté smazání cron babysitu.
2. Volitelné senzitivní experimenty (omit 0/250/500 iterací, čtení
   intervalu [100,200)) — kvantifikace vlivu otevřených vidliček.
3. Od uživatele stále chybí (pokud existují): Johanson MSc 2007, Burch
   PhD PDF, Schmid dizertace, Zenodo ACPC 2014 logy, samotný
   `count_nl_infosets.tar` (máme jen ověřovací report), CSV↔ACPC log
   párování pro 9. disconnect hand.
4. Follow-up e-mail Johansonovi je připraven (odeslání na uživateli).
