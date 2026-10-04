"""M1 family A: dual-key DCT transport through an actual optimized VAE latent.

Primary output is only D(z). Optional source-bypass output is a separately
labelled hybrid. The unmodified v5 verifier re-extracts CLIP from each saved
suspect; source features/keys are used only by the embedder and diagnostics.
No diffusion or scientific run starts on import. All supplied cohorts must be
reserved development images. See research/m1-dual-latent-design.md.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ASSETS = MAIN / ".thesis-build/assets/a6"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import revised_watermark_v5 as codec

VERSION = "m1-dual-latent-v1"
CLIP_SOURCE = "external:clip-vit-b32-a6-40d365715913"
DEFAULT_CONFIG = {
    "robust_steps": 60, "joint_steps": 40, "learning_rate": 0.01,
    "quality_psnr_db": 35.2, "quality_weight": 1.0,
    "quality_excess_weight": 10.0, "semantic_weight": 8.0,
    "instance_weight": 4.0, "cycle_weight": 8.0,
    "semantic_margin": 9.0, "instance_margin": 9.0, "cycle_margin": 8.5,
    "cycle_every": 4, "checkpoint_every": 10,
    "initialization": "posterior-mode", "reconstruction_step": 200,
    "routes": ["pure-decoder"], "precision": "float32", "seed": 0,
    "size": [512, 512], "decoder_checkpoint": True,
    "gpu_budget_bytes": 10 * 1024**3, "run_seconds_cap": 3600,
    "owner": "qim-pilot-owner-alpha", "wrong_owner": "qim-pilot-owner-beta",
    "instance_binding": "source-phash-before-watermark",
    "surrogate": "v5-pattern-score-source-fixed-slot-weights",
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024**2), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def validate_config(value):
    if not isinstance(value, dict) or set(value) != set(DEFAULT_CONFIG):
        raise ValueError("Configuration keys must exactly match DEFAULT_CONFIG")
    result = dict(value)
    for name in ("robust_steps", "joint_steps", "cycle_every", "checkpoint_every",
                 "gpu_budget_bytes", "run_seconds_cap", "reconstruction_step"):
        if type(value[name]) is not int or value[name] <= 0:
            raise ValueError(f"{name} must be a positive integer")
    for name in ("learning_rate", "quality_psnr_db", "quality_weight",
                 "quality_excess_weight", "semantic_weight", "instance_weight",
                 "cycle_weight", "semantic_margin", "instance_margin", "cycle_margin"):
        if type(value[name]) not in (int, float) or not math.isfinite(value[name]) or value[name] < 0:
            raise ValueError(f"{name} must be finite and nonnegative")
    if value["learning_rate"] <= 0 or min(value[x] for x in
            ("semantic_margin", "instance_margin", "cycle_margin")) <= 0:
        raise ValueError("Learning rate and score margins must be positive")
    if value["initialization"] not in ("posterior-mode", "reconstruction-checkpoint"):
        raise ValueError("Unknown initialization")
    routes = value["routes"]
    if (not isinstance(routes, list) or not routes or len(set(routes)) != len(routes)
            or any(r not in ("pure-decoder", "hybrid-source-bypass") for r in routes)):
        raise ValueError("Explicit distinct output routes required")
    for name in ("precision", "size", "instance_binding", "surrogate"):
        if value[name] != DEFAULT_CONFIG[name]:
            raise ValueError(f"Unsupported {name}")
    if type(value["decoder_checkpoint"]) is not bool or type(value["seed"]) is not int:
        raise ValueError("Invalid checkpoint or seed type")
    codec.canonical_owner(value["owner"])
    codec.canonical_owner(value["wrong_owner"])
    if value["owner"] == value["wrong_owner"]:
        raise ValueError("Wrong-owner control must differ")
    return result


def dct_basis(*, device="cpu", dtype=None):
    import torch
    dtype = dtype or torch.float32
    n = torch.arange(8, dtype=torch.float64)
    basis = torch.cos(math.pi * (n[None, :] + .5) * n[:, None] / 8) * .5
    basis[0] /= math.sqrt(2)
    return basis.to(device=device, dtype=dtype)


class FixedPatternObjective:
    """Differentiable v5 pattern score; source slot weights held fixed.

    At the source image the projections reproduce v5's source analysis. At
    changed images this is explicitly a training surrogate because the real
    detector recomputes its activity masks and slot weights. Expected patterns
    use source CLIP q and source pHash h, with no iterative re-signing.
    """

    def __init__(self, source_rgb, source_features, owner, profile, device="cpu", dtype=None):
        import numpy as np
        import torch
        dtype = dtype or torch.float32
        source = np.asarray(source_rgb)
        if source.dtype != np.uint8 or source.shape != (512, 512, 3):
            raise ValueError("Objective needs canonical 512x512 RGB8 source")
        if profile.get("semantic_source") != CLIP_SOURCE:
            raise ValueError("CLIP profile required; no implicit layout proxy")
        checked, key, config = codec._resolve(profile, None)
        owner_bytes = codec.canonical_owner(owner)
        luma = codec.luminance_from_rgb(source.tolist())
        self.q = codec.semantic_code(source_features, profile=checked)
        self.h = codec.perceptual_hash(luma, profile=checked)
        ws, wi = codec.derive_keys(self.q, self.h, owner_bytes, key, config)
        robust = codec._Robust(codec._coarse(luma), luma, checked,
            codec._robust_carrier(key, config, owner_bytes, len(checked["robust_frequencies"])))
        fragile = codec._Fragile(checked, key, config, owner_bytes, 512, 512)
        coefficients = codec.base._analyse(luma, fragile.analysis)[1]
        fragile_projections = fragile.projections(coefficients)
        tensor = lambda data: torch.tensor(data, dtype=dtype, device=device)
        indices = lambda data: torch.tensor(data, dtype=torch.long, device=device)
        self.basis = dct_basis(device=device, dtype=dtype)
        self.device, self.dtype = device, dtype
        self.robust_positions = tuple(robust.positions)
        self.instance_positions = tuple(fragile.positions)
        self.rs = indices([p[0] for p in robust.positions]), indices([p[1] for p in robust.positions])
        self.ins = indices([p[0] for p in fragile.positions]), indices([p[1] for p in fragile.positions])
        self.whitening = tensor(robust.weights)
        self.floor = float(checked["robust"]["floor"])
        self.robust_chip = indices(robust.carrier[0])
        self.robust_sign = tensor(robust.carrier[1])
        self.slot_weights = tensor(robust.slot_weights)
        self.robust_norms = tensor(robust.norms)
        self.instance_chip = indices(fragile.carrier[0])
        self.instance_sign = tensor(fragile.carrier[1])
        self.instance_norms = tensor(fragile.carrier[2])
        self.ws, self.wi = tensor(ws), tensor(wi)
        self.reference_projections = {"semantic": robust.projections, "instance": fragile_projections}
        self.receipt = {
            "semantic_code": f"{self.q:08x}", "perceptual_hash": f"{self.h:08x}",
            "detector_config_id": config.hex(), "decision_id": codec.decision_id(checked),
            "source_rgb8_sha256": hashlib.sha256(source.tobytes()).hexdigest(),
            "instance_binding": "source-phash-before-watermark",
            "surrogate_slot_weights_sha256": canonical_hash(robust.slot_weights),
            "patterns_sha256": canonical_hash({"s": ws, "i": wi}),
            "surrogate_is_final_detector": False,
        }

    def coefficients(self, luma, positions):
        blocks = luma.unfold(0, 8, 8).unfold(1, 8, 8)
        transformed = self.basis @ blocks @ self.basis.T
        return transformed[:, :, positions[0], positions[1]].reshape(-1, len(positions[0]))

    def projections(self, rgb):
        import torch
        if tuple(rgb.shape) != (1, 3, 512, 512):
            raise ValueError("Expected one 512x512 image in unit-range NCHW")
        luma = (rgb[0, 0] * .299 + rgb[0, 1] * .587 + rgb[0, 2] * .114) * 255
        coarse = torch.nn.functional.avg_pool2d(luma[None, None], 4)[0, 0]
        values = self.coefficients(coarse, self.rs) * self.whitening
        values = (values / torch.sqrt(self.floor**2 + values.square().mean(1, keepdim=True))).reshape(-1)
        weighted = values * self.slot_weights * self.robust_sign
        semantic = torch.zeros(codec.CHANNEL_CHIPS, device=rgb.device, dtype=rgb.dtype)
        semantic = semantic.index_add(0, self.robust_chip, weighted) / self.robust_norms
        values = self.coefficients(luma, self.ins).reshape(-1) * self.instance_sign
        instance = torch.zeros(codec.CHANNEL_CHIPS, device=rgb.device, dtype=rgb.dtype)
        instance = instance.index_add(0, self.instance_chip, values) / self.instance_norms
        return semantic, instance

    @staticmethod
    def score(values, pattern):
        import torch
        norm = torch.linalg.vector_norm(values)
        return torch.where(norm > 1e-12, (values * pattern).sum() / norm.clamp_min(1e-12), norm * 0)

    def scores(self, rgb):
        s, i = self.projections(rgb)
        return self.score(s, self.ws), self.score(i, self.wi)


def load_pinned_clip():
    """Load only the verified MAIN asset, independently of legacy probe roots."""
    import torch
    from PIL import Image
    from scripts.a6_clip_visual import load_visual_encoder
    model, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")

    def feature(rgb):
        with torch.inference_mode():
            value = model.encode_image(transform(Image.fromarray(rgb)).unsqueeze(0)).float()
        return (value / torch.linalg.vector_norm(value)).reshape(-1).tolist()
    return feature


def blind_detect(rgb, owner, profile, feature_extractor):
    """Suspect-only verification boundary: no source key/features accepted."""
    import numpy as np
    suspect = np.asarray(rgb)
    if suspect.dtype != np.uint8 or suspect.shape != (512, 512, 3):
        raise ValueError("Blind detector expects saved/redecoded RGB8")
    features = feature_extractor(suspect)
    result = codec.detect_rgb(suspect.tolist(), owner, profile=profile, semantic_features=features)
    result["verification_features"] = "recomputed-from-this-suspect-image"
    result["side_information"] = ["public OwnerID", "versioned v5 detector profile", "pinned CLIP weights"]
    result["qualified_state"] = {
        "authentic": "authentic-consistent", "regenerated": "regeneration-consistent",
        "copy_paste": "content-transplant-consistent", "not_detected": "no-evidence",
        "unclassified": "abstain",
    }[result["proposal_state"]]
    result["label_scope"] = "Operational dual-channel signature; does not identify causal history or cryptographic ownership"
    # The unchanged verifier reports its image-domain origin. Retain that field;
    # actual embedding route belongs to the enrollment record, not this detector.
    result["extractor_domain"] = "image-DCT-with-CLIP; no VAE and no diffusion inversion"
    return result


class DualLatentEmbedder:
    def __init__(self, vae, config):
        self.vae = vae.eval().requires_grad_(False)
        self.config = validate_config(config)
        self.device = next(vae.parameters()).device

    def decode(self, z):
        # z uses unscaled VAE posterior coordinates, exactly as reconstruction.
        return ((self.vae.decode(z, return_dict=False)[0].float() + 1) / 2).clamp(0, 1)

    def cycle(self, rgb):
        return self.decode(self.vae.encode(rgb * 2 - 1).latent_dist.mode())

    def image(self, z, source, reference, route):
        decoded = self.decode(z)
        if route == "pure-decoder":
            return decoded
        if route == "hybrid-source-bypass":
            return (source + decoded - reference).clamp(0, 1)
        raise ValueError("Unknown route")

    def optimize(self, source, z_reference, objective, route, event, checkpoint_callback=None, deadline=None):
        """Optimize only z; callbacks journal all steps and shard checkpoints.

        Returns the final-cap image and latent, never the best checkpoint.
        A failed/nonfinite gradient raises and is retained by the run harness.
        """
        import torch
        from torch.utils.checkpoint import checkpoint
        cfg = self.config
        z = z_reference.detach().clone().float().to(self.device).requires_grad_(True)
        with torch.no_grad():
            reference = self.decode(z_reference.to(self.device)).detach()
        optimizer = torch.optim.Adam([z], lr=cfg["learning_rate"], betas=(.9, .999), eps=1e-8)
        budget = 10**(-cfg["quality_psnr_db"] / 10)
        total = cfg["robust_steps"] + cfg["joint_steps"]
        started = time.monotonic()

        def render(latent):
            return self.image(latent, source, reference, route)

        def image_graph():
            return checkpoint(render, z, use_reentrant=False) if cfg["decoder_checkpoint"] else render(z)

        for step in range(total):
            if deadline is not None and time.monotonic() >= deadline:
                raise RuntimeError("Run wall-time cap reached during shard; earlier checkpoints retained")
            phase = "robust" if step < cfg["robust_steps"] else "joint"
            optimizer.zero_grad(set_to_none=True)
            output = image_graph()
            d = (output - source).square().mean() / budget
            zs, zi = objective.scores(output)
            loss = cfg["quality_weight"] * d + cfg["quality_excess_weight"] * torch.relu(d - 1).square()
            loss = loss + cfg["semantic_weight"] * (torch.relu(cfg["semantic_margin"] - zs) / cfg["semantic_margin"]).square()
            if phase == "joint":
                loss = loss + cfg["instance_weight"] * (torch.relu(cfg["instance_margin"] - zi) / cfg["instance_margin"]).square()
            if not bool(torch.isfinite(loss)):
                raise RuntimeError("Nonfinite clean loss")
            loss.backward()
            row = {"phase": "optimizer_step", "route": route, "stage": phase,
                   "step": step + 1, "measurement_time": "before-update",
                   "quality_budget_ratio": float(d.detach()), "surrogate_semantic": float(zs.detach()),
                   "surrogate_instance": float(zi.detach()), "clean_loss": float(loss.detach())}
            del output, d, zs, zi, loss
            if cfg["cycle_weight"] > 0 and step % cfg["cycle_every"] == 0:
                # Rebuild/consume the second graph separately to limit GPU memory.
                output = image_graph()
                cycled = checkpoint(self.cycle, output, use_reentrant=False) if cfg["decoder_checkpoint"] else self.cycle(output)
                zs_cycle, _ = objective.scores(cycled)
                cycle_loss = cfg["cycle_weight"] * (torch.relu(cfg["cycle_margin"] - zs_cycle) / cfg["cycle_margin"]).square()
                if not bool(torch.isfinite(cycle_loss)):
                    raise RuntimeError("Nonfinite VAE-cycle loss")
                cycle_loss.backward()
                row.update(surrogate_cycle_semantic=float(zs_cycle.detach()), cycle_loss=float(cycle_loss.detach()))
                del output, cycled, zs_cycle, cycle_loss
            if z.grad is None or not bool(torch.isfinite(z.grad).all()):
                raise RuntimeError("Missing/nonfinite latent gradient")
            row["latent_gradient_l2"] = float(torch.linalg.vector_norm(z.grad))
            optimizer.step()
            if not bool(torch.isfinite(z).all()):
                raise RuntimeError("Nonfinite latent after update")
            row["seconds"] = time.monotonic() - started
            event(row)
            if checkpoint_callback is not None and ((step + 1) % cfg["checkpoint_every"] == 0 or step + 1 == total):
                checkpoint_callback(step + 1, z.detach().cpu(), row)
            if z.device.type == "cuda" and torch.cuda.memory_allocated() > cfg["gpu_budget_bytes"]:
                raise RuntimeError("GPU allocation budget exceeded")
        with torch.no_grad():
            final = render(z).detach()
            zs, zi = objective.scores(final)
            final_cycle_s, _ = objective.scores(self.cycle(final))
        return final, z.detach(), {
            "outcome": "completed", "steps": total, "final_selection": "last-fixed-step",
            "surrogate_semantic": float(zs), "surrogate_instance": float(zi),
            "surrogate_cycle_semantic": float(final_cycle_s),
            "latent_displacement_l2": float(torch.linalg.vector_norm(z.detach() - z_reference.to(self.device))),
            "seconds": time.monotonic() - started,
        }


def save_rgb(path, tensor):
    import numpy as np
    from PIL import Image
    array = (tensor.detach()[0].permute(1, 2, 0).float().cpu().numpy().clip(0, 1) * 255).round().astype(np.uint8)
    Image.fromarray(array).save(path)
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"), dtype=np.uint8).copy()


def validate_manifest(manifest):
    from scripts import m1_latent_reconstruction as reconstruction
    if manifest.get("schema_version") != VERSION or manifest.get("data_split") != "development":
        raise ValueError("Only versioned development manifests are accepted")
    cfg = validate_config(manifest["config"])
    cohort = ROOT / manifest["cohort_manifest"]
    if cohort.resolve() != (ROOT / "research/m1-reconstruction-dev.json").resolve():
        raise ValueError("Only the reserved M1 development cohort is allowed")
    reserved = reconstruction.cases_for(json.loads(cohort.read_text(encoding="utf-8")))
    requested = manifest["case_ids"]
    if (not requested or any(type(x) is not int for x in requested)
            or len(set(requested)) != len(requested)):
        raise ValueError("Explicit unique integer case IDs required")
    by_id = {case["id"]: case for case in reserved}
    if any(i not in by_id for i in requested):
        raise ValueError("Unreserved development source")
    profile_path = ROOT / manifest["detector_profile"]
    if profile_path.resolve() != (ROOT / "configs/revised-watermark-v5.example.json").resolve():
        raise ValueError("Only the pinned v5 reference profile is supported")
    profile = codec.load_profile(profile_path)
    profile["semantic_source"] = CLIP_SOURCE
    profile = codec.validate_profile(profile)
    return cfg, [by_id[i] for i in requested], profile, cohort, profile_path


def source_rgb(case):
    import numpy as np
    from PIL import Image, ImageOps, ImageCms
    if sha(case["path"]) != case["sha256"]:
        raise ValueError("Source hash mismatch")
    with Image.open(case["path"]) as image:
        if image.mode != "RGB":
            raise ValueError("Only RGB inputs supported")
        image.load()
        icc = image.info.get("icc_profile")
        image = ImageOps.exif_transpose(image)
        if icc:
            image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                ImageCms.createProfile("sRGB"), renderingIntent=0, outputMode="RGB", flags=0)
        native_shape = [image.height, image.width, 3]
        return np.asarray(image.resize((512, 512), Image.Resampling.BICUBIC), dtype=np.uint8).copy(), native_shape


def reconstruction_latent(run_path, case_id, step, expected_source_hash):
    """Read only a completed hash-verified checkpoint from a declared dev run."""
    import torch
    record = json.loads((run_path / "run.json").read_text(encoding="utf-8"))
    if record.get("data_split") != "development":
        raise ValueError("Initialization checkpoint is not a development run")
    rows = [r for r in record["cases"] if r["id"] == case_id]
    if len(rows) != 1 or rows[0].get("outcome") != "completed":
        raise ValueError("Reconstruction case is not completed")
    row = rows[0]
    if row.get("source_rgb8_sha256") != expected_source_hash:
        raise ValueError("Reconstruction and embedding source pixels differ")
    checkpoints = [c for c in row["checkpoints"] if c["step"] == step]
    if len(checkpoints) != 1:
        raise ValueError("Missing reconstruction checkpoint")
    path = run_path / f"{case_id}-step{step:03d}.pt"
    if sha(path) != checkpoints[0]["latent_sha256"]:
        raise ValueError("Reconstruction latent hash mismatch")
    obj = torch.load(path, map_location="cpu", weights_only=True)
    if obj.get("step") != step or not str(obj.get("latent_units", "")).startswith("unscaled VAE posterior mode"):
        raise ValueError("Reconstruction latent units/step mismatch")
    z = obj["z"]
    if tuple(z.shape) != (1, 4, 64, 64) or not bool(torch.isfinite(z).all()):
        raise ValueError("Invalid reconstruction latent")
    return z.float(), {"path": str(path.resolve()), "sha256": sha(path),
                       "run_json_sha256": sha(run_path / "run.json"), "commit": record.get("commit"),
                       "checkpoint_receipt": checkpoints[0], "reconstruction_config": record.get("config"),
                       "source_rgb8_sha256": row["source_rgb8_sha256"]}


def require_committed(paths):
    """A scientific run must execute committed inputs, including new files."""
    receipts = {}
    for path in paths:
        path = Path(path).resolve()
        relative = path.relative_to(ROOT).as_posix()
        committed = subprocess.check_output(["git", "rev-parse", f"HEAD:{relative}"], cwd=ROOT, text=True).strip()
        # Git's clean filters handle the checkout's core.autocrlf=true. Bytewise
        # SHA equality with git-show would incorrectly reject committed CRLF.
        current = subprocess.check_output(["git", "hash-object", "--path=" + relative, str(path)],
                                          cwd=ROOT, text=True).strip()
        if committed != current:
            raise ValueError("Scientific input differs from HEAD: " + relative)
        receipts[relative] = {"working_sha256": sha(path), "git_blob_oid": committed}
    return receipts


def run(manifest_path, output, reconstruction_run=None):
    """Bounded sequential development shards. Existing output dirs are refused.

    Each completed image/route is durable. On failure the remaining shards are
    marked unattempted; a new versioned manifest can rerun those shards in a
    new run directory, leaving this record intact.
    """
    started = time.monotonic()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cfg, cases, profile, cohort_path, profile_path = validate_manifest(manifest)
    if not output.resolve().is_relative_to((MAIN / ".thesis-build/dev-runs").resolve()):
        raise ValueError("Output must be a new directory under the authoritative dev-runs root")
    if (cfg["initialization"] == "reconstruction-checkpoint") != (reconstruction_run is not None):
        raise ValueError("Reconstruction checkpoint mode requires --reconstruction-run, and conversely")
    deps = [Path(__file__), manifest_path, cohort_path, profile_path,
            ROOT / "scripts/revised_watermark_v5.py", ROOT / "scripts/revised_watermark_v4.py",
            ROOT / "scripts/m1_latent_reconstruction.py", ROOT / "scripts/dev_v5_regeneration_check.py",
            ROOT / "scripts/three_threat_models.py", ROOT / "research/a6-candidate-model-assets.json",
            ROOT / "scripts/a6_clip_visual.py", ROOT / "scripts/check_a6_lpips_assets.py",
            ROOT / "scripts/dev_v5_channel_probe.py", ROOT / "scripts/verify_science_assets.py",
            ROOT / "scripts/three_threat_protocol.py",
            ROOT / "experiments/c4-qim-rgb-development-v1/cohort.json",
            ROOT / "experiments/c4-three-threat-small-v1/development-expansion.json"]
    committed_files = require_committed(deps)
    output.mkdir(parents=True, exist_ok=False)
    record = {"schema_version": "m1-development-run-v1", "method": VERSION,
              "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "command": sys.argv, "config": cfg, "config_sha256": canonical_hash(cfg),
              "profile": profile, "committed_files": committed_files,
              "manifest_sha256": sha(manifest_path), "seeds": [cfg["seed"]],
              "data_split": "development", "outcome": "started", "duration_seconds": 0,
              "cases": [], "environment": {"python": sys.version},
              "label": "Exploratory terminal-VAE-latent amendment; no initial-noise claim",
              "output_operators": {
                  "pure-decoder": "clip((VAE.decode(z)+1)/2,0,1)",
                  "hybrid-source-bypass": "clip(source+decoded(z)-decoded(z_reference),0,1)",
              },
              "optimized_variables": ["unscaled terminal VAE latent z"],
              "source_profile": "oriented RGB8 sRGB, bicubic resize to512; not native-resolution evidence",
              "binding": "source CLIP q and source pHash h before watermark",
              "verification": "CLIP re-extracted from each saved suspect, v5 unchanged detector",
              "safety": "VAE decoding only; no diffusion generation, human visual assessment missing"}
    write_json(output / "run.json", record)
    def event(value):
        with (output / "journal.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(value, allow_nan=False) + "\n")
    try:
        from scripts.three_threat_models import block_network, load_lpips, lpips_score
        block_network()
        import numpy as np
        import torch
        from diffusers import AutoencoderKL
        from scripts.m1_latent_reconstruction import quality
        from scripts.check_a6_lpips_assets import verify_package
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable")
        torch.manual_seed(cfg["seed"])
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.cuda.set_per_process_memory_fraction(min(1.0, cfg["gpu_budget_bytes"] / torch.cuda.get_device_properties(0).total_memory))
        record["environment"].update({p: importlib.metadata.version(p) for p in
            ("torch", "numpy", "scipy", "Pillow", "diffusers", "lpips")})
        record["environment"]["gpu"] = torch.cuda.get_device_name(0)
        lock = json.loads((ROOT / "research/a6-candidate-model-assets.json").read_text())
        assets = [x for x in lock["files"] if x["path"].startswith(("sd15-fp16/vae/", "clip/", "alexnet/"))]
        for item in assets:
            path = ASSETS / item["path"]
            if path.stat().st_size != item["size_bytes"] or sha(path) != item["sha256"]:
                raise ValueError("Asset mismatch: " + item["path"])
        record["asset_files"] = assets
        feature = load_pinned_clip()
        record["clip_adapter_sha256"] = sha(sys.modules["a6_clip_visual"].__file__)
        package = Path(importlib.metadata.distribution("lpips").locate_file("lpips"))
        verify_package(package)
        metric = load_lpips(ASSETS, package)
        record["lpips_learned_sha256"] = sha(package / "weights/v0.1/alex.pth")
        vae = AutoencoderKL.from_pretrained(ASSETS / "sd15-fp16/vae", variant="fp16",
            use_safetensors=True, local_files_only=True, torch_dtype=torch.float32).eval().requires_grad_(False).to("cuda")
        embedder = DualLatentEmbedder(vae, cfg)
        record["vae_scaling_factor"] = float(vae.config.scaling_factor)
        record["latent_units"] = "unscaled VAE posterior mode; decoder receives same units"
        def assess(array):
            q = quality(source, array)
            q["lpips"] = lpips_score(metric, source, array)
            q["quality_admissible"] = (q["psnr_infinite"] or q["psnr_db"] > 35) and q["ssim_rgb"] > .9 and q["lpips"] < .1
            q["correct_owner"] = blind_detect(array, cfg["owner"], profile, feature)
            q["wrong_owner"] = blind_detect(array, cfg["wrong_owner"], profile, feature)
            return q
        for case in cases:
            source, native_shape = source_rgb(case)
            source_hash = hashlib.sha256(source.tobytes()).hexdigest()
            row = {"id": case["id"], "outcome": "started", "native_shape": native_shape,
                   "raw_sha256": case["sha256"], "source_rgb8_sha256": source_hash, "routes": []}
            record["cases"].append(row)
            event({"phase": "case_started", "id": case["id"]})
            write_json(output / "run.json", record)
            source_tensor = torch.from_numpy(source).permute(2, 0, 1)[None].float().to("cuda") / 255
            source_png = output / f"{case['id']}-source.png"
            save_rgb(source_png, source_tensor)
            row.update(source_png=str(source_png.resolve()), source_png_sha256=sha(source_png))
            if reconstruction_run is None:
                with torch.no_grad():
                    z_ref = vae.encode(source_tensor * 2 - 1).latent_dist.mode().detach()
                row["initialization"] = {"kind": "posterior-mode"}
            else:
                z_ref, receipt = reconstruction_latent(reconstruction_run, case["id"], cfg["reconstruction_step"], source_hash)
                z_ref = z_ref.to("cuda")
                row["initialization"] = {"kind": "reconstruction-checkpoint", **receipt}
            objective = FixedPatternObjective(source, feature(source), cfg["owner"], profile, device="cuda")
            row["enrollment"] = objective.receipt
            row["C0_source"] = assess(source)
            with torch.no_grad():
                ref_image = embedder.decode(z_ref).detach()
            for route in cfg["routes"]:
                if time.monotonic() - started > cfg["run_seconds_cap"]:
                    raise RuntimeError("Run wall-time cap reached before next shard")
                route_row = {"route": route, "outcome": "started", "operator": record["output_operators"][route]}
                row["routes"].append(route_row)
                stem = f"{case['id']}-{route}"
                route_dir = output / stem
                route_dir.mkdir()
                event({"phase": "route_started", "id": case["id"], "route": route})
                with torch.no_grad():
                    c0 = embedder.image(z_ref, source_tensor, ref_image, route)
                c0_array = save_rgb(route_dir / "C0-matched.png", c0)
                route_row["C0_matched"] = {**assess(c0_array), "png_path": str((route_dir / "C0-matched.png").resolve()),
                                           "png_sha256": sha(route_dir / "C0-matched.png")}
                def checkpoint_fn(step, z, info):
                    path = route_dir / f"latent-step{step:03d}.pt"
                    torch.save({"z": z, "step": step, "route": route, "source_rgb8_sha256": source_hash,
                                "config_sha256": record["config_sha256"], "latent_units": record["latent_units"]}, path)
                    event({"phase": "latent_checkpoint", "id": case["id"], "route": route,
                           "step": step, "path": str(path), "sha256": sha(path)})
                torch.cuda.reset_peak_memory_stats()
                final, final_z, info = embedder.optimize(source_tensor, z_ref, objective, route,
                    lambda e: event({"id": case["id"], **e}), checkpoint_fn, deadline=started + cfg["run_seconds_cap"])
                marked = save_rgb(route_dir / "C1-final.png", final)
                route_row.update(optimization=info,
                    C1={**assess(marked), "png_path": str((route_dir / "C1-final.png").resolve()),
                        "png_sha256": sha(route_dir / "C1-final.png")},
                    peak_allocated_bytes=torch.cuda.max_memory_allocated())
                # Attack input is saved/redecoded RGB8, never the float optimizer result.
                with torch.no_grad():
                    attack_input = torch.from_numpy(marked).permute(2, 0, 1)[None].float().to("cuda") / 255
                    cycled = embedder.cycle(attack_input)
                cycle_array = save_rgb(route_dir / "C1-vae-cycle.png", cycled)
                route_row["C1_VAE_cycle"] = {**assess(cycle_array), "png_path": str((route_dir / "C1-vae-cycle.png").resolve()),
                                           "png_sha256": sha(route_dir / "C1-vae-cycle.png")}
                # Matched negative follows the identical saved-image attack path.
                with torch.no_grad():
                    c0_input = torch.from_numpy(c0_array).permute(2, 0, 1)[None].float().to("cuda") / 255
                    c0_cycle = embedder.cycle(c0_input)
                c0_cycle_array = save_rgb(route_dir / "C0-vae-cycle.png", c0_cycle)
                route_row["C0_VAE_cycle"] = {**assess(c0_cycle_array), "png_path": str((route_dir / "C0-vae-cycle.png").resolve()),
                                           "png_sha256": sha(route_dir / "C0-vae-cycle.png")}
                route_row["outcome"] = "completed"
                write_json(route_dir / "result.json", route_row)
                write_json(output / "run.json", record)
                del final, final_z, attack_input, cycled, c0, c0_input, c0_cycle
                torch.cuda.empty_cache()
            row["outcome"] = "completed"
            write_json(output / "run.json", record)
            del objective, source_tensor, z_ref, ref_image
            torch.cuda.empty_cache()
        record["outcome"] = "completed"
    except (Exception, KeyboardInterrupt) as error:
        status = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
        record.update(outcome=status, error=str(error) or type(error).__name__, traceback=traceback.format_exc())
        if record["cases"] and record["cases"][-1]["outcome"] == "started":
            row = record["cases"][-1]
            row.update(outcome=status, error=record["error"])
            if row["routes"] and row["routes"][-1]["outcome"] == "started":
                row["routes"][-1].update(outcome=status, error=record["error"])
        event({"phase": "run_" + status, "error": record["error"]})
    finally:
        attempted = {r["id"] for r in record["cases"]}
        for case in cases:
            if case["id"] not in attempted:
                record["cases"].append({"id": case["id"], "outcome": "not_attempted_after_stop"})
        for row in record["cases"]:
            if "routes" in row:
                attempted_routes = {r["route"] for r in row["routes"]}
                for route in cfg["routes"]:
                    if route not in attempted_routes:
                        row["routes"].append({"route": route, "outcome": "not_attempted_after_stop"})
        record["duration_seconds"] = time.monotonic() - started
        write_json(output / "run.json", record)
    return 0 if record["outcome"] == "completed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reconstruction-run", type=Path)
    args = parser.parse_args()
    return run(args.manifest.resolve(), args.output_dir.resolve(),
               args.reconstruction_run.resolve() if args.reconstruction_run else None)


if __name__ == "__main__":
    raise SystemExit(main())
