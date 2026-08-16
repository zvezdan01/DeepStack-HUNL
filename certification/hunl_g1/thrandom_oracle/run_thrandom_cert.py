#!/usr/bin/env python3
"""THRandom restoration certification (post container-loss re-anchor).

The certified `datagen/th_random.py` was lost with the DS workspace on
2026-08-14 and restored in-repo. This driver re-certifies the restored
port with the same oracle method as Phase 2A:

  Leg A — untouched-C oracle: THRandom.c copied verbatim from a fresh
      torch/torch7 clone pinned at the RECORDED provenance commit
      814ea4a (file SHA-256 verified against the clone), compiled with a
      minimal shim; 4 seeds x 10,000 draws x 5 stream kinds
      (u32, uniform-f32, randint(1,6), randint(1,52), randint(0,4)) —
      Python port must be BYTE-EQUAL on all 20 streams. (Phase 2A ran
      u32/f32/randint(1,6) = 12 streams; the two extra integer ranges
      cover the draws the HUNL turn datagen actually makes.)

  Leg B — frozen in-repo anchors: the Tammelin-oracle streams
      `certification/oracles/rng/mt_seed{0,1,42,6874}_n{10,…,10000}`
      (SHA256SUMS-verified, incl. the Phase-2A recorded cross-anchor
      d85832ea…) must be byte-equal to the restored port's u32 stream —
      proving continuity with the PRE-LOSS certified stream.

  Leg C — untouched Tammelin rng.c (third_party/CFR_plus, in-repo)
      compiled and re-run: regenerated u32 streams must reproduce the
      frozen anchor files byte-for-byte — proving the frozen anchors
      themselves regenerate from their untouched source.

Any byte difference anywhere -> hard failure.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
QT = HERE.parent.parent.parent
sys.path.insert(0, str(QT))

from datagen.th_random import THRandom  # noqa: E402

SEEDS = (0, 1, 42, 6874)
N = 10000
THRANDOM_C_SHA = ("5752496219762bfc70c359c8b3e3c96eae19ac"
                  "56478a38efd4190e7e4128ee36")
TORCH7_COMMIT = "814ea4afd6beb110705d2456de03876841fcf1fd"
report = []


def log(m):
    print(m, flush=True)
    report.append(m)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


t0 = time.time()
src = (HERE / "THRandom.c").read_bytes()
assert sha(src) == THRANDOM_C_SHA, "vendored THRandom.c drifted"
log(f"THRandom.c untouched (SHA {THRANDOM_C_SHA[:16]}…, "
    f"torch/torch7 @ {TORCH7_COMMIT[:7]})")

tmp = Path(tempfile.mkdtemp(prefix="thrandom_oracle_"))
exe = tmp / "harness"
subprocess.run(["cc", "-O2", "-I", str(HERE), str(HERE / "harness.c"),
                str(HERE / "THRandom.c"), "-o", str(exe), "-lm"],
               check=True)

# ---- Leg A: untouched-C oracle streams vs restored Python port -------
streams = 0
for seed in SEEDS:
    subprocess.run([str(exe), str(seed), str(N), str(tmp)], check=True)
    r = THRandom(seed)
    u32 = np.array([r.random_u32() for _ in range(N)], dtype="<u4")
    r = THRandom(seed)
    f32 = r.rand_float(N).astype("<f4")
    ints = {}
    for a, b in ((1, 6), (1, 52), (0, 4)):
        r = THRandom(seed)
        ints[(a, b)] = np.array([r.random_range(a, b) for _ in range(N)],
                                dtype="<i4")
    pairs = [(u32.tobytes(), tmp / f"seed{seed}_u32.bin"),
             (f32.tobytes(), tmp / f"seed{seed}_f32.bin"),
             (ints[(1, 6)].tobytes(), tmp / f"seed{seed}_randint_1_6.bin"),
             (ints[(1, 52)].tobytes(), tmp / f"seed{seed}_randint_1_52.bin"),
             (ints[(0, 4)].tobytes(), tmp / f"seed{seed}_randint_0_4.bin")]
    for ours, path in pairs:
        theirs = path.read_bytes()
        assert ours == theirs, f"LEG A DIVERGENCE {path.name}"
        streams += 1
log(f"Leg A PASS: {streams}/20 streams byte-equal vs untouched "
    f"THRandom.c oracle (4 seeds x {N} x u32/f32/randint(1,6)/(1,52)/(0,4))")

# ---- Leg B: frozen in-repo anchors vs restored port ------------------
ORC = QT / "certification/oracles/rng"
sums = {ln.split()[1].lstrip("./"): ln.split()[0] for ln in
        (QT / "certification/oracles/SHA256SUMS").read_text().splitlines()
        if "/rng/" in ln}
checked = 0
anchor42 = None
for seed in SEEDS:
    for n in (10, 100, 1000, 10000):
        binp = ORC / f"mt_seed{seed}_n{n}.bin"
        data = binp.read_bytes()
        assert sha(data) == sums[f"rng/{binp.name}"], f"frozen {binp.name} drifted"
        r = THRandom(seed)
        ours = np.array([r.random_u32() for _ in range(n)], dtype="<u4").tobytes()
        assert ours == data, f"LEG B DIVERGENCE {binp.name}"
        txt = (ORC / f"mt_seed{seed}_n{n}.txt").read_text()
        assert txt == "\n".join(str(v) for v in np.frombuffer(ours, "<u4")) + "\n"
        if seed == 42 and n == 10000:
            anchor42 = sha(data)
        checked += 1
assert anchor42 == ("d85832ea3fdd45aba234c2d43775a184"
                    "cc48d3b44da39c1d9b1389de82214741")
log(f"Leg B PASS: {checked}/16 frozen anchor streams byte-equal "
    f"(bin+txt), incl. Phase-2A cross-anchor d85832ea… (seed42 n10000)")

# ---- Leg C: untouched Tammelin rng.c regenerates the anchors ---------
rng_c = QT / "third_party/CFR_plus/rng.c"
leg_c_main = tmp / "tammelin_main.c"
leg_c_main.write_text("""
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "rng.h"
int main(int argc, char **argv) {
  rng_state_t s;
  init_genrand(&s, (uint32_t)strtoul(argv[1], NULL, 10));
  int n = atoi(argv[2]);
  FILE *f = fopen(argv[3], "wb");
  for (int i = 0; i < n; i++) { uint32_t v = genrand_int32(&s); fwrite(&v, 4, 1, f); }
  fclose(f);
  return 0;
}
""")
exe_c = tmp / "tammelin"
subprocess.run(["cc", "-O2", "-I", str(QT / "third_party/CFR_plus"),
                str(leg_c_main), str(rng_c), "-o", str(exe_c)], check=True)
regen = 0
for seed in SEEDS:
    for n in (10, 100, 1000, 10000):
        out = tmp / f"regen_{seed}_{n}.bin"
        subprocess.run([str(exe_c), str(seed), str(n), str(out)], check=True)
        assert out.read_bytes() == (ORC / f"mt_seed{seed}_n{n}.bin").read_bytes(), \
            f"LEG C DIVERGENCE seed{seed} n{n}"
        regen += 1
log(f"Leg C PASS: {regen}/16 frozen anchors regenerated byte-for-byte "
    f"from untouched Tammelin rng.c (SHA {sha(rng_c.read_bytes())[:16]}…)")

log(f"THRANDOM RESTORATION CERT: PASS — restored datagen/th_random.py is "
    f"BIT_EXACT vs untouched torch7 C, the frozen pre-loss anchors, and "
    f"untouched Tammelin C ({time.time()-t0:.0f}s)")
(HERE.parent / "latest_audit").mkdir(exist_ok=True)
(HERE.parent / "latest_audit" / "THRANDOM_RESTORATION_CERT.txt").write_text(
    "\n".join(report) + "\n")
