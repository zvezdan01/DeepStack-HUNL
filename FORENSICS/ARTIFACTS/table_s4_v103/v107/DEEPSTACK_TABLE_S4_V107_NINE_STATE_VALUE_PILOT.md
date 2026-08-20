# DeepStack Table S4 — V107 nine-state value pilot

Status: **NEW OUT-OF-SAMPLE VALUE CHECK / CORPUS EFFECT SURVIVES, BUT DOES NOT YET CONVERGE TO PAPER**

V106 used five diagnostic river states and showed that averaging materially reduced the one-state
norm-shape mismatch.

V107 adds four fresh held-out boards/range seeds without changing the scaled solver protocol.

Protocol:

- 9 total states;
- 1081 legal private hands per state;
- sparse 100 iterations / omit 50;
- FULL 400 iterations / omit 200;
- same frozen structural witnesses.

## Held-out extension

The four new states by themselves give:

- call-only mean ratio MARE: **25.50%**
- mean-action-norms MARE: **28.50%**

So the new block does not simply reproduce the especially favorable early two-state dip.

## Combined nine-state result

- call-only: **21.64%**
- mean-action-norms: **24.99%**
- best tested common layout: **call_only**
- best mean ratio MARE: **21.64%**

The key result is qualitative:

**the corpus-averaging improvement survives out-of-sample extension, but the error appears to be
settling in the low-20% range rather than collapsing toward zero on nine states.**

That makes a 20-100-state Mac run worthwhile as a discriminator, not as a formality.

If the curve stays around ~20-25%, the missing mechanism is likely not just state averaging.
If it keeps falling materially, the historical 100-state corpus becomes the dominant suspect.

## Boundary

This remains a scaled directional pilot. It is not the historical 1000-vs-4000 Table-S4 experiment,
and these are not the unrecovered historical states.

No non-DeepStack implementation semantics are imported.

## Validation

- V107 tests: **6/6 PASS**
- old states: **5**
- fresh held-out states: **4**
- combined states: **9**
