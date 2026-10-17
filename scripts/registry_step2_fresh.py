"""Conditional 60-source registry development construction and regeneration.

This is a scientific driver, not a launcher. It refuses execution unless the
consulted step-2a screen passed for the chosen method. Threshold calibration and
evaluation analysis are separate; this script never selects a threshold.
"""
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
sys.path[:0] = [str(ROOT),str(ROOT/'scripts')]
from registry_step1_transfer import ALPHA,BETA,SD21,STRENGTHS,SEEDS,journal,read,write


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--round3-evaluation-only', action='store_true', help='Authorized fixed 40-source round3 data cohort; no calibration')
    p.add_argument('--phase',choices=('embed','sd15','sd21'),required=True)
    p.add_argument('--sources',type=Path,required=True)
    p.add_argument('--screen-dir',type=Path,required=True)
    p.add_argument('--chosen-method',choices=('e3-s1','f5-r2'),required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--parent-spent-seconds',type=float,required=True,
                   help='All other step2 time, including screen, scenario and later phases on resume')
    p.add_argument('--max-seconds',type=float,default=14400.)
    p.add_argument('--sd21-assets',type=Path,default=SD21)
    a = p.parse_args()
    if not 0 < a.max_seconds <= 14400 or a.parent_spent_seconds < 0:
        raise ValueError('Step2 has at most four cumulative hours')
    screen = read(a.screen_dir/'run.json')
    if screen.get('outcome') != 'screen_pass_hypothesis' or screen['config']['chosen_method'] != a.chosen_method:
        raise ValueError('Conditional fresh experiment requires chosen-method step2a pass')
    selected = screen.get('selected_descriptor')
    if selected not in ('D1','D2') or screen['descriptors'][selected].get('decision') != 'pass':
        raise ValueError('A complete passing primary/fallback descriptor is required')
    manifest = read(a.sources)
    sources = manifest if isinstance(manifest,list) else manifest.get('sources',manifest.get('selected'))
    sources = copy.deepcopy(sources)
    expected_count = 40 if a.round3_evaluation_only else 60
    if len(sources) != expected_count or len({s['source_id'] for s in sources}) != expected_count:
        raise ValueError('Exactly sixty distinct development sources required')
    for i,s in enumerate(sources):
        expected = 'evaluation' if a.round3_evaluation_only else ('calibration' if i < 20 else 'evaluation')
        supplied_split = s.get('registry_split',s.get('split'))
        if supplied_split is not None and supplied_split != expected:
            raise ValueError('First20 calibration,last40 evaluation order differs')
        if s.get('development_reserved') is not True and s.get('data_split') != 'development-reserved':
            raise ValueError('Every source must be explicitly development reserved')
        if not s.get('canonical_path'):
            raise ValueError('Metadata-only selection needs acquired canonical image paths')
        s['registry_split'] = expected
    out = a.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    started = time.monotonic()
    commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    config = dict(sources_path=str(a.sources.resolve()),sources=sources,screen_dir=str(a.screen_dir.resolve()),
        screen_commit=screen['commit'],chosen_method=a.chosen_method,selected_descriptor=selected,
        strengths=list(STRENGTHS),seeds=list(SEEDS),steps=20,prompt='',negative_prompt='',guidance_scale=1.,eta=0.,
        sd21_assets=str(a.sd21_assets.resolve()),split='round3 all40 evaluation' if a.round3_evaluation_only else 'first20 calibration,last40 evaluation',
        side_information='trusted enrolled reference descriptors, owner and registry record lookup',
        quality_matched=False,human_admissibility='missing',cap_seconds=a.max_seconds)
    if (out/'run.json').exists():
        record = read(out/'run.json')
        if record['commit'] != commit or record['config'] != config:
            raise ValueError('Resume commit/config differs')
    else:
        record = dict(schema='registry-step2-fresh-v1',commit=commit,command=sys.argv,config=config,data_split='development',
            usd=0,sources=sources,duration_seconds=0.,phase_seconds={},phase_status={},outcome='running',invocations=[])
    prior = record['duration_seconds']
    prior_phase = record['phase_seconds'].get(a.phase,0.)
    invocation = dict(command=sys.argv,phase=a.phase,status='running',other_step2_seconds=a.parent_spent_seconds)
    record['invocations'].append(invocation)
    log = out/'rows.jsonl'
    if log.exists() and log.stat().st_size and not log.read_bytes().endswith(b'\n'):
        raw = log.read_bytes()
        end = raw.rfind(b'\n')+1
        (out/f'interrupted-tail-{time.time_ns()}.bin').write_bytes(raw[end:])
        log.write_bytes(raw[:end])
    rows = journal(log)
    def save():
        duration = time.monotonic()-started
        record['duration_seconds'] = prior+duration
        record['step2_accounted_seconds'] = prior+duration+a.parent_spent_seconds
        record['phase_seconds'][a.phase] = prior_phase+duration
        invocation['duration_seconds'] = duration
        write(out/'run.json',record)
    def budget():
        if prior+time.monotonic()-started+a.parent_spent_seconds >= a.max_seconds:
            raise TimeoutError('Four-hour cumulative step2 budget reached')
    def emit(row):
        with log.open('a',encoding='utf-8') as h:
            h.write(json.dumps(row,allow_nan=False)+'\n')
            h.flush()
        rows[row['id']] = copy.deepcopy(row)
        save()
    def done(rid):
        return rows.get(rid,{}).get('status') in ('ok','safety_blocked','scientific_failure','input_unavailable')
    def attempt(rid,source,**fields):
        row = dict(id=rid,source_id=source['source_id'],registry_split=source['registry_split'],
                   phase=a.phase,status='running',attempt=rows.get(rid,{}).get('attempt',0)+1,**fields)
        emit(row)
        return row
    save()
    try:
        budget()
        import numpy as np
        import torch
        import diffusers
        from PIL import Image
        from diffusers import AutoencoderKL,DDIMScheduler,StableDiffusionImg2ImgPipeline
        from f4_transfer_probe import ASSETS
        from journal_vae_probe import Evaluator,SDXL
        from journal_e3_writer import supply_f5,embed
        from journal_bch_readout import detect_rgb as e3_detect
        from m1b_e3_s1_analysis import predicates,strict_quality
        import three_threat_models as models
        if diffusers.__version__ != '0.35.1':
            raise ValueError('Pinned diffusers0.35.1 required')
        torch.set_num_threads(4)
        models.block_network()
        loadtick = time.monotonic()
        ev = Evaluator()
        record['environment'] = dict(torch=torch.__version__,diffusers=diffusers.__version__,gpu=torch.cuda.get_device_name(0),profile=ev.profile)
        pipe = other = channel = None
        if a.phase == 'sd15' or (a.phase == 'embed' and a.chosen_method == 'e3-s1'):
            pipe = models.load_regenerator(ASSETS)
        if a.phase == 'sd21':
            vae = AutoencoderKL.from_pretrained(a.sd21_assets/'vae',local_files_only=True,use_safetensors=True,torch_dtype=torch.float16)
            pipe = StableDiffusionImg2ImgPipeline.from_pretrained(a.sd21_assets,vae=vae,variant='fp16',local_files_only=True,
                use_safetensors=True,torch_dtype=torch.float16,safety_checker=None,requires_safety_checker=False)
            pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
            pipe.set_progress_bar_config(disable=True)
            pipe.to('cuda')
        if a.phase == 'embed' and a.chosen_method == 'e3-s1':
            from journal_ddim_channel import DifferentiableDDIM
            channel = DifferentiableDDIM(pipe)
            other = AutoencoderKL.from_pretrained(SDXL,local_files_only=True,use_safetensors=True,torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        invocation['model_loading_seconds'] = time.monotonic()-loadtick
        if pipe is not None:
            record.setdefault('models',{})[a.phase] = dict(safety_checker=pipe.safety_checker is not None,scheduler=dict(pipe.scheduler.config))
        save()
        def load(path):
            with Image.open(path) as image:
                if image.mode != 'RGB' or image.size != (512,512):
                    raise ValueError('RGB8 512-square required')
                return np.asarray(image,np.uint8).copy()
        def calls(rgb,payload,control):
            features,latent = ev.features(rgb,7),ev.reader.latent(rgb)
            detections,endpoints,times = {},{},{}
            for owner in ((ALPHA,BETA) if control == 'C1' else (ALPHA,)):
                budget()
                tick = time.monotonic()
                call = (e3_detect(rgb,latent,owner,ev.profile,features,binding='soft',roster_size=1)
                        if a.chosen_method == 'e3-s1' else ev.detect(rgb,'f5',owner,features,latent))
                detections[owner] = call
                endpoints[owner] = predicates(call,payload if control == 'C1' and owner == ALPHA else None)
                times[owner] = time.monotonic()-tick
            return dict(calls=detections,endpoints=endpoints,detector_seconds=times)
        for source in sources:
            sid,method = source['source_id'],a.chosen_method
            canonical = load(source['canonical_path'])
            if a.phase == 'embed':
                c0_id = f'clean:{sid}:{method}:C0'
                if not done(c0_id):
                    row = attempt(c0_id,source,method=method,control='C0',image=source['canonical_path'])
                    row.update(**calls(canonical,None,'C0'),status='ok')
                    emit(row)
                supplier_id = f'supplier:{sid}:{method}'
                if not done(supplier_id):
                    budget()
                    row = attempt(supplier_id,source,method=method)
                    folder = out/str(sid)/f'supplier-attempt{row["attempt"]}'
                    result = supply_f5(canonical,ev,folder,budget)
                    row['supplier'] = result
                    if result['status'] == 'ok':
                        row['status'] = 'ok'
                    elif 'Fresh F5 bootstrap native channels unreadable' in result.get('error',''):
                        row['status'] = 'scientific_failure'
                    else:
                        row['status'] = 'error'
                    emit(row)
                    if row['status'] == 'error':
                        raise RuntimeError(result.get('error','Unexplained supplier failure'))
                supplier = rows[supplier_id]['supplier']
                rid = f'clean:{sid}:{method}:C1'
                if not done(rid):
                    budget()
                    row = attempt(rid,source,method=method,control='C1')
                    tick = time.monotonic()
                    try:
                        if supplier['status'] != 'ok':
                            row.update(status='input_unavailable',supplier_status=supplier['status'])
                            continue
                        image,payload = supplier['bootstrap_image'],supplier['payload']
                        embedding_seconds = supplier['bootstrap_seconds']
                        if method == 'e3-s1':
                            result = embed(canonical,ALPHA,supplier['q'],supplier['h'],ev,other,channel,
                                           out/str(sid)/f'writer-attempt{row["attempt"]}',budget)
                            row['writer'] = result
                            if result.get('error'):
                                raise RuntimeError(result['error'])
                            image = result.get('final_image')
                            if image is None:
                                row.update(status='scientific_failure',error='Frozen writer returned no image')
                                continue
                            embedding_seconds = supplier['duration_seconds']+result['duration_seconds']
                        rgb = load(image)
                        row.update(image=image,payload=payload,payload_basis='intended q; operational supplier h; E3 explicitly carries supplied h',
                            quality=ev.metrics(canonical,rgb),embedding_seconds=embedding_seconds,
                            **calls(rgb,payload,'C1'),status='ok')
                        row['strict_quality'] = bool(strict_quality(row['quality']))
                    except Exception:
                        row.update(status='error',error=traceback.format_exc())
                        raise
                    finally:
                        row['duration_seconds'] = time.monotonic()-tick
                        emit(row)
            else:
                clean = rows.get(f'clean:{sid}:{method}:C1')
                if clean is None or clean['status'] not in ('ok','input_unavailable','scientific_failure'):
                    raise ValueError('Finish embedding before regeneration')
                for strength in STRENGTHS:
                    for seed in SEEDS:
                        for arm in ('C0',method):
                            rid = f'{a.phase}:{sid}:{strength}:{seed}:{arm}'
                            if done(rid):
                                continue
                            budget()
                            row = attempt(rid,source,strength=strength,seed=seed,arm=arm)
                            tick = time.monotonic()
                            try:
                                if arm != 'C0' and clean['status'] != 'ok':
                                    row.update(status='input_unavailable',input_status=clean['status'])
                                    continue
                                input_image = source['canonical_path'] if arm == 'C0' else clean['image']
                                inp = load(input_image)
                                row.update(input_image=input_image,transformation_attempted=True)
                                emit(row)
                                regen_tick = time.monotonic()
                                with torch.inference_mode():
                                    result = pipe(prompt='',negative_prompt='',image=Image.fromarray(inp),strength=strength,
                                        num_inference_steps=20,eta=0.,guidance_scale=1.,generator=torch.Generator(device='cuda').manual_seed(seed),
                                        num_images_per_prompt=1,output_type='pil',return_dict=True)
                                torch.cuda.synchronize()
                                image = str(out/(rid.replace(':','-')+f'-attempt{row["attempt"]}.png'))
                                result.images[0].save(image)
                                row.update(image=image,safety_flags=result.nsfw_content_detected,regeneration_seconds=time.monotonic()-regen_tick)
                                if a.phase == 'sd15':
                                    models.validate_generated(result)
                                rgb = load(image)
                                row.update(readouts={method:calls(rgb,None if arm == 'C0' else clean['payload'],'C0' if arm == 'C0' else 'C1')},
                                           quality_input=ev.metrics(inp,rgb),status='ok')
                            except Exception as exc:
                                if str(exc) == 'safety_checker_blocked_output':
                                    row.update(status='safety_blocked',error=str(exc))
                                else:
                                    row.update(status='error',error=traceback.format_exc())
                                    raise
                            finally:
                                row['duration_seconds'] = time.monotonic()-tick
                                emit(row)
                            print(json.dumps(dict(id=rid,status=row['status'])),flush=True)
        budget()
        invocation['status'] = 'completed'
        record['phase_status'][a.phase] = 'completed'
        record['outcome'] = 'completed' if all(record['phase_status'].get(p) == 'completed' for p in ('embed','sd15','sd21')) else 'partial'
    except Exception:
        invocation.update(status='incomplete',error=traceback.format_exc())
        record['phase_status'][a.phase] = 'incomplete'
        record['outcome'] = 'incomplete'
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
