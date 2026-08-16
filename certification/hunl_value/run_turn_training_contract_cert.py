from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import torch

from hunl.turn_bucket_reconstruction import ReconstructedTurnBucketProvider
from hunl.value_network import DeepStackHUNLValueNet,HUNLValueNetworkSpec
from hunl.value_training import prepare_turn_training_batch,forward_card_values,loss_on_prepared_batch

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'certification/hunl_bucketing/HUNL_TURN_BUCKET_RECONSTRUCTION_V1.npz'
DATA=ROOT/'certification/hunl_datagen_v2/HUNL_TURN_DATAGEN_V2_PRODUCTION_ANCHOR.npz'
OUT=ROOT/'certification/hunl_value/HUNL_TURN_TRAINING_CONTRACT_CERT.json'

z=np.load(DATA)
board=tuple(int(x) for x in z['board'])
ranges=z['ranges'].transpose(1,0,2) # [1,2,1326]
targets=z['targets']
pots=z['pot_half']
provider=ReconstructedTurnBucketProvider.from_file(ART)
batch=prepare_turn_training_batch(boards=[board],ranges=ranges,pot_halves=pots,card_targets=targets,bucket_provider=provider)

# Input range checks.
x=batch.inputs.detach().numpy()
r1=float(x[0,:1000].sum(dtype=np.float64)); r2=float(x[0,1000:2000].sum(dtype=np.float64))

# Fixed seed is PROJECT test determinism only, not author weight init claim.
torch.manual_seed(20260816)
model=DeepStackHUNLValueNet(HUNLValueNetworkSpec())
model.train()
out=forward_card_values(model,batch)
loss=loss_on_prepared_batch(model,batch)
loss.backward()
finite_grad=all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in model.parameters())
grad_norm=float(torch.sqrt(sum(torch.sum(p.grad.detach()**2) for p in model.parameters() if p.grad is not None)))

# Zero-sum must survive inverse bucketing by duality.
y=out.detach().numpy()[0]
u=float(np.dot(ranges[0,0].astype(np.float64),y[0].astype(np.float64)) + np.dot(ranges[0,1].astype(np.float64),y[1].astype(np.float64)))
blocked=~batch.legal_mask.numpy()[0]
blocked_max=float(np.max(np.abs(y[:,blocked])))

# Adam smoke: parameters change, gradients remain finite. Do not assert loss decrease in one stochastic step.
opt=torch.optim.Adam(model.parameters(),lr=1e-3)
first=next(model.parameters()).detach().clone()
opt.step()
param_delta=float(torch.max(torch.abs(next(model.parameters()).detach()-first)))

payload=out.detach().cpu().numpy().astype('<f4').tobytes()
cert={
 'schema':'HUNL_TURN_TRAINING_CONTRACT_CERT',
 'status':'PASS' if abs(r1-1)<2e-6 and abs(r2-1)<2e-6 and abs(u)<2e-5 and blocked_max==0.0 and finite_grad and grad_norm>0 and param_delta>0 else 'FAIL',
 'source_status':'SOURCE_CONSISTENT_RECONSTRUCTION_NOT_PRIVATE_TRAINER_BITEXACT',
 'board':list(board),'pot_half':int(pots[0]),
 'input_bucket_mass_p1':r1,'input_bucket_mass_p2':r2,
 'card_output_zero_sum_residual':u,
 'blocked_card_output_max_abs':blocked_max,
 'loss':float(loss.detach()),'gradient_norm':grad_norm,'finite_gradients':finite_grad,
 'adam_first_parameter_max_delta':param_delta,
 'card_output_sha256':hashlib.sha256(payload).hexdigest(),
 'training_locus': 'Huber after inverse bucketing in 1326-hand card space; chosen to avoid inventing unpublished card-target->bucket-target reduction.',
 'primary_evidence': [
   'DeepStack paper Fig.3: card ranges -> bucketing -> NN -> zero-sum -> inverse bucketing -> card counterfactual values',
   'DeepStack paper: output vectors are CFVs for each player and hand',
   'DeepStack supplement: Adam minimizes average Huber losses over counterfactual value errors',
   'Released DeepStack-Leduc bucket_conversion.lua: range sums into buckets; bucket values scatter back to cards',
 ],
 'unresolved':'Exact private HUNL trainer loss location / target aggregation code was not released.'
}
OUT.write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
print(json.dumps(cert,indent=2,sort_keys=True))
