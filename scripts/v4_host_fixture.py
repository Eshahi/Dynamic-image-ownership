"""Harmless CPU official-runner host-survival preflight; no scientific imports."""
import argparse
import json
from pathlib import Path
import time
from datetime import datetime, timezone
from v4_evaluation_journal import atomic_json


def run(manifest_path, output_path):
    manifest = json.loads(Path(manifest_path).read_text())
    if manifest["run_id"] != "c4-v4-recovery-host-check-002" or manifest["execution_target"] != "local":
        raise ValueError("fixture identity differs")
    if manifest["resources"]["vram_mib"] != 0 or manifest["budget"]["max_usd"] != 0:
        raise ValueError("CPU-only zero-cost fixture required")
    from v4_durable_host import ARTIFACTS, identity_alive
    from v4_evaluation_journal import object_sha
    expected = ARTIFACTS/manifest["stage_id"]/manifest["run_id"]
    if Path(output_path).resolve() != expected.resolve():
        raise ValueError("fixed one-shot preflight output root required")
    intent = ARTIFACTS/"host-intents"/(manifest["run_id"]+".json")
    request = json.loads(intent.read_text())
    owner = json.loads(intent.with_suffix(".owner.json").read_text())
    observations = []
    for step in range(6):
        atomic_json(Path(output_path)/"outputs/fixture.json",{"model_free":True,"step":step,"completed":step==5})
        observations.append({"step":step,"observed_at":datetime.now(timezone.utc).isoformat(),
                             "monotonic_ns":time.monotonic_ns(),
                             "host_alive":identity_alive(owner["pid"],owner["creation_time"]),
                             "initiator_alive":identity_alive(request["initiator_pid"],request["initiator_creation_time"]),
                             "official_status":json.loads((expected/"manifest.json").read_text())["status"]})
        atomic_json(Path(output_path)/"outputs/survival.json",{"request_sha256":object_sha(request),
                    "host_identity":{"pid":owner["pid"],"creation_time":owner["creation_time"]},
                    "observations":observations})
        time.sleep(2)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--output-dir",required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.manifest,args.output_dir))
