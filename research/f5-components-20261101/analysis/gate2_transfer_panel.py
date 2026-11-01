"""G2-B: fixed 480-case CPU residual-transfer panel from saved Stage-2 marks.

Create the manifest with --inventory, execute bounded --start/--count batches,
then use --summarize. No embedding, training, diffusion or download is called.
Only PNGs accepted by C, O, O_U, Bs, Bi or B are retained. All numerical
outcomes, including failed calls, remain in append-only per-batch JSONL files.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RD = ROOT / 'research/f5-components-20261101'
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
DEV = MAIN / '.thesis-build/dev-runs'
ASSETS = MAIN / '.thesis-build/assets/a6'
OUT = RD / 'results/g2-b-transfer'
PLAN = RD / 'analysis/GATE2-TEST-PLAN.md'
RULING = RD / 'gates/GATE-2-RULING.md'
PROFILE = ROOT / 'experiments/c4-v5-two-tier-regeneration-v1/profile.json'
GATE = DEV / '20261005-0640-f5-gate-soft-views7/run.json'
OLD_T4 = DEV / '20261005-0700-f5r2-t4/run.json'
ACCOUNT = Path(__file__).with_name('account_saved_development.py')
COMMON = Path(__file__).with_name('gate2_reader.py')
SCALES = (0.5, 1.0)
ENDPOINTS = ('C', 'O', 'O_U', 'Bs', 'Bi', 'B')
ALPHA = 'qim-pilot-owner-alpha'
IMAGE_BASES = {
    'stage2a': DEV / '20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images',
    'stage2b': DEV / '20261025-0128-encoder-transfer-stage2b/results/stage2b-full/images',
}


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def output_path(name):
    path = OUT / name
    if not OUT.resolve().is_relative_to((RD / 'results').resolve()):
        raise ValueError('Output root escaped RD/results')
    if not path.resolve().is_relative_to(OUT.resolve()):
        raise ValueError('Output path escaped the fixed G2-B directory')
    return path


def write_new(path, value):
    path = output_path(Path(path).relative_to(OUT))
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def provenance(start):
    dependencies = [Path(__file__), ACCOUNT, COMMON, PLAN, RULING, PROFILE,
                    ROOT / 'scripts/f5_latent_codec.py', ROOT / 'scripts/f5_gate.py',
                    ROOT / 'scripts/three_threat_protocol.py',
                    ROOT / 'scripts/three_threat_models.py',
                    ROOT / 'scripts/m1_latent_reconstruction.py',
                    ROOT / 'scripts/revised_watermark_v5.py',
                    ROOT / 'scripts/revised_watermark_v4.py',
                    ROOT / 'scripts/a6_clip_visual.py',
                    ROOT / 'scripts/check_a6_lpips_assets.py']
    return {
        'schema': 'f5c-g2b-provenance-v1',
        'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'command': [sys.executable, *sys.argv], 'python': sys.version,
        'seconds': time.monotonic() - start,
        'dependencies_sha256': {str(p.relative_to(ROOT)): digest(p) for p in dependencies},
        'cuda_visible_devices': os.environ.get('CUDA_VISIBLE_DEVICES'),
        'phase_b_journals': 'off', 'data_split': 'development',
        'threads': 4, 'workers': 1, 'human_visual_verdict': 'MISSING',
    }


def clean_asset(row, lineno):
    if row['status'] != 'ok' or row['channel'] != 'clean':
        raise ValueError('Only successful saved clean rows may supply pixels')
    remote = row['output']['path']
    matches = [key for key in IMAGE_BASES if f'/{key}-full/images/' in remote]
    if len(matches) != 1:
        raise ValueError('Unrecognized saved Stage-2 image path: ' + remote)
    base = IMAGE_BASES[matches[0]]
    path = base / Path(remote).name
    if not path.resolve().is_relative_to(base.resolve()) or path.suffix != '.png':
        raise ValueError('Saved image path escaped allowlisted PNG directory')
    if not path.is_file():
        raise FileNotFoundError(path)
    expected = row['output']['sha256']
    if digest(path) != expected:
        raise ValueError('Saved image hash mismatch: ' + str(path))
    return {'path': str(path), 'sha256': expected, 'row_id': row['id'],
            'journal_line': lineno, 'arm': row['arm'], 'source': row['source_id']}


def inventory():
    started = time.monotonic()
    if OUT.exists():
        raise FileExistsError('Refusing to overwrite existing panel: ' + str(OUT))
    api = runpy.run_path(str(ACCOUNT))
    saved, inputs = api['load']('stage2')
    clean = {(row['source_id'], row['arm']): (line, row)
             for line, row in saved.values() if row['channel'] == 'clean'}
    sources = sorted({source for source, arm in clean})
    if len(sources) != 60 or any(type(s) is not int for s in sources):
        raise ValueError('Expected the fixed sixty integer Stage-2 source IDs')
    design, evaluate = sources[::2], sources[1::2]
    donors, recipients = design[:8], evaluate
    gate = json.loads(GATE.read_text(encoding='utf-8'))
    old = json.loads(OLD_T4.read_text(encoding='utf-8'))
    if gate.get('data_split') != 'development' or old.get('data_split') != 'development':
        raise ValueError('Historical input manifest is not development')
    if old['band'] != [4, 32] or old['whitening'] != 1.0 or old['binding'] != 'soft' or old['semantic_views'] != 7:
        raise ValueError('Historical F5 reader differs from the pinned configuration')
    assets = {}
    for source, arm in [(s, a) for s in donors for a in ('unmarked', 'f5-r2')] + [(s, 'unmarked') for s in recipients]:
        line, row = clean[source, arm]
        assets[f'{source}:{arm}'] = clean_asset(row, line)
    items = []
    for donor in donors:
        for recipient in recipients:
            for scale in SCALES:
                items.append({'index': len(items), 'id': f'g2b-{donor}-{recipient}-{scale}',
                              'donor': donor, 'recipient': recipient, 'scale': scale,
                              'donor_split': 'DESIGN', 'recipient_split': 'EVALUATE',
                              'donor_c1': f'{donor}:f5-r2', 'donor_c0': f'{donor}:unmarked',
                              'recipient_c0': f'{recipient}:unmarked'})
    if len(items) != 480 or set(donors) & set(recipients):
        raise ValueError('Fixed 8 x 30 x 2 disjoint panel invariant failed')
    meta = provenance(started)
    manifest = {
        'schema': 'f5c-g2b-inventory-v1', 'source_ids': sources,
        'design': design, 'evaluate': evaluate, 'donors': donors, 'recipients': recipients,
        'scales': list(SCALES), 'items': items, 'assets': assets, 'stage2_input': inputs,
        'profile': gate['profile'], 'historical_inputs_sha256': {str(p): digest(p) for p in (GATE, OLD_T4)},
        'reader': {'band': [4, 32], 'whitening': 1.0, 'binding': 'soft',
                   'semantic_views': 7, 'device': 'cpu', 'owner': ALPHA, 'roster_size': 1},
        'formula': 'three_threat_protocol.residual_transfer: clip then ties-to-even RGB8 rounding',
        'png_retention': 'any C or O or O_U or Bs or Bi or B, regardless of quality',
        'kill_rule': 'any B and not C at PSNR > 35 dB and SSIM > .9',
        'provenance': meta,
    }
    OUT.mkdir(parents=True, exist_ok=False)
    write_new(output_path('inventory.json'), manifest)
    print(json.dumps({'items': len(items), 'donors': donors, 'recipients': len(recipients),
                      'output': str(OUT), 'seconds': time.monotonic() - started}))


def load_inventory():
    path = output_path('inventory.json')
    inv = json.loads(path.read_text(encoding='utf-8'))
    expected = [(d, r, scale) for d in inv['source_ids'][::2][:8]
                for r in inv['source_ids'][1::2] for scale in SCALES]
    actual = [(x['donor'], x['recipient'], x['scale']) for x in inv['items']]
    if len(inv['source_ids']) != 60 or actual != expected or len(actual) != 480:
        raise ValueError('Manifest does not match the fixed G2-B construction')
    for item in inv['assets'].values():
        path = Path(item['path'])
        if not any(path.resolve().is_relative_to(base.resolve()) for base in IMAGE_BASES.values()):
            raise ValueError('Nonallowlisted input asset')
        if path.suffix != '.png':
            raise ValueError('Only PNG inputs are authorized')
    return inv


def load_optional_lpips(models):
    """Existing explicit weights only; models.block_network is already active."""
    try:
        package = Path(importlib.metadata.distribution('lpips').locate_file('lpips'))
        weights = [ASSETS / 'alexnet/alexnet-owt-7be5be79.pth', package / 'weights/v0.1/alex.pth']
        if not all(p.is_file() for p in weights):
            raise FileNotFoundError('Existing AlexNet and LPIPS weights are both required')
        from check_a6_lpips_assets import verify_package
        verified = verify_package(package)
        metric = models.load_lpips(ASSETS, package)
        return metric, {'status': 'available', 'weights_sha256': {str(p): digest(p) for p in weights},
                        'verified_package': verified}
    except Exception as exc:
        return None, {'status': 'MISSING', 'reason': repr(exc), 'download_attempted': False}


def quality_eligible(metrics):
    psnr = metrics.get('psnr_db')
    return bool((metrics.get('psnr_infinite') or psnr is not None and psnr > 35.0)
                and metrics.get('ssim_rgb') is not None and metrics['ssim_rgb'] > 0.9)


def batch(start_index, count):
    started = time.monotonic()
    if not 0 <= start_index < 480 or not 1 <= count <= 8 or start_index + count > 480:
        raise ValueError('Require --start 0..479 and --count 1..8 inside the fixed panel')
    inv = load_inventory()
    selected = inv['items'][start_index:start_index + count]
    name = f'batch-{start_index:04d}-{count:02d}'
    target, run_path = output_path(name + '.jsonl'), output_path(name + '-run.json')
    if target.exists() or run_path.exists():
        raise FileExistsError('Refusing to overwrite batch: ' + name)
    selected_ids = {x['id'] for x in selected}
    for previous in sorted(OUT.glob('batch-*.jsonl')):
        for line in previous.read_text(encoding='utf-8').splitlines():
            if line.strip() and json.loads(line)['id'] in selected_ids:
                raise ValueError('A selected ID already has a retained outcome: ' + str(previous))
    for variable in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'DIFFUSERS_OFFLINE',
                     'HF_DATASETS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY'):
        os.environ[variable] = '1'
    sys.path[:0] = [str(Path(__file__).parent), str(ROOT), str(ROOT / 'scripts')]
    import numpy as np
    import torch
    from PIL import Image
    import three_threat_models as models
    models.block_network()
    from scripts import f5_latent_codec as f5
    from scripts import revised_watermark_v5 as v5
    from a6_clip_visual import load_visual_encoder
    from f5_gate import semantic_feature
    from m1_latent_reconstruction import quality
    from three_threat_protocol import residual_transfer
    from gate2_reader import endpoints

    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    if torch.cuda.is_available():
        raise RuntimeError('CUDA must be unavailable')
    profile = json.loads(PROFILE.read_text(encoding='utf-8'))
    if v5.validate_profile(profile) != v5.validate_profile(inv['profile']):
        raise ValueError('Current and frozen saved profiles differ')
    reader = f5.Reader(ASSETS, device='cpu')
    clip, transform = load_visual_encoder(ASSETS / 'clip/ViT-B-32.pt', device='cpu')
    metric, lpips_meta = load_optional_lpips(models)
    meta = provenance(started)
    meta.update({'inventory_sha256': digest(output_path('inventory.json')), 'batch': name,
                 'selected_indices': [x['index'] for x in selected], 'selected': len(selected),
                 'reader': inv['reader'], 'lpips': lpips_meta,
                 'model_assets_sha256': {str(p): digest(p) for p in (
                     ASSETS / 'sd15-fp16/vae/config.json',
                     ASSETS / 'sd15-fp16/vae/diffusion_pytorch_model.fp16.safetensors',
                     ASSETS / 'clip/ViT-B-32.pt')},
                 'status': 'started', 'completed': 0, 'failure': None})
    cache = {}

    def pixels(key):
        if key not in cache:
            record = inv['assets'][key]
            path = Path(record['path'])
            if digest(path) != record['sha256']:
                raise ValueError('Input hash changed: ' + str(path))
            with Image.open(path) as image:
                if image.mode != 'RGB' or image.size != (512, 512):
                    raise ValueError('Expected saved RGB 512x512 PNG: ' + str(path))
                cache[key] = np.asarray(image, np.uint8).copy()
        return cache[key]

    durations = []
    status, failure = 'complete', None
    with target.open('x', encoding='utf-8') as handle:
        for item in selected:
            elapsed = time.monotonic() - started
            # Leave a large allowance for one CPU image and final provenance.
            allowance = max(90.0, 1.5 * max(durations, default=0.0))
            if elapsed > 360.0 or elapsed + allowance > 510.0:
                status = 'partial-time-budget'
                break
            tick = time.monotonic()
            row = dict(item)
            row.update({'result_status': 'started', 'owner': ALPHA,
                        'input_sha256': {key: inv['assets'][item[key]]['sha256']
                                         for key in ('donor_c1', 'donor_c0', 'recipient_c0')},
                        'provenance': {'batch_run': run_path.name, 'commit': meta['commit'],
                                       'script_sha256': meta['dependencies_sha256'][str(Path(__file__).relative_to(ROOT))],
                                       'inventory_sha256': meta['inventory_sha256']},
                        'raw': None, 'endpoints': None, 'quality': None, 'saved_png': None})
            try:
                d1, d0, r0 = (pixels(item[key]) for key in ('donor_c1', 'donor_c0', 'recipient_c0'))
                # This is the exact function used by the 20261005 historical panel.
                out = np.asarray(residual_transfer(r0.tolist(), d1.tolist(), d0.tolist(), item['scale']), np.uint8)
                row['output_rgb8_sha256'] = hashlib.sha256(out.tobytes()).hexdigest()
                metrics = quality(r0, out)
                metrics.update({'lpips': None, 'lpips_status': lpips_meta['status']})
                if metric is not None:
                    metrics.update({'lpips': models.lpips_score(metric, r0, out), 'lpips_status': 'ok'})
                metrics['strict_psnr_ssim'] = quality_eligible(metrics)
                row['quality'] = metrics
                features = semantic_feature(models, clip, transform, out, 7)
                latent = reader.latent(out)
                raw = f5.detect_rgb(out, latent, ALPHA, profile, features,
                                    binding_mode='combined', roster_size=1,
                                    band=(4, 32), whitening=1.0, binding='soft')
                ep = endpoints(raw)
                if not all(type(ep[key]) is bool for key in ENDPOINTS):
                    raise ValueError('Common endpoint module did not return Boolean acceptance fields')
                row.update({'raw': raw, 'endpoints': ep,
                            'g2b_kill_event': bool(ep['B'] and not ep['C'] and metrics['strict_psnr_ssim'])})
                if any(ep[key] for key in ENDPOINTS):
                    png = output_path(item['id'] + '.png')
                    with png.open('xb') as image_handle:
                        Image.fromarray(out).save(image_handle, format='PNG')
                    row['saved_png'] = {'path': png.name, 'sha256': digest(png),
                                        'criterion': [key for key in ENDPOINTS if ep[key]]}
                row['result_status'] = 'ok'
            except Exception as exc:
                row.update({'result_status': 'error', 'error': repr(exc), 'traceback': traceback.format_exc()})
                status, failure = 'failed', repr(exc)
            row['seconds'] = time.monotonic() - tick
            durations.append(row['seconds'])
            handle.write(json.dumps(row, allow_nan=False) + '\n')
            handle.flush()
            meta['completed'] += 1
            if failure:
                break
    meta.update({'status': status, 'failure': failure, 'seconds': time.monotonic() - started,
                 'output_sha256': digest(target), 'per_image_seconds': durations,
                 'under_540_seconds': time.monotonic() - started < 540.0})
    write_new(run_path, meta)
    print(json.dumps({key: meta[key] for key in ('batch', 'selected', 'completed', 'status', 'failure', 'seconds')}))
    if not meta['under_540_seconds']:
        raise RuntimeError('Run exceeded the conservative 540-second budget')
    if failure:
        raise RuntimeError(failure)


def summarize():
    started = time.monotonic()
    inv = load_inventory()
    targets = [output_path(x) for x in ('summary.json', 'by-donor.csv', 'by-recipient.csv', 'REPORT.md')]
    if any(p.exists() for p in targets):
        raise FileExistsError('Refusing to overwrite an existing G2-B summary')
    expected = {item['id']: item for item in inv['items']}
    rows, batches = {}, []
    for path in sorted(OUT.glob('batch-*.jsonl')):
        run_path = path.with_name(path.stem + '-run.json')
        run = json.loads(run_path.read_text(encoding='utf-8'))
        if digest(path) != run['output_sha256'] or run['inventory_sha256'] != digest(output_path('inventory.json')):
            raise ValueError('Batch output or inventory hash mismatch')
        batches.append({'file': path.name, 'sha256': digest(path), 'run': run_path.name,
                        'run_sha256': digest(run_path), 'status': run['status'],
                        'seconds': run['seconds'], 'under_540_seconds': run['under_540_seconds'],
                        'commit': run['commit'], 'completed': run['completed']})
        for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row['id'] not in expected or row['id'] in rows:
                raise ValueError('Unknown or duplicate retained outcome ID: ' + row['id'])
            if any(row[key] != expected[row['id']][key] for key in ('donor', 'recipient', 'scale', 'index')):
                raise ValueError('Outcome differs from the frozen panel identity')
            if row['result_status'] == 'ok':
                if bool(row['saved_png']) != any(row['endpoints'][key] for key in ENDPOINTS):
                    raise ValueError('PNG retention did not match the fixed any-endpoint criterion')
                if row['saved_png'] and digest(output_path(row['saved_png']['path'])) != row['saved_png']['sha256']:
                    raise ValueError('Accepted PNG hash mismatch')
            row['location'] = f'{path.name}:{lineno}'
            rows[row['id']] = row
    good = [r for r in rows.values() if r['result_status'] == 'ok']
    eligible = [r for r in good if quality_eligible(r['quality'])]
    kills = [r for r in eligible if r['endpoints']['B'] and not r['endpoints']['C']]

    def counts(group, scheduled):
        successful = [r for r in group if r['result_status'] == 'ok']
        strict = [r for r in successful if quality_eligible(r['quality'])]
        result = {'scheduled': scheduled, 'recorded': len(group), 'ok': len(successful),
                  'missing_or_error': scheduled - len(successful), 'strict_psnr_ssim': len(strict)}
        for key in ENDPOINTS:
            result[key] = sum(bool(r['endpoints'][key]) for r in successful)
            result[key + '_strict'] = sum(bool(r['endpoints'][key]) for r in strict)
        result['B_not_C_strict'] = sum(r['endpoints']['B'] and not r['endpoints']['C'] for r in strict)
        return result

    all_counts = counts(list(rows.values()), 480)
    by_axes = {}
    for axis, sources in (('donor', inv['donors']), ('recipient', inv['recipients'])):
        groups = []
        for source in sources:
            for scale in ('all', *SCALES):
                scheduled = [r for r in inv['items'] if r[axis] == source and (scale == 'all' or r['scale'] == scale)]
                group = [rows[r['id']] for r in scheduled if r['id'] in rows]
                groups.append({axis: source, 'scale': scale, **counts(group, len(scheduled))})
        by_axes[axis] = groups
        with output_path(f'by-{axis}.csv').open('x', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(groups[0]))
            writer.writeheader()
            writer.writerows(groups)
    complete = len(good) == 480
    summary = {'schema': 'f5c-g2b-summary-v1', 'counts': all_counts, 'complete': complete,
               'kill_events': [{'id': r['id'], 'location': r['location'], 'donor': r['donor'],
                                'recipient': r['recipient'], 'scale': r['scale'], 'quality': r['quality']}
                               for r in kills],
               'promotion_killed_by_g2b': bool(kills),
               'g2b_status': 'KILL' if kills else 'NO_EVENT_COMPLETE' if complete else 'INCOMPLETE',
               'missing_ids': sorted(set(expected) - set(rows)),
               'error_ids': sorted(r['id'] for r in rows.values() if r['result_status'] != 'ok'),
               'lpips_status_counts': dict(Counter(r['quality']['lpips_status'] for r in good)),
               'independent_zero_event_95_upper': 1.0 - math.pow(0.05, 1.0 / len(eligible))
                   if complete and eligible and not kills else None,
               'independence_caveat': 'Images share donors and recipients; the independent-binomial bound is not valid panel-level evidence.',
               'batches': batches, 'provenance': provenance(started),
               'inventory_sha256': digest(output_path('inventory.json')),
               'limitations': ['Saved-mark residual transfers require paired donor C1/C0 access.',
                               'Development evidence only; no adaptive public-key security guarantee.',
                               'PSNR/SSIM do not establish invisibility; human visual assessment is MISSING.',
                               'G2-B alone cannot establish that B satisfies the other G2-A promotion conditions.']}
    write_new(output_path('summary.json'), summary)
    lines = ['# G2-B saved-mark residual-transfer panel', '',
             'MEASURED: Exploratory development results. Fixed 8 DESIGN donors x 30 EVALUATE recipients x 2 scales.', '',
             f"MEASURED: {len(good)}/480 successful reads; {len(eligible)} meet PSNR > 35 dB and SSIM > .9. "
             f"B-and-not-C strict-quality events: {len(kills)}. G2-B status: {summary['g2b_status']}.", '',
             '| Endpoint | All successful reads | Strict PSNR/SSIM |', '|---|---:|---:|']
    lines += [f"| {key} | {all_counts[key]} | {all_counts[key + '_strict']} |" for key in ENDPOINTS]
    lines += ['', 'MEASURED: Per-donor and per-recipient counts, including scales and missingness, are in by-donor.csv and by-recipient.csv. '
              'Every successful raw detector call and quality result is preserved in batch JSONL; exact input and run hashes are in inventory.json and batch run files.', '',
              'DERIVED: With zero events in 480 independent trials, the one-sided 95% binomial upper bound would be '
              f"{100 * (1 - math.pow(.05, 1 / 480)):.3f}%. These images are dependent through repeated donors and recipients, so that interpretation does not apply.", '',
              'JUDGMENT: Any strict-quality B accept rejected by C kills B promotion under the fixed ruling. '
              'Zero G2-B events establish neither adaptive security nor satisfaction of the separate G2-A conditions. '
              'No human visual verdict was supplied.']
    with output_path('REPORT.md').open('x', encoding='utf-8') as handle:
        handle.write('\n'.join(lines) + '\n')
    print(json.dumps({'counts': all_counts, 'g2b_status': summary['g2b_status'], 'batches': len(batches)}))


def main():
    if os.environ.get('CUDA_VISIBLE_DEVICES') != '-1':
        raise RuntimeError('Keep CUDA_VISIBLE_DEVICES=-1')
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--inventory', action='store_true')
    modes.add_argument('--summarize', action='store_true')
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--count', type=int, default=1)
    args = parser.parse_args()
    if args.inventory:
        inventory()
    elif args.summarize:
        summarize()
    else:
        batch(args.start, args.count)


if __name__ == '__main__':
    main()
