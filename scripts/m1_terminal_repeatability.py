"""Deterministic A-C execution and independent-process prefix verification.

No model loads on import. --probe runs only a10-update measurement prefix;
--compare is CPU-only and never promotes an incomplete scientific pilot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

VERSION = 'ac-deterministic-execution-v1'
PROBE_VERSION = 'ac-gradient-prefix-v1'
COMPARISON_VERSION = 'ac-gradient-prefix-comparison-v1'
PREFIX_STEPS = 10
WORKSPACE = ':4096:8'


def configure():
    """Must run before CUDA initialization; nondeterministic ops fail closed."""
    import torch
    if torch.cuda.is_initialized():
        raise RuntimeError('Deterministic execution must be configured before CUDA initialization')
    current = os.environ.get('CUBLAS_WORKSPACE_CONFIG')
    if current not in (None, WORKSPACE):
        raise ValueError('Conflicting CUBLAS_WORKSPACE_CONFIG; no silent override')
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = WORKSPACE
    torch.use_deterministic_algorithms(True, warn_only=False)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cuda.matmul.allow_tf32 = False
    return dict(version=VERSION, deterministic_algorithms=True, warn_only=False,
                cudnn_deterministic=True, cudnn_benchmark=False,
                cudnn_allow_tf32=False, matmul_allow_tf32=False,
                cublas_workspace_config=WORKSPACE,
                attention_backend='unchanged; deterministic API enforced',
                fill_uninitialized_memory=bool(torch.utils.deterministic.fill_uninitialized_memory))


def scientific_files(committed_files):
    """A report-only commit is irrelevant; executed bytes/configs never are."""
    return {k: v for k, v in committed_files.items() if not str(k).lower().endswith('.md')}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked(receipt):
    path = Path(receipt['path'])
    if not path.is_file() or sha(path) != receipt['sha256']:
        raise ValueError('Missing or changed probe artifact')
    return path


def compare_records(left, right):
    """Strict tensor/gradient equality, without a data-fitted tolerance."""
    import numpy as np
    import torch
    import m1_terminal_continuous as method
    if left.get('process_id') == right.get('process_id'):
        raise ValueError('Two independently launched probe processes required')
    fields = ('schema','data_split','config','manifest_sha256','execution_variant',
              'deterministic_execution','scientific_files','environment','assets',
              'device_identity','lpips_learned_sha256','reconstruction_run_sha256')
    for value in (left, right):
        if value.get('run_kind') != PROBE_VERSION or value.get('outcome') != 'probe_completed':
            raise ValueError('Completed prefix probe required')
        if value.get('repeatability_prefix_updates') != PREFIX_STEPS or value.get('conditions') != [] or value.get('gate') is not None:
            raise ValueError('Probe must not contain scientific enrollment conditions/gate')
        if value.get('execution_variant') != VERSION or value.get('deterministic_execution',{}).get('deterministic_algorithms') is not True:
            raise ValueError('Deterministic execution receipt required')
        if len(value.get('case_events', [])) != 1:
            raise ValueError('Single-source prefix required')
    for field in fields:
        if left.get(field) != right.get(field) or field not in left:
            raise ValueError('Probe identity mismatch: ' + field)
    a, b = left['case_events'][0], right['case_events'][0]
    for value in (a,b):
        if value.get('source_id') != 1675 or value.get('outcome') != 'probe_completed':
            raise ValueError('Fixed source1675 required')
        checked(value['source'])
    for field in ('initialization','source_E','source_H','probe_trajectory'):
        if a.get(field) != b.get(field) or field not in a:
            raise ValueError('Fresh prefix differs: ' + field)
    if a['source']['rgb8_sha256'] != b['source']['rgb8_sha256'] or a['source']['sha256'] != b['source']['sha256']:
        raise ValueError('Source bytes differ')
    for case in (a,b):
        if [v['step'] for v in case.get('probe_trajectory', [])] != list(range(1,PREFIX_STEPS+1)):
            raise ValueError('All ten before/after-update trajectory measurements required')
        if [v['step'] for v in case.get('probe_gradients', [])] != list(range(1,PREFIX_STEPS+1)):
            raise ValueError('All ten full gradient arrays required')
        if [v['step'] for v in case.get('checkpoints', [])] != [0,PREFIX_STEPS]:
            raise ValueError('Fresh step0/10 checkpoints required')
    gradients=[]
    for x,y in zip(a['probe_gradients'],b['probe_gradients']):
        gx=np.load(checked(x),allow_pickle=False);gy=np.load(checked(y),allow_pickle=False)
        if gx.shape != (1,4,64,64) or gx.dtype != np.float32 or gy.dtype != np.float32 or not np.isfinite(gx).all() or not np.isfinite(gy).all() or not np.any(gx) or not np.array_equal(gx,gy):
            raise ValueError('Fresh full gradient arrays differ')
        gradients.append(dict(step=x['step'],sha256=x['sha256'],exact=True))
    for x,y in zip(a['checkpoints'],b['checkpoints']):
        cx=torch.load(checked(x),map_location='cpu',weights_only=False)
        cy=torch.load(checked(y),map_location='cpu',weights_only=False)
        for field in ('u','optimizer','rng','step'):
            if not method.exact_tree_equal(cx[field],cy[field]):
                raise ValueError('Fresh checkpoint differs: ' + field)
    if set(a.get('probe_arrays',{})) != {'reference','decoded','surrogate'} or set(b.get('probe_arrays',{})) != set(a['probe_arrays']):
        raise ValueError('All diagnostic forward arrays required')
    for field in a['probe_arrays']:
        x=np.load(checked(a['probe_arrays'][field]),allow_pickle=False)
        y=np.load(checked(b['probe_arrays'][field]),allow_pickle=False)
        if not np.isfinite(x).all() or not np.isfinite(y).all() or not np.array_equal(x,y):
            raise ValueError('Fresh forward array differs: ' + field)
    return dict(passed=True,gradient_steps=gradients,checkpoint_steps=[0,PREFIX_STEPS],
                source_id=1675,full_scientific_steps=100,measured_prefix_steps=PREFIX_STEPS,
                full100_step_repeatability_tested=False,
                old_nondeterministic_replay_required=False,
                scientific_files=left['scientific_files'],manifest_sha256=left['manifest_sha256'],
                deterministic_execution=left['deterministic_execution'],environment=left['environment'],
                device_identity=left['device_identity'])


def compare(left_dir,right_dir,output):
    import m1_terminal_continuous as method
    output=Path(output).resolve()
    if not output.is_relative_to((method.MAIN/'.thesis-build/dev-runs').resolve()):
        raise ValueError('Fresh MAIN development output required')
    paths=[Path(p).resolve()/'run.json' for p in (left_dir,right_dir)]
    if paths[0]==paths[1]:raise ValueError('Distinct probe directories required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    record=dict(schema=COMPARISON_VERSION,data_split='development',command=sys.argv,
                outcome='started',input_runs=[dict(path=str(p),sha256=sha(p)) for p in paths],
                commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=method.ROOT,text=True).strip())
    try:
        values=[json.loads(p.read_text()) for p in paths]
        record['comparison']=compare_records(*values)
        record['outcome']='completed'
    except Exception as error:
        record.update(outcome='failed',error=repr(error))
    record['duration_seconds']=time.monotonic()-started
    method.util.write(output/'run.json',record)
    return 0 if record['outcome']=='completed' else 1


def require_receipt(path,committed_files,manifest_sha256):
    """Recheck both prefix artifacts; a forged/stale summary cannot unlock fitting."""
    path=Path(path).resolve();record=json.loads(path.read_text())
    if record.get('schema')!=COMPARISON_VERSION or record.get('data_split')!='development' or record.get('outcome')!='completed':
        raise ValueError('Passing independent-process repeatability receipt required')
    inputs=record.get('input_runs',[])
    if len(inputs)!=2 or inputs[0]['path']==inputs[1]['path']:
        raise ValueError('Two probe inputs required')
    values=[json.loads(checked(item).read_text()) for item in inputs]
    fresh=compare_records(*values)
    if fresh!=record.get('comparison'):
        raise ValueError('Repeatability comparison differs on revalidation')
    if fresh['scientific_files']!=scientific_files(committed_files) or fresh['manifest_sha256']!=manifest_sha256:
        raise ValueError('Probe scientific code/config bytes differ from current worker')
    return dict(path=str(path),sha256=sha(path),comparison=fresh)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--probe',action='store_true')
    group.add_argument('--compare',nargs=2,type=Path,metavar=('LEFT','RIGHT'))
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.compare:return compare(*args.compare,args.output_dir)
    if not args.manifest:parser.error('--probe requires --manifest')
    import m1_terminal_continuous as method
    return method.run(args.manifest,args.output_dir,probe_mode=True)


if __name__=='__main__':raise SystemExit(main())
