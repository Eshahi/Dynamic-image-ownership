"""Offline evaluator/attack adapters. No model imports or loads at import time.

Study calls require the exact approved worker package. CLIP/LPIPS are evaluator
only; neither enters the blind QIM detector. No automatic weight acquisition.
"""
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import socket

from check_a6_lpips_assets import LOCK_SHA256, verify_package
from verify_science_assets import verify
from three_threat_protocol import REGEN_SETTINGS

SD_FILES = frozenset({
    "feature_extractor/preprocessor_config.json", "model_index.json",
    "safety_checker/config.json", "safety_checker/model.fp16.safetensors",
    "scheduler/scheduler_config.json", "text_encoder/config.json",
    "text_encoder/model.fp16.safetensors", "tokenizer/merges.txt",
    "tokenizer/special_tokens_map.json", "tokenizer/tokenizer_config.json",
    "tokenizer/vocab.json", "unet/config.json",
    "unet/diffusion_pytorch_model.fp16.safetensors", "vae/config.json",
    "vae/diffusion_pytorch_model.fp16.safetensors",
})
DDIM_CONFIG = {
    "num_train_timesteps": 1000, "beta_start": 0.00085, "beta_end": 0.012,
    "beta_schedule": "scaled_linear", "trained_betas": None,
    "clip_sample": False, "set_alpha_to_one": False, "steps_offset": 1,
    "prediction_type": "epsilon", "thresholding": False,
    "timestep_spacing": "leading", "rescale_betas_zero_snr": False,
}


def block_network():
    for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "DIFFUSERS_OFFLINE",
                 "HF_DATASETS_OFFLINE", "HF_HUB_DISABLE_TELEMETRY"):
        os.environ[name] = "1"
    def denied(*args, **kwargs):
        raise RuntimeError("Three-threat worker forbids network connections")
    socket.socket.connect = denied
    socket.socket.connect_ex = denied
    socket.create_connection = denied


def verify_assets(asset_root, lock_path):
    raw = Path(lock_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != LOCK_SHA256:
        raise ValueError("existing asset lock changed")
    lock = json.loads(raw)
    receipt = verify(Path(asset_root), lock)
    if len(receipt["files"]) != 17:
        raise ValueError("exact seventeen existing assets required")
    listed = {entry["path"].removeprefix("sd15-fp16/") for entry in lock["files"]
              if entry["path"].startswith("sd15-fp16/")}
    model_dir = Path(asset_root) / "sd15-fp16"
    actual = {path.relative_to(model_dir).as_posix() for path in model_dir.rglob("*") if path.is_file()}
    if listed != SD_FILES or actual != SD_FILES:
        raise ValueError("exact local SD fp16 directory required")
    package_root = Path(importlib.metadata.distribution("lpips").locate_file("lpips"))
    verify_package(package_root)
    return receipt, package_root


def regeneration_kwargs(strength, seed, image, generator_factory):
    """A fresh generator is created for every C0/C1 call with the same seed."""
    if type(seed) is not int or seed not in REGEN_SETTINGS["seeds"]:
        raise ValueError("unlisted regeneration seed")
    if type(strength) not in (int, float) or strength not in REGEN_SETTINGS["strengths"]:
        raise ValueError("unlisted regeneration strength")
    generator = generator_factory(device="cuda").manual_seed(seed)
    return {"prompt": "", "negative_prompt": "", "image": image,
            "strength": strength, "num_inference_steps": 20, "eta": 0.0,
            "guidance_scale": 1.0, "generator": generator,
            "num_images_per_prompt": 1, "output_type": "pil", "return_dict": True}


def validate_generated(result):
    if len(result.images) != 1 or result.nsfw_content_detected is None or len(result.nsfw_content_detected) != 1:
        raise RuntimeError("generation/safety result incomplete")
    flag = result.nsfw_content_detected[0]
    if type(flag) is not bool:
        raise RuntimeError("malformed safety verdict")
    if flag:
        raise RuntimeError("safety_checker_blocked_output")
    image = result.images[0]
    if image.mode != "RGB" or image.size != (512, 512):
        raise RuntimeError("generated image differs from frozen RGB geometry")
    return image


def load_regenerator(asset_root):
    import torch
    from diffusers import DDIMScheduler, StableDiffusionImg2ImgPipeline
    pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
        Path(asset_root) / "sd15-fp16", variant="fp16", use_safetensors=True,
        local_files_only=True, torch_dtype=torch.float16,
    )
    if pipeline.safety_checker is None or pipeline.feature_extractor is None:
        raise RuntimeError("required safety components missing")
    # Explicit adaptation from pinned PNDM-trained config; no upstream defaults
    # are relied on for these scheduler fields.
    pipeline.scheduler = DDIMScheduler(**DDIM_CONFIG)
    for key, value in DDIM_CONFIG.items():
        if getattr(pipeline.scheduler.config, key) != value:
            raise RuntimeError("effective DDIM config mismatch: " + key)
    pipeline.set_progress_bar_config(disable=True)
    pipeline.to("cuda")
    return pipeline


def load_lpips(asset_root, package_root):
    import torch
    import torchvision
    import lpips
    metric = lpips.LPIPS(pretrained=False, pnet_rand=True, net="alex", version="0.1",
                         spatial=False, use_dropout=True, eval_mode=True, verbose=False)
    trunk = torchvision.models.alexnet(weights=None)
    state = torch.load(Path(asset_root) / "alexnet/alexnet-owt-7be5be79.pth",
                       map_location="cpu", weights_only=True)
    if not isinstance(state, dict) or not all(isinstance(k, str) and isinstance(v, torch.Tensor) for k, v in state.items()):
        raise RuntimeError("invalid AlexNet tensor state")
    trunk.load_state_dict(state, strict=True)
    for name, start, stop in (("slice1", 0, 2), ("slice2", 2, 5), ("slice3", 5, 8),
                              ("slice4", 8, 10), ("slice5", 10, 12)):
        setattr(metric.net, name, torch.nn.Sequential(*(trunk.features[i] for i in range(start, stop))))
    state = torch.load(Path(package_root) / "weights/v0.1/alex.pth", map_location="cpu", weights_only=True)
    required = {f"lin{i}.model.1.weight" for i in range(5)}
    if not isinstance(state, dict) or not required.issubset(state) or set(state) - set(metric.state_dict()):
        raise RuntimeError("invalid LPIPS learned state")
    missing, unexpected = metric.load_state_dict(state, strict=False)
    if unexpected or any(k.startswith("lin") and not k.startswith("lins.") for k in missing):
        raise RuntimeError("incomplete LPIPS learned layers")
    return metric.requires_grad_(False).eval().to("cpu")


def lpips_score(metric, left, right):
    import torch
    def tensor(rgb):
        return torch.from_numpy(rgb.copy()).permute(2, 0, 1).unsqueeze(0).float() / 255 * 2 - 1
    with torch.inference_mode():
        score = metric(tensor(left), tensor(right), normalize=False)
    if score.numel() != 1 or not bool(torch.isfinite(score).all()):
        raise RuntimeError("invalid LPIPS score")
    return float(score.item())


def clip_feature(model, transform, rgb):
    from PIL import Image
    import torch
    with torch.inference_mode():
        value = model.encode_image(transform(Image.fromarray(rgb)).unsqueeze(0)).float()
    if value.shape != (1, 512) or not bool(torch.isfinite(value).all()):
        raise RuntimeError("invalid CLIP feature")
    norm = float(torch.linalg.vector_norm(value))
    if not math.isfinite(norm) or norm < 1e-12:
        raise RuntimeError("degenerate CLIP feature")
    return (value / norm).cpu()
