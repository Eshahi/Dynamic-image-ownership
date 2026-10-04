"""A-C: bounded terminal-latent optimization; unchanged B3 blind reader.

No model loads on import. Only --run executes the two-source development
experiment. Resumption reads an identical prior attempt into a fresh directory.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
import m1_blind_noise_core as core
import m1_blind_noise as blind
import m1_dual_latent as old_a
import m1_phase_residual as residual
import m1_phasemark as util
import revised_watermark_v5 as codec

MAIN = util.MAIN
VERSION = 'm1-terminal-continuous-v1'
IDS = (1675, 4795)
RECONSTRUCTION = MAIN / '.thesis-build/dev-runs/20261003-1455-latent-reconstruction'
EPSILON = 10 ** (-35.2 / 20)


def configuration():
    cohort = json.loads((ROOT / 'research/m1-reconstruction-dev.json').read_text())
    return dict(schema=VERSION, data_split='development',
        cases=[c for c in cohort['cases'] if c['id'] in IDS],
        reconstruction_run=str(RECONSTRUCTION), reconstruction_step=200,
        owners=list(core.OWNERS), threshold=4., steps=100, learning_rate=.01,
        adam_betas=[.9,.999], adam_eps=1e-8, seed=0, checkpoint_every=10,
        semantic_margin=6., instance_margin=8., cycle_margin=6., cycle_every=2,
        quality_weight=.01, psnr_cap_db=35.2, bisection_steps=36,
        embedder_precision='float32', reader_precision='float16',
        profile='configs/revised-watermark-v5.example.json',
        run_seconds_cap=1800, gpu_budget_bytes=10*1024**3, gpu_reserve_bytes=512*1024**2,
        ram_budget_bytes=16*1024**3, artifact_budget_bytes=500*1024**2,
        final_selection='last-fixed-step; quality-only cap')


def planned():
    return [dict(id=f'{ident}-{arm}-{dose}', source_id=ident, control=arm,
                 dose=dose, outcome='planned', human_visual_verdict=None)
            for ident in IDS for arm in ('C0','C1') for dose in ('clean','vae_cycle')]


def pilot_gate(rows):
    """Fixed two-source gate; absent/invalid observations never disappear."""
    complete=len(rows)==8 and {r['id'] for r in rows}=={r['id'] for r in planned()} and all(r.get('outcome')=='completed' for r in rows)
    clean=[r for r in rows if r['control']=='C1' and r['dose']=='clean']
    cycle=[r for r in rows if r['control']=='C1' and r['dose']=='vae_cycle']
    clean_quality=sum(r.get('quality_vs_source',{}).get('quality_admissible') is True for r in clean)
    clean_both=sum(r.get('owner_decisions',{}).get(core.OWNERS[0],{}).get('state')=='both_match' for r in clean)
    cycle_semantic=sum(r.get('owner_decisions',{}).get(core.OWNERS[0],{}).get('flags',{}).get('s') is True for r in cycle)
    negatives=[]
    for row in rows:
        for owner in core.OWNERS if row['control']=='C0' else core.OWNERS[1:]:
            flags=row.get('owner_decisions',{}).get(owner,{}).get('flags',{})
            negatives.append(flags.get('s') is False and flags.get('i') is False)
    return dict(planned_source_n=2,planned_conditions=8,planned_owner_queries=32,
        complete=complete,clean_quality_n=clean_quality,clean_both_n=clean_both,vae_semantic_n=cycle_semantic,
        negative_queries_below_both_n=sum(negatives),planned_negative_queries=28,
        passes=complete and clean_quality==2 and clean_both==2 and cycle_semantic==2 and len(negatives)==28 and all(negatives))


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def gpu_allocation_budget(configured,free,total,reserve):
    """CPU arithmetic only; runtime supplies the device's current free bytes."""
    if any(type(v) is not int for v in (configured,free,total,reserve)):
        raise ValueError('GPU memory quantities must be integer bytes')
    if configured<=0 or total<=0 or reserve<0 or not 0<=free<=total:
        raise ValueError('Invalid GPU memory quantities')
    effective=min(configured,free-reserve)
    if effective<=0:raise RuntimeError('No positive GPU allocation budget after reserve')
    return dict(configured_bytes=configured,free_bytes_before_models=free,total_bytes=total,
                reserve_bytes=reserve,effective_allocation_bytes=effective,
                allocator_fraction=effective/total)


