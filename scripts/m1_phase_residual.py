"""Fixed source-bypass PhaseMark diagnostic; original pilot stays immutable."""
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
SOURCE=MAIN/'.thesis-build/dev-runs/20261003-2355-phasemark-pilot'
SOURCE_SHA='0fd2f7f8a1cdb34e6a129f753eb1f090e279cd8c1018a774a262a84bb7a123c8'
VERSION='m1-phasemark-residual-v1'
PROFILES=('full','quality-cap')

def compose(source,delta,weight):
    import numpy as np
    if source.dtype!=np.uint8 or source.shape!=delta.shape or not np.isfinite(delta).all():
        raise ValueError('Matching finite residual and RGB8 source required')
    if not 0<=weight<=1:raise ValueError('Weight outside frozen interval')
    return np.rint(255*np.clip(source.astype(np.float64)/255+weight*delta.astype(np.float64),0,1)).astype(np.uint8)

def pixel_sse(left,right):
    import numpy as np
    difference=left.astype(np.int64)-right.astype(np.int64)
    return int(np.square(difference).sum())

def cap(source,delta):
    budget=255**2*10**(-35.2/10)
    def feasible(weight):return pixel_sse(source,compose(source,delta,weight))/source.size<=budget
    lo,hi=0.,1.
    if feasible(1.):lo=hi=1.
    else:
        for _ in range(36):
            mid=(lo+hi)/2
            if feasible(mid):lo=mid
            else:hi=mid
    rgb=compose(source,delta,lo);sse=pixel_sse(source,rgb)
    if sse/source.size>budget:raise ValueError('Saved-pixel cap violated')
    return rgb,dict(weight=lo,lo=lo,hi=hi,budget_mse_rgb8=budget,sse_rgb8=sse,mse_rgb8=sse/source.size,iterations=0 if lo==1 else 36)

def planned():
    return [dict(id=f'{ident}-{arm}-{profile}-{control}-{dose}',source_id=ident,arm=arm,profile=profile,control=control,dose=dose,outcome='planned',human_visual_verdict=None)
        for ident in phase.IDS for arm in phase.ARMS for profile in PROFILES for control in ('C0','C1') for dose in ('clean','vae_cycle')]

def configuration():
    return dict(schema=VERSION,data_split='development',input_run=str(SOURCE),input_run_sha256=SOURCE_SHA,
        ids=list(phase.IDS),arms=list(phase.ARMS),profiles=list(PROFILES),owners=list(phase.OWNERS),
        threshold=82,psnr_cap_db=35.2,bisection_steps=36,run_seconds_cap=600,gpu_budget_bytes=10*1024**3,
        ram_budget_bytes=16*1024**3,artifact_budget_bytes=250*1024**2)

