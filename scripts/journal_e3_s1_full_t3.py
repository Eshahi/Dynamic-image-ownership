"""Stage C E3-S1 development panel; conditional on completed Stage B.

CPU helpers recompute native calls. Reused observations are not replication.
No held-out execution, retries, threshold fitting or official gate promotion.
"""
from __future__ import annotations
import time
STARTED = time.monotonic()
import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from journal_e3_threat_supplement import MAIN, IDS, ALPHA, OWNERS, read, write, working_set
from journal_bch_analysis import endpoint

CAP, GPU_CAP, RAM_CAP = 900., 10*1024**3, 16*1024**3
HISTORY = MAIN / '.thesis-build/dev-runs/20261010-1418-e3-full-t3'
NEGATIVES = MAIN / '.thesis-build/dev-runs/20261010-1501-e3-negative-completion'
PLAN = tuple((sid, s, seed) for sid in IDS for s in (.1, .2) for seed in range(3))


def rows_at(path):
    return [json.loads(x) for x in Path(path).read_text(encoding='utf-8-sig').splitlines() if x.strip()]


def identity(row):
    return int(row['source_id']), float(row['strength']), int(row['seed'])


def label(key):
    return f'{key[0]}|{key[1]}|{key[2]}'


def native_endpoint(call, owner, payload=None):
    if (call.get('method') != 'E1-BCH59-A' or call.get('owner_id') != owner or
        call.get('owners_tested') != 1 or call.get('binding_mode') != 'combined' or
        call.get('binding') != 'soft' or not call.get('detector_config_id')):
        raise ValueError('Frozen native source-blind decoder configuration differs')
    return endpoint(call, payload)


def fixed_comparison():
    run = read(HISTORY / 'run.json')
    result = {}
    for strength, n in ((.1, 29), (.2, 28)):
        keys = [tuple(k) for k in run['comparison_sets'][str(strength)]['I']]
        if len(keys) != n or len(set(keys)) != n or not set(keys) <= set(PLAN) or any(k[1] != strength for k in keys):
            raise ValueError('Retained fixed comparison identity set invalid')
        result[str(strength)] = keys
    return result


