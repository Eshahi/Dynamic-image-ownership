"""Development-only deterministic original200 -> unchanged A-C100 worker.

No model loads on import. Scientific math is imported from the live, unchanged
terminal continuous module. IO orchestration is versioned independently.
"""
from __future__ import annotations
import argparse, gc, hashlib, importlib.metadata, json, math, os, random, subprocess, sys, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_terminal_continuous as component
import m1_source_initialization_audit as initialization
core,blind,old_a,residual,util,codec,repeatability=(component.core,component.blind,component.old_a,component.residual,component.util,component.codec,component.repeatability)
MAIN=component.MAIN
VERSION='m1-terminal-continuous-e2e-v1'
IDS=(1675,4795,6012,25394,80932,109798,134882,147498,177015,190676,468505,499768)
PILOT_IDS=IDS[:2]
Embedder,FixedSourceScores,PublicReader=(component.Embedder,component.FixedSourceScores,component.PublicReader)
optimize,detect,checkpoint_save,checkpoint_load=(component.optimize,component.detect,component.checkpoint_save,component.checkpoint_load)
move_inference_models,gpu_allocation_budget=(component.move_inference_models,component.gpu_allocation_budget)

def configuration():
    cfg=component.configuration()
    cohort=json.loads((ROOT/'research/m1-reconstruction-dev.json').read_text())
    if tuple(c['id'] for c in cohort['cases'])!=IDS:raise ValueError('Fixed twelve development sources required')
    cfg.update(schema=VERSION,cases=cohort['cases'],initialization='verified deterministic original200 bridge only',
        execution_phase_seed=0,execution_rng_policy='fresh_phase_zero_resume_restores_saved_rng',
        source_execution='one source per owned process; original two-source gate before other ten',
        gate='clean quality+clean both+VAE semantic+all fourteen per-source negative queries')
    del cfg['reconstruction_run']
    return cfg

def planned(source_ids):
    return [dict(id=f'{ident}-{arm}-{dose}',source_id=ident,control=arm,dose=dose,
        outcome='planned',human_visual_verdict=None) for ident in source_ids
        for arm in ('C0','C1') for dose in ('clean','vae_cycle')]

def source_gate(rows,source_id):
    import m1_analyze_terminal_continuous as analyzer
    expected={r['id']:r for r in planned([source_id])}
    complete=isinstance(rows,list) and len(rows)==4 and all(isinstance(r,dict) for r in rows)
    complete=complete and {r['id'] for r in rows}==set(expected)
    complete=complete and all(r.get('outcome')=='completed' and all(r.get(k)==expected[r['id']][k]
        for k in ('source_id','control','dose')) and set(r.get('owner_decisions',{}))==set(core.OWNERS) for r in rows)
    def valid_decision(d):
        if not isinstance(d,dict) or any(type(d.get(k)) not in (float,int) or not math.isfinite(d[k]) for k in ('s','i')):return False
        expected=core.classify_scores(d['s'],d['i'])
        return d.get('flags')==expected['flags'] and d.get('state')==expected['state']
    complete=complete and all(valid_decision(d) for r in rows for d in r['owner_decisions'].values())
    negatives=[];clean_quality=clean_both=cycle_semantic=0
    for row in rows:
        if not isinstance(row,dict):continue
        if row.get('control')=='C1' and row.get('dose')=='clean':
            q=row.get('quality_vs_source',{})
            clean_quality+=q.get('quality_admissible') is True and analyzer.quality_pass(q) is True
            clean_both+=row.get('owner_decisions',{}).get(core.OWNERS[0],{}).get('state')=='both_match'
        if row.get('control')=='C1' and row.get('dose')=='vae_cycle':
            cycle_semantic+=row.get('owner_decisions',{}).get(core.OWNERS[0],{}).get('flags',{}).get('s') is True
        for owner in core.OWNERS if row.get('control')=='C0' else core.OWNERS[1:]:
            flags=row.get('owner_decisions',{}).get(owner,{}).get('flags',{})
            negatives.append(flags.get('s') is False and flags.get('i') is False)
    return dict(planned_source_n=1,planned_conditions=4,planned_owner_queries=16,
        complete=complete,clean_quality_n=clean_quality,clean_both_n=clean_both,vae_semantic_n=cycle_semantic,
        negative_queries_below_both_n=sum(negatives),planned_negative_queries=14,
        passes=complete and clean_quality==clean_both==cycle_semantic==1 and len(negatives)==14 and all(negatives))

def two_source_gate(rows):
    if not isinstance(rows,list):raise ValueError('Condition list required')
    gates={str(s):source_gate([r for r in rows if r.get('source_id')==s],s) for s in PILOT_IDS}
    complete=len(rows)==8 and all(g['complete'] for g in gates.values())
    return dict(planned_conditions=8,planned_owner_queries=32,planned_negative_queries=28,
        complete=complete,source_gates=gates,passes=complete and all(g['passes'] for g in gates.values()))

def read(path):
    def invalid(v):raise ValueError('Nonfinite JSON token: '+v)
    return json.loads(Path(path).read_text(encoding='utf-8'),parse_constant=invalid)

