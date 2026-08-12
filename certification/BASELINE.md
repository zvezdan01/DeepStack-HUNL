# PHASE 0 — BASELINE FREEZE

Date: 2026-08-12
Branch: `claude/huhl-deepstack-certification-tutg3b`

## CRITICAL BASELINE FINDING

**The repository `zvezdan01/quant-trade` is EMPTY at certification start.**

- `git log`: no commits on any branch
- `git ls-remote origin`: zero refs (no default branch, no tags)
- Working tree at session start: only `.git/`

Consequence: there is **no HUHL/DeepStack production solver, no CFR loop, no
gadget, no training pipeline, no weights/checkpoints, no configs, no seeds and
no existing test suite** in this repository. Statements in the test plan that
reference "current project", "F1/F2/F5 fixes", "480/480 tensors exact",
existing regression suites, or prior certifications could not be located here:

- Fixes F1/F2/F5: **NOT PRESENT** (no code exists to contain them)
- Prior DeepStack reconstruction fixes: **NOT PRESENT**
- Existing oracle/regression tests: **NOT PRESENT**
- Weights / checkpoints / training logs: **NOT PRESENT**

Everything project-dependent in the certification plan is therefore reported
as `NOT_TESTABLE_WITH_AVAILABLE_ORACLE` (object under test absent). What CAN
be certified — and was — is the reference-oracle infrastructure supplied via
uploads (original CFR+ author source, AGT raw .npz oracles, official Kuhn
CFR/CFR+ traces), plus independent cross-oracle triangulation.

## Baseline freeze actions taken

- This branch (`claude/huhl-deepstack-certification-tutg3b`) is the first ref
  ever pushed to the repository; the first commit is tagged
  `huhl-baseline-pre-certification` and contains ONLY certification
  infrastructure and immutable oracle copies (no solver code).
- No production math was created or modified.

## Environment / platform freeze

| Item | Value |
|---|---|
| OS | Linux 6.18.5-fc-v20 x86_64 (Ubuntu 24.04 userland) |
| CPU | Intel(R) Xeon(R) Processor @ 2.80GHz |
| gcc | 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1) |
| Python | 3.11.15 |
| numpy | 2.4.6 |
| scipy | 1.17.1 |
| pytest | 9.1.1 |
| GPU | none available (CPU-only container) |

## Uploaded reference oracles (immutable) — SHA-256

| File | SHA-256 |
|---|---|
| CFR_plus (1).tar.bz2 (Tammelin original CFR+ source) | `177fb8ac00bbf66abfb372c9d6e1465c334fada40ef0d305b5c80f00a8b10f0f` |
| davis20asupp.pdf | `81c538e7bb3f5eea6a144372ca69f5772442dbea99627a9bd5b4d4d090bae7b6` |
| game_theory_2023master.zip | `e21c3fa15bc0372f34df4c8612e67c09be1ca0a3cb78aded163873857aa15ca5` |
| algorithmic_game_theorymain.zip | `7ebd91f4c41c1c01b720ef42b4ad17a5af243e68a065f889c92d0106b479afc2` |

Extracted immutable copies live under `third_party/`:
- `third_party/CFR_plus/` — original author C source (kuhn.game, leduc.game, rng.c, ...)
- `third_party/agt_tests/` — AGT raw .npz oracles + `ref_cfr_kuhn.txt`, `ref_cfr_plus_kuhn.txt`
- `third_party/agt_templates/`, `third_party/agt_tasks/` — game/algorithm specs (templates are stubs — no reference implementation is included in AGT)
- `third_party/game_theory_2023_libs/` — course libs weeks 1–3 with their own unit tests

## Random seeds

No project seeds exist to freeze. All seeds used by newly generated oracles
are recorded next to each generated oracle and in `certification/results/`.
