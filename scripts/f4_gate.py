"""M1a regeneration gate for family 4 (chroma-channel carrier), development sources only.

Embeds owner alpha into the twelve canonical development sources (the exact
pixels of the v5 dev-001 study), then runs the v5 study's attack grid on the
marked (C1) and unmarked (C0) images: clean, VAE posterior mode, and pinned
SD1.5 DDIM img2img at .05/.1/.2/.4 with seeds 0/1/2.  Every image is read
blind by :func:`f4_chroma_codec.detect_rgb` for the four study owners with the
suspect's own CLIP features.  Safety-checker blocks stay as missing rows.  The
summary joins C1 semantic success with v5 dev-001 by source/strength/seed.
"""
from __future__ import annotations

import argparse, hashlib, importlib.metadata, json, subprocess, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from scripts import f4_chroma_codec as f4  # noqa: E402
from scripts import revised_watermark_v5 as v5  # noqa: E402
from f4_transfer_probe import SOURCES, MAIN, ASSETS  # noqa: E402

OWNERS = ("qim-pilot-owner-alpha", "qim-pilot-owner-beta", "qim-pilot-owner-gamma", "qim-pilot-owner-delta")
STRENGTHS = (0.05, 0.1, 0.2, 0.4)
SEEDS = (0, 1, 2)
V5_RESULTS = MAIN / ".thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001/outputs/results.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_WORKER = {}


def _init_worker(profile_json: str):
    import torch
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder
    torch.set_num_threads(1)
    _WORKER["clip"], _WORKER["transform"] = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
    _WORKER["models"], _WORKER["profile"] = models, json.loads(profile_json)


