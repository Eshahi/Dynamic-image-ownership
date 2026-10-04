"""Actual current A-C science on owned generated fixtures; never a scientific unlock.

Import is standard-library only. Model loading is confined to run(), after private
owned-child scope validation. Candidate adoption and real-data execution remain pending.
"""
from __future__ import annotations
import argparse, hashlib, io, json, math, os, random, re, subprocess, sys, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
PLAN=ROOT/'research/m1-candidate-rehearsal-v1.json'
VERSION='m1-candidate-rehearsal-v1'
CAP_FIELDS={'schema','manifest_sha256','plan_sha256','worker_sha256','scientific_core_sha256',
 'output_directory','child_pid','parent_pid','job_id','assignment_verified','token_sha256',
 'stage','scenario','unit_index','stop_phase','stop_step','upstream','injection',
 'cooperative_stop_path','expires_unix'}


def read(path):
    def bad(v):raise ValueError('Nonfinite JSON: '+v)
    return json.loads(Path(path).read_text(encoding='utf8'),parse_constant=bad)


def object_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()


def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    with temp.open('x',encoding='utf8') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    temp.replace(path)


def configuration():return read(PLAN)

def generated_seeds():return [0,1]


def dependency_paths():
    names=['m1_git_input_identity.py','m1_candidate_rehearsal_worker.py','m1_candidate_model_context.py','m1_confirmatory_image_operations.py','m1_confirmatory_t5_pairs.py','m1_candidate_adapter.py','m1_owner_interface.py','a4_protocol_reference.py','m1_canonical_source.py','m1_source_initialization.py',
      'm1_terminal_continuous.py','m1_terminal_repeatability.py','m1_blind_noise_core.py',
      'm1_blind_noise.py','m1_dual_latent.py','m1_phase_residual.py','m1_phasemark.py',
      'm1_latent_reconstruction.py','revised_watermark_v5.py','revised_watermark_v4.py',
      'three_threat_models.py','three_threat_protocol.py','a6_clip_visual.py',
      'verify_science_assets.py','check_a6_lpips_assets.py']
    return [ROOT/'scripts'/n for n in names]+[PLAN,ROOT/'research/a6-candidate-model-assets.json',
      ROOT/'configs/revised-watermark-v5.example.json',ROOT/'research/m1-reconstruction-dev.json']


def scientific_core_sha256():
    return object_sha({p.relative_to(ROOT).as_posix():file_sha(p) for p in dependency_paths()})


def destination(value):
    path=Path(value).absolute();base=(MAIN/'.thesis-build/rehearsal').absolute()
    if path==base or not path.is_relative_to(base):raise ValueError('Owned MAIN rehearsal child directory required')
    for current in (path,*path.parents):
        if current.is_symlink() or (current.exists() and getattr(current.lstat(),'st_file_attributes',0)&0x400):
            raise ValueError('Reparse path refused')
        if current==base:break
    return path


