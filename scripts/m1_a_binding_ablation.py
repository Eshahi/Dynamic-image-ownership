"""Frozen CPU reread of original-A saved transfer PNGs; no image generation."""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess, sys, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT))
import m1_assess_dual_threats as source_api
import m1_phasemark as util
import revised_watermark_v5 as codec
VERSION='m1-A-binding-ablation-v1'
SOURCE=util.MAIN/'.thesis-build/dev-runs/20261004-0900-A-hybrid-threats'
SOURCE_SHA='7929d9cbbf7a9314f7959d85144fe26d99324ffd7ecc10e40455f5f623ce07a6'
CONDITIONS_SHA='404aefbe30d934b8405732cf62a3765da4550fba30e5ee7f4030a11eeb5a5b4e'
SOURCE_MANIFEST=ROOT/'research/m1-A-hybrid-twelve-threats-dev.json'
SOURCE_MANIFEST_SHA='7ff2ba30bf0004c5abc2f5ac33b2ddd60da1d69140def2c586bdbf5013ac52c6'
MODES=('combined','none','semantic_only','perceptual_only')
OWNER='qim-pilot-owner-alpha'
DEPENDENCIES=['scripts/m1_a_binding_ablation.py','research/m1-A-binding-ablation-dev.json',
 'research/m1-A-binding-ablation.md','scripts/m1_assess_dual_threats.py','scripts/m1_dual_latent.py',
 'scripts/m1_phasemark.py','scripts/revised_watermark_v5.py','scripts/revised_watermark_v4.py',
 'scripts/three_threat_protocol.py','scripts/v5_study_protocol.py','scripts/three_threat_models.py',
 'scripts/a6_clip_visual.py','scripts/m1_latent_reconstruction.py','scripts/verify_science_assets.py',
 'scripts/check_a6_lpips_assets.py','research/a6-candidate-model-assets.json',
 'experiments/c4-three-threat-small-v1/semantic-labels.json']

def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def finite(value):return type(value) in (int,float) and math.isfinite(value)
def quality_pass(q):
    if not isinstance(q,dict) or type(q.get('psnr_infinite')) is not bool:return None
    if not all(finite(q.get(k)) for k in ('mse_rgb8','ssim_rgb','lpips')):return None
    if q['psnr_infinite']:
        if q.get('psnr_db') is not None or q['mse_rgb8']!=0:return None
    elif not finite(q.get('psnr_db')):return None
    if q['lpips']<0 or q['mse_rgb8']<0:return None
    return (q['psnr_infinite'] or q['psnr_db']>35) and q['ssim_rgb']>.9 and q['lpips']<.1

def fixed_inventory():
    pairs=read(source_api.LABELS)['pairs']
    return [r for r in source_api.planned(pairs) if r['axis'] in ('T4','T5-transfer')]

def transfer_rows(rows):
    expected={r['id']:r for r in fixed_inventory()};selected={};errors=[]
    for row in rows:
        if row.get('axis') not in ('T4','T5-transfer'):continue
        rid=row.get('id')
        if rid not in expected or rid in selected:raise ValueError('Unexpected/duplicate transfer ID')
        if any(row.get(k)!=v for k,v in expected[rid].items()):raise ValueError('Transfer membership mismatch: '+rid)
        selected[rid]=row
    for rid in expected:
        if rid not in selected:errors.append(rid+': absent source row')
    return [selected.get(r['id'],dict(**r,outcome='missing')) for r in expected.values()],errors

