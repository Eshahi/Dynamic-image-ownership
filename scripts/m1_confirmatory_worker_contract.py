"""Candidate-independent unit contract and generated-image adapter seam.

Scientific execution is unavailable. Metadata validation never opens sources.
The fixture child is for the existing owned-process rehearsal infrastructure.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import time
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from m1_confirmatory_harness import atomic, object_sha, file_sha, verify_initial_output
from m1_windows_job import OwnedJobProcess

SCHEMA = 'm1-worker-contract-v1'
CANDIDATES = {'UNRESOLVED', 'original-A', 'A-C'}
AXES = {'clean', 'T3', 'T4', 'T5'}
KEY = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z')
HASH = re.compile(r'[0-9a-f]{64}\Z')
REHEARSAL_ROOTS = (ROOT / '.thesis-build/rehearsal', Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/rehearsal'))

def fixture_destination(output):
    path = Path(output).resolve()
    if not any(path.is_relative_to(root.resolve()) for root in REHEARSAL_ROOTS):
        raise ValueError('Generated fixture outputs require rehearsal root')
    return path

FIXTURE_FIELDS = {'width', 'height', 'fail_phase', 'delay_seconds'}
UNIT_FIELDS = {'id', 'source_uid', 'group_id', 'method', 'axis', 'arm', 'owner', 'seed_uint64_hex', 'dependencies'}


def validate_plan(plan):
    """Validate metadata only. No raw path/annotation/model access is provided."""
    if not isinstance(plan, dict) or set(plan) != {'schema', 'mode', 'candidate', 'units'}:
        raise ValueError('Exact worker plan fields required')
    if plan['schema'] != SCHEMA or plan['mode'] not in ('synthetic-only', 'scientific') or plan['candidate'] not in CANDIDATES:
        raise ValueError('Unknown schema/mode/candidate')
    if plan['mode'] == 'synthetic-only' and plan['candidate'] != 'UNRESOLVED':
        raise ValueError('Fixture cannot select a scientific candidate')
    if plan['mode'] == 'scientific' and plan['candidate'] == 'UNRESOLVED':
        raise ValueError('Scientific metadata must name its eventual candidate')
    if not isinstance(plan['units'], list) or not 1 <= len(plan['units']) <= 10000:
        raise ValueError('Bounded nonempty unit list required')
    ids = set()
    for unit in plan['units']:
        if not isinstance(unit, dict) or set(unit) != UNIT_FIELDS:
            raise ValueError('Exact metadata-only unit fields required')
        if not isinstance(unit['id'], str) or not KEY.fullmatch(unit['id']) or unit['id'] in ids:
            raise ValueError('Invalid or duplicate condition ID')
        ids.add(unit['id'])
        for field in ('source_uid', 'group_id', 'owner'):
            if type(unit[field]) is not str or not unit[field] or '\x00' in unit[field]:
                raise ValueError('Missing source/group/claim identity')
        if type(unit['axis']) is not str or unit['axis'] not in AXES or unit['method'] not in ('candidate', 'v5') or unit['arm'] not in ('C0-source', 'C0', 'C1', 'sham'):
            raise ValueError('Unknown planned condition')
        if type(unit['seed_uint64_hex']) is not str or not re.fullmatch(r'[0-9a-f]{16}', unit['seed_uint64_hex']):
            raise ValueError('Exact uint64 seed hex required, never float')
        deps = unit['dependencies']
        if not isinstance(deps, list) or any(type(d) is not str for d in deps) or len(deps) != len(set(deps)):
            raise ValueError('Distinct dependency condition IDs required')
    by_id = {u['id']: u for u in plan['units']}
    visiting, done = set(), set()
    def visit(ident):
        if ident not in ids: raise ValueError('Undeclared dependency')
        if ident in visiting: raise ValueError('Cyclic dependency')
        if ident in done: return
        visiting.add(ident)
        for dep in by_id[ident]['dependencies']: visit(dep)
        visiting.remove(ident); done.add(ident)
    for ident in ids: visit(ident)
    object_sha(plan)  # rejects unsupported/nonfinite JSON without touching files
    return plan


def initial_inventory(plan):
    validate_plan(plan)
    return [dict(unit, outcome='planned', reason='not_attempted', unit_sha256=object_sha(unit),
                 artifacts=[], stages=[], human_visual_verdict=None) for unit in plan['units']]


def safe_artifact(output, relative):
    if type(relative) is not str or not relative or '\\' in relative:
        raise ValueError('Canonical relative artifact path required')
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] not in ('outputs', 'checkpoints', 'metrics', 'logs'):
        raise ValueError('Artifact path outside declared roots')
    resolved = (Path(output) / path).resolve()
    if not resolved.is_relative_to(Path(output).resolve()): raise ValueError('Artifact escapes through symlink')
    return resolved


def completed_receipts(row, unit, output):
    """An explicit completed claim must have intact uniquely-owned artifacts."""
    if row.get('unit_sha256') != object_sha(unit): raise ValueError('Unit identity differs')
    if any(row.get(k) != v for k, v in unit.items()): raise ValueError('Condition fields differ')
    if row.get('outcome') != 'completed': return False
    duration = row.get('duration_seconds')
    if type(duration) not in (int,float) or not math.isfinite(duration) or duration < 0:
        raise ValueError('Completed unit lacks finite duration')
    if not isinstance(row.get('stages'),list) or not row['stages'] or any(not isinstance(s,dict) or s.get('outcome')!='completed' for s in row['stages']):
        raise ValueError('Completed unit lacks completed stages')
    artifacts = row.get('artifacts')
    if not isinstance(artifacts, list) or not artifacts: raise ValueError('Completed unit lacks artifacts')
    seen = set()
    for receipt in artifacts:
        if not isinstance(receipt, dict) or set(receipt) != {'path', 'sha256', 'size_bytes'}:
            raise ValueError('Malformed artifact receipt')
        if receipt['path'] in seen: raise ValueError('Duplicate artifact receipt')
        seen.add(receipt['path'])
        if type(receipt['sha256']) is not str or not HASH.fullmatch(receipt['sha256']) or type(receipt['size_bytes']) is not int or receipt['size_bytes'] <= 0:
            raise ValueError('Malformed artifact hash/size')
        path = safe_artifact(output, receipt['path'])
        parts=Path(receipt['path']).parts
        if len(parts)<4 or parts[1:3]!=('units',unit['id']):
            raise ValueError('Artifact does not belong to expected condition namespace')
        if not path.is_file() or path.stat().st_size != receipt['size_bytes'] or file_sha(path) != receipt['sha256']:
            raise ValueError('Missing or corrupt artifact')
    return True


def reconcile(plan, observed, output):
    """Fixed denominator ledger; missing/invalid rows remain, never drop."""
    rows = {r['id']: r for r in initial_inventory(plan)}
    seen, artifact_owners = set(), {}
    for row in observed:
        ident = row.get('id')
        if ident not in rows or ident in seen: raise ValueError('Extra or duplicate result row')
        seen.add(ident)
        expected = next(u for u in plan['units'] if u['id'] == ident)
        try:
            complete = completed_receipts(row, expected, output)
            if row.get('outcome') not in ('completed', 'failed', 'missing', 'interrupted', 'timeout', 'planned'):
                raise ValueError('Unknown unit outcome')
            if not complete and (type(row.get('reason')) is not str or not row['reason']):
                raise ValueError('Noncompleted row requires reason')
            for receipt in row.get('artifacts', []):
                path = receipt['path']
                if path in artifact_owners: raise ValueError('Artifact reused by another condition')
                artifact_owners[path] = ident
            rows[ident] = row
        except (ValueError, TypeError, KeyError, OSError) as exc:
            rows[ident] = dict(rows[ident], outcome='failed', reason='receipt_validation: '+str(exc), observed=row)
    # Dependency status is checked on the final ledger, not observation order.
    changed=True
    while changed:
        changed=False
        for unit in plan['units']:
            row=rows[unit['id']]
            if row['outcome']=='completed' and any(rows[d]['outcome']!='completed' for d in unit['dependencies']):
                rows[unit['id']]=dict(row,outcome='failed',reason='dependency_not_completed');changed=True
    return [rows[u['id']] for u in plan['units']]


def validate_fixture(config):
    if not isinstance(config, dict) or set(config) != FIXTURE_FIELDS: raise ValueError('Exact generated fixture fields required')
    if any(type(config[k]) is not int or not 1 <= config[k] <= 512 for k in ('width','height')):
        raise ValueError('Fixture dimension1..512 required')
    if config['fail_phase'] not in (None, 'generate', 'save', 'finalize'): raise ValueError('Unknown injected failure phase')
    delay = config['delay_seconds']
    if type(delay) not in (int, float) or not math.isfinite(delay) or not 0 <= delay <= 1: raise ValueError('Bounded finite delay required')


def fixture_png(width, height, seed):
    """Generated RGB8 PNG, no source files or scientific carrier."""
    def chunk(tag, data):
        return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    pixels = bytes((seed + i*17 + (i//3)*7) & 255 for i in range(width*height*3))
    scan = b''.join(b'\0'+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    png = b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b'')
    return png, hashlib.sha256(pixels).hexdigest()


def execute_fixture(plan, ident, config, output):
    validate_plan(plan)
    # Reject scientific mode before creating directories or reading any paths.
    if plan['mode'] != 'synthetic-only' or plan['candidate'] != 'UNRESOLVED': raise ValueError('Scientific adapter/unlock unavailable')
    validate_fixture(config)
    matching = [u for u in plan['units'] if u['id'] == ident]
    if len(matching) != 1: raise ValueError('Unknown fixture condition')
    unit = matching[0]; row = next(r for r in initial_inventory(plan) if r['id'] == ident)
    started = time.monotonic(); directory = fixture_destination(output)
    row.update(outcome='started', reason=None, synthetic=True, scientific_verdict='NOT_EVIDENCE')
    record = safe_artifact(directory, f'outputs/unit-receipts/{ident}.json')
    record.parent.mkdir(parents=True, exist_ok=True)
    if record.exists(): raise ValueError('Fixture attempt overwrite refused')
    atomic(record,row)
    try:
        time.sleep(config['delay_seconds'])
        row['stages'].append(dict(stage='generate',outcome='started'))
        if config['fail_phase']=='generate': raise RuntimeError('Injected generate failure')
        png, raw_hash = fixture_png(config['width'],config['height'],int(unit['seed_uint64_hex'],16))
        row['stages'][-1].update(outcome='completed',rgb8_sha256=raw_hash)
        row['stages'].append(dict(stage='save',outcome='started'))
        if config['fail_phase']=='save': raise RuntimeError('Injected save failure')
        relative=f'outputs/units/{ident}/image.png'; path=safe_artifact(directory,relative)
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as handle: handle.write(png)
        row['artifacts'].append(dict(path=relative,sha256=file_sha(path),size_bytes=path.stat().st_size))
        row['stages'][-1]['outcome']='completed'; atomic(record,row)
        if config['fail_phase']=='finalize': raise RuntimeError('Injected finalize failure')
        row.update(outcome='completed', reason=None)
    except Exception as exc:
        row.update(outcome='failed',reason=str(exc),error_type=type(exc).__name__)
        if row['stages'] and row['stages'][-1]['outcome']=='started': row['stages'][-1]['outcome']='failed'
    finally:
        row['duration_seconds']=time.monotonic()-started; atomic(record,row)
    return row


def launch_fixture(plan, ident, config, output, *, timeout_seconds=2, ownership_callback=None):
    """Owned-child seam, not a second shard lifecycle or scientific runner."""
    validate_plan(plan)
    if plan['mode']!='synthetic-only': raise ValueError('Scientific adapter/unlock unavailable')
    validate_fixture(config)
    if ident not in {u['id'] for u in plan['units']}:raise ValueError('Unknown fixture condition')
    if type(timeout_seconds) not in (int,float) or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 60:
        raise ValueError('Bounded timeout required')
    output=fixture_destination(output)
    # Only generated JSON/PNG is read/written; no scientific source access.
    output.mkdir(parents=True,exist_ok=True)
    inventory_path=output/'checkpoints/fixture-inventory.json'
    if inventory_path.exists():raise ValueError('Fixture ledger overwrite refused')
    atomic(inventory_path,initial_inventory(plan))
    request=output/'fixture-request.json'
    payload=dict(plan=plan,unit_id=ident,fixture=config)
    with request.open('x',encoding='utf-8') as handle:json.dump(payload,handle,allow_nan=False)
    log=output/'fixture-child.log'
    ownership=[]
    def receipt(value):
        ownership.append(value);atomic(output/'fixture-ownership.json',ownership)
        if ownership_callback:ownership_callback(value)
    command=[sys.executable,str(Path(__file__).resolve()),'--fixture-request',str(request),'--request-sha256',file_sha(request),'--fixture-output',str(output)]
    with log.open('x',encoding='utf-8') as handle:
        process=None
        try:
            process=OwnedJobProcess(command,handle,cwd=ROOT,receipt=receipt)
            deadline=time.monotonic()+timeout_seconds
            while process.poll() is None:
                if time.monotonic()>=deadline:raise TimeoutError('Owned fixture unit deadline')
                time.sleep(.01)
            if process.returncode:raise RuntimeError('Fixture child failed: '+str(process.returncode))
        except (Exception,KeyboardInterrupt) as exc:
            ledger=initial_inventory(plan)
            for row in ledger:
                if row['id']==ident:row.update(outcome='timeout' if isinstance(exc,TimeoutError) else 'interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed',reason=str(exc))
            atomic(inventory_path,ledger);raise
        finally:
            if process is not None:
                process.close();atomic(output/'fixture-ownership-final.json',dict(process.ownership))
    row=json.loads(safe_artifact(output,f'outputs/unit-receipts/{ident}.json').read_text(encoding='utf-8'))
    atomic(inventory_path,reconcile(plan,[row],output))
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-request',type=Path,required=True)
    parser.add_argument('--request-sha256',required=True)
    parser.add_argument('--fixture-output',type=Path,required=True)
    args=parser.parse_args()
    if not HASH.fullmatch(args.request_sha256) or file_sha(args.fixture_request)!=args.request_sha256:
        raise ValueError('Generated request receipt mismatch')
    request=json.loads(args.fixture_request.read_text(encoding='utf-8'))
    if set(request)!={'plan','unit_id','fixture'}:raise ValueError('Exact generated request fields required')
    execute_fixture(request['plan'],request['unit_id'],request['fixture'],args.fixture_output)
    return 0

if __name__=='__main__':sys.exit(main())
