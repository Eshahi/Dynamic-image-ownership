"""Conditional development489 A-C assessment; model-free on import.

Generation and readout are separate phases. Every owned partition is bounded;
continuation uses a fresh directory and immutable condition-level image aliases.
"""
from __future__ import annotations
import argparse, gc, hashlib, importlib.metadata, json, math, os, subprocess, sys, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_terminal_e2e as candidate
import m1_assess_dual_threats as original
import three_threat_protocol as protocol
import v5_study_protocol as graph
core,util=candidate.core,candidate.util
MAIN=candidate.MAIN
VERSION='m1-terminal-e2e-threats-v1'
ATTACK_VERSION='ac-native-projection-v1'
LABEL_SHA='89dd92ebbd1c0807880178146ae1ff7dd5b1dfb682229f45a7524656b6f7ceae'
TUPLES=('DD','DR','RD','RR')
GROUPS=tuple(tuple(candidate.IDS[n:n+2]) for n in range(0,12,2))
PARTITIONS=tuple(f'shard-{n}' for n in range(6))+('transfers',)
read=candidate.read

def schedule():
    if util.sha(original.LABELS)!=LABEL_SHA:raise ValueError('Frozen development label bytes changed')
    rows=original.planned(read(original.LABELS)['pairs'])
    return dict(schema=VERSION,data_split='development',candidate=candidate.VERSION,
        attack_version=ATTACK_VERSION,owners=list(core.OWNERS),threshold=4.,
        source_ids=list(candidate.IDS),labels_sha256=LABEL_SHA,conditions=rows,
        partitions={p:[r['id'] for r in rows if (r['axis'] in ('clean','T3') and r['source_id'] in GROUPS[n])]
            for n,p in enumerate(PARTITIONS[:6])} | {'transfers':[r['id'] for r in rows if r['axis'] not in ('clean','T3')]},
        attack_settings=dict(strengths=list(graph.STRENGTHS),seeds=list(graph.SEEDS),steps=20,
            guidance_scale=1.,prompt='',negative_prompt='',eta=0.,
            diffusion_posterior='unchanged pinned img2img pipeline sampling/noising',vae='posterior-mode',
            projection_dtype='float64 then pinned fp16 decoder',projection_conversion='CPU float64 division by 0.18215, then one NumPy FP16 cast; direct FP16 decode',
            projection_precision_version='ac-native-projection-precision-v1',projection_cap_db=35.2,bisection_steps=36,
            adaptive_detector_decision_queries=0),
        budgets=dict(run_seconds_cap=1800,gpu_budget_bytes=10*1024**3,gpu_reserve_bytes=512*1024**2,
            ram_budget_bytes=16*1024**3,artifact_budget_bytes=500*1024**2),
        planned_counts=dict(conditions=489,images=423,primary_queries=1692,negative_slots=1437,
            source_oracles=336,transfer_tuples=348,anchor_tuples=216,cross_templates=264,
            diagnostic_queries=1164,primary_plus_diagnostic=2856,pair_geometry=528,transfer_geometry=348))

def directed_pairs(rows=None):
    rows=rows or schedule()['conditions']
    return sorted({(r['donor_id'],r['recipient_id']) for r in rows if r['axis'] in ('T4','T5-transfer')})

def diagnostic_inventory(rows=None):
    rows=rows or schedule()['conditions'];out=[]
    for r in rows:
        if r['axis'] in ('clean','T3'):out.append(dict(id=r['id']+'-source-oracle',kind='source-oracle',condition=r['id']))
        elif r['axis'] in ('T4','T5-transfer'):
            out.extend(dict(id=r['id']+'-'+t,kind='transfer-tuple',condition=r['id'],descriptor_tuple=t) for t in TUPLES)
        else:
            out.extend(dict(id=r['id']+f'-{c}-{direction}',kind='cross-template',condition=r['id'],control=c,direction=direction)
                for c in ('C0','C1') for direction in ('left-under-right','right-under-left'))
    for donor,recipient in directed_pairs(rows):
        out.extend(dict(id=f'anchor-{donor}-{recipient}-{anchor}-{t}',kind='anchor-tuple',donor_id=donor,recipient_id=recipient,
            anchor=anchor,descriptor_tuple=t) for anchor in ('donor-C1','recipient-C0') for t in TUPLES)
    return out

def dependencies():
    extra=[Path(__file__),ROOT/'scripts/m1_analyze_terminal_e2e_threats.py',ROOT/'research/m1-terminal-e2e-threat-schedule.json',
        ROOT/'scripts/m1_assess_dual_threats.py',ROOT/'scripts/v5_study_protocol.py',ROOT/'scripts/three_threat_protocol.py',
        ROOT/'research/m1-terminal-continuous-expansion-design.md',original.LABELS]
    extra.append(ROOT/'research/m1-native-projection-precision.md')
    return list(dict.fromkeys(candidate.dependency_paths()+extra))

def receipt(path):
    path=Path(path).resolve();return dict(path=str(path),sha256=util.sha(path))

def checked(r):
    path=Path(r['path']).resolve()
    if not path.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()) or util.sha(path)!=r['sha256']:
        raise ValueError('Immutable MAIN development receipt changed')
    return path

