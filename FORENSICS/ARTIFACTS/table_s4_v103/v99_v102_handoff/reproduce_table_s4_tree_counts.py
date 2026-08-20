
from dataclasses import dataclass
from fractions import Fraction as F

@dataclass
class Node:
    player:int
    spent:tuple
    max_spent:int
    min_raise_to:int
    depth:int
    terminal:str|None=None
    folder:int|None=None
    actions:list=None
    children:list=None
    def __post_init__(self):
        if self.actions is None:self.actions=[]
        if self.children is None:self.children=[]

STACK=20000
BB=100

def expand(n, menus):
    if n.terminal is not None:
        return
    p=n.player; opp=1-p

    # Fold is legal only when facing an outstanding bet.
    if n.spent[p] != n.max_spent and n.spent[p] != STACK:
        n.actions.append(("fold",0))
        n.children.append(Node(opp,n.spent,n.max_spent,n.min_raise_to,n.depth+1,
                               terminal="fold",folder=p))

    # Call/check. Any action at depth>=1 closes the river after call/check in this audit tree.
    sp=list(n.spent)
    sp[p]=min(n.max_spent,STACK)
    closes=n.depth>=1
    c=Node(opp,tuple(sp),n.max_spent,n.min_raise_to,n.depth+1,
           terminal="showdown" if closes else None)
    n.actions.append(("call",0))
    n.children.append(c)
    if not closes:
        expand(c,menus)

    if n.spent[opp]>=STACK or n.spent[p]>=STACK:
        return

    mn,mx=n.min_raise_to,STACK
    if mn>mx:
        if n.max_spent>=mx:return
        mn=mx

    menu=menus[min(n.depth,len(menus)-1)]
    cands=[]
    for x in menu:
        if x=="MIN":
            r=mn
        else:
            f=F(x)
            # Recovered Table-S4 diagnostic convention:
            # raise-to = current max spent + fraction * current pot,
            # with current pot = 2*max_spent in the symmetric river-start audit state.
            delta=f*(2*n.max_spent)
            r=n.max_spent+round(float(delta))
        if mn<=r<mx:
            cands.append(int(r))

    cands.append(mx)  # explicit all-in

    for r in sorted(set(cands)):
        sp=list(n.spent); sp[p]=r
        c=Node(opp,tuple(sp),r,max(n.min_raise_to,2*r-n.max_spent),n.depth+1)
        n.actions.append(("raise",r))
        n.children.append(c)
        expand(c,menus)

def build(menus,pot=200):
    # Symmetric street-start representation used in the audited witness.
    half=pot//2
    root=Node(0,(half,half),half,half+BB,0)
    expand(root,menus)
    return root

def counts(root):
    public=0
    decision=0
    def walk(n):
        nonlocal public,decision
        public+=1
        if n.terminal is None:
            decision+=1
        for c in n.children:
            walk(c)
    walk(root)
    return public,decision

# V86 sparse continuation family.
SPARSE = {
    "2P": ((F(2),),(F(2),),(F(2),)),
    "1/2P": ((F(1,2),),(F(1,2),),(F(1,2),)),
    "P": ((F(1),),(F(1),),(F(1),)),
    "1/2P+P": ((F(1,2),F(1)),("MIN",),(F(3,4),)),
    "P+2P": ((F(1),F(2)),("MIN",),(F(3,4),F(3))),
    "1/2P+P+2P": ((F(1,2),F(1),F(2)),("MIN",),(F(1,4),F(10))),
}

# V43 FULL structural witness.
FULL = (
    ("MIN",F(1,4),F(1,2),F(3,4),F(1),F(2),F(10)),
    ("MIN",F(3),F(10)),
    (F(1),F(3)),
)

def main():
    expected={
        "2P":(45,16),
        "1/2P":(93,32),
        "P":(57,20),
        "1/2P+P":(117,40),
        "P+2P":(189,64),
        "1/2P+P+2P":(333,112),
        "FULL":(513,172),
    }
    got={}
    for name,menus in SPARSE.items():
        got[name]=counts(build(menus))
    got["FULL"]=counts(build(FULL))
    for name in expected:
        print(f"{name:12s} public={got[name][0]:3d} decision={got[name][1]:3d}")
        assert got[name]==expected[name], (name,got[name],expected[name])

    D=[got[x][1] for x in ["2P","1/2P","P","1/2P+P","P+2P","1/2P+P+2P","FULL"]]
    size=[3250*d-4000 for d in D]
    print("D =",D)
    print("3250*D-4000 =",size)
    assert size==[48000,100000,61000,126000,204000,360000,555000]

if __name__=="__main__":
    main()
