#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from hunl.bucket_features import turn_board_final_equity_histograms,turn_final_equity_histogram
from hunl.cards import possible_hands_mask
boards=[(0,5,10,15),(3,18,32,49),(4,21,34,47),(8,13,38,43)]
sha=hashlib.sha256(); comparisons=0; times=[]
for board in boards:
 t=time.perf_counter();bulk=turn_board_final_equity_histograms(board);times.append(time.perf_counter()-t)
 pm=possible_hands_mask(board);ids=np.flatnonzero(pm)
 assert bulk.shape==(1326,50);assert np.all(bulk[ids].sum(1)==46);assert np.all(bulk[~pm]==0)
 # Compare 32 spread-out legal hands per board to independent single-hand path.
 pick=ids[np.linspace(0,len(ids)-1,32,dtype=int)]
 for h in pick:
  one=turn_final_equity_histogram(board,int(h))
  assert np.array_equal(one.counts,bulk[h])
  comparisons+=1
 sha.update(np.asarray(board,dtype='<i2').tobytes());sha.update(bulk.astype('<i2').tobytes())
res={'schema':'hunl-bulk-turn-feature-cert-v1','status':'PASS','boards':len(boards),'single_hand_exact_comparisons':comparisons,'legal_hands_per_board':1128,'observations_per_legal_hand':46,'hist_bins':50,'seconds_per_board':times,'mean_seconds_per_board':float(np.mean(times)),'feature_stream_sha256':sha.hexdigest()}
Path(__file__).with_name('HUNL_BULK_TURN_FEATURE_CERT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps(res,indent=2))
