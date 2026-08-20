# DeepStack Table S4 — V102 exact seven-row center-line identity

Status: **NEW EXACT-TO-UNIT SIZE ARITHMETIC MILESTONE / ALL SEVEN PRINTED CENTERS HAVE ZERO RESIDUAL**

Treat the printed `k` cells as nominal thousand centers:

`48,000 / 100,000 / 61,000 / 126,000 / 204,000 / 360,000 / 555,000`.

The current exact reconstructed decision-node vector is:

`16 / 32 / 20 / 40 / 64 / 112 / 172`.

All seven satisfy, with **zero residual to the unit**:

`Size_center = 3250 * D_decision - 4000`.

Every one of the 21 pairwise slopes between rows is exactly `3250`.

This is stronger numerically than merely overlapping nearest-thousand bins.

However, the reconstructed trees obey:

`N_public = 3D - 3`
and
`E = 3D - 4`.

Therefore the same exact law is algebraically equivalent to:

`Size = (3250/3) * N_public - 750`
or
`Size = (3250/3) * E + 1000/3`.

So V99's identifiability warning still applies: exact arithmetic does not prove the private code
literally counted decision nodes.

The slope also has the exact decomposition:

`3250 = 3*1081 + 7`.

This shows algebraically why the exact river-hand width 1081 remains compatible with the center-line
identity through a small per-decision correction and offset, without identifying the storage layout.

## Held-out discriminator

The missing nonempty subset `1/2P+2P` has the frozen V87 prediction `D=146`.

The exact center law therefore predicts:

`3250*146 - 4000 = 470,500`.

That lands exactly on a nearest-thousand halfway boundary. An original DeepStack artifact containing
this omitted row would therefore test both the accounting family and the unknown tie/rounding
convention.

## Boundary

The paper prints `k` values. Interpreting `48k` as nominal center `48,000` does not prove the hidden
raw Size was exactly 48,000.

No Supremus, CPRG, Leduc, Libratus, or Pluribus semantics are imported as DeepStack facts.

## Validation

- V102 tests: **8/8 PASS**
- exact residuals: **0 / 0 / 0 / 0 / 0 / 0 / 0**
- pairwise slopes: **21/21 exactly 3250**
- held-out raw prediction: **470,500**
