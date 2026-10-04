"""CPU-only independent A-C489 receipt/score/control replay; no model loads."""
from __future__ import annotations
import argparse, hashlib, json, math, re, subprocess, sys, time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_assess_terminal_e2e as worker
import m1_analyze_terminal_continuous as audit_math
core,util=worker.core,worker.util
VERSION='m1-terminal-e2e-threat-analysis-v1'

def array(r,shape):
    value=np.load(worker.checked(r),allow_pickle=False)
    if value.dtype!=np.float64 or value.shape!=shape or not np.isfinite(value).all():raise ValueError('Finite FP64 array shape/dtype mismatch')
    return value

def decisions(z,E,H):return {owner:core.scores(z,E,H,owner) for owner in core.OWNERS}

def verify_image_row(spec,row,anchors,manifest):
    rgb=worker.original.read_rgb(worker.checked(row['image']))
    if hashlib.sha256(rgb.tobytes()).hexdigest()!=row['image']['rgb8_sha256']:raise ValueError('Saved image pixel receipt mismatch')
    z=array(row['reader_latent'],(core.N,));E=np.asarray(row['suspect_E'],np.float64);H=row['suspect_H']
    if E.shape!=(512,) or not np.isfinite(E).all() or abs(np.linalg.norm(E)-1)>1e-6 or type(H) is not int:raise ValueError('Invalid suspect descriptors')
    codec=worker.candidate.codec;profile=codec.validate_profile(codec.load_profile(ROOT/worker.candidate.configuration()['profile']))
    if codec.perceptual_hash(codec.luminance_from_rgb(rgb.tolist()),profile=profile)!=H:raise ValueError('Suspect hash differs from PNG')
    recomputed=decisions(z,E,H);audit_math.equal(row['owner_decisions'],recomputed,'blind')
    if any(d['state']=='invalid_measurement' for d in recomputed.values()):raise ValueError('Invalid primary reader slot')
    if not audit_math.finite(row.get('extract_seconds')) or row['extract_seconds']<0:raise ValueError('Readout timing missing')
    ref=spec.get('recipient_id',spec.get('source_id'));source=anchors[ref,'C0'];arm=spec.get('control','C0')
    source_rgb=worker.original.read_rgb(worker.checked(source['image']));arm_rgb=worker.original.read_rgb(worker.checked(anchors[ref,arm]['image']))
    for key,left in (('quality_vs_source',source_rgb),('quality_vs_same_arm_original',arm_rgb)):
        audit_math.pixel_quality(row[key],left,rgb)
        if audit_math.quality_pass(row[key]) is None:raise ValueError('Invalid retained LPIPS/quality observation')
        if row[key].get('quality_admissible')!=(audit_math.quality_pass(row[key]) is True):raise ValueError('Quality admissibility predicate differs')
    audit_math.equal(row['source_clip_cosine'],float(np.asarray(source['E'])@E),'cosine')
    audit_math.equal(row['source_phash_distance'],int((source['H']^H).bit_count()),'hashdistance')
    if row.get('reader_reuse'):
        case=next(c for c in manifest['cases'] if c['id']==spec['source_id'])
        old=next(r for r in case['rows'] if r['control']==spec['control'] and r['dose']==('clean' if spec['axis']=='clean' else 'vae_cycle'))
        if row['reader_reuse']['source_run']!=case['source_run'] or row['reader_reuse']['condition_sha256']!=worker.candidate.component.canonical_sha(old):raise ValueError('Enrollment readout alias changed')
        for a,b in (('image','image'),('reader_latent','terminal_reader_latent'),('suspect_E','suspect_E'),('suspect_H','suspect_H'),('owner_decisions','owner_decisions')):
            if row[a]!=old[b]:raise ValueError('Reused operator readout differs')
    elif spec['axis']=='clean' or spec.get('dose')=='vae_mode':raise ValueError('Clean/VAE must alias verified candidate endpoint')
    if spec['axis'] in ('clean','T3'):
        audit_math.equal(row['source_template_oracle'],core.scores(z,source['E'],source['H'],core.OWNERS[0]),'sourceoracle')
        if spec.get('dose')=='diffusion':
            expected=[float(t) for t in reversed(range(1,1000,50))][20-int(20*spec['strength']):]
            if row.get('actual_ddim_timesteps')!=expected or row.get('nfe_unet')!=len(expected):raise ValueError('Actual DDIM timestep/NFE inventory differs')
    else:
        donor,recipient=anchors[spec['donor_id'],'C1'],anchors[spec['recipient_id'],'C0']
        tuples=worker.tuple_scores(z,donor,recipient);audit_math.equal(row['tuple_scores'],tuples,'tuples')
        geometry={owner:core.projection_diagnostic(donor['E'],donor['H'],E,H,owner) for owner in core.OWNERS}
        audit_math.equal(row['donor_geometry'],geometry,'geometry')
        dtuples=worker.tuple_scores(donor['z'],donor,recipient);rtuples=worker.tuple_scores(recipient['z'],donor,recipient)
        expected=worker.transfer_witness(donor['blind'][core.OWNERS[0]],tuples,rtuples,row['quality_vs_source'],dtuples)
        audit_math.equal(row['delivery'],expected,'delivery')
        if row.get('adaptive_detector_decision_queries')!=0:raise ValueError('Undeclared adaptive detector query')
        if spec['arm']=='clean_donor_residual':
            d0=worker.original.read_rgb(worker.checked(anchors[spec['donor_id'],'C0']['image']))
            d1=worker.original.read_rgb(worker.checked(donor['image']))
            expected_rgb=np.asarray(worker.protocol.residual_transfer(source_rgb.tolist(),d1.tolist(),d0.tolist(),spec['scale']),np.uint8)
            if not np.array_equal(rgb,expected_rgb):raise ValueError('Residual byte-unit operator differs')
        else:verify_projection(spec,row,anchors,rgb,source_rgb)
    return dict(id=spec['id'],axis=spec['axis'],verified=True,blind=recomputed,
        quality_pass=audit_math.quality_pass(row['quality_vs_source']),psnr_db=row['quality_vs_source']['psnr_db'],
        quality_vs_source=row['quality_vs_source'],quality_vs_same_arm_original=row['quality_vs_same_arm_original'],
        source_id=spec.get('source_id'),strength=spec.get('strength'),seed=spec.get('seed'),control=spec.get('control'),
        recipient_id=spec.get('recipient_id'),donor_id=spec.get('donor_id'),arm=spec.get('arm'),
        delivery=row.get('delivery'),input_outcome=row['outcome'],extract_seconds=row['extract_seconds'])