def summarize(rows, comparison_sets, historical_rows=()):
    """Target values enter only CPU endpoints, after complete detector calls."""
    expected = {(arm, k) for arm in ('candidate_C1', 'shared_C0') for k in PLAN}
    actual = [(r['arm'], identity(r)) for r in rows]
    complete = len(actual) == 144 and set(actual) == expected
    operational, negatives, candidates, unavailable = [], [], {}, []
    full_calls = 0
    for row in rows:
        key, arm, status = identity(row), row['arm'], row.get('status')
        calls = row.get('calls', {})
        if status != 'ok':
            unavailable.append(dict(arm=arm, identity=label(key), status=status, error=row.get('error')))
            if status != 'safety_blocked' or calls:
                operational.append(dict(arm=arm, identity=label(key), reason=status))
        elif set(calls) != set(OWNERS):
            operational.append(dict(arm=arm, identity=label(key), reason='Missing/extra native owner calls'))
        for owner, call in calls.items():
            full_calls += 1
            try:
                e = native_endpoint(call, owner, row.get('payload') if arm == 'candidate_C1' and owner == ALPHA else None)
            except (KeyError, TypeError, ValueError) as exc:
                operational.append(dict(arm=arm, identity=label(key), reason=str(exc), owner=owner))
                continue
            if arm == 'candidate_C1' and owner == ALPHA:
                if status == 'ok': candidates[key] = e
            else:
                negatives.append(dict(arm=arm, identity=label(key), owner=owner, any_detection=e['A']))
    historical = {identity(r):r for r in historical_rows if r.get('arm') == 'candidate_C1'}
    strengths = {}
    for s, n, v5 in ((.1,29,27),(.2,28,18)):
        keys = [k for k in PLAN if k[1] == s]
        fixed = [tuple(k) for k in comparison_sets.get(str(s), [])]
        valid = len(fixed) == len(set(fixed)) == n and set(fixed) <= set(keys)
        successes = {m:sum(bool(candidates.get(k, {}).get(m)) for k in keys) for m in ('S','Q','J','H','F')}
        values = [candidates[k] for k in keys if k in candidates]
        retention = {}
        for m in ('S','Q','J','F'):
            old = {k:endpoint(historical[k]['calls'][ALPHA],historical[k]['payload'])[m]
                   for k in keys if k in historical and historical[k]['status'] == 'ok'}
            retention[m] = dict(observed_historical=len(old),
                lost=[label(k) for k in old if old[k] and not candidates.get(k,{}).get(m)],
                gained=[label(k) for k in old if not old[k] and candidates.get(k,{}).get(m)])
        count = sum(bool(candidates.get(k,{}).get('S')) for k in fixed)
        strengths[str(s)] = dict(planned=36, observed=len(values), successes=successes,
            intersection=dict(fixed_identities=len(fixed), identities=list(map(label,fixed)), candidate_S=count, v5_S=v5),
            comparative_pass=bool(valid and count>v5), historical_retention_descriptive=retention,
            histograms={f:dict(Counter(str(e[f]) for e in values)) for f in ('raw_coded_bit_errors','q_bit_errors','bch_reason')},
            per_source={str(sid):{m:sum(bool(candidates.get((sid,s,seed),{}).get(m)) for seed in range(3))
                for m in ('S','Q','J','F')} for sid in IDS})
    blocked = sum(r.get('status') == 'safety_blocked' for r in rows)
    negative_blocked = sum((4 if r['arm'] == 'shared_C0' else 3) for r in rows if r.get('status') == 'safety_blocked')
    detections = sum(n['any_detection'] for n in negatives)
    accounted = len(negatives)+negative_blocked == 504
    passed = bool(complete and not operational and accounted and full_calls == 576-4*blocked and
                  not detections and all(v['comparative_pass'] for v in strengths.values()))
    return dict(planned_image_rows=144, recorded_image_rows=len(rows), complete=complete,
        planned_full_calls=576, observed_full_calls=full_calls, planned_negative_calls=504,
        observed_negative_calls=len(negatives), unavailable_negative_calls=negative_blocked,
        negative_accounted=accounted, negative_any_detections=detections, negative_calls=negatives,
        safety_blocked_image_rows=blocked, unavailable_rows=unavailable, operational_failures=operational,
        strengths=strengths, scientific_stage_c_pass=passed, m1a_pass=False,
        interpretation='E3-A1 disclosed safety missingness; Q/J/F, raw errors and retention are descriptive, not extra E3-B gates. T4/T5 pending. Reused calls are not independent replication.')


