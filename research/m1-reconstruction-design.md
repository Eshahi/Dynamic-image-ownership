# M1 reconstruction channel diagnostic

Fixed before run, 2026-10-03. Exploratory development; no watermark or efficacy claim.

Hypothesis: the pinned SD1.5 decoder can represent each of the 12 reserved COCO development images at source PSNR >35 dB, RGB SSIM >.9 and LPIPS <.1 after optimizing only its posterior-mode latent. This is a necessary quality diagnostic for the simplest pure decoded-image candidate, not a mathematical bound on every latent or architecture.

Manifest: m1-reconstruction-dev.json. No held-out data. Unit: source image. Preprocess: EXIF transpose, profile-aware RGB, bicubic512x512 as existing pilot. Frozen VAE fp32; Adam lr.02, steps0/50/100/200. Save unmarked RGB8 outputs at each stage, quantization included; source is original resized image. No pixel residual, source blending, or posthoc watermark. All12 sources remain denominator. Outcomes: PSNR/SSIM/LPIPS, within-image progression, convergence, peak memory, elapsed time. No p-values; 12 dev groups cannot establish population performance. Human visual verdicts missing.

Stop at200 steps per image or failure; preserve failure record, fix infrastructure in a new run. If all12 satisfy conjunction at200, proceed to latent watermark objective. If some fail, examine convergence and spend a bounded larger budget on representative failures before abandoning this instantiation; consider explicit hybrid amendment and separately investigate initial-noise and final-latent symbol designs. A failed first optimization is not global impossibility. Thresholds are acceptance.md numeric quality targets, not chosen using these outcomes. SSIM implementation is explicitly recorded; final candidate must use contract-compatible metric parity.

Local RTX5070Ti, batch1,10GiB VRAM allocation ceiling, USD0, no download, no authorization JSON. Expected20–50min initially, to be measured on first source. Outputs under MAIN/.thesis-build/dev-runs/ with immutable unique run directory; source/model/code hashes, seeds, commit, command, errors and durations retained.
