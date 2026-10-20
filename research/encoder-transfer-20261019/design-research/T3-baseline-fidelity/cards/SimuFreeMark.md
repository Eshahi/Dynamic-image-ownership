# SimuFreeMark: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **SimuFreeMark: A Noise-Simulation-Free Robust Watermarking Against Image Editing**. Version/date: arXiv:2511.11295v1 [cs.CV] 14 Nov 2025. Venue: arXiv preprint 2025; venue not verified.

Authors: Yichao Tang; Mingyang Li; Di Miao; Sheng Li; Zhenxing Qian; Xinpeng Zhang. Year: 2025. DOI: not established for this inspected version.

Stable ID: `arxiv:2511.11295v1`. Citekey: `T3SimuFreeMark2511`. Canonical URL: https://arxiv.org/abs/2511.11295v1

Primary full text: https://arxiv.org/html/2511.11295v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/simufreemark.txt`
SHA-256: `a964732819a4f3a5ee991566b450cb9d582da59ac1366665f0c3bb14d7fb5ed6`

Actually inspected: §§3.2–3.3,4.1–4.2, Tables 1–2.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A low-frequency latent watermark combines a frozen diffusion VAE with a learned residual encoder. A central FFT low-pass surrogate and restored high-frequency content avoid running iterative diffusion in training.

## Native operating point and detector side information

The reported setting is 512-pixel RGB, 64 raw bits, a central 20% FFT region, latent residual alpha=.2 and pixel range [-.5,.5]. CNN sigmoid outputs are rounded to bits. No native calibrated presence threshold or ECC is specified; executable resizing, clamping and quantization could not be verified because no official release was found.

## Code, weights, pinned release and licenses

Exact-title web and GitHub repository searches found no verified official code or weights. No released implementation or checkpoint license was established; faithful implementation would be new work.

## Published evaluation and regeneration conditions

Training uses 20,000 COCO images; testing uses 1,000 UltraEdit images with instructions and masks. Table 2 reports SDIP+ full-image inpainting/regeneration bit accuracy 97.64/94.05/92.25% at strengths .1/.3/.5, and InstructPix2Pix 90.42%. Clean quality is PSNR 39.19 and SSIM .990. Exact model revisions, sampler, steps, prompt strings and per-strength seed counts are incompletely specified. These are bit accuracies without a calibrated negative population, not TPR.

## Cost and uncertainty

A feed-forward latent encoder would require a VAE roundtrip, but neither target inference time nor peak memory is established. Avoid translating training efficiency into an invented runtime.

## Limitation and design implication

Directly relevant evidence for surrogate-trained regeneration robustness, but release and attack-detail gaps prevent a faithful runnable proposal now.

Disposition: **Literature coverage; excluded**
