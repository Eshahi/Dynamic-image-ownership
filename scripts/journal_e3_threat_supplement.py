"""Bounded E3-A1 residual-transfer and component-geometry development supplement.

This adapter does not execute the assessors' complete contracts. Strict E3-B
remains failed; the projection and genuine cross-owner panels remain missing.
"""
from __future__ import annotations

import time
STARTED = time.monotonic()  # Inclusive of scientific imports and model startup.
import argparse
import ctypes
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
F5_DIR = MAIN / '.thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7'
F5_T4 = MAIN / '.thesis-build/dev-runs/20261005-0700-f5r2-t4'
F5_T5 = MAIN / '.thesis-build/dev-runs/20261005-0700-f5r2-t5/run.json'
CAP, GPU_CAP, RAM_CAP, DISK_CAP = 900., 10*1024**3, 16*1024**3, 1024**3
IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
ALPHA = 'qim-pilot-owner-alpha'
OWNERS = tuple('qim-pilot-owner-'+o for o in ('alpha', 'beta', 'gamma', 'delta'))
METHODS = ('E3', 'F5', 'v5')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def full(call):
    return isinstance(call, dict) and all(k in call for k in ('semantic', 'instance', 'outcome', 'owner_id', 'owners_tested', 'binding_mode', 'detector_config_id'))


def measures(call, target=None):
    from journal_bch_analysis import endpoint
    e = endpoint(call, target)
    e['D'] = bool(e['Q'] and e['H']) if target else None
    e['semantic_presence'] = bool(call['semantic']['found'])
    e['both_presence'] = bool(call['semantic']['found'] and call['instance']['found'])
    return e


