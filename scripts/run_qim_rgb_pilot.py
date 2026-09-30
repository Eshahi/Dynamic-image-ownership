"""Windows official-runner entrypoint; bounded existing WSL CPU child."""
import argparse
import json
import os
import subprocess
from pathlib import Path


def linux_path(path):
    value = str(Path(path).resolve()).replace("\\", "/")
    if len(value) < 3 or value[1:3] != ":/":
        raise ValueError("expected absolute Windows drive path")
    return "/mnt/" + value[0].lower() + value[2:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if manifest["budget"]["max_seconds"] != 1200:
        raise ValueError("unexpected duration")
    worker = Path(__file__).with_name("qim_rgb_pilot.py")
    command = ["C:/Windows/System32/wsl.exe", "--", "timeout", "--signal=TERM", "--kill-after=5s", "1100s", "env", "OPENBLAS_NUM_THREADS=1", "OMP_NUM_THREADS=1", "CUDA_VISIBLE_DEVICES=", "/home/soroush/.cache/thesis-a6-science-clean-py314/bin/python", "-B", linux_path(worker), "--manifest", linux_path(args.manifest), "--output-dir", linux_path(output)]
    with (output / "logs/cpu-worker.log").open("w", encoding="utf-8") as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=1160, env={key: value for key, value in os.environ.items() if key in {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "USERPROFILE", "LOCALAPPDATA"}})
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
