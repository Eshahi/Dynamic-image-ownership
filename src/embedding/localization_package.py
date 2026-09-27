"""Exact prospective three-arm C4 recipe, not approval or execution."""
from . import quality_package as custody
from .validation_bridge import REQUIRED as VALIDATION, check_inputs

EXPERIMENT = "c4-reconstruction-localization-development-v1"
RUN = "c4-reconstruction-dev-001"
SPEC = "experiments/" + EXPERIMENT
SCRIPT = "scripts/run_c4_localization.py"
CHILD = "scripts/c4_localization.py"
OUTPUTS = ["outputs/localization.json", "logs/localization-progress.jsonl", "logs/localization-launcher.jsonl",
           *["outputs/" + arm + ".png" for arm in ("vae_only", "ddim_zero_noise", "ddim_fixed_base_noise")]]
METRICS = ["mse_rgb01", "psnr_db", "ssim_rgb", "lpips_alex_v01", "matched_control_pixel_replay"]
BUDGET = {"max_seconds": 1200, "max_usd": 0, "hourly_usd": 0}
RESOURCES = {"vram_mib": 9216, "ram_mib": 12288, "disk_mib": 4096}
REQUIRED = custody.REQUIRED | VALIDATION | frozenset({SCRIPT, CHILD,
    "scripts/prepare_c4_localization.py", "src/embedding/localization_package.py",
    "src/embedding/reconstruction.py", "src/embedding/proposed.py",
    "src/embedding/local_assets.py", "src/embedding/residency.py", "src/embedding/checkpointing.py",
    "scripts/verify_science_assets.py", "scripts/base_noise_reference.py", "scripts/pixel_dct_control.py",
    "research/a6-candidate-model-assets.json", SPEC+"/experiment-spec.yaml",
    "research/c4-reconstruction-localization-design-20260927.md"})


def inputs(raw, root):
    manifest, snapshots, pins = check_inputs(raw, root)
    expected = {"experiment_id": EXPERIMENT, "run_id": RUN, "stage_id": "C4-localization-development",
        "task_id": "C4", "execution_target": "local", "seeds": [0], "reviewed_script": SCRIPT,
        "outputs": OUTPUTS, "metrics": METRICS, "budget": BUDGET, "resources": RESOURCES,
        "cleanup_policy": "stop-for-recovery"}
    if any(custody.canonical(manifest.get(k)) != custody.canonical(v) for k,v in expected.items()):
        raise ValueError("unexpected fixed localization recipe")
    if set(snapshots) != REQUIRED or pins["configs/c4-development.json"] != custody.CONFIG_SHA:
        raise ValueError("localization inventory/config changed")
    if manifest.get("script_sha256") != pins[SCRIPT]: raise ValueError("launcher digest mismatch")
    spec = custody.strict_json_bytes(snapshots[SPEC+"/experiment-spec.yaml"])
    if custody.canonical(manifest.get("datasets")) != custody.canonical(spec["datasets"]):
        raise ValueError("localization source identity mismatch")
    return manifest, snapshots, pins
