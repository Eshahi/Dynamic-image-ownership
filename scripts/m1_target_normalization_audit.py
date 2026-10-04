"""Exact CPU reproduction of the pinned CUDA scalar RGB8 normalization.

Audit-only: no model loading, CUDA operation, monkeypatch or checkpoint rewrite.
The arithmetic is selected by a declared runtime policy, never by matching a
checkpoint hash. Unknown execution policies fail closed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

VERSION='m1-cuda-rgb8-scalar-normalization-audit-v1'
POLICY={'torch_version':'2.12.1+cu130','cuda_version':'13.0','device':'cuda:0'}


def target_from_rgb8(rgb, runtime):
    """Return CPU FP32 NCHW RN32(RGB8 * RN32(1/255)) for the pinned runtime.

    The deployed CUDA tensor/scalar division was observed to implement this
    reciprocal multiplication. CPU tensor division instead rounds RGB8/255
    directly. The two operations are deliberately not treated as equivalent.
    """
    import numpy as np
    import torch
    if not isinstance(runtime,dict) or any(runtime.get(k)!=v for k,v in POLICY.items()):
        raise ValueError('Unvalidated normalization execution policy')
    if str(torch.__version__)!=POLICY['torch_version']:
        raise ValueError('CPU audit Torch build differs from normalization policy')
    if not isinstance(rgb,np.ndarray) or rgb.dtype!=np.uint8 or rgb.shape!=(512,512,3):
        raise ValueError('Canonical512 RGB8 required')
    x=torch.from_numpy(rgb.copy()).permute(2,0,1).unsqueeze(0).float()
    reciprocal=torch.tensor(1.0/255.0,dtype=torch.float32,device='cpu')
    return x*reciprocal


def diagnostic(directory):
    """Independently validate all sealed generated phase states, no GPU access.

    This focused proof does not replace the complete artifact/endpoint/lifecycle
    audit. It leaves every existing artifact and recorded failure unchanged.
    """
    import numpy as np
    import torch
    import m1_candidate_rehearsal_worker as worker
    import m1_source_initialization as init
    base=worker.destination(directory)
    path=base/'outputs/worker-run.json';record=worker.read(path)
    if record.get('generated_only') is not True or record.get('unit_index') not in (0,1):
        raise ValueError('Completed generated fixture only')
    if record.get('outcome') not in ('completed','prefix_completed'):
        raise ValueError('Completed generated computation required')
    source,_,receipt=worker.generated_source(record['unit_index'])
    if receipt!=record['source']:raise ValueError('Generated source receipt mismatch')
    target=target_from_rgb8(source,record['binding']['runtime'])
    division=torch.from_numpy(source.copy()).permute(2,0,1)[None].float()/255
    initializer=None;checks=[]
    for cp in record['checkpoints']:
        checkpoint=worker.destination(cp['path'])
        if not checkpoint.is_relative_to(base) or worker.file_sha(checkpoint)!=cp['sha256']:
            raise ValueError('Checkpoint containment/hash differs')
        payload=torch.load(checkpoint,map_location='cpu',weights_only=True)
        if payload['phase']!=cp['phase'] or payload['step']!=cp['step']:
            raise ValueError('Checkpoint receipt phase/step differs')
        worker.validate_phase_checkpoint(payload,record,target,initializer_payload=initializer)
        if payload['phase']=='initialization' and payload['step']==200:initializer=payload
        checks.append({'phase':cp['phase'],'step':cp['step'],'sha256':cp['sha256'],'exact_state_validation':True})
    if not checks:raise ValueError('No checkpoints')
    return {'schema':VERSION,'run_json_path':str(path),'run_json_sha256':worker.file_sha(path),
        'source_rgb8_sha256':receipt['rgb8_sha256'],'source_unique_byte_values':len(np.unique(source)),
        'policy':POLICY,'normalization':'RN32(float32(RGB8) * RN32(1/255)); NCHW CPU float32',
        'reciprocal_float32_bits_hex':f'{int(np.asarray(np.float32(1/255)).view(np.uint32)):08x}',
        'reproduced_target_sha256':init.digest(target),'cpu_direct_division_sha256':init.digest(division),
        'different_components':int((target!=division).sum()),'total_components':target.numel(),
        'maximum_abs_difference':float((target-division).abs().max()),
        'checks':checks,'all_checkpoint_states_valid':True,'full_artifact_audit_performed':False,
        'scientific_verdict':'NOT_EVIDENCE','cuda_initialized':torch.cuda.is_initialized()}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True)
    args=p.parse_args();print(json.dumps(diagnostic(args.directory),sort_keys=True,allow_nan=False))


if __name__=='__main__':main()
