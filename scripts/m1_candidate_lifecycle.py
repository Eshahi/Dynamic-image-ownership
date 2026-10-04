"""Owned generated-image candidate lifecycle rehearsal; no scientific unlock.

Official entry accepts --manifest/--output-dir. Resume receipts are a separate
generated-only development seam until the official recovery input is adopted.
"""
from __future__ import annotations
import argparse, hashlib, importlib, json, os, re, secrets, signal, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from m1_confirmatory_harness import FIELDS, atomic, contained, file_sha, object_sha, read, verify_initial_output
from m1_windows_job import OwnedJobProcess
from m1_owned_cleanup_evidence import close_with_evidence, gpu_snapshot, job_snapshot
MAIN=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
VERSION='m1-candidate-lifecycle-v1'
CATALOG=ROOT/'research/m1-candidate-lifecycle-v1.json'
WORKER=ROOT/'scripts/m1_candidate_rehearsal_worker.py'
PYTHON=MAIN/'.thesis-build/a6-science-venv/Scripts/python.exe'
OUTPUTS=['outputs/lifecycle-run.json','outputs/worker-run.json','outputs/worker-heartbeat.json',
    'checkpoints/lifecycle-journal.json','checkpoints/worker-journal.json']
DATASET=[dict(id='m1-candidate-generated-rehearsal',version='1',license='generated-in-process',split='synthetic')]

def destination(value):
    if '..' in Path(value).parts:raise ValueError('Rehearsal path traversal refused')
    path=Path(value).absolute()
    allowed=(MAIN/'.thesis-build/rehearsal').absolute()
    if path==allowed or not path.is_relative_to(allowed):raise ValueError('MAIN generated rehearsal destination required')
    for current in (path,*path.parents):
        if current==allowed:break
        if current.is_symlink() or (current.exists() and getattr(current.lstat(),'st_file_attributes',0)&0x400):
            raise ValueError('Reparse rehearsal destination refused')
    return path

def adapter_worker():
    if not WORKER.is_file():raise ValueError('Actual candidate rehearsal worker unavailable')
    return importlib.import_module('m1_candidate_rehearsal_worker')

def dependencies():
    return list(dict.fromkeys([Path(__file__),CATALOG,ROOT/'scripts/m1_windows_job.py',
        ROOT/'scripts/m1_confirmatory_harness.py',ROOT/'scripts/m1_owned_cleanup_evidence.py',*adapter_worker().dependency_paths()]))

def validate_manifest(manifest):
    if set(manifest)!=FIELDS or manifest.get('schema_version')!='1.0':raise ValueError('Exact official envelope required')
    for key in ('experiment_id','run_id','stage_id','task_id'):
        if type(manifest[key]) is not str or re.fullmatch('[A-Za-z0-9][A-Za-z0-9_-]{0,127}',manifest[key]) is None:raise ValueError('Identifier')
    catalog=read(CATALOG)
    if catalog.get('schema')!=VERSION or manifest['stage_id'] not in catalog['cases']:raise ValueError('Frozen generated rehearsal stage required')
    if manifest['execution_target']!='local' or manifest['cleanup_policy']!='stop-for-recovery' or manifest['datasets']!=DATASET:
        raise ValueError('Generated USD0 local rehearsal only')
    if manifest['outputs']!=OUTPUTS or manifest['metrics']!=['candidate_generated_rehearsal_units']:raise ValueError('Exact lifecycle output/metric inventory')
    if contained(ROOT,manifest['reviewed_script'])!=Path(__file__).resolve() or manifest['script_sha256']!=file_sha(__file__):raise ValueError('Reviewed launcher identity differs')
    if not re.fullmatch('[a-f0-9]{40}',manifest['git_commit']):raise ValueError('Exact commit required')
    if manifest['seeds']!=catalog['seeds']:raise ValueError('Frozen uint64 metadata seeds required')
    budget=manifest['budget'];resources=manifest['resources']
    if set(budget)!={'max_seconds','max_usd','hourly_usd'} or type(budget['max_seconds']) is not int or not 1<=budget['max_seconds']<=3600 or budget['max_usd']!=0 or budget['hourly_usd']!=0:raise ValueError('Bounded local USD0 budget')
    if resources!={'vram_mib':10240,'ram_mib':16384,'disk_mib':500}:raise ValueError('Frozen resource caps required')
    expected={p.relative_to(ROOT).as_posix():file_sha(p) for p in dependencies()}
    entries=manifest['inputs']
    if not isinstance(entries,list) or any(set(e)!={'path','sha256'} for e in entries) or len(entries)!=len(expected) or {e['path']:e['sha256'] for e in entries}!=expected:
        raise ValueError('Exact committed worker/infrastructure dependency receipts required')
    return catalog['cases'][manifest['stage_id']]

