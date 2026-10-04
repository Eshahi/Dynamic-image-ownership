"""Measure and close one verified private Windows Job; no global PID kills."""
import ctypes, os, shutil, subprocess, time

def job_snapshot(process):
    if os.name!='nt' or not process.job or process.ownership.get('assignment_verified') is not True:
        raise ValueError('Live verified private Windows Job handle required')
    from ctypes import wintypes as w
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    query=kernel.QueryInformationJobObject
    query.argtypes=[w.HANDLE,ctypes.c_int,w.LPVOID,w.DWORD,ctypes.POINTER(w.DWORD)];query.restype=w.BOOL
    class Accounting(ctypes.Structure):
        _fields_=[(k,ctypes.c_int64) for k in ('user','kernel','period_user','period_kernel')]+[(k,w.DWORD) for k in ('faults','total','active','terminated')]
    info=Accounting();length=w.DWORD()
    if not query(process.job,1,ctypes.byref(info),ctypes.sizeof(info),ctypes.byref(length)):raise ctypes.WinError(ctypes.get_last_error())
    data=ctypes.create_string_buffer(65536)
    if not query(process.job,3,data,len(data),ctypes.byref(length)):raise ctypes.WinError(ctypes.get_last_error())
    assigned=int(ctypes.c_uint32.from_buffer(data,0).value);listed=int(ctypes.c_uint32.from_buffer(data,4).value)
    if listed>(len(data)-8)//ctypes.sizeof(ctypes.c_size_t):raise ValueError('Owned Job PID list exceeds bounded evidence buffer')
    ids=[int(ctypes.c_size_t.from_buffer(data,8+n*ctypes.sizeof(ctypes.c_size_t)).value) for n in range(listed)]
    return dict(active_process_count=int(info.active),assigned_process_count=assigned,process_ids=ids,total_process_count=int(info.total))

def terminate_job(process):
    if os.name!='nt' or not process.job or process.ownership.get('assignment_verified') is not True:
        raise ValueError('Exact verified private Job handle required')
    from ctypes import wintypes as w
    call=ctypes.WinDLL('kernel32',use_last_error=True).TerminateJobObject
    call.argtypes=[w.HANDLE,w.UINT];call.restype=w.BOOL
    if not call(process.job,1):raise ctypes.WinError(ctypes.get_last_error())

def gpu_snapshot(owned_pids=()):
    """Read-only free-memory and owned compute-PID evidence; no GPU workload."""
    executable=shutil.which('nvidia-smi')
    if not executable:return dict(available=False,reason='nvidia-smi unavailable',owned_compute_pids=None)
    try:
        resources=subprocess.check_output([executable,'--query-gpu=uuid,memory.free,memory.total','--format=csv,noheader,nounits'],text=True,timeout=3)
        applications=subprocess.check_output([executable,'--query-compute-apps=pid,gpu_uuid,used_gpu_memory','--format=csv,noheader,nounits'],text=True,timeout=3)
        owned=set(owned_pids);rows=[]
        for line in applications.splitlines():
            parts=[p.strip() for p in line.split(',')]
            if len(parts)==3 and parts[0].isdigit() and int(parts[0]) in owned:rows.append(dict(pid=int(parts[0]),gpu_uuid=parts[1],memory_mib=parts[2]))
        devices=[]
        for line in resources.splitlines():
            parts=[p.strip() for p in line.split(',')]
            if len(parts)!=3 or not parts[1].isdigit() or not parts[2].isdigit():raise ValueError('GPU memory telemetry malformed')
            devices.append(dict(uuid=parts[0],free_mib=int(parts[1]),total_mib=int(parts[2])))
        return dict(available=True,devices=devices,owned_compute_pids=sorted({r['pid'] for r in rows}),owned_compute_rows=rows,
            scope='Observed owned PIDs only; WDDM/driver process visibility limits apply')
    except Exception as error:return dict(available=False,reason=repr(error),owned_compute_pids=None)

def close_with_evidence(process,baseline=None,observed_pids=(),grace_seconds=5):
    """Terminate our Job, query quiescence with live handle, then close it."""
    evidence=dict(job_id=process.ownership.get('job_id'),gpu_baseline=baseline,errors=[])
    owned=set(observed_pids);owned.add(process.pid)
    try:
        initial=job_snapshot(process);owned.update(initial['process_ids']);evidence['job_before_close']=initial
        terminate_job(process);deadline=time.monotonic()+grace_seconds
        while True:
            final=job_snapshot(process);owned.update(final['process_ids'])
            if final['active_process_count']==0 and not final['process_ids']:break
            if time.monotonic()>=deadline:break
            time.sleep(.05)
        evidence['job_after_termination']=final
        evidence['job_quiescent']=final['active_process_count']==0 and not final['process_ids']
    except Exception as error:evidence['job_quiescent']=False;evidence['errors'].append(repr(error))
    finally:process.close()
    evidence['owned_pids_observed']=sorted(owned)
    deadline=time.monotonic()+grace_seconds
    while True:
        after=gpu_snapshot(owned)
        if not after['available'] or not after['owned_compute_pids'] or time.monotonic()>=deadline:break
        time.sleep(.1)
    evidence['gpu_after_close']=after
    evidence['owned_gpu_pids_absent']=not after['owned_compute_pids'] if after['available'] else None
    evidence['cleanup_verified']=evidence['job_quiescent'] is True and evidence['owned_gpu_pids_absent'] is True
    if baseline and baseline.get('available') and after.get('available'):
        before={r['uuid']:r['free_mib'] for r in baseline['devices']}
        evidence['free_memory_delta_mib']={r['uuid']:r['free_mib']-before[r['uuid']] for r in after['devices'] if r['uuid'] in before}
    evidence['scope']='Exact private Job quiescence plus observed owned GPU PID absence; memory deltas are descriptive, not global cleanup proof'
    return evidence