def checked_record(path):
    path=Path(path).resolve()
    if not path.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('MAIN development receipt required')
    value=read(path)
    return value,dict(path=str(path),sha256=util.sha(path))

def require_owner_extension(path,old_sha):
    value,receipt=checked_record(path)
    current=util.sha(ROOT/'scripts/m1_blind_noise_core.py')
    expected={'legacy_cells_per_pass':128,'legacy_passes':2,'development_replayed_queries':32,
        'projection_cells':512,'alignment_cells':8192,'null_cells':512,'distinct_maps':20}
    if (value.get('schema')!='m1-owner-extension-audit-v1' or value.get('outcome')!='completed'
        or value.get('data_split')!='synthetic-and-retained-development'
        or value.get('compatibility_passed') is not True or value.get('errors')!=[]
        or value.get('old_source_sha256')!=old_sha or value.get('new_source_sha256')!=current
        or any(value.get('summary',{}).get(k)!=v for k,v in expected.items())):
        raise ValueError('Full matching owner-extension compatibility audit required')
    pinned=value.get('committed_files',{})
    for rel in ('scripts/m1_owner_extension_audit.py','scripts/m1_blind_noise_core.py'):
        if pinned.get(rel)!=util.sha(ROOT/rel):raise ValueError('Owner audit executed-code receipt differs')
    for rel,digest in pinned.items():
        p=(ROOT/rel).resolve()
        if not p.is_relative_to(ROOT.resolve()) or util.sha(p)!=digest:raise ValueError('Owner audit dependency changed')
    base=Path(path).resolve().parent
    if not value.get('outputs'):raise ValueError('Owner audit outputs missing')
    if value['outputs']!={p.name:util.sha(p) for p in base.iterdir() if p.is_file() and p.name!='run.json'}:
        raise ValueError('Owner audit output inventory differs')
    for name,digest in value['outputs'].items():
        p=(base/name).resolve()
        if not p.is_relative_to(base) or util.sha(p)!=digest:raise ValueError('Owner audit output changed')
    return receipt

def require_component_analysis(path,owner_extension_receipt=None):
    value,receipt=checked_record(path)
    gate=value.get('gate',{})
    if (value.get('schema')!='m1-terminal-continuous-analysis-v1' or value.get('data_split')!='development'
        or value.get('outcome')!='completed' or value.get('errors')!=[] or gate.get('promotion') is not True
        or gate.get('receipt_integrity') is not True or gate.get('inventory_complete') is not True
        or gate.get('negative_queries')!={'planned':28,'observed':28,'below_both':28}):
        raise ValueError('Passing complete original two-source component analysis required')
    for k in ('clean_quality','clean_blind_both','cycle_blind_semantic'):
        if gate.get(k)!={'planned':2,'observed':2,'positive':2}:raise ValueError('Component endpoint gate differs')
    inputs=value.get('inputs',{});runs=[p for p in inputs if Path(p).name=='run.json']
    if len(runs)!=1:raise ValueError('Exactly one pinned component run required')
    run,r=checked_record(runs[0])
    if r['sha256']!=inputs[runs[0]] or run.get('schema')!=component.VERSION or run.get('outcome')!='completed':
        raise ValueError('Component source receipt differs')
    for p,h in inputs.items():
        if not Path(p).resolve().is_relative_to(Path(runs[0]).parent) or util.sha(p)!=h:raise ValueError('Component input changed')
    if component.pilot_gate(run.get('conditions',[]))['passes'] is not True:raise ValueError('Component raw gate fails')
    old=run.get('committed_files',{}).get('scripts/m1_blind_noise_core.py',{}).get('working_sha256')
    if not isinstance(old,str):raise ValueError('Component scientific-core receipt missing')
    if old!=util.sha(ROOT/'scripts/m1_blind_noise_core.py'):
        if owner_extension_receipt is None:raise ValueError('Changed public owner core requires explicit compatibility proof')
        receipt['owner_extension']=require_owner_extension(owner_extension_receipt,old)
    for name,digest in value.get('outputs',{}).items():
        p=Path(path).parent/name
        if not p.resolve().is_relative_to(Path(path).resolve().parent) or util.sha(p)!=digest:raise ValueError('Component analysis output changed')
    return receipt

def require_expansion(path,method_core_sha256):
    value,receipt=checked_record(path)
    if (value.get('schema')!='m1-terminal-e2e-pilot-merge-v1' or value.get('data_split')!='development'
        or value.get('outcome')!='completed' or value.get('method_core_sha256')!=method_core_sha256
        or value.get('gate',{}).get('passes') is not True):raise ValueError('Passing same-core e2e pilot merge required')
    rows=[]
    for r in value.get('source_runs',[]):
        run,current=checked_record(r['path'])
        if current!=r or run.get('outcome')!='completed' or run.get('method_core_sha256')!=method_core_sha256:
            raise ValueError('Pilot run changed/incomplete')
        audit_source_run(Path(r['path']).parent)
        rows.extend(run.get('conditions',[]))
    if two_source_gate(rows)!=value['gate']:raise ValueError('Pilot gate mismatch')
    return receipt

