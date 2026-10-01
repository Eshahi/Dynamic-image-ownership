"""Harmless CPU official-runner host-survival preflight; no scientific imports."""
import argparse
import json
from pathlib import Path
import time
from v4_evaluation_journal import atomic_json


def run(manifest_path, output_path):
    manifest = json.loads(Path(manifest_path).read_text())
    if manifest["run_id"] != "c4-v4-recovery-host-check-001" or manifest["execution_target"] != "local":
        raise ValueError("fixture identity differs")
    if manifest["resources"]["vram_mib"] != 0 or manifest["budget"]["max_usd"] != 0:
        raise ValueError("CPU-only zero-cost fixture required")
    from v4_durable_host import ARTIFACTS
    expected = ARTIFACTS/manifest["stage_id"]/manifest["run_id"]
    if Path(output_path).resolve() != expected.resolve():
        raise ValueError("fixed one-shot preflight output root required")
    for step in range(6):
        atomic_json(Path(output_path)/"outputs/fixture.json",{"model_free":True,"step":step,"completed":step==5})
        time.sleep(2)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--output-dir",required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.manifest,args.output_dir))
