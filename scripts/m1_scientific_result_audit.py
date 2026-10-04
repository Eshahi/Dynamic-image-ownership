"""CPU audit of retained unit artifacts; no raw acquisition or model inference.

The caller first validates authority, run/core identity and recovery lineage.
CLIP/VAE/LPIPS outputs remain recorded model observations, not independently
re-inferred by this module. Receipt hashes alone do not establish authority.
"""
from __future__ import annotations
import hashlib
import io
import math
import os
from pathlib import Path
import re
import stat
import numpy as np
from PIL import Image
import m1_blind_noise_core as core
from m1_latent_reconstruction import quality as pixel_quality
from m1_scientific_analysis import quality as validate_quality

VERSION='m1-scientific-result-audit-v1'


def audit_v5_image(row,artifacts,*,source_rgb8,matched_clean_rgb8,profile,queries):
    """Replay codec from saved pixels and its exact retained feature input."""
    from m1_confirmatory_image_operations import V5Comparator
    if row.get('outcome')!='completed':raise ValueError('Completed image required')
    rgb=artifacts.image(row['image'],row['rgb8_sha256'])
    if row.get('safety')!={'checker':'pinned SD1.5 FP16','nsfw':False}:
        raise ValueError('Successful pinned safety receipt required')
    audit_quality(source_rgb8,rgb,row['quality_vs_source'])
    audit_quality(matched_clean_rgb8,rgb,row['quality_vs_same_arm_clean'])
    feature=artifacts.array(row['reader_arrays']['v5_semantic_features'],(512,))
    comparator=V5Comparator(profile,lambda image:feature)
    checked=[]
    for query in queries:
        if query.get('outcome')!='completed' or query.get('upstream_image_id')!=row['id']:
            raise ValueError('Completed query image identity differs')
        for key,expected in [('upstream_image',row['image']),('upstream_rgb8_sha256',row['rgb8_sha256']),('reader_arrays',row['reader_arrays'])]:
            if query.get(key)!=expected:raise ValueError('Query image/readout receipt differs')
        actual=comparator.extract(rgb,query['owner'])
        recorded=query['decision']
        # Wall-clock timings are observations, never part of detector algebra.
        for decision in (actual,recorded):
            timing=decision.get('timing_ms')
            if type(timing) is not dict or set(timing)!={'setup','transform','features','scoring','total'} or any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in timing.values()):
                raise ValueError('Finite nonnegative codec timing required')
        scientific=lambda d:{key:value for key,value in d.items() if key!='timing_ms'}
        if scientific(actual)!=scientific(recorded):raise ValueError('Independent v5 codec replay differs')
        checked.append(query['id'])
    return dict(schema=VERSION,image_id=row['id'],verified_queries=checked,
        pixels='verified',codec='recomputed_exactly_except_timing_ms',
        semantic_features='exact retained comparator input, not re-inferred',
        authority='REQUIRED_UPSTREAM',run_and_recovery_identity='REQUIRED_UPSTREAM')


class Artifacts:
    def __init__(self,roots):
        self.roots=tuple(Path(p).absolute() for p in roots)
        if not self.roots:raise ValueError('Explicit verified attempt roots required')
        for root in self.roots:self._path(root)

    def _path(self,value):
        path=Path(value).absolute()
        if '..' in path.parts or not any(path.is_relative_to(r) for r in self.roots):
            raise ValueError('Artifact outside verified attempt roots')
        for part in (path,*path.parents):
            if part.exists():
                info=part.lstat()
                if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
                    raise ValueError('Linked artifact path refused')
        return path

    def read(self,receipt,limit=128*1024*1024):
        if type(receipt) is not dict or not {'path','sha256'}<=receipt.keys():
            raise ValueError('Explicit artifact receipt required')
        if type(receipt['sha256']) is not str or not re.fullmatch('[0-9a-f]{64}',receipt['sha256']):
            raise ValueError('Exact SHA256 required')
        path=self._path(receipt['path'])
        with path.open('rb') as stream:
            from m1_confirmatory_raw_guard import _handle_final_path
            if os.path.normcase(str(_handle_final_path(stream.fileno())))!=os.path.normcase(str(path)):
                raise ValueError('Opened artifact handle path differs')
            before=os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or not 0<before.st_size<=limit:
                raise ValueError('Artifact type/link/size differs')
            raw=stream.read(limit+1);after=os.fstat(stream.fileno())
        identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
        if identity(before)!=identity(after) or identity(after)!=identity(path.stat()):
            raise ValueError('Artifact changed during audit')
        if len(raw)!=before.st_size or hashlib.sha256(raw).hexdigest()!=receipt['sha256']:
            raise ValueError('Artifact bytes differ from receipt')
        if 'size_bytes' in receipt and (type(receipt['size_bytes']) is not int or receipt['size_bytes']!=len(raw)):
            raise ValueError('Artifact byte count differs')
        return raw

    def image(self,receipt,pixel_sha):
        with Image.open(io.BytesIO(self.read(receipt,8*1024*1024))) as im:
            if im.format!='PNG' or im.mode!='RGB' or im.size!=(512,512):
                raise ValueError('Exact saved RGB512 PNG required')
            value=np.asarray(im).copy()
        if hashlib.sha256(value.tobytes()).hexdigest()!=pixel_sha:raise ValueError('Saved pixel hash differs')
        return value

    def array(self,receipt,shape):
        value=np.load(io.BytesIO(self.read(receipt)),allow_pickle=False)
        if value.shape!=shape or value.dtype.kind!='f' or not np.isfinite(value).all():
            raise ValueError('Finite floating observation shape required')
        return value


