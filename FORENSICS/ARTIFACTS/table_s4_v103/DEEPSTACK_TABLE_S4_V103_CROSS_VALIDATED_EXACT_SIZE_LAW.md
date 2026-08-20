# DeepStack Table S4 — V103 cross-validated exact Size law

Status: NEW CROSS-VALIDATION MILESTONE

The six sparse rows alone imply the exact nominal-center law:

    Size_center = 3250 * D_decision - 4000

Sparse decision-node counts:
16 / 32 / 20 / 40 / 64 / 112

Published nominal centers:
48,000 / 100,000 / 61,000 / 126,000 / 204,000 / 360,000

Holding FULL out entirely, D_FULL=172 predicts:

    3250 * 172 - 4000 = 555,000

which equals the published FULL value 555k exactly.

Cross-validation:
- all 15/15 two-row training pairs among the six sparse rows imply the same line and predict FULL exactly;
- all 7/7 leave-one-out published-row tests have zero nominal-center residual.

Held-out missing subset prediction:
- 1/2P + 2P: D=146
- predicted nominal Size center = 470,500.

Boundary:
The source prints k values. This exact nominal-center identity does not prove that the hidden raw Size
values equal the nominal centers, nor does it identify the private operational Size counter.
