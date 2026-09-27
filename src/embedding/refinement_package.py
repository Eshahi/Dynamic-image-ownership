"""Fixed prospective six-arm recipe, not execution authorization."""
from . import quality_package as custody
from .validation_bridge import REQUIRED as VALIDATION, check_inputs
from .refinement_comparison import ARMS, RefinementComparisonPolicy
from .latent_refinement import RefinementPolicy
from .inversion import InversionPolicy

EXPERIMENT = "c4-refined-target-reconstruction-development-v1"
RUN = "c4-refined-target-dev-001"
STAGE = "C4-refined-target-development"
SPEC = "experiments/"+EXPERIMENT
SCRIPT = "scripts/run_c4_refinement.py"
CHILD = "scripts/c4_refinement.py"
POLICY = "configs/c4-refinement-comparison.json"
OUTPUTS = ["outputs/refinement.json", "logs/refinement-progress.jsonl", "logs/refinement-launcher.jsonl",
           *["outputs/"+arm+".png" for arm in ARMS]]
METRICS = ["mse_rgb01", "psnr_db", "ssim_rgb", "lpips_alex_v01", "q_hamming", "h_hamming",
           "matched_control_pixel_replay", "roundtrip_residual_max"]
BUDGET = {"max_seconds": 1200, "max_usd": 0, "hourly_usd": 0}
RESOURCES = {"vram_mib": 9216, "ram_mib": 12288, "disk_mib": 4096}
REQUIRED = custody.REQUIRED | VALIDATION | frozenset({SCRIPT, CHILD, POLICY,
    "scripts/prepare_c4_refinement.py", "src/embedding/refinement_package.py",
    "src/embedding/refinement_comparison.py", "src/embedding/latent_refinement.py",
    "src/embedding/inversion.py", "src/embedding/inversion_path.py",
    "src/embedding/proposed.py", "src/embedding/local_assets.py", "src/embedding/residency.py",
    "src/embedding/checkpointing.py", "scripts/verify_science_assets.py",
    "scripts/base_noise_reference.py", "scripts/pixel_dct_control.py",
    "research/a6-candidate-model-assets.json", SPEC+"/experiment-spec.yaml",
    "research/c4-refined-target-execution-design-20260927.md"})
PARAMETERS = {"profile": "c4-six-arm-refined-terminal-v1", "arms": list(ARMS),
    "refinement": {"iterations": 64, "maximum_evaluations": 257, "maximum_backtracks": 2,
        "learning_rate": 1., "maximum_displacement_l2": 80., "latent_penalty": 0.,
        "mse_tolerance": .0003, "maximum_seconds": 720.},
    "inverse": {"method": "fixed_point", "max_evaluations": 32, "residual_tolerance": 1e-5,
        "damping": 1., "denominator_eta": 1e-6, "maximum_coordinate_step": 1.,
        "max_backtracks": 8, "prior_weight": 0., "prior_beta": 1.},
    "maximum_evaluations_per_inverse_arm": 128, "maximum_seconds": 1000., "roundtrip_tolerance": 1e-5}


def policy(raw):
    values = custody.strict_json_bytes(raw)
    if custody.canonical(values) != custody.canonical(PARAMETERS):
        raise ValueError("fixed prospective refinement policy changed")
    return RefinementComparisonPolicy(RefinementPolicy(**values["refinement"]),
        InversionPolicy(**values["inverse"]), values["maximum_evaluations_per_inverse_arm"],
        values["maximum_seconds"], values["roundtrip_tolerance"])


def inputs(raw, root):
    manifest, snapshots, pins = check_inputs(raw, root)
    expected = {"experiment_id": EXPERIMENT, "run_id": RUN, "stage_id": STAGE,
        "task_id": "C4", "execution_target": "local", "seeds": [0], "reviewed_script": SCRIPT,
        "outputs": OUTPUTS, "metrics": METRICS, "budget": BUDGET, "resources": RESOURCES,
        "cleanup_policy": "stop-for-recovery"}
    if any(custody.canonical(manifest.get(k)) != custody.canonical(v) for k, v in expected.items()):
        raise ValueError("unexpected fixed refined-target recipe")
    if set(snapshots) != REQUIRED or pins["configs/c4-development.json"] != custody.CONFIG_SHA:
        raise ValueError("refined-target inventory or historical config changed")
    if manifest.get("script_sha256") != pins[SCRIPT]: raise ValueError("launcher digest mismatch")
    policy(snapshots[POLICY])
    spec = custody.strict_json_bytes(snapshots[SPEC+"/experiment-spec.yaml"])
    if custody.canonical(manifest.get("datasets")) != custody.canonical(spec["datasets"]):
        raise ValueError("refined-target source identity mismatch")
    return manifest, snapshots, pins