def freeze(source_dirs,pilot_receipt,destination):
    """CPU integrity admission; expanded clean failures remain eligible inputs."""
    if len(source_dirs)!=12:raise ValueError('All twelve source lineages required')
    audits=[];cases=[]
    for sid,entry in zip(candidate.IDS,source_dirs):
        if isinstance(entry,dict):
            if entry.get('id')!=sid or entry.get('status')!='missing' or not entry.get('reason') or not entry.get('source_run'):
                raise ValueError('Missing source needs fixed ID, explicit reason and terminal attempt receipt')
            attempt=read(checked(entry['source_run']))
            if attempt.get('data_split')!='development' or attempt.get('outcome') not in ('failed','interrupted','incomplete','operational_failed'):
                raise ValueError('Missing source must reference a retained terminal development attempt')
            actual=attempt.get('source_id',attempt.get('source',{}).get('id'))
            if actual!=sid:raise ValueError('Missing lineage source ID differs')
            if sid in candidate.PILOT_IDS:raise ValueError('Original pilot cannot be missing')
            cases.append(dict(entry));continue
        audit=candidate.audit_source_run(entry);audits.append(audit)
        run=read(Path(entry)/'run.json');ce=run['case_events'][0]
        if audit['source_id']!=sid:raise ValueError('Fixed source partition order required')
        cases.append(dict(id=sid,status='available',source_run=audit['source_run'],source=ce['source'],
            rows=run['conditions'],clean_gate=audit['gate'],initialization=ce['initialization']))
    if len({r['method_core_sha256'] for r in audits})!=1:
        raise ValueError('Fixed ordered twelve sources with one identical candidate core required')
    method=audits[0]['method_core_sha256'];pilot=candidate.require_expansion(pilot_receipt,method)
    cfg=schedule();value=dict(schema=VERSION,data_split='development',schedule=cfg,pilot=pilot,
        method_core_sha256=method,cases=cases,dependencies={p.relative_to(ROOT).as_posix():util.sha(p) for p in dependencies()},
        primary_reader_side_information=['suspect RGB8','public candidate OwnerID','pinned public models/profile/maps'],
        scientific_status='conditional exploratory development; no held-out authorization',human_visual_verdict=None)
    value['assessment_core_sha256']=candidate.component.canonical_sha(dict(dependencies={k:v for k,v in value['dependencies'].items()
        if not k.endswith('.md')},schedule=cfg,method_core_sha256=method))
    destination=Path(destination)
    if destination.exists():raise ValueError('Refuse manifest replacement')
    validate(value);util.write(destination,value)
    return value

def validate(manifest,reaudit=True):
    if manifest.get('schema')!=VERSION or manifest.get('data_split')!='development' or manifest.get('schedule')!=schedule():
        raise ValueError('Exact development assessment schedule required')
    expected={p.relative_to(ROOT).as_posix() for p in dependencies()}
    if set(manifest.get('dependencies',{}))!=expected:raise ValueError('Exact dependency inventory required')
    for rel,h in manifest['dependencies'].items():
        if util.sha(ROOT/rel)!=h:raise ValueError('Assessment dependency changed: '+rel)
    digest=candidate.component.canonical_sha(dict(dependencies={k:v for k,v in manifest['dependencies'].items() if not k.endswith('.md')},
        schedule=manifest['schedule'],method_core_sha256=manifest['method_core_sha256']))
    if digest!=manifest.get('assessment_core_sha256'):raise ValueError('Assessment scientific identity changed')
    cases=manifest.get('cases',[])
    if [c.get('id') for c in cases]!=list(candidate.IDS):raise ValueError('Fixed twelve source receipts required')
    candidate.require_expansion(checked(manifest['pilot']),manifest['method_core_sha256'])
    for case in cases:
        path=checked(case['source_run']);run=read(path)
        if case.get('status')=='missing':
            if case['id'] in candidate.PILOT_IDS or not case.get('reason') or run.get('outcome') not in ('failed','interrupted','incomplete','operational_failed'):
                raise ValueError('Missing source terminal provenance differs')
            if run.get('source_id',run.get('source',{}).get('id'))!=case['id']:raise ValueError('Missing source membership differs')
            continue
        if case.get('status')!='available':raise ValueError('Source status required')
        if run.get('method_core_sha256')!=manifest['method_core_sha256'] or run.get('source_id')!=case['id'] or run.get('outcome')!='completed':
            raise ValueError('Source scientific identity differs')
        if case['rows']!=run['conditions'] or case['source']!=run['case_events'][0]['source']:raise ValueError('Frozen endpoint receipt differs')
        if reaudit:candidate.audit_source_run(path.parent)
        for row in case['rows']:
            for key in ('image','terminal_reader_latent','terminal_fp32_latent'):checked(row[key])
    return manifest['schedule']['conditions']

