"""Frozen C-L100 schedule-only synthetic carrier diagnosis; no import-time models.

Oracle predecode traces are diagnostics, never image-detector successes.
Fresh output only: preserve failed/interrupted attempts, retry in a new directory.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_progressive_latent as original
from m1_gaussian_shading import require_committed
from m1_phasemark import working_set_bytes
MAIN=original.MAIN
VERSION='m1-progressive-phase-diagnostic-v1'
SOURCE=MAIN/'.thesis-build/dev-runs/20261004-0031-progressive'
SOURCE_SHA='c3436690fd0ae549d0a2a3ac71c00e43105d753697f0b26ce61984ccee62ff94'
OLD_SCRIPT_SHA='1ab50ebf7d94883c80af623b1f14f1a7c6412c1ea4b8a83b8e06b80be0e52914'
ORIGINAL='1011010001101001'
COMPLEMENT='0100101110010110'
ARMS=('C0-replay','C-E100-replay','C-L100','C-L100-complement')
STAGES=('terminal_predecode','clipped_float_cycle','clean_rgb8','additional_vae_rgb8')
sha=original.sha
write=original.write


def configuration():
    cases=json.loads((ROOT/'research/m1-progressive-synthetic.json').read_text())['cases']
    return dict(schema_version=VERSION,data_split='synthetic',cases=cases,arms=list(ARMS),
        alpha=.5,eta=100.,steps=50,guidance_scale=7.5,sampler_eta=0.,payload=ORIGINAL,
        complement=COMPLEMENT,presence_matches=14,source_run=str(SOURCE),source_run_sha256=SOURCE_SHA,
        original_script_sha256=OLD_SCRIPT_SHA,original_config=original.CONFIG,
        run_seconds_cap=300,gpu_budget_bytes=10*1024**3,ram_budget_bytes=16*1024**3,
        artifact_budget_bytes=250*1024**2)


def planned():
    return [dict(id=f'seed{s}-{arm}',seed=s,arm=arm,outcome='planned',
        intended_payload=COMPLEMENT if arm.endswith('complement') else ORIGINAL,
        original_payload=ORIGINAL,conditions={c:dict(outcome='planned') for c in ('clean','vae')},
        human_visual_verdict=None) for s in range(1000,1004) for arm in ARMS]


def guided_indices(arm):
    if arm not in ARMS:raise ValueError('Unplanned arm')
    return [] if arm=='C0-replay' else list(range(25)) if arm=='C-E100-replay' else list(range(25,50))


def evaluate_word(word,intended):
    if len(word)!=16 or len(intended)!=16 or set(word+intended)-set('01'):raise ValueError('Binary16 words required')
    scores={name:sum(a==b for a,b in zip(word,target)) for name,target in
        (('intended',intended),('original',ORIGINAL),('complement',COMPLEMENT))}
    return dict(bits=word,intended_payload=intended,original_payload=ORIGINAL,complement_payload=COMPLEMENT,
        **{name+'_matches':v for name,v in scores.items()},
        **{name+'_bit_accuracy':v/16 for name,v in scores.items()},
        **{name+'_present':v>=14 for name,v in scores.items()})


def target(alpha,basis,payload):
    import torch
    out=torch.zeros((64,64),device=basis.device);mask=torch.zeros_like(out)
    for i,(u,v) in enumerate(original.positions()):
        out[u,v]=alpha*(1 if payload[i//8]=='1' else -1);mask[u,v]=1
    return out,mask


def stage(plane,basis,intended,alpha=.5):
    import torch
    coeff=original.dct2(plane.float(),basis)[tuple(zip(*original.positions()))]
    signs=(coeff>0).reshape(16,8)
    word=''.join(str(int(x)) for x in (signs.sum(1)>4).tolist())
    expected=torch.tensor([alpha*(1 if b=='1' else -1) for b in intended for _ in range(8)],device=coeff.device)
    values=coeff.tolist()
    return {**evaluate_word(word,intended), 'selected_coefficients':values,
        'coefficient_sign_matches':int(((coeff>0)==(expected>0)).sum()),
        'target_mse':float((coeff-expected).square().mean()),'zero_count':int((coeff==0).sum()),
        'nonfinite_count':int((~torch.isfinite(coeff)).sum()),
        'wrong_payload_queries':original.wrong_payload_scores([int(b) for b in word])}


def ddim_factors(scheduler,t):
    prev=int(t)-scheduler.config.num_train_timesteps//scheduler.num_inference_steps
    a=float(scheduler.alphas_cumprod[int(t)])
    ap=float(scheduler.alphas_cumprod[prev] if prev>=0 else scheduler.final_alpha_cumprod)
    return a,ap,ap**.5-(a*(1-ap)/(1-a))**.5


def replay_receipts(source):
    if source.get('outcome')!='completed' or source.get('script_sha256')!=OLD_SCRIPT_SHA:
        raise ValueError('Original completed source/script receipt required')
    out={}
    for s in range(1000,1004):
        for arm,ident in (('C0-replay',f'seed{s}-C0'),('C-E100-replay',f'seed{s}-a0.5-e100.0')):
            rows=[r for r in source['rows'] if r['id']==ident and r['outcome']=='completed']
            if len(rows)!=1:raise ValueError('Missing/duplicate original replay row')
            for channel in ('clean','vae'):
                values=[a for a in rows[0]['artifacts'] if a['path'].endswith('-'+channel+'.png')]
                if len(values)!=1:raise ValueError('Missing/duplicate original replay PNG receipt')
                a=values[0];path=original.artifact_path(SOURCE,a['path'])
                if sha(path)!=a['sha256']:raise ValueError('Original PNG hash differs')
                out[(s,arm,channel)]=a
    return out


def replay_status(expected,actual):
    return dict(expected_sha256=expected,actual_sha256=actual,matched=expected==actual,
        attribution='exact-PNG-replay' if expected==actual else 'replay-attribution-failure',
        original_latent_hash=None,original_latent_hash_availability='not retained')


def gates(rows):
    complete={r['id'] for r in rows}=={r['id'] for r in planned()} and len(rows)==16 and all(r.get('outcome')=='completed' and
        set(r['conditions'])=={'clean','vae'} and
        all(v.get('outcome')=='completed' for v in r['conditions'].values()) for r in rows)
    if not complete:return dict(complete=False,replay=None,late_carrier=None,c0_absence=None,late_quality=None)
    replay=all(v.get('replay',{}).get('matched') is True for r in rows if r['arm'] in ARMS[:2]
        for v in r['conditions'].values())
    late=[r for r in rows if r['arm'] in ('C-L100','C-L100-complement')]
    c0=[r for r in rows if r['arm']=='C0-replay']
    carrier=all(v['native_vae_dct']['intended_present'] for r in late for v in r['conditions'].values())
    absent=all(not v['native_vae_dct']['original_present'] and not v['native_vae_dct']['complement_present']
        for r in c0 for v in r['conditions'].values())
    quality=all(r['quality_to_new_C0']['quality_admissible'] for r in late)
    return dict(complete=True,replay=replay,late_carrier=carrier,c0_absence=absent,late_quality=quality,
        necessary_condition=(carrier and absent) if replay else None,
        quality_attribution=quality if replay else None,late_clean_denominator=8,late_cycle_denominator=8,
        c0_source_clusters=4,caveat='Generated counterfactual carrier diagnosis; not independent image trials or M1 acceptance')


def generate(pipe,case,arm,intended,save_array,trace,check,device='cuda'):
    import torch
    from diffusers import DDIMScheduler
    from three_threat_models import DDIM_CONFIG
    pipe.scheduler=DDIMScheduler(**DDIM_CONFIG);pipe.scheduler.set_timesteps(50,device=device)
    basis=original.dct_matrix(64,device=device);targ,mask=target(.5,basis,intended)
    indices=guided_indices(arm)
    with torch.inference_mode():
        embeddings,unconditional=pipe.encode_prompt(case['prompt'],device,1,True,negative_prompt='')[:2]
        embeddings=torch.cat([unconditional,embeddings])
        z=torch.randn((1,4,64,64),generator=torch.Generator(device=device).manual_seed(case['seed']),
            device=device,dtype=pipe.unet.dtype)*pipe.scheduler.init_noise_sigma
        initial=save_array('initial_latent',z)
        for i,t in enumerate(pipe.scheduler.timesteps):
            check();before=z
            raw=pipe.unet(pipe.scheduler.scale_model_input(torch.cat([z,z]),t),t,
                encoder_hidden_states=embeddings,return_dict=False)[0]
            u,c=raw.chunk(2);eps=u+7.5*(c-u)
            a=pipe.scheduler.alphas_cumprod[int(t)].to(device=device,dtype=torch.float32)
            ordinary=(z.float()-(1-a).sqrt()*eps.float())/a.sqrt()
            corrected=ordinary.clone();grad=torch.zeros((64,64),device=device)
            guided=i in indices
            supplied=eps
            proposed=eps.float()
            if guided:
                grad=original.analytic_gradient(ordinary[0,0],targ,mask,basis)
                corrected[0,0]-=100.*grad
                proposed=(z.float()-a.sqrt()*corrected)/(1-a).sqrt()
                supplied=proposed.to(pipe.unet.dtype)
            effective=(z.float()-(1-a).sqrt()*supplied.float())/a.sqrt()
            # Stateless eta0 DDIM algebra on the identical current state/epsilon.
            aa=pipe.scheduler.alphas_cumprod[int(t)]
            prev=int(t)-1000//50
            ap=pipe.scheduler.alphas_cumprod[prev] if prev>=0 else pipe.scheduler.final_alpha_cumprod
            ordinary_step_clean=(before-(1-aa).sqrt()*eps)/aa.sqrt()
            unmarked=ap.sqrt()*ordinary_step_clean+(1-ap).sqrt()*eps
            z=pipe.scheduler.step(supplied,t,before,eta=0.,return_dict=False)[0]
            _,_,q=ddim_factors(pipe.scheduler,t)
            delta=corrected-ordinary;observed=z.float()-unmarked.float()
            changed=(supplied!=eps)
            trace(dict(step_index=i,timestep=int(t),guided=guided,q_t=q,
                stages={name:stage(value[0,0],basis,intended) for name,value in
                    (('ordinary_predicted_clean',ordinary),('corrected_predicted_clean',corrected),
                     ('effective_fp16_predicted_clean',effective),('actual_noisy_scheduler_output',z))},
                gradient_l2=float(grad.norm()),intended_clean_correction_l2=float(delta.norm()),
                epsilon_correction_before_cast_l2=float((proposed-eps.float()).norm()),
                epsilon_correction_after_cast_l2=float((supplied.float()-eps.float()).norm()),
                changed_channel0_fraction=float(changed[:,0].float().mean()),
                changed_other_channels_count=int(changed[:,1:].sum()),
                supplied_epsilon_zero_count=int((supplied==0).sum()),
                supplied_epsilon_nonfinite_count=int((~torch.isfinite(supplied)).sum()),
                ordinary_epsilon_dtype=str(eps.dtype),supplied_epsilon_dtype=str(supplied.dtype),
                predicted_clean_dtype=str(ordinary.dtype),scheduler_output_dtype=str(z.dtype),
                local_scheduler_displacement_l2=float(observed.norm()),
                local_formula_discrepancy_l2=float((observed-q*delta).norm())))
            if not bool(torch.isfinite(z).all()):raise ValueError('Nonfinite denoising state')
        final=save_array('terminal_latent',z)
        terminal=stage(z[0,0],basis,intended)
        decoded=pipe.vae.decode(z/pipe.vae.config.scaling_factor,return_dict=False)[0]
        decoder=save_array('decoder_float',decoded)
        decoded,flags=pipe.run_safety_checker(decoded,device,pipe.vae.dtype)
        if flags is None or len(flags)!=1 or bool(flags[0]):raise RuntimeError('Safety checker incomplete/blocked')
        clipped=decoded.clamp(-1,1)
        clipped_receipt=save_array('clipped_decoder_float',clipped)
        float_z=pipe.vae.encode(clipped).latent_dist.mode()*pipe.vae.config.scaling_factor
        float_receipt=save_array('clipped_float_cycle_latent',float_z)
        image=pipe.image_processor.postprocess(decoded,output_type='pil',do_denormalize=[True])[0]
    return image,dict(initial_latent=initial,terminal_latent=final,decoder_float=decoder,
        clipped_decoder_float=clipped_receipt,clipped_float_cycle_latent=float_receipt,
        clipping_fraction=float((decoded!=clipped).float().mean()),
        timesteps=[int(t) for t in pipe.scheduler.timesteps],guided_step_indices=indices,safety_flag=False,
        readout_stages={'terminal_predecode':dict(terminal,eligible_image_detector=False),
            'clipped_float_cycle':dict(stage(float_z[0,0],basis,intended),eligible_image_detector=False)})


def run(manifest_path,output):
    output=Path(output).resolve();manifest_path=Path(manifest_path).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN development output required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    rows=planned();record=dict(schema_version=VERSION,command=sys.argv,data_split='synthetic',
        seeds=list(range(1000,1004)),outcome='started',duration_seconds=0,rows=rows,config={},human_visual_verdict=None)
    def checkpoint():
        record['duration_seconds']=time.monotonic()-started;write(output/'run.json',record)
        write(output/'conditions.json',[dict(generation_id=r['id'],channel=c,**v) for r in rows for c,v in r['conditions'].items()])
    def event(value):
        with (output/'rows.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(dict(seconds=time.monotonic()-started,**value),allow_nan=False)+'\n');f.flush()
    checkpoint()
    active=None
    try:
        cfg=json.loads(manifest_path.read_text());record['config']=cfg
        if cfg!=configuration():raise ValueError('Exact frozen phase diagnostic manifest required')
        dependencies=[Path(__file__),manifest_path,ROOT/'research/m1-progressive-diagnosis.md',
            ROOT/'research/m1-progressive-synthetic.json',ROOT/'scripts/m1_progressive_latent.py',
            ROOT/'scripts/m1_gaussian_shading.py',ROOT/'scripts/m1_phasemark.py',
            ROOT/'scripts/three_threat_models.py',ROOT/'scripts/three_threat_protocol.py',
            ROOT/'scripts/m1_latent_reconstruction.py',ROOT/'scripts/check_a6_lpips_assets.py',
            ROOT/'scripts/verify_science_assets.py',ROOT/'scripts/a6_clip_visual.py',ROOT/'research/a6-candidate-model-assets.json']
        record.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            committed_files=require_committed(dependencies),manifest_sha256=sha(manifest_path))
        if sha(ROOT/'scripts/m1_progressive_latent.py')!=OLD_SCRIPT_SHA:raise ValueError('Original working script receipt differs')
        if sha(SOURCE/'run.json')!=SOURCE_SHA:raise ValueError('Original source run receipt differs')
        source=json.loads((SOURCE/'run.json').read_text());old=replay_receipts(source)
        (output/'manifest.json').write_bytes(manifest_path.read_bytes())
        record['source_receipts']={'run_sha256':SOURCE_SHA,'replay_pngs':{str(k):v for k,v in old.items()}}
        record['planned_counts']=dict(generations=16,image_conditions=32,unet_calls=800,source_clusters=4)
        checkpoint()
        from three_threat_models import block_network,verify_assets,load_lpips,lpips_score
        block_network()
        import torch
        import numpy as np
        from PIL import Image
        from diffusers import StableDiffusionPipeline
        from m1_latent_reconstruction import quality
        if not torch.cuda.is_available():raise RuntimeError('CUDA required')
        receipt,package=verify_assets(original.ASSETS,ROOT/'research/a6-candidate-model-assets.json')
        record['assets']=receipt
        record['environment']={'python':sys.version,**{p:importlib.metadata.version(p) for p in ('torch','diffusers','transformers','numpy','Pillow','lpips')}}
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False
        free,total=torch.cuda.mem_get_info();effective_gpu=min(cfg['gpu_budget_bytes'],free-512*1024**2)
        if effective_gpu<1024**3:raise RuntimeError('Insufficient free GPU memory with 512MiB headroom')
        record['effective_gpu_budget_bytes']=effective_gpu
        torch.cuda.set_per_process_memory_fraction(min(1.,effective_gpu/total));checkpoint()
        pipe=StableDiffusionPipeline.from_pretrained(original.ASSETS/'sd15-fp16',variant='fp16',use_safetensors=True,
            local_files_only=True,torch_dtype=torch.float16).to('cuda');pipe.set_progress_bar_config(disable=True)
        if pipe.safety_checker is None or pipe.feature_extractor is None:raise RuntimeError('Safety components required')
        for component in (pipe.unet,pipe.vae,pipe.text_encoder,pipe.safety_checker):component.eval().requires_grad_(False)
        if float(pipe.vae.config.scaling_factor)!=.18215:raise ValueError('Pinned scaling differs')
        metric=load_lpips(original.ASSETS,package)
        def check():
            if time.monotonic()-started>300:raise RuntimeError('Wall-time cap reached')
            if working_set_bytes()>cfg['ram_budget_bytes']:raise RuntimeError('RAM cap reached')
            if torch.cuda.memory_allocated()>effective_gpu:raise RuntimeError('GPU cap reached')
            if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise RuntimeError('Artifact cap reached')
        def artifact(path):return dict(path=path.name,sha256=sha(path),bytes=path.stat().st_size)
        def q(left,right):
            value={**quality(left,right),'lpips':lpips_score(metric,left,right)}
            value['quality_admissible']=(value['psnr_infinite'] or value['psnr_db']>35) and value['ssim_rgb']>.9 and value['lpips']<.1
            return value
        def native_stage(rgb,intended):
            tensor=pipe.image_processor.preprocess(Image.fromarray(rgb)).to(device='cuda',dtype=pipe.vae.dtype)
            with torch.inference_mode():z=pipe.vae.encode(tensor).latent_dist.mode()*pipe.vae.config.scaling_factor
            return dict(stage(z[0,0],original.dct_matrix(64,device='cuda'),intended),eligible_image_detector=True)
        c0={};initial_hash={}
        for case in cfg['cases']:
            for arm in ARMS:
                check();active=next(r for r in rows if r['seed']==case['seed'] and r['arm']==arm)
                active.update(outcome='started',artifacts=[]);unit_started=time.monotonic()
                event(dict(generation_id=active['id'],outcome='started'));checkpoint()
                def save_array(name,value):
                    path=output/(active['id']+'-'+name+'.npy');np.save(path,value.detach().cpu().numpy(),allow_pickle=False)
                    receipt=artifact(path);receipt.update(shape=list(value.shape),dtype=str(value.dtype),raw_sha256=hashlib.sha256(value.detach().cpu().numpy().tobytes()).hexdigest())
                    active['artifacts'].append(receipt);checkpoint();return receipt
                trace_path=output/(active['id']+'-trace.jsonl')
                def trace(value):
                    with trace_path.open('a',encoding='utf-8') as f:f.write(json.dumps(value,allow_nan=False)+'\n');f.flush()
                image,generation=generate(pipe,case,arm,active['intended_payload'],save_array,trace,check)
                active['generation']=generation;active['artifacts'].append(artifact(trace_path));checkpoint()
                raw=generation['initial_latent']['raw_sha256'];seed=case['seed']
                if seed in initial_hash and initial_hash[seed]!=raw:raise ValueError('Paired initial latent differs')
                initial_hash[seed]=raw;active['paired_initial_latent_matches']=True
                variants={'clean':image}
                # Identical original extra VAE cycle: encode PNG-equivalent RGB8, mode, decode, safety, PIL.
                rgb=np.asarray(image).copy()
                with torch.inference_mode():
                    tensor=pipe.image_processor.preprocess(Image.fromarray(rgb)).to(device='cuda',dtype=pipe.vae.dtype)
                    decoded=pipe.vae.decode(pipe.vae.encode(tensor).latent_dist.mode(),return_dict=False)[0]
                    decoded,flags=pipe.run_safety_checker(decoded,'cuda',pipe.vae.dtype)
                    if flags is None or len(flags)!=1 or bool(flags[0]):raise RuntimeError('VAE cycle safety incomplete/blocked')
                    variants['vae']=pipe.image_processor.postprocess(decoded,output_type='pil',do_denormalize=[True])[0]
                if arm=='C0-replay':c0[seed]=rgb
                active['quality_to_new_C0']=q(c0[seed],rgb)
                old_c0_path=SOURCE/old[(seed,'C0-replay','clean')]['path']
                with Image.open(old_c0_path) as old_image:old_c0=np.asarray(old_image.convert('RGB')).copy()
                active['quality_to_old_C0']=q(old_c0,rgb)
                active['quality_reference']='generated same-seed new C0, not existing photograph'
                for channel,pil in variants.items():
                    check();path=output/(active['id']+'-'+channel+'.png');pil.save(path)
                    suspect=np.asarray(Image.open(path).convert('RGB')).copy()
                    receipt=artifact(path);active['artifacts'].append(receipt)
                    read=original.score(pipe,suspect)
                    for name in ('native_vae_dct','image_dct_diagnostic'):
                        read[name].update(evaluate_word(read[name]['bits'],active['intended_payload']))
                    read.update(outcome='completed',artifact=receipt,quality_vs_same_arm_clean=q(rgb,suspect))
                    if arm in ('C0-replay','C-E100-replay'):
                        read['replay']=replay_status(old[(seed,arm,channel)]['sha256'],receipt['sha256'])
                    active['conditions'][channel]=read
                    stage_name='clean_rgb8' if channel=='clean' else 'additional_vae_rgb8'
                    generation['readout_stages'][stage_name]=native_stage(suspect,active['intended_payload'])
                    event(dict(generation_id=active['id'],channel=channel,**read))
                    checkpoint()
                active.update(outcome='completed',duration_seconds=time.monotonic()-unit_started,
                    peak_allocated_bytes=torch.cuda.max_memory_allocated())
                event(dict(generation_id=active['id'],outcome='completed',duration_seconds=active['duration_seconds']))
                checkpoint();active=None;torch.cuda.empty_cache()
        replay_ok=all(v['replay']['matched'] for r in rows for v in r['conditions'].values() if 'replay' in v)
        record.update(outcome='completed',replay_attribution_gate=replay_ok,scientific_interpretation_ready=replay_ok,
            replay_caveat=None if replay_ok else 'PNG replay attribution failed; diagnose before exact matched mechanism conclusions')
    except KeyboardInterrupt:
        record.update(outcome='interrupted',error='KeyboardInterrupt')
        if active:active.update(outcome='interrupted',error='KeyboardInterrupt')
    except Exception as err:
        record.update(outcome='failed',error=str(err),traceback=traceback.format_exc())
        if active:active.update(outcome='failed',error=str(err))
    finally:
        if active:
            partial_trace=output/(active['id']+'-trace.jsonl')
            if partial_trace.exists() and not any(a['path']==partial_trace.name for a in active.get('artifacts',[])):
                active.setdefault('artifacts',[]).append(dict(path=partial_trace.name,sha256=sha(partial_trace),
                    bytes=partial_trace.stat().st_size,partial=True))
        record['incomplete_planned_ids']=[r['id'] for r in rows if r['outcome']!='completed']
        record['missing_image_conditions']=[r['id']+'-'+c for r in rows for c,v in r['conditions'].items() if v['outcome']!='completed']
        record['gates']=gates(rows)
        event(dict(outcome=record['outcome'],error=record.get('error')))
        checkpoint()
    return 0 if record['outcome']=='completed' else 1


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',required=True,type=Path);p.add_argument('--output-dir',required=True,type=Path)
    args=p.parse_args();return run(args.manifest,args.output_dir)


if __name__=='__main__':raise SystemExit(main())
