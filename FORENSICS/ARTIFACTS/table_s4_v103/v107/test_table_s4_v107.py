import json
from pathlib import Path
HERE=Path(__file__).parent
R=json.loads((HERE/"table_s4_v107_nine_state_value_pilot.json").read_text())
def test_nine_states():
    assert R["protocol"]["states"]==9
def test_new_block_is_heldout_extension():
    assert R["protocol"]["held_out_extension_states"]==4
def test_call_only_remains_better_than_original_single_state():
    assert R["result"]["nine_state_call_only_MARE"] < 0.3521
def test_nine_state_not_near_exact():
    assert R["result"]["best_nine_state_mean_ratio_MARE"] > 0.15
def test_heldout_four_are_not_cherry_picked_success():
    assert R["result"]["four_new_state_call_only_MARE"] > 0.24
def test_external_semantics_fail_closed():
    b=" ".join(R["boundary"]).lower()
    for x in ["supremus","cprg","leduc","libratus","pluribus"]:
        assert x in b
