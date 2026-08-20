import subprocess,sys
from pathlib import Path
def test_reproducer_runs_exact():
    p=subprocess.run([sys.executable,str(Path(__file__).parent/"reproduce_table_s4_tree_counts.py")],
                     capture_output=True,text=True,check=True)
    assert "D = [16, 32, 20, 40, 64, 112, 172]" in p.stdout
    assert "555000" in p.stdout
def test_family_definition():
    import json
    r=json.loads((Path(__file__).parent/"TREE_FAMILY_DEFINITION.json").read_text())
    assert r["exact_counts"]["decision"]==[16,32,20,40,64,112,172]
    assert r["exact_counts"]["public"]==[45,93,57,117,189,333,513]
def test_identity():
    D=[16,32,20,40,64,112,172]
    N=[45,93,57,117,189,333,513]
    assert [3*d-3 for d in D]==N