def pin_execution(manifest):
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if head!=manifest['git_commit']:raise ValueError('Current HEAD differs')
    from m1_git_input_identity import verify_git_input
    expected={v['path']:v['sha256'] for v in manifest['inputs']}
    return {path.relative_to(ROOT).as_posix():verify_git_input(path,head,ROOT,expected[path.relative_to(ROOT).as_posix()]) for path in dependencies()}


def upstream_receipts(value):
    if value is None:return None
    if set(value)!={'run','checkpoint'}:raise ValueError('Explicit run/checkpoint recovery receipts required')
    for receipt in value.values():
        if set(receipt)!={'path','sha256'} or not re.fullmatch('[0-9a-f]{64}',receipt['sha256']):raise ValueError('Recovery receipt malformed')
        path=destination(receipt['path'])
        if not path.is_file() or file_sha(path)!=receipt['sha256']:raise ValueError('Recovery receipt changed')
    return value

def capability(manifest,case,output,token,ownership,upstream,unit_index=0):
    if ownership.get('assignment_verified') is not True or ownership.get('created_suspended') is not True:
        raise ValueError('Child must be assigned and verified before scope issuance')
    return dict(schema='m1-candidate-rehearsal-launch-v1',manifest_sha256=object_sha(manifest),
        plan_sha256=object_sha(adapter_worker().configuration()),worker_sha256=file_sha(WORKER),
        scientific_core_sha256=adapter_worker().scientific_core_sha256(),output_directory=str(output),
        child_pid=ownership['pid'],parent_pid=os.getpid(),job_id=ownership['job_id'],assignment_verified=True,unit_index=unit_index,
        token_sha256=hashlib.sha256(token.encode()).hexdigest(),stage=case['stage'],scenario=manifest['stage_id'],
        stop_phase=case['stop_phase'],stop_step=case['stop_step'],upstream=upstream,injection=case['injection'],
        cooperative_stop_path=str(output/'checkpoints/stop-request.json'),expires_unix=time.time()+manifest['budget']['max_seconds']+30)

def triggered(control,heartbeat,elapsed):
    if control['after_seconds'] is not None and elapsed>=control['after_seconds']:return True
    if not heartbeat or control['phase'] is None:return False
    return heartbeat.get('phase')==control['phase'] and (control['step'] is None or type(heartbeat.get('step')) is int and heartbeat['step']>=control['step'])

def recovery_check(prior,manifest):
    value=upstream_receipts(prior)
    if value is None:raise ValueError('Resume requires explicit generated prior receipts')
    run=read(Path(value['run']['path']))
    if run.get('generated_only') is not True or run.get('scientific_core_sha256')!=adapter_worker().scientific_core_sha256():
        raise ValueError('Recovery must bind the same actual generated candidate core')
    return value

def require_parity(parity):
    names={'initialization_exact','embedding_adam_rng_exact','endpoint_rgb8_exact','blind_decisions_exact','overlap_inventory_exact','overlap_states_adam_rng_exact'}
    checks=parity.get('checks',{})
    overlap=parity.get('overlap_checks',{})
    overlap_names={f'embedding-{n}' for n in range(0,101,10)}|{f'initialization-{n}' for n in range(100,201,10)}
    if parity.get('passes') is not True or not names<=set(checks) or set(overlap)!=overlap_names or any(value is not True for value in checks.values()) or any(value is not True for value in overlap.values()) or any(type(value) is bool and value is not True for value in parity.values()):
        raise ValueError('Exact full/resume parity checks did not all pass')
    return parity

