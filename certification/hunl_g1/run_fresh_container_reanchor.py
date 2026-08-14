#!/usr/bin/env python3
"""Fresh-container re-anchor battery (post 2026-08-14 container loss).

The Golden Baseline v1 gates were certified in a container that no
longer exists. This driver re-runs, IN THE CURRENT CONTAINER, every
frozen G1 harness whose oracles survive (in-repo, or restored with
recorded-SHA verification), and documents exactly which certified
surfaces are NOT re-runnable because their oracle died with the DS
workspace. Frozen RESULT/ANCHOR files are never left overwritten:
regenerated outputs go to latest_audit/, frozen files are restored via
`git checkout` (the run_turn_engine_regression.py convention).

Runnable here (oracle provenance):
  - hunl/ tree identity vs Golden Baseline commit 34a50560 (git)
  - certification/oracles SHA256SUMS integrity (in-repo)
  - THRandom restoration cert (untouched torch7 C + frozen anchors)
  - run_g1_2_3.py       (terminal matrices; in-repo oracles)
  - run_g1_tree.py      (ACPC betting oracle; game.c restored from the
                         public project_acpc_server mirror, SHA-verified
                         against the RECORDED anchor 85b5325d…)
  - run_g1_1.py         (evalHandTables oracle; restored, SHA 9b8bb8e1…
                         already in the evaluator's known set)
  - run_g1_turn_engine.py sections 1–6 (ACPC + LP + reference oracles)
      — EXPECTED to stop at section 7 (CFR-D gadget) with the
      deepstack_leduc shim's loud-fail: the golden gadget died with the
      container. Recorded as the documented re-run boundary.
  - run_g1_turn.py up to its RiverResolver transition section (same
      boundary, same reason).
  - determinism double-solve (2 fresh processes, full 1000/500 state,
      SHA over CFVs+BR+strategy) — fresh anchor for THIS container.

NOT re-runnable in this container (oracle lost with the DS workspace,
by design reported rather than substituted): Leduc golden-engine pytest,
certification/ds_scripts comparators, G1.7/G1.8 river-resolver gates,
CFR-D gadget re-solves, run_g1_turn's turn→river transition section.

Numeric caveat recorded in the output: frozen anchors were produced
under the old container's numpy/BLAS; a byte-level anchor difference
here is an ENVIRONMENT observation (documented per FAILURE_MATRIX F-07),
not an engine regression — PASS/FAIL below is decided by each harness's
own oracle assertions, all of which run fresh in this container.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

QT = Path("/home/user/quant-trade")
DS = Path("/workspace/deepstack_leduc_v1.1-bitexact-certified")
AUD = QT / "certification/hunl_g1/latest_audit"
AUD.mkdir(exist_ok=True)
ENV = {**os.environ, "LD_LIBRARY_PATH": str(DS),
       "PYTHONPATH": f"{QT}:{QT / 'certification/hunl_g1'}:{DS}",
       "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}
GOLDEN = "34a50560a30cbff156e979b59af6c00e39f7f1a9"
GAME_C_SHA = "85b5325dd54e043fdb22548d4e1bfe4ed40b820a87f75f252d93875688b5c7cc"
SHIM_MARK = "lost with the 2026-08-14 container reclaim"
FROZEN = ["G1_1_RESULT.txt", "G1_2_3_RESULT.txt", "G1_TREE_RESULT.txt",
          "G1_78_RESULT.txt", "G1_78_ANCHORS.txt", "G1_TURN_RESULT.txt",
          "G1_TURN_REGRESSION.txt"]
report: list[str] = []
T0 = time.time()


def log(m):
    print(m, flush=True)
    report.append(m)


def run(cmd, tag, expect_shim_stop=False, timeout=3 * 3600):
    t = time.time()
    r = subprocess.run(cmd, cwd=QT, env=ENV, capture_output=True,
                       text=True, timeout=timeout)
    (AUD / f"REANCHOR_{tag}.log").write_text(
        r.stdout + ("\n--- stderr ---\n" + r.stderr if r.stderr else ""))
    dt = time.time() - t
    if r.returncode == 0:
        last = (r.stdout.strip().splitlines() or ["<no output>"])[-1]
        log(f"{tag}: PASS — {last} ({dt:.0f}s)")
        return "PASS"
    if expect_shim_stop and SHIM_MARK in (r.stdout + r.stderr):
        done = [ln for ln in r.stdout.splitlines() if " PASS" in ln]
        log(f"{tag}: PARTIAL (documented boundary) — {len(done)} section "
            f"PASSes, stopped at the lost-golden-engine shim ({dt:.0f}s)")
        for ln in done:
            log(f"    {ln}")
        return "PARTIAL"
    log(f"{tag}: FAIL rc={r.returncode} ({dt:.0f}s) — see REANCHOR_{tag}.log")
    log("    tail: " + "; ".join((r.stdout + r.stderr).strip().splitlines()[-3:]))
    return "FAIL"


def restore_frozen():
    subprocess.run(["git", "checkout", "--"] +
                   [f"certification/hunl_g1/{f}" for f in FROZEN],
                   cwd=QT, check=True)


verdicts = {}

# ---- 0. identity & integrity ----------------------------------------
d = subprocess.run(["git", "diff", "--stat", GOLDEN, "HEAD", "--", "hunl/"],
                   cwd=QT, capture_output=True, text=True, check=True).stdout
assert d.strip() == "", f"hunl/ drifted from Golden Baseline v1:\n{d}"
log(f"0a PASS: hunl/ tree byte-identical to Golden Baseline v1 {GOLDEN[:7]}")
r = subprocess.run(["sha256sum", "-c", "SHA256SUMS"],
                   cwd=QT / "certification/oracles",
                   capture_output=True, text=True)
bad = [ln for ln in r.stdout.splitlines() if not ln.endswith(": OK")]
assert r.returncode == 0 and not bad, f"oracle integrity: {bad}"
log(f"0b PASS: certification/oracles SHA256SUMS "
    f"{len(r.stdout.splitlines())}/{len(r.stdout.splitlines())} OK")
gc = DS / "reference_lua/ACPCServer/game.c"
assert hashlib.sha256(gc.read_bytes()).hexdigest() == GAME_C_SHA
log(f"0c PASS: restored ACPC game.c matches recorded anchor "
    f"{GAME_C_SHA[:16]}…")
verdicts["integrity"] = "PASS"

# ---- 1. THRandom restoration cert (fast, full 3 legs) ----------------
verdicts["thrandom"] = run(
    [sys.executable,
     str(QT / "certification/hunl_g1/thrandom_oracle/run_thrandom_cert.py")],
    "thrandom_cert")

# ---- 2. frozen harnesses with surviving/restored oracles -------------
verdicts["g1_2_3"] = run(
    [sys.executable, str(QT / "certification/hunl_g1/run_g1_2_3.py")],
    "g1_2_3")
restore_frozen()
verdicts["g1_tree"] = run(
    [sys.executable, str(QT / "certification/hunl_g1/run_g1_tree.py"),
     "/tmp/reanchor_g1_tree"], "g1_tree")
restore_frozen()
verdicts["g1_1"] = run(
    [sys.executable, str(QT / "certification/hunl_g1/run_g1_1.py"),
     "/tmp/reanchor_g1_1"], "g1_1")
restore_frozen()
verdicts["g1_turn_engine"] = run(
    [sys.executable, str(QT / "certification/hunl_g1/run_g1_turn_engine.py")],
    "g1_turn_engine", expect_shim_stop=True)
restore_frozen()
verdicts["g1_turn"] = run(
    [sys.executable, str(QT / "certification/hunl_g1/run_g1_turn.py")],
    "g1_turn", expect_shim_stop=True)
restore_frozen()

# ---- 3. determinism double-solve (fresh anchor for THIS container) ---
DET = r"""
import sys, hashlib, numpy as np
sys.path.insert(0, "/home/user/quant-trade")
np.seterr(all="ignore")
from hunl.turn_engine import TurnEngine
from hunl_datagen.turn_datagen import DGCFG, CountingTHRandom, \
    HunlTurnRangeGenerator, sample_board, sample_pot, shard_seed
