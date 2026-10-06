"""Linux rehearsal on the rented GPU: the full synthetic rehearsal plan through the official dispatcher.

Run on the server: /workspace/venv/bin/python /root/rehearse_linux.py   (writes /root/rehearsal-linux.json)

Synthetic data only. On Windows this plan gave a complete inventory: 926 planned rows, of which 920 completed
and the rest were safety-blocked or dependent; worker status `finished`, dispatcher status `completed`. Expect
the same here.
"""
import json
import subprocess
import time
from pathlib import Path

REPO = Path("/workspace/m1b")
PY = "/workspace/venv/bin/python"
R = "W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/rehearsal"
MAN = Path("/workspace/rehearsal-manifests")
DISPATCH = "C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/dispatch_experiment.py"
PLAN = "research/rehearsal/m1b-rehearsal-full.m1b-plan.json"
RUN_ID = "rehearsal-full-linux-1"


def sh(args):
    t0 = time.time()
    p = subprocess.run(args, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout + "\n" + p.stderr)[-3000:], round(time.time() - t0, 1)


MAN.mkdir(parents=True, exist_ok=True)
approval_path = json.loads((REPO / PLAN).read_text(encoding="utf-8"))["approval_path"]
(REPO / approval_path).parent.mkdir(parents=True, exist_ok=True)
manifest = MAN / f"{RUN_ID}.json"
steps = {
    "manifest": sh([PY, "scripts/m1b_prepare_package.py", "manifest", "--plan", PLAN, "--run-id", RUN_ID,
                    "--max-seconds", "3600", "--out", str(manifest)]),
}
steps["approve"] = sh([PY, "scripts/m1b_make_rehearsal.py", "approve", "--manifest", str(manifest), "--out", approval_path])
code, text, seconds = sh([PY, DISPATCH, "dispatch", str(manifest), "--repo", ".", "--artifacts", R + "/m1b-dispatch",
                          "--execute", "--approval", approval_path])
art = REPO / R / "m1b-dispatch" / "M1b-rehearsal" / RUN_ID
rec = json.loads((art / "manifest.json").read_text(encoding="utf-8")) if (art / "manifest.json").exists() else {}
run = json.loads((art / "outputs/run.json").read_text(encoding="utf-8")) if (art / "outputs/run.json").exists() else {}
result = dict(exit=code, seconds=seconds, dispatcher_status=rec.get("status"), dispatcher_errors=rec.get("errors"),
              worker_status=run.get("status"), worker_error=run.get("infrastructure_error"), inventory=run.get("inventory"),
              steps={k: [v[0], v[1][-400:]] for k, v in steps.items()}, tail=text[-600:])
Path("/root/rehearsal-linux.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
print(json.dumps({k: result[k] for k in ("exit", "seconds", "dispatcher_status", "worker_status", "inventory")}, indent=1))
