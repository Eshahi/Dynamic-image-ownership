"""Single fixed three-threat study worker; launch only through approved runner.

Every planned row exists before processing. Failures are retained, never retried.
No visual admissibility is inferred: two-reviewer labels are downstream evidence.
"""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import resource
import time

from three_threat_protocol import (EXPANDED_IDS, ORIGINAL_IDS, binding_distance,
                                  center_patch, inventory, residual_transfer)
from three_threat_models import block_network

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "experiments/c4-three-threat-small-v1"
RUN_ID = "c4-three-threat-small-dev-001"
OWNERS = ("qim-pilot-owner-alpha", "qim-pilot-owner-beta", "qim-pilot-owner-gamma",
          "qim-pilot-owner-delta", "wrong-owner-590")


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def run(manifest_path, output_path):
    block_network()
    import numpy as np
    import torch
    from PIL import Image
    from a6_clip_visual import load_visual_encoder
    from qim_rgb_pilot import (canonical_rgb, host_path, luminance, mark_rgb,
                               persist_rgb, quality, write_json)
    from revised_watermark import DEFAULT_PROFILE, detect, load_profile, perceptual_bits
    from three_threat_models import (clip_feature, load_lpips, load_regenerator,
                                    lpips_score, regeneration_kwargs,
                                    validate_generated, verify_assets)

    manifest = json.loads(host_path(manifest_path).read_text())
    if manifest["experiment_id"] != "c4-three-threat-small-v1" or manifest["run_id"] != RUN_ID or manifest["execution_target"] != "local":
        raise ValueError("unlisted scientific run")
    if manifest["seeds"] != [0, 1, 2] or manifest["budget"] != {"max_seconds": 86400, "max_usd": 0, "hourly_usd": 0}:
        raise ValueError("unexpected frozen seed/watchdog/cost profile")
    if manifest["resources"] != {"vram_mib": 8192, "ram_mib": 8192, "disk_mib": 2048}:
        raise ValueError("unexpected resource envelope")
    for item in manifest["inputs"]:
        if digest(ROOT / item["path"]) != item["sha256"]:
            raise ValueError("package input changed: " + item["path"])
    runtime = json.loads((PACKAGE / "runtime-files-v2.json").read_text())
    for item in runtime["files"]:
        if digest(item["path"]) != item["sha256"]:
            raise ValueError("installed runtime bytes changed: " + item["path"])
    profile = load_profile(ROOT / "configs/revised-watermark.example.json")
    if profile != DEFAULT_PROFILE:
        raise ValueError("supplied codec/profile must remain unchanged")
    original = json.loads((ROOT / "experiments/c4-qim-rgb-development-v1/cohort.json").read_text())["cases"]
    expansion = json.loads((PACKAGE / "development-expansion.json").read_text())
    cases = sorted(original + expansion["new_cases"], key=lambda row: row["source_id"])
    if tuple(row["source_id"] for row in original) != ORIGINAL_IDS or tuple(row["source_id"] for row in cases) != EXPANDED_IDS:
        raise ValueError("development cohort changed")
    labels = json.loads((PACKAGE / "semantic-labels.json").read_text())
    expected_pairs = {(row["left"], row["right"]) for row in inventory() if row["axis"] == "T5"}
    if len(labels["pairs"]) != 66 or {(row["left"], row["right"]) for row in labels["pairs"]} != expected_pairs:
        raise ValueError("semantic label inventory differs")
    assets = host_path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets/a6")
    receipt, lpips_package = verify_assets(assets, ROOT / "research/a6-candidate-model-assets.json")
    output = host_path(output_path)
    images_dir = output / "outputs/images"
    images_dir.mkdir(parents=True, exist_ok=False)
    if os.environ.get("PYTHONHASHSEED") != "0" or os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8":
        raise ValueError("deterministic launch environment missing")
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_num_threads(1)
    if not torch.cuda.is_available():
        raise RuntimeError("approved local CUDA device unavailable; no fallback")
    torch.cuda.reset_peak_memory_stats()
    free, total = torch.cuda.mem_get_info()
    if free < (8192 + 512) * 1024**2:
        raise RuntimeError("insufficient free VRAM for frozen envelope and headroom")
    started = time.monotonic()
    deadline = started + 86000
    rows = [{**item, "status": "NOT_RUN", "detections": [], "visual_retention": "NOT_REVIEWED"} for item in inventory()]
    row_index = {row["id"]: row for row in rows}
    label_index = {(row["left"], row["right"]): row for row in labels["pairs"]}
    failures = []
    saved = {}
    native_receipt = []
    runtime_receipt = {"asset_files": receipt["files"], "cuda_device": torch.cuda.get_device_name(),
                       "cuda_total_bytes": total, "cuda_free_before_bytes": free,
                       "runtime_inventory_sha256": digest(PACKAGE / "runtime-files-v2.json"),
                       "owners": OWNERS, "analysis": "exploratory; source clustered; visual labels pending",
                       "planned_detector_calls": 672, "planned_rows": len(rows),
                       "native_to_pilot": native_receipt}

    def checkpoint():
        write_json(output / "outputs/results.json", {"run_id": RUN_ID, "rows": rows,
                   "stage_failures": failures, "elapsed_seconds": time.monotonic() - started,
                   "scientific_verdict": "PENDING_ANALYSIS_AND_VISUAL_REVIEW",
                   "method_acceptance": False, "planned_detector_calls": 672,
                   "completed_detector_calls": sum(len(row["detections"]) for row in rows)})
        runtime_receipt["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        runtime_receipt["cuda_peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
        runtime_receipt["cuda_peak_reserved_bytes"] = torch.cuda.max_memory_reserved()
        write_json(output / "outputs/runtime.json", runtime_receipt)

    def guard():
        if time.monotonic() >= deadline:
            raise TimeoutError("fixed operational watchdog reached")
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > 8192 * 1024:
            raise MemoryError("RAM envelope exceeded; no automatic enlargement")
        if torch.cuda.max_memory_reserved() > 8192 * 1024**2:
            raise MemoryError("VRAM envelope exceeded; no automatic enlargement")
        if sum(path.stat().st_size for path in images_dir.iterdir() if path.is_file()) > 2000 * 1024**2:
            raise OSError("output image disk allowance exceeded")

    def fail(row, error):
        row["status"] = "failed"
        row["error"] = {"type": type(error).__name__, "message": str(error)}
        checkpoint()

    def save(row, rgb):
        guard()
        destination = images_dir / (row["id"] + ".png")
        observed = persist_rgb(destination, rgb)
        row["image"] = {"path": str(destination.relative_to(output)), "sha256": digest(destination),
                        "pixel_sha256": hashlib.sha256(observed.tobytes()).hexdigest()}
        saved[row["id"]] = destination
        row["status"] = "image_saved"
        checkpoint()
        return observed

    def read(identity):
        path = saved[identity]
        row = row_index[identity]
        if digest(path) != row["image"]["sha256"]:
            raise ValueError("saved suspect changed")
        with Image.open(path) as image:
            image.load()
            if image.mode != "RGB" or image.size != (512, 512):
                raise ValueError("saved RGB geometry changed")
            rgb = np.asarray(image, dtype=np.uint8).copy()
        if hashlib.sha256(rgb.tobytes()).hexdigest() != row["image"]["pixel_sha256"]:
            raise ValueError("saved suspect pixel hash changed")
        return rgb

    checkpoint()
    # Source/C0 checks remain independent of embedding success.
    for case in cases:
        identity = case["source_id"]
        c0, c1 = row_index[f"clean-{identity}-C0"], row_index[f"clean-{identity}-C1"]
        try:
            guard()
            path = host_path(case["path"])
            if digest(path) != case["raw_sha256"]:
                raise ValueError("native raw bytes changed")
            native = canonical_rgb(path)
            if native.shape != (case["height"], case["width"], 3):
                raise ValueError("native geometry changed")
            source = np.asarray(Image.fromarray(native).resize((512, 512), Image.Resampling.BICUBIC), dtype=np.uint8).copy()
            native_receipt.append({"source_id": identity, "raw_sha256": case["raw_sha256"],
                                   "native_shape": list(native.shape), "pilot_shape": [512, 512, 3],
                                   "native_pixel_sha256": hashlib.sha256(native.tobytes()).hexdigest()})
            source = save(c0, source)
        except Exception as error:
            fail(c0, error)
            fail(c1, RuntimeError("source prerequisite failed"))
            continue
        try:
            marked = save(c1, mark_rgb(source, profile))
            c1["changed_channels"] = int(np.count_nonzero(source != marked))
            c1["quality"] = quality(source, marked)
            c1["quality"]["lpips"] = {"status": "NOT_RUN", "reason": "pending separately resident evaluator phase"}
        except Exception as error:
            fail(c1, error)

    for row in rows:
        if row["axis"] != "T4":
            continue
        try:
            recipient = read(f"clean-{row['recipient_id']}-C0")
            if row["arm"] == "unmarked_patch_sham":
                donor0 = read(f"clean-{row['donor_id']}-C0")
                rgb = center_patch(recipient.tolist(), donor0.tolist(), row["patch_size"])
            elif row["arm"] == "public_patch":
                donor1 = read(f"clean-{row['donor_id']}-C1")
                rgb = center_patch(recipient.tolist(), donor1.tolist(), row["patch_size"])
            else:
                donor0 = read(f"clean-{row['donor_id']}-C0")
                donor1 = read(f"clean-{row['donor_id']}-C1")
                rgb = residual_transfer(recipient.tolist(), donor1.tolist(), donor0.tolist(), row["scale"])
            observed = save(row, np.asarray(rgb, dtype=np.uint8))
            row["quality"] = quality(recipient, observed)
            row["quality"]["lpips"] = {"status": "NOT_RUN", "reason": "pending evaluator"}
        except Exception as error:
            fail(row, error)

    # One model resident; no retries, no outcome-conditioned seed selection.
    pipeline = None
    try:
        guard()
        pipeline = load_regenerator(assets)
        from three_threat_models import DDIM_CONFIG
        runtime_receipt["effective_ddim_config"] = DDIM_CONFIG
        def on_step(pipe, step, timestep, values):
            guard()
            return values
        for row in rows:
            if row["axis"] != "T3":
                continue
            try:
                guard()
                rgb = read(f"clean-{row['source_id']}-{row['control']}")
                kwargs = regeneration_kwargs(row["strength"], row["seed"], Image.fromarray(rgb), torch.Generator)
                with torch.inference_mode():
                    result = pipeline(**kwargs, callback_on_step_end=on_step, callback_on_step_end_tensor_inputs=["latents"])
                row["safety_checked"] = True
                image = validate_generated(result)
                save(row, np.asarray(image, dtype=np.uint8).copy())
            except Exception as error:
                fail(row, error)
    except Exception as error:
        failures.append({"stage": "regenerator_load", "type": type(error).__name__, "message": str(error)})
    finally:
        del pipeline
        gc.collect()
        torch.cuda.empty_cache()
        checkpoint()

    # Suspect-only detector calls cannot see references, semantic labels or models.
    for row in rows:
        if row["axis"] == "T5" or row["status"] == "failed" or row["id"] not in saved:
            continue
        claimed = OWNERS if row["axis"] == "clean" and row["control"] == "C1" else OWNERS[:4] if row["axis"] == "T3" else OWNERS[:1]
        try:
            rgb = read(row["id"])
            for owner in claimed:
                guard()
                result = detect(luminance(rgb).tolist(), owner, profile=profile)
                row["detections"].append({"claimed_owner": owner, "result": result})
                checkpoint()
            row["status"] = "detected"
        except Exception as error:
            fail(row, error)

    metric = None
    try:
        guard()
        metric = load_lpips(assets, lpips_package)
        for row in rows:
            if row["axis"] == "T5" or row["status"] != "detected":
                continue
            try:
                guard()
                suspect = read(row["id"])
                if row["axis"] == "clean":
                    references = {"quality": f"clean-{row['source_id']}-C0"}
                elif row["axis"] == "T4":
                    references = {"quality": f"clean-{row['recipient_id']}-C0"}
                else:
                    references = {"quality_immediate": f"clean-{row['source_id']}-{row['control']}",
                                  "quality_source": f"clean-{row['source_id']}-C0"}
                for name, identity in references.items():
                    reference = read(identity)
                    scores = quality(reference, suspect)
                    scores["lpips"] = {"status": "measured", "value": lpips_score(metric, reference, suspect)}
                    row[name] = scores
                row["status"] = "metrics_complete"
                checkpoint()
            except Exception as error:
                fail(row, error)
    except Exception as error:
        failures.append({"stage": "lpips_load", "type": type(error).__name__, "message": str(error)})
    finally:
        del metric
        gc.collect()
        checkpoint()

    model = transform = None
    try:
        guard()
        model, transform = load_visual_encoder(assets / "clip/ViT-B-32.pt", device="cpu")
        features = {}
        bindings = {}
        marked_bindings = {}
        for identity in EXPANDED_IDS:
            try:
                guard()
                source = read(f"clean-{identity}-C0")
                features[identity] = clip_feature(model, transform, source)
                bindings[identity] = perceptual_bits(luminance(source).tolist()) >> 4
                marked = read(f"clean-{identity}-C1")
                marked_bindings[identity] = perceptual_bits(luminance(marked).tolist()) >> 4
                row_index[f"clean-{identity}-C1"]["same_instance_binding_distance"] = binding_distance(bindings[identity], marked_bindings[identity])
            except Exception as error:
                failures.append({"stage": "clip_binding_source", "source_id": identity,
                                 "type": type(error).__name__, "message": str(error)})
                checkpoint()
        for row in rows:
            try:
                guard()
                if row["axis"] == "T3" and row["status"] == "metrics_complete":
                    feature = clip_feature(model, transform, read(row["id"]))
                    row["clip_source_cosine"] = float((features[row["source_id"]] * feature).sum())
                    row["clip_retention_threshold"] = 0.90
                elif row["axis"] == "T5":
                    left, right = row["left"], row["right"]
                    row["semantic_label"] = label_index[(left, right)]["label"]
                    row["binding_distance_source"] = binding_distance(bindings[left], bindings[right])
                    row["binding_distance_marked"] = binding_distance(marked_bindings[left], marked_bindings[right])
                    row["clip_pair_cosine"] = float((features[left] * features[right]).sum())
                    row["status"] = "complete_component_diagnostic"
                checkpoint()
            except Exception as error:
                fail(row, error)
    except Exception as error:
        failures.append({"stage": "clip_binding", "type": type(error).__name__, "message": str(error)})
    finally:
        del model, transform
        gc.collect()
        checkpoint()
    # Visual labels remain intentionally absent, never fabricated as a verdict.
    complete = (not failures and all(row["status"] in ("metrics_complete", "complete_component_diagnostic") for row in rows)
                and sum(len(row["detections"]) for row in rows) == 672)
    return 0 if complete else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    arguments = parser.parse_args()
    raise SystemExit(run(arguments.manifest, arguments.output_dir))
