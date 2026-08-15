# DeepStack-Leduc — referenční implementace data generation

**Co to je.** `lifrordi/DeepStack-Leduc`, jediná veřejná implementace DeepStack pipeline.
Autor **Martin Schmid** (spolu-první autor paperu), 2 commity, oba 2017-04-05, „Initial commit"
(mapa týmu, nález T5). Lua/Torch7.

**Proč je to relevantní.** Obsahuje přesně ty soubory, které původní zadání huntu jmenovalo
jako fingerprinty: `data_generation.lua`, `data_generation_call.lua`, `main_data_generation.lua`,
`range_generator.lua`, `random_card_generator.lua`, `train.lua`, a datové soubory
`train.inputs` / `train.targets` / `train.mask`.

> **Trvalá výhrada:** Leduc **není HUNL oracle**. Má 6 karet, 2 kola, jiné sázení.
> Vše níže je *evidence o implementačním idiomu spoluautora*, ne o HUNL DataGeneratoru.
> Původní pravidlo „nepovažuj DeepStack-Leduc za HUNL oracle" **zůstává v platnosti.**

---

## ⭐⭐ L1 (P0, cíl D) — referenční generátor **vůbec neseeduje**

`main_data_generation.lua` — celý soubor:

```lua
local arguments = require 'Settings.arguments'
local data_generation = require 'DataGeneration.data_generation'

data_generation:generate_data(arguments.train_data_count, arguments.valid_data_count)
```

`Settings/arguments.lua` — **žádný parametr seed neexistuje.**

Grep `manualSeed|torch.seed|randomseed|seed` přes všechny `.lua`:

| Výskyt | Kontext |
|---|---|
| `card_tools.lua:76-80` | `get_random_range(board, seed)`, `seed = seed or torch.random()`, vlastní generátor `gen` — **v data-generation cestě se nepoužívá** |
| `next_round_value_test.lua:41` | `torch.manualSeed(0)` — **test**, ne produkce |

Data generation používá **globální torch RNG, neinicializovaný** → Torch se seeduje sám
z `/dev/urandom` nebo času při startu.

> **Vygenerovaný dataset není reprodukovatelný ani pro své vlastní autory.**
>
> **Dopad na cíl D:** hledáme originální `rngseed` DeepStack DataGeneratoru. Referenční
> implementace ukazuje, že **žádný takový parametr nemusel existovat**. To je nezávislé
> posílení nálezu #44 (znalost seedu nestačí) z opačné strany:
> **možná není co znát.**

---

## ⚠️ L2 (P0) — OPRAVA nálezu #20 v ledgeru

`Settings/arguments.lua`:

```lua
--- the number of iterations that DeepStack runs CFR for
params.cfr_iters = 1000
--- the number of preliminary CFR iterations which DeepStack doesn't factor into
--- the average strategy (included in cfr_iters)
params.cfr_skip_iters = 500

assert(params.cfr_iters > params.cfr_skip_iters)
```

`data_generation.lua` volá `Resolving()`, které **tytéž parametry používá** —
offline generování dat i online re-solving sdílí jeden solver a jednu konfiguraci.

> **V referenční implementaci se skip iterace v offline generování dat POUŽÍVAJÍ.**
> 1 000 iterací celkem, 500 zahozených.

### Co to dělá s nálezem #20

Ledger #20 tvrdí, na základě HUNL supplementu, že `omit_iters` patří **výhradně** online
solveru, a odvozuje z toho pravidlo *„nepřenášet `omit_iters` do offline generátoru"*.

Ten závěr **stojí na textu HUNL supplementu a ten se nemění**: supplement popisuje offline
generování jako „1,000 iterations of CFR⁺" bez zmínky o vynechávání, zatímco omission
popisuje jen u online hybridu (per-round tabulka `tab-lookahead`).

**Ale jediná dochovaná referenční implementace to dělá opačně.** Takže:

| | |
|---|---|
| Co říká HUNL supplement | offline = čisté CFR⁺, 1 000 iterací, o omission ani slovo |
| Co dělá Leduc reference | offline i online sdílí solver; `cfr_skip_iters = 500` platí pro obojí |

> **Pravidlo #20 tímto klesá z „potvrzeno z primárního zdroje" na „platí pro text
> supplementu, ale referenční implementace mu odporuje".** Pokud jste na něm postavili
> rozhodnutí ve svém generátoru, tohle je důvod ho znovu zvážit — ne nutně změnit,
> ale vědomě rozhodnout, kterému zdroji dáváte přednost.

---

## ⭐⭐ L3 (P0, cíl A) — žádné pot biny, a čitelný výklad `[100, 100)`

`data_generation.lua`:

```lua
--generating pot sizes between ante and stack - 0.1
local min_pot = arguments.ante
local max_pot = arguments.stack - 0.1
local pot_range = max_pot - min_pot

local random_pot_sizes = torch.rand(arguments.gen_batch_size, 1):mul(pot_range):add(min_pot)
```

S `params.ante = 100`, `params.stack = 1200` → **spojité uniform na `[100, 1199.9)`**.
**Žádné intervaly, žádné biny.**

### Strukturální paralela k HUNL

| | Leduc reference | HUNL supplement |
|---|---|---|
| dolní mez | `min_pot = ante = **100**` | první bin začíná na **100** (= big blind) |
| horní mez | `max_pot = stack − 0.1 = 1199.9` | poslední bin končí na **19950** (stack 20000 − 50) |
| tvar | jedno spojité uniform | pět intervalů, uniform mezi nimi i uvnitř |

