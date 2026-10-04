"""Own one fixed local development worker and retain an outer timeout receipt."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from m1_windows_job import OwnedJobProcess

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ALLOWED={'m1_source_initialization_audit.py','m1_terminal_e2e.py'}


def run(script,arguments,destination,timeout=1800):
    if script not in ALLOWED or type(timeout) is not int or not 1<=timeout<=1830:
        raise ValueError('Fixed local development worker and bounded timeout required')
    output=Path(destination).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):
        raise ValueError('Fresh MAIN development receipt directory required')
    output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();worker=None
    command=[sys.executable,str(ROOT/'scripts'/script),*arguments]
    record=dict(schema='m1-owned-development-launch-v1',data_split='development',
                command=command,timeout_seconds=timeout,ownership=[],outcome='started',
                commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    def persist():
        temporary=output/'run.json.tmp'
        temporary.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n',encoding='utf8')
        temporary.replace(output/'run.json')
    def receipt(value):
        record['ownership'].append(value);persist()
    try:
        record['committed_files']={}
        for name in ('scripts/m1_dev_owned.py','scripts/m1_windows_job.py','scripts/'+script):
            oid=subprocess.check_output(['git','rev-parse','HEAD:'+name],cwd=ROOT,text=True).strip()
            current=subprocess.check_output(['git','hash-object','--path='+name,str(ROOT/name)],cwd=ROOT,text=True).strip()
            if oid!=current:raise ValueError('Uncommitted worker/containment source: '+name)
            record['committed_files'][name]=dict(git_blob_oid=oid,working_sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest())
        persist()
        with (output/'child.log').open('x',encoding='utf8') as log:
            worker=OwnedJobProcess(command,log,cwd=ROOT,receipt=receipt)
            while worker.poll() is None:
                if time.monotonic()-started>=timeout:raise TimeoutError('Owned development wall-time cap')
                time.sleep(.25)
            record.update(outcome='completed' if worker.returncode==0 else 'worker_failed',exit_code=worker.returncode)
    except (Exception,KeyboardInterrupt) as exc:
        record.update(outcome='interrupted' if isinstance(exc,KeyboardInterrupt) else 'timeout' if isinstance(exc,TimeoutError) else 'failed',error=repr(exc))
    finally:
        if worker is not None:
            worker.close();record['final_ownership']=dict(worker.ownership)
        record['duration_seconds']=time.monotonic()-started
        persist()
    print(json.dumps({k:record.get(k) for k in ('outcome','exit_code','duration_seconds','error')}))
    return 0 if record['outcome']=='completed' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--script',required=True,choices=sorted(ALLOWED))
    p.add_argument('--receipt-dir',type=Path,required=True)
    p.add_argument('--timeout',type=int,default=1800)
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    a=p.parse_args();args=a.arguments[1:] if a.arguments[:1]==['--'] else a.arguments
    raise SystemExit(run(a.script,args,a.receipt_dir,a.timeout))