def run(manifest_path,output):
    import numpy as np
    output=Path(output).resolve();manifest_path=Path(manifest_path).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('MAIN development output required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    rows={r['id']:r for r in planned()};cfg=configuration()
    record=dict(schema=VERSION,command=sys.argv,data_split='development',seeds=[0],config=cfg,outcome='started',duration_seconds=0)
    def retain(row):
        rows[row['id']]=row
        with (output/'rows.jsonl').open('a',encoding='utf-8') as handle:handle.write(json.dumps(row,allow_nan=False)+'\n')
        phase.write(output/'conditions.json',list(rows.values()))
    def check():
        if time.monotonic()-started>cfg['run_seconds_cap']:raise RuntimeError('Wall-time cap reached')
        if phase.working_set_bytes()>cfg['ram_budget_bytes']:raise RuntimeError('RAM cap reached')
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise RuntimeError('Artifact cap reached')
    for row in list(rows.values()):retain(row)
    try:
        if json.loads(manifest_path.read_text())!=cfg:raise ValueError('Frozen configuration differs')
        dependencies=[Path(__file__),manifest_path,ROOT/'scripts/m1_phasemark.py',ROOT/'research/m1-phasemark-pilot-decision.md',
            ROOT/'scripts/m1_latent_reconstruction.py',ROOT/'scripts/three_threat_models.py',ROOT/'scripts/three_threat_protocol.py',
            ROOT/'scripts/check_a6_lpips_assets.py',ROOT/'scripts/verify_science_assets.py',ROOT/'scripts/a6_clip_visual.py',ROOT/'research/a6-candidate-model-assets.json']
        record.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            committed_files=phase.require_committed(dependencies),manifest_sha256=phase.sha(manifest_path))
        (output/'manifest.json').write_bytes(manifest_path.read_bytes())
        if phase.sha(SOURCE/'run.json')!=SOURCE_SHA:raise ValueError('Source run changed')
        old=json.loads((SOURCE/'run.json').read_text());record['input_receipts']=dict(run_sha256=SOURCE_SHA,files={})
        if old['outcome']!='completed':raise ValueError('Source pilot not complete')
        # Check every retained pilot artifact, not just the successful rows.
        for name,digest in old['output_hashes'].items():
            if phase.sha(SOURCE/name)!=digest:raise ValueError('Changed pilot artifact '+name)
            record['input_receipts']['files'][name]=digest
        (output/'input-run.json').write_bytes((SOURCE/'run.json').read_bytes())
        from three_threat_models import block_network,verify_assets,load_lpips,lpips_score,clip_feature
        block_network()
        import torch
        from PIL import Image
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
        if scale!=old['vae_scaling_factor']:raise ValueError('Latent scaling mismatch')
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
            with torch.inference_mode():return vae.encode((torch.from_numpy(rgb.copy()).permute(2,0,1)[None].float().to('cuda')/255)*2-1).latent_dist.mean*scale
        def decode(z):
            with torch.inference_mode():value=((vae.decode(z/scale,return_dict=False)[0]+1)/2)[0].permute(1,2,0).clamp(0,1)
            if not bool(torch.isfinite(value).all()):raise ValueError('Nonfinite decoded latent')
            return value.cpu().numpy()
        def load_decode(name,png):
            value=torch.load(SOURCE/name,map_location='cpu',weights_only=True)
            if value['scaling_factor']!=scale or value['scaled_z'].dtype!=torch.float32 or tuple(value['scaled_z'].shape)!=(1,4,64,64):raise ValueError('Stored latent contract mismatch')
            decoded=decode(value['scaled_z'].to('cuda'))
            if not np.array_equal(np.rint(255*decoded).astype(np.uint8),read(SOURCE/png)):raise ValueError('Re-decoded pilot pixels differ: '+name)
            return decoded.astype(np.float64)
        def q(left,right):
            value=quality(left,right);value['lpips']=lpips_score(metric,left,right)
            value['clip_cosine']=float((clip_feature(clip,transform,left)*clip_feature(clip,transform,right)).sum())
            value['quality_admissible']=(value['psnr_infinite'] or value['psnr_db']>35) and value['ssim_rgb']>.9 and value['lpips']<.1
            return value
        for ident in phase.IDS:
            check();source=read(SOURCE/f'{ident}-source.png')
            source,source_receipt=save(f'{ident}-C0-clean',source)
            d0=load_decode(f'{ident}-C0-latent.pt',f'{ident}-C0.png')
            cycle0,cycle0_receipt=save(f'{ident}-C0-cycle',np.rint(255*decode(encode(source))).astype(np.uint8))
            for arm in phase.ARMS:
                dm=load_decode(f'{ident}-{arm}-C1-latent.pt',f'{ident}-{arm}-C1.png');delta=dm-d0
                for profile in PROFILES:
                    check()
                    if profile=='full':
                        marked=compose(source,delta,1);composition=dict(weight=1.,sse_rgb8=pixel_sse(source,marked))
                    else:marked,composition=cap(source,delta)
                    composition.update(delta_float64_sha256=hashlib.sha256(delta.tobytes()).hexdigest(),delta_l2=float(np.linalg.norm(delta)),rounding='numpy.rint ties-to-even',decoder_precision='float32',composition_precision='float64')
                    marked,marked_receipt=save(f'{ident}-{arm}-{profile}-C1-clean',marked)
                    cycled,cycled_receipt=save(f'{ident}-{arm}-{profile}-C1-cycle',np.rint(255*decode(encode(marked))).astype(np.uint8))
                    for control,dose,rgb,receipt in (('C0','clean',source,source_receipt),('C0','vae_cycle',cycle0,cycle0_receipt),('C1','clean',marked,marked_receipt),('C1','vae_cycle',cycled,cycled_receipt)):
                        row=rows[f'{ident}-{arm}-{profile}-{control}-{dose}'];row.update(outcome='started',image=receipt,source=source_receipt);retain(row)
                        try:
                            check();torch.cuda.synchronize();tick=time.monotonic();extracted=phase.extract_latent(encode(rgb),arm);torch.cuda.synchronize();elapsed=time.monotonic()-tick
                            decisions={owner:dict(matches=sum(a==b for a,b in zip(extracted['bits'],phase.payload(owner)))) for owner in phase.OWNERS}
                            for value in decisions.values():value.update(present=value['matches']>=82,bit_accuracy=value['matches']/128)
                            row.update(outcome='completed',composition=composition if control=='C1' else None,extracted=extracted,owner_decisions=decisions,extract_seconds=elapsed,
                                quality_vs_source=q(source,rgb),quality_vs_same_arm_clean=q(source if control=='C0' else marked,rgb))
                        except Exception as error:row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc())
                        retain(row)
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