def phase_seed_zero():
    import numpy as np
    import torch
    random.seed(0);np.random.seed(0);torch.manual_seed(0);torch.cuda.manual_seed_all(0)


def dependency_paths():
    paths=[Path(__file__),ROOT/'research/m1-terminal-e2e-dev.json',ROOT/'scripts/m1_terminal_continuous.py',
        ROOT/'scripts/m1_source_initialization_audit.py',ROOT/'scripts/m1_source_initialization.py',
        ROOT/'research/m1-end-to-end-initialization-design.md',ROOT/'research/m1-terminal-continuous-expansion-design.md',
        ROOT/'research/m1-terminal-continuous-design.md',ROOT/'research/m1-terminal-continuous-recovery.md',
        ROOT/'scripts/m1_terminal_repeatability.py',ROOT/'scripts/m1_analyze_terminal_continuous.py',ROOT/'scripts/m1_owner_extension_audit.py',ROOT/'research/m1-terminal-continuous-replay-diagnosis.md',
        ROOT/'scripts/m1_blind_noise_core.py',ROOT/'scripts/m1_blind_noise.py',ROOT/'scripts/m1_dual_latent.py',
        ROOT/'scripts/m1_phase_residual.py',ROOT/'scripts/m1_phasemark.py',ROOT/'scripts/m1_latent_reconstruction.py',
        ROOT/'scripts/revised_watermark_v5.py',ROOT/'scripts/revised_watermark_v4.py',ROOT/'scripts/three_threat_models.py',
        ROOT/'scripts/three_threat_protocol.py',ROOT/'scripts/a6_clip_visual.py',ROOT/'scripts/verify_science_assets.py',
        ROOT/'scripts/check_a6_lpips_assets.py',ROOT/'research/a6-candidate-model-assets.json',
        ROOT/'research/m1-reconstruction-dev.json',ROOT/'configs/revised-watermark-v5.example.json']
    return list(dict.fromkeys(paths+initialization.scientific_paths()))


