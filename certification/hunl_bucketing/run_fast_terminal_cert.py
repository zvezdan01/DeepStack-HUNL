#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from hunl.river_terminal_fast import RiverTerminalFastKernel
from hunl.showdown import showdown_matrix
from hunl.blockers import legal_pairs_mask
from hunl.cards import possible_hands_mask

BOARDS=[(0,5,10,15,20),(3,18,32,49,7),(4,21,34,47,1),(8,13,38,43,17)]
rng=np.random.default_rng(20260816)
max_sd=max_fl=0.0
sha=hashlib.sha256()
checks=0
bench={}
for board in BOARDS:
    k=RiverTerminalFastKernel.build(board)
    m,legal,_=showdown_matrix(board)
    md=m.astype(np.float64); fm=legal_pairs_mask(board).astype(np.float64)
    pm=possible_hands_mask(board)
    for B in [1,2,5,11]:
        R=rng.random((B,1326)); R[:,~pm]=0
        oldsd=R@md.T; oldfl=R@fm
        newsd=k.showdown(R); newfl=k.fold(R)
        max_sd=max(max_sd,float(np.max(np.abs(oldsd-newsd))))
        max_fl=max(max_fl,float(np.max(np.abs(oldfl-newfl))))
        assert np.allclose(oldsd,newsd,rtol=2e-12,atol=1e-12)
        assert np.allclose(oldfl,newfl,rtol=2e-12,atol=1e-12)
        sha.update(newsd.astype('<f8').tobytes()); sha.update(newfl.astype('<f8').tobytes())
        checks+=B*2

# Benchmark a realistic batched board operation.
board=BOARDS[0]; k=RiverTerminalFastKernel.build(board); m,legal,_=showdown_matrix(board)
md=m.astype(np.float64); fm=legal.astype(np.float64); pm=possible_hands_mask(board)
R=rng.random((8,1326));R[:,~pm]=0
# warm
k.showdown(R);k.fold(R);R@md.T;R@fm
N=100
t=time.perf_counter()
for _ in range(N): R@md.T; R@fm
old=time.perf_counter()-t
t=time.perf_counter()
for _ in range(N): k.showdown(R); k.fold(R)
new=time.perf_counter()-t
bench={'batch':8,'repeats':N,'dense_seconds':old,'fast_seconds':new,'speedup':old/new}
res={'schema':'hunl-fast-river-terminal-cert-v1','status':'PASS','boards':len(BOARDS),'operator_vector_checks':checks,'max_abs_showdown_diff':max_sd,'max_abs_fold_diff':max_fl,'output_sha256':sha.hexdigest(),'benchmark':bench,'claim':'SEMANTIC/NUMERIC equivalence; not BLAS bit identity'}
out=Path(__file__).with_name('HUNL_FAST_RIVER_TERMINAL_CERT.json');out.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print(json.dumps(res,indent=2))
