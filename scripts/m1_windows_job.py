"""Windows own-child containment: suspended creation, assignment, then execution.

No PID enumeration or external process lookup. Every operation targets handles
created by this object. A private noninherited kill-on-close Job contains children.
"""
from __future__ import annotations
import ctypes
from ctypes import wintypes as w
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

if sys.platform=='win32':
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    SIZE=ctypes.c_size_t;ULONG_PTR=SIZE
    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_=[('nLength',w.DWORD),('lpSecurityDescriptor',w.LPVOID),('bInheritHandle',w.BOOL)]
    class STARTUPINFO(ctypes.Structure):
        _fields_=[('cb',w.DWORD),('lpReserved',w.LPWSTR),('lpDesktop',w.LPWSTR),('lpTitle',w.LPWSTR),
            ('dwX',w.DWORD),('dwY',w.DWORD),('dwXSize',w.DWORD),('dwYSize',w.DWORD),
            ('dwXCountChars',w.DWORD),('dwYCountChars',w.DWORD),('dwFillAttribute',w.DWORD),
            ('dwFlags',w.DWORD),('wShowWindow',w.WORD),('cbReserved2',w.WORD),('lpReserved2',ctypes.POINTER(w.BYTE)),
            ('hStdInput',w.HANDLE),('hStdOutput',w.HANDLE),('hStdError',w.HANDLE)]
    class STARTUPINFOEX(ctypes.Structure):_fields_=[('StartupInfo',STARTUPINFO),('lpAttributeList',w.LPVOID)]
    class PROCESS_INFORMATION(ctypes.Structure):
        _fields_=[('hProcess',w.HANDLE),('hThread',w.HANDLE),('dwProcessId',w.DWORD),('dwThreadId',w.DWORD)]
    class BASIC_LIMIT(ctypes.Structure):
        _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),
            ('LimitFlags',w.DWORD),('MinimumWorkingSetSize',SIZE),('MaximumWorkingSetSize',SIZE),
            ('ActiveProcessLimit',w.DWORD),('Affinity',ULONG_PTR),('PriorityClass',w.DWORD),('SchedulingClass',w.DWORD)]
    class IO_COUNTERS(ctypes.Structure):
        _fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
    class EXTENDED_LIMIT(ctypes.Structure):
        _fields_=[('BasicLimitInformation',BASIC_LIMIT),('IoInfo',IO_COUNTERS),('ProcessMemoryLimit',SIZE),
            ('JobMemoryLimit',SIZE),('PeakProcessMemoryUsed',SIZE),('PeakJobMemoryUsed',SIZE)]
    def bind(name,args,result):
        fn=getattr(k,name);fn.argtypes=args;fn.restype=result;return fn
    CreateJob=bind('CreateJobObjectW',[w.LPVOID,w.LPCWSTR],w.HANDLE)
    SetJob=bind('SetInformationJobObject',[w.HANDLE,ctypes.c_int,w.LPVOID,w.DWORD],w.BOOL)
    Assign=bind('AssignProcessToJobObject',[w.HANDLE,w.HANDLE],w.BOOL)
    InJob=bind('IsProcessInJob',[w.HANDLE,w.HANDLE,ctypes.POINTER(w.BOOL)],w.BOOL)
    Close=bind('CloseHandle',[w.HANDLE],w.BOOL)
    Resume=bind('ResumeThread',[w.HANDLE],w.DWORD)
    Terminate=bind('TerminateProcess',[w.HANDLE,w.UINT],w.BOOL)
    Wait=bind('WaitForSingleObject',[w.HANDLE,w.DWORD],w.DWORD)
    ExitCode=bind('GetExitCodeProcess',[w.HANDLE,ctypes.POINTER(w.DWORD)],w.BOOL)
    InitAttributes=bind('InitializeProcThreadAttributeList',[w.LPVOID,w.DWORD,w.DWORD,ctypes.POINTER(SIZE)],w.BOOL)
    UpdateAttributes=bind('UpdateProcThreadAttribute',[w.LPVOID,w.DWORD,ULONG_PTR,w.LPVOID,SIZE,w.LPVOID,w.LPVOID],w.BOOL)
    DeleteAttributes=bind('DeleteProcThreadAttributeList',[w.LPVOID],None)
    CreateProcess=bind('CreateProcessW',[w.LPCWSTR,w.LPWSTR,w.LPVOID,w.LPVOID,w.BOOL,w.DWORD,w.LPVOID,w.LPCWSTR,ctypes.POINTER(STARTUPINFOEX),ctypes.POINTER(PROCESS_INFORMATION)],w.BOOL)
    GetCurrent=bind('GetCurrentProcess',[],w.HANDLE)
    Duplicate=bind('DuplicateHandle',[w.HANDLE,w.HANDLE,w.HANDLE,ctypes.POINTER(w.HANDLE),w.DWORD,w.BOOL,w.DWORD],w.BOOL)
    CreateFile=bind('CreateFileW',[w.LPCWSTR,w.DWORD,w.DWORD,ctypes.POINTER(SECURITY_ATTRIBUTES),w.DWORD,w.DWORD,w.HANDLE],w.HANDLE)