def cap_tensor(source, residual_tensor):
    """Differentiable radial cap; norm's zero derivative is defined by torch."""
    import torch
    rho = torch.linalg.vector_norm(residual_tensor) / math.sqrt(residual_tensor.numel())
    # max(rho, epsilon) gives beta1 at zero without evaluating a zero division.
    beta = EPSILON / rho.clamp_min(EPSILON)
    return (source + beta*residual_tensor).clamp(0,1), rho, beta


class FixedSourceScores:
    """Embedding-only oracle. Never passed to the primary detector."""
    def __init__(self,E,H,owner,device,dtype=None):
        import torch
        dtype = dtype or torch.float32
        p = core.template(E,H,owner)
        self.arrays = {k:torch.tensor(p[k].copy(),device=device,
            dtype=torch.long if k.startswith('coords_') else dtype)
            for k in ('coords_s','coords_i','v_s','v_i','r_s','r_i')}

    def scores(self,scaled_latent):
        import torch
        z = scaled_latent.reshape(-1)
        if z.numel()!=core.N:
            raise ValueError('Exactly one 4x64x64 latent required')
        answer=[]
        for j in ('s','i'):
            weights=z[self.arrays[f'coords_{j}']]*self.arrays[f'v_{j}']
            denominator=torch.linalg.vector_norm(weights)
            numerator=(weights*self.arrays[f'r_{j}']).sum()
            if not bool(torch.isfinite(denominator)) or float(denominator.detach())<=0 or not bool(torch.isfinite(numerator)):
                raise ValueError('Invalid oracle score, without stabilization')
            answer.append(numerator/denominator)
        return tuple(answer)


def hinge(score,margin):
    import torch
    return (torch.relu(margin-score)/margin).square()


class Embedder:
    def __init__(self,vae):
        self.vae=vae

    def decode(self,u):
        return ((self.vae.decode(u,return_dict=False)[0]+1)/2).clamp(0,1)

    def encode(self,rgb):
        return self.vae.encode(rgb*2-1).latent_dist.mode()*.18215

    def cycle(self,rgb):
        return self.decode(self.encode(rgb)/.18215)


class PublicReader:
    """Only suspect bytes, public models/profile, and owner reach readout."""
    def __init__(self,vae,processor,feature,profile):
        self.vae,self.processor,self.feature,self.profile=vae,processor,feature,profile
        self.cache_key=None
        self.cache_value=None

    def observations(self,rgb):
        import numpy as np
        import torch
        from PIL import Image
        key=hashlib.sha256(rgb.tobytes()).hexdigest()
        if key!=self.cache_key:
            with torch.inference_mode():
                x=self.processor.preprocess(Image.fromarray(rgb)).to('cuda',dtype=self.vae.dtype)
                z=self.vae.encode(x).latent_dist.mode()*.18215
            e=self.feature(rgb)
            h=codec.perceptual_hash(codec.luminance_from_rgb(rgb.tolist()),profile=self.profile)
            self.cache_value=(e,h,z.float().cpu().numpy().reshape(-1).astype(np.float64))
            self.cache_key=key
        return self.cache_value


def detect(image_rgb8,owner_id,pinned_public_profile_and_models):
    return blind.detect(image_rgb8,owner_id,pinned_public_profile_and_models)


def cpu_tree(value):
    import torch
    if torch.is_tensor(value):return value.detach().cpu()
    if isinstance(value,dict):return {k:cpu_tree(v) for k,v in value.items()}
    if isinstance(value,list):return [cpu_tree(v) for v in value]
    if isinstance(value,tuple):return tuple(cpu_tree(v) for v in value)
    return value


def rng_state():
    import numpy as np
    import torch
    ns=np.random.get_state()
    return dict(torch_cpu=torch.get_rng_state(),torch_cuda=torch.cuda.get_rng_state_all(),
        python=random.getstate(),numpy=[ns[0],ns[1].tolist(),ns[2],ns[3],ns[4]])


