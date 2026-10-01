"""Official-runner entrypoint, fixed offline evaluation worker only."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from run_v4_study import linux_path


def command(manifest, output):
    worker = Path(__file__).with_name("v4_saved_evaluation_worker.py")
    return ["C:/Windows/System32/wsl.exe","--exec","timeout","--signal=TERM","--kill-after=30s","86200s",
            "env","-i","PATH=/usr/bin:/bin","LANG=C.UTF-8","OPENBLAS_NUM_THREADS=1","OMP_NUM_THREADS=1",
            "MKL_NUM_THREADS=1","PYTHONHASHSEED=0","PYTHONNOUSERSITE=1","PYTHONDONTWRITEBYTECODE=1",
            "HF_HUB_OFFLINE=1","TRANSFORMERS_OFFLINE=1","DIFFUSERS_OFFLINE=1","HF_DATASETS_OFFLINE=1",
            "HF_HUB_DISABLE_TELEMETRY=1","/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python","-B",
            linux_path(worker),"--manifest",linux_path(manifest),"--output-dir",linux_path(output)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--output-dir",required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    if manifest["run_id"] != "c4-v4-saved-evaluation-002" or manifest["execution_target"] != "local":
        raise ValueError("unlisted evaluation identity")
    if manifest["resources"] != {"ram_mib":6144,"vram_mib":0,"disk_mib":2048}:
        raise ValueError("unlisted CPU envelope")
    from v4_durable_host import ARTIFACTS, verify_preflight
    expected = ARTIFACTS/manifest["stage_id"]/manifest["run_id"]
    if Path(args.output_dir).resolve() != expected.resolve():
        raise ValueError("fixed one-shot evaluation output root required")
    verify_preflight(ARTIFACTS,manifest)
    env = {k:v for k,v in os.environ.items() if k.upper() in
           {"SYSTEMROOT","WINDIR","PATH","TEMP","TMP","USERPROFILE","LOCALAPPDATA"}}
    with (Path(args.output_dir)/"logs/evaluation-worker.log").open("x",encoding="utf-8") as log:
        result = subprocess.run(command(args.manifest,args.output_dir),stdout=log,stderr=subprocess.STDOUT,
                                timeout=86300,env=env)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