def validate_launch_scope(manifest,output,*,scope=None,token=None,now=None):
    """Integrity/owned-launch guard, not cryptographic same-user isolation."""
    output=destination(output)
    import m1_candidate_lifecycle as launcher
    case=launcher.validate_manifest(manifest)
    token=os.environ.get('M1_REHEARSAL_TOKEN') if token is None else token
    if type(token) is not str or not re.fullmatch('[0-9a-f]{64}',token):raise ValueError('Private owned-launch token required')
    if scope is None:
        path=destination(os.environ.get('M1_REHEARSAL_CAPABILITY',''))
        if path!=output/'logs/launch-capability.json':raise ValueError('Capability must belong to exact child output')
        scope=read(path)
    if not isinstance(scope,dict) or set(scope)!=CAP_FIELDS:raise ValueError('Exact private capability schema')
    expected=dict(schema='m1-candidate-rehearsal-launch-v1',manifest_sha256=object_sha(manifest),
        plan_sha256=object_sha(configuration()),worker_sha256=file_sha(__file__),
        scientific_core_sha256=scientific_core_sha256(),output_directory=str(output),
        child_pid=os.getpid(),parent_pid=os.getppid(),assignment_verified=True,
        token_sha256=hashlib.sha256(token.encode()).hexdigest(),scenario=manifest['stage_id'],
        stage=case['stage'],stop_phase=case['stop_phase'],stop_step=case['stop_step'],injection=case['injection'],
        cooperative_stop_path=str(output/'checkpoints/stop-request.json'))
    if any(type(scope.get(k)) is not type(v) or scope[k]!=v for k,v in expected.items()):raise ValueError('Owned capability binding differs')
    if type(scope['job_id']) is not str or not scope['job_id']:raise ValueError('Job assignment identity missing')
    if type(scope['unit_index']) is not int or scope['unit_index'] not in (0,1) or scope['unit_index']==1 and manifest['stage_id']!='scale':raise ValueError('Unit roster differs')
    current=time.time() if now is None else now
    expiry=scope['expires_unix']
    if type(expiry) not in (int,float) or not current<expiry<=current+3630:raise ValueError('Expired/unbounded capability')
    if scope['stage']=='resume':
        checked_upstream(scope['upstream'])
    elif scope['upstream'] is not None:raise ValueError('Unexpected prior inputs')
    return scope


def checked_upstream(upstream):
    if not isinstance(upstream,dict) or set(upstream)!={'run','checkpoint'}:raise ValueError('Explicit two recovery receipts required')
    for receipt in upstream.values():
        if not isinstance(receipt,dict) or set(receipt)!={'path','sha256'}:raise ValueError('Exact recovery receipt')
        path=destination(receipt['path'])
        if not path.is_file() or file_sha(path)!=receipt['sha256']:raise ValueError('Recovery receipt changed')
    return upstream