> **Výklad `[100, 100)`:** v obou případech je `100` **minimální možný pot** (ante v Leducu,
> big blind v HUNL). Leduc ho bere jako dolní mez spojitého intervalu. HUNL ho vyčleňuje
> jako samostatný „interval" — a `[100, 100)` je zjevně míněno jako **degenerovaný bod
> pot = 100**, zapsaný chybnou závorkou místo `[100, 100]`.
>
> **To je nejsilnější dosavadní opora pro čtení `[100, 100]` (jediná hodnota), nikoli
> `[100, 200)`.** Zůstává to inference ze sourozenecké implementace, ne důkaz — ale je to
> první evidence, která mezi těmi dvěma čteními rozhoduje, a podporuje vaše původní
> pravidlo neopravovat to na `[100, 200)`.

---

## L4 (P1, cíl A) — range generator randomizuje lichý střed

`range_generator.lua`, `_generate_recursion`:

```lua
local rand = torch.rand(batch_size)
local mass1 = mass:clone():cmul(rand)
local mass2 = mass - mass1
local halfSize = card_count/2
--if the tensor contains an odd number of cards, randomize which way the
--middle card goes
if halfSize % 1 ~= 0 then
  halfSize = halfSize - 0.5
  halfSize = halfSize + torch.random(0,1)
end
self:_generate_recursion(cards[{{}, {1, halfSize}}], mass1)
self:_generate_recursion(cards[{{}, {halfSize +1, -1}}], mass2)
```

| Aspekt | Supplement R(S,p) | Leduc reference |
|---|---|---|
| `p₁` | uniformně z `(0, p)` | `mass * torch.rand()` ✓ shoda |
| dělení | `\|S₁\| = ⌊\|S\|/2⌋` | pro sudé ✓; **pro liché `torch.random(0,1)`** — střed padne náhodně |
| terminace | `\|S\| = 1` → `Pr(s) = p` | `cards:copy(mass)` ✓ shoda |
| řazení | podle hand strength | `non_coliding_strengths:sort()` v `set_board` |

> **Implementace je *náhodnější* než specifikace.** Supplement o randomizaci lichého středu
> **nemluví vůbec**. To je druhý zdroj nedeterminismu vedle remíz (#49) — a znovu potvrzuje,
> že bit-exact rekonstrukce není dosažitelná (#53), teď i z nezávislého směru.
>
> Remízová otázka zůstává otevřená: `sort()` v Torchi není dokumentovaně stabilní,
> takže pořadí stejně silných rukou určuje implementace řazení, ne kód.

---

## L5 (P1) — jeden board na celou dávku

`data_generation.lua`, hlavní smyčka:

```lua
for batch = 1, batch_count do
  local board = card_generator:generate_cards(game_settings.board_card_count)
  range_generator:set_board(board)
  ...
  for i=1,batch_size do   -- batch_size situací sdílí TENTÝŽ board
```

S `gen_batch_size = 10` sdílí **deset situací jeden board**. Situace uvnitř dávky tedy
**nejsou nezávislé**. Supplement o tom nic neříká.

## L6 — CFV cíle a normalizace

```lua
local root_values = resolving:get_root_cfv_both_players()
root_values:mul(1/pot_size)
```

Funkce **`get_root_cfv_both_players()`** — přesně jméno z původního fingerprint listu.
Hodnoty se dělí velikostí potu → shoda se supplementem: *„output values are interpreted
as fractions of the pot size"*.

Vstupy: `bucket_count * players_count + 1` (poslední feature = pot znormalizovaný
`pot_size / stack`). Cíle: `bucket_count * players_count`. Plus `mask` možných bucketů.
Ukládá se `torch.save` do `.inputs` / `.targets` / `.mask`.

## L7 — ostatní parametry reference

| Parametr | Leduc | HUNL (supplement) |
|---|---|---|
| síť | `nn.Linear(in,50), nn.PReLU(), nn.Linear(50,out)` | 7 vrstev × 500, PReLU |
| `cfr_iters` | 1 000 | 1 000 (turn) |
| `cfr_skip_iters` | **500** | v offline popisu neuvedeno (viz L2) |
| `gen_batch_size` | 10 | — |
| `train_data_count` | 100 | 10 000 000 (turn) |
| `bet_sizing` | `{1}` (jen pot bet) | fold, call, pot, all-in |
| `learning_rate` | 0.001 | 0.001, po 200 epochách 0.0001 |

---

## Shrnutí dopadu na cíle A–E

| Cíl | Co Leduc reference přidává |
|---|---|
| **A** range generator | Kompletní sourozenecká implementace. Randomizace lichého středu (L4) a výklad `[100,100]` (L3). **Neřeší** tie-breaking — ten zůstává na `sort()` |
| **B** DataGenerator | Kompletní sourozenecká implementace včetně smyčky, batchování a formátu výstupu |
| **C** raw samples | `Data/TrainSamples/PotBet/*.inputs/.targets/.mask` existují — **pro Leduc**, ne HUNL |
| **D** seed | **Reference neseeduje vůbec** (L1). Možná nikdy žádný seed nebyl |
| **E** cluster | Reference je jednoprocesová, žádný cluster kód |

**Cíle A–E pro HUNL zůstávají NOT FOUND.** Leduc reference je nejbližší dochovaný
příbuzný a mění interpretaci tří otevřených otázek — neposkytuje ale originální artefakty.
