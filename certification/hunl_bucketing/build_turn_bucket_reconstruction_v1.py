#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from hunl.turn_bucket_reconstruction import sample_turn_features,fit_reconstruction_v1,ReconstructedTurnBucketProvider
from hunl.cards import HAND_CARDS,hand_index

SEED=20260816
# 64 boards * 160 legal hands = 10,240 feature vectors.  This is a compact
# bootstrap reconstruction artifact, not a claim about original training size.
t=time.perf_counter();x,smeta=sample_turn_features(seed=SEED,boards=64,hands_per_board=160);feature_seconds=time.perf_counter()-t
feature_sha=hashlib.sha256(x.astype('<f4').tobytes()).hexdigest()
t=time.perf_counter();art=fit_reconstruction_v1(x,k=1000,seed=SEED,iterations=5);fit_seconds=time.perf_counter()-t
art.manifest['training_sample']=smeta
art.manifest['training_feature_sha256']=feature_sha
art.manifest['feature_generation_seconds']=feature_seconds
art.manifest['fit_seconds']=fit_seconds
artifact_path=Path(__file__).with_name('HUNL_TURN_BUCKET_RECONSTRUCTION_V1.npz');art.save(artifact_path)
# Provider determinism and suit-isomorphism assignment check on one board/hand set.
p=ReconstructedTurnBucketProvider(art);board=(0,5,10,15);m1=p.for_board(board);m2=p.for_board(board);assert np.array_equal(m1.hand_to_bucket,m2.hand_to_bucket)
# Global suit permutation: bucket features are invariant, so corresponding hands must map identically.
perm=(1,0,3,2)
def pc(c): return (c//4)*4+perm[c%4]
pb=tuple(pc(c) for c in board);pm=p.for_board(pb)
checks=0
for h in np.flatnonzero(m1.legal_mask)[::37]:
 c0,c1=map(int,HAND_CARDS[h]);ph=hand_index(pc(c0),pc(c1));assert int(m1.hand_to_bucket[h])==int(pm.hand_to_bucket[ph]);checks+=1
sha=hashlib.sha256(artifact_path.read_bytes()).hexdigest()
res={'schema':'hunl-turn-bucket-reconstruction-v1-cert','status':'PASS','artifact':artifact_path.name,'artifact_sha256':sha,'centroid_sha256':art.manifest['centroid_sha256'],'training_samples':int(x.shape[0]),'feature_generation_seconds':feature_seconds,'fit_seconds':fit_seconds,'objective_history':art.manifest['objective_history_bin_units'],'empty_clusters_final':art.manifest['empty_clusters_final'],'provider_deterministic':True,'suit_assignment_checks':checks,'claim':'PROJECT_RECONSTRUCTION_NOT_ORIGINAL'}
Path(__file__).with_name('HUNL_TURN_BUCKET_RECONSTRUCTION_V1_CERT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps(res,indent=2))
