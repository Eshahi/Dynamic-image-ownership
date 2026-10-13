"""Conditional paired retained-artifact development probe; no writer or tuning.

All identities are allocated before model loading. Safety/missing calls remain
visible; identical I/E observations alias explicitly and are not replication.
"""
from __future__ import annotations
import time
STARTED = time.monotonic()
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
OWNERS = ('qim-pilot-owner-alpha', 'qim-pilot-owner-beta')
ALPHA, BETA = OWNERS
GPU_CAP, RAM_CAP = 9 * 1024**3, 16 * 1024**3


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    # Atomic replacement of this new study's own files, never retained data.
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    tmp.replace(path)


def available_ram():
    """Live Windows physical headroom, separate from the process RSS cap."""
    import ctypes
    class MemoryStatus(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
            (name, ctypes.c_ulonglong) for name in ('total_physical', 'available_physical',
            'total_page', 'available_page', 'total_virtual', 'available_virtual', 'extended')]
    memory = MemoryStatus(); memory.length = ctypes.sizeof(memory)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        raise ctypes.WinError()
    return int(memory.available_physical)


def summarize(rows):
    """Fixed-denominator descriptive counts, including adverse missingness."""
    indexed = {(r['source_id'], r['arm'], r['strength'], r['seed']): r for r in rows}
    def endpoint_value(sid, arm, strength, seed, metric):
        row = indexed[(sid, arm, strength, seed)]
        return row.get('endpoints', {}).get(ALPHA, {}).get(metric) if row['status'] == 'ok' else None
    clean = {}
    for arm in ('I', 'E'):
        entries = [indexed[(sid, arm, None, None)] for sid in IDS]
        clean[arm] = dict(observed=sum(r['status'] == 'ok' for r in entries),
            strict_quality=sum(r.get('strict_quality') is True for r in entries),
            exact={m: sum(endpoint_value(sid, arm, None, None, m) is True for sid in IDS)
                   for m in ('Q', 'H', 'F')},
            eligible_ids=[sid for sid, r in zip(IDS, entries) if r.get('clean_eligible') is True],
            metrics_by_source={str(r['source_id']): r.get('quality_source') for r in entries})
    strengths = {}
    for strength in (.1, .2):
        arms = {}
        for arm in ('I', 'E'):
            per_source = {}
            for sid in IDS:
                value = {}
                for metric in ('S', 'Q', 'J', 'H', 'F'):
                    vals = [endpoint_value(sid, arm, strength, seed, metric) for seed in (6, 7, 8)]
                    yes, missing = sum(v is True for v in vals), sum(v is None for v in vals)
                    value[metric] = dict(successes=yes, unavailable=missing, mean_operational=yes / 3,
                        majority_lower=yes >= 2, majority_upper=yes + missing >= 2)
                value['clean_eligible'] = sid in clean[arm]['eligible_ids']
                per_source[str(sid)] = value
            observed_eps = [indexed[(sid, arm, strength, seed)].get('endpoints', {}).get(ALPHA)
                            for sid in IDS for seed in (6, 7, 8)]
            observed_eps = [e for e in observed_eps if e is not None]
            arms[arm] = dict(per_source=per_source,
                majority={m: sum(v[m]['majority_lower'] for v in per_source.values()) for m in ('S', 'Q', 'J', 'H', 'F')},
                seed_successes={m: sum(v[m]['successes'] for v in per_source.values()) for m in ('S', 'Q', 'J', 'H', 'F')},
                joint_clean_majority_J=sum(v['clean_eligible'] and v['J']['majority_lower'] for v in per_source.values()),
                histograms={key: dict(Counter(str(e[key]) for e in observed_eps))
                            for key in ('raw_coded_bit_errors', 'q_bit_errors', 'h_bit_errors', 'bch_reason')})
        paired = Counter()
        lower, upper = 0, 0
        for sid in IDS:
            i, e = (arms[a]['per_source'][str(sid)]['J'] for a in ('I', 'E'))
            paired['both' if i['majority_lower'] and e['majority_lower'] else
                   'E_only' if e['majority_lower'] else 'I_only' if i['majority_lower'] else 'neither'] += 1
            lower += int(e['majority_lower']) - int(i['majority_upper'])
            upper += int(e['majority_upper']) - int(i['majority_lower'])
        strengths[str(strength)] = dict(arms=arms, paired_J=dict(paired),
            E_minus_I_majority_J=arms['E']['majority']['J'] - arms['I']['majority']['J'],
            E_minus_I_J_source_count_interval=[lower, upper], denominator=12)
    negatives = {}
    for phase in ('clean', 'T3'):
        for arm, owner in (('C0', ALPHA), ('C0', BETA), ('I', BETA), ('E', BETA)):
            selected = [r for r in rows if r['phase'] == phase and r['arm'] == arm]
            events = [r for r in selected if r.get('endpoints', {}).get(owner, {}).get('A') is True]
            unavailable = [r for r in selected if owner not in r.get('endpoints', {})]
            source_events = sorted({r['source_id'] for r in events})
            unresolved = sorted({r['source_id'] for r in unavailable} - set(source_events))
            negatives[f'{phase}:{arm}:{owner}'] = dict(planned_calls=len(selected), observed_calls=len(selected)-len(unavailable),
                events=len(events), unavailable_calls=len(unavailable), event_source_ids=source_events,
                unresolved_source_ids=unresolved, source_event_rate_bracket=[len(source_events)/12, (len(source_events)+len(unresolved))/12])
    return dict(planned_rows=252, recorded_rows=len(rows), statuses=dict(Counter(r['status'] for r in rows)),
        complete=all(r['status'] in ('ok', 'safety_blocked') for r in rows),
        actual_transformation_attempts=sum(r.get('transformation_attempted', False) for r in rows),
        aliases=sum(bool(r.get('alias_of')) for r in rows), clean=clean, strengths=strengths,
        common_clean_eligible_ids=sorted(set(clean['I']['eligible_ids']) & set(clean['E']['eligible_ids'])),
        negatives=negatives, interpretation='Exploratory fixed seen-source screen; missing positive calls count unsuccessful operationally. No population FPR or confirmatory significance claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--census', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--deadline-utc', default='2026-10-13T13:32:00+00:00')
    args = parser.parse_args()
    census_path = args.census / 'run.json' if args.census.is_dir() else args.census
    census = read(census_path)
    if census.get('outcome') != 'completed' or census.get('data_split') != 'development':
        raise ValueError('Completed development census required before any inference')
    sources = census['rows']
    if tuple(r['source_id'] for r in sources) != IDS:
        raise ValueError('Exact twelve-source census required')
    if not any(r['identical_pixels'] is False for r in sources):
        raise ValueError('All retained I/E pairs identical: protocol prohibits new inference')
    deadline = datetime.fromisoformat(args.deadline_utc)
    if deadline.tzinfo is None:
        raise ValueError('Deadline must include UTC offset')
    end_unix = min(deadline.timestamp(), float(census['started_unix']) + 2700)
    source_map = {r['source_id']: r for r in sources}
    rows = []
    for sid in IDS:
        for strength, seed in [(None, None)] + [(s, n) for s in (.1, .2) for n in (6, 7, 8)]:
            for arm in ('C0', 'I', 'E'):
                row = dict(id=f'{sid}:{strength}:{seed}:{arm}', source_id=sid, arm=arm,
                    phase='clean' if strength is None else 'T3', condition='clean' if strength is None else 't3', strength=strength, seed=seed,
                    payload=source_map[sid]['payload'], status='not_started', calls={}, endpoints={})
                if arm == 'E' and source_map[sid]['identical_pixels']:
                    row['alias_of'] = f'{sid}:{strength}:{seed}:I'
                    row['reuse_of'] = row['alias_of']
                rows.append(row)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / 'images').mkdir()
    write(out / 'source-census.json', census)
    record = dict(schema='post-m2-refinement-probe-v1', outcome='running', command=sys.argv,
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        data_split='development', usd=0, census=str(census_path.resolve()),
        started_at_utc=datetime.now(timezone.utc).isoformat(), inclusive_started_unix=census['started_unix'],
        deadline_utc=datetime.fromtimestamp(end_unix, timezone.utc).isoformat(),
        config=dict(sources=list(IDS), seeds=[6, 7, 8], strengths=[.1, .2], steps=20,
            scheduler='DDIM', prompt='', negative_prompt='', guidance_scale=1., eta=0.,
            dtype='float16', safety_checker=True, binding='soft', binding_mode='combined', roster_size=1,
            semantic_views=7, gpu_cap_bytes=GPU_CAP, ram_cap_bytes=RAM_CAP,
            protocol='research/journal-upgrade-20261009/post-m2-fair-comparison-protocol.md'))
    ev = None
    def save():
        record['duration_seconds'] = time.monotonic() - STARTED
        record['inclusive_duration_seconds'] = time.time() - census['started_unix']
        record['budget_overrun'] = time.time() > end_unix
        if record['budget_overrun'] and record['outcome'] == 'completed':
            record.update(outcome='incomplete', error='Inclusive deadline exceeded during finalization')
        record['summary'] = summarize(rows)
        write(out / 'rows.json', rows)
        (out / 'rows.jsonl').write_text(''.join(json.dumps(r, allow_nan=False)+'\n' for r in rows), encoding='utf-8')
        write(out / 'run.json', record)
        write(out / 'summary.json', record['summary'])
    def budget():
        if time.time() >= end_unix:
            raise RuntimeError('Inclusive study deadline reached')
        rss, peak = working_set()
        record['peak_ram_bytes'] = max(rss, peak, record.get('peak_ram_bytes', 0))
        if ev is not None:
            record['peak_allocated_bytes'] = int(ev.torch.cuda.max_memory_allocated())
        if record['peak_ram_bytes'] > RAM_CAP or record.get('peak_allocated_bytes', 0) > GPU_CAP:
            raise RuntimeError('Study resource cap exceeded')
        if os.name == 'nt' and available_ram() < 1024**3:
            raise RuntimeError('Less than 1 GiB live RAM headroom')
    save()
    try:
        from journal_e3_threat_supplement import working_set
        budget()
        import numpy as np
        import torch
        import diffusers
        from PIL import Image
        import three_threat_models as models
        from journal_bch_readout import detect_rgb
        from journal_bch_analysis import endpoint
        from journal_e3_writer import strict_quality
        from f4_transfer_probe import ASSETS
        from journal_vae_probe import Evaluator
        budget()
        if diffusers.__version__ != '0.35.1':
            raise ValueError('Pinned diffusers 0.35.1 required')
        models.block_network()
        free, total = torch.cuda.mem_get_info()
        if free < GPU_CAP:
            raise RuntimeError('Less than 9 GiB CUDA free headroom before loading')
        # Windows available physical memory, before loading pinned assets.
        if os.name == 'nt':
            record['available_ram_before_loading'] = available_ram()
            if record['available_ram_before_loading'] < 8 * 1024**3:
                raise RuntimeError('Less than 8 GiB RAM headroom before loading')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP / total)
        record['environment'] = dict(torch=torch.__version__, diffusers=diffusers.__version__,
            gpu=torch.cuda.get_device_name(0), assets=str(ASSETS), free_gpu_before_loading=free)
        ev = Evaluator(); budget()
        historical = read(Path(census['config']['source_run']) / 'run.json')
        if ev.profile != historical['config']['profile']:
            raise ValueError('Reader profile differs from retained source run')
        record['config']['profile'] = ev.profile
        pipe = models.load_regenerator(ASSETS); budget()
        if pipe.safety_checker is None or pipe.feature_extractor is None:
            raise RuntimeError('Required safety components missing')
        def load(path):
            with Image.open(path) as image:
                if image.mode != 'RGB' or image.size != (512, 512):
                    raise ValueError('RGB8 512x512 required')
                return np.asarray(image, dtype=np.uint8).copy()
        indexed = {r['id']: r for r in rows}
        for row in rows:
            budget()
            tick = time.monotonic()
            row['status'] = 'running'; save()
            try:
                if row.get('alias_of'):
                    original = indexed[row['alias_of']]
                    if original['status'] not in ('ok', 'safety_blocked'):
                        raise RuntimeError('Alias authority not finished')
                    for field in ('calls', 'endpoints', 'quality_source', 'quality_input', 'quality_marked', 'quality_attacked_C0',
                                  'strict_quality', 'clean_eligible', 'image', 'raw_output_image', 'safety_flags', 'timesteps'):
                        if field in original:
                            row[field] = copy.deepcopy(original[field])
                    row['status'] = original['status']
                    row['input_image'] = str(source_map[row['source_id']]['final'])
                    row['reuse_scope'] = 'Exact RGB8 I/E identity; shared observation, zero paired effect'
                    continue
                source = source_map[row['source_id']]
                input_path = source[{'C0': 'source_image', 'I': 'initializer', 'E': 'final'}[row['arm']]]
                row['input_image'] = str(input_path)
                unmarked, rgb_input = load(source['source_image']), load(input_path)
                if row['phase'] == 'T3':
                    budget(); row['transformation_attempted'] = True; save()
                    kwargs = dict(prompt='', negative_prompt='', image=Image.fromarray(rgb_input),
                        strength=row['strength'], num_inference_steps=20, eta=0., guidance_scale=1.,
                        generator=torch.Generator(device='cuda').manual_seed(row['seed']),
                        num_images_per_prompt=1, output_type='pil', return_dict=True)
                    with torch.inference_mode():
                        output = pipe(**kwargs)
                    row['safety_flags'] = list(output.nsfw_content_detected) if output.nsfw_content_detected is not None else None
                    timesteps, _ = pipe.get_timesteps(20, row['strength'], pipe._execution_device)
                    row['timesteps'] = timesteps.cpu().tolist()
                    raw = out / 'images' / (row['id'].replace(':', '-') + '.png')
                    output.images[0].save(raw); row['raw_output_image'] = str(raw); save()
                    if len(row['timesteps']) != int(20 * row['strength']):
                        raise ValueError('Effective timestep count differs')
                    image = models.validate_generated(output)
                    rgb = np.asarray(image, dtype=np.uint8).copy(); row['image'] = str(raw)
                else:
                    rgb = rgb_input; row['image'] = str(input_path)
                budget()
                features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
                for owner in OWNERS:
                    budget()
                    call = detect_rgb(rgb, latent, owner, ev.profile, features,
                        binding='soft', binding_mode='combined', roster_size=1)
                    row['calls'][owner] = call
                    row['endpoints'][owner] = endpoint(call, row['payload'] if row['arm'] in ('I', 'E') and owner == ALPHA else None)
                    save()
                budget(); row['quality_source'] = ev.metrics(unmarked, rgb)
                budget(); row['quality_input'] = ev.metrics(rgb_input, rgb)
                row['quality_marked'] = row['quality_input']
                if row['phase'] == 'clean':
                    row['strict_quality'] = strict_quality(row['quality_source'])
                    positive = row['endpoints'][ALPHA]
                    row['clean_eligible'] = bool(row['strict_quality'] and all(positive[m] for m in ('Q', 'H', 'F')))
                elif row['arm'] != 'C0':
                    control = indexed[f"{row['source_id']}:{row['strength']}:{row['seed']}:C0"]
                    if control['status'] == 'ok':
                        budget(); row['quality_attacked_C0'] = ev.metrics(load(control['image']), rgb)
                budget(); row['status'] = 'ok'
            except Exception as exc:
                row['error'] = f'{type(exc).__name__}: {exc}'
                if isinstance(exc, RuntimeError) and str(exc) == 'safety_checker_blocked_output' and row.get('safety_flags') == [True] and not row['calls']:
                    row['status'] = 'safety_blocked'
                else:
                    row['status'] = 'failed'; raise
            finally:
                row['duration_seconds'] = time.monotonic() - tick; save()
            print(json.dumps(dict(id=row['id'], status=row['status'])), flush=True)
        budget(); record['outcome'] = 'completed'
    except Exception as exc:
        record.update(outcome='incomplete', error=f'{type(exc).__name__}: {exc}', traceback=traceback.format_exc())
    finally:
        save()
    if record['outcome'] != 'completed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
