# Zhang et al. (2025): MarkPlugger

**Verification: V2.** Method IV and evaluation V of [arXiv:2404.05607v2](https://arxiv.org/html/2404.05607v2) read on 2026-10-18 PDT. [arXiv metadata](https://arxiv.org/abs/2404.05607) explicitly identifies IEEE TMM 2025 and links DOI [10.1109/TMM.2025.3565960](https://doi.org/10.1109/TMM.2025.3565960). v2 was submitted 11 October 2025; this is a journal-linked author manuscript, not a verified byte-identical version of record.

The trained watermark encoder adds a compressed binary-image payload to a denoised latent before the frozen VAE decoder; a trained image-space decoder recovers it. “Without retraining” concerns the LDM: watermark components are trained. Detector side information includes learned extraction weights and the expected payload for verification.

V-A/B describes 82,783 COCO training pairs, 10,000 inference pairs and Flickr8k's 8,091-image external corpus. Training on SD1.1 transfers to other SD variants. Quality uses PSNR/SSIM/LPIPS and relative FID; payload recovery uses normalized correlation and character errors, not TPR at fixed FPR. Baselines include HiDDeN, SSL watermarking and open Stable Signature; the latter's fixed payload limits the comparison, while unavailable ENDE code restricts comparison to efficiency/visualization. V-E tests six conventional distortions and acknowledges weaker cross-dataset robustness. No diffusion-regeneration evaluation is presented there. V-H reports component FLOPs/parameters, rather than complete attribution latency; A800 hardware is specified. Code release was not established by the inspected manuscript.

**Assessment.** This is a useful latent-insertion comparator, not evidence that recovered text establishes ownership. Require a negative-image decision rule before translating its recovery metrics into attribution performance. Dataset counts alone do not establish source-level independence or duplicate exclusion. A fair future comparison must align payload, attack access and decision endpoints.

**Locators:** IV-A/B; V-A/B; V-C/E/H; Tables I–III; Figures 3–6.