rng = CountingTHRandom(shard_seed(9999))
board, _ = sample_board(rng)
gen = HunlTurnRangeGenerator(); gen.set_board(board)
r1 = gen.generate(1, rng)[0].astype(np.float64)
r2 = gen.generate(1, rng)[0].astype(np.float64)
pot = sample_pot(rng)
te = TurnEngine(board, pot, cfg=DGCFG)
cfvs = te.resolve_first_node(r1, r2)
br0 = te.best_response_value(0, r2)
br1 = te.best_response_value(1, r1)
h = hashlib.sha256()
for a in (cfvs, br0, br1, te.root_strategy):
    h.update(np.ascontiguousarray(a).tobytes())
print(h.hexdigest())
"""
hashes = []
t = time.time()
for i in range(2):
    r = subprocess.run([sys.executable, "-c", DET], env=ENV, cwd=QT,
                       capture_output=True, text=True, timeout=3600 * 2)
    assert r.returncode == 0, r.stderr[-500:]
    hashes.append(r.stdout.strip())
assert hashes[0] == hashes[1], f"DETERMINISM FAILURE: {hashes}"
log(f"3 PASS: determinism double-solve (2 fresh processes, datagen config "
    f"1000/500, CFVs+BR+strategy) SHA {hashes[0][:32]}… "
    f"byte-identical ({time.time()-t:.0f}s)")
verdicts["determinism"] = "PASS"

# ---- 4. NOT re-runnable (lost oracle) — explicit record --------------
for item in ("Leduc golden-engine pytest (36 tests)",
             "ds_scripts comparators (8 scripts, ~25k trace tensors)",
             "G1.7/G1.8 river-resolver gates (golden Lookahead)",
             "CFR-D gadget re-solves (golden CFRDGadget)",
             "turn->river transition section of run_g1_turn.py"):
    log(f"NOT_RE_RUNNABLE_IN_CONTAINER: {item} — oracle lost with the DS "
        f"workspace; last certified in the pre-loss container (frozen "
        f"results committed), NOT re-certified here")

fails = [k for k, v in verdicts.items() if v == "FAIL"]
log(f"\nFRESH-CONTAINER RE-ANCHOR: {'PASS' if not fails else 'FAIL'} "
    f"— {verdicts} ({(time.time()-T0)/60:.1f} min)")
(AUD / "FRESH_CONTAINER_REANCHOR.txt").write_text("\n".join(report) + "\n")
sys.exit(1 if fails else 0)
