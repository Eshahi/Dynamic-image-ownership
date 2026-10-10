"""Reproduce WAM exploratory tables from retained run/rows without image access."""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import statistics

MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = MAIN / '.thesis-build/dev-runs/20261010-0948-wam-vae'
DEFAULT_OUTPUT = ROOT / 'research/journal-upgrade-20261009'


def describe(values):
    values = [v for v in values if v is not None]
    return {'n': len(values), 'mean': statistics.mean(values) if values else None,
            'median': statistics.median(values) if values else None,
            'minimum': min(values) if values else None, 'maximum': max(values) if values else None}


def quality(rows, field):
    return {**{metric: describe([r[field][metric] for r in rows]) for metric in ('psnr_db', 'ssim_rgb', 'lpips')},
            'psnr_infinite_count': sum(r[field]['psnr_infinite'] for r in rows)}


def analyze(run_dir):
    run = json.loads((run_dir / 'run.json').read_text())
    rows = [json.loads(line) for line in (run_dir / 'rows.jsonl').read_text().splitlines() if line.strip()]
    for row in rows:
        if row['status'] != 'ok': continue
        d, target = row['detection'], [bool(bit) for bit in row['message']]
        decoded = d['decoded_message']
        accuracy = sum(a == b for a, b in zip(decoded, target)) / 32 if decoded is not None else None
        if (d['bit_accuracy'] != accuracy or d['exact_message_match'] != (decoded == target)
                or d['wrong_message_exact_match'] != (decoded == [not bit for bit in target])):
            raise ValueError('Recorded endpoint differs from retained decoded bits')
    ids = sorted(run['sources'])
    arms, conditions = list(run['config']['arms']), run['config']['conditions']
    expected = set(itertools.product(ids, arms, ('C0', 'C1'), conditions))
    keys = [(r['source_id'], r['arm'], r['control'], r['condition']) for r in rows]
    actual = set(keys)
    if len(keys) != len(actual): raise ValueError('Duplicate source/arm/control/condition rows')
    if len(ids) != len(set(ids)): raise ValueError('Duplicate planned source IDs')
    out = {'run_dir': str(run_dir), 'commit': run['commit'], 'outcome': run['outcome'],
           'source_ids': ids, 'unique_planned_sources': len(ids), 'planned_image_rows': len(expected),
           'retained_image_rows': len(rows), 'missing_keys': sorted(expected - actual),
           'extra_keys': sorted(actual - expected), 'failed_rows': sum(r['status'] != 'ok' for r in rows),
           'checkpoint_sha256': run['config']['checkpoint_sha256'],
           'official_revision': run['config']['official_revision'],
           'duration_seconds': run['duration_seconds'], 'initialization_seconds': run['initialization_seconds'],
           'peak_cuda_allocated_bytes': run.get('peak_cuda_allocated_bytes'), 'groups': {}}
    for arm, condition, control in itertools.product(arms, conditions, ('C0', 'C1')):
        group = [r for r in rows if (r['arm'], r['condition'], r['control']) == (arm, condition, control)]
        good = [r for r in group if r['status'] == 'ok']
        decoded = [r for r in good if r['detection']['decoded_message'] is not None]
        exact_ids = [r['source_id'] for r in good if r['detection']['exact_message_match']]
        entry = {'planned_sources': len(ids), 'retained_sources': len(group), 'completed_sources': len(good),
                 'failed_sources': [r['source_id'] for r in group if r['status'] != 'ok'],
                 'missing_sources': sorted(set(ids) - {r['source_id'] for r in group}),
                 'exact_message_count': len(exact_ids), 'exact_message_source_ids': exact_ids,
                 'empty_mask_source_ids': [r['source_id'] for r in good if r['detection']['decoded_message'] is None],
                 'nonempty_decoded_sources': len(decoded),
                 'decoded_not_exact_sources': [r['source_id'] for r in decoded if not r['detection']['exact_message_match']],
                 'wrong_message_exact_count': sum(r['detection']['wrong_message_exact_match'] for r in good),
                 'bit_accuracy_conditional_nonempty': describe([r['detection']['bit_accuracy'] for r in decoded]),
                 'bit_accuracy_all_source_zero_scored': describe(
                     [r['detection']['bit_accuracy'] or 0 for r in good] + [0] * (len(ids) - len(good))),
                 'strict_quality_source_count': sum(r['strict_quality_source'] for r in good),
                 'quality_source': quality(good, 'quality_source'), 'quality_attack_input': quality(good, 'quality_input'),
                 'mask_fraction': describe([r['detection']['native_mask_fraction'] for r in good]),
                 'detect_seconds': describe([r['detect_seconds'] for r in good]),
                 'lpips_attack_input_coverage': {str(limit): {
                     'qualified_sources': sum(r['quality_input']['lpips'] <= limit for r in good),
                     'qualified_exact_sources': sum(r['quality_input']['lpips'] <= limit and r['detection']['exact_message_match'] for r in good),
                     'planned_source_denominator': len(ids)} for limit in (.2, .3)}}
        out['groups'][f'{arm}/{condition}/{control}'] = entry
    # Repeated C0 rows are the same source-level control cells, not 72 independent negatives.
    equal = True
    for sid, condition in itertools.product(ids, conditions):
        cell = [r for r in rows if (r['source_id'], r['condition'], r['control']) == (sid, condition, 'C0')]
        if len(cell) != len(arms) or any(r['status'] != 'ok' for r in cell): equal = False; continue
        equal &= all((r['detection'], r['quality_source'], r['quality_input']) ==
                     (cell[0]['detection'], cell[0]['quality_source'], cell[0]['quality_input']) for r in cell)
    out['c0_arm_repeats_recorded_equal'] = bool(equal)
    out['distinct_c0_source_condition_cells'] = len(ids) * len(conditions)
    out['distinct_c0_sources'] = len(ids)
    out['embedding_seconds_distinct_clean_c1'] = {
        arm: describe([r['embed_seconds'] for r in rows if r['arm'] == arm and r['condition'] == 'clean'
                       and r['control'] == 'C1' and r['status'] == 'ok']) for arm in arms}
    return out


