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
