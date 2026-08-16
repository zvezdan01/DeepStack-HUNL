# AIVAT — L0 implementační specifikace (transkripce z prvoautorského vat.tex)

Zdroj: `FORENSICS/ARTIFACTS/arxiv_tex/aivat_v2/vat.tex` (arXiv AIVAT v2,
Burch, Schmid, Moravčík, Bowling). Tento dokument je věrná transkripce
rovnic do implementovatelné podoby pro two-player poker (Leduc, HUNL/HUHL).
Nic zde není domyšleno nad rámec textu; kde text nechává volnost, je to
označeno ⚠ OPEN.

## 1. Objekty

- Hráči `P = {1, 2}` + náhoda `p_c`. Stavy `h` = historie akcí od ∅,
  terminály `Z`, hodnoty `v_p(z)` (zero-sum: `v_1 = -v_2`).
- `π(h) = Π σ_{p(h')}(h', a)` — součin pravděpodobností všech aktérů na
  cestě; `π_p(h)` — jen faktory hráče `p`; pro množinu `T`:
  `π_T(h) = Π_{p∈T} π_p(h)`.
- `P_a` = hráči se známou strategií (vždy obsahuje `p_c`; v praxi
  `P_a = {p_c, x}` pro našeho agenta x). `P_o = P \ P_a` (soupeř).

## 2. Partition H (korekční členy)

`𝓗` je rozklad stavů `{h | p(h) ∈ P_a}` splňující:

1. ∀p ∈ P_o, ∀σ_p: `π_p(h) = π_p(h')` pro h, h' ve stejné části — stejná
   sekvence soupeřových information setů + stejné akce v nich.
2. Žádné h ⊏ h' uvnitř části ⇒ pro každý terminál z protíná část nejvýše
   jeden stav (unikátní pozorovaná akce `a_O`).
3. Rozšíření akcí: `A(H) = ∪_{h∈H} A(h)`, přičemž `σ(h,a) = 0` pro akce
   nedostupné v konkrétním h.

**Konkrétní volba pro Leduc/HUNL (autorská, §Experimental Results):**
část `H` = stavy se **shodným bettingem, shodnými public board kartami
a shodnými hole kartami hráčů v P_o**; liší se tedy jen privátní karty
hráčů v P_a. Pro `P_a = {p_c, x}` v HUNL: H = {všechny kombinace hole
karet hráče x kompatibilní s deskou} × pevný betting prefix. Chance uzly
(dealy) jsou také stavy s `p(h) = p_c ∈ P_a`, tj. i pro ně vznikají
korekční členy (MIVAT-like, ale s imaginary observations — viz §5 příklad
J♥: jako možnou kartu hráče uvažujeme i kartu, která ve skutečnosti padla
na board).

## 3. Korekční člen

Pro pozorovaný terminál `z` a část `H ∈ 𝓗`:

- pokud žádné h ∈ H není prefixem z: `k_H(z) = 0`;
- jinak s unikátní pozorovanou akcí `a_O`:

```
k_H(z) =  Σ_{a∈A(H)} Σ_{h∈H} π_{P_a}(h·a) · u_h(a)
          ───────────────────────────────────────────
                     Σ_{h∈H} π_{P_a}(h)

        -  Σ_{h∈H} π_{P_a}(h·a_O) · u_h(a_O)
          ─────────────────────────────────────
             Σ_{h∈H} π_{P_a}(h·a_O)
```

První zlomek = očekávaná hodnota PŘED volbou (přes všechny kompatibilní
historie a všechny akce, váženo reach pravděpodobnostmi P_a); druhý =
hodnota PO pozorované volbě. `E[k_H] = 0` (Lemma 1, dokázáno v textu
přes π_{P_o}(H)/π_{P_o}(H) trik + teleskopování).

## 4. Base value (imaginary observations)

Párový rozklad `𝓦` terminálů: z, z' ve stejné části ⟺

- ∀p ∈ P_o: `π_p(z) = π_p(z')`;
- hráč z P_a jednal v z ⟺ jednal v z';
- pokud jednal, poslední P_a-stavy na cestách z a z' leží ve stejné
  části 𝓗.

(Poslední dvě podmínky brání dvojímu započtení mezi base value a
korekčními členy — bias nevzniká, ale rostl by rozptyl.)

Base hodnota pro pozorovaný `z ∈ W`:

