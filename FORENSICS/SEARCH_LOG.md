# SEARCH LOG — DeepStack HUNL DataGenerator forensic hunt

Session: claude/generator-dat-pro-huhl-forenzic-rvclmx, started 2026-08-14 ~22:15 UTC.
Format: `[time] TOOL query/target -> result (POS/NEG)`. Negative results are kept deliberately.

## Network capability map (constrains all following searches)

| channel | status | evidence |
|---|---|---|
| WebSearch (server-side) | **WORKS** | returned arxiv/ualberta hits incl. snippet quoting pot intervals |
| git clone of any public GitHub repo (proxy anonymous lane) | **WORKS** | torch7, acpc, lifrordi/DeepStack-Leduc cloned earlier |
| WebFetch github.com HTML | **WORKS** | repo page fetch OK (stars/forks count) |
| WebFetch arxiv.org | **BLOCKED** (egress) | EGRESS_BLOCKED |
| WebFetch poker.cs.ualberta.ca | **BLOCKED** | EGRESS_BLOCKED |
| WebFetch zenodo.org | **BLOCKED** | EGRESS_BLOCKED |
| WebFetch web.archive.org | **BLOCKED** (tool refusal) | "unable to fetch" |
| curl arbitrary domains | **BLOCKED** (gateway 403 CONNECT) | arxiv.org:443 denied |
| pypi / files.pythonhosted.org | **WORKS** (noProxy direct) | pip install numpy/scipy earlier |

Consequence: raw artifact mirroring from arXiv/Zenodo/ualberta is NOT possible
from this container; those targets are pursued via (a) WebSearch snippet
evidence, (b) GitHub mirrors, (c) pypi packages. Recorded as capability
limits, not as artifact non-existence.

## Log

[22:18] curl arxiv.org e-print v1-v3 -> NEG (egress 403). Recorded above.
[22:19] WebSearch `DeepStack "1701.01724" supplementary pot sizes "19950"` ->
    POS: confirmed supplementary wording "pot sizes selected from the
    intervals ... [2000,6000) or [6000,19950] with uniform probability,
    followed by uniformly selecting an integer from within the chosen
    interval" (search snippet, Tier 2). Sources list incl.
    poker.cs.ualberta.ca/publications/17science-supplementary.pdf and
    arxiv pdf v1/v2/v3 (all still listing the paper).
[22:20] WebFetch poker.cs.ualberta.ca supplementary PDF -> NEG (blocked).
[22:20] WebFetch web.archive.org -> NEG (blocked).
[22:21] WebFetch github.com/lifrordi/DeepStack-Leduc -> POS: 949 stars,
    **225 forks** (fork network = enumeration target).
[22:21] WebFetch zenodo.org/records/13997158 -> NEG (blocked).
[22:5x] git full-clone lifrordi/DeepStack-Leduc -> POS(struct): only 2 commits
    (import 2017-04-05 + readme). NEG for hidden history.
[22:5x] fork sweep 223 forks (ls-remote) -> COMPLETE: 6 DIFF (andreayres
    unrelated-notebook, hmate9 from_turn.game, sjtuwy NLHE-HU adaptation
    Tier4, snarb cache, xiaoyjy scripts, mathemage 2 tree_builder patches),
    ~20 GONE (deleted accounts/forks, recorded in results file). NEG for
    original artifacts. Results: FORENSICS/SCRIPTS/fork_sweep_results.txt
[22:5x] mathemage/TensorCFR GitHub mirror -> POS Tier3: full 2886-commit
    history; generate_data --seed/--size; seed=offset+generation*size;
    Metacentrum #PBS scripts; per-seed dataset files. GitLab origin 403.
[22:5x] rggibson/open-pure-cfr -> POS Tier3: 4-seed --rng CLI, per-thread
    seeds[i]=base+1234+4*thread+i, init_by_array, RNG_SEEDS dumped to
    results; generate_hand -> ACPC dealCards directly; vendored rng.c
    BYTE-IDENTICAL (0e4a4d7a) to ACPC/Tammelin/DS copies; game.c differs
    (083ff9d9 = older ACPC revision).
[22:5x] kdub0 (Waugh) repos -> hand-isomorphism cloned (Tier3, unmined);
    subzero = website only NEG; kuhn3p noted.
