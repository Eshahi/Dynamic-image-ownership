"""Descriptive development-only A-C versus retained v5; stdlib, JSON/bytes only."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

VERSION = 'm1-terminal-v5-descriptive-v1'
BASELINE_SHA = '58766c579377f344770887e6cad8bf4ed779ee207c2b6872b4a24ac4a90b9b4d'
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
BASELINE = MAIN / '.thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001/outputs/results.json'
ORIGINAL_IDS = (6012,25394,80932,109798,134882,147498,177015,190676,468505,499768)
EXPANDED_IDS = tuple(sorted((*ORIGINAL_IDS,1675,4795)))
OWNERS = tuple('qim-pilot-owner-'+s for s in ('alpha','beta','gamma','delta'))
RECOMPUTED = 5.243804105290349
DECODED = 8.423231196698145


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path, expected=None):
    path = Path(path)
    if path.suffix != '.json':
        raise ValueError('Only JSON inputs permitted')
    data = path.read_bytes()
    if expected is not None and hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Input SHA-256 mismatch: '+str(path))
    return json.loads(data, parse_constant=lambda s: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def receipt(value):
    return read(value['path'], value['sha256'])


def index(rows):
    result = {}
    for row in rows:
        if row['id'] in result:
            raise ValueError('Duplicate condition ID: '+row['id'])
        result[row['id']] = row
    return result


def selected(control='C1'):
    rows = [dict(id=f'clean-{s}-{control}',axis='clean',source_id=s,control=control,
                 dose=None,strength=None,seed=None) for s in EXPANDED_IDS]
    rows += [dict(id=f'vae-{s}-{control}',axis='T3',source_id=s,control=control,
                  dose='vae_mode',strength=None,seed=None) for s in ORIGINAL_IDS]
    rows += [dict(id=f't3-{s}-{strength}-{seed}-{control}',axis='T3',source_id=s,
                  control=control,dose='diffusion',strength=strength,seed=seed)
             for s in ORIGINAL_IDS for strength in (.1,.2,.4) for seed in (0,1,2)]
    return rows


def finite(x):
    return type(x) in (float,int) and math.isfinite(x)


def candidate_value(row, owner):
    if row is None or row.get('verified') is not True:
        return dict(observed=False,outcome=row.get('input_outcome','missing') if row else 'missing')
    d = row['blind'][owner]
    if not all(finite(d.get(c)) for c in ('s','i')):
        raise ValueError('Verified candidate score nonfinite')
    flags = {c: d[c]>=4 for c in ('s','i')}
    state = ('both_match' if flags['i'] else 'semantic_only') if flags['s'] else (
        'ambiguous_instance_only' if flags['i'] else 'neither_supported')
    if any(type(d['flags'].get(c)) is not bool for c in ('s','i')) or flags != d['flags'] or state != d['state']:
        raise ValueError('Candidate threshold/state parity failed')
    return dict(observed=True,outcome=row['input_outcome'],semantic=flags['s'],instance=flags['i'],
                both=flags['s'] and flags['i'],state=state,scores={c:d[c] for c in ('s','i')},
                quality=row.get('quality_vs_source'),quality_pass=row.get('quality_pass'))


def baseline_value(row, owner):
    if row is None or row.get('detection_complete') is not True:
        return dict(observed=False,outcome=row.get('status','missing') if row else 'missing')
    ds = [d for d in row['detections'] if d.get('claimed_owner')==owner and d.get('binding_mode')=='combined']
    if len(ds)!=1:
        raise ValueError('Baseline combined owner slot inventory differs')
    d = ds[0]['result']
    if d['owners_tested']!=4 or d['binding_mode']!='combined' or d['embedding_domain']!='image':
        raise ValueError('Baseline detector operating metadata differs')
    for c in ('semantic','instance'):
        channel=d[c]
        if channel['recomputed_threshold']!=RECOMPUTED or channel['decoded_threshold']!=DECODED:
            raise ValueError('Baseline threshold differs')
        if type(channel['content_match']) is not bool or type(channel['found']) is not bool:
            raise ValueError('Baseline decisions malformed')
    s,i = d['semantic']['content_match'],d['instance']['content_match']
    if (d['outcome']=='both_match') != (s and i):
        raise ValueError('Baseline both-match parity failed')
    return dict(observed=True,outcome=row['status'],semantic=s,instance=i,both=s and i,
                state=d['outcome'],semantic_found=d['semantic']['found'],instance_found=d['instance']['found'],
                watermark_found=d['watermark_found'],quality=row.get('quality',row.get('quality_source')))


def counts(values):
    observed=[r for r in values if r['observed']]
    outcomes={}
    states={}
    for r in values:
        outcomes[r['outcome']]=outcomes.get(r['outcome'],0)+1
    for r in observed:
        states[r['state']]=states.get(r['state'],0)+1
    return dict(planned=len(values),observed=len(observed),missing_or_adverse=len(values)-len(observed),
                semantic=sum(r['semantic'] for r in observed),instance=sum(r['instance'] for r in observed),
                both=sum(r['both'] for r in observed),outcomes=outcomes,states=states,
                semantic_found=sum(r.get('semantic_found') is True for r in observed) if any('semantic_found' in r for r in observed) else None,
                instance_found=sum(r.get('instance_found') is True for r in observed) if any('instance_found' in r for r in observed) else None,
                watermark_found=sum(r.get('watermark_found') is True for r in observed) if any('watermark_found' in r for r in observed) else None)


def compare_rows(candidate_rows, baseline_rows, schedule, cases):
    candidate,baseline,specs=index(candidate_rows),index(baseline_rows),index(schedule)
    sources={c['id']:c for c in cases}
    source_parity=[]
    for sid in EXPANDED_IDS:
        case=sources.get(sid)
        v=baseline.get(f'clean-{sid}-C0',{})
        a=case.get('source',{}).get('rgb8_sha256') if case else None
        b=v.get('image',{}).get('pixel_sha256')
        status='unavailable' if a is None or b is None else 'equal' if a==b else 'different'
        source_parity.append(dict(source_id=sid,candidate_rgb8_sha256=a,v5_pixel_sha256=b,status=status))
        if status=='different':
            raise ValueError('Canonical source pixel hash mismatch: '+str(sid))
    pairs=[]
    negatives={'candidate':[],'v5':[]}
    for spec in selected():
        if spec['id'] not in specs or any(specs[spec['id']].get(k)!=v for k,v in spec.items()):
            raise ValueError('Selected schedule membership differs: '+spec['id'])
        for table in (candidate,baseline):
            row=table.get(spec['id'])
            if row is not None and any(row.get(k)!=spec[k] for k in ('axis','source_id','control','strength','seed')):
                raise ValueError('Selected row membership differs: '+spec['id'])
        pairs.append(dict(**spec,candidate=candidate_value(candidate.get(spec['id']),OWNERS[0]),
                          v5=baseline_value(baseline.get(spec['id']),OWNERS[0])))
        for control,owners in (('C0',OWNERS),('C1',OWNERS[1:])):
            key=spec['id'][:-2]+control
            for owner in owners:
                negatives['candidate'].append(candidate_value(candidate.get(key),owner))
                negatives['v5'].append(baseline_value(baseline.get(key),owner))
    groups=[]
    for dose,strength in ((None,None),('vae_mode',None),('diffusion',.1),('diffusion',.2),('diffusion',.4)):
        rows=[r for r in pairs if r['dose']==dose and r['strength']==strength]
        both_observed=[r for r in rows if r['candidate']['observed'] and r['v5']['observed']]
        joint={f'candidate_{a}_v5_{b}':sum(r['candidate']['both']==a and r['v5']['both']==b for r in both_observed)
               for a in (False,True) for b in (False,True)}
        groups.append(dict(dose=dose or 'clean',strength=strength,planned=len(rows),
                           source_clusters=len({r['source_id'] for r in rows}),paired_observed=len(both_observed),
                           paired_unavailable=len(rows)-len(both_observed),candidate=counts([r['candidate'] for r in rows]),
                           v5=counts([r['v5'] for r in rows]),descriptive_both_table=joint))
    return dict(groups=groups,rows=pairs,canonical_source_parity=source_parity,
                negative_slots={k:counts(v) for k,v in negatives.items()})


def load_inputs(analysis_path, analysis_sha, baseline_path=BASELINE):
    record=read(analysis_path,analysis_sha)
    if record.get('schema')!='m1-terminal-e2e-threat-analysis-v1' or record.get('data_split')!='development':
        raise ValueError('Expected development terminal threat analysis')
    if record.get('outcome')!='completed' or record.get('errors'):
        raise ValueError('Independent candidate integrity analysis must complete without errors')
    directory=Path(analysis_path).resolve().parent
    actual={p.name:sha(p) for p in directory.iterdir() if p.is_file() and p.name!='run.json'}
    if actual!=record['outputs']:
        raise ValueError('Analysis output hash inventory differs')
    if 'conditions.json' not in actual:
        raise ValueError('Verified conditions absent')
    manifest=receipt(record['manifest'])
    if manifest.get('data_split')!='development' or manifest['schedule'].get('threshold')!=4:
        raise ValueError('Development threshold-4 manifest required')
    if tuple(manifest['schedule']['source_ids'])!=EXPANDED_IDS or tuple(manifest['schedule']['owners'])!=OWNERS:
        raise ValueError('Frozen source/owner inventory differs')
    if tuple(c['id'] for c in manifest['cases'])!=EXPANDED_IDS:
        raise ValueError('Manifest source-case inventory differs')
    for r in record['inputs']:
        receipt(r)  # Retained partition run bytes only; no image or latent is opened.
    for case in manifest['cases']:
        receipt(case['source_run'])
    baseline=read(baseline_path,BASELINE_SHA)
    if len(baseline['rows'])!=617:
        raise ValueError('Pinned baseline row inventory differs')
    rows=read(directory/'conditions.json',actual['conditions.json'])
    if len(rows)!=489 or set(index(rows))!=set(index(manifest['schedule']['conditions'])):
        raise ValueError('Analyzer complete condition inventory differs')
    return record,manifest,rows,baseline


def run(analysis_path, analysis_sha, output):
    started=time.monotonic()
    record,manifest,rows,baseline=load_inputs(analysis_path,analysis_sha)
    result=compare_rows(rows,baseline['rows'],manifest['schedule']['conditions'],manifest['cases'])
    result.update(schema=VERSION,data_split='development',scope='Descriptive exploratory paired source/dose/seed inventory only',
        analysis=dict(path=str(Path(analysis_path).resolve()),sha256=analysis_sha),baseline=dict(path=str(BASELINE),sha256=BASELINE_SHA),
        manifest=record['manifest'],candidate_scientific_complete=record['scientific_complete'],
        operating_points=dict(candidate_threshold=4,v5_recomputed_threshold=RECOMPUTED,v5_decoded_threshold=DECODED,owners_tested=4),
        limitations=['A-C semantic is a continuous score flag; v5 semantic is content_match after discrete decoding/correction.',
                    'The v5 found fields are reported separately and are not content_match.',
                    'Paired source/dose/seed does not imply identical generated or attacked image bytes.',
                    'No equal operating point, superiority, inferential significance, independent-query FPR, or confirmatory claim.',
                    'The three diffusion seeds per source are dependent descriptive observations.',
                    'Human visual verdicts remain missing; quality values are retained inference, not rerun.',
                    'T4/T5 operators and delivery criteria differ across methods and are not pooled in this comparison.',
                    'Strength .05 and the two expanded T3 sources are excluded prospectively from this common subset.'],
        detector_side_information=dict(candidate=['suspect RGB8','public OwnerID','pinned CLIP/VAE models and public profile/maps'],
                                       v5=['suspect RGB8','suspect CLIP feature','public OwnerID','public image-domain codec/profile']))
    output=Path(output).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):
        raise ValueError('Fresh MAIN development output required')
    output.mkdir(parents=True,exist_ok=False)
    dest=output/'comparison.json'
    dest.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    root=Path(__file__).resolve().parents[1]
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    (output/'run.json').write_text(json.dumps(dict(schema=VERSION,data_split='development',outcome='completed',
        commit=commit,command=sys.argv,config=result['operating_points'],seeds=[0,1,2],
        duration_seconds=time.monotonic()-started,analysis=result['analysis'],baseline=result['baseline'],
        code_sha256=sha(Path(__file__)),outputs={'comparison.json':sha(dest)}),indent=2)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--analysis',type=Path,required=True)
    p.add_argument('--analysis-sha256',required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args()
    result=run(a.analysis,a.analysis_sha256,a.output_dir)
    print(json.dumps(result['groups'],allow_nan=False))


if __name__=='__main__':
    main()
