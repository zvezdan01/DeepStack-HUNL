"""Independent check of the V103 claim: decision-node counts of river
sparse betting trees (non-decreasing pot fractions, all-in capped by
stack) for the Table S4 menus. Scan pots to see if any reference pot
reproduces D = [16,32,20,40,64,112] and FULL=172."""
from fractions import Fraction as F

MENUS = {
    "F,C,2P,A":        [F(2)],
    "F,C,1/2P,A":      [F(1,2)],
    "F,C,P,A":         [F(1)],
    "F,C,1/2P,P,A":    [F(1,2), F(1)],
    "F,C,P,2P,A":      [F(1), F(2)],
    "F,C,1/2P,P,2P,A": [F(1,2), F(1), F(2)],
    "FULL":            [F(1,2)*F(1,2), F(1,2), F(3,4), F(1), F(2), F(3), F(10)],  # 1/4,1/2,3/4,P,2P,3P,10P (Min zvlast)
}
TARGET = {"F,C,2P,A":16, "F,C,1/2P,A":32, "F,C,P,A":20, "F,C,1/2P,P,A":40,
          "F,C,P,2P,A":64, "F,C,1/2P,P,2P,A":112, "FULL":172}

def count(menu, pot, stack, min_bet=False):
    """Decision nodes in a river betting round. State: (invested_each_before,
    faced_add, min_frac_idx, acted). Bet of fraction f = f*(pot after call).
    All-in always available. Returns decision-node count."""
    seen = [0]
    def rec(pot_now, faced, fmin_idx, first_action, spent_cap):
        # pot_now = total pot if current player calls; faced = amount to call
        # spent_cap = remaining stack of actor after calling (symmetric approx)
        seen[0] += 1
        # opponent responses / actions:
        # 1) fold (only if faced>0) -> terminal
        # 2) call/check -> terminal or (first check -> opponent acts)
        if faced == 0 and first_action:
            rec(pot_now, 0, fmin_idx, False, spent_cap)  # check -> other player decision
        # 3) raises: fractions >= fmin
        for i, f in enumerate(menu[fmin_idx:], start=fmin_idx):
            amt = f * pot_now
            if amt < spent_cap:      # normal raise, opponent gets a decision
                rec(pot_now + 2*amt, amt, i, False, spent_cap - amt)
            # amt >= remaining -> covered by all-in below
        # 4) all-in (if any chips remain)
        if spent_cap > 0:
            rec(pot_now + 2*spent_cap, spent_cap, len(menu), False, 0)
        # faced allin -> opponent can only fold/call: that IS still a decision node (counted on entry)
    rec(pot, 0, 0, True, stack)
    return seen[0]

for pot in [100, 200, 400, 1000, 2000, 4000, 100000]:
    row = {k: count(m, F(pot), F(20000)) for k, m in MENUS.items()}
    hit = sum(row[k] == TARGET[k] for k in TARGET)
    print(pot, [row[k] for k in TARGET], f"match {hit}/7")

print("=== striktne rostouci frakce (dalsi bet > predchozi) ===")
def count_strict(menu, pot, stack):
    seen = [0]
    def rec(pot_now, faced, fmin_idx, first_action, spent_cap):
        seen[0] += 1
        if faced == 0 and first_action:
            rec(pot_now, 0, fmin_idx, False, spent_cap)
        for i, f in enumerate(menu[fmin_idx:], start=fmin_idx):
            amt = f * pot_now
            if amt < spent_cap:
                rec(pot_now + 2*amt, amt, i + 1, False, spent_cap - amt)  # STRICT: next > f
        if spent_cap > 0:
            rec(pot_now + 2*spent_cap, spent_cap, len(menu), False, 0)
    rec(pot, 0, 0, True, stack)
    return seen[0]

for pot in [100, 200, 400]:
    row = {k: count_strict(m, F(pot), F(20000)) for k, m in MENUS.items()}
    hit = sum(row[k] == TARGET[k] for k in TARGET)
    print(pot, [row[k] for k in TARGET], f"match {hit}/7")

print("=== neklesajici, frakce z potu PRED callem ===")
def count_pre(menu, pot, stack):
    seen = [0]
    def rec(pot_now, faced, fmin_idx, first_action, spent_cap):
        # pot_now = pot pred callem (obsahuje faced jednou)
        seen[0] += 1
        if faced == 0 and first_action:
            rec(pot_now, 0, fmin_idx, False, spent_cap)
        for i, f in enumerate(menu[fmin_idx:], start=fmin_idx):
            amt = f * pot_now   # frakce z potu PRED callem
            if amt < spent_cap:
                rec(pot_now + faced + 2*amt, amt, i, False, spent_cap - amt)
        if spent_cap > 0:
            rec(pot_now + faced + 2*spent_cap, spent_cap, len(menu), False, 0)
    rec(pot, 0, 0, True, stack)
    return seen[0]

print("=== nerostouci frakce (dalsi bet <= predchozi) ===")
def count_noninc(menu, pot, stack):
    seen = [0]
    def rec(pot_now, faced, fmax_idx, first_action, spent_cap):
        seen[0] += 1
        if faced == 0 and first_action:
            rec(pot_now, 0, fmax_idx, False, spent_cap)
        for i in range(0, fmax_idx + 1):
            f = menu[i]
            amt = f * pot_now
            if amt < spent_cap:
                rec(pot_now + 2*amt, amt, i, False, spent_cap - amt)
        if spent_cap > 0:
            rec(pot_now + 2*spent_cap, spent_cap, -1 if False else fmax_idx, False, 0)
    rec(pot, 0, len(menu) - 1, True, stack)
    return seen[0]

for name, fn in (("pre", count_pre), ("noninc", count_noninc)):
    for pot in [100, 200, 400]:
        row = {k: fn(m, F(pot), F(20000)) for k, m in MENUS.items()}
        hit = sum(row[k] == TARGET[k] for k in TARGET)
        print(name, pot, [row[k] for k in TARGET], f"match {hit}/7")
