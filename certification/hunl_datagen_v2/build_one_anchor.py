from __future__ import annotations
import sys,time,json,hashlib
from pathlib import Path
import numpy as np
from hunl_datagen.turn_datagen_v2 import *
idx=int(sys.argv[1]); ROOT=Path(__file__).resolve().parents[2]; master=20260816; sd=shard_seed(master,100+idx)
cfg=TurnDatagenV2Config(mode=DatagenMode.RELEASED_CODE_ANCHORED,batch_size=1,cfr_iters=1000,cfr_skip_iters=500,terminal_backend='rank_numba',master_seed=master)
gen=TurnDataGeneratorV2(cfg); rng=CountingTHRandom(sd); inp=gen.make_batch_inputs(rng)
t0=time.perf_counter(); sol=gen.solve_batch(inp); dt=time.perf_counter()-t0
out=ROOT/f'certification/hunl_datagen_v2/anchor4_{idx}.npz'
np.savez_compressed(out,board=np.asarray(inp.board,dtype=np.int16),pot_half=inp.pots,ranges=inp.ranges[:,0,:],targets=sol.targets[0],residuals=sol.expected_utility_residuals,seeds=np.asarray([sd],dtype=np.uint32),rng_draws=np.asarray([inp.rng_draws_after],dtype=np.int32),boundary_ties=np.asarray([inp.boundary_ties],dtype=np.int32),solve_seconds=np.asarray([dt],dtype=np.float64))
print(json.dumps({'idx':idx,'seed':sd,'board':inp.board,'pot':int(inp.pots[0]),'seconds':dt,'residual':float(sol.expected_utility_residuals[0]),'target_sha256':hashlib.sha256(sol.targets[0].astype('<f4').tobytes()).hexdigest()}))
