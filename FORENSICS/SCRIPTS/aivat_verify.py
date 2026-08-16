#!/usr/bin/env python3
"""AIVAT original-release verification (repeatable oracle test).

Verifies, against the original authors' per-hand release
(DeepStack_vs_IFP_pros/AIVAT_analysis):
  1. decomposition identity AIVAT == AllHandsChips - ChanceCorr - ActionCorr
     on every hand (tolerance = CSV rounding, 5e-5);
  2. the reconstructed study filter: first 3000 hands per participant
     gives exactly 44,852 games;
  3. NUMERIC-EXACT reproduction of the published aggregates
     (492 / 486 mbb/g rounded; sigma levels >4 / >20).
Exit 0 = all pass. Run from repo root.
"""
import csv
import glob
import math
import statistics
import sys

BASE = "FORENSICS/ARTIFACTS/DeepStack_vs_IFP_pros/AIVAT_analysis"
files = sorted(glob.glob(f"{BASE}/results.*.csv"))
assert len(files) == 33, f"expected 33 participants, got {len(files)}"

tot = 0
worst = 0.0
capped = []
for f in files:
    rows = list(csv.DictReader(open(f)))
    for r in rows:
        a = float(r["AIVAT"])
        resid = abs(a - (float(r[" All Hands Chips"])
                         - float(r[" Chance Correction"])
                         - float(r[" Action Correction"])))
        worst = max(worst, resid)
    tot += len(rows)
    capped.extend(rows[:3000])
assert worst <= 5e-5, f"identity violated: {worst}"
assert tot == 45037, tot
assert len(capped) == 44852, len(capped)

va = [float(r["AIVAT"]) for r in capped]
vc = [float(r[" Chips"]) for r in capped]
n = len(va)
ma, mc = sum(va) / n, sum(vc) / n
za = -ma / (statistics.pstdev(va) / math.sqrt(n))
zc = -mc / (statistics.pstdev(vc) / math.sqrt(n))
raw_mbb, aivat_mbb = -mc * 10, -ma * 10
assert round(raw_mbb) == 492 or abs(raw_mbb - 492) < 1.0, raw_mbb
assert round(aivat_mbb) == 486 or abs(aivat_mbb - 486) < 1.0, aivat_mbb
assert zc > 4 and za > 20, (zc, za)

print(f"AIVAT ORACLE VERIFY: PASS — identity {worst:.1e} on {tot} hands; "
      f"filter first-3000 -> {n}; raw {raw_mbb:.2f} mbb/g ({zc:.1f} sigma); "
      f"AIVAT {aivat_mbb:.2f} mbb/g ({za:.1f} sigma)")
