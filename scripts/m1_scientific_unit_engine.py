"""Injected scientific unit orchestration; never reads raw files or grants authority."""
from __future__ import annotations
import copy
import math
import re
import time
import numpy as np
import m1_owner_interface as owners
import m1_confirmatory_image_operations as operations

VERSION='m1-scientific-unit-engine-v1'


def _finite(value):
    if isinstance(value,(float,np.floating)) and not math.isfinite(value):
        raise ValueError('Nonfinite scientific result')
    if isinstance(value,dict):
        for item in value.values():_finite(item)
    elif isinstance(value,(list,tuple)):
        for item in value:_finite(item)


def _receipt(value):
    if not isinstance(value,dict) or type(value.get('sha256')) is not str or re.fullmatch('[0-9a-f]{64}',value['sha256']) is None:
        raise ValueError('Sink must return explicit lowercase SHA256 artifact receipt')
    return copy.deepcopy(value)


def validate_identity(rgb,identity,mode,schedule=None,owner=None):
    """Identity checks are integrity checks, never a raw-source authorization."""
    rgb=operations.rgb8(rgb)
    if not isinstance(identity,dict) or identity.get('source_rgb8_sha256')!=operations.pixel_sha(rgb):
        raise ValueError('Canonical source hash differs')
    uid=identity.get('source_id')
    if type(uid) is not str or not uid:raise ValueError('Explicit source_id required')
    if mode=='scientific':
        if identity.get('data_split')!='test' or identity.get('source_uid')!=uid or type(identity.get('group_id')) is not str or not identity['group_id']:
            raise ValueError('Exact scientific UID/group/test identity required')
        if not isinstance(schedule,dict) or schedule.get('source_uid')!=uid or schedule.get('group_id')!=identity['group_id']:
            raise ValueError('Scheduled UID/group differs')
        expected=owners.source_schedule(uid)
        for field in ('owner','wrong_owner','seed_uint64_decimal','seed_uint64_hex'):
            if schedule.get(field)!=expected[field]:raise ValueError('Scheduled owner/uint64 differs: '+field)
        owners.validate_seed_metadata(schedule['seed_uint64_decimal'],schedule['seed_uint64_hex'])
        if owner is not None and owner!=expected['owner']:raise ValueError('Explicit owner differs from schedule')
        return rgb,expected['owner'],uid
    if mode=='generated':
        from m1_blind_noise_core import OWNERS
        if (not uid.startswith('fixture:') or identity.get('data_split')!='synthetic' or
                type(identity.get('generator_seed')) is not int or identity['generator_seed'] not in (0,1) or
                schedule is not None or owner not in OWNERS):
            raise ValueError('Generated fixture identity/owner cannot impersonate scientific schedule')
        return rgb,owner,None
    raise ValueError('Explicit generated or scientific identity mode required')


