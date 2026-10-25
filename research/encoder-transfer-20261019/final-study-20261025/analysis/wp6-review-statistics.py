"""Independent abstract arithmetic audit; no experimental execution or author imports."""
from fractions import Fraction as F
from itertools import product
from math import comb, fsum, log, log1p, exp
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
N, ALPHA = 200, F(1,260)
GRID = [F(1,16),F(1,8),F(1,4),F(1,2),F(3,4),F(1)]
def mix(vals):
    wealth = [F(1)]*6
    for z in vals:
        assert -1 <= z <= F(4,5)
        wealth = [k*(1+l*z) for k,l in zip(wealth,GRID)]
    return sum(wealth)/6
def by_count(k,n=200):
    return sum((1+l/5)**(n-k)*(1-4*l/5)**k for l in GRID)/6
def tail(k,p,n=200):
    return sum(F(comb(n,j))*p**j*(1-p)**(n-j) for j in range(k+1))
def pval(e):
    return min(F(1),1/e) if e else F(1)

mean_pass = [k for k in range(201) if by_count(k)>=260]
cal_pass = [k for k in range(201) if tail(k,F(1,10))<=ALPHA]
assert mean_pass==list(range(21)) and cal_pass==list(range(10))
scenarios = {str(e):float(tail(9,e)) for e in [F(1,100),F(1,50),F(3,100),F(1,25),F(1,20),F(3,40)]}
perfect = {}
for b in [F(1,4),F(1,10),F(1,25),F(1,100)]:
    n=0
    while sum((1+F(4,5)*b*l)**n for l in GRID)/6 < 260:
        n+=1
    perfect[str(b)] = {'minimum_n':n,'p_at_200':float(pval(mix([F(4,5)*b]*200)))}
assert [v['minimum_n'] for v in perfect.values()]==[40,94,228,900]

# Null identity at several finite n, enumerating endpoint counts, not sampling.
# Z=.8 with probability5/9 and -1 otherwise has exactly zero mean.
null = {}
for n in [1,2,10,30]:
    expected=sum(F(comb(n,k))*F(5,9)**k*F(4,9)**(n-k)*mix([F(4,5)]*k+[F(-1)]*(n-k)) for k in range(n+1))
    assert expected==1
    null[str(n)]=str(expected)
# Legal zero factor eliminates lambda=1; averaging retains its weight.
assert mix([F(-1)]) == sum(1-l for l in GRID)/6
assert mix([F(4,5),F(-1)]) == mix([F(-1),F(4,5)])

# Check all three-call majority sets and all combinations of A/Q/S types.
patterns=[]
for pattern in product([0,1,None],repeat=3):
    options=[(0,1) if x is None else (x,) for x in pattern]
    feasible=sorted({int(sum(v)>=2) for v in product(*options)})
    p,u=pattern.count(1),pattern.count(None)
    claimed=list(range(int(p>=2),int(p+u>=2)+1))
    assert feasible==claimed
    patterns.append({'pattern':pattern,'majorities':feasible})
losschecks=0
for a_set,s_set,q_set in product([(0,),(1,),(0,1)],[(0,),(1,),(0,1)],[(F(0),),(F(1,4),),(F(1,2),),(F(1),),None]):
    lower=min(F(4,5)*(q-y)**2-(a-y)**2 for a,y in product(a_set,s_set) for q in ((F(y),) if q_set is None else q_set))
    # For an absent comparator, check an exact grid plus the proven minimizer y.
    qs=[F(j,20) for j in range(21)] if q_set is None else q_set
    for a,q,y in product(a_set,qs,s_set):
        t=F(4,5)*(q-y)**2-(a-y)**2
        assert -1 <= lower <= t <= F(4,5)
        losschecks+=1
    if len(a_set)==len(q_set or [])==1 and len(s_set)==2:
        y=1-a_set[0]
        assert lower==F(4,5)*(q_set[0]-y)**2-1

# CP inversions use direct binomial sums and 80 bounded bisection iterations.
def cdf_float(k,p):
    return fsum(comb(N,j)*p**j*(1-p)**(N-j) for j in range(k+1))
def upper_cp(k):
    lo,hi=0.,1.
    for _ in range(80):
        mid=(lo+hi)/2
        if cdf_float(k,mid)>float(ALPHA): lo=mid
        else: hi=mid
    return (lo+hi)/2
cp={'mismatch_9_upper':upper_cp(9),'quality_175_lower':1-upper_cp(25),'control_191_lower':1-upper_cp(9),'removal_120_lower':1-upper_cp(80)}
counter_p=F(1001,1800)
counter_logs=[float(counter_p)*log1p(float(l)*.8)+float(1-counter_p)*log1p(-float(l)) for l in GRID[:-1]]
assert all(v<0 for v in counter_logs)
out={
 'purpose':'Independent WP6 finite arithmetic; no experimental data, simulations, author imports or fitting',
 'fixed_grid':[str(l) for l in GRID], 'mean_cutoff':max(mean_pass),'calibration_and_joint_cutoff':max(cal_pass),
 'scenario_joint_power':scenarios, 'boundary_p':{str(k):float(pval(by_count(k))) for k in [9,20,21]},
 'perfect_law_constant_baseline':perfect,'null_expected_mixture_checks':null,
 'majority_patterns':patterns,'completion_loss_comparisons':losschecks,'cp_first_holm_limits':cp,
 'positive_mean_counterexample_mean':str(counter_p*F(4,5)+(1-counter_p)*(-1)),
 'positive_mean_counterexample_log_growth':counter_logs,
 'zero_factor_and_permutation_checks':'passed', 'all_checks_passed':True
}
(HERE/'wp6-review-statistics.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='majority_patterns'},indent=2))