def validate_finished(path):
    """Final records only; parent wall must certify inclusive time before passage."""
    path = Path(path); run = read(path/'run.json')
    if run.get('schema') != 'journal-e3-s1-stage-c-v1' or run.get('outcome') not in ('completed','failed'):
        raise ValueError('Finished Stage C required')
    saved = read(path/'summary.json')
    computed = summarize(rows_at(path/'rows.jsonl'),run['comparison_sets'],rows_at(HISTORY/'rows.jsonl'))
    if saved != run.get('summary') or saved != computed:
        raise ValueError('Recorded native-call summary differs')
    wall = read(path/'parent-wall.json')
    seconds = wall.get('parent_inclusive_seconds',wall.get('duration_seconds'))
    cap_pass = bool(isinstance(seconds,(int,float)) and 0<seconds<=CAP and
        run.get('peak_allocated_bytes',GPU_CAP+1)<=GPU_CAP and run.get('peak_ram_bytes',RAM_CAP+1)<=RAM_CAP and
        not run.get('budget_overrun'))
    return computed, dict(run, stage_c_pass_recomputed=bool(cap_pass and run['outcome']=='completed' and
        run.get('stage_b_validated') is True and computed['scientific_stage_c_pass']), cap_pass=cap_pass)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('stage-b-dir','stage-a-dir','output-dir'): p.add_argument('--'+name,type=Path,required=True)
    args = p.parse_args()
    from journal_e3_s1_full_writer import validate_stage_b
    source_rows, stage_b = validate_stage_b(args.stage_b_dir)
    if Path(stage_b['ancestry']['stage_a']).resolve()!=args.stage_a_dir.resolve():
        raise ValueError('Stage C must reuse the exact Stage A ancestry validated by B')
    stage_a = read(args.stage_a_dir/'run.json')
    if stage_a.get('outcome') != 'completed' or stage_a.get('stage_a_pass') is not True:
        raise ValueError('Final passing Stage A required')
    if len(source_rows)!=12 or {r['source_id'] for r in source_rows}!=set(IDS):
        raise ValueError('All twelve fixed Stage B sources required')
    selected = {r['source_id']:r for r in source_rows}
    inherited = rows_at(args.stage_a_dir/'t3-rows.jsonl')
    expected_a = {(sid,s,seed) for sid in (6012,147498) for s in (.1,.2) for seed in range(3)}
    if len(inherited)!=12 or {identity(r) for r in inherited}!=expected_a:
        raise ValueError('Exact twelve Stage A T3 identities required')
    for row in inherited:
        if row['payload'] != selected[row['source_id']]['payload']:
            raise ValueError('Stage A and B S1 targets differ')
    c0 = [r for r in rows_at(NEGATIVES/'rows.jsonl') if r['arm']=='shared_C0']
    if len(c0)!=72 or {identity(r) for r in c0}!=set(PLAN):
        raise ValueError('Complete unchanged C0 inventory required')
    comparison = fixed_comparison(); historical = rows_at(HISTORY/'rows.jsonl')
    rows = []
    for row in c0+inherited:
        r = copy.deepcopy(row)
        r['arm'] = row.get('arm','candidate_C1')
        r['reuse_provenance'] = dict(record=str((NEGATIVES if r['arm']=='shared_C0' else args.stage_a_dir)/
            ('rows.jsonl' if r['arm']=='shared_C0' else 't3-rows.jsonl')), identity=label(identity(r)),
            scope='Exact development observation inherited once; not independent replication')
        rows.append(r)
    for key in PLAN:
        if key not in expected_a:
            rows.append(dict(arm='candidate_C1',source_id=key[0],strength=key[1],seed=key[2],
                payload=selected[key[0]]['payload'],status='not_started',calls={}))
    preexisting = [r for r in rows if r.get('reuse_provenance')]
    check = summarize(preexisting,comparison)
    if check['operational_failures'] or check['negative_any_detections']:
        raise ValueError('Inherited calls invalid or negative detection observed')
    out = args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=False)
    (out/'images').mkdir()
    record = dict(schema='journal-e3-s1-stage-c-v1',method='E3-S1+E3-BCH59-Q080',
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=sys.argv,
        data_split='development',usd=0,sources=list(IDS),seeds=[0,1,2],outcome='running',stage_b_validated=True,
        ancestry=dict(stage_b=str(args.stage_b_dir),stage_a=str(args.stage_a_dir),c0=str(NEGATIVES),historical=str(HISTORY)),
        comparison_sets=comparison,inherited_image_rows=84,fresh_planned_image_rows=60,
        config=dict(cap_seconds=CAP,gpu_cap_bytes=GPU_CAP,ram_cap_bytes=RAM_CAP,
            strengths=[.1,.2],steps=20,scheduler='DDIM',prompt='',negative_prompt='',guidance_scale=1.,eta=0.,
            safety_checker=True,semantic_views=7,binding='soft',binding_mode='combined',roster_size=1,
            protocol='research/journal-upgrade-20261009/e3-s1-full-development.md'),m1a_pass=False)
    ev = None
    def budget():
        rss, peak = working_set(); record['peak_ram_bytes']=max(rss,peak,record.get('peak_ram_bytes',0))
        gpu = int(ev.torch.cuda.max_memory_allocated()) if ev else 0
        record['peak_allocated_bytes']=max(gpu,record.get('peak_allocated_bytes',0))
        if time.monotonic()-STARTED>=CAP or gpu>GPU_CAP or record['peak_ram_bytes']>RAM_CAP:
            raise RuntimeError('Stage C inclusive resource cap exceeded')
    def save():
        (out/'rows.jsonl').write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in rows),encoding='utf-8')
        record['duration_seconds']=time.monotonic()-STARTED
        record['budget_overrun']=record['duration_seconds']>CAP
        record['summary']=summarize(rows,comparison,historical)
        record['stage_c_pass']=bool(record['outcome']=='completed' and not record['budget_overrun'] and
            record['summary']['scientific_stage_c_pass'])
        write(out/'run.json',record); write(out/'summary.json',record['summary'])
    save()
    try:
        budget()
        import numpy as np
        import torch
        import diffusers
        from PIL import Image
        from f4_transfer_probe import ASSETS
        from journal_vae_probe import Evaluator
        from journal_e3_s1_probe import official_kwargs
        from journal_bch_readout import detect_rgb
        import three_threat_models as models
        if diffusers.__version__!='0.35.1': raise ValueError('Pinned diffusers required')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/torch.cuda.get_device_properties(0).total_memory)
        ev=Evaluator(); budget()
        if ev.profile != stage_b['config']['profile']:
            raise ValueError('Stage C reader profile differs from frozen Stage B')
        pipe=models.load_regenerator(ASSETS); budget()
        if pipe.safety_checker is None or pipe.feature_extractor is None:
            raise RuntimeError('Official safety checker required')
        record['environment']=dict(torch=torch.__version__,diffusers=diffusers.__version__,gpu=torch.cuda.get_device_name(0))
        record['config']['profile']=ev.profile
        def load(path):
            with Image.open(path) as image:
                if image.mode!='RGB' or image.size!=(512,512): raise ValueError('RGB8 512x512 required')
                return np.asarray(image,dtype=np.uint8).copy()
        for r in rows:
            if r['status']!='not_started': continue
            budget(); r['status']='running'; save(); tick=time.monotonic()
            try:
                marked_path=selected[r['source_id']]['conditions']['clean']['image']
                r['marked_input']=str(marked_path); marked=load(marked_path)
                with torch.inference_mode():
                    output=pipe(**official_kwargs(r['strength'],r['seed'],Image.fromarray(marked),torch.Generator))
                steps,_=pipe.get_timesteps(20,r['strength'],pipe._execution_device)
                r['timesteps']=steps.cpu().tolist()
                if len(r['timesteps'])!=int(20*r['strength']): raise ValueError('Official effective timesteps differ')
                budget()
                # Preserve the actual returned checker output, even if blocked.
                r['safety_flags']=list(output.nsfw_content_detected) if output.nsfw_content_detected is not None else None
                raw=out/'images'/f"raw-{label(identity(r)).replace('|','-')}.png"
                output.images[0].save(raw); r['raw_output_image']=str(raw)
                image=models.validate_generated(output)
                path=out/'images'/f"C1-{label(identity(r)).replace('|','-')}.png"
                image.save(path); r['image']=str(path); rgb=load(path)
                budget(); features,latent=ev.features(rgb,7),ev.reader.latent(rgb); budget()
                for owner in OWNERS:
                    budget()
                    call=detect_rgb(rgb,latent,owner,ev.profile,features,binding='soft',binding_mode='combined',roster_size=1)
                    r['calls'][owner]=call
                    r.setdefault('endpoints',{})[owner]=native_endpoint(call,owner,r['payload'] if owner==ALPHA else None)
                r['quality_marked']=ev.metrics(marked,rgb); budget(); r['status']='ok'
            except Exception as exc:
                r['error']=f'{type(exc).__name__}: {exc}'
                # Only the official validator's explicit checker rejection is safety missingness.
                if isinstance(exc,RuntimeError) and str(exc)=='safety_checker_blocked_output' and not r['calls'] and r.get('safety_flags')==[True]:
                    r['status']='safety_blocked'
                else:
                    r['status']='failed'; raise
            finally:
                r['duration_seconds']=time.monotonic()-tick; save()
            print(json.dumps(dict(identity=label(identity(r)),status=r['status'])),flush=True)
        budget(); record['outcome']='completed'
    except Exception as exc:
        record.update(outcome='failed',error=f'{type(exc).__name__}: {exc}',traceback=traceback.format_exc())
    finally:
        save()
    if record['outcome']=='failed': raise SystemExit(1)


if __name__=='__main__':
    main()
