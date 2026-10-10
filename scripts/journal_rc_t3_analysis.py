"""Independent stdlib analysis of terminated F5-RC1 matched T3 development runs.

Full detector fields are inputs; probe summaries and stored endpoints are not.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from journal_read_conditioning_analysis import (
    IDS, ENDPOINTS, ALPHA, endpoints, verify_route,
)

ROOT = Path(__file__).resolve().parents[1]
OWNERS = tuple('qim-pilot-owner-' + o for o in ('alpha', 'beta', 'gamma', 'delta'))
STRENGTHS = (.1, .2)
SEEDS = (0, 1, 2)
ARMS = ('frozen_C1_enrichment', 'shared_C0', 'candidate_C1')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def rows(path):
    return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]


def identity(r):
    return int(r['source_id']), float(r['strength']), int(r['seed'])


def label(k):
    return f'{k[0]}|{k[1]}|{k[2]}'


def totals(items):
    return {e: sum(x[e] for x in items) for e in ENDPOINTS}


def retained(record):
    """Freeze sets from retained development metadata, not new outcomes."""
    old = rows(Path(record['frozen_run']) / 'rows.jsonl')
    lookup = {}
    for control in ('C0', 'C1'):
        selected = [r for r in old if r.get('dose') == 'diffusion'
                    and r.get('control') == control and r.get('strength') in STRENGTHS]
        keys = [identity(r) for r in selected]
        expected = {(sid, s, seed) for sid in IDS for s in STRENGTHS for seed in SEEDS}
        if len(keys) != 72 or set(keys) != expected:
            raise ValueError('Retained development grid is not the fixed unique 72 identities')
        lookup[control] = dict(zip(keys, selected))
    v5_record = load(record['v5_results'])
    v5 = {}
    for r in v5_record['rows']:
        if (r.get('axis') == 'T3' and r.get('control') == 'C1'
                and r.get('dose') == 'diffusion' and r.get('strength') in STRENGTHS
                and r.get('status') == 'metrics_complete'):
            call = next(d['result'] for d in r['detections']
                        if d['claimed_owner'] == ALPHA and d['binding_mode'] == 'combined')
            k = identity(r)
            if k in v5:
                raise ValueError('Duplicate retained v5 identity')
            v5[k] = bool(call['semantic']['found'] and call['semantic']['content_match'])
    sets = {}
    for s, n, successes in ((.1, 29, 27), (.2, 28, 18)):
        p = {k for k in lookup['C1'] if k[1] == s}
        f = {k for k in p if lookup['C1'][k]['outcome'] == 'completed'}
        i = f & set(v5)
        if len(f) != 35 or len(i) != n or sum(v5[k] for k in i) != successes:
            raise ValueError('Historical 35/29/28 and v5 27/18 comparator mismatch')
        if sum(r['outcome'] == 'completed' for k, r in lookup['C0'].items() if k[1] == s) != 33:
            raise ValueError('Retained C0 coverage differs from 33 per strength')
        if any(not (lookup['C1'][k]['calls'][ALPHA]['semantic_found'] and
                    lookup['C1'][k]['calls'][ALPHA]['semantic_content_match']) for k in f):
            raise ValueError('Historical frozen semantic success is not 35/35')
        sets[str(s)] = {'P': sorted(p), 'F': sorted(f), 'I': sorted(i)}
    declared = {s: {name: [list(k) for k in group] for name, group in x.items()} for s, x in sets.items()}
    if record['comparison_sets'] != declared:
        raise ValueError('Recorded comparison sets differ from independently reconstructed sets')
    return lookup, v5, sets


def inventory(data, expected):
    keys = [(r['arm'], identity(r)) for r in data]
    counts = Counter(keys)
    return dict(planned=len(expected), recorded=len(data), unique=len(counts),
                duplicates=[{'arm': a, 'identity': label(k), 'count': n} for (a, k), n in counts.items() if n > 1],
                missing=[{'arm': a, 'identity': label(k)} for a, k in sorted(expected-set(keys))],
                extra=[{'arm': a, 'identity': label(k)} for a, k in sorted(set(keys)-expected)],
                statuses=dict(Counter(r.get('status', 'missing_status') for r in data)),
                failed=[{'arm': r['arm'], 'identity': label(identity(r)), 'status': r.get('status')}
                        for r in data if r.get('status') not in ('ok', 'safety_blocked')],
                safety_blocked=[{'arm': r['arm'], 'identity': label(identity(r))}
                                for r in data if r.get('status') == 'safety_blocked'],
                actual_source_ids=sorted({int(r['source_id']) for r in data}), expected_source_ids=sorted(IDS))


def budget(record, run_path):
    if record['config']['candidate'] == 'D2':
        duration = float(record['duration_seconds'])
        if (record['outcome'] == 'running' or record.get('prior_active_seconds') != 0 or
                abs(float(record['shared_duration_seconds'])-duration) > 1e-6):
            raise ValueError('D2 must record only its fresh terminated T3 execution cost')
        writer = load(Path(record['screen_run'])/'run.json')
        utility = load(Path(writer['utility_run'])/'run.json')
        writer_seconds, utility_seconds = float(writer['duration_seconds']), float(utility['duration_seconds'])
        return dict(cap_seconds=1800, measured_seconds=duration, within_cap=duration <= 1800,
            chain=[dict(path=str(run_path), candidate='D2', duration_seconds=duration)],
            cached_stage_seconds=writer_seconds, cached_stage_cap_seconds=3300,
            cached_stage_within_cap=writer_seconds <= 3300 and utility_seconds <= 300,
            utility_seconds=utility_seconds, utility_cap_seconds=300,
            total_d2_seconds=utility_seconds+writer_seconds+duration,
            shared_evidence_prior_duration_seconds=record['shared_evidence_prior_duration_seconds'],
            accounting='Fresh D2 T3; writer and utility caps separate; inherited RC evidence is reused, not re-executed')
    seen, chain = set(), []
    current, path = record, run_path
    while True:
        resolved = str(path.resolve()).casefold()
        if resolved in seen:
            raise ValueError('Prior-run duration chain is cyclic')
        seen.add(resolved)
        if current['outcome'] == 'running' or current.get('data_split') != 'development':
            raise ValueError('Budget chain contains active or non-development run')
        duration = float(current['duration_seconds'])
        prior_duration = float(current.get('prior_active_seconds', 0))
        if abs(float(current['shared_duration_seconds']) - duration - prior_duration) > 1e-6:
            raise ValueError('Shared duration is not current duration plus prior once')
        chain.append(dict(path=str(path), candidate=current['config']['candidate'], duration_seconds=duration))
        if not current.get('prior_run'):
            if prior_duration != 0:
                raise ValueError('Initial run has nonzero prior duration')
            break
        path = Path(current['prior_run'])
        prior = load(path/'run.json')
        if abs(prior_duration-float(prior['shared_duration_seconds'])) > 1e-6:
            raise ValueError('Prior active time disagrees with preceding shared total')
        current = prior
    measured = sum(x['duration_seconds'] for x in chain)
    cached = sum(float(load(Path(record[k])/'run.json')['duration_seconds']) for k in ('screen_run', 'binding_run'))
    return dict(cap_seconds=5400, measured_seconds=measured, within_cap=measured <= 5400,
                chain=chain, cached_stage_seconds=cached, cached_stage_cap_seconds=1800,
                cached_stage_within_cap=cached <= 1800,
                accounting='Each preceding T3 run counted once; cached stage separate; later T4/T5/synthesis not yet included')


def describe(values):
    if not values:
        return dict(n=0, minimum=None, mean=None, maximum=None)
    return dict(n=len(values), minimum=min(values), mean=sum(values)/len(values), maximum=max(values))


def quality(group, completed, endpoint_lookup):
    output = {'planned': 36, 'completed': len(completed), 'missing_or_failed_or_blocked': 36-len(completed),
              'human_admissibility': 'missing; no human verdict inferred', 'distortion': {}, 'subsets': {}}
    for field in ('quality_input', 'quality_source'):
        output['distortion'][field] = {metric: describe([r[field][metric] for r in completed if metric in r.get(field, {})])
                                      for metric in ('psnr_db', 'ssim_rgb', 'lpips')}
        for limit in (.2, .3):
            selected = [r for r in completed if r.get(field, {}).get('lpips') is not None and r[field]['lpips'] <= limit]
            output['subsets'][f'{field}_lpips_le_{limit}'] = dict(
                planned=36, qualified=len(selected),
                excluded_completed=len(completed)-len(selected), unavailable=36-len(completed),
                successes=totals([endpoint_lookup[identity(r)]['rc'] for r in selected]),
                identities=[label(identity(r)) for r in selected],
                interpretation='descriptive proxy subset; all failures retained in planned denominator; not a quality gate')
    return output


def analyze(path):
    record = load(path/'run.json')
    if record['outcome'] == 'running':
        raise ValueError('T3 probe is running; partial outputs cannot be analyzed as final')
    if (record.get('schema') != 'journal-rc-t3-v1' or record.get('method') != 'F5-RC1'
            or record.get('data_split') != 'development' or record.get('usd') != 0
            or record['config']['candidate'] not in ('RC2', 'RC3', 'D2')
            or record['config']['owners'] != list(OWNERS) or record['seeds'] != list(SEEDS)):
        raise ValueError('Unexpected scientific provenance')
    data = rows(path/'rows.jsonl')
    old, v5, sets = retained(record)
    expected = {('frozen_C1_enrichment', k) for x in sets.values() for k in x['F']}
    expected |= {(a, k) for a in ('shared_C0', 'candidate_C1') for x in sets.values() for k in x['P']}
    inv = inventory(data, expected)
    full_inventory = not any(inv[k] for k in ('duplicates', 'missing', 'extra', 'failed'))
    lookup = {a: {} for a in ARMS}
    ep = {a: {} for a in ARMS}
    discrepancies, call_errors, thresholds = [], [], set()
    screen_rows = rows(Path(record['screen_run'])/'rows.jsonl')
    targets = {r['source_id']: r['payload'] for r in screen_rows if r.get('config') == record['config']['candidate']}
    for r in data:
        a, k = r['arm'], identity(r)
        if a not in lookup or (a, k) not in expected or k in lookup[a]:
            continue
        lookup[a][k] = r
        if r.get('payload') and r['payload'] != targets.get(k[0]):
            raise ValueError('q/h target metadata differs from fixed cached candidate targets')
        if r.get('status') != 'ok':
            continue
        if a != 'candidate_C1':
            source = old['C0' if a == 'shared_C0' else 'C1'][k]
            if r.get('image') != source['image']['path'] or r.get('retained_outcome') != source['outcome']:
                raise ValueError('Retained suspect metadata mismatch')
        try:
            for method, field in (('rc', 'calls'), ('native', 'native_calls')):
                if set(r[field]) != set(OWNERS):
                    raise ValueError('Missing/extra owner calls')
                for call in r[field].values():
                    if method == 'rc':
                        verify_route(call)
                    for tier in ('semantic', 'instance'):
                        thresholds.add((call[tier]['decoded_threshold'], call[tier]['recomputed_threshold']))
            if a != 'shared_C0':
                q, h = r['payload']['q'], r['payload']['h']
                ep[a][k] = {m: endpoints(r[field][ALPHA], q, h) for m, field in (('rc','calls'),('native','native_calls'))}
            if a == 'frozen_C1_enrichment':
                compact = old['C1'][k]['calls'][ALPHA]
                historical = bool(compact['semantic_found'] and compact['semantic_content_match'])
                if historical != ep[a][k]['native']['S']:
                    discrepancies.append(label(k))
        except (KeyError, TypeError, ValueError) as error:
            ep[a].pop(k, None)
            call_errors.append(dict(arm=a, identity=label(k), error=str(error)))
    frozen, candidate = ep['frozen_C1_enrichment'], ep['candidate_C1']
    strengths = {}
    for s in STRENGTHS:
        p, f, i = (sets[str(s)][name] for name in ('P', 'F', 'I'))
        good = [k for k in p if k in candidate]
        baseline = [k for k in f if k in frozen]
        retention = {}
        for e in ENDPOINTS:
            positive = [k for k in baseline if frozen[k]['native'][e]]
            lost = [k for k in positive if k not in candidate or not candidate[k]['rc'][e]]
            gained = [k for k in baseline if not frozen[k]['native'][e] and k in candidate and candidate[k]['rc'][e]]
            retention[e] = dict(frozen_positive=len(positive), retained=len(positive)-len(lost),
                                lost=[label(k) for k in lost], gained=[label(k) for k in gained])
        paired = [dict(identity=label(k), candidate_status=lookup['candidate_C1'].get(k, {}).get('status', 'missing'),
                       in_F=k in f, in_I=k in i, v5_S=v5.get(k),
                       frozen_native=frozen.get(k, {}).get('native'), frozen_RC=frozen.get(k, {}).get('rc'),
                       candidate_RC=candidate.get(k, {}).get('rc'), candidate_native=candidate.get(k, {}).get('native')) for k in p]
        isuccess = sum(k in candidate and candidate[k]['rc']['S'] for k in i)
        historical = isuccess == len(i) and isuccess > sum(v5[k] for k in i)
        exact = len(baseline) == len(f) and not any(retention[e]['lost'] for e in ('Q','J'))
        majorities = {}
        for arm, values, method in (('candidate_RC', candidate, 'rc'), ('candidate_native', candidate, 'native'), ('frozen_native', frozen, 'native')):
            majorities[arm] = {e: dict(successes=sum(sum((sid,s,seed) in values and values[(sid,s,seed)][method][e] for seed in SEEDS) >= 2 for sid in IDS), planned_sources=12)
                               for e in ('S','C','J')}
        group = [r for k,r in lookup['candidate_C1'].items() if k[1] == s]
        strengths[str(s)] = dict(planned=36, completed=len(good),
            statuses=dict(Counter(r['status'] for r in group)), missing=36-len(group),
            candidate_RC=totals([candidate[k]['rc'] for k in good]),
            candidate_native=totals([candidate[k]['native'] for k in good]),
            frozen_native=totals([frozen[k]['native'] for k in baseline]),
            frozen_RC=totals([frozen[k]['rc'] for k in baseline]),
            frozen_completed_planned=35, frozen_enriched_completed=len(baseline),
            candidate_on_F=totals([candidate[k]['rc'] for k in f if k in candidate]),
            v5_on_P=dict(successes=sum(v5[k] for k in p if k in v5),completed=sum(k in v5 for k in p),planned=36),
            v5_on_F=dict(successes=sum(v5[k] for k in f if k in v5),completed=sum(k in v5 for k in f),planned=35),
            I=dict(planned=len(i), candidate_S=isuccess, frozen_S=len(i), v5_S=sum(v5[k] for k in i),
                   failed_or_absent=[label(k) for k in i if k not in candidate]),
            retention=retention, paired_identities=paired, source_majority=majorities,
            historical_semantic_continuity_pass=historical, exact_q_continuity_pass=exact,
            quality=quality(group, [lookup['candidate_C1'][k] for k in good], candidate))
    negative = {}
    for method, field in (('rc','calls'), ('native','native_calls')):
        cells = {}
        for a, owners, planned in (('shared_C0',OWNERS,288), ('candidate_C1',OWNERS[1:],216)):
            observed, errors, error_ids = 0, 0, []
            for k,r in lookup[a].items():
                # Record every observed negative even if its row status says failure.
                for owner in owners:
                    call = r.get(field, {}).get(owner)
                    if call is None:
                        continue
                    observed += 1
                    if endpoints(call,None,None)['A']:
                        errors += 1
                        error_ids.append(dict(identity=label(k), owner=owner))
            cells[a] = dict(planned=planned, observed=observed, unavailable=planned-observed,
                            any_detections=errors, detected_identities=error_ids)
        negative[method] = dict(cells=cells, planned=504, observed=sum(c['observed'] for c in cells.values()),
                                any_detections=sum(c['any_detections'] for c in cells.values()))
    n = negative['rc']
    available_negative_complete = (n['cells']['shared_C0']['observed'] == 264 and
                                   n['cells']['candidate_C1']['observed'] == 3*len(candidate))
    blocks_match = all(lookup['shared_C0'].get(k, {}).get('status') ==
                       ('ok' if r['outcome'] == 'completed' else 'safety_blocked') for k,r in old['C0'].items())
    candidate_operational_complete = all(lookup['candidate_C1'].get(k, {}).get('status') in ('ok','safety_blocked')
                                        for x in sets.values() for k in x['P'])
    costs = budget(record, path)
    threshold_pass = thresholds == {(8.259326826136963,4.982033056390042)}
    passed = (full_inventory and not call_errors and not discrepancies and costs['within_cap']
              and costs['cached_stage_within_cap'] and threshold_pass and blocks_match
              and candidate_operational_complete and available_negative_complete and n['any_detections'] == 0
              and all(x['historical_semantic_continuity_pass'] and x['exact_q_continuity_pass'] for x in strengths.values()))
    return dict(schema='journal-rc-t3-analysis-v1',method='F5-RC1',candidate=record['config']['candidate'],
                input=dict(path=str(path.resolve()),commit=record['commit'],command=record['command'],outcome=record['outcome'],
                           frozen_run=record['frozen_run'],v5_results=record['v5_results']),
                inventory=inv, call_errors=call_errors, frozen_S_discrepancies=discrepancies,
                thresholds=dict(observed=[list(x) for x in sorted(thresholds)],unchanged=threshold_pass,
                                status='frozen exploratory values; routed system population FPR uncalibrated'),
                budget=costs,strengths=strengths,negatives=negative,
                coverage=dict(available_negative_panel_complete=available_negative_complete,
                              retained_C0_statuses_match=blocks_match,candidate_operational_complete=candidate_operational_complete,
                              planned_negative_panel_exhaustive=n['observed']==504,retained_C0_blocked_call_slots=24),
                measured_t3_continuity_pass=passed,
                reuse=dict(prior_run=record.get('prior_run'),shared_rows=sum('shared_origin' in r for r in data),
                           interpretation='Reused frozen enrichment and C0 are shared evidence, not independent replicates'),
                endpoint_definitions=dict(A='semantic.found OR instance.found',S='semantic.found AND content_match',
                    R='semantic.read',C='semantic.read AND content_match',Q='semantic.read AND exact original q',
                    J='Q AND content_match',U='S AND NOT read',H='instance.read AND exact operational h',D='Q AND H',F='both_match'),
                status=dict(evidence='exploratory reused development sources; seeds and decoder rules not independent samples',
                            T4='not yet run for candidate',T5='not yet run; inherited all-alpha attribution endpoint not identifiable',
                            new_six_pair_payload_origin='not yet run',human_admissibility='missing',
                            full_amendment='not granted by this T3 analysis',historical_M1_M2='unchanged'))


def report(data):
    lines = ['# F5-RC1 matched T3 development results','',
             f"Candidate {data['candidate']}; measured T3 continuity: **{data['measured_t3_continuity_pass']}**. This is a bounded development result, not a full amendment or historical lifecycle verdict.",'',
             'The analysis recomputes endpoints from full calls against original recorded q and frozen native-clean decoded operational h. Original h is unknown. Stored probe summaries/endpoints are not analysis inputs. Candidate-native calls are the frozen decoder on new candidate pixels; frozen-native enrichment is the old writer/attack baseline.','',
             '## Inventory and time','',
             f"Run: {data['input']['path']}; commit `{data['input']['commit']}`; outcome {data['input']['outcome']}.",
             f"Rows {data['inventory']['recorded']}/214; unique {data['inventory']['unique']}; missing {len(data['inventory']['missing'])}; duplicates {len(data['inventory']['duplicates'])}; extras {len(data['inventory']['extra'])}; failed {len(data['inventory']['failed'])}; blocked {len(data['inventory']['safety_blocked'])}. Actual source IDs: {data['inventory']['actual_source_ids']}.",
             f"T3 stage {data['budget']['measured_seconds']:.3f}/{data['budget']['cap_seconds']} s; prerequisite stage {data['budget']['cached_stage_seconds']:.3f}/{data['budget']['cached_stage_cap_seconds']} s. {data['budget']['accounting']}. T4/T5 are not established by this assessment.",
             f"Reused prior run: {data['reuse']['prior_run']}; explicitly shared rows: {data['reuse']['shared_rows']}. Controls are shared evidence, not independent n.",
             f"Unchanged threshold check: {data['thresholds']['unchanged']}; frozen S discrepancies: {data['frozen_S_discrepancies']}; call-field errors: {data['call_errors']}.",'',
             '## Fixed denominators and endpoints','',
             '| Strength | Completed / 36 | S | R | C | Q | J | U | H | D | Full F | Fixed I candidate / frozen / v5 | S continuity | Q/J continuity |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|']
    for s,x in data['strengths'].items():
        count=' | '.join(str(x['candidate_RC'][e]) for e in ('S','R','C','Q','J','U','H','D','F'))
        i=x['I']
        lines.append(f"| {s} | {x['completed']}/36 | {count} | {i['candidate_S']}/{i['planned']}; {i['frozen_S']}/{i['planned']}; {i['v5_S']}/{i['planned']} | {x['historical_semantic_continuity_pass']} | {x['exact_q_continuity_pass']} |")
    lines += ['', 'Every success above uses all 36 planned identities; the completed denominator is shown separately. Frozen F has 35 identities at each strength, fixed I has 29/28. Failed/blocked candidate identities never shrink I. Candidate blocks outside I and frozen Q/J-positive obligations permit only coverage-qualified measured continuity; operational failures or missing records cannot pass.','',
              '| Strength / endpoint | Frozen positive / 35 | Retained | Lost identities | Gained identities |',
              '|---|---:|---:|---|---|']
    for s,x in data['strengths'].items():
        for e in ('S','R','C','Q','J'):
            r=x['retention'][e]
            lost = ', '.join(r['lost']).replace('|', '\\|') or 'none'
            gained = ', '.join(r['gained']).replace('|', '\\|') or 'none'
            lines.append(f"| {s} / {e} | {r['frozen_positive']}/35 | {r['retained']} | {lost} | {gained} |")
    lines += ['', 'Full P/F and paired native/new counts, every endpoint, and 72 per-identity arrays are in the statistics JSON. Gains elsewhere never erase a lost frozen-positive identity. H/D/full acceptance are descriptive, with no invented fragile-h diffusion gate.','',
              '## Source-majority and quality','',
              'Source-majority means at least two successful seeds out of three, over the fixed twelve sources. Blocked/missing/failed seeds count as no success. These are descriptive development counts, not independent seed or sample inference.']
    for s,x in data['strengths'].items():
        for arm, counts in x['source_majority'].items():
            lines.append(f"- {s} {arm}: "+'; '.join(f"{e} {counts[e]['successes']}/12" for e in ('S','C','J'))+'.')
        lines.append(f"- {s} statuses: {x['statuses']}; missing {x['missing']}.")
        for field, summary in x['quality']['distortion'].items():
            lines.append(f"- {s} {field}: "+'; '.join(f"{metric} n={v['n']}, mean={v['mean']}, range={v['minimum']}–{v['maximum']}" for metric,v in summary.items())+'.')
        for subset,c in x['quality']['subsets'].items():
            lines.append(f"- {s} {subset}: qualified {c['qualified']}/36; S/C/J successes {c['successes']['S']}/{c['successes']['C']}/{c['successes']['J']} over 36 planned and {c['qualified']} qualified; unavailable {c['unavailable']}.")
    lines += ['', 'Distortion is measured against marked input and original source. LPIPS .20/.30 subsets are descriptive proxies; all attempts and failures remain in planned denominators. Human visual/semantic admissibility remains missing.','',
              '## Negatives and limits','']
    for method,x in data['negatives'].items():
        for cell,c in x['cells'].items():
            lines.append(f"- {method} {cell}: {c['any_detections']}/{c['observed']} observed any-channel detections; {c['planned']} planned; {c['unavailable']} unavailable.")
    lines += ['', 'C0 has 288 planned calls; six retained blocked rows leave 24 unavailable slots and 264 observable calls. C1 wrong-owner calls have 216 planned slots and three calls per available candidate row. No missing decision is synthesized as zero; zero observed calls do not establish zero/504 or population FPR.',
              'Four separate owner calls use roster_size=1. They reuse sources, attacks and sometimes pixels. The frozen numerical thresholds and legacy bound fields are not a routed-system FPR certificate.',
              'T4/T5 and the new six-pair candidate payload-origin arm are not yet run. The inherited all-alpha T5 geometry cannot identify false attribution between distinct legitimate owners. No complete amendment pass, fresh calibration, held-out confirmation or retroactive change to historical M1/M2 is claimed.','']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',required=True,type=Path)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'research/journal-upgrade-20261009')
    args=parser.parse_args()
    data=analyze(args.run)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'rc-t3-statistics.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    (args.output_dir/'rc-t3-results.md').write_text(report(data),encoding='utf-8')
    print(json.dumps(dict(candidate=data['candidate'],thresholds_unchanged=data['thresholds']['unchanged'],
                         measured_t3_continuity_pass=data['measured_t3_continuity_pass'],
                         strengths={s:dict(S=x['candidate_RC']['S'],Q=x['candidate_RC']['Q'],J=x['candidate_RC']['J'],
                                           I_S=x['I']['candidate_S'],Q_lost=len(x['retention']['Q']['lost']),J_lost=len(x['retention']['J']['lost']))
                                    for s,x in data['strengths'].items()},
                         negatives=data['negatives']['rc']['any_detections'],observed=data['negatives']['rc']['observed'])))


if __name__=='__main__':
    main()