def source_receipts():
    if sha(SOURCE/'run.json')!=SOURCE_SHA or sha(SOURCE/'conditions.json')!=CONDITIONS_SHA:raise ValueError('Retained original-A source changed')
    run=read(SOURCE/'run.json');manifest=read(SOURCE_MANIFEST)
    if sha(SOURCE_MANIFEST)!=SOURCE_MANIFEST_SHA or SOURCE_MANIFEST_SHA!=run['manifest_sha256'] or run['data_split']!='development' or run['route']!='hybrid-source-bypass':raise ValueError('Source manifest/route/split changed')
    if manifest['profile']!=run['profile'] or manifest['owners'][0]!=OWNER:raise ValueError('Frozen profile/owner mismatch')
    for rel,digest in manifest['dependencies'].items():
        if sha(ROOT/rel)!=digest:raise ValueError('Original-A scientific dependency changed: '+rel)
    enrolled={};receipts=[]
    for r in run['input_runs']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Enrollment run receipt mismatch')
        prior=read(r['path'])
        if prior['data_split']!='development':raise ValueError('Development enrollment only')
        for case in prior['cases']:
            if case['id'] in enrolled:raise ValueError('Duplicate enrollment source')
            enrolled[case['id']]=case['enrollment']
        receipts.append(r)
    rows,errors=transfer_rows(read(SOURCE/'conditions.json'))
    cases={c['id']:c for c in manifest['cases']}
    for row in rows:
        if row.get('image'):
            image=Path(row['image']['path']).resolve()
            if not image.is_relative_to(SOURCE.resolve()) or sha(image)!=row['image']['sha256']:raise ValueError('Transfer PNG hash/path mismatch')
        row['donor_enrollment']=enrolled.get(row['donor_id'])
        row['recipient_source']=cases[row['recipient_id']]['images']['source']
        if sha(row['recipient_source']['path'])!=row['recipient_source']['sha256']:raise ValueError('Recipient source hash mismatch')
    return run,rows,receipts,errors

def configuration():
    run,rows,receipts,errors=source_receipts()
    return dict(schema=VERSION,data_split='development',source_run=str(SOURCE),source_run_sha256=SOURCE_SHA,
        source_conditions_sha256=CONDITIONS_SHA,source_commit=run['commit'],source_manifest_sha256=run['manifest_sha256'],
        profile=run['profile'],owner=OWNER,roster_size=1,modes=list(MODES),planned_pngs=87,planned_calls=348,
        t4_pngs=80,t5_transfer_pngs=7,minimum_distinct_t4_recipients=10,source_clusters=12,
        enrollment_runs=receipts,input_errors=errors,
        conditions=[dict(id=r['id'],axis=r['axis'],donor_id=r['donor_id'],recipient_id=r['recipient_id'],
            arm=r['arm'],source_outcome=r['outcome'],source_row_sha256=canonical({k:v for k,v in r.items() if k not in ('donor_enrollment','recipient_source')}),
            image=r.get('image'),donor_enrollment=r['donor_enrollment'],recipient_source=r['recipient_source']) for r in rows],
        quality={'psnr_gt':35.,'ssim_gt':.9,'lpips_lt':.1,'lpips_measurement':'retained original-A hash-pinned CPU LPIPS; not rerun'},
        delivery={'carrier':'binding-none found; same owner is not donor identity',
          'attribution':'read decoded code, corrected Hamming versus frozen donor source q/h; existing radius6',
          'semantic_and_dual_separate':True,'sham_never_counts_as_delivery':True},
        run_seconds_cap=1800,ram_budget_bytes=16*1024**3,artifact_budget_bytes=50*1024**2,
        gpu=False,human_visual_verdict=None)

def strip_result(result):
    keys=('outcome','proposal_state','present','watermark_found','semantic','instance','semantic_code','perceptual_hash',
          'instance_tested_with_semantic_code','binding_mode','owner_id','owners_tested','security','semantic_source',
          'embedding_domain','detector_config_id','decision_id','version','revision','height','width')
    if any(k not in result for k in keys):raise ValueError('Missing detector field')
    return {k:result[k] for k in keys}

def parity(left,right):
    def equal(a,b):
        if isinstance(b,dict):return isinstance(a,dict) and set(a)==set(b) and all(equal(a[k],v) for k,v in b.items())
        if isinstance(b,bool) or b is None or isinstance(b,str):return type(a)==type(b) and a==b
        return finite(a) and finite(b) and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9)
    return equal(strip_result(left),strip_result(right))

