"""Fixed six-source chip-versus-symbol scientific probe; no minimax writer.
PGD is a frozen clone of f5_latent_codec.py at 546ac1f; only the objective
expression changes, with explicit finite checks. No global monkeypatch.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
IDS = (30, 72, 73, 89, 127, 165)
ALPHA, BETA = 'qim-pilot-owner-alpha', 'qim-pilot-owner-beta'
GPU_CAP, RAM_CAP = 9*1024**3, 10*1024**3

def margin_loss(torch, m, target_margin=4., objective='chip'):
    if m.numel() != 320:
        raise ValueError('Exactly 320 margins required')
    if objective == 'chip':
        return torch.relu(target_margin-m).pow(2).mean()
    if objective != 'symbol':
        raise ValueError('Unknown objective')
    return sum(((320*(i+1))//59-(320*i)//59) *
        torch.relu(target_margin-m[(320*i)//59:(320*(i+1))//59].mean()).pow(2)
        for i in range(59))/320

def energy(x, y):
    import numpy as np
    d = y.astype(np.int64)-x.astype(np.int64)
    return int(np.square(d).sum())

def match_energy(x, c, s):
    import numpy as np
    ec, es = energy(x,c), energy(x,s)
    target = min(ec,es)
    arm = 'C' if ec>es else 'S'
    y = c if arm=='C' else s
    def scaled(t):
        return np.clip(np.rint(x.astype(np.float64)+t*(y.astype(np.float64)-x)),0,255).astype(np.uint8)
    lo, hi = 0., 1.
    candidates = [(abs(energy(x,scaled(t))-target),t,scaled(t)) for t in (0.,1.)]
    for _ in range(32):
        t = (lo+hi)/2; z=scaled(t); e=energy(x,z)
        candidates.append((abs(e-target),t,z))
        if e<target: lo=t
        else: hi=t
    _, t, z = min(candidates,key=lambda item:(item[0],item[1]))
    if ec==es: t=1.; z=y
    result={'C':c,'S':s}; result[arm]=z
    final={a:energy(x,rgb) for a,rgb in result.items()}
    residual=abs(final['C']-final['S'])
    return result, dict(initial_energy={'C':ec,'S':es}, target_energy=target,
        scaled_arm=arm, scale=t, final_energy=final, discrete_residual=residual,
        relative_discrepancy=residual/target if target else None,
        controlled=bool(target and residual/target<=.01), bisections=32)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8'); tmp.replace(path)

def robust_pgd(reader: Reader, rgb01: np.ndarray, layout: Layout, ws: Sequence[float], psnr_db: float,
               steps: int, target_margin: float, mask_power: float = 0.0, objective: str = "chip"):
    """Pixel change at a PSNR budget that drives every chip margin ws_i * p_i towards ``target_margin``.

    Squared hinge on the margins, normalised-gradient ascent with an L2 ball
    (in the mask-weighted metric) and the [0,1] box.  Returns the float image.
    """
    import numpy as np
    import math
    from scripts.f5_latent_codec import _activity_mask, v5
    torch = reader.torch
    dev = reader.device
    x = reader.tensor(rgb01)
    mask = torch.from_numpy(_activity_mask(rgb01, mask_power).astype(np.float32))[None, None].to(dev)
    budget = 10 ** (-psnr_db / 20) * math.sqrt(rgb01.size)
    D = torch.from_numpy(layout.dct.astype(np.float32)).to(dev)
    ch, u, v = (torch.from_numpy(a).to(dev) for a in (layout.ch, layout.u, layout.v))
    coeff = torch.from_numpy((layout.weights * layout.signs).astype(np.float32)).to(dev)
    chip = torch.from_numpy(layout.chip).to(dev)
    norms = torch.from_numpy(layout.norms.astype(np.float32)).to(dev)
    w = torch.from_numpy(np.asarray(ws, np.float32)).to(dev)
    eta = torch.zeros_like(x, requires_grad=True)  # delta = mask * eta; budget applies to delta

    def margins(delta):
        z = reader.encode((x + delta).clamp(0, 1))
        c = torch.einsum("ij,cjk,lk->cil", D, z, D)
        totals = torch.zeros(v5.CHANNEL_CHIPS, device=dev).index_add(0, chip, c[ch, u, v] * coeff)
        return w * totals / norms

    for step in range(steps):
        lr = budget * (0.2 if step < steps // 2 else 0.05)
        m = margins(mask * eta)
        loss = margin_loss(torch, m, target_margin, objective)
        if not bool(torch.isfinite(loss)):
            raise ValueError("Nonfinite initializer objective")
        g, = torch.autograd.grad(loss, eta)
        if not bool(torch.isfinite(g).all()):
            raise ValueError("Nonfinite initializer gradient")
        with torch.no_grad():
            eta -= lr * g / (g.norm() + 1e-12)
            delta = (x + mask * eta).clamp(0, 1) - x
            n = delta.norm()
            if n > budget:
                delta *= budget / n
            eta.copy_(delta / mask)
    with torch.no_grad():
        out = (x + mask * eta).clamp(0, 1)[0].permute(1, 2, 0).double().cpu().numpy()
    return out


def main():
    started=time.monotonic()
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage-a-run',type=Path,required=True)
    ap.add_argument('--sources',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--max-seconds',type=float,default=2700)
    args=ap.parse_args()
    if not 0<args.max_seconds<=2700: raise ValueError('Maximum inclusive cap is 2700 seconds')
    stage_path=args.stage_a_run/'run.json' if args.stage_a_run.is_dir() else args.stage_a_run
    stage=read(stage_path); cohort=read(args.sources)
    if stage.get('outcome') in (None,'running'): raise ValueError('Parent science must exit first')
    if stage.get('data_split')!='development': raise ValueError('Development parent required')
    if tuple(sorted(s['source_id'] for s in cohort['sources'])[:6])!=IDS: raise ValueError('Frozen first six IDs required')
    source_map={s['source_id']:s for s in stage['sources']}
    out=args.output_dir.resolve()
    if out.exists():
        record=read(out/'run.json')
        if record['config']['max_seconds']!=args.max_seconds: raise ValueError('Resume cannot change the inclusive cap')
        if record['config']['stage_a_run']!=str(stage_path.resolve()): raise ValueError('Different parent')
        if record['outcome'] in ('completed','scientific_stop'): raise ValueError('Finished screen cannot be retried')
        record['outcome']='running'
    else:
        out.mkdir(parents=True); (out/'images').mkdir()
        rows=[dict(id=f'{sid}:{phase}:{arm}',source_id=sid,phase=phase,arm=arm,status='not_started',calls={},endpoints={})
            for sid in IDS for phase in ('clean','sd15_vae','sdxl_vae') for arm in ('C0','C','S')]
        for idx,sid in enumerate(IDS):
            for strength in (.2,.4):
                for seed in (9,10,11):
                    for arm in ('C0', 'C', 'S') if idx%2==0 else ('C0','S','C'):
                        rows.append(dict(id=f'{sid}:T3:{strength}:{seed}:{arm}',source_id=sid,phase='T3',arm=arm,
                            strength=strength,seed=seed,status='not_started',calls={},endpoints={}))
        record=dict(schema='fresh-symbol-objective-v1',outcome='running',data_split='development',usd=0,
            commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=sys.argv,
            elapsed_seconds=0.,sources={str(sid):dict(status='not_started') for sid in IDS},rows=rows,
            config=dict(stage_a_run=str(stage_path.resolve()),sources=list(IDS),seeds=[9,10,11],strengths=[.2,.4],
                max_seconds=args.max_seconds,construction_cap=1800,prerequisite_cap=650,steps=20,
                prompt='',negative_prompt='',guidance_scale=1.,eta=0.,dtype='float16',safety_checker=True,
                objective='length-weighted symbol mean squared hinge',margin=4.,schedule=[[46,150],[52,50]],
                selector=[1.,.8],gpu_cap_bytes=GPU_CAP,rss_cap_bytes=RAM_CAP,minimum_available_ram_bytes=3*1024**3))
    prior=record['elapsed_seconds']; rows=record['rows']; index={r['id']:r for r in rows}; ev=None; phase_cap=args.max_seconds
    def elapsed(): return prior+time.monotonic()-started
    def save():
        record['elapsed_seconds']=elapsed()
        from fresh_symbol_objective_analysis import summarize
        record['summary']=summarize(record)
        write(out/'run.json',record); write(out/'summary.json',record['summary'])
    def budget():
        from journal_e3_threat_supplement import working_set
        from post_m2_refinement_probe import available_ram
        if elapsed()>=min(args.max_seconds,phase_cap): raise RuntimeError('Inclusive phase budget reached')
        rss,_=working_set(); record['peak_rss_bytes']=max(record.get('peak_rss_bytes',0),rss)
        if rss>RAM_CAP or available_ram()<3*1024**3: raise RuntimeError('RAM cap breached')
        if ev is not None:
            allocated=ev.torch.cuda.max_memory_allocated(); record['peak_gpu_bytes']=int(allocated)
            if allocated>GPU_CAP: raise RuntimeError('GPU cap breached')
    save()
    try:
        import numpy as np
        import torch
        import diffusers
        from PIL import Image
        from diffusers import AutoencoderKL
        from journal_vae_probe import Evaluator, SDXL
        from f4_transfer_probe import ASSETS
        import three_threat_models as models
        from journal_e3_writer import strict_quality, contract, _BoundedReader
        from journal_bch_probe import patterns,restore_fragile,coded_diagnostics
        from journal_bch_readout import detect_rgb
        from journal_bch_analysis import endpoint
        from journal_readability_probe import reconstruct
        torch.set_num_threads(4); budget()
        if diffusers.__version__!='0.35.1': raise ValueError('Pinned diffusers required')
        models.block_network(); free,total=torch.cuda.mem_get_info()
        if free<GPU_CAP: raise RuntimeError('Insufficient GPU headroom')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/total)
        phase_cap=record.get('attack_deadline_seconds', 650 if record['sources'][str(IDS[1])]['status']!='ok' else 1800)
        ev=Evaluator(); budget()
        if ev.profile!=stage['config']['profile']: raise ValueError('Parent profile differs')
        record['config']['profile']=ev.profile
        record['environment']=dict(torch=torch.__version__,diffusers=diffusers.__version__,assets=str(ASSETS),sdxl=str(SDXL))
        other=None
        if 'construction_completed_seconds' not in record:
            other=AutoencoderKL.from_pretrained(SDXL,local_files_only=True,use_safetensors=True,torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda'); budget()
        def load(path):
            with Image.open(path) as im:
                if im.mode!='RGB' or im.size!=(512,512): raise ValueError('Canonical RGB8 required')
                return np.asarray(im,np.uint8).copy()
        def image_save(path,rgb):
            Image.fromarray(rgb).save(path); return load(path)
        def observe(row,rgb,canonical,input_rgb,payload):
            budget(); latent=ev.reader.latent(rgb); features=ev.features(rgb,7)
            for owner in (ALPHA,BETA):
                if owner in row['calls']: continue
                budget(); call=detect_rgb(rgb,latent,owner,ev.profile,features,binding='soft',binding_mode='combined',roster_size=1)
                row['calls'][owner]=call; row['endpoints'][owner]=endpoint(call,payload if row['arm']!='C0' and owner==ALPHA else None); save()
            layout,w,_=patterns(ev.profile,int(payload['q'],16)); p=layout.projections(latent); m=w*p
            means=np.array([m[(320*i)//59:(320*(i+1))//59].mean() for i in range(59)])
            sums=[float(m[(320*i)//59:(320*(i+1))//59].sum()) for i in range(59)]
            numerator=sum(float(np.square(m[(320*i)//59:(320*(i+1))//59]-means[i]).sum()) for i in range(59))
            denominator=float(np.square(p).sum())
            row['projection_diagnostics']=dict(intended_raw_symbol_sums=sums,symbol_means=means.tolist(),
                within_symbol_H=numerator/denominator if denominator else None,matched_amplitude=float(m.mean()),minimum_symbol_mean=float(means.min()),
                raw_systematic_q_errors=(int(row['calls'][ALPHA]['semantic']['raw_coded_word'],16)>>27 ^ int(payload['q'],16)).bit_count()
                    if row['calls'][ALPHA]['semantic'].get('raw_coded_word') else None)
            row['coded_diagnostics']=coded_diagnostics(row['calls'][ALPHA],int(payload['q'],16))
            budget(); row['quality_source']=ev.metrics(canonical,rgb); budget(); row['quality_input']=ev.metrics(input_rgb,rgb)
            row['strict_quality']=strict_quality(row['quality_source']); row['clean_eligible']=row['arm']!='C0' and row['strict_quality'] and all(row['endpoints'][ALPHA][m] for m in ('Q','H','F'))
            row['status']='ok'; budget(); save()
        for source_index,sid in enumerate(IDS):
            checkpoint=record['sources'][str(sid)]; shared=source_map.get(sid,{})
            if checkpoint['status']=='ok': continue
            if checkpoint['status']!='not_started': raise RuntimeError('Interrupted source retained; no retry')
            if shared.get('supplier',{}).get('status')!='ok' or not shared.get('initializer'):
                raise RuntimeError('Shared supplier/initializer unavailable; fixed denominator retained')
            budget(); checkpoint.update(status='running',shared_record=str(stage_path),shared_source=shared); save()
            canonical=load(shared['canonical_path']); payload=shared['payload']; q,h=int(payload['q'],16),int(payload['h'],16)
            layout,w,_=patterns(ev.profile,q); ev.reader.vae.enable_gradient_checkpointing()
            reader=_BoundedReader(ev.reader,budget)
            tick=time.monotonic()
            first=robust_pgd(reader,canonical.astype(np.float64)/255,layout,w,46.,150,4.,0.,'symbol')
            first,r1=restore_fragile(np.clip(np.rint(first*255),0,255).astype(np.uint8),q,h,ev.profile)
            first=image_save(out/'images'/f'{sid}-S-first.png',first)
            second=robust_pgd(reader,first.astype(np.float64)/255,layout,w,52.,50,4.,0.,'symbol')
            second,r2=restore_fragile(np.clip(np.rint(second*255),0,255).astype(np.uint8),q,h,ev.profile)
            second=image_save(out/'images'/f'{sid}-S-initializer.png',second)
            checkpoint.update(construction_seconds=time.monotonic()-tick,restorations=[r1,r2],selector={})
            chosen={}
            for arm,rgb in (('C',load(shared['initializer'])),('S',second)):
                budget(); metrics=ev.metrics(canonical,rgb); retain=strict_quality(metrics)
                chosen[arm]=rgb if retain else contract(rgb,canonical)
                path=out/'images'/f'{sid}-{arm}-selected.png'; chosen[arm]=image_save(path,chosen[arm])
                checkpoint['selector'][arm]=dict(input_quality=metrics,branch='retain' if retain else 'contract_0.8',image=str(path))
            matched,control=match_energy(canonical,chosen['C'],chosen['S']); checkpoint['energy_control']=control
            checkpoint['images']={'C0':shared['canonical_path']}
            for arm,rgb in matched.items():
                path=out/'images'/f'{sid}-{arm}-matched.png'; image_save(path,rgb); checkpoint['images'][arm]=str(path)
            save()
            for condition in ('clean','sd15_vae','sdxl_vae'):
                for arm in ('C0','C','S'):
                    budget(); row=index[f'{sid}:{condition}:{arm}']; row['status']='running'; save()
                    inp=load(checkpoint['images'][arm]); rgb=reconstruct(ev,other,inp,condition)
                    path=out/'images'/f'{sid}-{condition}-{arm}.png'; rgb=image_save(path,rgb); row['image']=str(path)
                    observe(row,rgb,canonical,inp,payload)
            c,s=(index[f'{sid}:clean:{a}'] for a in ('C','S'))
            lp=abs(c['quality_source']['lpips']-s['quality_source']['lpips']); ss=abs(c['quality_source']['ssim_rgb']-s['quality_source']['ssim_rgb'])
            checkpoint['comparability']=dict(lpips_difference=lp,ssim_difference=ss,pass_tolerances=lp<=.01 and ss<=.005)
            negative_ok=all(not index[f'{sid}:{phase}:{arm}']['endpoints'][owner]['A']
                for phase in ('clean','sd15_vae','sdxl_vae') for arm,owner in (('C0',ALPHA),('C0',BETA),('C',BETA),('S',BETA)))
            checkpoint['pair_pass']=bool(control['controlled'] and c['clean_eligible'] and s['clean_eligible'] and lp<=.01 and ss<=.005 and negative_ok)
            checkpoint['status']='ok'; save()
            if not checkpoint['pair_pass']:
                record.update(outcome='scientific_stop',stop_reason='Fixed clean/admission/comparability/negative prerequisite failed'); save(); return
            if source_index==1: phase_cap=1800
        budget()
        if 'construction_completed_seconds' not in record:
            record['construction_completed_seconds']=elapsed()
            record['attack_deadline_seconds']=min(args.max_seconds,elapsed()+900)
        save(); del other; torch.cuda.empty_cache()
        phase_cap=record['attack_deadline_seconds']
        pipe=models.load_regenerator(ASSETS); budget()
        if pipe.safety_checker is None or pipe.feature_extractor is None: raise RuntimeError('Safety components required')
        for row in rows:
            if row['phase']!='T3' or row['status'] in ('ok','safety_blocked'): continue
            if row['status']!='not_started': raise RuntimeError('Interrupted identity retained; no retry')
            budget(); row['status']='running'; row['transformation_attempted']=True; save()
            sid=row['source_id']; checkpoint=record['sources'][str(sid)]; shared=source_map[sid]
            inp=load(checkpoint['images'][row['arm']]); canonical=load(shared['canonical_path'])
            with torch.inference_mode():
                output=pipe(prompt='',negative_prompt='',image=Image.fromarray(inp),strength=row['strength'],num_inference_steps=20,
                    eta=0.,guidance_scale=1.,generator=torch.Generator(device='cuda').manual_seed(row['seed']),num_images_per_prompt=1,output_type='pil',return_dict=True)
            row['safety_flags']=list(output.nsfw_content_detected) if output.nsfw_content_detected is not None else None
            times,_=pipe.get_timesteps(20,row['strength'],pipe._execution_device); row['timesteps']=times.cpu().tolist()
            path=out/'images'/(row['id'].replace(':','-')+'.png'); output.images[0].save(path); row['raw_output_image']=str(path); save()
            if len(row['timesteps'])!=int(20*row['strength']): raise ValueError('Effective steps differ')
            try: rgb=np.asarray(models.validate_generated(output),np.uint8).copy()
            except RuntimeError as exc:
                if str(exc)=='safety_checker_blocked_output' and row['safety_flags']==[True]:
                    row['status']='safety_blocked'; save(); continue
                raise
            row['image']=str(path); observe(row,rgb,canonical,inp,shared['payload'])
            if row['arm']!='C0':
                control=index[f"{sid}:T3:{row['strength']}:{row['seed']}:C0"]
                if control['status']=='ok':
                    budget(); row['quality_attacked_C0']=ev.metrics(load(control['image']),rgb)
            save()
        budget(); record['outcome']='completed'
    except BaseException as exc:
        record.update(outcome='incomplete',error=f'{type(exc).__name__}: {exc}',traceback=traceback.format_exc())
    finally: save()
    if record['outcome']!='completed': raise SystemExit(1)

if __name__=='__main__': main()
