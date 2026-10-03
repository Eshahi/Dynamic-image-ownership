"""Development check: does the v5 reference codec survive a latent-diffusion channel?

Development tooling, not a study run.  Hosts are procedural or generated here
from fixed prompts and seeds; no study image is read.  Outputs go under
``.thesis-build/rehearsal/`` and are labelled synthetic.  The numbers guide
engineering defaults and tell whether a study is worth preparing; they are not
evidence about photographs.

For every host the real codec (``revised_watermark_v5``, the standard-library
implementation that the tests cover) marks the image.  The saved, reopened
marked image (C1) and the unmarked host (C0) then go through

* the deterministic VAE mode round trip,
* SD 1.5 img2img with the settings of the retained revision-2 study (DDIM,
  20 steps, eta 0, guidance 1, empty prompt) at each strength and seed,
* a few ordinary operations (JPEG, blur, resizing),

and the detector is run on every output.

    .thesis-build/a6-science-venv/Scripts/python.exe scripts/dev_v5_regeneration_check.py --tag default
"""

from __future__ import annotations

import argparse
import importlib.metadata
import io
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dev_v5_channel_probe as probe  # noqa: E402
from scripts import revised_watermark_v5 as codec  # noqa: E402

OWNER = "dev-owner-0001"
OTHER = "dev-owner-0002"
SEEDS = (0, 1, 2)
CLIP_SOURCE = "external:clip-vit-b32-a6-40d365715913"
# The pinned CLIP adapter lives on the study branches; the main checkout does not carry it.
CLIP_ADAPTER_DIRS = (Path(__file__).resolve().parent, Path("C:/Users/Soroush/.codex/worktrees/v4r2-study/THESIS_GUIDE_OFFLINE_v5/scripts"))


def load_clip():
    """The pinned local CLIP ViT-B/32 image encoder of the study, on the CPU; returns ``rgb -> unit vector``."""
    import torch
    from PIL import Image

    for directory in CLIP_ADAPTER_DIRS:
        if (directory / "a6_clip_visual.py").is_file():
            sys.path.insert(0, str(directory))
            break
    else:
        raise RuntimeError("a6_clip_visual.py not found")
    from a6_clip_visual import load_visual_encoder

    model, transform = load_visual_encoder(probe.ASSETS.parent / "clip" / "ViT-B-32.pt", device="cpu")

    def feature(rgb: np.ndarray) -> list[float]:
        with torch.inference_mode():
            value = model.encode_image(transform(Image.fromarray(rgb)).unsqueeze(0)).float()
        return (value / torch.linalg.vector_norm(value)).reshape(-1).tolist()

    return feature


def load_lpips():
    import lpips
    import torch
    import torchvision

    assets = probe.ASSETS.parent
    metric = lpips.LPIPS(pretrained=False, pnet_rand=True, net="alex", version="0.1", spatial=False, use_dropout=True, eval_mode=True, verbose=False)
    trunk = torchvision.models.alexnet(weights=None)
    trunk.load_state_dict(torch.load(assets / "alexnet" / "alexnet-owt-7be5be79.pth", map_location="cpu", weights_only=True), strict=True)
    for name, start, stop in (("slice1", 0, 2), ("slice2", 2, 5), ("slice3", 5, 8), ("slice4", 8, 10), ("slice5", 10, 12)):
        setattr(metric.net, name, torch.nn.Sequential(*(trunk.features[i] for i in range(start, stop))))
    package = Path(importlib.metadata.distribution("lpips").locate_file("lpips"))
    metric.load_state_dict(torch.load(package / "weights" / "v0.1" / "alex.pth", map_location="cpu", weights_only=True), strict=False)
    return metric.requires_grad_(False).eval()


def lpips_score(metric, left: np.ndarray, right: np.ndarray) -> float:
    import torch

    def tensor(rgb):
        return torch.from_numpy(rgb.copy()).permute(2, 0, 1).unsqueeze(0).float() / 255 * 2 - 1

    with torch.inference_mode():
        return float(metric(tensor(left), tensor(right), normalize=False).item())


def hosts(which: str = "dev") -> list[tuple[str, np.ndarray]]:
    """``dev``: the tuning hosts; ``holdout``: the held-out set of ``dev_v5_holdout_hosts`` (never used for tuning)."""
    from PIL import Image

    if which == "holdout":
        return [(path.stem, np.asarray(Image.open(path).convert("RGB"))) for path in sorted((probe.OUTPUT / "holdout").glob("holdout-*.png"))]
    out = [(f"procedural-{index}", probe.procedural(100 + index)) for index in range(4)]
    for path in sorted((probe.OUTPUT / "hosts").glob("generated-*.png")):
        out.append((path.stem, np.asarray(Image.open(path).convert("RGB"))))
    return out


