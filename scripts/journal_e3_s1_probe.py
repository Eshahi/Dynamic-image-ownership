"""Frozen two-source callable/supplier screen, followed by conditional official T3."""
from __future__ import annotations
import time
STARTED = time.monotonic()
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts')]
from journal_e3_threat_supplement import MAIN, ALPHA, OWNERS, read, write, working_set
from f4_transfer_probe import ASSETS
from journal_bch_analysis import endpoint, CONDITIONS

IDS = (6012, 147498)
CAP, GPU_CAP, RAM_CAP = 1800., 10*1024**3, 16*1024**3
COMPOSITION = MAIN/'.thesis-build/dev-runs/20261010-1417-e3-quality-composition'
T3 = MAIN/'.thesis-build/dev-runs/20261010-1418-e3-full-t3'


def rows_at(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def arm_pass(arm):
    if arm.get('writer', {}).get('admitted') is not True or set(arm.get('conditions', {})) != set(CONDITIONS):
        return False
    for name, cell in arm['conditions'].items():
        positive = cell['endpoints'][ALPHA]
        if not (positive['S'] and positive['J']) or cell['endpoints'][OWNERS[1]]['A'] or cell['c0_endpoint']['A']:
            return False
        if name == 'clean' and not (positive['Q'] and positive['H'] and positive['F']):
            return False
    return True


def summarize(rows, t3_rows, historical):
    screen = len(rows) == 2 and [r['source_id'] for r in rows] == list(IDS) and all(
        r.get('supplier', {}).get('status') == 'ok' and
        all(arm_pass(r.get('arms', {}).get(arm, {})) for arm in ('historical', 'S1')) for r in rows)
    counts = {str(s):{k:0 for k in ('planned', 'observed', 'S', 'Q', 'J', 'wrong_A')} for s in (.1, .2)}
    lost = []
    for r in t3_rows:
        c = counts[str(r['strength'])]; c['planned'] += 1
        ep = r.get('endpoints', {}).get(ALPHA)
        if ep is not None:
            c['observed'] += 1
            for key in ('S','Q','J'): c[key] += bool(ep[key])
            c['wrong_A'] += sum(r['endpoints'][o]['A'] for o in OWNERS[1:])
        old = historical[(r['source_id'],r['strength'],r['seed'])]
        if old['status'] == 'ok':
            prior = endpoint(old['calls'][ALPHA],old['payload'])
            for key in ('S','J'):
                if prior[key] and (ep is None or not ep[key]):
                    lost.append(dict(source_id=r['source_id'],strength=r['strength'],seed=r['seed'],endpoint=key))
    complete = len(t3_rows)==12 and len({(r['source_id'],r['strength'],r['seed']) for r in t3_rows})==12
    t3_pass = complete and not lost and all(counts[str(s)]['J'] >= n and
        counts[str(s)]['wrong_A'] == 0 for s,n in ((.1,6),(.2,5))) and all(
        r['status'] in ('ok','safety_blocked') for r in t3_rows)
    return dict(clean_vae_screen_pass=bool(screen), t3=counts, t3_complete=complete,
        lost_historical_positive_identities=lost, t3_screen_pass=bool(t3_pass),
        scientific_stage_a_pass=bool(screen and t3_pass), m1a_pass=False,
        supplied_pair_changes=[r['source_id'] for r in rows if r.get('same_pair') is False],
        distinct_writer_executions=sum(len({a['writer']['final_image'] for a in r.get('arms',{}).values()
            if a.get('writer',{}).get('final_image')}) for r in rows),
        scope='Development callable/supplier screen only; no full M1a, unseen-channel or population inference.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args(); out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=False)
    selected={r['source_id']:r for r in rows_at(COMPOSITION/'rows.jsonl')}
    historical={(r['source_id'],r['strength'],r['seed']):r for r in rows_at(T3/'rows.jsonl')
        if r['arm']=='candidate_C1' and r['source_id'] in IDS}
    if len(historical)!=12 or any(s not in selected for s in IDS):
        raise ValueError('Frozen two-source development ancestry missing')
    rows,t3_rows,c0_rows=[],[],[]
    record=dict(schema='journal-e3-s1-stage-a-v1',method='E3-S1+E3-BCH59-Q080',
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=sys.argv,data_split='development',usd=0,seeds=[0,1,2],sources=list(IDS),outcome='running',
        config=dict(cap_seconds=CAP,gpu_cap_bytes=GPU_CAP,ram_cap_bytes=RAM_CAP,owner=ALPHA,
            strengths=[.1,.2],semantic_views=7,binding='soft',roster_size=1,
            same_pair_reuse='only identical source and fixed q/h within this run',
            method_contract='research/journal-upgrade-20261009/e3-freeze-design.md',
            protocol='research/journal-upgrade-20261009/e3-s1-stage-a.md'),
        historical_targets={str(s):selected[s]['payload'] for s in IDS},ancestry=dict(composition=str(COMPOSITION),t3=str(T3)))
    ev=None
    def budget():
        rss,peak=working_set(); record['peak_ram_bytes']=max(peak,record.get('peak_ram_bytes',0))
        gpu=int(ev.torch.cuda.max_memory_allocated()) if ev else 0
        record['peak_allocated_bytes']=max(gpu,record.get('peak_allocated_bytes',0))
        if time.monotonic()-STARTED>=CAP or gpu>GPU_CAP or max(rss,peak)>RAM_CAP:
            raise RuntimeError('Frozen E3-S1 inclusive resource cap exceeded')
    def save():
        for name,data in (('rows',rows),('t3-rows',t3_rows),('c0-rows',c0_rows)):
            (out/(name+'.jsonl')).write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in data),encoding='utf-8')
        record['duration_seconds']=time.monotonic()-STARTED
        record['summary']=summarize(rows,t3_rows,historical)
        record['budget_overrun']=record['duration_seconds']>CAP
        record['stage_a_pass']=bool(record['outcome']=='completed' and not record['budget_overrun'] and
            record['summary']['scientific_stage_a_pass'])
        write(out/'run.json',record); write(out/'summary.json',record['summary'])
    save()
    try:
        import numpy as np
        import torch
        import diffusers
        from diffusers import AutoencoderKL
        from PIL import Image
        import three_threat_models as models
        from f4_transfer_probe import SOURCES
        from journal_vae_probe import Evaluator,SDXL,SDXL_REV
        from journal_ddim_channel import DifferentiableDDIM
        from journal_readability_probe import load,reconstruct
        from journal_e3_writer import embed,supply_f5
        from journal_bch_readout import detect_rgb
        if diffusers.__version__!='0.35.1': raise ValueError('Pinned diffusers required')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/torch.cuda.get_device_properties(0).total_memory)
        ev=Evaluator(); channel=DifferentiableDDIM(models.load_regenerator(ASSETS))
        other=AutoencoderKL.from_pretrained(SDXL,local_files_only=True,use_safetensors=True,
            torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        record['config'].update(profile=ev.profile,sdxl_revision=SDXL_REV)
        record['environment']=dict(torch=torch.__version__,diffusers=diffusers.__version__,gpu=torch.cuda.get_device_name(0),
            threads=torch.get_num_threads(),matmul_tf32=torch.backends.cuda.matmul.allow_tf32,cudnn_tf32=torch.backends.cudnn.allow_tf32)
        record['startup_seconds']=time.monotonic()-STARTED
        def calls(rgb,owners):
            budget(); features,latent=ev.features(rgb,7),ev.reader.latent(rgb)
            result={o:detect_rgb(rgb,latent,o,ev.profile,features,binding='soft',binding_mode='combined',roster_size=1) for o in owners}
            budget(); return result
        for sid in IDS:
            budget(); source=load(SOURCES[sid]); target=selected[sid]['payload']
            row=dict(source_id=sid,source_image=str(SOURCES[sid]),historical_payload=target,arms={})
            rows.append(row); folder=out/str(sid); folder.mkdir(); save()
            c0={}
            for condition in CONDITIONS:
                rgb=reconstruct(ev,other,source,condition); path=folder/f'C0-{condition}.png'
                Image.fromarray(rgb).save(path); rgb=load(path); call=calls(rgb,(ALPHA,))[ALPHA]
                c0[condition]=dict(source_id=sid,condition=condition,image=str(path),call=call,endpoint=endpoint(call))
                c0_rows.append(c0[condition])
            def evaluate(writer,payload,arm):
                result=dict(writer=writer,payload=payload,conditions={})
                if not writer.get('final_image') or 'clean' not in writer.get('conditions', {}): return result
                marked=load(writer['final_image'])
                for condition in CONDITIONS:
                    rgb=reconstruct(ev,other,marked,condition); path=folder/f'{arm}-{condition}.png'
                    Image.fromarray(rgb).save(path); rgb=load(path)
                    if condition=='clean':
                        native={ALPHA:writer['conditions']['clean']['calls'][ALPHA],**calls(rgb,(OWNERS[1],))}
                    else: native=calls(rgb,OWNERS[:2])
                    result['conditions'][condition]=dict(image=str(path),calls=native,
                        endpoints={o:endpoint(c,payload if o==ALPHA else None) for o,c in native.items()},
                        c0_call_reference=c0[condition]['image'],c0_endpoint=c0[condition]['endpoint'],
                        quality_source=ev.metrics(source,rgb),quality_marked=ev.metrics(marked,rgb))
                    budget()
                return result
            old_writer=embed(source,ALPHA,int(target['q'],16),int(target['h'],16),ev,other,channel,folder/'historical-writer',budget)
            row['arms']['historical']=dict(writer=old_writer,payload=target,conditions={}); save(); budget()
            if old_writer['status']=='construction_failed': raise RuntimeError('Historical writer execution failure; retained result.json')
            row['arms']['historical']=evaluate(old_writer,target,'historical'); save()
            supplier=supply_f5(source,ev,folder/'S1-supplier',budget); row['supplier']=supplier
            if supplier['status']=='ok':
                row['same_pair']=all(supplier['payload'][k]==target[k] for k in ('q','h'))
            budget(); save()
            if supplier['status']=='supplier_failed' and 'Fresh F5 bootstrap native channels unreadable' not in supplier.get('error',''):
                raise RuntimeError('S1 supplier execution failure; retained supplier.json')
            if supplier['status']=='ok':
                if row['same_pair']:
                    row['arms']['S1']=copy.deepcopy(row['arms']['historical'])
                    row['arms']['S1'].update(payload=supplier['payload'],reuse='same source and exact q/h in this run; historical writer and evaluation calls reused once')
                else:
                    new_writer=embed(source,ALPHA,supplier['q'],supplier['h'],ev,other,channel,folder/'S1-writer',budget)
                    row['arms']['S1']=dict(writer=new_writer,payload=supplier['payload'],conditions={}); save(); budget()
                    if new_writer['status']=='construction_failed': raise RuntimeError('S1 writer execution failure; retained result.json')
                    row['arms']['S1']=evaluate(new_writer,supplier['payload'],'S1')
            save(); print(json.dumps(dict(source_id=sid,supplier=supplier['status'],same_pair=row.get('same_pair'),
                arms={k:arm_pass(v) for k,v in row['arms'].items()})),flush=True)
        if summarize(rows,t3_rows,historical)['clean_vae_screen_pass']:
            for row in rows:
                arm=row['arms']['S1']; marked=load(arm['writer']['final_image']); folder=out/str(row['source_id'])
                for strength in (.1,.2):
                    for seed in (0,1,2):
                        budget(); r=dict(source_id=row['source_id'],strength=strength,seed=seed,status='running',payload=arm['payload'])
                        t3_rows.append(r); save()
                        try:
                            with torch.inference_mode():
                                output=channel.pipe(**models.regeneration_kwargs(strength,seed,Image.fromarray(marked),torch.Generator))
                            steps,_=channel.pipe.get_timesteps(20,strength,channel.pipe._execution_device)
                            r['timesteps']=steps.cpu().tolist()
                            if len(r['timesteps'])!=int(20*strength): raise ValueError('Official effective timesteps differ')
                            image=models.validate_generated(output)
                            path=folder/f'S1-t3-{strength}-{seed}.png'; image.save(path); rgb=load(path)
                            native=calls(rgb,OWNERS)
                            r.update(status='ok',image=str(path),calls=native,
                                endpoints={o:endpoint(c,arm['payload'] if o==ALPHA else None) for o,c in native.items()},
                                quality_marked=ev.metrics(marked,rgb))
                        except RuntimeError as exc:
                            if str(exc)!='safety_checker_blocked_output':
                                r.update(status='failed',error=traceback.format_exc()); raise
                            r.update(status='safety_blocked',image=None,calls={},endpoints={})
                        budget(); save(); print(json.dumps({k:r[k] for k in ('source_id','strength','seed','status')}),flush=True)
        budget(); record['outcome']='completed'
    except Exception:
        record.update(outcome='failed',error=traceback.format_exc()); raise
    finally:
        save()


if __name__=='__main__': main()