def generated_source(unit_index):
    """Integer literal generator, encoded in-process; no source path accepted."""
    if type(unit_index) is not int or unit_index not in (0,1):raise ValueError('Frozen synthetic unit')
    import numpy as np
    from PIL import Image
    from m1_canonical_source import canonicalize
    y,x=np.indices((512,512),dtype=np.int64);k=unit_index
    rgb=np.stack(((x//4+y//8+(x*y)%251//4+17*k)%256,
       (x//8+2*(y//4)+29*k)%256,(x//3+y//3+(x^y)%67+43*k)%256),axis=-1).astype(np.uint8)
    buf=io.BytesIO();Image.fromarray(rgb).save(buf,format='PNG');raw=buf.getvalue()
    result,receipt=canonicalize(raw,hashlib.sha256(raw).hexdigest())
    receipt.update(uid=f'fixture:candidate-{k}',generator=configuration()['generator'],generator_seed=k,
        data_split='synthetic',external_raw_io=False)
    return result,raw,receipt


class PrefixComplete(Exception):pass
class CooperativeStop(Exception):pass


def run(manifest_path,output):
    manifest=read(manifest_path);scope=validate_launch_scope(manifest,output);output=destination(output)
    import m1_candidate_lifecycle as launcher
    input_git_identities=launcher.pin_execution(manifest)
    if (output/'outputs/worker-run.json').exists():raise ValueError('Worker receipt already exists')
    cfg=configuration();started=time.monotonic();events=[];latest=None;phase='scope';step=None
    record=dict(schema=VERSION,generated_only=True,scientific_verdict='NOT_EVIDENCE',
      candidate_status=cfg['candidate_status'],commit=manifest['git_commit'],command=sys.argv,
      manifest_sha256=object_sha(manifest),config=cfg,scientific_core_sha256=scientific_core_sha256(),
      input_git_identities=input_git_identities,scope_sha256=object_sha(scope),scenario=scope['scenario'],stage=scope['stage'],unit_index=scope['unit_index'],
      outcome='started',seeds=generated_seeds(),human_visual_verdict=None,peak_rss_bytes=0,peak_allocated_bytes=0,conditions=[
        dict(control=a,dose=d,outcome='planned') for a in ('C0','C1') for d in ('clean','vae_cycle')],
      raw_injection_applicable=False,decode_injection_applicable=False,checkpoints=[])
    runpath=output/'outputs/worker-run.json';journal=output/'checkpoints/worker-journal.json'
    def persist():
        record['duration_seconds']=time.monotonic()-started
        atomic(runpath,record);atomic(journal,dict(schema=VERSION,events=events))
    def event(kind,**fields):
        events.append(dict(kind=kind,elapsed_seconds=time.monotonic()-started,**fields));persist()
    def check():
        if time.monotonic()-started>min(cfg['run_seconds_cap'],manifest['budget']['max_seconds']):raise TimeoutError('Worker bounded wall deadline')
        if Path(scope['cooperative_stop_path']).exists():raise CooperativeStop('Owned cooperative stop')
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise RuntimeError('Artifact budget')
        if 'm1_phasemark' in sys.modules:
            current_rss=sys.modules['m1_phasemark'].working_set_bytes()
            record['peak_rss_bytes']=max(record['peak_rss_bytes'],current_rss)
            if current_rss>cfg['ram_budget_bytes']:raise RuntimeError('RAM cap')
        if 'torch' in sys.modules:
            tm=sys.modules['torch']
            if tm.cuda.is_initialized():
                record['peak_allocated_bytes']=max(record['peak_allocated_bytes'],tm.cuda.max_memory_allocated())
                if tm.cuda.memory_allocated()>record.get('gpu_allocation_budget',{}).get('effective_allocation_bytes',cfg['gpu_budget_bytes']):raise RuntimeError('GPU allocation cap')
    def pulse(p,s=None):
        nonlocal phase,step
        changed=phase!=p;phase=p;step=s
        if changed:event('phase_transition',phase=p,step=s)
        atomic(output/'outputs/worker-heartbeat.json',dict(phase=p,step=s,elapsed_seconds=time.monotonic()-started,checkpoint=latest))
        check()
    def inject(p,s=None):
        request=scope['injection']
        if request is not None and request['phase']==p and (request['at_step'] is None or request['at_step']==s):
            raise RuntimeError('Declared owned fixture injection: '+p+':'+str(s))
    def receipt(path):return dict(path=str(path),sha256=file_sha(path))
    atomic(output/'outputs/worker-manifest.json',manifest)
    persist()
    try:
        import numpy as np
        import torch
        import m1_source_initialization as initializer
        import m1_blind_noise_core as core
        import m1_phasemark as util
        import revised_watermark_v5 as codec
        from m1_candidate_model_context import CandidateModelContext
        from PIL import Image
        if cfg['owners']!=list(core.OWNERS):raise ValueError('Owner core differs')
        pulse('model');inject('model')
        def publish_context(values):
            values=dict(values)
            for name in ('peak_rss_bytes','peak_allocated_bytes'):
                if name in values:values[name]=max(record[name],values[name])
            record.update(values);persist()
        context=CandidateModelContext(cfg,record['scientific_core_sha256'],publish=publish_context,event=event,check=check)
        adapter=context.adapter;public=adapter.public;feature=context.feature;profile=context.profile
        source,raw,source_receipt=generated_source(scope['unit_index']);record['source']=source_receipt
        rawpath=output/'outputs/generated-source.png'
        with rawpath.open('xb') as f:f.write(raw)
        record['generated_png']=receipt(rawpath)
        E=feature(source);H=codec.perceptual_hash(codec.luminance_from_rgb(source.tolist()),profile=profile)
        record.update(source_E=E.tolist(),source_H=H)
        identity=dict(source_id=source_receipt['uid'],source_rgb8_sha256=source_receipt['rgb8_sha256'],data_split='synthetic',generator_seed=scope['unit_index'])
        prior=None;resume=None
        if scope['stage']=='resume':
            prior=audit_rehearsal_run(Path(scope['upstream']['run']['path']).parent.parent)
            if prior['outcome']!='prefix_completed' or prior['unit_index']!=scope['unit_index'] or prior['source']!=source_receipt or prior['latest_checkpoint']!=scope['upstream']['checkpoint']:
                raise ValueError('Exact same-source prefix100 recovery required')
            if prior['environment']!=record['environment'] or prior['device_identity']!=record['device_identity'] or prior['driver_inventory']!=record['driver_inventory']:
                raise ValueError('Recovery execution runtime changed')
            resume=torch.load(scope['upstream']['checkpoint']['path'],map_location='cpu',weights_only=True)
            record['upstream']=scope['upstream']
        context.place_inference('cpu')
        def save_phase(value):
            nonlocal latest
            p=value['phase'];n=value['step'];inject('save',n)
            path=output/f'checkpoints/{p}-{n:03d}.pt'
            with path.open('xb') as f:torch.save(value,f);f.flush();os.fsync(f.fileno())
            latest=receipt(path);record['checkpoints'].append(dict(phase=p,step=n,**latest));record['latest_checkpoint']=latest
            record['binding']=value['binding']
            pulse(p,n);event('checkpoint',phase=p,step=n,**latest);inject('initializer' if p=='initialization' else 'embedding',n)
        init_result=adapter.initialize(source,identity,core.OWNERS[0],resume=resume,
            stop_step=100 if scope['stage']=='prefix' else 200,on_checkpoint=save_phase,check=check)
        if scope['stage']=='prefix':raise PrefixComplete()
        record['initialization_endpoint_digest']=initializer.digest(init_result)
        embedded=adapter.embed(source,init_result,on_checkpoint=save_phase,
            event=lambda row:event('optimizer',**row),check=check)
        if not embedded['completed']:raise RuntimeError('Fixed embedding100 did not complete')
        record['embedding_endpoint_digest']=initializer.digest(embedded['checkpoint'])
        result=embedded['core_result'];marked=embedded['marked_rgb8'];cap=embedded['cap']
        context.place_inference('cuda')
        def array(value):return value.detach().float().cpu().numpy()[0].transpose(1,2,0).astype(np.float64)
        record['cap']=cap
        def safety_check(rgb):return context.safety_check(rgb,before_safety=lambda:inject('safety'))
        def cycle(rgb):return context.vae_cycle(rgb,before_safety=lambda:inject('safety'))
        q=context.quality
        record['float_arrays']={}
        for name in ('reference','decoded','residual','surrogate'):
            path=output/f'outputs/{name}.npy';np.save(path,array(result[name]),allow_pickle=False);record['float_arrays'][name]=receipt(path)
        images={('C0','clean'):source,('C1','clean'):marked,('C0','vae_cycle'):cycle(source),('C1','vae_cycle'):cycle(marked)}
        for row in record['conditions']:
            pulse('detector');inject('detector');rgb=images[(row['control'],row['dose'])];safety_check(rgb)
            path=output/f"outputs/{row['control']}-{row['dose']}.png";Image.fromarray(rgb).save(path)
            with Image.open(path) as im:
                if not np.array_equal(np.asarray(im),rgb):raise ValueError('PNG byte-value identity')
            torch.cuda.synchronize();tick=time.monotonic();decisions={owner:adapter.readout(rgb,owner) for owner in core.OWNERS};torch.cuda.synchronize()
            elapsed=time.monotonic()-tick;e,h,z=public.observations(rgb)
            zp=output/f"outputs/{row['control']}-{row['dose']}-reader.npy";np.save(zp,z,allow_pickle=False)
            row.update(outcome='completed',image=receipt(path),rgb8_sha256=hashlib.sha256(rgb.tobytes()).hexdigest(),reader_latent=receipt(zp),
              suspect_E=e.tolist(),suspect_H=h,owner_decisions=decisions,extract_seconds=elapsed,source_clip_cosine=float(E@e),
              quality_vs_source=q(source,rgb),quality_vs_same_arm_clean=q(images[(row['control'],'clean')],rgb))
            persist()
        pulse('finalization');time.sleep(.3);check();inject('finalization')
        record['outcome']='completed';record['peak_allocated_bytes']=torch.cuda.max_memory_allocated()
    except PrefixComplete:
        record['outcome']='prefix_completed'
    except (Exception,KeyboardInterrupt) as error:
        record.update(outcome='interrupted' if isinstance(error,(KeyboardInterrupt,CooperativeStop)) else 'failed',error=repr(error),traceback=traceback.format_exc(),failure_phase=phase,failure_step=step)
    finally:
        try:
            if 'm1_phasemark' in sys.modules:record['peak_rss_bytes']=max(record['peak_rss_bytes'],sys.modules['m1_phasemark'].working_set_bytes())
            if 'torch' in sys.modules and sys.modules['torch'].cuda.is_initialized():record['peak_allocated_bytes']=max(record['peak_allocated_bytes'],sys.modules['torch'].cuda.max_memory_allocated())
        except Exception as memory_error:record['final_memory_receipt_error']=repr(memory_error)
        for row in record['conditions']:
            if row['outcome']=='planned':row['missing_reason']='Stopped before condition; denominator retained'
        record['output_hashes']={p.relative_to(output).as_posix():file_sha(p) for p in output.rglob('*') if p.is_file() and p!=runpath and p!=journal and p.relative_to(output).parts[0] in ('outputs','checkpoints') and p.name not in ('lifecycle-run.json','lifecycle-journal.json','stop-request.json')}
        persist()
        record['worker_journal']=receipt(journal);atomic(runpath,record)
    return 0 if record['outcome'] in ('completed','prefix_completed') else 1


def validate_rng(value,runtime,*,embedding):
    """Check saved Python/NumPy/Torch state without changing global execution RNG."""
    import numpy as np
    import torch
    keys={'python','numpy','torch_cpu','torch_cuda'} if embedding else {'python','numpy','torch','cuda'}
    if not isinstance(value,dict) or set(value)!=keys:raise ValueError('RNG inventory differs')
    try:
        random.Random().setstate(value['python'])
        n=value['numpy']
        if not isinstance(n,(tuple,list)) or len(n)!=5 or n[0]!='MT19937' or len(n[1])!=624 or any(type(v) is not int or not 0<=v<2**32 for v in n[1]):raise ValueError('NumPy RNG words')
        local=np.random.RandomState(0)
        local.set_state((n[0],np.asarray(n[1],dtype=np.uint32),n[2],n[3],n[4]))
        cpu=value['torch_cpu' if embedding else 'torch']
        if not isinstance(cpu,torch.Tensor) or cpu.dtype!=torch.uint8 or cpu.ndim!=1:raise ValueError('CPU RNG tensor')
        torch.Generator(device='cpu').set_state(cpu)
        cuda=value['torch_cuda' if embedding else 'cuda']
        if not isinstance(cuda,list) or len(cuda)!=runtime['cuda_rng_devices'] or any(not isinstance(v,torch.Tensor) or v.dtype!=torch.uint8 or v.ndim!=1 or not v.numel() for v in cuda):raise ValueError('CUDA RNG inventory')
    except (KeyError,TypeError,RuntimeError,IndexError,OverflowError) as error:raise ValueError('Malformed RNG') from error


def validate_phase_checkpoint(payload,record,target,*,initializer_payload=None):
    import torch
    import m1_candidate_adapter as candidate
    import m1_source_initialization as init
    candidate._check_seal(payload)
    binding=record['binding'];phase=payload['phase'];state=payload['state']
    frozen_runtime=dict(cublas_workspace_config=':4096:8',deterministic=True,deterministic_warn_only=False,matmul_tf32=False,cudnn_tf32=False,cudnn_benchmark=False,cudnn_deterministic=True)
    if any(binding['runtime'].get(k)!=v for k,v in frozen_runtime.items()) or binding['fill_uninitialized_memory'] is not True:raise ValueError('Deterministic runtime policy differs')
    if payload['binding']!=binding or payload['step']!=state['step']:raise ValueError('Checkpoint binding/step differs')
    if binding['candidate_version']!=candidate.VERSION or binding['model_identity']!=record['model_identity'] or binding['scientific_core_sha256']!=record['scientific_core_sha256']:
        raise ValueError('Candidate/model/core binding differs')
    if binding['source_rgb8_sha256']!=record['source']['rgb8_sha256'] or binding['source_identity']['source_id']!=record['source']['uid'] or binding['owner']!=record['config']['owners'][0] or binding['source_uid'] is not None or binding['schedule'] is not None:
        raise ValueError('Synthetic source/owner binding differs')
    if binding['execution_phase_seed']!=0 or binding['scientific_embedding_seed'] is not None:raise ValueError('Execution seed role differs')
    limit=200 if phase=='initialization' else 100
    if type(payload['step']) is not int or payload['step'] not in range(0,limit+1,10):raise ValueError('Fixed phase step')
    if phase=='initialization':
        identity=dict(source_id=binding['source_identity']['source_id'],source_rgb8_sha256=binding['source_rgb8_sha256'],
          model_sha256=record['model_identity']['vae_fp32'],candidate_binding_sha256=init.digest(binding))
        init._validate_payload(state,identity,init.digest(target),binding['runtime'])
        if state['z'].shape!=(1,4,64,64):raise ValueError('Initializer latent shape')
        if payload['optimizer_phase']!='unmarked initialization Adam only':raise ValueError('Initialization optimizer provenance')
    elif phase=='embedding':
        if initializer_payload is None or initializer_payload['step']!=200:raise ValueError('Embedding needs explicit complete initializer')
        candidate.CandidateAdapter._validate_embedding_state(state,initializer_payload['state']['z'])
        if payload['initializer_step']!=200 or payload['initializer_sha256']!=init.digest(initializer_payload):raise ValueError('Embedding initializer provenance')
        import numpy as np
        feature_receipt={'E':torch.from_numpy(np.asarray(record['source_E'],np.float64)), 'H':record['source_H']}
        if payload['feature_sha256']!=init.digest(feature_receipt) or payload['optimizer_phase']!='fresh embedding Adam; no initialization moments':raise ValueError('Embedding feature/optimizer provenance')
    else:raise ValueError('Unknown checkpoint phase')
    validate_rng(state['rng'],binding['runtime'],embedding=phase=='embedding')


def validate_quality(value):
    if not isinstance(value,dict) or type(value.get('psnr_infinite')) is not bool or type(value.get('quality_admissible')) is not bool:raise ValueError('Quality schema')
    for key in ('mse_rgb8','ssim_rgb','lpips'):
        if type(value.get(key)) not in (int,float) or not math.isfinite(value[key]):raise ValueError('Finite quality required')
    if value['mse_rgb8']<0 or value['lpips']<0:raise ValueError('Negative distortion')
    if value['psnr_infinite']:
        if value.get('psnr_db') is not None or value['mse_rgb8']!=0:raise ValueError('Infinite PSNR representation')
    elif type(value.get('psnr_db')) not in (int,float) or not math.isfinite(value['psnr_db']) or value['mse_rgb8']<=0:raise ValueError('Finite PSNR required')
    admissible=(value['psnr_infinite'] or value['psnr_db']>35) and value['ssim_rgb']>.9 and value['lpips']<.1
    if value['quality_admissible']!=admissible:raise ValueError('Quality conjunction differs')


def audit_rehearsal_run(directory):
    """CPU exact sealed phase/state/artifact audit; no models/CUDA initialization."""
    import torch
    import m1_candidate_adapter as candidate
    import m1_source_initialization as init
    base=destination(directory);record=read(base/'outputs/worker-run.json')
    if record.get('schema')!=VERSION or record.get('generated_only') is not True or record.get('config')!=configuration() or record.get('scientific_core_sha256')!=scientific_core_sha256():raise ValueError('Generated core/plan differs')
    if record.get('adapter_version')!=candidate.VERSION or record.get('adapter_configuration')!=candidate.CONFIG:raise ValueError('Adapter configuration differs')
    if record.get('outcome') not in ('prefix_completed','completed'):raise ValueError('Not a completed prefix/full worker')
    if record['stage']=='prefix' and record['outcome']!='prefix_completed' or record['stage']!='prefix' and record['outcome']!='completed':raise ValueError('Stage/outcome mismatch')
    journal_receipt=record['worker_journal'];journal_path=destination(journal_receipt['path'])
    if journal_path!=base/'checkpoints/worker-journal.json' or file_sha(journal_path)!=journal_receipt['sha256']:raise ValueError('Worker journal differs')
    source,_,source_receipt=generated_source(record['unit_index'])
    if record['source']!=source_receipt:raise ValueError('Generated source differs')
    locked={v['path']:v['sha256'] for v in read(ROOT/'research/a6-candidate-model-assets.json')['files']}
    model_identity=dict(vae_fp32=locked['sd15-fp16/vae/diffusion_pytorch_model.fp16.safetensors'],vae_public=locked['sd15-fp16/vae/diffusion_pytorch_model.fp16.safetensors'],clip=locked['clip/ViT-B-32.pt'],profile=file_sha(ROOT/record['config']['profile']),scientific_core_sha256=record['scientific_core_sha256'])
    if record['model_identity']!=model_identity:raise ValueError('Pinned model identities differ')
    snapshot=read(base/'outputs/worker-manifest.json')
    if object_sha(snapshot)!=record['manifest_sha256'] or snapshot['git_commit']!=record['commit']:raise ValueError('Manifest/commit snapshot differs')
    inputs={e['path']:e['sha256'] for e in snapshot['inputs']}
    if len(inputs)!=len(snapshot['inputs']):raise ValueError('Duplicate input receipts')
    for dep in dependency_paths():
        rel=dep.relative_to(ROOT).as_posix()
        if inputs.get(rel)!=file_sha(dep):raise ValueError('Worker dependency differs')
    for rel,expected in inputs.items():
        path=ROOT/rel
        if not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Dependency escapes checkout')
        from m1_git_input_identity import verify_git_input
        current=verify_git_input(path,record['commit'],ROOT,expected)
        if record['input_git_identities'].get(rel)!=current:raise ValueError('Recorded byte/Git identity differs')
    if set(record['input_git_identities'])!=set(inputs):raise ValueError('Byte/Git identity inventory differs')
    actual_files={p.relative_to(base).as_posix():file_sha(p) for p in base.rglob('*') if p.is_file() and p.relative_to(base).parts[0] in ('outputs','checkpoints') and p.name not in ('worker-run.json','worker-journal.json','lifecycle-run.json','lifecycle-journal.json','stop-request.json')}
    if actual_files!=record['output_hashes']:raise ValueError('Exact worker output inventory differs')
    cps=record['checkpoints'];expected=range(0,101,10) if record['outcome']=='prefix_completed' else range(0,201,10)
    if record['stage']=='resume':expected=range(100,201,10)
    if [c['step'] for c in cps if c['phase']=='initialization']!=list(expected):raise ValueError('Fixed initialization checkpoint inventory')
    target=torch.from_numpy(source.copy()).permute(2,0,1)[None].float()/255;initializer_payload=None
    for cp in cps:
        path=destination(cp['path'])
        if not path.is_relative_to(base) or file_sha(path)!=cp['sha256']:raise ValueError('Checkpoint ownership/hash')
        payload=torch.load(path,map_location='cpu',weights_only=True)
        validate_phase_checkpoint(payload,record,target,initializer_payload=initializer_payload)
        if payload['step']!=cp['step'] or payload['phase']!=cp['phase']:raise ValueError('Checkpoint receipt phase/step')
        if cp['phase']=='initialization' and cp['step']==200:
            initializer_payload=payload
            if init.digest(payload)!=record['initialization_endpoint_digest']:raise ValueError('Initialization endpoint seal')
    if not cps or record['latest_checkpoint']!={k:cps[-1][k] for k in ('path','sha256')}:raise ValueError('Latest checkpoint differs')
    if record['outcome']=='completed':
        if [c['step'] for c in cps if c['phase']=='embedding']!=list(range(0,101,10)):raise ValueError('Fixed embedding inventory')
        endpoint=torch.load(cps[-1]['path'],map_location='cpu',weights_only=True)
        if init.digest(endpoint)!=record['embedding_endpoint_digest']:raise ValueError('Embedding endpoint seal')
        rows=record['conditions']
        if len(rows)!=4 or {(r['control'],r['dose']) for r in rows}!={(a,d) for a in ('C0','C1') for d in ('clean','vae_cycle')} or any(r['outcome']!='completed' for r in rows):raise ValueError('Four endpoint conditions required')
        from PIL import Image
        import numpy as np
        import m1_blind_noise_core as core
        for row in rows:
            for field in ('quality_vs_source','quality_vs_same_arm_clean'):validate_quality(row.get(field))
            if type(row.get('extract_seconds')) not in (int,float) or not math.isfinite(row['extract_seconds']) or row['extract_seconds']<0:raise ValueError('Readout timing')
            for field in ('image','reader_latent'):
                path=destination(row[field]['path'])
                if not path.is_relative_to(base) or file_sha(path)!=row[field]['sha256']:raise ValueError('Endpoint artifact receipt')
            with Image.open(row['image']['path']) as image:
                rgb=np.asarray(image).copy()
            if rgb.shape!=(512,512,3) or rgb.dtype!=np.uint8 or hashlib.sha256(rgb.tobytes()).hexdigest()!=row['rgb8_sha256']:raise ValueError('Endpoint pixel identity')
            z=np.load(row['reader_latent']['path'],allow_pickle=False)
            if set(row['owner_decisions'])!=set(record['config']['owners']):raise ValueError('Fixed owner query inventory')
            for owner in record['config']['owners']:
                if core.scores(z,row['suspect_E'],row['suspect_H'],owner)!=row['owner_decisions'][owner]:raise ValueError('Independent blind readout differs')
    return record


def compare_full_resume(full,resumed):
    """Exact sealed states at every overlapping step, endpoints and reader output."""
    import torch
    import m1_source_initialization as init
    left=audit_rehearsal_run(full);right=audit_rehearsal_run(resumed)
    if left['stage']!='full' or right['stage']!='resume' or left['outcome']!='completed' or right['outcome']!='completed' or left['source']!=right['source']:raise ValueError('Same-source complete full/resume endpoints required')
    states=lambda r:{(v['phase'],v['step']):v for v in r['checkpoints']}
    l,r=states(left),states(right);overlap=sorted(set(l)&set(r))
    expected=[('embedding',n) for n in range(0,101,10)]+[('initialization',n) for n in range(100,201,10)]
    overlap_checks={f'{phase}-{step}':init.digest(torch.load(l[(phase,step)]['path'],map_location='cpu',weights_only=True))==init.digest(torch.load(r[(phase,step)]['path'],map_location='cpu',weights_only=True)) for phase,step in overlap}
    images=lambda x:{(v['control'],v['dose']):v['rgb8_sha256'] for v in x['conditions']}
    decisions=lambda x:{(v['control'],v['dose']):v['owner_decisions'] for v in x['conditions']}
    checks=dict(overlap_inventory_exact=overlap==expected,overlap_states_adam_rng_exact=bool(overlap_checks) and all(overlap_checks.values()),
      initialization_exact=left['initialization_endpoint_digest']==right['initialization_endpoint_digest'],
      embedding_adam_rng_exact=left['embedding_endpoint_digest']==right['embedding_endpoint_digest'],
      endpoint_rgb8_exact=images(left)==images(right),blind_decisions_exact=decisions(left)==decisions(right))
    return dict(passes=all(checks.values()),checks=checks,overlap_checks=overlap_checks,scientific_verdict='NOT_EVIDENCE')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest',required=True);parser.add_argument('--output-dir',required=True)
    args=parser.parse_args();return run(args.manifest,args.output_dir)

if __name__=='__main__':raise SystemExit(main())
