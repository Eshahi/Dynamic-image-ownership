"""Render committed registry experiment schemas into Markdown without recomputation.

This script reads numeric artifacts only. It does not run models, select a
threshold, change a verdict, or imply human visual approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
from statistics import median


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def fmt(value):
    if value is None:
        return 'missing'
    if isinstance(value, bool):
        return 'yes' if value else 'no'
    if isinstance(value, float):
        return f'{value:.6g}'
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return str(value).replace('|', '\\|').replace('\n', ' ')


def fraction(n, d):
    return f'{fmt(n)}/{fmt(d)}'


def table(headers, rows):
    rows = list(rows)
    if not rows:
        return 'Missing: no observations supplied.\n'
    return '\n'.join(['| ' + ' | '.join(map(fmt, headers)) + ' |',
                      '| ' + ' | '.join('---' for _ in headers) + ' |'] +
                     ['| ' + ' | '.join(map(fmt, row)) + ' |' for row in rows]) + '\n'


def link(path, label=None):
    path = Path(path).resolve()
    return f'[{label or path.name}](<{path.as_posix()}>)'


def availability(v):
    if not v:
        return 'missing'
    return f'{fraction(v.get("positives"), v.get("planned"))}; unresolved {fmt(v.get("unresolved"))}'


def latest_rows(path):
    result = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines(keepends=True):
            if not line.endswith('\n'):
                break
            row = json.loads(line)
            result[row['id']] = row
    return list(result.values())


def step1(run_dir):
    run, summary = read(run_dir / 'run.json'), read(run_dir / 'summary.json')
    choice = summary['method_choice']
    lines = ['# Unseen-regenerator development results', '',
        f'Run status: **{fmt(run.get("outcome"))}**. Frozen method choice: **{fmt(choice.get("choice"))}**. '
        f'SD2.1-base at strength .2 gives E3-S1 {fmt(choice.get("e3_success"))}/24 and F5 r2 {fmt(choice.get("f5_success"))}/24; '
        f'E3 minus F5 = {fmt(choice.get("difference"))} sources, against the fixed threshold of 3.', '',
        'This is exploratory evidence on 24 development sources. Clean quality is unmatched across methods. '
        'No held-out execution or human visual admissibility judgment is supplied. These are image-domain comparators, not a demonstrated proposal latent method.', '',
        fmt(choice.get('rule')), '', fmt(summary.get('missing_policy')), '', fmt(summary.get('interpretation')), '',
        '## Clean construction and quality', '',
        table(['Method','Observed','Strict quality','Minimum PSNR dB','Minimum SSIM','Median LPIPS','Maximum LPIPS','Median embedding s'],
              [(m, fraction(c.get('observed'),24), fraction(c.get('strict_quality'),24), c.get('psnr_min'), c.get('ssim_min'),
                c.get('lpips_median'),c.get('lpips_max'),c.get('embedding_seconds_median')) for m,c in summary['clean'].items()]),
        'Strict quality means PSNR >35 dB, SSIM >.9 and LPIPS <.1. Embedding times retain each source’s recorded construction basis; retained E3/F5 times are not fresh timing reruns.', '',
        '## Seed endpoints', '',
        'Entries are successes/planned calls followed by unavailable calls. Planned denominator is 72 per cell. '
        'Frozen predicates: S = semantic found and content match; C = semantic read and content match; '
        'Q = read q exactly equals the target; J = Q and semantic content match; H = read h exactly equals the target; '
        'F = both_match; A = either tier found.', '']
    rules = ('S','C','Q','J','H','F','A')
    seedrows, sourcerows, unknownrows, negatives = [], [], [], []
    for cell, methods in summary['cells'].items():
        for method, v in methods.items():
            seedrows.append([cell,method]+[availability(v.get('seeds',{}).get(r)) for r in rules])
            sourcerows.append([cell,method]+[fraction(v.get('source_majority',{}).get(r,{}).get('positives'),24) for r in rules])
            unknownrows.append([cell,method]+[availability(v.get('supplemental_source_majority_unknown_bounds',{}).get(r)) for r in rules])
            for panel in ('c0_A_clustered','wrong_owner_A_clustered'):
                c = v.get(panel,{})
                negatives.append([cell,method,panel,fraction(c.get('positives'),24),c.get('completely_evaluated_sources'),
                                  c.get('sources_with_unavailable_calls'),c.get('planned_rate_bounds'),
                                  c.get('conservative_upper_one_sided_95')])
    lines += [table(['Cell','Method']+list(rules),seedrows), '## Source-majority endpoints', '',
        'Success requires at least two observed True seeds; unavailable slots do not contribute successes. Every main endpoint uses all 24 sources.', '',
        table(['Cell','Method']+list(rules),sourcerows), '## Supplemental unavailable-seed bounds', '',
        'These tri-state summaries preserve unresolved seed majorities. They do not replace the fixed-denominator primary counts.', '',
        table(['Cell','Method']+list(rules),unknownrows), '## Paired checked-semantic C tests', '',
        table(['Cell and comparison','Left successes','Right successes','Left only','Right only','Difference pp','One-sided exact p','Holm p (18 tests)'],
            [(k,fraction(v.get('left_success'),24),fraction(v.get('right_success'),24),v.get('left_only'),v.get('right_only'),
              None if v.get('risk_difference') is None else 100*v['risk_difference'],v.get('exact_mcnemar_one_sided_p'),v.get('holm_p_18_tests'))
             for k,v in summary['comparisons'].items()]),
        'The test direction is left > right. A nonsignificant result does not establish equality or equivalence.', '',
        '## Transfer drop: SD1.5 minus SD2.1 source-majority C', '',
        table(['Strength and method','Sources','Rate','Supplemental unknown bounds'],
              [(k,v.get('count'),v.get('rate'),v.get('supplemental_unknown_count_bounds')) for k,v in summary['transfer_drop_source_majority_C'].items()]),
        '## Negative controls clustered by source', '',
        'A cluster is adverse if any observed A call accepts. Unavailable negatives remain unresolved; conservative bounds include them as potentially adverse.', '',
        table(['Cell','Method','Panel','Adverse sources','Complete sources','Unavailable sources','Rate bounds','Conservative 95% upper'],negatives),
        '## Safety policy, execution inventory and VAE comparison', '']
    row_counts = Counter((r.get('phase'),r.get('arm',r.get('method')),r.get('status')) for r in latest_rows(run_dir/'rows.jsonl'))
    lines += [table(['Phase','Arm or method','Latest status','Rows'],[(p,m,s,n) for (p,m,s),n in sorted(row_counts.items(),key=lambda x:str(x[0]))]),
        f'SD2.1 VAE comparison: `{fmt(run.get("sd21_vae_comparison"))}`.', '',
        f'Regenerator configuration and safety-checker presence: `{fmt(run.get("regenerators"))}`. '
        'SD1.5 retains its frozen safety checker; SD2.1 has none. Missing or blocked outputs are not silently rerun without safety checks.', '',
        'SDXL full generation was omitted prospectively in unseen-regenerator-protocol.md because safe fit was not established on the shared 12 GB desktop GPU. This is a conservative feasibility decision, not a measured out-of-memory result. The SDXL VAE control remains in step 2. '
        'No absent SDXL arm is represented as a measured result.', '',
        '## Limits and numeric evidence', '', fmt(summary.get('exact_H_note')), '',
        'The detector uses the claimed owner, public profile and pinned VAE/CLIP models, without an enrolled reference image in this step. '
        'The .2 transfer comparison is development evidence; it does not establish generalization to every regenerator. '
        'Source selection, safety policy and unmatched quality constrain interpretation.', '',
        'Numeric sources: '+', '.join(link(run_dir/n) for n in ('run.json','summary.json','rows.jsonl'))+'.', '',
        f'Commit: `{fmt(run.get("commit"))}`. Duration: {fmt(run.get("duration_seconds"))} seconds. '
        f'Incomplete primary choice executions: `{fmt(choice.get("incomplete_execution_ids"))}`.', '']
    return '\n'.join(lines)


def scenario_section(directory, heading='Regenerate-and-enroll scenario'):
    if directory is None or not (directory/'run.json').exists():
        return [f'## {heading}', '', 'Missing: scenario execution/results were not supplied. No watermark attribution advantage can be inferred.', '']
    run = read(directory/'run.json')
    lines = [f'## {heading}', '',
        f'Status: **{fmt(run.get("outcome"))}**. Registry size: {fmt(run.get("config",{}).get("registry_records"))} planned records. '
        'Alpha’s original publications are enrolled first; beta enrolls their seed-12 regenerated copies later, without embedding a new mark. '
        'Queries are the exact enrolled copy and its seed-13 further regeneration.', '']
    rows = []
    availability_rows = []
    for cell,s in run.get('summary',{}).items():
        for d,v in s.get('by_descriptor',{}).items():
            attribution = v.get('pointer_attribution',{})
            rows.append([cell,d,fraction(s.get('observed_sources'),s.get('planned_sources')),
                attribution.get('original_owner_unique',0),attribution.get('wrong_owner',0),
                attribution.get('ambiguous_owners',0),attribution.get('no_attribution',0),
                v.get('pointer_original_record'),v.get('fingerprint_original_record'),
                v.get('fingerprint_both_owners'),v.get('fingerprint_order_can_favor_alpha')])
            reference = v.get('reference_availability') or {}
            owners = reference.get('by_owner') or {}
            beta_reference = owners.get('beta',owners.get('qim-pilot-owner-beta')) or {}
            availability_rows.append([cell,d,v.get('query_observed'),v.get('query_abstaining'),v.get('query_unknown'),
                fraction(reference.get('searchable'),reference.get('planned')),
                fraction(beta_reference.get('searchable'),beta_reference.get('planned')),
                reference.get('abstaining'),reference.get('unknown'),
                beta_reference.get('abstaining'),beta_reference.get('unknown'),
                v.get('original_owner_unique_with_searchable_own_beta_record'),
                v.get('original_owner_unique_with_unsearchable_own_beta_record')])
    lines += [table(['Cell','Descriptor','Observed/planned','Pointer original owner','Wrong owner','Ambiguous','No attribution',
        'Pointer original record','Fingerprint original record','Fingerprint both owners','Order can favor alpha'],rows),
        'Original-owner uniqueness is distinct from selecting the original source record. Fingerprint matches to both owners '
        'are not unique owner attribution; preferring the earlier enrollment is an external registry-order rule. '
        'The native pointer is evaluated for alpha and beta here, so a zero wrong-owner rate in the alpha-only screen is not substituted for this scenario.', '',
        'Native calls, all matching record IDs, cosine scores and enrollment-order choices: '+link(directory/'rows.jsonl')+'. '
        'This scenario does not test re-embedding/T6 or arbitrary-owner security.', '']
    lines += [table(['Cell','Descriptor','Query observed','Query abstaining','Query unknown','Searchable/planned references',
        'Searchable/planned beta references','Reference abstentions','Reference unknown','Beta abstentions','Beta unknown',
        'Unique alpha with searchable own beta','Unique alpha with unsearchable own beta'],availability_rows),
        'A planned registry slot can lack a searchable descriptor. Unique alpha attribution with an unsearchable competing beta record '
        'is reported separately from uniqueness against a searchable competing record. Verified native weak-detail abstentions are '
        'deterministic rejections; genuine missing data remain unknown. Older runs without these availability fields display missing values, '
        'not measured zeros.', '']
    observations = latest_rows(directory/'rows.jsonl')
    statuses = Counter((r.get('phase'),r.get('status')) for r in observations)
    available = [r['registry_available_records'] for r in observations if 'registry_available_records' in r]
    lines += [table(['Phase','Status','Rows'],[(phase,status,n) for (phase,status),n in sorted(statuses.items(),key=lambda x:str(x[0]))]),
        f'Available descriptor-bearing records per observed query: minimum {fmt(min(available) if available else None)}, '
        f'maximum {fmt(max(available) if available else None)}; planned N is not silently substituted for availability.', '']
    return lines


def fresh_construction_section(directory):
    """Summarize existing fresh rows only; thresholds and detectors are untouched."""
    if directory is None or not (directory/'run.json').exists():
        return ['## Fresh construction and native-control availability', '',
                'Missing: fresh construction run directory was not supplied or its run artifact is absent.', '']
    run = read(directory/'run.json')
    config = run.get('config',{})
    method = config.get('chosen_method')
    sources = run.get('sources',config.get('sources',[]))
    rows = {r['id']:r for r in latest_rows(directory/'rows.jsonl')}
    alpha,beta = 'qim-pilot-owner-alpha','qim-pilot-owner-beta'
    quality_rows, control_rows = [], []
    for split in ('calibration','evaluation'):
        ids = [s['source_id'] for s in sources if s.get('registry_split',s.get('split')) == split]
        if not ids:
            continue
        clean = [rows.get(f'clean:{sid}:{method}:C1',{}) for sid in ids]
        ok = [r for r in clean if r.get('status') == 'ok']
        qualities = [r.get('quality',{}) for r in ok]
        def numbers(field):
            return [q[field] for q in qualities if isinstance(q.get(field),(int,float)) and not isinstance(q.get(field),bool)]
        psnr,ssim,lpips = numbers('psnr_db'),numbers('ssim_rgb'),numbers('lpips')
        times = [r['embedding_seconds'] for r in ok if isinstance(r.get('embedding_seconds'),(int,float))
                 and not isinstance(r.get('embedding_seconds'),bool)]
        statuses = dict(Counter(r.get('status','missing') for r in clean))
        quality_rows.append([split,method,fraction(len(ok),len(ids)),
            fraction(sum(r.get('strict_quality') is True for r in ok),len(ids)),
            sum(not isinstance(r.get('strict_quality'),bool) for r in clean),
            min(psnr) if psnr else None,sum(q.get('psnr_infinite') is True for q in qualities),
            min(ssim) if ssim else None,median(lpips) if lpips else None,max(lpips) if lpips else None,
            fraction(len(times),len(ids)),median(times) if times else None,max(times) if times else None,
            sum(times) if times else None,statuses])
        conditions = [('clean',None)] + [(model,strength) for model in ('sd15','sd21')
                     for strength in config.get('strengths',[.1,.2,.4])]
        for model,strength in conditions:
            seeds = [None] if model == 'clean' else config.get('seeds',[12,13,14])
            for panel,owner,arm in (('C0 native A',alpha,'C0'),('C1 wrong-owner native A',beta,method)):
                selected, cluster_values = [], []
                for sid in ids:
                    values = []
                    for seed in seeds:
                        identity = (f'clean:{sid}:{method}:{"C0" if arm == "C0" else "C1"}' if model == 'clean'
                                    else f'{model}:{sid}:{strength}:{seed}:{arm}')
                        row = rows.get(identity,{})
                        selected.append(row)
                        readout = row if model == 'clean' else row.get('readouts',{}).get(method,{})
                        endpoint = readout.get('endpoints',{}).get(owner,{}).get('A')
                        call = readout.get('calls',{}).get(owner)
                        values.append(endpoint if row.get('status') == 'ok' and call and isinstance(endpoint,bool) else None)
                    cluster_values.append(values)
                values = [v for cluster in cluster_values for v in cluster]
                complete = sum(all(v is not None for v in cluster) for cluster in cluster_values)
                adverse = sum(any(v is True for v in cluster) for cluster in cluster_values)
                unresolved_clusters = sum(not any(v is True for v in cluster) and any(v is None for v in cluster)
                                          for cluster in cluster_values)
                control_rows.append([split,model,strength,panel,fraction(sum(v is not None for v in values),len(values)),
                    sum(v is True for v in values),sum(v is None for v in values),fraction(adverse,len(ids)),
                    complete,unresolved_clusters,dict(Counter(r.get('status','missing') for r in selected))])
    return ['## Fresh construction and native-control availability', '',
        f'Fresh construction status: **{fmt(run.get("outcome"))}**; method: **{fmt(method)}**. '
        f'Phase status: `{fmt(run.get("phase_status"))}`. These summaries use the latest complete journal event per identity, '
        'including failed or unavailable identities in the planned denominators.', '',
        table(['Split','Method','Clean observed/planned','Strict quality/planned','Strict quality unknown','Minimum finite PSNR dB',
               'Infinite PSNR count','Minimum SSIM','Median LPIPS','Maximum LPIPS','Embedding time known/planned',
               'Median embedding s','Maximum embedding s','Sum known embedding s','Clean latest status'],quality_rows),
        'Strict quality uses the recorded PSNR >35 dB, SSIM >.9 and LPIPS <.1 predicate. '
        'Reported extrema and embedding-time summaries use available measurements only; missing constructions are not quality successes. '
        'Clean quality is not matched to another method in this fresh chosen-method-only run. '
        'For F5, embedding_seconds is the recorded native bootstrap time; for E3 it includes the recorded supplier and writer durations. '
        'Model loading and detector/quality assessment time are included in run duration, not silently attributed to embedding.', '',
        table(['Split','Condition','Strength','Control','Known/planned calls','Observed A accepts','Unknown calls',
               'Sources with observed A','Complete sources','Unresolved source clusters','Latest row status'],control_rows),
        'These are native detector A controls (either watermark tier found), separate from registry acceptance. '
        'A recorded call and Boolean A endpoint are both required for call availability. Safety-blocked, failed, not-yet-run '
        'and otherwise absent calls stay unknown. An unresolved source cluster has no observed A acceptance and at least one unknown call. '
        'No unavailable negative call is counted as an observed rejection. These inventories are not population false-positive estimates.', '',
        f'Fresh construction evidence: {link(directory/"run.json")}, {link(directory/"rows.jsonl")}. '
        f'Commit `{fmt(run.get("commit"))}`; duration {fmt(run.get("duration_seconds"))} seconds; '
        f'accounted step-2 duration {fmt(run.get("step2_accounted_seconds"))} seconds. Human visual admissibility remains missing.', '']


def calibration_threshold_driver_section(directory):
    """Describe stored calibration negatives; never fit or substitute a threshold."""
    rows, sources = [], []
    for path in sorted(directory.glob('calibration-D*-scores.json')):
        negatives = read(path).get('negatives',[])
        finite = [r for r in negatives if isinstance(r.get('score'),(int,float))
                  and not isinstance(r['score'],bool) and math.isfinite(r['score'])]
        without_near = [r for r in finite if r.get('family') != 'real_near_duplicate']
        maximum = max(finite,key=lambda r:r['score']) if finite else {}
        other = max(without_near,key=lambda r:r['score']) if without_near else {}
        delta = maximum['score']-other['score'] if maximum and other else None
        rows.append([path.name.removeprefix('calibration-').removesuffix('-scores.json'),
            maximum.get('id'),maximum.get('family'),maximum.get('score'),
            sum(r['score'] == maximum['score'] for r in finite) if maximum else None,
            other.get('id'),other.get('family'),other.get('score'),delta])
        sources.append(link(path))
    return ['### Calibration threshold drivers (descriptive)', '',
        table(['Descriptor','Maximum negative ID','Family','Maximum finite score','Rows tied at maximum',
               'Maximum ID excluding real near-duplicates','Family excluding real near-duplicates',
               'Maximum score excluding real near-duplicates','Maximum minus excluded-family maximum'],rows),
        'The difference describes how far the real-near-duplicate family raises the maximum finite calibration negative. '
        'If several rows tie, the displayed ID is the first stored row; the tie count includes every row at that maximum. '
        'Absent finite scores display missing. This is a descriptive family-exclusion comparison, not an alternative threshold, '
        'gate, descriptor rescue or evaluation-based selection. The frozen threshold remains nextafter above the maximum '
        'finite calibration negative across all families.', '',
        'Calibration score evidence: '+(', '.join(sources) if sources else 'missing')+'.', '']


def fresh_primary_evaluation_lead(fresh):
    """Lead with the saved fresh primary result when an evaluation is present."""
    evaluation = fresh.get('evaluation')
    if not isinstance(evaluation,dict):
        return []
    config = fresh.get('config',{})
    descriptor = evaluation.get('selected_descriptor',config.get('selected_descriptor'))
    primary = evaluation.get('primary') or evaluation.get('descriptors',{}).get(descriptor,{})
    cells = primary.get('cells',{})
    sd15,sd21 = cells.get('sd15/0.2',{}),cells.get('sd21/0.2',{})
    lines = ['**Fresh primary evaluation (amended development evidence):** '
        f'saved `development_pass` = **{fmt(primary.get("development_pass"))}**; '
        f'completeness = **{fmt(primary.get("complete"))}**; descriptor = **{fmt(descriptor)}**. '
        f'SD1.5/.2 source-majority F_R = **{fraction(sd15.get("source_majority_F_R"),sd15.get("source_denominator"))}**; '
        f'SD2.1/.2 = **{fraction(sd21.get("source_majority_F_R"),sd21.get("source_denominator"))}**; '
        f'observed false accepts = **{fmt(primary.get("observed_false_accepts"))}**. '
        f'Frozen method **{fmt(config.get("chosen_method"))}** remains unchanged, with no descriptor rescue. '
        'This result takes precedence over the earlier screen pass. It uses the post-hoc calibration, pre-evaluation '
        f'availability amendment `{fmt(config.get("availability_amendment"))}` and frozen calibration thresholds; '
        'it is development evidence, not held-out confirmation. Expected safety-blocked negatives remain unresolved.', '']
    frontier = []
    for model in ('sd15','sd21'):
        for strength in (.1,.2,.4):
            cell = f'{model}/{strength}'
            c = cells.get(cell,{})
            frontier.append([cell,fraction(c.get('seed_F_R'),c.get('planned_seeds')),
                fraction(c.get('source_majority_F_R'),c.get('source_denominator')),
                fraction(c.get('seed_fingerprint_correct'),c.get('planned_seeds')),
                fraction(c.get('source_majority_fingerprint'),c.get('source_denominator'))])
    near = primary.get('negative_families',{}).get('real_near_duplicate',{})
    deficits = [max(0,36-c['source_majority_F_R']) if isinstance(c.get('source_majority_F_R'),int) else None
                for c in (sd15,sd21)]
    lines += [table(['Primary cell','F_R seeds','F_R source majority','Fingerprint seeds','Fingerprint source majority'],frontier),
        f'At .2, the deficits to the fixed 36/40 criterion are {fmt(deficits[0])} sources for SD1.5 and '
        f'{fmt(deficits[1])} for SD2.1. Real near-duplicate fingerprint false accepts: '
        f'{fraction(near.get("fingerprint_false_accepts"),near.get("planned"))}; pointer-plus-registry false accepts: '
        f'{fraction(near.get("registry_false_accepts"),near.get("planned"))}. '
        f'This panel has {fmt(near.get("observed"))} finite cosines, '
        f'{fmt(near.get("verified_native_weak_detail_abstentions"))} verified native abstentions and '
        f'{fmt(near.get("unknown"))} unknown comparisons. These observed controls do not establish a population false-positive rate.', '']
    return lines


def fresh_descriptor_tpr(observations, cell, tau, planned_seeds, source_denominator):
    """Read-only own-record cosine TPR, independent of pointer/identification."""
    missing = {'seed':None,'majority':None,'seed_rate':None,'majority_rate':None}
    if observations is None or not isinstance(tau,(int,float)) or not math.isfinite(tau):
        return missing
    ids = sorted({o['source_id'] for o in observations})
    # Stored score vectors follow the split's sorted source IDs. Do not infer
    # an index from an incomplete source inventory.
    if len(ids) != source_denominator or not planned_seeds or not source_denominator:
        return missing
    index = {sid:i for i,sid in enumerate(ids)}
    successes = {sid:set() for sid in ids}
    for o in observations:
        if o.get('control') != 'C1' or f'{o.get("phase")}/{o.get("strength")}' != cell:
            continue
        scores = o.get('scores') or []
        if len(scores) != len(ids):
            continue
        score = scores[index[o['source_id']]]
        if isinstance(score,(int,float)) and not isinstance(score,bool) and math.isfinite(score) and score >= tau:
            successes[o['source_id']].add(o.get('seed'))
    seed = sum(len(v) for v in successes.values())
    majority = sum(len(v) >= 2 for v in successes.values())
    return dict(seed=seed,majority=majority,seed_rate=seed/planned_seeds,majority_rate=majority/source_denominator)


def execution_accounting_section(screen_dir, scenario_dir, fresh_dir, analysis_dir, scenario_fresh_dir):
    paths = [('Screen',screen_dir),('Screen competing enrollment',scenario_dir),('Fresh construction/grid',fresh_dir)]
    analysis = read(analysis_dir/'run.json') if analysis_dir and (analysis_dir/'run.json').exists() else {}
    original = analysis.get('config',{}).get('cache_source_dir')
    paths += [('Original failed calibration',Path(original) if original else None),('Amended calibration/evaluation',analysis_dir),('Fresh competing enrollment',scenario_fresh_dir)]
    rows,total = [],0.
    for label,directory in paths:
        if directory is None or not (directory/'run.json').exists():
            rows.append([label,'missing','missing','missing']); continue
        run = read(directory/'run.json')
        duration = run.get('duration_seconds')
        if isinstance(duration,(int,float)): total += duration
        rows.append([label,run.get('outcome'),duration,run.get('commit')])
    final = read(scenario_fresh_dir/'run.json') if scenario_fresh_dir and (scenario_fresh_dir/'run.json').exists() else {}
    charged = final.get('config',{}).get('parent_spent_seconds',0)+final.get('duration_seconds',0) if final else None
    return ['## Execution accounting and interruptions', '',
        table(['Component','Saved outcome','Recorded wall seconds','Scientific commit'],rows),
        f'Recorded component wall time totals {fmt(total)} seconds. Charged step-2 budget is {fmt(charged)} seconds; '
        f'the difference is {fmt(charged-total if charged is not None else None)} seconds of interruption allowance, not measured compute. '
        'The cap is 14400 seconds. These are conservative wall-time charges, not isolated GPU benchmarks; free acquisition time is excluded.', '',
        'The original calibration failure is retained. Two app restarts interrupted evaluation before completion; their last-journaled durations '
        'remain included in the amended run. Historical invocation entries marked running are retained interruption evidence, not live children. '
        'Unchanged-code resumes reused saved native calls and lossless descriptor files. The final evaluation and competing-enrollment invocations completed. '
        'The first SD1.5 fresh-grid invocation also retained a Windows status-file-lock failure before unchanged-code resume. '
        'Download/helper failures and canonical source-release checks remain in the acquisition records and dev-log. No threshold, descriptor, source or rule changed on resume.', '']


def step2(screen_dir, scenario_dir=None, fresh_analysis_dir=None, fresh_scenario_dir=None, fresh_dir=None):
    run = read(screen_dir/'run.json')
    config = run['config']
    lines = ['# Registry verification development results', '',
        f'Screen status: **{fmt(run.get("outcome"))}**. Chosen step-1 method: **{fmt(config.get("chosen_method"))}**. '
        f'Descriptor selected by the fixed D1-then-D2 rule: **{fmt(run.get("selected_descriptor"))}**. '
        f'Advance to fresh calibration/evaluation: **{fmt(run.get("advance_to_2b"))}**.', '',
        'This method adds detector side information: access to a trusted, available registry holding each published marked image’s '
        'owner, record ID, native q/h and continuous descriptor vectors. Registry trust, availability and descriptor privacy are limitations. '
        'Ownership transfer, rights management and ledgers remain outside thesis scope.', '',
        'The real near-duplicate panel uses 20 fixed different-frame pairs from one licensed Tears of Steel live-action footage collection, '
        'split 7/13 for calibration/evaluation. Separate photographs define different instances here. Fixed scene-linear clipping and sRGB conversion '
        'can remove detail; verified abstentions do not demonstrate content discrimination. This narrow panel is not a representative population sample.', '',
        'The semantic mark is an owner-and-record pointer. F_R requires a found/read pointer, a record within the native q radius, '
        'and correct-record identification above the descriptor threshold. Fingerprint-only search omits the pointer. '
        'The screen uses 24 consulted development sources per method (N=24), not held-out data. '
        'Thresholds are nextafter above the maximum observed primary negative and are exploratory.', '',
        f'Native q radius: {fmt(run.get("native_q_radius"))}. Human visual admissibility: missing.', '',
        '## Descriptor thresholds and fixed screen gate', '']
    fresh_evaluation = None
    if fresh_analysis_dir is not None and (fresh_analysis_dir/'run.json').exists():
        fresh_summary = read(fresh_analysis_dir/'run.json')
        fresh_evaluation = fresh_summary.get('evaluation')
        lines[2:2] = fresh_primary_evaluation_lead(fresh_summary)
    gate_rows, cells, controls, costs = [], [], [], []
    for name,s in run.get('descriptors',{}).items():
        gate_rows.append([name,s.get('tau'),s.get('max_negative'),s.get('negative_n'),s.get('observed_descriptor_false_accepts'),
                          s.get('decision'),s.get('passes_kill_rule'),len(s.get('missing',[])),s.get('unresolved_safety_blocked_impostor_pairs')])
        for key,c in s.get('cells',{}).items():
            margin = None if c.get('min_positive') is None or c.get('max_negative') is None else c['min_positive']-c['max_negative']
            cells.append([name,key,c.get('auc'),c.get('min_positive'),c.get('max_negative'),margin,
                fraction(c.get('known'),c.get('planned')),fraction(c.get('descriptor_accepts'),c.get('planned')),
                fraction(c.get('correct_record_F_R'),c.get('planned')),fraction(c.get('source_majority_F_R'),24),
                fraction(c.get('fingerprint_correct'),c.get('planned')),c.get('fingerprint_wrong_accepts'),
                c.get('safety_blocked'),c.get('execution_unknown')])
            kk = c.get('candidate_multiplicity',[])
            costs.append([name,key,min(kk) if kk else None,median(kk) if kk else None,max(kk) if kk else None])
        n = s.get('negative_controls',{})
        controls.append([name,n.get('C0_planned'),n.get('C0_known'),n.get('C0_pointer_found'),n.get('C0_registry_accepts'),
            n.get('C0_fingerprint_correct'),n.get('C0_fingerprint_wrong_accepts'),n.get('wrong_owner_pointer_found'),
            n.get('wrong_owner_registry_accepts')])
    lines += [table(['Descriptor','Tau','Maximum negative','Observed negatives','Observed false accepts','Decision','Pass','Execution/descriptor missing','Unresolved blocked negative pairs'],gate_rows),
        'D1 is primary. D2 becomes primary only after a decisive D1 failure; D3 is descriptive. '
        'The chosen method must reach at least 21/24 source majorities at .2 on both SD1.5 and SD2.1, with zero observed false accepts. '
        'Safety blocks are failed positive slots, while their negative comparisons stay unresolved. '
        'Execution errors are not hidden as safety blocks. Missing descriptive PP1 results do not change the primary gate.', '',
        '## Per-cell discrimination, detection and identification', '',
        'Descriptor TPR and F_R entries use the fixed planned-seed denominator; known/planned exposes unavailable similarities. '
        'Source-majority F_R requires at least two successful seeds. Clean/VAE conditions use one observation per source. '
        'AUC and maximum-negative comparisons use the pooled observed primary negatives.', '',
        table(['Descriptor','Method/model/strength','AUC','Minimum positive','Maximum negative','Margin','Known/planned','Descriptor TPR','Correct-record F_R','Majority F_R','Fingerprint correct','Fingerprint wrong accept','Blocked','Unknown'],cells),
        '## Negative controls and unresolved evidence', '',
        table(['Descriptor','C0 planned','C0 known','C0 pointer found','C0 registry accepts','C0 fingerprint correct','C0 fingerprint wrong','Wrong-owner pointer found','Wrong-owner registry accepts'],controls),
        'Unmarked C0 queries matching their own source record are expected fingerprint matches. Their pointer/registry accepts are adverse provenance controls. '
        'The alpha-only screen has no beta records, so zero beta registry accepts alone is not evidence of arbitrary-owner security. '
        'Zero observed negative accepts does not establish a population false-positive rate.', '']
    for name,s in run.get('descriptors',{}).items():
        lines += [f'{name}: true missing evidence `{fmt(s.get("missing"))}`; descriptive PP1 missing evidence `{fmt(s.get("descriptive_PP1_missing"))}`. '
                  f'Negative scope: {fmt(s.get("false_positive_scope"))}', '']
        scorepath = screen_dir/f'{name}-scores.json'
        if scorepath.exists():
            scores = read(scorepath)
            pp = scores.get('PP1_descriptive',[])
            lines += [f'{name} retained PP1 (descriptive): {len(pp)} observed rows; '
                f'{sum(r.get("descriptive_descriptor_accept") is True for r in pp)} descriptor accepts; '
                f'{sum(r.get("descriptive_pointer_and_descriptor") is True for r in pp)} pointer-plus-descriptor donor accepts. '
                'This historical 12-source panel is excluded from the primary threshold fit.', '']
    lines += ['## Registry size, storage and measured lookup cost', '',
        table(['Descriptor','Method/model/strength','Minimum K','Median K','Maximum K'],costs)]
    storage = []
    for name,s in run.get('descriptors',{}).items():
        for method,values in s.get('per_record_descriptor_bytes',{}).items():
            known = [v for v in values if v is not None]
            storage.append([name,method,len(values),min(known) if known else None,max(known) if known else None,
                            sum(known),sum(v is None for v in values)])
    lines += [table(['Descriptor','Method','Records N','Minimum bytes/record','Maximum bytes/record','Total raw descriptor bytes','Missing vectors'],storage),
        'Bytes refer to the saved normalized float64 vector only; q/h, record metadata, indexes and file/container overhead are additional. '
        'Screen scoring computes exhaustive N=24 cosine tables for impostor analysis. A prospective registry query filters owner/q and compares K candidates; '
        'fingerprint-only search compares N records.', '',
        f'Measured timing summary: `{fmt(run.get("timing_summary"))}`.', '',fmt(run.get('timing_scope')), '',
        '## ROC artifacts and complete numeric evidence', '',
        ', '.join(link(screen_dir/f'{d}-roc.json') for d in run.get('descriptors',{}))+'. '
        +(link(screen_dir/'pooled-descriptor-roc.svg','Standalone pooled descriptor ROC figure')
          if (screen_dir/'pooled-descriptor-roc.svg').exists() else 'Standalone ROC SVG: missing (numeric ROC links remain available)')+'. '
        'The curves describe descriptor discrimination and omit pointer failures; F_R above includes pointer failures.', '',
        'Complete native calls, all ordered impostor pairs, q-nearest flags, residual T4 and PP1 scores: '
        +', '.join(link(screen_dir/f'{d}-scores.json') for d in run.get('descriptors',{}))+'.', '',
        f'Run provenance: {link(screen_dir/"run.json")}; descriptor cache references: {link(screen_dir/"descriptor-index.json")}. '
        f'Commit `{fmt(run.get("commit"))}`; screen duration {fmt(run.get("duration_seconds"))} seconds; '
        f'accounted step-2 duration {fmt(run.get("step2_accounted_seconds"))} seconds.', '']
    lines += scenario_section(scenario_dir)
    if fresh_dir is None and fresh_analysis_dir is not None and (fresh_analysis_dir/'run.json').exists():
        inferred = read(fresh_analysis_dir/'run.json').get('config',{}).get('fresh_dir')
        fresh_dir = Path(inferred) if inferred else None
    if fresh_dir is not None or fresh_analysis_dir is not None:
        lines += fresh_construction_section(fresh_dir)
    if fresh_analysis_dir is not None:
        freshpath = fresh_analysis_dir/'run.json'
        if not freshpath.exists():
            lines += ['## Conditional fresh calibration and evaluation', '', 'Missing: no fresh analysis run artifact.', '']
        else:
            fresh = read(freshpath)
            lines += ['## Fresh calibration and evaluation', '',f'Fresh analysis status: **{fmt(fresh.get("outcome"))}**. '
                'Thresholds are fitted only on the 20 calibration sources and licensed near-duplicate calibration pairs, then frozen. '
                'Evaluation uses the disjoint 40-source development split; it remains development evidence.', '']
            amendment = fresh.get('config',{}).get('availability_amendment')
            lines += [f'Availability amendment: `{fmt(amendment)}`. '
                'The original calibration failure is preserved: 415.907 seconds at commit `cf5de20`, before any threshold was frozen. '
                'The amended run uses post-hoc calibration, pre-evaluation semantics; it is not an unchanged preregistered analysis. '
                'Only D1 vectors independently verified to abstain below the existing native detail floor are deterministic rejections. '
                'D1 remains the fixed primary descriptor, with no D2 rescue and no feature, floor, threshold-selection or source-selection change. '
                'Expected safety-blocked negative comparisons remain unresolved under the original convention; they are not observed cosine scores or observed rejections. '
                'Genuine execution, image, call or descriptor errors remain unknown.', '',
                'Calibration `development_pass` is diagnostic only; there is no 18/20 calibration gate. '
                'The evaluation gate remains at least 36/40 source majorities at .2 on both models with zero observed false accepts. '
                'Verified abstentions fail positive slots in the full planned denominator; negative abstentions are deterministic rejects. '
                'Finite cosine coverage, verified abstentions and unknowns are reported separately below.', '']
            lines += calibration_threshold_driver_section(fresh_analysis_dir)
            for split in ('calibration','evaluation'):
                content = fresh.get(split)
                if content is None:
                    lines += [f'{split.capitalize()}: missing.', '']
                    continue
                freshrows, negrows, resource_rows = [], [], []
                for d,s in content.get('descriptors',{}).items():
                    lookup = s.get('lookup_timing') or {}
                    lookup_seconds,lookup_calls = lookup.get('seconds'),lookup.get('calls')
                    k = [n for c in s.get('cells',{}).values() for n in c.get('candidate_counts',[])
                         if isinstance(n,(int,float)) and not isinstance(n,bool) and math.isfinite(n)]
                    extraction = content.get('descriptor_extraction_metrics') or {}
                    scorepath = fresh_analysis_dir/f'{split}-{d}-scores.json'
                    observations = read(scorepath).get('positives_and_C0') if scorepath.exists() else None
                    searchable = None
                    if observations is not None:
                        source_ids = sorted({o['source_id'] for o in observations})
                        source_index = {sid:i for i,sid in enumerate(source_ids)}
                        clean_searchable = set()
                        for o in observations:
                            if o.get('phase') != 'clean' or o.get('control') != 'C1':
                                continue
                            scores = o.get('scores') or []
                            own = scores[source_index[o['source_id']]] if len(scores) == len(source_ids) == s.get('registry_N') else None
                            if o.get('own_score_availability') == 'observed' or (
                                    isinstance(own,(int,float)) and not isinstance(own,bool) and math.isfinite(own)):
                                clean_searchable.add(o['source_id'])
                        searchable = len(clean_searchable)
                    resource_rows.append([d,s.get('registry_N'),fraction(searchable,s.get('registry_N')),
                        s.get('descriptor_bytes'),lookup_calls,lookup_seconds,
                        lookup_seconds/lookup_calls if isinstance(lookup_seconds,(int,float)) and lookup_calls else None,
                        len(k),min(k) if k else None,median(k) if k else None,max(k) if k else None,
                        extraction.get('extraction_seconds',{}).get(d)])
                    for cell,c in s.get('cells',{}).items():
                        tpr = fresh_descriptor_tpr(observations,cell,s.get('tau'),c.get('planned_seeds'),c.get('source_denominator'))
                        freshrows.append([d,cell,s.get('tau'),fraction(c.get('observed'),c.get('planned_seeds')),
                            c.get('own_cosine_observed'),c.get('own_verified_native_weak_detail_abstentions'),
                            f'{fraction(tpr["seed"],c.get("planned_seeds"))}; rate {fmt(tpr["seed_rate"])}',
                            f'{fraction(tpr["majority"],c.get("source_denominator"))}; rate {fmt(tpr["majority_rate"])}',
                            fraction(c.get('seed_F_R'),c.get('planned_seeds')),fraction(c.get('source_majority_F_R'),c.get('source_denominator')),
                            c.get('TPR_seed'),c.get('TPR_source_majority'),
                            fraction(c.get('seed_fingerprint_correct'),c.get('planned_seeds')),
                            fraction(c.get('source_majority_fingerprint'),c.get('source_denominator')),c.get('old_F_seed'),c.get('old_F_source_majority'),
                            c.get('safety_blocked'),c.get('execution_unknown'),s.get('development_pass')])
                    for family,n in s.get('negative_families',{}).items():
                        negrows.append([d,family,fraction(n.get('observed'),n.get('planned')),n.get('registry_false_accepts'),n.get('fingerprint_false_accepts'),
                            n.get('verified_native_weak_detail_abstentions'),n.get('unknown'),
                            n.get('registry_source_clustered'),n.get('fingerprint_source_clustered')])
                lines += [f'### {split.capitalize()}', '',table(['Descriptor','Cell','Frozen tau','Available images','Own cosine finite','Own native abstentions','Own-descriptor TPR seed','Own-descriptor TPR majority','Seed F_R','Majority F_R','Stored TPR_seed (F_R rate)','Stored TPR_source_majority (F_R rate)','Fingerprint correct','Fingerprint majority','Old F seeds','Old F majority','Blocked','Unknown','Diagnostic pass (cal) / development pass (eval)'],freshrows),
                    table(['Descriptor','Negative family','Observed cosine/planned','Registry false accepts','Fingerprint false accepts','Native abstentions','Unknown','Registry cluster bounds','Fingerprint cluster bounds'],negrows)]
                lines += ['TPR_seed and TPR_source_majority are the stored correct-record F_R rates on the full planned seed '
                          'and source denominators, respectively; the adjacent F_R columns retain their numerator/denominator counts. '
                          'Unavailable or abstaining positives do not contribute successes.', '']
                lines += ['Own-descriptor TPR compares each C1 query only with its own enrolled record at the frozen descriptor tau '
                          '(inclusive >=), without requiring a pointer or winning identification. It is computed from the saved score '
                          'vectors in sorted source-ID record order. Missing/nonfinite own scores fail; source majority requires at least '
                          'two successful seeds. Both rates retain full planned denominators; absent score files or an incomplete record '
                          'ordering inventory display missing rather than a measured zero.', '']
                lines += [table(['Descriptor','Planned registry N','Searchable clean references/planned','Raw descriptor bytes','Lookup calls','Lookup seconds',
                    'Mean seconds/call','K observations','Minimum K','Median K','Maximum K','Extraction seconds in cache metrics'],resource_rows),
                    f'Saved split extraction/cache metrics: `{fmt(content.get("descriptor_extraction_metrics"))}`.', '',
                    'N is the planned split-local registry size. Searchable clean references count unique clean C1 sources with '
                    'observed own-score availability or a finite saved own cosine; abstaining reference slots remain planned but '
                    'unsearchable. Raw descriptor bytes sum the available saved float64 vectors; '
                    'record metadata, q/h, indexes and container overhead are additional. K summarizes the stored positive-cell '
                    'candidate_counts, not all registry records or negative queries. Lookup timing covers paired registry and '
                    'fingerprint identification on already computed scores; the reported mean divides their combined seconds '
                    'by their combined call count, and excludes cosine extraction and scoring. Extraction/cache metrics are '
                    'the latest saved invocation snapshot with memory/disk reuse, not a cumulative extraction benchmark or '
                    'a cold-cache per-image cost. Split snapshots may overlap and must not be summed.', '']
                if split == 'calibration':
                    lines += ['The diagnostic calibration flag does not authorize, stop or select the method; the 18/20 value used internally by that diagnostic is not a protocol gate.', '']
            lines += ['Fresh numeric evidence: '+link(freshpath)+', '+link(fresh_analysis_dir/'calibration-thresholds.json')+'.', '',
                f'Saved fresh analysis duration: {fmt(fresh.get("duration_seconds"))} seconds; '
                f'accounted step-2 duration: {fmt(fresh.get("step2_accounted_seconds"))} seconds. '
                'Run duration includes journaled interrupted invocations as well as completed ones. Any separately recorded '
                'allowance for unjournaled interruption time is separate budget accounting, not measured extraction or lookup time.', '']
    if fresh_scenario_dir is not None:
        lines += scenario_section(fresh_scenario_dir,'Fresh regenerate-and-enroll scenario')
    if fresh_analysis_dir is not None:
        lines += execution_accounting_section(screen_dir,scenario_dir,fresh_dir,fresh_analysis_dir,fresh_scenario_dir)
    primary = (fresh_evaluation or {}).get('primary',{})
    if primary.get('complete') is True and primary.get('development_pass') is False:
        interpretation = ('The completed fresh primary evaluation failed the fixed development gate. The earlier screen pass does not '
            'override this failed fresh design, and no held-out confirmatory run is launched. The user decision is whether to close '
            'this route and use the bounded negative thesis result, or authorize a new research direction. Descriptor rescue, threshold '
            'retuning and a new direction are not automatic continuations of this result.')
    else:
        interpretation = ('A screen pass is a hypothesis selected on consulted images. A completed fresh development pass would still '
            'require user approval before a held-out confirmatory run. A kill-rule failure closes this registry route under the fixed design.')
    lines += ['## Interpretation and next decision', '',interpretation+' '
        'No chapter finalization, submission, publication or human visual verdict is implied.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='step',required=True)
    one = subs.add_parser('step1')
    one.add_argument('--run-dir',type=Path,required=True)
    one.add_argument('--output',type=Path,required=True)
    two = subs.add_parser('step2')
    two.add_argument('--screen-dir',type=Path,required=True)
    two.add_argument('--scenario-dir',type=Path)
    two.add_argument('--fresh-analysis-dir',type=Path)
    two.add_argument('--fresh-scenario-dir',type=Path)
    two.add_argument('--fresh-dir',type=Path,help='Optional fresh construction directory; otherwise inferred from fresh analysis config')
    two.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    content = step1(args.run_dir) if args.step == 'step1' else step2(args.screen_dir,args.scenario_dir,args.fresh_analysis_dir,args.fresh_scenario_dir,args.fresh_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(content,encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
