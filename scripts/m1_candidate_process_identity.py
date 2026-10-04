"""Bind actual Python interpreter to its already verified private Windows Job.

Windows venv redirectors create a second interpreter process. No model work is
allowed until the parent verifies the registration against its live Job handle.
"""
import hashlib
import json
import os
from pathlib import Path
import time

def _read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def _atomic(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('x',encoding='utf8') as stream:
        json.dump(value,stream,allow_nan=False);stream.flush();os.fsync(stream.fileno())
    tmp.replace(path)

def verify_registration(scope,request,owned_pids):
    fields={'worker_pid','worker_parent_pid','root_pid','launcher_pid','job_id','token_sha256'}
    if type(request) is not dict or set(request)!=fields:raise ValueError('Exact process registration required')
    if any(type(request[k]) is not int or request[k]<=0 for k in ('worker_pid','worker_parent_pid','root_pid','launcher_pid')):raise ValueError('Exact positive process IDs required')
    for k,v in dict(root_pid=scope['child_pid'],launcher_pid=scope['parent_pid'],job_id=scope['job_id'],token_sha256=scope['token_sha256']).items():
        if request[k]!=v:raise ValueError('Registration launch identity differs: '+k)
    ids=set(owned_pids)
    if request['root_pid'] not in ids or request['worker_pid'] not in ids:raise ValueError('Interpreter/root absent from exact owned Job')
    parent=request['worker_parent_pid']
    if parent not in ids and not (request['worker_pid']==request['root_pid'] and parent==request['launcher_pid']):raise ValueError('Interpreter parent not in owned launch lineage')
    return dict(request,assignment_verified=True)

def accept_registration(output,scope,owned_pids):
    output=Path(output);request_path=output/'logs/worker-process-registration.json';binding=output/'logs/worker-process-binding.json'
    if not request_path.exists() or binding.exists():return None
    value=verify_registration(scope,_read(request_path),owned_pids)
    _atomic(binding,value);return value

def register_interpreter(output,scope,token,*,timeout_seconds=20):
    output=Path(output);sha=hashlib.sha256(token.encode()).hexdigest()
    if sha!=scope['token_sha256']:raise ValueError('Registration token differs')
    request=dict(worker_pid=os.getpid(),worker_parent_pid=os.getppid(),root_pid=scope['child_pid'],launcher_pid=scope['parent_pid'],job_id=scope['job_id'],token_sha256=sha)
    _atomic(output/'logs/worker-process-registration.json',request)
    path=output/'logs/worker-process-binding.json';deadline=time.monotonic()+timeout_seconds
    while not path.exists():
        if time.monotonic()>=deadline:raise TimeoutError('Owned interpreter registration not verified')
        time.sleep(.02)
    binding=_read(path)
    if binding!=dict(request,assignment_verified=True):raise ValueError('Interpreter binding differs')
    return binding