def verify_projection(spec,row,anchors,rgb,source_rgb):
    projection=row['projection'];arrays=projection['arrays']
    if set(arrays)!={'residual','donor_observed_z','recipient_observed_z','target_z','target_u64','target_u16','baseline_u64','baseline_u16'}:raise ValueError('Projection evidence inventory differs')
    donor=array(arrays['donor_observed_z'],(core.N,));recipient=array(arrays['recipient_observed_z'],(core.N,));target=array(arrays['target_z'],(core.N,))
    original_donor=anchors[spec['donor_id'],'C0' if spec['arm']=='unmarked_projection_sham' else 'C1'];original_recipient=anchors[spec['recipient_id'],'C0']
    if not np.array_equal(donor,original_donor['z']) or not np.array_equal(recipient,original_recipient['z']):raise ValueError('Projection input mode differs from supplied-image readout')
    d=projection['donor_descriptor']
    if d!={'E':original_donor['E'],'H':original_donor['H']}:raise ValueError('Public donor descriptor differs')
    expected,info=worker.projection_displacement(donor,recipient,d['E'],d['H'])
    if not np.array_equal(expected,target):raise ValueError('One-shot target displacement differs')
    for key,value in info.items():audit_math.equal(projection[key],value,'projection:'+key)
    represented={}
    for name,z64 in (('target',target),('baseline',recipient)):
        u64,u16,represented[name],conversion=worker.decoder_input(z64)
        saved_half=np.load(worker.checked(arrays[name+'_u16']),allow_pickle=False)
        if saved_half.dtype!=np.float16 or saved_half.shape!=(core.N,) or not np.array_equal(array(arrays[name+'_u64'],(core.N,)),u64) or not np.array_equal(saved_half,u16):
            raise ValueError('Actual decoder input differs from frozen conversion')
        audit_math.equal(projection['decoder_conversion'][name],conversion,'conversion:'+name)
    audit_math.equal(projection['postcast_projection_residuals'],worker.postcast_residuals(represented['target'],represented['baseline'],donor,d['E'],d['H'],info['coefficients']),'postcast')
    audit_math.equal(projection['projection_precision'],worker.precision_receipt(projection),'precision-receipt')
    residual=array(arrays['residual'],(512,512,3));expected_rgb,cap=audit_math.cap(source_rgb,residual)
    if not np.array_equal(rgb,expected_rgb):raise ValueError('Native projection quality-only cap replay differs')
    audit_math.equal(projection['cap'],cap,'projectioncap')
    error=represented['target']-target
    for k,v in (('fp16_scaled_roundtrip_rms',float(np.sqrt(np.mean(error**2)))),('fp16_scaled_roundtrip_max',float(np.max(np.abs(error))))):
        audit_math.equal(projection[k],v,'conversion:'+k)
    if set(projection.get('decoder_stage_hashes',{}))!={'target_decode','baseline_decode'}:raise ValueError('Decoder-stage receipts missing')
    if any(not isinstance(h,str) or re.fullmatch('[0-9a-f]{64}',h) is None for h in projection['decoder_stage_hashes'].values()):raise ValueError('Decoder-stage hashes invalid')

