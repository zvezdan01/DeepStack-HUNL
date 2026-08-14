# FORENSICS — DeepStack HUNL DataGenerator artifact hunt

Mission: locate original or near-original artifacts (A. range generator
source, B. DataGenerator/job scripts, C. raw training samples, D. RNG
seed/config, E. cluster manifests/logs) that reduce bit-exact unknowns
of the original DeepStack HUNL offline training-data pipeline.

- FINDINGS.md — live findings, evidence-tiered
- EVIDENCE_TABLE.csv — artifact register (id, provenance, SHA, tier)
- SEARCH_LOG.md — every query incl. negative results + network capability map
- UNRESOLVED.md — current exact unknowns
- ARTIFACTS/ — preserved originals (nothing modified)
- MIRRORS/ — mirrored materials
- SCRIPTS/ — sweep/analysis scripts (fork_sweep.sh etc.)

Rules: primary sources over summaries; community reimplementations are
Tier 4 fossils, never oracles; every artifact gets SHA-256; negative
results are recorded.
