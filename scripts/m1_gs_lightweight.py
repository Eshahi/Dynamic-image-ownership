"""B-LW1: read-only GS initial-noise/terminal-sign diagnostic; no inversion.

The native Gaussian Shading adaptation is unchanged. Public development key and
nonce are detector fixtures; reference payload is evaluator-only side information.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import hashlib
import importlib.metadata
import inspect
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ASSETS=MAIN/'.thesis-build/assets/a6'
VERSION='m1-gs-terminal-sign-v1'
CONFIG={'presence_matches':180,'posterior':'mode','precision':'float16','batch_size':1,
    'units':'scaled-terminal-VAE-latent','gpu_budget_bytes':10*1024**3,
    'ram_budget_bytes':16*1024**3,'artifact_budget_bytes':100*1024**2,'seconds_cap':1200}
NATIVE_HASH='5249122b9493d33869f24f9cae99eac87d3eec69ecd2f561938a28a809c6cd92'
MANIFEST_HASH='88ef9fa1caabbeb3f5db7ea35212244144ed7778ab8463abb3bf4a4a5bfcdd89'

@lru_cache(maxsize=1)
def native():
    # No model import or scientific work at module import time.
    sys.path.insert(0,str(ROOT/'scripts'))
    import m1_gaussian_shading
    return m1_gaussian_shading

def sha(path):return native().digest(path)
def write(path,value):native().write(Path(path),value)

def decode_votes(latent,key,nonce):
    import numpy as np
    value=np.asarray(latent)
    if value.shape!=(1,4,64,64) or value.dtype.kind!='f' or not np.isfinite(value).all():
        raise ValueError('Finite floating latent with exact 1x4x64x64 shape required')
    plain=((value.reshape(-1)>0).astype(np.uint8)^native().bitstream(key,nonce,16384))
    votes=plain.reshape(4,8,8,8,8).sum(axis=(1,3))
    return (votes>32).astype(np.uint8),votes

def evaluate(bits,votes,reference):
    import numpy as np
    if np.shape(reference)!=(4,8,8) or not np.isin(reference,[0,1]).all():raise ValueError('Binary reference256 required')
    matches=int((bits==reference).sum())
    return {'bits':bits.reshape(-1).tolist(),'votes':votes.reshape(-1).tolist(),
        'tie_count':int((votes==32).sum()),'matches':matches,'bit_accuracy':matches/256,
        'exact_message':matches==256,'present':matches>=180}

def latent_diagnostics(u,z):
    import numpy as np
    for value in (u,z):
        if value.shape!=(1,4,64,64) or value.dtype!=np.float16 or not np.isfinite(value).all():
            raise ValueError('Finite fp16 posterior/scaled tensors required')
    f=z.astype(np.float32)
    return {'shape':list(z.shape),'finite':True,'posterior_dtype':str(u.dtype),'scaled_dtype':str(z.dtype),
        'decoder_dtype':'float32','posterior_zero_count':int((u==0).sum()),'scaled_zero_count':int((z==0).sum()),
        'sign_changes_after_scaling':int(((u>0)!=(z>0)).sum()),
        'channel_mean':f.mean(axis=(0,2,3)).tolist(),'channel_std':f.std(axis=(0,2,3)).tolist()}

def processor_for(vae):
    from diffusers.image_processor import VaeImageProcessor
    return VaeImageProcessor(vae_scale_factor=2**(len(vae.config.block_out_channels)-1))

def terminal_sign(image,vae,key,nonce,*,wrong_key=None):
    """No reference, attack label, initial noise, CLIP or inverse pipeline input."""
    import torch
    device=next(vae.parameters()).device
    sync=lambda:torch.cuda.synchronize(device) if device.type=='cuda' else None
    processor=processor_for(vae);sync();start=time.monotonic()
    x=processor.preprocess(image).to(device,dtype=vae.dtype)
    with torch.inference_mode():
        u=vae.encode(x).latent_dist.mode()
        z=u*vae.config.scaling_factor
    sync();encoded=time.monotonic()
    un=u.detach().cpu().numpy();zn=z.float().cpu().numpy()
    diagnostics=latent_diagnostics(un,z.detach().cpu().numpy())
    bits,votes=decode_votes(zn,key,nonce)
    wrong=decode_votes(zn,wrong_key,nonce) if wrong_key is not None else None
    end=time.monotonic()
    diagnostics.update(scaling_factor=float(vae.config.scaling_factor),units=CONFIG['units'],
        encode_seconds=encoded-start,decode_transfer_seconds=end-encoded,total_seconds=end-start,
        vae_encodes=1,unet_evaluations=0,text_encoder_evaluations=0)
    return bits,votes,diagnostics,wrong

def conditional_null(reference):
    """Arithmetic reference ONLY: independent fair dewhitened chips."""
    w=sum(int(b) for b in reference.reshape(-1));q=(1-math.comb(64,32)/2**64)/2
    a=[math.comb(w,k)*q**k*(1-q)**(w-k) for k in range(w+1)]
    n=256-w;b=[math.comb(n,k)*(1-q)**k*q**(n-k) for k in range(n+1)]
    return {'payload_ones':w,'decoded_one_probability':q,'ideal_mean_agreement':(w*q+n*(1-q))/256,
        'ideal_tail_ge180':sum(x*y for i,x in enumerate(a) for j,y in enumerate(b) if i+j>=180),
        'label':'conditional arithmetic reference; not validated population FPR'}

def selfcheck(seed,key):
    import numpy as np
    gs=native();reference=gs.payload_for(seed);nonce=gs.nonce_for(seed)
    base=np.random.default_rng(seed).standard_normal((1,4,64,64)).astype(np.float32)
    marked=(np.abs(base).reshape(-1)*(2*gs.embed_signs(reference,key,nonce).astype(np.float32)-1)).reshape(base.shape).astype(np.float16)
    bits,votes=decode_votes(marked,key,nonce)
    return dict(evaluate(bits,votes,reference),zero_count=int((marked==0).sum()),
        tensor_sha256=hashlib.sha256(marked.tobytes()).hexdigest(),
        provenance='deterministically reconstructed fp16 generation input, not retained original tensor')

def plan(manifest):
    return [{'id':f"{c['id']}-{arm}-{channel}",'case':c['id'],'generation_seed':c['seed'],
        'arm':arm,'channel':channel,'strength':strength,'attack_seed':seed,
        'outcome':'missing_native_row','readout_id':VERSION,'human_visual_verdict':None}
        for c in manifest['cases'] for arm in ('C0','C1') for channel,strength,seed in native().channels_for_run()]

def validate(manifest):
    if manifest!={'schema_version':VERSION,'data_split':'synthetic','config':CONFIG,
        'native_script_sha256':NATIVE_HASH,'native_manifest_sha256':MANIFEST_HASH}:
        raise ValueError('Frozen B-LW1 synthetic manifest required')
    if sha(ROOT/'scripts/m1_gaussian_shading.py')!=NATIVE_HASH or sha(ROOT/'research/m1-gs-synthetic.json')!=MANIFEST_HASH:
        raise ValueError('Frozen generating experiment changed')

def collect(source,manifest):
    """Read metadata/hash checks only; missing native rows remain planned."""
    gs=native();required=('run.json','artifacts.json','rows.jsonl','rows-receipt.json')
    receipts={name:{'path':str(source/name),'sha256':sha(source/name)} for name in required if (source/name).is_file()}
    record=json.loads((source/'run.json').read_text(encoding='utf-8'))
    if record.get('script_sha256')!=NATIVE_HASH or record.get('manifest_sha256')!=MANIFEST_HASH or record.get('config')!=gs.CONFIG:
        raise ValueError('Source run generating fingerprint differs')
    commit=record.get('commit')
    if not isinstance(commit,str) or len(commit) not in (40,64) or any(c not in '0123456789abcdef' for c in commit):raise ValueError('Native commit missing/malformed')
    artifacts,rows,seen=gs.load_resume_state(source,manifest,record)
    for row in rows:
        for name in ('bit_accuracy','wrong_key_bit_accuracy','detector_seconds'):
            v=row.get(name)
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError('Malformed native score/time: '+name)
        for name in ('detected','wrong_key_detected','exact_payload'):
            if type(row.get(name)) is not bool:raise ValueError('Malformed native decision: '+name)
        if row.get('detector_unet_evaluations')!=50:raise ValueError('Unexpected native inversion NFE')
    index={f"{r['case']}-{r['arm']}-{r['channel']}":r for r in rows}
    return record,receipts,index,artifacts

def summarize(rows):
    summary=[]
    for channel,_,_ in native().channels_for_run():
        group=[r for r in rows if r['channel']==channel]
        for decoder in ('lightweight','native'):
            available=lambda r:r['outcome']=='completed' if decoder=='lightweight' else 'native' in r
            c1=[r for r in group if r['arm']=='C1' and available(r)]
            c0=[r for r in group if r['arm']=='C0' and available(r)]
            def value(row,wrong=False):
                if decoder=='lightweight':return row['wrong_key' if wrong else 'correct_key']['present']
                return row['native']['wrong_key_detected' if wrong else 'detected']
            acc=[{'case':r['case'],'accuracy':r['correct_key']['bit_accuracy'] if decoder=='lightweight' else r['native']['bit_accuracy']} for r in c1]
            summary.append({'channel':channel,'decoder':decoder,'sources_planned_per_arm':4,'C1_present':sum(value(r) for r in c1),
                'C1_exact':sum(r['correct_key']['exact_message'] if decoder=='lightweight' else r['native']['exact_payload'] for r in c1),
                'C0_positive':sum(value(r) for r in c0),'C1_wrong_positive':sum(value(r,True) for r in c1),
                'C1_accuracies':acc,'C1_mean_accuracy':sum(a['accuracy'] for a in acc)/len(acc) if acc else None,
                'missing_C1':4-len(c1),'missing_C0':4-len(c0)})
    gates={}
    for channel in ('clean','vae'):
        r=next(r for r in summary if r['channel']==channel and r['decoder']=='lightweight')
        gates[channel]=None if r['missing_C1'] or r['missing_C0'] else r['C1_present']==4 and r['C0_positive']==0 and r['C1_wrong_positive']==0
    comparisons=[]
    for r in rows:
        if r['outcome']!='completed':continue
        n=r['native'];l=r['correct_key'];ni=int(round(n['bit_accuracy']*256))
        comparisons.append({'id':r['id'],'case':r['case'],'arm':r['arm'],'channel':r['channel'],
            'native_matches_minus_lightweight':ni-l['matches'],'presence_cell':
            'both' if n['detected'] and l['present'] else 'native-only' if n['detected'] else 'lightweight-only' if l['present'] else 'neither'})
    strengths=[{'strength':s,'sources_planned':4,'repeated_C1_conditions_planned':12,
        'conditions':[r['id'] for r in rows if r['arm']=='C1' and r['strength']==s],
        'completed_C1':sum(r['outcome']=='completed' for r in rows if r['arm']=='C1' and r['strength']==s)} for s in native().CONFIG['strengths']]
    return {'channels':summary,'gates':gates,'paired_comparisons':comparisons,'strength_clusters':strengths,
        'label':'descriptive four-prompt clusters; no pooled TPR, semantic binding or human verdict'}

def run(manifest_path,source,output):
    gs=native();source=Path(source).resolve();output=Path(output).resolve();manifest_path=Path(manifest_path).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()) or output==source:raise ValueError('Separate MAIN dev-runs output required')
    generating=json.loads((ROOT/'research/m1-gs-synthetic.json').read_text(encoding='utf-8'))
    rows={r['id']:r for r in plan(generating)};started=time.monotonic();previous=0;prior=None;resume_validated=False
    if output.exists():prior=json.loads((output/'run.json').read_text(encoding='utf-8'))
    else:output.mkdir(parents=True)
    record={'schema_version':VERSION,'command':sys.argv,'config':CONFIG,'seeds':[1000,1001,1002,1003],
        'data_split':'synthetic','duration_seconds':0,'outcome':'started','conditions':list(rows.values()),
        'human_visual_verdict':None,'source_directory':str(source),'expected_conditions':112}
    if not prior:write(output/'run.json',record);write(output/'conditions.json',list(rows.values()))
    try:
        record.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),manifest_sha256=sha(manifest_path))
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'));validate(manifest)
        source_record,receipts,index,artifacts=collect(source,generating)
        deps=[Path(__file__),manifest_path,ROOT/'scripts/m1_gaussian_shading.py',ROOT/'research/m1-gs-synthetic.json',
            ROOT/'research/m1-initial-noise-lightweight-diagnostic.md',ROOT/'scripts/three_threat_models.py',
            ROOT/'scripts/verify_science_assets.py',ROOT/'scripts/check_a6_lpips_assets.py',ROOT/'research/a6-candidate-model-assets.json',
            ROOT/'scripts/m1_phasemark.py']
        fingerprint={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'manifest_sha256':sha(manifest_path),'script_sha256':sha(__file__),'committed_files':gs.require_committed(deps),
            'source_receipts':receipts,'source_directory':str(source),'config':CONFIG}
        if prior:
            if any(prior.get(k)!=v for k,v in fingerprint.items()):raise ValueError('Resume requires identical code/config/source receipts')
            for name,digest in prior.get('output_hashes',{}).items():
                if sha(output/name)!=digest:raise ValueError('Assessor output receipt mismatch: '+name)
            if 'conditions.json' not in prior.get('output_hashes',{}):raise ValueError('Resume condition receipt missing')
            if (output/'rows.jsonl').exists() and 'rows.jsonl' not in prior['output_hashes']:raise ValueError('Resume journal receipt missing')
            retained=json.loads((output/'conditions.json').read_text(encoding='utf-8'))
            if [r['id'] for r in retained]!=list(rows):raise ValueError('Resume denominator differs')
            rows={r['id']:r for r in retained};previous=prior['duration_seconds']
        resume_validated=True
        for ident,row in rows.items():
            if ident in index:
                nr=index[ident]
                row.update(native=nr,image_sha256=nr['image_sha256'],source_row_sha256=hashlib.sha256(json.dumps(nr,sort_keys=True,separators=(',',':')).encode()).hexdigest())
        record.update(fingerprint,source_run=source_record,outcome='started')
        for name in receipts:(output/('source-'+name)).write_bytes((source/name).read_bytes())
        (output/'manifest.json').write_bytes(manifest_path.read_bytes())
        write(output/'run.json',record)
        from three_threat_models import block_network,verify_assets
        block_network()
        import numpy as np
        import torch
        from PIL import Image
        from diffusers import AutoencoderKL
        from m1_phasemark import working_set_bytes
        checks={str(c['seed']):selfcheck(c['seed'],generating['development_key_hex']) for c in generating['cases']}
        record['reconstructed_source_noise_selfchecks']=checks
        record['conditional_null']={str(c['seed']):conditional_null(gs.payload_for(c['seed'])) for c in generating['cases']}
        if any(r['matches']!=256 for r in checks.values()):raise RuntimeError('Reconstructed fp16 source-noise selfcheck failed')
        if not torch.cuda.is_available():raise RuntimeError('CUDA required; no CPU scientific substitution')
        torch.cuda.set_per_process_memory_fraction(min(1.,CONFIG['gpu_budget_bytes']/torch.cuda.get_device_properties(0).total_memory))
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.manual_seed(0)
        assets,_=verify_assets(ASSETS,ROOT/'research/a6-candidate-model-assets.json');record['asset_receipt']=assets
        asset_receipt_id=hashlib.sha256(json.dumps(assets,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        tick=time.monotonic()
        vae=AutoencoderKL.from_pretrained(ASSETS/'sd15-fp16/vae',variant='fp16',use_safetensors=True,local_files_only=True,torch_dtype=torch.float16).eval().requires_grad_(False).to('cuda')
        torch.cuda.synchronize();record['model_load_seconds']=time.monotonic()-tick
        if float(vae.config.scaling_factor)!=.18215 or len(vae.config.block_out_channels)!=4:raise ValueError('Pinned SD1.5 VAE scale/config differs')
        processor=processor_for(vae)
        from diffusers import image_processor
        record['preprocessing']={'class':'diffusers.image_processor.VaeImageProcessor','config':dict(processor.config),
            'module_sha256':sha(inspect.getfile(image_processor)),'diffusers_version':importlib.metadata.version('diffusers')}
        record['environment']={'python':sys.version,**{p:importlib.metadata.version(p) for p in ('torch','numpy','diffusers','Pillow')}}
        record['detector_side_information']='pinned VAE/preprocessing, public development key and per-image nonce; payload evaluator-only'
        first=True
        for ident,row in rows.items():
            if row['outcome']=='completed':continue
            if ident not in index:continue
            if time.monotonic()-started>CONFIG['seconds_cap']:break
            ram=working_set_bytes();record['peak_observed_ram_bytes']=max(record.get('peak_observed_ram_bytes',0),ram)
            if ram>CONFIG['ram_budget_bytes'] or sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>CONFIG['artifact_budget_bytes']:raise RuntimeError('Resource cap reached')
            nr=index[ident];row.update(native=nr,image_sha256=nr['image_sha256'],source_row_sha256=hashlib.sha256(json.dumps(nr,sort_keys=True,separators=(',',':')).encode()).hexdigest())
            try:
                path=gs.verify_artifact(source,nr['image'],artifacts)
                with Image.open(path) as image:
                    if image.mode!='RGB' or image.size!=(512,512):raise ValueError('Exact saved native RGB512 required')
                    image.load();torch.cuda.reset_peak_memory_stats()
                    nonce=gs.nonce_for(row['generation_seed'])
                    bits,votes,diagnostics,wrong=terminal_sign(image,vae,generating['development_key_hex'],nonce,wrong_key=generating['wrong_key_hex'])
                reference=gs.payload_for(row['generation_seed'])
                row.update(correct_key=evaluate(bits,votes,reference),wrong_key=evaluate(*wrong,reference),diagnostics=diagnostics,
                    preprocessing=record['preprocessing'],reference_payload_sha256=hashlib.sha256(reference.tobytes()).hexdigest(),
                    key_identifiers={k:hashlib.sha256(bytes.fromhex(generating[k])).hexdigest() for k in ('development_key_hex','wrong_key_hex')},
                    nonce=nonce,first_call=first,peak_allocated_bytes=torch.cuda.max_memory_allocated(),outcome='completed')
                row['vae_asset_receipt_id']=asset_receipt_id
                first=False
                if row['peak_allocated_bytes']>CONFIG['gpu_budget_bytes']:raise RuntimeError('GPU cap exceeded')
            except Exception as error:row.update(outcome='failed',error=repr(error),traceback=traceback.format_exc())
            with (output/'rows.jsonl').open('a',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(row,allow_nan=False)+'\n');stream.flush()
            write(output/'conditions.json',list(rows.values()))
            record.update(conditions=list(rows.values()),duration_seconds=previous+time.monotonic()-started)
            record['output_hashes']={p.name:sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'}
            write(output/'run.json',record)
        record['outcome']='completed' if all(r['outcome']=='completed' for r in rows.values()) else 'incomplete'
    except (Exception,KeyboardInterrupt) as error:
        # A rejected resume must never overwrite the previous output receipt.
        if prior and not resume_validated:raise
        record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error),traceback=traceback.format_exc())
    write(output/'conditions.json',list(rows.values()));write(output/'summary.json',summarize(list(rows.values())))
    record.update(conditions=list(rows.values()),duration_seconds=previous+time.monotonic()-started,
        completed_conditions=sum(r['outcome']=='completed' for r in rows.values()),
        output_hashes={p.name:sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'})
    write(output/'run.json',record)
    return 0 if record['outcome']=='completed' else 1

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--input-dir',type=Path,required=True);parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--preflight-only',action='store_true',help='Validate metadata and file hashes only; no model loading or writes')
    args=parser.parse_args()
    if args.preflight_only:
        validate(json.loads(args.manifest.read_text(encoding='utf-8')))
        generating=json.loads((ROOT/'research/m1-gs-synthetic.json').read_text(encoding='utf-8'))
        record,receipts,index,_=collect(args.input_dir.resolve(),generating)
        print(json.dumps({'native_outcome':record['outcome'],'native_commit':record['commit'],
            'expected_conditions':112,'available_native_rows':len(index),'input_receipts':receipts},indent=2))
        return 0
    if args.output_dir is None:parser.error('--output-dir is required unless --preflight-only')
    return run(args.manifest,args.input_dir,args.output_dir)

if __name__=='__main__':raise SystemExit(main())