def verify_partition(directory,manifest):
    base=Path(directory).resolve();run=worker.read(worker.checked(worker.receipt(base/'run.json')))
    part=run.get('partition')
    if part not in worker.PARTITIONS:raise ValueError('Unknown partition')
    manifest_path=worker.checked(run['manifest'])
    if worker.read(manifest_path)!=manifest:raise ValueError('Partition frozen manifest differs')
    expected_identity=worker.assessment_identity(manifest,util.sha(manifest_path),part)
    if run.get('schema')!=worker.VERSION or run.get('data_split')!='development' or run.get('identity')!=expected_identity:raise ValueError('Partition scientific identity differs')
    actual={p.name:util.sha(p) for p in base.iterdir() if p.is_file() and p.name!='run.json'}
    if actual!=run.get('output_hashes'):raise ValueError('Partition output hash inventory differs')
    rows=worker.read(worker.checked(run['conditions_receipt']))
    if {r['id'] for r in rows}!=set(expected_identity['condition_ids']) or len(rows)!=len(expected_identity['condition_ids']):raise ValueError('Partition row inventory differs')
    pinned=run.get('committed_files',{})
    expected_deps={p.relative_to(ROOT).as_posix() for p in worker.dependencies()+[manifest_path]}
    if set(pinned)!=expected_deps or any(util.sha(ROOT/k)!=v['working_sha256'] for k,v in pinned.items()):raise ValueError('Partition committed scientific bytes changed')
    budgets=manifest['schedule']['budgets']
    if not audit_math.finite(run.get('duration_seconds')) or not 0<=run['duration_seconds']<=budgets['run_seconds_cap']:raise ValueError('Cumulative wall cap')
    if type(run.get('peak_rss_bytes')) is not int or not 0<run['peak_rss_bytes']<=budgets['ram_budget_bytes']:raise ValueError('RAM receipt cap')
    gpu=run['gpu_budget']
    if gpu!=worker.candidate.gpu_allocation_budget(budgets['gpu_budget_bytes'],gpu['free_bytes_before_models'],gpu['total_bytes'],budgets['gpu_reserve_bytes']):raise ValueError('GPU allocation receipt')
    if type(run.get('peak_allocated_bytes')) is not int or not 0<=run['peak_allocated_bytes']<=gpu['effective_allocation_bytes']:raise ValueError('GPU peak receipt')
    if run.get('previous_artifact_bytes',0)+sum(p.stat().st_size for p in base.rglob('*') if p.is_file())>budgets['artifact_budget_bytes']:raise ValueError('Cumulative artifact budget')
    if run.get('resume_input'):
        prior=worker.read(worker.checked(run['resume_input']))
        if prior.get('identity')!=run['identity'] or prior.get('resume_input') or prior.get('outcome')=='completed':raise ValueError('Continuation identity/lineage invalid')
        oldrows={r['id']:r for r in worker.read(worker.checked(prior['conditions_receipt']))}
        for row in rows:
            previous=oldrows[row['id']]
            if previous.get('image') and row.get('image')!=previous['image']:raise ValueError('Completed generated image was replaced on continuation')
            if previous.get('outcome')=='safety_blocked' and row!=previous:raise ValueError('Safety terminal row was retried')
    return run,rows,worker.receipt(base/'run.json')

