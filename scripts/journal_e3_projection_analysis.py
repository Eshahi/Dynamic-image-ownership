"""Stdlib-only descriptive analysis of finalized E3-PP1 native public projection."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
from journal_bch_analysis import endpoint, strict_quality

ROOT = Path(__file__).resolve().parents[1]
METHODS = ('E3', 'v5')
MODES = ('combined', 'semantic_only', 'perceptual_only', 'none')
STRATA = {'T4_projection': 20, 'T4_sham': 20, 'T5_same': 7}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def ep(call, target):
    target = {k:v for k,v in (target or {}).items() if k in ('q','h') and v is not None}
    e = endpoint(call, target)
    for tier, key in (('semantic', 'q_bit_errors'), ('instance', 'h_bit_errors')):
        if not call[tier]['read']:
            e[key] = None
    e.update(D=bool(e['Q'] and e['H']) if target else None,
        semantic_presence=bool(call['semantic']['found']),
        fragile_presence=bool(call['instance']['found']),
        both_presence=bool(call['semantic']['found'] and call['instance']['found']))
    return e


def differences(saved, actual, path=''):
    """Check every saved endpoint leaf, including nested channel scalars."""
    if isinstance(saved, dict):
        result = []
        for k,v in saved.items():
            if k not in actual:
                result.append(path+'/'+k+'/missing')
            else:
                result.extend(differences(v, actual[k], path+'/'+k))
        return result
    return [] if saved == actual else [path]


def descriptive(values):
    known = [v for v in values if isinstance(v, (int,float)) and not isinstance(v,bool) and math.isfinite(v)]
    return dict(recorded=len(values), known=len(known), unknown=len(values)-len(known),
        minimum=min(known) if known else None, maximum=max(known) if known else None,
        mean=sum(known)/len(known) if known else None)


def conditional(panel, selection, sham):
    if sham:
        return dict(denominator=None, false_F=None, rejection_fraction=None,
            status='not_applicable_unmarked_sham')
    selected = [r for r in panel if r['e']['none'][selection] is True]
    f = sum(r['e']['combined']['F'] for r in selected)
    return dict(denominator=len(selected), false_F=f,
        rejection_fraction=(len(selected)-f)/len(selected) if selected else None,
        status='descriptive_selected_cases' if selected else 'undefined_zero_delivery')


def predicates(r, radius):
    c = r['calls']['combined']; s,i = c['semantic'],c['instance']
    own = c.get('instance_own_content_status')
    if own is not None:
        own_match = bool(i['found'] and own in ('match','unchecked'))
        # Both statuses have rank zero in the native content-state relation.
    elif radius is not None and isinstance(i.get('corrected_distance'), (int,float)):
        own_match = bool(i['found'] and i['corrected_distance'] <= radius)
    elif not i['found']:
        own_match = False
    else:
        own_match = None
    sm = bool(s['found'] and s['content_match']); both = bool(s['found'] and i['found'])
    return dict(identity=r['attack_id'], delivered_Q=r['e']['none']['Q'],
        delivered_D=r['e']['none']['D'], combined_exact_D=r['e']['combined']['D'],
        semantic_presence=bool(s['found']), fragile_presence=bool(i['found']),
        semantic_match=sm, own_instance_match=own_match,
        own_instance_status=own, corrected_instance_distance=i.get('corrected_distance'),
        own_instance_reject=bool(i['found'] and not own_match) if own_match is not None else None,
        semantic_reject=bool(s['found'] and not sm),
        ablations=dict(combined=bool(both and sm and own_match) if own_match is not None else None,
            semantic_only=bool(both and sm),
            perceptual_only=bool(both and own_match) if own_match is not None else None,
            none=both), recorded_combined_F=r['e']['combined']['F'])


def analyze(folder):
    run = read(folder/'run.json')
    if run.get('outcome') not in ('completed','failed') or run.get('qualification') in ('pending','pending_finalization'):
        raise ValueError('Requires finalized completed/failed run.json')
    wall = read(folder/'parent-wall.json')  # Required; never use a child-time fallback.
    if not isinstance(wall.get('duration_seconds'), (int,float)) or not math.isfinite(wall['duration_seconds']):
        raise ValueError('Requires finalized parent-wall.json duration_seconds')
    rows = [json.loads(s) for s in (folder/'rows.jsonl').read_text(encoding='utf-8-sig').splitlines() if s.strip()]
    planned = run.get('planned_identities', []); counts = Counter(r['id'] for r in rows)
    good = [r for r in rows if r.get('status')=='ok']
    done = {r['id'] for r in good}
    stats = dict(strict_e3_b='FAILED_FINAL', m1a_pass=False,
        qualification='exploratory_E3_PP1_post_hoc_supplement_only',
        inventory=dict(expected_rows=94, planned_rows=len(planned), recorded_rows=len(rows),
            completed_rows=len(done), missing_identities=sorted(set(planned)-done),
            failed_rows=[dict(id=r['id'],status=r.get('status'),error=r.get('error')) for r in rows if r.get('status')!='ok'],
            duplicate_identities=sorted(k for k,v in counts.items() if v>1),
            duplicate_planned_identities=sorted(k for k,v in Counter(planned).items() if v>1),
            extra_identities=sorted(set(counts)-set(planned))), strata={}, issues=[])
    stage = read(Path(run['e3_stage_a_dir'])/'run.json')
    radius = stage.get('config',{}).get('profile',{}).get('decision',{}).get('instance_radius')
    provenance = Counter(); coverage = Counter(); endpoint_disagreements=[]; bound_inventory={}
    for r in rows:
        for mode,c in r.get('calls',{}).items():
            provenance[r.get('call_provenance',{}).get(mode,{}).get('kind','missing')]+=1
            coverage[(r.get('method'),mode)]+=1
            if mode not in MODES:
                stats['issues'].append(f"Unexpected call mode {r['id']}/{mode}")
            for tier in ('semantic','instance'):
                channel=c[tier]
                key=f"{r.get('method')}/{tier}"
                b=bound_inventory.setdefault(key,dict(calls=0, finite_model_bounds=0, hypothetical_bounds=0, statuses=Counter()))
                b['calls']+=1
                b['finite_model_bounds']+=isinstance(channel.get('log10_false_positive_bound'),(int,float))
                b['hypothetical_bounds']+=isinstance(channel.get('hypothetical_log10_sign_bound'),(int,float))
                b['statuses'][channel.get('fpr_fields_status','missing')]+=1
        if r.get('status')!='ok':
            continue
        if set(r.get('calls',{}))!=set(MODES):
            stats['issues'].append(f"Incomplete four-mode call set: {r['id']}")
        r['e']={mode:ep(c,r.get('payload')) for mode,c in r['calls'].items()}
        endpoint_disagreements.extend(differences(r.get('endpoints',{}), r['e'], r['id']))
        if set(r.get('endpoints',{}))!=set(r['calls']):
            stats['issues'].append(f"Incomplete saved endpoint set: {r['id']}")
    stats['call_inventory']=dict(expected_calls=376, actual_calls=sum(provenance.values()),
        expected_reused_calls=188, reused_calls=provenance['reused_full_call'],
        new_calls=provenance['new_call'], provenance_counts=dict(provenance),
        coverage_by_method_mode={f'{m}/{b}':v for (m,b),v in coverage.items()})
    stats['bound_inventory']=bound_inventory
    for stratum,n in STRATA.items():
        cell={}; positive={}; sham=stratum=='T4_sham'
        for method in METHODS:
            panel=[r for r in good if r.get('method')==method and r.get('stratum')==stratum and set(r['e'])==set(MODES)]
            positive[method]={r['attack_id'] for r in panel if r['e']['combined']['F']}
            ps=[predicates(r,radius) for r in panel]
            if any(p['own_instance_match'] is None for p in ps):
                stats['issues'].append(f'Unknown own instance predicate: {stratum}/{method}')
            if any(p['ablations']['combined'] != p['recorded_combined_F'] for p in ps):
                stats['issues'].append(f'Combined predicate disagrees with native outcome: {stratum}/{method}')
            cell[method]=dict(planned=n, available=len(panel), unavailable=n-len(panel), false_F=len(positive[method]),
                false_F_per_available=len(positive[method])/len(panel) if panel else None,
                false_F_all_planned=len(positive[method])/n if len(panel)==n else None,
                all_planned_rate_status='descriptive_fixed_cases' if len(panel)==n else 'undefined_incomplete_coverage',
                false_F_identities=sorted(positive[method]),
                exact_delivery_status='not_applicable_unmarked_sham' if sham else 'fixed_evaluator_donor_targets',
                endpoint_counts={key:(None if sham and key in ('Q','H','D') else sum(r['e']['none'][key] is True for r in panel))
                    for key in ('Q','H','D','A','semantic_presence','fragile_presence','both_presence')},
                native_modes={mode:{key:(None if sham and key in ('Q','H','D') else sum(r['e'][mode][key] is True for r in panel))
                    for key in ('F','Q','H','D','A','S','semantic_presence','fragile_presence','both_presence')} for mode in MODES},
                conditional={key:conditional(panel,key,sham) for key in ('Q','D')},
                quality_all_attempts={key:descriptive([r['recipient_quality'].get(key) for r in panel]) for key in ('psnr_db','ssim_rgb','lpips')},
                strict_recipient_quality=sum(strict_quality(r['recipient_quality']) for r in panel),
                exploratory_proxy_subsets={str(limit):dict(available=sum(r['recipient_quality']['lpips']<=limit for r in panel),
                    false_F=sum(r['e']['combined']['F'] for r in panel if r['recipient_quality']['lpips']<=limit)) for limit in (.2,.3)},
                same_combined_call_predicates=dict(instance_radius=radius, rows=ps,
                    ablation_counts={mode:sum(p['ablations'][mode] is True for p in ps) for mode in MODES},
                    delivered_D_own_instance_rejections=None if sham else sum(p['delivered_D'] is True and p['own_instance_reject'] is True for p in ps),
                    delivered_D_semantic_rejections=None if sham else sum(p['delivered_D'] is True and p['semantic_reject'] for p in ps)),
                bit_errors={mode:{key:descriptive([r['e'][mode][key] for r in panel]) for key in ('q_bit_errors','h_bit_errors','raw_coded_bit_errors')} for mode in MODES},
                target_bases=[dict(identity=r['attack_id'],payload=r.get('payload'),donor_clean_decoded=r.get('donor_clean_decoded')) for r in panel],
                projection_errors=[dict(identity=r['attack_id'],**r.get('projection_errors',{})) for r in panel])
        cell['new_E3_false_F_vs_v5']=sorted(positive['E3']-positive['v5'])
        cell['lost_E3_false_F_vs_v5']=sorted(positive['v5']-positive['E3'])
        cell['continuity_pass']=all(cell[m]['available']==n for m in METHODS) and not cell['new_E3_false_F_vs_v5'] and cell['E3']['false_F']<=cell['v5']['false_F']
        stats['strata'][stratum]=cell
    unknown_strata={r.get('stratum') for r in good}-set(STRATA)
    if unknown_strata: stats['issues'].append(f'Unexpected successful strata: {unknown_strata}')
    cfg=run.get('config',{})
    pairs=((wall['duration_seconds'],cfg.get('cap_seconds')),(run.get('duration_seconds'),cfg.get('cap_seconds')),
        (run.get('peak_allocated_bytes'),cfg.get('gpu_cap_bytes')),(run.get('peak_ram_bytes'),cfg.get('ram_cap_bytes')))
    caps_ok=all(isinstance(v,(int,float)) and math.isfinite(v) and isinstance(cap,(int,float)) and 0<=v<=cap for v,cap in pairs) and not run.get('budget_overrun') and run.get('usd')==0
    stats['resources']=dict(parent_inclusive_seconds=wall['duration_seconds'],parent_wall=wall,
        child_inclusive_seconds=run.get('duration_seconds'),peak_allocated_bytes=run.get('peak_allocated_bytes'),
        peak_ram_bytes=run.get('peak_ram_bytes'),usd=run.get('usd'),budget_overrun=run.get('budget_overrun'),
        caps={k:cfg.get(k) for k in ('cap_seconds','gpu_cap_bytes','ram_cap_bytes')},caps_pass=caps_ok)
    inv=stats['inventory']; ci=stats['call_inventory']
    stats['projection_continuity_pass']=bool(run['outcome']=='completed' and len(planned)==94 and done==set(planned)
        and not any(inv[k] for k in ('failed_rows','duplicate_identities','duplicate_planned_identities','extra_identities'))
        and ci['actual_calls']==376 and ci['reused_calls']==ci['new_calls']==188 and not provenance['missing']
        and caps_ok and not endpoint_disagreements and not stats['issues'] and all(c['continuity_pass'] for c in stats['strata'].values()))
    saved=read(folder/'summary.json')
    shared={k:stats[k] for k in ('strict_e3_b','m1a_pass','strata','projection_continuity_pass')}
    # Compare shared saved fields only; independent resource-inclusive verdict is explicit.
    def shared_differences(a,b,p=''):
        if isinstance(a,dict) and isinstance(b,dict):
            return [x for k,v in a.items() if k in b for x in shared_differences(v,b[k],p+'/'+k)]
        return [] if a==b else [p]
    observed_differences=shared_differences(saved,shared)
    format_differences=[p for p in observed_differences if '/conditional/' in p and (p.endswith('/status') or '/T4_sham/' in p)]
    stats['recorded_summary_agreement']=dict(mismatches=[p for p in observed_differences if p not in format_differences],
        explicit_representation_differences=format_differences,
        run_summary_matches_file=run.get('summary')==saved,endpoint_disagreements=endpoint_disagreements)
    stats['provenance']=dict(raw_commit=run.get('commit'),analysis_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        raw_records=[str(folder/name) for name in ('run.json','rows.jsonl','summary.json','parent-wall.json')],ancestry=run.get('ancestry'))
    stats['limitations']='Fixed exploratory development cases only; no population FPR or calibrated bound. Native attack inverses and operating points differ. E3 q is original intended and h operational; v5 targets are historical original intended: no matched-target-basis ranking. None-mode delivery is separate from same-combined-call predicate ablations; v5 routing differences are not pure ablations. LPIPS subsets are exploratory proxies, without human admissibility. T5_same F measures suspect consistency; reference-specific same-owner attribution is unidentifiable in the source-blind API. Strict E3-B remains failed and M1a incomplete.'
    return stats


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args(); stats=analyze(args.run_dir.resolve())
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'stats.json').write_text(json.dumps(stats,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines=['# E3-PP1 public projection analysis','',f"Resource-inclusive continuity: {stats['projection_continuity_pass']}. Strict E3-B: FAILED_FINAL. M1a: incomplete.",'',
        f"Rows {stats['inventory']['completed_rows']}/94; calls {stats['call_inventory']['actual_calls']}/376; reused {stats['call_inventory']['reused_calls']}; new {stats['call_inventory']['new_calls']}.",'',
        '| Stratum | Method | Available/planned | F | Q | H | D | A | Semantic/fragile/both presence | Q/D conditional rejection |',
        '|---|---|---:|---:|---:|---:|---:|---:|---|---|']
    for stratum,cell in stats['strata'].items():
        for method in METHODS:
            c=cell[method]; e=c['endpoint_counts']; fmt=lambda x:'N/A' if x is None else str(x)
            lines.append(f"| {stratum} | {method} | {c['available']}/{c['planned']} | {c['false_F']} | "+' | '.join(fmt(e[k]) for k in ('Q','H','D','A'))+f" | {e['semantic_presence']}/{e['fragile_presence']}/{e['both_presence']} | "+'/'.join(fmt(c['conditional'][k]['rejection_fraction']) for k in ('Q','D'))+' |')
    for stratum,cell in stats['strata'].items():
        lines+=['',f"{stratum}: new E3 F identities {cell['new_E3_false_F_vs_v5']}; lost {cell['lost_E3_false_F_vs_v5']}."]
        for method in METHODS:
            c=cell[method]
            lines+=[f"{method}: all-attempt recipient quality {json.dumps(c['quality_all_attempts'])}; strict quality {c['strict_recipient_quality']}/{c['available']}; exploratory LPIPS subsets {json.dumps(c['exploratory_proxy_subsets'])}.",
                f"{method} native modes {json.dumps(c['native_modes'])}; same-combined-call predicate counts {json.dumps(c['same_combined_call_predicates']['ablation_counts'])}.",
                f"{method} bit errors {json.dumps(c['bit_errors'])}.",
                f"{method} projection errors: "+json.dumps({f'{phase}/{tier}/{metric}':descriptive([r.get(phase,{}).get(tier,{}).get(metric) for r in c['projection_errors'] if isinstance(r.get(phase),dict)]) for phase in ('before','after') for tier in ('semantic','fragile') for metric in ('absolute_rms','normalized_l2')})+'. Per-identity values remain in stats.json.']
    lines+=['',stats['limitations'],'','Bound-field counts (not population FPR): '+json.dumps(stats['bound_inventory']),
        '', 'Inventory: '+json.dumps(stats['inventory']), '', 'Resources: '+json.dumps(stats['resources']),
        '', 'Endpoint/summary agreement: '+json.dumps(stats['recorded_summary_agreement']),
        '', 'Issues: '+json.dumps(stats['issues']), '', 'Provenance: '+json.dumps(stats['provenance'])]
    (args.output_dir/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
