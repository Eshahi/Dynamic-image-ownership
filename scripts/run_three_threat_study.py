"""Official-runner Windows entrypoint for the fixed offline WSL study worker."""
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


def command(manifest, output):
    worker = Path(__file__).with_name("three_threat_worker.py")
    return ["C:/Windows/System32/wsl.exe", "--exec", "timeout", "--signal=TERM",
            "--kill-after=30s", "86200s", "env", "-i", "PATH=/usr/bin:/bin", "LANG=C.UTF-8",
            "OPENBLAS_NUM_THREADS=1", "OMP_NUM_THREADS=1", "MKL_NUM_THREADS=1",
            "PYTHONHASHSEED=0", "PYTHONNOUSERSITE=1", "CUBLAS_WORKSPACE_CONFIG=:4096:8",
            "HF_HUB_OFFLINE=1", "TRANSFORMERS_OFFLINE=1", "DIFFUSERS_OFFLINE=1",
            "HF_DATASETS_OFFLINE=1", "HF_HUB_DISABLE_TELEMETRY=1",
            "/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python", "-B",
            linux_path(worker), "--manifest", linux_path(manifest), "--output-dir", linux_path(output)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if manifest["run_id"] != "c4-three-threat-small-dev-001" or manifest["execution_target"] != "local":
        raise ValueError("unexpected execution identity/target")
    if manifest["budget"] != {"max_seconds": 86400, "max_usd": 0, "hourly_usd": 0}:
        raise ValueError("unexpected operational watchdog/cost budget")
    output = Path(args.output_dir)
    safe_env = {key: value for key, value in os.environ.items() if key.upper() in
                {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "USERPROFILE", "LOCALAPPDATA"}}
    with (output / "logs/study-worker.log").open("x", encoding="utf-8") as log:
        result = subprocess.run(command(args.manifest, output), stdout=log,
                                stderr=subprocess.STDOUT, timeout=86300, env=safe_env)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
