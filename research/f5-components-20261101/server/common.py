"""Shared offline planning and future execution checks; stdlib on import.

No function grants spending authority. --execute is for a later explicitly
approved server invocation; this research session runs only plan/logic tests.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RD = ROOT / 'research/f5-components-20261101'
sys.path[:0] = [str(ROOT / 'scripts'), str(RD / 'analysis')]
S60 = (30,72,73,89,127,165,309,370,436,450,459,471,508,529,544,599,626,629,636,673,
       693,715,723,790,853,902,908,913,960,1180,1295,1323,1330,1332,1355,1359,1397,
       1398,1404,1408,1464,1507,1522,1536,1548,1596,1637,1639,1647,1655,1670,1682,
       1712,1720,1737,1774,1777,1779,1785,1786)
S12, SEEDS = S60[:12], (12,13,14)
ALPHA, BETA = 'qim-pilot-owner-alpha', 'qim-pilot-owner-beta'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def text_digest(path):
    return hashlib.sha256(Path(path).read_text(encoding='utf-8').encode()).hexdigest()

def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    temp.replace(path)

def split(source):
    return 'DESIGN' if S60.index(source) % 2 == 0 else 'EVALUATE'

def load_config():
    config = read(ROOT / 'research/encoder-transfer-20261019/stage2b-config.json')
    if config['data_split'] != 'development' or tuple(config['seeds']) != SEEDS:
        raise ValueError('Frozen development configuration differs')
    for field in ('sources', 'profile', 'asset_plan'):
        path = ROOT / config[field+'_file']
        if text_digest(path) != config[field+'_sha256']:
            raise ValueError('Frozen text identity differs: '+field)
    sources = read(ROOT / config['sources_file'])
    if tuple(sorted(s['source_id'] for s in sources['sources'])) != S60:
        raise ValueError('S60 identities differ from original development source list')
    if config['f5'] != dict(psnr_db=52., steps=150, target_margin=4., mask_power=0.,
                           band=[4,32], whitening=1., refine_rounds=1, binding='soft', semantic_views=7):
        raise ValueError('Frozen F5 r2 configuration differs')
    return config

def journal_rows(path):
    """Latest physical row per exact id; no repair, filtering or silent retry."""
    rows = {}
    with Path(path).open('r', encoding='utf-8') as f:
        for line_no, line in enumerate(f, 1):
            if not line.endswith('\n'):
                raise ValueError(f'Torn journal tail: {path}:{line_no}')
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get('id'), str):
                raise ValueError(f'Journal row lacks exact id: {path}:{line_no}')
            rows[row['id']] = row
    return rows

def native_rows(stage2a, stage2b):
    return {**journal_rows(Path(stage2a)/'rows.jsonl'), **journal_rows(Path(stage2b)/'rows.jsonl')}

def clean_inputs(stage2a, stage2b, ids, arms):
    rows, result = native_rows(stage2a, stage2b), {}
    roots = {'stage2a-full': Path(stage2a).resolve(), 'stage2b-full': Path(stage2b).resolve()}
    if not set(ids) <= set(S60) or not set(arms) <= {'unmarked','f5-r2','v5-r3','vine-r'}:
        raise ValueError('Only fixed development inputs allowed')
    for source in ids:
        for arm in arms:
            rid = f'clean:{source}:{arm}:None:None'
            row = rows.get(rid)
            if row is None or row.get('status') != 'ok' or not row.get('output'):
                raise ValueError('Missing successful frozen clean input: '+rid)
            if row.get('source_id') != source or row.get('arm') != arm or row.get('channel') != 'clean':
                raise ValueError('Clean row identities disagree: '+rid)
            parts = PurePosixPath(row['output']['path'].replace('\\','/')).parts
            names = [name for name in roots if name in parts]
            if len(names) != 1 or parts[-2] != 'images':
                raise ValueError('Unknown original image root: '+rid)
            root = roots[names[0]]
            path = (root/'images'/parts[-1]).resolve()
            if not path.is_relative_to(root/'images') or digest(path) != row['output']['sha256']:
                raise ValueError('Saved clean input hash/path mismatch: '+rid)
            result[(source, arm)] = {**row, 'local_path': str(path)}
    return result

def reader_fields(raw, ep):
    from gate2_reader import endpoints
    import revised_watermark_v5 as v5
    result = endpoints(raw, ep)
    s, i = raw['semantic'], raw['instance']
    td, tiq = v5._threshold(1e-6/4,2**32), v5._threshold(1e-6/4,2**64)
    result.update(O_Q=bool((s['decoded_score'] >= td and s['content_match']) or
                          ((i['decoded_score'] >= tiq or i['recomputed_score'] >= td) and i['content_match'])),
                  sf=bool(s['found']), **{'if': bool(i['found'])},
                  io=bool(i['found'] and i['content_match']), H=ep.get('H'))
    return result

def add_execution_args(parser):
    parser.add_argument('--execute', action='store_true')
    for name in ('assets','stage2a','stage2b','out','instance-start'):
        parser.add_argument('--'+name)
    for name in ('hourly','max-hours','max-usd'):
        parser.add_argument('--'+name, type=float)

def validate_args(args):
    for field in ('assets','stage2a','stage2b','out','instance_start','hourly','max_hours','max_usd'):
        if getattr(args,field,None) is None:
            raise ValueError('Future --execute requires --'+field.replace('_','-'))
    for field in ('hourly','max_hours','max_usd'):
        value = getattr(args,field)
        if not math.isfinite(value) or value <= 0:
            raise ValueError('Positive finite actual paid value required: '+field)
    if os.environ.get('CUDA_VISIBLE_DEVICES') in ('-1',''):
        raise RuntimeError('CUDA is hidden; do not change this session guard to execute')
    roots = [Path(getattr(args,f)).resolve() for f in ('assets','stage2a','stage2b')]
    if any(not p.is_dir() for p in roots):
        raise ValueError('Pre-existing staged assets and both retained run directories required')
    out = Path(args.out).resolve()
    if any(out == p or out.is_relative_to(p) or p.is_relative_to(out) for p in roots):
        raise ValueError('Output must be separate from all retained inputs/assets')
    if out == ROOT or not out.is_relative_to(RD):
        # Future server output may live outside checkout; inside checkout only RD is allowed.
        if out.is_relative_to(ROOT):
            raise ValueError('Output inside repository must be within this research directory')

def verify_assets(assets, config, queue, budget):
    """Read-only pinned checks. Never invoke historical preparation/download code."""
    import three_threat_models as models
    from encoder_transfer_assets import verify_ready
    assets = Path(assets)
    sources = read(ROOT/config['sources_file'])
    verify_ready(assets,config,sources)
    models.verify_assets(assets/'a6', ROOT/'research/a6-candidate-model-assets.json')
    plan = read(ROOT/config['asset_plan_file'])
    prefixes = ('sdxl/', 'vine/decoder/') if queue == 'Q-RES' else ('sdxl/', 'kandinsky3/')
    selected = [x for x in plan['files'] if x['path'].startswith(prefixes)]
    if not all(any(x['path'].startswith(p) for x in selected) for p in prefixes):
        raise ValueError('Required asset family absent from frozen plan')
    for entry in selected:
        budget.check()
        path = (assets/entry['path']).resolve()
        if not path.is_relative_to(assets.resolve()) or path.stat().st_size != entry['size_bytes'] or digest(path) != entry['sha256']:
            raise ValueError('Pinned asset identity differs: '+entry['path'])
    if queue == 'Q-RES':
        repo = assets/'vine/source'
        head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
        if head != plan['vine_revision']:
            raise ValueError('VINE source revision differs')
        # Decoder code must be pristine; original encoder path patches are irrelevant here.
        changed = subprocess.check_output(['git','diff','HEAD','--','vine/src/stega_encoder_decoder.py'],cwd=repo,text=True)
        if changed:
            raise ValueError('VINE decoder source modified')
    versions = {name: importlib.metadata.version(name) for name in config['packages']}
    if versions != config['packages']:
        raise ValueError('Runtime versions differ from frozen package pins')
    return versions

def execution_context(args, queue):
    validate_args(args)
    config = load_config()
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
    import three_threat_models as models
    models.block_network()
    from encoder_transfer_runtime import Budget
    budget = Budget(args.instance_start, args.hourly, reserve_seconds=1800,
                    max_hours=args.max_hours, max_usd=args.max_usd)
    budget.check()
    verify_assets(args.assets,config,queue,budget)
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('Future server execution requires approved CUDA server')
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    return config, budget

def provenance(queue):
    paths = [ROOT/'scripts'/name for name in ('encoder_transfer_runtime.py','encoder_transfer_test.py',
             'f5_latent_codec.py','revised_watermark_v5.py','three_threat_models.py','journal_vae_probe.py')]
    paths += [RD/'server/common.py',RD/'server'/('q_res.py' if queue=='Q-RES' else 'q_stage.py'),
              RD/'analysis/gate2_reader.py']
    return dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                normalized_code_sha256={p.relative_to(ROOT).as_posix():text_digest(p) for p in paths},
                data_split='development', human_visibility='MISSING', execution_approval='separate user decision required')
