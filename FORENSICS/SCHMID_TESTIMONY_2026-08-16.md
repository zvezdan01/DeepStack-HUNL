# Martin Schmid testimony — 2026-08-16

## Provenance
Direct email reply from Martin Schmid to Adam Amrich, received 2026-08-16.
This is first-party author testimony. The exact email remains outside the source
repository; this note records only the claims relevant to the reconstruction.

## Author-confirmed claim
Schmid's answer to the question about CFR+ iterations used when generating
training targets was, in substance:

> He thinks skip iterations were always used.

### Evidence status
- **Existence of a skip/burn-in window in DeepStack target generation:**
  **AUTHOR-CONFIRMED (recollection)**.
- **Exact private-HUNL skip count:** **NOT author-confirmed by this email**.
- `500` remains the reconstruction value because the released
  Schmid/Moravcik DeepStack-Leduc code uses `cfr_iters=1000` and
  `cfr_skip_iters=500`, and the released datagen path consumes that setting.
  Status: **RELEASED-CODE-ANCHORED / exact HUNL count unresolved**.

This replaces the old fork "skip vs no skip". Future sensitivity experiments
should compare candidate *skip counts*, not whether early iterations were
included at all.

## Author recommendation
Schmid recommended the follow-up paper:

Ryan Zarick, Bryan Pellegrino, Noam Brown, Caleb Banister,
"Unlocking the Potential of Deep Counterfactual Value Networks",
arXiv:2007.10442 (2020).

A copy supplied by the project owner is vendored at:
`third_party/papers/2007.10442v1.pdf`.

## Scope warning
This testimony does **not** establish the exact private HUNL RNG, seed schedule,
river bucketing, target serialization, or the exact numerical skip count.