def donor_channel(channel,donor_code,radius):
    if type(channel.get('found')) is not bool or type(channel.get('read')) is not bool:raise ValueError('Missing presence/read boolean')
    if not channel['read']:return dict(carrier_found=channel['found'],read=False,donor_distance=None,donor_corrected_distance=None,donor_attributed=False)
    error=channel.get('decoding_error_rate')
    if not finite(error) or not 0<=error<.5:raise ValueError('Invalid decoding error rate')
    distance=(int(channel['decoded_code'],16)^int(donor_code,16)).bit_count()
    corrected=round(min(32.,max(0.,(distance-32*error)/(1-2*error))),6)
    return dict(carrier_found=channel['found'],read=True,donor_distance=distance,donor_corrected_distance=corrected,
        donor_attributed=channel['found'] and corrected<=radius)

def delivery(result,enrollment,profile,arm):
    s=donor_channel(result['semantic'],enrollment['semantic_code'],profile['decision']['semantic_radius'])
    i=donor_channel(result['instance'],enrollment['perceptual_hash'],profile['decision']['instance_radius'])
    is_transfer=arm!='unmarked_projection_sham'
    return dict(semantic=s,instance=i,semantic_donor_delivered=is_transfer and s['donor_attributed'],
        dual_donor_delivered=is_transfer and s['donor_attributed'] and i['donor_attributed'],
        evaluator_side_information='frozen donor enrollment q/h; attribution diagnostic only, not blind verification')

def evaluate_modes(rgb,feature,profile,detector=codec.detect_rgb,callback=None):
    output=[]
    for mode in MODES:
        started=time.monotonic()
        try:
            result=detector(rgb.tolist(),OWNER,profile=profile,semantic_features=feature,binding_mode=mode,roster_size=1)
            call=dict(binding_mode=mode,outcome='completed',result=result,seconds=time.monotonic()-started)
        except Exception as ex:call=dict(binding_mode=mode,outcome='failed',result=None,error=repr(ex),seconds=time.monotonic()-started)
        output.append(call)
        if callback:callback(list(output))
    return output

def summarize(rows):
    summaries=[]
    for axis in ('T4','T5-transfer'):
        selected=[r for r in rows if r['axis']==axis];completed=[r for r in selected if r.get('outcome')=='completed']
        semantic={r['recipient_id'] for r in completed if r['strict_recipient_quality'] and r['delivery']['semantic_donor_delivered']}
        dual={r['recipient_id'] for r in completed if r['strict_recipient_quality'] and r['delivery']['dual_donor_delivered']}
        summaries.append(dict(axis=axis,planned_pngs=80 if axis=='T4' else 7,completed_pngs=len(completed),
            planned_calls=(80 if axis=='T4' else 7)*4,attempted_calls=sum(len(r.get('calls',[])) for r in selected),completed_calls=sum(c.get('outcome')=='completed' for r in selected for c in r.get('calls',[])),
            recipient_clusters=len({r['recipient_id'] for r in selected}),strict_quality_n=sum(r['strict_recipient_quality'] for r in completed),
            semantic_delivered_quality_recipient_n=len(semantic),dual_delivered_quality_recipient_n=len(dual),
            minimum10_t4_semantic_delivery_coverage=None if len(completed)!=80 or axis!='T4' else len(semantic)>=10,
            minimum10_t4_dual_delivery_coverage=None if len(completed)!=80 or axis!='T4' else len(dual)>=10,
            old_clip_receipt_exact_n=sum(r['old_clip_receipt_equal'] for r in completed),old_combined_parity_n=sum(r['old_combined_parity'] for r in completed),
            combined_both_n=sum(r['calls'][0]['result']['outcome']=='both_match' for r in completed),
            adequate_delivery_rejected_n=sum(r['strict_recipient_quality'] and r['delivery']['dual_donor_delivered'] and r['calls'][0]['result']['outcome']!='both_match' for r in completed),
            delivered_quality_combined_outcomes={label:sum(r['strict_recipient_quality'] and r['delivery']['dual_donor_delivered'] and r['calls'][0]['result']['outcome']==label for r in completed) for label in sorted({r['calls'][0]['result']['outcome'] for r in completed})},
            security_verdict=None,human_visual_verdict=None))
    return summaries