class UnitEngine:
    """One primitive path for prefix/full/resume and persist-before-readout.

    Sink owns storage and verification. Its save_image returns reread pixels;
    engine refuses changed saved bytes before any detector or quality call.
    Context owns pinned model loading/placement and adapter mathematical code.
    """
    def __init__(self,context,sink,check=lambda:None,event=lambda row:None,stop_exceptions=(TimeoutError,)):
        self.context,self.sink,self.check,self.event=context,sink,check,event
        self.stop_exceptions=stop_exceptions

    def _checkpoint(self,value):
        self.check()
        receipt=_receipt(self.sink.save_checkpoint(f"{value['phase']}-{value['step']:03d}",value))
        self.event(dict(kind='checkpoint',phase=value['phase'],step=value['step'],receipt=receipt))

    def initialize(self,rgb8,identity,*,mode,schedule=None,owner=None,resume=None,stop_step=200):
        source,owner,uid=validate_identity(rgb8,identity,mode,schedule,owner)
        self.context.place_inference('cpu');self.check()
        return self.context.adapter.initialize(source,copy.deepcopy(identity),owner,source_uid=uid,
            resume=resume,stop_step=stop_step,on_checkpoint=self._checkpoint,check=self.check)

    def _persist_image(self,name,rgb):
        image=operations.rgb8(rgb);self.check()
        saved,receipt=self.sink.save_image(name,image.copy())
        saved=operations.rgb8(saved)
        if not np.array_equal(saved,image):raise ValueError('Saved RGB8 bytes differ from operator output')
        return dict(rgb8=saved,image=_receipt(receipt),rgb8_sha256=operations.pixel_sha(saved))

    def _array(self,name,value):
        if hasattr(value,'detach'):value=value.detach().float().cpu().numpy()
        value=np.asarray(value)
        if value.dtype.kind not in 'fiu' or not np.isfinite(value).all():raise ValueError('Finite numeric stage array required')
        return _receipt(self.sink.save_array(name,value.copy()))

    def enroll(self,rgb8,identity,initializer,*,mode,schedule=None,owner=None,resume=None,stop_step=100):
        source,owner,uid=validate_identity(rgb8,identity,mode,schedule,owner)
        binding=initializer.get('binding',{})
        if binding.get('source_identity')!=identity or binding.get('owner')!=owner or binding.get('source_uid')!=uid:
            raise ValueError('Initializer source/owner/mode differs')
        self.context.place_inference('cpu');self.check()
        result=self.context.adapter.embed(source,initializer,resume=resume,stop_step=stop_step,
            on_checkpoint=self._checkpoint,event=self.event,check=self.check)
        output=dict(schema=VERSION,completed=result['completed'],checkpoint=result['checkpoint'],mode=mode)
        if not result['completed']:return output
        from m1_blind_noise import rgb8 as quantize
        reference=result['core_result']['reference']
        if hasattr(reference,'detach'):
            reference=reference.detach().float().cpu().numpy()[0].transpose(1,2,0).astype(np.float64)
        elif np.asarray(reference).shape==(1,3,512,512):
            reference=np.asarray(reference)[0].transpose(1,2,0).astype(np.float64)
        images={'C0-source':source,'C0-reconstruction':quantize(reference),'C1':result['marked_rgb8']}
        output['images']={name:self._persist_image(name,image) for name,image in images.items()}
        output['arrays']={name:self._array(name,result['core_result'][name]) for name in ('reference','decoded','residual','surrogate')}
        output['cap']=copy.deepcopy(result['cap']);_finite(output['cap'])
        self.context.place_inference('cuda')
        output['quality_vs_source']={name:self.context.quality(source,item['rgb8']) for name,item in output['images'].items()}
        output['quality_vs_reconstruction']=self.context.quality(images['C0-reconstruction'],images['C1'])
        _finite(output['quality_vs_source']);_finite(output['quality_vs_reconstruction'])
        return output

    def assess_image(self,unit_id,rgb8,*,source_rgb8,matched_clean_rgb8,claims,mode,reader=None,retain_latent=True,image_unit=None,query_units=None):
        roster=owners.A4_OWNERS
        if mode=='generated':
            from m1_blind_noise_core import OWNERS
            roster=OWNERS
        elif mode!='scientific':raise ValueError('Explicit identity mode required')
        if not isinstance(claims,(tuple,list)) or not claims or len(set(claims))!=len(claims) or any(type(o) is not str or o not in roster for o in claims):
            raise ValueError('Exact unique claims required')
        source=operations.rgb8(source_rgb8);clean=operations.rgb8(matched_clean_rgb8)
        if image_unit is not None and (image_unit.get('id')!=unit_id or image_unit.get('kind')!='image'):
            raise ValueError('Exact planned image unit required')
        if query_units is not None:
            if image_unit is None or len(query_units)!=len(claims) or [q.get('owner') for q in query_units]!=list(claims) or len({q.get('id') for q in query_units})!=len(query_units):
                raise ValueError('Exact ordered planned query units required')
            for query in query_units:
                if query.get('kind')!='query' or unit_id not in query.get('dependencies',[]):raise ValueError('Query dependency differs')
                for field in ('source_uid','group_id','method'):
                    if query.get(field)!=image_unit.get(field):raise ValueError('Query source/group/method differs')
        saved=self._persist_image(unit_id,rgb8)
        self.context.place_inference('cuda');self.check()
        safety=self.context.safety_check(saved['rgb8'])
        result=dict(copy.deepcopy(image_unit or {}),schema=VERSION,id=unit_id,outcome='completed',**saved,safety=copy.deepcopy(safety),
                    quality_vs_source=self.context.quality(source,saved['rgb8']),
                    quality_vs_same_arm_clean=self.context.quality(clean,saved['rgb8']),queries=[])
        _finite(result['quality_vs_source']);_finite(result['quality_vs_same_arm_clean'])
        if retain_latent:
            E,H,z=self.context.adapter.public.observations(saved['rgb8'])
            result['reader_arrays']=dict(E=self._array(unit_id+'-E',E),z=self._array(unit_id+'-z',z))
            result['suspect_H']=int(H)
            result['suspect_E']=np.asarray(E,dtype=np.float64).tolist()
        read=self.context.readout if reader is None else reader
        synchronize=getattr(self.context,'synchronize',lambda:None)
        synchronize();started=time.monotonic()
        for index,owner in enumerate(claims):
            self.check();tick=time.monotonic();decision=read(saved['rgb8'].copy(),owner);_finite(decision)
            planned=copy.deepcopy(query_units[index]) if query_units is not None else {}
            result['queries'].append(dict(planned,outcome='completed',owner=owner,decision=copy.deepcopy(decision),
                upstream_image_id=unit_id,upstream_image=saved['image'],upstream_rgb8_sha256=saved['rgb8_sha256'],wall_seconds=time.monotonic()-tick))
        synchronize();result['extract_seconds']=time.monotonic()-started
        return result

    def clean(self,enrollment,*,claims_by_control,mode):
        """Explicit roster prevents adding reconstruction to an older parity roster."""
        if not enrollment.get('completed') or enrollment.get('mode')!=mode:
            raise ValueError('Complete same-mode enrollment required for clean assessment')
        images=enrollment['images']
        if not isinstance(claims_by_control,dict) or not claims_by_control or not set(claims_by_control)<=set(images):
            raise ValueError('Explicit planned clean control roster required')
        return {control:self.assess_image(control+'-clean',images[control]['rgb8'],
            source_rgb8=images['C0-source']['rgb8'],matched_clean_rgb8=images[control]['rgb8'],
            claims=claims,mode=mode) for control,claims in claims_by_control.items()}

    def attack(self,unit_id,operation,**assessment):
        """Failure retains condition identity; caller propagates its dependencies."""
        try:
            self.check();generated=operation()
            if not isinstance(generated,operations.OperationResult):raise ValueError('Explicit image operation result required')
            value=self.assess_image(unit_id,generated.rgb8,**assessment)
            value['operator_receipt']=copy.deepcopy(generated.receipt)
            return value
        except Exception as error:
            failed=dict(schema=VERSION,id=unit_id,outcome='execution_failed',error=str(error),
                operator_receipt=copy.deepcopy(getattr(error,'receipt',None)),human_visual_verdict=None)
            if isinstance(error,self.stop_exceptions):
                self.event(dict(kind='unit_stopped',unit=failed))
                raise
            self.check() # A failure cannot suppress a newly exhausted global budget.
            return failed

    def comparator_enroll(self,unit_id,rgb8,source_uid,comparator):
        result,report=comparator.embed(operations.rgb8(rgb8),source_uid)
        saved=self._persist_image(unit_id,result.rgb8)
        return dict(schema=VERSION,outcome='completed',**saved,operator_receipt=result.receipt,
                    codec_report=copy.deepcopy(report))


def propagate_missing(planned_rows,failed_ids):
    """Retain IDs/denominators; never convert missing descendants to negatives."""
    rows=copy.deepcopy(planned_rows)
    if len({r['id'] for r in rows})!=len(rows):raise ValueError('Duplicate planned unit ID')
    ids={r['id'] for r in rows};failed=set(failed_ids)
    if not failed<=ids:raise ValueError('Unknown failed unit')
    for row in rows:
        if not set(row.get('dependencies',[]))<=ids:raise ValueError('Unknown dependency')
    changed=True
    while changed:
        changed=False
        for row in rows:
            missing=sorted(set(row.get('dependencies',[]))&failed)
            if missing and row['id'] not in failed:
                if row.get('outcome')=='completed':raise ValueError('Completed descendant contradicts missing upstream')
                row.update(outcome='missing_dependency',missing_dependencies=missing,reason='Upstream attempt absent or failed')
                failed.add(row['id']);changed=True
    return rows
