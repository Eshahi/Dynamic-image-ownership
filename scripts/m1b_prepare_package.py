"""Prepare the M1b execution manifest, its scientific-core hash and the approval question.

    python scripts/m1b_prepare_package.py manifest --plan research/m1b-coco512-test.m1b-plan.json \
        --run-id coco512-confirm-1 --max-seconds 28800 --out <outside the repo>/execution-manifest.json
    python scripts/m1b_prepare_package.py rerun-check --approved <approved manifest> --approval <its approval> \
        --new <new manifest> --previous-run <artifact dir of the interrupted attempt>

This script never writes an approval. For a test plan it prints the template the user saves
as their own approval; the question it answers covers the manifest hash, the scientific-core
hash and up to 2 continuations that reuse the journal of the interrupted approved run
(`research/approval-policy.md`, infrastructure-only rerun allowance).
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


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def build_manifest(plan_path: str, run_id: str, max_seconds: int) -> tuple[dict, dict]:
    plan = json.loads((ROOT / plan_path).read_text(encoding="utf-8"))
    W.validate_plan(plan)
    if git("status", "--porcelain"):
        raise SystemExit("clean checkout required")
    core = W.scientific_core(plan)
    inputs = sorted({plan_path, *core["data_sha256"]})
    split = plan["data_split"]
    test = split == "test"
    manifest = dict(
        schema_version="1.0", experiment_id=f"M1b-coco512-{split}", run_id=run_id,
        stage_id=f"M1b-{split}", task_id="coco512-f5r2-v5r3", execution_target="local",
        reviewed_script=W.ENTRY, script_sha256=sha(ROOT / W.ENTRY), git_commit=git("rev-parse", "HEAD"),
        seeds=list(W.SEEDS),
        datasets=[dict(id="ms-coco", version="coco-2017 val2017 (study_split=test, frozen 300 representatives)",
                       license="images: per-image Flickr licences, rights pending, local research only; annotations CC-BY-4.0",
                       split="test")] if test else
                 [dict(id=f"{split}-sources", version=plan.get("label", split)[:120], license="synthetic or development reservation",
                       split=split)],
        inputs=[dict(path=p, sha256=sha(ROOT / p)) for p in inputs],
        outputs=["outputs/run.json", "outputs/journal.jsonl", "outputs/run-context.json", "outputs/lineage.json",
                 "metrics/endpoints.json"],
        metrics=["clean C1 both_match", "clean C0/wrong-owner any_found (primary) and both_match",
                 "T3 semantic per dose and seed (source majority)", "T4 false donor full attribution",
                 "T5 false full match", "PSNR/SSIM/LPIPS"],
        budget=dict(max_seconds=int(max_seconds), max_usd=0, hourly_usd=0),
        resources=dict(vram_mib=9000, ram_mib=16000, disk_mib=4000),
        cleanup_policy="stop-for-recovery")
    return manifest, core


def cmd_manifest(a) -> None:
    m, core = build_manifest(a.plan, a.run_id, a.max_seconds)
    out = Path(a.out)
    if W.under(out, ROOT):
        raise SystemExit("write the execution manifest outside the repository (keeps the checkout clean)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=1) + "\n", encoding="utf-8")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    template = dict(schema_version="1.0", experiment_id=m["experiment_id"], run_id=m["run_id"], execution_target="local",
                    manifest_sha256=W.object_digest(m), decision="approve",
                    timestamp=now.isoformat().replace("+00:00", "Z"),
                    expires_at=(now + timedelta(days=7)).isoformat().replace("+00:00", "Z"),
                    max_seconds=m["budget"]["max_seconds"], max_usd=0, actor="<your name>",
                    source_ref=(f"approve manifest {W.object_digest(m)[:16]}, scientific core {core['core_sha256'][:16]}, "
                                "and up to 2 continuations that reuse the journal of this run if it is interrupted"))
    print(json.dumps(dict(manifest=str(out), manifest_sha256=W.object_digest(m), scientific_core_sha256=core["core_sha256"],
                          git_commit=m["git_commit"], code_files=len(core["code_sha256"]),
                          approval_template=template), indent=1))


def core_at(commit: str, plan: dict) -> dict:
    def read(p):
        try:
            return subprocess.check_output(["git", "show", f"{commit}:{p}"], cwd=ROOT, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return None
    return W.scientific_core(plan, read_bytes=read)


def cmd_rerun_check(a) -> None:
    approved = json.loads(Path(a.approved).read_text(encoding="utf-8"))
    approval = json.loads(Path(a.approval).read_text(encoding="utf-8"))
    new = json.loads(Path(a.new).read_text(encoding="utf-8"))
    prev = Path(a.previous_run)
    plan_of = lambda m, commit: json.loads(subprocess.check_output(
        ["git", "show", f"{commit}:{next(i['path'] for i in m['inputs'] if i['path'].endswith('.m1b-plan.json'))}"], cwd=ROOT))
    p_old, p_new = plan_of(approved, approved["git_commit"]), plan_of(new, new["git_commit"])
    c_old, c_new = core_at(approved["git_commit"], p_old), core_at(new["git_commit"], p_new)
    prev_core = json.loads((prev / "outputs/run-context.json").read_text(encoding="utf-8"))["core_sha256"]
    protected = set(c_new["code_sha256"]) | set(c_new["data_sha256"])
    changed = git("diff", "--name-only", approved["git_commit"], new["git_commit"]).split()
    prev_manifest = json.loads((prev / "manifest.json").read_text(encoding="utf-8")) if (prev / "manifest.json").exists() else {}
    lineage = prev / "outputs/lineage.json"
    depth = 1 + (json.loads(lineage.read_text(encoding="utf-8"))["depth"] if lineage.exists() else 0)
    expires = datetime.fromisoformat(approval["expires_at"].replace("Z", "+00:00"))
    checks = {
        "1_same_scientific_core": c_old["core_sha256"] == c_new["core_sha256"] == prev_core,
        "2_no_core_file_changed": not (set(changed) & protected),
        "3_previous_incomplete_and_preserved": prev_manifest.get("status") not in (None, "completed")
                                               and (prev / "outputs/journal.jsonl").exists(),
        "3b_previous_is_the_approved_run": prev_manifest.get("approval_reference") == W.object_digest(approval)
                                           or prev_manifest.get("approval_reference") == p_new.get("resume_parent_approval_sha256"),
        "3c_new_plan_resumes_previous": bool(p_new.get("resume_from"))
                                        and W.resolve(p_new["resume_from"]).resolve() == prev.resolve(),
        "4_failure_record": prev_manifest.get("errors") or "see outputs/run.json infrastructure_error",
        "5_reviewer": "an identity other than the author confirms this output and the failure record",
        "6_same_budget_and_unexpired_approval": new["budget"] == approved["budget"] and datetime.now(timezone.utc) < expires,
        "6b_continuations_at_most_2": depth <= W.MAX_RESUME_DEPTH,
    }
    print(json.dumps(dict(checks=checks, changed_paths=changed, core_sha256=c_new["core_sha256"], continuation_depth=depth),
                     indent=1, default=str))


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
    r.add_argument("--approval", required=True)
    r.add_argument("--new", required=True)
    r.add_argument("--previous-run", required=True)
    a = ap.parse_args()
    (cmd_manifest if a.cmd == "manifest" else cmd_rerun_check)(a)


if __name__ == "__main__":
    main()
