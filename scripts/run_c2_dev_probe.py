"""Reviewed Windows launcher for one approved, offline, bounded WSL C2 probe.

Invoke only through the official compute runner with exact manifest approval.
No execute flag or user-verdict authoring is provided by this algorithm launcher.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path


def linux_path(path):
    value=str(Path(path).absolute()).replace("\\","/")
    if not re.match(r"^[A-Za-z]:/",value):
        raise ValueError("requires an absolute Windows drive path")
    return "/mnt/"+value[0].lower()+value[2:]


def command(manifest_path, output_path):
    manifest=json.loads(Path(manifest_path).read_bytes())
    if (manifest["experiment_id"]!="c2-semantic-development-v1" or manifest["task_id"]!="C2"
            or manifest["execution_target"]!="local" or manifest["budget"]["max_seconds"]!=1200
            or manifest["budget"]["max_usd"]!=0 or manifest["seeds"]!=[0]):
        raise ValueError("unexpected fixed C2 execution contract")
    repo=Path(__file__).resolve().parents[1]
    # Linux timeout owns the Python process group and escalates after 10 sec;
    # its deadline precedes the official runner's outer Windows timeout.
    return ["C:/Windows/System32/wsl.exe","-d","Ubuntu","--cd",linux_path(repo),"--",
            "/usr/bin/timeout","--signal=TERM","--kill-after=10s","1160s",
            "/usr/bin/env","-i","PYTHONNOUSERSITE=1","HF_HUB_OFFLINE=1",
            "TRANSFORMERS_OFFLINE=1","CUBLAS_WORKSPACE_CONFIG=:4096:8",
            "/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python",
            "scripts/c2_dev_probe.py","--manifest",linux_path(manifest_path),
            "--output-dir",linux_path(output_path)]


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True,type=Path)
    parser.add_argument("--output-dir",required=True,type=Path)
    args=parser.parse_args()
    completed=subprocess.run(command(args.manifest,args.output_dir),check=False,timeout=1190)
    raise SystemExit(completed.returncode)