def working_set():
    # Windows process RSS, using the platform API rather than another dependency.
    class Counters(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
            'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
            'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
    c = Counters(); c.cb = ctypes.sizeof(c)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    api = ctypes.WinDLL('psapi', use_last_error=True).GetProcessMemoryInfo
    api.argtypes = [ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong]
    if not api(kernel.GetCurrentProcess(), ctypes.byref(c), c.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(c.WorkingSetSize), int(c.PeakWorkingSetSize)


def summary(rows, planned):
    clean = [r for r in rows if r.get('axis')=='clean' and r.get('status')=='ok']
    attacks = [r for r in rows if r.get('axis')=='T4' and r.get('status')=='ok']
    geometry = [r for r in rows if r.get('axis')=='T5_geometry' and r.get('status')=='ok']
    done = {r['id'] for r in rows if r.get('status')=='ok'}
    result = dict(m1a_pass=False, strict_e3_b='FAILED_FINAL',
        scope='post hoc E3-A1 immediate development supplement only; no full assessor contract',
        inventory=dict(planned_rows=len(planned), completed_rows=len(done),
            missing_identities=sorted(set(planned)-done),
            failed_rows=[r for r in rows if r.get('status')=='failed'],
            duplicate_identities=sorted({r['id'] for r in rows if sum(x['id']==r['id'] for x in rows)>1})),
        clean={}, T4={}, T5={}, unmeasured=['20 public projections', '20 projection shams',
            '7 same-topic public transfers', 'genuine cross-owner T5 panel',
            'reference-specific same-owner instance attribution'],
        interpretation='geometry is component proximity, never a false-attribution denominator; delivery losses are descriptive; native operating points differ, no matched-FPR claim')
    for method in METHODS:
        panel = [r for r in clean if r['method']==method]
        c1 = [r for r in panel if r['control']=='C1']
        c0 = [r for r in panel if r['control']=='C0']
        result['clean'][method] = dict(c1_rows=len(c1), c0_rows=len(c0),
            genuine_positive=sum(r['endpoints'][ALPHA]['F'] for r in c1),
            clean_exact_q_h_both=sum(bool(r['endpoints'][ALPHA]['Q'] and r['endpoints'][ALPHA]['H'] and r['endpoints'][ALPHA]['F']) for r in c1),
            wrong_owner_any=sum(r['endpoints'][o]['A'] for r in c1 for o in OWNERS[1:]),
            c0_any=sum(r['endpoints'][o]['A'] for r in c0 for o in OWNERS),
            calls=sum(len(r['calls'])+1 for r in panel),
            reused_calls=sum(sum(p['kind']=='reused_full_call' for p in r['call_provenance'].values()) for r in panel),
            planned=dict(genuine=12, wrong_owner=36, c0=48, none_delivery_controls=24))
    residual_ok = True
    for scale in (.5, 1.):
        cell = {}
        positives = {}
        delivered = {}
        for method in METHODS:
            panel = [r for r in attacks if r['method']==method and r['scale']==scale]
            positives[method] = {r['attack_id'] for r in panel if r['endpoints']['combined']['F']}
            delivered[method] = {r['attack_id'] for r in panel if r['endpoints']['none']['D']}
            cell[method] = dict(attempts=len(panel), false_full=len(positives[method]),
                false_full_identities=sorted(positives[method]),
                exact_Q=sum(r['endpoints']['none']['Q'] for r in panel),
                exact_H=sum(r['endpoints']['none']['H'] for r in panel), exact_D=len(delivered[method]),
                semantic_presence=sum(r['endpoints']['none']['semantic_presence'] for r in panel),
                both_presence=sum(r['endpoints']['none']['both_presence'] for r in panel),
                binding_rejection_given_exact_D=(sum(not r['endpoints']['combined']['F'] for r in panel if r['endpoints']['none']['D'])/len(delivered[method]) if delivered[method] else None),
                conditional_binding_status='undefined_zero_delivery' if not delivered[method] else 'descriptive_selected_delivered_cases')
        cell['new_false_full_vs_v5'] = sorted(positives['E3']-positives['v5'])
        cell['lost_false_full_vs_v5'] = sorted(positives['v5']-positives['E3'])
        cell['delivery_changes'] = {m:dict(lost=sorted(delivered[m]-delivered['E3']), new=sorted(delivered['E3']-delivered[m])) for m in ('F5', 'v5')}
        cell['delivery_identity_changes'] = {}
        for endpoint_name in ('Q', 'H', 'D', 'semantic_presence', 'both_presence'):
            sets = {m:{r['attack_id'] for r in attacks if r['method']==m and r['scale']==scale and r['endpoints']['none'][endpoint_name]} for m in METHODS}
            cell['delivery_identity_changes'][endpoint_name] = {m:dict(lost=sorted(sets[m]-sets['E3']), gained=sorted(sets['E3']-sets[m])) for m in ('F5', 'v5')}
        cell['continuity_pass'] = all(cell[m]['attempts']==20 for m in METHODS) and not cell['new_false_full_vs_v5'] and cell['E3']['false_full']<=cell['v5']['false_full']
        residual_ok &= cell['continuity_pass']
        result['T4'][str(scale)] = cell
    geometry_ok = len(geometry)==66
    keys = ('E3_single_C0','E3_single_C1','E3_seven_C0','E3_seven_C1','F5_single_C0','F5_single_C1','v5_C0','v5_C1')
    for label in sorted({r['semantic_label'] for r in geometry}):
        panel = [r for r in geometry if r['semantic_label']==label]
        cell = {}
        for key in keys:
            vals = [r['distances'][key] for r in panel]
            cell[key] = dict(pairs=len(vals), q_near=sum(d['semantic']<=6 for d in vals),
                h_near=sum(d['instance']<=6 for d in vals),
                joint_near=sum(d['semantic']<=6 and d['instance']<=6 for d in vals))
        for control in ('C0','C1'):
            def near(key):
                return {r['pair_id'] for r in panel if r['distances'][key]['semantic']<=6 and r['distances'][key]['instance']<=6}
            old, new = near('v5_'+control), near('E3_single_'+control)
            cell['historical_'+control] = dict(new_joint_identities=sorted(new-old), lost_joint_identities=sorted(old-new), continuity_pass=not(new-old) and len(new)<=len(old))
            geometry_ok &= cell['historical_'+control]['continuity_pass']
        result['T5'][label] = cell
    e3clean = result['clean']['E3']
    result['clean_control_pass'] = bool(e3clean['c1_rows']==e3clean['c0_rows']==12 and
        e3clean['clean_exact_q_h_both']==12 and not e3clean['wrong_owner_any'] and not e3clean['c0_any'])
    result['immediate_continuity_pass'] = bool(residual_ok and geometry_ok and result['clean_control_pass'] and done==set(planned) and not result['inventory']['duplicate_identities'])
    result['new_calls'] = sum(sum(p['kind']!='reused_full_call' for p in r.get('call_provenance', {}).values()) for r in rows)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--e3-stage-a-dir', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=False)
    rows, planned, ev = [], [], None
    record = dict(schema='journal-e3-a1-immediate-threat-supplement-v1',
        commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        command=sys.argv, config=dict(cap_seconds=CAP, gpu_cap_bytes=GPU_CAP, ram_cap_bytes=RAM_CAP,
            extra_disk_cap_bytes=DISK_CAP, E3_decoder='E1-BCH59-A', E3_views=7, E3_binding='soft',
            E3_roster=1, v5_clean_roster=4, v5_T4_roster='original per-call value',
            attack='three_threat_protocol.residual_transfer unchanged', scales=[.5,1.],
            detector_feedback_queries=0, thresholds='unchanged', strict_e3_b='FAILED_FINAL'),
        data_split='development', sources=list(IDS), seeds=[], usd=0,
        e3_stage_a_dir=str(args.e3_stage_a_dir.resolve()), outcome='running')
    write(out/'run.json', record)

    def check():
        rss, peak = working_set()
        record['peak_ram_bytes'] = max(record.get('peak_ram_bytes',0), peak)
        gpu = int(ev.torch.cuda.max_memory_allocated()) if ev else 0
        record['peak_allocated_bytes'] = max(record.get('peak_allocated_bytes',0), gpu)
        disk = sum(f.stat().st_size for f in out.rglob('*') if f.is_file())
        record['extra_disk_bytes'] = disk
        if time.monotonic()-STARTED>CAP or gpu>GPU_CAP or rss>RAM_CAP or peak>RAM_CAP or disk>DISK_CAP:
            raise RuntimeError('Fixed inclusive E3-A1 time/resource cap exceeded')

    def append(row):
        rows.append(row)
        with (out/'rows.jsonl').open('a', encoding='utf-8') as h:
            h.write(json.dumps(row, allow_nan=False)+'\n')
        print(json.dumps(dict(id=row['id'], status=row['status'])), flush=True)
        check()

    active = None
    try:
        check()
        import numpy as np
        from PIL import Image
        from journal_bch_quality_select import validate_stage_a
        from journal_vae_probe import Evaluator
        from f4_gate import V5_RESULTS
        from three_threat_protocol import residual_transfer
        from scripts import journal_bch_readout as rc, f5_latent_codec as f5, revised_watermark_v5 as v5
        e3rows, e3run = validate_stage_a(args.e3_stage_a_dir)
        e3 = {r['source_id']:r for r in e3rows}
        old = read(V5_RESULTS)['rows']
        old4 = [r for r in old if r.get('axis')=='T4' and r.get('arm')=='clean_donor_residual']
        old5 = [r for r in old if r.get('axis')=='T5']
        pairs = sorted({(r['donor_id'],r['recipient_id']) for r in old4})
        if len(old4)!=40 or len(pairs)!=20 or len(old5)!=66:
            raise ValueError('Historical 40 residual and 66 geometry inventory required')
        historical_f5 = read(F5_T4/'run.json')
        historical_geometry = read(F5_T5)
        f5gate = read(F5_DIR/'run.json')
        expected4={(d,r,s) for d,r in pairs for s in (.5,1.)}
        if ({(r['donor_id'],r['recipient_id'],r['scale']) for r in old4}!=expected4 or
            len(historical_f5['rows'])!=40 or
            {(r['donor_id'],r['recipient_id'],r['scale']) for r in historical_f5['rows']}!=expected4 or
            len(historical_geometry['rows'])!=66 or
            {r['id'] for r in historical_geometry['rows']}!={r['id'] for r in old5}):
            raise ValueError('Historical control identities are incomplete or differ')
        if any((r['left'],r['right'],r['semantic_label'])!=(next(x for x in old5 if x['id']==r['id'])['left'],
                next(x for x in old5 if x['id']==r['id'])['right'],next(x for x in old5 if x['id']==r['id'])['semantic_label'])
                for r in historical_geometry['rows']):
            raise ValueError('Historical F5 geometry labels/identities differ')
        if (f5gate['params'].get('binding')!='soft' or f5gate['params'].get('semantic_views')!=7):
            raise ValueError('Frozen F5 soft/seven-view rule required')
        planned = [f'clean/{m}/{sid}/{c}' for m in METHODS for sid in IDS for c in ('C0','C1')]
        planned += [f'T4/{m}/{d}/{r}/{s}' for m in METHODS for d,r in pairs for s in (.5,1.)]
        planned += ['geometry/'+r['id'] for r in old5]
        if len(set(planned))!=258:
            raise ValueError('Unexpected supplement identities')
        record['planned_identities'] = planned
        record['ancestry'] = dict(E3=str(args.e3_stage_a_dir/'run.json'), F5=str(F5_DIR/'run.json'),
            F5_T4=str(F5_T4/'run.json'), F5_T5=str(F5_T5), v5=str(V5_RESULTS))
        write(out/'run.json', record)
        import torch
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/torch.cuda.get_device_properties(0).total_memory)
        profile = v5.validate_profile(e3run['config']['profile'])
        ev = Evaluator(); check()
        if profile!=v5.validate_profile(f5gate['profile']) or profile!=v5.validate_profile(ev.profile):
            raise ValueError('Fixed profiles differ')
        ev.profile = profile
        original_clean = {(r['source_id'],r['control']):r for r in old if r.get('axis')=='clean' and r.get('control') in ('C0','C1')}
        targets = {'E3':{}, 'F5':{}, 'v5':{}}
        pixels, paths, codes, clean_ids = {}, {}, {}, {}

        def load(path):
            with Image.open(path) as img:
                rgb = np.asarray(img.convert('RGB'), np.uint8)
            if rgb.shape!=(512,512,3):
                raise ValueError('Expected retained RGB8 512x512')
            return rgb

        def detect(rgb, method, owner, features, latent, mode, roster=None):
            check()
            if method=='E3':
                value = rc.detect_rgb(rgb,latent,owner,profile,features,binding_mode=mode,roster_size=1,binding='soft')
            elif method=='F5':
                value = f5.detect_rgb(rgb,latent,owner,profile,features,binding_mode=mode,roster_size=1,
                    band=tuple(f5gate['params']['band']),whitening=f5gate['params']['whitening'],binding='soft')
            else:
                value = v5.detect_rgb(rgb.tolist(),owner,profile=profile,semantic_features=features,
                    binding_mode=mode,roster_size=roster)
            check(); return value

        # Each unique clean call is recorded once; donor positives and recipient
        # shams below link these rows, avoiding artificial replication counts.
        for method in METHODS:
            for sid in IDS:
                if method in ('E3','F5'):
                    targets[method][sid] = dict(e3[sid]['payload'])
                else:
                    report = original_clean[sid,'C1']['source_feature_embedding_report']
                    targets[method][sid] = dict(q=report['semantic_code'],h=report['perceptual_hash'],
                        q_target_basis='original recorded intended embedding payload',h_target_basis='original recorded intended embedding payload')
                for control in ('C0','C1'):
                    rid = f'clean/{method}/{sid}/{control}'; active = dict(id=rid,axis='clean',method=method,source_id=sid,control=control,status='running')
                    if method=='E3':
                        path = Path(e3[sid]['conditions']['clean']['image' if control=='C1' else 'c0_image'])
                    elif method=='F5':
                        path = F5_DIR/'images'/f'clean-{sid}-{control}.png'
                    else:
                        path = V5_RESULTS.parent.parent/original_clean[sid,control]['image']['path']
                    rgb = load(path); pixels[method,sid,control] = rgb; paths[method,sid,control] = str(path)
                    if control=='C0' and method!='E3' and not np.array_equal(rgb,pixels['E3',sid,'C0']):
                        raise ValueError('Methods do not share the exact historical unmarked recipient')
                    features = ev.features(rgb,1 if method=='v5' else 7)
                    latent = ev.reader.latent(rgb) if method!='v5' else None
                    calls, provenance = {}, {}
                    active.update(calls=calls,call_provenance=provenance)
                    for owner in OWNERS:
                        inherited = None
                        if method=='E3':
                            c = e3[sid]['conditions']['clean']
                            inherited = c['calls'].get(owner) if control=='C1' else (c['c0_call'] if owner==ALPHA else None)
                        elif method=='v5':
                            options = [d['result'] for d in original_clean[sid,control]['detections'] if d['claimed_owner']==owner and d['binding_mode']=='combined']
                            if len(options)==1: inherited=options[0]
                        if full(inherited):
                            calls[owner] = inherited
                            provenance[owner] = dict(kind='reused_full_call',record=str(args.e3_stage_a_dir/'rows.jsonl') if method=='E3' else str(V5_RESULTS),identity=rid)
                        else:
                            calls[owner] = detect(rgb,method,owner,features,latent,'combined',4 if method=='v5' else 1)
                            provenance[owner] = dict(kind='retained_pixel_enrichment' if method=='F5' else 'new_missing_call',image=str(path))
                    none = detect(rgb,method,ALPHA,features,latent,'none',1)
                    provenance['none/alpha'] = dict(kind='new_missing_delivery_control',image=str(path),roster_size=1)
                    target = targets[method][sid]
                    ep = {o:measures(calls[o],target if control=='C1' and o==ALPHA else None) for o in OWNERS}
                    # Recomputed components, not decoded watermark payloads.
                    codes[method,sid,control,7 if method!='v5' else 1] = (calls[ALPHA]['semantic_code'],calls[ALPHA]['perceptual_hash'])
                    if method=='E3':
                        single = ev.features(rgb,1)
                        codes[method,sid,control,1] = (f'{v5.semantic_code(single,profile=profile):08x}', f'{v5.perceptual_hash(v5.luminance_from_rgb(rgb.tolist()),profile=profile):08x}')
                    active.update(status='ok',image=str(path),calls=calls,delivery_none=none,
                        endpoints=ep,delivery_endpoints=measures(none,target if control=='C1' else None),
                        call_provenance=provenance,payload=target if control=='C1' else None)
                    clean_ids[method,sid,control] = rid; append(active); active=None

        for donor,recipient in pairs:
            for scale in (.5,1.):
                for method in METHODS:
                    rid = f'T4/{method}/{donor}/{recipient}/{scale}'
                    attack_id = f'{donor}|{recipient}|{scale}'
                    active = dict(id=rid,attack_id=attack_id,axis='T4',method=method,donor_id=donor,recipient_id=recipient,scale=scale,status='running')
                    calls, provenance = {}, {}
                    active.update(calls=calls,call_provenance=provenance)
                    r0 = pixels[method,recipient,'C0']
                    if method=='v5':
                        match = [r for r in old4 if (r['donor_id'],r['recipient_id'],r['scale'])==(donor,recipient,scale)]
                        if len(match)!=1: raise ValueError('Missing/duplicate v5 residual row')
                        ref=match[0]; path=V5_RESULTS.parent.parent/ref['image']['path']; rgb=load(path)
                        for mode in ('combined','none'):
                            matchcall=[d['result'] for d in ref['detections'] if d['claimed_owner']==ALPHA and d['binding_mode']==mode]
                            if len(matchcall)!=1 or not full(matchcall[0]): raise ValueError('Missing full v5 attack control')
                            calls[mode]=matchcall[0]; provenance[mode]=dict(kind='reused_full_call',record=str(V5_RESULTS),identity=ref['id'])
                    else:
                        if method=='F5':
                            path=F5_T4/f't4-residual-{donor}-{recipient}-{scale}.png'; rgb=load(path)
                            compact=[r for r in historical_f5['rows'] if (r['donor_id'],r['recipient_id'],r['scale'])==(donor,recipient,scale)]
                            if len(compact)!=1: raise ValueError('Missing historical F5 residual row')
                        else:
                            rgb=np.asarray(residual_transfer(r0.tolist(),pixels[method,donor,'C1'].tolist(),pixels[method,donor,'C0'].tolist(),scale),np.uint8)
                            path=out/f'e3-residual-{donor}-{recipient}-{scale}.png'; Image.fromarray(rgb).save(path); rgb=load(path)
                        features=ev.features(rgb,7); latent=ev.reader.latent(rgb)
                        for mode in ('combined','none'):
                            calls[mode]=detect(rgb,method,ALPHA,features,latent,mode)
                            provenance[mode]=dict(kind='retained_pixel_enrichment' if method=='F5' else 'new_call',image=str(path))
                            if method=='F5':
                                oldcall=compact[0]['calls'][mode]
                                if calls[mode]['outcome']!=oldcall['outcome'] or any(calls[mode][tier]['found']!=oldcall[tier+'_found'] for tier in ('semantic','instance')):
                                    raise ValueError('F5 retained-pixel enrichment disagrees with historical compact call')
                    target=targets[method][donor]
                    active.update(status='ok',image=str(path),calls=calls,call_provenance=provenance,
                        payload=target,endpoints={mode:measures(call,target) for mode,call in calls.items()},
                        recipient_quality=ev.metrics(r0,rgb),donor_positive_row=clean_ids[method,donor,'C1'],
                        recipient_sham_row=clean_ids[method,recipient,'C0'])
                    append(active); active=None

        f5geometry={r['id']:r for r in historical_geometry['rows']}
        for oldrow in old5:
            active=dict(id='geometry/'+oldrow['id'],pair_id=oldrow['id'],axis='T5_geometry',
                left=oldrow['left'],right=oldrow['right'],semantic_label=oldrow['semantic_label'],status='running')
            distances={}
            for control in ('C0','C1'):
                for views,name in ((1,'single'),(7,'seven')):
                    a,b=(codes['E3',sid,control,views] for sid in (oldrow['left'],oldrow['right']))
                    distances['E3_'+name+'_'+control] = dict(semantic=(int(a[0],16)^int(b[0],16)).bit_count(),instance=(int(a[1],16)^int(b[1],16)).bit_count())
                distances['v5_'+control]=oldrow['distances_'+control]
                distances['F5_single_'+control]=f5geometry[oldrow['id']]['f4_'+control]
            active.update(status='ok',distances=distances,call_provenance={},
                historical_provenance=dict(v5=str(V5_RESULTS),F5=str(F5_T5)),
                interpretation='component geometry only; all marks alpha; zero distinct-owner pair denominator')
            append(active); active=None
        check(); record['outcome']='completed'
    except Exception:
        error=traceback.format_exc()
        record.update(outcome='failed',error=error)
        failure=active or dict(id='supplement_failure',axis='failure')
        failure.update(status='failed',error=error)
        rows.append(failure)
        with (out/'rows.jsonl').open('a',encoding='utf-8') as h: h.write(json.dumps(failure,allow_nan=False)+'\n')
        write(out/'failure.json',failure)
        raise
    finally:
        record['duration_seconds']=time.monotonic()-STARTED
        record['budget_overrun']=record['duration_seconds']>CAP
        record['summary']=summary(rows,planned)
        if record['outcome']!='completed' or record['budget_overrun']:
            record['summary']['immediate_continuity_pass']=False
        write(out/'summary.json',record['summary']); write(out/'run.json',record)
        # Include ordinary final serialization in the recorded inclusive budget.
        record['duration_seconds']=time.monotonic()-STARTED
        record['budget_overrun']=record['duration_seconds']>CAP
        if record['budget_overrun']: record['summary']['immediate_continuity_pass']=False
        write(out/'summary.json',record['summary']); write(out/'run.json',record)


if __name__=='__main__':
    main()