def run(manifest_path,output,source_id,bridge_dir,component_analysis,resume_from=None,expansion_receipt=None,owner_extension_receipt=None):
    import numpy as np
    from PIL import Image
    manifest_path=Path(manifest_path).resolve();output=Path(output).resolve();cfg=configuration();all_cfg=cfg;cfg=dict(cfg,cases=[c for c in cfg['cases'] if c['id']==source_id])
    if manifest_path!=(ROOT/'research/m1-terminal-e2e-dev.json').resolve():raise ValueError('Canonical committed manifest path required')
    if read(manifest_path)!=all_cfg:raise ValueError('Exact frozen manifest required')
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN development output required')
    if type(source_id) is not int or source_id not in IDS:raise ValueError('Fixed development source only')
    component_receipt=require_component_analysis(component_analysis,owner_extension_receipt)
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic();previous_duration=0.
    rows={r['id']:r for r in planned([source_id])}
    record=dict(schema=VERSION,data_split='development',command=sys.argv,config=cfg,seeds=[0],
                outcome='started',duration_seconds=0.,case_events=[],conditions=list(rows.values()),
                optimized_variables=['unscaled terminal VAE latent'],nfe_unet=0,
                detector_side_information=['suspect RGB8','candidate public OwnerID','pinned VAE/CLIP/hash profile and maps'])
    record.update(run_kind='scientific-pilot',process_id=os.getpid(),
        control_reference='C0 is canonical source; pure u0 decode quality separately recorded')
    def persist():util.write(output/'run.json',record)
    def event(value):
        with (output/'journal.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(value,allow_nan=False)+'\n')
    def retain(row):
        event(dict(kind='condition',**row));util.write(output/'conditions.json',list(rows.values()));persist()
    def check():
        if previous_duration+time.monotonic()-started>cfg['run_seconds_cap']:raise RuntimeError('Cumulative1800s cap')
        ram=util.working_set_bytes();record['peak_rss_bytes']=max(record.get('peak_rss_bytes',0),ram)
        if ram>cfg['ram_budget_bytes']:raise RuntimeError('RAM cap')
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise RuntimeError('Artifact cap')
        if 'torch' in sys.modules:
            tm=sys.modules['torch']
            effective=record.get('gpu_allocation_budget',{}).get('effective_allocation_bytes',cfg['gpu_budget_bytes'])
            if tm.cuda.is_initialized() and tm.cuda.memory_allocated()>effective:raise RuntimeError('Effective GPU allocation cap')
    for row in rows.values():retain(row)
    try:
        deps=dependency_paths()
        record.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            committed_files=util.require_committed(deps),manifest_sha256=util.sha(manifest_path),
            component_analysis=component_receipt,source_id=source_id,bridge_dir=str(Path(bridge_dir).resolve()))
        record['scientific_files']=repeatability.scientific_files(record['committed_files'])
        record['method_core_files']={k:v['working_sha256'] for k,v in record['committed_files'].items()
            if not k.lower().endswith('.md')}
        record['method_core_sha256']=component.canonical_sha(dict(files=record['method_core_files'],config=all_cfg))
        fingerprint=dict(method_core_sha256=record['method_core_sha256'],manifest_sha256=record['manifest_sha256'])
        if source_id not in PILOT_IDS:
            if expansion_receipt is None:raise ValueError('Original two-source e2e gate required before other ten')
            record['expansion_receipt']=require_expansion(expansion_receipt,record['method_core_sha256'])
        record['execution_variant']=repeatability.VERSION
        prior=None
        if resume_from:
            resume_from=Path(resume_from).resolve()
            if not resume_from.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Resume source must be MAIN development run')
            prior=json.loads((resume_from/'run.json').read_text())
            if prior.get('schema')!=VERSION or prior.get('data_split')!='development' or any(prior.get(k)!=v for k,v in fingerprint.items()):raise ValueError('Resume requires identical version/commit/receipts')
            if prior.get('run_kind')!='scientific-pilot' or prior.get('execution_variant')!=repeatability.VERSION:raise ValueError('Cannot resume a probe or earlier execution variant')
            if prior.get('outcome')=='completed':raise ValueError('Completed run is not a resume source')
            previous_duration=prior['duration_seconds']
            if prior.get('source_id')!=source_id or prior.get('config')!=cfg:raise ValueError('Resume source/config differs')
            record['resume_input']=dict(path=str(resume_from),run_sha256=util.sha(resume_from/'run.json'),duration_seconds=previous_duration)
        (output/'manifest.json').write_bytes(manifest_path.read_bytes());persist();check()
        from three_threat_models import block_network,verify_assets,load_lpips,lpips_score,clip_feature
        block_network()
        import torch
        from diffusers import AutoencoderKL
        from diffusers.image_processor import VaeImageProcessor
        from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
        from transformers import CLIPImageProcessor
        from a6_clip_visual import load_visual_encoder
        from m1_latent_reconstruction import quality
        record['deterministic_execution']=repeatability.configure()
        if not torch.cuda.is_available():raise RuntimeError('CUDA required')
        torch.manual_seed(0);np.random.seed(0);random.seed(0)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False
        record['device_identity']=dict(name=torch.cuda.get_device_name(0),capability=list(torch.cuda.get_device_capability(0)),
            cuda_version=torch.version.cuda,cudnn_version=torch.backends.cudnn.version())
        record['driver_inventory']=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,driver_version,pci.bus_id','--format=csv,noheader'],text=True).strip()
        free_bytes,total_bytes=torch.cuda.mem_get_info(0)
        record['gpu_allocation_budget']=gpu_allocation_budget(cfg['gpu_budget_bytes'],int(free_bytes),int(total_bytes),cfg['gpu_reserve_bytes'])
        torch.cuda.set_per_process_memory_fraction(record['gpu_allocation_budget']['allocator_fraction'])
        persist();check()
        assets,package=verify_assets(util.ASSETS,ROOT/'research/a6-candidate-model-assets.json')
        def load_vae(dtype):
            model=AutoencoderKL.from_pretrained(util.ASSETS/'sd15-fp16/vae',variant='fp16',use_safetensors=True,local_files_only=True,torch_dtype=dtype).eval().requires_grad_(False).to('cuda')
            if float(model.config.scaling_factor)!=.18215:raise ValueError('Unexpected scaling factor')
            return model
        embedder=Embedder(load_vae(torch.float32));reader_vae=load_vae(torch.float16)
        processor=VaeImageProcessor(vae_scale_factor=8)
        safety=StableDiffusionSafetyChecker.from_pretrained(util.ASSETS/'sd15-fp16/safety_checker',variant='fp16',use_safetensors=True,local_files_only=True,torch_dtype=torch.float16).eval().requires_grad_(False).to('cuda')
        safety_processor=CLIPImageProcessor.from_pretrained(util.ASSETS/'sd15-fp16/feature_extractor',local_files_only=True)
        clip,transform=load_visual_encoder(util.ASSETS/'clip/ViT-B-32.pt',device='cpu')
        metric=load_lpips(util.ASSETS,package)
        profile=codec.validate_profile(codec.load_profile(ROOT/cfg['profile']))
        def feature(rgb):
            value=np.asarray(clip_feature(clip,transform,rgb),np.float64).reshape(-1)
            norm=np.linalg.norm(value)
            if value.shape!=(512,) or not np.isfinite(value).all() or norm<=0:raise ValueError('Invalid CLIP')
            return value/norm
        public=PublicReader(reader_vae,processor,feature,profile)
        record.update(assets=assets,environment={'python':sys.version,**{p:importlib.metadata.version(p) for p in ('torch','numpy','scipy','Pillow','diffusers','lpips')}},
            latent_units='unscaled VAE posterior coordinate for optimization; reader output times.18215',
            lpips_learned_sha256=util.sha(package/'weights/v0.1/alex.pth'),initializer_run_sha256=util.sha(Path(bridge_dir)/'run.json'))
        record['execution_runtime']=dict(threads=torch.get_num_threads(),
            fill_uninitialized_memory=bool(torch.utils.deterministic.fill_uninitialized_memory),
            embedding_device='cuda',embedding_dtype='float32',public_reader_dtype='float16')
        def tensor(rgb,dtype=torch.float32):return torch.from_numpy(rgb.copy()).permute(2,0,1)[None].to('cuda',dtype=dtype)/255
        def array(value):return value.detach().float().cpu().numpy()[0].transpose(1,2,0).astype(np.float64)
        def safety_check(rgb):
            with torch.inference_mode():
                inputs=safety_processor([Image.fromarray(rgb)],return_tensors='pt').pixel_values.to('cuda',dtype=torch.float16)
                _,flags=safety(images=rgb[None].astype(np.float32)/255,clip_input=inputs)
            if flags!=[False]:raise RuntimeError('Safety checker blocked output')
        def save_png(name,rgb):
            safety_check(rgb);path=output/(name+'.png');Image.fromarray(rgb).save(path)
            with Image.open(path) as im:saved=np.asarray(im.convert('RGB')).copy()
            if not np.array_equal(saved,rgb):raise ValueError('PNG pixel mismatch')
            return saved,dict(path=str(path),sha256=util.sha(path),rgb8_sha256=hashlib.sha256(saved.tobytes()).hexdigest())
        def save_array(name,value):
            path=output/(name+'.npy');np.save(path,value,allow_pickle=False)
            return dict(path=str(path),sha256=util.sha(path))
        def cycle(rgb):
            with torch.inference_mode():
                x=processor.preprocess(Image.fromarray(rgb)).to('cuda',dtype=torch.float16)
                z=reader_vae.encode(x).latent_dist.mode()*.18215
                decoded=reader_vae.decode(z/.18215,return_dict=False)[0]
                safety_input=safety_processor(processor.postprocess(decoded,output_type='pil'),return_tensors='pt').pixel_values.to('cuda',dtype=torch.float16)
                checked,flags=safety(images=decoded,clip_input=safety_input)
                if flags!=[False]:raise RuntimeError('VAE cycle safety checker blocked output')
                value=processor.postprocess(checked,output_type='np',do_denormalize=[True])[0]
            return blind.rgb8(value)
        def q(a,b):
            val=quality(a,b);val['lpips']=lpips_score(metric,a,b)
            val['quality_admissible']=(val['psnr_infinite'] or val['psnr_db']>35) and val['ssim_rgb']>.9 and val['lpips']<.1
            return val
        def placement(device,ident):
            def snapshot(stage):
                torch.cuda.synchronize()
                free,total=torch.cuda.mem_get_info(0)
                value=dict(kind='gpu_memory',source_id=ident,stage=stage,
                    allocated_bytes=torch.cuda.memory_allocated(),reserved_bytes=torch.cuda.memory_reserved(),
                    peak_allocated_bytes=torch.cuda.max_memory_allocated(),free_bytes=int(free),total_bytes=int(total))
                event(value);return value
            before=snapshot('before_inference_models_to_'+device)
            sizes=move_inference_models((reader_vae,safety),device)
            gc.collect();torch.cuda.empty_cache()
            after=snapshot('after_inference_models_to_'+device)
            ce.setdefault('memory_placements',[]).append(dict(device=device,model_tensor_bytes=sizes,before=before,after=after));persist();check()
        for case in cfg['cases']:
            check();ident=case['id'];source,_=old_a.source_rgb(case)
            source,receipt=save_png(f'{ident}-source',source)
            ce=dict(source_id=ident,outcome='started',source=receipt,checkpoints=[]);record['case_events'].append(ce);persist()
            E=feature(source);H=codec.perceptual_hash(codec.luminance_from_rgb(source.tolist()),profile=profile)
            ce.update(source_E=E.tolist(),source_H=H)
            u0,initial=initialization.load_development_bridge(bridge_dir,ident,receipt['rgb8_sha256'])
            ce['initialization']=initial
            identity=dict(version=VERSION,**fingerprint,source_id=ident,source_rgb8_sha256=receipt['rgb8_sha256'],initialization=initial,
                execution_variant=record['execution_variant'],run_kind=record['run_kind'])
            resume=None
            if prior:
                old=[e for e in prior['case_events'] if e['source_id']==ident]
                if old and old[0]['checkpoints']:
                    selected=max(old[0]['checkpoints'],key=lambda e:e['step'])
                    resume=checkpoint_load(selected,identity);ce['resume_checkpoint']=selected
            source_tensor=tensor(source);u0=u0.to('cuda');oracle=FixedSourceScores(E,H,core.OWNERS[0],'cuda')
            def save(step,u,optimizer):
                cr=checkpoint_save(output/f'{ident}-step{step:03d}.pt',u,optimizer,step,identity)
                ce['checkpoints'].append(cr);event(dict(kind='checkpoint',source_id=ident,**cr));persist();check()
            def optimization_event(row):event(dict(kind='optimizer',source_id=ident,**row))
            placement('cpu',ident)
            # Reset only a fresh phase, after all models/features/placement.
            if resume is None:phase_seed_zero()
            fit_started=time.monotonic()
            fit_cfg=cfg
            result=optimize(embedder,source_tensor,u0,oracle,fit_cfg,optimization_event,save,check,resume)
            ce['embedding_seconds']=time.monotonic()-fit_started
            placement('cuda',ident)
            raw=array(result['residual']);marked,cap=residual.cap(source,raw)
            ce.update(cap=cap,beta_final=result['beta'],residual_rms=result['rho'],
                final_surrogate_scores=result['surrogate_scores'],final_surrogate_cycle_scores=result['surrogate_cycle_scores'],
                surrogate_vs_capped_rmse=float(np.sqrt(np.mean((array(result['surrogate'])-marked.astype(np.float64)/255)**2))),
                pure_reference_quality=q(source,blind.rgb8(array(result['reference']))),pure_final_quality=q(source,blind.rgb8(array(result['decoded']))),
                float_arrays={name:save_array(f'{ident}-{name}',array(result[name])) for name in ('reference','decoded','residual','surrogate')})
            images={('C0','clean'):source,('C1','clean'):marked}
            images[('C0','vae_cycle')]=cycle(source);images[('C1','vae_cycle')]=cycle(marked)
            for (arm,dose),rgb in images.items():
                check();row=rows[f'{ident}-{arm}-{dose}'];row['outcome']='started';retain(row)
                rgb,img=save_png(f'{ident}-{arm}-{dose}',rgb)
                tick=time.monotonic();decisions={owner:detect(rgb,owner,public) for owner in core.OWNERS};elapsed=time.monotonic()-tick
                e,h,z=public.observations(rgb)
                with torch.no_grad():z32=embedder.encode(tensor(rgb)).float().cpu().numpy().reshape(-1).astype(np.float64)
                row.update(outcome='completed',image=img,source=receipt,owner_decisions=decisions,extract_seconds=elapsed,
                    source_clip_cosine=float(E@e),source_phash_distance=int((H^h).bit_count()),suspect_E=e.tolist(),suspect_H=h,
                    source_template_oracle_fp16=core.scores(z,E,H,core.OWNERS[0]),source_template_oracle_fp32=core.scores(z32,E,H,core.OWNERS[0]),
                    terminal_reader_latent=save_array(f'{ident}-{arm}-{dose}-reader-z',z),
                    terminal_fp32_latent=save_array(f'{ident}-{arm}-{dose}-fp32-z',z32),
                    projection_diagnostics={owner:core.projection_diagnostic(E,H,e,h,owner) for owner in core.OWNERS},
                    quality_vs_source=q(source,rgb),quality_vs_same_arm_clean=q(images[(arm,'clean')],rgb))
                retain(row)
            ce['outcome']='completed';persist()
            del source_tensor,u0,oracle,result;gc.collect();torch.cuda.empty_cache();check()
        record['outcome']='completed'
        record['peak_allocated_bytes']=torch.cuda.max_memory_allocated()
    except (Exception,KeyboardInterrupt) as error:
        record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error),traceback=traceback.format_exc())
        if record['case_events'] and record['case_events'][-1]['outcome']=='started':record['case_events'][-1]['outcome']=record['outcome']
    finally:
        for row in rows.values():
            if row['outcome'] in ('planned','started'):row['outcome']='not_completed_after_stop';event(dict(kind='condition',**row))
        util.write(output/'conditions.json',list(rows.values()))
        record.update(duration_seconds=previous_duration+time.monotonic()-started,attempt_duration_seconds=time.monotonic()-started,
            gate=source_gate(list(rows.values()),source_id),
            output_hashes={p.name:util.sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'})
        persist()
    return 0 if record['outcome']=='completed' else 1


def audit_source_run(directory):
    """CPU-only stage/endpoint audit, reusing the original independent reader audit.

    Does not infer CLIP/LPIPS anew. Those model observations remain recorded.
    GPU initializer audit is revalidated from retained complete checkpoints.
    """
    import numpy as np
    import m1_analyze_terminal_continuous as analyzer
    base=Path(directory).resolve();record,receipt=checked_record(base/'run.json')
    sid=record.get('source_id');cfg=configuration()
    if type(sid) is not int or sid not in IDS:raise ValueError('Unknown source')
    per_cfg=dict(cfg,cases=[c for c in cfg['cases'] if c['id']==sid])
    if (record.get('schema')!=VERSION or record.get('data_split')!='development'
        or record.get('outcome')!='completed' or record.get('config')!=per_cfg
        or read(base/'manifest.json')!=cfg or record.get('manifest_sha256')!=util.sha(base/'manifest.json')):
        raise ValueError('Incomplete or changed source/config')
    component_receipt=record['component_analysis']
    current_component=require_component_analysis(component_receipt['path'],component_receipt.get('owner_extension',{}).get('path'))
    if current_component!=component_receipt:raise ValueError('Component/owner proof changed')
    if util.sha(record['component_analysis']['path'])!=record['component_analysis']['sha256']:raise ValueError('Component receipt changed')
    deps=record.get('committed_files',{})
    expected_dependencies={p.relative_to(ROOT).as_posix() for p in dependency_paths()}
    if set(deps)!=expected_dependencies:raise ValueError('Method dependency inventory incomplete/unexpected')
    if not deps or any(util.sha(ROOT/k)!=v['working_sha256'] for k,v in deps.items()):raise ValueError('Current method dependency changed')
    expected_core={k:v['working_sha256'] for k,v in deps.items() if not k.lower().endswith('.md')}
    if expected_core!=record.get('method_core_files') or component.canonical_sha(dict(files=expected_core,config=cfg))!=record.get('method_core_sha256'):
        raise ValueError('Method core hash mismatch')
    actual={p.name:util.sha(p) for p in base.iterdir() if p.is_file() and p.name!='run.json'}
    if actual!=record.get('output_hashes'):raise ValueError('Output inventory changed')
    if read(base/'conditions.json')!=record.get('conditions'):raise ValueError('Condition snapshot differs')
    if record.get('execution_variant')!=repeatability.VERSION:raise ValueError('Deterministic execution variant missing')
    if not analyzer.finite(record.get('duration_seconds')) or not 0<=record['duration_seconds']<=cfg['run_seconds_cap']:raise ValueError('Wall budget')
    if type(record.get('peak_rss_bytes')) is not int or not 0<record['peak_rss_bytes']<=cfg['ram_budget_bytes']:raise ValueError('RAM receipt missing/exceeded')
    budget=record['gpu_allocation_budget']
    if budget!=gpu_allocation_budget(cfg['gpu_budget_bytes'],budget['free_bytes_before_models'],budget['total_bytes'],cfg['gpu_reserve_bytes']):raise ValueError('GPU allocation receipt')
    if type(record.get('peak_allocated_bytes')) is not int or not 0<=record['peak_allocated_bytes']<=budget['effective_allocation_bytes']:raise ValueError('GPU peak')
    if sum(p.stat().st_size for p in base.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise ValueError('Artifact budget')
    events=record.get('case_events',[])
    if len(events)!=1 or events[0].get('source_id')!=sid or events[0].get('outcome')!='completed':raise ValueError('Exactly one completed source event required')
    ce=events[0];audit=analyzer.Audit(base)
    source=audit.receipt(ce['source'],'source',png=True)
    canonical,_=old_a.source_rgb(per_cfg['cases'][0])
    if not np.array_equal(source,canonical):raise ValueError('Canonical source differs')
    if Path(ce['source']['path']).name!=f'{sid}-source.png':raise ValueError('Source artifact membership')
    init=ce['initialization'];bridge=Path(record['bridge_dir']);ir=read(bridge/'run.json')
    if util.sha(bridge/'run.json')!=record['initializer_run_sha256'] or util.sha(bridge/'run.json')!=init['run_json_sha256']:raise ValueError('Initializer receipt changed')
    if init.get('initializer_kind')!='verified deterministic original200' or init.get('embedding_optimizer')!='fresh independent Adam':raise ValueError('Forbidden initializer fallback')
    proof=initialization.checked(init['audit_proof']);_,entries=initialization.verify_audit(proof.parent)
    if init['initializer_scientific_core_sha256']!=entries[0][1]['scientific_core_sha256']:raise ValueError('Initializer scientific core mismatch')
    if ir.get('stage')=='initialize':initialization.load_run(bridge,'initialize')
    elif ir.get('stage')!='compare':raise ValueError('Initializer stage differs')
    if ir['u0_bridge']['source_id']!=sid or ir['u0_bridge']['initializer_state']!=init['full_initializer_state']:raise ValueError('Initializer source/full checkpoint mismatch')
    import torch
    import m1_source_initialization as initializer_adapter
    full=initializer_adapter.load_checkpoint(initialization.checked(init['full_initializer_state']))
    initializer_adapter._validate_payload(full,full['identity'],full['target_sha256'],full['runtime'])
    endpoint_path=audit.receipt(init,'initializer endpoint',inside=False)
    endpoint=torch.load(endpoint_path,map_location='cpu',weights_only=True)
    if (full['step']!=200 or full['identity']['source_id']!=sid
        or full['identity']['source_rgb8_sha256']!=ce['source']['rgb8_sha256']
        or full['identity']['scientific_core_sha256']!=init['initializer_scientific_core_sha256']
        or endpoint.get('step')!=200 or not torch.equal(endpoint['z'],full['z'])):
        raise ValueError('Initializer full-state/bridge tensor differs')
    if init['checkpoint_receipt']['step']!=200 or init['full_initializer_state']['step']!=200 or init['source_rgb8_sha256']!=ce['source']['rgb8_sha256']:raise ValueError('Initializer endpoint/source mismatch')
    steps=[r['step'] for r in ce['checkpoints']]
    start=ce.get('resume_checkpoint',{}).get('step',0)
    if steps!=list(range(start,101,10)):raise ValueError('Full every-ten embedding checkpoint sequence missing')
    for r in ce['checkpoints']:
        audit.receipt(r,'checkpoint'+str(r['step']))
        if Path(r['path']).name!=f'{sid}-step{r["step"]:03d}.pt':raise ValueError('Checkpoint filename')
    arrays={k:audit.receipt(v,'float:'+k,array=True) for k,v in ce['float_arrays'].items()}
    if set(arrays)!={'reference','decoded','residual','surrogate'} or any(v.shape!=(512,512,3) for v in arrays.values()):raise ValueError('Stage arrays missing')
    for k,v in ce['float_arrays'].items():
        if Path(v['path']).name!=f'{sid}-{k}.npy':raise ValueError('Stage array membership')
    if not np.allclose(arrays['decoded']-arrays['reference'],arrays['residual'],rtol=0,atol=7e-8):raise ValueError('Decoder residual differs')
    marked,cap=analyzer.cap(source,arrays['residual']);analyzer.equal(ce['cap'],cap,'cap')
    rho=float(np.sqrt(np.mean(arrays['residual']**2)));beta=min(1.,component.EPSILON/rho) if rho else 1.
    analyzer.equal(ce['residual_rms'],rho,'rho',tol=1e-6);analyzer.equal(ce['beta_final'],beta,'beta',tol=1e-6)
    target=np.clip(source.astype(np.float64)/255+beta*arrays['residual'],0,1)
    if not np.allclose(target,arrays['surrogate'],rtol=0,atol=2e-7):raise ValueError('Differentiable cap stage mismatch')
    analyzer.equal(ce['surrogate_vs_capped_rmse'],float(np.sqrt(np.mean((arrays['surrogate']-marked/255.)**2))),'cap rounding')
    for field,key in (('pure_reference_quality','reference'),('pure_final_quality','decoded')):
        analyzer.pixel_quality(ce[field],source,np.rint(255*np.clip(arrays[key],0,1)).astype(np.uint8))
    for key in ('final_surrogate_scores','final_surrogate_cycle_scores'):
        if len(ce[key])!=2 or not all(analyzer.finite(v) for v in ce[key]):raise ValueError('Surrogate oracle missing')
    profile=codec.validate_profile(codec.load_profile(ROOT/cfg['profile']))
    verified=[analyzer.verify_row(audit,row,ce,source,marked,profile) for row in record['conditions']]
    gate=source_gate(record['conditions'],sid)
    if gate!=record.get('gate') or not gate['complete']:raise ValueError('Source gate differs/incomplete')
    return dict(source_run=receipt,source_id=sid,method_core_sha256=record['method_core_sha256'],
        gate=gate,verified_conditions=verified,stage_scope='Original independent cap and verify_row; CLIP/LPIPS inference recorded-only')


def merge_pilot(source_dirs,output):
    if len(source_dirs)!=2:raise ValueError('Exactly two independently audited source runs required')
    output=Path(output).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Development output required')
    audits=[audit_source_run(p) for p in source_dirs]
    if [v['source_id'] for v in audits]!=list(PILOT_IDS):raise ValueError('Original ordered two-source pilot required')
    if len({v['method_core_sha256'] for v in audits})!=1:raise ValueError('Mixed candidate core')
    rows=[r for p in source_dirs for r in read(Path(p)/'run.json')['conditions']]
    result=dict(schema='m1-terminal-e2e-pilot-merge-v1',data_split='development',
        method_core_sha256=audits[0]['method_core_sha256'],source_runs=[v['source_run'] for v in audits],
        source_audits=audits,gate=two_source_gate(rows),outcome='completed',command=sys.argv,
        scientific_status='exploratory development gate; no M1 or held-out authorization')
    output.mkdir(parents=True,exist_ok=False);util.write(output/'run.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write-manifest',type=Path);g.add_argument('--run',action='store_true');g.add_argument('--merge-pilot',nargs=2,type=Path)
    p.add_argument('--manifest',type=Path);p.add_argument('--output-dir',type=Path);p.add_argument('--source-id',type=int)
    p.add_argument('--bridge-dir',type=Path);p.add_argument('--component-analysis',type=Path)
    p.add_argument('--resume-from',type=Path);p.add_argument('--expansion-receipt',type=Path)
    p.add_argument('--owner-extension-receipt',type=Path)
    a=p.parse_args()
    if a.write_manifest:
        with a.write_manifest.open('x',encoding='utf-8') as f:json.dump(configuration(),f,indent=2);f.write('\n')
        return 0
    if a.merge_pilot:
        if a.output_dir is None:p.error('merge requires output-dir')
        return 0 if merge_pilot(a.merge_pilot,a.output_dir)['gate']['passes'] else 2
    if any(getattr(a,k) is None for k in ('manifest','output_dir','source_id','bridge_dir','component_analysis')):
        p.error('run requires manifest/output-dir/source-id/bridge-dir/component-analysis')
    return run(a.manifest,a.output_dir,a.source_id,a.bridge_dir,a.component_analysis,a.resume_from,a.expansion_receipt,a.owner_extension_receipt)

if __name__=='__main__':raise SystemExit(main())

