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
| L0 paper-equation | AIVAT equations spec | PARTIAL — decomposition + sign conventions CONFIRMED from release README; full per-term equations still to be transcribed from arXiv 1612.06915 (egress-blocked here; snippets + owner materials) |
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
