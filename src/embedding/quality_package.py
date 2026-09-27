"""Fixed C4 retained-pair recipe/custody checks. Import is stdlib-only.

This supplements, never replaces, the official runner's approval and clean
commit checks. No execution toggle, datasets, model import or download here.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from src.runtime.config import strict_json_bytes

EXPERIMENT = "c4-saved-pair-quality-development-v1"
RUN = "c4-saved-pair-dev-001"
SPEC = "experiments/" + EXPERIMENT
ENV = "experiments/c4-embedding-development-v1/environment.json"
SCRIPT = "scripts/run_c4_saved_pair.py"
CHILD = "scripts/c4_saved_pair.py"
OUTPUTS = ["outputs/saved-pair-quality.json", "logs/saved-pair-progress.jsonl",
           "logs/saved-pair-launcher.jsonl"]
METRICS = ["mse_rgb01", "psnr_db", "ssim_rgb", "lpips_alex_v01", "q_hamming", "h_hamming"]
BUDGET = {"max_seconds": 1200, "max_usd": 0, "hourly_usd": 0}
RESOURCES = {"vram_mib": 4096, "ram_mib": 6144, "disk_mib": 1024}
REQUIRED = frozenset({SCRIPT, CHILD, "scripts/prepare_c4_saved_pair.py",
    "src/__init__.py", "src/embedding/__init__.py", "src/data/__init__.py",
    "src/runtime/__init__.py", "src/signatures/__init__.py", "src/runtime/config.py",
    "src/embedding/quality.py", "src/embedding/quality_package.py",
    "src/data/preprocess.py", "src/signatures/semantic.py", "src/signatures/instance.py",
    "src/signatures/owner.py", "scripts/a6_clip_visual.py", "configs/data.json",
    "configs/c4-development.json", ENV, SPEC + "/experiment-spec.yaml",
    "research/c4-saved-pair-quality-design-20260927.md"})
PRIOR = ".thesis-build/c4-runs/C4-development/c4-embedding-dev-003"
ASSETS = ".thesis-build/assets/a6"
TRIAL = "outputs/c4-trial-06yo3so7/"
FILES = {
    "source": ("checkpoints/source-snapshot.bin", 125000,
               "8fafbfb6d1c320f9efc59291748c0b9a730726db311364c03280b2de39fe656f"),
    "control": (TRIAL + "matched_control.png", 293695,
                "53aceddd708642bb26c9fbd5393670282d7feb813cfab0aece824305a0b71d2c"),
    "candidate": (TRIAL + "marked_candidate.png", 293660,
                  "3d561c3b431943096a06e65abffb46eea2b0cd97b52e55893c38b12f6ed27289"),
}
PIXELS = {
    "source": "b1a1f8710eb0a60875240b8ab5daf4c0475ba3a7549946a833dccae49a8f4a97",
    "control": "9c22104e1382176aff0d97811601f893684b6f9e9144d1e6093a97f6f28ea9ba",
    "candidate": "54627a82f7d99ee608fbc10c012edc881d5ba2c7801fbfcbc2d80a8855557f33",
}
CONFIG_SHA = "27bedaf1cd7f848ecc9b5b4a76ebe3ca3189c5da099fb3a4a00fac29063b216b"
OWNER = "c4-public-development-owner-v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def sha(raw): return hashlib.sha256(raw).hexdigest()


def unlinked(path):
    path = Path(path)
    if not path.is_absolute() or any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)):
        raise ValueError("absolute unlinked paths required")
    return path


def read(path, maximum=2*1024*1024):
    path = unlinked(path)
    if not path.is_file() or path.stat().st_size > maximum:
        raise ValueError("missing/oversized retained input")
    with path.open("rb") as stream:
        raw = stream.read(maximum+1)
    if len(raw) > maximum: raise ValueError("input grew beyond bound")
    return raw


def checked(path, digest, size=None):
    raw = read(path, maximum=size if size is not None else 2*1024*1024)
    if (size is not None and len(raw) != size) or sha(raw) != digest:
        raise ValueError("retained input digest/size mismatch")
    return raw


def recipe(manifest, snapshots):
    expected = {"experiment_id": EXPERIMENT, "run_id": RUN, "stage_id": "C4-quality-development",
                "task_id": "C4", "execution_target": "local", "seeds": [0],
                "reviewed_script": SCRIPT, "outputs": OUTPUTS, "metrics": METRICS,
                "budget": BUDGET, "resources": RESOURCES, "cleanup_policy": "stop-for-recovery"}
    if any(canonical(manifest.get(k)) != canonical(v) for k, v in expected.items()):
        raise ValueError("unexpected fixed saved-pair recipe")
    if set(snapshots) != REQUIRED:
        raise ValueError("exact transitive inventory required")
    if sha(snapshots["configs/c4-development.json"]) != CONFIG_SHA:
        raise ValueError("retained method config changed")
    if manifest.get("script_sha256") != sha(snapshots[SCRIPT]):
        raise ValueError("saved-pair launcher digest mismatch")
    spec = strict_json_bytes(snapshots[SPEC + "/experiment-spec.yaml"])
    if canonical(manifest.get("datasets")) != canonical(spec["datasets"]):
        raise ValueError("dataset identity differs from prospective spec")


def inputs(raw, root):
    root = unlinked(root)
    if len(raw) > 2*1024*1024: raise ValueError("oversized manifest")
    manifest = strict_json_bytes(raw)
    if type(manifest) is not dict or type(manifest.get("inputs")) is not list:
        raise ValueError("malformed manifest")
    commit = manifest.get("git_commit")
    if type(commit) is not str or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("exact commit required")
    pins, snapshots = {}, {}
    for item in manifest["inputs"]:
        if type(item) is not dict or set(item) != {"path", "sha256"}:
            raise ValueError("malformed input pin")
        name, digest = item["path"], item["sha256"]
        if (type(name) is not str or name not in REQUIRED or
                str(PurePosixPath(name)) != name or name in pins or
                type(digest) is not str or len(digest) != 64 or
                any(c not in "0123456789abcdef" for c in digest)):
            raise ValueError("unknown/aliased/duplicate input")
        snapshots[name] = checked(root/name, digest)
        pins[name] = digest
    recipe(manifest, snapshots)
    return manifest, snapshots, pins


def retained(stable):
    """Only metadata and byte custody, before any pixel/model computation."""
    prior = unlinked(stable/PRIOR)
    record = strict_json_bytes(checked(prior/"manifest.json",
        "e3b54a21cc594a6eacd445b2f6772ebf97ed0e579275cee20339e6c324c40539"))
    if record.get("status") != "completed":
        raise ValueError("prior run not terminal completed")
    pair = strict_json_bytes(checked(prior/(TRIAL+"pair.json"),
        "8f160985ad0eca3b0a5a62ab1de5b97e7f4e67146d802848586997e6560ad86b"))
    if pair.get("status") != "saved_pair_pending_metrics_and_blind_verification":
        raise ValueError("unexpected prior pair")
    rows = pair["rows"]
    if len(rows) != 2 or any(row.get("safety_flagged") is not False for row in rows):
        raise ValueError("prior pair safety/profile incomplete")
    trajectory = checked(prior/(TRIAL+"trajectory.jsonl"),
        "7b024cb2ce6bb5f8a11d5a39625d6882fc22842d0c7db30fa5ec80f5bb0507a7")
    enrollment = strict_json_bytes(trajectory.splitlines()[0])["enrollment"]
    expected = {"q": "5f0f", "h": "40a9a967", "OwnerID": OWNER,
        "Ws": "a19372203dc6735b3ff30701e87572a5bd82a5df312ab80fd2e3e85c55378b54",
        "Wi": "ad6fc565f4c3068dc333561de41339a6729889080514dd1309feb10481db1015"}
    if any(enrollment.get(k) != v for k, v in expected.items()):
        raise ValueError("prior source enrollment mismatch")
    snapshots = {name: checked(prior/relative, digest, size)
                 for name, (relative, size, digest) in FILES.items()}
    return snapshots, expected
