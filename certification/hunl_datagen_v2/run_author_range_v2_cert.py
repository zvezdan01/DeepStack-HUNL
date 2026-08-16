from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from hunl.blockers import blocker_matrix
from hunl.cards import HAND_CARDS,HAND_COUNT,possible_hands_mask
from hunl.evaluator import rank_suit_masks,suit_masks
from hunl.showdown import showdown_matrix
from hunl_datagen.author_range_v2 import AuthorRangeGeneratorV2,current_public_hand_strength
from hunl_datagen.source_contract_v2 import GeneratorSourceStatus,UnresolvedSourceAmbiguity,literal_integer_values,reconstruction_v1_integer_values

def py_ranks(board):
    pm=possible_hands_mask(board); ids=np.flatnonzero(pm)
    cards=np.empty((ids.size,6),np.int8); cards[:,:2]=HAND_CARDS[ids]; cards[:,2:]=np.asarray(board,np.int8)
    r=rank_suit_masks(suit_masks(cards)).astype(np.int32)
    out=np.full(HAND_COUNT,-1,np.int32); out[ids]=r; return out

def ensure_oracle():
    exe=Path(__file__).with_name('rank6_board_oracle')
    src=Path(__file__).with_name('rank6_board_oracle.c')
    third=ROOT/'third_party'/'CFR_plus'
    subprocess.check_call(['gcc','-O2','-I'+str(third),str(src),str(third/'game.c'),str(third/'rng.c'),'-o',str(exe)])
    return exe

def c_ranks(board):
    exe=Path(__file__).with_name('rank6_board_oracle')
    raw=subprocess.check_output([str(exe),*map(str,board)])
    return np.frombuffer(raw,dtype=np.int32).copy(),raw

class FixtureRNG:
    def __init__(self): self.g=np.random.default_rng(20260816); self.scalar_draws=0; self.calls=0
    def uniform01(self,n):
        self.calls+=1; self.scalar_draws+=int(n)
        x=self.g.random(n); x=np.maximum(x,np.finfo(float).tiny); return np.minimum(x,np.nextafter(1.0,0.0))

def legacy_score(board):
    acc=np.zeros((HAND_COUNT,HAND_COUNT),np.int16)
    for c in range(52):
        if c in board: continue
        m,_,_=showdown_matrix(tuple(board)+(c,)); acc += m.astype(np.int16,copy=False)
    return acc.sum(1).astype(np.int64)

def main():
    ensure_oracle()
    boards=[(0,5,10,15),(5,22,34,39),(1,2,47,51),(3,16,29,42),(7,18,31,48),(4,9,37,50),(6,11,24,45),(8,19,33,46)]
    stream=bytearray()
    for b in boards:
        p=py_ranks(b); c,raw=c_ranks(b); assert np.array_equal(p,c),b; stream.extend(raw)
    board=(5,22,34,39); hs=current_public_hand_strength(board); ids=hs.legal_hands
    assert ids.size==1128 and np.all(hs.opponent_counts==1035)
    ranks=py_ranks(board); compat=blocker_matrix()==0; pm=possible_hands_mask(board)
    g=np.random.default_rng(817263); checked=g.choice(ids,size=64,replace=False); maxerr=0.0
    for h in checked:
        opp=np.flatnonzero(pm & compat[int(h)]); assert opp.size==1035
        ref=np.count_nonzero(ranks[int(h)]>ranks[opp])/1035.0
        maxerr=max(maxerr,abs(float(hs.strengths[int(h)])-ref))
    assert maxerr==0.0
    cur=hs.strengths[ids]; old=legacy_score(board)[ids]
    diffs=int(np.count_nonzero(np.sign(cur[:,None]-cur[None,:]) != np.sign(old[:,None]-old[None,:]))); assert diffs>0
    rg=AuthorRangeGeneratorV2(board); fr=FixtureRNG(); batch=4; rr=rg.generate(batch,fr)
    assert np.all(rr[:,~pm]==0); sumerr=float(np.max(np.abs(rr.sum(1)-1.0))); assert sumerr<5e-15
    expected=batch*(ids.size-1); assert fr.scalar_draws==expected and fr.calls==ids.size-1
    try: literal_integer_values(0)
    except UnresolvedSourceAmbiguity: fail_closed=True
    else: raise AssertionError
    counts=[len(literal_integer_values(i)) for i in range(1,5)]; assert counts==[200,1600,4000,13951]
    assert reconstruction_v1_integer_values(0)==(100,)
    st=GeneratorSourceStatus()
    result={
      'schema':'HUNL_AUTHOR_RANGE_V2_CERT_V1',
      'rank6_author_oracle':{'boards_checked':len(boards),'hand_slots_per_board':HAND_COUNT,'total_slots_checked':len(boards)*HAND_COUNT,'mismatches':0,'author_output_stream_sha256':hashlib.sha256(bytes(stream)).hexdigest()},
      'turn_hand_strength':{'board4':list(board),'legal_hands':int(ids.size),'uniform_legal_opponents_per_fixed_hand':1035,'independent_hand_recounts':len(checked),'max_abs_error':maxerr,'definition':'P(current six-card holding strictly beats uniform disjoint opponent holding; no future river)','legacy_future_runout_pair_order_sign_differences':diffs},
      'range_recursion':{'batch':batch,'floor_split':True,'random_odd_split':False,'scalar_uniform_draws':fr.scalar_draws,'expected_scalar_uniform_draws':expected,'uniform_vector_calls':fr.calls,'max_range_sum_error':sumerr,'blocked_mass_exact_zero':True,'recursive_split_boundaries_with_equal_strength_tie':rg.boundary_tie_count,'tie_policy':'PROJECT_CANONICAL frozen hand-id within equal strength; original private convention unresolved','rng':'TEST_FIXTURE_ONLY; original HUNL RNG unresolved'},
      'pot_distribution':{'published_first_interval':'[100,100)','author_strict_first_interval_fail_closed':fail_closed,'literal_integer_counts_other_intervals':counts,'reconstruction_v1_first_category':[100],'reconstruction_v1_status':'PROJECT_CANONICAL_NOT_AUTHOR_CONFIRMED'},
      'published_turn_generation_scale':{'situations':st.turn_situations,'cfr_iterations':st.cfr_iterations,'actions':list(st.actions),'card_abstraction':st.card_abstraction,'cpu_cores':st.cpu_cores,'core_years_lower_bound':st.core_years_lower_bound},
      'status':'SOURCE-CONSTRAINED RANGE/STATE CONTRACT; private RNG, tie ordering, [100,100) correction and exact offline CFR implementation remain unresolved'}
    out=Path(__file__).with_name('HUNL_AUTHOR_RANGE_V2_CERT.json'); out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__': main()
