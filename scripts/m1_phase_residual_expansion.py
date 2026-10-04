"""Frozen IPS quality-cap expansion on remaining ten development sources.

Reuse vetted PhaseMark IPS and exact residual cap; no model loads on import.
Public presence carrier only, not content-binding or a three-state method.
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
import m1_phasemark as phase
MAIN=phase.MAIN
VERSION='m1-phasemark-residual-expansion-v1'
IDS=(6012,25394,80932,109798,134882,147498,177015,190676,468505,499768)
from m1_phase_residual import compose,pixel_sse,cap


def configuration():
    reserved=json.loads((ROOT/'research/m1-reconstruction-dev.json').read_text(encoding='utf-8'))
    if reserved.get('data_split')!='development':raise ValueError('Development source reservation required')
    cases=[c for c in reserved['cases'] if c['id'] in IDS]
    if [c['id'] for c in cases]!=list(IDS):raise ValueError('Exact remaining-ten reservation required')
    return dict(schema=VERSION,data_split='development',ids=list(IDS),arms=['IPS'],profiles=['quality-cap'],owners=list(phase.OWNERS),
        threshold=82,psnr_cap_db=35.2,bisection_steps=36,run_seconds_cap=900,gpu_budget_bytes=10*1024**3,
        ram_budget_bytes=16*1024**3,artifact_budget_bytes=250*1024**2,cases=cases,
        payloads={o:phase.payload(o) for o in phase.OWNERS},rectangles=[list(b) for b in phase.bit_blocks()],
        upstream_revision=phase.REVISION,upstream_hashes=phase.UPSTREAM_HASHES,
        source_policy='RGB required; EXIF transpose; embedded ICC to sRGB intent0 flags0; bicubic512',
        latent_policy='fresh fp32 posterior mean times .18215; D01 decode clamp; float64 signed residual',seed=0)


def validate(manifest):
    if manifest!=configuration():raise ValueError('Frozen expansion manifest differs from reserved configuration')
    return manifest['cases']


def planned():
    return [dict(id=f'{i}-IPS-quality-cap-{c}-{d}',source_id=i,arm='IPS',profile='quality-cap',control=c,dose=d,
                 outcome='planned',human_visual_verdict=None)
        for i in IDS for c in ('C0','C1') for d in ('clean','vae_cycle')]


def source_bypass(source,unmarked_decode,marked_decode):
    """Exact cap on signed decoded residual; no detector or learned metric input."""
    import numpy as np
    delta=marked_decode.astype(np.float64)-unmarked_decode.astype(np.float64)
    marked,receipt=cap(source,delta)
    receipt.update(delta_float64_sha256=hashlib.sha256(delta.tobytes()).hexdigest(),delta_l2=float(np.linalg.norm(delta)),
                   rounding='numpy.rint ties-to-even',decoder_precision='float32',composition_precision='float64')
    return marked,receipt


def run(manifest_path,output):
    import numpy as np
    output=Path(output).resolve();manifest_path=Path(manifest_path).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('MAIN development output required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    rows={r['id']:r for r in planned()};cfg={}
    record=dict(schema=VERSION,command=sys.argv,data_split='development',seeds=[0],config=cfg,outcome='started',duration_seconds=0)
    def retain(row):
        rows[row['id']]=row
        with (output/'rows.jsonl').open('a',encoding='utf-8') as handle:handle.write(json.dumps(row,allow_nan=False)+'\n')
        phase.write(output/'conditions.json',list(rows.values()))
    def check():
        if time.monotonic()-started>cfg['run_seconds_cap']:raise RuntimeError('Wall-time cap reached')
        ram=phase.working_set_bytes();record['peak_observed_ram_bytes']=max(record.get('peak_observed_ram_bytes',0),ram)
        if ram>cfg['ram_budget_bytes']:raise RuntimeError('RAM cap reached')
        if torch.cuda.memory_allocated()>cfg['gpu_budget_bytes']:raise RuntimeError('GPU cap reached')
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise RuntimeError('Artifact cap reached')
    phase.write(output/'run.json',record)
    for row in list(rows.values()):retain(row)
    try:
        cfg=configuration();record['config']=cfg
        cases=validate(json.loads(manifest_path.read_text(encoding='utf-8')))
        dependencies=[Path(__file__),manifest_path,ROOT/'scripts/m1_phasemark.py',ROOT/'research/m1-phasemark-pilot-decision.md',ROOT/'scripts/m1_phase_residual.py',ROOT/'research/m1-reconstruction-dev.json',
            ROOT/'scripts/m1_latent_reconstruction.py',ROOT/'scripts/three_threat_models.py',ROOT/'scripts/three_threat_protocol.py',
            ROOT/'scripts/check_a6_lpips_assets.py',ROOT/'scripts/verify_science_assets.py',ROOT/'scripts/a6_clip_visual.py',ROOT/'research/a6-candidate-model-assets.json']+[phase.UPSTREAM/n for n in phase.UPSTREAM_HASHES]
        record.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            committed_files=phase.require_committed(dependencies),manifest_sha256=phase.sha(manifest_path))
        (output/'manifest.json').write_bytes(manifest_path.read_bytes())
        for name,digest in phase.UPSTREAM_HASHES.items():
            if phase.sha(phase.UPSTREAM/name)!=digest:raise ValueError('Official phase source changed: '+name)
        record.update(upstream_revision=phase.REVISION,upstream_hashes=phase.UPSTREAM_HASHES,
                      payloads=cfg['payloads'],rectangles=cfg['rectangles'],source_policy=cfg['source_policy'],
                      labels='public128-bit phase presence carrier; source bypass; no three-state/content binding')
        from three_threat_models import block_network,verify_assets,load_lpips,lpips_score,clip_feature
        block_network()
        import torch
        from PIL import Image,ImageOps,ImageCms
        import io
        from diffusers import AutoencoderKL
        from a6_clip_visual import load_visual_encoder
        from m1_latent_reconstruction import quality
        if not torch.cuda.is_available():raise RuntimeError('CUDA required')
        torch.manual_seed(0);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False
        torch.cuda.set_per_process_memory_fraction(min(1.,cfg['gpu_budget_bytes']/torch.cuda.get_device_properties(0).total_memory))
        assets,package=verify_assets(phase.ASSETS,ROOT/'research/a6-candidate-model-assets.json')
        metric=load_lpips(phase.ASSETS,package);clip,transform=load_visual_encoder(phase.ASSETS/'clip/ViT-B-32.pt',device='cpu')
        vae=AutoencoderKL.from_pretrained(phase.ASSETS/'sd15-fp16/vae',variant='fp16',use_safetensors=True,local_files_only=True,torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        scale=float(vae.config.scaling_factor)
        if scale!=.18215:raise ValueError('Pinned SD1.5 latent scaling mismatch')
        record.update(assets=assets,environment={'python':sys.version,**{name:importlib.metadata.version(name) for name in ('torch','numpy','scipy','Pillow','diffusers','lpips')}},vae_scaling_factor=scale,lpips_learned_sha256=phase.sha(package/'weights/v0.1/alex.pth'),
            detector_side_information=['suspect RGB8','public owner payload','phase arm','pinned VAE/mask'],output_operator='phase-latent-residual-source-bypass')
        phase.write(output/'run.json',record)
        def read(path):
            with Image.open(path) as image:return np.asarray(image.convert('RGB')).copy()
        def save(name,rgb):
            path=output/(name+'.png');Image.fromarray(rgb).save(path);saved=read(path)
            if not np.array_equal(saved,rgb):raise ValueError('PNG pixel mismatch')
            return saved,dict(path=str(path),sha256=phase.sha(path),rgb8_sha256=hashlib.sha256(saved.tobytes()).hexdigest())
        def encode(rgb):
            with torch.inference_mode():value=vae.encode((torch.from_numpy(rgb.copy()).permute(2,0,1)[None].float().to('cuda')/255)*2-1).latent_dist.mean*scale
            if tuple(value.shape)!=(1,4,64,64) or value.dtype!=torch.float32 or not bool(torch.isfinite(value).all()):raise ValueError('Posterior mean contract mismatch')
            return value
        def decode(z):
            with torch.inference_mode():value=((vae.decode(z/scale,return_dict=False)[0]+1)/2)[0].permute(1,2,0).clamp(0,1)
            if tuple(value.shape)!=(512,512,3) or value.dtype!=torch.float32 or not bool(torch.isfinite(value).all()):raise ValueError('Nonfinite/malformed decoded latent')
            return value.cpu().numpy()
        def q(left,right):
            value=quality(left,right);value['lpips']=lpips_score(metric,left,right)
            value['clip_cosine']=float((clip_feature(clip,transform,left)*clip_feature(clip,transform,right)).sum())
            value['quality_admissible']=(value['psnr_infinite'] or value['psnr_db']>35) and value['ssim_rgb']>.9 and value['lpips']<.1
            return value
        for case in cases:
            ident=case['id'];check()
            try:
                if phase.sha(case['path'])!=case['sha256']:raise ValueError('Raw development source hash differs')
                with Image.open(case['path']) as image:
                    if image.mode!='RGB':raise ValueError('RGB source required')
                    image.load();icc=image.info.get('icc_profile');image=ImageOps.exif_transpose(image)
                    if icc:image=ImageCms.profileToProfile(image,ImageCms.ImageCmsProfile(io.BytesIO(icc)),ImageCms.createProfile('sRGB'),renderingIntent=0,outputMode='RGB',flags=0)
                    source=np.asarray(image.resize((512,512),Image.Resampling.BICUBIC)).copy()
                source,source_receipt=save(f'{ident}-C0-clean',source)
                source_receipt.update(raw_path=case['path'],raw_sha256=case['sha256'])
                z0=encode(source)
                if tuple(z0.shape)!=(1,4,64,64) or z0.dtype!=torch.float32 or not bool(torch.isfinite(z0).all()):raise ValueError('Fresh posterior contract mismatch')
                with torch.inference_mode():zm,embedding=phase.embed_latent(z0,phase.payload(phase.OWNERS[0]),'IPS')
                if embedding['inverse_imag_max_abs']>1e-5:raise ValueError('Significant Hermitian imaginary residual')
                latent_receipts={}
                for label,z in (('C0',z0),('C1',zm)):
                    path=output/f'{ident}-{label}-latent.pt'
                    torch.save(dict(scaled_z=z.cpu(),units='VAE posterior mean multiplied by scaling_factor',scaling_factor=scale),path)
                    latent_receipts[label]=dict(path=str(path),sha256=phase.sha(path))
                marked,composition=source_bypass(source,decode(z0),decode(zm))
                marked,marked_receipt=save(f'{ident}-IPS-quality-cap-C1-clean',marked)
                # Saved/reopened RGB8 is the input to both attack and detector.
                cycle0,cycle0_receipt=save(f'{ident}-C0-cycle',np.rint(255*decode(encode(source))).astype(np.uint8))
                cycled,cycled_receipt=save(f'{ident}-IPS-quality-cap-C1-cycle',np.rint(255*decode(encode(marked))).astype(np.uint8))
                for control,dose,rgb,receipt in (('C0','clean',source,source_receipt),('C0','vae_cycle',cycle0,cycle0_receipt),('C1','clean',marked,marked_receipt),('C1','vae_cycle',cycled,cycled_receipt)):
                    row=rows[f'{ident}-IPS-quality-cap-{control}-{dose}'];row.update(outcome='started',image=receipt,source=source_receipt,
                         latent_receipts=latent_receipts,embedding=embedding if control=='C1' else None,
                         composition=composition if control=='C1' else None);retain(row)
                    try:
                        check();torch.cuda.synchronize();tick=time.monotonic();extracted=phase.extract_latent(encode(rgb),'IPS');torch.cuda.synchronize();elapsed=time.monotonic()-tick
                        decisions={owner:dict(matches=sum(a==b for a,b in zip(extracted['bits'],phase.payload(owner)))) for owner in phase.OWNERS}
                        for value in decisions.values():value.update(present=value['matches']>=82,bit_accuracy=value['matches']/128)
                        row.update(outcome='completed',extracted=extracted,owner_decisions=decisions,extract_seconds=elapsed,
                                   quality_vs_source=q(source,rgb),quality_vs_same_arm_clean=q(source if control=='C0' else marked,rgb))
                    except Exception as error:row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc())
                    retain(row)
                del z0,zm;torch.cuda.empty_cache()
            except Exception as error:
                for row in list(rows.values()):
                    if row['source_id']==ident and row['outcome']!='completed':row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc());retain(row)
        record['outcome']='completed' if all(r['outcome']=='completed' for r in rows.values()) else 'incomplete'
        record['peak_allocated_bytes']=torch.cuda.max_memory_allocated()
    except (Exception,KeyboardInterrupt) as error:
        record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error),traceback=traceback.format_exc())
    finally:
        for row in list(rows.values()):
            if row['outcome'] in ('planned','started'):row.update(outcome='not_completed_after_stop');retain(row)
        record.update(conditions=list(rows.values()),duration_seconds=time.monotonic()-started,output_hashes={p.name:phase.sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'})
        phase.write(output/'run.json',record)
    return 0 if record['outcome']=='completed' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();raise SystemExit(run(args.manifest,args.output_dir))