def restore_rng(value):
    import numpy as np
    import torch
    torch.set_rng_state(value['torch_cpu']);torch.cuda.set_rng_state_all(value['torch_cuda'])
    random.setstate(value['python']);n=value['numpy']
    np.random.set_state((n[0],np.asarray(n[1],dtype=np.uint32),n[2],n[3],n[4]))


def checkpoint_save(path,u,optimizer,step,identity):
    import torch
    path=Path(path)
    if path.exists():raise ValueError('Refuse checkpoint replacement')
    temporary=path.with_suffix('.pt.tmp')
    torch.save(dict(u=u.detach().cpu(),optimizer=cpu_tree(optimizer.state_dict()),
                    step=step,identity=identity,rng=rng_state()),temporary)
    temporary.replace(path)
    return dict(step=step,path=str(path),sha256=util.sha(path))


def checkpoint_load(receipt,identity):
    import torch
    path=Path(receipt['path'])
    if util.sha(path)!=receipt['sha256']:raise ValueError('Resume checkpoint hash differs')
    data=torch.load(path,map_location='cpu',weights_only=True)
    if data['identity']!=identity or data['step']!=receipt['step'] or data['step'] not in range(0,101,10):
        raise ValueError('Resume identity or step mismatch')
    if data['u'].shape!=(1,4,64,64) or data['u'].dtype!=torch.float32 or not bool(torch.isfinite(data['u']).all()):
        raise ValueError('Invalid resumed latent')
    return data


def move_inference_models(models,device):
    """Execution-only placement; retain weights, dtypes and frozen status."""
    sizes=[]
    for model in models:
        if any(p.requires_grad for p in model.parameters()):
            raise ValueError('Only frozen inference models may be moved')
        sizes.append(sum(v.numel()*v.element_size() for v in (*model.parameters(),*model.buffers())))
        model.to(device=device)
    return sizes


def exact_tree_equal(left,right):
    """Exact scientific tensor/state parity, excluding provenance identity."""
    import torch
    if torch.is_tensor(left) or torch.is_tensor(right):
        return torch.is_tensor(left) and torch.is_tensor(right) and left.dtype==right.dtype and left.shape==right.shape and torch.equal(left,right)
    if type(left) is not type(right):return False
    if isinstance(left,dict):return left.keys()==right.keys() and all(exact_tree_equal(left[k],right[k]) for k in left)
    if isinstance(left,(list,tuple)):return len(left)==len(right) and all(exact_tree_equal(a,b) for a,b in zip(left,right))
    return left==right


def verify_completed_case_replay(current_case,current_rows,reference):
    """Compare fresh results; never initialize from the reference checkpoint."""
    import torch
    old=[r for r in reference['case_events'] if r['source_id']==current_case['source_id'] and r['outcome']=='completed']
    if len(old)!=1:raise ValueError('Replay requires exactly one completed reference case')
    old=old[0]
    if current_case['source']['rgb8_sha256']!=old['source']['rgb8_sha256'] or current_case['initialization']!=old['initialization']:
        raise ValueError('Replay source/initialization differs')
    endpoints=[]
    for case in (old,current_case):
        receipts=[r for r in case['checkpoints'] if r['step']==100]
        if len(receipts)!=1 or util.sha(Path(receipts[0]['path']))!=receipts[0]['sha256']:
            raise ValueError('Replay endpoint receipt invalid')
        endpoints.append(torch.load(receipts[0]['path'],map_location='cpu',weights_only=True))
    if any(not exact_tree_equal(endpoints[0][k],endpoints[1][k]) for k in ('u','optimizer','rng','step')):
        raise ValueError('Fresh endpoint replay differs in latent/Adam/RNG/step')
    old_rows={r['id']:r for r in reference['conditions'] if r['source_id']==current_case['source_id']}
    new_rows={r['id']:r for r in current_rows if r['source_id']==current_case['source_id']}
    if len(old_rows)!=4 or old_rows.keys()!=new_rows.keys():raise ValueError('Replay image inventory differs')
    for ident,row in new_rows.items():
        previous=old_rows[ident]
        if row['outcome']!='completed' or previous['outcome']!='completed':raise ValueError('Replay image incomplete')
        for field in ('image','terminal_reader_latent','terminal_fp32_latent'):
            for value in (row[field],previous[field]):
                if util.sha(Path(value['path']))!=value['sha256']:raise ValueError('Replay artifact hash mismatch')
            if row[field]['sha256']!=previous[field]['sha256']:raise ValueError('Fresh image/reader-latent replay differs')
        if not exact_tree_equal(row['owner_decisions'],previous['owner_decisions']):raise ValueError('Replay decisions differ')
    return dict(source_id=current_case['source_id'],passed=True,images=4,reader_arrays=8,
                endpoint_fields=['u','optimizer','rng','step'],provenance_identity_compared=False,
                caveat='Fresh same-source replay, not an independent image or cross-commit resume')


