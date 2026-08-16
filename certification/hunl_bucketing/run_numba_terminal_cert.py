#!/usr/bin/env python3
from __future__ import annotations
import json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from hunl.river_terminal_fast import RiverTerminalFastKernel,showdown_numba,fold_numba,NUMBA_AVAILABLE
from hunl.showdown import showdown_matrix
from hunl.blockers import legal_pairs_mask
from hunl.cards import possible_hands_mask
assert NUMBA_AVAILABLE
boards=[(0,5,10,15,20),(3,18,32,49,7),(4,21,34,47,1),(8,13,38,43,17)]
rng=np.random.default_rng(260816)
maxsd=maxfl=0.; checks=0
for b in boards:
 k=RiverTerminalFastKernel.build(b);m,legal,_=showdown_matrix(b);md=m.astype(float);fm=legal_pairs_mask(b).astype(float);pm=possible_hands_mask(b)
 for B in [1,2,5,11]:
  R=rng.random((B,1326));R[:,~pm]=0
  ns=showdown_numba(k,R);nf=fold_numba(k,R);ds=R@md.T;df=R@fm
  maxsd=max(maxsd,float(np.max(np.abs(ns-ds))));maxfl=max(maxfl,float(np.max(np.abs(nf-df))))
  assert np.allclose(ns,ds,rtol=3e-12,atol=2e-12)
  assert np.allclose(nf,df,rtol=3e-12,atol=2e-12)
  checks+=2*B
# benchmark after JIT warmup
b=boards[0];k=RiverTerminalFastKernel.build(b);m,legal,_=showdown_matrix(b);md=m.astype(float);fm=legal.astype(float);pm=possible_hands_mask(b)
R=rng.random((5,1326));R[:,~pm]=0
showdown_numba(k,R);fold_numba(k,R);R@md.T;R@fm
N=200
t=time.perf_counter()
for _ in range(N):
 _=R@md.T;_=R@fm
dense=time.perf_counter()-t
t=time.perf_counter()
for _ in range(N):
 _=showdown_numba(k,R);_=fold_numba(k,R)
native=time.perf_counter()-t
res={'schema':'hunl-numba-terminal-cert-v1','status':'PASS','boards':len(boards),'checks':checks,'max_abs_showdown_diff':maxsd,'max_abs_fold_diff':maxfl,'benchmark':{'batch':5,'repeats':N,'dense_seconds':dense,'native_seconds':native,'speedup':dense/native},'claim':'algebraically exact, numerically equivalent; different FP reduction order'}
Path(__file__).with_name('HUNL_NUMBA_TERMINAL_CERT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps(res,indent=2))