```
base(z) = Σ_{z'∈W} π_{P_a}(z') · v_p(z')  /  Σ_{z'∈W} π_{P_a}(z')
```

V pokeru: přehrání terminálu se **všemi možnými privátními kartami**
hráčů v P_a, váženo pravděpodobností jejich držení při pozorované hře
(„Example 3: Private Information", Bowling et al. 2008).

## 5. Odhad

```
AIVAT(z) = base(z) + Σ_{H∈𝓗} k_H(z)          (rovnice 1, eqn:vat)
```

Nestrannost: base je nestranný IS odhad; Σ k_H má E = 0 (Theorem 1).
⚠ Rozdíl proti „MIVAT+IO": v AIVAT každý korekční člen uvažuje historie
kompatibilní se stavem V MÍSTĚ rozhodnutí (ne s terminálem) — proto J♥
příklad výše.

## 6. Hodnotové funkce u_h(a) (autorská instanciace)

- Self-play hodnoty z varianty **MCCFR** (Lanctot et al. 2009): pro
  hráče p_x a část H se přes všechny iterace průměrují pozorované
  hodnoty soupeře p_y:
  `w_H(a) ≈ Σ_h π_{p_x}(h·a)·E[v_{p_y}(h)] / Σ_h π_{p_x}(h·a)`.
- Zero-sum ⇒ `u_h(a) = -w_H(a)` ∀h ∈ H (u je konstantní na části H).
- HUNL: `w_H(a)` z řešení **malé abstrakce s 8M information sety**
  (odkazy psopti + Ganzfried14) — hrubý odhad shodný přes mnoho částí.
  ⚠ OPEN: přesná abstrakce/parametry MCCFR nejsou v textu specifikovány.
- u_h(a) smí být LIBOVOLNÁ pevná funkce — nestrannost na ní nezávisí,
  jen míra redukce rozptylu.

## 7. Pozice (střídání pozic v matchi)

Modeluje se rozšířenou hrou: úvodní 50/50 chance event přiřadí pozici,
a **i pro tento event se přidá AIVAT korekční člen** (u = hodnota pozice).

## 8. Implementační kontrakt (co musí kód zachovat)

1. Reach váhy π_{P_a} počítat z PŘESNÉ strategie agenta (tytéž pravděpodobnosti
   v base i korekcích); soupeřova strategie se nikde nevyskytuje.
2. Korekční člen pro každý P_a-uzel na pozorované cestě (akce agenta
   + každý chance deal + pozice), nikdy pro uzly soupeře.
3. V části H enumerovat všechny hole-card kombinace agenta nekolidující
   s pozorovanými public kartami a kartami P_o hráčů (u chance členů se
   kolize posuzuje k stavu PŘED dealem — viz J♥).
4. σ(h,a) = 0 pro akce nelegální v konkrétním h (property 3) — např.
   all-in větve dostupné jen pro některé stack konfigurace se v jiných
   historiích váží nulou, ne vynecháním.
5. base(z) přehrává showdown/fold hodnoty se všemi kartami agenta;
   vyloučit terminály pokryté korekčními členy dle podmínek 𝓦.
6. Jednotky: čipy na hru; agregace = prostý průměr přes hry.

## 9. Ověřené kotvy (naše session)

- `FORENSICS/SCRIPTS/aivat_verify.py`: na publikovaných DeepStack IFP
  CSV je per-hand identita `chips = aivat + Σ korekce` splněna ≤ 5e-5;
  agregáty 491.50 (AIVAT) / 485.74 (chips) mbb/g, σ 4.4 vs 23.6 — tj.
  ~81% redukce SD, konzistentní s ~68% na horší value funkci z vat.tex.
- Leduc self-play tabulka (Fig. 3): chips SD 3.513 → AIVAT(P_a={p_c,x})
  SD 0.00643 (−99.8 %) — použitelné jako regresní cíl pro naši Leduc
  implementaci.
- open_pvat (DIVAT rodina, project_uoapoker r6077) zrekonstruován a
  golden test byte-identical — předchůdcovská linie L4.

## 10. Hranice L0

Tato spec je **algorithm-exact** transkripce; NENÍ to produkční kód CPRG
(ten se nedochoval — viz UNRESOLVED.md). ⚠ OPEN položky: přesná HUNL
value abstrakce (8M infosetů), MCCFR varianta/parametry/seed, produkční
implementační detaily (pořadí enumerace, zaokrouhlování float/double).
