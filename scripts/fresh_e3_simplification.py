"""Prospective fresh-development full E3 versus fixed initializer quality selector.

One scientific driver, with source-boundary checkpoints. No historical payload
lookup, threshold fitting, automatic attack launch, or scientific failure retry.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
ALPHA, BETA = 'qim-pilot-owner-alpha', 'qim-pilot-owner-beta'
GPU_CAP, RAM_CAP = 9 * 1024**3, 10 * 1024**3
PROTOCOL = ROOT / 'research/journal-upgrade-20261009/fresh-simplification-protocol.md'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def memory():
    """Live process RSS/peak and physical headroom, Windows or Linux."""
    if os.name == 'nt':
        from journal_e3_threat_supplement import working_set
        import ctypes
        class Status(ctypes.Structure):
            _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
                (name, ctypes.c_ulonglong) for name in ('total', 'available', 'tp', 'ap', 'tv', 'av', 'extended')]
        status = Status(); status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise ctypes.WinError()
        rss, peak = working_set()
        return rss, peak, int(status.available)
    values = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    available = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    return tuple(int(v.split()[0]) * 1024 for v in (values['VmRSS'], values['VmHWM'], available['MemAvailable']))


def summary(record):
    sources = record['sources']; n = len(sources)
    clean = {}
    for arm in ('full', 'lean'):
        rows = [s.get('clean', {}).get(arm, {}) for s in sources]
        clean[arm] = dict(denominator=n, observed=sum(r.get('status') == 'ok' for r in rows),
            strict_quality=sum(r.get('strict_quality') is True for r in rows),
            eligible=sum(r.get('clean_eligible') is True for r in rows),
            exact={m: sum(r.get('endpoints', {}).get(ALPHA, {}).get(m) is True for r in rows) for m in ('Q', 'H', 'F')})
    negatives = {}
    for arm, owner in (('C0', ALPHA), ('C0', BETA), ('full', BETA), ('lean', BETA)):
        calls = [s.get('clean', {}).get(arm, {}).get('endpoints', {}).get(owner) for s in sources]
        negatives[f'{arm}:{owner}'] = dict(planned=n, observed=sum(c is not None for c in calls),
            A=sum(c is not None and c['A'] for c in calls), unavailable=sum(c is None for c in calls))
    paired_times = [s['timing'] for s in sources if 'timing' in s]
    ratios = [s['lean_stage_sum_estimate_seconds'] / s['full_supplier_writer_seconds'] for s in paired_times]
    median = __import__('statistics').median
    return dict(denominator=n, statuses=dict(Counter(s['status'] for s in sources)), clean=clean,
        clean_negatives=negatives, timing=dict(observed=len(ratios), ratios=ratios,
            median_paired_ratio=median(ratios) if ratios else None,
            ratio_of_medians=median([s['lean_stage_sum_estimate_seconds'] for s in paired_times]) /
                median([s['full_supplier_writer_seconds'] for s in paired_times]) if ratios else None),
        attacks=dict(planned=27*n, recorded=len(record.get('attacks', [])),
            statuses=dict(Counter(r['status'] for r in record.get('attacks', [])))),
        interpretation='Exploratory fixed-denominator fresh development. Missing positives are unsuccessful; missing negatives unresolved. No population FPR claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--phase', choices=('construct', 'attack'), required=True)
    parser.add_argument('--max-seconds', type=float, required=True, help='Inclusive invocation cap from predeclared protocol')
    args = parser.parse_args()
    if args.phase == 'attack':
        raise ValueError('Construction-only driver: implement all protocol VAE/T3/T4/T5 controls before Stage B')
    if args.max_seconds <= 0 or args.max_seconds > 4500 or not PROTOCOL.exists():
        raise ValueError('Positive predeclared cap and frozen protocol required')
    supplied = read(args.sources)
    cohort = supplied if isinstance(supplied, list) else supplied['sources']
    if len(cohort) != 24 or len({s['source_id'] for s in cohort}) != 24:
        raise ValueError('Exactly 24 unique prospective development identities required')
    for source in cohort:
        source['canonical_path'] = str(Path(source['canonical_path']).resolve())
        if digest(source['canonical_path']) != source['sha256']:
            raise ValueError('Canonical input hash mismatch')
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    path = out / 'run.json'
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if path.exists():
        record = read(path)
        if record['input_cohort'] != cohort or record['commit'] != commit or record['protocol_sha256'] != digest(PROTOCOL):
            raise ValueError('Resume requires identical cohort, code commit and protocol')
        for source in record['sources'] + ([record['warmup']] if 'warmup' in record else []):
            if source['status'] == 'running':
                source.update(status='incomplete', error='Previous invocation interrupted; retained without scientific retry')
    else:
        if args.phase != 'construct':
            raise ValueError('Construction must precede attacks')
        record = dict(schema='fresh-e3-simplification-v1', commit=commit, command=sys.argv,
            input_cohort=cohort, sources=[dict(**s, status='not_started', clean={}) for s in cohort],
            data_split='development', usd=0, protocol=str(PROTOCOL), protocol_sha256=digest(PROTOCOL),
            started_at_utc=datetime.now(timezone.utc).isoformat(), outcome='running', duration_seconds=0.,
            attacks=[], invocations=[], config=dict(seeds=[6, 7, 8], strengths=[.1, .2, .4], steps=20,
                scheduler='DDIM', prompt='', negative_prompt='', guidance_scale=1., eta=0., safety_checker=True,
                semantic_views=7, cpu_threads=4, gpu_cap_bytes=GPU_CAP, ram_cap_bytes=RAM_CAP,
                lean_selector=[1., .8], selector_basis='strict quality only; one contraction; no payload choice',
                timing_basis='Shared supplier and full initializer computation. Lean standalone time is a stage-sum estimate, not independently measured.',
                human_admissibility='missing', binding='soft', binding_mode='combined', roster_size=1))
    started = time.monotonic(); prior_duration = record['duration_seconds']; ev = None
    invocation = dict(phase=args.phase, command=sys.argv, started_at_utc=datetime.now(timezone.utc).isoformat(),
        max_seconds=args.max_seconds, outcome='running')
    record['invocations'].append(invocation)
    def save():
        record['duration_seconds'] = prior_duration + time.monotonic()-started
        record['summary'] = summary(record)
        write(path, record); write(out / 'summary.json', record['summary'])
    def budget():
        rss, peak, available = memory()
        record['peak_ram_bytes'] = max(record.get('peak_ram_bytes', 0), rss, peak)
        allocated = int(ev.torch.cuda.max_memory_allocated()) if ev is not None else 0
        record['peak_gpu_allocated_bytes'] = max(record.get('peak_gpu_allocated_bytes', 0), allocated)
        if prior_duration + time.monotonic()-started >= args.max_seconds or rss > RAM_CAP or allocated > GPU_CAP or available < 3 * 1024**3:
            raise RuntimeError('Inclusive time, memory cap or live headroom reached')
    save()
    try:
        budget()
        import numpy as np
        import torch
        import diffusers
        from PIL import Image
        from diffusers import AutoencoderKL
        import three_threat_models as models
        from f4_transfer_probe import ASSETS, SOURCES
        from journal_vae_probe import Evaluator, SDXL
        from journal_ddim_channel import DifferentiableDDIM
        from journal_e3_writer import supply_f5, embed, strict_quality, contract
        from journal_bch_readout import detect_rgb
        from journal_bch_analysis import endpoint
        if diffusers.__version__ != '0.35.1':
            raise ValueError('Pinned diffusers 0.35.1 required')
        models.block_network()
        free, total = torch.cuda.mem_get_info()
        if free < GPU_CAP:
            raise RuntimeError('Less than 9 GiB free GPU before loading')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/total)
        loading = time.monotonic(); ev = Evaluator(); budget()
        pipe = models.load_regenerator(ASSETS); budget()
        other = channel = None
        if args.phase == 'construct':
            channel = DifferentiableDDIM(pipe)
            other = AutoencoderKL.from_pretrained(SDXL, local_files_only=True,
                use_safetensors=True, torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        invocation['model_loading_seconds'] = time.monotonic()-loading
        record['config']['profile'] = ev.profile
        record['environment'] = dict(torch=torch.__version__, diffusers=diffusers.__version__,
            gpu=torch.cuda.get_device_name(0), cpu_threads=torch.get_num_threads(), assets=str(ASSETS), sdxl=str(SDXL))
        def load(image_path):
            with Image.open(image_path) as image:
                if image.mode != 'RGB' or image.size != (512, 512):
                    raise ValueError('Canonical RGB8 512x512 required')
                return np.asarray(image, np.uint8).copy()
        def qualify(rgb, canonical, payload, genuine):
            budget(); tick = time.monotonic()
            features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
            row = dict(status='running', calls={}, endpoints={})
            beta_seconds = 0.
            for owner in (ALPHA, BETA):
                budget()
                call_tick = time.monotonic()
                call = detect_rgb(rgb, latent, owner, ev.profile, features,
                    binding='soft', binding_mode='combined', roster_size=1)
                if owner == BETA:
                    beta_seconds = time.monotonic()-call_tick
                row['calls'][owner] = call
                row['endpoints'][owner] = endpoint(call, payload if genuine and owner == ALPHA else None)
            budget(); row['quality_source'] = ev.metrics(canonical, rgb)
            row['strict_quality'] = strict_quality(row['quality_source'])
            row['clean_eligible'] = bool(genuine and row['strict_quality'] and all(row['endpoints'][ALPHA][m] for m in ('Q', 'H', 'F')))
            row.update(status='ok', duration_seconds=time.monotonic()-tick, beta_evaluation_seconds=beta_seconds)
            budget(); return row
        if args.phase == 'construct':
            if 'warmup' not in record:
                record['warmup'] = dict(source_id=1675, canonical_path=str(SOURCES[1675]), status='not_started', clean={})
            if record['warmup']['status'] not in ('not_started', 'ok'):
                raise RuntimeError('Interrupted fixed warmup remains incomplete; no automatic retry')
            for source in [record['warmup']] + record['sources']:
                if source['status'] != 'not_started':
                    continue  # Interrupted/failed sources are retained; never retry.
                budget(); source.update(status='running'); save()
                source_tick = time.monotonic()
                is_warmup = source is record['warmup']
                folder = out / ('warmup-1675' if is_warmup else str(source['source_id'])); folder.mkdir()
                try:
                    canonical = load(source['canonical_path'])
                    torch.cuda.synchronize()
                    supplier_tick = time.monotonic()
                    supplier = supply_f5(canonical, ev, folder / 'supplier', budget)
                    torch.cuda.synchronize()
                    supplier_wall = time.monotonic()-supplier_tick
                    source['supplier'] = supplier; write(folder / 'checkpoint.json', source); save(); budget()
                    if supplier['status'] != 'ok':
                        if 'Fresh F5 bootstrap native channels unreadable' in supplier.get('error', ''):
                            if is_warmup:
                                raise RuntimeError('Fixed warmup supplier unreadable')
                            source['status'] = 'supplier_failed'; continue
                        raise RuntimeError('Supplier execution interrupted: ' + supplier.get('error', 'unknown'))
                    source['payload'] = supplier['payload']
                    torch.cuda.synchronize(); writer_tick = time.monotonic()
                    full = embed(canonical, ALPHA, supplier['q'], supplier['h'], ev, other, channel, folder / 'full', budget)
                    torch.cuda.synchronize(); writer_wall = time.monotonic()-writer_tick
                    source['full_result'] = full; write(folder / 'checkpoint.json', source); save(); budget()
                    if full['status'] == 'construction_failed' or not full.get('final_image'):
                        raise RuntimeError('Full writer execution interrupted: ' + full.get('error', 'unknown'))
                    source['initializer'] = full['start_image']; source['full_image'] = full['final_image']
                    source['clean']['full'] = qualify(load(full['final_image']), canonical, supplier['payload'], True)
                    torch.cuda.synchronize(); tick = time.monotonic()
                    initializer = load(full['start_image'])
                    metrics = ev.metrics(canonical, initializer); retain = strict_quality(metrics)
                    lean = initializer if retain else contract(initializer, canonical)
                    lean_path = folder / 'lean.png'; Image.fromarray(lean).save(lean_path)
                    source.update(lean_image=str(lean_path), lean_branch='retain' if retain else 'contract_0.8', initializer_quality=metrics)
                    source['clean']['lean'] = qualify(load(lean_path), canonical, supplier['payload'], True)
                    torch.cuda.synchronize(); selector = time.monotonic()-tick
                    remainder = writer_wall-sum(full[k] for k in
                        ('construction_seconds', 'refinement_seconds', 'quality_qualification_seconds'))
                    if remainder < -1e-6:
                        raise ValueError('Overlapping full writer timers')
                    source['timing'] = dict(supplier_seconds=supplier_wall,
                        full_writer_seconds=writer_wall, construction_seconds=full['construction_seconds'],
                        full_refinement_seconds=full['refinement_seconds'], full_quality_qualification_seconds=full['quality_qualification_seconds'],
                        lean_selector_qualification_measured_seconds=selector-source['clean']['lean']['beta_evaluation_seconds'],
                        full_bookkeeping_remainder_seconds=max(0., remainder),
                        lean_stage_sum_estimate_seconds=supplier_wall+full['construction_seconds']+
                            selector-source['clean']['lean']['beta_evaluation_seconds']+max(0., remainder),
                        full_supplier_writer_seconds=supplier_wall+writer_wall,
                        basis=record['config']['timing_basis'],
                        overhead_policy='Full writer residual bookkeeping is charged conservatively to lean. Beta calls and duplicate full qualification are evaluation-only.')
                    source['clean']['C0'] = qualify(canonical, canonical, None, False)
                    source['status'] = 'ok'  # Admission failures remain scientific outcomes.
                    source['shared_elapsed_seconds'] = time.monotonic()-source_tick
                    budget()
                except BaseException:
                    source.update(status='incomplete', error=traceback.format_exc()); raise
                finally:
                    source['attempt_elapsed_seconds'] = time.monotonic()-source_tick
                    write(folder / 'checkpoint.json', source); save()
                    if not is_warmup:
                        with (out / 'rows.jsonl').open('a', encoding='utf-8') as evidence:
                            evidence.write(json.dumps(source, allow_nan=False)+'\n')
                        shard = record['sources'].index(source)//6
                        write(out / f'shard-{shard:02d}.json', record['sources'][shard*6:(shard+1)*6])
                print(json.dumps(dict(source_id=source['source_id'], status=source['status'])), flush=True)
                if is_warmup:
                    continue
                full_clean, lean_clean = (source['clean'][a] for a in ('full', 'lean'))
                if ((full_clean['strict_quality'] and not lean_clean['strict_quality']) or
                        (full_clean['clean_eligible'] and not lean_clean['clean_eligible'])):
                    record['early_stop'] = dict(source_id=source['source_id'], reason='Observed lean-only quality/admission loss',
                        decision='reject-fixed-lean; planned remaining sources are retained unobserved')
                    break
            record['construction_outcome'] = 'completed' if all(s['status'] in ('ok', 'supplier_failed') for s in record['sources']) else 'stopped_with_unresolved_sources'
            screen = summary(record)
            resolved = all(s['status'] in ('ok', 'supplier_failed') for s in record['sources'])
            complete_cost = screen['timing']['observed'] == 24
            negatives_resolved_zero = all(v['observed'] == 24 and v['A'] == 0 for v in screen['clean_negatives'].values())
            losses = any(s.get('clean', {}).get('full', {}).get(field) is True and
                s.get('clean', {}).get('lean', {}).get(field) is not True
                for s in record['sources'] for field in ('strict_quality', 'clean_eligible'))
            gate = resolved and complete_cost and negatives_resolved_zero and not losses and \
                min(screen['clean'][a]['eligible'] for a in ('full', 'lean')) >= 23 and screen['timing']['ratio_of_medians'] <= .75
            record['stage_A'] = dict(pass_screen=gate, resolved=resolved, complete_cost=complete_cost,
                negatives_resolved_zero=negatives_resolved_zero, lean_only_loss=losses,
                decision='lean-survivor' if gate else 'reject-fixed-lean' if losses or
                    (resolved and complete_cost and screen['timing']['ratio_of_medians'] > .75) else 'inconclusive',
                attack_permission='Requires parent review and complete Stage B implementation')
        budget(); record['outcome'] = 'completed'; invocation['outcome'] = 'completed'
    except BaseException:
        record.update(outcome='incomplete', error=traceback.format_exc()); invocation['outcome'] = 'incomplete'
    finally:
        invocation['duration_seconds'] = time.monotonic()-started; save()
    if invocation['outcome'] != 'completed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
