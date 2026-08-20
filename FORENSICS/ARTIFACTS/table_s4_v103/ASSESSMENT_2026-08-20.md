# Posouzení checkpointu "Table S4 V103 size law" (2026-08-20)

Upload: DeepStack_Table_S4_V103_checkpoint.zip
SHA-256: 4bf0d2f3c3701f1c931a2e61a1afcf13030c7391fcdb7d89fd9d5f2291260f1f

## Co je POTVRZENO (ověřeno v této session)

1. Publikované hodnoty sedí prvoautorsky: arXiv ds_v3 appendix.tex,
   tabulka `tab:cfvs` (= supplement Table S4; river, 100 náhodných
   situací, 1000 CFR iterací, neklesající frakce potu):
   48k/100k/61k/126k/204k/360k a FULL 555k — přesně jak checkpoint uvádí.
2. Aritmetika: všech 7 hodnot leží PŘESNĚ na přímce S = 3250·D − 4000,
   ekvivalentně S + 4000 ≡ 0 (mod 3250) pro všech 7 řádků. Pro násobky
   1000 je šance jednoho řádku 1/13; sedmi nezávislých ≈ 2e-7 —
   kolinearita je téměř jistě strukturní vlastnost autorova výpočtu
   "Size" (lineární v nějakém celočíselném čítači, slope 3250,
   offset −4000). To je reálný, netriviální forenzní nález.

## Co je HYPOTÉZA (neprokázáno checkpointem)

3. Checkpoint D hodnoty (16/32/20/40/64/112/172) NEDERIVUJE — dodaný
   pytest je má natvrdo a "cross-validace 15/15 párů + leave-one-out"
   je při exaktní kolinearitě tautologická (každé 2 body určují tutéž
   přímku). Skutečný obsah nálezu je kolinearita sama, ne křížová
   validace. D mohla vzniknout zpětně jako (S+4000)/3250.
4. Interpretace "D = počet rozhodovacích uzlů sparse stromu": náš
   nezávislý enumerátor (count_decisions.py zde) reprodukuje PŘESNĚ
   16/32/20 pro jednofrakční menu {2P},{1/2P},{P} při minimálním river
   potu 200 a neklesajících frakcích — to interpretaci podporuje. Ale
   žádná ze 4 testovaných přirozených variant pravidel (neklesající /
   striktně rostoucí / nerostoucí / frakce z potu před callem; poty
   100–400) nedává vícefrakční hodnoty 40/64/112/172 (dostáváme např.
   100/48/184/2348). Vícefrakční D tedy zůstává NEOVĚŘENÁ.
5. Predikce 470 500 pro {1/2P, 2P} (D=146) visí výhradně na bodě 4.

## Doporučení

Vyžádat od zdrojové session derivační skript pro D (pokud existuje);
do té doby klasifikace: kolinearita = CONFIRMED (first-party čísla),
"size law přes decision uzly" = HYPOTHESIS (částečná podpora u
jednofrakčních menu).

## Dodatek: V104 + V105 (přijato a nezávisle ověřeno 2026-08-20)

Upload V105 zip SHA-256:
771cd297a87ea206fcaaba7795bf7aab924de6985f1bb43d50a5636782f02d07
(vendorováno ve v104_v105/).

Nezávislá re-verifikace vlastní implementací (exact Fraction 2D-LP
feasibilita, včetně dx=0 případu, který dodaný kód přeskakuje):

- V104: z 5 040 permutací přiřazení Size↔řádek je afinně feasibilní
  (i s plnou ±500 rounding volností) PŘESNĚ 1 — skutečné přiřazení. ✓
- V105: při držení šesti D a skenu kandidáta 1..500 přežívá pro FULL
  jen 172 a pro 2P jen 16 (ostatní řádky dle dodaného pytestu 6/6,
  reprodukován zde). ✓

Interpretace: tato dvojice KOREKTNĚ vyvrací námitku „generická náhoda
zaokrouhlených čísel" pro PÁROVÁNÍ hodnot — afinní vztah je numericky
rigidní (i široké ±500 biny určují celočíselný vektor jednoznačně).

Co se NEMĚNÍ: oba testy jsou podmíněné vektorem D, který ani zde není
derivován (v testech natvrdo). Rigidita afinního vztahu je při exaktní
kolinearitě očekávatelná (2 stupně volnosti vs 7 vazeb) — V104/V105 ji
kvantifikují, ale nedodávají nezávislou provenienci D. V104 boundary
sekce sama odkazuje na „V99's algebraic ambiguity between decision
nodes, public nodes, and edges" — tj. derivační rodina stromů ve
zdrojové session EXISTUJE. Klíčový chybějící artefakt zůstává:
skripty V99–V102 (derivace 16/32/20/40/64/112/172 ze stromu, včetně
rozlišení decision/public/edge čítače).

Klasifikace beze změny: kolinearita+rigidita = CONFIRMED (derived,
Tier 3); „D = decision-node counts konkrétní rodiny stromů" =
HYPOTHESIS s částečnou podporou (jednofrakční menu při potu 200).
