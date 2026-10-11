"""Versioned S1 scientific extension of the existing M1b worker (no launch surface)."""
from __future__ import annotations
import json
import math
import time
import uuid
import sys
from pathlib import Path

PROTOCOL = 'e3-s1-v1'
METHODS = ('e3-s1', 'v5-r3')
OWNERS = tuple('qim-pilot-owner-' + x for x in ('alpha', 'beta', 'gamma', 'delta'))
MODES = ('combined', 'semantic_only', 'perceptual_only', 'none')
DOSES = tuple(f'ddim-{s}-{seed}' for s in (.1, .2) for seed in (3, 4, 5))
CONDITIONS = ('residual-0.5', 'residual-1.0', 'public', 'public-sham')
FRESH_INDEX = 'research/journal-upgrade-20261009/e3-s1-external-index.json'
FRESH_SCHEDULE = 'research/journal-upgrade-20261009/e3-s1-schedule.json'
FRESH_INDEX_SHA256 = '754e0362791d627dc0af23530993bbee30ecc7d31a8fcb8cb4af439d27415581'
LINUX_FRESH_INDEX = 'research/journal-upgrade-20261009/e3-s1-linux-external-index.json'
LINUX_FRESH_INDEX_SHA256 = '091bad0fae4092ed8332ca64e44873cafcabd88ebfa8636957d5104be7a80a0f'
FRESH_SCHEDULE_SHA256 = 'fada9a67f066f2dc4bde5931d46911eb11bb10cb6e6bebcaa7abf33192cac9d0'
S1_CONFIG_SHA256 = 'f5ad6b66c7b2a6c0a337dd5243c86b832b8e0dc134e7926ac5be80b3dcb2cb2a'
FRESH_INVENTORY = 'research/journal-upgrade-20261009/e3-s1-fresh-cohort.json'


def planned_ids(plan, sources, selected):
    ids = [f"src:{s['uid']}:canon" for s in sources]
    ids.append('t5:selection')
    for s in sources:
        u = s['uid']
        ids.append(f'src:{u}:e3-s1:supplier')
        for m in METHODS:
            ids.append(f'src:{u}:{m}:embed')
            ids.extend(f'src:{u}:{m}:clean:{a}:{o}' for a in ('C0', 'C1') for o in OWNERS)
        for d in DOSES:
            ids.extend(f'atk:{u}:{a}:{d}' for a in ('C0', *(f'C1-{m}' for m in METHODS)))
            ids.extend(f't3:{u}:{m}:{a}:{d}:{o}' for m in METHODS for a in ('C0','C1') for o in OWNERS)
    for axis, pairs in (('t4', plan['t4_pairs']), ('t5', selected or [])):
        for k, _ in enumerate(pairs):
            if axis=='t5': ids.append(f't5desc:{k}')
            for m in METHODS:
                for c in CONDITIONS if axis == 't4' else CONDITIONS[2:]:
                    ids.append(f'{axis}img:{k}:{m}:{c}')
                    ids.extend(f'{axis}:{k}:{m}:{c}:{mode}' for mode in MODES)
    return ids


class _BudgetInterrupt(BaseException):
    """Bypass frozen writer's scientific Exception catcher; worker translates it."""
    def __init__(self, cause): self.cause = cause