def projection_displacement(z_donor,z_recipient,E,H,owner=None):
    """Frozen one-shot minimum-norm transplant in scaled C-order float64 units."""
    import numpy as np
    owner=owner or core.OWNERS[0];donor=np.asarray(z_donor,np.float64);recipient=np.asarray(z_recipient,np.float64)
    if donor.shape!=(core.N,) or recipient.shape!=(core.N,) or not np.isfinite(donor).all() or not np.isfinite(recipient).all():
        raise ValueError('Finite scaled flat latent pair required')
    template=core.template(E,H,owner);w={}
    for j in ('s','i'):
        w[j]=np.zeros(core.N,np.float64);w[j][template['coords_'+j]]=template['r_'+j]*template['v_'+j]
    if not all(abs(float(w[j]@w[j])-1)<1e-12 for j in w) or abs(float(w['s']@w['i']))>1e-12:raise ValueError('Projection orthogonality failed')
    a={j:float((donor-recipient)@w[j]) for j in w}
    target=recipient+a['s']*w['s']+a['i']*w['i']
    errors={j:float(target@w[j])-float(donor@w[j]) for j in w}
    if any(abs(v)>1e-10 for v in errors.values()):raise ValueError('Projection matching failed')
    return target,dict(version=ATTACK_VERSION,coefficients=a,projection_residuals=errors,
        displacement_l2=float(np.linalg.norm(target-recipient)),minimum_norm_squared=a['s']**2+a['i']**2,
        latent_units='scaled VAE posterior mode times .18215',adaptive_detector_decision_queries=0)

def tuple_scores(z,donor,recipient):
    out={t:core.scores(z,donor['E'] if t[0]=='D' else recipient['E'],donor['H'] if t[1]=='D' else recipient['H'],core.OWNERS[0]) for t in TUPLES}
    for a,b in (('DD','DR'),('RD','RR')):
        if not math.isclose(out[a]['s'],out[b]['s'],rel_tol=0,abs_tol=1e-12):raise ValueError('H-independent semantic parity failed')
    return out

def decoder_input(z,scale=.18215):
    """Frozen CPU division and one half cast; model-free conversion receipt."""
    import numpy as np
    z=np.asarray(z,np.float64)
    if scale!=.18215 or z.shape!=(core.N,) or not np.isfinite(z).all():raise ValueError('Decoder input units/shape/scale')
    u64=np.divide(z,np.float64(scale))
    with np.errstate(over='ignore',invalid='ignore'):u16=u64.astype(np.float16)
    if not np.isfinite(u16).all():raise ValueError('Decoder FP16 overflow')
    represented=np.float64(scale)*u16.astype(np.float64)
    def errors(delta,reference):
        l2=float(np.linalg.norm(delta));den=float(np.linalg.norm(reference))
        return dict(l2=l2,rms=float(np.sqrt(np.mean(delta**2))),max_abs=float(np.max(np.abs(delta))),relative_l2=l2/den if den else None)
    info=dict(version='ac-native-projection-precision-v1',shape=[1,4,64,64],dtype='float16',order='C',
        fp16_bytes_sha256=hashlib.sha256(u16.astype('<f2').tobytes()).hexdigest(),
        unscaled_error=errors(u16.astype(np.float64)-u64,u64),scaled_error=errors(represented-z,z))
    return u64,u16,represented,info

def postcast_residuals(target,recipient,donor,E,H,coefficients):
    import numpy as np
    p=core.template(E,H,core.OWNERS[0]);out={}
    for j in ('s','i'):
        w=np.zeros(core.N,np.float64);w[p['coords_'+j]]=p['r_'+j]*p['v_'+j]
        out[j]=dict(absolute=float(target@w)-float(donor@w),displacement=float((target-recipient)@w)-coefficients[j])
    return out

def precision_receipt(projection):
    arrays=projection['arrays'];inputs={}
    for label,name,zkey in (('projected','target','target_z'),('reference','baseline','recipient_observed_z')):
        value=projection['decoder_conversion'][name]
        inputs[label]=dict(scaled_latent=arrays[zkey],unscaled_float64=arrays[name+'_u64'],
            decoder_input_float16=arrays[name+'_u16'],unscaled_conversion_error=value['unscaled_error'],scaled_conversion_error=value['scaled_error'])
    return dict(version='ac-native-projection-precision-v1',operation='cpu_float64_divide_then_float16',
        scale_float64=.18215,decoder_shape=[1,4,64,64],inputs=inputs,
        projection_residuals={j:dict(precast=projection['projection_residuals'][j],
            postcast_absolute=projection['postcast_projection_residuals'][j]['absolute'],
            postcast_displacement=projection['postcast_projection_residuals'][j]['displacement']) for j in ('s','i')})

def transfer_witness(donor_blind,output_tuples,background_tuples,quality,donor_tuples):
    from m1_analyze_terminal_continuous import quality_pass
    valid=lambda d:d.get('state')!='invalid_measurement' and all(type(d.get(k)) in (int,float) and math.isfinite(d[k]) for k in ('s','i'))
    inputs_valid=all(valid(d) for d in (donor_blind,output_tuples['DD'],background_tuples['DD'],donor_tuples['RR']))
    admissible=quality_pass(quality) is True
    def channel(flag):
        return inputs_valid and admissible and donor_blind['flags'][flag] and output_tuples['DD']['flags'][flag] and not background_tuples['DD']['flags'][flag]
    return dict(inputs_valid=inputs_valid,recipient_quality_admissible=admissible,
        strict_dual_delivery=inputs_valid and admissible and donor_blind['state']=='both_match' and output_tuples['DD']['state']=='both_match' and background_tuples['DD']['state']!='both_match',
        semantic_delivery=channel('s'),instance_delivery=channel('i'),
        continuous_semantic_challenge=inputs_valid and donor_blind['state']=='both_match' and donor_tuples['RR']['s']>=4.,
        evaluator_side_information='fixed donor C1 / recipient C0 descriptors; no causal or authentication claim')

