"""Stdlib exact finite-sum planning only: no observations, RNG, images or models.
Run with bundled Python. Executes only allowlisted pure functions from runner AST.
All sensitivity parameters are hypothetical, not estimated.
"""
import ast
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[3]
NS = (60, 90, 120)
PS = [j/100 for j in range(50,91)]
QS = [j/100 for j in range(50,91,5)]
RHOS = (0.,.1,.3,.5,.9,1.)
DS = (0.,.01,.05,.1,.2)

def binpmf(n,p):
    return [math.comb(n,k)*p**k*(1-p)**(n-k) for k in range(n+1)]

def betapmf(n,p,rho):
    if rho == 0: return binpmf(n,p)
    if rho == 1: return [1-p]+[0.]*(n-1)+[p]
    a,b=p*(1/rho-1),(1-p)*(1/rho-1)
    lb=lambda x,y: math.lgamma(x)+math.lgamma(y)-math.lgamma(x+y)
    return [math.exp(math.log(math.comb(n,k))+lb(k+a,n-k+b)-lb(a,b)) for k in range(n+1)]

def summarize(pmf,n):
    assert abs(math.fsum(pmf)-1)<2e-11
    cut=(3*n+3)//4
    fail=math.fsum(v for k,v in enumerate(pmf) if 2*k<n)
    transfer=math.fsum(pmf[cut:])
    partial=math.fsum(v for k,v in enumerate(pmf) if 2*k>=n and k<cut)
    assert abs(fail+partial+transfer-1)<2e-11
    return dict(FAILS=fail,PARTIAL=partial,TRANSFERS=transfer)

def oc(n,p,rho=0):
    return summarize(betapmf(n,p,rho),n)

def seed_majority(q,rho,success_loss=0):
    return math.fsum(v*math.fsum(binpmf(k,1-success_loss)[2:])
                    for k,v in enumerate(betapmf(3,q,rho)))

def exchangeable_bounds(q,rho):
    s=q*q+rho*q*(1-q)
    lo,hi=max(0.,2*s-q),min(s,1-3*q+3*s)
    assert lo<=hi+1e-12
    return 3*s-2*hi,3*s-2*lo

def informative_loss(p,d,ratio):
    d0=d/(p*ratio+1-p)
    d1=ratio*d0
    assert 0<=d0<=1 and 0<=d1<=1
    return d1,d0