[22:5x] happypepper/DeepHoldem -> POS Tier4: pot table min={100,200,400,
    2000,6000} max={100,400,2000,6000,18000} -> first bin literally
    constant 100 (singleton corroboration #3); max 18000 not 19950.
[22:5x] uoftcprg/phh-dataset cloned (16G) -> ACPC data EXCLUDED from git
    (Zenodo-only, egress-blocked); git history NEVER contained ACPC files
    (diff-filter=D sweep NEG). ACPC-2014 pot-histogram analysis BLOCKED
    from this container; precise pointer: DOI 10.5281/zenodo.10796885 v3.
[22:5x] lifrordi/webpage -> single HTML, NEG.
[22:5x] dspace.cuni.cz (Schmid dissertation PDF) -> EGRESS_BLOCKED; located
    URL recorded (bitstream 140094808.pdf). webdocs.cs.ualberta.ca also
    BLOCKED.
[23:0x] DeepStack-Leduc issues #5 (random situation solving, 2017-12) and
    #3 (Texas Hold'em, 2017-08) -> NEG: no maintainer replies visible in
    threads. Issue inventory pages 1-2 recorded (24 issue numbers, rest PRs).
[23:0x] issue #33 -> NEG no maintainer reply. computerpokercompetition.org
    -> EGRESS_BLOCKED. cdn.aaai.org (Refining Subgames PDF) -> BLOCKED.
[23:1x] Nyx via WebSearch -> Tier2 snippets: 2nd place ACPC 2014 HUNL TBR;
    card abstraction for base strategy (Schmid 2015/Johanson 2013 methods),
    fine-grained endgame without card abstraction ("Refining Subgames",
    AAAI). Schmid quote on modeling random moves (opponent exploitation).
[23:1x] kdub0/acpc_hand_converter -> POS convention: ACPC agent log naming
    `<agent>_2pn_<year>` (hyperborian_2pn_2014, act1_2pn_2016) => Zenodo
    2014 archive should contain nyx_2pn_2014 files.
[23:1x] "19950" code search -> only reimplementation repos (godmoves/
    DeeperStack cloned: datagen pot via tools:get_pot_size (18000-max DH
    line), resolving bet_sizing {0.5,1}; the ½-pot claim is a RESOLVING
    config there, not datagen — supports owner's note 21). noambrown/
    poker_solver + AI-Decision/DecisionHoldem noted for later mining.
[23:1x] PyStack -> Tier4 own params (suggested cfr_iters=800/skip=500,
    2M river+0.5M other situations on 1000 CPU nodes) — NOT original.
[15.8. ~19:4x] OWNER-SUPPLIED first-party testimony: Kevin Waugh e-mail
    (WAUGH_TESTIMONY.md) -> resolves B-localization (private, non-CPRG),
    AIVAT L4 localization (CPRG internal, unarchived), FCPA 3/9/27/81BB
    CONFIRMED, canonical-board indexing CONFIRMED, CPRG MT19937
    CONFIRMED with explicit DeepStack carve-out.
[16.8.] BIT-TESTY SVĚDECTVÍ + hlubší sweep:
  - FCPA chain test PASS 3/3 (tree+ACPC oracle+closed form) — viz
    JOHANSON_TESTIMONY.md a latest_audit/FCPA_CHAIN_TESTIMONY_TEST.txt.
  - hand-isomorphism: self-test PASS; kanonické velikosti 169/1755/
    16432/134459 + hand-index tabulka; **cross-test vs certifikovaný
    evaluátor: 200/200 izomorfních 5-card boardů permutačně IDENTICKÉ
    rank vektory (265 200 porovnání)**. Historie: psáno 2013, PR #1 od
    dmorrill10 (CPRG) 2014 — přímý CPRG dotyk s veřejnou knihovnou.
  - card_tools.c (Tammelin CFR+/Cepheus linie, TŘETÍ STRANA V REPU):
    obsahuje kanonickou suit-mapping indexaci (canonIndex, "smallest
    suit values") = kandidát č. 2 Johansonova svědectví JE v repu.
  - Cepheus: žádný oficiální github mirror; solver = Tammelin CFR+
    (BSD) dle CPRG stránky — máme vendorovaný.
  - NOVÉ KLONY: ericgjackson/slumbot2019 (run_rgbr, rgbr.cpp — RGBR
    fingerprint v ACPC ekosystému, Tier 3-4); krukah/robopoker
    (crates/arena/src/aivat.rs — komunitní AIVAT implementace, Tier 4 —
    kandidát na adaptaci pro test proti našemu 45k L3 oracle).
  - Johanson MSc 2007 (starší indexace): URL lokalizovány, egress-
    blokovány (kandidát na owner upload).
