"""Sequential, journaled fixed development expansion; no scientific parameter choice.

Each initializer/embedding remains a separate owned, bounded development run.
Resume reuses only successful recorded phases; failed phases require diagnosis.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path
import m1_dev_owned as owned

ROOT=owned.ROOT
BASE=owned.MAIN/'.thesis-build/dev-runs'
IDS=(25394,80932,109798,134882,147498,177015,190676,468505,499768)
PROOFS={
 'audit':'20261004-1102-initializer-comparison',
 'component':'20261004-1045-terminal-deterministic-analysis/run.json',
 'owner':'20261004-1050-owner-extension/run.json',
 'expansion':'20261004-1134-e2e-pilot-analysis/run.json',
}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def persist(path,value):
    tmp=path.with_suffix('.tmp')
    with tmp.open('w',encoding='utf8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.flush();os.fsync(stream.fileno())
    tmp.replace(path)

def run(directory,resume=False,max_phases=17):
    if type(max_phases) is not int or not 1<=max_phases<=17:raise ValueError('Bounded1..17 phase chunk')
    directory=Path(directory).resolve()
    if not directory.is_relative_to(BASE.resolve()) or directory==BASE.resolve():raise ValueError('MAIN development child required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    rel=Path(__file__).relative_to(ROOT).as_posix()
    committed=subprocess.check_output(['git','rev-parse','HEAD:'+rel],cwd=ROOT,text=True).strip()
    if subprocess.check_output(['git','hash-object','--path='+rel,__file__],cwd=ROOT,text=True).strip()!=committed:raise ValueError('Commit queue code first')
    record_path=directory/'run.json'
    if resume:
        record=read(record_path)
        if record['source_ids']!=list(IDS) or record['script_sha256']!=sha(__file__):raise ValueError('Fixed queue changed')
        if any(p['outcome']!='completed' for p in record['phases']):raise ValueError('Diagnose retained failed/incomplete phase before new queue')
    else:
        directory.mkdir(parents=True,exist_ok=False)
        record=dict(schema='m1-fixed-e2e-expansion-queue-v1',data_split='development',command=sys.argv,
          commit=head,script_sha256=sha(__file__),source_ids=list(IDS),proofs=PROOFS,
          seeds=[0],outcome='started',phases=[],duration_seconds=0)
    prior_duration=record['duration_seconds'];started=time.monotonic();completed_now=0
    record.update(process_id=os.getpid(),outcome='started');persist(record_path,record)
    try:
        for sid in IDS:
            initializer=BASE/'20261004-1205-initialize-25394' if sid==25394 else directory/f'initialize-{sid}'
            for phase in ('initialize','e2e'):
                if sid==25394 and phase=='initialize':
                    r=read(initializer/'run.json')
                    if r.get('outcome')!='completed':raise ValueError('Preexisting25394 initializer incomplete')
                    record['preexisting_initializer']=dict(path=str(initializer/'run.json'),sha256=sha(initializer/'run.json'))
                    continue
                key=f'{sid}-{phase}'
                previous=next((p for p in record['phases'] if p['key']==key),None)
                if previous:
                    if sha(Path(previous['output_directory'])/'run.json')!=previous['worker_run_sha256']:raise ValueError('Retained completed phase changed')
                    continue
                output=initializer if phase=='initialize' else directory/f'e2e-{sid}'
                if phase=='initialize':
                    script='m1_source_initialization_audit.py'
                    args=['--stage','initialize','--source-id',str(sid),'--audit-dir',str(BASE/PROOFS['audit'])]
                else:
                    script='m1_terminal_e2e.py'
                    args=['--run','--manifest',str(ROOT/'research/m1-terminal-e2e-dev.json'),
                      '--source-id',str(sid),'--bridge-dir',str(initializer),
                      '--component-analysis',str(BASE/PROOFS['component']),
                      '--owner-extension-receipt',str(BASE/PROOFS['owner']),
                      '--expansion-receipt',str(BASE/PROOFS['expansion'])]
                args+=['--output-dir',str(output)]
                item=dict(key=key,source_id=sid,phase=phase,output_directory=str(output),outcome='started')
                record['phases'].append(item);persist(record_path,record)
                code=owned.run(script,args,directory/(key+'-launch'),1800)
                item['outcome']='completed' if code==0 else 'failed'
                if (output/'run.json').exists():item['worker_run_sha256']=sha(output/'run.json')
                record['duration_seconds']=prior_duration+time.monotonic()-started;persist(record_path,record)
                if code:raise RuntimeError('Retained phase failed; stop for technical diagnosis: '+key)
                print(json.dumps(dict(queue_phase=key,outcome='completed')),flush=True)
                completed_now+=1
                if completed_now>=max_phases:
                    record['outcome']='completed' if len(record['phases'])==17 else 'checkpointed';return 0
        record['outcome']='completed'
    except (Exception,KeyboardInterrupt) as error:
        record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error))
    finally:
        record['duration_seconds']=prior_duration+time.monotonic()-started;persist(record_path,record)
    return 0 if record['outcome']=='completed' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True);parser.add_argument('--resume',action='store_true')
    parser.add_argument('--max-phases',type=int,default=17)
    a=parser.parse_args();raise SystemExit(run(a.output_dir,a.resume,a.max_phases))