def enrollment_anchors(manifest):
    import numpy as np
    anchors={}
    for case in manifest['cases']:
        if case['status']!='available':continue
        for row in case['rows']:
            if row['dose']!='clean':continue
            z=np.load(checked(row['terminal_reader_latent']),allow_pickle=False)
            anchors[case['id'],row['control']]=dict(E=row['suspect_E'],H=row['suspect_H'],z=z,image=row['image'],
                blind=row['owner_decisions'],source=case['source'])
    return anchors

def component_pair(spec,anchors):
    import numpy as np
    values={}
    for control in ('C0','C1'):
        left,right=anchors[spec['left'],control],anchors[spec['right'],control]
        values[control]=dict(clip_cosine=float(np.asarray(left['E'])@np.asarray(right['E'])),
            hash_hamming=int((left['H']^right['H']).bit_count()),
            cross_template={'left-under-right':core.scores(left['z'],right['E'],right['H'],core.OWNERS[0]),
                'right-under-left':core.scores(right['z'],left['E'],left['H'],core.OWNERS[0])},
            self_scores={'left':left['blind'][core.OWNERS[0]],'right':right['blind'][core.OWNERS[0]]},
            geometry={owner:core.projection_diagnostic(left['E'],left['H'],right['E'],right['H'],owner) for owner in core.OWNERS})
    return dict(**spec,outcome='completed',components=values,human_visual_verdict=None,
        semantic_label_source='immutable exploratory agent labels; no human verdict')

def anchor_controls(anchors):
    rows=[]
    for donor,recipient in directed_pairs():
        if (donor,'C1') not in anchors or (recipient,'C0') not in anchors:
            rows.append(dict(donor_id=donor,recipient_id=recipient,outcome='missing_enrollment'));continue
        d,r=anchors[donor,'C1'],anchors[recipient,'C0']
        rows.append(dict(donor_id=donor,recipient_id=recipient,outcome='completed',
            donor_C1=tuple_scores(d['z'],d,r),recipient_C0=tuple_scores(r['z'],d,r)))
    return rows

