"""Pure fixed-inventory summaries after caller verification of retained artifacts.

No files/models/threshold fitting. This arithmetic is not an artifact audit or
authorization: the official collector must verify every supplied observation.
"""
from __future__ import annotations
from collections import Counter
import math
from m1_confirmatory_endpoints import cell, bounds
from m1_blind_noise_core import classify_scores

VERSION='m1-scientific-analysis-v1'
V5_THRESHOLDS=(4.982033056390042,8.259326826136963)

def finite(v):return type(v) in (int,float) and math.isfinite(v)

def decisions(method,value):
    if type(value) is not dict:raise ValueError('Explicit detector result required')
    if method=='candidate':
        if not all(finite(value.get(c)) for c in ('s','i')):raise ValueError('Invalid candidate scores')
        expected=classify_scores(value['s'],value['i'])
        if value.get('flags')!=expected['flags'] or value.get('state')!=expected['state']:
            raise ValueError('Candidate threshold/state parity differs')
        if any(type(value['flags'].get(c)) is not bool for c in ('s','i')):raise ValueError('Exact channel Boolean required')
        s,i=expected['flags']['s'],expected['flags']['i']
        return dict(semantic=s,instance=i,both=s and i,state=expected['state'],carrier_presence=None)
    if method!='v5':raise ValueError('Frozen method name required')
    if value.get('owners_tested')!=1 or value.get('binding_mode')!='combined' or value.get('embedding_domain')!='image':
        raise ValueError('Frozen v5 single-claim image-domain operating point required')
    for name in ('semantic','instance'):
        c=value.get(name,{})
        if (c.get('recomputed_threshold'),c.get('decoded_threshold'))!=V5_THRESHOLDS:raise ValueError('V5 thresholds differ')
        if any(type(c.get(k)) is not bool for k in ('content_match','found')):raise ValueError('V5 channel flags malformed')
    s,i=(value[n]['content_match'] for n in ('semantic','instance'))
    if type(value.get('outcome')) is not str or (value['outcome']=='both_match')!=(s and i):raise ValueError('V5 joint state differs')
    if type(value.get('watermark_found')) is not bool:raise ValueError('V5 presence missing')
    return dict(semantic=s,instance=i,both=s and i,state=value['outcome'],carrier_presence=value['watermark_found'])

def quality(value):
    if type(value) is not dict or type(value.get('psnr_infinite')) is not bool:raise ValueError('Explicit PSNR finite/infinite convention required')
    if value['psnr_infinite']:
        if value.get('psnr_db') is not None:raise ValueError('Infinite PSNR must use null numeric value')
        p=True
    else:
        if not finite(value.get('psnr_db')):raise ValueError('Finite PSNR required')
        p=value['psnr_db']>35
    if not finite(value.get('ssim_rgb')) or not finite(value.get('lpips')):raise ValueError('SSIM/LPIPS unavailable')
    if not -1<=value['ssim_rgb']<=1 or value['lpips']<0:raise ValueError('Metric range invalid')
    result=dict(psnr=p,ssim=value['ssim_rgb']>.9,lpips=value['lpips']<.1)
    result['joint']=all(result.values())
    if 'quality_admissible' in value and (type(value['quality_admissible']) is not bool or value['quality_admissible']!=result['joint']):raise ValueError('Recorded quality conjunction differs')
    return result

def cell_identity(unit):
    axis=unit['axis'];role=unit['claim_role'];arm=unit['arm']
    base=[unit['method'],axis,arm,role]
    if axis=='clean':return tuple(base),unit['group_id']
    if axis=='T3':return tuple(base+[unit['attack_channel']['id']]),unit['group_id']
    stratum='same-public-owner' if unit.get('same_public_owner') else 'different-public-owner'
    if axis=='T4':return tuple(base+[str(unit['patch_size']),unit['donor_arm'],stratum]),str(unit['pair_index'])
    if axis=='T5':return tuple(base+[unit['endpoint'],stratum]),unit['pair_id']
    raise ValueError('Unknown planned axis')

