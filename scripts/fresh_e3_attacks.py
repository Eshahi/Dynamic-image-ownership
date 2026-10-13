"""Conditional bounded Stage B scientific probe on saved fresh E/L pixels."""
from __future__ import annotations
import time
STARTED=time.monotonic()
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from fresh_e3_attacks_analysis import summarize,ALPHA,BETA
GPU_CAP,RAM_CAP=9*1024**3,10*1024**3

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p); tmp=p.with_suffix(p.suffix+'.tmp'); tmp.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8'); tmp.replace(p)

def plan(parent,pairs):
    rows=[]
    for phase in ('sd15_vae','sdxl_vae','T3'):
        for i,s in enumerate(parent['sources']):
            order=('E','L') if i%2==0 else ('L','E')
            cells=[(None,None)] if phase!='T3' else [(v,n) for v in (.1,.2,.4) for n in (6,7,8)]
            for strength,seed in cells:
                for arm in ('C0',)+order:
                    rows.append(dict(id=f"{s['source_id']}:{phase}:{strength}:{seed}:{arm}",source_id=s['source_id'],phase=phase,arm=arm,strength=strength,seed=seed,status='not_started',calls={},endpoints={}))
    for phase,pp in (('T4',pairs['t4_pairs']),('T5',[dict(donor_id=int(p['left'].split(':')[-1]),recipient_id=int(p['right'].split(':')[-1])) for p in pairs['t5_schedule']['pairs']])):
        for i,p in enumerate(pp):
            operators=('residual_0.5','residual_1.0','public','sham') if phase=='T4' else ('public','sham')
            for op in operators:
                for arm in (('E','L') if i%2==0 else ('L','E')):
                    rows.append(dict(id=f"{phase}:{p['donor_id']}:{p['recipient_id']}:{op}:{arm}",phase=phase,arm=arm,operator=op,donor_id=p['donor_id'],recipient_id=p['recipient_id'],status='not_started',calls={},endpoints={}))
    return rows

def retain_attempt(row):
    """Keep prior incomplete evidence and give each retry a fresh image path."""
    if row['status'] != 'not_started':
        history=row.setdefault('attempt_history',[])
        history.append(copy.deepcopy({k:v for k,v in row.items() if k!='attempt_history'}))
    row.update(status='running',calls={},endpoints={},transformation_attempted=False)

def alias_observation(row, original):
    keep={k:row[k] for k in ('id','arm','phase','source_id','strength','seed')}
    history=copy.deepcopy(row.get('attempt_history',[]))
    row.update(copy.deepcopy({k:v for k,v in original.items() if k!='attempt_history'}))
    row.update(keep,alias_of=original['id'],transformation_attempted=False,
        attempt_history=history,reuse_scope='byte-identical E/L pixels, same observation')

