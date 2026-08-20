#!/usr/bin/env python3
"""Coincidence battery for the Table S4 size law (V106, this session).

Question: is the observed structure explainable as a rounded-number
accident?  Three independent probes, none assuming the sibling session's
D vector:

  P1  lattice probe   - all 7 published sizes lie on 48000 + 13000*k.
      Null: sizes are independent multiples of 1000 near the published
      magnitudes.  MC estimate of P(pairwise-diff gcd >= 13000).
  P2  anchored probe  - the line is FIXED in advance by two
      independently derived tree counts ((16,48k),(20,61k) from our
      river enumerator at min pot 200, non-decreasing fractions); the
      third verified count (32) must then hit 100k exactly and the four
      remaining published sizes must land on the integer-D lattice.
      Null: those five sizes are independent multiples of 1000 within
      +-30% of their published values.
  P3  look-elsewhere  - how many (rule variant x pot x counter type)
      combos reproduce the same success as (non-decreasing, pot 200,
      decision nodes)?  Quantifies selection freedom on our side.
"""
import json
import random
from fractions import Fraction as F
from functools import reduce
from math import gcd

S = [48000, 100000, 61000, 126000, 204000, 360000, 555000]
MENU_1 = {"2P": [F(2)], "halfP": [F(1, 2)], "P": [F(1)]}

# ---------------------------------------------------------------- P1 --
def p1(trials=2_000_000, seed=1):
    rng = random.Random(seed)
    hits13 = hits3250 = 0
    for _ in range(trials):
        v = [1000 * rng.randint(round(0.7 * s / 1000), round(1.3 * s / 1000))
             for s in S]
        g = reduce(gcd, [abs(a - b) for i, a in enumerate(v) for b in v[i+1:]])
        if g >= 13000:
            hits13 += 1
        if g >= 3250:
            hits3250 += 1
    return hits13 / trials, hits3250 / trials


# ------------------------------------------------- river enumerators --
def make_counter(mode):
    """Returns fn(menu, pot, stack) -> dict of counters."""
    def count(menu, pot, stack):
        c = {"decision": 0, "terminal": 0, "edges": 0}
        def rec(pot_now, faced, fmin, first, cap, pre_pot):
            c["decision"] += 1
            n_edges = 0
            if faced > 0:
                c["terminal"] += 1; n_edges += 1              # fold
            c["terminal"] += 1; n_edges += 1                  # call/check-end
            if faced == 0 and first:
                rec(pot_now, 0, fmin, False, cap, pot_now); n_edges += 1
            idxs = (range(fmin, len(menu)) if mode != "noninc"
                    else range(0, fmin + 1))
            for i in idxs:
                f = menu[i]
                base = pre_pot if mode == "pre" else pot_now
                amt = f * base
                if amt < cap:
                    nxt = i + 1 if mode == "strict" else i
                    rec(pot_now + 2 * amt, amt, nxt, False, cap - amt,
                        pot_now)
                    n_edges += 1
            if cap > 0:
                rec(pot_now + 2 * cap, cap, len(menu) - 1 if mode == "noninc"
                    else len(menu), False, 0, pot_now)
                n_edges += 1
            c["edges"] += n_edges
        rec(pot, 0, 0 if mode != "noninc" else len(menu) - 1, True,
            F(stack), pot)
        return c
    return count


def p3():
    """Sweep: for each combo, do the three single-menu counts define a
    line that (a) is exactly collinear over all three, (b) has integer
    slope dividing the remaining four published sizes into positive
    integers?"""
    wins, tested = [], 0
    for mode in ("nondec", "strict", "noninc", "pre"):
        cnt = make_counter(mode)
        for pot in (100, 150, 200, 250, 300, 400, 600, 1000):
            cs = {k: cnt(m, F(pot), 20000) for k, m in MENU_1.items()}
            for kind in ("decision", "terminal", "edges",
                         "dec_plus_term"):
                tested += 1
                if kind == "dec_plus_term":
                    d = {k: cs[k]["decision"] + cs[k]["terminal"]
                         for k in cs}
                else:
                    d = {k: cs[k][kind] for k in cs}
                x1, x2, x3 = d["2P"], d["halfP"], d["P"]
                if x2 == x1 or x3 == x1:
                    continue
                # line through (x1,48000),(x2,100000)
                num, den = 100000 - 48000, x2 - x1
                if num * (x3 - x1) != (61000 - 48000) * den:
                    continue          # third point off the line
                if num % den:
                    continue
                a = num // den
                b = 48000 - a * x1
                rest = [126000, 204000, 360000, 555000]
                ok = all((s - b) % a == 0 and (s - b) // a > 0
                         for s in rest)
                if ok:
                    wins.append((mode, pot, kind, a, b,
                                 [x1, x2, x3]))
    return tested, wins


# ---------------------------------------------------------------- P2 --
def p2(trials=5_000_000, seed=2):
    """Line fixed by verified (16,48000),(20,61000): a=3250, b=-4000.
    Null: S(32-row) and the four multi-fraction sizes are independent
    multiples of 1000 within +-30%.  Success: S(32-row)=100000 exactly
    AND the other four all satisfy (s+4000) % 3250 == 0."""
    rng = random.Random(seed)
    hits = 0
    targets = [100000, 126000, 204000, 360000, 555000]
    for _ in range(trials):
        v = [1000 * rng.randint(round(0.7 * s / 1000), round(1.3 * s / 1000))
             for s in targets]
        if v[0] == 100000 and all((s + 4000) % 3250 == 0 for s in v[1:]):
            hits += 1
    return hits / trials


if __name__ == "__main__":
    q13, q3250 = p1()
    print(f"P1 lattice: P(gcd>=13000) = {q13:.2e}; "
          f"P(gcd>=3250) = {q3250:.2e}  (MC 2e6, null: nezavisle nasobky "
          f"1000 v +-30% pasmech)")
    tested, wins = p3()
    print(f"P3 look-elsewhere: {tested} kombinaci pravidel x pot x citac; "
          f"uspesnych: {len(wins)}")
    for w in wins:
        print("   WIN:", w)
    q2 = p2()
    print(f"P2 anchored: P = {q2:.2e}  (MC 5e6; analyticky ~ "
          f"1/61 * (1/13)^4 = {1/61*(1/13)**4:.2e})")
    json.dump({"p1_gcd13000": q13, "p1_gcd3250": q3250,
               "p3_tested": tested,
               "p3_wins": [[str(x) for x in w] for w in wins],
               "p2": q2},
              open(__file__.replace("coincidence_tests.py",
                                    "coincidence_results.json"), "w"),
              indent=1)