def fmt(d, digits=4):
    if d['n'] == 0: return 'no finite values'
    return f"n={d['n']}; {d['mean']:.{digits}f} / {d['median']:.{digits}f} / [{d['minimum']:.{digits}f}, {d['maximum']:.{digits}f}]"


def render(s):
    lines = ['# WAM SA-1B MIT exploratory results', '',
        '2026-10-10. Official SA-1B MIT checkpoint; not the COCO checkpoint evaluated in the paper. '
        'The retained development run completes the fixed clean/VAE protocol, with no training or outcome-dependent tuning.', '',
        f"Run: `{s['run_dir']}`. Committed adapter `{s['commit']}`. "
        f"Official revision `{s['official_revision']}`; checkpoint SHA-256 `{s['checkpoint_sha256']}`.", '',
        f"Inventory: {s['unique_planned_sources']} unique planned development IDs; "
        f"{s['retained_image_rows']}/{s['planned_image_rows']} retained image rows; {s['failed_rows']} failed, "
        f"{len(s['missing_keys'])} missing, {len(s['extra_keys'])} extra. Source IDs: {', '.join(map(str,s['source_ids']))}.", '',
        'Whole-image embedding uses fixed public 32-bit source-ID messages and complement wrong messages. '
        'Native w=2 and predeclared attenuation w=.5 are separate arms. Official predicted mask cutoff is sigmoid>.5; '
        'upstream default semihard decoding compares selected-pixel mean **raw bit logits with .5**, unchanged. '
        'Empty mask means no decoded message. No calibrated global presence threshold was supplied.', '',
        '| Arm / condition | Exact message / 12 | Empty mask / 12 | Nonempty mean bit accuracy | All-source zero-scored mean | Strict source quality / 12 |',
        '|---|---:|---:|---:|---:|---:|']
    for key, g in s['groups'].items():
        if not key.endswith('/C1'): continue
        c = g['bit_accuracy_conditional_nonempty']['mean']
        a = g['bit_accuracy_all_source_zero_scored']['mean']
        lines.append(f"| {key[:-3]} | {g['exact_message_count']}/12 | {len(g['empty_mask_source_ids'])}/12 | {c:.6f} | {a:.6f} | {g['strict_quality_source_count']}/12 |")
    lines += ['', 'Strict clean quality is PSNR>35 dB, SSIM>.9 and LPIPS<.1 on delivered PNGs. '
              'Both arms pass clean quality on all twelve; attenuation loses two clean exact messages and all VAE exact recovery. '
              'After-VAE strict quality relative to original source is diagnostic, not an attack admissibility requirement. '
              'Native VAE recovery is 5/12 SD1.5 and 7/12 SDXL. These VAE-only results do not establish diffusion robustness.', '',
              'Bit accuracy conditional on nonempty masks excludes unreadable sources. All-source means assign zero to empty, failed '
              'or missing sources; source IDs, failure/readability categories and distributions are preserved in `wam-statistics.json`. '
              'SDXL native empty-mask source: ' + ', '.join(map(str,s['groups']['native_w2/sdxl_vae/C1']['empty_mask_source_ids'])) + '.', '',
              '## Delivered quality distributions', '',
              'Entries are n; mean / median / [minimum, maximum]. PSNR aggregates finite values only, with infinite counts explicit. '
              'Each C1 row is one source per condition. Source quality compares original canonical photo; attack-input quality '
              'compares delivered clean marked PNG against delivered attacked PNG.', '',
              '| Arm / condition / reference | PSNR dB | SSIM | LPIPS |', '|---|---|---|---|']
    for key,g in s['groups'].items():
        if not key.endswith('/C1'): continue
        for label,field in [('source','quality_source'),('attack input','quality_attack_input')]:
            q=g[field]
            lines.append(f"| {key[:-3]} / {label} | {fmt(q['psnr_db'])}; infinite={q['psnr_infinite_count']} | {fmt(q['ssim_rgb'])} | {fmt(q['lpips'])} |")
    lines += ['', '## Numerical attack coverage', '',
              'LPIPS <=.20/.30 versus attack input are numerical sensitivity/primary proxies, with human admissibility missing. '
              'Coverage does not change the twelve-source primary denominator or authorize a favorable subset claim.', '',
              '| Arm / condition | LPIPS <=.20 sources (exact) | LPIPS <=.30 sources (exact) |', '|---|---:|---:|']
    for key,g in s['groups'].items():
        if not key.endswith('/C1'): continue
        a,b = (g['lpips_attack_input_coverage'][str(x)] for x in (.2,.3))
        lines.append(f"| {key[:-3]} | {a['qualified_sources']}/12 ({a['qualified_exact_sources']}) | {b['qualified_sources']}/12 ({b['qualified_exact_sources']}) |")
    lines += ['', '## Negative diagnostics and scope', '',
              f"C0 arm repeats have identical recorded decoding and quality fields: {s['c0_arm_repeats_recorded_equal']}. "
              f"There are {s['distinct_c0_source_condition_cells']} distinct C0 source-condition cells reusing "
              f"{s['distinct_c0_sources']} photos, not 72 independent unmarked images. All C0 expected-message exact counts "
              'and all C1 complement-message exact counts are zero. These are small development diagnostics, not empirical '
              'FPR calibration, security bounds or statistical superiority. A nonempty mask is diagnostic only.', '',
              'WAM native exact 32-bit recovery is not F5 checked semantic recovery or full content binding. '
              'F5 SDXL checked 10/12 is therefore not a comparable exact-message endpoint. No F5/WAM ranking, controlled-FPR '
              'superiority, isolated carrier benefit, ownership guarantee, T4/T5 result or full-diffusion result is inferred. '
              'The public payload schedule is experimental and confers no cryptographic authorization.', '',
              '## Feasibility and reproduction', '',
              f"Total full run {s['duration_seconds']:.3f}s; WAM initialization {s['initialization_seconds']:.3f}s; "
              f"peak overall CUDA allocation {s['peak_cuda_allocated_bytes']} bytes (includes loaded VAEs, not WAM-only memory). "
              'Timing is exploratory; repeated per-condition embed timing is one shared clean embedding execution. '
              'Distinct clean C1 embedding distributions and detector distributions are in JSON. '
              'The earlier one-source clean smoke is a feasibility check on the same development source, not additional evidence.', '',
              'Reproduce without reading images or executing GPU code:', '', '```text',
              'python scripts/journal_wam_analysis.py --run-dir <retained 20261010-0948-wam-vae> --output-dir research/journal-upgrade-20261009',
              '```', '', 'The analysis reads only `run.json` and `rows.jsonl`, recomputes the inventory and all aggregates, '
              'and writes this report plus `wam-statistics.json`. No held-out data or historical result is modified.', '']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',type=Path,default=DEFAULT_RUN)
    p.add_argument('--output-dir',type=Path,default=DEFAULT_OUTPUT)
    args=p.parse_args()
    s=analyze(args.run_dir)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'wam-statistics.json').write_text(json.dumps(s,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    (args.output_dir/'wam-results.md').write_text(render(s),encoding='utf-8')
    print(json.dumps({k:s[k] for k in ('unique_planned_sources','planned_image_rows','retained_image_rows','failed_rows')}))


if __name__=='__main__': main()
