"""Render committed registry experiment schemas into Markdown without recomputation.

This script reads numeric artifacts only. It does not run models, select a
threshold, change a verdict, or imply human visual approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
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
    for cell,s in run.get('summary',{}).items():
        for d,v in s.get('by_descriptor',{}).items():
            attribution = v.get('pointer_attribution',{})
            rows.append([cell,d,fraction(s.get('observed_sources'),s.get('planned_sources')),
                attribution.get('original_owner_unique',0),attribution.get('wrong_owner',0),
                attribution.get('ambiguous_owners',0),attribution.get('no_attribution',0),
                v.get('pointer_original_record'),v.get('fingerprint_original_record'),
                v.get('fingerprint_both_owners'),v.get('fingerprint_order_can_favor_alpha')])
    lines += [table(['Cell','Descriptor','Observed/planned','Pointer original owner','Wrong owner','Ambiguous','No attribution',
        'Pointer original record','Fingerprint original record','Fingerprint both owners','Order can favor alpha'],rows),
        'Original-owner uniqueness is distinct from selecting the original source record. Fingerprint matches to both owners '
        'are not unique owner attribution; preferring the earlier enrollment is an external registry-order rule. '
        'The native pointer is evaluated for alpha and beta here, so a zero wrong-owner rate in the alpha-only screen is not substituted for this scenario.', '',
        'Native calls, all matching record IDs, cosine scores and enrollment-order choices: '+link(directory/'rows.jsonl')+'. '
        'This scenario does not test re-embedding/T6 or arbitrary-owner security.', '']
    observations = latest_rows(directory/'rows.jsonl')
    statuses = Counter((r.get('phase'),r.get('status')) for r in observations)
    available = [r['registry_available_records'] for r in observations if 'registry_available_records' in r]
    lines += [table(['Phase','Status','Rows'],[(phase,status,n) for (phase,status),n in sorted(statuses.items(),key=lambda x:str(x[0]))]),
        f'Available descriptor-bearing records per observed query: minimum {fmt(min(available) if available else None)}, '
        f'maximum {fmt(max(available) if available else None)}; planned N is not silently substituted for availability.', '']
    return lines


def step2(screen_dir, scenario_dir=None, fresh_analysis_dir=None, fresh_scenario_dir=None):
    run = read(screen_dir/'run.json')
    config = run['config']
    lines = ['# Registry verification development results', '',
        f'Screen status: **{fmt(run.get("outcome"))}**. Chosen step-1 method: **{fmt(config.get("chosen_method"))}**. '
        f'Descriptor selected by the fixed D1-then-D2 rule: **{fmt(run.get("selected_descriptor"))}**. '
        f'Advance to fresh calibration/evaluation: **{fmt(run.get("advance_to_2b"))}**.', '',
        'This method adds detector side information: access to a trusted, available registry holding each published marked image’s '
        'owner, record ID, native q/h and continuous descriptor vectors. Registry trust, availability and descriptor privacy are limitations. '
        'Ownership transfer, rights management and ledgers remain outside thesis scope.', '',
        'The semantic mark is an owner-and-record pointer. F_R requires a found/read pointer, a record within the native q radius, '
        'and correct-record identification above the descriptor threshold. Fingerprint-only search omits the pointer. '
        'The screen uses 24 consulted development sources per method (N=24), not held-out data. '
        'Thresholds are nextafter above the maximum observed primary negative and are exploratory.', '',
        f'Native q radius: {fmt(run.get("native_q_radius"))}. Human visual admissibility: missing.', '',
        '## Descriptor thresholds and fixed screen gate', '']
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
    if fresh_analysis_dir is not None:
        freshpath = fresh_analysis_dir/'run.json'
        if not freshpath.exists():
            lines += ['## Conditional fresh calibration and evaluation', '', 'Missing: no fresh analysis run artifact.', '']
        else:
            fresh = read(freshpath)
            lines += ['## Fresh calibration and evaluation', '',f'Fresh analysis status: **{fmt(fresh.get("outcome"))}**. '
                'Thresholds are fitted only on the 20 calibration sources and licensed near-duplicate calibration pairs, then frozen. '
                'Evaluation uses the disjoint 40-source development split; it remains development evidence.', '']
            for split in ('calibration','evaluation'):
                content = fresh.get(split)
                if content is None:
                    lines += [f'{split.capitalize()}: missing.', '']
                    continue
                freshrows, negrows = [], []
                for d,s in content.get('descriptors',{}).items():
                    for cell,c in s.get('cells',{}).items():
                        freshrows.append([d,cell,s.get('tau'),fraction(c.get('observed'),c.get('planned_seeds')),
                            fraction(c.get('seed_F_R'),c.get('planned_seeds')),fraction(c.get('source_majority_F_R'),c.get('source_denominator')),
                            fraction(c.get('seed_fingerprint_correct'),c.get('planned_seeds')),c.get('old_F_seed'),c.get('old_F_source_majority'),
                            c.get('safety_blocked'),c.get('execution_unknown'),s.get('development_pass')])
                    for family,n in s.get('negative_families',{}).items():
                        negrows.append([d,family,fraction(n.get('observed'),n.get('planned')),n.get('registry_false_accepts'),n.get('fingerprint_false_accepts'),
                            n.get('registry_source_clustered'),n.get('fingerprint_source_clustered')])
                lines += [f'### {split.capitalize()}', '',table(['Descriptor','Cell','Frozen tau','Observed','Seed F_R','Majority F_R','Fingerprint correct','Old F seeds','Old F majority','Blocked','Unknown','Development pass'],freshrows),
                    table(['Descriptor','Negative family','Observed','Registry false accepts','Fingerprint false accepts','Registry cluster bounds','Fingerprint cluster bounds'],negrows)]
            lines += ['Fresh numeric evidence: '+link(freshpath)+', '+link(fresh_analysis_dir/'calibration-thresholds.json')+'.', '']
    if fresh_scenario_dir is not None:
        lines += scenario_section(fresh_scenario_dir,'Fresh regenerate-and-enroll scenario')
    lines += ['## Interpretation and next decision', '',
        'A screen pass is a hypothesis selected on consulted images. A completed fresh development pass would still require user approval '
        'before a held-out confirmatory run. A kill-rule failure closes this registry route under the fixed design. '
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
    two.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    content = step1(args.run_dir) if args.step == 'step1' else step2(args.screen_dir,args.scenario_dir,args.fresh_analysis_dir,args.fresh_scenario_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(content,encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