def run(manifest_path,output,upstream=None,unit_index=0):
    manifest=read(Path(manifest_path));case=validate_manifest(manifest);pin_execution(manifest)
    if type(unit_index) is not int or unit_index not in (0,1) or unit_index==1 and manifest['stage_id']!='scale':raise ValueError('Frozen generated scale unit only')
    output=destination(output);output.mkdir(parents=True,exist_ok=True)
    upstream=recovery_check(upstream,manifest) if case['stage']=='resume' else upstream_receipts(upstream)
    if case['stage']!='resume' and upstream is not None:raise ValueError('Nonresume prior input refused')
    lock=output/'lifecycle.lock';fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL)
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    process=None;previous={};record=None;started=time.monotonic();journal=[];baseline=None;observed=set()
    def close_child():
        if process is not None and record is not None and 'cleanup_evidence' not in record:
            record['cleanup_evidence']=close_with_evidence(process,baseline,observed)
    try:
        verify_initial_output(output,manifest,lock)
        record=dict(schema=VERSION,manifest_sha256=object_sha(manifest),command=sys.argv,
            generated_only=True,scientific_verdict='NOT_EVIDENCE',scenario=manifest['stage_id'],case=case,
            commit=manifest['git_commit'],outcome='started',upstream=upstream,human_visual_verdict=None)
        atomic(output/'outputs/lifecycle-run.json',record)
        def event(kind,**fields):
            journal.append(dict(kind=kind,elapsed_seconds=time.monotonic()-started,**fields))
            atomic(output/'checkpoints/lifecycle-journal.json',dict(schema=VERSION,manifest_sha256=object_sha(manifest),events=journal))
        def interrupted(signum,frame):raise KeyboardInterrupt('Launcher received '+str(signum))
        for sig in (signal.SIGINT,signal.SIGTERM):previous[sig]=signal.signal(sig,interrupted)
        token=secrets.token_hex(32);scope_path=output/'logs/launch-capability.json'
        scope_path.parent.mkdir(parents=True,exist_ok=True)
        command=[str(PYTHON),str(WORKER),'--manifest',str(Path(manifest_path).resolve()),'--output-dir',str(output)]
        with (output/'logs/worker.log').open('x',encoding='utf-8') as log:
            def before_resume(child):
                ownership=child.ownership
                atomic(scope_path,capability(manifest,case,output,token,ownership,upstream,unit_index))
                event('scope_issued',ownership=ownership,capability_sha256=file_sha(scope_path))
            oldenv={k:os.environ.get(k) for k in ('M1_REHEARSAL_TOKEN','M1_REHEARSAL_CAPABILITY')}
            baseline=gpu_snapshot()
            try:
                os.environ['M1_REHEARSAL_TOKEN']=token;os.environ['M1_REHEARSAL_CAPABILITY']=str(scope_path)
                process=OwnedJobProcess(command,log,cwd=ROOT,receipt=lambda v:event('ownership',ownership=v),before_resume=before_resume)
            finally:
                for k,v in oldenv.items():
                    if v is None:os.environ.pop(k,None)
                    else:os.environ[k]=v
            control=case['control'];injected=False;grace_deadline=None
            while process.poll() is None:
                observed.update(job_snapshot(process)['process_ids'])
                elapsed=time.monotonic()-started;hbpath=output/'outputs/worker-heartbeat.json'
                heartbeat=read(hbpath) if hbpath.exists() else None
                if elapsed>=manifest['budget']['max_seconds']:raise TimeoutError('Owned shard hard deadline')
                if not injected and triggered(control,heartbeat,elapsed):
                    injected=True;event('lifecycle_injection',action=control['action'],heartbeat=heartbeat)
                    if control['action']=='hostloss':os._exit(91) # OS handle closure kills the private child Job; stale evidence is retained.
                    if control['action']=='kill':close_child();break
                    if control['action']=='term':
                        atomic(output/'checkpoints/stop-request.json',dict(schema=VERSION,reason='prespecified cooperative termination',manifest_sha256=object_sha(manifest)))
                        grace_deadline=time.monotonic()+control['grace_seconds']
                    if control['action']=='timeout':raise TimeoutError('Prespecified lifecycle deadline')
                if grace_deadline is not None and time.monotonic()>=grace_deadline:
                    event('cooperative_grace_expired');close_child();break
                time.sleep(.1)
            code=process.returncode;close_child();event('owned_child_closed',ownership=process.ownership,returncode=code,cleanup=record['cleanup_evidence'])
            record['child_returncode']=code
            worker_run=output/'outputs/worker-run.json'
            if worker_run.exists():record['worker_run']=dict(path=str(worker_run),sha256=file_sha(worker_run))
            record['outcome']='completed' if code==0 and worker_run.exists() and record['cleanup_evidence']['cleanup_verified'] is True else 'interrupted' if injected else 'failed'
            if record['cleanup_evidence']['cleanup_verified'] is not True:record['cleanup_status']='unverified; rehearsal completion refused'
            # Process completion is infrastructure evidence, not candidate correctness or a rehearsal pass.
            record['candidate_verification']='PENDING_INDEPENDENT_STAGE_AND_PARITY_AUDIT'
            return 0 if record['outcome']=='completed' else 2
    except (Exception,KeyboardInterrupt) as error:
        if record is not None:record.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'timeout' if isinstance(error,TimeoutError) else 'failed',error=repr(error))
        return 2
    finally:
        if process is not None:close_child()
        if record is not None:
            record['duration_seconds']=time.monotonic()-started
            if process is not None:record['ownership']=process.ownership
            record['outputs']={p.relative_to(output).as_posix():file_sha(p) for p in output.rglob('*') if p.is_file() and p not in (output/'outputs/lifecycle-run.json',lock)}
            atomic(output/'outputs/lifecycle-run.json',record)
        for sig,handler in previous.items():signal.signal(sig,handler)
        lock.unlink(missing_ok=True)

