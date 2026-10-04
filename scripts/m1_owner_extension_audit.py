"""Fixed CPU owner-domain parity and geometry audit; no model or image access."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import types
import numpy as np
import m1_blind_noise_core as core

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
REFERENCE_COMMIT = 'fe02a466b5ba33f7a9fd7d5a4df0080098defaf2'
REFERENCE_SHA = 'df3e7140ee910519a1f57d8ea564d55636671c7404ca574fd40695e8514bccef'
VERSION = 'm1-owner-extension-audit-v1'
DOMAINS = ('coordinates', 'semantic-columns', 'instance-pre-signs', 'instance-rows',
           'semantic-row-signs', 'instance-row-signs')
CONFIG = dict(schema=VERSION, descriptor_pairs=32, descriptor_seed=0, latent_seed=1,
              reference_commit=REFERENCE_COMMIT, reference_sha256=REFERENCE_SHA,
              threshold=4., geometry_tolerance=1e-12, run_seconds_cap=300,
              artifact_budget_bytes=50*1024**2, data_split='synthetic-and-retained-development')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(value):
    if isinstance(value, np.ndarray):
        a = np.ascontiguousarray(value)
        return dict(dtype=a.dtype.str, shape=list(a.shape), sha256=hashlib.sha256(a.tobytes()).hexdigest())
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [normalize(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def digest(value):
    return hashlib.sha256(json.dumps(normalize(value), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def compare_exact(left, right, label):
    if isinstance(left, np.ndarray):
        if not isinstance(right, np.ndarray) or left.dtype != right.dtype or left.shape != right.shape or not np.array_equal(left, right):
            raise ValueError(label + ': array differs')
    elif isinstance(left, dict):
        if not isinstance(right, dict) or left.keys() != right.keys():
            raise ValueError(label + ': keys differ')
        for key in left:
            compare_exact(left[key], right[key], label + '/' + key)
    elif isinstance(left, (tuple, list)):
        if type(left) is not type(right) or len(left) != len(right):
            raise ValueError(label + ': sequence differs')
        for i, (a, b) in enumerate(zip(left, right)):
            compare_exact(a, b, label + '/' + str(i))
    elif type(left) is not type(right) or left != right:
        raise ValueError(label + ': scalar differs')


def fixtures():
    rng = np.random.Generator(np.random.PCG64(0))
    latent_rng = np.random.Generator(np.random.PCG64(1))
    for _ in range(32):
        e, e2 = rng.standard_normal((2, 512))
        e /= np.linalg.norm(e); e2 /= np.linalg.norm(e2)
        h, h2 = [int(v) for v in rng.integers(0, 2**32, size=2, dtype=np.uint64)]
        yield e, h, e2, h2, latent_rng.standard_normal(16384)


def load_reference():
    raw = subprocess.check_output(['git', 'show', REFERENCE_COMMIT + ':scripts/m1_blind_noise_core.py'], cwd=ROOT)
    if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA:
        raise ValueError('Immutable reference core bytes differ')
    module = types.ModuleType('_m1_verified_legacy_owner_core')
    sys.modules[module.__name__] = module
    exec(compile(raw, REFERENCE_COMMIT + ':m1_blind_noise_core.py', 'exec'), module.__dict__)
    return module, raw


def geometry(e, h, e2, h2, owner, parts, diag):
    other = core.template(e2, h2, owner)
    if set(parts['coords_s']) & set(parts['coords_i']) or len(set(parts['coords_s']) | set(parts['coords_i'])) != core.N:
        raise ValueError('Coordinates do not form disjoint complete partition')
    checks = [(np.linalg.norm(parts['v_s']), 1.), (np.linalg.norm(parts['v_i']), 1.),
              (np.sqrt(np.mean(parts['T']**2)), 1.),
              (parts['v_s'] @ other['v_s'], e @ e2),
              (diag['kernel_exact'], float(e @ e2) * (1-2*(h ^ h2).bit_count()/32))]
    maps = core._owner_maps(owner)
    # Independent finite-population variance formula, including N/(N-1).
    b = np.array([2*((h >> (31-k)) & 1)-1 for k in range(32)])/np.sqrt(32)
    b2 = np.array([2*((h2 >> (31-k)) & 1)-1 for k in range(32)])/np.sqrt(32)
    u = core.fwht(maps.pre_signs_i * np.outer(e, b).ravel())
    w = core.fwht(maps.pre_signs_i * np.outer(e2, b2).ravel())
    factor = core.N**2 * (1-core.M/core.N) / core.M
    for field, population in (('variance_norm_1', u*u), ('variance_norm_2', w*w), ('variance_inner', u*w)):
        checks.append((diag[field], factor * float(np.var(population, ddof=1))))
    if not all(np.isfinite(a) and np.isfinite(b) and abs(a-b) <= 1e-12 for a, b in checks):
        raise ValueError('Algebraic geometry or variance identity failed')
    if diag['normalization_error_bound'] is not None and diag['normalized_error'] > diag['normalization_error_bound'] + 1e-12:
        raise ValueError('Normalization bound violated')


def audit(output, development_run):
    output = Path(output).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):
        raise ValueError('Fresh MAIN development output required')
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    record = dict(schema=VERSION, data_split='synthetic-and-retained-development', command=sys.argv,
                  config=CONFIG, seeds=[0, 1],
                  outcome='started', compatibility_passed=False, errors=[], duration_seconds=0.,
                  old_source_sha256=REFERENCE_SHA, new_source_sha256=sha(ROOT/'scripts/m1_blind_noise_core.py'))
    def write(name, value):
        (output/name).write_text(json.dumps(normalize(value), indent=2, allow_nan=False)+'\n', encoding='utf-8')
    def check():
        if time.monotonic()-started > CONFIG['run_seconds_cap']:
            raise RuntimeError('CPU audit time cap')
        if sum(p.stat().st_size for p in output.iterdir() if p.is_file()) > CONFIG['artifact_budget_bytes']:
            raise RuntimeError('Audit artifact budget')
    write('run.json', record)
    try:
        files = ['scripts/m1_owner_extension_audit.py', 'scripts/m1_blind_noise_core.py',
                 'scripts/m1_owner_interface.py', 'scripts/a4_protocol_reference.py',
                 'research/m1-owner-seed-extension-design.md', 'research/m1-owner-extension-audit-v1.json']
        record['commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        record['committed_files'] = {}
        for name in files:
            committed = subprocess.check_output(['git', 'rev-parse', 'HEAD:'+name], cwd=ROOT, text=True).strip()
            working = subprocess.check_output(['git','hash-object','--path='+name,str(ROOT/name)],cwd=ROOT,text=True).strip()
            if committed != working:
                raise ValueError('Uncommitted dependency: '+name)
            record['committed_files'][name] = sha(ROOT/name)
        if json.loads((ROOT/'research/m1-owner-extension-audit-v1.json').read_text()) != CONFIG:
            raise ValueError('Frozen audit manifest differs')
        write('manifest.json', CONFIG)
        record['environment'] = dict(python=sys.version, numpy=np.__version__)
        if tuple(core.ACCEPTED_OWNERS) != tuple(core.OWNERS) + tuple(core.A4_OWNERS) or len(core.A4_OWNERS) != 16:
            raise ValueError('Exact20-owner extension required')
        old, raw = load_reference()
        (output/'legacy-core.py').write_bytes(raw)
        fixtures_list = list(fixtures())
        parity = []
        for repetition in range(2):
            if repetition:
                old._owner_maps.cache_clear(); core._owner_maps.cache_clear()
                for owner in core.A4_OWNERS:
                    core.template(fixtures_list[0][0], fixtures_list[0][1], owner)
            for j, (e, h, e2, h2, z) in enumerate(fixtures_list):
                check()
                for owner in core.OWNERS:
                    a = dict(template=old.template(e, h, owner), diagnostic=old.projection_diagnostic(e,h,e2,h2,owner), scores=old.scores(z,e,h,owner))
                    b = dict(template=core.template(e,h,owner), diagnostic=core.projection_diagnostic(e,h,e2,h2,owner), scores=core.scores(z,e,h,owner))
                    compare_exact(a,b,f'parity/{repetition}/{j}/{owner}')
                    parity.append(dict(repetition=repetition, fixture=j, owner=owner, exact=True, old_digest=digest(a), new_digest=digest(b)))
        write('legacy-parity.json', parity)
        map_receipts = []
        for owner in core.ACCEPTED_OWNERS:
            def frame(v):
                b=v.encode('utf-8'); return len(b).to_bytes(4,'big')+b
            for domain in DOMAINS:
                if core._prefix(domain, owner) != frame('m1-blind-noise-template-v1')+frame(domain)+frame(owner):
                    raise ValueError('Map prefix framing differs')
            maps = vars(core._owner_maps(owner))
            map_receipts.append(dict(owner=owner, map_sha256=digest(maps), arrays=normalize(maps)))
        if len({r['map_sha256'] for r in map_receipts}) != 20:
            raise ValueError('Distinct public owners have aliased maps')
        write('maps.json', map_receipts)
        diagnostics=[]; alignment=[]; null=[]
        for j,(e,h,e2,h2,z) in enumerate(fixtures_list):
            check()
            for donor in core.A4_OWNERS:
                parts=core.template(e,h,donor); diag=core.projection_diagnostic(e,h,e2,h2,donor)
                geometry(e,h,e2,h2,donor,parts,diag)
                diagnostics.append(dict(fixture=j,owner=donor,**diag))
                null.append(dict(fixture=j,owner=donor,**core.scores(z,e,h,donor)))
                for owner in core.A4_OWNERS:
                    scores=core.scores(parts['T'],e,h,owner)
                    if scores['state']=='invalid_measurement' or (owner==donor and scores['state']!='both_match'):
                        raise ValueError('Invalid alignment or failed exact-template diagonal')
                    alignment.append(dict(fixture=j,donor=donor,owner=owner,diagonal=donor==owner,**scores))
        write('projection-diagnostics.json',diagnostics);write('alignment.json',alignment);write('null.json',null)
        maxima=[]
        for j in range(32):
            for donor in core.A4_OWNERS:
                cross_row=[r for r in alignment if r['fixture']==j and r['donor']==donor and not r['diagonal']]
                maxima.append(dict(fixture=j,donor=donor,**{k:max(r[k] for r in cross_row) for k in ('s','i')}))
        write('alignment-row-maxima.json',maxima)
        write('null-owner-extrema.json',[
            dict(owner=owner,**{k:[min(r[k] for r in null if r['owner']==owner),max(r[k] for r in null if r['owner']==owner)] for k in ('s','i')})
            for owner in core.A4_OWNERS])
        # Direct old/new replay on retained model arrays, never model/pixel inference.
        base=Path(development_run).resolve()
        if not base.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):
            raise ValueError('Retained development run required')
        data=json.loads((base/'run.json').read_text())
        if data.get('data_split')!='development' or data.get('outcome')!='completed':
            raise ValueError('Completed development receipt required')
        replay=[]
        for row in data['conditions']:
            receipt=row['terminal_reader_latent']; path=Path(receipt['path']).resolve()
            if not path.is_relative_to(base) or sha(path)!=receipt['sha256']:
                raise ValueError('Development latent receipt differs')
            z=np.load(path,allow_pickle=False)
            for owner in core.OWNERS:
                a=old.scores(z,row['suspect_E'],row['suspect_H'],owner)
                b=core.scores(z,row['suspect_E'],row['suspect_H'],owner)
                compare_exact(a,b,'development/'+row['id']+'/'+owner)
                compare_exact(a,row['owner_decisions'][owner],'recorded-development/'+row['id']+'/'+owner)
                replay.append(dict(id=row['id'],owner=owner,exact=True,old_digest=digest(a),new_digest=digest(b)))
        write('development-replay.json',replay)
        check()
        record['development_input']=dict(path=str(base/'run.json'),sha256=sha(base/'run.json'))
        diagonal=[r for r in alignment if r['diagonal']]; cross=[r for r in alignment if not r['diagonal']]
        record['summary']=dict(legacy_cells_per_pass=128,legacy_passes=2,distinct_maps=20,
                              projection_cells=len(diagnostics),alignment_cells=len(alignment),null_cells=len(null),
                              development_replayed_queries=len(replay),
                              diagonal={k:[min(r[k] for r in diagonal),max(r[k] for r in diagonal)] for k in ('s','i')},
                              cross_exceedances={k:sum(r['flags'][k] for r in cross) for k in ('s','i')},
                              null_exceedances={k:sum(r['flags'][k] for r in null) for k in ('s','i')},
                              cross_both=sum(r['state']=='both_match' for r in cross),
                              null_both=sum(r['state']=='both_match' for r in null),
                              null_invalid=sum(r['state']=='invalid_measurement' for r in null))
        if record['summary']['null_invalid']:
            raise ValueError('Invalid synthetic null observation')
        record['outcome']='completed'
        record['compatibility_passed']=True
        record['interpretation']='Exact compatibility and finite synthetic geometry only; no photograph FPR or authentication inference; no owner/threshold selection.'
    except Exception as exc:
        record['outcome']='failed';record['errors'].append(repr(exc))
    finally:
        record['duration_seconds']=time.monotonic()-started
        record['outputs']={p.name:sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'}
        write('run.json',record)
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--development-run',type=Path,required=True)
    args=p.parse_args(); result=audit(args.output_dir,args.development_run)
    print(json.dumps({k:result.get(k) for k in ('outcome','duration_seconds','summary','errors')}))
    raise SystemExit(0 if result['outcome']=='completed' else 1)
