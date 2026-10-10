"""Stdlib-only descriptive analysis of the finalized E3-A1 threat supplement."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
from journal_bch_analysis import endpoint

ROOT = Path(__file__).resolve().parents[1]
ALPHA = 'qim-pilot-owner-alpha'
OWNERS = tuple('qim-pilot-owner-'+x for x in ('alpha', 'beta', 'gamma', 'delta'))
METHODS = ('E3', 'F5', 'v5')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def ep(call, target=None):
    e = endpoint(call, target)
    e.update(D=bool(e['Q'] and e['H']) if target else None,
             semantic_presence=bool(call['semantic']['found']),
             both_presence=bool(call['semantic']['found'] and call['instance']['found']))
    return e


def conditional(panel, selection):
    chosen = [r for r in panel if r['e']['none'][selection]]
    f = sum(r['e']['combined']['F'] for r in chosen)
    return dict(denominator=len(chosen), false_full=f,
        false_full_rate=f/len(chosen) if chosen else None,
        rejection_rate=(len(chosen)-f)/len(chosen) if chosen else None,
        status='descriptive_selected_cases' if chosen else 'undefined_zero_delivery')


def analyze(folder):
    run = read(folder/'run.json')
    if run.get('outcome') not in ('completed', 'failed') or run.get('qualification') in ('pending','pending_finalization'):
        raise ValueError('Requires finalized completed/failed run.json')
    wall = read(folder/'parent-wall.json')
    if not isinstance(wall.get('duration_seconds'), (int, float)):
        raise ValueError('Requires finalized parent-wall.json duration_seconds')
    rows = [json.loads(line) for line in (folder/'rows.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    planned = run.get('planned_identities', [])
    counts = Counter(r['id'] for r in rows)
    done = {r['id'] for r in rows if r.get('status') == 'ok'}
    stats = dict(method='E3', strict_e3_b='FAILED_FINAL', m1a_pass=False,
        qualification='post_hoc_development_immediate_supplement_only',
        inventory=dict(planned_rows=len(planned), expected_rows=258, recorded_rows=len(rows),
            completed_rows=len(done), missing_identities=sorted(set(planned)-done),
            extra_identities=sorted(set(counts)-set(planned)),
            duplicate_identities=sorted(k for k,v in counts.items() if v > 1),
            failed_rows=[r for r in rows if r.get('status') != 'ok']),
        clean={}, T4={}, T5={}, issues=[])
    calls, provenance, attacks, clean = [], Counter(), [], []
    endpoint_disagreements = []
    for r in rows:
        actual = dict(r.get('calls', {}))
        if r.get('delivery_none'):
            actual['none/alpha'] = r['delivery_none']
        for key, call in actual.items():
            calls.append(dict(row_id=r['id'], key=key, method=r.get('method'),
                provenance=r.get('call_provenance', {}).get(key)))
            provenance[r.get('call_provenance', {}).get(key, {}).get('kind', 'missing')] += 1
        if r.get('status') != 'ok':
            continue
        if r.get('axis') == 'clean':
            r['e'] = {o:ep(c, r.get('payload') if o == ALPHA and r['control'] == 'C1' else None)
                      for o,c in r['calls'].items()}
            r['de'] = ep(r['delivery_none'], r.get('payload'))
            clean.append(r)
        elif r.get('axis') == 'T4':
            r['e'] = {mode:ep(c, r['payload']) for mode,c in r['calls'].items()}
            attacks.append(r)
        else:
            continue
        for key, saved_ep in r.get('endpoints', {}).items():
            for field in ('A', 'S', 'Q', 'H', 'F', 'D', 'semantic_presence', 'both_presence'):
                if field in saved_ep and saved_ep[field] != r['e'][key][field]:
                    endpoint_disagreements.append([r['id'], key, field])
    stats['call_inventory'] = dict(expected_actual_calls=600, actual_calls=len(calls),
        provenance_counts=dict(provenance), reused_calls=provenance['reused_full_call'],
        new_calls=sum(v for k,v in provenance.items() if k != 'reused_full_call'),
        coverage_by_method=dict(Counter(c['method'] for c in calls)),
        note='Unique recorded clean calls reused as donor/sham references are counted once; inherited full calls retained.',
        calls=calls)
    for method in METHODS:
        panel = [r for r in clean if r['method'] == method]
        c1, c0 = ([r for r in panel if r['control'] == arm] for arm in ('C1','C0'))
        stats['clean'][method] = dict(c1_rows=len(c1), c0_rows=len(c0),
            genuine_positive=sum(r['e'][ALPHA]['F'] for r in c1),
            clean_exact_q_h_both=sum(bool(r['e'][ALPHA]['Q'] and r['e'][ALPHA]['H'] and r['e'][ALPHA]['F']) for r in c1),
            wrong_owner_any=sum(r['e'][o]['A'] for r in c1 for o in OWNERS[1:]),
            c0_any=sum(r['e'][o]['A'] for r in c0 for o in OWNERS),
            calls=sum(len(r['calls'])+1 for r in panel),
            reused_calls=sum(p['kind']=='reused_full_call' for r in panel for p in r['call_provenance'].values()),
            planned=dict(genuine=12, wrong_owner=36, c0=48, none_delivery_controls=24))
    stage = read(Path(run['ancestry']['E3'])) if run.get('ancestry', {}).get('E3') else {}
    radius = stage.get('config', {}).get('profile', {}).get('decision', {}).get('instance_radius')
    if radius is None:
        stats['issues'].append('Instance radius unavailable: own-h predicate is unknown; no guessed threshold')
    residual_ok = True
    for scale in (.5, 1.):
        cell, sets = {}, {}
        for method in METHODS:
            panel = [r for r in attacks if r['method'] == method and r['scale'] == scale]
            sets[method] = {name:{r['attack_id'] for r in panel if r['e']['combined' if name=='F' else 'none'][name]}
                            for name in ('F','Q','H','D','semantic_presence','both_presence')}
            predicates = []
            for r in panel:
                c = r['calls']['combined']; i, s = c['instance'], c['semantic']
                own_match = bool(i['found'] and i['corrected_distance'] <= radius) if radius is not None else None
                predicates.append(dict(identity=r['attack_id'], delivered_D=r['e']['none']['D'],
                    combined_exact_D=r['e']['combined']['D'], presence=bool(i['found'] and s['found']),
                    own_h_match=own_match, semantic_match=bool(s['found'] and s['content_match']),
                    own_h_reject=None if own_match is None else bool(i['found'] and not own_match),
                    semantic_reject=bool(s['found'] and not s['content_match']),
                    semantic_absent=not s['found'], instance_absent=not i['found'],
                    full=r['e']['combined']['F']))
            delivered = [p for p in predicates if p['delivered_D']]
            cell[method] = dict(attempts=len(panel), false_full=len(sets[method]['F']),
                false_full_identities=sorted(sets[method]['F']),
                exact_Q=len(sets[method]['Q']), exact_H=len(sets[method]['H']), exact_D=len(sets[method]['D']),
                semantic_presence=len(sets[method]['semantic_presence']), both_presence=len(sets[method]['both_presence']),
                conditional_Q=conditional(panel, 'Q'), conditional_D=conditional(panel, 'D'),
                binding_rejection_given_exact_D=conditional(panel,'D')['rejection_rate'],
                conditional_binding_status='undefined_zero_delivery' if not delivered else 'descriptive_selected_delivered_cases',
                same_combined_call_predicates=dict(instance_radius=radius, delivered_rows=delivered,
                    own_h_rejections=sum(p['own_h_reject'] is True for p in delivered) if radius is not None else None,
                    semantic_rejections=sum(p['semantic_reject'] for p in delivered),
                    note='Own-h uses corrected distance before semantic propagation. Native none delivery selection is a separate call; v5 routing can differ.'))
        cell['new_false_full_vs_v5'] = sorted(sets['E3']['F']-sets['v5']['F'])
        cell['lost_false_full_vs_v5'] = sorted(sets['v5']['F']-sets['E3']['F'])
        cell['delivery_identity_changes'] = {e:{m:dict(lost=sorted(sets[m][e]-sets['E3'][e]),
            gained=sorted(sets['E3'][e]-sets[m][e])) for m in ('F5','v5')}
            for e in ('Q','H','D','semantic_presence','both_presence')}
        cell['false_full_changes'] = {m:dict(lost=sorted(sets[m]['F']-sets['E3']['F']),
            new=sorted(sets['E3']['F']-sets[m]['F'])) for m in ('F5','v5')}
        cell['continuity_pass'] = all(cell[m]['attempts']==20 for m in METHODS) and not cell['new_false_full_vs_v5'] and cell['E3']['false_full']<=cell['v5']['false_full']
        residual_ok &= cell['continuity_pass']; stats['T4'][str(scale)] = cell
    geometry = [r for r in rows if r.get('axis')=='T5_geometry' and r.get('status')=='ok']
    geometry_ok = len(geometry)==66
    for label in sorted({r['semantic_label'] for r in geometry}):
        panel = [r for r in geometry if r['semantic_label']==label]; cell = {}
        for key in ('E3_single_C0','E3_single_C1','E3_seven_C0','E3_seven_C1','F5_single_C0','F5_single_C1','v5_C0','v5_C1'):
            vals = [r['distances'][key] for r in panel]
            cell[key] = dict(pairs=len(vals), q_near=sum(d['semantic']<=6 for d in vals),
                h_near=sum(d['instance']<=6 for d in vals), joint_near=sum(d['semantic']<=6 and d['instance']<=6 for d in vals))
        for control in ('C0','C1'):
            near = lambda key:{r['pair_id'] for r in panel if r['distances'][key]['semantic']<=6 and r['distances'][key]['instance']<=6}
            a = near('E3_single_'+control)
            for comparator in ('v5','F5_single'):
                b = near(comparator+'_'+control)
                cell[comparator+'_changes_'+control] = dict(new_joint_identities=sorted(a-b), lost_joint_identities=sorted(b-a))
            b = near('v5_'+control)
            cell['historical_'+control] = dict(new_joint_identities=sorted(a-b), lost_joint_identities=sorted(b-a), continuity_pass=not(a-b) and len(a)<=len(b))
            geometry_ok &= cell['historical_'+control]['continuity_pass']
        stats['T5'][label] = cell
    stats['T5_interpretation'] = '66 component-geometry pairs; historical single-view and native seven-view differ. All marks alpha: zero genuine distinct-owner pairs, never an attribution denominator.'
    config = run.get('config', {})
    resources = {key:run.get(key) for key in ('duration_seconds','peak_allocated_bytes','peak_ram_bytes','extra_disk_bytes','budget_overrun')}
    resources.update(parent_inclusive_seconds=wall['duration_seconds'], parent_wall=wall,
        caps={k:config.get(k) for k in ('cap_seconds','gpu_cap_bytes','ram_cap_bytes','extra_disk_cap_bytes')})
    caps_ok = all(isinstance(v,(int,float)) and isinstance(cap,(int,float)) and 0<=v<=cap for v,cap in (
        (wall['duration_seconds'],config.get('cap_seconds')), (run.get('duration_seconds'),config.get('cap_seconds')),
        (run.get('peak_allocated_bytes'),config.get('gpu_cap_bytes')), (run.get('peak_ram_bytes'),config.get('ram_cap_bytes')),
        (run.get('extra_disk_bytes'),config.get('extra_disk_cap_bytes')))) and not run.get('budget_overrun')
    stats['resources'] = resources; stats['resources']['caps_pass'] = caps_ok
    c = stats['clean']['E3']
    stats['clean_control_pass'] = c['c1_rows']==c['c0_rows']==12 and c['clean_exact_q_h_both']==12 and not c['wrong_owner_any'] and not c['c0_any']
    stats['new_calls'] = stats['call_inventory']['new_calls']
    stats['immediate_continuity_pass'] = bool(residual_ok and geometry_ok and stats['clean_control_pass'] and done==set(planned)
        and len(planned)==258 and not stats['inventory']['duplicate_identities'] and not stats['inventory']['extra_identities']
        and len(calls)==600 and caps_ok and run['outcome']=='completed' and not endpoint_disagreements and not stats['issues'])
    saved = read(folder/'summary.json'); mismatches = []
    def compare(expected, observed, path):
        if isinstance(expected,dict) and isinstance(observed,dict):
            for k,v in expected.items():
                if k in observed: compare(v,observed[k],path+'/'+k)
        elif expected != observed: mismatches.append(path)
    for key in ('inventory','clean','T4','T5','new_calls','clean_control_pass','immediate_continuity_pass'):
        compare(saved.get(key),stats[key],key)
    stats['recorded_summary_agreement'] = dict(checked_fields='shared descriptive endpoints plus continuity (resource-inclusive)', mismatches=mismatches,
        run_summary_matches_file=run.get('summary')==saved, endpoint_disagreements=endpoint_disagreements)
    stats['provenance'] = dict(raw_commit=run.get('commit'), analysis_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        raw_records=[str(folder/name) for name in ('run.json','rows.jsonl','summary.json','parent-wall.json')], ancestry=run.get('ancestry'))
    stats['limitations'] = 'Exploratory fixed development sources; no population FPR, causal binding efficacy, full assessor contract or strict E3-B passage. E3/F5 use recorded operational h, whereas v5 uses original intended h: exact q/h counts are not a matched-target-basis ranking. Public projection, sham, same-topic transfer and genuine cross-owner attribution remain unmeasured here.'
    return stats


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True)
    args = p.parse_args(); stats = analyze(args.run_dir.resolve())
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'stats.json').write_text(json.dumps(stats,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines = ['# E3-A1 immediate supplement analysis','',f"Strict E3-B: FAILED_FINAL. M1a: false. Immediate continuity: {stats['immediate_continuity_pass']}.",'',
        f"Rows: {stats['inventory']['completed_rows']}/258. Actual recorded calls: {stats['call_inventory']['actual_calls']}/600; inherited: {stats['call_inventory']['reused_calls']}; new: {stats['new_calls']}.",'']
    for m,c in stats['clean'].items(): lines.append(f"Clean {m}: F {c['genuine_positive']}/12, exact q/h/F {c['clean_exact_q_h_both']}/12; wrong-owner any {c['wrong_owner_any']}/36; C0 any {c['c0_any']}/48.")
    for scale,cell in stats['T4'].items():
        for m in METHODS:
            c=cell[m]; lines.append(f"T4 scale {scale}, {m}: F/Q/H/D {c['false_full']}/{c['exact_Q']}/{c['exact_H']}/{c['exact_D']} of {c['attempts']}; conditional D rejection {c['binding_rejection_given_exact_D']}.")
    for label,cell in stats['T5'].items():
        lines.append(f"T5 geometry {label}: "+'; '.join(f"{k} q/h/joint {v['q_near']}/{v['h_near']}/{v['joint_near']} of {v['pairs']}" for k,v in cell.items() if 'pairs' in v))
    lines += ['',stats['T5_interpretation'], '',stats['limitations'],'',
        'Inclusive resource accounting: '+json.dumps(stats['resources']), '',
        'Recorded summary agreement: '+json.dumps(stats['recorded_summary_agreement']), '',
        'Provenance: '+json.dumps(stats['provenance'])]
    (args.output_dir/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
