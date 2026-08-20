# DeepStack Table S4 — V105 inverse decision-count lock

Status: **NEW INVERSE-VALIDATION MILESTONE / EACH OF THE SEVEN STRUCTURAL COUNTS IS UNIQUELY RECOVERED FROM SIZE**

V104 showed that the row labeling is unique among all permutations.

V105 asks a different adversarial question:

> If one reconstructed decision count is wrong, can we change it to another integer and still explain
> every published Size cell by some affine law after allowing full nearest-thousand uncertainty?

## Test

For each of the seven rows in turn:

1. hold the other six decision counts fixed;
2. replace the held-out count by every integer `1..500`;
3. for each candidate, allow an entirely new real affine slope and intercept;
4. allow every printed Size value to float anywhere in its full integer publication bin
   `[center-500, center+499]`;
5. ask whether all seven rows can still be satisfied simultaneously.

Total candidate structural vectors tested:

`7 * 500 = 3,500`.

## Result

For every row, exactly one integer survives.

- 2P -> **16**
- 1/2P -> **32**
- P -> **20**
- 1/2P+P -> **40**
- P+2P -> **64**
- 1/2P+P+2P -> **112**
- FULL -> **172**

These are exactly the current reconstructed counts.

Every `D-1` and `D+1` neighbor is rejected.

Thus, inside the affine-family hypothesis, the published rounded Size values do not merely correlate
with the reconstructed structure: they **invert back to the same integer structural vector**.

## Why this is stronger

V102 was forward fitting: reconstructed counts -> exact Size centers.

V103 held rows out.

V104 randomized row labels.

V105 reverses the direction:

**Size bins -> unique integer decision counts.**

Even after re-optimizing slope and intercept for every candidate, no alternative integer count from
1..500 survives for any row.

## Boundary

This does not prove DeepStack's private Size counter literally counted decision nodes. Public nodes and
edges remain algebraically linked to D on this reconstructed family.

It is instead a strong consistency test of the reconstructed structural fingerprint.

No Supremus, CPRG, Leduc, Libratus, or Pluribus implementation semantics are imported as DeepStack
facts.

## Validation

- V105 tests: **6/6 PASS**
- candidate vectors tested: **3,500**
- rows uniquely recovered: **7/7**
- adjacent-count alternatives rejected: **14/14 where positive**
