"""Matched exploratory WAM T3 exact-message probe; no calibrated presence endpoint."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from journal_wam_probe import MAIN, ASSET, ARMS, REVISION, Adapter, message, sha, write

WAM_RUN = MAIN / '.thesis-build/dev-runs/20261010-0948-wam-vae'
F5_RUN = MAIN / '.thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7'
STRENGTHS, SEEDS, CAP = (.1, .2), (0, 1, 2), 900.
IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768)
CHECKPOINT_SHA = '90ef232384e023bd63245eb0c131abd69d2afc7b8f17a71ccedceb542bf009e2'


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def identity(row):
    return row['source_id'], row['strength'], row['seed']


def summarize(rows):
    result = {'cells': {}, 'planned_image_attempts': 216, 'recorded_rows': len(rows),
              'scope': 'Exact public 32-bit recovery and mask diagnostics; no population FPR or binding superiority'}
    for arm in (*ARMS, 'shared_C0'):
        for strength in STRENGTHS:
            cell = [r for r in rows if r['arm'] == arm and r['strength'] == strength]
            good = [r for r in cell if r['status'] == 'ok']
            readable = [r for r in good if r['detection']['bit_accuracy'] is not None]
            result['cells'][f'{arm}/{strength}'] = {
                'planned': 36, 'completed': len(good),
                'blocked': sum(r['status'] == 'safety_blocked' for r in cell),
                'failed': sum(r['status'] == 'failed' for r in cell),
                'budget_unattempted': sum(r['status'] == 'budget_unattempted' for r in cell),
                'missing': 36 - len(cell),
                'exact_recovery': sum(r['detection']['exact_message_match'] for r in good),
                'exact_recovery_rate_all_planned': sum(r['detection']['exact_message_match'] for r in good) / 36,
                'bit_accuracy_mean_all_planned_zero_scored': sum(r['detection']['bit_accuracy'] or 0 for r in good) / 36,
                'bit_accuracy_mean_nonempty': sum(r['detection']['bit_accuracy'] for r in readable) / len(readable) if readable else None,
                'empty_masks_completed': len(good) - len(readable),
                'wrong_complement_exact_diagnostic': sum(r['detection']['wrong_message_exact_match'] for r in good),
                'negative_interpretation': 'Shared C0 source-ID message diagnostic' if arm == 'shared_C0' else 'Complement of expected public message; not wrong-owner cryptographic test'}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / 'images').mkdir()
    record = dict(schema='journal-wam-t3-v1', commit=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=sys.argv,
        data_split='development', usd=0, seeds=list(SEEDS), strengths=list(STRENGTHS),
        frozen_wam_run=str(WAM_RUN), frozen_c0_run=str(F5_RUN), outcome='running',
        config=dict(arms=ARMS, official_revision=REVISION, checkpoint_sha256=CHECKPOINT_SHA,
            payload_bits=32, message_schedule='journal-wam-dev-v1 source-ID SHA256 first32 MSB',
            native_decoder='semihard/default', mask_threshold=.5, cap_seconds=CAP,
            attack='official local SD1.5 half DDIM20; empty both prompts; CFG1; eta0; safety unchanged',
            human_admissibility='missing', quality='descriptive only; no row filtering'),
        duration_seconds=None)
    keys = [(sid, s, seed) for sid in IDS for s in STRENGTHS for seed in SEEDS]
    rows = []
    plan = [(arm, k) for arm in (*ARMS, 'shared_C0') for k in keys]
    record['sources'] = list(IDS)
    write(args.output_dir / 'run.json', record)

    def emit(row):
        rows.append(row)
        with (args.output_dir / 'rows.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(row, allow_nan=False) + '\n')
        print(json.dumps({k: row[k] for k in ('arm', 'source_id', 'strength', 'seed', 'status')}), flush=True)

    try:
        sys.path[:0] = [str(MAIN / '.thesis-build/journal-wam-deps'), str(ASSET / 'source')]
        import numpy as np
        from PIL import Image
        import torch
        from f4_transfer_probe import SOURCES, ASSETS
        from m1_latent_reconstruction import quality
        import three_threat_models as models
        ids = sorted(SOURCES)
        if ids != list(IDS):
            raise ValueError('Expected fixed twelve development sources')
        checkpoint = ASSET / 'wam_mit.pth'
        prior = json.loads((WAM_RUN / 'run.json').read_text(encoding='utf-8'))
        if (prior.get('outcome') != 'completed' or prior.get('sources') != ids or
                prior.get('config', {}).get('arms') != ARMS or
                prior['config'].get('official_revision') != REVISION or
                prior['config'].get('checkpoint_sha256') != CHECKPOINT_SHA or sha(checkpoint) != CHECKPOINT_SHA):
            raise ValueError('Frozen WAM run/checkpoint/configuration differs')
        clean_rows = [r for r in read_rows(WAM_RUN / 'rows.jsonl') if r.get('control') == 'C1' and r.get('condition') == 'clean']
        marks = {(r['arm'], r['source_id']): r for r in clean_rows}
        if len(clean_rows) != 24 or set(marks) != {(a, sid) for a in ARMS for sid in ids}:
            raise ValueError('Frozen clean WAM inventory differs')
        def load(path):
            with Image.open(path) as image:
                if image.mode != 'RGB' or image.size != (512, 512):
                    raise ValueError('Frozen RGB512 geometry differs')
                return np.asarray(image, np.uint8).copy()
        sources = {sid: load(SOURCES[sid]) for sid in ids}
        for (arm, sid), r in marks.items():
            expected = WAM_RUN / 'images' / f'{sid}-{arm}-C1-clean.png'
            if r['status'] != 'ok' or r['message'] != message(sid) or Path(r['image']).resolve() != expected.resolve():
                raise ValueError('Frozen WAM clean path/message/status differs')
            load(expected)
        controls = [r for r in read_rows(F5_RUN / 'rows.jsonl') if r.get('control') == 'C0' and r.get('dose') == 'diffusion' and r.get('strength') in STRENGTHS]
        c0 = {identity(r): r for r in controls}
        if len(controls) != 72 or set(c0) != set(keys):
            raise ValueError('Frozen C0 identity grid differs')
        for s in STRENGTHS:
            group = [r for r in controls if r['strength'] == s]
            if sum(r['outcome'] == 'completed' for r in group) != 33 or sum(r['outcome'] == 'safety_blocked' for r in group) != 3:
                raise ValueError('Expected 33 completed plus three genuine C0 blocks per strength')
        for sid in ids:
            if not np.array_equal(sources[sid], load(F5_RUN / 'images' / f'clean-{sid}-C0.png')):
                raise ValueError('Frozen C0 input differs from canonical development source')
        torch.set_num_threads(4)
        torch.cuda.reset_peak_memory_stats()
        adapter = Adapter(ASSET / 'source', checkpoint, 'cuda')
        lpips = models.load_lpips(ASSETS, Path(importlib.metadata.distribution('lpips').locate_file('lpips')))
        pipe = models.load_regenerator(ASSETS)
        record['environment'] = {n: importlib.metadata.version(n) for n in ('torch', 'diffusers', 'numpy', 'lpips', 'omegaconf')}
        record['native_params'] = adapter.params
        write(args.output_dir / 'run.json', record)
        for arm, k in plan:
            tick = time.monotonic()
            sid, strength, seed = k
            row = dict(arm=arm, control='C0' if arm == 'shared_C0' else 'C1',
                source_id=sid, strength=strength, seed=seed, message=message(sid))
            try:
                if arm == 'shared_C0' and c0[k]['outcome'] == 'safety_blocked':
                    row.update(status='safety_blocked', error=c0[k].get('error'),
                        source_record=str(F5_RUN / 'rows.jsonl'), reuse_interpretation='Retained block; no retry/replacement')
                elif time.monotonic() - started >= CAP:
                    row.update(status='budget_unattempted', error='Fixed 900-second all-in cap exhausted')
                else:
                    path = args.output_dir / 'images' / f'{sid}-{arm}-s{strength}-seed{seed}.png'
                    row['image'] = str(path)
                    if arm == 'shared_C0':
                        old = c0[k]
                        rgb = load(old['image']['path'])
                        Image.fromarray(rgb).save(path)
                        marked = sources[sid]
                        row.update(source_record=str(F5_RUN / 'rows.jsonl'), retained_image=old['image']['path'],
                            reuse_interpretation='Same frozen C0 pixels; fresh WAM decode; shared control, not replicate')
                    else:
                        input_path = marks[arm, sid]['image']
                        marked = load(input_path)
                        row['input_path'] = input_path
                        with torch.inference_mode():
                            result = pipe(prompt='', negative_prompt='', image=Image.fromarray(marked),
                                strength=strength, num_inference_steps=20, eta=0., guidance_scale=1.,
                                generator=torch.Generator(device='cuda').manual_seed(seed),
                                num_images_per_prompt=1, output_type='pil', return_dict=True)
                        # Preserve any returned PNG even when the unchanged checker blocks it.
                        if len(result.images) == 1 and result.images[0].mode == 'RGB':
                            result.images[0].save(path)
                        rgb = np.asarray(models.validate_generated(result), np.uint8)
                        Image.fromarray(rgb).save(path)
                    rgb = load(path)
                    row['detection'] = adapter.detect(rgb, message(sid))
                    def metrics(reference):
                        return {**quality(reference, rgb), 'lpips': models.lpips_score(lpips, reference, rgb)}
                    row.update(status='ok', quality_source=metrics(sources[sid]), quality_input=metrics(marked),
                        quality_interpretation='Descriptive only; no attack-quality filtering', human_admissibility_verdict=None)
            except Exception as error:
                row.update(status='safety_blocked' if 'safety_checker_blocked_output' in str(error) else 'failed', error=traceback.format_exc())
                torch.cuda.empty_cache()
            row['duration_seconds'] = time.monotonic() - tick
            emit(row)
        record['outcome'] = ('budget_exhausted' if any(r['status'] == 'budget_unattempted' for r in rows) else
            'completed' if all(r['status'] in ('ok', 'safety_blocked') for r in rows) else 'completed_with_failures')
        record['peak_cuda_allocated_bytes'] = torch.cuda.max_memory_allocated()
    except Exception:
        record.update(outcome='failed', error=traceback.format_exc())
        for arm, (sid, s, seed) in plan[len(rows):]:
            emit(dict(arm=arm, source_id=sid, strength=s, seed=seed, status='failed',
                message=message(sid), error='Fatal/setup failure; see run.json', duration_seconds=0.))
        raise
    finally:
        record['summary'] = summarize(rows)
        write(args.output_dir / 'summary.json', record['summary'])
        record['duration_seconds'] = time.monotonic() - started
        record['budget_overrun'] = record['duration_seconds'] > CAP
        write(args.output_dir / 'run.json', record)


if __name__ == '__main__':
    main()
