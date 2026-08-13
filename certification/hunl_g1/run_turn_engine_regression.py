#!/usr/bin/env python3
"""Turn-engine gate frozen-regression battery — ZERO CHANGE required.

Same coverage as the transition-gate battery, plus the transition gate
itself. Frozen RESULT/ANCHOR files are NEVER left overwritten: harnesses
that write into certification/hunl_g1 have their regenerated outputs
compared against the committed versions (anchors byte-compared), copied
into certification/hunl_g1/latest_audit/, and the frozen files restored
via git checkout.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

QT = Path("/home/user/quant-trade")
DS = Path("/workspace/deepstack_leduc_v1.1-bitexact-certified")
ENV = {**os.environ, "LD_LIBRARY_PATH": str(DS),
       "PYTHONPATH": f"{QT}:{QT / 'certification/hunl_g1'}:{DS}"}
AUD = QT / "certification/hunl_g1/latest_audit"
AUD.mkdir(exist_ok=True)
FROZEN = ["G1_1_RESULT.txt", "G1_2_3_RESULT.txt", "G1_TREE_RESULT.txt",
          "G1_78_RESULT.txt", "G1_78_ANCHORS.txt", "G1_TURN_RESULT.txt",
          "G1_TURN_REGRESSION.txt"]
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
     "/tmp/g1_1_r2"], QT, "run_g1_1")
run([sys.executable, str(QT / "certification/hunl_g1/run_g1_2_3.py")],
    QT, "run_g1_2_3")
run([sys.executable, str(QT / "certification/hunl_g1/run_g1_tree.py"),
     "/tmp/g1_tree_r2"], QT, "run_g1_tree")
run([sys.executable, str(QT / "certification/hunl_g1/run_g1_78.py")],
    DS, "run_g1_78")
regen = (QT / "certification/hunl_g1/G1_78_ANCHORS.txt").read_text()
assert regen == frozen_anchors, "river corpus anchors CHANGED"
log("river corpus anchors: ZERO CHANGE (byte-for-byte)")
run([sys.executable, str(QT / "certification/hunl_g1/run_g1_turn.py")],
    DS, "run_g1_turn (transition gate)")

# archive regenerated logs; restore frozen files
for f in FROZEN:
    p = QT / "certification/hunl_g1" / f
    if p.exists():
        shutil.copy(p, AUD / f)
subprocess.run(["git", "checkout", "--"] +
               [f"certification/hunl_g1/{f}" for f in FROZEN],
               cwd=QT, check=True)
clean = subprocess.run(["git", "status", "--porcelain"], cwd=QT,
                       capture_output=True, text=True, check=True).stdout
assert not any(f in clean for f in FROZEN), "frozen files left modified"
log("frozen RESULT files restored; regenerated logs in latest_audit/")
log("TURN-ENGINE REGRESSION BATTERY: PASS")
(AUD / "TURN_ENGINE_REGRESSION.txt").write_text("\n".join(report) + "\n")
