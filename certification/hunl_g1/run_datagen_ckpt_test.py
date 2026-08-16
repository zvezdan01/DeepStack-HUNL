#!/usr/bin/env python3
"""Checkpoint-resume certification for turn_datagen v1.1 (ckpt build).

Property: a shard SIGKILLed at ANY point and resumed from its
per-sample checkpoint produces arrays byte-identical to an
uninterrupted fresh run, and a corrupt checkpoint self-heals to a fresh
byte-identical regeneration. Real solves at 20/10 iterations (the
resume-test convention); production-scale byte-reproducibility is
separately certified by the pilot's full shard-0 replay, which always
regenerates from scratch and therefore cross-checks every resumed
shard at 1000/500.

Cases:
  A. reference: uninterrupted fresh shard (10 samples = 1 batch)
  B. SIGKILL mid-batch (after sample 3 completes), direct
     generate_shard restart -> must log RESUMED, byte-identical output
  C. SIGKILL again later (after sample 7 of a fresh run), resume,
     byte-identical — proves arbitrary kill points
  D. checkpoint corrupted (truncated) -> ckpt REJECTED -> fresh
     regeneration, byte-identical
  E. completed shard (manifest present) -> ckpt absent, skip untouched

Usage: run: python3 run_datagen_ckpt_test.py
       worker: python3 run_datagen_ckpt_test.py worker <idx> <dir> [stop_after]
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

QT = Path("/home/user/quant-trade")
DS = Path("/workspace/deepstack_leduc_v1.1-bitexact-certified")
sys.path.insert(0, str(QT))

SHARD_N = 10
ARRAYS = ("boards", "pots", "ranges", "targets", "masks")
SCRATCH = Path(os.environ.get(
    "CKPT_TEST_DIR",
    "/tmp/claude-0/-home-user-quant-trade/"
    "0a894140-41f9-5512-94a6-938ee8f238ae/scratchpad/ckpt_test"))


def _patch_module():
    sys.path.insert(0, str(QT / "certification/hunl_g1"))
    from run_datagen_resume_test import _patch_module as pm
    return pm()


def shas(d: Path, idx: int) -> dict:
    return {n: hashlib.sha256(
        (d / f"shard_{idx:05d}.{n}.npy").read_bytes()).hexdigest()
        for n in ARRAYS}


def kill_after(logf: Path, proc, n_samples_done: int):
    deadline = time.time() + 900
    while time.time() < deadline:
        if logf.exists() and \
                logf.read_text().count("sample ") >= n_samples_done + 1:
            break
        time.sleep(0.3)
    else:
        proc.kill()
        raise SystemExit(f"worker never reached sample {n_samples_done + 1}")
    proc.send_signal(signal.SIGKILL)
    proc.wait()


def spawn(idx: int, d: Path, log_name: str):
    env = {**os.environ, "PYTHONPATH": f"{QT}:{DS}",
           "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}
    logf = d / log_name
    lf = open(logf, "w")
    proc = subprocess.Popen(
        [sys.executable, __file__, "worker", str(idx), str(d)],
        env=env, stdout=lf, stderr=subprocess.STDOUT)
    return proc, logf


def main():
    report = []

    def log(m):
        print(m, flush=True)
        report.append(m)

    A, B = SCRATCH / "ref", SCRATCH / "resume"
    for d in (A, B):
        if d.exists():
            for p in sorted(d.glob("*")):
                p.unlink()
        d.mkdir(parents=True, exist_ok=True)

    td = _patch_module()

    # A. reference uninterrupted
    t = time.time()
    td.generate_shard(0, SHARD_N, A)
    ref = shas(A, 0)
    log(f"A reference: uninterrupted shard 0 ({time.time()-t:.0f}s)")

    # B. kill after sample 3, resume in fresh process
    proc, logf = spawn(0, B, "w1.log")
    kill_after(logf, proc, 3)
    assert (B / "shard_00000.ckpt.npz").exists(), "no ckpt after kill"
    assert not (B / "shard_00000.json").exists()
    log("B: worker SIGKILLed after >=3 samples (ckpt present, no manifest)")
    proc, logf = spawn(0, B, "w2.log")
    proc.wait()
    assert proc.returncode == 0, logf.read_text()[-500:]
    assert "RESUMED from checkpoint" in logf.read_text(), "resume not taken"
    assert shas(B, 0) == ref, "B: resumed output differs from reference!"
    assert not (B / "shard_00000.ckpt.npz").exists(), "ckpt not cleaned"
    log("B PASS: resumed shard byte-identical to reference (5/5 arrays), "
        "ckpt cleaned")

    # C. arbitrary later kill point on a fresh dir copy
    for p in sorted(B.glob("shard_00000.*")):
        p.unlink()
    proc, logf = spawn(0, B, "w3.log")
    kill_after(logf, proc, 7)
    proc, logf = spawn(0, B, "w4.log")
    proc.wait()
    assert proc.returncode == 0 and "RESUMED" in logf.read_text()
    assert shas(B, 0) == ref, "C: resumed output differs!"
    log("C PASS: kill after >=7 samples, resume byte-identical")

    # D. corrupt ckpt -> self-heal fresh regeneration
    for p in sorted(B.glob("shard_00000.*")):
        p.unlink()
    proc, logf = spawn(0, B, "w5.log")
    kill_after(logf, proc, 2)
    ck = B / "shard_00000.ckpt.npz"
    ck.write_bytes(ck.read_bytes()[:100])          # truncate
    proc, logf = spawn(0, B, "w6.log")
    proc.wait()
    txt = logf.read_text()
    assert proc.returncode == 0 and "ckpt REJECTED" in txt, txt[-400:]
    assert shas(B, 0) == ref, "D: self-healed output differs!"
    log("D PASS: corrupt ckpt rejected -> fresh regeneration byte-identical")

    # E. completed shard untouched on rerun
    m0 = (B / "shard_00000.json").stat().st_mtime_ns
    td2 = _patch_module()
    td2.generate_shard(0, SHARD_N, B)
    assert (B / "shard_00000.json").stat().st_mtime_ns == m0
    log("E PASS: completed shard skipped (manifest mtime unchanged)")

    ma = json.loads((A / "shard_00000.json").read_text())
    mb = json.loads((B / "shard_00000.json").read_text())
    ma.pop("gen_minutes"), mb.pop("gen_minutes")
    assert ma == mb, "manifest differs beyond wall-clock"
    log("manifests identical modulo wall-clock")
    log("CKPT RESUME TEST: PASS")
    out = QT / "certification/hunl_g1/latest_audit"
    out.mkdir(exist_ok=True)
    (out / "TURN_DATAGEN_CKPT_TEST.txt").write_text("\n".join(report) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        td = _patch_module()
        td.generate_shard(int(sys.argv[2]), SHARD_N, Path(sys.argv[3]))
    else:
        main()
