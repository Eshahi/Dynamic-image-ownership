"""Exact same-start continuation recipe; no scientific authorization."""
import struct
from . import quality_package as custody
from .validation_bridge import REQUIRED as VALIDATION, check_inputs
from .decoder_continuation import ARMS, ContinuationPolicy
from .latent_refinement import RefinementPolicy
from .adaptive_refinement import AdaptivePolicy

EXPERIMENT = "c4-decoder-continuation-development-v1"
RUN = "c4-decoder-continuation-dev-001"
STAGE = "C4-decoder-continuation-development"
SPEC = "experiments/"+EXPERIMENT
SCRIPT = "scripts/run_c4_continuation.py"
CHILD = "scripts/c4_continuation.py"
POLICY = "configs/c4-decoder-continuation.json"
RETENTION = "research/c4-continuation-inputs-20260927.json"
OUTPUTS = ["outputs/continuation.json", "logs/continuation-progress.jsonl", "logs/continuation-launcher.jsonl",
           *["outputs/"+arm+".png" for arm in ARMS]]
METRICS = ["mse_rgb01", "psnr_db", "ssim_rgb", "lpips_alex_v01", "q_hamming", "h_hamming",
           "retained_start_pixel_replay", "final_gradient_l2", "decoder_evaluations"]
BUDGET = {"max_seconds": 3600, "max_usd": 0, "hourly_usd": 0}
RESOURCES = {"vram_mib": 9216, "ram_mib": 12288, "disk_mib": 4096}
REQUIRED = custody.REQUIRED | VALIDATION | frozenset({SCRIPT, CHILD, POLICY, RETENTION,
    "scripts/prepare_c4_continuation.py", "src/embedding/continuation_package.py",
    "src/embedding/decoder_continuation.py", "src/embedding/adaptive_refinement.py",
    "src/embedding/latent_refinement.py", "src/embedding/inversion.py", "src/embedding/inversion_path.py",
    "src/embedding/proposed.py", "src/embedding/local_assets.py", "src/embedding/residency.py",
    "src/embedding/checkpointing.py", "scripts/verify_science_assets.py",
    "scripts/base_noise_reference.py", "scripts/pixel_dct_control.py",
    "research/a6-candidate-model-assets.json", SPEC+"/experiment-spec.yaml",
    "research/c4-decoder-continuation-design-20260927.md"})
PARAMETERS = {"profile": "same-start-original-anchor-decoder-continuation-long-v2", "arms": list(ARMS),
    "control": {"iterations": 512, "maximum_evaluations": 2049, "maximum_backtracks": 2,
        "learning_rate": 1., "maximum_displacement_l2": 80., "latent_penalty": 0.,
        "mse_tolerance": .0003, "maximum_seconds": 1500.},
    "adaptive": {"iterations": 512, "maximum_evaluations": 2049, "maximum_backtracks": 16,
        "initial_step": .25, "minimum_step": 2**-16, "maximum_step": 1., "armijo": .0001,
        "radius_l2": 80., "gradient_tolerance": 1e-12, "objective_tolerance": .0003,
        "maximum_seconds": 1500.}, "maximum_seconds": 3060.}
PARENT = ".thesis-build/c4-runs/C4-refined-target-development/c4-refined-target-dev-001"
PINS = {
    "manifest.json": "2d3cde49d1c0857e0464002e6a863771f7d556859c57d7724fb8d5aa4e9baa21",
    "outputs/refinement.json": "c63202c36206ee251338417f62d1006cf37f1f32e46fedffaeea50fff57fc794",
    "logs/refinement-progress.jsonl": "11fba38f0263db064fef5e9be6d711307496717fc83a695bdeaf44ee9193a8aa"}
STATES = {
    "anchor": {"path": "checkpoints/refinement-states/000000-shared_encoded.safetensors", "size": 49232,
        "sha256": "639a54905c50ac272461e96c037b9102fcd7baf5fb60c2c6b9f30e5f7c32fce8"},
    "start": {"path": "checkpoints/refinement-states/000152-decoder_refinement.safetensors", "size": 49232,
        "sha256": "2d951881fd40debc224b3e394b8fbad50ed19d5438bb53fa36e074bc35ff7639"}}
