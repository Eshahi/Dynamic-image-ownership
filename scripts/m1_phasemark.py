"""Family D PhaseMark APM/IPS research adaptation; no models load on import.

Adapted from Sung Ju Lee and Nam Ik Cho's PhaseMark, revision
dfe42ad0449459e26fe1579957c6d05ccdee9b92, utils.py/fast_try.py.
Copyright (c) 2026 Sung Ju Lee, Nam Ik Cho (Seoul National University).
CC BY-NC 4.0: https://creativecommons.org/licenses/by-nc/4.0/
Source: https://github.com/thomas11809/PhaseMark/tree/dfe42ad0449459e26fe1579957c6d05ccdee9b92
Changes: offline SD1.5 RGB8 pilot, public SHAKE payload, corrected integer-tail
rule, float metrics, receipts, soft scores and failure inventory. No upstream
module is imported. Layout/modulation/Hermitian conventions are retained.
"""
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
MAIN=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ASSETS=MAIN/'.thesis-build/assets/a6'
UPSTREAM=ROOT/'research/literature/m1-primary-extension/phasemark-code'
VERSION='m1-phasemark-pilot-v1'
REVISION='dfe42ad0449459e26fe1579957c6d05ccdee9b92'
IDS=(1675,4795)
OWNERS=tuple('qim-pilot-owner-'+o for o in ('alpha','beta','gamma','delta'))
ARMS=('APM','IPS')
UPSTREAM_HASHES={'utils.py':'de23bef357e3524dde2cead837c0d08d112610ed652374e230c3d0621395178d',
    'fast_try.py':'8867b19b732f85d919fc2f5f67f5555661157f550faba1bd3049619fa6b767fe',
    'LICENSE':'f2f715abab48515faa39f2e42e07ed3518da2fdae36838e6e48ea4a20c2678b8'}
CONFIG={'arms':list(ARMS),'owners':list(OWNERS),'bits':128,'channels':[0,1,2,3],
    'bits_per_channel':32,'crop':[10,54,10,54],'layout_shape':[22,22],
    'block_size':2,'r_min':10,'r_max':18,'axis_offset':1,'fft_norm':'backward',
    'posterior':'mean','hermitian':'upstream-shifted-authoritative-right-half',
    'presence_matches':82,'descriptive_thresholds':[78,81,82],
    'payload_prefix':'M1-PhaseMark-pilot-v1|','precision':'float32','batch_size':1,
    'size':[512,512],'seed':0,'gpu_budget_bytes':10*1024**3,
    'ram_budget_bytes':16*1024**3,'artifact_budget_bytes':250*1024**2,'run_seconds_cap':900}

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024**2),b''):h.update(block)
    return h.hexdigest()

