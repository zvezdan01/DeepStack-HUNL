# UNRESOLVED — exact current unknowns (DeepStack HUNL DataGenerator)

Updated 2026-08-14. Each item stays here until a Tier ≤2 artifact
resolves it. See also certification/results/HUNL_DATAGEN_PROVENANCE_NOTES.md.

- [100,100) meaning (H1 [100,200) vs H2 singleton-100 vs H3 transcription
  vs H4 deliberate degenerate vs H5 boundary omitted) — present in ALL
  arXiv versions + Science supplement per owner's notes; arXiv TeX source
  comparison NOT possible from this container (egress).
- RNG implementation of the original generator (MT19937/ACPC family has
  Tier-3 genealogy support only)
- master seed
- worker/job seed derivation (CPRG fingerprints: base+1234+4*thread+i;
  TensorCFR: offset+generation*size; ACPC: explicit CLI seed — none
  proven for DeepStack itself)
- RNG call ordering
- board/card sampler of private HUNL generator (released DeepStack-Leduc uses Torch7 rejection sampling uniformly without replacement; HUNL private implementation still unobserved)
- 1326 hand enumeration order
- tie-breaking in hand-strength sorting
- hand-strength *definition* RESOLVED by supplement: P(strictly beats a uniform compatible hand in the current public state); private tie/order implementation remains unresolved
- blocker handling in R(S,p) is mathematically fixed by the current public state and independently certified in V2; private serialization/index order remains unresolved
- range normalization RESOLVED by R(S,1): mass sums to 1; V2 certifies blocked mass = 0 and f32 sum error <2e-6
- exact private HUNL OFFLINE solver implementation remains unobserved; strongest reconstruction evidence is DeepStack hybrid (RM+, simultaneous, uniform) plus released DeepStack-Leduc DataGeneration using the same resolve_first_node path
- offline skip/omit count is not stated separately for HUNL training targets; 500 is HIGH-CONFIDENCE RELEASED-CODE-ANCHORED (online HUNL turn schedule = 1000/500; released Leduc DataGeneration = 1000/500), not author-explicit for the private HUNL generator
- floating point precision
- parallel reduction order
- serialization format of original samples
- job allocation across 6,144 cores (256-node PBS inference unproven)
- original bucket centroids/mapping (for NN input reproduction)

## Resolved/refined by Waugh testimony (2026-08-15, Tier 2)
- DataGenerator location: RESOLVED — separate private program
  (Schmid/Moravčík), NOT in CPRG SVN; hunt re-targeted.
- CPRG-internal RNG: CONFIRMED MT19937 (all internal code);
  DeepStack-side RNG instance remains UNKNOWN — Torch7 THRandom
  hypothesis gains standing (DeepStack stack was Torch7/Lua).
- FCPA integer raise-to chain 3/9/27/81 BB: CONFIRMED (CPRG internal).
- Canonical board indexing (CPRG no-limit storage): CONFIRMED;
  private-card canonicalization uncertain.
- AIVAT implementation location: CPRG internal code (project_uoapoker
  lineage, unarchived, never git-converted) — L4 public-release
  likelihood LOW.

## Doplněno svědectvím „Mike" (CPRG, 2026-08-16, Tier 2)
- DeepStack = nový repozitář od nuly (2. nezávislé potvrzení) →
  B-artefakt veřejně prakticky nedosažitelný; formální cesta: dotaz na
  Dr. Bowlinga (očekáváno „proprietární").
- CPRG hand indexing: 2 kandidátní systémy (kdub0/hand-isomorphism vs
  starší CFR-éra indexace) — pro CPRG artefakty; DeepStack 1326
  ordering zůstává UNKNOWN (od-nuly kód).
- CFRPLUS_HOLDEM_NOLIMIT_FCPA = pravděpodobně strategy-file jméno
  (gamedef-agnostický solver).

## 2026-08-16 Schmid update
- **CLOSED:** whether offline target generation used a skip/burn-in window.
  Martin Schmid recalls that skip iterations were always used.
- **STILL OPEN:** the exact private-HUNL skip count. `500` is
  RELEASED-CODE-ANCHORED (DeepStack-Leduc), not explicitly confirmed by the
  email.
- **STILL OPEN / strengthened:** exact river card-bucket abstraction used by
  original play-time turn resolves. Zarick et al. (2020) explicitly state that
  DeepStack used bucketed river actions and that the details were never
  presented.
