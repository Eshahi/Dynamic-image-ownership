"""Frozen E3-RC1 public initializer reissues; one development invocation, no retry."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
ALPHA, BETA = 'qim-pilot-owner-alpha', 'qim-pilot-owner-beta'
PAIRS = ((30, 72), (73, 89), (127, 165), (309, 370), (436, 450), (459, 471))
MODES = ('combined', 'semantic_only', 'perceptual_only', 'none')
SEED, GPU_CAP, RAM_CAP, HEADROOM = 2026101317, 9*1024**3, 10*1024**3, 3*1024**3
PROTOCOL = ROOT / 'research/journal-upgrade-20261009/binding-positive-protocol.md'
STAGE_A = '546ac1fbf644e3d1ab3f454c9eb8ae736dbd072a'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def invariant(call):
    """Binding modes may alter predicates, never extraction or carrier routing."""
    return {**{k: call[k] for k in ('q_bound', 'routing', 'semantic_code', 'perceptual_hash')},
        **{tier: {k: v for k, v in call[tier].items()
                   if k not in ('content_status', 'content_match', 'soft_distance')}
           for tier in ('semantic', 'instance')}}


def summarize(record):
    cells = record['cells']
    tables = {}
    for label in ('RR', 'DR', 'RD', 'DD'):
        rows = [c for c in cells if c['cell'] == label]
        qualified = [c for c in rows if c.get('quality_both') is True
                     and c.get('endpoints', {}).get('none', {}).get('D') is True]
        tables[label] = dict(planned=6, saved_images=sum('image' in c for c in rows),
            completed=sum(c['status'] == 'ok' for c in rows),
            quality_recipient=sum(c.get('quality_recipient_pass') is True for c in rows),
            quality_canonical=sum(c.get('quality_canonical_pass') is True for c in rows),
            quality_both=sum(c.get('quality_both') is True for c in rows),
            modes={mode: dict(planned=6, observed=sum(mode in c.get('endpoints', {}) for c in rows),
                unresolved=sum(mode not in c.get('endpoints', {}) for c in rows),
                **{key: sum(c.get('endpoints', {}).get(mode, {}).get(key) is True for c in rows)
                   for key in ('A', 'S', 'Q', 'J', 'H', 'D', 'F')}) for mode in MODES},
            conditional_delivered_quality=dict(denominator=len(qualified),
                identities=[[c['recipient'], c['donor']] for c in qualified],
                modes={mode: dict(observed=sum(mode in c.get('endpoints', {}) for c in qualified),
                    F=sum(c.get('endpoints', {}).get(mode, {}).get('F') is True for c in qualified))
                   for mode in MODES},
                combined_vs_perceptual_disagreements=sum(
                    c.get('endpoints', {}).get('combined', {}).get('F') is not None
                    and c.get('endpoints', {}).get('perceptual_only', {}).get('F') is not None
                    and c['endpoints']['combined']['F'] != c['endpoints']['perceptual_only']['F']
                    for c in qualified)))
    rr = [c for c in cells if c['cell'] == 'RR']
    nonidentical = sum(c.get('changed_rgb_components', 0) > 0 for c in rr)
    positive = all(c['status'] == 'ok' and c.get('quality_both') is True
                   and c['endpoints']['none']['D'] and c['endpoints']['combined']['F'] for c in rr) and nonidentical > 0
    dr = [c for c in cells if c.get('primary_witness') is True]
    rd = [c for c in cells if c.get('reciprocal_witness') is True]
    beta = [c['beta_endpoint'] for c in cells if 'beta_endpoint' in c]
    return dict(fixed_denominators=tables, positive_control_gate=positive,
        nonidentical_RR=nonidentical, primary_witness_count=len(dr),
        primary_witness_pairs=[[c['recipient'], c['donor']] for c in dr],
        reciprocal_witness_count=len(rd), beta=dict(planned=24, observed=len(beta),
            unresolved=24-len(beta), A=sum(c['A'] for c in beta)),
        repeated_incremental_witness=positive and len(dr) >= 2,
        unqualified_useful_result=record['outcome'] == 'completed'
            and record['duration_seconds'] <= 1800 and positive and len(dr) >= 2
            and len(beta) == 24 and not any(c['A'] for c in beta),
        interpretation='Exploratory paired public reissue component panel. None F is not ownership. No human semantics, authentication, population FPR, or new significance claim.')


def main():
    started = time.monotonic()  # Inclusive: precedes scientific imports and loading.
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-receipt', 'fresh-receipt', 'output-dir', 'main', 'dev-log'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--desktop-pids', type=int, nargs='*', default=[],
        help='Operator-observed desktop-only nvidia-smi PID snapshot; never science PIDs')
    args = parser.parse_args()
    out = args.output_dir.resolve()
    main_root = args.main.resolve()
    if not out.is_relative_to(main_root / '.thesis-build/dev-runs'):
        raise ValueError('New development output must be beneath MAIN/.thesis-build/dev-runs')
    if args.dev_log.resolve() not in (main_root / 'experiments/dev-log.md', ROOT / 'experiments/dev-log.md'):
        raise ValueError('Use the ordinary MAIN or current worktree development log')
    out.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    record = dict(schema='journal-binding-reissue-v1', commit=commit, command=sys.argv,
        protocol=str(PROTOCOL), protocol_sha256=digest(PROTOCOL),
        started_at_utc=datetime.now(timezone.utc).isoformat(), data_split='development-reserved', usd=0,
        outcome='running', duration_seconds=0., targets={}, shared_stages=[],
        cells=[dict(recipient=r, donor=d, cell=c, status='not_started', phase='not_started',
                    calls={}, endpoints={}) for r, d in PAIRS for c in ('RR', 'DR', 'RD', 'DD')],
        config=dict(seed=SEED, max_seconds=1800, gpu_cap_bytes=GPU_CAP,
            process_rss_cap_bytes=RAM_CAP, minimum_available_ram_bytes=HEADROOM,
            semantic_views=7, precision='float32', binding='soft', roster_size=1,
            schedule='pairs in fixed order; qR then qD; hR then hD independently',
            first_stage=dict(psnr=46, steps=150, margin=4, mask_power=0),
            branch=dict(psnr=52, steps=50, margin=4, mask_power=0), planned_pgd_steps=3000,
            human_admissibility='missing', no_retry=True),
        resources=dict(peak_gpu_allocated_bytes=0, peak_process_rss_bytes=0,
            minimum_available_ram_bytes=None), attempted_forward_steps=0, completed_pgd_steps=0,
        step_count_convention='Forward attempts counted only during PGD; complete native phases counted only after return. Partial forward attempts do not certify backward/update completion.')
    path = out / 'run.json'
    torch = ev = None
    active = None

    def save():
        record['duration_seconds'] = time.monotonic()-started
        record['summary'] = summarize(record)
        write(path, record)

    save()  # Register commit/protocol/run identity before scientific imports.
    try:
        for tracked in (Path(__file__), PROTOCOL, args.fresh_receipt,
                        args.fresh_receipt.with_name('fresh-development-selection.json')):
            rel = str(tracked.resolve().relative_to(ROOT))
            subprocess.check_call(['git', 'ls-files', '--error-unmatch', rel], cwd=ROOT,
                                  stdout=subprocess.DEVNULL)
            if subprocess.call(['git', 'diff', '--quiet', 'HEAD', '--', rel], cwd=ROOT):
                raise ValueError('Driver, protocol and configuration must be committed before execution')
        receipt, fresh = read(args.source_receipt), read(args.fresh_receipt)
        selection_path = args.fresh_receipt.with_name('fresh-development-selection.json')
        selection = read(selection_path)
        if receipt['commit'] != STAGE_A or receipt['outcome'] != 'completed':
            raise ValueError('Completed frozen Stage A receipt required')
        cohort = {int(s['source_id']): s for s in fresh['sources']}
        ids = [sid for pair in PAIRS for sid in pair]
        if sorted(cohort)[:12] != sorted(ids) or fresh['selection_sha256'] != digest(selection_path):
            raise ValueError('Fixed first twelve source identities/selection receipt mismatch')
        sources = {int(s['source_id']): s for s in receipt['sources']}
        selected = {int(s['source_id']): s for s in selection['selected']}
        exclusions = set(selection['raw_sha256_exclusions'])
        for sid in ids:
            s, f = sources[sid], cohort[sid]
            clean = s['clean']['full']; call = clean['calls'][ALPHA]
            if not (f['development_reserved'] is True and f['raw_overlap'] is False
                    and f['raw_sha256'] not in exclusions and sid in selected
                    and s['source_uid'] == f['source_uid'] and s['sha256'] == f['sha256']
                    and s['raw_sha256'] == f['raw_sha256'] and clean['status'] == 'ok'
                    and all(clean['endpoints'][ALPHA][k] is True for k in ('Q', 'H', 'F'))
                    and call['semantic']['read'] and call['instance']['read']
                    and call['outcome'] == 'both_match'):
                raise ValueError(f'Incomplete input/exclusion/clean exact evidence: {sid}')
            canonical, full = Path(s['canonical_path']), Path(s['full_image'])
            if digest(canonical) != f['sha256'] or not full.is_file():
                raise ValueError(f'Missing or changed input: {sid}')
            record['targets'][str(sid)] = dict(q=int(call['semantic']['decoded_code'], 16),
                h=int(call['perceptual_hash'], 16), original_operational_h=int(call['instance']['decoded_code'], 16),
                q_receipt_field='clean.full.calls.alpha.semantic.decoded_code',
                h_receipt_field='clean.full.calls.alpha.perceptual_hash',
                canonical_path=str(canonical), full_image=str(full),
                historical_clean_call=call, canonical_sha256=f['sha256'], raw_sha256=f['raw_sha256'])
        record['inputs'] = dict(source_receipt=str(args.source_receipt.resolve()),
            fresh_receipt=str(args.fresh_receipt.resolve()), fresh_sha256=digest(args.fresh_receipt),
            exclusion_receipt=str(selection_path.resolve()), selection_sha256=digest(selection_path),
            excluded_hash_count=len(exclusions), historical_controls='Stage A clean full/C0/beta retained, not new observations')
        save()
        os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
        from fresh_e3_simplification import memory

        def budget():
            rss, peak, available = memory()
            allocated = int(torch.cuda.max_memory_allocated()) if torch is not None and torch.cuda.is_initialized() else 0
            resources = record['resources']
            resources['peak_gpu_allocated_bytes'] = max(resources['peak_gpu_allocated_bytes'], allocated)
            resources['peak_process_rss_bytes'] = max(resources['peak_process_rss_bytes'], rss, peak)
            resources['minimum_available_ram_bytes'] = min(resources['minimum_available_ram_bytes'] or available, available)
            elapsed = time.monotonic()-started
            if elapsed >= 1800 or allocated > GPU_CAP or rss > RAM_CAP or available < HEADROOM:
                raise RuntimeError(f'Execution envelope reached: elapsed={elapsed:.6f}, GPU={allocated}, RSS={rss}, available={available}')

        budget()
        observed = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid',
            '--format=csv,noheader,nounits'], text=True)
        pids = [int(line.strip()) for line in observed.splitlines() if line.strip()]
        record['gpu_process_preflight'] = dict(observed_pids=pids, desktop_pids=args.desktop_pids, self_pid=os.getpid())
        if any(pid != os.getpid() and pid not in args.desktop_pids for pid in pids):
            raise RuntimeError('Another non-desktop GPU process present')
        import numpy as np
        import torch as torch_module
        torch = torch_module
        import three_threat_models as models
        models.block_network()
        from PIL import Image
        from journal_vae_probe import Evaluator
        from journal_e3_writer import _BoundedReader, strict_quality, patterns, restore_fragile
        from f5_latent_codec import robust_pgd
        from journal_bch_readout import detect_rgb
        from journal_bch_analysis import endpoint
        random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
        free, total = torch.cuda.mem_get_info()
        if free < GPU_CAP:
            raise RuntimeError('Less than 9 GiB free GPU before loading')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/total)
        budget(); ev = Evaluator(); budget()
        ev.reader.vae.enable_gradient_checkpointing()
        record['environment'] = dict(python=sys.version, torch=torch.__version__,
            gpu=torch.cuda.get_device_name(), threads=torch.get_num_threads(), profile=ev.profile)

        class Reader(_BoundedReader):
            def encode(self, x):
                self.budget()
                active['attempted_forward_steps'] += 1
                record['attempted_forward_steps'] += 1
                z = self.reader.encode(x)
                if not bool(torch.isfinite(z).all()):
                    raise ValueError('Nonfinite native PGD latent')
                budget()
                return z

        bounded = Reader(ev.reader, budget)

        def load(p):
            with Image.open(p) as image:
                if image.mode != 'RGB' or image.size != (512, 512):
                    raise ValueError('512x512 RGB8 required')
                return np.asarray(image, np.uint8).copy()

        def pgd(rgb, layout, w, psnr, steps):
            value = robust_pgd(bounded, rgb.astype(np.float64)/255., layout, w, psnr, steps, 4., 0.)
            if not np.isfinite(value).all():
                raise ValueError('Nonfinite PGD image')
            active['completed_pgd_steps'] = steps
            record['completed_pgd_steps'] += steps
            budget()
            return np.clip(np.rint(value*255), 0, 255).astype(np.uint8)

        def save_rgb(p, rgb):
            Image.fromarray(rgb).save(p)
            reloaded = load(p); budget()
            return reloaded

        for recipient, donor in PAIRS:
            r, d = record['targets'][str(recipient)], record['targets'][str(donor)]
            # Original references enter quality evaluation only.
            original, canonical = load(r['full_image']), load(r['canonical_path'])
            folder = out / f'{recipient}-{donor}'; folder.mkdir()
            for qi, q in enumerate((r['q'], d['q'])):
                active = dict(recipient=recipient, donor=donor, q=q, status='running',
                    phase='first_pgd150', attempted_forward_steps=0, completed_pgd_steps=0)
                record['shared_stages'].append(active); save(); budget()
                layout, w, _ = patterns(ev.profile, q)
                shared = pgd(original.copy(), layout, w, 46., 150)
                shared_path = folder / f'q{qi}-first150.png'
                shared = save_rgb(shared_path, shared)
                active.update(status='ok', phase='saved', image=str(shared_path)); save()
                for hi, h in enumerate((r['h'], d['h'])):
                    label = ('RR', 'RD', 'DR', 'DD')[qi*2+hi]
                    active = next(c for c in record['cells'] if c['recipient'] == recipient and c['cell'] == label)
                    active.update(status='running', phase='restore1', supplied_q=q, supplied_h=h,
                        payload=dict(q=f'{q:08x}', h=f'{h:08x}'), attempted_forward_steps=0,
                        completed_pgd_steps=0, shared_image=str(shared_path),
                        equal_q=r['q'] == d['q'], equal_h=r['h'] == d['h'],
                        target_h_differs_from_original_operational=h != r['original_operational_h'])
                    save(); budget()
                    restored, report = restore_fragile(shared.copy(), q, h, ev.profile)
                    active['first_restore'] = report; budget()
                    active['phase'] = 'branch_pgd50'
                    result = pgd(restored, layout, w, 52., 50)
                    active['phase'] = 'restore2'
                    result, report = restore_fragile(result, q, h, ev.profile)
                    active['second_restore'] = report; budget()
                    image_path = folder / f'{label}.png'
                    result = save_rgb(image_path, result)
                    delta = result.astype(np.int32)-original.astype(np.int32)
                    active.update(image=str(image_path), phase='quality',
                        changed_rgb_components=int(np.count_nonzero(delta)),
                        changed_pixels=int(np.count_nonzero(np.any(delta != 0, axis=2))),
                        maximum_absolute_pixel_change=int(np.abs(delta).max()), idempotent=not bool(np.any(delta)))
                    save()
                    for name, reference in (('recipient', original), ('canonical', canonical)):
                        metrics = ev.metrics(reference, result)
                        active['quality_'+name] = metrics
                        active['quality_'+name+'_pass'] = strict_quality(metrics)
                        budget()
                    active['quality_both'] = active['quality_recipient_pass'] and active['quality_canonical_pass']
                    active['phase'] = 'suspect_features'
                    features = ev.features(result, 7); budget()
                    latent = ev.reader.latent(result); budget()
                    active['phase'] = 'detection'
                    baseline = None
                    for mode in MODES:
                        call = detect_rgb(result, latent, ALPHA, ev.profile, features,
                            binding_mode=mode, binding='soft', roster_size=1)
                        active['calls'][mode] = call
                        ep = endpoint(call, active['payload']); ep['D'] = ep['Q'] and ep['H']
                        active['endpoints'][mode] = ep
                        write(folder / f'{label}-{mode}.json', call); budget()
                        fingerprint = invariant(call)
                        if baseline is not None and fingerprint != baseline:
                            raise RuntimeError('Implementation discrepancy: binding modes changed extraction/readability/routing')
                        baseline = fingerprint; save()
                    beta = detect_rgb(result, latent, BETA, ev.profile, features,
                        binding_mode='combined', binding='soft', roster_size=1)
                    active['beta_call'], active['beta_endpoint'] = beta, endpoint(beta)
                    write(folder / f'{label}-beta.json', beta); budget()
                    eps, combined = active['endpoints'], active['calls']['combined']
                    eligible = active['quality_both'] and eps['none']['D']
                    active['primary_witness'] = bool(label == 'DR' and eligible and q != r['q']
                        and eps['perceptual_only']['F'] and not eps['combined']['F']
                        and combined['semantic']['found'] and not combined['semantic']['content_match']
                        and combined['instance_own_content_status'] == 'match')
                    active['reciprocal_witness'] = bool(label == 'RD' and eligible and h != r['h']
                        and eps['semantic_only']['F'] and not eps['combined']['F']
                        and combined['semantic']['content_match']
                        and combined['instance']['found'] and combined['instance_own_content_status'] != 'match')
                    if label == 'RR':
                        active['positive_classification'] = ('construction_quality_failure' if not active['quality_both']
                            else 'construction_delivery_failure' if not eps['none']['D']
                            else 'constructed_positive_rejection' if not eps['combined']['F']
                            else 'idempotent_accepted' if active['idempotent'] else 'rewritten_positive_accepted')
                    active.update(status='ok', phase='complete'); save(); budget()
        record['outcome'] = 'completed'
        record['terminal_reason'] = 'Fixed schedule completed, regardless of measured quality/delivery/predicate failures'
    except Exception:
        record.update(outcome='stopped', terminal_reason=traceback.format_exc())
        if active is not None and active.get('status') == 'running':
            active.update(status='partial', error=record['terminal_reason'])
    finally:
        record['duration_seconds'] = time.monotonic()-started
        record['deadline_overrun_seconds'] = max(0., record['duration_seconds']-1800)
        save()
        with args.dev_log.open('a', encoding='utf-8') as log:
            log.write(f"\n- {datetime.now(timezone.utc).isoformat()} Codex agent: E3-RC1 binding reissue; "
                f"commit {commit}; command {json.dumps(sys.argv)}; development seed {SEED}; "
                f"duration {record['duration_seconds']:.3f} s; outcome {record['outcome']}; "
                f"PGD completed {record['completed_pgd_steps']}/3000, forward attempts {record['attempted_forward_steps']}; "
                f"run {path}; USD 0; no retry.\n")
    return 0 if record['outcome'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
