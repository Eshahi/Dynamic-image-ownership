"""Frozen E3-PP1 public donor-vector projection; exploratory development only."""
from __future__ import annotations

import time
STARTED = time.monotonic()  # Includes imports, model startup and finalization.
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts')]
from journal_e3_threat_supplement import (read, write, working_set, full, ALPHA, IDS,
    candidate_arguments, load_candidate, retained_rows, reuse_row, RETAINED_PROJECTION)

CAP, GPU_CAP, RAM_CAP = 1800., 10*1024**3, 16*1024**3
MODES = ('combined', 'semantic_only', 'perceptual_only', 'none')
METHODS = ('E3', 'v5')


def endpoints(call, target=None):
    from journal_bch_analysis import endpoint
    target = {k:v for k,v in (target or {}).items() if k in ('q','h') and v is not None}
    result = endpoint(call, target)
    for tier, key in (('semantic','q_bit_errors'), ('instance','h_bit_errors')):
        if not call[tier]['read']:
            result[key] = None
    result['D'] = bool(result['Q'] and result['H']) if target else None
    result['semantic_presence'] = bool(call['semantic']['found'])
    result['fragile_presence'] = bool(call['instance']['found'])
    result['both_presence'] = bool(result['semantic_presence'] and result['fragile_presence'])
    return result


def vector_error(value, target):
    import numpy as np
    value, target = np.asarray(value, np.float64), np.asarray(target, np.float64)
    if not np.isfinite(value).all() or not np.isfinite(target).all():
        raise ValueError('Nonfinite native vector')
    difference = value-target
    norm = float(np.linalg.norm(target))
    return dict(absolute_rms=float(np.sqrt(np.mean(difference**2))),
        normalized_l2=float(np.linalg.norm(difference)/norm) if norm else None,
        normalized_l2_reason=None if norm else 'zero_target_norm', target_norm=norm)


def semantic_inverse(reader, recipient, layout, target, check):
    """Only public pD enters the attack; never an intended/decoded payload."""
    import numpy as np
    torch, dev = reader.torch, reader.device
    x = reader.tensor(recipient.astype(np.float64)/255.)
    budget = math.sqrt(recipient.size)*10**(-35.2/20)
    D = torch.from_numpy(layout.dct.astype(np.float32)).to(dev)
    ch,u,v = (torch.from_numpy(a).to(dev) for a in (layout.ch,layout.u,layout.v))
    coeff = torch.from_numpy((layout.weights*layout.signs).astype(np.float32)).to(dev)
    chip = torch.from_numpy(layout.chip).to(dev)
    norms = torch.from_numpy(layout.norms.astype(np.float32)).to(dev)
    pD = torch.from_numpy(np.asarray(target,np.float32)).to(dev)
    delta = torch.zeros_like(x,requires_grad=True)
    losses = []
    for step in range(40):
        check()
        z = reader.encode((x+delta).clamp(0,1))
        c = torch.einsum('ij,cjk,lk->cil',D,z,D)
        p = torch.zeros(320,device=dev).index_add(0,chip,c[ch,u,v]*coeff)/norms
        loss = (p-pD).square().mean()
        g, = torch.autograd.grad(loss,delta)
        if not torch.isfinite(loss).item() or not torch.isfinite(g).all().item():
            raise ValueError(f'Nonfinite semantic loss/gradient at step {step}')
        losses.append(float(loss.item()))
        with torch.no_grad():
            delta -= budget*(.2 if step<20 else .05)*g/(g.norm()+1e-12)
            projected = (x+delta).clamp(0,1)-x
            n = projected.norm()
            if n>budget: projected *= budget/n
            delta.copy_(projected)
            if not torch.isfinite(delta).all().item():
                raise ValueError(f'Nonfinite iterate at step {step}')
        check()
    with torch.no_grad():
        continuous = (x+delta).clamp(0,1)[0].permute(1,2,0).double().cpu().numpy()
    return np.clip(np.rint(255*continuous),0,255).astype(np.uint8), dict(
        gradient_evaluations=40, detector_feedback_queries=0, losses=losses,
        continuous_l2=float(delta.detach().norm().item()), budget_l2=budget)