class ReadoutModels:
    """Same pinned PublicReader/operator; additional IO for fixed attack decode."""
    def __init__(self,assets,package):
        import numpy as np
        import torch
        from diffusers import AutoencoderKL
        from diffusers.image_processor import VaeImageProcessor
        from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
        from transformers import CLIPImageProcessor
        from a6_clip_visual import load_visual_encoder
        import three_threat_models as models
        self.np,self.torch,self.models=np,torch,models
        self.vae=AutoencoderKL.from_pretrained(assets/'sd15-fp16/vae',variant='fp16',use_safetensors=True,
            local_files_only=True,torch_dtype=torch.float16).eval().requires_grad_(False).to('cuda')
        if float(self.vae.config.scaling_factor)!=.18215:raise ValueError('Unexpected VAE scaling factor')
        self.processor=VaeImageProcessor(vae_scale_factor=8)
        self.safety=StableDiffusionSafetyChecker.from_pretrained(assets/'sd15-fp16/safety_checker',variant='fp16',
            use_safetensors=True,local_files_only=True,torch_dtype=torch.float16).eval().requires_grad_(False).to('cuda')
        self.safety_processor=CLIPImageProcessor.from_pretrained(assets/'sd15-fp16/feature_extractor',local_files_only=True)
        self.clip,self.transform=load_visual_encoder(assets/'clip/ViT-B-32.pt',device='cpu')
        self.metric=models.load_lpips(assets,package)
        self.profile=candidate.codec.validate_profile(candidate.codec.load_profile(ROOT/candidate.configuration()['profile']))
        self.public=candidate.PublicReader(self.vae,self.processor,self.feature,self.profile)
        self.model_calls=dict(reader_vae_encodes=0,reader_clip_encodes=0,projection_vae_decodes=0,safety_calls=0,lpips_calls=0)

    def feature(self,rgb):
        value=self.np.asarray(self.models.clip_feature(self.clip,self.transform,rgb),self.np.float64).reshape(-1)
        norm=self.np.linalg.norm(value)
        if value.shape!=(512,) or not self.np.isfinite(value).all() or norm<=0:raise ValueError('Invalid CLIP feature')
        self.model_calls['reader_clip_encodes']+=1
        return value/norm

    def safety_check(self,rgb):
        from PIL import Image
        torch=self.torch;np=self.np
        with torch.inference_mode():
            inputs=self.safety_processor([Image.fromarray(rgb)],return_tensors='pt').pixel_values.to('cuda',dtype=torch.float16)
            _,flags=self.safety(images=rgb[None].astype(np.float32)/255,clip_input=inputs)
        self.model_calls['safety_calls']+=1
        if flags!=[False]:raise RuntimeError('Safety checker blocked output')

    def observe(self,rgb):
        tick=time.monotonic()
        uncached=hashlib.sha256(rgb.tobytes()).hexdigest()!=self.public.cache_key
        decisions={owner:candidate.detect(rgb,owner,self.public) for owner in core.OWNERS}
        E,H,z=self.public.observations(rgb)
        self.model_calls['reader_vae_encodes']+=int(uncached)
        return dict(E=E.tolist(),H=H,z=z,blind=decisions,extract_seconds=time.monotonic()-tick)

    def quality(self,left,right):
        from m1_latent_reconstruction import quality
        from m1_analyze_terminal_continuous import quality_pass
        value=quality(left,right);value['lpips']=self.models.lpips_score(self.metric,left,right)
        self.model_calls['lpips_calls']+=1;value['quality_admissible']=quality_pass(value) is True
        return value

    def project(self,donor,recipient,donor_rgb,recipient_rgb):
        # Supplied-image public observations, never enrollment embedding latents.
        def analytic(rgb):
            uncached=hashlib.sha256(rgb.tobytes()).hexdigest()!=self.public.cache_key
            E,H,z=self.public.observations(rgb);self.model_calls['reader_vae_encodes']+=int(uncached)
            return dict(E=E.tolist(),H=H,z=z)
        d=analytic(donor_rgb);r=analytic(recipient_rgb)
        target,info=projection_displacement(d['z'],r['z'],d['E'],d['H'])
        torch,np=self.torch,self.np
        with torch.inference_mode():
            def decode(z):
                u64,u16,represented,conversion=decoder_input(z)
                u=torch.from_numpy(u16.reshape(1,4,64,64).copy()).to('cuda')
                out=((self.vae.decode(u,return_dict=False)[0]+1)/2).clamp(0,1)
                return out.float().cpu().numpy()[0].transpose(1,2,0).astype(np.float64),(u64,u16,represented,conversion)
            changed,target_input=decode(target);baseline,baseline_input=decode(r['z'])
        self.model_calls['projection_vae_decodes']+=2
        quantized=target_input[2]
        error=quantized-target
        info.update(fp16_scaled_roundtrip_rms=float(np.sqrt(np.mean(error**2))),fp16_scaled_roundtrip_max=float(np.max(np.abs(error))),
            decoder='pinned frozen fp16 SD1.5 VAE; each output clipped before residual',
            projection_inputs='donor supplied C1 (C0 for sham), recipient C0; public feature/mode observations only',
            donor_descriptor=dict(E=d['E'],H=d['H']),donor_observed_z=d['z'],recipient_observed_z=r['z'],target_z=target)
        residual=changed-baseline;rgb,cap=candidate.residual.cap(recipient_rgb,residual)
        info['cap']=cap;info['float_arrays']={'residual':residual,
            'target_u64':target_input[0],'target_u16':target_input[1],
            'baseline_u64':baseline_input[0],'baseline_u16':baseline_input[1]}
        info['decoder_conversion']={'target':target_input[3],'baseline':baseline_input[3]}
        info['postcast_projection_residuals']=postcast_residuals(target_input[2],baseline_input[2],d['z'],d['E'],d['H'],info['coefficients'])
        info['decoder_stage_hashes']={k:hashlib.sha256(v.astype('<f8').tobytes()).hexdigest() for k,v in
            (('target_decode',changed),('baseline_decode',baseline))}
        return rgb,info

def assessment_identity(manifest,manifest_sha,partition):
    return dict(schema=VERSION,assessment_core_sha256=manifest['assessment_core_sha256'],
        method_core_sha256=manifest['method_core_sha256'],manifest_sha256=manifest_sha,partition=partition,
        condition_ids=manifest['schedule']['partitions'][partition])

def resume_rows(prior_directory,identity):
    path=Path(prior_directory).resolve();old=read(checked(receipt(path/'run.json')))
    if old.get('identity')!=identity or old.get('outcome')=='completed' or old.get('resume_input'):
        raise ValueError('Only one continuation of identical incomplete assessment partition permitted')
    rows=read(checked(old['conditions_receipt']))
    for row in rows:
        if row.get('id') not in identity['condition_ids']:raise ValueError('Unrelated prior row')
        if row.get('image'):checked(row['image'])
        if row.get('reader_latent'):checked(row['reader_latent'])
        for r in row.get('projection',{}).get('arrays',{}).values():checked(r)
        if row.get('outcome')=='execution_failed':
            row['prior_execution_failure']=dict(error=row.get('error'),outcome=row['outcome'],run_json=str(path/'run.json'))
            row['outcome']='attack_persisted' if row.get('image') else 'planned'
    if len(rows)!=len(identity['condition_ids']) or len({r['id'] for r in rows})!=len(rows):raise ValueError('Prior partition inventory incomplete/duplicated')
    return old,rows,receipt(path/'run.json')