def write(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8');tmp.replace(path)

def payload(owner):
    data=hashlib.shake_256((CONFIG['payload_prefix']+owner).encode('utf-8')).digest(16)
    return [(byte>>shift)&1 for byte in data for shift in range(7,-1,-1)]

def fair_tail(k,n=128):
    return sum(math.comb(n,j) for j in range(k,n+1))/2**n

def integer_cutoff(alpha,n=128):
    return next(k for k in range(n+1) if fair_tail(k,n)<=alpha)

def overlap(a,b):
    return not (a[2]<=b[0] or b[2]<=a[0] or a[3]<=b[1] or b[3]<=a[1])

def bit_blocks():
    """Upstream greedy radius layout, with stable insertion-order tie breaks."""
    size=2
    def in_band(x,y):return all(10<=math.sqrt((x+i)**2+(y+j)**2)<=18 for i in range(size) for j in range(size))
    candidates=[]
    for x in range(1,22-size+1):
        for y in range(1,22-size+1):
            if in_band(x,y) and (x==y or y>x and in_band(y,x)):
                candidates.append((x,y,x+size,y+size,math.sqrt((x+1)**2+(y+1)**2),x==y))
    candidates.sort(key=lambda c:c[4])
    selected=[]
    for c in candidates:
        a=tuple(c[:4]);b=(c[1],c[0],c[3],c[2])
        if c[5]:
            if not any(overlap(a,p) for p in selected):selected.append(a)
        elif not overlap(a,b) and not any(overlap(a,p) or overlap(b,p) for p in selected):selected.extend((a,b))
        if len(selected)>=32:return selected[:32]
    return selected

def hermitian_shifted(freq):
    """Literal even-size upstream restoration, keeping its authoritative half."""
    import torch
    if freq.ndim!=4 or freq.shape[-2:]!=(44,44):raise ValueError('Expected shifted complex 44x44 FFT')
    if not torch.is_complex(freq):raise ValueError('Expected complex spectrum')
    out=freq.clone();original=freq.clone();h=w=44
    for x,y in ((h//2,w//2),(0,0),(h//2,0),(0,w//2)):out[:,:,x,y]=original[:,:,x,y].real
    out[:,:,0,1:w//2]=torch.conj(torch.flip(original[:,:,0,w//2+1:],dims=[2]))
    out[:,:,h//2,1:w//2]=torch.conj(torch.flip(original[:,:,h//2,w//2+1:],dims=[2]))
    out[:,:,1:h//2,0]=torch.conj(torch.flip(original[:,:,h//2+1:,0],dims=[2]))
    out[:,:,1:h//2,w//2]=torch.conj(torch.flip(original[:,:,h//2+1:,w//2],dims=[2]))
    out[:,:,1:h//2,1:w//2]=torch.conj(torch.flip(original[:,:,h//2+1:,w//2+1:],dims=[2,3]))
    out[:,:,h//2+1:,1:w//2]=torch.conj(torch.flip(original[:,:,1:h//2,w//2+1:],dims=[2,3]))
    return out

def modulate_fft(freq,bits,blocks,arm):
    """Magnitude-preserving upstream APM/IPS block operations; bits are 0/1."""
    import torch
    if arm not in ARMS or len(bits)!=len(blocks) or any(type(b) is not int or b not in (0,1) for b in bits):
        raise ValueError('Explicit arm and one binary bit per rectangle required')
    out=freq.clone()
    for bit,(x,y,xx,yy) in zip(bits,blocks):
        block=out[x:xx,y:yy]
        if arm=='APM':
            phase=torch.full_like(block.real,math.pi/2 if bit else -math.pi/2)
            out[x:xx,y:yy]=block.abs()*torch.exp(1j*phase)
        else:
            values=block.flatten().clone()
            if values.numel()!=4:raise ValueError('IPS requires exactly four row-major coefficients')
            delta=0 if bit else math.pi
            values[1]=values[1].abs()*torch.exp(1j*(torch.angle(values[0])+delta))
            values[3]=values[3].abs()*torch.exp(1j*(torch.angle(values[2])+delta))
            out[x:xx,y:yy]=values.reshape(2,2)
    return out

def read_fft(freq,blocks,arm):
    import torch
    if arm not in ARMS:raise ValueError('Unknown phase arm')
    scores=[];zeros=[]
    for x,y,xx,yy in blocks:
        values=freq[x:xx,y:yy].flatten();phase=torch.angle(values)
        if arm=='APM':score=phase.sum()
        else:
            diff1=torch.remainder(phase[0]-phase[1]+math.pi,2*math.pi)-math.pi
            diff2=torch.remainder(phase[2]-phase[3]+math.pi,2*math.pi)-math.pi
            score=torch.cos(diff1)+torch.cos(diff2)
        scores.append(float(score));zeros.append(int((values.abs()==0).sum()))
    return {'bits':[int(s>0) for s in scores],'scores':scores,'zero_magnitude_coefficients_per_block':zeros}

def extract_latent(scaled,arm):
    import torch
    if tuple(scaled.shape)!=(1,4,64,64) or not bool(torch.isfinite(scaled).all()):raise ValueError('Finite four-channel latent required')
    freq=torch.fft.fft2(scaled[0,:,10:54,10:54],norm='backward')
    results=[read_fft(freq[ch],bit_blocks(),arm) for ch in range(4)]
    return {key:[v for r in results for v in r[key]] for key in results[0]}

def embed_latent(scaled,bits,arm):
    import torch
    if tuple(scaled.shape)!=(1,4,64,64) or not bool(torch.isfinite(scaled).all()):raise ValueError('Finite four-channel latent required')
    if len(bits)!=128:raise ValueError('128 payload bits required')
    crop=scaled[:,:,10:54,10:54]
    spectrum=torch.fft.fft2(crop,norm='backward')
    marked=spectrum.clone()
    for channel in range(4):marked[0,channel]=modulate_fft(spectrum[0,channel],bits[channel*32:(channel+1)*32],bit_blocks(),arm)
    restored=torch.fft.ifftshift(hermitian_shifted(torch.fft.fftshift(marked,dim=(-2,-1))),dim=(-2,-1))
    inverse=torch.fft.ifft2(restored,norm='backward')
    output=scaled.clone();output[:,:,10:54,10:54]=inverse.real
    receipt={'inverse_imag_max_abs':float(inverse.imag.abs().max()),
        'spectral_displacement_energy':float((restored-spectrum).abs().square().sum()),
        'crop_displacement_energy':float((inverse.real-crop).square().sum()),
        'fft_parseval_divisor':44*44,'direct_latent_readout':extract_latent(output,arm)}
    return output,receipt

def planned():
    return [{'id':f'{ident}-{arm}-{control}-{dose}','source_id':ident,'arm':arm,'control':control,'dose':dose}
            for ident in IDS for arm in ARMS for control in ('C0','C1') for dose in ('clean','vae_cycle')]

def validate(manifest):
    if manifest.get('schema')!=VERSION or manifest.get('data_split')!='development' or manifest.get('config')!=CONFIG:
        raise ValueError('Fixed development PhaseMark manifest required')
    if manifest.get('upstream_revision')!=REVISION or manifest.get('upstream_hashes')!=UPSTREAM_HASHES:
        raise ValueError('Pinned official source identity required')
    if manifest.get('rectangles')!=[list(b) for b in bit_blocks()] or len(bit_blocks())!=32:
        raise ValueError('Exact upstream 32-rectangle layout required')
    if manifest.get('payloads')!={o:payload(o) for o in OWNERS}:raise ValueError('Frozen public owner payloads required')
    cases=manifest.get('cases',[])
    if [c['id'] for c in cases]!=list(IDS):raise ValueError('Fixed two-image denominator required')
    reserved=json.loads((ROOT/'research/m1-reconstruction-dev.json').read_text())['cases']
    for case in cases:
        ref=next(c for c in reserved if c['id']==case['id'])
        if Path(case['path']).resolve()!=Path(ref['path']).resolve() or case['sha256']!=ref['sha256']:
            raise ValueError('Reserved source path/hash differs')
    return cases

def require_committed(paths):
    receipt={}
    for p in paths:
        p=Path(p).resolve();rel=p.relative_to(ROOT).as_posix()
        oid=subprocess.check_output(['git','rev-parse','HEAD:'+rel],cwd=ROOT,text=True).strip()
        if subprocess.check_output(['git','hash-object','--path='+rel,str(p)],cwd=ROOT,text=True).strip()!=oid:
            raise ValueError('Uncommitted scientific input: '+rel)
        receipt[rel]={'git_blob_oid':oid,'working_sha256':sha(p)}
    return receipt

def working_set_bytes():
    """Windows current-process RAM, avoiding another runtime dependency."""
    if sys.platform!='win32':raise RuntimeError('This pilot RAM monitor is Windows-only')
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in
            ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
             'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
    kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p
    fn=ctypes.windll.psapi.GetProcessMemoryInfo;fn.argtypes=[ctypes.c_void_p,ctypes.POINTER(Counters),wintypes.DWORD]
    value=Counters();value.cb=ctypes.sizeof(value)
    if not fn(kernel.GetCurrentProcess(),ctypes.byref(value),value.cb):raise RuntimeError('Cannot measure pilot RAM')
    return int(value.WorkingSetSize)

def run(manifest_path,output):
    output,manifest_path=Path(output).resolve(),Path(manifest_path).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN dev-runs output required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    rows={r['id']:dict(r,outcome='planned',human_visual_verdict=None) for r in planned()}
    record={'schema':VERSION,'data_split':'development','config':CONFIG,'command':sys.argv,'seeds':[0],
        'duration_seconds':0,'outcome':'started','conditions':list(rows.values()),'human_visual_verdict':None}
    write(output/'run.json',record)
    def retain(row):
        rows[row['id']]=row
        with (output/'rows.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row,allow_nan=False)+'\n')
        write(output/'conditions.json',list(rows.values()))
    def journal(value):
        with (output/'journal.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(elapsed_seconds=time.monotonic()-started,**value),allow_nan=False)+'\n')
    for row in list(rows.values()):retain(row)
    try:
        record['commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        record['manifest_path']=str(manifest_path)
        record['manifest_sha256']=sha(manifest_path)
        (output/'manifest.json').write_bytes(manifest_path.read_bytes())
        write(output/'run.json',record)
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'));cases=validate(manifest)
        for name,digest in UPSTREAM_HASHES.items():
            if sha(UPSTREAM/name)!=digest:raise ValueError('Official PhaseMark source changed: '+name)
        deps=[Path(__file__),manifest_path,ROOT/'research/m1-phasemark-feasibility.md',ROOT/'research/m1-reconstruction-dev.json',
            ROOT/'scripts/m1_latent_reconstruction.py',ROOT/'scripts/three_threat_models.py',ROOT/'scripts/three_threat_protocol.py',
            ROOT/'scripts/check_a6_lpips_assets.py',ROOT/'scripts/verify_science_assets.py',ROOT/'scripts/a6_clip_visual.py',
            ROOT/'research/a6-candidate-model-assets.json']+[UPSTREAM/n for n in UPSTREAM_HASHES]
        record.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            manifest_sha256=sha(manifest_path),committed_files=require_committed(deps),upstream_revision=REVISION,
            upstream_hashes=UPSTREAM_HASHES,payloads=manifest['payloads'],rectangles=manifest['rectangles'],
            reference_tails={str(k):fair_tail(k) for k in (77,78,81,82)},
            detector_side_information=['public owner payload','phase variant','mask/FFT/crop conventions','pinned VAE and preprocessing'],
            labels='terminal-latent phase carrier; no three-state or ownership claim')
        sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT))
        from three_threat_models import block_network,verify_assets,load_lpips,lpips_score,clip_feature
        block_network()
        import numpy as np
        import torch
        from PIL import Image,ImageOps,ImageCms
        import io
        from diffusers import AutoencoderKL
        from a6_clip_visual import load_visual_encoder
        from scripts.m1_latent_reconstruction import quality
        if not torch.cuda.is_available():raise RuntimeError('No CUDA; no CPU scientific substitution')
        torch.manual_seed(0);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False
        torch.cuda.set_per_process_memory_fraction(min(1.,CONFIG['gpu_budget_bytes']/torch.cuda.get_device_properties(0).total_memory))
        assets,package=verify_assets(ASSETS,ROOT/'research/a6-candidate-model-assets.json')
        record.update(asset_receipt=assets,environment={'python':sys.version,**{p:importlib.metadata.version(p) for p in ('torch','numpy','scipy','Pillow','diffusers','lpips')}},
            lpips_learned_sha256=sha(package/'weights/v0.1/alex.pth'))
        metric=load_lpips(ASSETS,package);clip,transform=load_visual_encoder(ASSETS/'clip/ViT-B-32.pt',device='cpu')
        vae=AutoencoderKL.from_pretrained(ASSETS/'sd15-fp16/vae',variant='fp16',use_safetensors=True,
            local_files_only=True,torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        scale=float(vae.config.scaling_factor);record['vae_scaling_factor']=scale
        write(output/'run.json',record)
        def limits():
            ram=working_set_bytes();record['peak_observed_ram_bytes']=max(record.get('peak_observed_ram_bytes',0),ram)
            if ram>CONFIG['ram_budget_bytes']:raise RuntimeError('RAM budget exceeded')
            if torch.cuda.memory_allocated()>CONFIG['gpu_budget_bytes']:raise RuntimeError('GPU budget exceeded')
            if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>CONFIG['artifact_budget_bytes']:raise RuntimeError('Artifact budget exceeded')
            if time.monotonic()-started>CONFIG['run_seconds_cap']:raise RuntimeError('Pilot wall-time cap reached')
        def tensor(rgb):return torch.from_numpy(rgb.copy()).permute(2,0,1)[None].float().to('cuda')/255
        def encode(rgb):
            with torch.inference_mode():value=vae.encode(tensor(rgb)*2-1).latent_dist.mean*scale
            if tuple(value.shape)!=(1,4,64,64) or value.dtype!=torch.float32 or not bool(torch.isfinite(value).all()):
                raise RuntimeError('Nonfinite or malformed posterior-mean latent')
            return value
        def decode(z):
            with torch.inference_mode():value=(vae.decode(z/scale,return_dict=False)[0]+1)/2
            if tuple(value.shape)!=(1,3,512,512) or not bool(torch.isfinite(value).all()):
                raise RuntimeError('Nonfinite or malformed pure decoder output')
            return value[0].permute(1,2,0).clamp(0,1).cpu().numpy()
        def save(name,array):
            p=output/(name+'.png');Image.fromarray(array).save(p)
            with Image.open(p) as image:rgb=np.asarray(image.convert('RGB')).copy()
            return rgb,{'path':str(p),'sha256':sha(p),'rgb8_sha256':hashlib.sha256(rgb.tobytes()).hexdigest()}
        def decoded(name,z):return save(name,np.rint(decode(z)*255).astype(np.uint8))
        def q(left,right):
            result=quality(left,right);result['lpips']=lpips_score(metric,left,right)
            result['clip_cosine']=float((clip_feature(clip,transform,left)*clip_feature(clip,transform,right)).sum())
            result['quality_admissible']=(result['psnr_infinite'] or result['psnr_db']>35) and result['ssim_rgb']>.9 and result['lpips']<.1
            result['clip085_exploratory']=result['clip_cosine']>=.85
            return result
        for case in cases:
            limits();ident=case['id'];torch.cuda.reset_peak_memory_stats()
            try:
                if sha(case['path'])!=case['sha256']:raise ValueError('Raw source hash differs')
                with Image.open(case['path']) as image:
                    if image.mode!='RGB':raise ValueError('RGB source required')
                    image.load();icc=image.info.get('icc_profile');image=ImageOps.exif_transpose(image)
                    if icc:image=ImageCms.profileToProfile(image,ImageCms.ImageCmsProfile(io.BytesIO(icc)),ImageCms.createProfile('sRGB'),renderingIntent=0,outputMode='RGB',flags=0)
                    source=np.asarray(image.resize((512,512),Image.Resampling.BICUBIC)).copy()
                source,source_receipt=save(f'{ident}-source',source)
                source_receipt.update(raw_path=case['path'],raw_sha256=case['sha256'])
                z=encode(source);c0,c0_receipt=decoded(f'{ident}-C0',z)
                c0_cycle,c0_cycle_receipt=decoded(f'{ident}-C0-cycle',encode(c0))
                torch.save({'scaled_z':z.cpu(),'units':'VAE posterior mean multiplied by scaling_factor','scaling_factor':scale},output/f'{ident}-C0-latent.pt')
                for arm in ARMS:
                    limits()
                    try:
                        with torch.inference_mode():marked,embedding=embed_latent(z,payload(OWNERS[0]),arm)
                        if embedding['inverse_imag_max_abs']>1e-5:raise RuntimeError('Hermitian inverse has significant imaginary residual')
                        c1,c1_receipt=decoded(f'{ident}-{arm}-C1',marked)
                        c1_cycle,c1_cycle_receipt=decoded(f'{ident}-{arm}-C1-cycle',encode(c1))
                        torch.save({'scaled_z':marked.cpu(),'units':'VAE posterior mean multiplied by scaling_factor','scaling_factor':scale},output/f'{ident}-{arm}-C1-latent.pt')
                        journal({'phase':'embedded','source_id':ident,'arm':arm,'embedding':embedding})
                        for control,dose,rgb,receipt in (('C0','clean',c0,c0_receipt),('C0','vae_cycle',c0_cycle,c0_cycle_receipt),('C1','clean',c1,c1_receipt),('C1','vae_cycle',c1_cycle,c1_cycle_receipt)):
                            row=rows[f'{ident}-{arm}-{control}-{dose}'];row.update(outcome='started',image=receipt,source=source_receipt)
                            retain(row);limits()
                            try:
                                torch.cuda.synchronize();tick=time.monotonic();extracted=extract_latent(encode(rgb),arm);torch.cuda.synchronize()
                                decisions={o:{'matches':sum(a==b for a,b in zip(extracted['bits'],payload(o)))} for o in OWNERS}
                                for decision in decisions.values():
                                    decision.update(bit_accuracy=decision['matches']/128,pilot_state='pilot-present' if decision['matches']>=82 else 'pilot-absent',
                                        descriptive_threshold_decisions={str(k):decision['matches']>=k for k in (78,81,82)})
                                same=c0 if control=='C0' else c1
                                row.update(extracted=extracted,owner_decisions=decisions,extract_seconds=time.monotonic()-tick,
                                    quality_vs_source=q(source,rgb),quality_vs_same_arm_clean=q(same,rgb),
                                    paired_C1_vs_C0_quality=q(c0,rgb) if control=='C1' and dose=='clean' else None,
                                    embedding=embedding if control=='C1' else None,outcome='completed')
                                retain(row)
                            except Exception as error:row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc());retain(row)
                        del marked
                    except Exception as error:
                        for row in list(rows.values()):
                            if row['source_id']==ident and row['arm']==arm and row['outcome']!='completed':
                                row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc());retain(row)
                record['peak_allocated_bytes']=max(record.get('peak_allocated_bytes',0),torch.cuda.max_memory_allocated())
                del z;torch.cuda.empty_cache()
            except Exception as error:
                for row in list(rows.values()):
                    if row['source_id']==ident and row['outcome']!='completed':row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc());retain(row)
            limits()
        record['outcome']='completed' if all(r['outcome']=='completed' for r in rows.values()) else 'incomplete'
        record['arm_screen']={}
        for arm in ARMS:
            group=[r for r in rows.values() if r['arm']==arm]
            complete=all(r['outcome']=='completed' for r in group)
            carrier=all(r['owner_decisions'][OWNERS[0]]['matches']>=82 and all(r['owner_decisions'][o]['matches']<82 for o in OWNERS[1:])
                if r['control']=='C1' else all(r['owner_decisions'][o]['matches']<82 for o in OWNERS) for r in group) if complete else None
            quality_gate=all(r['quality_vs_source']['quality_admissible'] for r in group if r['control']=='C1' and r['dose']=='clean') if complete else None
            record['arm_screen'][arm]={'n_sources_planned':2,'n_conditions_planned':8,'complete':complete,
                'carrier_gate':carrier,'source_quality_gate':quality_gate,'human_visual_verdict':None}
    except (Exception,KeyboardInterrupt) as error:
        record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error),traceback=traceback.format_exc())
        journal({'phase':'run_failed','error':repr(error)})
    finally:
        for row in list(rows.values()):
            if row['outcome'] in ('planned','started'):row.update(outcome='not_completed_after_stop');retain(row)
        record.update(conditions=list(rows.values()),duration_seconds=time.monotonic()-started,
            output_hashes={p.name:sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'})
        write(output/'run.json',record)
    return 0 if record['outcome']=='completed' else 1

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args();return run(args.manifest,args.output_dir)

if __name__=='__main__':raise SystemExit(main())