def optimize(embedder,source,u0,oracle,cfg,event,save,check,resume=None):
    import torch
    from torch.utils.checkpoint import checkpoint
    with torch.no_grad():reference=embedder.decode(u0).detach()
    u=(resume['u'].to(source.device) if resume else u0.detach().clone()).requires_grad_(True)
    optimizer=torch.optim.Adam([u],lr=cfg['learning_rate'],betas=tuple(cfg['adam_betas']),eps=cfg['adam_eps'])
    start=0
    if resume:
        optimizer.load_state_dict(resume['optimizer']);start=resume['step'];restore_rng(resume['rng'])
    save(start,u,optimizer)

    def render(value):return cap_tensor(source,embedder.decode(value)-reference)[0]
    def observations(value):return oracle.scores(embedder.encode(value))
    for step in range(start,cfg['steps']):
        check();optimizer.zero_grad(set_to_none=True)
        image=checkpoint(render,u,use_reentrant=False)
        s,i=checkpoint(observations,image,use_reentrant=False)
        ratio=(image-source).square().mean()/EPSILON**2
        loss=hinge(s,6.)+hinge(i,8.)+.01*ratio
        if not bool(torch.isfinite(loss)):raise ValueError('Nonfinite clean loss')
        row=dict(step=step+1,measurement_time='before-update',clean_loss=float(loss.detach()),
                 source_s=float(s.detach()),source_i=float(i.detach()),quality_budget_ratio=float(ratio.detach()))
        loss.backward();del image,s,i,loss,ratio
        if step%cfg['cycle_every']==0:
            image=checkpoint(render,u,use_reentrant=False)
            cycled=checkpoint(embedder.cycle,image,use_reentrant=False)
            s,i=checkpoint(observations,cycled,use_reentrant=False)
            loss=hinge(s,6.)
            if not bool(torch.isfinite(loss)):raise ValueError('Nonfinite cycle loss')
            row.update(cycle_source_s=float(s.detach()),cycle_source_i=float(i.detach()),cycle_loss=float(loss.detach()))
            loss.backward();del image,cycled,s,i,loss
        if u.grad is None or not bool(torch.isfinite(u.grad).all()):raise ValueError('Missing/nonfinite latent gradient')
        row['gradient_l2']=float(torch.linalg.vector_norm(u.grad))
        optimizer.step()
        if not bool(torch.isfinite(u).all()):raise ValueError('Nonfinite latent update')
        with torch.no_grad():
            _,rho,beta=cap_tensor(source,embedder.decode(u)-reference)
            row.update(after_update_residual_rms=float(rho),after_update_beta=float(beta))
        event(row)
        if (step+1)%cfg['checkpoint_every']==0:save(step+1,u,optimizer)
    with torch.no_grad():
        decoded=embedder.decode(u);r=decoded-reference;image,rho,beta=cap_tensor(source,r)
        scores=oracle.scores(embedder.encode(image));cycle_scores=oracle.scores(embedder.encode(embedder.cycle(image)))
    return dict(u=u.detach(),reference=reference,decoded=decoded,residual=r,surrogate=image,
        beta=float(beta),rho=float(rho),surrogate_scores=[float(v) for v in scores],
        surrogate_cycle_scores=[float(v) for v in cycle_scores])


