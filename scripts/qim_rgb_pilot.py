"""Frozen CPU RGB/PNG development pilot for the supplied DCT-QIM candidate."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import platform
import resource
import time
from pathlib import Path

import numpy as np
import PIL
from PIL import Image, ImageCms, ImageOps
import skimage
from skimage.metrics import structural_similarity

from revised_watermark import DEFAULT_PROFILE, detect, embed, load_profile

ROOT = Path(__file__).resolve().parents[1]
OWNERS = ("qim-pilot-owner-alpha", "qim-pilot-owner-beta", "qim-pilot-owner-gamma", "qim-pilot-owner-delta")
CONDITIONS = ("native_png", "jpeg_q80", "noise_sigma1", "resize075_restore", "shift1_left_restore")


def host_path(value):
    value = str(value).replace("\\", "/")
    return Path("/mnt/" + value[0].lower() + value[2:]) if len(value) > 2 and value[1:3] == ":/" else Path(value)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def luminance(rgb):
    rgb = np.asarray(rgb, dtype=np.float64)
    return rgb[..., 0] * .299 + rgb[..., 1] * .587 + rgb[..., 2] * .114


def mark_rgb(rgb, profile):
    source = luminance(rgb)
    marked_y = np.asarray(embed(source.tolist(), OWNERS[0], profile=profile), dtype=np.float64)
    delta = marked_y - source
    return np.rint(np.clip(np.asarray(rgb, dtype=np.float64) + delta[..., None], 0, 255)).astype(np.uint8)


def canonical_rgb(path):
    with Image.open(path) as image:
        if image.mode != "RGB" or image.format not in ("JPEG", "PNG"):
            raise ValueError("unsupported source mode/format")
        image.load()
        icc = image.info.get("icc_profile")
        image = ImageOps.exif_transpose(image)
        if icc:
            image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(icc)), ImageCms.createProfile("sRGB"), renderingIntent=0, outputMode="RGB", flags=0)
        return np.asarray(image, dtype=np.uint8).copy()


def persist_rgb(path, rgb):
    Image.fromarray(rgb).save(path, format="PNG", compress_level=6, optimize=False)
    with Image.open(path) as image:
        image.load()
        observed = np.asarray(image, dtype=np.uint8).copy()
    if not np.array_equal(observed, rgb):
        raise ValueError("PNG round trip changed RGB bytes")
    return observed


def transform(rgb, condition, seed):
    image = Image.fromarray(rgb)
    if condition == "native_png":
        return rgb.copy()
    if condition == "jpeg_q80":
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=80, subsampling=2, optimize=False, progressive=False)
        buffer.seek(0)
        with Image.open(buffer) as reopened:
            reopened.load()
            return np.asarray(reopened.convert("RGB"), dtype=np.uint8).copy()
    if condition == "noise_sigma1":
        noise = np.random.default_rng(seed).normal(0, 1, rgb.shape)
        return np.rint(np.clip(rgb.astype(np.float64) + noise, 0, 255)).astype(np.uint8)
    if condition == "resize075_restore":
        size = (round(image.width * .75), round(image.height * .75))
        return np.asarray(image.resize(size, Image.Resampling.BICUBIC).resize(image.size, Image.Resampling.BICUBIC), dtype=np.uint8).copy()
    if condition == "shift1_left_restore":
        return np.concatenate((rgb[:, 1:], rgb[:, -1:]), axis=1)
    raise ValueError("unknown frozen condition")


def quality(source, marked):
    error = float(np.mean((source.astype(np.float64) - marked.astype(np.float64)) ** 2))
    return {"mse_rgb255": error, "psnr_db": None if error == 0 else 10 * math.log10(255 ** 2 / error), "zero_error": error == 0,
            "ssim_rgb": float(structural_similarity(source, marked, data_range=255, channel_axis=2, gaussian_weights=True, sigma=1.5, use_sample_covariance=False)),
            "lpips": {"status": "NOT_RUN", "reason": "This CPU codec pilot does not load learned quality weights."}}


def summarize(rows):
    summary = {"n_planned": 10, "n_completed": sum(row["status"] == "completed" for row in rows), "native_joint_passes": 0, "by_condition": {condition: {"c1_present": 0, "c0_present": 0, "c1_completed_calls": 0, "c0_completed_calls": 0, "planned_sources": 10} for condition in CONDITIONS}, "native_c2_present": 0, "native_c2_completed_calls": 0, "native_c2_planned_calls": 30, "full_quality_goal": "NOT_EVALUABLE_LPIPS_NOT_RUN", "confidence_interval": None}
    for row in rows:
        native = [item for item in row.get("detections", []) if item["condition"] == "native_png"]
        for item in row.get("detections", []):
            if item["control"] in ("C0", "C1"):
                summary["by_condition"][item["condition"]][item["control"].lower() + "_present"] += int(item["result"]["present"])
                summary["by_condition"][item["condition"]][item["control"].lower() + "_completed_calls"] += 1
            elif item["condition"] == "native_png":
                summary["native_c2_present"] += int(item["result"]["present"])
                summary["native_c2_completed_calls"] += 1
        q = row.get("quality", {})
        psnr_ok = q.get("zero_error", False) or (q.get("psnr_db") is not None and q["psnr_db"] > 35)
        positive = [item for item in native if item["control"] == "C1"]
        negative = [item for item in native if item["control"] in ("C0", "C2")]
        row["native_joint_pass"] = bool(row["status"] == "completed" and len(positive) == 1 and positive[0]["result"]["present"] and len(negative) == 4 and not any(item["result"]["present"] for item in negative) and row.get("changed_channels", 0) > 0 and psnr_ok and q.get("ssim_rgb", 0) > .9)
        summary["native_joint_passes"] += int(row["native_joint_pass"])
    summary["native_joint_pass_fraction"] = summary["native_joint_passes"] / 10
    summary["native_c2_missing_calls"] = 30 - summary["native_c2_completed_calls"]
    for value in summary["by_condition"].values():
        value["c0_missing_calls"] = 10 - value["c0_completed_calls"]
        value["c1_missing_calls"] = 10 - value["c1_completed_calls"]
    summary["engineering_verdict"] = "PASS_DEVELOPMENT_ONLY" if summary["native_joint_passes"] == 10 else "FAIL_OR_INCOMPLETE"
    return summary


def run(manifest, output):
    if manifest["experiment_id"] != "c4-qim-rgb-development-v1" or manifest["run_id"] != "c4-qim-rgb-dev-001" or manifest["resources"] != {"vram_mib": 0, "ram_mib": 4096, "disk_mib": 512}:
        raise ValueError("unexpected experiment/run/resources")
    if manifest["budget"] != {"max_seconds": 1200, "max_usd": 0, "hourly_usd": 0} or manifest["seeds"] != [0]:
        raise ValueError("unexpected time/cost/seed profile")
    resource.setrlimit(resource.RLIMIT_AS, (4096 * 1024 ** 2, 4096 * 1024 ** 2))
    if (platform.python_version(), PIL.__version__, np.__version__, skimage.__version__) != ("3.14.4", "12.3.0", "2.5.3", "0.26.0"):
        raise ValueError("pinned CPU runtime mismatch")
    for entry in manifest["inputs"]:
        if sha(ROOT / entry["path"]) != entry["sha256"]:
            raise ValueError("input hash mismatch: " + entry["path"])
    runtime = json.loads((ROOT / "experiments/c4-qim-rgb-development-v1/runtime-files.json").read_text())
    for entry in runtime["files"]:
        if sha(entry["path"]) != entry["sha256"]:
            raise ValueError("installed numerical runtime bytes changed")
    cohort = json.loads((ROOT / "experiments/c4-qim-rgb-development-v1/cohort.json").read_text())
    profile = load_profile(ROOT / "configs/revised-watermark.example.json")
    if json.dumps(profile, sort_keys=True) != json.dumps(DEFAULT_PROFILE, sort_keys=True):
        raise ValueError("profile must equal the strictly typed frozen supplied example")
    cases = cohort["cases"]
    if [case["source_id"] for case in cases] != [6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768]:
        raise ValueError("cohort must contain exactly ten distinct cases")
    output = Path(output)
    (output / "outputs/images").mkdir(parents=True, exist_ok=False)
    rows = [{"source_id": case["source_id"], "status": "NOT_RUN"} for case in cases]
    started = time.monotonic()
    deadline = started + 1050
    receipt = {"python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__, "skimage": skimage.__version__, "platform": platform.platform(), "runtime_file_count": len(runtime["files"]), "runtime_file_inventory_sha256": sha(ROOT / "experiments/c4-qim-rgb-development-v1/runtime-files.json"), "cuda_used": False, "owners": list(OWNERS), "conditions": list(CONDITIONS), "profile": profile, "analysis_unit": "source", "n_planned": 10}
    write_json(output / "outputs/runtime.json", receipt)
    def checkpoint():
        summary = summarize(rows)
        write_json(output / "outputs/results.json", {"run_id": manifest["run_id"], "cases": rows, "summary": summary, "elapsed_seconds": time.monotonic() - started, "n_planned": 10, "method_acceptance": False})
    checkpoint()
    for index, case in enumerate(cases):
        row = rows[index]
        row["status"] = "running"
        row["detections"] = []
        checkpoint()
        try:
            if time.monotonic() >= deadline:
                raise TimeoutError("internal total CPU deadline")
            path = host_path(case["path"])
            if sha(path) != case["raw_sha256"]:
                raise ValueError("raw source hash mismatch")
            source = canonical_rgb(path)
            if source.shape != (case["height"], case["width"], 3):
                raise ValueError("native dimensions differ from frozen source manifest")
            marked = mark_rgb(source, profile)
            row["images"] = []
            for name, rgb in (("source", source), ("marked", marked)):
                destination = output / "outputs/images" / (str(case["source_id"]) + "-" + name + ".png")
                observed = persist_rgb(destination, rgb)
                row["images"].append({"path": str(destination.relative_to(output)), "sha256": sha(destination), "pixel_sha256": hashlib.sha256(observed.tobytes()).hexdigest()})
                if name == "marked":
                    marked = observed
                else:
                    source = observed
            row["quality"] = quality(source, marked)
            row["changed_channels"] = int(np.count_nonzero(source != marked))
            for condition in CONDITIONS:
                seed = int(case["source_id"])
                for control, rgb, owners in (("C0", source, OWNERS[:1]), ("C1", marked, OWNERS[:1]), ("C2", marked, OWNERS[1:])):
                    if condition != "native_png" and control == "C2":
                        continue
                    if time.monotonic() >= deadline:
                        raise TimeoutError("internal total CPU deadline")
                    transformed = transform(rgb, condition, seed)
                    destination = output / "outputs/images" / (str(case["source_id"]) + "-" + control + "-" + condition + ".png")
                    if not destination.exists():
                        transformed = persist_rgb(destination, transformed)
                    else:
                        with Image.open(destination) as reopened:
                            transformed = np.asarray(reopened, dtype=np.uint8).copy()
                    for owner in owners:
                        before = time.monotonic()
                        decision = detect(luminance(transformed).tolist(), owner, profile=profile)
                        row["detections"].append({"condition": condition, "control": control, "claimed_owner": owner, "result": decision, "seconds": time.monotonic() - before, "path": str(destination.relative_to(output)), "sha256": sha(destination)})
                    checkpoint()
            row["status"] = "completed"
        except Exception as error:
            row["status"] = "failed"
            row["error"] = {"type": type(error).__name__, "message": str(error)}
        checkpoint()
    return 0 if all(row["status"] == "completed" for row in rows) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    raise SystemExit(run(json.loads(host_path(args.manifest).read_text()), host_path(args.output_dir)))
