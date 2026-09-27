"""Native saved-pair quality and key-drift primitives; no model at import.

Study-image calls belong only inside an exact-approved compute package.
This module has no CLI, data discovery, downloader or acceptance decision.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PAIRS = (("control_source", "source", "control"),
         ("candidate_source", "source", "candidate"),
         ("candidate_control", "control", "candidate"))
ALEX_SHA = "7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02"
LEARNED_SHA = "df73285e35b22355a2df87cdb6b70b343713b667eddbda73e1977e0c860835c0"
LPIPS_FILES = {
    "lpips.py": "780d09b907cb9b661e0ae28b2d163ddfba92f9e870d7feba34d4790cc6590658",
    "pretrained_networks.py": "6a27f714c51796db466e86bebba6a617c1bfc4d566f3a1756497629c1248686e",
    "__init__.py": "36ee004a45e2cc2c5ab47fa3955f00c0e41f6a151ef0249fb6f362533ed58b22",
    "weights/v0.1/alex.pth": LEARNED_SHA,
}


@dataclass(frozen=True)
class FrozenLPIPS:
    metric: object
    structure: tuple
    tensor_digest: str


def _structure(metric) -> tuple:
    expected = {"version": "0.1", "pnet_type": "alex", "lpips": True,
                "spatial": False, "pnet_tune": False, "pnet_rand": True,
                "L": 5, "chns": [64, 192, 384, 256, 256]}
    if any(type(getattr(metric, key, None)) is not type(value) or
           getattr(metric, key, None) != value for key, value in expected.items()):
        raise ValueError("LPIPS declared profile changed")
    modules = tuple(metric.named_modules())
    if any(module.training for _, module in modules):
        raise ValueError("LPIPS child evaluation profile changed")
    return tuple((name, id(module), type(module)) for name, module in modules)


def _tensor_digest(metric) -> str:
    digest = hashlib.sha256()
    for kind, values in (("parameter", metric.named_parameters()),
                         ("buffer", metric.named_buffers())):
        for name, value in values:
            if (value.requires_grad or str(value.dtype) != "torch.float32" or
                    value.device.type != "cuda"):
                raise ValueError("LPIPS tensor profile changed")
            raw = value.detach().cpu().contiguous().numpy().tobytes()
            header = repr((kind, name, tuple(value.shape))).encode("ascii")
            digest.update(len(header).to_bytes(8, "big") + header)
            digest.update(len(raw).to_bytes(8, "big") + raw)
    return digest.hexdigest()


def rgb8(value: np.ndarray) -> np.ndarray:
    if (not isinstance(value, np.ndarray) or value.dtype != np.uint8 or
            value.ndim != 3 or value.shape[2] != 3 or min(value.shape[:2]) < 63):
        raise ValueError("native HWC RGB8 with both sides >=63 required")
    return np.array(value, copy=True, order="C")


def classical(reference: np.ndarray, candidate: np.ndarray) -> dict:
    """RGB float64 MSE/PSNR and fixed Gaussian/population-covariance SSIM."""
    from skimage.metrics import structural_similarity
    left, right = rgb8(reference), rgb8(candidate)
    if left.shape != right.shape:
        raise ValueError("no implicit resizing, padding or alignment")
    x, y = left.astype(np.float64) / 255.0, right.astype(np.float64) / 255.0
    mse = float(np.mean((x - y) ** 2, dtype=np.float64))
    # JSON has no portable infinity: explicitly encode the exact-identity case.
    psnr = None if mse == 0 else -10.0 * math.log10(mse)
    ssim = float(structural_similarity(
        x, y, data_range=1.0, channel_axis=2, gaussian_weights=True,
        sigma=1.5, win_size=11, use_sample_covariance=False, K1=0.01, K2=0.03))
    if not math.isfinite(ssim) or (psnr is not None and not math.isfinite(psnr)):
        raise ValueError("nonfinite classical metric")
    return {"mse_rgb01": mse, "psnr_db": psnr,
            "psnr_positive_infinity": mse == 0, "ssim_rgb": ssim}


def target_checks(metrics: dict) -> dict:
    """Strict proposal inequalities; a descriptive per-pair diagnostic only."""
    mse, psnr, ssim, distance = (metrics[k] for k in
                               ("mse_rgb01", "psnr_db", "ssim_rgb", "lpips_alex_v01"))
    infinite = metrics["psnr_positive_infinity"]
    if (type(infinite) is not bool or type(mse) is not float or
            not math.isfinite(mse) or mse < 0 or
            infinite != (mse == 0) or
            (infinite and psnr is not None) or
            (not infinite and (type(psnr) is not float or not math.isfinite(psnr))) or
            any(type(v) is not float or not math.isfinite(v) for v in (ssim, distance))):
        raise ValueError("invalid/nonfinite metric record")
    checks = {"psnr_gt_35": infinite or psnr > 35.0,
              "ssim_gt_0_9": ssim > 0.9, "lpips_lt_0_1": distance < 0.1}
    return {**checks, "all_three_targets": all(checks.values()),
            "scientific_acceptance": False}


def hamming(left: bytes, right: bytes, bits: int) -> int:
    if type(bits) is not int or bits not in (12, 32):
        raise ValueError("only frozen q12/h32 widths")
    size = (bits + 7) // 8
    if any(type(v) is not bytes or len(v) != size or
           int.from_bytes(v, "little") >= (1 << bits) for v in (left, right)):
        raise ValueError("noncanonical code bytes")
    return (int.from_bytes(left, "little") ^ int.from_bytes(right, "little")).bit_count()


def drift(source_q: bytes, source_h: bytes, output_q: bytes, output_h: bytes) -> dict:
    qd, hd = hamming(source_q, output_q, 12), hamming(source_h, output_h, 32)
    return {"q_hamming": qd, "h_hamming": hd,
            "source_q_in_output_radius1": qd <= 1,
            "source_h_in_output_radius1": hd <= 1,
            "both_source_codes_in_radius1": qd <= 1 and hd <= 1,
            "blind_detection": "NOT_RUN", "scientific_acceptance": False}


def _checked_bytes(path: Path, digest: str, size: int | None = None) -> bytes:
    path = Path(path)
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink() or ancestor.is_junction():
            raise ValueError("linked weight/package path")
    if not path.is_file() or (size is not None and path.stat().st_size != size):
        raise ValueError("missing/wrong-size weight/package")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("weight/package digest mismatch")
    return raw


def load_lpips(alexnet: Path, device: str):
    """Explicit model-load boundary. Local verified two-weight route only.

    No caller is authorized by this function: the runner must approve its
    exact experiment. Snapshot checked bytes prevent a second mutable open.
    """
    import importlib.metadata
    import io
    import sys
    if device != "cuda":
        raise ValueError("frozen metric profile requires cuda fp32")
    if any(name == "lpips" or name.startswith("lpips.") for name in sys.modules):
        raise ValueError("fresh isolated process required; LPIPS already imported")
    dist = importlib.metadata.distribution("lpips")
    if dist.version != "0.1.4":
        raise ValueError("LPIPS package version changed")
    snapshots = {name: _checked_bytes(Path(dist.locate_file("lpips/" + name)), sha)
                 for name, sha in LPIPS_FILES.items()}
    alex = _checked_bytes(alexnet, ALEX_SHA, 244408911)
    if len(snapshots["weights/v0.1/alex.pth"]) != 6009:
        raise ValueError("LPIPS learned layer size changed")
    import lpips
    for name, relative in (("lpips", "__init__.py"), ("lpips.lpips", "lpips.py"),
                           ("lpips.pretrained_networks", "pretrained_networks.py")):
        actual = getattr(sys.modules.get(name), "__file__", None)
        if actual is None or Path(actual).resolve() != Path(dist.locate_file("lpips/" + relative)).resolve():
            raise ValueError("imported LPIPS origin mismatch")
        _checked_bytes(Path(actual), LPIPS_FILES[relative])
    if lpips.LPIPS.__module__ != "lpips.lpips":
        raise ValueError("imported LPIPS class substitution")
    import torch
    import torchvision
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    metric = lpips.LPIPS(pretrained=False, pnet_rand=True, net="alex", version="0.1",
                        spatial=False, use_dropout=True, eval_mode=True, verbose=False)
    trunk = torchvision.models.alexnet(weights=None)
    state = torch.load(io.BytesIO(alex), map_location="cpu", weights_only=True)
    if not isinstance(state, dict) or any(type(k) is not str or not isinstance(v, torch.Tensor)
                                          for k, v in state.items()):
        raise ValueError("invalid AlexNet tensor state")
    trunk.load_state_dict(state, strict=True)
    for name, start, end in (("slice1", 0, 2), ("slice2", 2, 5), ("slice3", 5, 8),
                             ("slice4", 8, 10), ("slice5", 10, 12)):
        setattr(metric.net, name, torch.nn.Sequential(*list(trunk.features.children())[start:end]))
    learned = torch.load(io.BytesIO(snapshots["weights/v0.1/alex.pth"]),
                         map_location="cpu", weights_only=True)
    keys = {f"lin{i}.model.1.weight" for i in range(5)}
    if not isinstance(learned, dict) or set(learned) != keys:
        raise ValueError("unexpected LPIPS learned tensor inventory")
    if any(not isinstance(v, torch.Tensor) or not torch.isfinite(v).all() for v in learned.values()):
        raise ValueError("invalid LPIPS learned tensor")
    result = metric.load_state_dict(learned, strict=False)
    if result.unexpected_keys or any(k in keys for k in result.missing_keys):
        raise ValueError("LPIPS calibrated-layer load failed")
    metric.requires_grad_(False).eval().to(device=device, dtype=torch.float32)
    return FrozenLPIPS(metric, _structure(metric), _tensor_digest(metric))


def lpips_distance(loaded: FrozenLPIPS, reference: np.ndarray, candidate: np.ndarray) -> float:
    import torch
    left, right = rgb8(reference), rgb8(candidate)
    if left.shape != right.shape:
        raise ValueError("LPIPS requires identical native grids")
    def tensor(value):
        return (torch.from_numpy(value).permute(2, 0, 1).unsqueeze(0)
                .to(device="cuda", dtype=torch.float32) / 255.0 * 2.0 - 1.0)
    if type(loaded) is not FrozenLPIPS:
        raise ValueError("verified LPIPS loader receipt required")
    metric = loaded.metric
    if (_structure(metric) != loaded.structure or
            _tensor_digest(metric) != loaded.tensor_digest):
        raise ValueError("LPIPS loaded structure/weight identity changed")
    if (not torch.are_deterministic_algorithms_enabled() or
            torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32 or
            torch.backends.cudnn.benchmark or metric.training or
            any(p.requires_grad or p.dtype != torch.float32 or p.device.type != "cuda"
                for p in metric.parameters())):
        raise ValueError("LPIPS frozen inference profile changed")
    with torch.inference_mode(), torch.autocast("cuda", enabled=False):
        value = metric(tensor(left), tensor(right), normalize=False)
    if value.numel() != 1 or not torch.isfinite(value).all():
        raise ValueError("invalid LPIPS scalar output")
    return float(value.item())
