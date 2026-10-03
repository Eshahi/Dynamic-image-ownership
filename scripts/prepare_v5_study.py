"""Metadata-only v5 two-tier study manifest builder; no human decision and no model execution.

``--rehearsal`` builds the manifest of the synthetic rehearsal: same inputs, the
rehearsal run identity, and a dataset entry that names the generated stand-ins.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from v5_study_limits import BUDGET

ROOT=Path(__file__).resolve().parents[1]
EXP="c4-v5-two-tier-regeneration-v1"
RUN="c4-v5-two-tier-dev-001"
REHEARSAL_RUN=RUN+"-rehearsal"


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def build(rehearsal=False):
    if subprocess.check_output(["git","-C",str(ROOT),"status","--porcelain"],text=True).strip():
        raise ValueError("clean exact commit required")
    commit=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    package=ROOT/"experiments"/EXP
    old=ROOT/"experiments/c4-three-threat-small-v1"
    spec=json.loads((package/"experiment-spec.yaml").read_text())
    cases=json.loads((ROOT/"experiments/c4-qim-rgb-development-v1/cohort.json").read_text())["cases"]
    cases+=json.loads((old/"development-expansion.json").read_text())["new_cases"]
    if not rehearsal:  # a rehearsal reads no study image, not even to hash it
        for c in cases:
            if sha(c["path"])!=c["raw_sha256"]:
                raise ValueError("reserved source bytes differ")
    scripts=["revised_watermark_v5.py","revised_watermark_v4.py","revised_watermark.py",
             "qim_rgb_pilot.py","a6_clip_visual.py","verify_science_assets.py","check_a6_lpips_assets.py",
             "three_threat_protocol.py","three_threat_models.py","v5_study_protocol.py",
             "v4_study_models.py","v4_study_boundary.py","v5_study_worker.py","run_v5_study.py","prepare_v5_study.py",
             "analyze_v5_study.py","test_revised_watermark_v5.py","test_revised_watermark_v4.py","test_v5_study.py",
             "watermark_synthetic.py", "v5_study_limits.py", "test_v5_limits.py"]
    files=["scripts/"+p for p in scripts]
    files+=["research/a6-candidate-model-assets.json","research/proposal-aligned-plan-20260930.md",
            "research/method-amendment-v5.md","research/method-amendment-decision-20261002.md",
            "research/method-amendment-v4.md","research/research-contract.md","research/scope-guard.md",
            "research/redesign-inputs/literature-verification-20261002.md",
            "configs/revised-watermark-v5.example.json","configs/revised-watermark-v5-keyed.example.json",
            "configs/revised-watermark-v5.schema.json","configs/revised-watermark.example.json",
            "experiments/c4-qim-rgb-development-v1/cohort.json"]
    files += ["experiments/c4-three-threat-small-v1/"+p for p in
              ["development-expansion.json","semantic-labels.json","runtime-files-v2.json"]]
    files += [p.relative_to(ROOT).as_posix() for p in package.iterdir() if p.is_file()]
    datasets=spec["datasets"]
    if rehearsal:
        datasets=[{"id":"synthetic-rehearsal-hosts","version":"twelve images generated locally from fixed prompts and seeds by scripts/dev_v5_channel_probe.py",
                   "license":"generated for rehearsal; no study image","split":"rehearsal only; no scientific evidence"}]
    return {"schema_version":"1.0","experiment_id":EXP,"run_id":REHEARSAL_RUN if rehearsal else RUN,
            "stage_id":"C4-v5-two-tier-rehearsal" if rehearsal else "C4-v5-two-tier-development",
            "task_id":"C4","execution_target":"local","reviewed_script":"scripts/run_v5_study.py",
            "script_sha256":sha(ROOT/"scripts/run_v5_study.py"),"git_commit":commit,"seeds":[0,1,2],
            "datasets":datasets,"inputs":[{"path":p,"sha256":sha(ROOT/p)} for p in sorted(set(files))],
            "outputs":["outputs/results.json","outputs/runtime.json","logs/study-worker.log"],
            "metrics":["rgb_quality","suspect_only_clip_two_tier_detection","regeneration_dose_response",
                       "ordinary_processing_supplementary","transfer_delivery_binding_false_attribution",
                       "semantic_instance_code_distances"],
            "budget":dict(BUDGET),
            "resources":{"vram_mib":8192,"ram_mib":6144,"disk_mib":2048},
            "cleanup_policy":"stop-for-recovery"}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",required=True)
    parser.add_argument("--rehearsal",action="store_true")
    args=parser.parse_args()
    destination=Path(args.out).resolve()
    if destination.is_relative_to(ROOT):
        raise ValueError("store manifest outside clean checkout")
    manifest=build(args.rehearsal)
    with destination.open("x",encoding="utf-8") as f:
        json.dump(manifest,f,sort_keys=True,indent=2,allow_nan=False)
        f.write("\n")
    canonical=json.dumps(manifest,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    print(json.dumps({"manifest_sha256":hashlib.sha256(canonical).hexdigest(),
                      "git_commit":manifest["git_commit"],"run_id":manifest["run_id"],"execute":False}))
