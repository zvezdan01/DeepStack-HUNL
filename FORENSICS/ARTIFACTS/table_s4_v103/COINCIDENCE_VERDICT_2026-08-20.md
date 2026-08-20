# Table S4 size law — test náhodnosti (V106, tato session)

Otázka vlastníka: „je jen náhoda, že to všechno sedí?"
Odpověď: **NE. Pravděpodobnost náhody je řádu 10⁻⁷ ve dvou nezávislých
nulových modelech.** Skript: `coincidence_tests.py`, výsledky
`coincidence_results.json`.

## Rozklad (exaktní, bez simulace)

gcd všech párových rozdílů sedmi publikovaných Size hodnot je **13 000**:
S = 48 000 + 13 000·k, k = [0,4,1,6,12,24,39]; D = 16+4k je jen
reparametrizace. Celý „zákon" je ekvivalentní téhle mřížkové struktuře.

## P1 — mřížkový test (bez jakékoli hypotézy o stromech)

Nulový model: 7 nezávislých násobků 1 000 v ±30% pásmech kolem
publikovaných hodnot. MC 2×10⁶:
- P(gcd párových rozdílů ≥ 13 000) ≈ **5×10⁻⁷**
- P(gcd ≥ 3 250) ≈ 3.6×10⁻⁴
Publikovaná tabulka tedy nese exaktní vnitřní mřížku, která náhodným
zaokrouhleným číslům prakticky nevzniká.

## P2 — ukotvený test (linie fixována PŘEDEM nezávislými počty)

Přímka a=3250, b=−4000 je určena už DVĚMA nezávisle odvozenými počty
rozhodovacích uzlů z našeho enumerátoru ((16, 48k), (20, 61k) — river,
minimální pot 200, neklesající frakce; derivace nezávislá na Size).
Nulový model pro zbylých 5 publikovaných hodnot (nezávislé násobky
1 000, ±30 %): P(třetí ověřený počet 32 trefí přesně 100 000 A všechny
4 vícefrakční hodnoty padnou do celočíselné mřížky) =
**2×10⁻⁷ MC / 5.7×10⁻⁷ analyticky** (1/61 × (1/13)⁴).

## P3 — look-elsewhere (kolik JINÝCH zákonů by taky „vyšlo")

Sweep 128 kombinací (4 varianty pravidel × 8 potů × 4 typy čítačů):
20 kombinací uspělo — ale VŠECHNY jsou algebraicky TENTÝŽ zákon:
- terminály = 2D−2 ⇒ 1625·(2D−2)−750 ≡ 3250·D−4000 (identita),
- decision při potu 600 = D−4 ⇒ 3250·(D−4)+9000 ≡ 3250·D−4000 (identita),
- pre-call varianta při potu 1000 reprodukuje přímo [16,32,20].
Žádný alternativní (neekvivalentní) zákon ve sweepu neexistuje; „edges"
čítač a striktně rostoucí pravidla nevyhovují nikdy. Look-elsewhere
efekt je tedy ~1 rodina zákonů, ne 20 nezávislých.

Tohle současně REPRODUKUJE „V99 algebraic ambiguity" zdrojové session:
decision/terminal/(pot-posunuté) čítače jsou na této rodině stromů
afinně svázané — zákon je jednoznačný jako třída ekvivalence, nikoli
jako konkrétní čítač.

## Verdikt a klasifikace

1. **Mřížka S = 48 000+13 000·k: CONFIRMED strukturní invariant
   publikované Table S4** (p ≈ 5×10⁻⁷ proti náhodě). Autoři „Size"
   téměř jistě počítali deterministicky z celočíselného strukturního
   čítače lookahead stromu.
2. **Ukotvený zákon 3250·D−4000 s D z nezávislého enumerátoru
   (jednofrakční menu): CONFIRMED** (p ≈ 2–6×10⁻⁷).
3. **Který přesný čítač** (decision vs terminal vs posunutá
   parametrizace; a derivace vícefrakčních 40/64/112/172): OPEN —
   třída ekvivalence je určena, reprezentant ne. K rozhodnutí by
   pomohly V99–V102 skripty zdrojové session.
