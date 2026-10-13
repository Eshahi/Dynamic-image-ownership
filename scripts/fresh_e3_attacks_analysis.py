"""Fixed-denominator Stage B analysis; no inference or threshold fitting."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

ALPHA, BETA = 'qim-pilot-owner-alpha', 'qim-pilot-owner-beta'
METRICS = ('S', 'Q', 'J', 'H', 'F')

def summarize(record, rows, parent):
    ids = [s['source_id'] for s in parent['sources']]
    index = {r['id']: r for r in rows}
    if len(index) != len(rows):
        raise ValueError('Duplicate scientific identities')
    def value(r, owner, metric, mode=None):
        if r.get('status') != 'ok': return None
        e = r.get('endpoints', {})
        if mode: e = e.get(mode, {})
        return e.get(owner, {}).get(metric)
    strengths = {}
    for strength in (.1, .2, .4):
        cells = {}
        for arm in ('E', 'L'):
            sources = {}
            for sid in ids:
                entries = [index[f'{sid}:T3:{strength}:{seed}:{arm}'] for seed in (6,7,8)]
                sources[str(sid)] = {m: dict(success=sum(value(r,ALPHA,m) is True for r in entries),
                    missing=sum(value(r,ALPHA,m) is None for r in entries)) for m in METRICS}
                for m in METRICS:
                    cell=sources[str(sid)][m]; cell['lower']=cell['success']>=2; cell['upper']=cell['success']+cell['missing']>=2
            eligible={str(s['source_id']):s['clean']['full' if arm=='E' else 'lean']['clean_eligible'] for s in parent['sources']}
            cells[arm]=dict(per_source=sources, denominator=24, seed_denominator=72,
                seed_successes={m:sum(s[m]['success'] for s in sources.values()) for m in METRICS},
                majority_lower={m:sum(s[m]['lower'] for s in sources.values()) for m in METRICS},
                majority_upper={m:sum(s[m]['upper'] for s in sources.values()) for m in METRICS},
                clean_gated_J=sum(eligible[sid] and s['J']['lower'] for sid,s in sources.items()))
        lower=sum(int(cells['L']['per_source'][str(s)]['J']['lower'])-int(cells['E']['per_source'][str(s)]['J']['upper']) for s in ids)
        upper=sum(int(cells['L']['per_source'][str(s)]['J']['upper'])-int(cells['E']['per_source'][str(s)]['J']['lower']) for s in ids)
        strengths[str(strength)]=dict(arms=cells,L_minus_E_J_interval=[lower,upper],
            discordant_ids=[s for s in ids if cells['L']['per_source'][str(s)]['J']['lower']!=cells['E']['per_source'][str(s)]['J']['lower']])
    negatives={}
    negative_block=False; negative_unknown=False; vae_loss=False; vae_unknown=False
    for phase in ('sd15_vae','sdxl_vae','T3'):
        selected=[r for r in rows if r['phase']==phase]
        for arm,owner in (('C0',ALPHA),('C0',BETA),('E',BETA),('L',BETA)):
            panel=[r for r in selected if r['arm']==arm]
            negatives[f'{phase}:{arm}:{owner}']=dict(planned=len(panel),observed=sum(value(r,owner,'A') is not None for r in panel),
                events=sum(value(r,owner,'A') is True for r in panel),unresolved=sum(value(r,owner,'A') is None for r in panel))
        for r in selected:
            if r['arm']=='C0':
                negative_block |= any(value(r,o,'A') is True for o in (ALPHA,BETA))
                negative_unknown |= any(value(r,o,'A') is None for o in (ALPHA,BETA))
            if r['arm']=='L':
                e=index[r['id'][:-1]+'E']; lv,ev=value(r,BETA,'A'),value(e,BETA,'A')
                negative_block |= lv is True and ev is False
                negative_unknown |= lv is None or ev is None
                if phase!='T3':
                    lj,ej=value(r,ALPHA,'J'),value(e,ALPHA,'J')
                    vae_loss |= lj is False and ej is True
                    vae_unknown |= lj is None or ej is None
    transfers={}; transfer_block=False; transfer_unknown=False
    for phase in ('T4','T5'):
        panel=[r for r in rows if r['phase']==phase]
        transfers[phase]={}
        for arm in ('E','L'):
            for op in sorted({r['operator'] for r in panel}):
                entries=[r for r in panel if r['arm']==arm and r['operator']==op]
                modes={}
                for mode in ('none','semantic_only','perceptual_only','combined'):
                    observed=[r for r in entries if value(r,ALPHA,'A',mode) is not None]
                    delivered=[r for r in observed if value(r,ALPHA,'D',mode)]
                    modes[mode]=dict(planned=len(entries),observed=len(observed),unresolved=len(entries)-len(observed),
                        unconditional={m:sum(value(r,ALPHA,m,mode) is True for r in entries) for m in ('Q','H','D','F','A')},
                        delivered_denominator=len(delivered),delivered_F=sum(value(r,ALPHA,'F',mode) is True for r in delivered),
                        beta_negative=dict(planned=len(entries),observed=sum(value(r,BETA,'A',mode) is not None for r in entries),
                            events=sum(value(r,BETA,'A',mode) is True for r in entries),unresolved=sum(value(r,BETA,'A',mode) is None for r in entries)))
                transfers[phase][f'{arm}:{op}']=modes
        for r in panel:
            if r['operator']=='sham':
                transfer_block |= any(value(r,o,'A',m) is True for o in (ALPHA,BETA) for m in ('none','semantic_only','perceptual_only','combined'))
                transfer_unknown |= any(value(r,o,'A',m) is None for o in (ALPHA,BETA) for m in ('none','semantic_only','perceptual_only','combined'))
            elif r['arm']=='L':
                e=index[r['id'][:-1]+'E']; l,v=value(r,ALPHA,'F','combined'),value(e,ALPHA,'F','combined')
                transfer_block |= l is True and v is False
                transfer_unknown |= l is None or v is None
    primary=all(strengths[str(s)]['L_minus_E_J_interval'][0]>=-1 for s in (.1,.2))
    complete=all(r['status'] in ('ok','safety_blocked') for r in rows)
    resolved=complete and not (negative_unknown or vae_unknown or transfer_unknown)
    t5_complete=record['t5_shortfall']==0
    full_pass=primary and resolved and t5_complete and not (negative_block or vae_loss or transfer_block) and record.get('outcome')=='completed'
    return dict(planned=len(rows),statuses=dict(Counter(r['status'] for r in rows)),complete=complete,
        actual_transformation_attempts=sum(r.get('transformation_attempted') is True for r in rows),aliases=sum(bool(r.get('alias_of')) for r in rows),
        strengths=strengths,negatives=negatives,transfers=transfers,stage_A_clean_reuse=parent['summary']['clean'],
        t5_shortfall=record['t5_shortfall'],t5_requested_pairs=6,t5_selected_pairs=6-record['t5_shortfall'],
        t5_requested_transformations=24,t5_unavailable_shortfall_transformations=4*record['t5_shortfall'],
        primary_preservation=primary,vae_loss=vae_loss,negative_regression=negative_block,
        transfer_regression=transfer_block,missing_relevant_calls=not resolved,full_threat_pass=full_pass,
        decision='lean-survivor' if full_pass else 'reject-fixed-lean' if (vae_loss or negative_block or transfer_block or any(strengths[str(s)]['L_minus_E_J_interval'][1]<-1 for s in (.1,.2))) else 'inconclusive',
        interpretation='Exploratory only; missing positives bound false/true, missing negatives unresolved. T5 shortfall prevents full threat pass; human admissibility missing.')

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--run',type=Path,required=True); a=p.parse_args()
    r=json.loads(a.run.read_text()); rows=json.loads((a.run.parent/'rows.json').read_text()); parent=json.loads(Path(r['parent']).read_text())
    print(json.dumps(summarize(r,rows,parent),indent=2))

if __name__=='__main__': main()
