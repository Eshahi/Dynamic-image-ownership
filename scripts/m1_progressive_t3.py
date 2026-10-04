"""Conditional fixed T3 screen. Manifest preparation and run both fail closed on source gates."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_progressive_redundancy as parent
MAIN=parent.MAIN
VERSION='m1-progressive-conditional-t3-v1'
SOURCE_ARMS=('C0-replay','C-Q5M5','C-Q5M5-complement')
STRENGTHS=(.1,.4)
sha=parent.sha
write=parent.write


def expected_timesteps(strength):
    if strength not in STRENGTHS:raise ValueError('Unplanned strength')
    return list(range(51,0,-50)) if strength==.1 else list(range(351,0,-50))


def word_from_coefficients(stage):
    values=stage['selected_coefficients']
    if len(values)!=128 or not all(type(x) in (int,float) and math.isfinite(x) for x in values):
        raise ValueError('Invalid selected coefficients')
    word=''.join(str(int(sum(x>0 for x in values[i:i+8])>4)) for i in range(0,128,8))
    if word!=stage['bits']:raise ValueError('Coefficient/raw-word mismatch')
    return word


def verify_source_code(record):
    commit=record['commit'];receipts=record['committed_files']
    if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):raise ValueError('Invalid source commit')
    required={'scripts/m1_progressive_redundancy.py','research/m1-progressive-redundancy-dev.json',
        'scripts/m1_progressive_vote_margin.py','scripts/m1_progressive_phase.py','scripts/m1_progressive_latent.py'}
    if not required.issubset(receipts):raise ValueError('Missing source code receipt')
    for relative,receipt in receipts.items():
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe source code path')
        oid=subprocess.check_output(['git','rev-parse',commit+':'+relative],cwd=ROOT,text=True).strip()
        if oid!=receipt['git_blob_oid']:raise ValueError('Source commit/blob receipt differs')


def checked_artifact(folder,receipt):
    name=receipt['path'];path=folder/name
    if Path(name).name!=name or path.is_symlink() or path.resolve().parent!=folder.resolve() or not path.is_file():
        raise ValueError('Missing/unsafe source artifact')
    if sha(path)!=receipt['sha256'] or path.stat().st_size!=receipt['bytes']:raise ValueError('Source artifact receipt differs')
    return path


def source_snapshot(folder,expected_sha=None):
    """All checks happen before Torch/model loading; no source file is modified."""
    folder=Path(folder).resolve()
    if not folder.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('MAIN development source required')
    source_path=folder/'run.json';source_sha=sha(source_path)
    if expected_sha is not None and source_sha!=expected_sha:raise ValueError('Frozen source run hash differs')
    record=json.loads(source_path.read_text())
    if record.get('outcome')!='completed' or record.get('schema_version')!=parent.VERSION or record.get('config')!=parent.configuration():
        raise ValueError('Completed exact Q5M5 source required')
    gate=parent.gates(record['rows'])
    if gate!=record.get('gates') or not gate['complete'] or not gate['replay'] or not gate['c0_absence'] or gate['promoted_operator']!='C-Q5M5':
        raise ValueError('All-eight clean/quality/VAE/replay source gate required')
    if record.get('planned_counts')!=dict(generations=20,image_conditions=40,unet_calls=1000,source_clusters=4):
        raise ValueError('Source declared inventory differs')
    if sha(folder/'manifest.json')!=record['manifest_sha256'] or json.loads((folder/'manifest.json').read_text())!=record['config']:
        raise ValueError('Source copied manifest receipt differs')
    verify_source_code(record)
    receipts={};inputs=[];initials={}
    for row in record['rows']:
        suffixes=['initial_latent.npy','terminal_latent.npy','decoder_float.npy','clipped_decoder_float.npy',
            'clipped_float_cycle_latent.npy','trace.jsonl','clean.png','vae.png']
        expected={row['id']+'-'+suffix for suffix in suffixes}
        if len(row['artifacts'])!=8 or {a['path'] for a in row['artifacts']}!=expected:raise ValueError('Source eight-artifact inventory differs')
        by_name={a['path']:a for a in row['artifacts']}
        for artifact in row['artifacts']:
            checked_artifact(folder,artifact);receipts[artifact['path']]=artifact
        generation=row['generation']
        if generation['timesteps']!=list(range(981,0,-20)) or generation['guided_step_indices']!=parent.guided_indices(row['arm']) or generation.get('unet_calls')!=50:
            raise ValueError('Source generation schedule differs')
        initial_hash=by_name[row['id']+'-initial_latent.npy']['sha256']
        if row['seed'] in initials and initials[row['seed']]!=initial_hash:raise ValueError('Source paired initial tensors differ')
        initials[row['seed']]=initial_hash
        trace=[json.loads(line) for line in (folder/(row['id']+'-trace.jsonl')).read_text().splitlines()]
        if len(trace)!=50 or [x['step_index'] for x in trace]!=list(range(50)):raise ValueError('Source trace inventory differs')
        for item in trace:
            if set(item['stages'])!={'ordinary_predicted_clean','corrected_predicted_clean','effective_fp16_predicted_clean','actual_noisy_scheduler_output'}:
                raise ValueError('Source trace stages differ')
            for stage in item['stages'].values():word_from_coefficients(stage)
        if set(generation['readout_stages'])!=set(parent.STAGES):raise ValueError('Source endpoint stages differ')
        for stage in generation['readout_stages'].values():word_from_coefficients(stage)
        for channel,stage_name in [('clean','clean_rgb8'),('vae','additional_vae_rgb8')]:
            condition=row['conditions'][channel]
            if condition['artifact']!=by_name[row['id']+'-'+channel+'.png']:raise ValueError('Source condition/artifact mismatch')
            if condition['native_vae_dct']['bits']!=generation['readout_stages'][stage_name]['bits']:
                raise ValueError('Source primary/endpoint word mismatch')
        if row['arm'] in SOURCE_ARMS:
            inputs.append(dict(generation_id=row['id'],seed=row['seed'],arm=row['arm'],
                intended_payload=row['intended_payload'],artifact=row['conditions']['clean']['artifact']))
    inputs.sort(key=lambda r:(r['seed'],SOURCE_ARMS.index(r['arm'])))
    if len(inputs)!=12 or len(receipts)!=160:raise ValueError('Source fixed inventory differs')
    if sha(source_path)!=source_sha:raise ValueError('Source changed during validation')
    return dict(source_dir=str(folder),source_run_sha256=source_sha,source_commit=record['commit'],
        source_manifest_sha256=record['manifest_sha256'],source_gate=gate,inputs=inputs,
        source_assets=record['assets'],source_artifact_receipts=receipts,
        source_committed_files=record['committed_files'])


def configuration(snapshot):
    return dict(schema_version=VERSION,data_split='synthetic',source_dir=snapshot['source_dir'],
        source_run_sha256=snapshot['source_run_sha256'],source_commit=snapshot['source_commit'],
        source_manifest_sha256=snapshot['source_manifest_sha256'],inputs=snapshot['inputs'],
        operator='C-Q5M5',strengths=list(STRENGTHS),steps=20,guidance_scale=1.,sampler_eta=0.,
        prompt='',negative_prompt='',attack_seed=0,presence_matches=14,
        planned_counts=dict(source_images=12,attack_conditions=24,unet_calls=120,source_clusters=4),
        run_seconds_cap=180,gpu_budget_bytes=10*1024**3,ram_budget_bytes=16*1024**3,artifact_budget_bytes=150*1024**2)


def prepare(source,manifest_output):
    snapshot=source_snapshot(source)
    path=Path(manifest_output)
    if path.exists():raise FileExistsError(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    # This is an experiment manifest, not an approval or lifecycle verdict.
    write(path,configuration(snapshot))
    return dict(path=str(path.resolve()),sha256=sha(path),source_run_sha256=snapshot['source_run_sha256'])


def planned():
    return [dict(id=f'seed{seed}-{arm}-t3-{strength:g}',source_id=f'seed{seed}-{arm}',seed=seed,
        arm=arm,strength=strength,attack_seed=0,outcome='planned',
        intended_payload=parent.COMPLEMENT if arm.endswith('complement') else parent.ORIGINAL,
        expected_timesteps=expected_timesteps(strength),human_visual_verdict=None)
        for seed in range(1000,1004) for arm in SOURCE_ARMS for strength in STRENGTHS]


def gates(rows):
    reference={r['id']:r for r in planned()}
    if len(rows)!=24 or {r['id'] for r in rows}!=set(reference) or any(r.get('outcome')!='completed' for r in rows):
        return dict(complete=False,by_strength=None,joint_pass=None)
    groups={}
    try:
        for r in rows:
            if any(r[k]!=reference[r['id']][k] for k in ('seed','arm','strength','attack_seed','intended_payload','source_id')):
                raise ValueError('Condition identity differs')
            if r['actual_timesteps']!=r['expected_timesteps'] or r['actual_timesteps']!=expected_timesteps(r['strength']) or r['unet_calls']!=len(r['actual_timesteps']):
                raise ValueError('Observed attack schedule differs')
        for strength in STRENGTHS:
            marked=[r for r in rows if r['strength']==strength and r['arm']!='C0-replay']
            absent=[r for r in rows if r['strength']==strength and r['arm']=='C0-replay']
            carrier=all(parent.evaluate_word(r['readout']['native_vae_dct']['bits'],r['intended_payload'])['intended_present'] for r in marked)
            null=all(not parent.evaluate_word(r['readout']['native_vae_dct']['bits'],parent.ORIGINAL)[ref+'_present'] for r in absent for ref in ('original','complement'))
            groups[str(strength)]=dict(marked_denominator=8,c0_denominator=4,carrier=carrier,c0_absence=null,pass_gate=carrier and null)
    except (KeyError,ValueError,TypeError) as error:return dict(complete=False,by_strength=None,joint_pass=None,error=str(error))
    return dict(complete=True,by_strength=groups,joint_pass=all(v['pass_gate'] for v in groups.values()),
        source_clusters=4,caveat='Fixed public-carrier development result; no dual binding, authentication or independent FPR calibration')


def attack_one(attack,rgb,strength,check,progress=None):
    import torch
    from PIL import Image
    from diffusers import DDIMScheduler
    from three_threat_models import DDIM_CONFIG,validate_generated
    attack.scheduler=DDIMScheduler(**DDIM_CONFIG)
    progress={} if progress is None else progress
    unet_times=progress.setdefault('unet_timesteps',[]);step_times=progress.setdefault('scheduler_step_timesteps',[])
    def hook(module,args):
        check();unet_times.append(int(args[1]))
    def callback(pipeline,index,timestep,kwargs):
        check();step_times.append(int(timestep));return kwargs
    handle=attack.unet.register_forward_pre_hook(hook)
    try:
        with torch.inference_mode():
            result=attack(prompt='',negative_prompt='',image=Image.fromarray(rgb),strength=strength,
                num_inference_steps=20,eta=0.,guidance_scale=1.,generator=torch.Generator(device='cuda').manual_seed(0),
                output_type='pil',callback_on_step_end=callback)
        image=validate_generated(result)
    finally:handle.remove()
    if unet_times!=expected_timesteps(strength) or step_times!=unet_times:raise ValueError('Actual T3 UNet/step timesteps differ')
    return image,step_times,len(unet_times)


def run(manifest_path,output):
    manifest_path=Path(manifest_path).resolve();output=Path(output).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN development output required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic();rows=planned();active=None
    record=dict(schema_version=VERSION,command=sys.argv,outcome='started',data_split='synthetic',rows=rows,
        seeds=list(range(1000,1004)),attack_seed=0,planned_counts=dict(source_images=12,attack_conditions=24,unet_calls=120,source_clusters=4),human_visual_verdict=None)
    def checkpoint():
        record['duration_seconds']=time.monotonic()-started;write(output/'run.json',record);write(output/'conditions.json',rows)
    def event(value):
        with (output/'rows.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps(dict(seconds=time.monotonic()-started,**value),allow_nan=False)+'\n');stream.flush()
    checkpoint()
    try:
        cfg=json.loads(manifest_path.read_text());record['config']=cfg
        snapshot=source_snapshot(cfg['source_dir'],cfg['source_run_sha256'])
        if cfg!=configuration(snapshot):raise ValueError('Exact prepared manifest required; no source or arm override')
        dependencies=[Path(__file__),manifest_path,ROOT/'research/m1-progressive-redundancy-design.md',
            *[ROOT/relative for relative in snapshot['source_committed_files']]]
        record.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            committed_files=parent.require_committed(dependencies),manifest_sha256=sha(manifest_path),source_snapshot=snapshot)
        (output/'manifest.json').write_bytes(manifest_path.read_bytes());checkpoint()
        from three_threat_models import block_network,verify_assets,load_lpips,lpips_score
        block_network()
        import numpy as np
        import torch
        from PIL import Image
        from diffusers import StableDiffusionPipeline,StableDiffusionImg2ImgPipeline
        from m1_latent_reconstruction import quality
        if not torch.cuda.is_available():raise RuntimeError('CUDA required')
        assets,package=verify_assets(parent.original.ASSETS,ROOT/'research/a6-candidate-model-assets.json')
        if assets!=snapshot['source_assets']:raise ValueError('Attack/source asset identities differ')
        record['assets']=assets
        record['environment']={'python':sys.version,**{name:importlib.metadata.version(name) for name in ('torch','diffusers','transformers','numpy','Pillow','lpips')}}
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False
        free,total=torch.cuda.mem_get_info();budget=min(cfg['gpu_budget_bytes'],free-512*1024**2)
        if budget<1024**3:raise RuntimeError('Insufficient GPU headroom')
        torch.cuda.set_per_process_memory_fraction(min(1.,budget/total));record['effective_gpu_budget_bytes']=budget
        pipe=StableDiffusionPipeline.from_pretrained(parent.original.ASSETS/'sd15-fp16',variant='fp16',use_safetensors=True,
            local_files_only=True,torch_dtype=torch.float16).to('cuda');pipe.set_progress_bar_config(disable=True)
        if pipe.safety_checker is None or pipe.feature_extractor is None:raise RuntimeError('Safety components required')
        for component in (pipe.unet,pipe.vae,pipe.text_encoder,pipe.safety_checker):component.eval().requires_grad_(False)
        if float(pipe.vae.config.scaling_factor)!=.18215:raise ValueError('Pinned latent scaling differs')
        attack=StableDiffusionImg2ImgPipeline(**pipe.components);attack.set_progress_bar_config(disable=True)
        metric=load_lpips(parent.original.ASSETS,package)
        def check():
            if time.monotonic()-started>cfg['run_seconds_cap']:raise RuntimeError('Time cap reached')
            if parent.working_set_bytes()>cfg['ram_budget_bytes']:raise RuntimeError('RAM cap reached')
            if torch.cuda.memory_allocated()>budget:raise RuntimeError('GPU cap reached')
            if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise RuntimeError('Artifact cap reached')
        inputs={value['generation_id']:value for value in snapshot['inputs']}
        for active in rows:
            check();active['outcome']='started';unit_started=time.monotonic();event(dict(id=active['id'],outcome='started'));checkpoint()
            source=inputs[active['source_id']];path=checked_artifact(Path(snapshot['source_dir']),source['artifact'])
            with Image.open(path) as image:
                if image.mode!='RGB' or image.size!=(512,512):raise ValueError('Frozen source RGB geometry differs')
                rgb=np.asarray(image).copy()
            active['source_png_receipt']=source['artifact']
            active['attack_trace']={}
            image,timesteps,calls=attack_one(attack,rgb,active['strength'],check,active['attack_trace'])
            path=output/(active['id']+'.png');image.save(path)
            active.update(artifact=dict(path=path.name,sha256=sha(path),bytes=path.stat().st_size),
                actual_timesteps=timesteps,unet_calls=calls,safety_flag=False)
            checkpoint()
            with Image.open(path) as saved:suspect=np.asarray(saved.convert('RGB')).copy()
            readout=parent.original.score(pipe,suspect)
            for name in ('native_vae_dct','image_dct_diagnostic'):
                readout[name].update(parent.evaluate_word(readout[name]['bits'],active['intended_payload']))
            tensor=pipe.image_processor.preprocess(Image.fromarray(suspect)).to(device='cuda',dtype=pipe.vae.dtype)
            with torch.inference_mode():latent=pipe.vae.encode(tensor).latent_dist.mode()*pipe.vae.config.scaling_factor
            trace=parent.stage(latent[0,0],parent.original.dct_matrix(64,device='cuda'),active['intended_payload'],.5)
            if word_from_coefficients(trace)!=readout['native_vae_dct']['bits']:raise ValueError('T3 primary/trace readout mismatch')
            active.update(outcome='completed',readout=readout,
                native_coefficient_trace=dict(trace,eligible_image_detector=True),
                quality_vs_same_arm_clean={**quality(rgb,suspect),'lpips':lpips_score(metric,rgb,suspect)},
                quality_scope='Descriptive attack change from the same marked/C0 source; not the clean embedding quality gate',
                duration_seconds=time.monotonic()-unit_started,peak_allocated_bytes=torch.cuda.max_memory_allocated())
            event(active);checkpoint();active=None;torch.cuda.empty_cache()
        if sum(r['unet_calls'] for r in rows)!=120:raise ValueError('Total UNet call inventory differs')
        record['observed_unet_calls']=120;record['outcome']='completed'
    except KeyboardInterrupt:
        record.update(outcome='interrupted',error='KeyboardInterrupt')
        if active:active.update(outcome='interrupted',error='KeyboardInterrupt')
    except Exception as error:
        record.update(outcome='failed',error=str(error),traceback=traceback.format_exc())
        if active:active.update(outcome='failed',error=str(error))
    finally:
        record['observed_unet_calls']=sum(len(r.get('attack_trace',{}).get('unet_timesteps',[])) for r in rows)
        record['missing_condition_ids']=[r['id'] for r in rows if r['outcome']!='completed']
        record['gates']=gates(rows);event(dict(outcome=record['outcome'],error=record.get('error')));checkpoint()
    return 0 if record['outcome']=='completed' else 1


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
    parser=sub.add_parser('prepare');parser.add_argument('--source-dir',type=Path,required=True);parser.add_argument('--manifest-output',type=Path,required=True)
    parser=sub.add_parser('run');parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    if args.action=='prepare':print(json.dumps(prepare(args.source_dir,args.manifest_output)));return 0
    return run(args.manifest,args.output_dir)


if __name__=='__main__':raise SystemExit(main())
