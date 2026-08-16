from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np

from hunl.cards import HAND_CARDS, HAND_COUNT, HAND_INDEX, possible_hands_mask
from hunl.turn_bucket_reconstruction import ReconstructionArtifact, ReconstructedTurnBucketProvider

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'certification/hunl_bucketing/HUNL_TURN_BUCKET_RECONSTRUCTION_V1.npz'
OUT=ROOT/'certification/hunl_bucketing/HUNL_BUCKET_ALGEBRA_RECON_V1_CERT.json'

artifact=ReconstructionArtifact.load(ART)
provider=ReconstructedTurnBucketProvider(artifact)
boards=[(0,5,10,15),(1,14,27,40),(3,11,31,48),(8,19,33,51)]
rng=np.random.default_rng(20260816)
max_mass=0.0; max_duality=0.0; max_block=0.0
suit_checks=0; suit_fail=0
stream=[]

# card id convention is rank*4+suit in the frozen HUNL layer.
def perm_card(c,p): return (c//4)*4+p[c%4]
def perm_hand_id(h,p):
    a,b=HAND_CARDS[h]
    aa,bb=sorted((perm_card(int(a),p),perm_card(int(b),p)))
    # frozen HANDS is lexicographic combinations; build lookup once outside would be faster
    return int(HAND_INDEX[aa,bb])

for board in boards:
    bm=provider.for_board(board)
    legal=possible_hands_mask(board)
    assert np.all(bm.hand_to_bucket[~legal]==-1)
    assert np.all((bm.hand_to_bucket[legal]>=0)&(bm.hand_to_bucket[legal]<1000))
    max_block=max(max_block,float(np.max(np.abs((bm.hand_to_bucket[~legal]+1).astype(np.float64))))) if np.any(~legal) else max_block
    # random legal probability ranges and bucket duality
    for _ in range(16):
        x=rng.random(HAND_COUNT)
        x[~legal]=0
        x/=x.sum()
        br=bm.range_to_buckets(x)
        max_mass=max(max_mass,abs(float(br.sum())-1.0))
        v=rng.standard_normal(1000)
        hv=bm.bucket_values_to_hands(v)
        lhs=float(np.dot(x,hv)); rhs=float(np.dot(br,v))
        max_duality=max(max_duality,abs(lhs-rhs))
    # global suit relabeling must preserve reconstruction feature => same bucket label
    base=bm.hand_to_bucket
    for p in [(1,0,2,3),(0,2,1,3),(3,1,2,0),(2,3,0,1),(1,2,3,0)]:
        pb=tuple(perm_card(c,p) for c in board)
        pm=provider.for_board(pb).hand_to_bucket
        ids=np.flatnonzero(legal)
        for h in ids[::17]:
            hp=perm_hand_id(int(h),p)
            suit_checks+=1
            if int(base[h])!=int(pm[hp]): suit_fail+=1
    stream.append(bm.hand_to_bucket.astype('<i2').tobytes())

cert={
 'schema':'HUNL_BUCKET_ALGEBRA_RECON_V1_CERT',
 'status':'PASS' if suit_fail==0 and max_mass<2e-15 and max_duality<2e-12 else 'FAIL',
 'artifact_status':artifact.manifest.get('status'),
 'boards':len(boards),
 'bucket_count':1000,
 'range_mass_max_abs_error':max_mass,
 'range_value_duality_max_abs_error':max_duality,
 'blocked_mapping_error':max_block,
 'global_suit_checks':suit_checks,
 'global_suit_failures':suit_fail,
 'mapping_stream_sha256':hashlib.sha256(b''.join(stream)).hexdigest(),
 'source_contract':{
   'card_range_to_bucket':'sum masses of all hands assigned to bucket (released DeepStack-Leduc bucket_conversion.lua)',
   'bucket_value_to_card':'copy bucket value to every hand assigned to bucket (released DeepStack-Leduc bucket_conversion.lua)',
   'duality':'<card_range,inverse(bucket_value)> == <bucket_range,bucket_value>',
 },
 'claim':'Algebra is released-code anchored; mapping centroids are PROJECT_RECONSTRUCTION_NOT_ORIGINAL.'
}
OUT.write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
print(json.dumps(cert,indent=2,sort_keys=True))