def analyze_verified_units(planned,observed,*,t5_selected_pairs=None,owner_schedule=None):
    """Caller supplies artifact-verified observations; missing/invalid stays adverse.

    Each observed query repeats all scientific metadata from its planned unit,
    and carries ``decision``. Image observations carry ``quality_vs_source``.
    T5 units are materialized only by the fixed post-unlock selector, with
    pair_id and endpoint left/right; no pair observations are inferred here.
    """
    by_id={u['id']:u for u in planned}
    if len(by_id)!=len(planned):raise ValueError('Duplicate planned unit')
    enrolled=dict(owner_schedule or {})
    for unit in planned:
        if unit.get('axis')=='clean' and unit.get('claim_role')=='marked-correct':
            uid,owner=unit['source_uid'],unit['owner']
            if uid in enrolled and enrolled[uid]!=owner:raise ValueError('Conflicting enrolled owner schedule')
            enrolled[uid]=owner
    for unit in planned:
        if unit.get('kind')!='query' or unit.get('axis') not in ('T4','T5'):continue
        try:
            same=(enrolled[unit['donor_uid']]==enrolled[unit['recipient_uid']] if unit['axis']=='T4'
                  else enrolled[unit['source_uid']]==unit['owner'])
        except KeyError as error:raise ValueError('Exact owner schedule required for paired claims') from error
        if type(unit.get('same_public_owner')) is not bool or unit['same_public_owner']!=same:
            raise ValueError('Paired public-owner equality flag differs')
    actual={}
    for row in observed:
        if row.get('id') not in by_id or row['id'] in actual:raise ValueError('Extra/duplicate observed unit')
        actual[row['id']]=row
    errors={};groups={};quality_groups={};ledger=[]
    metadata=('method','source_uid','group_id','axis','arm','owner','claim_role','attack_channel',
      'pair_index','donor_uid','recipient_uid','patch_size','donor_arm','pair_id','endpoint','same_public_owner','seed_uint64_hex')
    for unit in planned:
        if unit.get('kind') not in ('image','query','stage'):raise ValueError('Unknown planned unit kind')
        row=actual.get(unit['id']);value=None;q=None
        status=row.get('outcome','missing') if row else 'missing'
        if status=='completed':
            try:
                for key in metadata:
                    if key in unit and row.get(key)!=unit[key]:raise ValueError('Planned metadata differs: '+key)
                if unit['kind']=='query':value=decisions(unit['method'],row.get('decision'))
                if unit['kind']=='image' and unit['axis']=='clean' and unit['arm']=='C1':q=quality(row.get('quality_vs_source'))
            except (ValueError,KeyError,TypeError) as error:
                status='invalid_observation';errors[unit['id']]=str(error)
        ledger.append(dict(id=unit['id'],outcome=status,decision=value,quality=q))
        if unit['kind']=='query':
            key,cluster=cell_identity(unit)
            group=groups.setdefault(key,dict(units=[],values={},states=Counter(),same_owner=0))
            if cluster in group['values']:raise ValueError('Repeated cluster inside one binomial cell; do not inflate N')
            group['units'].append(cluster);group['values'][cluster]=value
            if value:group['states'][value['state']]+=1
            if unit.get('same_public_owner') is True:group['same_owner']+=1
        if unit['kind']=='image' and unit['axis']=='clean' and unit['arm']=='C1':
            group=quality_groups.setdefault(unit['method'],{})
            if unit['group_id'] in group:raise ValueError('Repeated clean source quality group')
            group[unit['group_id']]=q
    summaries=[]
    for key,group in sorted(groups.items()):
        method,axis,arm,role,*rest=key
        positive=(axis=='clean' and role=='marked-correct') or (axis=='T3' and arm=='C1' and role=='correct')
        values=group['values']
        endpoints={}
        for channel in ('semantic','instance','both'):
            obs={u:None if v is None else v[channel] for u,v in values.items()}
            valid=[v for v in obs.values() if v is not None];missing=len(obs)-len(valid)
            item=dict(planned=len(obs),valid=len(valid),missing=missing,supported=sum(valid),
              observed_valid=bounds(sum(valid),len(valid)),
              possible_full_denominator_rate=[sum(valid)/len(obs),(sum(valid)+missing)/len(obs)],
              meaning='Component support is descriptive, not independently a false-attribution verdict')
            same_owner_pair=axis in ('T4','T5') and key[-1]=='same-public-owner'
            if channel=='both' and same_owner_pair:
                item['meaning']='Same public owner: descriptive support, not false cross-owner attribution or an instance-origin test'
            if channel=='both' and not (axis=='T4' and role=='recipient') and not same_owner_pair:
                item['conservative']=cell(group['units'],obs,event_kind='positive_success' if positive else 'negative_error')
                if axis!='clean':
                    item['conservative'].pop('numerical_target');item['conservative'].pop('meets_numerical_target')
            endpoints[channel]=item
        summaries.append(dict(key=list(key),independent_unit='source_group' if axis in ('clean','T3') else 'disjoint_pair',
          endpoints=endpoints,
          states=dict(group['states']),same_public_owner_queries=group['same_owner'],
          caveat='Per-cell descriptive, repeated cells are dependent; no delivery/security/human verdict implied'))
    qualities={method:dict(planned=len(rows),observed=sum(v is not None for v in rows.values()),
      missing=sum(v is None for v in rows.values()),counts={c:sum(v is not None and v[c] for v in rows.values()) for c in ('psnr','ssim','lpips','joint')}) for method,rows in quality_groups.items()}
    if t5_selected_pairs is not None and (type(t5_selected_pairs) is not int or not 0<=t5_selected_pairs<=30):raise ValueError('Bounded selected pair count')
    return dict(schema=VERSION,planned_units=len(planned),observed_units=len(actual),outcomes=dict(Counter(r['outcome'] for r in ledger)),
      ledger=ledger,cells=summaries,clean_quality=qualities,invalid_observations=errors,
      t5=dict(requested_pairs=30,selected_pairs=t5_selected_pairs,sufficient_fixed_coverage=None if t5_selected_pairs is None else t5_selected_pairs==30),
      artifact_verification='REQUIRED_UPSTREAM; this function validates metadata and arithmetic only',
      human_visual_verdict=None,milestone_verdict=None,security_verdict=None)
