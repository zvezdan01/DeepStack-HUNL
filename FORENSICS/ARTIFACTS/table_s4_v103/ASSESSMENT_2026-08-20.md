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
