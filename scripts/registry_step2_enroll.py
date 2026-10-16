"""Fixed regenerate-and-enroll scenario; no writer or ownership-transfer operation.

The original alpha records are enrolled first. Beta records contain seed12
regenerated copies without re-embedding. A second query regenerates that copy
with seed13, at the same model and strength. Every registry has 48 records.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from registry_step1_transfer import ALPHA, BETA, MAIN, METHODS, SD21, journal, read, write


def classify(records, similarities, threshold, calls, radius):
    """Keep all threshold matches, deterministic best and enrollment-order effects."""
    def summarize(indices):
        matches = [i for i in indices if similarities[i] is not None and similarities[i] >= threshold]
        ranked = sorted(matches, key=lambda i: (-similarities[i], records[i]['record_id']))
        best = records[ranked[0]]['record_id'] if ranked else None
        tied = [records[i]['record_id'] for i in ranked if similarities[i] == similarities[ranked[0]]] if ranked else []
        owners = sorted({records[i]['owner'] for i in matches})
        first = min(matches, key=lambda i: records[i]['enrollment_index']) if matches else None
        return dict(candidate_count=len(indices), match_count=len(matches),
                    matches=[dict(record_id=records[i]['record_id'], owner=records[i]['owner'], cosine=similarities[i]) for i in ranked],
                    best_record=best, best_ties=tied, owners=owners,
                    enrollment_order_first_record=records[first]['record_id'] if first is not None else None,
                    enrollment_order_first_owner=records[first]['owner'] if first is not None else None,
                    enrollment_order_alone_can_favor_original_owner=bool(first is not None and records[first]['owner'] == ALPHA and owners != [ALPHA]))
    fingerprint = summarize(list(range(len(records))))
    candidates = []
    gates = {}
    for owner in (ALPHA, BETA):
        semantic = calls[owner]['semantic']
        decoded = semantic.get('decoded_code')
        gate = bool(semantic.get('found') and semantic.get('read') and decoded is not None)
        gates[owner] = dict(found_readable=gate, decoded_q=decoded)
        if gate:
            q = int(decoded, 16)
            candidates.extend(i for i,r in enumerate(records) if r['owner'] == owner and r.get('q') is not None and (q ^ int(r['q'], 16)).bit_count() <= radius)
    pointer = summarize(candidates)
    pointer['gates'] = gates
    pointer['attribution'] = ('original_owner_unique' if pointer['owners'] == [ALPHA] else
                              'wrong_owner' if pointer['owners'] == [BETA] else
                              'ambiguous_owners' if len(pointer['owners']) == 2 else 'no_attribution')
    return dict(fingerprint_only=fingerprint, pointer_registry=pointer)


def scenario_summary(rows,source_count=24):
    from collections import Counter
    summary = {}
    for model in ('sd15','sd21'):
        for strength in (.2,.4):
            for kind in ('exact_copy','further_regeneration'):
                selected = [r for r in rows.values() if r.get('phase') == 'evaluate' and r.get('model') == model and r.get('strength') == strength and r.get('kind') == kind]
                descriptors = sorted({d for r in selected for d in r.get('verification',{})})
                summary[f'{model}/{strength}/{kind}'] = dict(planned_sources=source_count, observed_sources=sum(r.get('status') == 'ok' for r in selected),
                    by_descriptor={d:dict(pointer_attribution=dict(Counter(r['verification'][d]['pointer_registry']['attribution'] for r in selected if r.get('status') == 'ok')),
                        pointer_original_record=sum(r['verification'][d]['pointer_registry']['best_record'] == f'alpha:{r["source_id"]}' for r in selected if r.get('status') == 'ok'),
                        fingerprint_original_record=sum(r['verification'][d]['fingerprint_only']['best_record'] == f'alpha:{r["source_id"]}' for r in selected if r.get('status') == 'ok'),
                        fingerprint_multiple_matches=sum(r['verification'][d]['fingerprint_only']['match_count'] > 1 for r in selected if r.get('status') == 'ok'),
                        fingerprint_both_owners=sum(len(r['verification'][d]['fingerprint_only']['owners']) > 1 for r in selected if r.get('status') == 'ok'),
                        fingerprint_order_can_favor_alpha=sum(r['verification'][d]['fingerprint_only']['enrollment_order_alone_can_favor_original_owner'] for r in selected if r.get('status') == 'ok')) for d in descriptors})
    return summary


class ScenarioAdapter:
    """Reference the screen's lossless descriptor files; write only new vectors locally."""
    def __init__(self, screen_dir, out, ev, budget):
        from registry_step2_screen import DescriptorCache
        self.np = __import__('numpy')
        self.screen = read(screen_dir/'run.json')
        indexpath = screen_dir/'descriptor-index.json'
        self.index = read(indexpath) if indexpath.exists() else {}
        self.cache = DescriptorCache(out,ev,ev.profile,
            MAIN/'.thesis-build/assets/freqmark-reconstruction-20261013/dino',budget)
        self.out = out
    def thresholds(self, method):
        if self.screen['config']['chosen_method'] != method:
            raise ValueError('Scenario method differs from screen')
        return {d:s['tau'] for d,s in self.screen['descriptors'].items() if s.get('tau') is not None}
    def extract(self, path):
        path = str(Path(path).resolve())
        if path in self.index:
            return self.index[path]
        self.cache.get(path)
        self.index[path] = self.cache.index[path]
        write(self.out/'descriptor-index.json',self.index)
        return self.index[path]
    def vector(self, descriptor_ref, descriptor):
        if descriptor_ref is None:
            return None
        with self.np.load(descriptor_ref['cache'],allow_pickle=False) as data:
            vector = data[descriptor]
        return vector if vector.size else None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chosen-method', choices=('e3-s1','f5-r2'), required=True)
    p.add_argument('--transfer-dir', type=Path, required=True)
    p.add_argument('--screen-dir', type=Path, required=True)
    p.add_argument('--source-split',choices=('development','calibration','evaluation'),default='development',
                   help='Original24 development, or a conditional fresh20/40 split')
    p.add_argument('--calibration-dir',type=Path,help='For fresh split scenarios, frozen calibration-thresholds.json directory')
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--max-seconds', type=float, required=True)
    p.add_argument('--parent-spent-seconds', type=float, default=0.)
    p.add_argument('--sd21-assets', type=Path, default=SD21)
    args = p.parse_args()
    if not 0 < args.max_seconds <= 14400 or not 0 <= args.parent_spent_seconds < 14400:
        raise ValueError('Scenario and parent must fit step2 cumulative four-hour budget')
    started = time.monotonic()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    transfer = read(args.transfer_dir/'run.json')
    inputs = journal(args.transfer_dir/'rows.jsonl')
    cohort = transfer['sources'] if args.source_split == 'development' else [s for s in transfer['sources'] if s.get('registry_split') == args.source_split]
    ids = sorted(s['source_id'] for s in cohort)
    expected = {'development':24,'calibration':20,'evaluation':40}[args.source_split]
    if len(ids) != expected or transfer['data_split'] != 'development':
        raise ValueError('Complete development cohort/split required')
    if args.source_split != 'development' and args.calibration_dir is None:
        raise ValueError('Fresh scenarios require frozen calibration thresholds')
    config = dict(chosen_method=args.chosen_method, transfer_dir=str(args.transfer_dir.resolve()),
                  screen_dir=str(args.screen_dir.resolve()), models=['sd15','sd21'], strengths=[.2,.4],
                  first_seed=12, further_seed=13, second_input='seed12 regenerated copy', no_reembedding=True,
                  registry_records=2*len(ids), source_split=args.source_split,
                  calibration_dir=str(args.calibration_dir.resolve()) if args.calibration_dir else None,
                  parent_spent_seconds=args.parent_spent_seconds, max_seconds=args.max_seconds,
                  added_side_information='trusted enrolled reference descriptors, owner and record lookup',
                  arbitrary_owner_security=False)
    commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    record = read(out/'run.json') if (out/'run.json').exists() else dict(schema='registry-regenerate-enroll-v1',commit=commit,
        command=sys.argv,config=config,data_split='development',usd=0,duration_seconds=0.,outcome='running',invocations=[])
    if record['config'] != config or record['commit'] != commit:
        raise ValueError('Resume config or commit differs')
    prior = record['duration_seconds']
    log = out/'rows.jsonl'
    if log.exists() and log.stat().st_size and not log.read_bytes().endswith(b'\n'):
        raw = log.read_bytes()
        end = raw.rfind(b'\n')+1
        (out/f'interrupted-tail-{time.time_ns()}.bin').write_bytes(raw[end:])
        log.write_bytes(raw[:end])
    rows = journal(log)
    invocation = dict(command=sys.argv,status='running')
    record['invocations'].append(invocation)
    def save():
        record['duration_seconds'] = prior + time.monotonic()-started
        invocation['duration_seconds'] = time.monotonic()-started
        record['summary'] = scenario_summary(rows,len(ids))
        write(out/'run.json',record)
    def budget():
        total = prior + time.monotonic()-started
        if total >= args.max_seconds or total + args.parent_spent_seconds >= 14400:
            raise RuntimeError('Cumulative step2 scenario budget reached')
    def emit(row):
        with (out/'rows.jsonl').open('a',encoding='utf-8') as handle:
            handle.write(json.dumps(row,allow_nan=False)+'\n')
            handle.flush()
        rows[row['id']] = row.copy()
        save()
    save()
    try:
        budget()
        import numpy as np
        import torch
        from PIL import Image
        from diffusers import AutoencoderKL,DDIMScheduler,StableDiffusionImg2ImgPipeline
        from journal_vae_probe import Evaluator
        from journal_bch_readout import detect_rgb as e3_detect
        from f4_transfer_probe import ASSETS
        import three_threat_models as models
        torch.set_num_threads(4)
        models.block_network()
        ev = Evaluator()
        adapter = ScenarioAdapter(args.screen_dir,out,ev,budget)
        thresholds = adapter.thresholds(args.chosen_method)
        if args.calibration_dir:
            frozen = read(args.calibration_dir/'calibration-thresholds.json')
            if frozen['chosen_method'] != args.chosen_method:
                raise ValueError('Calibration method differs')
            thresholds = {d:s['tau'] for d,s in frozen['descriptors'].items()}
        if not thresholds:
            raise ValueError('Screen thresholds are unavailable')
        record['thresholds'] = thresholds
        radius = int(ev.profile['decision']['semantic_radius'])
        def load(path):
            with Image.open(path) as im:
                if im.mode != 'RGB' or im.size != (512,512):
                    raise ValueError('512-square RGB8 required')
                return np.asarray(im,np.uint8).copy()
        def observe(path):
            rgb = load(path)
            features,latent = ev.features(rgb,7),ev.reader.latent(rgb)
            calls = {o:(e3_detect(rgb,latent,o,ev.profile,features,binding='soft',roster_size=1) if args.chosen_method == 'e3-s1'
                        else ev.detect(rgb,'f5',o,features,latent)) for o in (ALPHA,BETA)}
            return dict(calls=calls,descriptors=adapter.extract(path))
        for model in ('sd15','sd21'):
            pipe = None
            for strength in (.2,.4):
                # All later records exist before any query in this cell is evaluated.
                registry = []
                copies = {}
                for owner in (ALPHA,BETA):
                    for sid in ids:
                        key = f'enroll:{model}:{strength}:{owner}:{sid}'
                        if rows.get(key,{}).get('status') not in ('ok','input_unavailable'):
                            budget()
                            source = inputs[f'clean:{sid}:{args.chosen_method}:C1'] if owner == ALPHA else inputs[f'{model}:{sid}:{strength}:12:{args.chosen_method}']
                            if source['status'] != 'ok':
                                row = dict(id=key,phase='enroll',model=model,strength=strength,source_id=sid,owner=owner,
                                    q=None,h=None,descriptors=None,image=None,status='input_unavailable',input_status=source['status'])
                            else:
                                image = source['image']
                                observation = observe(image)
                                # Recomputed beta q is obtained from beta's own native detector call.
                                q = source['payload']['q'] if owner == ALPHA else observation['calls'][BETA]['semantic_code']
                                row = dict(id=key,phase='enroll',model=model,strength=strength,source_id=sid,owner=owner,
                                    q=q,h=source['payload']['h'] if owner == ALPHA else observation['calls'][BETA].get('perceptual_hash'),q_basis='original supplied alpha q' if owner == ALPHA else 'native recomputed beta semantic_code',
                                    image=image,**observation,status='ok')
                            emit(row)
                        enrolled = rows[key]
                        registry.append(dict(record_id=f'{"alpha" if owner == ALPHA else "beta"}:{sid}',owner=owner,q=enrolled['q'],h=enrolled['h'],
                            source_id=sid,enrollment_index=len(registry),descriptors=enrolled['descriptors']))
                        if owner == BETA:
                            copies[sid] = enrolled
                write(out/f'registry-{model}-{strength}.json',registry)
                for sid in ids:
                    for kind in ('exact_copy','further_regeneration'):
                        key = f'evaluate:{model}:{strength}:{sid}:{kind}'
                        if rows.get(key,{}).get('status') in ('ok','safety_blocked','input_unavailable'):
                            continue
                        budget()
                        row = dict(id=key,phase='evaluate',model=model,strength=strength,source_id=sid,kind=kind,status='running')
                        old = rows.get(key,{})
                        row['attempt'] = old.get('attempt',0)+1
                        emit(row)
                        tick = time.monotonic()
                        try:
                            if copies[sid]['status'] != 'ok':
                                row.update(status='input_unavailable',input_status=copies[sid]['status'])
                                continue
                            if kind == 'exact_copy':
                                image = copies[sid]['image']
                                observation = {k:copies[sid][k] for k in ('calls','descriptors')}
                            else:
                                if pipe is None:
                                    if model == 'sd15':
                                        pipe = models.load_regenerator(ASSETS)
                                    else:
                                        vae = AutoencoderKL.from_pretrained(args.sd21_assets/'vae',local_files_only=True,use_safetensors=True,torch_dtype=torch.float16)
                                        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(args.sd21_assets,vae=vae,variant='fp16',
                                            use_safetensors=True,local_files_only=True,torch_dtype=torch.float16,safety_checker=None,requires_safety_checker=False)
                                        pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
                                        pipe.set_progress_bar_config(disable=True)
                                        pipe.to('cuda')
                                    record.setdefault('models',{})[model] = dict(safety_checker=pipe.safety_checker is not None,scheduler=dict(pipe.scheduler.config))
                                    save()
                                with torch.inference_mode():
                                    result = pipe(prompt='',negative_prompt='',image=Image.fromarray(load(copies[sid]['image'])),strength=strength,
                                        num_inference_steps=20,eta=0.,guidance_scale=1.,generator=torch.Generator(device='cuda').manual_seed(13),
                                        num_images_per_prompt=1,output_type='pil',return_dict=True)
                                image = str(out/f'{model}-{strength}-{sid}-further-attempt{row["attempt"]}.png')
                                result.images[0].save(image)
                                row.update(image=image,safety_flags=result.nsfw_content_detected)
                                if model == 'sd15':
                                    models.validate_generated(result)
                                observation = observe(image)
                            row.update(image=image,**observation,registry_size=2*len(ids),
                                       registry_available_records=sum(r['descriptors'] is not None for r in registry),verification={})
                            for descriptor,threshold in thresholds.items():
                                vector = adapter.vector(observation['descriptors'],descriptor)
                                reference_vectors = [adapter.vector(r['descriptors'],descriptor) for r in registry]
                                similarities = [float(np.dot(vector,v)) if vector is not None and v is not None else None for v in reference_vectors]
                                row['verification'][descriptor] = classify(registry,similarities,threshold,observation['calls'],radius)
                                row['verification'][descriptor]['unavailable_scores'] = sum(v is None for v in similarities)
                            row['status'] = 'ok'
                        except Exception as exc:
                            if str(exc) == 'safety_checker_blocked_output':
                                row.update(status='safety_blocked',error=str(exc))
                            else:
                                row.update(status='error',error=traceback.format_exc())
                                raise
                        finally:
                            row['duration_seconds'] = time.monotonic()-tick
                            emit(row)
                if pipe is not None:
                    pipe.to('cpu')
                    del pipe
                    pipe = None
                    torch.cuda.empty_cache()
        record['outcome'] = 'completed'
        invocation['status'] = 'completed'
    except Exception:
        record['outcome'] = 'incomplete'
        invocation.update(status='incomplete',error=traceback.format_exc())
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
