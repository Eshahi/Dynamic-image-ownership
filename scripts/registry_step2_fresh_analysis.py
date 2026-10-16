"""Freeze registry thresholds on 20 calibration sources, then evaluate 40 fresh sources.

Calibration and evaluation are separate invocations. Evaluation never changes
the selected descriptor or thresholds. Registry records are split-local clean
publications; real near-duplicate pairs form an additional explicit 1:1 panel.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT),str(ROOT/'scripts')]
from registry_step1_transfer import ALPHA,BETA,MAIN,STRENGTHS,SEEDS,journal,read,write
from registry_step2_screen import DescriptorCache,DESCRIPTORS,identify,pointer,distance
from m1b_e3_s1_analysis import clustered_negative


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',choices=('calibrate','evaluate'),required=True)
    p.add_argument('--fresh-dir',type=Path,required=True)
    p.add_argument('--near-duplicates',type=Path,required=True,help='Acquired receipt with pairs/selected rows, split,left_path,right_path')
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--parent-spent-seconds',type=float,required=True,help='All other step2 time; exclude this analysis run')
    p.add_argument('--max-seconds',type=float,default=14400.)
    a = p.parse_args()
    if not 0 < a.max_seconds <= 14400 or a.parent_spent_seconds < 0:
        raise ValueError('Four-hour step2 cumulative cap required')
    fresh = read(a.fresh_dir/'run.json')
    if fresh['data_split'] != 'development':
        raise ValueError('Fresh development input required')
    method = fresh['config']['chosen_method']
    chosen = fresh['config']['selected_descriptor']
    if chosen not in ('D1','D2'):
        raise ValueError('Use the descriptor already selected by step2a')
    cohort = fresh['sources']
    if len(cohort) != 60 or sum(s['registry_split'] == 'calibration' for s in cohort) != 20 or sum(s['registry_split'] == 'evaluation' for s in cohort) != 40:
        raise ValueError('Frozen20/40 split required')
    near = read(a.near_duplicates)
    pairs = near if isinstance(near,list) else near.get('pairs',near.get('selected'))
    if len(pairs) < 20 or sum(p['split'] == 'calibration' for p in pairs) < 7 or sum(p['split'] == 'evaluation' for p in pairs) < 13:
        raise ValueError('At least7 calibration and13 evaluation real near-duplicate pairs required')
    split = 'calibration' if a.phase == 'calibrate' else 'evaluation'
    sources = sorted((s for s in cohort if s['registry_split'] == split),key=lambda s:s['source_id'])
    split_pairs = [p for p in pairs if p['split'] == split]
    if any(not p.get('left_path') or not p.get('right_path') for p in split_pairs):
        raise ValueError('Real near-duplicate images must be acquired, registered and decoded first')
    out = a.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    (out/'images').mkdir(exist_ok=True)
    commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    config = dict(fresh_dir=str(a.fresh_dir.resolve()),fresh_commit=fresh['commit'],chosen_method=method,selected_descriptor=chosen,
        near_duplicates=str(a.near_duplicates.resolve()),source_order=[s['source_id'] for s in cohort],
        threshold='nextafter(maximum calibration negative,+inf); accept cosine>=tau',registry='split-local clean published images',
        side_information='trusted owner/record lookup and stored continuous descriptors',cap_seconds=a.max_seconds,
        human_admissibility='missing',negative_scope='ordered wrong-source, q-nearest subset, residualT4, real near-duplicate1:1')
    record = read(out/'run.json') if (out/'run.json').exists() else dict(schema='registry-fresh-analysis-v1',commit=commit,config=config,
        data_split='development',usd=0,duration_seconds=0.,invocations=[],outcome='running')
    if record['commit'] != commit or record['config'] != config:
        raise ValueError('Resume code/config differs')
    frozen_path = out/'calibration-thresholds.json'
    if a.phase == 'evaluate' and not frozen_path.exists():
        raise ValueError('Commit-independent frozen calibration artifact must exist before evaluation')
    if a.phase == 'calibrate' and frozen_path.exists():
        raise ValueError('Calibration thresholds already frozen; cannot refit')
    prior = record['duration_seconds']
    started = time.monotonic()
    invocation = dict(phase=a.phase,command=sys.argv,status='running',other_step2_seconds=a.parent_spent_seconds)
    record['invocations'].append(invocation)
    log = out/'calls.jsonl'
    if log.exists() and log.stat().st_size and not log.read_bytes().endswith(b'\n'):
        raw = log.read_bytes(); end = raw.rfind(b'\n')+1
        (out/f'interrupted-tail-{time.time_ns()}.bin').write_bytes(raw[end:])
        log.write_bytes(raw[:end])
    local,inputs = journal(log),journal(a.fresh_dir/'rows.jsonl')
    def save():
        record['duration_seconds'] = prior+time.monotonic()-started
        record['step2_accounted_seconds'] = record['duration_seconds']+a.parent_spent_seconds
        invocation['duration_seconds'] = time.monotonic()-started
        write(out/'run.json',record)
    def budget():
        if prior+time.monotonic()-started+a.parent_spent_seconds >= a.max_seconds:
            raise TimeoutError('Four-hour cumulative step2 budget reached')
    def emit(row):
        with log.open('a',encoding='utf-8') as handle:
            handle.write(json.dumps(row,allow_nan=False)+'\n'); handle.flush()
        local[row['id']] = row
        save()
    save()
    try:
        budget()
        import numpy as np
        import torch
        from PIL import Image
        from journal_vae_probe import Evaluator
        from journal_bch_readout import detect_rgb as e3_detect
        from three_threat_protocol import residual_transfer
        import three_threat_models as models
        models.block_network(); torch.set_num_threads(4)
        ev = Evaluator()
        radius = int(ev.profile['decision']['semantic_radius'])
        cache = DescriptorCache(out,ev,ev.profile,MAIN/'.thesis-build/assets/freqmark-reconstruction-20261013/dino',budget)
        ids = [s['source_id'] for s in sources]
        source_index = {s['source_id']:s for s in sources}
        records = []
        missing = []
        for sid in ids:
            clean = inputs.get(f'clean:{sid}:{method}:C1',{})
            records.append(dict(record_id=f'{method}:{sid}',source_id=sid,owner=ALPHA,
                q=clean.get('payload',{}).get('q'),h=clean.get('payload',{}).get('h'),image=clean.get('image') if clean.get('status') == 'ok' else None))
            if records[-1]['image'] is None:
                missing.append(dict(id=records[-1]['record_id'],reason='clean registry enrollment unavailable'))
        if any(r['q'] is None for r in records):
            raise ValueError('Registry enrollment incomplete; retain construction failure and do not report a full registry')
        targets = {r['source_id']:r for r in records}
        def rgb(path):
            with Image.open(path) as im:
                return np.asarray(im.convert('RGB'),np.uint8).copy()
        def detect(path):
            budget(); x = rgb(path)
            features,z = ev.features(x,7),ev.reader.latent(x)
            return {o:(e3_detect(x,z,o,ev.profile,features,binding='soft',roster_size=1) if method == 'e3-s1'
                       else ev.detect(x,'f5',o,features,z)) for o in (ALPHA,BETA)}
        def cosine(path,ref,descriptor):
            if not path or not ref:
                return None
            aa,bb = cache.get(path)[descriptor],cache.get(ref)[descriptor]
            return None if aa is None or bb is None else float(np.dot(aa,bb))
        observations = []
        for sid in ids:
            for phase in ('clean','sd15','sd21'):
                cells = [(None,None)] if phase == 'clean' else [(s,seed) for s in STRENGTHS for seed in SEEDS]
                for strength,seed in cells:
                    for control in ('C0','C1'):
                        rid = f'clean:{sid}:{method}:{control}' if phase == 'clean' else f'{phase}:{sid}:{strength}:{seed}:{"C0" if control == "C0" else method}'
                        row = inputs.get(rid,{})
                        calls = row.get('calls',{}) if phase == 'clean' else row.get('readouts',{}).get(method,{}).get('calls',{})
                        observations.append(dict(id=rid,phase=phase,source_id=sid,strength=strength,seed=seed,control=control,
                            image=row.get('image'),calls=calls,status=row.get('status','missing')))
        transfers = []
        for i,sid in enumerate(ids):
            recipient = ids[(i+1)%len(ids)]
            for scale in (.5,1.):
                rid = f'T4:{split}:{sid}:{recipient}:{scale}'
                if local.get(rid,{}).get('status') != 'ok':
                    budget()
                    image = out/'images'/(rid.replace(':','-')+'.png')
                    x = residual_transfer(rgb(source_index[recipient]['canonical_path']).tolist(),rgb(targets[sid]['image']).tolist(),
                                          rgb(source_index[sid]['canonical_path']).tolist(),scale)
                    Image.fromarray(np.asarray(x,np.uint8)).save(image)
                    emit(dict(id=rid,status='ok',image=str(image),source_id=sid,recipient_id=recipient,scale=scale,calls=detect(image)))
                transfers.append(local[rid])
        for pair in split_pairs:
            rid = f'near:{pair["pair_id"]}'
            if local.get(rid,{}).get('status') != 'ok':
                emit(dict(id=rid,status='ok',left_path=pair['left_path'],right_path=pair['right_path'],calls=detect(pair['right_path']),
                          reference_calls=detect(pair['left_path'])))
        # Descriptor cache is resumable; evaluation paths are never opened in calibration.
        paths = {r['image'] for r in records if r['image']}
        paths |= {o['image'] for o in observations if o['status'] == 'ok' and o.get('image')}
        paths |= {t['image'] for t in transfers}
        paths |= {p[k] for p in split_pairs for k in ('left_path','right_path')}
        for i,path in enumerate(sorted(paths)):
            cache.get(path)
            if i%25 == 0:
                write(out/f'descriptor-index-{split}.json',cache.index); save()
        write(out/f'descriptor-index-{split}.json',cache.index)
        summaries,thresholds = {},{}
        frozen = read(frozen_path) if a.phase == 'evaluate' else None
        # Descriptor selection is inherited, never repeated on fresh data.
        for descriptor in DESCRIPTORS:
            negatives,outcomes = [],[]
            desc_missing = list(missing)
            for obs in observations:
                scores = [cosine(obs['image'],r['image'],descriptor) for r in records] if obs['status'] == 'ok' else [None]*len(records)
                nearest = min((sid for sid in ids if sid != obs['source_id']),key=lambda sid:(distance(targets[obs['source_id']]['q'],targets[sid]['q']),sid))
                carried = pointer(obs['calls'].get(ALPHA))
                outcomes.append(dict(**obs,scores=scores,pointer=carried))
                for rec,score in zip(records,scores):
                    if rec['source_id'] == obs['source_id']:
                        continue
                    eligible = carried['recovered'] and distance(carried['q'],rec['q']) <= radius
                    negatives.append(dict(id=obs['id'],source_cluster=f'source:{obs["source_id"]}',family='wrong_source',
                        target=rec['record_id'],score=score,pointer_candidate=eligible,q_nearest=rec['source_id'] == nearest,
                        expected_safety_blocked=obs['status'] == 'safety_blocked'))
            for t in transfers:
                carried = pointer(t['calls'][ALPHA]); rec = targets[t['source_id']]
                negatives.append(dict(id=t['id'],source_cluster=f'source:{t["source_id"]}',family='T4',target=rec['record_id'],
                    score=cosine(t['image'],rec['image'],descriptor),pointer_candidate=carried['recovered'] and distance(carried['q'],rec['q']) <= radius))
            for pair in split_pairs:
                row = local[f'near:{pair["pair_id"]}']; carried = pointer(row['calls'][ALPHA])
                q = row['reference_calls'][ALPHA]['semantic_code']
                negatives.append(dict(id=row['id'],source_cluster=f'near:{pair["pair_id"]}',family='real_near_duplicate',
                    score=cosine(pair['right_path'],pair['left_path'],descriptor),pointer_candidate=carried['recovered'] and distance(carried['q'],q) <= radius))
            finite = [r['score'] for r in negatives if r['score'] is not None]
            if a.phase == 'calibrate':
                if any(r['score'] is None and not r.get('expected_safety_blocked') for r in negatives) or not finite:
                    raise ValueError('Calibration has genuine missing negative execution/descriptors; no threshold may be frozen')
                # Pinned safety-blocked attempts have no image; their negatives
                # remain unresolved. Fit only observed negatives, as in 2a.
                tau = float(np.nextafter(max(finite),np.inf))
            else:
                tau = frozen['descriptors'][descriptor]['tau']
            thresholds[descriptor] = dict(tau=tau,calibration_max_negative=max(finite) if a.phase == 'calibrate' else frozen['descriptors'][descriptor]['calibration_max_negative'])
            lookup = dict(seconds=0.,calls=0)
            for obs in outcomes:
                tick = time.monotonic()
                obs['registry'] = identify(obs['scores'],records,tau,obs['pointer'],radius)
                obs['fingerprint'] = identify(obs['scores'],records,tau)
                lookup['seconds'] += time.monotonic()-tick; lookup['calls'] += 2
                target = f'{method}:{obs["source_id"]}'
                obs['F_R'] = obs['registry']['accepted'] and obs['registry']['record_id'] == target
                obs['fingerprint_correct'] = obs['fingerprint']['accepted'] and obs['fingerprint']['record_id'] == target
                obs['execution_unknown'] = obs['status'] not in ('ok','safety_blocked') or (obs['status'] == 'ok' and any(v is None for v in obs['scores']))
            for row in negatives:
                row['descriptor_accept'] = None if row['score'] is None else row['score'] >= tau
                row['F_R_false_accept'] = None if row['score'] is None else bool(row['pointer_candidate'] and row['score'] >= tau)
            cells = {}
            for model in ('sd15','sd21'):
                for strength in STRENGTHS:
                    group = [o for o in outcomes if o['control'] == 'C1' and o['phase'] == model and o['strength'] == strength]
                    cells[f'{model}/{strength}'] = dict(planned_seeds=len(ids)*3,observed=sum(o['status'] == 'ok' for o in group),
                        seed_F_R=sum(o['F_R'] for o in group),seed_fingerprint_correct=sum(o['fingerprint_correct'] for o in group),
                        source_majority_F_R=sum(sum(o['F_R'] for o in group if o['source_id'] == sid)>=2 for sid in ids),
                        source_majority_upper=sum(sum(o['F_R'] or o['execution_unknown'] for o in group if o['source_id'] == sid)>=2 for sid in ids),
                        source_majority_fingerprint=sum(sum(o['fingerprint_correct'] for o in group if o['source_id'] == sid)>=2 for sid in ids),
                        source_denominator=len(ids),safety_blocked=sum(o['status'] == 'safety_blocked' for o in group),
                        execution_unknown=sum(o['execution_unknown'] for o in group),candidate_counts=[o['registry']['candidates'] for o in group])
                    cells[f'{model}/{strength}']['TPR_seed'] = cells[f'{model}/{strength}']['seed_F_R']/(len(ids)*3)
                    cells[f'{model}/{strength}']['TPR_source_majority'] = cells[f'{model}/{strength}']['source_majority_F_R']/len(ids)
                    cells[f'{model}/{strength}']['old_F_seed'] = sum(o['calls'].get(ALPHA,{}).get('outcome') == 'both_match' for o in group)
                    cells[f'{model}/{strength}']['old_F_source_majority'] = sum(sum(o['calls'].get(ALPHA,{}).get('outcome') == 'both_match' for o in group if o['source_id'] == sid)>=2 for sid in ids)
            families = {}
            for family in ('wrong_source','q_nearest','T4','real_near_duplicate'):
                subset = [r for r in negatives if r.get('q_nearest')] if family == 'q_nearest' else [r for r in negatives if r['family'] == family]
                clusters = defaultdict(list); fp_clusters = defaultdict(list)
                for row in subset:
                    clusters[row['source_cluster']].append(row['F_R_false_accept'])
                    fp_clusters[row['source_cluster']].append(row['descriptor_accept'])
                families[family] = dict(planned=len(subset),observed=sum(r['score'] is not None for r in subset),
                    registry_false_accepts=sum(r['F_R_false_accept'] is True for r in subset),fingerprint_false_accepts=sum(r['descriptor_accept'] is True for r in subset),
                    registry_source_clustered=clustered_negative(list(clusters.values())),fingerprint_source_clustered=clustered_negative(list(fp_clusters.values())))
            c0_clusters = [[o['registry']['accepted'] if o['status'] == 'ok' else None for o in outcomes if o['source_id'] == sid and o['control'] == 'C0'] for sid in ids]
            primary_cells = [cells[f'{m}/0.2'] for m in ('sd15','sd21')]
            observed_fa = sum(r['F_R_false_accept'] is True for r in negatives)+sum(o['registry']['accepted'] for o in outcomes if o['control'] == 'C0')
            complete = all(r['score'] is not None or r.get('expected_safety_blocked') for r in negatives) and not any(o['execution_unknown'] for o in outcomes)
            passed = complete and observed_fa == 0 and all(c['source_majority_F_R'] >= (18 if split == 'calibration' else 36) for c in primary_cells)
            summaries[descriptor] = dict(tau=tau,cells=cells,negative_families=families,observed_false_accepts=observed_fa,
                C0_source_clustered=clustered_negative(c0_clusters),complete=complete,development_pass=passed,
                unresolved_safety_blocked_negative_comparisons=sum(r['score'] is None and r.get('expected_safety_blocked',False) for r in negatives),
                false_positive_scope='Observed calls only; safety-blocked negative comparisons remain unresolved.',
                registry_N=len(records),descriptor_bytes=sum(cache.get(r['image'])[descriptor].nbytes for r in records if cache.get(r['image'])[descriptor] is not None),
                lookup_timing=lookup,zero_wrong_owner_accepts_reason='No beta records enrolled; this is not evidence of arbitrary-owner security',
                interval_scope='hypothetical exchangeable source/pair clusters; fixed development cohort does not establish population FPR')
            write(out/f'{split}-{descriptor}-scores.json',dict(positives_and_C0=outcomes,negatives=negatives))
        if a.phase == 'calibrate':
            budget()
            write(frozen_path,dict(schema='registry-fresh-calibration-thresholds-v1',commit=commit,chosen_method=method,
                selected_descriptor=chosen,source_ids=ids,near_duplicate_ids=[p['pair_id'] for p in split_pairs],
                descriptors=thresholds,rule='calibration negatives only; nextafter(max,+inf), inclusive acceptance >=tau'))
        record[split] = dict(descriptors=summaries,selected_descriptor=chosen,primary=summaries[chosen],
                             descriptor_extraction_metrics=getattr(cache,'metrics',None))
        record['outcome'] = 'calibrated' if a.phase == 'calibrate' else ('development_pass' if summaries[chosen]['development_pass'] else 'development_fail_or_incomplete')
        invocation['status'] = 'completed'
    except Exception:
        invocation.update(status='incomplete',error=traceback.format_exc()); record['outcome'] = 'incomplete'
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
