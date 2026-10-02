"""Development probe: which block-DCT bands does a latent-diffusion channel keep?

Development tooling for the v5 candidate, not a study run.  It reads no study
image: every host is either procedural or generated here from a fixed prompt
and seed with the pinned local Stable Diffusion 1.5 weights.  It writes only
under ``.thesis-build/rehearsal/`` and every output is labelled synthetic.  Its
numbers choose engineering defaults (which scale, which coefficients, which
colour channel); they are not evidence about photographs and must not be cited
as a result of the thesis.

For each host, each colour channel (Y, Cb, Cr) and each scale s in SCALES the
probe adds a small pseudorandom change to the 8x8 block-DCT coefficients of the
image area-averaged by s, sends the marked and the unmarked image through the
same channel with the same seed, and records per coefficient position

* ``host_rms``   RMS of the host coefficient,
* ``noise_rms``  RMS change the channel makes to the unmarked host coefficient,
* ``gain``       regression of the paired output difference on the input change.

Channels: the deterministic VAE mode round trip and SD 1.5 img2img with the
settings of the retained revision-2 study (DDIM, 20 steps, eta 0, guidance 1,
empty prompt).

Run with the science interpreter:

    .thesis-build/a6-science-venv/Scripts/python.exe scripts/dev_v5_channel_probe.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy.fft import dctn, idctn

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / ".thesis-build" / "assets" / "a6" / "sd15-fp16"
OUTPUT = ROOT / ".thesis-build" / "rehearsal" / "v5-channel-dev"
SCALES = (1, 2, 4, 8)
STRENGTHS = (0.05, 0.1, 0.2, 0.4)
CHANNELS = ("Y", "Cb", "Cr")
AMPLITUDE = 3.0
PROMPTS = (
    "a photograph of a mountain lake at sunrise, detailed landscape",
    "a photograph of a city street with parked cars and shop fronts",
    "a close-up photograph of a bowl of fruit on a wooden table",
    "a photograph of a brown dog running on a beach",
    "a photograph of a living room with a sofa and bookshelves",
    "a photograph of a forest path in autumn",
    "a photograph of a red bicycle leaning against a brick wall",
    "a photograph of a snowy mountain under a clear blue sky",
    "a photograph of a plate of pasta in a restaurant",
    "a photograph of a harbour with fishing boats",
    "a photograph of a field of sunflowers under clouds",
    "a photograph of a kitchen counter with pots and vegetables",
    "a photograph of a cat sleeping on a windowsill",
    "a photograph of a desert road with distant hills",
    "a photograph of a train station platform",
    "a photograph of a flower market stall",
)
DDIM = {
    "num_train_timesteps": 1000, "beta_start": 0.00085, "beta_end": 0.012,
    "beta_schedule": "scaled_linear", "trained_betas": None, "clip_sample": False,
    "set_alpha_to_one": False, "steps_offset": 1, "prediction_type": "epsilon",
    "thresholding": False, "timestep_spacing": "leading", "rescale_betas_zero_snr": False,
}


def offline() -> None:
    for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "DIFFUSERS_OFFLINE", "HF_DATASETS_OFFLINE", "HF_HUB_DISABLE_TELEMETRY"):
        os.environ[name] = "1"


def to_ycc(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.float64) for i in range(3))
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return np.stack([y, -0.168736 * r - 0.331264 * g + 0.5 * b, 0.5 * r - 0.418688 * g - 0.081312 * b], axis=-1)


def ycc_delta_to_rgb(channel: int, delta: np.ndarray) -> np.ndarray:
    """RGB change that moves one of Y, Cb, Cr by ``delta`` and leaves the other two alone."""
    weights = ((1.0, 1.0, 1.0), (0.0, -0.344136, 1.772), (1.402, -0.714136, 0.0))[channel]
    return np.stack([delta * w for w in weights], axis=-1)


def coarse_dct(plane: np.ndarray, scale: int) -> np.ndarray:
    """8x8 block DCT of ``plane`` area-averaged by ``scale``: array [blocks_y, blocks_x, 8, 8]."""
    h, w = plane.shape
    h, w = h - h % (8 * scale), w - w % (8 * scale)
    small = plane[:h, :w].reshape(h // scale, scale, w // scale, scale).mean(axis=(1, 3))
    blocks = small.reshape(h // scale // 8, 8, w // scale // 8, 8).transpose(0, 2, 1, 3)
    return dctn(blocks, axes=(2, 3), norm="ortho")


def band_change(shape: tuple[int, int], scale: int, rng: np.random.Generator, amplitude: float) -> tuple[np.ndarray, np.ndarray]:
    """A full-resolution change whose coarse 8x8 block DCT moves by a white +-amplitude pattern.

    Built from the low 8x8 corner of the (8*scale)-point block DCT, which
    area-averages exactly onto the 8-point basis, so the change is smooth
    inside each block.  Returns (pixel change, realised coarse-coefficient change).
    """
    h, w = shape
    side = 8 * scale
    by, bx = h // side, w // side
    wanted = rng.choice((-amplitude, amplitude), size=(by, bx, 8, 8))
    wanted[..., 0, 0] = 0.0
    big = np.zeros((by, bx, side, side))
    big[..., :8, :8] = wanted * scale  # an orthonormal coarse coefficient is 1/scale of the fine one, up to the averaging gain
    pixels = idctn(big, axes=(2, 3), norm="ortho").transpose(0, 2, 1, 3).reshape(by * side, bx * side)
    change = np.zeros(shape)
    change[: by * side, : bx * side] = pixels
    return change, coarse_dct(change, scale)


def procedural(seed: int, size: int = 512) -> np.ndarray:
    """A colour 1/f field with a few flat regions and edges."""
    rng = np.random.default_rng(seed)
    fy, fx = np.meshgrid(np.fft.fftfreq(size), np.fft.fftfreq(size), indexing="ij")
    radius = np.hypot(fy, fx)
    radius[0, 0] = 1.0
    planes = []
    for _ in range(3):
        spectrum = (rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size))) / radius ** rng.uniform(1.0, 1.4)
        field = np.fft.ifft2(spectrum).real
        planes.append(128 + 45 * field / field.std())
    image = np.stack(planes, axis=-1)
    for _ in range(4):
        y0, x0 = rng.integers(0, size - 96, size=2)
        hh, ww = rng.integers(64, 200, size=2)
        image[y0 : y0 + hh, x0 : x0 + ww] = rng.uniform(40, 215, size=3) + rng.normal(0, 2.0, size=image[y0 : y0 + hh, x0 : x0 + ww].shape)
    return np.clip(np.rint(image), 0, 255).astype(np.uint8)


def load(device: str = "cuda"):
    import torch
    from diffusers import DDIMScheduler, StableDiffusionImg2ImgPipeline, StableDiffusionPipeline

    text = StableDiffusionPipeline.from_pretrained(ASSETS, variant="fp16", use_safetensors=True, local_files_only=True, torch_dtype=torch.float16)
    if text.safety_checker is None:
        raise RuntimeError("safety checker missing")
    text.scheduler = DDIMScheduler(**DDIM)
    text.set_progress_bar_config(disable=True)
    text.to(device)
    image = StableDiffusionImg2ImgPipeline(**text.components)
    image.set_progress_bar_config(disable=True)
    return text, image


def vae_round_trip(pipe, rgb: np.ndarray) -> np.ndarray:
    import torch
    from PIL import Image

    with torch.inference_mode():
        inputs = pipe.image_processor.preprocess(Image.fromarray(rgb)).to(device="cuda", dtype=pipe.vae.dtype)
        decoded = pipe.vae.decode(pipe.vae.encode(inputs).latent_dist.mode(), return_dict=False)[0]
        image = pipe.image_processor.postprocess(decoded, output_type="pil", do_denormalize=[True])[0]
    return np.asarray(image, dtype=np.uint8)


def regenerate(pipe, rgb: np.ndarray, strength: float, seed: int) -> np.ndarray | None:
    import torch
    from PIL import Image

    with torch.inference_mode():
        result = pipe(
            prompt="", negative_prompt="", image=Image.fromarray(rgb), strength=strength, num_inference_steps=20, eta=0.0,
            guidance_scale=1.0, generator=torch.Generator(device="cuda").manual_seed(seed), num_images_per_prompt=1, output_type="pil",
        )
    if result.nsfw_content_detected and result.nsfw_content_detected[0]:
        return None
    return np.asarray(result.images[0], dtype=np.uint8)


def hosts(text_pipe, count: int, directory: Path) -> list[tuple[str, np.ndarray]]:
    import torch
    from PIL import Image

    directory.mkdir(parents=True, exist_ok=True)
    out = []
    for index in range(4):
        out.append((f"procedural-{index}", procedural(100 + index)))
    for index, prompt in enumerate(PROMPTS[:count]):
        path = directory / f"generated-{index:02d}.png"
        if path.exists():
            out.append((f"generated-{index:02d}", np.asarray(Image.open(path).convert("RGB"))))
            continue
        with torch.inference_mode():
            result = text_pipe(
                prompt=prompt, negative_prompt="", height=512, width=512, num_inference_steps=25, guidance_scale=7.5,
                generator=torch.Generator(device="cuda").manual_seed(1000 + index), output_type="pil",
            )
        if result.nsfw_content_detected and result.nsfw_content_detected[0]:
            continue
        result.images[0].save(path)
        out.append((f"generated-{index:02d}", np.asarray(result.images[0])))
    for name, rgb in out[:4]:
        Image.fromarray(rgb).save(directory / f"{name}.png")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--amplitude", type=float, default=AMPLITUDE)
    parser.add_argument("--tag", default="probe")
    args = parser.parse_args()
    offline()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    text_pipe, image_pipe = load()
    started = time.time()
    images = hosts(text_pipe, args.generated, OUTPUT / "hosts")
    channel_names = ["vae"] + [f"sd{strength}" for strength in STRENGTHS]

    def send(rgb: np.ndarray) -> dict[str, np.ndarray | None]:
        out = {"vae": vae_round_trip(image_pipe, rgb)}
        for strength in STRENGTHS:
            out[f"sd{strength}"] = regenerate(image_pipe, rgb, strength, args.seed)
        return out

    shape = (len(CHANNELS), len(SCALES), 8, 8)
    host_sq = np.zeros(shape)
    host_n = np.zeros(shape)
    noise_sq = {name: np.zeros(shape) for name in channel_names}
    cross = {name: np.zeros(shape) for name in channel_names}
    power = {name: np.zeros(shape) for name in channel_names}
    count = {name: np.zeros(shape) for name in channel_names}
    blocked = 0
    rng = np.random.default_rng(20261002)
    for name, rgb in images:
        clean = send(rgb)
        base = to_ycc(rgb)
        clean_ycc = {key: None if value is None else to_ycc(value) for key, value in clean.items()}
        for c in range(len(CHANNELS)):
            for s, scale in enumerate(SCALES):
                coefficients = coarse_dct(base[..., c], scale)
                host_sq[c, s] += (coefficients**2).sum(axis=(0, 1))
                host_n[c, s] += coefficients.shape[0] * coefficients.shape[1]
                change, moved = band_change(rgb.shape[:2], scale, rng, args.amplitude)
                marked = np.clip(np.rint(rgb.astype(np.float64) + ycc_delta_to_rgb(c, change)), 0, 255).astype(np.uint8)
                moved = coarse_dct(to_ycc(marked)[..., c], scale) - coefficients  # what rounding and clipping left
                sent = send(marked)
                for key in channel_names:
                    if sent[key] is None or clean_ycc[key] is None:
                        blocked += 1
                        continue
                    after_clean = coarse_dct(clean_ycc[key][..., c], scale)
                    after_marked = coarse_dct(to_ycc(sent[key])[..., c], scale)
                    noise_sq[key][c, s] += ((after_clean - coefficients) ** 2).sum(axis=(0, 1))
                    cross[key][c, s] += ((after_marked - after_clean) * moved).sum(axis=(0, 1))
                    power[key][c, s] += (moved**2).sum(axis=(0, 1))
                    count[key][c, s] += coefficients.shape[0] * coefficients.shape[1]
        print(name, f"{time.time() - started:.0f}s", flush=True)
    report = {
        "label": "synthetic development probe; not study evidence",
        "hosts": [name for name, _ in images],
        "amplitude": args.amplitude,
        "seed": args.seed,
        "scales": list(SCALES),
        "channels": list(CHANNELS),
        "safety_blocked_calls": blocked,
        "host_rms": np.sqrt(host_sq / host_n).tolist(),
        "channel": {
            key: {
                "noise_rms": np.sqrt(noise_sq[key] / np.maximum(count[key], 1)).tolist(),
                "gain": (cross[key] / np.maximum(power[key], 1e-12)).tolist(),
            }
            for key in channel_names
        },
        "seconds": time.time() - started,
    }
    path = OUTPUT / f"{args.tag}.json"
    path.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
