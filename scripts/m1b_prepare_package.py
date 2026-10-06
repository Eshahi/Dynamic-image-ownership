"""Prepare the M1b execution manifest, its scientific-core hash and the approval question.

    python scripts/m1b_prepare_package.py manifest --plan research/m1b-coco512-test.m1b-plan.json \
        --run-id coco512-confirm-1 --max-seconds 43200 --out <outside the repo>/execution-manifest.json
    python scripts/m1b_prepare_package.py rerun-check --approved <approved manifest> --new <new manifest> \
        --previous-run <artifact dir of the incomplete attempt>

This script writes no approval. It prints the exact JSON the user saves as their approval
record (`research/approval-policy.md`: the user approves the manifest hash, the scientific-core
hash and up to 2 infrastructure-only reruns).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import m1b_coco512_worker as W  # noqa: E402

FIXED_INPUTS = ("configs/f5-r2.json", "experiments/c4-v5-two-tier-regeneration-v1/profile.json",
                "research/a6-candidate-model-assets.json")


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def core_hash(plan: dict) -> str:
    """Scientific core: plan science fields, frozen code, worker version. Operational fields excluded."""
    return W.object_digest(dict(version=W.VERSION, science_digest=W.science_digest(plan),
                                code_sha256={f: sha(ROOT / f) for f in W.CODE_FILES}))


def build_manifest(plan_path: str, run_id: str, max_seconds: int) -> dict:
    plan = json.loads((ROOT / plan_path).read_text(encoding="utf-8"))
    W.validate_plan(plan)
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if dirty:
        raise SystemExit("clean checkout required:\n" + dirty)
    inputs = [plan_path, *FIXED_INPUTS]
    if "index" in plan["sources"]:
        inputs.append(plan["sources"]["index"]["path"])
        inputs.append("research/m1-confirmatory-schedule-draft.json")
    test = plan["data_split"] == "test"
    return dict(
        schema_version="1.0", experiment_id="M1b-coco512-confirmatory" if test else "M1b-coco512-development",
        run_id=run_id, stage_id="M1b-confirmatory" if test else "M1b-development", task_id="coco512-f5r2-v5r3",
        execution_target="local", reviewed_script="scripts/m1b_coco512_worker.py",
        script_sha256=sha(ROOT / "scripts/m1b_coco512_worker.py"),
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        seeds=list(W.SEEDS),
        datasets=[dict(id="ms-coco", version="coco-2017 val2017 (study_split=test, frozen 300 representatives)",
                       license="images: per-image Flickr licences, rights pending, local research only; annotations CC-BY-4.0",
                       split="test")] if test else
                 [dict(id="development-sources", version="m1a-twelve", license="development reservation", split="development")],
        inputs=[dict(path=p, sha256=sha(ROOT / p)) for p in inputs],
        outputs=["outputs/run.json", "outputs/journal.jsonl", "outputs/run-context.json", "metrics/endpoints.json"],
        metrics=["clean C1 both_match", "clean C0/wrong-owner false attribution", "T3 semantic per dose (source majority)",
                 "T4 false donor full attribution", "T5 false full match", "PSNR/SSIM/LPIPS"],
        budget=dict(max_seconds=int(max_seconds), max_usd=0, hourly_usd=0),
        resources=dict(vram_mib=9000, ram_mib=16000, disk_mib=4000),
        cleanup_policy="stop-for-recovery")


def cmd_manifest(a) -> None:
    m = build_manifest(a.plan, a.run_id, a.max_seconds)
    out = Path(a.out)
    if out.resolve().is_relative_to(ROOT.resolve()):
        raise SystemExit("write the execution manifest outside the repository (keeps the checkout clean)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=1) + "\n", encoding="utf-8")
    plan = json.loads((ROOT / a.plan).read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).replace(microsecond=0)
    approval = dict(schema_version="1.0", experiment_id=m["experiment_id"], run_id=m["run_id"], execution_target="local",
                    manifest_sha256=W.object_digest(m), decision="approve", timestamp=now.isoformat().replace("+00:00", "Z"),
                    expires_at=(now + timedelta(days=7)).isoformat().replace("+00:00", "Z"),
                    max_seconds=m["budget"]["max_seconds"], max_usd=0, actor="<your name>",
                    source_ref=f"chat approval of manifest {W.object_digest(m)[:12]}, core {core_hash(plan)[:12]}, up to 2 infrastructure-only reruns")
    print(json.dumps(dict(manifest=str(out), manifest_sha256=W.object_digest(m), scientific_core_sha256=core_hash(plan),
                          git_commit=m["git_commit"], approval_template=approval), indent=1))


def cmd_rerun_check(a) -> None:
    """Conditions 1-4 of the infrastructure-only rerun allowance, from files only."""
    approved = json.loads(Path(a.approved).read_text(encoding="utf-8"))
    new = json.loads(Path(a.new).read_text(encoding="utf-8"))
    prev = Path(a.previous_run)
    plan_of = lambda m: json.loads((ROOT / next(i["path"] for i in m["inputs"] if i["path"].endswith(".m1b-plan.json"))).read_text(encoding="utf-8"))
    p_old, p_new = plan_of(approved), plan_of(new)
    checks = {}
    checks["1_same_scientific_core"] = W.science_digest(p_old) == W.science_digest(p_new) and \
        json.loads((prev / "outputs/run-context.json").read_text(encoding="utf-8"))["science_digest"] == W.science_digest(p_new)
    changed = subprocess.check_output(["git", "diff", "--name-only", approved["git_commit"], new["git_commit"]], cwd=ROOT, text=True).split()
    checks["2_changed_paths_are_harness"] = not set(changed) & set(W.CODE_FILES)
    run = prev / "outputs/run.json"
    status = json.loads(run.read_text(encoding="utf-8"))["status"] if run.exists() else "no run.json"
    checks["3_previous_incomplete_and_preserved"] = status != "finished" and (prev / "outputs/journal.jsonl").exists()
    checks["4_not_scientific_validation_failure"] = "see the retained failure record; reviewer confirms"
    checks["6_same_budget"] = new["budget"] == approved["budget"]
    print(json.dumps(dict(checks=checks, changed_paths=changed, previous_status=status,
                          resume_from=p_new.get("resume_from")), indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest")
    m.add_argument("--plan", required=True)
    m.add_argument("--run-id", required=True)
    m.add_argument("--max-seconds", type=int, required=True)
    m.add_argument("--out", required=True)
    r = sub.add_parser("rerun-check")
    r.add_argument("--approved", required=True)
    r.add_argument("--new", required=True)
    r.add_argument("--previous-run", required=True)
    a = ap.parse_args()
    (cmd_manifest if a.cmd == "manifest" else cmd_rerun_check)(a)


if __name__ == "__main__":
    main()
