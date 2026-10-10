"""Recompute native writer development endpoints from retained detector calls (CPU only)."""
import argparse
import collections
import json
from pathlib import Path
import statistics

IDS = [1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768]
OWNER = 'qim-pilot-owner-alpha'
CONDITIONS = ('clean', 'sd15_vae', 'sdxl_vae')


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def any_detection(call):
    return bool(call['watermark_found'] or call['semantic']['found'] or call['instance']['found'])


def analyze(path):
    run = json.loads((path/'run.json').read_text(encoding='utf-8'))
    rows = read_rows(path/'rows.jsonl')
    counts = collections.Counter(r['source_id'] for r in rows)
    inventory_ok = set(counts) == set(IDS) and all(v == 1 for v in counts.values())
    baseline = {r['source_id']: r['max_loss'] for r in read_rows(path/'iterations.jsonl') if r['stage'] == 'baseline'}
    source_rows = []
    summary = dict(planned_sources=12, completed=0, strict_quality=0, clean_exact_qh_both=0,
        feasible=0, joint_fixed_q={c: 0 for c in CONDITIONS}, c0_observed=0, c0_any=0,
        wrong_owner_observed=0, wrong_owner_any=0)
    for sid in IDS:
        matches = [r for r in rows if r['source_id'] == sid]
        if len(matches) != 1 or matches[0]['status'] != 'ok':
            source_rows.append(dict(source_id=sid, status='missing_failed_or_duplicate'))
            continue
        r = matches[0]
        summary['completed'] += 1
        q, h = int(r['payload']['q'], 16), int(r['payload']['h'], 16)
        out = dict(source_id=sid, status='ok', accepted_updates=r['accepted_updates'],
            start_max_loss=baseline[sid], final_max_loss=r['final_loss_vector']['max_loss'],
            update_status=r['update_status'], quality=r['conditions']['clean']['quality_source'], conditions={})
        m = out['quality']
        strict = (m['psnr_infinite'] or m['psnr_db'] > 35) and m['ssim_rgb'] > .9 and m['lpips'] < .1
        summary['strict_quality'] += int(strict)
        b = r['final_balls']
        feasible = b['box'] and b['added_norm'] <= b['added_radius'] and b['total_norm'] <= b['total_radius']
        summary['feasible'] += int(feasible)
        for condition in CONDITIONS:
            c = r['conditions'][condition]
            call = c['calls'][OWNER]
            sem, inst = call['semantic'], call['instance']
            q_exact = bool(sem['read'] and int(sem['decoded_code'], 16) == q)
            h_exact = bool(inst['read'] and int(inst['decoded_code'], 16) == h)
            joint = bool(q_exact and sem['content_match'] and sem['found'])
            out['conditions'][condition] = dict(q_exact=q_exact, h_exact=h_exact, joint_fixed_q=joint,
                q_bit_errors=(int(sem['decoded_code'], 16)^q).bit_count(),
                read=sem['read'], found=sem['found'], content_match=sem['content_match'])
            summary['joint_fixed_q'][condition] += int(joint)
            if condition == 'clean':
                summary['clean_exact_qh_both'] += int(q_exact and h_exact and call['outcome'] == 'both_match')
            summary['c0_observed'] += 1
            summary['c0_any'] += int(any_detection(c['c0_call']))
            for owner, wrong in c['calls'].items():
                if owner != OWNER:
                    summary['wrong_owner_observed'] += 1
                    summary['wrong_owner_any'] += int(any_detection(wrong))
        source_rows.append(out)
    summary['prerequisite_pass'] = bool(inventory_ok and run['outcome'] == 'completed' and
        not run['budget_overrun'] and run['duration_seconds'] <= 3300 and
        all(summary[k] == 12 for k in ('completed', 'strict_quality', 'clean_exact_qh_both', 'feasible')) and
        summary['joint_fixed_q']['sd15_vae'] == 12 and summary['joint_fixed_q']['sdxl_vae'] >= 11 and
        summary['c0_observed'] == summary['wrong_owner_observed'] == 36 and
        summary['c0_any'] == summary['wrong_owner_any'] == 0)
    quality = {k: dict(mean=statistics.mean(v), minimum=min(v), maximum=max(v))
        for k in ('psnr_db', 'ssim_rgb', 'lpips')
        if (v := [r['quality'][k] for r in source_rows if r['status'] == 'ok' and r['quality'][k] is not None])}
    return dict(run=str(path), code_commit=run.get('commit'), duration_seconds=run['duration_seconds'],
        outcome=run['outcome'], budget_overrun=run['budget_overrun'], inventory_ok=inventory_ok,
        summary=summary, quality=quality, sources=source_rows,
        provenance='Recomputed from retained full detector calls and logged loss/feasibility measurements; no floating-point or image replay.',
        limitations=['Development only; same transformations optimized and evaluated.',
            'Operational h is frozen clean-decoded, not known original embedded h.',
            'Shared C0 pixels and twelve sources do not establish population FPR.',
            'No official full-pipeline T3 outcome is inferred from internal loss branches.'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = analyze(args.run)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(result['summary']))


if __name__ == '__main__':
    main()