def audit_quality(source,suspect,recorded):
    validate_quality(recorded)
    actual=pixel_quality(source,suspect)
    for key,value in actual.items():
        if recorded.get(key)!=value:raise ValueError('Saved-pixel quality differs: '+key)
    return dict(pixel_metrics='recomputed_exactly',lpips='retained_model_observation')


def audit_enrollment(source_rgb8,images,arrays,cap,artifacts,*,layout='native'):
    """Reconstruct saved controls and RGB8 quality cap, without decoding a model."""
    from m1_blind_noise import rgb8 as quantize
    from m1_phase_residual import cap as apply_cap
    if set(images)!={'C0-source','C0-reconstruction','C1'} or set(arrays)!={'reference','decoded','residual','surrogate'}:
        raise ValueError('Exact enrollment control/stage inventory required')
    shape=(1,3,512,512) if layout=='native' else (512,512,3)
    if layout not in ('native','generated-hwc-float64'):raise ValueError('Explicit stage layout required')
    values={name:artifacts.array(receipt,shape) for name,receipt in arrays.items()}
    if layout=='native':values={name:x[0].transpose(1,2,0).astype(np.float64) for name,x in values.items()}
    expected_residual=(values['decoded'].astype(np.float32)-values['reference'].astype(np.float32)).astype(np.float64)
    if not np.array_equal(values['residual'],expected_residual):raise ValueError('Saved decoded residual algebra differs')
    marked,expected_cap=apply_cap(source_rgb8,values['residual'])
    if expected_cap!=cap:raise ValueError('Independent RGB8 quality cap differs')
    expected={'C0-source':source_rgb8,'C0-reconstruction':quantize(values['reference']),'C1':marked}
    for name,item in images.items():
        actual=artifacts.image(item['image'],item['rgb8_sha256'])
        if not np.array_equal(actual,expected[name]):raise ValueError('Enrollment control pixels differ: '+name)
    return dict(schema=VERSION,controls=list(expected),cap='recomputed_exactly',
        decoder_outputs='retained_model_observations',checkpoint_lineage='REQUIRED_UPSTREAM')


def audit_candidate_image(row,artifacts,*,source_rgb8,matched_clean_rgb8,queries=None):
    if row.get('outcome')!='completed':raise ValueError('Completed image required')
    rgb=artifacts.image(row['image'],row['rgb8_sha256'])
    if row.get('safety')!={'checker':'pinned SD1.5 FP16','nsfw':False}:
        raise ValueError('Successful pinned safety receipt required')
    audit_quality(source_rgb8,rgb,row['quality_vs_source'])
    audit_quality(matched_clean_rgb8,rgb,row['quality_vs_same_arm_clean'])
    E=artifacts.array(row['reader_arrays']['E'],(512,))
    z=artifacts.array(row['reader_arrays']['z'],(16384,))
    H=row['suspect_H']
    if type(H) is not int or not 0<=H<2**32:raise ValueError('Exact32bit pHash required')
    if not np.array_equal(E,np.asarray(row['suspect_E'],dtype=np.float64)):
        raise ValueError('Feature list/array differs')
    checked=[]
    for query in row['queries'] if queries is None else queries:
        if query.get('outcome')!='completed' or query.get('upstream_image_id')!=row['id']:
            raise ValueError('Completed query image identity differs')
        if query.get('upstream_image')!=row['image'] or query.get('upstream_rgb8_sha256')!=row['rgb8_sha256']:
            raise ValueError('Query image receipt differs')
        for key in ('reader_arrays','suspect_H','suspect_E'):
            if key in query and query[key]!=row[key]:raise ValueError('Query readout observation differs')
        if query['decision']!=core.scores(z,E,H,query['owner']):
            raise ValueError('Independent candidate score algebra differs')
        checked.append(query.get('id'))
    return dict(schema=VERSION,image_id=row['id'],verified_queries=checked,
        pixels='verified',quality='PSNR/SSIM recomputed; LPIPS retained',
        model_observations='CLIP/VAE/safety retained, not re-inferred',
        authority='REQUIRED_UPSTREAM',run_and_recovery_identity='REQUIRED_UPSTREAM')