def scientific_stop(record, rows, parent):
    s=summarize(record,rows,parent)
    reason=('Observed VAE L-only J loss' if s['vae_loss'] else
        'Observed C0 or new L-only beta A event' if s['negative_regression'] else
        'Observed L-only combined F or sham A transfer event' if s['transfer_regression'] else
        'Most favorable primary L-minus-E bound below -1' if any(s['strengths'][str(v)]['L_minus_E_J_interval'][1]<-1 for v in (.1,.2)) else None)
    if reason:
        record.update(outcome='scientific_stop',scientific_stop_reason=reason)
    return reason is not None

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--parent',type=Path,required=True); p.add_argument('--pairs',type=Path,default=ROOT/'research/journal-upgrade-20261009/fresh-development-transfer-pairs.json'); p.add_argument('--output-dir',type=Path,required=True); p.add_argument('--max-seconds',type=float,default=2700); a=p.parse_args()
    if not 0<a.max_seconds<=2700: raise ValueError('Inclusive cap must be at most 2700 seconds')
    parent_path=a.parent/'run.json' if a.parent.is_dir() else a.parent
    parent=read(parent_path); pairs=read(a.pairs)
    if parent.get('outcome')!='completed' or parent.get('data_split')!='development' or parent.get('stage_A',{}).get('pass_screen') is not True: raise ValueError('Finished passing Stage A required; no inference launched')
    ids=[s['source_id'] for s in parent['sources']]
    if len(ids)!=24 or len(set(ids))!=24 or len(pairs['t4_pairs'])!=6: raise ValueError('Frozen 24-source/six T4 panel required')
    if [(q['donor_id'],q['recipient_id']) for q in pairs['t4_pairs']]!=list(zip(ids[:12:2],ids[1:12:2])): raise ValueError('T4 source order differs')
    planned=plan(parent,pairs); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if (out/'run.json').exists():
        record=read(out/'run.json'); rows=read(out/'rows.json')
        if record['outcome'] in ('completed','scientific_stop'): raise ValueError('Terminal scientific runs cannot resume')
        if record['commit']!=commit or record['parent']!=str(parent_path.resolve()) or record['pairs']!=pairs or [r['id'] for r in rows]!=[r['id'] for r in planned] or record['config']['max_seconds']!=a.max_seconds: raise ValueError('Resume identity/config differs')
    else:
        rows=planned; record=dict(schema='fresh-e3-attacks-v1',commit=commit,parent=str(parent_path.resolve()),pairs=pairs,t5_shortfall=pairs['t5_schedule']['shortfall'],command=sys.argv,data_split='development',usd=0,outcome='running',elapsed_seconds=0,config=dict(max_seconds=a.max_seconds,strengths=[.1,.2,.4],seeds=[6,7,8],steps=20,effective_steps=[2,4,8],batch=1,cpu_threads=4,binding='soft',semantic_views=7,roster_size=1,gpu_cap_bytes=GPU_CAP,ram_cap_bytes=RAM_CAP,free_ram_min_bytes=3*1024**3),planned_counts=dict(VAE=144,T3=648,T4=48,T5=len(pairs['t5_schedule']['pairs'])*4),clean_observation_reuse='Stage A saved clean calls/admission, no new clean tuning')
    record['config'].update(prompt='',negative_prompt='',eta=0.,guidance_scale=1.,dtype='float16',safety_checker=True,
        scheduler='DDIM',asset_loading='Frozen three_threat_models.load_regenerator, local files only')
    prior=record['elapsed_seconds']; ev=None; active=None
    def save():
        record['elapsed_seconds']=prior+time.monotonic()-STARTED
        record['budget_overrun']=record['elapsed_seconds']>a.max_seconds
        if record['budget_overrun'] and record['outcome']!='scientific_stop': record['outcome']='incomplete'
        record['summary']=summarize(record,rows,parent); write(out/'rows.json',rows); write(out/'run.json',record)
    def budget():
        from fresh_e3_simplification import memory
        rss,peak,free=memory(); record['peak_ram_bytes']=max(peak,record.get('peak_ram_bytes',0))
        gpu=int(ev.torch.cuda.max_memory_allocated()) if ev else 0
        record['peak_gpu_bytes']=max(gpu,record.get('peak_gpu_bytes',0))
        if prior+time.monotonic()-STARTED>=a.max_seconds or rss>RAM_CAP or peak>RAM_CAP or free<3*1024**3 or gpu>GPU_CAP: raise RuntimeError('Cooperative inclusive resource cap reached')
    save()
    try:
        budget()
        import numpy as np
        import torch
        import diffusers
        from PIL import Image
        from diffusers import AutoencoderKL
        from journal_vae_probe import Evaluator,SDXL
        from f4_transfer_probe import ASSETS
        import three_threat_models as models
        from journal_readability_probe import reconstruct
        from journal_bch_readout import detect_rgb
        from journal_bch_analysis import endpoint
        from journal_e3_public_projection import semantic_inverse,fragile_replace,endpoints,vector_error
        from three_threat_protocol import residual_transfer
        from scripts import f5_latent_codec as f5,revised_watermark_v5 as v5
        torch.set_num_threads(4)
        record['environment']=dict(torch=torch.__version__,diffusers=diffusers.__version__,gpu=torch.cuda.get_device_name(0),cpu_threads=torch.get_num_threads(),sd15_assets=str(ASSETS),sdxl_vae_assets=str(SDXL),pinned_model_basis='Frozen local loaders and Stage A profile/assets; no downloads')
        if diffusers.__version__!='0.35.1': raise ValueError('Pinned diffusers required')
        models.block_network(); free,total=torch.cuda.mem_get_info()
        if free<GPU_CAP: raise RuntimeError('Insufficient free GPU headroom')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/total)
        ev=Evaluator(); budget()
        if ev.profile!=parent['config']['profile']: raise ValueError('Frozen profile differs')
        pipe=models.load_regenerator(ASSETS); budget()
        if pipe.safety_checker is None or pipe.feature_extractor is None: raise ValueError('Required safety checker absent')
        other=AutoencoderKL.from_pretrained(SDXL,local_files_only=True,use_safetensors=True,torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda'); budget()
        checked,key,config=v5._resolve(ev.profile,None); owner=v5.canonical_owner(ALPHA)
        layout=f5.Layout(checked,key,config,owner); fragile=v5._Fragile(checked,key,config,owner,512,512)
        sources={s['source_id']:s for s in parent['sources']}; index={r['id']:r for r in rows}
        def load(path):
            with Image.open(path) as im:
                if im.mode!='RGB' or im.size!=(512,512): raise ValueError('Saved RGB8 512 square required')
                return np.asarray(im,np.uint8).copy()
        def pixels(sid,arm): return load(sources[sid]['canonical_path' if arm=='C0' else 'full_image' if arm=='E' else 'lean_image'])
        def fvector(rgb): return fragile.projections(v5.base._analyse(v5.luminance_from_rgb(rgb.tolist()),fragile.analysis)[1])
        for r in rows:
            if r['status'] in ('ok','safety_blocked'): continue
            active=r; budget(); tick=time.monotonic(); retain_attempt(r); save()
            image_slot=f"{rows.index(r)}-attempt{len(r.get('attempt_history',[]))}"
            try:
                if r['phase'] in ('T4','T5'):
                    r['transformation_attempted']=True; save()
                    sid=r['donor_id']; recipient=pixels(r['recipient_id'],'C0'); inp=pixels(sid,'C0' if r['operator']=='sham' else r['arm'])
                    if r['operator'].startswith('residual'):
                        rgb=np.asarray(residual_transfer(recipient.tolist(),inp.tolist(),pixels(sid,'C0').tolist(),float(r['operator'].split('_')[-1])),np.uint8)
                    else:
                        # Attack accepts only public native vectors and recipient pixels.
                        pd=layout.projections(ev.reader.latent(inp)); fd=fvector(inp)
                        r['public_vector_targets']=dict(semantic=pd,fragile=fd)
                        intermediate,opt=semantic_inverse(ev.reader,recipient,layout,pd,budget)
                        rgb=np.asarray(fragile_replace(intermediate,fragile,fd,v5,budget),np.uint8); r['optimization']=opt
                        r['projection_errors']=dict(semantic=vector_error(layout.projections(ev.reader.latent(rgb)),pd),fragile=vector_error(fvector(rgb),fd))
                    r['valid_clean_donor']=sources[sid]['clean']['full' if r['arm']=='E' else 'lean']['clean_eligible']
                    target=None if r['operator']=='sham' else sources[sid]['payload']
                    modes=('none','semantic_only','perceptual_only','combined')
                else:
                    sid=r['source_id']; inp=pixels(sid,r['arm']); recipient=pixels(sid,'C0'); target=sources[sid]['payload'] if r['arm']!='C0' else None
                    modes=('combined',)
                    other_arm='L' if r['arm']=='E' else 'E'
                    alias=index.get(r['id'][:-1]+other_arm)
                    if r['arm']!='C0' and alias['status'] in ('ok','safety_blocked') and np.array_equal(inp,pixels(sid,other_arm)):
                        alias_observation(r,alias); save()
                        if scientific_stop(record,rows,parent): save(); return
                        continue
                    if r['phase']=='T3':
                        pipe.scheduler.set_timesteps(20,device=pipe._execution_device)
                        timesteps,_=pipe.get_timesteps(20,r['strength'],pipe._execution_device)
                        if len(timesteps)!=int(20*r['strength']): raise ValueError('Effective DDIM steps differ')
                        r['timesteps']=timesteps.cpu().tolist(); r['transformation_attempted']=True; save(); budget()
                        with torch.inference_mode(): result=pipe(prompt='',negative_prompt='',image=Image.fromarray(inp),strength=r['strength'],num_inference_steps=20,eta=0.,guidance_scale=1.,generator=torch.Generator(device='cuda').manual_seed(r['seed']),num_images_per_prompt=1,output_type='pil',return_dict=True)
                        r['safety_flags']=list(result.nsfw_content_detected) if result.nsfw_content_detected is not None else None
                        raw=out/(image_slot+'.png'); result.images[0].save(raw); r['raw_output_image']=str(raw)
                        rgb=np.asarray(models.validate_generated(result),np.uint8).copy()
                    else: r['transformation_attempted']=True; rgb=reconstruct(ev,other,inp,r['phase'])
                budget(); path=out/(image_slot+'.png'); Image.fromarray(rgb).save(path); rgb=load(path); r['image']=str(path)
                features,latent=ev.features(rgb,7),ev.reader.latent(rgb)
                for mode in modes:
                    calls={}; eps={}
                    for claimed in (ALPHA,BETA):
                        budget(); call=detect_rgb(rgb,latent,claimed,ev.profile,features,binding='soft',binding_mode=mode,roster_size=1)
                        calls[claimed]=call
                        eps[claimed]=endpoints(call,target if claimed==ALPHA else None) if r['phase'] in ('T4','T5') else endpoint(call,target if claimed==ALPHA else None)
                    if r['phase'] in ('T4','T5'): r['calls'][mode]=calls; r['endpoints'][mode]=eps
                    else: r['calls']=calls; r['endpoints']=eps
                    save()
                budget(); r['quality_recipient' if r['phase'] in ('T4','T5') else 'quality_source']=ev.metrics(recipient,rgb); budget(); r['quality_input']=ev.metrics(inp,rgb)
                if r['phase'] not in ('T4','T5') and r['arm']!='C0':
                    c0=index[r['id'][:-1]+'C0']
                    if c0['status']=='ok': budget(); r['quality_attacked_C0']=ev.metrics(load(c0['image']),rgb)
                r['status']='ok'
            except Exception as exc:
                if str(exc)=='safety_checker_blocked_output' and r.get('safety_flags')==[True] and not r['calls']: r.update(status='safety_blocked',error=str(exc))
                else: r.update(status='incomplete',error=traceback.format_exc()); raise
            finally:
                r['duration_seconds']=time.monotonic()-tick; save()
            print(json.dumps(dict(id=r['id'],status=r['status'])),flush=True); active=None
            if scientific_stop(record,rows,parent): save(); return
        budget(); record['outcome']='completed'
    except Exception:
        record.update(outcome='incomplete',error=traceback.format_exc())
        raise
    finally: save()

if __name__=='__main__': main()
