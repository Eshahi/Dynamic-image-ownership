# VINE-R: native implementation contract

Inspected 2026-10-19. Extend, rather than replace, dossier card `research/q1-dossier-20261018/02-literature/C1-posthoc/cards/Lu2025VINE.md`. V2 paper: [arXiv v2](https://arxiv.org/html/2410.18775v2), §§3.1–3.3, 4.1–4.3, Tables 1, 7, Appendix H. Current inspection reread mechanism, experimental settings, Table 1 and compute table. Source text is retained outside git in MAIN `.thesis-build/q1-research-20261018/cache/T3/`; manifest records hashes. No model was loaded or downloaded.

## Exact pins and dependency trap

- Official code: [Shilin-LU/VINE](https://github.com/Shilin-LU/VINE/tree/d72f11a93f8de9bc45ef61202b9c8dda2a70cc77), commit `d72f11a93f8de9bc45ef61202b9c8dda2a70cc77`.
- Encoder: `Shilin-LU/VINE-R-Enc`, revision `0c255688e032e4318c700c485c0625367b70908c`; [checkpoint URL](https://huggingface.co/Shilin-LU/VINE-R-Enc/resolve/0c255688e032e4318c700c485c0625367b70908c/model.safetensors), 4,019,166,704 bytes; remote LFS SHA-256 `16bf5f2acf5f7d5f00570431f5dc9dd61a8e95f828a2f68483ffe06448293dd6`.
- Decoder: `Shilin-LU/VINE-R-Dec`, revision `0f094b300be71a358f7c1769221f50318f1b4d74`; [checkpoint URL](https://huggingface.co/Shilin-LU/VINE-R-Dec/resolve/0f094b300be71a358f7c1769221f50318f1b4d74/model.safetensors), 354,802,864 bytes; remote LFS SHA-256 `9aded1fc22efe47bdafc8f436f81953cd06bde1d6c7242f86bf101c020d7eea0`.
- **Released constructor uses `stabilityai/sd-turbo`, despite paper/README/model-card prose saying SDXL-Turbo.** `vine/src/vine_turbo.py:138–155` initializes its tokenizer, CLIP text encoder, UNet and VAE; `vine/src/model.py:7–11` initializes its one-step DDPM scheduler. This is a material implementation/paper discrepancy, not authority to substitute SDXL weights.
- Dependency pin: `stabilityai/sd-turbo@b261bac6fd2cf515557d5d0707481eafa0485ec2`. Plain fp32 diffusers weights total 5,159,966,076 bytes: text encoder 1,361,596,304; UNet 3,463,726,504; VAE 334,643,268. With both VINE weights, total is 9,533,935,644 bytes plus small configs/tokenizer. Do not download monolithic `sd_turbo.safetensors` or fp16 duplicates. Exact dependency file paths, sizes, remote LFS hashes and immutable resolve URLs appear in manifest.json.

Research use is allowed by repository NTUITIVE noncommercial license; HF cards independently say MIT. Dependency currently carries Stability AI Community License (July 5, 2024), explicitly allowing research/noncommercial use. Treat these as distinct notices, not MIT licensing of the whole stack. Repository redistribution clauses conflict internally; do not vendor or redistribute upstream code/weights in the thesis repository. Local adapters can document the modified local loading paths. No broader legal conclusion is inferred.

## Adapter contract

Use `VINE_Turbo` from `vine.src.vine_turbo` and `CustomConvNeXt` from `vine.src.stega_encoder_decoder`. Official scripts use bare module imports because their script directory is on sys.path. Native load calls are `VINE_Turbo.from_pretrained(encoder_path)` and `CustomConvNeXt.from_pretrained(decoder_path)`; use local pinned snapshots and `local_files_only=True` where accepted by the pinned Hub mixin. A top-level local encoder path alone does **not** prevent the constructor fetching `stabilityai/sd-turbo`: redirect every nested `from_pretrained` in `vine_turbo.py` and `model.py` to the pinned local dependency directory, preserving subfolder arguments. Set offline environment variables during stage-2 execution to prove no fallback fetch. Keep a small patch manifest/diff, not a vendored repository. All weight loading must remain safetensors/strict compatible loading; no unsafe-pickle fallback.

The encoder is a one-step model. Its expected input is float tensor B×3×256×256 in [-1,1] plus B×100 float bits in {0,1}; expected return is B×3×256×256 in [-1,1]. `VAE_encode` uses posterior **mode**, not sampling. Empty text embedding and scheduler timestep are internal. Native precision is fp32; do not inherit autocast from the regenerator. Set eval and inference mode explicitly. The decoder expects B×3×256×256 in [0,1], returns B×100 probabilities through ConvNeXt-B plus sigmoid; do not ImageNet-normalize this input.

Follow `watermark_encoding.py:27–76` and `watermark_decoding.py:36–57`:

1. Use canonical 512×512 RGB input. Native CLI center-crops nonsquare inputs, irrelevant here; do not introduce another crop.
2. PIL RGB -> torchvision bicubic resize to 256 -> ToTensor -> 2x−1. Keep full original tensor at 512 in [-1,1].
3. Run encoder at 256. Subtract the **same resized input** to obtain residual. Bicubic-resize this tensor residual to 512 using torchvision Resize; add it to the original 512 tensor. Do not simply upsample the generated 256 image.
4. Map back to [0,1], clamp, and use native `ToPILImage` quantization before PNG round-trip. Its float-to-uint8 conversion truncates; replacing it with `np.rint` changes native output. Freeze torchvision/Pillow versions and antialias behavior.
5. Decoder: PNG RGB -> PIL bicubic resize256 -> ToTensor [0,1]; apply decoder and `numpy.round` to its probabilities, including its ties-to-even behavior. Validate finite values, output length100 and probability range.
6. Pass the recorded per-source 100 random bits directly. CLI text mode pads 12 characters and appends four fixed zeros; it is unsuitable for the stipulated random 100-bit message. No ECC is used in W-Bench bit metrics.

Full SD-Turbo init weights are the conservative compatible choice. A future config-only initialization of UNet/VAE could save ~3.80 GB because VINE loads learned tensors afterward, but is not approved as equivalent without strict state coverage checks, including aliased VAE tensors. It must not silently omit text-encoder computation or change scheduler config.

## Native versus common operating point

There is **no universal numeric native VINE presence threshold** in the inspected release. `watermark_decoding.py` prints bit accuracy. `watermark_decoding_wbench.py:144–150` computes sklearn ROC on original/marked bit-agreement scores and reports the last ROC TPR with FPR **strictly below** .01 and .001. Paper §4.2 reports those empirical operating points. Appendix C's threshold70 example is illustrative, not a deployment default. Do not mislabel 70%, 80%, exact-message match, or the common threshold as native VINE.

Freeze common presence at at least **69/100** agreeing bits, exact one-sided Binomial(100,.5) tail 0.00009157161244117683. This is nominal random-message null calibration, not measured image FPR. Report raw bit accuracy and exact-message recovery too. Report native W-Bench-style ROC descriptively with explicit denominator and attainable FPR resolution; 60–120 independent unmarked sources cannot validate .1% or 1e-4 FPR. Never choose the primary threshold from attacked outputs. Native empirical ROC is a reporting statistic, not an amended decision rule.

## Published evidence and limits

Table1 at 512: VINE-R clean PSNR37.34, SSIM.9934, LPIPS.0063; stochastic/deterministic regeneration TPR@.1% FPR 99.66%/99.98%. These aggregate heterogeneous severity levels, not SDXL strength.2. §4.1 stochastic noise timesteps60–240 in increments20; deterministic DPM-Solver15/25/35/45; all global/local editing50 steps, prompt guidance5–9 and image guidance1.5. Table7 on Quadro RTX6000 reports .0795 s/image and 4982MB for VINE; it is an author benchmark, not this server's timing. The native model is a strong approved comparator but not evidence that F5 should meet the same number under another encoder.
