"""One resumable, development-only three-method regenerator transfer experiment."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
PARENT = MAIN / '.thesis-build/dev-runs/20261013-1636-fresh-e3-simplification'
SD21 = MAIN / '.thesis-build/assets/registry-sd21-4e63672c'
METHODS = ('e3-s1', 'f5-r2', 'v5-r3')
ALPHA, BETA = ('qim-pilot-owner-' + v for v in ('alpha', 'beta'))
STRENGTHS, SEEDS = (.1, .2, .4), (12, 13, 14)
F5_PARAMS = dict(psnr_db=52., steps=150, target_margin=4., mask_power=0.,
                 band=[4, 32], whitening=1., refine_rounds=1, binding='soft', semantic_views=7)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    tmp.replace(path)


def journal(path):
    """Only complete newline-terminated events count; preserve interrupted tails."""
    latest = {}
    if path.exists():
        with path.open(encoding='utf-8') as handle:
            for line in handle:
                if not line.endswith('\n'):
                    break
                row = json.loads(line)
                latest[row['id']] = row
    return latest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('prepare', 'sd15', 'sd21'), required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--parent', type=Path, default=PARENT)
    parser.add_argument('--sd21-assets', type=Path, default=SD21)
    parser.add_argument('--max-seconds', type=float, default=5400.)
    args = parser.parse_args()
    if not 0 < args.max_seconds <= 5400:
        raise ValueError('Each phase has at most 5400 cumulative seconds')
    start = time.monotonic()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    parent = read(args.parent / 'run.json')
    sources = parent['sources']
    if parent['data_split'] != 'development' or len(sources) != 24 or len({s['source_id'] for s in sources}) != 24:
        raise ValueError('Exactly 24 reserved development sources required')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    config = dict(parent=str(args.parent.resolve()), parent_commit=parent['commit'], methods=list(METHODS),
                  strengths=list(STRENGTHS), seeds=list(SEEDS), steps=20, prompt='', negative_prompt='',
                  guidance_scale=1., eta=0., precision='float16', owners=[ALPHA, BETA],
                  sd21_assets=str(args.sd21_assets.resolve()), sd21_revision='4e63672c03103b6c636b8fb4119ba982469b2955',
                  f5=F5_PARAMS, detector_side_information='owner, public profile and pinned VAE/CLIP; no reference image',
                  clean_quality_matching=False, human_admissibility='missing', total_cap_seconds=18000)
    if (out / 'run.json').exists():
        record = read(out / 'run.json')
        if record['commit'] != commit or record['config'] != config:
            raise ValueError('Resume requires identical code commit and configuration')
    else:
        record = dict(schema='registry-step1-transfer-v1', commit=commit, command=sys.argv,
                      data_split='development', usd=0, outcome='running', config=config,
                      sources=[dict(source_id=s['source_id'], canonical_path=s['canonical_path']) for s in sources],
                      phase_seconds={}, invocations=[], phase_status={})
    previous = record['phase_seconds'].get(args.phase, 0.)
    prior_total = sum(record['phase_seconds'].values())
    invocation = dict(phase=args.phase, command=sys.argv, commit=commit, status='running')
    record['invocations'].append(invocation)
    log = out / 'rows.jsonl'
    # Never append after a torn line: retain the original bytes as an error artifact.
    if log.exists() and log.stat().st_size and not log.read_bytes().endswith(b'\n'):
        raw = log.read_bytes()
        tail = out / ('interrupted-journal-' + str(time.time_ns()) + '.bin')
        tail.write_bytes(raw[raw.rfind(b'\n') + 1:])
        log.write_bytes(raw[:raw.rfind(b'\n') + 1])
    rows = journal(log)
    ev = None

    def save():
        duration = time.monotonic() - start
        record['phase_seconds'][args.phase] = previous + duration
        record['duration_seconds'] = prior_total + duration
        invocation['duration_seconds'] = duration
        write(out / 'run.json', record)

    def budget():
        if previous + time.monotonic() - start >= args.max_seconds or prior_total + time.monotonic() - start >= 18000:
            raise RuntimeError('Cumulative step or phase time cap reached')

    def emit(row):
        with log.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(row, allow_nan=False) + '\n')
            handle.flush()
        rows[row['id']] = copy.deepcopy(row)
        save()

    def attempt(rid, **fields):
        old = rows.get(rid)
        attempt_number = (old or {}).get('attempt', 0) + 1
        row = dict(id=rid, attempt=attempt_number, status='running', **fields)
        emit(row)
        return row

    def done(rid):
        return rows.get(rid, {}).get('status') in ('ok', 'safety_blocked')

    save()
    try:
        budget()
        import numpy as np
        import torch
        import diffusers
        from PIL import Image
        from journal_vae_probe import Evaluator
        from journal_bch_readout import detect_rgb as e3_detect
        from m1b_e3_s1_analysis import predicates, strict_quality
        from scripts import revised_watermark_v5 as v5
        import three_threat_models as models
        from f4_transfer_probe import ASSETS
        torch.set_num_threads(4)
        models.block_network()
        ev = Evaluator()
        if ev.profile != parent['config']['profile']:
            raise ValueError('Retained mark profile differs')
        record['environment'] = dict(torch=torch.__version__, diffusers=diffusers.__version__, gpu=torch.cuda.get_device_name(0))

        def load(path):
            with Image.open(path) as image:
                if image.mode != 'RGB' or image.size != (512, 512):
                    raise ValueError('RGB8 512 square required')
                return np.asarray(image, dtype=np.uint8).copy()

        def calls(rgb, method, payload, control):
            features = ev.features(rgb, 1 if method == 'v5-r3' else 7)
            latent = ev.reader.latent(rgb) if method != 'v5-r3' else None
            results, endpoints, timings = {}, {}, {}
            for owner in ((ALPHA, BETA) if control == 'C1' else (ALPHA,)):
                budget()
                tick = time.monotonic()
                call = (e3_detect(rgb, latent, owner, ev.profile, features, binding='soft', roster_size=1)
                        if method == 'e3-s1' else ev.detect(rgb, 'f5' if method == 'f5-r2' else 'v5', owner, features, latent))
                results[owner] = call
                endpoints[owner] = predicates(call, payload if control == 'C1' and owner == ALPHA else None)
                timings[owner] = time.monotonic() - tick
            return dict(calls=results, endpoints=endpoints, detector_seconds=timings)

        if args.phase == 'prepare':
            frozen = read(MAIN / '.thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7/run.json')
            if frozen['params'] != F5_PARAMS or frozen['profile'] != ev.profile:
                raise ValueError('Frozen F5 r2 settings/profile differ')
            for source in sources:
                sid = source['source_id']
                canonical = load(source['canonical_path'])
                for method in METHODS:
                    rid = f'clean:{sid}:{method}:C1'
                    if done(rid):
                        continue
                    budget()
                    row = attempt(rid, phase='prepare', source_id=sid, method=method, control='C1')
                    tick = time.monotonic()
                    try:
                        if method == 'e3-s1':
                            image, payload = source['full_image'], source['payload']
                            embed_seconds = source['timing']['full_supplier_writer_seconds']
                            row['embedding_time_basis'] = 'retained measured supplier plus full writer wall time'
                        elif method == 'f5-r2':
                            supplier = source['supplier']
                            report = supplier['report']
                            expected = dict(family='f5-encoder-amplified-latent', revision=2, psnr_target_db=52., steps=150,
                                            target_margin=4., mask_power=0., band=[4,32], whitening=1., refine_rounds=1)
                            if supplier['status'] != 'ok' or any(report.get(k) != v for k,v in expected.items()):
                                raise ValueError('Retained supplier does not match frozen F5 r2')
                            image, payload = supplier['bootstrap_image'], supplier['payload']
                            embed_seconds = supplier['bootstrap_seconds']
                            row.update(embedding_time_basis='retained F5 constructor and saved-image wall time',
                                       payload_basis='intended native q; operational native-decoded h (original h not exported)',
                                       supplier_settings_verified=expected)
                        else:
                            embedding_tick = time.monotonic()
                            rgb, report = v5.embed_rgb(canonical.tolist(), ALPHA, profile=ev.profile,
                                                     semantic_features=ev.features(canonical, 1), strict=False)
                            embed_seconds = time.monotonic() - embedding_tick
                            image = str(out / f'{sid}-v5-attempt{row["attempt"]}.png')
                            Image.fromarray(np.asarray(rgb, np.uint8)).save(image)
                            payload = dict(q=report['semantic_code'], h=report['perceptual_hash'], h_target_basis='native intended h')
                            row.update(native_report=report, embedding_time_basis='fresh constructor including source CLIP feature extraction')
                        rgb = load(image)
                        row.update(image=str(image), payload=payload, embedding_seconds=embed_seconds,
                                   quality=ev.metrics(canonical, rgb), **calls(rgb, method, payload, 'C1'))
                        row['strict_quality'] = bool(strict_quality(row['quality']))
                        row['status'] = 'ok'
                    except Exception:
                        row.update(status='error', error=traceback.format_exc())
                        raise
                    finally:
                        row['duration_seconds'] = time.monotonic() - tick
                        emit(row)
                for method in METHODS:
                    rid = f'clean:{sid}:{method}:C0'
                    if not done(rid):
                        row = attempt(rid, phase='prepare', source_id=sid, method=method, control='C0', image=source['canonical_path'])
                        row.update(**calls(canonical, method, None, 'C0'), status='ok')
                        emit(row)
        else:
            if not all(done(f'clean:{s["source_id"]}:{m}:C1') for s in sources for m in METHODS):
                raise ValueError('Finish prepare before regeneration')
            if args.phase == 'sd15':
                pipe = models.load_regenerator(ASSETS)
            else:
                from diffusers import AutoencoderKL, DDIMScheduler, StableDiffusionImg2ImgPipeline
                # The downloaded snapshot may have fp16 variants or native filenames.
                variant = 'fp16' if (args.sd21_assets / 'unet/diffusion_pytorch_model.fp16.safetensors').exists() else None
                vae = AutoencoderKL.from_pretrained(args.sd21_assets / 'vae', local_files_only=True,
                                                   torch_dtype=torch.float16, use_safetensors=True)
                pipe = StableDiffusionImg2ImgPipeline.from_pretrained(args.sd21_assets, variant=variant,
                    vae=vae,
                    local_files_only=True, torch_dtype=torch.float16, use_safetensors=True,
                    safety_checker=None, requires_safety_checker=False)
                pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
                pipe.set_progress_bar_config(disable=True)
                pipe.to('cuda')
                # Compare every VAE state tensor, without allocating a second fp32 VAE.
                baseline = ev.reader.vae.state_dict()
                current = pipe.vae.state_dict()
                equal = set(current) == set(baseline) and all(
                    v.shape == baseline[k].shape and torch.equal(v.detach().cpu(), baseline[k].detach().cpu().to(v.dtype))
                    for k,v in current.items())
                record['sd21_vae_comparison'] = dict(equal_after_cast_to_regenerator_dtype=equal,
                    meaning='full state comparison at fp16 precision; equality can expose shared weights, inequality does not prove unrelated ancestry')
            record.setdefault('regenerators', {})[args.phase] = dict(safety_checker=pipe.safety_checker is not None,
                scheduler=dict(pipe.scheduler.config), assets=str(ASSETS / 'sd15-fp16' if args.phase == 'sd15' else args.sd21_assets))
            save()
            for source in sources:
                sid = source['source_id']
                for strength in STRENGTHS:
                    for seed in SEEDS:
                        for arm in ('C0',) + METHODS:
                            rid = f'{args.phase}:{sid}:{strength}:{seed}:{arm}'
                            if done(rid):
                                continue
                            budget()
                            row = attempt(rid, phase=args.phase, source_id=sid, strength=strength, seed=seed, arm=arm)
                            tick = time.monotonic()
                            try:
                                input_path = source['canonical_path'] if arm == 'C0' else rows[f'clean:{sid}:{arm}:C1']['image']
                                row['input_image'] = input_path
                                inp = load(input_path)
                                row['transformation_attempted'] = True
                                emit(row)
                                regen_tick = time.monotonic()
                                with torch.inference_mode():
                                    result = pipe(prompt='', negative_prompt='', image=Image.fromarray(inp), strength=strength,
                                        num_inference_steps=20, eta=0., guidance_scale=1.,
                                        generator=torch.Generator(device='cuda').manual_seed(seed), num_images_per_prompt=1,
                                        output_type='pil', return_dict=True)
                                torch.cuda.synchronize()
                                row['regeneration_seconds'] = time.monotonic() - regen_tick
                                row['safety_flags'] = result.nsfw_content_detected
                                image = out / (rid.replace(':', '-') + f'-attempt{row["attempt"]}.png')
                                result.images[0].save(image)
                                row['image'] = str(image)
                                if args.phase == 'sd15':
                                    models.validate_generated(result)
                                rgb = load(image)
                                row['readouts'] = {}
                                for method in (METHODS if arm == 'C0' else (arm,)):
                                    payload = None if arm == 'C0' else rows[f'clean:{sid}:{method}:C1']['payload']
                                    row['readouts'][method] = calls(rgb, method, payload, 'C0' if arm == 'C0' else 'C1')
                                    emit(row)
                                row.update(status='ok', quality_input=ev.metrics(inp, rgb))
                            except Exception as exc:
                                if str(exc) == 'safety_checker_blocked_output':
                                    row.update(status='safety_blocked', error=str(exc))
                                else:
                                    row.update(status='error', error=traceback.format_exc())
                                    raise
                            finally:
                                row['duration_seconds'] = time.monotonic() - tick
                                emit(row)
                            print(json.dumps(dict(id=rid, status=row['status'])), flush=True)
        budget()
        record['phase_status'][args.phase] = 'completed'
        record['outcome'] = 'completed' if all(record['phase_status'].get(p) == 'completed' for p in ('prepare','sd15','sd21')) else 'partial'
        invocation['status'] = 'completed'
    except Exception:
        record['phase_status'][args.phase] = 'incomplete'
        invocation.update(status='incomplete', error=traceback.format_exc())
        record['outcome'] = 'incomplete'
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