def fragile_replace(rgb, fragile, target, codec, check):
    """Exact final three-pass loop from v5_study_protocol.transfer."""
    output = rgb.tolist()
    height,width = rgb.shape[:2]
    bits,fragile_signs,fragile_norms = fragile.carrier
    per_block = len(fragile.positions)
    for _ in range(3):
        check()
        coefficients = codec.base._analyse(codec.luminance_from_rgb(output),fragile.analysis)[1]
        current = fragile.projections(coefficients)
        step = [(a-c)/norm for a,c,norm in zip(target,current,fragile_norms)]
        if not all(math.isfinite(s) for s in step): raise ValueError('Nonfinite fragile step')
        for b in range(len(coefficients)):
            values = [step[bits[b*per_block+offset]]*fragile_signs[b*per_block+offset] for offset in range(per_block)]
            top,left = b//(width//8)*8,b%(width//8)*8
            for y in range(8):
                for x in range(8):
                    delta = sum(value*plane[y*8+x] for value,plane in zip(values,fragile.planes))
                    output[top+y][left+x] = tuple(int(min(255,max(0,math.floor(c+delta+.5)))) for c in output[top+y][left+x])
        check()
    return output


def summarize(rows, planned):
    good = [r for r in rows if r.get('status')=='ok']
    done = {r['id'] for r in good}
    result = dict(m1a_pass=False, strict_e3_b='FAILED_FINAL',
        scope='E3-PP1 exploratory native public-projection supplement',
        inventory=dict(planned_rows=len(planned),completed_rows=len(done),
            missing_identities=sorted(set(planned)-done),failed_rows=[r['id'] for r in rows if r.get('status')=='failed']),
        strata={}, interpretation='native operating points/inverses differ; delivery loss is descriptive; no human admissibility or population FPR')
    for stratum,n in (('T4_projection',20),('T4_sham',20),('T5_same',7)):
        cell, positives = {},{}
        for method in METHODS:
            panel = [r for r in good if r['method']==method and r['stratum']==stratum]
            positives[method] = {r['attack_id'] for r in panel if r['endpoints']['combined']['F']}
            delivered = {key:[r for r in panel if r['endpoints']['none'][key]] for key in ('Q','D')}
            cell[method] = dict(planned=n,available=len(panel),false_F=len(positives[method]),
                exact_delivery_status='not_applicable_unmarked_sham' if stratum=='T4_sham' else 'fixed_evaluator_donor_targets',
                false_F_identities=sorted(positives[method]),endpoint_counts={key:(None if stratum=='T4_sham' and key in ('Q','H','D') else sum(bool(r['endpoints']['none'][key]) for r in panel)) for key in ('Q','H','D','A','semantic_presence','fragile_presence','both_presence')},
                conditional={key:dict(denominator=len(sub),false_F=sum(r['endpoints']['combined']['F'] for r in sub),
                    rejection_fraction=sum(not r['endpoints']['combined']['F'] for r in sub)/len(sub) if sub else None,
                    status='not_applicable_unmarked_sham' if stratum=='T4_sham' else ('descriptive' if sub else 'undefined_zero_delivery')) for key,sub in delivered.items()},
                exploratory_proxy_subsets={str(limit):dict(available=sum(r['recipient_quality']['lpips']<=limit for r in panel),false_F=sum(r['endpoints']['combined']['F'] for r in panel if r['recipient_quality']['lpips']<=limit)) for limit in (.2,.3)})
        cell['new_E3_false_F_vs_v5'] = sorted(positives['E3']-positives['v5'])
        cell['continuity_pass'] = all(cell[m]['available']==n for m in METHODS) and not cell['new_E3_false_F_vs_v5'] and cell['E3']['false_F']<=cell['v5']['false_F']
        if stratum=='T4_sham':
            cell['continuity_pass'] &= cell['E3']['endpoint_counts']['A']==0
        result['strata'][stratum] = cell
    result['projection_continuity_pass'] = done==set(planned) and all(c['continuity_pass'] for c in result['strata'].values())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    candidate_arguments(parser)
    parser.add_argument('--immediate-dir',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=False)
    rows,planned,ev,active = [],[],None,None
    record = dict(schema='journal-e3-pp1-v1',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=sys.argv,data_split='development',sources=list(IDS),seeds=[],usd=0,outcome='running',
        candidate_kind='E3-S1' if args.s1_stage_b_dir else 'E3-supplied-payload',
        immediate_dir=str(args.immediate_dir.resolve()),
        config=dict(cap_seconds=CAP,gpu_cap_bytes=GPU_CAP,ram_cap_bytes=RAM_CAP,steps=40,psnr_db=35.2,
            step_fractions=[.2,.05],fragile_passes=3,precision='float32',continuous_clamped_rgb=True,
            quantization_STE=False,roster=1,owner=ALPHA,E3_decoder='E1-BCH59-A',E3_views=7,E3_binding='soft',
            thresholds='unchanged',planned_gradient_evaluations=1880,detector_feedback_queries=0))
    candidate_dir = (args.s1_stage_b_dir or args.e3_stage_a_dir).resolve()
    candidate_key = 's1_stage_b_dir' if args.s1_stage_b_dir else 'e3_stage_a_dir'
    record[candidate_key] = str(candidate_dir)
    if args.s1_stage_b_dir:
        record['schema'] = 'journal-e3-s1-pp1-v1'
        record['config'].update(new_gradient_evaluations=1080, reused_gradient_evaluations=800)
    write(out/'run.json',record)

    def check():
        rss,peak = working_set()
        record['peak_ram_bytes'] = max(record.get('peak_ram_bytes',0),peak)
        gpu = int(ev.torch.cuda.max_memory_allocated()) if ev else 0
        record['peak_allocated_bytes'] = max(record.get('peak_allocated_bytes',0),gpu)
        if time.monotonic()-STARTED>CAP or gpu>GPU_CAP or max(rss,peak)>RAM_CAP:
            raise RuntimeError('Fixed E3-PP1 inclusive time/resource cap exceeded')

    def append(row):
        rows.append(row)
        with (out/'rows.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(row,allow_nan=False)+'\n')
        print(json.dumps(dict(id=row['id'],status=row['status'])),flush=True)

    try:
        check()
        import numpy as np
        from PIL import Image
        from journal_vae_probe import Evaluator
        from f4_gate import V5_RESULTS
        import f5_latent_codec as f5
        import revised_watermark_v5 as v5
        import journal_bch_readout as rc
        from v5_study_protocol import inventory
        e3rows,e3run = load_candidate(args)
        retained = retained_rows(RETAINED_PROJECTION, 'projection_continuity_pass') if args.s1_stage_b_dir else {}
        if retained and len(retained)!=94: raise ValueError('Retained projection inventory differs')
        e3 = {r['source_id']:r for r in e3rows}
        immediate = read(args.immediate_dir/'run.json')
        if immediate.get('outcome')!='completed' or not immediate['summary']['immediate_continuity_pass']:
            raise ValueError('Passing completed immediate supplement required')
        if (Path(immediate.get(candidate_key, '')).resolve()!=candidate_dir or
            (args.s1_stage_b_dir and immediate.get('candidate_kind')!='E3-S1')):
            raise ValueError('Immediate supplement uses a different E3 initializer')
        controls = {r['id']:r for r in (json.loads(s) for s in (args.immediate_dir/'rows.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()) if r.get('axis')=='clean'}
        old = read(V5_RESULTS)['rows']
        labels = [dict(left=r['left'],right=r['right'],label=r['semantic_label']) for r in old if r.get('axis')=='T5']
        slots = [r for r in inventory(labels) if (r['axis']=='T4' and r['arm'] in ('public_projection','unmarked_projection_sham')) or r['axis']=='T5-transfer']
        historical = {r['id']:r for r in old}
        if len(slots)!=47 or len({r['id'] for r in slots})!=47: raise ValueError('47 fixed identities required')
        planned = [m+'/'+r['id'] for m in METHODS for r in slots]
        if args.s1_stage_b_dir and set(retained)!=set(planned):
            raise ValueError('Retained projection identities differ from frozen inventory')
        record.update(planned_identities=planned,ancestry=dict(v5=str(V5_RESULTS),E3=str(candidate_dir/'rows.jsonl'),immediate=str(args.immediate_dir/'rows.jsonl')))
        if args.s1_stage_b_dir:
            record['ancestry'].update(S1_stage_b=str(candidate_dir/'run.json'),
                S1_stage_a=e3run['ancestry']['stage_a'], retained_projection=str(RETAINED_PROJECTION/'run.json'))
        record['evaluator_targets'] = {str(sid):dict(q=e3[sid]['payload']['q'],h=e3[sid]['payload']['h'],q_target_basis=e3[sid]['payload']['q_target_basis'],h_target_basis=e3[sid]['payload']['h_target_basis']) for sid in IDS}
        write(out/'run.json',record)
        import torch
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/torch.cuda.get_device_properties(0).total_memory)
        ev = Evaluator(); check()
        profile = v5.validate_profile(e3run['config']['profile'])
        if profile!=v5.validate_profile(ev.profile): raise ValueError('Pinned profile differs')
        checked,key,config = v5._resolve(profile,None)
        owner = v5.canonical_owner(ALPHA)
        layout = f5.Layout(checked,key,config,owner)
        fragile = v5._Fragile(checked,key,config,owner,512,512)

        def load(path):
            with Image.open(path) as image: rgb = np.asarray(image.convert('RGB'),np.uint8)
            if rgb.shape!=(512,512,3): raise ValueError('RGB8 512x512 required')
            return rgb

        def fragile_vector(rgb):
            return fragile.projections(v5.base._analyse(v5.luminance_from_rgb(rgb.tolist()),fragile.analysis)[1])

        cache = {}
        def pixels(method,sid,control):
            identity = f'clean/{method}/{sid}/{control}'
            row = controls[identity]
            if row['status']!='ok': raise ValueError('Unavailable immediate clean control')
            if identity not in cache: cache[identity] = load(row['image'])
            return cache[identity]

        for slot in slots:
            stratum = 'T5_same' if slot['axis']=='T5-transfer' else ('T4_sham' if slot['arm']=='unmarked_projection_sham' else 'T4_projection')
            donor,recipient = slot['donor_id'],slot['recipient_id']
            dc = 'C0' if stratum=='T4_sham' else 'C1'
            for method in METHODS:
                active = dict(id=method+'/'+slot['id'],attack_id=slot['id'],method=method,stratum=stratum,
                    axis=slot['axis'],arm=slot['arm'],donor_id=donor,recipient_id=recipient,status='running')
                check()
                if args.s1_stage_b_dir and (method=='v5' or stratum=='T4_sham'):
                    active = reuse_row(retained[active['id']], RETAINED_PROJECTION)
                    if stratum=='T4_sham':
                        for sid, key in ((donor,'donor_control_ref'),(recipient,'recipient_C0_ref')):
                            current = controls[f'clean/{method}/{sid}/C0']
                            if current.get('observation_provenance', {}).get('kind')!='reused_unchanged_observation':
                                raise ValueError('Sham reuse requires unchanged C0 observations')
                            active[key] = dict(record=str(args.immediate_dir/'rows.jsonl'), identity=current['id'])
                    append(active); active=None; continue
                donor_row = controls[f'clean/{method}/{donor}/{dc}']
                recipient_row = controls[f'clean/{method}/{recipient}/C0']
                target = None
                if dc=='C1':
                    if method=='E3': target = dict(record['evaluator_targets'][str(donor)])
                    else:
                        report = historical[f'clean-{donor}-C1']['source_feature_embedding_report']
                        target = dict(q=report.get('semantic_code'),h=report.get('perceptual_hash'),
                            q_target_basis='historical intended embedding report; absent remains unknown',h_target_basis='historical intended embedding report; absent remains unknown')
                active.update(payload=target,donor_control_ref=dict(record=str(args.immediate_dir/'rows.jsonl'),identity=donor_row['id']),
                    recipient_C0_ref=dict(record=str(args.immediate_dir/'rows.jsonl'),identity=recipient_row['id']),
                    donor_clean_decoded=dict(q=donor_row['calls'][ALPHA]['semantic'].get('decoded_code'),h=donor_row['calls'][ALPHA]['instance'].get('decoded_code')))
                r0 = pixels(method,recipient,'C0')
                if method=='v5' and not np.array_equal(r0,pixels('E3',recipient,'C0')):
                    raise ValueError('Methods do not share canonical recipient C0 pixels')
                if method=='v5':
                    ref = historical[slot['id']]
                    path = V5_RESULTS.parent.parent/ref['image']['path']
                    rgb = load(path)
                    calls = {}
                    for mode in MODES:
                        values = [d['result'] for d in ref['detections'] if d['claimed_owner']==ALPHA and d['binding_mode']==mode]
                        if len(values)!=1 or not full(values[0]) or values[0]['owners_tested']!=1: raise ValueError('Missing retained native v5 full call')
                        calls[mode] = values[0]
                    quality = dict(psnr_db=ref['quality']['psnr_db'],ssim_rgb=ref['quality']['ssim_rgb'],lpips=ref['quality']['lpips']['value'])
                    active.update(call_provenance={mode:dict(kind='reused_full_call',record=str(V5_RESULTS),identity=slot['id']) for mode in MODES},
                        pixel_provenance=dict(kind='reused_native_v5_transfer_pixel',record=str(V5_RESULTS),identity=slot['id']),
                        projection_errors=dict(status='not_recorded_historically',before=None,after=None),
                        quality_provenance=dict(kind='reused_retained_recipient_metrics',record=str(V5_RESULTS),identity=slot['id']))
                else:
                    # Intended targets and evaluator observations are not passed here.
                    donor_rgb = pixels(method,donor,dc)
                    pD = layout.projections(ev.reader.latent(donor_rgb)); fD = fragile_vector(donor_rgb)
                    active['public_vector_targets'] = dict(semantic=pD,fragile=fD,source_image=donor_row['image'])
                    vector_error(pD,pD); vector_error(fD,fD)
                    semantic_rgb,optimization = semantic_inverse(ev.reader,r0,layout,pD,check)
                    before = dict(semantic=vector_error(layout.projections(ev.reader.latent(semantic_rgb)),pD),fragile=vector_error(fragile_vector(semantic_rgb),fD))
                    active.update(optimization=optimization,projection_errors=dict(before=before))
                    rgb = np.asarray(fragile_replace(semantic_rgb,fragile,fD,v5,check),np.uint8)
                    path = out/(active['id'].replace('/','-')+'.png'); Image.fromarray(rgb).save(path); rgb = load(path)
                    latent = ev.reader.latent(rgb)
                    after = dict(semantic=vector_error(layout.projections(latent),pD),fragile=vector_error(fragile_vector(rgb),fD))
                    features = ev.features(rgb,7); calls = {}
                    for mode in MODES:
                        check()
                        calls[mode] = rc.detect_rgb(rgb,latent,ALPHA,profile,features,binding_mode=mode,roster_size=1,binding='soft')
                    quality = ev.metrics(r0,rgb)
                    active.update(projection_errors=dict(before=before,after=after),call_provenance={mode:dict(kind='new_call',image=str(path)) for mode in MODES},pixel_provenance=dict(kind='new_E3_PP1_public_vectors'))
                active.update(status='ok',image=str(path),calls=calls,endpoints={mode:endpoints(call,target) for mode,call in calls.items()},recipient_quality=quality)
                check(); append(active); active=None
        check(); record['outcome']='completed'
    except Exception:
        error = traceback.format_exc(); record.update(outcome='failed',error=error)
        failure = active or dict(id='projection_failure',axis='failure')
        failure.update(status='failed',error=error); append(failure); write(out/'failure.json',failure)
        raise
    finally:
        record['summary'] = summarize(rows,planned)
        for _ in range(2):
            record['duration_seconds'] = time.monotonic()-STARTED
            record['budget_overrun'] = record['duration_seconds']>CAP
            if record['budget_overrun'] or record['outcome']!='completed': record['summary']['projection_continuity_pass']=False
            write(out/'summary.json',record['summary']); write(out/'run.json',record)


if __name__=='__main__':
    main()
