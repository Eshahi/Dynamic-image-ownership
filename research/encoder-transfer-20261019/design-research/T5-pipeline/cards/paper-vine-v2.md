# Robust Watermarking Using Generative Priors Against Image Editing: From Benchmarking to Advances

[Primary source](https://arxiv.org/html/2410.18775v2). Verification level **V2: methods and evaluation inspected**. Recheck date2026-10-20.

**V2 recheck completed:** §3.1–3.3 architecture/training; §4.1 editing/regeneration protocol and §4.2–4.3 evaluation.

**Mechanism:** generative prior, secret-conditioning adapter, skip-connected VAE and ConvNeXt100bit extractor; VINE-R adds Pix2Pix regeneration adaptation with a straight-through training approximation. Paper says SDXL-Turbo; pinned released code actually uses SD-Turbo. Preserve that disagreement explicitly.

**Evaluation reread:** OpenImages training at256; evaluation uses10k UltraEdit images, with1k regeneration subsets and512 outputs. Regeneration includes stochastic VP timesteps60–240 in increments20 and deterministic DPM15/25/35/45. Editing uses50steps, text-guidance5–9/image1.5. TPR at.1%/1%FPR depends on benchmark-specific ROC calibration.

**Audit use / limits:** supports native100bit/residual-resolution pipeline and the need to state editing/reconstruction settings. No reported aggregate equals our empty-prompt DDIM20 SDXL .2 test. Common69/100 agreement is independently fixed random-message calibration, not the paper's empirical image operating point or an ECC decoder.

**Read locations:** `paper-vine.txt:370–480,490–516,755–787`.
