"""Read-only L1 endpoint analysis, including separately retained technical completion."""
import argparse
import collections
import json
from pathlib import Path

OWNER = 'qim-pilot-owner-alpha'
IDS = (1675, 468505)
ARMS = ('L', 'P')
CONDITIONS = ('clean', 'sd15_vae', 'sdxl_vae')


def checked(row, target):
    s = row['calls'][OWNER]['semantic']
    return bool(s['read'] and s['found'] and s['content_match'] and int(s['decoded_code'], 16) == target)


def quality(m):
    return bool((m.get('psnr_infinite') or m['psnr_db'] > 35) and m['ssim_rgb'] > .9 and m['lpips'] < .1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--completion', type=Path)
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    run = json.loads((args.run/'run.json').read_text(encoding='utf-8'))
    raw = run['rows']
    rows = {r['id']: r for r in raw}
    assert len(rows) == len(raw) == len(run['inventory']) == 96
    assert set(rows) == {r['id'] for r in run['inventory']}
    targets = {s: int(rows[f'direction-{s}']['intended_q'], 16) for s in IDS}
    original_status = dict(collections.Counter(r['status'] for r in raw))
    completion = None
    if args.completion:
        completion = json.loads((args.completion/'run.json').read_text(encoding='utf-8'))
        extra = completion['rows']
        expected = {k for k, r in rows.items() if r['status'] == 'failed' and r['phase'] == 'T3'
                    and r['strength'] == .1 and 'unlisted regeneration strength' in r['error']}
        assert len(expected) == 12 and {r['id'] for r in extra} == expected and len(extra) == 12
        for r in extra:
            for key in ('phase', 'source_id', 'strength', 'seed', 'control', 'arm'):
                assert r.get(key) == rows[r['id']].get(key), (r['id'], key)
            rows[r['id']] = r
    screen = []
    selected = {}
    for s in IDS:
        for arm in ARMS:
            eligible = []
            for f in (.25, .5, .75, 1.):
                group = {c: rows[f'screen-{s}-{arm}-{f}-{c}'] for c in CONDITIONS}
                exact = {c: checked(r, targets[s]) if r['status'] == 'ok' else False for c, r in group.items()}
                strict = group['clean']['status'] == 'ok' and quality(group['clean']['quality_source'])
                if strict and all(exact.values()):
                    eligible.append(f)
                screen.append(dict(source_id=s, arm=arm, fraction=f, strict_quality=strict,
                    quality=group['clean'].get('quality_source'), exact_checked=exact,
                    bit_errors={c: (int(r['calls'][OWNER]['semantic']['decoded_code'], 16)^targets[s]).bit_count()
                                for c, r in group.items() if r['status'] == 'ok'},
                    decoded_score={c: r['calls'][OWNER]['semantic']['decoded_score'] for c, r in group.items() if r['status'] == 'ok'},
                    fixed_q_score={c: r['analysis_only']['fixed_q_score'] for c, r in group.items()
                                   if r['status'] == 'ok' and 'fixed_q_score' in r['analysis_only']}))
            value = min(eligible) if eligible else None
            assert value == rows[f'selection-{s}-{arm}']['selected_fraction']
            selected[f'{s}/{arm}'] = value
    t3 = []
    for arm in ARMS:
        for strength in (.1, .2):
            group = [r for r in rows.values() if r['phase'] == 'T3' and r.get('arm') == arm and r['strength'] == strength]
            t3.append(dict(arm=arm, strength=strength, planned=len(group),
                completed=sum(r['status'] == 'ok' for r in group),
                status_counts=dict(collections.Counter(r['status'] for r in group)),
                exact_checked=sum(checked(r, targets[r['source_id']]) for r in group if r['status'] == 'ok'),
                semantic_found_content=sum(bool(r['calls'][OWNER]['semantic']['found'] and r['calls'][OWNER]['semantic']['content_match'])
                                           for r in group if r['status'] == 'ok')))
    negatives = dict(c0_calls=0, c0_any=0, wrong_owner_calls=0, wrong_owner_any=0)
    for r in rows.values():
        if r['status'] != 'ok' or 'calls' not in r:
            continue
        for owner, call in r['calls'].items():
            key = 'c0' if r['control'] == 'C0' else ('wrong_owner' if owner != OWNER else None)
            if key:
                negatives[key+'_calls'] += 1
                negatives[key+'_any'] += bool(call['watermark_found'] or call['semantic']['found'] or call['instance']['found'])
    result = dict(source_run=str(args.run), commit=run['commit'], original_outcome=run['outcome'],
        original_status_counts=original_status, original_seconds=run['duration_seconds'],
        completion_run=str(args.completion) if args.completion else None,
        completion_seconds=completion['duration_seconds'] if completion else None,
        total_seconds=run['duration_seconds']+(completion['duration_seconds'] if completion else 0),
        completed_status_counts=dict(collections.Counter(r['status'] for r in rows.values())),
        selected=selected, screen=screen, t3=t3, negatives=negatives,
        primary_success=False, conclusion='Fixed L1 construction fails clean exact-q screen; L T3 not triggered.',
        limits=['Two adaptively selected development sources.', 'No h was embedded.',
                'Observed dependent negatives do not establish population FPR.',
                'Technical completion preserves the original failed record.'])
    assert all(selected[f'{s}/L'] is None for s in IDS), 'Reassess conclusion if data change'
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/'l1-statistics.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    lines = ['# L1 decoder-tangent screen results', '',
        f'Exploratory local study at `{run["commit"]}`. The fixed L1 construction fails its clean exact-message screen; neither source supplies a qualifying latent-arm image. L-arm T3 was not executed.', '',
        '| Source | Arm | Fraction | Strict quality | Clean exact q | SD1.5 VAE exact q | SDXL VAE exact q |',
        '|---|---|---:|---:|---:|---:|---:|']
    for r in screen:
        fields = [r['source_id'], r['arm'], r['fraction'], int(r['strict_quality'])] + [int(r['exact_checked'][c]) for c in CONDITIONS]
        lines.append('| '+' | '.join(map(str, fields))+' |')
    lines += ['', 'Exact q requires readable original intended bits, semantic found and content match. The two sources and four fractions per arm are repeated development measurements, not sixteen independent images.', '',
        '| Arm | Strength | Completed / planned | Exact checked q | Semantic found + content |',
        '|---|---:|---:|---:|---:|']
    for r in t3:
        lines.append(f'| {r["arm"]} | {r["strength"]} | {r["completed"]}/{r["planned"]} | {r["exact_checked"]} | {r["semantic_found_content"]} |')
    lines += ['', 'The L-arm zero completed counts mean not selected, not twelve measured regeneration failures. P is a descriptive pixel control and cannot rescue L.', '',
        f'Observed negative detections: {negatives["c0_any"]}/{negatives["c0_calls"]} C0 calls and {negatives["wrong_owner_any"]}/{negatives["wrong_owner_calls"]} wrong-owner calls. These calls reuse two sources; no population rare-event bound follows.', '',
        f'Original duration {run["duration_seconds"]:.3f} s; total with technical completion {result["total_seconds"]:.3f} s, USD 0. The original twelve strength-.1 calls failed before generation due to an imported whitelist omitting .1. Their original errors remain retained; the completion changes no image, fraction, target, threshold or selection.', '',
        'This stops one fixed direction construction, not every terminal-latent method, and adds no independent design family. Native suspect-image DCT replaces the VAE watermark reader, while seven-view CLIP remains. There is no instance payload, full dual-tier candidate, cryptographic authorization, held-out result or new M1a passage.', '',
        f'Source: `{args.run}`.', f'Completion: `{args.completion}`.' if args.completion else 'Technical completion pending.', '']
    (args.output_dir/'l1-results.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('selected','t3','negatives','total_seconds')}))


if __name__ == '__main__':
    main()