def prepare_suite(directory,max_seconds=1800):
    directory=destination(directory);directory.mkdir(parents=True,exist_ok=False)
    catalog=read(CATALOG);head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    paths=[]
    for name in catalog['cases']:
        manifest=dict(schema_version='1.0',experiment_id='m1-candidate-generated',run_id=name+'-'+directory.name,
            stage_id=name,task_id='m1-candidate-rehearsal',execution_target='local',reviewed_script=Path(__file__).relative_to(ROOT).as_posix(),
            script_sha256=file_sha(__file__),git_commit=head,seeds=catalog['seeds'],datasets=DATASET,
            inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=file_sha(p)) for p in dependencies()],outputs=OUTPUTS,
            metrics=['candidate_generated_rehearsal_units'],budget=dict(max_seconds=max_seconds,max_usd=0,hourly_usd=0),
            resources=dict(vram_mib=10240,ram_mib=16384,disk_mib=500),cleanup_policy='stop-for-recovery')
        validate_manifest(manifest);path=directory/(name+'.json');atomic(path,manifest);paths.append(str(path))
    atomic(directory/'suite.json',dict(schema=VERSION,execution='unperformed',manifests=paths,
        readiness='Actual adapter required; candidate-specific parity/resource audit and official preview remain separate'))

def coordinate_suite(suite_path,output,selected_cases=None,prefix_directory=None,reference_full=None):
    """Sequential private outer Jobs preserve hostloss evidence and containment."""
    suite_path=destination(suite_path);suite=read(suite_path)
    if suite.get('schema')!=VERSION or suite.get('execution')!='unperformed':raise ValueError('Prepared generated suite required')
    selected_cases=selected_cases or ['real']
    if not 1<=len(selected_cases)<=2 or len(set(selected_cases))!=len(selected_cases) or not set(selected_cases)<=set(read(CATALOG)['cases']):
        raise ValueError('One or two fixed suite cases per bounded coordinator process')
    output=destination(output);output.mkdir(parents=True,exist_ok=False)
    prefix_directory=destination(prefix_directory) if prefix_directory else None
    reference_full=destination(reference_full) if reference_full else None
    coordinator_started=time.monotonic()
    record=dict(schema=VERSION,generated_only=True,outcome='started',attempts=[],scientific_verdict='NOT_EVIDENCE',
        selected_cases=selected_cases,planned_cases=list(read(CATALOG)['cases']),coordinator_seconds_cap=3500)
    for manifest_name in suite['manifests']:
        manifest_path=destination(manifest_name);manifest=read(manifest_path);validate_manifest(manifest)
        name=manifest['stage_id']
        if name not in selected_cases:continue
        for index in (0,1) if name=='scale' else (0,):
            attempt_dir=output/(name+'-'+str(index));command=[str(PYTHON),str(Path(__file__).resolve()),
                '--manifest',str(manifest_path),'--output-dir',str(attempt_dir),'--unit-index',str(index)]
            if name=='resume':
                if prefix_directory is None:
                    record['attempts'].append(dict(scenario=name,unit_index=index,outcome='blocked',reason='Explicit audited prefix directory required'))
                    atomic(output/'suite-run.json',record);continue
                prior=adapter_worker().audit_rehearsal_run(prefix_directory)
                if prior['outcome']!='prefix_completed' or prior['unit_index']!=0:raise ValueError('Matching fixed prefix source required')
                upstream=dict(run=dict(path=str(prefix_directory/'outputs/worker-run.json'),sha256=file_sha(prefix_directory/'outputs/worker-run.json')),
                    checkpoint=prior['latest_checkpoint'])
                handoff=output/'prefix-recovery-receipt.json';atomic(handoff,upstream)
                command.extend(['--upstream-receipt',str(handoff)])
            log_path=output/(name+'-'+str(index)+'.log');started=time.monotonic();process=None;observed=set();baseline=gpu_snapshot()
            attempt=dict(scenario=name,unit_index=index,output_directory=str(attempt_dir),outcome='started')
            record['attempts'].append(attempt);atomic(output/'suite-run.json',record)
            try:
                with log_path.open('x',encoding='utf-8') as log:
                    def ownership(value):attempt['ownership']=value;atomic(output/'suite-run.json',record)
                    process=OwnedJobProcess(command,log,cwd=ROOT,receipt=ownership)
                    while process.poll() is None:
                        observed.update(job_snapshot(process)['process_ids'])
                        if time.monotonic()-started>=manifest['budget']['max_seconds']+15 or time.monotonic()-coordinator_started>=3500:raise TimeoutError('Outer rehearsal/coordinator guard')
                        time.sleep(.1)
                    attempt.update(returncode=process.returncode,outcome='returned')
            except (Exception,KeyboardInterrupt) as error:
                attempt.update(outcome='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=repr(error))
                if isinstance(error,KeyboardInterrupt):raise
            finally:
                if process is not None:
                    attempt['cleanup_evidence']=close_with_evidence(process,baseline,observed)
                    attempt['cleanup_status']='verified' if attempt['cleanup_evidence']['cleanup_verified'] is True else 'unverified'
                    attempt['ownership']=process.ownership
                attempt['duration_seconds']=time.monotonic()-started
                attempt['artifacts']={p.relative_to(attempt_dir).as_posix():file_sha(p) for p in attempt_dir.rglob('*') if p.is_file()} if attempt_dir.exists() else {}
                atomic(output/'suite-run.json',record)
            if name in ('real','scale','prefix','resume') and attempt.get('returncode')==0:
                try:
                    audited=adapter_worker().audit_rehearsal_run(attempt_dir)
                    attempt['candidate_receipt_audit']=dict(outcome='completed',worker_outcome=audited['outcome'],latest_checkpoint=audited['latest_checkpoint'])
                    if name=='prefix':prefix_directory=attempt_dir
                    if name=='real':reference_full=attempt_dir
                    if name=='resume':
                        parity=adapter_worker().compare_full_resume(reference_full,attempt_dir) if reference_full else dict(outcome='unperformed',reason='Explicit full reference directory required')
                        attempt['full_resume_parity']=parity
                        if reference_full:
                            require_parity(parity)
                except Exception as error:attempt['candidate_receipt_audit']=dict(outcome='failed',error=repr(error))
                atomic(output/'suite-run.json',record)
    record.update(outcome='inventory_recorded',candidate_verification='PENDING_INDEPENDENT_STAGE_AND_PARITY_AUDIT')
    atomic(output/'suite-run.json',record)
    return 0

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path);p.add_argument('--output-dir',type=Path)
    p.add_argument('--upstream-receipt',type=Path);p.add_argument('--prepare-suite',type=Path)
    p.add_argument('--unit-index',type=int,default=0)
    p.add_argument('--coordinate-suite',type=Path)
    p.add_argument('--suite-case',action='append')
    p.add_argument('--prefix-directory',type=Path);p.add_argument('--reference-full-directory',type=Path)
    a=p.parse_args()
    if a.prepare_suite:prepare_suite(a.prepare_suite);return 0
    if a.coordinate_suite:
        if not a.output_dir:p.error('suite coordinator requires --output-dir')
        return coordinate_suite(a.coordinate_suite,a.output_dir,a.suite_case,a.prefix_directory,a.reference_full_directory)
    if not a.manifest or not a.output_dir:p.error('--manifest and --output-dir required')
    if a.upstream_receipt:destination(a.upstream_receipt)
    return run(a.manifest,a.output_dir,read(a.upstream_receipt) if a.upstream_receipt else None,a.unit_index)
if __name__=='__main__':raise SystemExit(main())