def _read_job(path: str) -> dict:
    """Blind reading of one saved PNG for every study owner, with the suspect's own CLIP features."""
    from PIL import Image
    rgb = np.asarray(Image.open(path).convert("RGB"), np.uint8)
    vector = _WORKER["models"].clip_feature(_WORKER["clip"], _WORKER["transform"], rgb).reshape(-1).tolist()
    calls = {}
    for owner in OWNERS:
        r = f4.detect_rgb(rgb.tolist(), owner, _WORKER["profile"], vector)
        calls[owner] = dict(outcome=r["outcome"], semantic_found=r["semantic"]["found"],
                            semantic_content_match=r["semantic"]["content_match"],
                            semantic_score=r["semantic"]["score"], semantic_threshold=r["semantic"]["threshold"],
                            semantic_recomputed_score=r["semantic"]["recomputed_score"],
                            instance_found=r["instance"]["found"], seconds=r["seconds"])
    return calls


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--profile", type=Path, default=ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json")
    p.add_argument("--embedding-override", type=str, default="{}", help="JSON merged into profile['embedding']")
    p.add_argument("--robust-override", type=str, default="{}", help="JSON merged into profile['robust']")
    p.add_argument("--workers", type=int, default=5, help="CPU processes for blind detection")
    a = p.parse_args()
    import torch
    from PIL import Image
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder
    from m1_latent_reconstruction import quality

    out = a.output_dir
    (out / "images").mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "scripts/f4_chroma_codec.py", "scripts/f4_gate.py"],
                                    cwd=ROOT, text=True).strip()
    if dirty:
        raise SystemExit("commit f4 code before running: " + dirty)
    profile = json.loads(a.profile.read_text(encoding="utf-8"))
    profile["embedding"].update(json.loads(a.embedding_override))
    profile["robust"].update(json.loads(a.robust_override))
    profile = v5.validate_profile(profile)
    clip, transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
    metric = models.load_lpips(ASSETS, Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
    pipe = models.load_regenerator(ASSETS)
    started = time.monotonic()

    def feature(rgb):
        return models.clip_feature(clip, transform, rgb).reshape(-1).tolist()

    def save(name, rgb):
        path = out / "images" / f"{name}.png"
        Image.fromarray(rgb).save(path)
        return np.asarray(Image.open(path).convert("RGB"), np.uint8), dict(path=str(path), pixel_sha256=sha(rgb.tobytes()))

    def vae_mode(rgb):
        with torch.inference_mode():
            t = pipe.image_processor.preprocess(Image.fromarray(rgb)).to("cuda", dtype=pipe.vae.dtype)
            decoded = pipe.vae.decode(pipe.vae.encode(t).latent_dist.mode(), return_dict=False)[0]
            array = pipe.image_processor.postprocess(decoded, output_type="np")
            array, flags = pipe.run_safety_checker(array, torch.device("cuda"), pipe.text_encoder.dtype)
        if flags is None or len(flags) != 1 or bool(flags[0]):
            raise RuntimeError("safety_checker_blocked_output")
        return np.rint(np.clip(array[0], 0, 1) * 255).astype(np.uint8)

    def img2img(rgb, strength, seed):
        with torch.inference_mode():
            result = pipe(prompt="", negative_prompt="", image=Image.fromarray(rgb), strength=strength,
                          num_inference_steps=20, eta=0.0, guidance_scale=1.0,
                          generator=torch.Generator(device="cuda").manual_seed(seed),
                          num_images_per_prompt=1, output_type="pil", return_dict=True)
        return np.asarray(models.validate_generated(result), np.uint8)

    rows = []
    log = (out / "rows.jsonl").open("w", encoding="utf-8")

    def emit(row):
        rows.append(row); log.write(json.dumps(row) + "\n"); log.flush()

    # Detection is pure-Python v5 code; it runs in worker processes, one saved PNG per task.
    import multiprocessing
    pool = multiprocessing.get_context("spawn").Pool(a.workers, initializer=_init_worker, initargs=(json.dumps(profile),))
    for sid, path in SOURCES.items():
        source = np.asarray(Image.open(path).convert("RGB"), np.uint8)
        tick = time.monotonic()
        marked_rows, report = f4.embed_rgb(source.tolist(), OWNERS[0], profile, feature(source))
        marked, receipt = save(f"clean-{sid}-C1", np.asarray(marked_rows, np.uint8))
        q = quality(source, marked)
        q["lpips"] = models.lpips_score(metric, source, marked)
        emit(dict(id=f"embed-{sid}", source_id=sid, outcome="embedded", seconds=time.monotonic() - tick, image=receipt,
                  quality=q, report={k: v for k, v in report.items() if k != "verification"},
                  self_verification=report["verification"]["outcome"]))
        _, c0_receipt = save(f"clean-{sid}-C0", source)
        pending = [(dict(id=f"clean-{sid}-C0", axis="clean", source_id=sid, control="C0", outcome="completed", image=c0_receipt)),
                   (dict(id=f"clean-{sid}-C1", axis="clean", source_id=sid, control="C1", outcome="completed", image=receipt))]
        for control, rgb in {"C0": source, "C1": marked}.items():
            specs = [("vae_mode", None, None)] + [("diffusion", s, seed) for s in STRENGTHS for seed in SEEDS]
            for dose, strength, seed in specs:
                rid = f"t3-{sid}-{control}-" + ("vae" if dose == "vae_mode" else f"{strength}-{seed}")
                try:
                    attacked = vae_mode(rgb) if dose == "vae_mode" else img2img(rgb, strength, seed)
                except RuntimeError as error:
                    emit(dict(id=rid, axis="T3", source_id=sid, control=control, dose=dose, strength=strength, seed=seed,
                              outcome="safety_blocked" if "safety" in str(error) else "failed", error=str(error)))
                    continue
                _, attacked_receipt = save(rid, attacked)
                pending.append(dict(id=rid, axis="T3", source_id=sid, control=control, dose=dose, strength=strength,
                                    seed=seed, outcome="completed", image=attacked_receipt))
        for row, calls in zip(pending, pool.map(_read_job, [r["image"]["path"] for r in pending])):
            row["calls"] = calls
            emit(row)
        print(f"source {sid}: {time.monotonic() - started:.0f}s", flush=True)
    pool.close(); pool.join()
    log.close()

    # Summary and pairing with v5 dev-001.
    alpha = OWNERS[0]
    v5rows = json.loads(V5_RESULTS.read_text(encoding="utf-8"))["rows"]
    v5ok = {}
    for r in v5rows:
        if r.get("axis") == "T3" and r.get("control") == "C1" and r.get("dose") == "diffusion" and r.get("status") == "metrics_complete":
            det = next(d["result"] for d in r["detections"] if d["claimed_owner"] == alpha and d["binding_mode"] == "combined")
            v5ok[(r["source_id"], r["strength"], r["seed"])] = bool(det["semantic"]["found"] and det["semantic"]["content_match"])
    def success(call):
        return bool(call["semantic_found"] and call["semantic_content_match"])
    summary = {}
    for control in ("C1", "C0"):
        for key in ("clean", "vae_mode") + STRENGTHS:
            sel = [r for r in rows if r.get("control") == control and r.get("outcome") == "completed" and
                   ((r.get("axis") == "clean" and key == "clean") or (r.get("dose") == key) or (r.get("strength") == key))]
            missing = sum(1 for r in rows if r.get("control") == control and r.get("outcome") not in ("completed",) and
                          (r.get("dose") == key or r.get("strength") == key))
            summary[f"{control}|{key}"] = dict(
                completed=len(sel), missing=missing,
                semantic_success=sum(success(r["calls"][alpha]) for r in sel),
                both_match=sum(r["calls"][alpha]["outcome"] == "both_match" for r in sel),
                wrong_owner_found=sum(c["semantic_found"] or c["instance_found"] for r in sel for o, c in r["calls"].items() if o != alpha),
                median_semantic_recomputed=float(np.median([r["calls"][alpha]["semantic_recomputed_score"] for r in sel])) if sel else None)
    paired = {}
    f4ok = {(r["source_id"], r["strength"], r["seed"]): success(r["calls"][alpha]) for r in rows
            if r.get("axis") == "T3" and r.get("control") == "C1" and r.get("dose") == "diffusion" and r.get("outcome") == "completed"}
    for s in STRENGTHS:
        keys = [k for k in f4ok if k[1] == s and k in v5ok]
        paired[str(s)] = dict(identities=len(keys), f4=sum(f4ok[k] for k in keys), v5=sum(v5ok[k] for k in keys),
                              only_f4=sum(f4ok[k] and not v5ok[k] for k in keys), only_v5=sum(v5ok[k] and not f4ok[k] for k in keys))
    embeds = [r for r in rows if r.get("outcome") == "embedded"]
    run = dict(schema="f4-gate-v1", data_split="development", family=f4.FAMILY, revision=f4.REVISION, commit=commit,
               command=sys.argv, profile=profile, detector_config_id=v5.detector_config_id(profile),
               owners=OWNERS, strengths=STRENGTHS, seeds=SEEDS, sources=list(SOURCES),
               attack="pinned SD1.5 DDIM img2img 20 steps, empty prompt, CFG 1, eta 0; VAE posterior mode",
               duration_seconds=time.monotonic() - started, outcome="completed",
               quality=dict(psnr_min=min(r["quality"]["psnr_db"] for r in embeds), ssim_min=min(r["quality"]["ssim_rgb"] for r in embeds),
                            lpips_max=max(r["quality"]["lpips"] for r in embeds),
                            self_verified=sum(r["self_verification"] == "both_match" for r in embeds)),
               summary=summary, paired_with_v5=paired, human_visual_verdict=None)
    (out / "run.json").write_text(json.dumps(run, indent=1), encoding="utf-8")
    print(json.dumps(dict(quality=run["quality"], paired=paired), indent=1))


if __name__ == "__main__":
    main()
