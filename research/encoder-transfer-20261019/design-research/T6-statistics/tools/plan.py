"""Pure stdlib probability arithmetic. No empirical data, RNG, image or GPU use."""
import ast
import hashlib
import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[3]

def binpmf(n, p):
    return [math.comb(n, k)*p**k*(1-p)**(n-k) for k in range(n+1)]

def betapmf(n, p, rho):
    if rho == 0:
        return binpmf(n,p)
    a,b=p*(1/rho-1),(1-p)*(1/rho-1)
    lb=lambda x,y: math.lgamma(x)+math.lgamma(y)-math.lgamma(x+y)
    return [math.exp(math.log(math.comb(n,k))+lb(k+a,n-k+b)-lb(a,b)) for k in range(n+1)]

def oc(n,p,rho=0):
    pmf=betapmf(n,p,rho)
    assert abs(sum(pmf)-1)<1e-11
    fail=math.fsum(v for k,v in enumerate(pmf) if 2*k<n)
    transfer=math.fsum(pmf[(3*n+3)//4:])
    return dict(n=n,p_source=p,source_icc=rho,FAILS=fail,PARTIAL=1-fail-transfer,TRANSFERS=transfer)

# Review only pure mathematical functions from the draft, without importing it.
draft=ROOT/'scripts/encoder_transfer_test.py'
source=draft.read_text(encoding='utf-8')
tree=ast.parse(source)
selected=['cp_interval','binomial_threshold','decision','sign_test','majority']
nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in selected]
namespace={'math':math}
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(draft),'exec'),namespace)
cp=namespace['cp_interval']
checks=[]
for n in (60,90,120):
    assert abs(cp(0,n)[1]-(1-.025**(1/n)))<1e-12
    assert abs(cp(n,n)[0]-.025**(1/n))<1e-12
    for k in range(n+1):
        lo,hi=cp(k,n)
        assert 0<=lo<=k/n<=hi<=1
        a,b=cp(n-k,n)
        assert abs(lo-(1-b))<1e-12 and abs(hi-(1-a))<1e-12
    checks.append(f'CP n={n}: all k bounds and reflection; exact k=0,n limits pass')
for n in range(60,121):
    cut=(3*n+3)//4
    for k in range(n+1):
        d=namespace['decision'](n,k,0,0,0,{'wam':k})
        assert d['label']==('FAILS' if 2*k<n else 'TRANSFERS' if k>=cut else 'PARTIAL')
        for neg in ((1,0,0),(0,1,0),(0,0,1)):
            assert namespace['decision'](n,k,*neg,{'wam':k})['label']!='TRANSFERS'
checks.append('All decision counts n=60..120 and nonzero/unresolved negatives pass')
assert namespace['sign_test']([True]*6,[False]*6)['p_two_sided']==.03125
assert namespace['sign_test']([True]*3,[True]*3)['p_two_sided']==1
checks.append('Sign test six all-direction discordances=.03125, no discordances=1')
ps=[.5,.6,.7,.75,.8,.85,.9]
ns=[60,90,120]
table=[oc(n,p) for n in ns for p in ps]
within=[]
for q in ps:
    for rho in (0,.1,.3,.5,.9):
        p=math.fsum(betapmf(3,q,rho)[2:])
        within.append(dict(p_seed=q,seed_icc=rho,p_source_majority=p,oc_n60=oc(60,p)))
cross=[oc(n,p,rho) for n in ns for p in ps for rho in (.01,.05)]
thresholds=[]
for bits in (32,100):
    k=namespace['binomial_threshold'](bits)
    thresholds.append(dict(bits=bits,k=k,tail=sum(math.comb(bits,j) for j in range(k,bits+1))/2**bits,
                           previous_tail=sum(math.comb(bits,j) for j in range(k-1,bits+1))/2**bits))
intervals=[dict(n=n,k=k,cp95=cp(k,n)) for n in ns for k in sorted({0,n//2,(3*n+3)//4,n})]
budget=[]
for n in ns:
    # Five image streams: four marked arms + shared C0. Wrong-owner is decoding only.
    core=90*n
    rinse=15*n # Reuses existing .1 first pass; three additional second passes.
    budget.append(dict(n=n,core_regeneration_calls=core,optional_rinse_extra_calls=rinse,
        d1_roundtrips=5*n,resize_controls=5*n,
        max_average_seconds_per_core_call_given_3h_nonregen_reserve=12*3600/core,
        max_average_seconds_per_call_with_rinse_given_3h_nonregen_reserve=12*3600/(core+rinse)))
output=dict(schema='encoder-transfer-T6-planning-v1',kind='analytic planning only; no observations or random simulations',
    recommendation_n=60,source_oc_assumption='independent exchangeable source-majority Bernoulli indicators; negative gate complete and zero',
    source_oc=table,within_source_beta_binomial=within,cross_source_beta_binomial_illustrative=cross,
    negative_gate='TRANSFERS probability is joint P(K>=ceil(.75n), G); table assumes G=1. FAILS unaffected. If independent G with probability g, multiply table TRANSFERS by g, move remainder to PARTIAL.',
    negative_gate_g_sensitivity=[dict(g=g,**{f'p{p}':oc(60,p)['TRANSFERS']*g for p in ps}) for g in (.8,.9,.95,1)],
    cp95_examples=intervals,thresholds=thresholds,budget=budget,
    zero_negative_one_sided95=[dict(n=n,upper=1-.05**(1/n)) for n in (60,120,540,1080)],
    independent_zero_trials_required_for_upper1e4=math.ceil(math.log(.05)/math.log(1-1e-4)),
    draft_review=dict(path=str(draft),sha256=hashlib.sha256(source.encode()).hexdigest(),checks=checks))
(OUT/'planning-table.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(source_oc=table,intervals=intervals,thresholds=thresholds,budget=budget,checks=checks),indent=2))