START_PIXELS = "d0aa90492602edf7579221f4aad61d52def1642a22b3db5bf91b13cbec83226b"
CUSTODY = {"parent": PARENT, "parent_status": "failed", "metadata_sha256": PINS,
    "states": STATES, "tensor": {"key": "latent", "dtype": "F32", "shape": [1, 4, 48, 64]},
    "start_pixel_sha256": START_PIXELS, "constraint": "original_encoded_anchor_radius80_not_recentered"}


def policy(raw):
    values = custody.strict_json_bytes(raw)
    if custody.canonical(values) != custody.canonical(PARAMETERS):
        raise ValueError("fixed continuation policy changed")
    return ContinuationPolicy(RefinementPolicy(**values["control"]), AdaptivePolicy(**values["adaptive"]),
                              values["maximum_seconds"])


def inputs(raw, root):
    manifest, snapshots, pins = check_inputs(raw, root)
    expected = {"experiment_id": EXPERIMENT, "run_id": RUN, "stage_id": STAGE, "task_id": "C4",
        "execution_target": "local", "seeds": [0], "reviewed_script": SCRIPT, "outputs": OUTPUTS,
        "metrics": METRICS, "budget": BUDGET, "resources": RESOURCES, "cleanup_policy": "stop-for-recovery"}
    if any(custody.canonical(manifest.get(k)) != custody.canonical(v) for k, v in expected.items()):
        raise ValueError("unexpected fixed continuation recipe")
    if set(snapshots) != REQUIRED or pins["configs/c4-development.json"] != custody.CONFIG_SHA:
        raise ValueError("continuation inventory/historical config changed")
    if manifest.get("script_sha256") != pins[SCRIPT]: raise ValueError("launcher digest mismatch")
    policy(snapshots[POLICY])
    if custody.canonical(custody.strict_json_bytes(snapshots[RETENTION])) != custody.canonical(CUSTODY):
        raise ValueError("continuation retained-input contract changed")
    spec = custody.strict_json_bytes(snapshots[SPEC+"/experiment-spec.yaml"])
    if custody.canonical(manifest.get("datasets")) != custody.canonical(spec["datasets"]):
        raise ValueError("continuation source identity mismatch")
    return manifest, snapshots, pins


def state_header(raw):
    """Bounded safetensors structure check only, never arbitrary pickle loading."""
    if len(raw) != 49232: raise ValueError("retained state length changed")
    length, = struct.unpack("<Q", raw[:8])
    if not 2 <= length <= 4096: raise ValueError("retained state header length")
    header = custody.strict_json_bytes(raw[8:8+length])
    if (header != {"latent": {"dtype": "F32", "shape": [1, 4, 48, 64], "data_offsets": [0, 49152]}}
            or len(raw)-8-length != 49152):
        raise ValueError("retained state tensor profile changed")
    return header


def retained_states(stable):
    """Return checked in-memory bytes. Failed parent remains failed, not resumed."""
    root = custody.unlinked(stable/PARENT)
    metadata = {name: custody.checked(root/name, digest) for name, digest in PINS.items()}
    runner = custody.strict_json_bytes(metadata["manifest.json"])
    report = custody.strict_json_bytes(metadata["outputs/refinement.json"])
    if runner.get("status") != "failed" or report.get("status") != "failed_retained_partial":
        raise ValueError("failed parent terminal identity changed")
    if (report.get("run_id") != "c4-refined-target-dev-001"
            or report.get("git_commit") != "dd347afb861774f7a86138e7170dba96d4f47044"
            or report["arms"]["decoder_refinement"]["pixel_sha256"] != START_PIXELS):
        raise ValueError("failed parent source/state identity changed")
    result = {}
    for role, entry in STATES.items():
        raw = custody.checked(root/entry["path"], entry["sha256"], entry["size"])
        state_header(raw); result[role] = raw
    return result
