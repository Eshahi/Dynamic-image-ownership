"""Hidden user-account host for the official runner, never an approval writer.

Launch only with real exact approval. No service, daemon, scheduler or auto-retry.
The process owns one fixed official dispatch and records its exit separately.
"""
import argparse
import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from v4_evaluation_journal import atomic_json, file_sha, object_sha

PYTHON = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe")
DISPATCH = Path("C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/dispatch_experiment.py")
RUNTIME = DISPATCH.parent/"_runtime"
ARTIFACTS = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/v4-recovery-runs")
PREFLIGHT_RUN = "c4-v4-recovery-host-check-003"
EVALUATION_RUN = "c4-v4-saved-evaluation-003"


def creation_time(pid):
    if os.name != "nt":
        raise RuntimeError("Windows host required")
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32",use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE,wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x101000,False,pid)
    if not handle:
        raise OSError(ctypes.get_last_error(),"process query failed")
    times = [wintypes.FILETIME() for _ in range(4)]
    try:
        if not kernel.GetProcessTimes(handle,*[ctypes.byref(t) for t in times]):
            raise OSError(ctypes.get_last_error(),"process time failed")
        state = kernel.WaitForSingleObject(handle,0)
        if state == 0:
            raise OSError(87,"process exited (object may still be retained)")
        if state != 258:
            raise OSError(ctypes.get_last_error(),"process liveness query failed")
        return str((times[0].dwHighDateTime<<32)|times[0].dwLowDateTime)
    finally:
        kernel.CloseHandle(handle)


def detach(command, log):
    if os.name != "nt":
        raise RuntimeError("Windows hidden detached host required")
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    with Path(log).open("xb") as stream:
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                   close_fds=True, startupinfo=startup,
                   creationflags=subprocess.DETACHED_PROCESS|subprocess.CREATE_NEW_PROCESS_GROUP)
    return child.pid, creation_time(child.pid)


