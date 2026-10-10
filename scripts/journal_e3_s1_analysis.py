"""CPU-only analysis of final E3-S1 Stage A recorded calls (no inference).

Arm aliases and repeated C0 references describe one recorded observation.
This analysis never qualifies M1a or substitutes unavailable safety outputs.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path

from journal_bch_analysis import endpoint, CONDITIONS

IDS = (6012, 147498)
OWNERS = tuple('qim-pilot-owner-' + name for name in ('alpha', 'beta', 'gamma', 'delta'))
ALPHA, BETA = OWNERS[:2]
CAP, GPU_CAP, RAM_CAP = 1800., 10 * 1024**3, 16 * 1024**3


def read(path, default=None):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default


def rows_at(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines()
            if line.strip()] if path.exists() else []


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def quality(metrics):
    """Return missing/invalid explicitly; all three acceptance boundaries are strict."""
    m = metrics or {}
    infinite = m.get('psnr_infinite')
    valid = (isinstance(infinite, bool) and number(m.get('ssim_rgb')) and
             number(m.get('lpips')) and
             ((infinite and m.get('psnr_db') is None) or
              (infinite is False and number(m.get('psnr_db')))))
    return dict(metrics=metrics, valid=bool(valid), strict_pass=bool(valid and
        (infinite or m['psnr_db'] > 35) and m['ssim_rgb'] > .9 and m['lpips'] < .1))


def same_pair(a, b):
    return bool(a and b and all(a.get(k) is not None and b.get(k) is not None and
        int(a[k], 16) == int(b[k], 16) for k in ('q', 'h')))


def analyze(folder):
    folder = Path(folder).resolve()
    run = read(folder / 'run.json')
    if not run or run.get('outcome') not in ('completed', 'failed'):
        raise ValueError('Requires a final completed/failed run.json; never read running rows')
    if run.get('data_split') != 'development' or run.get('schema') != 'journal-e3-s1-stage-a-v1':
        raise ValueError('Requires the development E3-S1 Stage A schema')
    rows, t3rows, c0rows = (rows_at(folder / name) for name in
                           ('rows.jsonl', 't3-rows.jsonl', 'c0-rows.jsonl'))
    issues, discrepancies, observations, aliases, representations = [], [], [], [], []
    indexed = {}

    def check(label, derived, recorded):
        if derived != recorded:
            discrepancies.append(dict(field=label, recomputed=derived, recorded=recorded))

    def derive(call, payload=None, saved=None, label='call'):
        if not call:
            return None
        try:
            result = endpoint(call, payload)
        except (KeyError, TypeError, ValueError) as exc:
            issues.append(f'{label}: malformed full call: {exc}')
            return None
        if saved is not None:
            check(label + '.endpoints', result, saved)
        return result

    def observe(image, owner, call, payload, label, negative=False, saved=None):
        e = derive(call, payload, saved, label)
        if e is None:
            return None
        # Canonicalized saved-image identity and owner: no pseudo-replication.
        key = (str(Path(image).resolve()) if image else label, owner)
        if key in indexed:
            prior = observations[indexed[key]]
            check(label + '.reused_full_call', call, prior['call'])
            check(label + '.reused_endpoint', e, prior['endpoints'])
            check(label + '.reused_negative_role', negative, prior['negative'])
            aliases.append(dict(label=label, observation_index=indexed[key]))
        else:
            indexed[key] = len(observations)
            observations.append(dict(label=label, image=image, owner=owner, negative=negative,
                                     endpoints=e, call=call))
        return e

    completion = None
    previous_seconds = 0.
    previous_gpu, previous_ram = 0, 0
    if run.get('completion_of'):
        reference = run['completion_of']
        prior_path = Path(reference if isinstance(reference, str) else reference['run_dir']).resolve()
        if prior_path == folder:
            raise ValueError('Completion cannot refer to itself')
        prior_run = read(prior_path / 'run.json', {})
        if prior_run.get('completion_of'):
            raise ValueError('Only one bounded wrapper correction is supported')
        prior_analysis = analyze(prior_path)
        prior_t3 = rows_at(prior_path / 't3-rows.jsonl')
        prior_wall = read(prior_path / 'parent-wall.json', {})
        previous_seconds = prior_wall.get('parent_inclusive_seconds', prior_wall.get('duration_seconds'))
        previous_gpu, previous_ram = prior_run.get('peak_allocated_bytes'), prior_run.get('peak_ram_bytes')
        error = prior_run.get('error', '')
        whitelist_error = (error.rstrip().endswith('ValueError: unlisted regeneration strength') and
                           'models.regeneration_kwargs' in error and 'three_threat_models.py' in error)
        generated_files = [str(path) for path in prior_path.glob('*/S1-t3-*.png')]
        zero_generation = bool(not generated_files and len(prior_t3) == 1 and
            (prior_t3[0].get('source_id'), prior_t3[0].get('strength'), prior_t3[0].get('seed')) == (6012, .1, 0) and
            all(not r.get('image') and not r.get('calls') and not r.get('endpoints') and not r.get('timesteps') and
                r.get('status') in ('running', 'failed') for r in prior_t3))
        copied_rows = rows == rows_at(prior_path / 'rows.jsonl')
        copied_c0 = c0rows == rows_at(prior_path / 'c0-rows.jsonl')
        declared_seconds = run.get('prior_parent_inclusive_seconds',
            run.get('config', {}).get('prior_parent_inclusive_seconds'))
        check('completion.prior_parent_inclusive_seconds', previous_seconds, declared_seconds)
        check('completion.prior_error', error, run.get('prior_error'))
        valid = bool(prior_run.get('outcome') == 'failed' and whitelist_error and zero_generation and
            prior_analysis['summary_recomputed']['clean_vae_screen_pass'] and copied_rows and copied_c0 and
            not prior_analysis['issues'] and not prior_analysis['discrepancies'] and
            number(previous_seconds) and 0 <= previous_seconds < CAP and
            prior_analysis['resources']['child_cap_pass'] and prior_analysis['resources']['parent_cap_pass'])
        if not valid:
            issues.append('Completion lacks valid clean screen, copied records, zero-generation whitelist failure, or prior cap proof')
        completion = dict(completion_of=str(prior_path), valid=valid, original_error=error,
            original_commit=prior_run.get('commit'), original_outcome=prior_run.get('outcome'),
            original_summary_recomputed=prior_analysis['summary_recomputed'],
            original_representation_differences=prior_analysis.get('representation_differences'),
            original_parent_wall=prior_wall, prior_parent_inclusive_seconds=previous_seconds,
            original_t3_rows=prior_t3, zero_generation_proof=dict(pass_recomputed=zero_generation,
                generated_files=generated_files), copied_rows_exact=copied_rows, copied_c0_exact=copied_c0)

    if run.get('sources') != list(IDS):
        issues.append('Recorded source plan differs from fixed 6012,147498 inventory')
    inventory = Counter(r.get('source_id') for r in rows)
    if inventory != Counter(IDS):
        issues.append(f'Source inventory mismatch: {dict(inventory)}')
    c0 = {}
    for r in c0rows:
        key = (r.get('source_id'), r.get('condition'))
        if key in c0:
            issues.append(f'Duplicate C0 cell {key}')
        c0[key] = r
        observe(r.get('image'), ALPHA, r.get('call'), None, f'C0:{key}', True,
                r.get('endpoint'))
    c0plan = {(sid, cond) for sid in IDS for cond in CONDITIONS}
    missing_c0 = sorted(c0plan - set(c0))
    extra_c0 = sorted(set(c0) - c0plan, key=str)
    if missing_c0 or extra_c0:
        issues.append('C0 screen inventory incomplete or extra')
    sources, arm_passes, distinct_writers = [], [], set()
    changed_pairs = []
    for sid in IDS:
        matches = [r for r in rows if r.get('source_id') == sid]
        r = matches[0] if len(matches) == 1 else {}
        supplier = r.get('supplier', {})
        native = derive(supplier.get('native_call'), supplier.get('payload'), label=f'{sid}.supplier')
        intended_q = supplier.get('report', {}).get('semantic_code')
        native_h = supplier.get('native_call', {}).get('instance', {}).get('decoded_code')
        supplied = supplier.get('payload', {})
        supplier_route_ok = bool(supplier.get('status') == 'ok' and native and
            native['R'] and native['instance_read'] and intended_q is not None and native_h is not None and
            int(supplied.get('q', '-1'), 16) == int(intended_q, 16) and
            int(supplied.get('h', '-1'), 16) == int(native_h, 16))
        equal = same_pair(supplied, r.get('historical_payload')) if supplier.get('status') == 'ok' else None
        if equal is not None:
            check(f'{sid}.same_pair', equal, r.get('same_pair'))
        if equal is False:
            changed_pairs.append(sid)
        source = dict(source_id=sid, available=bool(r), source_image=r.get('source_image'),
            historical_payload=r.get('historical_payload'), same_pair_recomputed=equal,
            supplier=dict(record=supplier, native_endpoint=native, intended_q=intended_q,
                          native_h=native_h, route_pass=supplier_route_ok,
                          original_h_known=False), arms={})
        for name in ('historical', 'S1'):
            arm = r.get('arms', {}).get(name, {})
            writer, payload = arm.get('writer', {}), arm.get('payload')
            if writer.get('final_image'):
                distinct_writers.add(str(Path(writer['final_image']).resolve()))
            initial = writer.get('initial_qualification', {})
            final = writer.get('final_qualification', {})
            initial_e = derive(initial.get('call'), payload, label=f'{sid}.{name}.initializer')
            final_e = derive(final.get('call'), payload, label=f'{sid}.{name}.selected_final')
            initial_q, final_q = quality(initial.get('metrics')), quality(final.get('metrics'))
            admitted = bool(final_e and final_e['Q'] and final_e['H'] and final_e['F'] and final_q['strict_pass'])
            check(f'{sid}.{name}.writer.admitted', admitted, writer.get('admitted'))
            initial_valid = bool(initial_e and initial_e['Q'] and initial_e['H'] and initial_e['F'] and
                initial_q['strict_pass'] and writer.get('initial_balls', {}).get('feasible') is True)
            e1_quality = quality(writer.get('e1_final_quality'))
            branch = ('retain' if e1_quality['strict_pass'] else 'contract_0.8') if e1_quality['valid'] else None
            if branch is not None:
                check(f'{sid}.{name}.quality_branch', branch, writer.get('quality_branch'))
            trace = []
            if writer.get('final_image'):
                trace = rows_at(Path(writer['final_image']).parent.parent / 'iterations.jsonl')
            result = dict(available=bool(arm), payload=payload, reuse=arm.get('reuse'),
                writer_status=writer.get('status', 'missing'), writer_error=writer.get('error'),
                admitted_recomputed=admitted, initializer_valid_recomputed=initial_valid,
                initializer=dict(endpoints=initial_e, quality=initial_q, balls=writer.get('initial_balls')),
                selected_final=dict(endpoints=final_e, quality=final_q, balls=writer.get('selected_final_balls')),
                quality_branch=writer.get('quality_branch'), quality_branch_recomputed=branch,
                e1_final_quality=e1_quality,
                timings={k: writer.get(k) for k in ('construction_seconds', 'refinement_seconds',
                    'quality_qualification_seconds', 'duration_seconds')},
                update_status=writer.get('update_status'), accepted_updates=writer.get('accepted_updates'),
                completed_logical_iterations=writer.get('completed_logical_iterations'),
                trace=trace, conditions={})
            for cond in CONDITIONS:
                cell = arm.get('conditions', {}).get(cond, {})
                label = f'{sid}.{name}.{cond}'
                endpoints = {}
                for owner, call in cell.get('calls', {}).items():
                    endpoints[owner] = observe(cell.get('image'), owner, call,
                        payload if owner == ALPHA else None, label + '.' + owner, owner != ALPHA,
                        cell.get('endpoints', {}).get(owner))
                negative = c0.get((sid, cond), {})
                c0e = derive(negative.get('call'), label=label + '.C0')
                if cell:
                    check(label + '.c0_reference', negative.get('image'), cell.get('c0_call_reference'))
                    check(label + '.c0_endpoint', c0e, cell.get('c0_endpoint'))
                q = quality(cell.get('quality_source'))
                ep, wrong = endpoints.get(ALPHA), endpoints.get(BETA)
                passed = bool(ep and wrong and c0e and ep['S'] and ep['J'] and
                    not wrong['A'] and not c0e['A'] and
                    (cond != 'clean' or (ep['Q'] and ep['H'] and ep['F'] and q['strict_pass'])))
                result['conditions'][cond] = dict(available=bool(cell), endpoints=endpoints,
                    quality_source=q, quality_marked=cell.get('quality_marked'), c0_endpoint=c0e,
                    pass_recomputed=passed, missing_owners=[o for o in (ALPHA, BETA) if not endpoints.get(o)])
            result['pass_recomputed'] = bool(admitted and all(c['pass_recomputed']
                for c in result['conditions'].values()))
            arm_passes.append(result['pass_recomputed'])
            source['arms'][name] = result
        if equal is True:
            old, new = r.get('arms', {}).get('historical', {}), r.get('arms', {}).get('S1', {})
            if not new.get('reuse'):
                issues.append(f'{sid}: equal-pair arm lacks explicit reuse annotation')
            check(f'{sid}.same_pair_writer_reuse', old.get('writer'), new.get('writer'))
            check(f'{sid}.same_pair_conditions_reuse', old.get('conditions'), new.get('conditions'))
        for name, expected in (('historical', r.get('historical_payload')), ('S1', supplied)):
            if source['arms'][name]['available'] and not same_pair(source['arms'][name]['payload'], expected):
                issues.append(f'{sid}.{name}: arm target disagrees with frozen supplier target')
        sources.append(source)
    screen = bool(inventory == Counter(IDS) and len(arm_passes) == 4 and all(arm_passes) and
                  all(s['supplier']['route_pass'] for s in sources) and not missing_c0 and not extra_c0)

    # Read only the recorded development ancestor; no model or image access.
    ancestor_path = run.get('ancestry', {}).get('t3')
    oldrows = rows_at(Path(ancestor_path) / 'rows.jsonl') if ancestor_path else []
    old = {}
    for r in oldrows:
        if r.get('arm') == 'candidate_C1' and r.get('source_id') in IDS:
            key = (r['source_id'], float(r['strength']), r['seed'])
            if key in old:
                issues.append(f'Duplicate historical identity {key}')
            old[key] = r
    plan = {(sid, strength, seed) for sid in IDS for strength in (.1, .2) for seed in range(3)}
    identities = Counter((r.get('source_id'), float(r['strength']), r.get('seed')) for r in t3rows)
    missing = sorted(plan - set(identities))
    extra = sorted(set(identities) - plan, key=str)
    duplicates = [list(k) for k, n in identities.items() if n != 1]
    t3cells, lost, retention_missing = [], [], []
    counts = {str(s): dict(planned=6, observed=0, S=0, Q=0, J=0, wrong_A=0) for s in (.1, .2)}
    for key in sorted(plan):
        matches = [r for r in t3rows if (r.get('source_id'), float(r['strength']), r.get('seed')) == key]
        r = matches[0] if len(matches) == 1 else {}
        payload = next(s['arms']['S1']['payload'] for s in sources if s['source_id'] == key[0])
        if r and not same_pair(r.get('payload'), payload):
            issues.append(f'T3 {key}: target differs from frozen S1 arm')
        eps = {owner: observe(r.get('image'), owner, call, payload if owner == ALPHA else None,
            f'T3:{key}:{owner}', owner != ALPHA, r.get('endpoints', {}).get(owner))
            for owner, call in r.get('calls', {}).items()}
        positive = eps.get(ALPHA)
        c = counts[str(key[1])]
        if positive:
            c['observed'] += 1
            for name in ('S', 'Q', 'J'):
                c[name] += bool(positive[name])
        c['wrong_A'] += sum(bool(e and e['A']) for o, e in eps.items() if o != ALPHA)
        prior = old.get(key, {})
        prior_e = derive(prior.get('calls', {}).get(ALPHA), prior.get('payload'), label=f'Historical:T3:{key}')
        if not prior:
            retention_missing.append(list(key))
        if prior.get('status') == 'ok' and prior_e:
            for name in ('S', 'J'):
                if prior_e[name] and not (positive and positive[name]):
                    lost.append(dict(source_id=key[0], strength=key[1], seed=key[2], endpoint=name))
        t3cells.append(dict(identity=list(key), status=r.get('status', 'missing'),
            error=r.get('error'), image=r.get('image'), endpoints=eps,
            quality_marked=r.get('quality_marked'), timesteps=r.get('timesteps'),
            historical_status=prior.get('status', 'missing'), historical_endpoint=prior_e,
            missing_owners=[o for o in OWNERS if not eps.get(o)],
            timestep_count_pass=(len(r.get('timesteps', [])) == int(20 * key[1])) if r.get('status') == 'ok' else None))
    complete = bool(len(t3rows) == 12 and set(identities) == plan and not duplicates)
    calls_complete = all((cell['status'] == 'safety_blocked' and not cell['endpoints']) or
        (cell['status'] == 'ok' and not cell['missing_owners'] and cell['timestep_count_pass']) for cell in t3cells)
    t3pass = bool(complete and calls_complete and not lost and not retention_missing and
        all(counts[str(s)]['J'] >= n and not counts[str(s)]['wrong_A'] for s, n in ((.1, 6), (.2, 5))))
    summary = dict(clean_vae_screen_pass=screen, t3=counts, t3_complete=complete,
        lost_historical_positive_identities=lost, t3_screen_pass=t3pass,
        scientific_stage_a_pass=bool(screen and t3pass), m1a_pass=False,
        supplied_pair_changes=changed_pairs, distinct_writer_executions=len(distinct_writers))
    for name, value in summary.items():
        recorded = run.get('summary', {}).get(name)
        if not complete and name == 't3' and isinstance(recorded, dict):
            for strength, cell in value.items():
                saved = recorded.get(strength, {})
                for metric, count in cell.items():
                    if metric == 'planned' and count != saved.get(metric):
                        representations.append(dict(field=f'run.summary.t3.{strength}.planned',
                            fixed_plan=count, recorded_started_rows=saved.get(metric),
                            note='Original summary counts started cells; analyzer retains all six fixed slots.'))
                    else:
                        check(f'run.summary.t3.{strength}.{metric}', count, saved.get(metric))
        elif not complete and name == 'lost_historical_positive_identities':
            started_lost = [item for item in value if
                (item['source_id'], item['strength'], item['seed']) in identities]
            check('run.summary.' + name + '.started_slots', started_lost, recorded)
            if started_lost != value:
                representations.append(dict(field='run.summary.' + name,
                    fixed_plan_unretained=value, recorded_started_slots=recorded,
                    note='Unavailable unstarted slots are unretained; this is not an observed detector loss.'))
        else:
            check('run.summary.' + name, value, recorded)
    saved_summary = read(folder / 'summary.json')
    if saved_summary is not None:
        check('summary.json', run.get('summary'), saved_summary)
    wall = read(folder / 'parent-wall.json', {})
    duration = run.get('duration_seconds')
    inclusive = wall.get('parent_inclusive_seconds', wall.get('duration_seconds'))
    combined = inclusive + previous_seconds if number(inclusive) and number(previous_seconds) else None
    if completion:
        if wall.get('combined_parent_inclusive_seconds') is not None:
            check('parent_wall.combined_parent_inclusive_seconds', combined, wall['combined_parent_inclusive_seconds'])
        if wall.get('prior_parent_inclusive_seconds') is not None:
            check('parent_wall.prior_parent_inclusive_seconds', previous_seconds, wall['prior_parent_inclusive_seconds'])
        if run.get('combined_prior_parent_and_child_seconds') is not None and number(duration) and number(previous_seconds):
            check('run.combined_prior_parent_and_child_seconds', previous_seconds + duration,
                  run['combined_prior_parent_and_child_seconds'])
    gpu, ram = run.get('peak_allocated_bytes'), run.get('peak_ram_bytes')
    child_ok = bool(number(duration) and 0 <= duration <= CAP and not run.get('budget_overrun') and
        number(gpu) and 0 < gpu <= GPU_CAP and number(ram) and 0 < ram <= RAM_CAP)
    parent_ok = (bool(0 <= combined <= CAP and (not number(duration) or inclusive >= duration))
                 if number(combined) else None)
    if parent_ok is None:
        issues.append('Missing finalized parent-inclusive duration; cap cannot be established')
    if run.get('config', {}).get('cap_seconds') != CAP:
        issues.append('Recorded child cap differs from frozen 1800 seconds')
    stage_pass = bool(run['outcome'] == 'completed' and summary['scientific_stage_a_pass'] and
                      child_ok and parent_ok is True and not issues and not discrepancies)
    recorded_stage_formula = bool(run['outcome'] == 'completed' and number(duration) and
        duration <= CAP and run.get('summary', {}).get('scientific_stage_a_pass'))
    check('run.stage_a_pass.child_formula', recorded_stage_formula, run.get('stage_a_pass'))
    negatives = [o for o in observations if o['negative']]
    positives = [o['endpoints'] for o in observations if not o['negative']]
    screen_counts = {arm: dict(planned_sources=2,
        available_sources=sum(s['arms'][arm]['available'] for s in sources),
        strict_clean_quality=sum(s['arms'][arm]['conditions']['clean']['quality_source']['strict_pass'] for s in sources),
        clean_exact_q_h_both=sum(bool((s['arms'][arm]['conditions']['clean']['endpoints'].get(ALPHA) or {}).get('Q') and
            (s['arms'][arm]['conditions']['clean']['endpoints'].get(ALPHA) or {}).get('H') and
            (s['arms'][arm]['conditions']['clean']['endpoints'].get(ALPHA) or {}).get('F')) for s in sources),
        S_Q_J={cond: {name:sum(bool((s['arms'][arm]['conditions'][cond]['endpoints'].get(ALPHA) or {}).get(name))
            for s in sources) for name in ('S', 'Q', 'J')} for cond in CONDITIONS},
        note='Arm descriptions may reuse identical observations; do not add across arms.')
        for arm in ('historical', 'S1')}
    historical_retention = {str(strength): {name: dict(
        planned=6,
        historical_available=sum(c['historical_status'] == 'ok' and c['historical_endpoint'] is not None
            for c in t3cells if c['identity'][1] == strength),
        historical_positive=sum(bool(c['historical_status'] == 'ok' and c['historical_endpoint'] and
            c['historical_endpoint'][name]) for c in t3cells if c['identity'][1] == strength),
        lost=[item for item in lost if item['strength'] == strength and item['endpoint'] == name])
        for name in ('S', 'J')} for strength in (.1, .2)}
    unique_writer_records = {}
    for r in rows:
        for arm in r.get('arms', {}).values():
            w = arm.get('writer', {})
            # Partial failed writer records still contribute their recorded cost.
            key = w.get('final_image') or w.get('start_image') or json.dumps(w, sort_keys=True)
            if w:
                unique_writer_records[key] = w
    return dict(schema='journal-e3-s1-recorded-analysis-v1', run_dir=str(folder),
        commit=run.get('commit'), config=run.get('config'), command=run.get('command'),
        data_split=run.get('data_split'), usd=run.get('usd'), outcome=run.get('outcome'),
        error=run.get('error'), environment=run.get('environment'), ancestry=run.get('ancestry'), completion=completion,
        sources=sources, screen_counts=screen_counts, inventory=dict(planned=list(IDS), observed=dict(inventory),
            missing_c0=missing_c0, extra_c0=extra_c0), observations=observations, reuse_aliases=aliases,
        independent_observation_count=len(observations),
        negative_controls=dict(observed_unique=len(negatives), any_detections=sum(o['endpoints']['A'] for o in negatives),
            clean_vae_C0_planned=6, clean_vae_wrong_owner_planned_maximum=12,
            by_record_type={name:dict(observed=sum(o['label'].startswith(prefix) for o in negatives),
                any_detections=sum(o['endpoints']['A'] for o in negatives if o['label'].startswith(prefix)))
                for name, prefix in (('C0', 'C0:'), ('T3_wrong_owner', 'T3:'))},
            clean_vae_wrong_owner_observed=sum(not o['label'].startswith(('C0:', 'T3:')) for o in negatives),
            clean_vae_wrong_owner_detections=sum(o['endpoints']['A'] for o in negatives
                if not o['label'].startswith(('C0:', 'T3:'))),
            t3_wrong_owner_planned=36, t3_C0='not planned; external original assessment remains separate',
            note='Unique recorded calls only; shared sources and reused arms are not independent population samples.'),
        t3=dict(conditional_trigger_recomputed=screen, identities=t3cells, counts=counts,
            planned=12, missing=missing, extra=extra, duplicates=duplicates, complete=complete,
            full_calls_complete=calls_complete, lost_historical_positive_identities=lost,
            historical_retention=historical_retention,
            missing_historical_identities=retention_missing, pass_recomputed=t3pass,
            safety_unavailable=[c['identity'] for c in t3cells if c['status'] == 'safety_blocked']),
        error_histograms={name:dict(Counter(str(e[name]) for e in positives if e[name] is not None))
            for name in ('raw_coded_bit_errors', 'q_bit_errors', 'h_bit_errors')},
        missing_error_values={name:sum(e[name] is None for e in positives)
            for name in ('raw_coded_bit_errors', 'q_bit_errors', 'h_bit_errors')},
        summary_recomputed=summary, recorded_summary=run.get('summary'),
        resources=dict(child_seconds=duration, parent_inclusive_seconds=inclusive, parent_wall=wall,
            prior_parent_inclusive_seconds=previous_seconds, combined_parent_inclusive_seconds=combined,
            combined_peak_allocated_bytes=max(gpu, previous_gpu) if number(gpu) and number(previous_gpu) else None,
            combined_peak_ram_bytes=max(ram, previous_ram) if number(ram) and number(previous_ram) else None,
            startup_seconds=run.get('startup_seconds'), peak_allocated_bytes=gpu, peak_ram_bytes=ram,
            seconds_cap=CAP, gpu_cap_bytes=GPU_CAP, ram_cap_bytes=RAM_CAP,
            child_cap_pass=child_ok, parent_cap_pass=parent_ok),
        unique_writer_timing_totals={name:dict(
            recorded_sum_seconds=sum(w[name] for w in unique_writer_records.values() if number(w.get(name))),
            missing_records=sum(not number(w.get(name)) for w in unique_writer_records.values()))
            for name in ('construction_seconds', 'refinement_seconds', 'quality_qualification_seconds', 'duration_seconds')},
        stage_a_pass_recomputed=stage_pass, recorded_stage_a_pass=run.get('stage_a_pass'),
        m1a_pass=False, issues=issues, discrepancies=discrepancies, representation_differences=representations,
        interpretation='Exploratory two-source callable/supplier screen. Strict clean quality, exact-message '
            'assessment and content predicates remain distinct. Safety blocks and operational failures '
            'remain in fixed denominators. Historical operational h is not original embedded h. '
            'Training channel evaluation is not unseen-channel evidence. No M1a promotion, '
            'T4/T5 qualification, population FPR or held-out inference follows.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir', required=True, type=Path)
    p.add_argument('--output-dir', type=Path, help='New analysis directory; defaults to a sibling of run-dir')
    args = p.parse_args()
    folder = args.run_dir.resolve()
    out = args.output_dir.resolve() if args.output_dir else folder.with_name(folder.name + '-analysis')
    if out == folder or folder in out.parents:
        raise ValueError('Analysis output must be outside the retained run directory')
    result = analyze(folder)
    out.mkdir(parents=True, exist_ok=False)
    (out / 'analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
