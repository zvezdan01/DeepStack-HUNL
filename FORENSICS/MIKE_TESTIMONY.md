# „Mike" (CPRG) — first-party svědectví (e-mail vlastníkovi, 2026-08-16)

Evidence class: **Tier 2 / CONFIRMED (first-party recollection)**. Autor se
podepisuje „Mike"; z kontextu (CPRG, PhD dokončen před spuštěním
DeepStacku, odchod týmu do DeepMind 2017, odkaz na „Dr. Bowlinga jako
posledního člena na univerzitě") jde velmi pravděpodobně o Michaela
Johansona [INFERENCE — identita neověřena artefaktem]. Paměťové výroky
(„nejsem si jistý", „nevím") značeny.

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
