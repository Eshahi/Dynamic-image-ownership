"""Metadata-only descriptive aggregation of a fixed dual-threat assessment.

No model/image access, threshold fitting or eligibility filtering. Incomplete
source receipts and every missing planned condition remain visible.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_assess_dual_threats as assessor

VERSION='m1-dual-threat-analysis-v1'

def flat(value,prefix=''):
    result={}
    for key,item in value.items():
        name=prefix+key
        if isinstance(item,dict): result.update(flat(item,name+'_'))
        elif isinstance(item,list): result[name]=json.dumps(item,sort_keys=True)
        else: result[name]=item
    return result

def finite_number(value):
    return type(value) in (int,float) and math.isfinite(value)

def quality_valid(q,include_clip=False):
    if not isinstance(q,dict): return None
    psnr=q.get('psnr_db');ssim=q.get('ssim_rgb');lpips=q.get('lpips')
    flag=q.get('psnr_infinite',False)
    if type(flag) is not bool: return False
    if not ((flag is True and psnr is None) or (flag is False and finite_number(psnr))): return False
    if not finite_number(ssim) or not finite_number(lpips): return False
    if include_clip and not finite_number(q.get('clip_cosine')): return False
    if 'mse_rgb8' in q and not finite_number(q['mse_rgb8']): return False
    return True

def quality_pass(q):
    if not quality_valid(q): return None
    psnr=q.get('psnr_db');ssim=q['ssim_rgb'];lpips=q['lpips']
    return (q.get('psnr_infinite') is True or psnr>35) and ssim>.9 and lpips<.1

def record_complete(spec,row):
    if row.get('outcome')!='completed': return False
    if spec['axis']=='T5':
        components=row.get('components')
        if not isinstance(components,dict) or set(components)!={'C0','C1'}: return False
        for value in components.values():
            if not isinstance(value,dict): return False
            for field in ('semantic_hamming','instance_hamming'):
                if type(value.get(field)) is not int or not 0<=value[field]<=32: return False
            if not finite_number(value.get('clip_cosine')): return False
        return True
    detections=row.get('detections')
    if not isinstance(detections,list) or len(detections)!=4: return False
    if any(not isinstance(d,dict) or not isinstance(d.get('owner'),str) for d in detections): return False
    if sorted(d.get('owner','') for d in detections)!=sorted(assessor.v5.OWNERS): return False
    for d in detections:
        r=d.get('result')
        if not finite_number(d.get('seconds')) or d['seconds']<0 or not isinstance(r,dict): return False
        if not all(isinstance(r.get(k),str) and r[k] for k in ('outcome','proposal_state','qualified_state')): return False
        for channel in ('semantic','instance'):
            c=r.get(channel)
            if not isinstance(c,dict) or any(type(c.get(k)) is not bool for k in ('found','content_match')): return False
    if not finite_number(row.get('suspect_clip_seconds')) or row['suspect_clip_seconds']<0: return False
    if spec['axis']=='T3' and (not finite_number(row.get('attack_seconds')) or row['attack_seconds']<0): return False
    if 'attack_seconds' in row and not finite_number(row['attack_seconds']): return False
    required=['quality_vs_same_arm_original','quality_vs_source']
    if spec['axis']=='clean' and spec.get('control')=='C1': required+=['paired_family_quality','source_preservation_quality']
    return all(quality_valid(row.get(k),include_clip=True) for k in required)

def detector_row(row):
    out={}
    for owner in assessor.v5.OWNERS:
        entries=row.get('detections',[])
        matches=[d for d in entries if isinstance(d,dict) and d.get('owner')==owner] if isinstance(entries,list) else []
        tag='correct' if owner==assessor.v5.OWNERS[0] else 'wrong_'+owner.rsplit('-',1)[-1]
        if len(matches)!=1 or not isinstance(matches[0].get('result'),dict):
            out[tag+'_missing']=True;continue
        d=matches[0];r=d['result'];out[tag+'_missing']=False
        for field in ('outcome','proposal_state','qualified_state'):
            value=r.get(field)
            out[tag+'_'+field]=value if isinstance(value,str) else None
            if value is not None and not isinstance(value,str):out[tag+'_'+field+'_malformed']=repr(value)
        out[tag+'_seconds']=d.get('seconds')
        for channel in ('semantic','instance'):
            value=r.get(channel,{})
            for field in ('content_match','found'):
                result=value.get(field) if isinstance(value,dict) else None
                out[tag+'_'+channel+'_'+field]=result if type(result) is bool else None
    return out

def tables(expected,actual):
    """Return denominator-complete raw and grouped descriptive tables."""
    raw=[];groups={};errors=[]
    byid={}
    for row in actual:
        if not isinstance(row,dict) or not isinstance(row.get('id'),str):
            errors.append('Malformed source condition');continue
        if row['id'] in byid: errors.append('Duplicate latest condition: '+row['id'])
        else: byid[row['id']]=row
    expected_ids={r['id'] for r in expected}
    for ident in sorted(set(byid)-expected_ids): errors.append('Unplanned condition: '+ident)
    for spec in expected:
        row=byid.get(spec['id'],{})
        if any(row.get(k,v)!=v for k,v in spec.items()):
            errors.append('Condition metadata mismatch: '+spec['id']);row={}
        out=dict(spec,source_outcome=row.get('outcome','missing_condition'),human_visual_verdict=None)
        out.update(detector_row(row))
        for name in ('paired_family_quality','source_preservation_quality','quality_vs_same_arm_original','quality_vs_source'):
            q=row.get(name)
            out[name+'_conjunction']=quality_pass(q)
            if isinstance(q,dict): out.update(flat(q,name+'_'))
        if isinstance(row.get('components'),dict): out.update(flat(row['components'],'components_'))
        if isinstance(row.get('same_instance_component_drift'),dict): out.update(flat(row['same_instance_component_drift'],'drift_'))
        out['attack_seconds']=row.get('attack_seconds');out['suspect_clip_seconds']=row.get('suspect_clip_seconds')
        out['error']=row.get('error')
        out['assessment_record_complete']=record_complete(spec,row)
        semantic=out.get('correct_semantic_content_match')
        qok=out.get('quality_vs_same_arm_original_conjunction')
        clip=out.get('quality_vs_same_arm_original_clip_cosine')
        out['semantic_match_and_same_arm_quality']=None if semantic is None or qok is None else bool(semantic and qok)
        out['semantic_match_and_clip085_exploratory']=None if semantic is None or not finite_number(clip) else bool(semantic and clip>=.85)
        raw.append(out)
        key=tuple(spec.get(k) for k in ('axis','control','dose','strength','arm','scale','semantic_label'))
        groups.setdefault(key,[]).append(out)
    summary=[]
    bool_fields=['paired_family_quality_conjunction','source_preservation_quality_conjunction',
        'quality_vs_same_arm_original_conjunction','semantic_match_and_same_arm_quality',
        'semantic_match_and_clip085_exploratory']
    bool_fields += [t+'_'+c+'_'+s for t in ('correct','wrong_beta','wrong_gamma','wrong_delta')
                   for c in ('semantic','instance') for s in ('content_match','found')]
    for key,rows in groups.items():
        s=dict(zip(('axis','control','dose','strength','arm','scale','semantic_label'),key))
        s['n_planned']=len(rows);s['n_completed']=sum(r['source_outcome']=='completed' for r in rows)
        sources=lambda subset: sorted({r[k] for r in subset for k in ('source_id','donor_id','recipient_id','left','right') if k in r})
        s['n_distinct_sources_planned']=len(sources(rows))
        s['n_distinct_sources_completed']=len(sources([r for r in rows if r['source_outcome']=='completed']))
        s['n_distinct_sources_complete_records']=len(sources([r for r in rows if r['assessment_record_complete']]))
        s['source_ids_planned']=json.dumps(sources(rows))
        s['n_distinct_donors_planned']=len({r['donor_id'] for r in rows if 'donor_id' in r})
        s['n_distinct_recipients_planned']=len({r['recipient_id'] for r in rows if 'recipient_id' in r})
        s['n_distinct_seeds_planned']=len({r['seed'] for r in rows if r.get('seed') is not None})
        s['denominator_unit']='planned conditions; repeated seeds are not independent source images'
        s['n_uncompleted']=len(rows)-s['n_completed']
        s['n_complete_records']=sum(r['assessment_record_complete'] for r in rows)
        s['n_missing_fields_or_conditions']=len(rows)-s['n_complete_records']
        s['source_status_counts']=json.dumps({v:sum(r['source_outcome']==v for r in rows) for v in sorted({r['source_outcome'] for r in rows})},sort_keys=True)
        for field in bool_fields:
            s[field+'_n_true']=sum(r.get(field) is True for r in rows)
            s[field+'_n_false']=sum(r.get(field) is False for r in rows)
            s[field+'_n_missing']=sum(r.get(field) is None for r in rows)
        for tag in ('correct','wrong_beta','wrong_gamma','wrong_delta'):
            for field in ('outcome','proposal_state','qualified_state'):
                values=[r.get(tag+'_'+field) for r in rows]
                s[tag+'_'+field+'_counts']=json.dumps({str(v):values.count(v) for v in sorted(set(values),key=str)},sort_keys=True)
        numeric=set(k for r in rows for k,v in r.items() if type(v) in (int,float) and k not in ('source_id','donor_id','recipient_id','left','right','seed','strength','scale'))
        for field in sorted(numeric):
            values=[r[field] for r in rows if type(r.get(field)) in (int,float) and math.isfinite(r[field])]
            if values:
                s[field+'_n']=len(values);s[field+'_min']=min(values);s[field+'_max']=max(values);s[field+'_mean']=statistics.mean(values)
        summary.append(s)
    return raw,summary,errors

def csv_write(path,rows):
    keys=sorted({k for row in rows for k in row})
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)

def analyze(directory,output):
    directory,output=Path(directory).resolve(),Path(output).resolve()
    if output.exists() or not output.is_relative_to((assessor.MAIN/'.thesis-build/dev-runs').resolve()):
        raise ValueError('Fresh MAIN dev-runs output required')
    output.mkdir(parents=True)
    started=time.monotonic();errors=[];pins=[]
    commit=assessor.git('rev-parse','HEAD')
    run=dict(schema=VERSION,commit=commit,command=sys.argv,config={'assessment_dir':str(directory)},
        data_split='development',seeds=list(assessor.v5.SEEDS),duration_seconds=0,outcome='started',human_visual_verdict=None)
    assessor.write(output/'run.json',run)
    def read(name,default):
        path=directory/name
        receipt={'path':str(path),'status':'missing'}
        if path.is_file():
            receipt.update(status='present',sha256=assessor.sha(path))
            try: value=json.loads(path.read_text())
            except Exception as e: receipt['status']='unreadable';errors.append(name+': '+repr(e));value=default
        else: errors.append('Missing input: '+name);value=default
        pins.append(receipt);return value
    try:
        source_run=read('run.json',{})
        if not isinstance(source_run,dict): errors.append('Invalid run.json object');source_run={}
        if source_run.get('data_split')=='development' and source_run.get('schema')==assessor.VERSION:
            actual=read('conditions.json',[])
        else:
            actual=[];errors.append('Refused conditions without valid development assessment receipt')
        if not isinstance(actual,list): errors.append('Invalid conditions.json list');actual=[]
        # Pin append-only history without treating old attempts as fresh conditions.
        for name in ('rows.jsonl','journal.jsonl'):
            p=directory/name;pins.append({'path':str(p),'status':'present' if p.exists() else 'missing',
                                          'sha256':assessor.sha(p) if p.exists() else None})
        if source_run.get('outcome')!='completed': errors.append('Source run not completed: '+str(source_run.get('outcome')))
        manifest_path=source_run.get('config',{}).get('manifest')
        if manifest_path and Path(manifest_path).is_file():
            digest=assessor.sha(manifest_path);pins.append({'path':manifest_path,'status':'present','sha256':digest})
            if digest!=source_run.get('manifest_sha256'):errors.append('Assessment manifest hash mismatch')
        else: errors.append('Frozen assessment manifest missing')
        labels=json.loads(assessor.LABELS.read_text())
        pins.append({'path':str(assessor.LABELS),'status':'present','sha256':assessor.sha(assessor.LABELS)})
        expected=assessor.planned(labels['pairs'])
        raw,summary,table_errors=tables(expected,actual);errors.extend(table_errors)
        csv_write(output/'conditions.csv',raw);csv_write(output/'summary.csv',summary)
        missing=[r for r in raw if not r['assessment_record_complete']]
        csv_write(output/'missing-or-failed.csv',missing)
        run.update(input_status=source_run.get('outcome'),route=source_run.get('route'),
            n_planned=len(raw),n_completed_source_conditions=sum(r['source_outcome']=='completed' for r in raw),
            n_complete_records=len(raw)-len(missing),n_missing_or_failed=len(missing),
            outcome='completed' if not missing and not errors else 'incomplete',errors=errors)
    except BaseException as error:
        run.update(outcome='failed',error=repr(error));raise
    finally:
        manifest=dict(schema=VERSION,commit=commit,command=sys.argv,config=run['config'],
            inputs=pins,data_split='development',seeds=list(assessor.v5.SEEDS),errors=errors,
            interpretation='Descriptive fixed-denominator development counts; CLIP085 exploratory; human verdict missing',
            duration_seconds=time.monotonic()-started,outcome=run['outcome'])
        assessor.write(output/'manifest.json',manifest)
        run.update(duration_seconds=manifest['duration_seconds'],inputs=pins,
            output_hashes={p.name:assessor.sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'})
        assessor.write(output/'run.json',run)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assessment-dir',required=True);parser.add_argument('--output-dir',required=True)
    args=parser.parse_args();analyze(args.assessment_dir,args.output_dir)

if __name__=='__main__':main()
