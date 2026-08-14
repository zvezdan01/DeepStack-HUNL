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