def checked(ok):
    if not ok:raise ctypes.WinError(ctypes.get_last_error())
    return ok

class OwnedJobProcess:
    def __init__(self,command,log,*,cwd=None,receipt=None,before_resume=None):
        if sys.platform!='win32':raise RuntimeError('Strict Windows Job containment unavailable on this host')
        if not command or not Path(command[0]).is_absolute():raise ValueError('Absolute executable required')
        import msvcrt
        self.job=self.process=self.thread=None;self.pid=None;self.returncode=None;self.closed=False
        self.ownership={'job_id':str(uuid.uuid4()),'parent_pid':os.getpid(),'command':list(command),
            'created_suspended':True,'kill_on_close':True,'breakaway_allowed':False,'state':'not_created'}
        attributes=None;duplog=w.HANDLE();null=None
        try:
            self.job=checked(CreateJob(None,None)) # Noninherited job; no global name.
            limit=EXTENDED_LIMIT();limit.BasicLimitInformation.LimitFlags=0x2000
            checked(SetJob(self.job,9,ctypes.byref(limit),ctypes.sizeof(limit)))
            checked(Duplicate(GetCurrent(),w.HANDLE(msvcrt.get_osfhandle(log.fileno())),GetCurrent(),ctypes.byref(duplog),0,True,2))
            security=SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES),None,True)
            null=CreateFile('NUL',0x80000000,3,ctypes.byref(security),3,0x80,None)
            if null==w.HANDLE(-1).value:raise ctypes.WinError(ctypes.get_last_error())
            size=SIZE();InitAttributes(None,1,0,ctypes.byref(size))
            attributes=ctypes.create_string_buffer(size.value)
            checked(InitAttributes(attributes,1,0,ctypes.byref(size)))
            handles=(w.HANDLE*2)(duplog.value,null)
            checked(UpdateAttributes(attributes,0,0x20002,ctypes.byref(handles),ctypes.sizeof(handles),None,None))
            startup=STARTUPINFOEX();startup.StartupInfo.cb=ctypes.sizeof(startup);startup.lpAttributeList=ctypes.cast(attributes,w.LPVOID)
            startup.StartupInfo.dwFlags=0x100;startup.StartupInfo.hStdInput=null
            startup.StartupInfo.hStdOutput=duplog;startup.StartupInfo.hStdError=duplog
            pi=PROCESS_INFORMATION();cmd=ctypes.create_unicode_buffer(subprocess.list2cmdline([str(c) for c in command]))
            checked(CreateProcess(str(command[0]),cmd,None,None,True,0x4|0x80000|0x8000000,None,str(cwd) if cwd else None,ctypes.byref(startup),ctypes.byref(pi)))
            self.process,self.thread,self.pid=pi.hProcess,pi.hThread,int(pi.dwProcessId)
            self.ownership.update(pid=self.pid,state='created_suspended')
            if receipt:receipt(dict(self.ownership)) # Ownership recorded before any possible termination.
            checked(Assign(self.job,self.process));inside=w.BOOL()
            checked(InJob(self.process,self.job,ctypes.byref(inside)))
            if not inside.value:raise RuntimeError('Own child Job assignment not verified')
            self.ownership.update(state='assigned_suspended',assignment_verified=True)
            if receipt:receipt(dict(self.ownership))
            if before_resume:before_resume(self) # Testable boundary: worker has not executed.
            if Resume(self.thread)==0xffffffff:raise ctypes.WinError(ctypes.get_last_error())
            self.ownership['state']='running'
            if receipt:receipt(dict(self.ownership))
            Close(self.thread);self.thread=None
        except BaseException:
            if self.process and not self.ownership.get('assignment_verified'):
                # Exact handle to our never-resumed child; no PID search or broad kill.
                Terminate(self.process,1)
            self.close()
            raise
        finally:
            if attributes:DeleteAttributes(attributes)
            if duplog.value:Close(duplog)
            if null and null!=w.HANDLE(-1).value:Close(null)

    def poll(self):
        if self.returncode is not None:return self.returncode
        result=Wait(self.process,0)
        if result==0x102:return None
        if result!=0:raise ctypes.WinError(ctypes.get_last_error())
        code=w.DWORD();checked(ExitCode(self.process,ctypes.byref(code)));self.returncode=int(code.value)
        return self.returncode

    def wait(self,timeout=None):
        result=Wait(self.process,0xffffffff if timeout is None else max(0,min(int(timeout*1000),0xfffffffe)))
        if result==0x102:raise subprocess.TimeoutExpired(self.ownership['command'],timeout)
        if result!=0:raise ctypes.WinError(ctypes.get_last_error())
        return self.poll()

    def close(self):
        if self.closed:return
        self.closed=True
        if self.job:checked(Close(self.job));self.job=None # Kernel kills all assigned descendants.
        if self.process:
            result=Wait(self.process,5000)
            if result!=0:raise RuntimeError('Owned root did not exit after Job close')
            self.poll();Close(self.process);self.process=None
        if self.thread:Close(self.thread);self.thread=None
        self.ownership['state']='closed'

    def __enter__(self):return self
    def __exit__(self,*args):self.close()
