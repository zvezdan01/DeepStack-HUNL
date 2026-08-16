from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from hunl.cards import possible_hands_mask
from hunl_datagen.source_contract_v2 import UnresolvedSourceAmbiguity
from hunl_datagen.turn_datagen_v2 import (
    CountingTHRandom, DatagenMode, TurnDataGeneratorV2, TurnDatagenV2Config,
    sample_pot_half, shard_seed, strict_readiness_check,
)

def digest(*arrays):
    h=hashlib.sha256()
    for a in arrays:
        a=np.ascontiguousarray(a); h.update(str(a.dtype).encode()); h.update(str(a.shape).encode()); h.update(a.tobytes())
    return h.hexdigest()

def main():
    try: strict_readiness_check()
    except UnresolvedSourceAmbiguity as e: strict_fail=True; strict_msg=str(e)
    else: raise AssertionError('AUTHOR_STRICT unexpectedly runnable')

    # Deterministic input generation replay, no solver involved.
    cfg=TurnDatagenV2Config(batch_size=3,cfr_iters=20,cfr_skip_iters=10,master_seed=20260816)
    seed=shard_seed(cfg.master_seed,0)
    g=TurnDataGeneratorV2(cfg)
    r1=CountingTHRandom(seed); a=g.make_batch_inputs(r1)
    r2=CountingTHRandom(seed); b=g.make_batch_inputs(r2)
    assert a.board==b.board and a.rng_draws_after==b.rng_draws_after
    assert np.array_equal(a.ranges,b.ranges) and np.array_equal(a.pots,b.pots) and np.array_equal(a.masks,b.masks)
    pm=possible_hands_mask(a.board)
    assert np.all(a.ranges[:,:,~pm]==0)
    sums=a.ranges.sum(axis=2,dtype=np.float64)
    max_sum_err=float(np.max(np.abs(sums-1.0)))
    assert max_sum_err < 2e-6
    assert np.all(a.masks[:,~pm]==0) and np.all(a.masks[:,pm]==1)
    assert np.all((a.pots>=100)&(a.pots<=19950))
    input_sha=digest(np.asarray(a.board,dtype=np.uint8),a.ranges,a.pots,a.masks)

    # Distribution contract: every category/value is sampled with two MT draws.
    prng=CountingTHRandom(8675309); vals=np.array([sample_pot_half(prng,DatagenMode.RELEASED_CODE_ANCHORED) for _ in range(10000)])
    assert prng.draws==20000
    legal=((vals==100)|((200<=vals)&(vals<400))|((400<=vals)&(vals<2000))|((2000<=vals)&(vals<6000))|((6000<=vals)&(vals<=19950)))
    assert bool(np.all(legal))

    # Small exact-solver smoke. This is not an original 1000-iteration target;
    # it certifies the V2 wiring and deterministic first-node path economically.
    smoke_cfg=TurnDatagenV2Config(batch_size=1,cfr_iters=20,cfr_skip_iters=10,master_seed=20260816)
    smoke=TurnDataGeneratorV2(smoke_cfg)
    srng=CountingTHRandom(shard_seed(smoke_cfg.master_seed,7)); inp=smoke.make_batch_inputs(srng)
    t=time.perf_counter(); sol=smoke.solve_batch(inp); secs=time.perf_counter()-t
    assert np.isfinite(sol.targets).all()
    assert abs(float(sol.expected_utility_residuals[0])) < 1e-5
    target_sha=digest(sol.targets)
    # replay entire solve
    srng2=CountingTHRandom(shard_seed(smoke_cfg.master_seed,7)); inp2=smoke.make_batch_inputs(srng2); sol2=smoke.solve_batch(inp2)
    assert np.array_equal(sol.targets,sol2.targets)
    assert np.array_equal(sol.expected_utility_residuals,sol2.expected_utility_residuals)

    result={
      'schema':'HUNL_TURN_DATAGEN_V2_CERT_V1',
      'author_strict':{'fail_closed':strict_fail,'reason':strict_msg},
      'released_code_anchored_inputs':{
        'seed':seed,'board':list(a.board),'batch':cfg.batch_size,'rng_draws':a.rng_draws_after,
        'boundary_ties':a.boundary_ties,'max_range_sum_error_f32':max_sum_err,'blocked_mass_zero':True,
        'replay_byte_exact':True,'input_stream_sha256':input_sha,
      },
      'pot_sampler':{'draws_for_10000_samples':prng.draws,'all_values_in_published_or_project_singleton_support':True,'min':int(vals.min()),'max':int(vals.max())},
      'solver_smoke':{
        'iterations':smoke_cfg.cfr_iters,'omit':smoke_cfg.cfr_skip_iters,'action_set':['F','C','P','A'],
        'board':list(inp.board),'pot_half':int(inp.pots[0]),'runtime_seconds_first':secs,
        'expected_utility_zero_sum_residual_chips':float(sol.expected_utility_residuals[0]),
        'targets_f32_sha256':target_sha,'full_replay_byte_exact':True,
      },
      'production_schedule':{'iterations':1000,'omit':500,'status':'HIGH-CONFIDENCE RELEASED-CODE-ANCHORED; HUNL offline omit not separately stated in paper'},
      'status':'V2 WIRING CERTIFIED; original-private bit identity intentionally not claimed',
    }
    out=Path(__file__).with_name('HUNL_TURN_DATAGEN_V2_CERT.json'); out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__': main()
