from table_s4_v105_inverse_oracle import bin_feasible
ROWS=["2P","1/2P","P","1/2P+P","P+2P","1/2P+P+2P","FULL"]
D=[16,32,20,40,64,112,172]
S=[48000,100000,61000,126000,204000,360000,555000]

def feasible_for_hold(hold):
    z=[]
    for cand in range(1,501):
        xs=D.copy(); xs[hold]=cand
        if bin_feasible(xs,S): z.append(cand)
    return z

def test_each_row_uniquely_recovered():
    for i,d in enumerate(D):
        assert feasible_for_hold(i)==[d]

def test_neighbor_counts_rejected_everywhere():
    for i,d in enumerate(D):
        for cand in [d-1,d+1]:
            if cand>=1:
                xs=D.copy(); xs[i]=cand
                assert not bin_feasible(xs,S)

def test_full_uniquely_172():
    assert feasible_for_hold(6)==[172]

def test_sparse_triple_uniquely_112():
    assert feasible_for_hold(5)==[112]

def test_current_vector_is_feasible():
    assert bin_feasible(D,S)

def test_candidate_volume():
    assert 7*500==3500
