"""Resumable step-2a registry screen on the 24 consulted development sources.

No tuning of writers or descriptors. Registry access is additional detector side
information. Thresholds fitted here are exploratory, not held-out calibration.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from registry_step1_transfer import MAIN, ALPHA, BETA, read, write, journal

METHODS = ('e3-s1', 'f5-r2')
DESCRIPTORS = ('D1', 'D2', 'D3')
PP1 = MAIN / '.thesis-build/dev-runs/20261010-1551-e3-s1-public-projection'


def pointer(call):
    """Read the carried q; never substitute recomputed q or content_match."""
    s = (call or {}).get('semantic') or {}
    word = s.get('decoded_code')
    try:
        valid = isinstance(word, str) and len(word) == 8 and 0 <= int(word, 16) < 2**32
    except ValueError:
        valid = False
    return dict(found=s.get('found') is True, read=s.get('read') is True,
                q=word if valid else None,
                recovered=s.get('found') is True and s.get('read') is True and valid)


def distance(a, b):
    return (int(a, 16) ^ int(b, 16)).bit_count()


def auc(pos, neg):
    """Mann-Whitney AUC including half credit for exact ties."""
    import numpy as np
    if not pos or not neg:
        return None
    n = np.sort(np.asarray(neg, dtype=np.float64))
    p = np.asarray(pos, dtype=np.float64)
    return float(np.mean((np.searchsorted(n, p, 'left') + np.searchsorted(n, p, 'right')) / (2 * len(n))))


def identify(scores, records, tau, carried=None, radius=6, owner=ALPHA, timings=None):
    """Timed record lookup over already computed cosine scores, when requested."""
    started = time.perf_counter()
    try:
        return _identify(scores, records, tau, carried, radius, owner)
    finally:
        if timings is not None:
            timings['calls'] = timings.get('calls', 0) + 1
            timings['seconds'] = timings.get('seconds', 0.) + time.perf_counter() - started


def _identify(scores, records, tau, carried=None, radius=6, owner=ALPHA):
    """Require the selected record to be correct in the caller, not just accepted."""
    candidates = [i for i, r in enumerate(records) if carried is None or
                  (carried['recovered'] and r['owner'] == owner and distance(carried['q'], r['q']) <= radius)]
    finite = [i for i in candidates if scores[i] is not None]
    if not finite:
        return dict(accepted=False, record_id=None, score=None, candidates=len(candidates), ties=0)
    best = max(scores[i] for i in finite)
    tied = [i for i in finite if scores[i] == best]
    # Sorted record ID is a transparent deterministic tie rule, not enrollment order.
    i = min(tied, key=lambda i: records[i]['record_id'])
    return dict(accepted=best >= tau, record_id=records[i]['record_id'] if best >= tau else None,
                score=best, candidates=len(candidates), ties=len(tied))


class DescriptorCache:
    """One compressed float64 vector file per saved pixel image, shared by methods."""
    def __init__(self, out, ev, profile, dino_path, budget):
        import torch
        from transformers import AutoImageProcessor, AutoModel
        from scripts import revised_watermark_v5 as v5
        self.np = __import__('numpy')
        self.torch, self.ev, self.budget = torch, ev, budget
        self.profile, self.key, self.config = v5._resolve(profile, None)
        self.processor = AutoImageProcessor.from_pretrained(dino_path, local_files_only=True)
        self.dino = AutoModel.from_pretrained(dino_path, local_files_only=True).eval()
        if self.dino.config.hidden_size != 384:
            raise ValueError('Pinned DINOv2-small must have 384-dimensional CLS')
        self.directory = out / 'descriptors'
        self.directory.mkdir(exist_ok=True)
        self.memory, self.index = {}, {}
        self.metrics = dict(extracted_images=0, memory_hits=0, disk_hits=0, disk_load_seconds=0.,
                            extraction_seconds={n:0. for n in DESCRIPTORS}, extraction_wall_seconds=0.)

    def get(self, path):
        import numpy as np
        from PIL import Image
        from scripts import journal_fine_gaussian_instance as fine
        from scripts import revised_watermark_v5 as v5
        path = Path(path).resolve()
        stat = path.stat()
        identity = f'{path}|{stat.st_size}|{stat.st_mtime_ns}'
        key = hashlib.sha256(identity.encode()).hexdigest()
        if key in self.memory:
            self.metrics['memory_hits'] += 1
            return self.memory[key]
        self.budget()
        dest = self.directory / (key + '.npz')
        if dest.exists():
            tick = time.perf_counter()
            with np.load(dest, allow_pickle=False) as a:
                result = {n: a[n] if a[n].size else None for n in DESCRIPTORS}
            self.metrics['disk_hits'] += 1
            self.metrics['disk_load_seconds'] += time.perf_counter() - tick
        else:
            wall_tick = time.perf_counter()
            with Image.open(path) as im:
                image = im.convert('RGB')
            rgb = np.asarray(image, dtype=np.uint8)
            tick = time.perf_counter()
            f = fine.descriptor(v5.luminance_from_rgb(rgb.tolist()), self.key, self.config)
            self.metrics['extraction_seconds']['D1'] += time.perf_counter() - tick
            with self.torch.inference_mode():
                tick = time.perf_counter()
                dino = self.dino(**self.processor(images=image, return_tensors='pt')).last_hidden_state[0, 0].float().numpy()
                self.metrics['extraction_seconds']['D2'] += time.perf_counter() - tick
                tick = time.perf_counter()
                clip = np.asarray(self.ev.features(rgb, 7), dtype=np.float64)
                self.metrics['extraction_seconds']['D3'] += time.perf_counter() - tick
            result = dict(D1=None if f['vector'] is None else np.asarray(f['vector'], np.float64), D2=dino, D3=clip)
            result = {n: None if v is None or not np.isfinite(v).all() or np.linalg.norm(v) <= 0
                      else np.asarray(v / np.linalg.norm(v), np.float64) for n, v in result.items()}
            tmp = dest.with_suffix('.tmp.npz')
            np.savez_compressed(tmp, **{n: np.array([], np.float64) if v is None else v for n, v in result.items()})
            tmp.replace(dest)
            self.metrics['extracted_images'] += 1
            self.metrics['extraction_wall_seconds'] += time.perf_counter() - wall_tick
        for name, dimension in (('D2', 384), ('D3', 512)):
            if result[name] is not None and result[name].shape != (dimension,):
                raise ValueError(f'{name} must be a {dimension}-dimensional vector')
        self.index[str(path)] = dict(cache=str(dest), image_size=stat.st_size, image_mtime_ns=stat.st_mtime_ns,
                                    dimensions={n: len(v) if v is not None else None for n, v in result.items()})
        self.memory[key] = result
        return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--step1-dir', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--chosen-method', choices=METHODS, required=True)
    p.add_argument('--pp1-dir', type=Path, default=PP1)
    p.add_argument('--max-seconds', type=float, default=14400)
    p.add_argument('--prior-step2-seconds', type=float, default=0,
                   help='All other step-2 GPU/wall compute already spent, including later phases on resume')
    a = p.parse_args()
    if not 0 < a.max_seconds <= 14400 or a.prior_step2_seconds < 0:
        raise ValueError('Step 2 has a cumulative four-hour cap')
    out = a.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / 'images').mkdir(exist_ok=True)
    step1 = read(a.step1_dir / 'run.json')
    parent = read(Path(step1['config']['parent']) / 'run.json')
    sources = sorted(step1['sources'], key=lambda r: r['source_id'])
    ids = [s['source_id'] for s in sources]
    if len(ids) != 24 or len(set(ids)) != 24 or step1['data_split'] != 'development':
        raise ValueError('Exactly 24 distinct development sources required')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    config = dict(step1_dir=str(a.step1_dir.resolve()), step1_commit=step1['commit'], chosen_method=a.chosen_method,
                  descriptors=list(DESCRIPTORS), sources=ids, strengths=[.1, .2, .4], seeds=[12, 13, 14],
                  pp1_dir=str(a.pp1_dir.resolve()), threshold='nextafter(global maximum primary negative,+inf)',
                  registry='single published marked image per source, owner alpha', fingerprint_N=24,
                  negative_calibration='all ordered impostors, q nearest, fixed siblings, cyclic residual T4; PP1 descriptive',
                  cap_seconds=a.max_seconds, dino_revision='ed25f3a3', clip_views=7,
                  descriptor_storage='float64 normalized vectors; NPZ compression is lossless',
                  human_admissibility='missing', side_information='owner, public profile, pinned VAE/CLIP; trusted available registry and per-record continuous descriptors',
                  limitations=['registry trust and availability', 'stored descriptor privacy', 'consulted development threshold selection'])
    runpath = out / 'run.json'
    if runpath.exists():
        result = read(runpath)
        if result['commit'] != commit or result['config'] != config:
            raise ValueError('Resume requires identical commit and configuration')
    else:
        result = dict(schema='registry-step2-screen-v1', commit=commit, command=sys.argv, config=config,
                      data_split='consulted development', usd=0, outcome='running', duration_seconds=0, invocations=[])
    previous = result['duration_seconds']
    started = time.monotonic()
    invocation = dict(command=sys.argv, status='running', prior_other_step2_seconds=a.prior_step2_seconds)
    result['invocations'].append(invocation)
    callpath = out / 'calls.jsonl'
    if callpath.exists() and callpath.stat().st_size and not callpath.read_bytes().endswith(b'\n'):
        raw = callpath.read_bytes()
        end = raw.rfind(b'\n') + 1
        (out / f'interrupted-call-tail-{time.time_ns()}.bin').write_bytes(raw[end:])
        callpath.write_bytes(raw[:end])
    local = journal(callpath)
    inputs = journal(a.step1_dir / 'rows.jsonl')
    ev = None

    def save():
        result['duration_seconds'] = previous + time.monotonic() - started
        result['step2_accounted_seconds'] = result['duration_seconds'] + a.prior_step2_seconds
        invocation['duration_seconds'] = time.monotonic() - started
        write(runpath, result)

    def budget():
        if previous + time.monotonic() - started + a.prior_step2_seconds >= a.max_seconds:
            raise TimeoutError('Cumulative four-hour step-2 budget reached')

    def emit(row):
        with (out / 'calls.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, allow_nan=False) + '\n')
            f.flush()
        local[row['id']] = row
        save()

    save()
    try:
        import numpy as np
        import torch
        from PIL import Image
        from diffusers import AutoencoderKL
        from journal_vae_probe import Evaluator, SDXL
        from journal_bch_readout import detect_rgb as e3_detect
        from scripts.watermark_synthetic import scene
        from three_threat_protocol import residual_transfer
        import three_threat_models as models
        models.block_network()
        ev = Evaluator()
        if ev.profile != parent['config']['profile']:
            raise ValueError('Descriptor profile differs from mark construction')
        cache = DescriptorCache(out, ev, ev.profile, MAIN / '.thesis-build/assets/freqmark-reconstruction-20261013/dino', budget)
        # Each resume adds a timing entry. Cache hits are distinct from extraction;
        # model initialization and detector calls remain in total run duration.
        extraction_metrics = result.setdefault('descriptor_timing_invocations', [])
        extraction_metrics.append(cache.metrics)
        lookup_metrics = dict(registry=dict(calls=0,seconds=0.), fingerprint=dict(calls=0,seconds=0.),
                              cosine=dict(calls=0,seconds=0.))
        result.setdefault('lookup_timing_invocations', []).append(lookup_metrics)
        result['timing_scope'] = 'Host wall seconds. D1/D2/D3 extraction excludes model initialization; cosine scoring including cached-vector access, and owner/q filtering plus best-record selection, are measured separately. Screen scores are exhaustive for impostor analysis, not a simulated production latency. Saved per-invocation totals include resumes; cached images are not charged extraction twice.'
        radius = int(ev.profile['decision']['semantic_radius'])
        result['native_q_radius'] = radius

        def rgb(path):
            with Image.open(path) as im:
                return np.asarray(im.convert('RGB'), np.uint8).copy()

        def detect(image, method):
            budget()
            x = rgb(image)
            features, z = ev.features(x, 7), ev.reader.latent(x)
            calls = {}
            for owner in (ALPHA, BETA):
                budget()
                calls[owner] = (e3_detect(x, z, owner, ev.profile, features, binding='soft', roster_size=1)
                                if method == 'e3-s1' else ev.detect(x, 'f5', owner, features, z))
            return calls

        def generated(rid, method, make, **fields):
            if local.get(rid, {}).get('status') == 'ok':
                return local[rid]
            budget()
            image = out / 'images' / (rid.replace(':', '-') + '.png')
            Image.fromarray(make()).save(image)
            row = dict(id=rid, image=str(image), method=method, status='ok', calls=detect(image, method), **fields)
            emit(row)
            return row

        observations, registries, missing = [], {}, []
        for method in METHODS:
            records = []
            for sid in ids:
                row = inputs.get(f'clean:{sid}:{method}:C1', {})
                if row.get('status') != 'ok':
                    raise ValueError(f'Missing enrolled clean image {method}:{sid}')
                records.append(dict(record_id=f'{method}:{sid}', source_id=sid, owner=ALPHA,
                                    q=row['payload']['q'], h=row['payload']['h'], image=row['image']))
            registries[method] = records
        result['registry_records'] = registries
        # Step-1 complete grid is fixed. Missing/safety-blocked outputs remain failed slots.
        phases = ['sd15', 'sd21'] + (['sdxl'] if 'sdxl' in step1.get('regenerators', {}) else [])
        for method in METHODS:
            for sid in ids:
                for control in ('C1', 'C0'):
                    row = inputs.get(f'clean:{sid}:{method}:{control}', {})
                    observations.append(dict(id=f'clean:{sid}:{method}:{control}', method=method, source_id=sid,
                        phase='clean', strength=None, seed=None, control=control, image=row.get('image'),
                        calls=row.get('calls', {}), status=row.get('status', 'missing')))
                for phase in phases:
                    for strength in (.1, .2, .4):
                        for seed in (12, 13, 14):
                            for control in ('C1', 'C0'):
                                rid = f'{phase}:{sid}:{strength}:{seed}:{method if control == "C1" else "C0"}'
                                row = inputs.get(rid, {})
                                observations.append(dict(id=rid + ':' + method + ':' + control, method=method, source_id=sid,
                                    phase=phase, strength=strength, seed=seed, control=control, image=row.get('image'),
                                    calls=row.get('readouts', {}).get(method, {}).get('calls', {}), status=row.get('status', 'missing')))
        # VAE-only reconstruction of every enrolled marked image, posterior mode fp32.
        for condition in ('sd15_vae', 'sdxl_vae'):
            other = None
            if condition == 'sdxl_vae':
                budget()
                other = AutoencoderKL.from_pretrained(SDXL, local_files_only=True, use_safetensors=True,
                            torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
            vae = ev.reader.vae if other is None else other
            for method in METHODS:
                for rec in registries[method]:
                    sid = rec['source_id']
                    def reconstruct(path=rec['image']):
                        with torch.inference_mode():
                            x = ev.reader.tensor(rgb(path).astype(np.float32) / 255)
                            y = vae.decode(vae.encode(x * 2 - 1).latent_dist.mode()).sample[0].permute(1, 2, 0).cpu().numpy()
                        return np.rint(np.clip(y * .5 + .5, 0, 1) * 255).astype(np.uint8)
                    row = generated(f'{condition}:{sid}:{method}', method, reconstruct, source_id=sid,
                                    phase=condition, strength=None, seed=None, control='C1')
                    observations.append(row)
            if other is not None:
                del other, vae
                torch.cuda.empty_cache()
        # Cyclic donor->next source, never selected using an outcome.
        transfers = []
        for method in METHODS:
            for k, donor in enumerate(ids):
                recipient = ids[(k + 1) % len(ids)]
                r0 = rgb(next(s['canonical_path'] for s in sources if s['source_id'] == recipient))
                d0 = rgb(next(s['canonical_path'] for s in sources if s['source_id'] == donor))
                d1 = rgb(next(r['image'] for r in registries[method] if r['source_id'] == donor))
                for scale in (.5, 1.):
                    row = generated(f'T4:{method}:{donor}:{recipient}:{scale}', method,
                        lambda r=r0, d=d1, c=d0, s=scale: np.asarray(residual_transfer(r.tolist(), d.tolist(), c.tolist(), s), np.uint8),
                        source_id=donor, recipient_id=recipient, phase='T4', strength=scale, seed=None, control='negative')
                    transfers.append(row)
        siblings = []
        for seed in range(1, 7):
            paths = []
            for detail in (11, 12):
                path = out / 'images' / f'sibling-{seed}-{detail}.png'
                if not path.exists():
                    Image.fromarray(np.clip(np.asarray(scene(seed, 512, 512, 12., detail)), 0, 255).astype(np.uint8)).save(path)
                paths.append(str(path))
            siblings.append(dict(seed=seed, images=paths))
        pp1_rows = []
        if (a.pp1_dir / 'run.json').exists():
            pp = read(a.pp1_dir / 'run.json')
            controls = journal(Path(pp['immediate_dir']) / 'rows.jsonl')
            for row in journal(a.pp1_dir / 'rows.jsonl').values():
                if row.get('method') == 'E3' and row.get('status') == 'ok' and row.get('stratum') != 'T4_sham':
                    ref = controls.get(f'clean/E3/{row["donor_id"]}/C1', {})
                    pp1_rows.append(dict(id=row['id'], image=row['image'], record_image=ref.get('image'),
                                         record_q=pointer(ref.get('calls', {}).get(ALPHA))['q'],
                                         source_id=row['donor_id'], calls=row['calls'].get('combined', {})))
        else:
            missing.append(dict(panel='PP1', reason='retained PP1 run missing'))
        if len(pp1_rows) != 27:
            missing.append(dict(panel='PP1', expected=27, observed=len(pp1_rows)))
        # Cache all vectors once. No image pairs trigger another neural extraction.
        paths = {r['image'] for rr in registries.values() for r in rr}
        paths |= {r['image'] for r in observations + transfers if r.get('status') == 'ok' and r.get('image')}
        paths |= {p for s in siblings for p in s['images']}
        paths |= {p for r in pp1_rows for p in (r['image'], r['record_image']) if p and Path(p).is_file()}
        for k, path in enumerate(sorted(paths)):
            cache.get(path)
            if k % 25 == 0:
                result['descriptor_images_complete'] = k + 1
                write(out / 'descriptor-index.json', cache.index)
                save()
                print(f'descriptors {k + 1}/{len(paths)}', flush=True)
        write(out / 'descriptor-index.json', cache.index)

        def cosine(path, other, name):
            tick = time.perf_counter()
            aa, bb = cache.get(path)[name], cache.get(other)[name]
            value = None if aa is None or bb is None else float(np.dot(aa, bb))
            lookup_metrics['cosine']['calls'] += 1
            lookup_metrics['cosine']['seconds'] += time.perf_counter() - tick
            return value

        # Store all scores and calls for independent analysis and later competing enrollment.
        result['descriptors'] = {}
        for name in DESCRIPTORS:
            negative, pairrows, outcomes = [], [], []
            desc_missing, blocked, pp_missing = [], [], list(missing)
            for method in METHODS:
                records = registries[method]
                targets = {r['source_id']: r for r in records}
                for obs in observations:
                    if obs['method'] != method:
                        continue
                    if obs['status'] != 'ok' or not obs.get('image') or not obs['calls'].get(ALPHA):
                        if obs['status'] == 'safety_blocked':
                            # The pinned safety policy completed its attempted
                            # transformation. This positive slot is a failure;
                            # its 23 impostor comparisons remain unobserved.
                            blocked.append(dict(id=obs['id'], control=obs['control'], unresolved_impostor_pairs=23))
                        else:
                            desc_missing.append(dict(id=obs['id'], reason=obs['status'] if obs['status'] != 'ok' else 'missing call/image'))
                        outcomes.append(dict(**obs, scores=None))
                        continue
                    if obs['control'] == 'C1' and not obs['calls'].get(BETA):
                        desc_missing.append(dict(id=obs['id'], reason='wrong-owner call missing'))
                    scores = [cosine(obs['image'], r['image'], name) for r in records]
                    if any(v is None for v in scores):
                        desc_missing.append(dict(id=obs['id'], reason='descriptor unavailable'))
                    outcomes.append(dict(**obs, scores=scores))
                    # Both marked and canonical/unmarked-regenerated suspects
                    # are impostors to every *other* source's record. Their own
                    # source is a fingerprint positive and excluded here.
                    if obs['control'] in ('C1', 'C0'):
                        nearest = min((i for i in ids if i != obs['source_id']),
                            key=lambda i: (distance(targets[obs['source_id']]['q'], targets[i]['q']), i))
                        for r, score in zip(records, scores):
                            if r['source_id'] == obs['source_id']:
                                continue
                            pairrows.append(dict(suspect_id=obs['id'], target=r['record_id'], score=score,
                                q_nearest=r['source_id'] == nearest, phase=obs['phase'], strength=obs['strength']))
                            if score is not None:
                                negative.append(score)
                for t in transfers:
                    if t['method'] != method:
                        continue
                    score = cosine(t['image'], targets[t['source_id']]['image'], name)
                    pairrows.append(dict(suspect_id=t['id'], target=targets[t['source_id']]['record_id'], score=score, phase='T4', strength=t['strength']))
                    if score is None:
                        desc_missing.append(dict(id=t['id'], reason='T4 descriptor unavailable'))
                    else:
                        negative.append(score)
            for s in siblings:
                score = cosine(*s['images'], name)
                pairrows.append(dict(suspect_id=f'sibling:{s["seed"]}', target=s['images'][0], score=score, phase='sibling', strength=None))
                if score is None:
                    desc_missing.append(dict(id=f'sibling:{s["seed"]}', reason='descriptor unavailable'))
                else:
                    negative.append(score)
            tau = float(np.nextafter(max(negative), np.inf)) if negative else None
            cells = {}
            for method in METHODS:
                records = registries[method]
                for obs in outcomes:
                    if obs['method'] != method:
                        continue
                    obs['pointer'] = pointer(obs['calls'].get(ALPHA))
                    obs['wrong_owner_pointer'] = pointer(obs['calls'].get(BETA))
                    scores = obs['scores'] or [None] * len(records)
                    obs['registry'] = identify(scores, records, tau, obs['pointer'], radius, timings=lookup_metrics['registry'])
                    obs['fingerprint'] = identify(scores, records, tau, timings=lookup_metrics['fingerprint'])
                    target = f'{method}:{obs["source_id"]}'
                    obs['F_R'] = obs['registry']['accepted'] and obs['registry']['record_id'] == target
                    obs['fingerprint_correct'] = obs['fingerprint']['accepted'] and obs['fingerprint']['record_id'] == target
                    obs['own_similarity'] = scores[ids.index(obs['source_id'])]
                    obs['execution_unknown'] = obs['status'] not in ('ok', 'safety_blocked') or (obs['status'] == 'ok' and (
                        not obs.get('image') or not obs['calls'].get(ALPHA) or obs['own_similarity'] is None))
                for phase in ['clean', 'sd15_vae', 'sdxl_vae'] + phases:
                    for strength in ([.1, .2, .4] if phase in phases else [None]):
                        group = [o for o in outcomes if o['method'] == method and o['phase'] == phase and o['strength'] == strength and o['control'] == 'C1']
                        pos = [o['own_similarity'] for o in group if o['own_similarity'] is not None]
                        by_source = defaultdict(list)
                        for o in group:
                            by_source[o['source_id']].append(o)
                        cells[f'{method}/{phase}/{strength}'] = dict(planned=24 * (3 if phase in phases else 1), known=len(pos),
                            min_positive=min(pos) if pos else None, max_negative=max(negative), threshold=tau,
                            auc=auc(pos, negative), descriptor_accepts=sum(v >= tau for v in pos),
                            registry_accepts=sum(o['registry']['accepted'] for o in group), correct_record_F_R=sum(o['F_R'] for o in group),
                            fingerprint_correct=sum(o['fingerprint_correct'] for o in group),
                            source_majority_fingerprint_correct=sum(sum(o['fingerprint_correct'] for o in rr) >= (2 if phase in phases else 1) for rr in by_source.values()),
                            fingerprint_wrong_accepts=sum(o['fingerprint']['accepted'] and not o['fingerprint_correct'] for o in group),
                            source_majority_F_R=sum(sum(o['F_R'] for o in rr) >= (2 if phase in phases else 1) for rr in by_source.values()),
                            source_majority_upper_with_execution_unknown=sum(sum(o['F_R'] or o['execution_unknown'] for o in rr) >= (2 if phase in phases else 1) for rr in by_source.values()),
                            safety_blocked=sum(o['status'] == 'safety_blocked' for o in group),
                            execution_unknown=sum(o['execution_unknown'] for o in group),
                            pointer_recovered=sum(o['pointer']['recovered'] for o in group),
                            candidate_multiplicity=[o['registry']['candidates'] for o in group])
            controls = [o for o in outcomes if o['control'] == 'C0']
            t4 = []
            for t in transfers:
                records = registries[t['method']]
                scores = [cosine(t['image'], r['image'], name) for r in records]
                pr = pointer(t['calls'][ALPHA])
                rr = identify(scores, records, tau, pr, radius, timings=lookup_metrics['registry'])
                fp = identify(scores, records, tau, timings=lookup_metrics['fingerprint'])
                t4.append(dict(id=t['id'], donor=t['source_id'], recipient=t['recipient_id'], pointer=pr,
                    registry=rr, fingerprint=fp, donor_false_accept=rr['accepted'] and rr['record_id'] == f'{t["method"]}:{t["source_id"]}',
                    fingerprint_donor_false_accept=fp['accepted'] and fp['record_id'] == f'{t["method"]}:{t["source_id"]}'))
            ppdesc = []
            for r in pp1_rows:
                score = cosine(r['image'], r['record_image'], name) if (
                    r['record_image'] and Path(r['image']).is_file() and Path(r['record_image']).is_file()) else None
                pr = pointer(r['calls'])
                candidate = pr['recovered'] and r['record_q'] is not None and distance(pr['q'], r['record_q']) <= radius
                ppdesc.append(dict(id=r['id'], donor=r['source_id'], similarity=score, pointer=pr,
                                   descriptive_descriptor_accept=score is not None and score >= tau,
                                   descriptive_pointer_and_descriptor=candidate and score is not None and score >= tau))
                if score is None:
                    pp_missing.append(dict(id=r['id'], reason='PP1 descriptor missing'))
            required = [cells[f'{a.chosen_method}/{phase}/0.2'] for phase in ('sd15', 'sd21')]
            full = not desc_missing
            control_false_accepts = sum(o['registry']['accepted'] for o in controls)
            passed = full and not control_false_accepts and all(c['source_majority_F_R'] >= 21 for c in required)
            impossible = any(c['source_majority_upper_with_execution_unknown'] < 21 for c in required)
            decision = 'pass' if passed else ('fail' if full or impossible or control_false_accepts else 'incomplete')
            summary = dict(tau=tau, max_negative=max(negative), negative_n=len(negative),
                observed_descriptor_false_accepts=sum(v >= tau for v in negative), cells=cells,
                negative_controls=dict(C0_planned=len(controls), C0_known=sum(o['scores'] is not None for o in controls),
                    C0_pointer_found=sum(o['pointer']['found'] for o in controls), C0_registry_accepts=sum(o['registry']['accepted'] for o in controls),
                    C0_fingerprint_accepts=sum(o['fingerprint']['accepted'] for o in controls),
                    C0_fingerprint_correct=sum(o['fingerprint_correct'] for o in controls),
                    C0_fingerprint_wrong_accepts=sum(o['fingerprint']['accepted'] and not o['fingerprint_correct'] for o in controls),
                    wrong_owner_pointer_found=sum(o['wrong_owner_pointer']['found'] for o in outcomes if o['control'] == 'C1'),
                    wrong_owner_registry_accepts=0, wrong_owner_registry_reason='No records enrolled for owner beta'),
                missing=desc_missing, descriptive_PP1_missing=pp_missing, complete=full, passes_kill_rule=passed,
                decision=decision, expected_safety_blocks=blocked,
                unresolved_safety_blocked_impostor_pairs=sum(r['unresolved_impostor_pairs'] for r in blocked),
                false_positive_scope='Zero observed primary-negative acceptances only; blocked negative comparisons are unresolved. No population FPR claim.',
                per_record_descriptor_bytes={m:[int(cache.get(r['image'])[name].nbytes) if cache.get(r['image'])[name] is not None else None for r in rr] for m,rr in registries.items()},
                lookup_cost='Screen computes exhaustive N=24 score tables for impostor analysis. Fingerprint searches N=24; prospective registry lookup filters owner/q then compares K candidates. Measured filter/selection time excludes separately measured cosine scoring.')
            write(out / f'{name}-scores.json', dict(positives_and_C0=outcomes, negatives=pairrows, T4=t4, PP1_descriptive=ppdesc))
            # Exact empirical ROC with tied scores handled at inclusive thresholds.
            pos = sorted(o['own_similarity'] for o in outcomes if o['control'] == 'C1' and o['own_similarity'] is not None)
            neg = sorted(negative)
            thresholds = np.unique(np.asarray(pos + neg, dtype=np.float64))[::-1]
            roc = [dict(threshold=float(np.nextafter(thresholds[0], np.inf)), tpr=0., fpr=0.)]
            roc += [dict(threshold=float(t), tpr=float(1 - np.searchsorted(pos, t, 'left') / len(pos)),
                         fpr=float(1 - np.searchsorted(neg, t, 'left') / len(neg))) for t in thresholds]
            write(out / f'{name}-roc.json', dict(meaning='pooled descriptor-only empirical ROC; registry pointer failures reported separately', points=roc))
            result['descriptors'][name] = summary
            save()
        d1, d2 = (result['descriptors'][n] for n in ('D1', 'D2'))
        selected = 'D1' if d1['decision'] == 'pass' else ('D2' if d1['decision'] == 'fail' and d2['decision'] == 'pass' else None)
        result['selected_descriptor'] = selected
        result['advance_to_2b'] = selected is not None
        result['timing_summary'] = dict(
            descriptor_extracted_images=sum(m['extracted_images'] for m in extraction_metrics),
            descriptor_extraction_seconds={n:sum(m['extraction_seconds'][n] for m in extraction_metrics) for n in DESCRIPTORS},
            descriptor_extraction_wall_seconds=sum(m['extraction_wall_seconds'] for m in extraction_metrics),
            descriptor_disk_load_seconds=sum(m['disk_load_seconds'] for m in extraction_metrics),
            lookup={arm:dict(calls=sum(m[arm]['calls'] for m in result['lookup_timing_invocations']),
                                 seconds=sum(m[arm]['seconds'] for m in result['lookup_timing_invocations']))
                    for arm in ('registry','fingerprint','cosine')})
        result['outcome'] = 'screen_pass_hypothesis' if selected else ('kill_rule_fired' if d1['decision'] == d2['decision'] == 'fail' else 'incomplete')
        invocation['status'] = 'completed'
    except Exception:
        result.update(outcome='incomplete', error=traceback.format_exc())
        invocation['status'] = 'incomplete'
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