def assess(manifest_path,partition,output,resume_from=None):
    import numpy as np
    from PIL import Image
    manifest_path=Path(manifest_path).resolve();manifest=read(manifest_path);specs=validate(manifest)
    if partition not in PARTITIONS:raise ValueError('Fixed partition required')
    output=Path(output).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN development output required')
    # Pin both code and prepared input manifest before any scientific execution.
    pins=util.require_committed(dependencies()+[manifest_path])
    identity=assessment_identity(manifest,util.sha(manifest_path),partition)
    selected=[r for r in specs if r['id'] in identity['condition_ids']]
    prior=None;previous_duration=0.;previous_artifact_bytes=0;rows={r['id']:dict(**r,outcome='planned',human_visual_verdict=None) for r in selected}
    if resume_from:
        prior,previous,resume_receipt=resume_rows(resume_from,identity)
        previous_duration=prior['duration_seconds'];rows={r['id']:r for r in previous}
        previous_artifact_bytes=sum(p.stat().st_size for p in Path(resume_from).rglob('*') if p.is_file())
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic();budget=manifest['schedule']['budgets']
    record=dict(schema=VERSION,data_split='development',identity=identity,command=sys.argv,partition=partition,
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),committed_files=pins,
        manifest=receipt(manifest_path),source_runs=[c['source_run'] for c in manifest['cases']],
        outcome='started',duration_seconds=previous_duration,process_id=os.getpid(),case_namespace=candidate.VERSION,
        primary_planned_queries=sum(r['axis']!='T5' for r in selected)*4,human_visual_verdict=None)
    if prior:record.update(resume_input=resume_receipt,previous_artifact_bytes=previous_artifact_bytes)
    def persist():
        record['duration_seconds']=previous_duration+time.monotonic()-started
        util.write(output/'conditions.json',list(rows.values()));record['conditions_receipt']=receipt(output/'conditions.json')
        util.write(output/'run.json',record)
    def event(value):original.append_jsonl(output/'journal.jsonl',dict(elapsed_seconds=time.monotonic()-started,**value))
    def retain(row):rows[row['id']]=row;event(dict(kind='condition',**row));persist()
    def check():
        ram=util.working_set_bytes();record['peak_rss_bytes']=max(record.get('peak_rss_bytes',0),ram)
        if previous_duration+time.monotonic()-started>budget['run_seconds_cap'] or ram>budget['ram_budget_bytes']:
            raise RuntimeError('Cumulative partition time/RAM cap')
        record['artifact_bytes']=previous_artifact_bytes+sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
        if record['artifact_bytes']>budget['artifact_budget_bytes']:raise RuntimeError('Cumulative partition disk cap')
        if 'torch' in sys.modules:
            torch=sys.modules['torch']
            if torch.cuda.is_initialized() and torch.cuda.memory_allocated()>record['gpu_budget']['effective_allocation_bytes']:raise RuntimeError('GPU cap')
    def save_array(name,value):
        path=output/(name+'.npy')
        with path.open('xb') as f:np.save(f,np.asarray(value,np.float16 if name.endswith('_u16') else np.float64),allow_pickle=False)
        return receipt(path)
    def save_png(row,rgb):
        path=output/(row['id']+'.png')
        with path.open('xb') as f:Image.fromarray(np.asarray(rgb,np.uint8)).save(f,format='PNG')
        row.update(image=dict(**receipt(path),rgb8_sha256=hashlib.sha256(rgb.tobytes()).hexdigest()),outcome='attack_persisted')
        retain(row);check()
    persist()
    models_live=None
    try:
        import three_threat_models as models
        models.block_network()
        import torch
        record['deterministic_execution']=candidate.repeatability.configure()
        if not torch.cuda.is_available():raise RuntimeError('CUDA required')
        free,total=torch.cuda.mem_get_info(0)
        record['gpu_budget']=candidate.gpu_allocation_budget(budget['gpu_budget_bytes'],int(free),int(total),budget['gpu_reserve_bytes'])
        torch.cuda.set_per_process_memory_fraction(record['gpu_budget']['allocator_fraction'])
        record['assets'],package=models.verify_assets(util.ASSETS,ROOT/'research/a6-candidate-model-assets.json')
        record['lpips_learned_sha256']=util.sha(package/'weights/v0.1/alex.pth')
        record['environment']=dict(python=sys.version,**{p:importlib.metadata.version(p) for p in ('torch','numpy','scipy','Pillow','diffusers','transformers','lpips')})
        record['device_identity']=dict(name=torch.cuda.get_device_name(0),capability=list(torch.cuda.get_device_capability(0)),cuda=torch.version.cuda,cudnn=torch.backends.cudnn.version())
        record['driver_inventory']=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,driver_version,pci.bus_id','--format=csv,noheader'],text=True).strip()
        record['runtime']=dict(threads=torch.get_num_threads(),fill_uninitialized_memory=bool(torch.utils.deterministic.fill_uninitialized_memory))
        anchors=enrollment_anchors(manifest);images={(sid,c):original.read_rgb(a['image']['path']) for (sid,c),a in anchors.items()}
        source_cases={c['id']:c for c in manifest['cases']};check();persist()
        for spec in selected:
            needed=[spec[k] for k in ('source_id','donor_id','recipient_id','left','right') if k in spec]
            missing=[sid for sid in needed if source_cases[sid]['status']=='missing']
            if missing:
                rows[spec['id']].update(outcome='missing_enrollment',missing_ids=missing,
                    missing_lineages=[source_cases[sid] for sid in missing]);retain(rows[spec['id']])
        # Clean/VAE aliases already passed exact candidate/operator/receipt audit.
        for spec in selected:
            if spec['axis'] not in ('clean','T3') or spec.get('dose')=='diffusion':continue
            row=rows[spec['id']]
            if row.get('outcome') in ('completed','safety_blocked','missing_enrollment'):continue
            dose='clean' if spec['axis']=='clean' else 'vae_cycle'
            old=next(r for r in source_cases[spec['source_id']]['rows'] if r['control']==spec['control'] and r['dose']==dose)
            source=anchors[spec['source_id'],'C0']
            z=np.load(checked(old['terminal_reader_latent']),allow_pickle=False)
            row.update(outcome='completed',image=old['image'],reader_latent=old['terminal_reader_latent'],suspect_E=old['suspect_E'],suspect_H=old['suspect_H'],
                owner_decisions=old['owner_decisions'],extract_seconds=old['extract_seconds'],attack_seconds=0.,
                quality_vs_source=old['quality_vs_source'],quality_vs_same_arm_original=old['quality_vs_same_arm_clean'],
                source_template_oracle=core.scores(z,source['E'],source['H'],core.OWNERS[0]),
                reader_reuse=dict(source_run=source_cases[spec['source_id']]['source_run'],condition_sha256=candidate.component.canonical_sha(old),
                    scientific_operator='exact frozen e2e clean/VAE readout',new_model_calls=0))
            row.update(source_clip_cosine=float(np.asarray(source['E'])@np.asarray(old['suspect_E'])),
                source_phash_distance=int((source['H']^old['suspect_H']).bit_count()))
            retain(row);check()
        pending=[r for r in selected if r['axis']=='T3' and r.get('dose')=='diffusion'
            and rows[r['id']].get('outcome') not in ('completed','safety_blocked','attack_persisted','missing_enrollment')]
        if pending:
            event(dict(kind='phase',phase='diffusion-generation',planned=len(pending)))
            pipeline=models.load_regenerator(util.ASSETS);record['ddim_config']=models.DDIM_CONFIG
            nfe=[0];timesteps=[]
            def note_forward(module,args,out):
                nfe[0]+=1;timesteps.append(float(args[1].detach().cpu().item()) if torch.is_tensor(args[1]) else float(args[1]))
            hook=pipeline.unet.register_forward_hook(note_forward)
            for spec in pending:
                check();row=rows[spec['id']];row.update(outcome='started');retain(row);tick=time.monotonic();calls=nfe[0]
                try:
                    with torch.inference_mode():
                        result=pipeline(prompt='',negative_prompt='',image=Image.fromarray(images[spec['source_id'],spec['control']]),
                            strength=spec['strength'],num_inference_steps=20,eta=0.,guidance_scale=1.,
                            generator=torch.Generator(device='cuda').manual_seed(spec['seed']),num_images_per_prompt=1,output_type='pil',return_dict=True)
                        attacked=np.asarray(models.validate_generated(result)).copy()
                    torch.cuda.synchronize();row.update(attack_seconds=time.monotonic()-tick,nfe_unet=nfe[0]-calls,
                        actual_ddim_timesteps=timesteps[calls:],scheduler_timesteps=[float(t) for t in pipeline.scheduler.timesteps.cpu().tolist()],
                        attack_operator='original pinned SD1.5 DDIM img2img')
                    save_png(row,attacked)
                except Exception as error:
                    row.update(outcome='safety_blocked' if 'safety' in str(error).lower() or 'nsfw' in str(error).lower() else 'execution_failed',
                        error=repr(error),traceback=traceback.format_exc(),attack_seconds=time.monotonic()-tick,nfe_unet=nfe[0]-calls,
                        actual_ddim_timesteps=timesteps[calls:]);retain(row)
            hook.remove();del pipeline;gc.collect();torch.cuda.empty_cache();check()
        pending_images=[r for r in selected if r['axis']!='T5' and rows[r['id']].get('outcome') not in ('completed','safety_blocked','execution_failed','missing_enrollment')]
        if pending_images:models_live=ReadoutModels(util.ASSETS,package);check()
        controls=anchor_controls(anchors) if partition=='transfers' else []
        if controls:util.write(output/'anchor-controls.json',controls);record['anchor_controls']=receipt(output/'anchor-controls.json')
        anchor_lookup={(v['donor_id'],v['recipient_id']):v for v in controls}
        for spec in selected:
            check();row=rows[spec['id']]
            if row.get('outcome') in ('completed','safety_blocked','execution_failed','missing_enrollment'):continue
            if spec['axis']=='T5':retain(component_pair(spec,anchors));continue
            try:
                if row.get('outcome')!='attack_persisted':
                    donor,recipient=spec['donor_id'],spec['recipient_id'];tick=time.monotonic()
                    if spec['arm']=='clean_donor_residual':
                        rgb=np.asarray(protocol.residual_transfer(images[recipient,'C0'].tolist(),images[donor,'C1'].tolist(),images[donor,'C0'].tolist(),spec['scale']),np.uint8)
                        row['attack_operator']='unchanged original residual_transfer RGB8 byte units'
                    else:
                        sham=spec['arm']=='unmarked_projection_sham'
                        rgb,projection=models_live.project(anchors[donor,'C0' if sham else 'C1'],anchors[recipient,'C0'],
                            images[donor,'C0' if sham else 'C1'],images[recipient,'C0'])
                        row['projection']={k:v for k,v in projection.items() if k not in ('float_arrays','donor_observed_z','recipient_observed_z','target_z')}
                        row['projection']['arrays']={k:save_array(spec['id']+'-projection-'+k,v) for k,v in
                            {**projection['float_arrays'],**{k:projection[k] for k in ('donor_observed_z','recipient_observed_z','target_z')}}.items()}
                        row['projection']['projection_precision']=precision_receipt(row['projection'])
                        row['attack_operator']=ATTACK_VERSION
                    models_live.safety_check(rgb);row.update(attack_seconds=time.monotonic()-tick,nfe_unet=0);save_png(row,rgb)
                rgb=original.read_rgb(checked(row['image']));obs=models_live.observe(rgb)
                row.update(suspect_E=obs['E'],suspect_H=obs['H'],owner_decisions=obs['blind'],extract_seconds=obs['extract_seconds'],
                    reader_latent=save_array(spec['id']+'-reader-z',obs['z']))
                ref=spec.get('recipient_id',spec.get('source_id'));arm=spec.get('control','C0')
                row.update(quality_vs_source=models_live.quality(images[ref,'C0'],rgb),
                    quality_vs_same_arm_original=models_live.quality(images[ref,arm],rgb),
                    source_clip_cosine=float(np.asarray(anchors[ref,'C0']['E'])@np.asarray(obs['E'])),
                    source_phash_distance=int((anchors[ref,'C0']['H']^obs['H']).bit_count()),adaptive_detector_decision_queries=0)
                if spec['axis'] in ('clean','T3'):
                    a=anchors[ref,'C0'];row['source_template_oracle']=core.scores(obs['z'],a['E'],a['H'],core.OWNERS[0])
                else:
                    d,r=anchors[spec['donor_id'],'C1'],anchors[spec['recipient_id'],'C0'];base=anchor_lookup[spec['donor_id'],spec['recipient_id']]
                    row['tuple_scores']=tuple_scores(obs['z'],d,r)
                    row['donor_geometry']={owner:core.projection_diagnostic(d['E'],d['H'],obs['E'],obs['H'],owner) for owner in core.OWNERS}
                    row['delivery']=transfer_witness(d['blind'][core.OWNERS[0]],row['tuple_scores'],base['recipient_C0'],row['quality_vs_source'],base['donor_C1'])
                row['outcome']='completed';retain(row)
            except Exception as error:
                row.update(outcome='safety_blocked' if 'safety' in str(error).lower() else 'execution_failed',error=repr(error),traceback=traceback.format_exc());retain(row)
        if models_live:record['model_calls']=models_live.model_calls
        record['outcome']='completed' if all(r['outcome'] in ('completed','safety_blocked','missing_enrollment') for r in rows.values()) else 'incomplete'
        record['scientific_complete']=all(r['outcome']=='completed' for r in rows.values())
        record['nfe_unet']=sum(r.get('nfe_unet',0) for r in rows.values())
        record['peak_allocated_bytes']=torch.cuda.max_memory_allocated();check()
    except (Exception,KeyboardInterrupt) as error:
        record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error),traceback=traceback.format_exc())
    finally:
        if models_live:record['model_calls']=models_live.model_calls
        if 'torch' in sys.modules and sys.modules['torch'].cuda.is_initialized():
            record['peak_allocated_bytes']=sys.modules['torch'].cuda.max_memory_allocated()
        record['peak_rss_bytes']=max(record.get('peak_rss_bytes',0),util.working_set_bytes())
        persist();record['output_hashes']={p.name:util.sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'}
        util.write(output/'run.json',record)
    return 0 if record['outcome']=='completed' else 1

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write-schedule',type=Path);g.add_argument('--prepare',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--manifest',type=Path);p.add_argument('--source-dir',action='append',type=Path);p.add_argument('--pilot-receipt',type=Path)
    p.add_argument('--source-inventory',type=Path,help='Ordered twelve-item JSON: available directory string or missing terminal-lineage record')
    p.add_argument('--partition',choices=PARTITIONS);p.add_argument('--output-dir',type=Path);p.add_argument('--resume-from',type=Path)
    a=p.parse_args()
    if a.write_schedule:
        with a.write_schedule.open('x',encoding='utf-8') as f:json.dump(schedule(),f,indent=2);f.write('\n')
        return 0
    if a.prepare:
        if (bool(a.source_dir)==bool(a.source_inventory)) or not a.pilot_receipt or not a.manifest:p.error('prepare requires source-dir XOR source-inventory plus pilot-receipt and manifest')
        freeze(read(a.source_inventory) if a.source_inventory else a.source_dir,a.pilot_receipt,a.manifest);return 0
    if not a.manifest or not a.partition or not a.output_dir:p.error('run requires manifest/partition/output-dir')
    return assess(a.manifest,a.partition,a.output_dir,a.resume_from)

if __name__=='__main__':raise SystemExit(main())

