#!/usr/bin/env python3
"""Turn-gate frozen-regression battery: ZERO CHANGE requirement on all
frozen Leduc + HUNL river results after adding the turn layer.

Runs, in order:
  - DS pytest suite + all 8 frozen ds_scripts comparators (Leduc Golden)
  - run_g1_1.py       (cards/evaluator, full 7-card space)
  - run_g1_2_3.py     (blockers/showdown incl. exhaustive river audit)
  - run_g1_tree.py    (ACPC betting tree, exhaustive pots)
  - run_g1_78.py      (river resolver corpus incl. Leduc byte-equivalence)
  - compares the regenerated G1_78_ANCHORS.txt byte-for-byte against the
    committed (frozen) version — ZERO CHANGE proof for the river corpus.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

QT = Path("/home/user/quant-trade")
DS = Path("/workspace/deepstack_leduc_v1.1-bitexact-certified")
ENV = {**os.environ, "LD_LIBRARY_PATH": str(DS),
       "PYTHONPATH": f"{QT}:{DS}"}
report = []


def log(m):
    print(m, flush=True)
    report.append(m)


def run(cmd, cwd, tag):
    t = time.time()
    r = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or ["<no output>"])[-1]
    assert r.returncode == 0, f"{tag} FAILED: {r.stdout[-500:]}{r.stderr[-500:]}"
    log(f"{tag}: {last} ({time.time()-t:.0f}s)")


frozen_anchors = subprocess.run(
    ["git", "show", "HEAD:certification/hunl_g1/G1_78_ANCHORS.txt"],
    cwd=QT, capture_output=True, text=True, check=True).stdout

run([sys.executable, "-m", "pytest", "-q", "tests"], DS, "Leduc pytest")
for s in ("compare_private_boards_480.py", "compare_continual_first_action.py",
          "compare_nn_root_trace.py", "compare_nn_boxes.py",
          "compare_root_cfv_both_players.py", "determinism_check.py",
          "m2_activation_probe.py", "regen_tree_manifest.py"):
    run([sys.executable, str(QT / "certification/ds_scripts" / s)], DS, s)
run([sys.executable, str(QT / "certification/hunl_g1/run_g1_1.py"),
     "/tmp/g1_1_regress"], QT, "run_g1_1 (cards/evaluator)")
run([sys.executable, str(QT / "certification/hunl_g1/run_g1_2_3.py")],
    QT, "run_g1_2_3 (blockers/showdown)")
run([sys.executable, str(QT / "certification/hunl_g1/run_g1_tree.py"),
     "/tmp/g1_tree_regress"], QT, "run_g1_tree (ACPC betting)")
run([sys.executable, str(QT / "certification/hunl_g1/run_g1_78.py")],
    DS, "run_g1_78 (river corpus)")

regen = (QT / "certification/hunl_g1/G1_78_ANCHORS.txt").read_text()
assert regen == frozen_anchors, "G1.7/G1.8 corpus anchors CHANGED"
log("river corpus anchors: regenerated == frozen committed version "
    "(ZERO CHANGE, byte-for-byte)")
log("REGRESSION BATTERY: PASS")
(QT / "certification/hunl_g1/G1_TURN_REGRESSION.txt").write_text(
    "\n".join(report) + "\n")