def ordinary(rgb: np.ndarray) -> dict[str, np.ndarray]:
    """Ordinary processing, for the benign-processing rows."""
    from PIL import Image, ImageFilter

    image = Image.fromarray(rgb)
    out = {}
    for quality in (75, 50):
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality)
        out[f"jpeg{quality}"] = np.asarray(Image.open(io.BytesIO(buffer.getvalue())).convert("RGB"))
    out["blur1.5"] = np.asarray(image.filter(ImageFilter.GaussianBlur(1.5)))
    out["down384"] = np.asarray(image.resize((384, 384), Image.LANCZOS))
    out["down384up"] = np.asarray(image.resize((384, 384), Image.LANCZOS).resize(rgb.shape[1::-1], Image.BICUBIC))
    return out


def brief(result: dict) -> dict:
    return {
        "outcome": result["outcome"],
        "state": result["proposal_state"],
        "s_found": result["semantic"]["found"],
        "s_match": result["semantic"]["content_match"],
        "s_candidate": result["semantic"]["candidate"],
        "s_recomputed": round(result["semantic"]["recomputed_score"], 3),
        "s_decoded": round(result["semantic"]["decoded_score"], 3),
        "s_distance": result["semantic"]["code_distance"],
        "s_corrected": result["semantic"]["corrected_distance"],
        "q": result["semantic_code"],
        "i_found": result["instance"]["found"],
        "i_recomputed": round(result["instance"]["recomputed_score"], 3),
        "i_decoded": round(result["instance"]["decoded_score"], 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="default")
    parser.add_argument("--profile", help="profile JSON to start from instead of the codec default")
    parser.add_argument("--hosts", default="dev", choices=("dev", "holdout"))
    parser.add_argument("--visibility", type=float)
    parser.add_argument("--cap", type=float, help="block_ratio_cap")
    parser.add_argument("--weber", type=float)
    parser.add_argument("--base", type=float)
    parser.add_argument("--min-psnr", type=float)
    parser.add_argument("--refine", action="store_true", help="refine the robust change through the frozen VAE and a one-step denoiser")
    parser.add_argument("--limit", type=int, default=0, help="use only the first N hosts")
    parser.add_argument("--clip", action="store_true", help="use the study's CLIP vector as semantic source instead of the layout proxy")
    args = parser.parse_args()
    from PIL import Image
    from skimage.metrics import structural_similarity

    profile = codec.load_profile(args.profile) if args.profile else codec.validate_profile(codec.DEFAULT_PROFILE)
    for section, name, value in (
        ("embedding", "visibility", args.visibility),
        ("embedding", "block_ratio_cap", args.cap),
        ("robust", "mask_weber", args.weber),
        ("robust", "mask_base", args.base),
        ("embedding", "min_robust_psnr_db", args.min_psnr),
    ):
        if value is not None:
            profile[section][name] = value
    if args.clip:
        profile["semantic_source"] = CLIP_SOURCE
    profile = codec.validate_profile(profile)
    probe.offline()
    feature = load_clip() if args.clip else (lambda _rgb: None)

    def read(image: np.ndarray, owner: str) -> dict:
        # The semantic vector always comes from the suspect image itself.
        return brief(codec.detect_rgb(image.tolist(), owner, profile=profile, semantic_features=feature(image)))

    _text, pipe = probe.load()
    metric = load_lpips()
    refiner = None
    if args.refine:
        from scripts import v5_channel_refine

        refiner = v5_channel_refine.Refiner(pipe)
    out_dir = probe.OUTPUT / f"check-{args.tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    started = time.time()
    selected = hosts(args.hosts)[: args.limit or None]
    for name, rgb in selected:
        row: dict[str, object] = {"host": name}
        try:
            change = None
            if refiner is not None:
                change, row["refine"] = refiner.refine(rgb, OWNER, profile, semantic_features=feature(rgb))
            marked, report = codec.embed_rgb(rgb.tolist(), OWNER, profile=profile, semantic_features=feature(rgb), strict=False, robust_change=change)
        except ValueError as error:  # includes EmbeddingError
            row["embedding_error"] = str(error)
            rows.append(row)
            print(name, "embedding error:", error, flush=True)
            continue
        marked = np.asarray(marked, dtype=np.uint8)
        path = out_dir / f"{name}-C1.png"
        Image.fromarray(marked).save(path)
        marked = np.asarray(Image.open(path).convert("RGB"))
        difference = marked.astype(np.float64) - rgb
        row["quality"] = {
            "rgb_psnr": float(10 * np.log10(255.0**2 / (difference**2).mean())),
            "luma_psnr": report["psnr_db"],
            "robust_psnr": report["robust_psnr_db"],
            "ssim": float(structural_similarity(rgb, marked, channel_axis=2, data_range=255)),
            "lpips": lpips_score(metric, rgb, marked),
            "max_abs": float(np.abs(difference).max()),
            "worst_block_rms": float(np.sqrt((difference**2).mean(axis=2).reshape(16, 32, 16, 32).mean(axis=(1, 3))).max()),
            "robust": report["robust_channel"],
        }
        row["verified"] = report["verified"]
        results: dict[str, object] = {}
        for control, image in (("C1", marked), ("C0", rgb)):
            entry: dict[str, object] = {"clean": read(image, OWNER)}
            if control == "C1":
                entry["wrong_owner"] = read(image, OTHER)
            entry["vae"] = read(probe.vae_round_trip(pipe, image), OWNER)
            for strength in probe.STRENGTHS:
                seeds = []
                for seed in SEEDS:
                    regenerated = probe.regenerate(pipe, image, strength, seed)
                    seeds.append(None if regenerated is None else read(regenerated, OWNER))
                entry[f"sd{strength}"] = seeds
            if control == "C1":
                for label, processed in ordinary(image).items():
                    entry[label] = read(processed, OWNER)
            results[control] = entry
        row["results"] = results
        rows.append(row)
        c1 = results["C1"]
        print(
            name,
            "psnr %.1f ssim %.3f lpips %.3f" % (row["quality"]["rgb_psnr"], row["quality"]["ssim"], row["quality"]["lpips"]),
            c1["clean"]["outcome"],
            "| vae", c1["vae"]["outcome"], c1["vae"]["s_recomputed"],
            "|", " ".join(f"{s}:" + ",".join("blk" if r is None else ("S" if r["s_found"] and r["s_match"] else "-") for r in c1[f"sd{s}"]) for s in probe.STRENGTHS),
            f"{time.time() - started:.0f}s",
            flush=True,
        )
    report = {
        "label": "synthetic development check; not study evidence",
        "codec": {"version": codec.VERSION, "revision": codec.REVISION, "detector_config_id": codec.detector_config_id(profile)},
        "profile": profile,
        "refined": bool(args.refine),
        "hosts": args.hosts,
        "semantic_source": profile["semantic_source"],
        "owner": OWNER,
        "seeds": list(SEEDS),
        "rows": rows,
        "seconds": time.time() - started,
    }
    (out_dir / "check.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    summarise(report)
    return 0


def summarise(report: dict) -> None:
    rows = [row for row in report["rows"] if "results" in row]
    print("hosts", len(report["rows"]), "embedded", len(rows), "verified", sum(bool(row["verified"]) for row in rows))
    if not rows:
        return
    for key in ("rgb_psnr", "ssim", "lpips"):
        values = [row["quality"][key] for row in rows]
        print(f"  {key}: median {np.median(values):.3f} min {min(values):.3f} max {max(values):.3f}")

    def kept(result):
        return result is not None and result["s_found"] and result["s_match"]

    labels = ["vae"] + [f"sd{strength}" for strength in probe.STRENGTHS]
    for label in labels:
        c1 = [row["results"]["C1"][label] for row in rows]
        c0 = [row["results"]["C0"][label] for row in rows]
        flat1 = [item for entry in c1 for item in (entry if isinstance(entry, list) else [entry])]
        flat0 = [item for entry in c0 for item in (entry if isinstance(entry, list) else [entry])]
        groups = sum(all(kept(item) for item in (entry if isinstance(entry, list) else [entry])) for entry in c1)
        outcomes: dict[str, int] = {}
        for item in flat1:
            name = "blocked" if item is None else item["outcome"]
            outcomes[name] = outcomes.get(name, 0) + 1
        print(
            f"  {label}: C1 semantic kept {sum(kept(item) for item in flat1)}/{len(flat1)}, groups with every seed kept {groups}/{len(rows)},",
            f"C0 found {sum(item is not None and (item['s_found'] or item['i_found']) for item in flat0)}/{len(flat0)}, outcomes {outcomes}",
        )
    for label in ("clean", "wrong_owner", "jpeg75", "jpeg50", "blur1.5", "down384", "down384up"):
        outcomes = {}
        for row in rows:
            name = row["results"]["C1"][label]["outcome"]
            outcomes[name] = outcomes.get(name, 0) + 1
        print(f"  {label}: {outcomes}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--summarise":
        summarise(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")))
        sys.exit(0)
    sys.exit(main())
