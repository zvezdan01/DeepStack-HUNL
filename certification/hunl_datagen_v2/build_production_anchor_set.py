from __future__ import annotations
import hashlib,json,time
from pathlib import Path
import numpy as np
from hunl_datagen.turn_datagen_v2 import TurnDatagenV2Config,TurnDataGeneratorV2,CountingTHRandom,shard_seed,DatagenMode

ROOT=Path(__file__).resolve().parents[2]
OUTNPZ=ROOT/'certification/hunl_datagen_v2/HUNL_TURN_DATAGEN_V2_ANCHOR_SET4.npz'
OUTJSON=ROOT/'certification/hunl_datagen_v2/HUNL_TURN_DATAGEN_V2_ANCHOR_SET4.json'
master=20260816
boards=[];pots=[];ranges=[];targets=[];res=[];seeds=[];draws=[];ties=[];times=[]
for j in range(4):
    sd=shard_seed(master,100+j)
    cfg=TurnDatagenV2Config(mode=DatagenMode.RELEASED_CODE_ANCHORED,batch_size=1,cfr_iters=1000,cfr_skip_iters=500,terminal_backend='rank_numba',master_seed=master)
    gen=TurnDataGeneratorV2(cfg); rng=CountingTHRandom(sd)
    inp=gen.make_batch_inputs(rng)
    t0=time.perf_counter(); sol=gen.solve_batch(inp); dt=time.perf_counter()-t0
    seeds.append(sd); boards.append(inp.board); pots.append(int(inp.pots[0])); ranges.append(inp.ranges[:,0,:]); targets.append(sol.targets[0]); res.append(float(sol.expected_utility_residuals[0])); draws.append(inp.rng_draws_after); ties.append(inp.boundary_ties); times.append(dt)
    print(j,sd,inp.board,int(inp.pots[0]),dt,res[-1],flush=True)
boards=np.asarray(boards,dtype=np.int16);pots=np.asarray(pots,dtype=np.int32);ranges=np.asarray(ranges,dtype=np.float32);targets=np.asarray(targets,dtype=np.float32);res=np.asarray(res,dtype=np.float64)
np.savez_compressed(OUTNPZ,boards=boards,pot_half=pots,ranges=ranges,targets=targets,residuals=res,seeds=np.asarray(seeds,dtype=np.uint32),rng_draws=np.asarray(draws,dtype=np.int32),boundary_ties=np.asarray(ties,dtype=np.int32))
h=hashlib.sha256();
for a in (boards.astype('<i2'),pots.astype('<i4'),ranges.astype('<f4'),targets.astype('<f4'),res.astype('<f8')): h.update(a.tobytes())
meta={'schema':'HUNL_TURN_DATAGEN_V2_ANCHOR_SET4','status':'RECONSTRUCTION_PRODUCTION_SHAPE_NOT_ORIGINAL_DATASET','samples':4,'cfr_iters':1000,'skip':500,'terminal_backend':'rank_numba','master_seed':master,'seeds':seeds,'boards':[list(map(int,b)) for b in boards],'pot_half':pots.tolist(),'rng_draws':draws,'boundary_ties':ties,'solve_seconds':times,'zero_sum_residual_max_abs_chips':float(np.max(np.abs(res))),'stream_sha256':h.hexdigest()}
OUTJSON.write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
print(json.dumps(meta,indent=2,sort_keys=True))
