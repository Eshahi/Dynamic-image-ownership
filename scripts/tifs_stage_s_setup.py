"""Future authorized Linux Stage S setup. Stdlib-only import; no science execution."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import tifs_common as common
import tifs_gate_profiles as gate_profiles
HERE=ROOT/'research/tifs-20261028/stage-s'
BASE_CONFIG=HERE/'frozen-config.json'
STAGE_P_MANIFEST=HERE.parent/'stage-p/source-manifest.json'
PREFIXES=('sdxl/','a6/','vine/','wam/','kandinsky3/')
CLIP_REVISION='d05afc436d78f1c48dc0dbf8e5980a9d471f35f6'


def safe_path(root,relative):
    if not isinstance(relative,str) or not relative or '\\' in relative or ':' in relative:
        raise ValueError('Unsafe asset/archive path')
    value=PurePosixPath(relative)
    if value.is_absolute() or any(p in ('','..','.') for p in relative.split('/')):
        raise ValueError('Unsafe asset/archive path')
    root=Path(root).resolve()
    target=root.joinpath(*value.parts)
    if not target.resolve().is_relative_to(root): raise ValueError('Asset symlink escapes root')
    # Every symlink is rejected, including a link whose destination happens to be local.
    for p in (target,*target.parents):
        if p==root: break
        if p.is_symlink(): raise ValueError('Symlink asset/archive path')
    return target


def selected_files(plan):
    rows=[row for row in plan['files'] if row['path'].startswith(PREFIXES)]
    if len({r['path'] for r in rows})!=len(rows): raise ValueError('Duplicate asset path')
    for r in rows:
        safe_path(Path.cwd(),r['path'])
        if not r.get('license') or not r['url'].startswith('https://') or type(r['size_bytes']) is not int or r['size_bytes']<0:
            raise ValueError('Missing pinned asset metadata')
        if len(r['sha256'])!=64 or any(c not in '0123456789abcdef' for c in r['sha256']):
            raise ValueError('Invalid asset SHA256')
    return rows


def verify_file(path,spec):
    if not Path(path).is_file() or Path(path).stat().st_size!=spec['size_bytes'] or common.sha256_file(path)!=spec['sha256']:
        raise ValueError('Pinned asset size/hash mismatch: '+str(path))


class Deadline:
    def __init__(self,start,clock=time.time,max_hours=15):
        if type(max_hours) not in (int,float) or not math.isfinite(max_hours) or not max_hours>0:
            raise ValueError('Invalid paid-session ceiling')
        instant=datetime.fromisoformat(start.replace('Z','+00:00'))
        if instant.tzinfo is None or instant.timestamp()>clock(): raise ValueError('Actual past instance-start UTC required')
        self.start=instant.astimezone(timezone.utc).isoformat()
        self.max_hours=max_hours
        self.end=instant.timestamp()+max_hours*3600-3600-30 # Bound one final network read within reserve.
        self.clock=clock
    def timeout(self,cap=None):
        remaining=self.end-self.clock()
        if remaining<=0: raise common.ResourceStop('Setup exhausted '+str(self.max_hours)+'h instance budget with 1h retrieval reserve')
        return remaining if cap is None else min(remaining,cap)


def setup_choices(config_path=BASE_CONFIG,receipt_path=None):
    """Read an external pre-output decision without requiring a P selection.

    Setup precedes tuning. load_execution_config would incorrectly require the
    selection that tuning has not produced yet, so validate the receipt itself.
    This helper reads only and never emits an authorization/approval artifact.
    """
    config_path=Path(config_path)
    config=common.load_json(config_path)
    if config.get('stage_p') or config.get('gate_profile','round1')!='round1':
        raise ValueError('Setup requires the committed default Stage S base config')
    digest=common.sha256_file(config_path)
    result=dict(base_config_sha256=digest,max_instance_hours=15,
                user_choice_sha256=None,stage_p='decline')
    if receipt_path:
        receipt=common.load_json(receipt_path)
        gate_profiles.validate_decision_receipt(receipt,digest)
        result.update(max_instance_hours=receipt['max_instance_hours'],stage_p=receipt['stage_p'],
                      user_choice_sha256=common.sha256_file(receipt_path))
    return result


def command(argv,deadline,**kwargs):
    timeout=deadline.timeout()
    capture=kwargs.pop('capture_output',False)
    if capture: kwargs.update(stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    with subprocess.Popen(argv,start_new_session=True,**kwargs) as process:
        try: stdout,stderr=process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL)
            process.communicate()
            raise
        if process.returncode: raise subprocess.CalledProcessError(process.returncode,argv,stdout,stderr)
        return subprocess.CompletedProcess(argv,process.returncode,stdout,stderr)


def fetch(spec,root,deadline,ledger):
    target=safe_path(root,spec['path']); target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        verify_file(target,spec)
        ledger.append({**spec,'status':'reused_verified'})
        return
    part=target.with_name(target.name+'.part')
    if part.is_symlink(): raise ValueError('Symlink partial download')
    # A completed matching .part is reusable. Incomplete parts restart, never append unverified bytes.
    if part.exists() and part.stat().st_size==spec['size_bytes']:
        verify_file(part,spec); part.replace(target)
        ledger.append({**spec,'status':'completed_partial_verified'}); return
    received=0
    try:
        with urllib.request.urlopen(spec['url'],timeout=deadline.timeout(30)) as response,part.open('wb') as stream:
            while True:
                deadline.timeout()
                block=response.read1(1024*1024)
                if not block: break
                received+=len(block)
                if received>spec['size_bytes']: raise ValueError('Asset exceeds frozen size')
                stream.write(block)
        verify_file(part,spec)
        part.replace(target)
        ledger.append({**spec,'status':'downloaded_verified'})
    except urllib.error.HTTPError as exc:
        if exc.code in (401,403): raise RuntimeError('Gated/auth asset unavailable; no automatic access or license acceptance') from exc
        raise


def verify_sources(root,manifest):
    common.validate_sources(manifest)
    records=[]
    for group in common.SOURCE_GROUPS:
        for row in manifest[group]:
            p=safe_path(root,'sources/'+str(row['source_id'])+'.png')
            if not p.is_file() or common.sha256_file(p)!=row['canonical_png_sha256']:
                raise ValueError('Supply unchanged canonical source PNG before setup: '+str(p))
            records.append(dict(source_id=row['source_id'],path=str(p),sha256=row['canonical_png_sha256']))
    return records


def verify_stage_p_sources(root,manifest_path,stage_s_manifest):
    """Verify all 24 predeclared P PNGs before downloads, without decoding them."""
    from tifs_stage_p import load_manifest
    manifest=load_manifest(manifest_path)  # sidecar, development tags and 16/8 split
    rows=manifest['tune_sources']+manifest['check_sources']
    stage_s_rows=[r for group in common.SOURCE_GROUPS for r in stage_s_manifest[group]]
    for key in ('source_id','source_uid','raw_sha256','canonical_png_sha256','rgb8_sha256'):
        if {str(r[key]) for r in rows}&{str(r[key]) for r in stage_s_rows}:
            raise ValueError('Stage P and Stage S sources overlap: '+key)
    records=[]
    for row in rows:
        path=safe_path(root,'sources/'+str(row['source_id'])+'.png')
        if not path.is_file() or common.sha256_file(path)!=row['canonical_png_sha256']:
            raise ValueError('Supply unchanged canonical Stage P source PNG before setup: '+str(path))
        records.append(dict(source_id=row['source_id'],path=str(path),sha256=row['canonical_png_sha256']))
    return records


def extract_wam(root,plan,deadline):
    archive=safe_path(root,'wam/source.zip')
    spec=next(r for r in plan['files'] if r['path']=='wam/source.zip')
    verify_file(archive,spec)
    prefix='watermark-anything-'+plan['wam_revision']+'/'
    with zipfile.ZipFile(archive) as z:
        if sum(i.file_size for i in z.infolist())>512*1024*1024: raise ValueError('Oversized WAM expansion')
        seen=set()
        for info in z.infolist():
            deadline.timeout()
            if not info.filename.startswith(prefix): raise ValueError('Unexpected WAM archive root')
            rel=info.filename[len(prefix):].rstrip('/')
            if not rel: continue
            if rel in seen: raise ValueError('Duplicate WAM archive path')
            seen.add(rel)
            path=safe_path(root,'wam/source/'+rel)
            mode=info.external_attr>>16
            if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0,stat.S_IFREG,stat.S_IFDIR)):
                raise ValueError('Unsafe special WAM archive entry')
            if info.is_dir(): path.mkdir(parents=True,exist_ok=True); continue
            data=z.read(info)
            if path.exists():
                if path.read_bytes()!=data: raise ValueError('Existing WAM source differs from pinned archive')
            else:
                path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)


def prepare_vine(root,plan,deadline):
    repo=safe_path(root,'vine/source')
    if not repo.exists():
        repo.parent.mkdir(parents=True,exist_ok=True)
        command(['git','clone','--filter=blob:none','--no-checkout',plan['vine_repository'],str(repo)],deadline)
        command(['git','checkout','--detach',plan['vine_revision']],deadline,cwd=repo)
    head=command(['git','rev-parse','HEAD'],deadline,cwd=repo,capture_output=True,text=True).stdout.strip()
    if head!=plan['vine_revision']: raise ValueError('VINE checkout revision mismatch; never reset existing checkout')
    dirty=command(['git','diff','--name-only','HEAD'],deadline,cwd=repo,capture_output=True,text=True).stdout.splitlines()
    if any(p not in plan['vine_patch_source_sha256'] for p in dirty): raise ValueError('Unexpected VINE source changes')
    target=str((root/'vine/sd-turbo').resolve())
    for name,digest in plan['vine_patch_source_sha256'].items():
        original=command(['git','show',plan['vine_revision']+':'+name],deadline,cwd=repo,capture_output=True).stdout
        if hashlib.sha256(original).hexdigest()!=digest: raise ValueError('VINE inspected file hash mismatch')
        patched=original.decode().replace('"stabilityai/sd-turbo"',repr(target)).replace("'stabilityai/sd-turbo'",repr(target)).encode()
        path=safe_path(repo,name)
        if path.read_bytes() not in (original,patched): raise ValueError('Unexpected existing VINE patch changes')
    # Reuse only the inspected local-path patch helper, never its broader prepare().
    # Its two git-show operations are bounded by temporarily wrapping its subprocess API.
    import encoder_transfer_assets as legacy
    original_check_output=legacy.subprocess.check_output
    def checked(*args,**kwargs):
        kwargs['timeout']=deadline.timeout()
        return original_check_output(*args,**kwargs)
    legacy.subprocess.check_output=checked
    try: legacy.patch_vine(root,plan)
    finally: legacy.subprocess.check_output=original_check_output


def validate_pins(requirements,config):
    lines={s.strip() for s in requirements.splitlines() if s.strip() and not s.startswith('#')}
    expected={k+'=='+v for k,v in config['packages'].items()}
    expected.add('clip @ git+https://github.com/openai/CLIP.git@'+CLIP_REVISION)
    expected.add('--extra-index-url https://download.pytorch.org/whl/cu128')
    if lines!=expected: raise ValueError('Requirements differ from exact retained Stage2b pins')


def install(venv,requirements,config,deadline):
    python=venv/'bin/python'
    if not python.exists(): command([sys.executable,'-m','venv',str(venv)],deadline)
    validate_pins(requirements.read_text(encoding='utf-8'),config)
    command([str(python),'-m','pip','install','--index-url','https://download.pytorch.org/whl/cu128',
             'torch=='+config['packages']['torch'],'torchvision=='+config['packages']['torchvision']],deadline)
    command([str(python),'-m','pip','install','-r',str(requirements)],deadline)
    code="import importlib.metadata as m,json; print(json.dumps({d.metadata['Name']:d.version for d in m.distributions()}))"
    versions=json.loads(command([str(python),'-I','-c',code],deadline,capture_output=True,text=True).stdout)
    normalized={k.lower().replace('_','-'):v for k,v in versions.items()}
    for name,pin in config['packages'].items():
        if normalized.get(name.lower().replace('_','-'))!=pin: raise ValueError('Installed package pin mismatch: '+name)
    clip_code="import importlib.metadata as m; print(m.distribution('clip').read_text('direct_url.json'))"
    clip=json.loads(command([str(python),'-I','-c',clip_code],deadline,capture_output=True,text=True).stdout)
    if clip.get('vcs_info',{}).get('commit_id')!=CLIP_REVISION: raise ValueError('Installed CLIP revision mismatch')
    command([str(python),'-m','pip','check'],deadline)
    return dict(versions=versions,clip_direct_url=clip)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets',required=True,type=Path)
    parser.add_argument('--venv',required=True,type=Path)
    parser.add_argument('--instance-start-utc',required=True)
    parser.add_argument('--config',type=Path,default=BASE_CONFIG,
                        help='Committed Stage S base config, before Stage P selection')
    parser.add_argument('--user-choice',type=Path,
                        help='Externally recorded pre-output user choice; never created by setup')
    args=parser.parse_args()
    if platform.system()!='Linux' or Path('/mnt/c/Users').exists(): raise RuntimeError('Setup is Linux server only; laptop execution prohibited')
    if common.load_json(HERE/'READINESS.json').get('status')!='COMPLETE': raise RuntimeError('Stage S readiness is INCOMPLETE')
    root=args.assets.resolve(); root.mkdir(parents=True,exist_ok=True)
    if (root/'RESOURCE_STOP-setup.json').exists():
        raise SystemExit(3)
    choices=setup_choices(args.config,args.user_choice)
    try: deadline=Deadline(args.instance_start_utc,max_hours=choices['max_instance_hours'])
    except common.ResourceStop as exc:
        common.atomic_json(root/'RESOURCE_STOP-setup.json',dict(status='RESOURCE_STOP',reason=str(exc)))
        raise SystemExit(3)
    plan=common.load_json(HERE/'asset-plan.json')
    config=common.load_json(ROOT/'research/encoder-transfer-20261019/stage2b-config.json')
    parent=ROOT/plan['parent_plan']
    if common.sha256_file(parent)!=plan['parent_plan_sha256']: raise ValueError('Retained parent asset plan changed')
    parent_plan=common.load_json(parent)
    if plan['files']!=selected_files(parent_plan): raise ValueError('Stage S asset selection differs from retained plan')
    for key in ('wam_revision','vine_repository','vine_revision','vine_patch_source_sha256'):
        if plan[key]!=parent_plan[key]: raise ValueError('Baseline source revision mismatch')
    ledger_path=root/'tifs-stage-s-download-ledger.json'
    seal=dict(schema='tifs-stage-s-setup-v1',instance_start_utc=deadline.start,asset_plan_sha256=common.sha256_file(HERE/'asset-plan.json'),
              requirements_sha256=common.sha256_file(HERE/'requirements.txt'),source_manifest_sha256=common.sha256_file(HERE/'source-manifest.json'))
    seal.update(base_config_sha256=choices['base_config_sha256'],max_instance_hours=choices['max_instance_hours'],
                user_choice_sha256=choices['user_choice_sha256'],
                stage_p_source_manifest_sha256=common.sha256_file(STAGE_P_MANIFEST) if choices['stage_p']=='run' else None)
    seal['setup_code_sha256']={name:common.sha256_file(ROOT/name) for name in
        ('scripts/tifs_stage_s_setup.py','scripts/tifs_stage_s_setup.sh','scripts/encoder_transfer_assets.py',
         'scripts/tifs_common.py','scripts/tifs_gate_profiles.py','scripts/tifs_stage_p.py')}
    ledger=common.load_json(ledger_path) if ledger_path.exists() else dict(identity=seal,events=[])
    if ledger['identity']!=seal: raise ValueError('Setup resume identity mismatch')
    (root/'tifs-stage-s-setup-ready.json').unlink(missing_ok=True)
    try:
        # Verify preexisting canonical sources before any install/download; never silently reacquire.
        stage_s_manifest=common.load_json(HERE/'source-manifest.json')
        sources=verify_sources(root,stage_s_manifest)
        stage_p_sources=(verify_stage_p_sources(root,STAGE_P_MANIFEST,stage_s_manifest)
                         if choices['stage_p']=='run' else [])
        packages=install(args.venv.resolve(),HERE/'requirements.txt',config,deadline)
        for spec in selected_files(plan):
            fetch(spec,root,deadline,ledger['events'])
            common.atomic_json(ledger_path,ledger)
        extract_wam(root,plan,deadline)
        prepare_vine(root,plan,deadline)
        deadline.timeout()
        common.atomic_json(root/'tifs-stage-s-setup-ready.json',dict(**seal,status='complete',sources=sources,
            stage_p_sources=stage_p_sources,packages=packages,
            setup_finished_utc=datetime.now(timezone.utc).isoformat(),remaining_compute_seconds=deadline.timeout()))
    except common.ResourceStop as exc:
        common.atomic_json(root/'RESOURCE_STOP-setup.json',dict(status='RESOURCE_STOP',reason=str(exc)))
        raise SystemExit(3)
    except subprocess.TimeoutExpired:
        common.atomic_json(root/'RESOURCE_STOP-setup.json',dict(status='RESOURCE_STOP',reason='Setup subprocess reached shared instance deadline'))
        raise SystemExit(3)
    except Exception as exc:
        try: deadline.timeout()
        except common.ResourceStop as stopped:
            common.atomic_json(root/'RESOURCE_STOP-setup.json',dict(status='RESOURCE_STOP',reason=str(stopped)))
            raise SystemExit(3)
        ledger['events'].append(dict(status='setup_error',error_type=type(exc).__name__,error=str(exc),utc=datetime.now(timezone.utc).isoformat()))
        raise
    finally: common.atomic_json(ledger_path,ledger)


if __name__=='__main__': main()
