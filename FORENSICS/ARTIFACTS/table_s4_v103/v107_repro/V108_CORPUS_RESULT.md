# V108 — korpusová studie norm-ratio otázky Table S4 (tato session)

Navazuje na V107 zadání: „rozšiř diagnostický korpus na 20/50/100 stavů
a zjisti, zda kumulativní MARE dál klesá."

## Reprodukce 9-state pilotu: NEPROVEDITELNÁ bez zdrojového skriptu

V107 checkpoint obsahuje jen výsledky, ne experimentální kód. Vyzkoušeno
7 receptů generování rangí × 5 variant solveru (alternace, lineární
průměrování, oba hráči, …) proti známým per-state normám (cíl
[7985.5, 383.5, 36.0] pro 2P call_only na 5sAdJdJsKh/seed 5) — žádná
kombinace nesedí (nejblíž [11408, 378, 19]). Recept rangí ze seedu
a mikro-konvence solveru zůstávají v sourozenecké session.
Agregační formule OVĚŘENA (průměr per-state norem → poměry → MARE).

## Vlastní implementace (nezávislá, plně dokumentovaná)

Zmrazené stromy z V99–V102 handoffu VERBATIM; certifikovaný evaluátor
(rychlé maticové river CFV ověřeno proti husté showdown matici na
1e-13); CFR+ (RM+, simultánní, uniformní průměr po skipu — konvence
našeho datagen pipeline); 1081-hand báze; 100/50 sparse, 400/200 FULL;
CFV/pot; stav k: board z default_rng(10000+k), range z default_rng(k)
uniformní na legálních rukou.

## Výsledek: křivka je PLOCHÁ

call_only mean-ratio MARE (kumulativně):
n=1: 1.340 · n=2: 1.074 · n=4: 1.092 · n=9: 1.077 · n=20: 1.066 ·
n=50: 1.114 · n=100: 1.133
(mean_action_norms 1.29–1.34, concat 1.94–2.09 — vše ploché od n≈2.)

## Závěry

1. **Průměrování přes stavy saturuje okamžitě** (od n≈2); rozšíření
   korpusu 9→100 nepřibližuje poměry k publikovaným hodnotám vůbec.
   Podmínka zadání pro spuštění historických 1000/4000 iterací
   („pokud se korpusový efekt dál zlepšuje") NENÍ splněna → neběženo.
2. **Chybějící mechanismus není velikost korpusu.** Rozdíl absolutní
   úrovně (moje ~1.07–1.13 vs sourozenecká ~0.22 na stejné stromové
   rodině) ukazuje, že dominantní je KONSTRUKCE STAVŮ — recept rangí
   (hladké uniformní range dávají málo špičaté chybové vektory, poměr
   L2/L∞ ~19 vs publikovaných ~8) a případně distribuce potů/boardů.
   To je konzistentní s V107 interpretací „the missing mechanism is
   likely not just state averaging" — a zpřesňuje ji: je to rozdělení
   stavů, ne jejich počet.
3. Doporučení: pro exact-protocol škálování je nutný V106/V107
   experimentální skript ze zdrojové session (recept rangí ze seedu +
   solver konvence). S ním lze korpus 100 stavů přepočítat za ~40 min
   touto infrastrukturou.

Artefakty: corpus_states.jsonl (100 stavů, per-menu per-layout normy),
corpus_cumulative.json, v107_fast.py, corpus_run.py.
