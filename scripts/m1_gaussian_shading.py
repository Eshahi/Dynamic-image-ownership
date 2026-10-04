"""Exploratory SD1.5 adaptation of Gaussian Shading; native inversion detector.

Not proposal DCT extraction, existing-photo attribution, cryptographic proof, or
confirmatory evidence. SHAKE256 replaces unavailable ChaCha20 for this baseline.
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
CONFIG = {
    "generation_steps": 50, "generation_cfg": 7.5,
    "inversion_steps": 50, "inversion_cfg": 1.0,
    "attack_steps": 20, "attack_cfg": 1.0, "attack_eta": 0.0,
    "strengths": [0.05, 0.1, 0.2, 0.4], "attack_seeds": [0, 1, 2],
    "payload_bits": 256, "channel_factor": 1, "hw_factor": 8,
    "threshold": 0.7, "size": [512, 512], "precision": "float16",
    "whitening": "SHAKE256-domain-separated-key-nonce-XOR",
    "gpu_budget_bytes": 10 * 1024**3,
}
PROMPTS = [
    "a photograph of a mountain lake at sunrise, detailed landscape",
    "a photograph of a city street with parked cars and shop fronts",
    "a close-up photograph of a bowl of fruit on a wooden table",
    "a photograph of a brown dog running on a beach",
]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024**2), b""):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def require_committed(paths):
    receipts = {}
    for path in paths:
        path = Path(path).resolve()
        relative = path.relative_to(ROOT).as_posix()
        committed = subprocess.check_output(["git", "rev-parse", "HEAD:" + relative], cwd=ROOT, text=True).strip()
        current = subprocess.check_output(["git", "hash-object", "--path=" + relative, str(path)], cwd=ROOT, text=True).strip()
        if current != committed:
            raise ValueError("Scientific input differs from HEAD: " + relative)
        receipts[relative] = {"working_sha256": digest(path), "git_blob_oid": committed}
    return receipts


def channels_for_run():
    return [("clean", None, None), ("vae", None, None)] + [
        (f"regen-{s:g}-seed{a}", s, a) for s in CONFIG["strengths"] for a in CONFIG["attack_seeds"]]


def expected_artifacts(manifest):
    return {f"{c['id']}-{arm}-{channel}.png" for c in manifest["cases"] for arm in ("C0", "C1")
            for channel in ["original"] + [x[0] for x in channels_for_run()]}


def verify_artifact(output, name, artifacts):
    path = output / name
    receipt = artifacts.get(name)
    if receipt is None or not path.is_file() or path.stat().st_size != receipt["size_bytes"] or digest(path) != receipt["sha256"]:
        raise ValueError("Missing/corrupt/unreceipted artifact; refused reuse/overwrite: " + name)
    return path


def save_artifact(image, output, name, artifacts):
    path = output / name
    if path.exists() or name in artifacts:
        raise ValueError("Refused artifact overwrite: " + name)
    image.save(path)
    artifacts[name] = {"sha256": digest(path), "size_bytes": path.stat().st_size}
    write(output / "artifacts.json", artifacts)


def load_resume_state(output, manifest, prior=None):
    """Validate before model imports; refuse truncated journals without altering bytes."""
    receipt_path = output / "artifacts.json"
    artifacts = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {}
    expected = expected_artifacts(manifest)
    if not isinstance(artifacts, dict) or set(artifacts) - expected:
        raise ValueError("Unexpected artifact receipt entries")
    for name in artifacts:
        verify_artifact(output, name, artifacts)
    for path in output.glob("*.png"):
        if path.name not in artifacts:
            raise ValueError("Unreceipted artifact preserved; refused overwrite: " + path.name)
    journal = output / "rows.jsonl"
    row_receipt = output / "rows-receipt.json"
    rows = []
    if journal.exists():
        raw = journal.read_bytes()
        if raw and not raw.endswith(b"\n"):
            raise ValueError("Truncated journal preserved unchanged; manual versioned recovery required")
        if not row_receipt.is_file():
            raise ValueError("Journal receipt missing; journal preserved unchanged")
        pinned = json.loads(row_receipt.read_text(encoding="utf-8"))
        if pinned.get("sha256") != digest(journal) or pinned.get("size_bytes") != len(raw):
            raise ValueError("Journal receipt mismatch; journal preserved unchanged")
        try:
            rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
        except (ValueError, UnicodeError) as exc:
            raise ValueError("Invalid journal preserved unchanged") from exc
        if pinned.get("row_count") != len(rows):
            raise ValueError("Journal row count mismatch")
    elif row_receipt.exists():
        raise ValueError("Receipted journal missing")
    planned = {(c["id"], arm, x[0]): c for c in manifest["cases"] for arm in ("C0", "C1") for x in channels_for_run()}
    seen = set()
    for row in rows:
        key = (row.get("case"), row.get("arm"), row.get("channel"))
        if key not in planned or key in seen:
            raise ValueError("Unplanned/duplicate completed journal row")
        seen.add(key)
        case = planned[key]
        name = f"{key[0]}-{key[1]}-{key[2]}.png"
        if row.get("image") != name or row.get("prompt") != case["prompt"] or row.get("generation_seed") != case["seed"]:
            raise ValueError("Completed row identity mismatch")
        verify_artifact(output, name, artifacts)
        if row.get("image_sha256") != artifacts[name]["sha256"]:
            raise ValueError("Completed row image hash mismatch")
        verify_artifact(output, f"{key[0]}-{key[1]}-original.png", artifacts)
    if prior and prior.get("outcome") == "completed":
        if seen != set(planned) or set(artifacts) != expected or prior.get("completed_rows") != len(rows):
            raise ValueError("Completed run has missing rows/artifacts")
        for name in ("rows.jsonl", "artifacts.json", "rows-receipt.json", "summary.json"):
            path = output / name
            if not path.is_file() or prior.get("completed_file_sha256", {}).get(name) != digest(path):
                raise ValueError("Completed run provenance mismatch: " + name)
    return artifacts, rows, seen


def append_row(journal, row, row_count):
    with journal.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    write(journal.parent / "rows-receipt.json", {"sha256": digest(journal),
          "size_bytes": journal.stat().st_size, "row_count": row_count})


def bitstream(key, nonce, count, domain=b"m1-gs-whitening-v1"):
    import numpy as np
    key, nonce = bytes.fromhex(key), bytes.fromhex(nonce)
    if len(key) != 32 or len(nonce) != 12:
        raise ValueError("32-byte key and 12-byte nonce required")
    return np.unpackbits(np.frombuffer(hashlib.shake_256(domain + key + nonce).digest((count+7)//8), dtype=np.uint8))[:count]


def payload_for(seed):
    import numpy as np
    raw = hashlib.shake_256(b"m1-gs-payload-v1" + str(seed).encode()).digest(32)
    return np.unpackbits(np.frombuffer(raw, dtype=np.uint8)).reshape(4, 8, 8)


def nonce_for(seed):
    return hashlib.sha256(b"m1-gs-nonce-v1" + str(seed).encode()).hexdigest()[:24]


def embed_signs(payload, key, nonce):
    import numpy as np
    if np.asarray(payload).shape != (4, 8, 8) or not np.isin(payload, [0, 1]).all():
        raise ValueError("256 binary payload bits required")
    return np.tile(payload, (1, 8, 8)).reshape(-1) ^ bitstream(key, nonce, 16384)


def decode(noise, key, nonce):
    import numpy as np
    noise = np.asarray(noise)
    if noise.size != 16384 or not np.isfinite(noise).all():
        raise ValueError("finite SD1.5 latent required")
    plain = ((noise.reshape(-1) > 0).astype(np.uint8) ^ bitstream(key, nonce, 16384)).reshape(4, 64, 64)
    # Tile order matches official .repeat(1, fc, fhw, fhw), ties become zero.
    return (plain.reshape(4, 8, 8, 8, 8).sum(axis=(1, 3)) > 32).astype(np.uint8)


def validate(manifest):
    if manifest.get("data_split") != "synthetic" or manifest.get("config") != CONFIG:
        raise ValueError("Fixed synthetic development manifest required")
    expected = [{"id": f"prompt-{i}", "prompt": p, "seed": 1000+i} for i, p in enumerate(PROMPTS)]
    if manifest.get("cases") != expected:
        raise ValueError("Only four preregistered synthetic prompt/seed cases permitted")
    for name in ("development_key_hex", "wrong_key_hex"):
        if len(bytes.fromhex(manifest[name])) != 32:
            raise ValueError("Invalid development key")
    if manifest["development_key_hex"] == manifest["wrong_key_hex"]:
        raise ValueError("Wrong key must differ")


def invert(pipe, image, inverse_scheduler):
    import torch
    with torch.inference_mode():
        x = pipe.image_processor.preprocess(image).to("cuda", dtype=pipe.vae.dtype)
        z = pipe.vae.encode(x).latent_dist.mode() * pipe.vae.config.scaling_factor
        emb, _ = pipe.encode_prompt("", "cuda", 1, False)
        inverse_scheduler.set_timesteps(CONFIG["inversion_steps"], device="cuda")
        for t in inverse_scheduler.timesteps:
            model_input = inverse_scheduler.scale_model_input(z, t)
            eps = pipe.unet(model_input, t, encoder_hidden_states=emb, return_dict=False)[0]
            z = inverse_scheduler.step(eps, t, z, return_dict=False)[0]
        if not torch.isfinite(z).all():
            raise RuntimeError("Nonfinite inversion latent")
        return z.float().cpu().numpy()


def run(manifest_path, output):
    started = time.monotonic()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate(manifest)
    dependency_names = ("three_threat_models.py", "three_threat_protocol.py", "m1_latent_reconstruction.py",
                        "check_a6_lpips_assets.py", "verify_science_assets.py", "a6_clip_visual.py")
    dependencies = [ROOT / "scripts" / name for name in dependency_names] + [ROOT / "research/a6-candidate-model-assets.json"]
    committed_files = require_committed([Path(__file__), manifest_path] + dependencies)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    fingerprint = {"manifest_sha256": digest(manifest_path), "script_sha256": digest(__file__), "commit": commit}
    fingerprint["dependency_sha256"] = {p.relative_to(ROOT).as_posix(): digest(p) for p in dependencies}
    fingerprint["committed_files"] = committed_files
    previous_duration = 0.0
    prior = None
    if output.exists():
        prior = json.loads((output / "run.json").read_text(encoding="utf-8"))
        if any(prior.get(k) != v for k, v in fingerprint.items()):
            raise ValueError("Resume requires identical manifest, script and commit")
        previous_duration = prior.get("duration_seconds", 0.0)
    else:
        output.mkdir(parents=True)
    artifacts, rows, done = load_resume_state(output, manifest, prior)
    if prior and prior.get("outcome") == "completed":
        return 0
    record = {"schema_version": "m1-gs-development-run-v1", **fingerprint,
              "command": sys.argv, "config": CONFIG, "seeds": [1000,1001,1002,1003,0,1,2],
              "data_split": "synthetic", "duration_seconds": previous_duration,
              "outcome": "started", "environment": {"python": sys.version},
              "detector_side_information": "SD1.5 model, empty prompt inversion, reference256-bit payload, secret whitening key and per-image nonce",
              "label": "Exploratory Gaussian Shading SD1.5/SHAKE adaptation, native inversion detector; no proposal/ownership claim",
              "false_positive_definition": "Empirical threshold0.7 positives on paired C0 images and C1 wrong-key queries; no population-FPR guarantee"}
    write(output / "run.json", record)
    journal = output / "rows.jsonl"
    try:
        from three_threat_models import block_network, DDIM_CONFIG, validate_generated, verify_assets, load_lpips, lpips_score
        block_network()
        import numpy as np
        import torch
        from PIL import Image
        from diffusers import DDIMScheduler, DDIMInverseScheduler, StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
        from m1_latent_reconstruction import quality
        record["environment"].update({p: importlib.metadata.version(p) for p in ("torch", "diffusers", "numpy", "Pillow", "lpips")})
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable")
        torch.cuda.set_per_process_memory_fraction(CONFIG["gpu_budget_bytes"] / torch.cuda.get_device_properties(0).total_memory)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        record["environment"]["gpu"] = torch.cuda.get_device_name(0)
        receipt, lpips_package = verify_assets(ASSETS, ROOT / "research/a6-candidate-model-assets.json")
        record["asset_receipt"] = receipt
        pipe = StableDiffusionPipeline.from_pretrained(ASSETS / "sd15-fp16", variant="fp16", use_safetensors=True,
                                                      local_files_only=True, torch_dtype=torch.float16).to("cuda")
        if pipe.safety_checker is None or pipe.feature_extractor is None:
            raise RuntimeError("Safety components missing")
        pipe.scheduler = DDIMScheduler(**DDIM_CONFIG)
        pipe.set_progress_bar_config(disable=True)
        attacker = StableDiffusionImg2ImgPipeline(**pipe.components)
        attacker.set_progress_bar_config(disable=True)
        inverse = DDIMInverseScheduler.from_config(pipe.scheduler.config)
        if inverse.config.prediction_type != "epsilon" or inverse.config.clip_sample:
            raise RuntimeError("Inverse scheduler differs from pinned epsilon unclipped config")
        record["scheduler"] = dict(pipe.scheduler.config)
        record["inverse_scheduler"] = dict(inverse.config)
        metric = load_lpips(ASSETS, lpips_package)
        from a6_clip_visual import load_visual_encoder
        from three_threat_models import clip_feature
        clip_model, clip_transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
        write(output / "run.json", record)
        channels = channels_for_run()
        for case in manifest["cases"]:
            cid, seed = case["id"], case["seed"]
            payload = payload_for(seed)
            nonce = nonce_for(seed)
            rng = np.random.default_rng(seed)
            base = rng.standard_normal((1,4,64,64)).astype(np.float32)
            marked = (np.abs(base).reshape(-1) * (2*embed_signs(payload, manifest["development_key_hex"], nonce).astype(np.float32)-1)).reshape(base.shape)
            originals = {}
            for arm, noise in (("C0", base), ("C1", marked)):
                path = output / f"{cid}-{arm}-original.png"
                if path.name not in artifacts:
                    with torch.inference_mode():
                        result = pipe(prompt=case["prompt"], negative_prompt="", height=512, width=512,
                                      num_inference_steps=50, guidance_scale=7.5, eta=0.0,
                                      latents=torch.from_numpy(noise).to("cuda",dtype=torch.float16),
                                      generator=torch.Generator(device="cuda").manual_seed(seed), output_type="pil")
                    save_artifact(validate_generated(result), output, path.name, artifacts)
                verify_artifact(output, path.name, artifacts)
                originals[arm] = Image.open(path).convert("RGB")
            clean_comparison = quality(np.asarray(originals["C0"]), np.asarray(originals["C1"]))
            clean_comparison["lpips_alex"] = lpips_score(metric, np.asarray(originals["C0"]), np.asarray(originals["C1"]))
            original_features = {arm: clip_feature(clip_model, clip_transform, np.asarray(im)) for arm, im in originals.items()}
            for channel, strength, attack_seed in channels:
                for arm in ("C0", "C1"):
                    if (cid, arm, channel) in done:
                        continue
                    row_started = time.monotonic()
                    source = originals[arm]
                    path = output / f"{cid}-{arm}-{channel}.png"
                    if path.name in artifacts:
                        verify_artifact(output, path.name, artifacts)
                        image = Image.open(path).convert("RGB")
                    else:
                        with torch.inference_mode():
                            if channel == "clean":
                                image = source
                            elif channel == "vae":
                                x = pipe.image_processor.preprocess(source).to("cuda",dtype=pipe.vae.dtype)
                                z = pipe.vae.encode(x).latent_dist.mode()
                                decoded = pipe.vae.decode(z,return_dict=False)[0]
                                checked, flags = pipe.run_safety_checker(decoded, "cuda", pipe.text_encoder.dtype)
                                if flags is None or len(flags)!=1 or bool(flags[0]):
                                    raise RuntimeError("VAE safety checker unavailable/blocked")
                                image = pipe.image_processor.postprocess(checked,output_type="pil",do_denormalize=[True])[0]
                            else:
                                result = attacker(prompt="", negative_prompt="", image=source, strength=strength,
                                                  num_inference_steps=20, guidance_scale=1.0, eta=0.0,
                                                  generator=torch.Generator(device="cuda").manual_seed(attack_seed), output_type="pil")
                                image = validate_generated(result)
                        save_artifact(image, output, path.name, artifacts)
                        image = Image.open(path).convert("RGB")
                    det_started = time.monotonic()
                    recovered = invert(pipe, image, inverse)
                    decoded = decode(recovered, manifest["development_key_hex"], nonce)
                    wrong = decode(recovered, manifest["wrong_key_hex"], nonce)
                    accuracy = float((decoded == payload).mean())
                    wrong_accuracy = float((wrong == payload).mean())
                    detector_seconds = time.monotonic() - det_started
                    q = quality(np.asarray(source), np.asarray(image))
                    q["lpips_alex"] = lpips_score(metric, np.asarray(source), np.asarray(image))
                    q["clip_cosine"] = float((original_features[arm] * clip_feature(clip_model, clip_transform, np.asarray(image))).sum())
                    row = {"case":cid,"prompt":case["prompt"],"generation_seed":seed,"arm":arm,"channel":channel,
                           "strength":strength,"attack_seed":attack_seed,"image":path.name,"image_sha256":digest(path),
                           "bit_accuracy":accuracy,"detected":accuracy>=CONFIG["threshold"],"exact_payload":accuracy==1.0,
                           "wrong_key_bit_accuracy":wrong_accuracy,"wrong_key_detected":wrong_accuracy>=CONFIG["threshold"],
                           "detector_seconds":detector_seconds,"detector_unet_evaluations":50,"quality_vs_same_arm_original":q,
                           "C1_quality_vs_paired_C0_clean":clean_comparison,"duration_seconds":time.monotonic()-row_started}
                    append_row(journal, row, len(rows)+1)
                    rows.append(row)
                    done.add((cid,arm,channel))
                    record.update(completed_rows=len(rows),duration_seconds=previous_duration+time.monotonic()-started)
                    write(output/"run.json",record)
                    print(json.dumps({"case":cid,"arm":arm,"channel":channel,"bit_accuracy":accuracy}),flush=True)
        summary = {}
        for channel, _, _ in channels:
            c0=[r for r in rows if r["channel"]==channel and r["arm"]=="C0"]
            c1=[r for r in rows if r["channel"]==channel and r["arm"]=="C1"]
            summary[channel]={"C1_n":len(c1),"C1_detected":sum(r["detected"] for r in c1),
                              "C1_mean_bit_accuracy":float(np.mean([r["bit_accuracy"] for r in c1])),
                              "C0_n":len(c0),"C0_false_positives":sum(r["detected"] for r in c0),
                              "C1_wrong_key_n":len(c1),"C1_wrong_key_false_positives":sum(r["wrong_key_detected"] for r in c1)}
        write(output/"summary.json",summary)
        record["completed_file_sha256"] = {name: digest(output/name) for name in
            ("rows.jsonl", "artifacts.json", "rows-receipt.json", "summary.json")}
        record.update(outcome="completed",completed_rows=len(rows),duration_seconds=previous_duration+time.monotonic()-started)
        write(output/"run.json",record)
        return 0
    except (Exception, KeyboardInterrupt) as exc:
        record.update(outcome="interrupted" if isinstance(exc, KeyboardInterrupt) else "error",error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc(),
                      completed_rows=len(rows),duration_seconds=previous_duration+time.monotonic()-started)
        record["recovery_file_sha256"] = {name: digest(output/name) for name in
            ("rows.jsonl", "artifacts.json", "rows-receipt.json") if (output/name).is_file()}
        write(output/"run.json",record)
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    args=p.parse_args()
    return run(args.manifest.resolve(),args.output_dir.resolve())


if __name__=="__main__":
    sys.exit(main())
