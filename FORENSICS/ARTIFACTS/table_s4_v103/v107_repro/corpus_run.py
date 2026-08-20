#!/usr/bin/env python3
"""V108 (this session): corpus-size discriminator for the Table S4
norm-ratio question, on a self-consistent documented implementation.

Protocol (frozen): V99-V102 handoff trees verbatim (pot 200/stack 20000,
layered menus), 1081-hand river basis, sparse 100 iters/skip 50, FULL
400/200, CFR+ (RM+, simultaneous, uniform avg after skip), CFVs/pot.
Corpus: state k has board = 5 distinct cards from default_rng(10000+k),
ranges r0, r1 from default_rng(k) uniform on legal hands, normalized.
NOT the sibling pilot's exact protocol (their range recipe is
unrecovered); the corpus-size TREND is the deliverable.
"""
import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from v107_fast import (Basis, Solver, build, SPARSE, FULL, MENU_ORDER,
                       PAPER, amap, norms)
from hunl.cards import card_to_string

N_STATES = 100
POT = 200.0
CKPT = HERE / "corpus_states.jsonl"

def board_str(k):
    rng = np.random.default_rng(10000 + k)
    cards = rng.choice(52, size=5, replace=False)
    return "".join(card_to_string(int(c)) for c in cards)

def ranges(basis, k):
    rng = np.random.default_rng(k)
    r0 = rng.random(basis.n); r0 /= r0.sum()
    r1 = rng.random(basis.n); r1 /= r1.sum()
    return r0, r1

def state_rows(k):
    bs = board_str(k)
    b = Basis(bs)
    r0, r1 = ranges(b, k)
    fr = build(FULL)
    fc = Solver(fr, b).solve(r0, r1, 400, 200) / POT
    fm = amap(fr)
    rows = {}
    for menu in MENU_ORDER:
        sr = build(SPARSE[menu])
        sc = Solver(sr, b).solve(r0, r1, 100, 50) / POT
        sm = amap(sr)
        common = [a for a in sm if a in fm]
        errs = {a: sc[sm[a]] - fc[fm[a]] for a in common}
        lay = {}
        lay["call_only"] = norms(errs[("call", 0)])
        pa = [norms(errs[a]) for a in common]
        lay["mean_action_norms"] = list(np.mean(pa, axis=0))
        lay["max_action_norms"] = list(np.max(pa, axis=0))
        stack = np.concatenate([errs[a] for a in common])
        lay["concat"] = norms(stack)
        lay["mean_vector"] = norms(np.mean([errs[a] for a in common], 0))
        rows[menu] = lay
    return {"k": k, "board": bs, "rows": rows}

def cumulative(states):
    lays = ["call_only", "mean_action_norms", "max_action_norms",
            "concat", "mean_vector"]
    out = {}
    for lay in lays:
        mares = []
        for menu in MENU_ORDER:
            m = np.mean([s["rows"][menu][lay] for s in states], axis=0)
            r = [m[0] / m[1], m[1] / m[2]]
            p1, p2, pinf = PAPER[menu]
            pr = [p1 / p2, p2 / pinf]
            mares.append(np.mean([abs(r[0]-pr[0])/pr[0],
                                  abs(r[1]-pr[1])/pr[1]]))
        out[lay] = float(np.mean(mares))
    return out

def main():
    done = []
    if CKPT.exists():
        done = [json.loads(l) for l in CKPT.read_text().splitlines() if l]
    have = {s["k"] for s in done}
    for k in range(N_STATES):
        if k in have:
            continue
        t0 = time.time()
        s = state_rows(k)
        done.append(s)
        with open(CKPT, "a") as f:
            f.write(json.dumps(s) + "\n")
        msg = f"state {k+1}/{N_STATES} {s['board']} ({time.time()-t0:.0f}s)"
        if len(done) in (9, 20, 50, 100):
            msg += f"  CUM@{len(done)}: " + json.dumps(
                {a: round(v, 4) for a, v in cumulative(done).items()})
        print(msg, flush=True)
    cum = {n: cumulative(done[:n]) for n in (1, 2, 4, 9, 20, 50, 100)}
    json.dump({"protocol": "self-consistent V108, see docstring",
               "cumulative": cum},
              open(HERE / "corpus_cumulative.json", "w"), indent=1)
    print("FINAL CUMULATIVE:")
    for n, v in cum.items():
        print(f"  n={n:3d}  call_only {v['call_only']:.4f}  "
              f"mean_action_norms {v['mean_action_norms']:.4f}  "
              f"concat {v['concat']:.4f}")

if __name__ == "__main__":
    main()
