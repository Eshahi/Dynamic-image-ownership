"""CPU-only fixed-denominator analysis for the prospective symbol screen."""
from __future__ import annotations
import statistics
IDS=(30,72,73,89,127,165)
ALPHA,BETA='qim-pilot-owner-alpha','qim-pilot-owner-beta'
METRICS=('S','Q','J','H','F')

def summarize(record):
    rows=record['rows']; sources=record['sources']; strengths={}
    def endpoint(row,owner,metric):
        return row.get('endpoints',{}).get(owner,{}).get(metric) if row.get('status')=='ok' else None
    def select(sid,arm,phase,strength=None):
        return [r for r in rows if r['source_id']==sid and r['arm']==arm and r['phase']==phase and (phase!='T3' or r['strength']==strength)]
    def single(sid,arm,phase): return select(sid,arm,phase)[0]
    clean={a:dict(denominator=6,strict_quality=sum(single(s,a,'clean').get('strict_quality') is True for s in IDS),
        admission=sum(single(s,a,'clean').get('clean_eligible') is True for s in IDS)) for a in ('C','S')}
    for strength in (.2,.4):
        arms={}
        for arm in ('C','S'):
            per_source={}
            for sid in IDS:
                item={}
                for metric in METRICS:
                    vals=[endpoint(r,ALPHA,metric) for r in select(sid,arm,'T3',strength)]
                    yes=sum(v is True for v in vals); missing=sum(v is None for v in vals)
                    item[metric]=dict(seed_successes=yes,unavailable=missing,majority_lower=yes>=2,majority_upper=yes+missing>=2)
                item['clean_admission']=single(sid,arm,'clean').get('clean_eligible') is True
                per_source[str(sid)]=item
            arms[arm]=dict(per_source=per_source,seed_denominator=18,source_denominator=6,
                seed_successes={m:sum(s[m]['seed_successes'] for s in per_source.values()) for m in METRICS},
                majority_lower={m:sum(s[m]['majority_lower'] for s in per_source.values()) for m in METRICS},
                majority_upper={m:sum(s[m]['majority_upper'] for s in per_source.values()) for m in METRICS},
                clean_gated_majority_J=sum(s['clean_admission'] and s['J']['majority_lower'] for s in per_source.values()))
        c,s=arms['C'],arms['S']
        lower=c['majority_lower']['J']-s['majority_upper']['J']; upper=c['majority_upper']['J']-s['majority_lower']['J']
        only=sum(c['per_source'][str(sid)]['J']['majority_lower'] and not s['per_source'][str(sid)]['J']['majority_upper'] for sid in IDS)
        strengths[str(strength)]=dict(arms=arms,C_minus_S_majority_J_bounds=[lower,upper],definite_C_only=only)
    negatives={}
    for phase in ('clean','sd15_vae','sdxl_vae','T3'):
        for arm,owner in (('C0',ALPHA),('C0',BETA),('C',BETA),('S',BETA)):
            selected=[r for r in rows if r['phase']==phase and r['arm']==arm]
            values=[endpoint(r,owner,'A') for r in selected]
            negatives[f'{phase}:{arm}:{owner}']=dict(planned=len(values),observed=sum(v is not None for v in values),events=sum(v is True for v in values),unavailable=sum(v is None for v in values))
    neg_complete=all(n['unavailable']==0 and n['events']==0 for n in negatives.values())
    vae_adverse=[]
    for sid in IDS:
        for phase in ('sd15_vae','sdxl_vae'):
            c,s=(endpoint(single(sid,a,phase),ALPHA,'J') for a in ('C','S'))
            if s is True and c is not True: vae_adverse.append(dict(source_id=sid,phase=phase,control_unavailable=c is None))
    lower_h=[]
    for sid in IDS:
        c,s=(single(sid,a,'clean').get('projection_diagnostics',{}).get('within_symbol_H') for a in ('C','S'))
        if c is not None and s is not None and c<s: lower_h.append(sid)
    raw={}; threshold_only=False
    for arm in ('C','S'):
        errors=[endpoint(r,ALPHA,'raw_coded_bit_errors') for r in rows if r['phase']=='T3' and r['strength']==.4 and r['arm']==arm]
        observed=[v for v in errors if v is not None]
        raw[arm]=dict(planned=18,observed=len(observed),median=statistics.median(observed) if observed else None)
    raw_improvement=all(raw[a]['observed']==18 for a in ('C','S')) and raw['C']['median']<raw['S']['median']
    clean_complete=all(sources[str(s)].get('status')=='ok' for s in IDS)
    pair_pass=all(sources[str(s)].get('pair_pass') is True for s in IDS)
    h1=(pair_pass and neg_complete and not vae_adverse and strengths['0.2']['C_minus_S_majority_J_bounds'][0]>=0 and
        strengths['0.4']['C_minus_S_majority_J_bounds'][0]>=2 and strengths['0.4']['definite_C_only']>=2)
    shaping=len(lower_h)>=5 and raw_improvement
    threshold_only=bool(strengths['0.4']['C_minus_S_majority_J_bounds'][0]>0 and not raw_improvement)
    if clean_complete and not pair_pass: decision='distortion-control-inconclusive'
    elif record['outcome']!='completed': decision='execution-inconclusive'
    elif h1 and shaping: decision='H1-mechanism-lead'
    elif not neg_complete: decision='execution-inconclusive'
    else: decision='H1-not-supported'
    # A fully measured preliminary unusable pair is a scientific stop, even
    # though the equal-distortion mechanism question remains inconclusive.
    if record['outcome']=='scientific_stop': decision='distortion-control-inconclusive'
    return dict(decision=decision,planned_sources=6,planned_transformations=108,planned_VAE_reconstructions=36,
        planned_rows=162,observed_rows=sum(r['status']=='ok' for r in rows),clean=clean,strengths=strengths,negatives=negatives,
        clean_pairs_complete=clean_complete,pair_pass=pair_pass,vae_adverse_identities=vae_adverse,
        endpoint_separation_predicate=h1,shaping_diagnostic_predicate=shaping,lower_H_control_sources=lower_h,
        raw_coded_errors_stress=raw,threshold_only_or_unexplained_effect=threshold_only,
        admissibility_proxies={str(limit):{arm:{basis:sum(r.get(basis,{}).get('lpips',float('inf'))<=limit
            for r in rows if r['phase']=='T3' and r['arm']==arm and r['status']=='ok')
            for basis in ('quality_input','quality_attacked_C0')} for arm in ('C','S')} for limit in (.2,.3)},
        interpretation='Exploratory initializer mechanism only; no candidate/security advancement or human admissibility.')
