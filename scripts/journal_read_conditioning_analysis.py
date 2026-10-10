"""Independent stdlib descriptive analysis of cached F5-RC1 development probes.

Reads full detector fields; never imports a detector or trusts stored summaries.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ROOT = Path(__file__).resolve().parents[1]
IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
CONDITIONS = ('clean', 'sd15_vae', 'sdxl_vae')
CONFIGS = ('RC2', 'RC3')
MODES = ('combined', 'semantic_only', 'perceptual_only', 'none')
ARMS = ('donor_positive', 'recipient_sham', 'residual_0.5', 'residual_1.0',
        'public_donor_synthesis', 'public_recipient_authorization_demo')
ALPHA, BETA = 'qim-pilot-owner-alpha', 'qim-pilot-owner-beta'
ENDPOINTS = ('A', 'S', 'R', 'C', 'Q', 'J', 'U', 'H', 'D', 'F')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def hex_equal(a, b):
    return b is not None and int(a, 16) == int(b, 16)


def endpoints(call, q, h):
    s, i = call['semantic'], call['instance']
    Q = bool(s['read'] and hex_equal(s['decoded_code'], q))
    H = bool(i['read'] and hex_equal(i['decoded_code'], h))
    return dict(A=bool(s['found'] or i['found']),
                S=bool(s['found'] and s['content_match']), R=bool(s['read']),
                C=bool(s['read'] and s['content_match']), Q=Q,
                J=bool(Q and s['content_match']),
                U=bool(s['found'] and s['content_match'] and not s['read']),
                H=H, D=bool(Q and H), F=call['outcome'] == 'both_match')


def own_status(call, decision):
    i = call['instance']
    if not i['found']:
        return None
    distance = i['corrected_distance']
    return ('match' if distance <= decision['instance_radius'] else
            'mismatch' if distance >= decision['instance_mismatch_distance'] else 'uncertain')


def predicates(call, decision):
    s, i = call['semantic'], call['instance']
    own = own_status(call, decision)
    return dict(semantic_rejection=bool(s['found'] and s['content_status'] != 'match'),
                instance_own_content_status=own,
                instance_own_rejection=bool(i['found'] and own != 'match'),
                propagated_instance_rejection=bool(i['found'] and i['content_status'] != 'match'),
                combined_nonacceptance=call['outcome'] != 'both_match',
                semantic_disabled_read_presence=bool(s['found'] and s['read']),
                both_disabled_read_presence=bool(s['found'] and s['read'] and i['found'] and i['read']))


def verify_route(call):
    expected = call['semantic']['decoded_code'] if call['semantic']['read'] else call['semantic_code']
    route = 'decoded_semantic_read' if call['semantic']['read'] else 'suspect_semantic_recomputed'
    if not hex_equal(call['q_bound'], expected) or call['routing'] != route:
        raise ValueError('Read-conditioned route violates the single-route contract')
    if call.get('watermark_found') != bool(call['semantic']['found'] or call['instance']['found']):
        raise ValueError('Any-channel stored flag disagrees with full fields')


def compact(call, q, h, decision, routed=False):
    if routed:
        verify_route(call)
    return dict(endpoints=endpoints(call, q, h), outcome=call['outcome'],
                q_decoded=call['semantic']['decoded_code'], h_decoded=call['instance']['decoded_code'],
                q_bit_errors=None if q is None else (int(call['semantic']['decoded_code'],16)^int(q,16)).bit_count(),
                h_bit_errors=None if h is None else (int(call['instance']['decoded_code'],16)^int(h,16)).bit_count(),
                q_now=call['semantic_code'], h_now=call['perceptual_hash'],
                q_bound=call.get('q_bound'), routing=call.get('routing'),
                predicates=predicates(call, decision))


def totals(items):
    return {k: sum(x[k] for x in items) for k in ENDPOINTS}


def paired(items):
    return {k: dict(native=sum(x['native']['endpoints'][k] for x in items),
                    new=sum(x['new']['endpoints'][k] for x in items),
                    gained=sum(not x['native']['endpoints'][k] and x['new']['endpoints'][k] for x in items),
                    lost=sum(x['native']['endpoints'][k] and not x['new']['endpoints'][k] for x in items))
            for k in ENDPOINTS}


def inventory(rows, expected, key):
    actual = [key(r) for r in rows]
    return dict(planned=len(expected), recorded=len(rows), unique=len(set(actual)),
                missing=[list(k) for k in sorted(expected-set(actual), key=str)],
                extra=[list(k) for k in sorted(set(actual)-expected, key=str)],
                duplicates=len(actual)-len(set(actual)),
                failed=[list(key(r)) for r in rows if r.get('status') != 'ok'])


def complete(inv, record):
    return (record['outcome'] == 'completed' and not inv['missing'] and not inv['extra']
            and not inv['duplicates'] and not inv['failed'])


def screen_analysis(record):
    rows = record['rows']
    expected = {(c, sid) for c in CONFIGS for sid in IDS} | {('frozen_clean_compatibility', sid) for sid in IDS}
    inv = inventory(rows, expected, lambda r: (r.get('config', r.get('arm')), r['source_id']))
    decision = record['profile']['decision']
    result = dict(inventory=inv, complete=complete(inv, record), configurations={}, sources=[])
    for config in CONFIGS:
        entries = []
        for r in rows:
            if r.get('config') != config:
                continue
            entry = dict(config=config, source_id=r['source_id'], status=r['status'])
            if r['status'] != 'ok':
                result['sources'].append(entry)
                continue
            q, h = r['payload']['q'], r['payload']['h']
            entry.update(q_target=q, h_target=h, q_target_basis=r['payload']['q_target_basis'],
                         h_target_basis=r['payload']['h_target_basis'], conditions={})
            for condition in CONDITIONS:
                c = r['conditions'][condition]
                entry['conditions'][condition] = dict(
                    new=compact(c['calls'][ALPHA], q, h, decision, True),
                    native=compact(c['native_calls'][ALPHA], q, h, decision),
                    negatives={label: endpoints(call, None, None)['A'] for label, call in
                               (('c0', c['c0_call']), ('wrong_owner', c['calls'][BETA]))},
                    native_negatives={label: endpoints(call, None, None)['A'] for label, call in
                                      (('c0', c['native_c0_call']), ('wrong_owner', c['native_calls'][BETA]))},
                    quality_source=c['quality_source'], fixed_q_score=c['diagnostics']['fixed_q_score'])
                verify_route(c['c0_call'])
                verify_route(c['calls'][BETA])
            quality = entry['conditions']['clean']['quality_source']
            entry['strict_clean_quality'] = (quality['psnr_db'] > 35 and quality['ssim_rgb'] > .9 and quality['lpips'] < .1)
            entries.append(entry)
            result['sources'].append(entry)
        counts = {b: totals([e['conditions'][b]['new']['endpoints'] for e in entries]) for b in CONDITIONS}
        negatives = {k: sum(e['conditions'][b]['negatives'][k] for e in entries for b in CONDITIONS) for k in ('c0', 'wrong_owner')}
        strict = sum(e['strict_clean_quality'] and e['conditions']['clean']['new']['endpoints']['D']
                     and e['conditions']['clean']['new']['endpoints']['F'] for e in entries)
        stats = dict(planned_sources=12, completed=len(entries), missing_or_failed=12-len(entries),
                     strict_clean_quality=sum(e['strict_clean_quality'] for e in entries), strict_clean=strict,
                     endpoints=counts, paired={b: paired([e['conditions'][b] for e in entries]) for b in CONDITIONS},
                     negative_detections=negatives, observed_negative_calls=6*len(entries), planned_negative_calls=72,
                     native_negative_detections={k: sum(e['conditions'][b]['native_negatives'][k] for e in entries for b in CONDITIONS) for k in negatives},
                     minimum_fixed_q_score=min((e['conditions'][b]['fixed_q_score'] for e in entries for b in CONDITIONS[1:]), default=None),
                     mean_clean_lpips=sum(e['conditions']['clean']['quality_source']['lpips'] for e in entries)/len(entries) if entries else None)
        stats['cached_screen_eligible'] = (len(entries)==12 and strict==12 and counts['sd15_vae']['J']==12
                                           and counts['sdxl_vae']['J']>=11 and sum(negatives.values())==0)
        result['configurations'][config] = stats
    compat = []
    for r in rows:
        if r.get('arm') == 'frozen_clean_compatibility' and r['status'] == 'ok':
            q, h = r['payload']['q'], r['payload']['h']
            compat.append(dict(source_id=r['source_id'], q_target=q, h_target=h,
                               new=compact(r['calls']['combined'], q, h, decision, True),
                               native=compact(r['native_calls']['combined'], q, h, decision)))
    result['frozen_compatibility'] = dict(planned=12, completed=len(compat), paired=paired(compat), sources=compat,
                                        target_provenance='original recorded q; frozen native-clean decoded operational h; original h unknown')
    result['ranked_screen_survivors'] = sorted([c for c in CONFIGS if result['configurations'][c]['cached_screen_eligible']],
        key=lambda c: (-result['configurations'][c]['endpoints']['sdxl_vae']['J'],
                       -result['configurations'][c]['minimum_fixed_q_score'], result['configurations'][c]['mean_clean_lpips'], CONFIGS.index(c))) if result['complete'] else []
    return result


def subset_stats(rows, planned):
    keys = ('semantic_rejection', 'instance_own_rejection', 'propagated_instance_rejection',
            'combined_nonacceptance', 'semantic_disabled_read_presence', 'both_disabled_read_presence')
    output = dict(planned=planned, completed=len(rows), endpoints=totals([r['new']['endpoints'] for r in rows]),
                  predicates={k: sum(r['new']['predicates'][k] for r in rows) for k in keys})
    output['acceptance_fraction'] = output['endpoints']['F']/planned if planned else None
    output['fraction_status'] = 'defined' if planned else 'undefined: zero delivered denominator'
    output['combined_extra_rejections_over_semantic'] = sum(
        r['new']['predicates']['both_disabled_read_presence'] and not r['new']['predicates']['semantic_rejection']
        and r['new']['predicates']['combined_nonacceptance'] for r in rows)
    return output


def binding_analysis(record):
    rows, decision = record['rows'], record['profile']['decision']
    pairs = list(zip(sorted(IDS)[::2], sorted(IDS)[1::2]))
    expected = {(d, r, a) for d, r in pairs for a in ARMS[:-1]} | {(*pairs[0], ARMS[-1])}
    inv = inventory(rows, expected, lambda r: (r['donor_id'], r['recipient_id'], r['arm']))
    out = dict(inventory=inv, complete=complete(inv, record), rows=[], arms={})
    for r in rows:
        item = {k: r[k] for k in ('donor_id', 'recipient_id', 'arm', 'status')}
        if r['status'] != 'ok':
            out['rows'].append(item)
            continue
        q, h = r['intended_payload']['q'], r['intended_payload']['h']
        call = r['calls']['combined']
        item.update(q_target=q, h_target=h, payload_origin=r['payload_origin'],
                    new=compact(call, q, h, decision, True), native=compact(r['native_calls']['combined'], q, h, decision),
                    original=endpoints(r['original_calls']['combined'], q, h),
                    quality_recipient=r['quality_recipient'], mode_outcomes={}, native_mode_outcomes={})
        for mode in MODES:
            c = r['calls'][mode]
            verify_route(c)
            # Every binding mode must use the same extracted signals and one route.
            for field in ('q_bound', 'routing', 'semantic_code', 'perceptual_hash'):
                if c[field] != call[field]:
                    raise ValueError('Mode-dependent read-conditioned routing')
            for tier in ('semantic', 'instance'):
                for field in ('found', 'read', 'decoded_code', 'score', 'threshold', 'corrected_distance'):
                    if c[tier][field] != call[tier][field]:
                        raise ValueError('Mode-dependent extracted signal')
            item['mode_outcomes'][mode] = c['outcome']
            item['native_mode_outcomes'][mode] = r['native_calls'][mode]['outcome']
        out['rows'].append(item)
    good = [r for r in out['rows'] if r['status']=='ok']
    for arm in ARMS:
        group = [r for r in good if r['arm']==arm]
        planned = 1 if arm==ARMS[-1] else 6
        out['arms'][arm] = dict(planned=planned, completed=len(group), missing_or_failed=planned-len(group),
                               paired=paired(group), original_endpoints=totals([r['original'] for r in group]), subsets={
                                   'all': subset_stats(group, planned),
                                   'exact_Q': subset_stats([r for r in group if r['new']['endpoints']['Q']], sum(r['new']['endpoints']['Q'] for r in group)),
                                   'exact_D': subset_stats([r for r in group if r['new']['endpoints']['D']], sum(r['new']['endpoints']['D'] for r in group))},
                               mode_outcomes={mode: dict(Counter(r['mode_outcomes'][mode] for r in group)) for mode in MODES},
                               native_mode_outcomes={mode: dict(Counter(r['native_mode_outcomes'][mode] for r in group)) for mode in MODES})
    old_delivered = [r for r in good if r['arm']=='public_donor_synthesis' and r['original']['D']]
    old_rejected = [r for r in good if r['arm'] != ARMS[-1] and not r['original']['F']]
    retained = [r for r in old_delivered if r['new']['endpoints']['D'] and r['new']['predicates']['both_disabled_read_presence']]
    new_accepts = [r for r in old_rejected if r['new']['endpoints']['F']]
    out['compatibility'] = dict(original_exact_donor_deliveries=len(old_delivered), retained_exact_donor_deliveries=len(retained),
                               old_rejected_count=len(old_rejected), newly_accepted_old_rejected=len(new_accepts),
                               lost_delivery_pairs=[[r['donor_id'],r['recipient_id']] for r in old_delivered if r not in retained],
                               newly_accepted_identities=[[r['donor_id'],r['recipient_id'],r['arm']] for r in new_accepts],
                               pass_=out['complete'] and len(old_delivered)==5 and len(retained)==5 and not new_accepts)
    return out


def provenance(path, record):
    return dict(path=str(path.resolve()), commit=record['commit'], command=record['command'],
                outcome=record['outcome'], duration_seconds=record['duration_seconds'],
                data_split=record['data_split'], seeds=record['seeds'], usd=record['usd'],
                config=record['config'], row_count=len(record['rows']))


def report(data):
    s, b = data['screen'], data['binding']
    lines = ['# Cached F5-RC1 read-conditioning results', '',
             'Exploratory paired decoder intervention on reused development pixels. Full detector fields are independently reduced by the stdlib analysis script; stored endpoint summaries are not inputs.', '',
             '## Inventory and provenance', '']
    for kind in ('screen', 'binding'):
        p, inv = data['inputs'][kind], data[kind]['inventory']
        lines.append(f"- {kind}: {p['path']}; commit `{p['commit']}`; {p['outcome']}; {inv['recorded']}/{inv['planned']} unique planned rows, {len(inv['failed'])} failed, {len(inv['missing'])} missing, {inv['duplicates']} duplicates; {p['duration_seconds']:.3f} s; USD {p['usd']}.")
    lines += ['', f"Shared cached-stage duration: {data['budget']['measured_seconds']:.3f}/1800 s; within cap: {data['budget']['within_cap']}. Routing checks cover every new screen positive/negative/compatibility call and all binding modes. No alternate-code search is evaluated.", '',
              '## Screen', '', '| Configuration | Quality | Strict clean exact q/h + acceptance | Joint q clean / SD1.5 / SDXL | C0 / wrong-owner any detections | Min VAE fixed-q score | Mean clean LPIPS | Cached eligible |',
              '|---|---:|---:|---|---|---:|---:|---|']
    for c, x in s['configurations'].items():
        count = '/'.join(str(x['endpoints'][k]['J']) for k in CONDITIONS)
        lines.append(f"| {c} | {x['strict_clean_quality']}/12 | {x['strict_clean']}/12 | {count} of 12 | {x['negative_detections']['c0']}/36; {x['negative_detections']['wrong_owner']}/36 | {x['minimum_fixed_q_score']:.6f} | {x['mean_clean_lpips']:.6f} | {x['cached_screen_eligible']} |")
    lines += ['', 'Ranking uses SDXL J, minimum VAE fixed-q score, lower clean LPIPS, then RC2. Both configurations and binding must be complete before advancement.',
              f"Ranked screen survivors: {', '.join(s['ranked_screen_survivors']) or 'none'}. Cached advancement ready: {data['cached_advancement_ready']}. This is not a T3 or full T5 pass.", '',
              '| Configuration / condition | Native H → new H | Native D → new D | Native S → new S | Native F → new F |', '|---|---|---|---|---|']
    for c,x in s['configurations'].items():
        for condition in CONDITIONS:
            p=x['paired'][condition]
            lines.append('| '+c+' / '+condition+' | '+' | '.join(f"{p[k]['native']} → {p[k]['new']}" for k in ('H','D','S','F'))+' |')
    compat = s['frozen_compatibility']['paired']
    lines += ['', f"Frozen clean compatibility: full acceptance native/new {compat['F']['native']}/{compat['F']['new']} of 12; exact D native/new {compat['D']['native']}/{compat['D']['new']} of 12. The q target is original recorded intended q; h is the frozen clean-decoded operational target. Original embedded h is unknown; compatibility does not recover historical intent.", '',
              '## Cached binding compatibility', '', '| Arm | Completed / planned | Native Q / D / F | New Q / D / F | F among Q | F among D | Semantic / own-h rejection among D |', '|---|---|---|---|---|---|---|']
    for arm,x in b['arms'].items():
        p=x['paired']; subsets=x['subsets']
        def ratio(name):
            a=subsets[name]
            return f"{a['endpoints']['F']}/{a['planned']}" if a['planned'] else 'undefined (0 delivered)'
        d=subsets['exact_D']
        rej=f"{d['predicates']['semantic_rejection']}/{d['planned']}; {d['predicates']['instance_own_rejection']}/{d['planned']}" if d['planned'] else 'undefined'
        lines.append(f"| {arm} | {x['completed']}/{x['planned']} | "+'/'.join(str(p[k]['native']) for k in ('Q','D','F'))+' | '+ '/'.join(str(p[k]['new']) for k in ('Q','D','F'))+f" | {ratio('exact_Q')} | {ratio('exact_D')} | {rej} |")
    c=b['compatibility']
    lines += ['', f"The original five exact public-donor deliveries retained with same-signal disabled read controls: {c['retained_exact_donor_deliveries']}/{c['original_exact_donor_deliveries']}. Newly accepted previously rejected non-demo rows: {c['newly_accepted_old_rejected']}/{c['old_rejected_count']}. Cached binding continuity: {c['pass_']}.", '',
              'Own-h predicates are recomputed from corrected h distance before semantic-status propagation. Disabled controls reuse the combined extraction; binding modes are also verified to use identical routing and extracted signals. Mode outcome tables and all 31 row endpoints are retained in the compact statistics JSON. Missing/failed rows remain in planned denominators; zero delivered denominators yield undefined conditionals.', '',
              'The public-recipient row is a separate authorization counterexample. Donor target q/h remain the original cached decoded-donor targets, including any difference from intended q. They are not replaced by whichever payload decodes successfully.', '',
              '## Interpretation limits', '',
              'The samples are small, previously seen development sources and transformed/cached pixels. Paired changes describe these calls, not population FPR, generalization or a causal decomposition of total system performance. Legacy bound fields remain unvalidated for the routed system. Quality is reused from exact cached pixels with source-record links; no new optimization or model inference occurs in this analysis.', '',
              'VAE round trips are not diffusion regeneration. Matched T3, new candidate-origin donor synthesis and T4 continuity remain subsequent measurements. The inherited all-alpha T5 geometry panel has zero distinct-owner marked pairs and cannot certify literal T5 false-attribution continuity. Historical frozen M1a/M2 and original failed R1–R4 screens remain unchanged.', '']
    delivered=b['arms']['public_donor_synthesis']['subsets']['exact_D']
    lines.insert(lines.index('## Interpretation limits'),
                 f"Among the {delivered['planned']} exact donor deliveries, combined checking adds {delivered['combined_extra_rejections_over_semantic']} observed rejections beyond semantic checking alone. Own-h rejection also occurs on {delivered['predicates']['instance_own_rejection']}/{delivered['planned']}; this panel cannot establish a combined-predicate benefit.\n")
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screen-run', type=Path, default=MAIN/'.thesis-build/dev-runs/20261010-1035-rc-screen')
    parser.add_argument('--binding-run', type=Path, default=MAIN/'.thesis-build/dev-runs/20261010-1040-rc-binding')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'research/journal-upgrade-20261009')
    args=parser.parse_args()
    records={kind: load(path/'run.json') for kind,path in (('screen',args.screen_run),('binding',args.binding_run))}
    # Analysis is allowed only after both processes have terminated; failures are reportable.
    if any(r['outcome']=='running' for r in records.values()):
        raise ValueError('Both cached probes must finish before analysis/ranking')
    for kind,path in (('screen',args.screen_run),('binding',args.binding_run)):
        rows=[json.loads(line) for line in (path/'rows.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        if rows != records[kind]['rows']:
            raise ValueError('run.json and rows.jsonl inventory differs')
        r=records[kind]
        if r['method']!='F5-RC1' or r['data_split']!='development' or r['usd']!=0 or r['seeds']!=[]:
            raise ValueError('Unexpected method/split/cost/seed provenance')
        if len(r['commit'])!=40 or r['duration_seconds'] is None:
            raise ValueError('Missing commit/duration provenance')
    measured=sum(r['duration_seconds'] for r in records.values())
    if abs(records['binding']['prior_screen_seconds']-records['screen']['duration_seconds'])>1e-6:
        raise ValueError('Shared-stage duration accounting mismatch')
    data=dict(schema='journal-read-conditioning-analysis-v1',
              inputs={kind:provenance(path,records[kind]) for kind,path in (('screen',args.screen_run),('binding',args.binding_run))},
              budget=dict(cap_seconds=1800, measured_seconds=measured, within_cap=measured<=1800),
              screen=screen_analysis(records['screen']), binding=binding_analysis(records['binding']),
              endpoint_definitions=dict(A='semantic.found OR instance.found', S='found semantic content match', R='semantic read',
                                        C='semantic read and content match', Q='readable exact target q', J='Q and content match',
                                        U='S without semantic read', H='readable exact target h', D='Q and H', F='both_match'),
              status=dict(T3='not evaluated here', literal_T5='not identifiable in inherited all-alpha panel',
                          population_FPR='not calibrated', human_admissibility='missing'))
    data['cached_advancement_ready']=bool(data['screen']['complete'] and data['binding']['complete']
        and data['binding']['compatibility']['pass_'] and data['screen']['ranked_screen_survivors'] and measured<=1800)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'read-conditioning-statistics.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    (args.output_dir/'read-conditioning-results.md').write_text(report(data),encoding='utf-8')
    print(json.dumps(dict(ranked=data['screen']['ranked_screen_survivors'], cached_advancement_ready=data['cached_advancement_ready'], seconds=measured)))


if __name__=='__main__':
    main()
