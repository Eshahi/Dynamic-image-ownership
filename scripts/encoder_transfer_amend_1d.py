"""Build the amendment-1d (stage 2a) contract from the reviewed freeze. Stdlib only; no outcomes.

Written by Claude (Opus 5.5) on 2026-10-23 at the user's request. It derives two files:

- research/encoder-transfer-20261019/stage2a-asset-plan.json: the frozen asset plan plus the
  pinned TrustMark Q, Pixel Seal and Kandinsky 3 MoVQ files (SHA-256 and sizes measured from
  local downloads) and the two pinned code repositories;
- research/encoder-transfer-20261019/stage2a-config.json: the frozen contract with the user's
  amendment 1d (BRIEF sections 1c and 1d) applied.

Usage (on the server, after downloading the new files to their asset paths):
  python scripts/encoder_transfer_amend_1d.py --downloads /workspace/assets --package lightning=X --package torchmetrics=Y
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "research" / "encoder-transfer-20261019"
CORE = ["f5-r2", "v5-r3", "wam", "vine-r"]

NEW_FILES = [
    # (published path under the assets root, URL, license)
    ("trustmark/models/trustmark_Q.yaml",
     "https://cai-watermark.adobe.net/watermarking/trustmark-models/trustmark_Q.yaml", "MIT"),
    ("trustmark/models/encoder_Q.ckpt",
     "https://cai-watermark.adobe.net/watermarking/trustmark-models/encoder_Q.ckpt", "MIT"),
    ("trustmark/models/decoder_Q.ckpt",
     "https://cai-watermark.adobe.net/watermarking/trustmark-models/decoder_Q.ckpt", "MIT"),
    ("videoseal/pixelseal-checkpoint.pth",
     "https://dl.fbaipublicfiles.com/videoseal/pixelseal/checkpoint.pth", "MIT"),
    ("kandinsky3/movq/config.json",
     "https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/movq/config.json",
     "Apache-2.0"),
    ("kandinsky3/movq/diffusion_pytorch_model.fp16.safetensors",
     "https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/movq/diffusion_pytorch_model.fp16.safetensors",
     "Apache-2.0"),
]
# MD5 values hard-coded in the pinned TrustMark loader (trustmark.py MODEL_CHECKSUMS).
TRUSTMARK_MD5 = {"trustmark_Q.yaml": "fe40df84a7feeebfceb7a7678d7e6ec6",
                 "encoder_Q.ckpt": "700328b8754db934b2f6cb5e5185d81f",
                 "decoder_Q.ckpt": "4ced90e9cfe13e3295ad082887fe9187"}
MOVQ_SHA256 = "8a4705625c160c49025e1f9b98776aaf5287240ca0d5ed39a1a235598fc39244"  # stage-1b pin record


def digest(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def build_assets(downloads):
    plan = json.loads((STUDY / "asset-download-plan.json").read_text(encoding="utf-8"))
    plan = copy.deepcopy(plan)
    receipts = []
    for path, url, license_name in NEW_FILES:
        local = downloads / path  # same layout as the assets root, so the server assets dir can be passed
        entry = dict(path=path, url=url, sha256=digest(local), size_bytes=local.stat().st_size, license=license_name)
        name = Path(path).name
        if name in TRUSTMARK_MD5 and digest(local, "md5") != TRUSTMARK_MD5[name]:
            raise ValueError(f"TrustMark file does not match the pinned loader MD5: {name}")
        if name == "diffusion_pytorch_model.fp16.safetensors" and entry["sha256"] != MOVQ_SHA256:
            raise ValueError("MoVQ weights differ from the stage-1b pin")
        receipts.append(entry)
    plan["files"] = plan["files"] + receipts
    plan["total_file_bytes"] = sum(f["size_bytes"] for f in plan["files"])
    plan["schema"] = "encoder-transfer-assets-v1+amendment-1d"
    plan["amendment_1d"] = dict(
        added_files=[r["path"] for r in receipts],
        trustmark_repository="https://github.com/adobe/trustmark.git",
        trustmark_revision="6df5a0a29b51cbec832695fdf02051a1937e37bd",
        trustmark_loader_md5=TRUSTMARK_MD5,
        videoseal_repository="https://github.com/facebookresearch/videoseal.git",
        videoseal_revision="870ca7fb33578b90f14c602016b6c2788096226e",
        kandinsky3_revision="bf79e6c219da8a94abb50235fdc4567eb8fb4632",
        note="Hashes measured by Claude from local downloads on 2026-10-23; the Pixel Seal URL is mutable, so its SHA-256 is the pin.")
    return plan


def build_config(asset_plan_sha, extra_packages):
    base_path = STUDY / "frozen-config.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    if base["status"] != "frozen-after-independent-review":
        raise ValueError("Base must be the independently reviewed freeze")
    config = copy.deepcopy(base)
    config["status"] = "user-amended-pre-outcome"
    config["asset_plan_file"] = "research/encoder-transfer-20261019/stage2a-asset-plan.json"
    config["asset_plan_sha256"] = asset_plan_sha
    config["arms"] = [*CORE, "trustmark-q", "pixelseal"]
    config["payload_bits"] = {**base["payload_bits"], "trustmark-q": 61, "pixelseal": 256}
    config["decision_external_arms"] = ["wam", "vine-r"]
    config["holm_arms"] = ["v5-r3", "wam", "vine-r"]
    config["protected_arms"] = CORE
    config["protected_channels"] = ["R0", "R1"]
    channels = {c["id"]: c for c in config["channels"]}
    channels["R0"].update(strengths=[0.2], arms=list(CORE))
    channels["R1"].update(strengths=[0.2], arms=[*CORE, "trustmark-q", "pixelseal"])
    channels["D1"]["arms"] = [*CORE, "trustmark-q"]
    channels["X1"]["arms"] = list(CORE)
    channels["X2"]["arms"] = list(CORE)
    channels["R1-rinse"].update(enabled=False, reason="Stage 2b only (BRIEF 1d): runs only if stage 2a gives TRANSFERS")
    d3 = dict(id="D3", kind="vae", family="kandinsky3-movq", resolution=1024, arms=list(CORE),
              semantics="Kandinsky3Img2ImgPipeline round trip: movq.encode(x).latents, then movq.decode(z, force_not_quantize=True); fp32 compute from the fp16 weights; no diffusion")
    order = [c["id"] for c in config["channels"]]
    config["channels"] = [channels[i] for i in order if i not in ("R2", "D2")] + [d3, channels["R2"], channels["D2"]]
    config["trustmark"] = dict(model_type="Q", use_ECC=True, encoding="BCH_5", payload_bits=61, wm_strength=1.0, wm_merge="bilinear",
                               decode="native unrotated path without the bbox detector", common_presence="native BCH detected AND binomial agreement on the 61 decoded payload bits",
                               scope="clean, D1, R1 0.2 (proposal P1)")
    config["pixelseal"] = dict(card="videoseal/cards/pixelseal.yaml", nbits=256, img_size_proc=256, mode="image (is_video=False)",
                               common_presence="binomial agreement on the 256 decoded bits", scope="clean, R1 0.2 (proposal P9)")
    # TrustMark imports lightning and torchmetrics, and the Pixel Seal import chain (videoseal.augmentation.video)
    # imports PyAV (av); their versions are the ones installed on the server.
    config["packages"] = {**base["packages"], **extra_packages}
    config["primary"] = {**base["primary"], "negative_scope": "all active R1 outputs (stage 2a: strength 0.2), no majority"}
    config["budget"] = dict(max_instance_hours=35, max_usd=30, retrieval_stop_reserve_seconds=1800,
                            reduction_steps=["channel:D3", "arm:trustmark-q", "arm:pixelseal"],
                            protected=["F5, v5, WAM, VINE-R and C0 at R0 0.2 and R1 0.2"],
                            scope="Total for stages 2a and 2b together (user, 2026-10-21)")
    config["amendment"] = dict(
        id="1d-stage2a", stage="2a", pre_outcome=True, date_utc="2026-10-23",
        author="Claude Code (Opus 5.5), at the user's request; the user decided, Claude implemented",
        base_config_file="research/encoder-transfer-20261019/frozen-config.json",
        base_config_sha256=digest(base_path), base_commit="e318757",
        user_decisions=[
            "2026-10-21, verbatim: Approve P1 TrustMark, P9 PixelSeal, P4 Kandinsky 3 and P5 smoothing; decline the rest; ceiling 35 instance-hours or USD 30.",
            "2026-10-21: approved the lean two-stage plan (BRIEF section 1d).",
            "2026-10-23: Claude is responsible for running stage 2, and the server work must continue if the SSH connection drops."],
        decision_rule="Section 3 unchanged; applied on stage 2a; B = max(WAM, VINE-R) at R1 0.2; TrustMark and Pixel Seal are descriptive.",
        not_run_by_design=["R0 and R1 strengths 0.1 and 0.4", "R1-rinse", "full P4 Kandinsky 3 regeneration", "P5 encoder-aware smoothing",
                           "TrustMark and Pixel Seal outside their proposal cells"],
        stage_2b_rule="Run only if the stage-2a label is TRANSFERS (ROUTE A or B), with the settings frozen at e318757 and the remaining budget.")
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--downloads", type=Path, required=True)
    parser.add_argument("--package", action="append", default=[], metavar="NAME=VERSION",
                        help="Extra pinned package (lightning, torchmetrics, av), as installed on the server")
    args = parser.parse_args()
    extra = dict(item.split("=", 1) for item in args.package)
    if set(extra) != {"lightning", "torchmetrics", "av"}:
        raise SystemExit("Pass exactly --package lightning=X --package torchmetrics=Y --package av=Z")
    asset_plan = build_assets(args.downloads)
    write(STUDY / "stage2a-asset-plan.json", asset_plan)
    config = build_config(digest(STUDY / "stage2a-asset-plan.json"), extra)
    write(STUDY / "stage2a-config.json", config)
    print(json.dumps(dict(asset_plan_sha256=config["asset_plan_sha256"], config_sha256=digest(STUDY / "stage2a-config.json"),
                          added=[f["path"] for f in asset_plan["files"][-len(NEW_FILES):]]), indent=2))


if __name__ == "__main__":
    main()
