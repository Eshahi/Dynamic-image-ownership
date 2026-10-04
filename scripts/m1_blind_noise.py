"""B3-C initial-noise continuous templates; blind VAE/CLIP/hash readout."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_phasemark as util
import revised_watermark_v5 as codec
MAIN=util.MAIN
VERSION='m1-blind-noise-template-v1'
IDS=(1675,4795)
ALPHAS=(.025,.05,.1)
ROUTES=('pure','hybrid')

def config():
    cohort=json.loads((ROOT/'research/m1-reconstruction-dev.json').read_text())
    if [c['id'] for c in cohort['cases'] if c['id'] in IDS]!=list(IDS):raise ValueError('Exact ordered pilot sources required')
    return dict(schema=VERSION,data_split='development',cases=[c for c in cohort['cases'] if c['id'] in IDS],
        alphas=list(ALPHAS),routes=list(ROUTES),owners=list(util.OWNERS),thresholds=dict(s=4.,i=4.),steps=50,guidance_scale=1.,eta=0.,seed=0,
        run_seconds_cap=900,gpu_budget_bytes=10*1024**3,ram_budget_bytes=16*1024**3,artifact_budget_bytes=500*1024**2,
        profile='configs/revised-watermark-v5.example.json',selection='smallest hybrid dose passing frozen clean quality and carrier gates')

def planned():
    return [dict(id=f'{ident}-{alpha}-{route}-{control}-{dose}',source_id=ident,alpha=alpha,route=route,control=control,dose=dose,outcome='planned',human_visual_verdict=None)
        for ident in IDS for alpha in ALPHAS for route in ROUTES for control in ('C0','C1') for dose in ('clean','vae_cycle')]

def rgb8(value):
    import numpy as np
    value=np.asarray(value,dtype=np.float64)
    if value.shape!=(512,512,3) or not np.isfinite(value).all():raise ValueError('Finite 512x512x3 float RGB required')
    return np.rint(255*np.clip(value,0,1)).astype(np.uint8)

def bypass(source,marked,baseline):
    import numpy as np
    return rgb8(source.astype(np.float64)/255+np.asarray(marked,np.float64)-np.asarray(baseline,np.float64))

def detect(image_rgb8,owner_id,pinned_public_profile_and_models):
    """Only suspect/owner/public runtime crosses this boundary; no enrollment."""
    public=pinned_public_profile_and_models
    import numpy as np
    if not isinstance(image_rgb8,np.ndarray) or image_rgb8.dtype!=np.uint8 or image_rgb8.shape!=(512,512,3):raise ValueError('RGB8 suspect required')
    E,H,z=public.observations(image_rgb8)
    import m1_blind_noise_core as core
    return core.scores(z,E,H,owner_id)

def run(manifest_path,output):
    import numpy as np
    output=Path(output).resolve();manifest_path=Path(manifest_path).resolve();cfg=config()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN development output required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic();rows={r['id']:r for r in planned()}
    record=dict(schema=VERSION,data_split='development',command=sys.argv,seeds=[0],config=cfg,outcome='started',duration_seconds=0)
    def retain(row):
        with (output/'rows.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row,allow_nan=False)+'\n')
        util.write(output/'conditions.json',list(rows.values()))
    def check():
        if time.monotonic()-started>cfg['run_seconds_cap']:raise RuntimeError('Wall-time cap')
        if util.working_set_bytes()>cfg['ram_budget_bytes']:raise RuntimeError('RAM cap')
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise RuntimeError('Artifact cap')
    for row in rows.values():retain(row)
    try:
        if json.loads(manifest_path.read_text())!=cfg:raise ValueError('Exact frozen configuration required')
        deps=[Path(__file__),manifest_path,ROOT/'scripts/m1_blind_noise_core.py',ROOT/'research/m1-blind-noise-template-design.md',ROOT/'scripts/m1_gaussian_shading.py',
            ROOT/'scripts/m1_phasemark.py',ROOT/'scripts/m1_latent_reconstruction.py',ROOT/'scripts/three_threat_models.py',ROOT/'scripts/a6_clip_visual.py',
            ROOT/'scripts/verify_science_assets.py',ROOT/'scripts/check_a6_lpips_assets.py',ROOT/'research/a6-candidate-model-assets.json',
            ROOT/'research/m1-reconstruction-dev.json',ROOT/cfg['profile'],ROOT/'scripts/revised_watermark_v5.py']
        record.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),committed_files=util.require_committed(deps),manifest_sha256=util.sha(manifest_path))
        (output/'manifest.json').write_bytes(manifest_path.read_bytes());util.write(output/'run.json',record)
        from three_threat_models import block_network,verify_assets,DDIM_CONFIG,load_lpips,lpips_score,clip_feature
        block_network()
        import torch
        from PIL import Image,ImageOps,ImageCms
        from diffusers import StableDiffusionPipeline,DDIMScheduler,DDIMInverseScheduler
        from a6_clip_visual import load_visual_encoder
        from m1_latent_reconstruction import quality
        from m1_gaussian_shading import invert
        import m1_blind_noise_core as core
        if not torch.cuda.is_available():raise RuntimeError('CUDA required')
        torch.manual_seed(0);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False
        torch.cuda.set_per_process_memory_fraction(min(1.,cfg['gpu_budget_bytes']/torch.cuda.get_device_properties(0).total_memory))
        assets,package=verify_assets(util.ASSETS,ROOT/'research/a6-candidate-model-assets.json')
        pipe=StableDiffusionPipeline.from_pretrained(util.ASSETS/'sd15-fp16',variant='fp16',use_safetensors=True,local_files_only=True,torch_dtype=torch.float16).to('cuda')
        if pipe.safety_checker is None or pipe.feature_extractor is None:raise RuntimeError('Safety components missing')
        pipe.set_progress_bar_config(disable=True);pipe.scheduler=DDIMScheduler(**DDIM_CONFIG)
        inverse=DDIMInverseScheduler.from_config(pipe.scheduler.config)
        if inverse.config.prediction_type!='epsilon' or inverse.config.clip_sample or pipe.scheduler.init_noise_sigma!=1.:raise ValueError('Pinned epsilon unclipped unit-sigma scheduler required')
        if float(pipe.vae.config.scaling_factor)!=.18215:raise ValueError('Unexpected latent scale')
        clip,transform=load_visual_encoder(util.ASSETS/'clip/ViT-B-32.pt',device='cpu');metric=load_lpips(util.ASSETS,package)
        profile=codec.validate_profile(codec.load_profile(ROOT/cfg['profile']))
        record.update(assets=assets,scheduler=dict(pipe.scheduler.config),inverse_scheduler=dict(inverse.config),
            environment={'python':sys.version,**{p:importlib.metadata.version(p) for p in ('torch','numpy','scipy','Pillow','diffusers','lpips')}},
            detector_side_information=['suspect RGB8','candidate public OwnerID','pinned VAE/CLIP/hash profile and maps'],
            lpips_learned_sha256=util.sha(package/'weights/v0.1/alex.pth'),vae_scaling_factor=.18215,case_events=[],nfe_total=0)
        def count_nfe(*args):record['nfe_total']+=1
        hook=pipe.unet.register_forward_hook(count_nfe)
        def save(name,array):
            path=output/(name+'.png');Image.fromarray(array).save(path)
            with Image.open(path) as image:saved=np.asarray(image.convert('RGB')).copy()
            if not np.array_equal(saved,array):raise ValueError('PNG pixel mismatch')
            return saved,dict(path=str(path),sha256=util.sha(path),rgb8_sha256=hashlib.sha256(saved.tobytes()).hexdigest())
        def feature(rgb):
            value=np.asarray(clip_feature(clip,transform,rgb),np.float64).reshape(-1)
            norm=float(np.linalg.norm(value))
            if value.shape!=(512,) or not np.isfinite(value).all() or norm<=0:raise ValueError('Invalid CLIP feature')
            return value/norm
        def phash(rgb):return codec.perceptual_hash(codec.luminance_from_rgb(rgb.tolist()),profile=profile)
        def encode(rgb):
            with torch.inference_mode():
                x=pipe.image_processor.preprocess(Image.fromarray(rgb)).to('cuda',dtype=pipe.vae.dtype)
                return pipe.vae.encode(x).latent_dist.mode()*pipe.vae.config.scaling_factor
        class PublicReader:
            # Cache by the suspect's exact bytes only; no source features/labels.
            cache_key=None
            cache_value=None
            def observations(self,rgb):
                key=hashlib.sha256(rgb.tobytes()).hexdigest()
                if key!=self.cache_key:
                    z=encode(rgb).float().cpu().numpy().reshape(-1).astype(np.float64)
                    self.cache_value=(feature(rgb),phash(rgb),z);self.cache_key=key
                return self.cache_value
        public=PublicReader()
        def safe_float(result):
            if result.nsfw_content_detected!=[False] or len(result.images)!=1:raise RuntimeError('Safety checker blocked or malformed')
            value=np.asarray(result.images[0])
            if value.shape!=(512,512,3) or not np.isfinite(value).all():raise ValueError('Malformed float decoder output')
            return np.clip(value,0,1).astype(np.float64)
        def forward(noise,name):
            check();before=record['nfe_total'];torch.cuda.synchronize();tick=time.monotonic()
            with torch.inference_mode():result=pipe(prompt='',negative_prompt='',height=512,width=512,num_inference_steps=50,guidance_scale=1.,eta=0.,
                latents=torch.from_numpy(noise).to('cuda',dtype=torch.float16),generator=torch.Generator(device='cuda').manual_seed(0),output_type='np')
            torch.cuda.synchronize();value=safe_float(result);np.save(output/(name+'.npy'),value,allow_pickle=False)
            receipt=dict(seconds=time.monotonic()-tick,nfe=record['nfe_total']-before,timesteps=[int(t) for t in pipe.scheduler.timesteps],float_path=str(output/(name+'.npy')),float_sha256=util.sha(output/(name+'.npy')),safety_blocked=False)
            if receipt['nfe']!=50:raise ValueError('Forward NFE differs')
            return value,receipt
        def cycle(rgb):
            with torch.inference_mode():
                z=encode(rgb);decoded=pipe.vae.decode(z/pipe.vae.config.scaling_factor,return_dict=False)[0]
                checked,flags=pipe.run_safety_checker(decoded,'cuda',pipe.text_encoder.dtype)
                if flags!=[False]:raise RuntimeError('VAE safety checker blocked or malformed')
                value=pipe.image_processor.postprocess(checked,output_type='np',do_denormalize=[True])[0]
            return rgb8(value)
        def q(left,right):
            value=quality(left,right);value['lpips']=lpips_score(metric,left,right)
            value['quality_admissible']=(value['psnr_infinite'] or value['psnr_db']>35) and value['ssim_rgb']>.9 and value['lpips']<.1
            return value
        source_features={}
        for case in cfg['cases']:
            ident=case['id'];event=dict(source_id=ident,outcome='started');record['case_events'].append(event);util.write(output/'run.json',record)
            try:
                check()
                if util.sha(case['path'])!=case['sha256']:raise ValueError('Raw source hash differs')
                with Image.open(case['path']) as image:
                    if image.mode!='RGB':raise ValueError('RGB source required')
                    image.load();icc=image.info.get('icc_profile');image=ImageOps.exif_transpose(image)
                    if icc:image=ImageCms.profileToProfile(image,ImageCms.ImageCmsProfile(io.BytesIO(icc)),ImageCms.createProfile('sRGB'),renderingIntent=0,outputMode='RGB',flags=0)
                    source=np.asarray(image.resize((512,512),Image.Resampling.BICUBIC)).copy()
                source,source_receipt=save(f'{ident}-source',source);E,H=feature(source),phash(source);source_features[ident]=(E,H)
                target=core.template(E,H,util.OWNERS[0]);T=np.asarray(target['T'],np.float32).reshape(1,4,64,64)
                before=record['nfe_total'];torch.cuda.synchronize();tick=time.monotonic();n0=invert(pipe,Image.fromarray(source),inverse);torch.cuda.synchronize()
                event.update(inverse_nfe=record['nfe_total']-before,inverse_seconds=time.monotonic()-tick,inverse_timesteps=[int(t) for t in inverse.timesteps],source_E=E.tolist(),source_H=H,source=source_receipt)
                if event['inverse_nfe']!=50:raise ValueError('Inverse NFE differs')
                np.save(output/f'{ident}-n0.npy',n0,allow_pickle=False);np.save(output/f'{ident}-T.npy',T,allow_pickle=False)
                d0,forward0=forward(n0,f'{ident}-D0');event['C0_forward']=forward0
                controls={}
                for route in ROUTES:
                    c0=rgb8(d0) if route=='pure' else source
                    controls[route]=[save(f'{ident}-{route}-C0-clean',c0),save(f'{ident}-{route}-C0-vae',cycle(c0))]
                for alpha in ALPHAS:
                    supplied=(n0.astype(np.float32)+alpha*T).astype(np.float16)
                    np.save(output/f'{ident}-{alpha}-supplied.npy',supplied,allow_pickle=False)
                    da,forward_receipt=forward(supplied,f'{ident}-{alpha}-Da')
                    perturbation=dict(l2=float(np.linalg.norm(supplied.astype(np.float64)-n0)),rounding_l2=float(np.linalg.norm(supplied.astype(np.float64)-(n0.astype(np.float32)+alpha*T).astype(np.float64))),
                        supplied_sha256=hashlib.sha256(supplied.tobytes()).hexdigest(),template_rms=float(np.sqrt(np.mean(T.astype(np.float64)**2))))
                    for route in ROUTES:
                        marked=rgb8(da) if route=='pure' else bypass(source,da,d0)
                        marked_rows=[save(f'{ident}-{alpha}-{route}-C1-clean',marked),save(f'{ident}-{alpha}-{route}-C1-vae',cycle(marked))]
                        for control,images in (('C0',controls[route]),('C1',marked_rows)):
                            for dose,(rgb,receipt) in zip(('clean','vae_cycle'),images):
                                row=rows[f'{ident}-{alpha}-{route}-{control}-{dose}'];row.update(outcome='started',image=receipt,source=source_receipt);retain(row)
                                try:
                                    check();torch.cuda.synchronize();tick=time.monotonic();decisions={owner:detect(rgb,owner,public) for owner in util.OWNERS};torch.cuda.synchronize();elapsed=time.monotonic()-tick
                                    e,h,z=public.observations(rgb)
                                    drift={owner:core.projection_diagnostic(E,H,e,h,owner) for owner in util.OWNERS}
                                    row.update(outcome='completed',owner_decisions=decisions,extract_seconds=elapsed,source_clip_cosine=float(E@e),source_phash_distance=int((H^h).bit_count()),
                                        suspect_E=e.tolist(),suspect_H=h,projection_diagnostics=drift,semantic_template_cosine=float(E@e),
                                        quality_vs_source=q(source,rgb),quality_vs_same_arm_clean=q(images[0][0],rgb),forward=forward_receipt if control=='C1' else forward0,perturbation=perturbation if control=='C1' else None)
                                except Exception as error:row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc())
                                retain(row)
                event['outcome']='completed'
            except Exception as error:
                event.update(outcome='failed',error=repr(error),traceback=traceback.format_exc())
                for row in rows.values():
                    if row['source_id']==ident and row['outcome'] in ('planned','started'):row.update(outcome='failed',error=repr(error));retain(row)
            util.write(output/'run.json',record)
        if len(source_features)==2:
            e,h=source_features[IDS[0]];f,g=source_features[IDS[1]]
            record['source_pair_projection']={owner:core.projection_diagnostic(e,h,f,g,owner) for owner in util.OWNERS}
        record['outcome']='completed' if all(r['outcome']=='completed' for r in rows.values()) else 'incomplete'
        if record['outcome']=='completed' and record['nfe_total']!=500:raise ValueError('Whole-run NFE must equal500')
        record['peak_allocated_bytes']=torch.cuda.max_memory_allocated();hook.remove()
    except (Exception,KeyboardInterrupt) as error:record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error),traceback=traceback.format_exc())
    finally:
        for row in rows.values():
            if row['outcome'] in ('planned','started'):row.update(outcome='not_completed_after_stop');retain(row)
        record.update(conditions=list(rows.values()),duration_seconds=time.monotonic()-started,output_hashes={p.name:util.sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'})
        util.write(output/'run.json',record)
    return 0 if record['outcome']=='completed' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();raise SystemExit(run(args.manifest,args.output_dir))
