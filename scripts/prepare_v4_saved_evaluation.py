"""Read-only metadata builder: exact CPU evaluation and harmless host preflight."""
import argparse
import json
from pathlib import Path
import subprocess
from v4_evaluation_journal import file_sha, object_sha

ROOT = Path(__file__).resolve().parents[1]
EXP = "c4-v4-three-threat-recovery-v1"


def state():
    if subprocess.check_output(["git","-C",str(ROOT),"status","--porcelain"],text=True).strip():
        raise ValueError("exact clean code commit required")
    return subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()


def files():
    names = ["revised_watermark_v4.py","revised_watermark_v3.py","revised_watermark.py",
             "qim_rgb_pilot.py","a6_clip_visual.py","verify_science_assets.py","check_a6_lpips_assets.py",
             "three_threat_protocol.py","three_threat_models.py","v4_study_protocol.py","run_v4_study.py",
             "v4_recovery_design.py","v4_evaluation_journal.py","v4_saved_evaluation_adapter.py",
             "v4_saved_evaluation_worker.py","run_v4_saved_evaluation.py","v4_durable_host.py",
             "v4_host_fixture.py","prepare_v4_saved_evaluation.py","test_v4_evaluation_journal.py",
             "test_v4_saved_evaluation.py","test_v4_recovery_design.py"]
    result = ["scripts/"+name for name in names]
    result += ["research/a6-candidate-model-assets.json","research/research-contract.md","research/scope-guard.md",
               "research/proposal-aligned-plan-20260930.md","research/method-amendment-v4.md",
               "research/method-amendment-decision-20261001.md","experiments/c4-v4-three-threat-small-v1/profile.json",
               "experiments/c4-v4-three-threat-small-v1/acceptance-criteria.md",
               "experiments/c4-three-threat-small-v1/runtime-files-v2.json",
               "experiments/c4-three-threat-small-v1/semantic-labels.json"]
    result += [p.relative_to(ROOT).as_posix() for p in (ROOT/"experiments"/EXP).iterdir() if p.is_file()]
    return sorted(set(result))


def base(run, stage, script, budget, resources):
    spec = json.loads((ROOT/"experiments"/EXP/"experiment-spec.yaml").read_text())
    return {"schema_version":"1.0","experiment_id":EXP,"run_id":run,"stage_id":stage,"task_id":"C4",
            "execution_target":"local","reviewed_script":"scripts/"+script,
            "script_sha256":file_sha(ROOT/"scripts"/script),"git_commit":state(),"seeds":[0,1,2],
            "datasets":spec["datasets"],"inputs":[{"path":p,"sha256":file_sha(ROOT/p)} for p in files()],
            "budget":budget,"resources":resources,"cleanup_policy":"stop-for-recovery"}


def build_fixture():
    result = base("c4-v4-recovery-host-check-003","C4-v4-recovery-host-preflight","v4_host_fixture.py",
                  {"max_seconds":60,"max_usd":0,"hourly_usd":0},{"ram_mib":128,"vram_mib":0,"disk_mib":16})
    result.update(outputs=["outputs/fixture.json","outputs/survival.json"],metrics=["model_free_detached_official_runner_survival"])
    return result


def build():
    lock = json.loads((ROOT/"experiments"/EXP/"parent-input-lock.json").read_text())
    parent = Path(lock["parent_root"])
    for item in lock["artifacts"]:
        path = parent/item["path"]
        if not path.resolve().is_relative_to(parent.resolve()) or file_sha(path) != item["sha256"]:
            raise ValueError("parent artifact changed")
    result = base("c4-v4-saved-evaluation-003","C4-v4-saved-evaluation","run_v4_saved_evaluation.py",
                  {"max_seconds":86400,"max_usd":0,"hourly_usd":0},{"ram_mib":6144,"vram_mib":0,"disk_mib":2048})
    result.update(outputs=["outputs/results.json","outputs/runtime.json","outputs/heartbeat.json",
                           "outputs/artifact-index.json","logs/evaluation-worker.log"],
                  metrics=["rgb_quality","saved_suspect_clip_dual_channel_detection",
                           "semantic_instance_diagnostics","atomic_evaluated_unit_completion"])
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture",action="store_true")
    args = parser.parse_args()
    print(json.dumps(build_fixture() if args.fixture else build(),sort_keys=True,indent=2))
