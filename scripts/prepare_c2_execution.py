"""Generate a fixed C2 execution manifest from a clean versioned checkout.

No model, data decode, GPU or execution approval occurs. Output is exclusive.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUTS=("scripts/c2_dev_probe.py","src/signatures/semantic.py","src/signatures/owner.py",
        "src/data/preprocess.py","scripts/a6_clip_visual.py","configs/semantic-dev.json",
        "configs/data.json","data/splits.csv","data/b4-admission-20260926/source-manifest.csv",
        "data/b4-admission-20260926/development-reservation.json",
        "requirements-wsl-stage2-py314.txt","requirements-wsl-torch-py314.txt",
        "experiments/c2-semantic-development-v1/experiment-spec.yaml",
        "experiments/c2-semantic-development-v1/plan.md",
        "experiments/c2-semantic-development-v1/acceptance-criteria.md")


def build():
    status=subprocess.run(["git","-C",str(ROOT),"status","--porcelain"],check=True,capture_output=True,text=True)
    if status.stdout.strip(): raise ValueError("manifest requires an exact clean Git checkout")
    commit=subprocess.run(["git","-C",str(ROOT),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip()
    spec=json.loads((ROOT/"experiments/c2-semantic-development-v1/experiment-spec.yaml").read_bytes())
    script="scripts/run_c2_dev_probe.py"
    return {"schema_version":"1.0","experiment_id":spec["experiment_id"],"run_id":"c2-semantic-dev-001",
            "stage_id":"C2-development","task_id":"C2","execution_target":"local","reviewed_script":script,
            "script_sha256":hashlib.sha256((ROOT/script).read_bytes()).hexdigest(),"git_commit":commit,
            "seeds":[0],"datasets":spec["datasets"],
            "inputs":[{"path":name,"sha256":hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in INPUTS],
            "outputs":["outputs/semantic-examples.json"],
            "metrics":["feature_distance","semantic_code_distance","key_distance","peak_torch_allocated_bytes"],
            "budget":{"max_seconds":1200,"max_usd":0,"hourly_usd":0},
            "resources":{"vram_mib":4096,"ram_mib":6144,"disk_mib":256},"cleanup_policy":"stop-for-recovery"}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args();manifest=build()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(manifest,handle,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False);handle.write("\n")
    digest=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
    print(json.dumps({"manifest_sha256":digest,"git_commit":manifest["git_commit"],"approval":"not_requested_or_granted"}))
