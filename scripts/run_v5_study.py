"""Official-runner Windows entrypoint for the fixed offline WSL v5 two-tier study worker.

The same entrypoint runs the synthetic rehearsal: a manifest whose run_id is the
rehearsal identity makes it pass ``--rehearsal`` to the worker.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess


def linux_path(path):
    value = str(Path(path).resolve()).replace("\\", "/")
    if len(value) < 3 or value[1:3] != ":/":
        raise ValueError("absolute Windows drive path required")
    return "/mnt/" + value[0].lower() + value[2:]


RUN = "c4-v5-two-tier-dev-001"
REHEARSAL_RUN = RUN + "-rehearsal"


def command(manifest, output, rehearsal=False):
    worker = Path(__file__).with_name("v5_study_worker.py")
    return ["C:/Windows/System32/wsl.exe", "--exec", "timeout", "--signal=TERM",
            "--kill-after=30s", "86200s", "env", "-i", "PATH=/usr/bin:/bin", "LANG=C.UTF-8",
            "OPENBLAS_NUM_THREADS=1", "OMP_NUM_THREADS=1", "MKL_NUM_THREADS=1",
            "PYTHONHASHSEED=0", "PYTHONNOUSERSITE=1", "CUBLAS_WORKSPACE_CONFIG=:4096:8",
            "HF_HUB_OFFLINE=1", "TRANSFORMERS_OFFLINE=1", "DIFFUSERS_OFFLINE=1",
            "HF_DATASETS_OFFLINE=1", "HF_HUB_DISABLE_TELEMETRY=1",
            "/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python", "-B",
            linux_path(worker), "--manifest", linux_path(manifest), "--output-dir", linux_path(output)] + (
                ["--rehearsal"] if rehearsal else [])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if manifest["run_id"] not in (RUN, REHEARSAL_RUN) or manifest["execution_target"] != "local":
        raise ValueError("unexpected execution identity/target")
    rehearsal = manifest["run_id"] == REHEARSAL_RUN
    if manifest["budget"] != {"max_seconds": 86400, "max_usd": 0, "hourly_usd": 0}:
        raise ValueError("unexpected operational watchdog/cost budget")
    output = Path(args.output_dir)
    if rehearsal:
        if ".thesis-build/rehearsal/" not in str(output.resolve()).replace("\\", "/") + "/":
            raise ValueError("a rehearsal writes only under .thesis-build/rehearsal")
        (output / "logs").mkdir(parents=True, exist_ok=True)
    safe_env = {key: value for key, value in os.environ.items() if key.upper() in
                {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "USERPROFILE", "LOCALAPPDATA"}}
    with (output / "logs/study-worker.log").open("x", encoding="utf-8") as log:
        result = subprocess.run(command(args.manifest, output, rehearsal), stdout=log,
                                stderr=subprocess.STDOUT, timeout=86300, env=safe_env)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
