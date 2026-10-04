"""Independent B-LW1-P1 arithmetic/readout probe; no generation or inversion.

Opaque worker inputs exclude reference payloads, original noise and source labels.
This is a restricted data-flow check, not an adversarial filesystem sandbox.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import inspect
import json
import math
import re
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ASSETS=MAIN/'.thesis-build/assets/a6'
VERSION='m1-gs-lightweight-positive-probe-v1'
CONFIG={'channels':['clean','vae','regen-0.4-seed0'],'presence_matches':180,'precision':'float16',
    'posterior':'mode','batch_size':1,'scale':.18215,'shape':[1,4,64,64],
    'gpu_budget_bytes':10*1024**3,'artifact_budget_bytes':100*1024**2,'seconds_cap':120,
    'readout_nonce_count':4,'column_roll':1}
LOCKS={'lightweight_run_sha256':'55b9edf853195abbd0c282442547442266d48570d5635da98e390fc89bd8789a',
    'lightweight_conditions_sha256':'5449d453af2e8a11855135105104e9e72fb15d77394438211bdb17cc5b161935'}

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for raw in iter(lambda:f.read(1024**2),b''):h.update(raw)
    return h.hexdigest()

def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8');temp.replace(path)

def whitening(key,nonce):
    import numpy as np
    rawkey,rawn=bytes.fromhex(key),bytes.fromhex(nonce)
    if len(rawkey)!=32 or len(rawn)!=12:raise ValueError('Public key/nonce byte lengths differ')
    raw=hashlib.shake_256(b'm1-gs-whitening-v1'+rawkey+rawn).digest(2048)
    return np.unpackbits(np.frombuffer(raw,dtype=np.uint8)).reshape(1,4,64,64)

def independent_votes(signs,key,nonce):
    """Explicit (channel,a+8*r,b+8*s) arithmetic, independent of GS helpers."""
    import numpy as np
    signs=np.asarray(signs)
    if signs.shape!=(1,4,64,64) or not np.isin(signs,[0,1]).all():raise ValueError('Binary sign tensor required')
    mask=whitening(key,nonce);votes=np.zeros((4,8,8),dtype=np.uint8)
    for channel in range(4):
        for a in range(8):
            for b in range(8):
                count=0
                for r in range(8):
                    for s in range(8):
                        row,col=a+8*r,b+8*s
                        count+=int(signs[0,channel,row,col])^int(mask[0,channel,row,col])
                votes[channel,a,b]=count
    return {'votes':votes.reshape(-1).tolist(),'bits':(votes>32).astype(np.uint8).reshape(-1).tolist(),
        'ties':int((votes==32).sum())}

def evaluate(result,reference):
    import numpy as np
    reference=np.asarray(reference)
    if reference.shape!=(4,8,8) or not np.isin(reference,[0,1]).all():raise ValueError('256 reference bits required')
    if len(result['bits'])!=256 or len(result['votes'])!=256:raise ValueError('256 emitted votes/bits required')
    if any(type(v)!=int or v not in (0,1) for v in result['bits']) or type(result['ties'])!=int:raise ValueError('Malformed bit/tie type')
    if any(type(v)!=int or not 0<=v<=64 for v in result['votes']):raise ValueError('Malformed vote count')
    if result['bits']!=[int(v>32) for v in result['votes']] or result['ties']!=result['votes'].count(32):raise ValueError('Vote/bit/tie mismatch')
    matches=sum(int(a)==int(b) for a,b in zip(result['bits'],reference.reshape(-1)))
    return {'matches':matches,'bit_accuracy':matches/256,'present':matches>=180,'exact':matches==256}

def message(seed):
    import numpy as np
    raw=hashlib.shake_256(b'm1-gs-payload-v1'+str(seed).encode()).digest(32)
    return np.unpackbits(np.frombuffer(raw,dtype=np.uint8)).reshape(4,8,8)

def nonce_for(seed):return hashlib.sha256(b'm1-gs-nonce-v1'+str(seed).encode()).hexdigest()[:24]

def initial_noises(seed,key):
    import numpy as np
    base=np.random.default_rng(seed).standard_normal((1,4,64,64)).astype(np.float32)
    reference=message(seed);repeated=np.empty((1,4,64,64),dtype=np.uint8)
    for channel in range(4):
        for row in range(64):
            for col in range(64):repeated[0,channel,row,col]=reference[channel,row%8,col%8]
    signed=repeated^whitening(key,nonce_for(seed))
    marked=(np.abs(base)*(2*signed.astype(np.float32)-1)).astype(np.float16)
    return base.astype(np.float16),marked

def synthetic_selfcheck():
    import numpy as np
    key='01'*32;nonce='02'*12;ref=message(1000);mask=whitening(key,nonce)
    signs=np.tile(ref,(1,8,8)).reshape(1,4,64,64)^mask
    exact=independent_votes(signs,key,nonce)
    changed=signs.copy();changed[0,0,0,0]^=1
    changed_votes=independent_votes(changed,key,nonce)['votes']
    expected=exact['votes'].copy();expected[0]+=1 if expected[0]==0 else -1
    plain=np.zeros((1,4,64,64),dtype=np.uint8);plain[:,:,0:32,:]=1
    tied=independent_votes(plain^mask,key,nonce)
    algebra=zero_aware_algebra(signs,1-signs,np.zeros_like(signs,dtype=bool),key,nonce)
    checks={'known_message':exact['bits']==ref.reshape(-1).tolist(),
        'one_coordinate':changed_votes==expected,'ties_decode_zero':tied['ties']==256 and not any(tied['bits']),
        'complement':all(algebra[k] for k in ('votes_complement_zero_adjusted','nonzero_sign_complement','zero_signs_remain_zero','nonzero_nontie_bits_complement'))}
    if not all(checks.values()):raise RuntimeError('Independent synthetic arithmetic selfcheck failed')
    return checks

def zero_aware_algebra(signs,negative,zeros,key,nonce):
    import numpy as np
    own=independent_votes(signs,key,nonce);neg=independent_votes(negative,key,nonce)
    delta=((2*whitening(key,nonce).astype(np.int16)-1)*zeros).reshape(4,8,8,8,8).sum(axis=(1,3)).reshape(-1)
    expected=64-np.asarray(own['votes'])+delta
    return {'votes_complement_zero_adjusted':bool(np.array_equal(expected,np.asarray(neg['votes']))),
        'zero_signs_remain_zero':bool(np.all(signs[zeros]==0) and np.all(negative[zeros]==0)),
        'nonzero_nontie_bits_complement':bool(np.all((np.asarray(neg['bits'])==1-np.asarray(own['bits']))[(delta==0)&(np.asarray(own['votes'])!=32)])),
        'zero_coordinate_count':int(zeros.sum()),'zero_vote_adjustments':delta.tolist(),
        'zero_affected_bits':int((zeros.reshape(4,8,8,8,8).sum(axis=(1,3))>0).sum()),
        'nonzero_sign_complement':bool(np.array_equal(negative[~zeros],1-signs[~zeros]))}

def sealed_validate(sealed):
    if set(sealed)!={'schema_version','config','keys','nonces','images'} or sealed['schema_version']!=VERSION or sealed['config']!=CONFIG:
        raise ValueError('Sealed reader schema/config differs')
    if set(sealed['keys'])!={'correct','wrong'} or len(sealed['nonces'])!=4 or len(set(sealed['nonces']))!=4:raise ValueError('Fixed key/nonce roster required')
    if len(sealed['images'])!=24 or len({i['opaque_id'] for i in sealed['images']})!=24:raise ValueError('Fixed opaque24 inventory required')
    for image in sealed['images']:
        if set(image)!={'opaque_id','path','sha256'}:raise ValueError('Reader input contains forbidden evaluator field')
        if not re.fullmatch(r'image-[0-9a-f]{64}-[0-9]{2}',image['opaque_id']) or not re.fullmatch(r'[0-9a-f]{64}',image['sha256']):raise ValueError('Opaque identity/hash malformed')
        if not Path(image['path']).is_absolute():raise ValueError('Absolute opaque path required')
        if Path(image['path']).name!=image['opaque_id']+'.png':raise ValueError('Opaque file name required')
    for key in sealed['keys'].values():
        for nonce in sealed['nonces']:whitening(key,nonce)

def readout_worker(sealed_path,expected_hash,output):
    """Reads only sealed reader inputs. It never opens the evaluator mapping."""
    if sha(sealed_path)!=expected_hash:raise ValueError('Sealed input hash mismatch')
    sealed=json.loads(sealed_path.read_text(encoding='utf-8'));sealed_validate(sealed)
    if output.resolve()!=sealed_path.parent.resolve()/'readout' or any(Path(i['path']).resolve().parent!=sealed_path.parent.resolve()/'inputs' for i in sealed['images']):raise ValueError('Reader boundary paths differ')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    rows=[{'opaque_id':i['opaque_id'],'image_sha256':i['sha256'],'outcome':'planned'} for i in sealed['images']]
    record={'schema_version':VERSION,'config':CONFIG,'command':sys.argv,'data_split':'synthetic',
        'seeds':[],'outcome':'started','rows':rows,'sealed_sha256':expected_hash,'human_visual_verdict':None}
    record['commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    record['script_sha256']=sha(__file__)
    write(output/'run.json',record)
    try:
        sys.path.insert(0,str(ROOT/'scripts'))
        from three_threat_models import block_network,verify_assets
        block_network()
        import numpy as np
        import torch
        from PIL import Image
        from diffusers import AutoencoderKL,image_processor
        if not torch.cuda.is_available():raise RuntimeError('CUDA required; no CPU inference substitution')
        assets,_=verify_assets(ASSETS,ROOT/'research/a6-candidate-model-assets.json');record['asset_receipt']=assets
        torch.cuda.set_per_process_memory_fraction(min(1.,CONFIG['gpu_budget_bytes']/torch.cuda.get_device_properties(0).total_memory))
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        vae=AutoencoderKL.from_pretrained(ASSETS/'sd15-fp16/vae',variant='fp16',use_safetensors=True,
            local_files_only=True,torch_dtype=torch.float16).eval().requires_grad_(False).to('cuda')
        if float(vae.config.scaling_factor)!=CONFIG['scale']:raise ValueError('VAE scale differs')
        processor=image_processor.VaeImageProcessor(vae_scale_factor=2**(len(vae.config.block_out_channels)-1))
        record['preprocessing']={'config':dict(processor.config),'module_sha256':sha(inspect.getfile(image_processor))}
        record['environment']={'python':sys.version,**{p:importlib.metadata.version(p) for p in ('torch','numpy','diffusers','Pillow')}}
        for image,row in zip(sealed['images'],rows):
            if time.monotonic()-started>=CONFIG['seconds_cap']:break
            tick=time.monotonic()
            try:
                if sha(image['path'])!=image['sha256']:raise ValueError('Sealed PNG hash differs')
                with Image.open(image['path']) as rgb:
                    if rgb.mode!='RGB' or rgb.size!=(512,512):raise ValueError('Native RGB512 required')
                    rgb.load();torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize()
                    x=processor.preprocess(rgb).to('cuda',dtype=torch.float16)
                    with torch.inference_mode():u=vae.encode(x).latent_dist.mode();z=u*vae.config.scaling_factor
                    torch.cuda.synchronize();encode_seconds=time.monotonic()-tick
                if tuple(z.shape)!=(1,4,64,64) or not bool(torch.isfinite(z).all()) or not bool(torch.isfinite(u).all()):raise ValueError('Malformed/nonfinite latent')
                latent=z.float().cpu().numpy();signs=(latent>0).astype(np.uint8);negative=(-latent>0).astype(np.uint8);zeros=latent==0
                prefix=output/image['opaque_id'];files={}
                for label,value in (('signs',signs),('latent',latent)):
                    path=prefix.with_suffix('.'+label+'.bin');path.write_bytes(value.tobytes());files[label]={'path':path.name,'sha256':sha(path),'dtype':str(value.dtype),'shape':list(value.shape)}
                queries={}
                for nonce in sealed['nonces']:
                    key=sealed['keys']['correct']
                    queries[nonce]={'correct':independent_votes(signs,key,nonce),
                        'wrong':independent_votes(signs,sealed['keys']['wrong'],nonce),
                        'shifted':independent_votes(np.roll(signs,1,axis=3),key,nonce),
                        'negative':independent_votes(negative,key,nonce),
                        'algebra':zero_aware_algebra(signs,negative,zeros,key,nonce)}
                row.update(outcome='completed',files=files,nonce_queries=queries,encode_seconds=encode_seconds,
                    total_seconds=time.monotonic()-tick,vae_encodes=1,unet_evaluations=0,text_encoder_evaluations=0,
                    scaling_factor=float(vae.config.scaling_factor),posterior_zero_count=int((u==0).sum()),
                    scaled_zero_count=int((z==0).sum()),sign_changes_after_scaling=int(((u>0)!=(z>0)).sum()),
                    peak_allocated_bytes=torch.cuda.max_memory_allocated())
                if row['peak_allocated_bytes']>CONFIG['gpu_budget_bytes']:raise RuntimeError('GPU cap exceeded')
            except Exception as error:row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc())
            with (output/'rows.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(row,allow_nan=False)+'\n')
            write(output/'run.json',record)
            if sum(p.stat().st_size for p in output.parent.rglob('*') if p.is_file())>CONFIG['artifact_budget_bytes']:raise RuntimeError('Artifact cap exceeded')
        record['outcome']='completed' if all(r['outcome']=='completed' for r in rows) else 'incomplete'
    except (Exception,KeyboardInterrupt) as error:record.update(outcome='failed',error=repr(error),traceback=traceback.format_exc())
    finally:
        for row in rows:
            if row['outcome']=='planned':row['outcome']='not_completed_after_stop'
        record['duration_seconds']=time.monotonic()-started;write(output/'run.json',record)
    return 0 if record['outcome']=='completed' else 1

def prepare(native_dir,lw_dir,output):
    # Metadata-only: old bit/vote references remain solely in evaluator-map.json.
    if sha(lw_dir/'run.json')!=LOCKS['lightweight_run_sha256'] or sha(lw_dir/'conditions.json')!=LOCKS['lightweight_conditions_sha256']:
        raise ValueError('Exact positive source receipt differs')
    lw=json.loads((lw_dir/'run.json').read_text(encoding='utf-8'))
    for name,receipt in lw['source_receipts'].items():
        if Path(name).name!=name or sha(native_dir/name)!=receipt['sha256']:raise ValueError('Native source receipt differs: '+name)
    for name,digest in lw['output_hashes'].items():
        if sha(lw_dir/name)!=digest:raise ValueError('LW output hash mismatch: '+name)
    generating=json.loads((ROOT/'research/m1-gs-synthetic.json').read_text(encoding='utf-8'))
    native=json.loads((native_dir/'run.json').read_text(encoding='utf-8'))
    if native.get('manifest_sha256')!=sha(ROOT/'research/m1-gs-synthetic.json') or native['commit']!='6a46faad51d91b285d00bbb6b2a4563ef681c11b':raise ValueError('Native manifest/commit differs')
    artifacts=json.loads((native_dir/'artifacts.json').read_text(encoding='utf-8'))
    for name,digest in native['completed_file_sha256'].items():
        if sha(native_dir/name)!=digest:raise ValueError('Native completed receipt mismatch')
    rows=json.loads((lw_dir/'conditions.json').read_text(encoding='utf-8'))
    selected=[r for r in rows if r['channel'] in CONFIG['channels']]
    expected={(f'prompt-{i}',arm,channel) for i in range(4) for arm in ('C0','C1') for channel in CONFIG['channels']}
    if len(selected)!=24 or {(r['case'],r['arm'],r['channel']) for r in selected}!=expected:raise ValueError('Exact24 condition identities required')
    mapping=[];images=[];inputs=output/'inputs';inputs.mkdir()
    for index,row in enumerate(sorted(selected,key=lambda r:(r['image_sha256'],r['id']))):
        if Path(row['native']['image']).name!=row['native']['image']:raise ValueError('Native PNG path must be local basename')
        path=native_dir/row['native']['image'];digest=row['image_sha256']
        if row['outcome']!='completed' or artifacts.get(path.name,{}).get('sha256')!=digest or sha(path)!=digest:raise ValueError('Native/LW PNG hash mismatch')
        opaque=f'image-{digest}-{index:02d}';copy=inputs/(opaque+'.png');copy.write_bytes(path.read_bytes())
        images.append({'opaque_id':opaque,'path':str(copy),'sha256':digest})
        mapping.append({'opaque_id':opaque,'source_row':row})
    sealed={'schema_version':VERSION,'config':CONFIG,'keys':{'correct':generating['development_key_hex'],'wrong':generating['wrong_key_hex']},
        'nonces':[nonce_for(seed) for seed in range(1000,1004)],'images':images}
    sealed_validate(sealed);write(output/'sealed-input.json',sealed)
    write(output/'evaluator-map.json',{'entries':mapping,'selfchecks':lw['reconstructed_source_noise_selfchecks'],'keys':sealed['keys']})
    for label,directory,names in (('native',native_dir,('run.json','artifacts.json','rows.jsonl','rows-receipt.json')),('lightweight',lw_dir,('run.json','conditions.json'))):
        for name in names:(output/(label+'-'+name)).write_bytes((directory/name).read_bytes())
    return {'native_commit':native['commit'],'lightweight_commit':lw['commit'],
        'source_receipts':{p.name:sha(p) for p in output.iterdir() if p.is_file()}}

def transport(latent,noise):
    import numpy as np
    a=latent.astype(np.float64).reshape(-1);b=noise.astype(np.float64).reshape(-1)
    norm=float(np.linalg.norm(a)*np.linalg.norm(b))
    return {'sign_agreement':float(((latent>0)==(noise>0)).mean()),'cosine':float(a@b/norm) if norm else None}

def evaluate_emitted(output):
    import numpy as np
    # Mapping is opened only after the worker has finished emitting its outputs.
    mapping=json.loads((output/'evaluator-map.json').read_text(encoding='utf-8'))
    emitted=json.loads((output/'readout/run.json').read_text(encoding='utf-8'))
    if len(emitted['rows'])!=24 or len({r['opaque_id'] for r in emitted['rows']})!=24:raise ValueError('Worker denominator/duplicate differs')
    index={r['opaque_id']:r for r in emitted['rows']};evaluated=[]
    key=mapping['keys']['correct'];noises={seed:initial_noises(seed,key) for seed in range(1000,1004)}
    checks={}
    for seed,(base,marked) in noises.items():
        checks[str(seed)]={'tensor_hash_matches':hashlib.sha256(marked.tobytes()).hexdigest()==mapping['selfchecks'][str(seed)]['tensor_sha256'],
            **evaluate(independent_votes((marked>0).astype(np.uint8),key,nonce_for(seed)),message(seed))}
    for entry in mapping['entries']:
        old=entry['source_row'];row=index.get(entry['opaque_id']);record={'opaque_id':entry['opaque_id'],'source_id':old['id'],'case':old['case'],'arm':old['arm'],'channel':old['channel'],'outcome':'missing'}
        try:
            if not row or row['outcome']!='completed':raise ValueError('Readout missing/failed')
            if row['image_sha256']!=old['image_sha256']:raise ValueError('Emitted image identity differs')
            own=nonce_for(old['generation_seed']);query=row['nonce_queries'][own];reference=message(old['generation_seed'])
            replication={}
            for newkey,oldkey in (('correct','correct_key'),('wrong','wrong_key')):
                result=query[newkey];oldresult=old[oldkey]
                replication[newkey]=(result['votes']==oldresult['votes'] and result['bits']==oldresult['bits'] and evaluate(result,reference)['matches']==oldresult['matches'])
            latent_file=output/'readout'/row['files']['latent']['path'];sign_file=output/'readout'/row['files']['signs']['path']
            if latent_file.name!=entry['opaque_id']+'.latent.bin' or sign_file.name!=entry['opaque_id']+'.signs.bin' or latent_file.parent.resolve()!=(output/'readout').resolve() or sign_file.parent.resolve()!=(output/'readout').resolve():raise ValueError('Raw artifact path differs')
            if sha(latent_file)!=row['files']['latent']['sha256'] or sha(sign_file)!=row['files']['signs']['sha256']:raise ValueError('Raw emitted tensor hash differs')
            latent=np.frombuffer(latent_file.read_bytes(),dtype=np.float32).reshape(1,4,64,64)
            signs=np.frombuffer(sign_file.read_bytes(),dtype=np.uint8).reshape(1,4,64,64)
            if not np.isfinite(latent).all() or not np.array_equal(signs,latent>0):raise ValueError('Emitted signs/latent disagree')
            for seed in range(1000,1004):
                candidate=row['nonce_queries'][nonce_for(seed)]
                for label,value,public_key in (('correct',signs,key),('wrong',signs,mapping['keys']['wrong']),('shifted',np.roll(signs,1,axis=3),key),('negative',(-latent>0).astype(np.uint8),key)):
                    if candidate[label]!=independent_votes(value,public_key,nonce_for(seed)):raise ValueError('Raw signs/emitted query differ')
                if candidate['algebra']!=zero_aware_algebra(signs,(-latent>0).astype(np.uint8),latent==0,key,nonce_for(seed)):raise ValueError('Emitted algebra differs')
            foreign=[{'foreign_seed':seed,**evaluate(row['nonce_queries'][nonce_for(seed)]['correct'],message(seed))} for seed in range(1000,1004) if seed!=old['generation_seed']]
            correlations={str(seed):{arm:transport(latent,noise) for arm,noise in zip(('C0_gaussian','C1_marked'),pair)} for seed,pair in noises.items()}
            record.update(outcome='completed',replication=replication,own=evaluate(query['correct'],reference),wrong=evaluate(query['wrong'],reference),
                foreign_nonce=foreign,shifted=evaluate(query['shifted'],reference),negative_own=evaluate(query['negative'],reference),
                own_complement=evaluate(query['correct'],1-reference),negative_complement=evaluate(query['negative'],1-reference),
                algebra=query['algebra'],transport=correlations)
        except Exception as error:record.update(outcome='failed',error=repr(error))
        evaluated.append(record)
    complete=len(evaluated)==24 and all(r['outcome']=='completed' for r in evaluated)
    replication=all(all(r['replication'].values()) for r in evaluated) if complete else None
    controls=all(not r['shifted']['present'] and all(not v['present'] for v in r['foreign_nonce']) for r in evaluated) if complete else None
    algebra=all(all(r['algebra'][k] for k in ('votes_complement_zero_adjusted','nonzero_sign_complement','zero_signs_remain_zero','nonzero_nontie_bits_complement')) for r in evaluated) if complete else None
    selfchecks=all(r['tensor_hash_matches'] and r['matches']==256 for r in checks.values())
    return {'rows':evaluated,'selfchecks':checks,'planned_images':24,'planned_foreign_queries':72,'planned_shifted_queries':24,
        'complete':complete,'exact_replication_gate':replication,'control_gate':controls,'algebra_gate':algebra,
        'implementation_gate':replication and controls and algebra and selfchecks if complete else None,
        'label':'exploratory correlated engineering controls, not independent FPR or ownership evidence','human_visual_verdict':None}

def run(manifest_path,native_dir,lw_dir,output):
    output=output.resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN dev-runs required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    record={'schema_version':VERSION,'config':CONFIG,'command':sys.argv,'data_split':'synthetic','seeds':[1000,1001,1002,1003],
        'outcome':'started','expected_images':24,'duration_seconds':0,'human_visual_verdict':None}
    record['planned_conditions']=[{'case':f'prompt-{i}','arm':arm,'channel':channel,'outcome':'planned'} for i in range(4) for arm in ('C0','C1') for channel in CONFIG['channels']]
    write(output/'run.json',record)
    try:
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest!={'schema_version':VERSION,'data_split':'synthetic','config':CONFIG,'source_locks':LOCKS}:raise ValueError('Frozen P1 manifest required')
        record['commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();record['manifest_sha256']=sha(manifest_path)
        deps=[Path(__file__),manifest_path,ROOT/'research/m1-gs-lightweight-positive-diagnosis.md',ROOT/'scripts/m1_windows_job.py',
            ROOT/'scripts/three_threat_models.py',ROOT/'scripts/three_threat_protocol.py',ROOT/'scripts/verify_science_assets.py',ROOT/'scripts/check_a6_lpips_assets.py',ROOT/'research/a6-candidate-model-assets.json',ROOT/'research/m1-gs-synthetic.json']
        record['committed_files']={}
        for p in deps:
            relative=p.resolve().relative_to(ROOT).as_posix();blob=subprocess.check_output(['git','rev-parse','HEAD:'+relative],cwd=ROOT,text=True).strip()
            if subprocess.check_output(['git','hash-object','--path='+relative,str(p)],cwd=ROOT,text=True).strip()!=blob:raise ValueError('Uncommitted P1 input: '+relative)
            record['committed_files'][relative]={'working_sha256':sha(p),'git_blob_oid':blob}
        record['synthetic_selfchecks']=synthetic_selfcheck()
        record.update(prepare(native_dir.resolve(),lw_dir.resolve(),output));write(output/'run.json',record)
        sys.path.insert(0,str(ROOT/'scripts'));from m1_windows_job import OwnedJobProcess
        sealed=output/'sealed-input.json'
        command=[sys.executable,str(Path(__file__).resolve()),'--readout-worker','--sealed-input',str(sealed),'--sealed-sha256',sha(sealed),'--output-dir',str(output/'readout')]
        with (output/'worker.log').open('w') as log:
            with OwnedJobProcess(command,log,receipt=lambda receipt:write(output/'worker-ownership.json',receipt)) as child:
                try:child.wait(max(1.,CONFIG['seconds_cap']-(time.monotonic()-started)))
                except subprocess.TimeoutExpired:record['worker_timeout']=True
        if (output/'readout/run.json').exists():
            assessment=evaluate_emitted(output);write(output/'assessment.json',assessment)
            record['outcome']='completed' if assessment['complete'] else 'incomplete';record['implementation_gate']=assessment['implementation_gate'] and all(record['synthetic_selfchecks'].values()) if assessment['complete'] else None
        else:raise RuntimeError('Worker produced no readable receipt')
    except (Exception,KeyboardInterrupt) as error:record.update(outcome='failed',error=repr(error),traceback=traceback.format_exc())
    finally:
        for row in record['planned_conditions']:row['outcome']='see_assessment' if (output/'assessment.json').exists() else 'not_completed_after_stop'
        record['artifact_bytes']=sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
        if record['artifact_bytes']>CONFIG['artifact_budget_bytes']:record.update(outcome='failed',artifact_cap_exceeded=True)
        record.update(duration_seconds=time.monotonic()-started,
            output_hashes={p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file() and p!=output/'run.json'})
        write(output/'run.json',record)
    return 0 if record['outcome']=='completed' else 1

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('manifest','native-dir','lightweight-dir','sealed-input','output-dir'):parser.add_argument('--'+name,type=Path)
    parser.add_argument('--readout-worker',action='store_true');parser.add_argument('--sealed-sha256')
    args=parser.parse_args()
    if args.readout_worker:
        if args.manifest or args.native_dir or args.lightweight_dir or not args.sealed_input or not args.sealed_sha256 or not args.output_dir:parser.error('Restricted sealed reader arguments required')
        return readout_worker(args.sealed_input,args.sealed_sha256,args.output_dir)
    if not all((args.manifest,args.native_dir,args.lightweight_dir,args.output_dir)):parser.error('Manifest/native/lightweight/output directories required')
    return run(args.manifest,args.native_dir,args.lightweight_dir,args.output_dir)

if __name__=='__main__':raise SystemExit(main())