def summaries(specs,verified):
    table={r['id']:r for r in verified};alpha=core.OWNERS[0]
    result={'planned':dict(conditions=489,images=423,primary_queries=1692,negative_slots=1437,diagnostic_queries=1164),
        'verified_image_n':sum(r.get('verified') is True and r['axis']!='T5' for r in verified),
        'missing_or_invalid_n':sum(r.get('verified') is not True for r in verified),
        'survival':[],'transfer_coverage':{},'population_claims':'No independent-query FPR or adaptive security inference'}
    for axis,control,dose,strength in [('clean','C1',None,None),('T3','C1','vae_mode',None)]+[('T3','C1','diffusion',s) for s in worker.graph.STRENGTHS]:
        wanted=[s for s in specs if s['axis']==axis and s.get('control')==control and (axis=='clean' or s.get('dose')==dose)
            and s.get('strength')==strength]
        observed=[table[s['id']] for s in wanted if table[s['id']].get('verified')]
        count=lambda k:sum(r['blind'][alpha]['flags'][k] for r in observed)
        result['survival'].append(dict(axis=axis,dose=dose,strength=strength,planned=len(wanted),source_clusters=12,
            observed=len(observed),semantic=count('s'),instance=count('i'),both=sum(r['blind'][alpha]['state']=='both_match' for r in observed),
            joint_quality_both=sum(r['quality_pass'] is True and r['blind'][alpha]['state']=='both_match' for r in observed),
            joint_clean_quality_both=sum(table[f'clean-{r["source_id"]}-C1'].get('quality_pass') is True and r['blind'][alpha]['state']=='both_match' for r in observed),
            rows=[dict(id=r['id'],source_id=r.get('source_id'),seed=r.get('seed'),state=r['blind'][alpha]['state']) for r in observed]))
    for axis in ('T4','T5-transfer'):
        wanted=[s for s in specs if s['axis']==axis];observed=[table[s['id']] for s in wanted if table[s['id']].get('verified')]
        strict=[r for r in observed if r['delivery']['strict_dual_delivery']]
        qualified=[r for r in strict if axis=='T4' or r['delivery']['continuous_semantic_challenge']]
        groups={}
        for r in observed:
            arm=r['arm'];groups.setdefault(arm,[]).append(r)
        result['transfer_coverage'][axis]=dict(planned=len(wanted),observed=len(observed),quality_admissible=sum(r['quality_pass'] is True for r in observed),
            strict_delivery=len(strict),qualifying_pairs=len(qualified),distinct_recipients=len({r['recipient_id'] for r in qualified}),
            coverage_denominator=10 if axis=='T4' else 7,coverage_target=10 if axis=='T4' else 5,
            coverage_met=len({r['recipient_id'] for r in qualified})>=10 if axis=='T4' else len(qualified)>=5,
            by_arm={arm:dict(observed=len(rs),delivery_recipients=sorted({r['recipient_id'] for r in rs if r['delivery']['strict_dual_delivery']})) for arm,rs in groups.items()},
            delivery_acceptance={f'{d}/{a}':sum((r['delivery']['strict_dual_delivery'] is d) and ((r['blind'][alpha]['state']=='both_match') is a) for r in observed)
                for d in (False,True) for a in (False,True)},security_pass=None)
    negative=[]
    for spec in specs:
        if spec['axis']=='T5':continue
        row=table[spec['id']]
        for owner in core.OWNERS if spec['axis'] in ('clean','T3') and spec['control']=='C0' else core.OWNERS[1:]:
            negative.append(None if not row.get('verified') else row['blind'][owner]['flags'])
    if len(negative)!=1437:raise ValueError('Negative-slot inventory changed')
    result['negative_controls']=dict(planned=1437,observed=sum(v is not None for v in negative),
        semantic_exceedances=sum(v is not None and v['s'] for v in negative),instance_exceedances=sum(v is not None and v['i'] for v in negative),
        joint_exceedances=sum(v is not None and v['s'] and v['i'] for v in negative),independent_sample_size=None)
    return result

