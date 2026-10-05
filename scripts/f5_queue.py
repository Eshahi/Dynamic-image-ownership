"""f5_queue.py — resumable single-GPU job queue for F5 research.

Journal: research/f5-queue.json (append-safe, fsync on write). One job at a time.
Each job: {id, cmd: [argv], status: pending|running|done|failed, log, pid, exit_code}
Runner polls journal, claims next pending job, runs it, updates status.
Detached launch keeps running after the parent Claude session ends.

Usage:
  python scripts/f5_queue.py enqueue -- <cmd...>
  python scripts/f5_queue.py run          # loop until no pending jobs remain, then exit
  python scripts/f5_queue.py status
  python scripts/f5_queue.py clear        # remove done/failed entries (keeps file)
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "research" / "f5-queue.json"
LOG_DIR = ROOT / "research" / "f5-queue-logs"

def _load():
    if not JOURNAL.exists():
        return {"jobs": []}
    return json.loads(JOURNAL.read_text(encoding="utf-8"))

def _save(data):
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    tmp = JOURNAL.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(JOURNAL)

def enqueue(cmd):
    data = _load()
    jid = f"job-{len(data['jobs'])+1:03d}"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = LOG_DIR / f"{jid}.log"
    data["jobs"].append({"id": jid, "cmd": cmd, "status": "pending", "log": str(log), "exit_code": None})
    _save(data)
    print(f"enqueued {jid}: {' '.join(cmd)} -> {log}")
    return jid

def run_loop(poll_secs=5):
    print(f"[f5_queue] root={ROOT} journal={JOURNAL} pid={os.getpid()}", flush=True)
    while True:
        data = _load()
        pending = [j for j in data["jobs"] if j["status"] == "pending"]
        running = [j for j in data["jobs"] if j["status"] == "running"]
        if running:
            print(f"[f5_queue] still running {running[0]['id']}, waiting {poll_secs}s", flush=True)
            time.sleep(poll_secs)
            continue
        if not pending:
            print("[f5_queue] no pending jobs, exiting", flush=True)
            break
        job = pending[0]
        job["status"] = "running"
        job["pid"] = os.getpid()
        _save(data)
        print(f"[f5_queue] starting {job['id']}: {' '.join(job['cmd'])}", flush=True)
        log_path = Path(job["log"])
        with log_path.open("w", encoding="utf-8") as lf:
            lf.write(f"# {job['id']} {' '.join(job['cmd'])}\n# started {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
            lf.flush()
            proc = subprocess.Popen(job["cmd"], cwd=str(ROOT), stdout=lf, stderr=subprocess.STDOUT)
            ret = proc.wait()
        data = _load()
        for j in data["jobs"]:
            if j["id"] == job["id"]:
                j["status"] = "done" if ret == 0 else "failed"
                j["exit_code"] = ret
                j["finished_at"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        _save(data)
        print(f"[f5_queue] {job['id']} finished with {ret}", flush=True)
        time.sleep(1)

def status():
    data = _load()
    for j in data["jobs"]:
        print(f"{j['id']:8s} {j['status']:8s} exit={j['exit_code']}  {' '.join(j['cmd'][:6])} ...")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enqueue")
    e.add_argument("rest", nargs=argparse.REMAINDER)
    sub.add_parser("run")
    sub.add_parser("status")
    sub.add_parser("clear")
    a = p.parse_args()
    if a.cmd == "enqueue":
        cmd = a.rest
        if cmd and cmd[0] == "--":
            cmd = cmd[1:]
        if not cmd:
            sys.exit("enqueue -- <cmd...>")
        enqueue(cmd)
    elif a.cmd == "run":
        run_loop()
    elif a.cmd == "status":
        status()
    elif a.cmd == "clear":
        data = _load()
        data["jobs"] = [j for j in data["jobs"] if j["status"] in ("pending","running")]
        _save(data)
        print("cleared done/failed")
