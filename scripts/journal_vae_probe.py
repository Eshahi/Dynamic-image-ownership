"""Fixed twelve-source, posterior-mode VAE generalization diagnostic (development only)."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5
from f5_gate import OWNERS, semantic_feature, V5_RESULTS
from f4_transfer_probe import MAIN, ASSETS, SOURCES
from m1_latent_reconstruction import quality

F5_RUN = MAIN / ".thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7"
SDXL = MAIN / ".thesis-build/assets/journal-sdxl-vae-6f5909a7"
SDXL_REV = "6f5909a7e596173e25d4e97b07fd19cdf9611c76"


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def compact(r):
    """Preserve read versus assumed match and exact decoded payload for diagnostics."""
    keys = ("found", "read", "content_match", "content_status", "decoded_code", "score",
            "threshold", "recomputed_score", "recomputed_threshold", "decoded_score", "decoded_threshold",
            "code_distance", "corrected_distance", "decoding_error_rate", "soft_distance")
    return {"outcome": r["outcome"], "watermark_found": r["watermark_found"],
            **{tier: {k: r[tier].get(k) for k in keys} for tier in ("semantic", "instance")}}


def checked(r):
    return bool(r["semantic"]["found"] and r["semantic"]["read"] and r["semantic"]["content_match"])


class Evaluator:
    def __init__(self):
        import torch
        import three_threat_models as models
        from a6_clip_visual import load_visual_encoder
        torch.set_num_threads(4)
        self.torch, self.models = torch, models
        self.reader = f5.Reader(ASSETS, device="cuda")
        self.clip, self.transform = load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
        self.lpips = models.load_lpips(ASSETS, Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
        self.profile = json.loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text())

    def features(self, rgb, views):
        return semantic_feature(self.models, self.clip, self.transform, rgb, views)

    def detect(self, rgb, method, owner, features=None, latent=None, mode="combined"):
        if features is None:
            features = self.features(rgb, 7 if method == "f5" else 1)
        if method == "f5":
            if latent is None:
                latent = self.reader.latent(rgb)
            return f5.detect_rgb(rgb, latent, owner, self.profile, features,
                                 binding_mode=mode, binding="soft", roster_size=1)
        return v5.detect_rgb(rgb, owner, profile=self.profile, semantic_features=features,
                             binding_mode=mode, roster_size=1)

    def metrics(self, source, rgb):
        return {**quality(source, rgb), "lpips": self.models.lpips_score(self.lpips, source, rgb)}


def summarize(rows):
    summary = {}
    for method in ("f5", "v5"):
        for condition in ("clean", "sd15_vae", "sdxl_vae"):
            group = [r for r in rows if r["method"] == method and r["condition"] == condition]
            c1 = [r for r in group if r["control"] == "C1"]
            c0 = [r for r in group if r["control"] == "C0"]
            good = [r for r in c1 if r["status"] == "ok"]
            calls = [r["calls"][OWNERS[0]] for r in good]
            summary[f"{method}/{condition}"] = {
                "planned_sources": 12, "completed_c1": len(good),
                "failed_rows": sum(r["status"] != "ok" for r in group),
                "semantic_checked": sum(checked(c) for c in calls),
                "semantic_found": sum(bool(c["semantic"]["found"]) for c in calls),
                "semantic_assumed": sum(bool(c["semantic"]["found"] and c["semantic"]["content_match"] and not c["semantic"]["read"]) for c in calls),
                "both_match": sum(c["outcome"] == "both_match" for c in calls),
                "c0_any": sum(bool(r["calls"][OWNERS[0]]["watermark_found"]) for r in c0 if r["status"] == "ok"),
                "c0_completed": sum(r["status"] == "ok" for r in c0),
                "wrong_owner_any": sum(bool(r["calls"][OWNERS[1]]["watermark_found"]) for r in good),
                "lpips_input_mean": float(np.mean([r["quality_input"]["lpips"] for r in good])) if good else None,
                "lpips_input_max": max((r["quality_input"]["lpips"] for r in good), default=None),
                "proxy": {str(limit): {
                    "qualified_c1": sum(r["quality_input"]["lpips"] <= limit for r in good),
                    "checked_c1": sum(checked(r["calls"][OWNERS[0]]) for r in good if r["quality_input"]["lpips"] <= limit)
                } for limit in (.2, .3)},
            }
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    from PIL import Image
    from diffusers import AutoencoderKL
    started = time.monotonic()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "images").mkdir()
    record = {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "command": sys.argv, "data_split": "development", "sources": sorted(SOURCES),
              "seeds": [], "config": {"precision": "float32", "posterior": "mode", "size": [512, 512],
              "conditions": ["clean", "sd15_vae", "sdxl_vae"], "owners": list(OWNERS[:2]),
              "sdxl_revision": SDXL_REV, "sdxl_license": "MIT", "roster_size": 1,
              "f5_saved_marks": str(F5_RUN), "v5_saved_marks": str(V5_RESULTS.parent / "images"),
              "human_admissibility": "missing", "safety_checker": "not used for VAE-only reconstruction",
              "primary_proxy_lpips": .3, "sensitivity_proxy_lpips": .2},
              "outcome": "running", "duration_seconds": None}
    write(args.output_dir / "run.json", record)
    rows = []
    try:
        ev = Evaluator()
        record["environment"] = {name: importlib.metadata.version(name) for name in ("torch", "diffusers", "numpy", "lpips")}
        record["environment"]["gpu"] = ev.torch.cuda.get_device_name(0)
        other = AutoencoderKL.from_pretrained(SDXL, use_safetensors=True, local_files_only=True,
                                              torch_dtype=ev.torch.float32).eval().requires_grad_(False).to("cuda")
        for sid in sorted(SOURCES):
            source = np.asarray(Image.open(SOURCES[sid]).convert("RGB"), np.uint8)
            for method in ("f5", "v5"):
                for control in ("C0", "C1"):
                    input_path = ((F5_RUN / "images") if method == "f5" else V5_RESULTS.parent / "images") / f"clean-{sid}-{control}.png"
                    rgb = np.asarray(Image.open(input_path).convert("RGB"), np.uint8)
                    if control == "C0" and not np.array_equal(source, rgb):
                        raise ValueError("Saved C0 is not the canonical source")
                    for condition in ("clean", "sd15_vae", "sdxl_vae"):
                        row = {"source_id": sid, "method": method, "control": control, "condition": condition,
                               "input_path": str(input_path), "status": "running"}
                        try:
                            if condition == "clean":
                                attacked = rgb.copy()
                            else:
                                vae = ev.reader.vae if condition == "sd15_vae" else other
                                with ev.torch.inference_mode():
                                    x = ev.reader.tensor(rgb.astype(np.float32) / 255)
                                    z = vae.encode(x * 2 - 1).latent_dist.mode()
                                    y = vae.decode(z).sample[0].permute(1, 2, 0).cpu().numpy()
                                attacked = np.rint(np.clip(y * .5 + .5, 0, 1) * 255).astype(np.uint8)
                            path = args.output_dir / "images" / f"{sid}-{method}-{control}-{condition}.png"
                            Image.fromarray(attacked).save(path)
                            saved = np.asarray(Image.open(path).convert("RGB"), np.uint8)
                            features = ev.features(saved, 7 if method == "f5" else 1)
                            latent = ev.reader.latent(saved) if method == "f5" else None
                            owners = OWNERS[:2] if control == "C1" else OWNERS[:1]
                            row.update(image=str(path), quality_input=ev.metrics(rgb, saved),
                                       quality_source=ev.metrics(source, saved),
                                       calls={o: compact(ev.detect(saved, method, o, features, latent)) for o in owners}, status="ok")
                        except Exception:
                            row.update(status="failed", error=traceback.format_exc())
                        rows.append(row)
                        with (args.output_dir / "rows.jsonl").open("a", encoding="utf-8") as handle:
                            handle.write(json.dumps(row, allow_nan=False) + "\n")
                        print(json.dumps({k: row[k] for k in ("source_id", "method", "control", "condition", "status")}), flush=True)
                        if row["status"] == "failed":
                            print(row["error"], flush=True)
            write(args.output_dir / "summary.json", summarize(rows))
        record["outcome"] = "completed" if all(r["status"] == "ok" for r in rows) else "completed_with_failures"
        record["rows"] = len(rows)
        record["summary"] = summarize(rows)
    except Exception:
        record.update(outcome="failed", error=traceback.format_exc())
        raise
    finally:
        record["duration_seconds"] = time.monotonic() - started
        write(args.output_dir / "run.json", record)


if __name__ == "__main__":
    main()