def analyze(manifest_path,input_dirs,output):
    started=time.monotonic();manifest=worker.read(manifest_path);specs=worker.validate(manifest)
    output=Path(output).resolve()
    if not output.is_relative_to((worker.MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN development output')
    output.mkdir(parents=True,exist_ok=False);anchors=worker.enrollment_anchors(manifest)
    record=dict(schema=VERSION,data_split='development',command=sys.argv,outcome='started',errors=[],inputs=[],
        manifest=worker.receipt(manifest_path),method_core_sha256=manifest['method_core_sha256'],assessment_core_sha256=manifest['assessment_core_sha256'],
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),human_visual_verdict=None)
    selected={};partitions={};expected={r['id']:r for r in specs}
    for directory in input_dirs:
        try:
            run,rows,r=verify_partition(directory,manifest);part=run['partition']
            if part in partitions:raise ValueError('Duplicate final partition; select only its explicitly resolved continuation')
            partitions[part]=run;record['inputs'].append(r)
            for row in rows:
                if row['id'] in selected:raise ValueError('Overlapping final condition IDs')
                if any(row.get(k)!=v for k,v in expected[row['id']].items()):raise ValueError('Condition scientific membership differs')
                selected[row['id']]=row
        except Exception as error:record['errors'].append(str(directory)+': '+str(error))
    verified=[];diagnostics=[];geometry=[]
    for spec in specs:
        row=selected.get(spec['id']);item=dict(**spec,verified=False,input_outcome=row.get('outcome') if row else 'missing_partition')
        if row and row.get('outcome')=='completed':
            try:
                if spec['axis']=='T5':
                    actual=worker.component_pair(spec,anchors);audit_math.equal(row['components'],actual['components'],'paircomponents')
                    item.update(verified=True,components=actual['components'])
                else:item=verify_image_row(spec,row,anchors,manifest)
            except Exception as error:item['error']=str(error);record['errors'].append(spec['id']+': '+str(error))
        elif row and row.get('outcome')=='missing_enrollment':
            missing=[manifest['cases'][worker.candidate.IDS.index(sid)]['status']=='missing' for sid in row.get('missing_ids',[])]
            if not missing or not all(missing):record['errors'].append(spec['id']+': invalid missing lineage')
        verified.append(item)
    resolved={r['id']:r for r in verified}
    baseline=worker.anchor_controls(anchors)
    transfer_run=partitions.get('transfers')
    baseline_ok=False
    if transfer_run:
        try:
            audit_math.equal(worker.read(worker.checked(transfer_run['anchor_controls'])),baseline,'baseline-controls');baseline_ok=True
        except Exception as error:record['errors'].append('anchor controls: '+str(error))
    baseline_lookup={(r['donor_id'],r['recipient_id']):r for r in baseline}
    for slot in worker.diagnostic_inventory(specs):
        entry=dict(slot,verified=False,scores=None)
        if slot['kind']=='anchor-tuple':
            pair=baseline_lookup[slot['donor_id'],slot['recipient_id']]
            if pair['outcome']=='completed' and baseline_ok:
                entry.update(verified=True,scores=pair['donor_C1' if slot['anchor']=='donor-C1' else 'recipient_C0'][slot['descriptor_tuple']])
        elif resolved[slot['condition']].get('verified'):
            row=selected[slot['condition']]
            if slot['kind']=='source-oracle':score=row['source_template_oracle']
            elif slot['kind']=='transfer-tuple':score=row['tuple_scores'][slot['descriptor_tuple']]
            else:score=row['components'][slot['control']]['cross_template'][slot['direction']]
            entry.update(verified=True,scores=score)
        diagnostics.append(entry)
    for spec in specs:
        row=selected.get(spec['id']);good=resolved[spec['id']].get('verified')
        if spec['axis']=='T5':
            geometry.extend(dict(id=f'{spec["id"]}-{c}-{o}',verified=bool(good),values=row['components'][c]['geometry'][o] if good else None)
                for c in ('C0','C1') for o in core.OWNERS)
        elif spec['axis'] in ('T4','T5-transfer'):
            geometry.extend(dict(id=spec['id']+'-'+o,verified=bool(good),values=row['donor_geometry'][o] if good else None) for o in core.OWNERS)
    record['summary']=summaries(specs,verified);record['diagnostics']=dict(planned=1164,verified=sum(r['verified'] for r in diagnostics))
    record['geometry']=dict(planned=876,verified=sum(r['verified'] for r in geometry))
    record['scope']='Scores/hash/PNG pixels/control geometry replayed on CPU; CLIP, VAE and LPIPS inference retained, not rerun'
    record['outcome']='completed' if not record['errors'] and set(partitions)==set(worker.PARTITIONS) else 'incomplete'
    record['scientific_complete']=all(r.get('verified') for r in verified)
    for name,value in (('conditions.json',verified),('diagnostics.json',diagnostics),('geometry.json',geometry),('anchor-controls.json',baseline)):
        util.write(output/name,value)
    record['duration_seconds']=time.monotonic()-started
    record['outputs']={p.name:util.sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'}
    util.write(output/'run.json',record);return record

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--input-dir',action='append',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args();result=analyze(a.manifest,a.input_dir,a.output_dir)
    print(json.dumps(dict(outcome=result['outcome'],summary=result['summary'],errors=result['errors']),allow_nan=False))
    return 0 if result['outcome']=='completed' else 2

if __name__=='__main__':raise SystemExit(main())
