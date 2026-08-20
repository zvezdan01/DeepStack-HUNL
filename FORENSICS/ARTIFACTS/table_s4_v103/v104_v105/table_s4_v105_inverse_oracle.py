from fractions import Fraction
def bin_feasible(xs,centers):
    lows=[c-500 for c in centers]; highs=[c+499 for c in centers]
    alo=None; ahi=None
    for i in range(len(xs)):
        for j in range(len(xs)):
            if i==j: continue
            dx=xs[j]-xs[i]; rhs=highs[j]-lows[i]
            if dx>0:
                v=Fraction(rhs,dx); ahi=v if ahi is None or v<ahi else ahi
            elif dx<0:
                v=Fraction(rhs,dx); alo=v if alo is None or v>alo else alo
    return (alo is None or ahi is None or alo<=ahi)
