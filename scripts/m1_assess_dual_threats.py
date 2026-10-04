"""Fixed development-only saved-image assessment; no models load on import.

Prepare freezes metadata, not outcomes. Execute only after committing the code
and prepared manifest. Failed/missing conditions keep their planned denominator.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ASSETS = MAIN / '.thesis-build/assets/a6'
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT))
import three_threat_protocol as protocol
import v5_study_protocol as v5

VERSION = 'm1-dual-threat-assessment-v1'
ATTACK_SETTINGS = dict(strengths=list(v5.STRENGTHS), seeds=list(v5.SEEDS), steps=20,
                      guidance_scale=1.0, prompt='', eta=0.0, vae='posterior-mode')
LABELS = ROOT / 'experiments/c4-three-threat-small-v1/semantic-labels.json'
DEPENDENCIES = ['scripts/m1_assess_dual_threats.py', 'scripts/m1_dual_latent.py',
    'scripts/revised_watermark_v5.py', 'scripts/revised_watermark_v4.py',
    'scripts/three_threat_protocol.py', 'scripts/v5_study_protocol.py',
    'scripts/three_threat_models.py', 'scripts/a6_clip_visual.py',
    'scripts/m1_latent_reconstruction.py', 'scripts/check_a6_lpips_assets.py',
    'scripts/verify_science_assets.py', 'research/a6-candidate-model-assets.json',
    'experiments/c4-qim-rgb-development-v1/cohort.json',
    'experiments/c4-three-threat-small-v1/development-expansion.json',
    'experiments/c4-three-threat-small-v1/semantic-labels.json']

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024**2), b''): h.update(block)
    return h.hexdigest()

def write(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    tmp.replace(path)

def append_jsonl(path, value):
    path=Path(path)
    # Preserve a killed process's truncated tail, but separate the next record.
    if path.exists() and path.stat().st_size:
        with path.open('rb') as f:
            f.seek(-1,2); unterminated=f.read(1)!=b'\n'
        if unterminated:
            with path.open('ab') as f: f.write(b'\n')
    with path.open('a',encoding='utf-8') as f:
        f.write(json.dumps(value,allow_nan=False)+'\n')

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args]).decode().strip()

def merge_enrollments(input_dirs, route):
    """Ordered metadata receipts. No duplicate-ID arbitration or image scoring."""
    if isinstance(input_dirs,(str,Path)): input_dirs=[input_dirs]
    if not input_dirs: raise ValueError('At least one enrollment shard required')
    entries, receipts, reference = {}, [], None
    for directory in input_dirs:
        runpath=Path(directory).resolve()/'run.json'
        source=json.loads(runpath.read_text())
        if source.get('data_split')!='development' or source['config']['owner']!=v5.OWNERS[0]:
            raise ValueError('Development enrollment with owner-alpha required')
        if route not in source['config']['routes']: raise ValueError('Selected route absent from enrollment configuration')
        code_files={p:v for p,v in source.get('committed_files',{}).items()
                    if p.startswith('scripts/') or p=='research/a6-candidate-model-assets.json'}
        signature={'schema':source.get('schema'),'profile':source.get('profile'),'code_files':code_files}
        if not source.get('commit') or not signature['profile'] or not code_files:
            raise ValueError('Enrollment code/profile provenance missing')
        if reference is None: reference=signature
        elif signature!=reference: raise ValueError('Shard code version/profile mismatch')
        receipt=dict(path=str(runpath),sha256=sha(runpath),commit=source['commit'],
                     outcome=source.get('outcome'),case_ids=[],order=len(receipts))
        for case in source.get('cases',[]):
            ident=case['id']
            if ident not in reservation(): raise ValueError('Unreserved enrollment ID')
            if ident in entries: raise ValueError('Overlapping enrollment IDs are forbidden, including incomplete cases')
            entries[ident]=dict(case,input_run=str(runpath))
            receipt['case_ids'].append(ident)
        receipts.append(receipt)
    return entries, receipts, reference

def planned(labels):
    # Inherit exact original pairings/public transfers; extend T3 to all twelve.
    old = v5.inventory(labels)
    rows = [r for r in old if r['axis'] in ('T4', 'T5', 'T5-transfer')]
    for ident in protocol.EXPANDED_IDS:
        for control in ('C0', 'C1'):
            rows.append(dict(id=f'clean-{ident}-{control}', axis='clean', source_id=ident, control=control))
            rows.append(dict(id=f'vae-{ident}-{control}', axis='T3', source_id=ident,
                             control=control, dose='vae_mode', seed=None, strength=None))
            for strength in v5.STRENGTHS:
                for seed in v5.SEEDS:
                    rows.append(dict(id=f't3-{ident}-{strength}-{seed}-{control}', axis='T3',
                        source_id=ident, control=control, dose='diffusion', strength=strength, seed=seed))
    if len(rows) != 489 or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Fixed 489-condition inventory violated')
    return rows

def reservation():
    original = json.loads((ROOT / DEPENDENCIES[-3]).read_text())['cases']
    extra = json.loads((ROOT / DEPENDENCIES[-2]).read_text())['new_cases']
    return {c['source_id']: c['raw_sha256'] for c in original + extra}

def validate(manifest):
    if manifest.get('schema') != VERSION or manifest.get('data_split') != 'development':
        raise ValueError('Reserved development manifest required')
    if manifest.get('route') not in ('pure-decoder', 'hybrid-source-bypass'):
        raise ValueError('Explicit pure-decoder or hybrid-source-bypass route required')
    if manifest.get('owners') != list(v5.OWNERS) or manifest.get('source_ids') != list(protocol.EXPANDED_IDS):
        raise ValueError('Exact owner roster and all twelve reserved IDs required')
    if manifest.get('assets') != str(ASSETS): raise ValueError('Explicit pinned MAIN assets required')
    if manifest.get('attack_settings') != ATTACK_SETTINGS: raise ValueError('Attack schedule must stay frozen')
    if set(manifest.get('dependencies', {})) != set(DEPENDENCIES): raise ValueError('Exact implementation locks required')
    receipts=manifest.get('input_runs')
    if receipts:
        if [r['order'] for r in receipts]!=list(range(len(receipts))): raise ValueError('Shard order must be explicit')
        all_ids=[i for r in receipts for i in r['case_ids']]
        if len(all_ids)!=len(set(all_ids)) or any(i not in protocol.EXPANDED_IDS for i in all_ids):
            raise ValueError('Duplicate/unreserved shard IDs')
        if len({r['path'] for r in receipts})!=len(receipts):raise ValueError('Duplicate shard receipt')
    cases = manifest.get('cases', [])
    if [c['id'] for c in cases] != list(protocol.EXPANDED_IDS): raise ValueError('Missing/duplicate planned ID')
    for case in cases:
        if case.get('status') not in ('available', 'missing'): raise ValueError('Invalid enrollment status')
        if case.get('raw_sha256') != reservation()[case['id']]: raise ValueError('Raw reservation hash differs')
        if case['status'] == 'available' and set(case['images']) != {'source', 'C0', 'C1'}:
            raise ValueError('Available case requires three frozen images')
        for item in case.get('images',{}).values():
            enrolled_run=case.get('input_run',manifest.get('input_run'))
            if not enrolled_run or not Path(item['path']).is_absolute() or not Path(item['path']).resolve().is_relative_to(Path(enrolled_run).resolve().parent):
                raise ValueError('Image must be an absolute artifact under enrollment run')
            if manifest.get('input_runs') and enrolled_run not in [r['path'] for r in manifest['input_runs']]:
                raise ValueError('Case enrollment run not in frozen receipts')
            if receipts and case['id'] not in next(r['case_ids'] for r in receipts if r['path']==enrolled_run):
                raise ValueError('Case not in declared enrollment shard')
    if manifest.get('labels_sha256') != sha(LABELS): raise ValueError('Frozen semantic labels changed')
    return planned(json.loads(LABELS.read_text())['pairs'])

def prepare(input_dir, route, destination):
    if Path(destination).exists(): raise ValueError('Refuse to overwrite a frozen manifest')
    entries, receipts, reference=merge_enrollments(input_dir,route)
    reserved = reservation()
    cases = []
    for ident in protocol.EXPANDED_IDS:
        c = entries.get(ident, {})
        routes = [r for r in c.get('routes', []) if r['route'] == route]
        row = dict(id=ident, raw_sha256=reserved[ident], status='missing', reason='not_enrolled_or_route_incomplete')
        if len(routes) > 1: raise ValueError('Duplicate enrollment route')
        if routes and all(k in routes[0] for k in ('C0_matched', 'C1')) and c.get('source_png'):
            if c.get('raw_sha256') != reserved[ident]: raise ValueError('Enrollment raw hash differs')
            images = {'source': {'path': c['source_png'], 'sha256': c['source_png_sha256']},
                'C0': {'path': routes[0]['C0_matched']['png_path'], 'sha256': routes[0]['C0_matched']['png_sha256']},
                'C1': {'path': routes[0]['C1']['png_path'], 'sha256': routes[0]['C1']['png_sha256']}}
            for item in images.values():
                if not Path(item['path']).is_absolute() or sha(item['path']) != item['sha256']:
                    raise ValueError('Enrollment image hash/path differs')
            row.update(status='available', images=images, enrollment_outcome=c.get('outcome'),
                       route_outcome=routes[0].get('outcome'),input_run=c['input_run'])
            row.pop('reason')
        elif c:
            row.update(input_run=c['input_run'],enrollment_outcome=c.get('outcome'))
        cases.append(row)
    manifest = dict(schema=VERSION, data_split='development', route=route, owners=list(v5.OWNERS),
        source_ids=list(protocol.EXPANDED_IDS), assets=str(ASSETS), input_runs=receipts,
        input_commits=[r['commit'] for r in receipts], enrollment_code_files=reference['code_files'],profile=reference['profile'],
        labels_sha256=sha(LABELS), cases=cases,
        scope='full-development' if all(c['status']=='available' for c in cases) else 'pilot-with-missing-planned-IDs',
        dependencies={p: sha(ROOT / p) for p in DEPENDENCIES},
        attack_settings=ATTACK_SETTINGS,
        human_visual_verdict=None)
    validate(manifest)
    write(destination, manifest)

def verified_images(manifest):
    for case in manifest['cases']:
        for item in case.get('images', {}).values():
            if sha(item['path']) != item['sha256']: raise ValueError('Frozen enrollment image changed')

def read_rgb(path):
    import numpy as np
    from PIL import Image
    with Image.open(path) as image:
        if image.mode != 'RGB' or image.size != (512, 512): raise ValueError('Expected saved RGB8 512x512')
        return np.asarray(image).copy()

def complete_artifact(row, root):
    if row.get('outcome') != 'completed': return False
    item = row.get('image')
    if not item: return row.get('axis') == 'T5' and set(row.get('components',{}))=={'C0','C1'}
    path = Path(item['path']).resolve()
    if not path.is_relative_to(root.resolve()): return False
    return (path.is_file() and sha(path) == item['sha256'] and
        [d.get('owner') for d in row.get('detections',[])]==list(v5.OWNERS) and
        all(isinstance(d.get('result'),dict) for d in row['detections']) and
        'quality_vs_same_arm_original' in row and 'quality_vs_source' in row and
        (row.get('axis')!='clean' or row.get('control')!='C1' or 'paired_family_quality' in row))

def assess(manifest_path, output, resume=False):
    manifest_path, output = Path(manifest_path).resolve(), Path(output).resolve()
    if not output.is_relative_to((MAIN / '.thesis-build/dev-runs').resolve()):
        raise ValueError('Output must be MAIN dev-runs')
    if output.exists() and not resume: raise ValueError('Fresh output required unless --resume')
    if resume and not (output / 'run.json').is_file(): raise ValueError('Missing resume run.json')
    output.mkdir(parents=True, exist_ok=resume)
    started = time.monotonic()
    commit = git('rev-parse', 'HEAD')
    record = dict(schema=VERSION, commit=commit, command=sys.argv, config={'manifest':str(manifest_path)},
        manifest_sha256=sha(manifest_path), data_split='development', seeds=list(v5.SEEDS),
        duration_seconds=0, outcome='started', planned_conditions=489, human_visual_verdict=None)
    if resume:
        old = json.loads((output / 'run.json').read_text())
        if old['manifest_sha256'] != record['manifest_sha256'] or old['commit'] != commit:
            raise ValueError('Resume must retain exact commit and manifest')
        record['previous_runs'] = old.get('previous_runs', []) + [old]
    write(output / 'run.json', record)
    def event(value):
        append_jsonl(output/'journal.jsonl',dict(elapsed_seconds=time.monotonic()-started, **value))
    state = {}
    if (output / 'rows.jsonl').exists():
        for line in (output / 'rows.jsonl').read_text().splitlines():
            try:
                row = json.loads(line); state[row['id']] = row
            except json.JSONDecodeError: event({'phase':'damaged_journal_line', 'line_sha256':hashlib.sha256(line.encode()).hexdigest()})
    def retain(row):
        state[row['id']] = row
        append_jsonl(output/'rows.jsonl',row)
        write(output / 'conditions.json', list(state.values()))
    try:
        manifest = json.loads(manifest_path.read_text()); rows = validate(manifest)
        # Inventory first, before hashing assets or loading any model.
        for spec in rows:
            if spec['id'] not in state: retain(dict(**spec, outcome='planned', human_visual_verdict=None))
        for name, digest in manifest['dependencies'].items():
            if sha(ROOT/name) != digest: raise ValueError('Dependency changed: '+name)
            if git('hash-object','--path='+name,str(ROOT/name)) != git('rev-parse','HEAD:'+name):
                raise ValueError('Uncommitted dependency: '+name)
        relative = manifest_path.relative_to(ROOT).as_posix()
        if git('hash-object','--path='+relative,str(manifest_path)) != git('rev-parse','HEAD:'+relative):
            raise ValueError('Manifest must be committed before scientific execution')
        receipts=manifest.get('input_runs') or [{'path':manifest['input_run'],'sha256':manifest['input_run_sha256']}]
        for receipt in receipts:
            if sha(receipt['path']) != receipt['sha256']: raise ValueError('Enrollment run changed')
        verified_images(manifest)
        import numpy as np
        from PIL import Image
        import torch
        import three_threat_models as models
        models.block_network()
        receipt, package = models.verify_assets(ASSETS, ROOT/'research/a6-candidate-model-assets.json')
        record.update(asset_receipt=receipt, scope=manifest['scope'], route=manifest['route'],
            profile=manifest['profile'], environment={'python':sys.version,'torch':torch.__version__,
                'packages':{p:importlib.metadata.version(p) for p in ('numpy','scipy','Pillow','diffusers','transformers','lpips')}},
            attack_settings=manifest['attack_settings'], ddim_config=models.DDIM_CONFIG,
            input_runs=receipts,
            lpips_learned_sha256=sha(package/'weights/v0.1/alex.pth'))
        write(output/'run.json',record)
        images = {c['id']:{k:read_rgb(v['path']) for k,v in c['images'].items()}
                  for c in manifest['cases'] if c['status']=='available'}
        pending = []
        event({'phase':'CPU_transfer_stage_started'})
        def persist(row, rgb):
            filename = row['id']+'-'+str(time.time_ns())+'.png'
            path = output / filename; Image.fromarray(np.asarray(rgb,dtype=np.uint8)).save(path)
            row.update(image={'path':str(path),'sha256':sha(path)}, outcome='attack_persisted')
            retain(row)
        for spec in rows:
            old = state[spec['id']]
            if complete_artifact(old, output): continue
            row = dict(spec, outcome='started', human_visual_verdict=None)
            dependencies = [spec[k] for k in ('source_id','donor_id','recipient_id','left','right') if k in spec]
            missing = [i for i in dependencies if i not in images]
            if missing:
                row.update(outcome='missing_enrollment', missing_ids=missing); retain(row); continue
            if old.get('outcome') == 'attack_persisted' and old.get('image'):
                p=Path(old['image']['path']).resolve()
                if p.is_relative_to(output) and p.exists() and sha(p)==old['image']['sha256']:
                    continue
            retain(row)
            try:
                if spec['axis']=='clean': persist(row, images[spec['source_id']][spec['control']])
                elif spec['axis'] in ('T4','T5-transfer'):
                    donor,recipient=images[spec['donor_id']],images[spec['recipient_id']]
                    if spec['arm']=='clean_donor_residual':
                        rgb=protocol.residual_transfer(recipient['C0'].tolist(),donor['C1'].tolist(),donor['C0'].tolist(),spec['scale'])
                    else:
                        donor_rgb=donor['C0'] if spec['arm']=='unmarked_projection_sham' else donor['C1']
                        rgb=v5.transfer(recipient['C0'].tolist(),donor_rgb.tolist(),manifest['profile'],spec['arm'])
                    persist(row,rgb)
                elif spec['axis']=='T3': pending.append(spec)
                else: retain(row)  # T5 component diagnostics are a later CPU stage.
            except Exception as error:
                row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc());retain(row)
        # CPU transfers complete before CUDA allocation. Each attack is durable.
        if pending:
            event({'phase':'GPU_attack_stage_started','conditions':len(pending)})
            torch.cuda.set_per_process_memory_fraction(min(1.0, 10*1024**3/torch.cuda.get_device_properties(0).total_memory))
            pipeline=models.load_regenerator(ASSETS)
            for spec in pending:
                row=dict(spec,outcome='started',human_visual_verdict=None)
                retain(row)
                try:
                    rgb=images[spec['source_id']][spec['control']]
                    torch.cuda.synchronize(); tick=time.monotonic()
                    with torch.inference_mode():
                        if spec['dose']=='vae_mode':
                            t=pipeline.image_processor.preprocess(Image.fromarray(rgb)).to('cuda',dtype=pipeline.vae.dtype)
                            z=pipeline.vae.encode(t).latent_dist.mode()
                            decoded=pipeline.vae.decode(z,return_dict=False)[0]
                            array=pipeline.image_processor.postprocess(decoded,output_type='np')
                            array,flags=pipeline.run_safety_checker(array,torch.device('cuda'),pipeline.text_encoder.dtype)
                            if flags is None or len(flags)!=1 or bool(flags[0]): raise RuntimeError('VAE safety verdict missing/blocked')
                            attacked=Image.fromarray(np.rint(np.clip(array[0],0,1)*255).astype(np.uint8))
                        else:
                            result=pipeline(prompt='',negative_prompt='',image=Image.fromarray(rgb),
                                strength=spec['strength'],num_inference_steps=20,eta=0.0,guidance_scale=1.0,
                                generator=torch.Generator(device='cuda').manual_seed(spec['seed']),
                                num_images_per_prompt=1,output_type='pil',return_dict=True)
                            attacked=models.validate_generated(result)
                    torch.cuda.synchronize();row['attack_seconds']=time.monotonic()-tick
                    persist(row,np.asarray(attacked))
                except Exception as error:
                    row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc());retain(row)
            del pipeline; torch.cuda.empty_cache()
        event({'phase':'CPU_evaluation_stage_started'})
        from scripts.m1_dual_latent import blind_detect, codec
        from scripts.m1_latent_reconstruction import quality
        from a6_clip_visual import load_visual_encoder
        encoder,transform=load_visual_encoder(ASSETS/'clip/ViT-B-32.pt',device='cpu')
        metric=models.load_lpips(ASSETS,package)
        def feature(rgb): return models.clip_feature(encoder,transform,rgb).reshape(-1).tolist()
        cache={}
        def components(ident,control):
            key=(ident,control)
            if key not in cache:
                rgb=images[ident][control];f=feature(rgb)
                cache[key]={'feature':f,'semantic':codec.semantic_code(f,profile=manifest['profile']),
                    'instance':codec.perceptual_hash(codec.luminance_from_rgb(rgb.tolist()),profile=manifest['profile'])}
            return cache[key]
        def q(left,right):
            result=quality(left,right);result['lpips']=models.lpips_score(metric,left,right)
            result['clip_cosine']=float(np.dot(feature(left),feature(right)))
            result['quality_admissible']=(result['psnr_infinite'] or result['psnr_db']>35) and result['ssim_rgb']>.9 and result['lpips']<.1
            result['clip_retained_exploratory']=result['clip_cosine']>=.85
            return result
        for spec in rows:
            row=state[spec['id']]
            if complete_artifact(row,output) or row['outcome'] in ('missing_enrollment','failed'): continue
            try:
                if spec['axis']=='T5':
                    row['components']={}
                    for control in ('C0','C1'):
                        left,right=components(spec['left'],control),components(spec['right'],control)
                        row['components'][control]={'semantic_hamming':v5.distance(left['semantic'],right['semantic']),
                            'instance_hamming':v5.distance(left['instance'],right['instance']),
                            'clip_cosine':float(np.dot(left['feature'],right['feature']))}
                    row['semantic_label_source']='frozen agent labels; no human verdict'
                else:
                    rgb=read_rgb(row['image']['path']); tick=time.monotonic();f=feature(rgb)
                    row['suspect_clip_seconds']=time.monotonic()-tick
                    row['suspect_clip_sha256']=hashlib.sha256(np.asarray(f,dtype='<f8').tobytes()).hexdigest()
                    row['detections']=[]
                    for owner in v5.OWNERS:
                        tick=time.monotonic()
                        detected=blind_detect(rgb,owner,manifest['profile'],lambda suspect:f)
                        row['detections'].append({'owner':owner,'result':detected,'seconds':time.monotonic()-tick})
                    ref=spec.get('recipient_id',spec.get('source_id'))
                    arm=spec.get('control','C0')
                    row['quality_vs_same_arm_original']=q(images[ref][arm],rgb)
                    row['quality_vs_source']=q(images[ref]['source'],rgb)
                    if spec['axis']=='clean' and arm=='C1':
                        row['paired_family_quality']=q(images[ref]['C0'],rgb)
                        row['source_preservation_quality']=row['quality_vs_source']
                        left,right=components(ref,'C0'),components(ref,'C1')
                        row['same_instance_component_drift']={'semantic_hamming':v5.distance(left['semantic'],right['semantic']),
                            'instance_hamming':v5.distance(left['instance'],right['instance'])}
                    row['owner_roster_policy']='four independent unchanged-verifier calls; no fitted roster threshold'
                row['outcome']='completed';retain(row)
            except Exception as error:
                row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc());retain(row)
        record['condition_counts']={status:sum(r['outcome']==status for r in state.values()) for status in sorted({r['outcome'] for r in state.values()})}
        record['outcome']='completed' if len(state)==489 and all(r['outcome']=='completed' for r in state.values()) else 'incomplete'
    except BaseException as error:
        record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error),traceback=traceback.format_exc())
        raise
    finally:
        record['duration_seconds']=time.monotonic()-started
        record['output_hashes']={p.name:sha(p) for p in (output/'rows.jsonl',output/'conditions.json',output/'journal.jsonl') if p.exists()}
        write(output/'run.json',record)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--output-dir')
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--input-dir',action='append',help='Repeat in declared chronological order; overlapping IDs rejected')
    parser.add_argument('--route',choices=('pure-decoder','hybrid-source-bypass'))
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    if args.prepare:
        if not args.input_dir or not args.route or args.output_dir or args.resume: parser.error('--prepare needs --input-dir and explicit --route only')
        prepare(args.input_dir,args.route,args.manifest)
    else:
        if not args.output_dir or args.input_dir or args.route: parser.error('Execute needs --output-dir; route is frozen in manifest')
        assess(args.manifest,args.output_dir,args.resume)

if __name__=='__main__': main()