def run(manifest_path,output):
    import numpy as np
    from PIL import Image
    output=Path(output).resolve();manifest_path=Path(manifest_path).resolve()
    if not output.is_relative_to((util.MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN development output only')
    manifest=read(manifest_path)
    if manifest!=configuration():raise ValueError('Exact frozen manifest required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    state={r['id']:dict(**r,outcome='planned',calls=[],human_visual_verdict=None) for r in manifest['conditions']}
    record=dict(schema=VERSION,command=sys.argv,config=manifest,data_split='development',seeds=[],outcome='started',duration_seconds=0.,
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),manifest_sha256=sha(manifest_path),
        nfe_unet=0,gpu_model_calls=0,planned_conditions=87,planned_calls=348,source_outcome='incomplete',human_visual_verdict=None)
    def retain(row):
        with (output/'journal.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row,allow_nan=False)+'\n')
        write(output/'conditions.json',list(state.values()));write(output/'run.json',record)
    for row in state.values():retain(row)
    try:
        record['committed_files']=util.require_committed([ROOT/p for p in DEPENDENCIES]);record['analyzed_manifest_sha256']=sha(manifest_path)
        (output/'manifest.json').write_bytes(manifest_path.read_bytes());write(output/'run.json',record)
        from three_threat_models import block_network,verify_assets,clip_feature
        from a6_clip_visual import load_visual_encoder
        from m1_latent_reconstruction import quality
        import torch,importlib.metadata
        block_network()
        assets,package=verify_assets(util.ASSETS,ROOT/'research/a6-candidate-model-assets.json');record['asset_receipt']=assets
        model,transform=load_visual_encoder(util.ASSETS/'clip/ViT-B-32.pt',device='cpu')
        record['environment']={'python':sys.version,'torch':torch.__version__,'torch_threads':torch.get_num_threads(),
             **{name:importlib.metadata.version(name) for name in ('numpy','scipy','Pillow')}}
        record['detector_side_information']=['suspect RGB8','public OwnerID-alpha','unchanged originalA v5 profile','CPU pinned CLIP']
        _,source_rows,_,_=source_receipts();old={r['id']:r for r in source_rows};source_cache={}
        def rgb(receipt):
            if sha(receipt['path'])!=receipt['sha256']:raise ValueError('Image changed before evaluation')
            with Image.open(receipt['path']) as im:
                if im.mode!='RGB' or im.size!=(512,512):raise ValueError('Expected RGB512 PNG')
                return np.asarray(im).copy()
        for row in state.values():
            try:
                if time.monotonic()-started>manifest['run_seconds_cap'] or util.working_set_bytes()>manifest['ram_budget_bytes'] or sum(p.stat().st_size for p in output.iterdir() if p.is_file())>manifest['artifact_budget_bytes']:raise RuntimeError('CPU run resource cap')
                if row['source_outcome']!='completed' or not row.get('image') or not row.get('donor_enrollment'):raise ValueError('Missing original completed transfer/enrollment')
                row['outcome']='started';retain(row);image=rgb(row['image'])
                tick=time.monotonic();feature=np.asarray(clip_feature(model,transform,image),dtype=np.float64).reshape(-1)
                row['clip_seconds']=time.monotonic()-tick
                if feature.shape!=(512,) or not np.isfinite(feature).all() or abs(np.linalg.norm(feature)-1)>1e-6:raise ValueError('Invalid CPU CLIP feature')
                row['suspect_clip_sha256']=hashlib.sha256(feature.astype('<f8').tobytes()).hexdigest();row['suspect_clip_feature']=feature.tolist()
                row['old_clip_receipt_equal']=row['suspect_clip_sha256']==old[row['id']]['suspect_clip_sha256']
                def retain_calls(calls):row['calls']=calls;retain(row)
                row['calls']=evaluate_modes(image,feature.tolist(),manifest['profile'],callback=retain_calls)
                if any(c['outcome']!='completed' for c in row['calls']):raise ValueError('One or more fixed detector calls failed')
                original=[d['result'] for d in old[row['id']]['detections'] if d['owner']==OWNER]
                row['old_combined_parity']=len(original)==1 and parity(row['calls'][0]['result'],original[0])
                if not row['old_combined_parity']:raise ValueError('Combined old/new numerical parity failed')
                for call in row['calls']:
                    for channel in ('semantic','instance'):
                        if any(call['result'][channel][k]!=row['calls'][0]['result'][channel][k] for k in ('found','read','decoded_code','score','threshold')):raise ValueError('Ablation changed carrier measurement')
                recipient=row['recipient_id']
                if recipient not in source_cache:
                    source_image=rgb(row['recipient_source']);source_feature=np.asarray(clip_feature(model,transform,source_image),np.float64).reshape(-1)
                    source_cache[recipient]=(source_image,source_feature)
                source_image,source_feature=source_cache[recipient]
                q=old[row['id']]['quality_vs_source'];actual=quality(source_image,image)
                for k in ('mse_rgb8','psnr_db','psnr_infinite','ssim_rgb'):
                    if actual[k] is None or type(actual[k]) is bool:
                        if actual[k]!=q.get(k):raise ValueError('Retained pixel quality differs')
                    elif not finite(q.get(k)) or not math.isclose(actual[k],q[k],rel_tol=1e-9,abs_tol=1e-9):raise ValueError('Retained pixel quality differs')
                row['quality_vs_recipient_source']=dict(q);row['recomputed_recipient_clip_cosine']=float(source_feature@feature)
                row['recipient_source_clip_sha256']=hashlib.sha256(source_feature.astype('<f8').tobytes()).hexdigest()
                row['clip_retained_exploratory']=row['recomputed_recipient_clip_cosine']>=.85
                row['strict_recipient_quality']=quality_pass(q)
                if row['strict_recipient_quality'] is None:raise ValueError('Invalid retained quality')
                row['delivery']=delivery(row['calls'][1]['result'],row['donor_enrollment'],manifest['profile'],row['arm'])
                row['outcome']='completed';retain(row)
            except Exception as ex:row.update(outcome='failed',error=repr(ex),traceback=traceback.format_exc());retain(row)
        record['summary']=summarize(list(state.values()))
        record['condition_counts']={status:sum(r['outcome']==status for r in state.values()) for status in sorted({r['outcome'] for r in state.values()})}
        record['call_counts']={status:sum(c.get('outcome')==status for r in state.values() for c in r['calls']) for status in ('completed','failed')}
        record['outcome']='completed' if all(r['outcome']=='completed' for r in state.values()) else 'incomplete'
    except BaseException as ex:
        record.update(outcome='interrupted' if isinstance(ex,KeyboardInterrupt) else 'failed',error=repr(ex),traceback=traceback.format_exc())
    finally:
        for row in state.values():
            if row['outcome'] in ('planned','started'):row['outcome']='not_completed_after_stop';retain(row)
        record['duration_seconds']=time.monotonic()-started
        record['output_hashes']={p.name:sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'}
        write(output/'run.json',record)
    return 0 if record['outcome']=='completed' else 2

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output-dir',type=Path);p.add_argument('--prepare',action='store_true');args=p.parse_args()
    if args.prepare:
        if args.output_dir:p.error('--prepare is metadata only')
        if args.manifest.exists():raise ValueError('Refuse manifest overwrite')
        write(args.manifest,configuration());return 0
    if not args.output_dir:p.error('--output-dir required')
    return run(args.manifest,args.output_dir)
if __name__=='__main__':raise SystemExit(main())