def run(manifest_path,output,resume_from=None,replay_reference=None):
    import numpy as np
    from PIL import Image
    manifest_path=Path(manifest_path).resolve();output=Path(output).resolve();cfg=configuration()
    if json.loads(manifest_path.read_text())!=cfg:raise ValueError('Exact frozen manifest required')
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN development output required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic();previous_duration=0.
    rows={r['id']:r for r in planned()}
    record=dict(schema=VERSION,data_split='development',command=sys.argv,config=cfg,seeds=[0],
                outcome='started',duration_seconds=0.,case_events=[],conditions=list(rows.values()),
                optimized_variables=['unscaled terminal VAE latent'],nfe_unet=0,
                detector_side_information=['suspect RGB8','candidate public OwnerID','pinned VAE/CLIP/hash profile and maps'])
    def persist():util.write(output/'run.json',record)
    def event(value):
        with (output/'journal.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(value,allow_nan=False)+'\n')
    def retain(row):
        event(dict(kind='condition',**row));util.write(output/'conditions.json',list(rows.values()));persist()
    def check():
        if previous_duration+time.monotonic()-started>cfg['run_seconds_cap']:raise RuntimeError('Cumulative1800s cap')
        if util.working_set_bytes()>cfg['ram_budget_bytes']:raise RuntimeError('RAM cap')
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise RuntimeError('Artifact cap')
        if 'torch' in sys.modules:
            tm=sys.modules['torch']
            effective=record.get('gpu_allocation_budget',{}).get('effective_allocation_bytes',cfg['gpu_budget_bytes'])
            if tm.cuda.is_initialized() and tm.cuda.memory_allocated()>effective:raise RuntimeError('Effective GPU allocation cap')
    for row in rows.values():retain(row)
    try:
        deps=[Path(__file__),manifest_path,ROOT/'research/m1-terminal-continuous-design.md',
            ROOT/'research/m1-terminal-continuous-recovery.md',
            ROOT/'scripts/m1_blind_noise_core.py',ROOT/'scripts/m1_blind_noise.py',ROOT/'scripts/m1_dual_latent.py',
            ROOT/'scripts/m1_phase_residual.py',ROOT/'scripts/m1_phasemark.py',ROOT/'scripts/m1_latent_reconstruction.py',
            ROOT/'scripts/revised_watermark_v5.py',ROOT/'scripts/revised_watermark_v4.py',ROOT/'scripts/three_threat_models.py',
            ROOT/'scripts/three_threat_protocol.py',ROOT/'scripts/a6_clip_visual.py',ROOT/'scripts/verify_science_assets.py',
            ROOT/'scripts/check_a6_lpips_assets.py',ROOT/'research/a6-candidate-model-assets.json',
            ROOT/'research/m1-reconstruction-dev.json',ROOT/cfg['profile']]
        record.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            committed_files=util.require_committed(deps),manifest_sha256=util.sha(manifest_path))
        fingerprint=dict(commit=record['commit'],committed_files=record['committed_files'],manifest_sha256=record['manifest_sha256'])
        replay=None
        if replay_reference:
            if resume_from:raise ValueError('Fresh replay cannot be combined with resume')
            replay_path=Path(replay_reference).resolve()/'run.json'
            if not replay_path.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Replay reference must be MAIN development run')
            replay=json.loads(replay_path.read_text())
            if replay.get('schema')!=VERSION or replay.get('config')!=cfg or replay.get('data_split')!='development':
                raise ValueError('Replay reference scientific configuration differs')
            if [r['source_id'] for r in replay['case_events'] if r['outcome']=='completed']!=[IDS[0]]:
                raise ValueError('Recovery replay requires completed first source only')
            record['replay_reference']=dict(path=str(replay_path),sha256=util.sha(replay_path),commit=replay['commit'],
                initialization='fresh original step200 reconstruction, no reference watermark checkpoint loaded for optimization')
        record['execution_variant']='inference-model-offload-v1'
        prior=None
        if resume_from:
            resume_from=Path(resume_from).resolve()
            if not resume_from.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Resume source must be MAIN development run')
            prior=json.loads((resume_from/'run.json').read_text())
            if prior.get('schema')!=VERSION or prior.get('data_split')!='development' or any(prior.get(k)!=v for k,v in fingerprint.items()):raise ValueError('Resume requires identical version/commit/receipts')
            if prior.get('outcome')=='completed':raise ValueError('Completed run is not a resume source')
            previous_duration=prior['duration_seconds']
            record['resume_input']=dict(path=str(resume_from),run_sha256=util.sha(resume_from/'run.json'),duration_seconds=previous_duration)
        (output/'manifest.json').write_bytes(manifest_path.read_bytes());persist();check()
        from three_threat_models import block_network,verify_assets,load_lpips,lpips_score,clip_feature
        block_network()
        import torch
        from diffusers import AutoencoderKL
        from diffusers.image_processor import VaeImageProcessor
        from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
        from transformers import CLIPImageProcessor
        from a6_clip_visual import load_visual_encoder
        from m1_latent_reconstruction import quality
        if not torch.cuda.is_available():raise RuntimeError('CUDA required')
        torch.manual_seed(0);np.random.seed(0);random.seed(0)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False
        free_bytes,total_bytes=torch.cuda.mem_get_info(0)
        record['gpu_allocation_budget']=gpu_allocation_budget(cfg['gpu_budget_bytes'],int(free_bytes),int(total_bytes),cfg['gpu_reserve_bytes'])
        torch.cuda.set_per_process_memory_fraction(record['gpu_allocation_budget']['allocator_fraction'])
        persist();check()
        assets,package=verify_assets(util.ASSETS,ROOT/'research/a6-candidate-model-assets.json')
        def load_vae(dtype):
            model=AutoencoderKL.from_pretrained(util.ASSETS/'sd15-fp16/vae',variant='fp16',use_safetensors=True,local_files_only=True,torch_dtype=dtype).eval().requires_grad_(False).to('cuda')
            if float(model.config.scaling_factor)!=.18215:raise ValueError('Unexpected scaling factor')
            return model
        embedder=Embedder(load_vae(torch.float32));reader_vae=load_vae(torch.float16)
        processor=VaeImageProcessor(vae_scale_factor=8)
        safety=StableDiffusionSafetyChecker.from_pretrained(util.ASSETS/'sd15-fp16/safety_checker',variant='fp16',use_safetensors=True,local_files_only=True,torch_dtype=torch.float16).eval().requires_grad_(False).to('cuda')
        safety_processor=CLIPImageProcessor.from_pretrained(util.ASSETS/'sd15-fp16/feature_extractor',local_files_only=True)
        clip,transform=load_visual_encoder(util.ASSETS/'clip/ViT-B-32.pt',device='cpu')
        metric=load_lpips(util.ASSETS,package)
        profile=codec.validate_profile(codec.load_profile(ROOT/cfg['profile']))
        def feature(rgb):
            value=np.asarray(clip_feature(clip,transform,rgb),np.float64).reshape(-1)
            norm=np.linalg.norm(value)
            if value.shape!=(512,) or not np.isfinite(value).all() or norm<=0:raise ValueError('Invalid CLIP')
            return value/norm
        public=PublicReader(reader_vae,processor,feature,profile)
        record.update(assets=assets,environment={'python':sys.version,**{p:importlib.metadata.version(p) for p in ('torch','numpy','scipy','Pillow','diffusers','lpips')}},
            latent_units='unscaled VAE posterior coordinate for optimization; reader output times.18215',
            lpips_learned_sha256=util.sha(package/'weights/v0.1/alex.pth'),reconstruction_run_sha256=util.sha(RECONSTRUCTION/'run.json'))
        def tensor(rgb,dtype=torch.float32):return torch.from_numpy(rgb.copy()).permute(2,0,1)[None].to('cuda',dtype=dtype)/255
        def array(value):return value.detach().float().cpu().numpy()[0].transpose(1,2,0).astype(np.float64)
        def safety_check(rgb):
            with torch.inference_mode():
                inputs=safety_processor([Image.fromarray(rgb)],return_tensors='pt').pixel_values.to('cuda',dtype=torch.float16)
                _,flags=safety(images=rgb[None].astype(np.float32)/255,clip_input=inputs)
            if flags!=[False]:raise RuntimeError('Safety checker blocked output')
        def save_png(name,rgb):
            safety_check(rgb);path=output/(name+'.png');Image.fromarray(rgb).save(path)
            with Image.open(path) as im:saved=np.asarray(im.convert('RGB')).copy()
            if not np.array_equal(saved,rgb):raise ValueError('PNG pixel mismatch')
            return saved,dict(path=str(path),sha256=util.sha(path),rgb8_sha256=hashlib.sha256(saved.tobytes()).hexdigest())
        def save_array(name,value):
            path=output/(name+'.npy');np.save(path,value,allow_pickle=False)
            return dict(path=str(path),sha256=util.sha(path))
        def cycle(rgb):
            with torch.inference_mode():
                x=processor.preprocess(Image.fromarray(rgb)).to('cuda',dtype=torch.float16)
                z=reader_vae.encode(x).latent_dist.mode()*.18215
                decoded=reader_vae.decode(z/.18215,return_dict=False)[0]
                safety_input=safety_processor(processor.postprocess(decoded,output_type='pil'),return_tensors='pt').pixel_values.to('cuda',dtype=torch.float16)
                checked,flags=safety(images=decoded,clip_input=safety_input)
                if flags!=[False]:raise RuntimeError('VAE cycle safety checker blocked output')
                value=processor.postprocess(checked,output_type='np',do_denormalize=[True])[0]
            return blind.rgb8(value)
        def q(a,b):
            val=quality(a,b);val['lpips']=lpips_score(metric,a,b)
            val['quality_admissible']=(val['psnr_infinite'] or val['psnr_db']>35) and val['ssim_rgb']>.9 and val['lpips']<.1
            return val
        def placement(device,ident):
            def snapshot(stage):
                torch.cuda.synchronize()
                free,total=torch.cuda.mem_get_info(0)
                value=dict(kind='gpu_memory',source_id=ident,stage=stage,
                    allocated_bytes=torch.cuda.memory_allocated(),reserved_bytes=torch.cuda.memory_reserved(),
                    peak_allocated_bytes=torch.cuda.max_memory_allocated(),free_bytes=int(free),total_bytes=int(total))
                event(value);return value
            before=snapshot('before_inference_models_to_'+device)
            sizes=move_inference_models((reader_vae,safety),device)
            gc.collect();torch.cuda.empty_cache()
            after=snapshot('after_inference_models_to_'+device)
            ce.setdefault('memory_placements',[]).append(dict(device=device,model_tensor_bytes=sizes,before=before,after=after));persist();check()
        for case in cfg['cases']:
            check();ident=case['id'];source,_=old_a.source_rgb(case)
            source,receipt=save_png(f'{ident}-source',source)
            ce=dict(source_id=ident,outcome='started',source=receipt,checkpoints=[]);record['case_events'].append(ce);persist()
            E=feature(source);H=codec.perceptual_hash(codec.luminance_from_rgb(source.tolist()),profile=profile)
            ce.update(source_E=E.tolist(),source_H=H)
            u0,initial=old_a.reconstruction_latent(RECONSTRUCTION,ident,200,receipt['rgb8_sha256'])
            ce['initialization']=initial
            identity=dict(version=VERSION,**fingerprint,source_id=ident,source_rgb8_sha256=receipt['rgb8_sha256'],initialization=initial)
            resume=None
            if prior:
                old=[e for e in prior['case_events'] if e['source_id']==ident]
                if old and old[0]['checkpoints']:
                    selected=max(old[0]['checkpoints'],key=lambda e:e['step'])
                    resume=checkpoint_load(selected,identity);ce['resume_checkpoint']=selected
            source_tensor=tensor(source);u0=u0.to('cuda');oracle=FixedSourceScores(E,H,core.OWNERS[0],'cuda')
            def save(step,u,optimizer):
                cr=checkpoint_save(output/f'{ident}-step{step:03d}.pt',u,optimizer,step,identity)
                ce['checkpoints'].append(cr);event(dict(kind='checkpoint',source_id=ident,**cr));persist();check()
            placement('cpu',ident)
            result=optimize(embedder,source_tensor,u0,oracle,cfg,lambda r:event(dict(kind='optimizer',source_id=ident,**r)),save,check,resume)
            placement('cuda',ident)
            raw=array(result['residual']);marked,cap=residual.cap(source,raw)
            ce.update(cap=cap,beta_final=result['beta'],residual_rms=result['rho'],
                final_surrogate_scores=result['surrogate_scores'],final_surrogate_cycle_scores=result['surrogate_cycle_scores'],
                surrogate_vs_capped_rmse=float(np.sqrt(np.mean((array(result['surrogate'])-marked.astype(np.float64)/255)**2))),
                pure_reference_quality=q(source,blind.rgb8(array(result['reference']))),pure_final_quality=q(source,blind.rgb8(array(result['decoded']))),
                float_arrays={name:save_array(f'{ident}-{name}',array(result[name])) for name in ('reference','decoded','residual','surrogate')})
            images={('C0','clean'):source,('C1','clean'):marked}
            images[('C0','vae_cycle')]=cycle(source);images[('C1','vae_cycle')]=cycle(marked)
            for (arm,dose),rgb in images.items():
                check();row=rows[f'{ident}-{arm}-{dose}'];row['outcome']='started';retain(row)
                rgb,img=save_png(f'{ident}-{arm}-{dose}',rgb)
                tick=time.monotonic();decisions={owner:detect(rgb,owner,public) for owner in core.OWNERS};elapsed=time.monotonic()-tick
                e,h,z=public.observations(rgb)
                with torch.no_grad():z32=embedder.encode(tensor(rgb)).float().cpu().numpy().reshape(-1).astype(np.float64)
                row.update(outcome='completed',image=img,source=receipt,owner_decisions=decisions,extract_seconds=elapsed,
                    source_clip_cosine=float(E@e),source_phash_distance=int((H^h).bit_count()),suspect_E=e.tolist(),suspect_H=h,
                    source_template_oracle_fp16=core.scores(z,E,H,core.OWNERS[0]),source_template_oracle_fp32=core.scores(z32,E,H,core.OWNERS[0]),
                    terminal_reader_latent=save_array(f'{ident}-{arm}-{dose}-reader-z',z),
                    terminal_fp32_latent=save_array(f'{ident}-{arm}-{dose}-fp32-z',z32),
                    projection_diagnostics={owner:core.projection_diagnostic(E,H,e,h,owner) for owner in core.OWNERS},
                    quality_vs_source=q(source,rgb),quality_vs_same_arm_clean=q(images[(arm,'clean')],rgb))
                retain(row)
            ce['outcome']='completed';persist()
            if replay and ident==IDS[0]:
                ce['execution_replay']=verify_completed_case_replay(ce,list(rows.values()),replay)
                record['execution_replay']=ce['execution_replay'];persist()
            del source_tensor,u0,oracle,result;gc.collect();torch.cuda.empty_cache();check()
        record['outcome']='completed'
        record['peak_allocated_bytes']=torch.cuda.max_memory_allocated()
    except (Exception,KeyboardInterrupt) as error:
        record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error),traceback=traceback.format_exc())
        if record['case_events'] and record['case_events'][-1]['outcome']=='started':record['case_events'][-1]['outcome']=record['outcome']
    finally:
        for row in rows.values():
            if row['outcome'] in ('planned','started'):row['outcome']='not_completed_after_stop';event(dict(kind='condition',**row))
        util.write(output/'conditions.json',list(rows.values()))
        record.update(duration_seconds=previous_duration+time.monotonic()-started,attempt_duration_seconds=time.monotonic()-started,
            gate=pilot_gate(list(rows.values())),
            output_hashes={p.name:util.sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'})
        persist()
    return 0 if record['outcome']=='completed' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write-manifest',type=Path);group.add_argument('--run',action='store_true')
    parser.add_argument('--manifest',type=Path);parser.add_argument('--output-dir',type=Path);parser.add_argument('--resume-from',type=Path)
    parser.add_argument('--replay-reference',type=Path,help='Fresh-run parity against a prior completed first source; never initializes from it')
    args=parser.parse_args()
    if args.write_manifest:
        with args.write_manifest.open('x',encoding='utf-8') as f:json.dump(configuration(),f,indent=2);f.write('\n')
    elif not args.manifest or not args.output_dir:parser.error('--run requires --manifest and --output-dir')
    else:raise SystemExit(run(args.manifest,args.output_dir,args.resume_from,args.replay_reference))
