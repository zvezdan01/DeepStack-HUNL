#!/usr/bin/env python3
"""Crash-resume certification test for the HUNL turn DataGenerator.

Property under test (iteration-count independent — the solver schedule is
reduced to 20/10 iterations here, with REAL solves, so the whole crash
matrix runs in minutes; production-scale byte-reproducibility of a
COMPLETED shard is certified separately by the pilot's full shard-0
replay):

  interrupted run + restart  ==  uninterrupted fresh run, byte-for-byte:
    - a shard killed mid-generation leaves no manifest; on restart the
      resume driver REJECTS and DELETES the stale partial files (logged)
      and regenerates the shard from its seed;
    - a shard killed mid-WRITE (some arrays final, some .tmp, no
      manifest) is likewise rejected/deleted;
    - COMPLETED shards (manifest present, SHAs verify) are skipped —
      never recomputed (asserted via file mtimes);
    - final arrays + manifests (modulo wall-clock fields) are identical
      to the uninterrupted run.

Resume-driver contract (production orchestration uses the same rules):
  if manifest exists: verify every array SHA -> SKIP (mismatch =
  fail-fast); else: delete every shard_XXXXX.* file (stale partial),
  then generate.

Usage:
  run:    python3 run_datagen_resume_test.py
  worker: python3 run_datagen_resume_test.py worker <shard_idx> <out_dir>
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
sys.path.insert(0, str(DS))

TEST_MASTER = 990814          # test-only master seed (distinct from pilot)
TEST_ITERS, TEST_OMIT = 20, 10
SHARD_N = 10                  # one batch
ARRAYS = ("boards", "pots", "ranges", "targets", "masks")


def _patch_module():
    import numpy as np
    np.seterr(all="ignore")
    import hunl_datagen.turn_datagen as td
    td.MASTER_SEED = TEST_MASTER
    td.CONFIG_CANON = dict(td.CONFIG_CANON,
                           master_seed=TEST_MASTER,
                           test_mode=f"resume-test {TEST_ITERS}/{TEST_OMIT}")
    td.CONFIG_SHA = hashlib.sha256(
        json.dumps(td.CONFIG_CANON, sort_keys=True).encode()).hexdigest()
    import dataclasses
    td.DGCFG = dataclasses.replace(td.DGCFG, turn_cfr_iters=TEST_ITERS,
                                   turn_cfr_omit=TEST_OMIT)
    return td


def resume_generate(td, idx: int, out_dir: Path, log) -> str:
    """The resume driver under test. Returns 'skipped' | 'generated'."""
    prefix = out_dir / f"shard_{idx:05d}"
    manifest_path = Path(f"{prefix}.json")
    if manifest_path.exists():
        m = json.loads(manifest_path.read_text())
        for name in ARRAYS:
            p = Path(f"{prefix}.{name}.npy")
            assert p.exists() and hashlib.sha256(
                p.read_bytes()).hexdigest() == m["sha256"][name], \
                f"completed shard {idx} fails SHA verify"
        log(f"shard {idx}: COMPLETE, SHA verified -> skip")
        return "skipped"
    stale = sorted(out_dir.glob(f"shard_{idx:05d}.*"))
    for p in stale:
        p.unlink()
    if stale:
        log(f"shard {idx}: PARTIAL ({len(stale)} stale files) -> "
            "REJECTED and deleted")
    td.generate_shard(idx, SHARD_N, out_dir)
    log(f"shard {idx}: generated")
    return "generated"


def worker(idx: int, out_dir: Path) -> None:
    td = _patch_module()
    td.generate_shard(idx, SHARD_N, out_dir)


def main() -> None:
    report = []

    def log(m):
        print(m, flush=True)
        report.append(m)

    env = {**os.environ, "LD_LIBRARY_PATH": str(DS),
           "PYTHONPATH": f"{QT}:{DS}",
           "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}
    base = Path(os.environ.get(
        "RESUME_TEST_DIR",
        "/tmp/claude-0/-home-user-quant-trade/"
        "ab297466-f300-5fe2-aeba-419112c121c8/scratchpad/resume_test"))
    A, B = base / "fresh", base / "interrupted"
    for d in (A, B):
        if d.exists():
            for p in sorted(d.glob("*")):
                p.unlink()
        d.mkdir(parents=True, exist_ok=True)

    td = _patch_module()

    # ---------- reference: uninterrupted fresh run (shards 0,1,2) ------
    t = time.time()
    for i in (0, 1, 2):
        td.generate_shard(i, SHARD_N, A)
    log(f"reference run A: 3 shards uninterrupted ({time.time()-t:.0f}s)")

    # ---------- interrupted run ---------------------------------------
    td.generate_shard(0, SHARD_N, B)                  # shard 0 completes
    mtimes0 = {n: Path(B / f"shard_00000.{n}.npy").stat().st_mtime_ns
               for n in ARRAYS}

    # kill shard 1 mid-solve (SIGKILL once the first sample is logged)
    logf = B / "worker1.log"
    with open(logf, "w") as lf:
        proc = subprocess.Popen(
            [sys.executable, __file__, "worker", "1", str(B)],
            cwd=DS, env=env, stdout=lf, stderr=subprocess.STDOUT)
        deadline = time.time() + 600
        while time.time() < deadline:
            if logf.read_text().count("sample 2/") >= 1:
                break
            time.sleep(0.5)
        else:
            proc.kill()
            raise SystemExit("worker never reached sample 2")
        proc.send_signal(signal.SIGKILL)
        proc.wait()
    assert not (B / "shard_00001.json").exists(), \
        "killed shard must not have a manifest"
    log("shard 1 SIGKILLed mid-solve (after sample 2 started, "
        "no manifest on disk)")

    # construct a mid-WRITE partial for shard 2: some arrays final, some
    # .tmp, NO manifest (worst write-window state)
    for n, mode in (("boards", "final"), ("pots", "final"),
                    ("ranges", "tmp")):
        src = A / f"shard_00002.{n}.npy"
        dst = (B / f"shard_00002.{n}.npy" if mode == "final"
               else B / f"shard_00002.{n}.tmp.npy")
        dst.write_bytes(src.read_bytes())
    log("shard 2 staged as mid-write partial (2 final arrays + 1 tmp, "
        "no manifest)")

    # ---------- restart: resume driver --------------------------------
    results = {i: resume_generate(td, i, B, log) for i in (0, 1, 2)}
    assert results == {0: "skipped", 1: "generated", 2: "generated"}
    mtimes0_after = {n: Path(B / f"shard_00000.{n}.npy").stat().st_mtime_ns
                     for n in ARRAYS}
    assert mtimes0_after == mtimes0, "completed shard 0 was recomputed!"
    log("restart: shard 0 skipped (mtimes unchanged => not recomputed); "
        "partials rejected+deleted; shards 1,2 regenerated")

    # ---------- byte-identity vs uninterrupted run --------------------
    for i in (0, 1, 2):
        for n in ARRAYS:
            a = hashlib.sha256((A / f"shard_{i:05d}.{n}.npy")
                               .read_bytes()).hexdigest()
            b = hashlib.sha256((B / f"shard_{i:05d}.{n}.npy")
                               .read_bytes()).hexdigest()
            assert a == b, f"shard {i} {n} differs after resume"
        ma = json.loads((A / f"shard_{i:05d}.json").read_text())
        mb = json.loads((B / f"shard_{i:05d}.json").read_text())
        for volatile in ("gen_minutes",):
            ma.pop(volatile), mb.pop(volatile)
        assert ma == mb, f"shard {i} manifest differs (beyond wall-clock)"
    log("RESULT: interrupted+resumed dataset BYTE-IDENTICAL to the "
        "uninterrupted fresh run (15 array files + manifests modulo "
        "wall-clock); no stale partial survived; no completed shard "
        "recomputed")
    log("RESUME TEST: PASS")
    out = QT / "certification/hunl_g1/latest_audit"
    out.mkdir(exist_ok=True)
    (out / "TURN_DATAGEN_RESUME_TEST.txt").write_text(
        "\n".join(report) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        worker(int(sys.argv[2]), Path(sys.argv[3]))
    else:
        main()