def paired_route(n,pf,pb,both):
    """Exact DP. WAM=VINE per source; prescribed F5/baseline joint law; G=1."""
    probs=[(0,0,1-pf-pb+both),(0,1,pb-both),(1,0,pf-both),(1,1,both)]
    assert min(x[2] for x in probs)>=-1e-12
    dp={(0,0):1.}
    for _ in range(n):
        new={}
        for (a,b),prob in dp.items():
            for da,db,w in probs:
                if w>0:
                    key=(a+da,b+db)
                    new[key]=new.get(key,0.)+prob*w
        dp=new
    result={k:0. for k in ("ROUTE A","ROUTE B","ROUTE C","ROUTE UNDECIDED")}
    for (f,b),prob in dp.items():
        route=("ROUTE C" if 2*f<n else "ROUTE UNDECIDED" if f<(3*n+3)//4
               else "ROUTE A" if f>=b-(n+19)//20 else "ROUTE B")
        result[route]+=prob
    assert abs(sum(result.values())-1)<2e-11
    return result

def independent_routes(n,pf,pw,pv):
    """A second explicit joint law: independent methods and independent sources."""
    ff,ww,vv=binpmf(n,pf),binpmf(n,pw),binpmf(n,pv)
    cut=(3*n+3)//4; margin=(n+19)//20
    route_a=math.fsum(ff[f]*math.fsum(ww[:min(n,f+margin)+1])*math.fsum(vv[:min(n,f+margin)+1])
                      for f in range(cut,n+1))
    base=oc(n,pf)
    return {"ROUTE A":route_a,"ROUTE B":base["TRANSFERS"]-route_a,
            "ROUTE C":base["FAILS"],"ROUTE UNDECIDED":base["PARTIAL"]}

def write_table(name,rows):
    path=OUT/"tables"
    path.mkdir(exist_ok=True)
    (path/(name+".json")).write_text(json.dumps(rows,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    if rows:
        with (path/(name+".csv")).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return dict(rows=len(rows),json=f"tables/{name}.json",csv=f"tables/{name}.csv")

def main():
    tables={}
    tables["source_oc"]=write_table("source_oc",[dict(n=n,p_source=p,**oc(n,p)) for n in NS for p in PS])
    within,bounds,missing,informative=[],[],[],[]
    for n,q,rho in itertools.product(NS,QS,RHOS):
        p=seed_majority(q,rho)
        within.append(dict(n=n,q_seed=q,seed_icc=rho,p_source=p,**oc(n,p)))
        plo,phi=exchangeable_bounds(q,rho)
        bounds.append(dict(n=n,q_seed=q,seed_icc=rho,p_source_min=plo,p_source_max=phi,
                           transfer_min=oc(n,plo)["TRANSFERS"],transfer_max=oc(n,phi)["TRANSFERS"]))
        for d in DS:
            for kind,peff in (("independent_unit_loss",seed_majority(q,rho,d)),("whole_source_loss",(1-d)*p)):
                missing.append(dict(n=n,q_seed=q,seed_icc=rho,original_p_source=p,
                    missing_fraction=d,loss_model=kind,effective_p_source=peff,**oc(n,peff)))
            if d:
                for ratio in (.5,2.):
                    d1,d0=informative_loss(q,d,ratio)
                    peff=seed_majority(q,rho,d1)
                    informative.append(dict(n=n,q_seed=q,seed_icc=rho,original_p_source=p,
                        missing_fraction=d,loss_model="unit_loss_conditional_on_latent_seed",
                        loss_risk_ratio=ratio,loss_given_success=d1,loss_given_failure=d0,
                        effective_p_source=peff,**oc(n,peff)))
                    d1,d0=informative_loss(p,d,ratio)
                    peff=p*(1-d1)
                    informative.append(dict(n=n,q_seed=q,seed_icc=rho,original_p_source=p,
                        missing_fraction=d,loss_model="source_loss_conditional_on_latent_majority",
                        loss_risk_ratio=ratio,loss_given_success=d1,loss_given_failure=d0,
                        effective_p_source=peff,**oc(n,peff)))
    tables["within_source"]=write_table("within_source",within)
    tables["exchangeable_bounds"]=write_table("exchangeable_bounds",bounds)
    tables["missing_positive"]=write_table("missing_positive",missing)
    tables["informative_missing_positive"]=write_table("informative_missing_positive",informative)
    tables["fixed_missing_sources"]=write_table("fixed_missing_sources",[
        dict(n=n,p_source=p,missing_sources=h,remaining_sources=n-h,**summarize(binpmf(n-h,p),n))
        for n in NS for p in QS for h in sorted({0,1,n//20,n//10,n//5,n-(3*n+3)//4,n-(3*n+3)//4+1})])
    tables["cross_source"]=write_table("cross_source",[
        dict(n=n,p_source=p,source_icc=rho,variance_inflation=1+(n-1)*rho,**oc(n,p,rho))
        for n in NS for p in QS for rho in (.01,.05)])
    tables["joint_negative_gate"]=write_table("joint_negative_gate",[
        dict(n=n,p_source=p,g_complete_zero=g,FAILS=oc(n,p)["FAILS"],
             transfer_lower=max(0.,oc(n,p)["TRANSFERS"]+g-1),
             transfer_upper=min(oc(n,p)["TRANSFERS"],g),
             transfer_if_independent=oc(n,p)["TRANSFERS"]*g,
             PARTIAL_if_independent=1-oc(n,p)["FAILS"]-oc(n,p)["TRANSFERS"]*g)
        for n in NS for p in QS for g in (.5,.8,.9,.95,1.)])
    tables["negative_missing_gate"]=write_table("negative_missing_gate",[
        dict(n=n,r1_strength_count=s,gate_calls=6*s*n,marginal_missing_rate=d,
             g_complete_independent_calls=(1-d)**(6*s*n),
             g_complete_whole_source_loss=(1-d)**n,g_complete_all_calls_common_loss=1-d,
             g_complete_arbitrary_dependence_lower=max(0,1-6*s*n*d),
             g_complete_arbitrary_dependence_upper=1-d)
        for n in NS for s in (2,3) for d in (.0001,.001,.005,.01,.05)])
    tables["negative_fpr_resolution"]=write_table("negative_fpr_resolution",[
        dict(n_sources=n,trial_unit=unit,independent_trials=m,one_sided95_upper=1-.05**(1/m),
             two_sided95_upper=1-.025**(1/m),empirical_step=1/m)
        for n in NS for unit,m in (("source_any_negative",n),("hypothetical_full_independent_calls",18*n),
                                  ("hypothetical_reduced_independent_calls",12*n))])
    tables["negative_false_gate"]=write_table("negative_false_gate",[
        dict(n=n,gate_calls=18*n,per_call_false_rate=f,g_zero_if_independent_calls=(1-f)**(18*n),
             g_zero_if_perfect_dependence_within_source=(1-f)**n,g_zero_if_all_calls_identical=1-f,
             g_zero_lower=max(0.,1-18*n*f),g_zero_upper=1-f)
        for n in NS for f in (1e-4,1e-3,1e-2)])
    routes=[]
    for n,pf,pb in itertools.product(NS,(.8,),(.8,.85)):
        for name,both in (("lowest_feasible_p11",max(0.,pf+pb-1)),("independent_F_and_shared_B",pf*pb),
                          ("highest_feasible_p11",min(pf,pb))):
            routes.append(dict(n=n,p_f5=pf,p_wam=pb,p_vine=pb,wam_equals_vine=True,
                               dependence=name,p11_f5_baseline=both,**paired_route(n,pf,pb,both)))
    tables["paired_route_examples"]=write_table("paired_route_examples",routes)
    independent=[dict(n=n,p_f5=pf,p_wam=pw,p_vine=pv,
                      dependence="independent_methods_and_sources_G1",**independent_routes(n,pf,pw,pv))
                 for n,pf,pw,pv in itertools.product(NS,(.75,.8,.85),(.8,.85),(.8,.85))]
    tables["independent_route_examples"]=write_table("independent_route_examples",independent)

    source=(ROOT/"scripts/encoder_transfer_test.py").read_text(encoding="utf-8")
    names=["cp_interval","binomial_threshold","decision","sign_test","majority","plan"]
    tree=ast.parse(source)
    nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names]
    env={"math":math,"unit_id":lambda *x:repr(x)}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),"runner_pure_functions","exec"),env)
    cp=env["cp_interval"]
    checks=[]
    for n in NS:
        for k in range(n+1):
            lo,hi=cp(k,n);a,b=cp(n-k,n)
            assert 0<=lo<=k/n<=hi<=1
            assert abs(lo-(1-b))<1e-12 and abs(hi-(1-a))<1e-12
        assert abs(cp(0,n)[1]-(1-.025**(1/n)))<1e-12
        assert abs(cp(n,n)[0]-.025**(1/n))<1e-12
    checks.append("CP every k at all three n: bounds, reflection, exact endpoint identities")
    for n in range(60,121):
        for k in range(n+1):
            label="FAILS" if 2*k<n else "TRANSFERS" if k>=(3*n+3)//4 else "PARTIAL"
            assert env["decision"](n,k,0,0,0,{"wam":k})["label"]==label
            for neg in ((1,0,0),(0,1,0),(0,0,1)):
                assert env["decision"](n,k,*neg,{"wam":k})["label"]!="TRANSFERS"
    checks.append("Runner exact thresholds and all three negative-gate blockers n60..120")
    for values in itertools.product((True,False,None),repeat=3):
        assert env["majority"](dict(zip((12,13,14),values)))==(values.count(True)>=2)
    checks.append("All 27 observed/missing seed patterns obey fixed majority")
    for q,rho in itertools.product(QS,RHOS):
        p=seed_majority(q,rho);plo,phi=exchangeable_bounds(q,rho)
        assert plo-1e-12<=p<=phi+1e-12
        assert abs(seed_majority(q,0)-(3*q*q-2*q**3))<1e-12
        assert abs(seed_majority(q,1)-q)<1e-12
        for d in DS:
            # Enumerate all 8 true triples and 8 retention masks independently.
            enumerated=0.
            for y in itertools.product((0,1),repeat=3):
                mass=betapmf(3,q,rho)[sum(y)]/math.comb(3,sum(y))
                for keep in itertools.product((0,1),repeat=3):
                    if sum(a*b for a,b in zip(y,keep))>=2:
                        enumerated+=mass*(1-d)**sum(keep)*d**(3-sum(keep))
            assert abs(enumerated-seed_majority(q,rho,d))<1e-12
            assert seed_majority(q,rho,d)<=p+1e-12
    checks.append("Beta limits, exchangeable bounds and missingness formula vs exhaustive 64-pattern enumeration")
    for q,rho in itertools.product(QS,RHOS):
        s=q*q+rho*q*(1-q)
        for t in (max(0.,2*s-q),min(s,1-3*q+3*s)):
            probs=[1-3*q+3*s-t,3*q-6*s+3*t,3*(s-t),t]
            assert min(probs)>-1e-12
            assert abs(sum(probs)-1)<1e-12
            assert abs(sum(k*x for k,x in enumerate(probs))/3-q)<1e-12
    checks.append("Sharp finite-exchangeable endpoints: valid probability distributions and preserved mean")
    assert env["sign_test"]([True]*6,[False]*6)["p_two_sided"]==.03125
    assert env["sign_test"]([True]*3,[True]*3)["p_two_sided"]==1
    checks.append("Exact sign test discordance examples and ties")
    for row in routes:
        assert abs(row["ROUTE A"]+row["ROUTE B"]-oc(row["n"],row["p_f5"])["TRANSFERS"])<1e-11
    checks.append("Paired-route DP collapses to univariate F5 transfer probability")
    for row in independent:
        assert abs(sum(row[k] for k in ("ROUTE A","ROUTE B","ROUTE C","ROUTE UNDECIDED"))-1)<2e-11
    checks.append("Independent-two-baseline route maximum partitions all labels")
    cfg=json.loads((ROOT/"research/encoder-transfer-20261019/frozen-config.json").read_text(encoding="utf-8-sig"))
    synthetic_ids={"sources":[{"source_id":i} for i in range(cfg["n"])],"smoke":[{"source_id":-1},{"source_id":-2}]}
    # Abstract identifiers only, no real image roster accessed.
    units=list(env["plan"](cfg,synthetic_ids))
    smoke=list(env["plan"](cfg,synthetic_ids,True))
    assert len(units)==125*cfg["n"] and len(smoke)==250
    checks.append("Frozen abstract plan 125n full units plus smoke250, no images/real records used")
    tables["cp_examples"]=write_table("cp_examples",[
        dict(n=n,k=k,lower=cp(k,n)[0],upper=cp(k,n)[1])
        for n in NS for k in sorted({0,n//2,(3*n+3)//4,n})])
    tables["budget"]=write_table("budget",[
        dict(n=n,full_units=125*n,smoke_units=250,total_units=125*n+250,
             primary_seed_calls=3*n,full_gate_calls=18*n,reduced_gate_calls=12*n,
             core_regeneration=90*n,rinse=15*n,clean=5*n,d1=5*n,x1_x2=10*n,
             illustrative_total_hours_low=10*(125*n+250)/7750,
             illustrative_total_hours_high=14*(125*n+250)/7750,
             average_seconds_per_unit_after_3h_reserve=(15-3)*3600/(125*n+250))
        for n in NS])
    thresholds=[]
    for bits in (32,100):
        k=env["binomial_threshold"](bits)
        tail=sum(math.comb(bits,j) for j in range(k,bits+1))/2**bits
        prev=sum(math.comb(bits,j) for j in range(k-1,bits+1))/2**bits
        assert tail<=1e-4<prev
        thresholds.append(dict(bits=bits,k=k,tail=tail,previous_tail=prev))
    output=dict(schema="encoder-transfer-T6-planning-v2",kind="analytic hypothetical planning; no observations",
        recommendation_n=60,source_rule_unchanged=True,seeds=[12,13,14],tables=tables,checks=checks,
        gate_scope="All TRANSFERS in count tables assume complete zero R1 F5 negatives; not unconditional assurance",
        negative_trials_for_one_sided95_upper_1e4=math.ceil(math.log(.05)/math.log(1-1e-4)),
        thresholds=thresholds,runner_sha256=hashlib.sha256(source.encode()).hexdigest(),
        frozen_config_sha256=hashlib.sha256((ROOT/"research/encoder-transfer-20261019/frozen-config.json").read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"planning-table-v2.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2))

if __name__=="__main__":
    main()