def process_identity(pid):
    """Live identity plus OS parent, guarded against PID reuse during snapshot."""
    from ctypes import wintypes
    created = creation_time(pid)
    class Entry(ctypes.Structure):
        _fields_ = [("size",wintypes.DWORD),("usage",wintypes.DWORD),("pid",wintypes.DWORD),
                    ("heap",ctypes.c_size_t),("module",wintypes.DWORD),("threads",wintypes.DWORD),
                    ("parent",wintypes.DWORD),("priority",wintypes.LONG),("flags",wintypes.DWORD),
                    ("exe",wintypes.WCHAR*260)]
    kernel = ctypes.WinDLL("kernel32",use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD,wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    for name in ("Process32FirstW","Process32NextW"):
        function = getattr(kernel,name)
        function.argtypes = [wintypes.HANDLE,ctypes.POINTER(Entry)]
        function.restype = wintypes.BOOL
    snapshot = kernel.CreateToolhelp32Snapshot(2,0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise OSError(ctypes.get_last_error(),"process snapshot failed")
    parent = None
    entry = Entry()
    entry.size = ctypes.sizeof(entry)
    try:
        found = kernel.Process32FirstW(snapshot,ctypes.byref(entry))
        while found:
            if entry.pid == pid:
                parent = entry.parent
                break
            found = kernel.Process32NextW(snapshot,ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    if parent is None or creation_time(pid) != created:
        raise ValueError("process identity disappeared or changed")
    return {"pid":pid,"creation_time":created,"parent_pid":parent,
            "parent_creation_time":creation_time(parent)}


def wait_json(path, seconds=15):
    deadline = time.monotonic()+seconds
    while not Path(path).exists():
        if time.monotonic() >= deadline:
            raise TimeoutError("host handshake timed out: "+Path(path).name)
        time.sleep(.05)
    return json.loads(Path(path).read_text())


def identity_alive(pid, created):
    try:
        return creation_time(pid) == created
    except OSError as exc:
        if exc.errno != 87:  # Access/query failure is not evidence of process exit.
            raise
        return False


def validate_ready(request, ready, launcher):
    if ready["request_sha256"] != object_sha(request):
        raise ValueError("host readiness request binding differs")
    identity = {k:ready[k] for k in ("pid","creation_time","parent_pid","parent_creation_time")}
    if process_identity(ready["pid"]) != identity:
        raise ValueError("host readiness live identity differs")
    # Direct interpreter: Popen identity is the host. Windows venv: its parent is Popen.
    direct = (identity["pid"],identity["creation_time"]) == (launcher["pid"],launcher["creation_time"])
    redirected = (identity["parent_pid"],identity["parent_creation_time"]) == (launcher["pid"],launcher["creation_time"])
    if not (direct or redirected) or creation_time(launcher["pid"]) != launcher["creation_time"]:
        raise ValueError("host launch lineage differs")
    if int(identity["creation_time"]) < int(launcher["creation_time"]):
        raise ValueError("host predates its launcher")
    return identity


def ack_value(request, ready, launcher):
    return {"request_sha256":object_sha(request),"ready_sha256":object_sha(ready),
            "launcher":launcher,"initiator_pid":request["initiator_pid"],
            "initiator_creation_time":request["initiator_creation_time"]}


def child_handshake(path, request, seconds=15):
    ready = {**process_identity(os.getpid()),"request_sha256":object_sha(request)}
    atomic_json(Path(path).with_suffix(".ready.json"),ready)
    ack = wait_json(Path(path).with_suffix(".ack.json"),seconds)
    launcher = ack["launcher"]
    if ack != ack_value(request,ready,launcher):
        raise ValueError("host acknowledgement binding differs")
    validate_ready(request,ready,launcher)
    if creation_time(request["initiator_pid"]) != request["initiator_creation_time"]:
        raise ValueError("actual initiating interpreter exited before acknowledgement")
    accepted = {"request_sha256":object_sha(request),"ready_sha256":object_sha(ready),
                "ack_sha256":object_sha(ack)}
    atomic_json(Path(path).with_suffix(".accepted.json"),accepted)
    return ready


def parent_handshake(path, request, launcher, seconds=15):
    ready = wait_json(Path(path).with_suffix(".ready.json"),seconds)
    identity = validate_ready(request,ready,launcher)
    ack = ack_value(request,ready,launcher)
    atomic_json(Path(path).with_suffix(".owner.json"),{**identity,"launcher":launcher,
                "request_sha256":object_sha(request),"manifest_sha256":request["manifest_sha256"]})
    atomic_json(Path(path).with_suffix(".ack.json"),ack)
    accepted = wait_json(Path(path).with_suffix(".accepted.json"),seconds)
    if accepted != {"request_sha256":object_sha(request),"ready_sha256":object_sha(ready),
                    "ack_sha256":object_sha(ack)}:
        raise ValueError("host accepted acknowledgement differs")
    return identity


def verify_request(request):
    sys.path.insert(0,str(RUNTIME))
    from thesis_agents.compute import approval_check, check_execution, git_state
    from thesis_agents.common import safe_env
    manifest = json.loads(Path(request["manifest"]).read_text())
    approval = json.loads(Path(request["approval"]).read_text())
    approval_check(approval,manifest)
    repo = Path(request["repo"])
    if Path(request["artifacts"]).resolve() != ARTIFACTS.resolve():
        raise ValueError("fixed one-shot artifact root required")
    check_execution(manifest,repo)
    if git_state(repo) != (manifest["git_commit"],False):
        raise ValueError("exact clean commit required")
    if manifest["run_id"] not in (PREFLIGHT_RUN,EVALUATION_RUN) or manifest["execution_target"] != "local":
        raise ValueError("unlisted host dispatch identity")
    if object_sha(manifest) != request["manifest_sha256"] or object_sha(approval) != request["approval_sha256"]:
        raise ValueError("host request changed")
    if file_sha(DISPATCH) != request["dispatch_sha256"]:
        raise ValueError("official runner changed")
    return manifest,safe_env()


def host(request_path):
    request = json.loads(Path(request_path).read_text())
    result = None
    error = None
    try:
        manifest,env = verify_request(request)
        child_handshake(request_path,request)
        # Revalidate exact authority/code immediately before dispatch, after ACK.
        manifest,env = verify_request(request)
        if manifest["run_id"] == EVALUATION_RUN:
            verify_preflight(Path(request["artifacts"]),manifest)
        command = [str(PYTHON),"-B",str(DISPATCH),"dispatch",request["manifest"],"--repo",request["repo"],
                   "--artifacts",request["artifacts"],"--approval",request["approval"],"--execute"]
        result = subprocess.run(command,env=env,cwd=request["repo"],timeout=manifest["budget"]["max_seconds"]+120,
                                capture_output=True,text=True,encoding="utf-8",errors="replace")
    except BaseException as exc:
        error = {"type":type(exc).__name__,"message":str(exc)}
    finally:
        destination = Path(request_path).with_suffix(".completion.json")
        atomic_json(destination,{"host_pid":os.getpid(),"host_creation_time":creation_time(os.getpid()),
                                 "manifest_sha256":request["manifest_sha256"],
                                 "request_sha256":object_sha(request),
                                 "exit_code":None if result is None else result.returncode,
                                 "finished_at":datetime.now(timezone.utc).isoformat(),"host_error":error,
                                 "runner_stdout":"" if result is None else result.stdout,
                                 "runner_stderr":"" if result is None else result.stderr})
    return 1 if result is None else result.returncode


def start(manifest_path, approval_path, repo, artifacts, request_path):
    manifest = json.loads(Path(manifest_path).read_text())
    approval = json.loads(Path(approval_path).read_text())
    request = {"manifest":str(Path(manifest_path).resolve()),"approval":str(Path(approval_path).resolve()),
               "repo":str(Path(repo).resolve()),"artifacts":str(Path(artifacts).resolve()),
               "manifest_sha256":object_sha(manifest),"approval_sha256":object_sha(approval),
               "dispatch_sha256":file_sha(DISPATCH),"initiator_pid":os.getpid(),
               "initiator_creation_time":creation_time(os.getpid()),"launch_nonce":uuid.uuid4().hex}
    verify_request(request)
    if manifest["run_id"] == EVALUATION_RUN:
        verify_preflight(Path(artifacts),manifest)
    destination = Path(request_path).resolve()
    if destination != (Path(artifacts)/"host-intents"/(manifest["run_id"]+".json")).resolve():
        raise ValueError("fixed host-intent path required")
    if destination.is_relative_to(Path(repo).resolve()):
        raise ValueError("host artifacts must stay outside clean checkout")
    destination.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive launch-intent prevents uncertain attempts being silently launched twice.
    with destination.open("x",encoding="utf-8") as stream:
        json.dump(request,stream,sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    pid, created = detach([str(PYTHON),"-B",str(Path(__file__).resolve()),"host",str(destination)],
                          destination.with_suffix(".log"))
    identity = parent_handshake(destination,request,{"pid":pid,"creation_time":created})
    return {"host_pid":identity["pid"],"creation_time":identity["creation_time"],
            "launcher_pid":pid,"request_path":str(destination),"dispatched_not_completed":True}


def verify_preflight(artifacts, evaluation_manifest):
    from prepare_v4_saved_evaluation import build_fixture
    root = artifacts/"C4-v4-recovery-host-preflight"/PREFLIGHT_RUN
    receipt = json.loads((root/"manifest.json").read_text())
    expected = build_fixture()
    if (receipt["status"] != "completed" or receipt["exit_status"] != 0 or
        receipt["git_commit"] != evaluation_manifest["git_commit"] or receipt["git_dirty"] or
        receipt["execution_manifest_sha256"] != object_sha(expected)):
        raise ValueError("exact official host preflight not completed")
    for artifact in receipt["output_artifacts"]:
        path = root/artifact["path"]
        if not path.resolve().is_relative_to(root.resolve()) or file_sha(path) != artifact["sha256"]:
            raise ValueError("preflight output changed")
    value = json.loads((root/"outputs/fixture.json").read_text())
    if value != {"model_free":True,"step":5,"completed":True}:
        raise ValueError("preflight fixture incomplete")
    intent = artifacts/"host-intents"/(PREFLIGHT_RUN+".json")
    owner = json.loads(intent.with_suffix(".owner.json").read_text())
    completion = json.loads(intent.with_suffix(".completion.json").read_text())
    request = json.loads(intent.read_text())
    ready = json.loads(intent.with_suffix(".ready.json").read_text())
    ack = json.loads(intent.with_suffix(".ack.json").read_text())
    accepted = json.loads(intent.with_suffix(".accepted.json").read_text())
    if (owner["request_sha256"] != object_sha(request) or
        ready != {k:owner[k] for k in ("pid","creation_time","parent_pid","parent_creation_time","request_sha256")} or
        ack != ack_value(request,ready,owner["launcher"]) or
        accepted != {"request_sha256":object_sha(request),"ready_sha256":object_sha(ready),"ack_sha256":object_sha(ack)}):
        raise ValueError("preflight launch acknowledgement chain differs")
    if (completion["exit_code"] != 0 or completion["host_error"] is not None or
        completion["manifest_sha256"] != object_sha(expected) or
        completion["request_sha256"] != object_sha(request) or owner["manifest_sha256"] != object_sha(expected) or
        (completion["host_pid"],completion["host_creation_time"]) != (owner["pid"],owner["creation_time"])):
        raise ValueError("detached official host outcome not verified")
    if identity_alive(request["initiator_pid"],request["initiator_creation_time"]):
        raise ValueError("preflight initiating process has not exited")
    survival = json.loads((root/"outputs/survival.json").read_text())
    if (survival["request_sha256"] != object_sha(request) or
        survival["host_identity"] != {"pid":owner["pid"],"creation_time":owner["creation_time"]}):
        raise ValueError("survival observation binding differs")
    observations = survival["observations"]
    good = [o for o in observations if o["initiator_alive"] is False and o["host_alive"] is True
            and o["official_status"] == "running" and 0 <= o["step"] < 5]
    if len(good) < 2 or any(b["step"] <= a["step"] or b["monotonic_ns"] <= a["monotonic_ns"]
                            for a,b in zip(good,good[1:])):
        raise ValueError("actual progress after initiating interpreter exit not established")
    return object_sha(expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action",required=True)
    p = sub.add_parser("host")
    p.add_argument("request")
    p = sub.add_parser("start")
    for name in ("manifest","approval","repo","artifacts","request"):
        p.add_argument("--"+name,required=True)
    args = parser.parse_args()
    if args.action == "host":
        raise SystemExit(host(args.request))
    print(json.dumps(start(args.manifest,args.approval,args.repo,args.artifacts,args.request)))
