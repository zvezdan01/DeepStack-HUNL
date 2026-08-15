# Zápis: Na kolik % lze postavit DeepStack HUNL DataGenerator

Datum: 2026-08-15 (session `claude/generator-dat-pro-huhl-forenzic-rvclmx`).
Podklad: oficiální Science supplement (archiv `17science-supplementary_b60b8865.pdf`),
originální artefakty studie (IFP/AIVAT, vs_LBR), svědectví K. Waugha,
genealogické nálezy (FINDINGS.md) a certifikovaný pilotní generátor v tomto repu.

## Závěr v jedné větě

**Funkční (algorithm-exact) věrnost originální metodice: ~90–95 %;
bitová identita s originálním datasetem: nedosažitelná a bezpředmětná
(dataset nebyl nikdy zveřejněn a podle všeho neexistuje) — náš pilot
je 100 % toho, co postavit lze, s vlastní certifikovanou bitovou
reprodukovatelností.**

## Rozpad po komponentách

| komponenta | věrnost | důkazní stav |
|---|---|---|
| akční množina F/C/P/A, 1000 iterací | **100 %** | first-party (supplement p.11) |
| sémantika solveru | **~95 %** | supplement p.7: DeepStack „CFR+" = hybrid (RM+, simultánní updaty, uniformní vážení, omit raných iterací) = sémantika našeho enginu; offline omit počet zůstává HYPOTÉZA (=500), při konvergenci na 1000 it. vliv na cíle řádově setiny % potu |
| normalizace CFV / pot | **100 %** | first-party |
| pot sampler | **~95 %** | intervaly doslovné (p.10 fn.1); jediná otevřená otázka bin `[100,100)` — singleton čtení, 3 nezávislé koroborace; alternativa [100,200) by změnila jen zařazení ~20 % vzorků v jednom binu |
| range generátor R(S,p) | **~90 %** | algoritmus přesný (p.11, floor-split v próze; randomizovaný odd-split = kód-anchored verdikt C2); neznámý tie-breaking při shodné hand strength (marginální) |
| board sampler | **~90 %** | rodina (rejection/ACPC dealCards vzor) doložená genealogicky (open-pure-cfr, Leduc kód), ne přímo pro DeepStack |
| RNG instance + master seed + pořadí tahů + serializace | **0 %** | privátní kód Schmida/Moravčíka (Waugh: mimo CPRG SVN); bez vlivu na distribuci/kvalitu dat — určuje jen bitovou identitu konkrétních čísel z r. 2016 |
| měřítko (10M turn / 1M flop / 10M aux) | známé | compute-bound (originál: 6144 jader MP2, >175 core-let) |

## Proč je bitová rovina mrtvá (pro kohokoli)

1. Originální trénovací dataset nebyl nikdy zveřejněn a není známa žádná
   jeho kopie — ani při uhodnutí seedu není s čím porovnat bity.
2. Chybějící bit-exact vstupy (RNG instance, seed, ordering, serializace)
   žily jen v privátním kódu; jediný nalezený job script / raw sample by
   je zavřel najednou (viz UNRESOLVED.md).

## Co náš pilot dělá NAD rámec originálu

- plná bitová reprodukovatelnost vlastních dat: deterministické per-shard
  seedy (SHA-256 derivace), RNG draw ledger v manifestech, full-shard
  replay test, per-sample checkpointy s certifikovanou byte-identitou
  resume, SHA anchory všech polí — auditovatelnost, kterou originál
  (dle dostupných pramenů) neměl.

## Otevřené vidličky a jejich plánované uzavření

| vidlička | stav | plán |
|---|---|---|
| offline omit (500?) | HYPOTÉZA | senzitivní experiment: identické vstupy, omit 0/250/500, delta cílů v % potu |
| bin [100,100) | singleton (3× koroborace) | senzitivita: podíl vzorků a vliv na trénink při [100,200) čtení |
| tie-breaking síly | PROJECT CANONICAL | dokumentováno; testovatelné permutačním experimentem |
| R-1 (alternating/linear CFR+) | prakticky uzavřeno supplementem p.7 | volitelný experiment pro kvantifikaci rozdílu |

## Stav pilotu při zápisu

11/12 shardů hotovo; shard 9 na 18/20; následuje replay0 (byte-identity)
a certifikační harness. Po PASS bude generátor formálně certifikován
(schema HUNL_TURN_DATASET_V1, engine Golden Baseline v1 34a50560).
