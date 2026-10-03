"""Exploratory VAE decoder reconstruction diagnostic; no watermark or diffusion.

Optimizes only the VAE latent against reserved development source RGB pixels.
Reports saved RGB8 quality at fixed steps; no source residual is composed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ASSETS = MAIN / ".thesis-build/assets/a6"
IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
CONFIG = {"steps": [0, 50, 100, 200], "learning_rate": 0.02,
          "precision": "float32", "batch_size": 1, "size": [512, 512],
          "gpu_budget_bytes": 10 * 1024**3, "seed": 0,
          "objective": "RGB pixel MSE", "decoder_checkpoint": True}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024**2), b""):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def cases_for(manifest):
    split = manifest.get("data_split")
    if split not in ("synthetic", "development"):
        raise ValueError("Only synthetic/development manifests are allowed")
    cases = manifest.get("cases", [])
    if not cases or len({str(c["id"]) for c in cases}) != len(cases):
        raise ValueError("Explicit nonempty unique cases are required")
    original = json.loads((ROOT / "experiments/c4-qim-rgb-development-v1/cohort.json").read_text())["cases"]
    extra = json.loads((ROOT / "experiments/c4-three-threat-small-v1/development-expansion.json").read_text())["new_cases"]
    authorized = {c["source_id"]: c for c in original + extra}
    for case in cases:
        if split == "development":
            ident = case["id"]
            if type(ident) is not int or ident not in IDS:
                raise ValueError("Unreserved development ID")
            record = authorized[ident]
            if Path(case["path"]).resolve() != Path(record["path"]).resolve() or case["sha256"] != record["raw_sha256"]:
                raise ValueError("Development path/hash differs from reservation")
        elif "procedural_seed" in case:
            if type(case["procedural_seed"]) is not int or case["procedural_seed"] not in range(100, 104):
                raise ValueError("Only procedural seeds 100..103 are allowed")
        else:
            path = Path(case["path"]).resolve()
            expected = MAIN / ".thesis-build/rehearsal/v5-channel-dev/hosts" / path.name
            if path != expected.resolve() or path.name not in {f"generated-{i:02d}.png" for i in range(12)}:
                raise ValueError("Unreserved synthetic host")
            if not isinstance(case.get("sha256"), str):
                raise ValueError("Synthetic file hash required")
    if manifest.get("config", CONFIG) != CONFIG:
        raise ValueError("Fixed diagnostic config differs")
    return cases


def quality(source, rgb):
    import numpy as np
    from scipy.ndimage import gaussian_filter
    x, y = source.astype(np.float64), rgb.astype(np.float64)
    mse = float(np.mean((x-y)**2))
    # Wang-style Gaussian-window SSIM, RGB channel mean, 11x11 valid window.
    filt = lambda a: gaussian_filter(a, sigma=(1.5, 1.5, 0), truncate=3.5, mode="reflect")
    ux, uy = filt(x), filt(y)
    vx, vy, cov = filt(x*x)-ux*ux, filt(y*y)-uy*uy, filt(x*y)-ux*uy
    score = ((2*ux*uy+6.5025)*(2*cov+58.5225))/((ux*ux+uy*uy+6.5025)*(vx+vy+58.5225))
    return {"mse_rgb8": mse, "psnr_db": None if mse == 0 else float(10*np.log10(255**2/mse)),
            "psnr_infinite": mse == 0, "ssim_rgb": float(score[5:-5, 5:-5].mean()),
            "ssim_definition": "Gaussian sigma1.5 population covariance, 11x11 valid RGB mean"}


def run(manifest_path, output):
    started = time.monotonic()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases = cases_for(manifest)
    output.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    record = {"schema_version": "m1-development-run-v1", "commit": commit,
              "command": sys.argv, "config": CONFIG, "seeds": [0],
              "data_split": manifest["data_split"], "manifest_sha256": sha(manifest_path),
              "script_sha256": sha(__file__), "duration_seconds": 0,
              "outcome": "started", "cases": [], "environment": {"python": sys.version},
              "label": "Exploratory pure-decoder reconstruction; no watermark, no method success",
              "safety": "No diffusion generation; VAE reconstruction safety not assessed"}
    write(output / "run.json", record)
    journal = output / "images.jsonl"
    def event(value):
        with journal.open("a", encoding="utf-8") as f:
            f.write(json.dumps(value, allow_nan=False) + "\n")
    try:
        from three_threat_models import block_network
        block_network()
        import numpy as np
        import torch
        from torch.utils.checkpoint import checkpoint
        from diffusers import AutoencoderKL
        from PIL import Image, ImageOps, ImageCms
        import io
        record["environment"].update({p: importlib.metadata.version(p) for p in
                                    ("torch", "numpy", "scipy", "Pillow", "diffusers", "lpips")})
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable; no silent CPU substitution")
        torch.cuda.set_per_process_memory_fraction(CONFIG["gpu_budget_bytes"] / torch.cuda.get_device_properties(0).total_memory)
        torch.manual_seed(0)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        record["environment"]["gpu"] = torch.cuda.get_device_name(0)
        lock = json.loads((ROOT / "research/a6-candidate-model-assets.json").read_text())
        vae_files = [x for x in lock["files"] if x["path"].startswith("sd15-fp16/vae/")]
        record["asset_files"] = vae_files
        for item in vae_files:
            path = ASSETS / item["path"]
            if path.stat().st_size != item["size_bytes"] or sha(path) != item["sha256"]:
                raise ValueError("VAE asset mismatch: " + item["path"])
        vae = AutoencoderKL.from_pretrained(ASSETS / "sd15-fp16/vae", variant="fp16", use_safetensors=True,
                                           local_files_only=True, torch_dtype=torch.float32).eval().requires_grad_(False).to("cuda")
        record["resolved_vae_scaling_factor"] = float(vae.config.scaling_factor)
        record["latent_units"] = "unscaled VAE posterior mode; decoder receives same units"
        metric = None
        try:
            from three_threat_models import load_lpips
            from check_a6_lpips_assets import verify_package
            alex = next(x for x in lock["files"] if x["path"].startswith("alexnet/"))
            if sha(ASSETS / alex["path"]) != alex["sha256"]:
                raise ValueError("AlexNet asset hash mismatch")
            package = Path(importlib.metadata.distribution("lpips").locate_file("lpips"))
            verify_package(package)
            metric = load_lpips(ASSETS, package)
            record["lpips_asset_files"] = [alex]
            record["lpips_learned_sha256"] = sha(package / "weights/v0.1/alex.pth")
        except Exception as error:
            record["lpips_unavailable"] = str(error)
        write(output / "run.json", record)
        for case in cases:
            row = {"id": case["id"], "outcome": "started", "checkpoints": []}
            record["cases"].append(row)
            event({"phase": "image_started", "id": case["id"]})
            write(output / "run.json", record)
            try:
                if "procedural_seed" in case:
                    from dev_v5_channel_probe import procedural
                    native = procedural(case["procedural_seed"])
                else:
                    path = Path(case["path"])
                    if sha(path) != case["sha256"]:
                        raise ValueError("Input raw hash mismatch")
                    row.update(path=str(path), raw_sha256=case["sha256"])
                    with Image.open(path) as image:
                        if image.mode != "RGB":
                            raise ValueError("Only RGB sources allowed")
                        image.load()
                        icc = image.info.get("icc_profile")
                        image = ImageOps.exif_transpose(image)
                        if icc:
                            image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(icc)), ImageCms.createProfile("sRGB"), renderingIntent=0, outputMode="RGB", flags=0)
                        native = np.asarray(image).copy()
                row["native_shape"] = list(native.shape)
                source = np.asarray(Image.fromarray(native).resize((512,512), Image.Resampling.BICUBIC), dtype=np.uint8).copy()
                row["source_rgb8_sha256"] = hashlib.sha256(source.tobytes()).hexdigest()
                target = torch.from_numpy(source).permute(2,0,1).unsqueeze(0).float().to("cuda") / 255
                with torch.no_grad():
                    initial = vae.encode(target*2-1).latent_dist.mode()
                z = initial.detach().clone().requires_grad_(True)
                optimizer = torch.optim.Adam([z], lr=.02)
                torch.cuda.reset_peak_memory_stats()
                def decode(latent):
                    return (vae.decode(latent, return_dict=False)[0]+1)/2
                for step in range(201):
                    if step in CONFIG["steps"]:
                        with torch.no_grad():
                            raw_decoded = decode(z)
                            float_mse = float((raw_decoded-target).square().mean().item())
                            displacement = float(torch.linalg.vector_norm(z-initial).item())
                            decoded = raw_decoded.clamp(0,1)
                            rgb = (decoded[0].permute(1,2,0).cpu().numpy()*255).round().astype(np.uint8)
                        stem = f"{case['id']}-step{step:03d}"
                        Image.fromarray(rgb).save(output / (stem+".png"))
                        torch.save({"z": z.detach().cpu(), "step": step, "latent_units": record["latent_units"]}, output / (stem+".pt"))
                        measurement = {"step": step, "objective_float_mse": float_mse,
                                       "latent_displacement_l2": displacement,
                                       **quality(source, rgb), "png_sha256": sha(output/(stem+".png")),
                                       "latent_sha256": sha(output/(stem+".pt")), "seconds": time.monotonic()-started}
                        if metric is not None:
                            from three_threat_models import lpips_score
                            measurement["lpips"] = lpips_score(metric, source, rgb)
                        row["checkpoints"].append(measurement)
                        event({"phase": "checkpoint", "id": case["id"], **measurement})
                        write(output / "run.json", record)
                    if step == 200:
                        break
                    optimizer.zero_grad(set_to_none=True)
                    decoded = checkpoint(decode, z, use_reentrant=False)
                    loss = (decoded-target).square().mean()
                    if not bool(torch.isfinite(loss)):
                        raise RuntimeError("Nonfinite loss")
                    loss.backward()
                    if z.grad is None or not bool(torch.isfinite(z.grad).all()):
                        raise RuntimeError("Missing/nonfinite latent gradient")
                    optimizer.step()
                    if (step+1) % 10 == 0:
                        event({"phase": "update", "id": case["id"], "step": step+1,
                               "loss_before_update": float(loss.detach().item()),
                               "seconds": time.monotonic()-started})
                    if torch.cuda.memory_allocated() > CONFIG["gpu_budget_bytes"]:
                        raise RuntimeError("GPU allocation budget exceeded")
                row.update(outcome="completed", peak_allocated_bytes=torch.cuda.max_memory_allocated())
                del target, initial, z, optimizer, decoded, raw_decoded, loss
                torch.cuda.empty_cache()
            except Exception as error:
                row.update(outcome="failed", error=str(error), traceback=traceback.format_exc())
                event({"phase": "image_failed", "id": case["id"], "error": str(error)})
                # Stop after a failure; planned cases remain explicit missing outcomes.
                raise
        record["outcome"] = "completed"
    except Exception as error:
        record.update(outcome="failed", error=str(error), traceback=traceback.format_exc())
    finally:
        attempted = {str(r["id"]) for r in record["cases"]}
        for case in cases:
            if str(case["id"]) not in attempted:
                record["cases"].append({"id": case["id"], "outcome": "not_attempted_after_failure"})
        record["duration_seconds"] = time.monotonic()-started
        write(output / "run.json", record)
    return 0 if record["outcome"] == "completed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    return run(args.manifest.resolve(), args.output_dir.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
