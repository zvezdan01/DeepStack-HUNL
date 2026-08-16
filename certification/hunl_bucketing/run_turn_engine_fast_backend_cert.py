#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from hunl.turn_engine import TurnEngine
from hunl.cards import possible_hands_mask

board=(37,5,14,28); pot=11717
pm=possible_hands_mask(board)
rng=np.random.default_rng(2026081601)
r1=rng.random(1326);r2=rng.random(1326);r1[~pm]=0;r2[~pm]=0;r1/=r1.sum();r2/=r2.sum()

def solve(backend,iters=20,skip=10):
 t=time.perf_counter();e=TurnEngine(board,pot,cfr_iters=iters,cfr_skip_iters=skip,terminal_backend=backend);v=e.resolve_first_node(r1,r2);dt=time.perf_counter()-t
 return e,v,dt
# warm numba before timing (JIT compile not counted as recurring production cost)
e0=TurnEngine(board,pot,cfr_iters=1,cfr_skip_iters=0,terminal_backend='rank_numba');e0.resolve_first_node(r1,r2)
dense,vd,td=solve('dense',20,10)
fast,vf,tf=solve('rank_numba',20,10)
maxcf=float(np.max(np.abs(vd-vf))); maxst=float(np.max(np.abs(dense.root_strategy-fast.root_strategy)))
# CFR is iterative and tiny FP order changes can accumulate. Certify tight numerical equivalence, not bit identity.
assert maxcf < 1e-7, maxcf
assert maxst < 1e-9, maxst
ud=float(np.dot(r1,vd[0])+np.dot(r2,vd[1])); uf=float(np.dot(r1,vf[0])+np.dot(r2,vf[1]))
# Repeat fast path deterministically.
fast2,vf2,tf2=solve('rank_numba',20,10)
assert np.array_equal(vf,vf2)
assert np.array_equal(fast.root_strategy,fast2.root_strategy)
h=hashlib.sha256();h.update(vf.astype('<f8').tobytes());h.update(fast.root_strategy.astype('<f8').tobytes())
res={'schema':'hunl-turn-engine-fast-backend-cert-v1','status':'PASS','board':board,'pot_half':pot,'iterations':20,'omit':10,'max_abs_root_cfv_dense_vs_fast':maxcf,'max_abs_root_strategy_dense_vs_fast':maxst,'dense_zero_sum_residual':ud,'fast_zero_sum_residual':uf,'dense_seconds':td,'fast_seconds':tf,'fast_replay_seconds':tf2,'speedup':td/tf,'fast_output_sha256':h.hexdigest(),'claim':'same game/CFR semantics; terminal reductions algebraically exact; FP summation order differs'}
Path(__file__).with_name('HUNL_TURN_ENGINE_FAST_BACKEND_CERT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps(res,indent=2))