class Runtime:
    def __init__(self, plan, base=None):
        import m1b_coco512_worker as W
        verify_runtime_locks(plan,base or W.ROOT)
        import numpy as np
        import torch
        import diffusers
        import three_threat_models as models
        import revised_watermark_v5 as v5
        import f5_latent_codec as f5
        import m1_confirmatory_image_operations as ops
        from diffusers import AutoencoderKL
        from journal_vae_probe import Evaluator, SDXL, SDXL_REV
        from journal_ddim_channel import DifferentiableDDIM
        from f4_transfer_probe import ASSETS
        from journal_e3_writer import embed, supply_f5
        from journal_bch_readout import detect_rgb
        base = base or W.ROOT
        if W.resolve(plan['assets_root'],base).resolve()!=ASSETS.resolve(): raise ValueError('Pinned asset root differs')
        if diffusers.__version__ != '0.35.1': raise ValueError('Pinned diffusers required')
        models.block_network()
        self.asset_receipt, _ = models.verify_assets(ASSETS, base / W.ASSET_LOCK)
        torch.cuda.set_per_process_memory_fraction(9 * 1024**3 / torch.cuda.get_device_properties(0).total_memory)
        self.ev = Evaluator()
        self.pipe = models.load_regenerator(ASSETS)
        self.channel = DifferentiableDDIM(self.pipe)
        self.other = AutoencoderKL.from_pretrained(SDXL, local_files_only=True, use_safetensors=True,
            torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        profile = v5.validate_profile(json.loads(W.resolve(plan['profile']['path'],base).read_text()))
        if profile != v5.validate_profile(self.ev.profile): raise ValueError('Evaluator profile mismatch')
        self.np, self.torch, self.v5, self.f5, self.ops = np, torch, v5, f5, ops
        self.embed_writer, self.supplier, self.readout = embed, supply_f5, detect_rgb
        self.profile, self.budget = profile, lambda: None
        checked, key, config = v5._resolve(profile,None)
        owner = v5.canonical_owner(OWNERS[0])
        self.layout = f5.Layout(checked,key,config,owner)
        self.fragile = v5._Fragile(checked,key,config,owner,512,512)
        self.environment = dict(torch=torch.__version__, diffusers=diffusers.__version__,
            sdxl_revision=SDXL_REV, threads=torch.get_num_threads(),
            matmul_tf32=torch.backends.cuda.matmul.allow_tf32, cudnn_tf32=torch.backends.cudnn.allow_tf32)

    def canonical(self, source):
        from m1b_canonical_source import canonicalize
        from PIL import UnidentifiedImageError
        raw=Path(source['raw_path']).read_bytes()  # storage errors remain infrastructure
        try:
            return canonicalize(raw,source['raw_sha256'])
        except UnidentifiedImageError as error:
            raise ScientificFailure('source_decode_unidentified') from error
        except ValueError as error:
            if str(error).startswith('Unsupported source mode '):
                raise ScientificFailure(str(error)) from error
            raise
        except OSError as error:
            if str(error).startswith('image file is truncated') or str(error)=='broken data stream when reading image file':
                raise ScientificFailure('source_decode_corrupt: '+str(error)) from error
            raise
    def phash(self,rgb):
        return int(self.v5.perceptual_hash(self.v5.luminance_from_rgb(rgb.tolist()),profile=self.profile))
    def categories(self,uids,t5):
        import m1b_coco512_worker as W
        return W.Runtime.categories(self,uids,t5)
    def clip_vector(self,rgb,views): return self.ev.features(rgb,views)
    def quality(self,ref,rgb): return self.ev.metrics(ref,rgb)
    def resources(self):
        return dict(peak_vram_allocated_mib=self.torch.cuda.max_memory_allocated()/2**20,
                    environment=self.environment)
    def supply(self,rgb,folder):
        report=self.supplier(rgb,self.ev,folder/'supplier',self.budget)
        self._execution_error(report)  # refuse software faults before supplier unit commits
        return report
    def embed(self,method,rgb,uid,owner,folder,supplier=None):
        from journal_readability_probe import load
        if owner != OWNERS[0]: raise ValueError('S1 literal alpha required')
        if method == 'e3-s1':
            if supplier is None: raise ValueError('Completed fresh supplier unit required')
            report = dict(supplier=supplier,admitted=False,admission=dict(accepted=False),payload=None)
            if supplier['status'] != 'ok':
                self._execution_error(supplier)
                return None, report
            report['payload'] = supplier['payload']
            writer = self.embed_writer(rgb,owner,supplier['q'],supplier['h'],self.ev,self.other,
                                       self.channel,folder/'writer',self.budget)
            report.update(writer=writer,admitted=writer.get('admitted',False),
                          admission=writer.get('admission',dict(accepted=False)))
            self._execution_error(writer)
            final = writer.get('final_image')
            return (load(final) if final and Path(final).is_file() else None), report
        out, native = self.v5.embed_rgb(rgb.tolist(),owner,profile=self.profile,
            semantic_features=self.ev.features(rgb,1),strict=False)
        return self.np.asarray(out,self.np.uint8), dict(native=native,
            payload=dict(q=native['semantic_code'],h=native['perceptual_hash'],h_target_basis='native intermediate intended h'),
            admitted=bool(native['verified']),admission=dict(accepted=bool(native['verified'])))
    def _execution_error(self,report):
        """Frozen writer catches Exception; restore a conservative typed boundary.

        The supplier has exactly one known expected exception: unreadable native
        channels. Admission failure is returned normally without an exception.
        Every other caught exception is an infrastructure/software interruption,
        except the exact safety-block terminal, which is an adverse observation.
        """
        error=report.get('error')
        status=report.get('status')
        if not error:
            if status in ('supplier_failed','construction_failed'):
                raise OSError('Missing caught-exception details: '+str(status))
            return
        terminal=str(error).strip().splitlines()[-1]
        if status=='supplier_failed' and terminal in (
                'ValueError: Fresh F5 bootstrap native channels unreadable',
                'Fresh F5 bootstrap native channels unreadable'):
            return
        if status in ('supplier_failed','construction_failed') and terminal in (
                'RuntimeError: safety_checker_blocked_output',
                'OperationFailure: safety_checker_blocked_output',
                'm1_confirmatory_image_operations.OperationFailure: safety_checker_blocked_output'):
            return
        raise OSError('Unexpected frozen scientific exception: '+str(error))
    def detect(self,method,rgb,claim,mode='combined',roster=1):
        self.budget()
        features = self.ev.features(rgb,7 if method=='e3-s1' else 1)
        if method=='e3-s1':
            call = self.readout(rgb,self.ev.reader.latent(rgb),claim,self.profile,features,
                binding='soft',binding_mode=mode,roster_size=1)
        else:
            call = self.v5.detect_rgb(rgb.tolist(),claim,profile=self.profile,semantic_features=features,
                binding_mode=mode,roster_size=roster)
        own = call.get('instance_own_content_status')
        if method=='v5-r3':
            distance=call['instance'].get('corrected_distance')
            own_match=(bool(call['instance']['found'] and distance<=int(self.profile['decision']['instance_radius']))
                       if distance is not None else None)
            own='match' if own_match is True else ('mismatch' if own_match is False else None)
            call['instance_own_content_status']=own
        else:
            own_match=own=='match' if own is not None else None
        call['instance']['own_h_content_match'] = own_match
        self.budget(); return call
    def attack(self,rgb,dose):
        _,strength,seed = dose.split('-')
        result = s1_regeneration(rgb,float(strength),int(seed),pipeline=self.pipe,
            generator_factory=self.torch.Generator,inference_context=self.torch.inference_mode)
        return result.rgb8,result.receipt
    def transfer(self,method,recipient,donor,donor_c0,condition):
        if condition.startswith('residual-'):
            from three_threat_protocol import residual_transfer
            scale = float(condition.split('-')[1])
            return self.np.asarray(residual_transfer(recipient.tolist(),donor.tolist(),donor_c0.tolist(),scale),self.np.uint8),dict(operator='residual_transfer',scale=scale)
        if method=='v5-r3':
            from v5_study_protocol import transfer
            return self.np.asarray(transfer(recipient.tolist(),donor.tolist(),self.profile,
                'unmarked_projection_sham' if condition=='public-sham' else 'public_projection'),self.np.uint8),dict(operator='v5_study_protocol.transfer',condition=condition)
        from journal_e3_public_projection import semantic_inverse,fragile_replace
        pD = self.layout.projections(self.ev.reader.latent(donor))
        fD = self.fragile.projections(self.v5.base._analyse(self.v5.luminance_from_rgb(donor.tolist()),self.fragile.analysis)[1])
        semantic,receipt = semantic_inverse(self.ev.reader,recipient,self.layout,pD,self.budget)
        result = fragile_replace(semantic,self.fragile,fD,self.v5,self.budget)
        return self.np.asarray(result,self.np.uint8),dict(operator='E3-PP1',optimization=receipt,public_vector_targets=dict(semantic=self.np.asarray(pD).tolist(),fragile=self.np.asarray(fD).tolist()))


def run(worker):
    """Reuse existing unit journal, failure classification, saved-pixel and resume boundary."""
    import m1b_coco512_worker as W
    w = worker
    def budget():
        try:
            w.check_budget()
            resources = getattr(w.rt,'resources',lambda:{})()
            if resources.get('peak_vram_allocated_mib',0)>9*1024:
                raise W.InfrastructureStop('budget','GPU memory ceiling')
        except (W.Stop,W.InfrastructureStop) as e: raise _BudgetInterrupt(e)
    w.rt.budget = budget
    def image(unit):
        row=w.journal.get(unit)
        if not row or row.get('outcome')!='completed' or not row.get('image'): return None
        return w._load(row['image'])
    def payload(uid,m): return (w.journal.get(f'src:{uid}:{m}:embed') or {}).get('payload')
    def call(rid,img,m,owner,fields,mode='combined',roster=None,target=None):
        fields.update(binding_mode=mode,roster_size=roster or (1 if m=='e3-s1' else 4),
            claimed_owner=owner,payload=target)
        if img is None: return w._missing(rid,'pixels unavailable',**fields)
        def detect():
            d=w.rt.detect(m,img,owner,mode,fields['roster_size'])
            body=dict(detection=d)
            if fields.get('stage') in ('t4','t5'):
                reference=w.journal.get(f"src:{fields['recipient_uid']}:{m}:clean:C0:{OWNERS[0]}") or {}
                source_call=reference.get('detection') or {}
                diag=dict(q_now=d.get('semantic_code'),h_now=d.get('perceptual_hash'),
                    q_bound=d.get('q_bound',d.get('instance_tested_with_semantic_code')),
                    recipient_source_q=source_call.get('semantic_code'),recipient_source_h=source_call.get('perceptual_hash'),
                    h_target_route='supplier operational h' if m=='e3-s1' else 'native intermediate intended h',
                    source_h_route='native C0 perceptual recomputation')
                for tier,key,current in (('semantic','q',d.get('semantic_code')),('instance','h',d.get('perceptual_hash'))):
                    intended=(target or {}).get(key)
                    source_word=source_call.get('semantic_code' if key=='q' else 'perceptual_hash')
                    diag[key+'_donor_to_current_distance']=(int(intended,16)^int(current,16)).bit_count() if intended is not None and current is not None else None
                    diag[key+'_donor_equals_recipient_source']=intended==source_word if intended is not None and source_word is not None else None
                body['content_diagnostics']=diag

            if mode=='combined':
                sem,inst=d['semantic'],d['instance']
                body['same_call_predicates']=same_call_predicates(d)
            return body
        return w._unit(rid,detect,**fields)
    try:
        # All source descriptors and source-only selection precede every supplier/mark/detector.
        for s in w.sources:
            uid=s['uid']
            def canon(s=s,uid=uid):
                rgb,receipt=w.rt.canonical(s)
                return dict(image=w._save(f'{W.file_tag(uid)}-C0-{uuid.uuid4().hex}.png',rgb),canonical_receipt=receipt,source_phash=w.rt.phash(rgb))
            w._unit(f'src:{uid}:canon',canon,stage='source',uid=uid,group_id=s['group_id'])
        def selection():
            from m1_confirmatory_t5_pairs import schedule
            uids=[s['uid'] for s in w.sources]; cats=w.rt.categories(uids,w.plan['t5']); observations=[]
            for s in w.sources:
                c=cats.get(s['uid']); row=w.journal.get(f"src:{s['uid']}:canon") or {}
                error='canonical_source_unavailable' if row.get('outcome')!='completed' else ('annotation:'+c if isinstance(c,str) else None)
                observations.append(dict(uid=s['uid'],group_id=s['group_id'],error=error,
                    categories=None if error else list(c or []),phash=None if error else row['source_phash']))
            return dict(selection=schedule(observations,uids,w.plan['t5']['max_pairs']),observations=observations)
        selected_row=w._unit('t5:selection',selection,stage='t5_selection')
        selected=selected_row['selection']['pairs'] if selected_row.get('outcome')=='completed' else None
        for s in w.sources:
            uid=s['uid']; c0=image(f'src:{uid}:canon')
            supplier_id=f'src:{uid}:e3-s1:supplier'
            if c0 is None: w._missing(supplier_id,'canonical source unavailable',stage='supplier',uid=uid,method='e3-s1')
            else:
                def supply(c0=c0,uid=uid):
                    folder=w.images/('s-'+W.sha_bytes(uid.encode('utf-8'))[:12]+'-'+uuid.uuid4().hex[:12]);folder.mkdir(exist_ok=False)
                    report=w.rt.supply(c0,folder)
                    if hasattr(w.rt,'_execution_error'): w.rt._execution_error(report)
                    return dict(supplier=report,payload=report.get('payload'),supplier_success=report.get('status')=='ok')
                w._unit(supplier_id,supply,stage='supplier',uid=uid,method='e3-s1')
            supplier=(w.journal.get(supplier_id) or {}).get('supplier')
            for m in METHODS:
                eid=f'src:{uid}:{m}:embed'
                if c0 is None: w._missing(eid,'canonical source unavailable',stage='embed',uid=uid,method=m)
                else:
                    def embed(m=m,uid=uid,c0=c0,supplier=supplier):
                        folder=w.images/('c-'+W.sha_bytes(uid.encode('utf-8'))[:12]+'-'+uuid.uuid4().hex[:12])
                        folder.mkdir(exist_ok=False)
                        if m=='e3-s1' and (supplier or {}).get('status')!='ok':
                            rgb,report=None,dict(supplier=supplier,admitted=False,admission=dict(accepted=False),payload=None)
                        else:
                            rgb,report=w.rt.embed(m,c0,uid,OWNERS[0],folder,supplier)
                        body=dict(report=report,admitted=bool(report.get('admitted')),admission=report.get('admission'),payload=report.get('payload'),supplier_success=((report.get('supplier') or {}).get('status')=='ok' if m=='e3-s1' else None),returned_final_pixels=rgb is not None)
                        if rgb is not None:
                            body.update(image=w._save(f'{W.file_tag(uid)}-C1-{m}-{uuid.uuid4().hex}.png',rgb),quality=w.rt.quality(c0,rgb))
                        return body
                    w._unit(eid,embed,stage='embed',uid=uid,method=m,owner=OWNERS[0])
                c1=image(eid)
                for arm,img in (('C0',c0),('C1',c1)):
                    for owner in OWNERS:
                        call(f'src:{uid}:{m}:clean:{arm}:{owner}',img,m,owner,
                            dict(stage='clean',uid=uid,method=m,arm=arm,claim='correct' if owner==OWNERS[0] else 'wrong'),target=payload(uid,m) if arm=='C1' and owner==OWNERS[0] else None)
        for s in w.sources:
            uid=s['uid']; c0=image(f'src:{uid}:canon')
            for dose in DOSES:
                for key,dep in [('C0',f'src:{uid}:canon')]+[(f'C1-{m}',f'src:{uid}:{m}:embed') for m in METHODS]:
                    aid=f'atk:{uid}:{key}:{dose}'; original=image(dep)
                    if original is None: w._missing(aid,'input pixels unavailable',stage='t3_attack',uid=uid,input=key,dose=dose)
                    else:
                        def attack(original=original,key=key,dose=dose,uid=uid,c0=c0):
                            rgb,receipt=w.rt.attack(original,dose)
                            return dict(image=w._save(f'{W.file_tag(uid)}-{key}-{dose}-{uuid.uuid4().hex}.png',rgb),operation_receipt=receipt,quality_vs_input=w.rt.quality(original,rgb),quality_vs_source=w.rt.quality(c0,rgb))
                        w._unit(aid,attack,stage='t3_attack',uid=uid,input=key,dose=dose)
                    attacked=image(aid)
                    for m in METHODS if key=='C0' else (key[3:],):
                        arm='C0' if key=='C0' else 'C1'
                        for owner in OWNERS:
                            call(f't3:{uid}:{m}:{arm}:{dose}:{owner}',attacked,m,owner,
                                dict(stage='t3',uid=uid,method=m,arm=arm,dose=dose,claim='correct' if owner==OWNERS[0] else 'wrong'),target=payload(uid,m) if arm=='C1' and owner==OWNERS[0] else None)
        for axis,pairs in (('t4',w.plan['t4_pairs']),('t5',selected or [])):
            for k,p in enumerate(pairs):
                donor=p['donor_uid'] if axis=='t4' else p['left']; recipient=p['recipient_uid'] if axis=='t4' else p['right']
                r0=image(f'src:{recipient}:canon'); d0=image(f'src:{donor}:canon')
                if axis=='t5':
                    def describe(r0=r0,d0=d0):
                        return dict(descriptors={f'clip_cosine_views{views}':float(sum(a*b for a,b in zip(w.rt.clip_vector(d0,views),w.rt.clip_vector(r0,views)))) for views in (1,7)})
                    w._unit(f't5desc:{k}',describe,stage='t5_descriptors',pair_index=k,donor_uid=donor,recipient_uid=recipient,phash_distance=p['phash_distance'])
                for m in METHODS:
                    for condition in CONDITIONS if axis=='t4' else CONDITIONS[2:]:
                        iid=f'{axis}img:{k}:{m}:{condition}'; d=image(f'src:{donor}:{m}:embed') if condition!='public-sham' else d0
                        fields=dict(stage=axis+'_image',pair_index=k,method=m,condition=condition,donor_uid=donor,recipient_uid=recipient)
                        if r0 is None or d is None or d0 is None: w._missing(iid,'donor/recipient pixels unavailable',**fields)
                        else:
                            def transfer(m=m,condition=condition,r0=r0,d=d,d0=d0,iid=iid):
                                rgb,receipt=w.rt.transfer(m,r0,d,d0,condition)
                                return dict(image=w._save(W.file_tag(iid)+'-'+uuid.uuid4().hex+'.png',rgb),operation_receipt=receipt,quality_vs_recipient=w.rt.quality(r0,rgb))
                            w._unit(iid,transfer,**fields)
                        transferred=image(iid); target=payload(donor,m) if condition!='public-sham' else None
                        for mode in MODES:
                            call(f'{axis}:{k}:{m}:{condition}:{mode}',transferred,m,OWNERS[0],
                                dict(stage=axis,pair_index=k,method=m,condition=condition,donor_uid=donor,recipient_uid=recipient,quality_vs_recipient=(w.journal.get(iid) or {}).get('quality_vs_recipient')),mode=mode,roster=1,target=target)
        return 'finished',selected,None
    except _BudgetInterrupt as e:
        if isinstance(e.cause,W.Stop): status,error='checkpointed',None
        else: status,error='infrastructure_stop',str(e.cause)
    except W.Stop: status,error='checkpointed',None
    except W.InfrastructureStop as e: status,error='infrastructure_stop',str(e)
    sel=w.journal.get('t5:selection') or {}
    return status,sel.get('selection',{}).get('pairs'),error


def validate_plan(plan,base):
    import m1b_coco512_worker as W
    if plan.get('schema')!=W.PLAN_SCHEMA or plan.get('data_split') not in W.SPLITS: raise ValueError('invalid S1 schema/split')
    if set(plan)-set(W.SCIENCE_FIELDS)-set(W.OPERATIONAL_FIELDS): raise ValueError('unknown S1 plan fields')
    if tuple(plan.get('methods',()))!=METHODS or tuple(plan.get('owners',()))!=OWNERS:
        raise ValueError('S1 methods and literal owner roster required')
    if plan.get('strengths')!=[.1,.2] or plan.get('seeds')!=[3,4,5] or plan.get('patch_sizes')!=[]:
        raise ValueError('S1 frozen T3 grid required')
    for k in ('f5_config','profile','s1_config','environment_lock','sdxl_lock'): W._ref(plan.get(k),k)
    sources=W.load_sources(plan,base); uids=[s['uid'] for s in sources]
    if plan.get('t3_uids')!=uids: raise ValueError('S1 T3 uses every source in frozen order')
    pairs=plan.get('t4_pairs'); used=set()
    if not isinstance(pairs,list) or len(pairs)>30: raise ValueError('S1 T4 cap30 required')
    for i,p in enumerate(pairs):
        if p.get('pair_index')!=i or p.get('donor_uid') not in uids or p.get('recipient_uid') not in uids or p['donor_uid']==p['recipient_uid']:
            raise ValueError('invalid S1 T4 pair')
        if p['donor_uid'] in used or p['recipient_uid'] in used: raise ValueError('S1 T4 requires disjoint source pairs')
        used.update((p['donor_uid'],p['recipient_uid']))
    if len({s['group_id'] for s in sources})!=len(sources): raise ValueError('S1 distinct source groups required')
    t5=plan.get('t5') or {}
    if t5.get('selector') not in ('coco-instances','fixture-categories') or not isinstance(t5.get('max_pairs'),int) or not 1<=t5['max_pairs']<=30:
        raise ValueError('S1 frozen source-only T5 selector required')
    if t5['selector']=='coco-instances': W._ref(t5.get('annotations'),'t5.annotations')
    if plan.get('max_wall_seconds') is not None and (type(plan['max_wall_seconds'])!=int or plan['max_wall_seconds']<60): raise ValueError('invalid unit time ceiling')
    if plan.get('resume_from') and plan['data_split']!='development' and not isinstance(plan.get('resume_parent_approval_sha256'),str): raise ValueError('continuation parent approval required')
    if plan['data_split'] in ('test','rehearsal') and not isinstance(plan.get('approval_path'),str): raise ValueError('approval_path required')
    for f in plan.get('fault_injection') or []:
        if set(f)!={'unit','kind'} or f['kind'] not in ('oserror','cuda','scientific'): raise ValueError('invalid fault injection')
    if plan['data_split']=='test':
        index=W._ref(plan['sources'].get('index'),'sources.index'); sched=W._ref(plan.get('schedule'),'schedule')
        index_path,index_hash = (LINUX_FRESH_INDEX,LINUX_FRESH_INDEX_SHA256) if sys.platform=='linux' else (FRESH_INDEX,FRESH_INDEX_SHA256)
        if index['path']!=index_path or index['sha256']!=index_hash or sched['path']!=FRESH_SCHEDULE or sched['sha256']!=FRESH_SCHEDULE_SHA256: raise ValueError('S1 fresh frozen metadata contract required')
        if W.sha_file(W.resolve(sched['path'],base))!=sched['sha256']: raise ValueError('S1 schedule hash mismatch')
        schedule=json.loads(W.resolve(sched['path'],base).read_text(encoding='utf-8-sig'))
        if schedule.get('t3_source_uids')!=uids or schedule.get('t4_pairs')!=pairs or [c['source_uid'] for c in schedule.get('clean',[])]!=uids: raise ValueError('S1 schedule differs')
        if t5['selector']!='coco-instances' or t5['max_pairs']!=30 or t5['annotations']['sha256']!=W.HELD_OUT_ANNOTATION_SHA256 or plan.get('fault_injection'): raise ValueError('S1 test frozen T5 contract required')
    else:
        held=W.held_out_identities(base)
        for s in sources:
            if s['uid'] in held['uids'] or s['group_id'] in held['groups'] or s['raw_sha256'] in held['raw'] or W.under_held_out_root(s['raw_path']): raise ValueError('non-test source intersects held-out metadata')
        if t5['selector']=='coco-instances' and (t5['annotations']['sha256']==W.HELD_OUT_ANNOTATION_SHA256 or W.under_held_out_root(W.resolve(t5['annotations']['path'],base))): raise ValueError('non-test held-out annotation refused')
    return plan,sources


def verify_runtime_locks(plan,base):
    """Approval happens in main first; enforce runtime/model locks before loading models."""
    import sys
    import platform
    import importlib.metadata
    import m1b_coco512_worker as W
    refs={k:W.resolve(plan[k]['path'],base) for k in ('s1_config','environment_lock','sdxl_lock')}
    for k,p in refs.items():
        if W.sha_file(p)!=plan[k]['sha256']: raise ValueError(k+' digest changed')
    if W.sha_file(refs['s1_config'])!=S1_CONFIG_SHA256: raise ValueError('frozen S1 config differs')
    env=json.loads(refs['environment_lock'].read_text())
    if platform.python_version()!=env['python'] or sys.platform!=env['platform']: raise ValueError('Python/platform lock differs')
    for package,version in env['packages'].items():
        if importlib.metadata.version(package)!=version: raise ValueError('package lock differs: '+package)
    lock=json.loads(refs['sdxl_lock'].read_text())
    if lock['revision']!='6f5909a7e596173e25d4e97b07fd19cdf9611c76' or lock['dtype']!='float32': raise ValueError('SDXL lock differs')
    root=Path(lock['root'])
    from thesis_deployment_paths import SDXL
    if root.resolve()!=SDXL.resolve(): raise ValueError('Pinned SDXL root differs')
    for f in lock['files']:
        p=root/f['path']
        if not W.under(p,root) or p.stat().st_size!=f['size_bytes'] or W.sha_file(p)!=f['sha256']: raise ValueError('SDXL asset differs: '+f['path'])


def same_call_predicates(call):
    """Hold channel presence and routing fixed when comparing content predicates."""
    sem,inst=call['semantic'],call['instance']
    present=bool(sem.get('found') and inst.get('found'))
    return dict(semantic_only=present and bool(sem.get('content_match')),
        perceptual_only=present and bool(inst.get('own_h_content_match')),
        none=present,combined=present and bool(sem.get('content_match') and inst.get('content_match')),
        instance_own_h_content_match=inst.get('own_h_content_match'))


def s1_regeneration(image,strength,seed,*,pipeline,generator_factory,inference_context):
    """Same saved-pixel DDIM operator, explicit S1 strengths and fresh seed roster.

    Keep historical operation/constants untouched. Only its versioned seed
    validation changes here; all scheduler, safety, conversion and receipt checks
    are the existing operator's exact contract.
    """
    import numpy as np
    from PIL import Image
    import m1_confirmatory_image_operations as ops
    import three_threat_models as models
    image=ops.rgb8(image)
    if type(strength) not in (int,float) or strength not in (.1,.2): raise ValueError('S1 frozen strength required')
    if type(seed) is not int or seed not in (3,4,5): raise ValueError('S1 frozen evaluation seed required')
    for key,expected in models.DDIM_CONFIG.items():
        if getattr(pipeline.scheduler.config,key,object())!=expected: raise ValueError('Effective DDIM config mismatch: '+key)
    if pipeline.safety_checker is None or pipeline.feature_extractor is None: raise ValueError('Required pipeline safety components missing')
    receipt=ops._receipt(image,'SD1.5 DDIM20 img2img')
    receipt.update(protocol=PROTOCOL,strength=strength,seed=seed,ddim_config=dict(models.DDIM_CONFIG),
        prompt='',negative_prompt='',guidance_scale=1.,eta=0.,num_inference_steps=20,
        actual_ddim_timesteps=[],nfe_unet=0,safety_verdict=None)
    def forward(module,args,kwargs,output):
        t=args[1] if len(args)>1 else kwargs['timestep']
        if hasattr(t,'detach'): t=t.detach().cpu().item()
        t=float(t)
        if not math.isfinite(t): raise ValueError('Nonfinite actual UNet timestep')
        receipt['actual_ddim_timesteps'].append(t);receipt['nfe_unet']+=1
    hook=pipeline.unet.register_forward_hook(forward,with_kwargs=True)
    try:
        generator=generator_factory(device='cuda').manual_seed(seed)
        kwargs=dict(prompt='',negative_prompt='',image=Image.fromarray(image),strength=strength,
            num_inference_steps=20,eta=0.,guidance_scale=1.,generator=generator,
            num_images_per_prompt=1,output_type='pil',return_dict=True)
        with inference_context(): result=pipeline(**kwargs)
        receipt['safety_verdict']=getattr(result,'nsfw_content_detected',None)
        receipt['scheduler_timesteps']=ops._numbers(pipeline.scheduler.timesteps)
        generated=models.validate_generated(result)
        expected=list(ops.TIMESTEPS[-int(20*strength):])
        if receipt['scheduler_timesteps']!=list(ops.TIMESTEPS) or receipt['actual_ddim_timesteps']!=expected:
            raise ValueError('Actual DDIM timestep inventory differs from frozen operator')
        return ops._finish(np.asarray(generated),receipt)
    except Exception as error:
        raise ops.OperationFailure(str(error),receipt) from error
    finally: hook.remove()


class ScientificFailure(Exception):
    """An explicit known adverse scientific/data observation, never a code defect."""


def is_scientific_failure(error):
    """S1 allowlist. Untyped AssertionError/ValueError never become outcomes."""
    if isinstance(error,ScientificFailure): return True
    # A wrapped OperationFailure can carry this exact safety message. A merely
    # similar message or an exception whose cause is a software bug is refused.
    terminal=str(error).strip()
    if terminal!='safety_checker_blocked_output': return False
    chain=error
    for _ in range(8):
        if chain is None: break
        if not isinstance(chain,RuntimeError) or str(chain).strip()!='safety_checker_blocked_output': return False
        chain=chain.__cause__ or chain.__context__
    return True
