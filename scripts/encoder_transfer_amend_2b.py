"""Build the amendment-2b (stage 2b) contract from the stage-2a contract. No stage-2b outcome exists.

Written by Claude (Opus 5.5) on 2026-10-24 at the user's request ("Prepare the stage-2b extension
amendment (strength curve, rinse, full Kandinsky 3, smoothing) with its exact cost and the new server
plan, without running it."). Stage 2a gave FAILS, ROUTE C, and that label is final; stage 2b is
descriptive. Every stage-2b cell uses settings fixed before any stage-2 output existed:
- the reviewed freeze e318757: R0/R1 strengths .1 and .4, the R1 rinse;
- the approved proposals P4 (full Kandinsky 3) and P5 (encoder-aware smoothing) in
  budget-and-proposals.md at e318757.
The implementation details this file fixes (Kandinsky 3 steps and scheduler, the P5 noise seed) are
chosen to match the frozen R0/R1 path, never from any output.

It derives two files:
- research/encoder-transfer-20261019/stage2b-asset-plan.json: the stage-2a asset plan plus the pinned
  Kandinsky 3 pipeline files (sizes and LFS SHA-256 published by Hugging Face at revision bf79e6c;
  the small files' SHA-256 measured from the download) and a raised download allowance;
- research/encoder-transfer-20261019/stage2b-config.json: the stage-2a contract with amendment 2b.

Usage (on the server, after downloading the Kandinsky 3 files; needs numpy for the P5 arrays):
  python scripts/encoder_transfer_amend_2b.py --downloads /workspace/assets \
      --package sentencepiece=X --package protobuf=Y --spent-hours H --spent-usd U --approval "<user's words>"
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_test as et  # noqa: E402

STUDY = et.ROOT / "research" / "encoder-transfer-20261019"
CORE = ["f5-r2", "v5-r3", "wam", "vine-r"]
STAGE2A_SHA256 = "87e4142f2a070ac5405dff4a9b0c95591bc6de230c7a4ce9336f426b4e23fa68"
K3_REVISION = "bf79e6c219da8a94abb50235fdc4567eb8fb4632"
K3_URL = f"https://huggingface.co/kandinsky-community/kandinsky-3/resolve/{K3_REVISION}/"
# Sizes and LFS SHA-256 from the Hugging Face API at that revision (stage-1 cache
# T2-kandinsky-community--kandinsky-3-api.txt). MoVQ is already in the stage-2a plan.
K3_FILES = {
    "model_index.json": (417, None),
    "scheduler/scheduler_config.json": (509, None),
    "text_encoder/config.json": (793, None),
    "text_encoder/model.safetensors.index.fp16.json": (27893, None),
    "text_encoder/model.fp16-00001-of-00005.safetensors": (4994491352, "2745f08c74c13536c67282afc1e5ba80daf67e5ded7925845f3cb5e1983a2826"),
    "text_encoder/model.fp16-00002-of-00005.safetensors": (4932632832, "a1c184e0f3a2e8c80360379ada2d9fce40bee23647a63e3baefa00d837084408"),
    "text_encoder/model.fp16-00003-of-00005.safetensors": (4831960880, "3a6e4c548e5c2e6aa080a5eefad31e973dbba55b6918f95fb77af97fce341c94"),
    "text_encoder/model.fp16-00004-of-00005.safetensors": (4999741472, "3e7652beb11f33c5549d391c2affacd6642d9ca21bc0d4319cba60fe1b357ff0"),
    "text_encoder/model.fp16-00005-of-00005.safetensors": (1979772184, "f41b9aea886f3d583c026011cb7251ff21f615774ad604264aaaa01605e02326"),
    "tokenizer/added_tokens.json": (3255, None),
    "tokenizer/special_tokens_map.json": (2543, None),
    "tokenizer/spiece.model": (791656, "d60acb128cf7b7f2536e8f38a5b18a05535c9e14c7a355904270e15b0945ea86"),
    "tokenizer/tokenizer_config.json": (25436, None),
    "unet/config.json": (322, None),
    "unet/diffusion_pytorch_model.fp16.safetensors": (6110842296, "805179fe9c10cd1e01c59057f0c2bb07ce57834ad343f721e50ca16bef6952f6"),
}
# 40 GB frozen asset reserve plus the approved P4 assets (28.4 GB) rounded up; absolute budget 100 GB.
DOWNLOAD_ALLOWANCE = 60_000_000_000
P5_NOISE_SEED = 20261019 + 5  # the study's message seed plus the proposal number; public
STAGE2A_DECISION = dict(label="FAILS", route="ROUTE C", f5=0, best_external=60,
                        source="results.md at commit 8432c7c (metrics.json of the stage-2a run)")
USER_DECISIONS = [
    "2026-10-21, verbatim: Approve P1 TrustMark, P9 PixelSeal, P4 Kandinsky 3 and P5 smoothing; decline the rest; ceiling 35 instance-hours or USD 30.",
    "2026-10-21: approved the lean two-stage plan (BRIEF section 1d); stage 2b then ran only if TRANSFERS.",
    "2026-10-24, verbatim, after the stage-2a label FAILS, ROUTE C: Prepare the stage-2b extension amendment (strength curve, rinse, full Kandinsky 3, smoothing) with its exact cost and the new server plan, without running it.",
]


def build_assets(downloads):
    plan = copy.deepcopy(et.read(STUDY / "stage2a-asset-plan.json"))
    receipts = []
    for name, (size, lfs_sha) in K3_FILES.items():
        path = f"kandinsky3/{name}"
        local = Path(downloads) / path
        entry = dict(path=path, url=K3_URL + name, sha256=et.digest(local), size_bytes=local.stat().st_size, license="Apache-2.0")
        if entry["size_bytes"] != size:
            raise ValueError(f"Kandinsky 3 file size differs from the pinned revision: {name}")
        if lfs_sha and entry["sha256"] != lfs_sha:
            raise ValueError(f"Kandinsky 3 file differs from its published LFS SHA-256: {name}")
        receipts.append(entry)
    plan["files"] = plan["files"] + receipts
    plan["total_file_bytes"] = sum(f["size_bytes"] for f in plan["files"])
    plan["download_allowance_bytes"] = DOWNLOAD_ALLOWANCE
    plan["schema"] = plan["schema"] + "+amendment-2b"
    plan["amendment_2b"] = dict(
        added_files=[r["path"] for r in receipts], kandinsky3_revision=K3_REVISION,
        note="Large files match the LFS SHA-256 published at the revision; small files are pinned by the SHA-256 measured from the revision-pinned download.")
    return plan


def p5_spec():
    import hashlib
    import numpy as np
    spec = dict(sigma=2 / 255, pairs=4, shape=[3, 1024, 1024], noise_seed=P5_NOISE_SEED, dtype="float32",
                generator="numpy default_rng (PCG64) standard_normal, float32, times sigma",
                encoder="SDXL VAE posterior mode, full fp32, on the 1024 Lanczos input",
                smoothing="mean of the modes of clip(x + g_k, 0, 1) and clip(x - g_k, 0, 1), k = 1..4, x in [0, 1]",
                control="R1-mode: the mode of the unperturbed x",
                diffusion="R1's frozen img2img path at .2 (DDIM 20 scheduled, 4 executed, empty prompt, CFG 1, seeds 12, 13, 14) from the given latent; the pipeline adds the seed's noise",
                cache="one latent per marked input (300 inputs), reused by its three seeds")
    rng = np.random.default_rng(P5_NOISE_SEED)
    arrays = rng.standard_normal((spec["pairs"], *spec["shape"]), dtype=np.float32) * np.float32(spec["sigma"])
    spec["noise_sha256"] = hashlib.sha256(arrays.tobytes()).hexdigest()
    return spec


def inherited_cells(stage2a, sources):
    return sorted({(u["channel"], u["strength"], u["arm"]) for u in et.plan(stage2a, sources)}, key=str)


def build_config(asset_plan_sha, extra_packages, spent_hours, spent_usd, approval, p5=None):
    path = STUDY / "stage2a-config.json"
    if et.digest(path) != STAGE2A_SHA256:
        raise ValueError("Stage-2a contract differs from the one that ran")
    stage2a, sources = et.load_contract(path)
    config = copy.deepcopy(stage2a)
    base = config["amendment"]
    config["asset_plan_file"] = "research/encoder-transfer-20261019/stage2b-asset-plan.json"
    config["asset_plan_sha256"] = asset_plan_sha
    channels = {c["id"]: c for c in config["channels"]}
    channels["R0"]["strengths"] = [0.1, 0.2, 0.4]
    channels["R1"]["strengths"] = [0.1, 0.2, 0.4]
    # TrustMark and Pixel Seal stay in their approved R1 .2 cell (P1, P9).
    channels["R1"]["arms_by_strength"] = {"0.1": list(CORE), "0.4": list(CORE)}
    rinse = channels["R1-rinse"]
    rinse.pop("enabled", None)
    rinse.pop("reason", None)
    rinse["arms"] = list(CORE)
    sdxl = {k: channels["R1"][k] for k in ("resolution", "steps", "prompt", "guidance_scale", "scheduler_overrides")}
    smooth = dict(id="R1-smooth", kind="smoothing", family="sdxl", base_channel="R1", strengths=[0.2], seeds=[12, 13, 14],
                  arms=list(CORE), semantics="P5 encoder-aware smoothing: the mean SDXL posterior mode over 4 antithetic Gaussian pairs, then R1's .2 path", **sdxl)
    mode = dict(id="R1-mode", kind="mode", family="sdxl", base_channel="R1", strengths=[0.2], seeds=[12, 13, 14],
                arms=list(CORE), semantics="P5 matched control: the SDXL posterior mode of the unperturbed input, then the same .2 path", **sdxl)
    k3 = dict(id="R3", kind="diffusion", family="kandinsky3", resolution=1024, steps=20, prompt="", guidance_scale=1.0,
              strengths=[0.2], seeds=[12, 13, 14], arms=list(CORE),
              semantics="P4 full Kandinsky 3 img2img at revision bf79e6c: native DDPMScheduler as shipped (no override), 20 scheduled steps at strength .2 (4 executed), empty prompt without guidance (guidance 1), fp16 variant; the empty-prompt embedding is computed once with the pipeline's own encode_prompt(_cut_context=True); output quantized as diffusers numpy_to_pil")
    order = [c["id"] for c in config["channels"]]
    rebuilt = []
    for cid in order:
        rebuilt.append(channels[cid])
        if cid == "R1-rinse":
            rebuilt += [smooth, mode]  # SDXL stays loaded from the rinse to P5
        if cid == "D3":
            rebuilt.append(k3)
    config["channels"] = rebuilt
    config["inherited_cells"] = [list(cell) for cell in inherited_cells(stage2a, sources)]
    config["p5"] = p5 or p5_spec()
    config["kandinsky3"] = dict(revision=K3_REVISION, pipeline="diffusers Kandinsky3Img2ImgPipeline (diffusers 0.35.1)",
                                scheduler="DDPMScheduler as shipped: squaredcos_cap_v2, clip_sample, epsilon, leading spacing, steps_offset 1",
                                matched_to="R0/R1: 20 scheduled steps, strength .2, seeds 12/13/14, empty prompt, no guidance, 1024 Lanczos in and out")
    # The pinned T5 tokenizer of Kandinsky 3 needs sentencepiece (and protobuf on some transformers paths).
    config["packages"] = {**config["packages"], **extra_packages}
    config["primary"] = {**config["primary"], "negative_scope": "all active R1 outputs (stage 2b: .1, .2, .4), no majority; the stage-2a label stays final"}
    hours, usd = round(35 - spent_hours, 2), round(30 - spent_usd, 2)
    if hours <= 0 or usd <= 0:
        raise ValueError("No stage-2b budget remains under the 35 h / USD 30 ceiling")
    config["budget"] = dict(max_instance_hours=hours, max_usd=usd, retrieval_stop_reserve_seconds=1800,
                            reduction_steps=["channel:R1-smooth,R1-mode", "channel:R3", "strength_0.1"],
                            protected=["every inherited stage-2a cell; R0/R1 .4 and the stage-2a .2 cells"],
                            scope="The remainder of the 35 h / USD 30 total for stages 2a and 2b (user, 2026-10-21)",
                            stage2a_spent=dict(instance_hours=spent_hours, usd=spent_usd),
                            drop_order_source="BRIEF section 1d: P5, then P4, then strength .1 (with its rinse)")
    config["amendment"] = dict(
        id="2b-stage2b", stage="2b", pre_outcome=True, date_utc="2026-10-24",
        outcomes_seen="Stage 2a only (FAILS, ROUTE C). No stage-2b cell has any output; its settings were fixed at e318757 or in the approved proposals before stage 2 ran.",
        author="Claude Code (Opus 5.5), at the user's request; the user decided, Claude implemented",
        base_config_file=base["base_config_file"], base_config_sha256=base["base_config_sha256"], base_commit=base["base_commit"],
        previous_amendment=dict(file="research/encoder-transfer-20261019/stage2a-config.json", sha256=STAGE2A_SHA256, id=base["id"]),
        user_decisions=USER_DECISIONS + ([f"Execution approval, verbatim: {approval}"] if approval else []),
        stage2a_decision=STAGE2A_DECISION,
        decision_rule="The stage-2a label is final. Stage 2b is descriptive; its analysis must reproduce the stage-2a label from the inherited rows.",
        not_run_by_design=["R2/D2 FLUX (gated)", "TrustMark and Pixel Seal outside their proposal cells",
                           "declined proposals P2, P3, P6, P7, P8 and P10"],
        inherited="Every stage-2a row is copied into the stage-2b journal before the run; inherited cells are verified, never rerun.")
    config["status"] = "user-amended-pre-outcome"
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--downloads", type=Path, required=True)
    parser.add_argument("--package", action="append", default=[], metavar="NAME=VERSION")
    parser.add_argument("--spent-hours", type=float, required=True, help="stage-2a instance-hours from the vast.ai bill")
    parser.add_argument("--spent-usd", type=float, required=True, help="stage-2a dollars from the vast.ai bill")
    parser.add_argument("--approval", required=True, help="the user's go-ahead for stage 2b, verbatim")
    args = parser.parse_args()
    extra = dict(item.split("=", 1) for item in args.package)
    if set(extra) != {"sentencepiece", "protobuf"}:
        raise SystemExit("Pass exactly --package sentencepiece=X --package protobuf=Y")
    asset_plan = build_assets(args.downloads)
    et.write(STUDY / "stage2b-asset-plan.json", asset_plan)
    config = build_config(et.digest(STUDY / "stage2b-asset-plan.json"), extra, args.spent_hours, args.spent_usd, args.approval)
    et.write(STUDY / "stage2b-config.json", config)
    print(json.dumps(dict(asset_plan_sha256=config["asset_plan_sha256"], config_sha256=et.digest(STUDY / "stage2b-config.json"),
                          budget=config["budget"], new_units=sum(1 for u in et.plan(config, et.read(et.ROOT / config["sources_file"]))
                                                                 if [u["channel"], u["strength"], u["arm"]] not in config["inherited_cells"])), indent=2))


if __name__ == "__main__":
    main()
