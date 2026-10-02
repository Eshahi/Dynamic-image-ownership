# Verification of the Perplexity brief (2026-10-02)

Input: [perplexity-agent-brief-20261002.md](perplexity-agent-brief-20261002.md), a byte-identical copy of the file the user supplied (`diffusion-watermark-agent-brief.md`, SHA-256 `0e8308e4...2312a1`). Checked by Claude Code (`claude-opus-5-5`) on 2026-10-02 by opening each cited page. "Checked" below means the page was opened and its title, authors and venue were read; "abstract" or "full text" says how far the content was read. Nothing here is a reproduction of a result. These entries are not yet in `literature-matrix.csv` or `references.bib`; adding them is ordinary B1 work.

## Citation check

| Ref | As cited in the brief | What the page shows | Verdict |
| --- | --- | --- | --- |
| 1 | Rombach et al., CVPR 2022, LDM | CVF page refused automated access (HTTP 403). Title and venue are common knowledge, not re-read today. | Not re-checked |
| 2 | "Zhao et al., Generative Autoencoders as Watermark Attackers, ICML 2023", `proceedings.mlr.press/v202/zhao23g.html` | That URL is "Revisiting Simple Regret: Fast Rates for Returning a Good Arm" (Y. Zhao, Stephens, Szepesvari, Jun), a bandit paper. A search finds "Generative Autoencoders as Watermark Attackers: Analyses of Vulnerabilities and Threats" only as a 2023 preprint by Zhao, Zhang, Wang and Li; to the checker's knowledge it is the first version of arXiv 2306.01953, which is reference 3, but the arXiv page read today does not show earlier titles. No ICML 2023 paper of that title was found. | **Wrong link and venue; duplicate of 3** |
| 3 | "Sadasivan et al., Invisible Image Watermarks Are Provably Removable Using Generative AI, NeurIPS 2024" | Title and venue correct. Authors are Xuandong Zhao, Kexun Zhang, Zihao Su, Saastha Vasan, Ilya Grishchenko, Christopher Kruegel, Giovanni Vigna, Yu-Xiang Wang, Lei Li. Already in `references.bib` as `Zhao2023Regenerationv3`. | **Wrong first author** |
| 4 | An et al., WAVES, ICML 2024, arXiv 2401.08573 | Correct. Full text read in part. | OK |
| 5 | "Zhao et al., Image Watermarks are Removable Using Controllable Regeneration from Clean Noise, 2024", arXiv 2410.05470 | Authors are Yepeng Liu, Yiren Song, Hai Ci, Yu Zhang, Haofan Wang, Mike Zheng Shou, Yuheng Bu; ICLR 2025. | **Wrong first author, venue missing** |
| 6, 7 | Zhang et al., ZoDiac, NeurIPS 2024 | Correct (Lijun Zhang, Xiao Liu, Antoni Viros Martin, Cindy Xiong Bearfield, Yuriy Brun, Hui Guan; arXiv 2401.04247). Full text read in part. | OK |
| 8 | Wen et al., Tree-Ring, NeurIPS 2023 | Correct (Wen, Kirchenbauer, Geiping, Goldstein). Abstract. | OK |
| 9 | Yang et al., Gaussian Shading, 2024, arXiv 2404.04956 | Correct; CVPR 2024. Abstract. | OK (venue missing) |
| 10 | Fernandez et al., Stable Signature, ICCV 2023 | Correct. Abstract. | OK |
| 11, 12 | Lu et al., VINE, ICLR 2025, arXiv 2410.18775, and its repository | Correct (Shilin Lu, Zihan Zhou, Jiayou Lu, Yuanzhi Zhu, Adams Wai-Kin Kong). Full text read in part. | OK |
| 13 | Tancik et al., StegaStamp, CVPR 2020 | CVF page refused automated access. Not re-read today. | Not re-checked |
| 14 | Bui et al., TrustMark, arXiv 2311.18297 | Correct (Tu Bui, Shruti Agarwal, John Collomosse). Abstract. | OK |
| 15 | Bui et al., TrustMark, ICCV 2025 | CVF page refused automated access. | Not re-checked |
| 16 | "Jiang et al., Stable Signature is Unstable, 2024", arXiv 2405.07145 | Authors are Yuepeng Hu, Zhengyuan Jiang, Moyang Guo, Neil Gong. | **Wrong first author** |

Four of sixteen references carry a wrong author or link. The brief's own instruction to treat its citations as unverified was warranted.

## What the sources say, where it matters for the design

Figures are the papers' own, read from the text; none was reproduced here.

- **ZoDiac (refs 6, 7), the brief's "primary" recommendation.** It optimises the DDIM-inverted latent of an existing image so that the regenerated image carries a ring pattern in the Fourier transform of that latent. Detection runs DDIM inversion on the suspect (Stable Diffusion 2.1 base, 50 steps). Reported on MS-COCO: PSNR 29.41 dB, SSIM 0.92, LPIPS 0.09; 45 to 256 s to mark one image; false-positive rate 6.2% at the default detection threshold and 0.4% at the strictest one tested, where detection after the diffusion regeneration attack is 93.8%. With zero denoising steps (the autoencoder alone) detection before any attack falls to 94.2% and after the regeneration attack to 71.2%. Rotation is not survived.
- **WAVES (ref 4).** Reports detection as TPR at 0.1% FPR. In its benchmark a single diffusion or VAE regeneration "significantly" harms Tree-Ring, in contrast to the earlier conclusion of Zhao et al.; regeneration is "completely destructive" for Stable Signature; StegaStamp is "mildly affected", and only by diffusion regeneration. Tree-Ring is additionally vulnerable to adversarial embedding attacks.
- **Zhao et al. (ref 3).** Proves removability of pixel-level invisible watermarks by noise-then-reconstruct attacks and names watermarks that keep the image only semantically similar as the alternative.
- **Liu et al. (ref 5).** Regeneration from clean noise under semantic and spatial control, presented as removing state-of-the-art watermarks broadly.
- **VINE (refs 11, 12).** Its frequency analysis finds that image editing removes mid- and high-frequency patterns and leaves low-frequency ones "relatively unaffected"; blur is therefore used as a cheap training surrogate for editing. 100-bit payload; SDXL-Turbo as encoder prior. Reported TPR at 0.1% FPR after stochastic regeneration: 91.0% (VINE-B, 40.5 dB) and 99.7% (VINE-R, 37.3 dB). Weights are released; they are not available offline here.
- **Gaussian Shading (ref 9), Tree-Ring (ref 8).** Initial-noise marks for images generated by the marking party; extraction needs DDIM inversion.
- **Stable Signature (ref 10), Hu et al. (ref 16).** Decoder-rooted mark read by a trained extractor; removable by fine-tuning the decoder.

Two further sources, found while checking and not in the brief:

- **FreqMark** (Guo, Li, Hui, Guo, Zhang, Cai, Wan, Wang; NeurIPS 2024; arXiv 2410.20824). Optimises a perturbation in the Fourier transform of the VAE latent (SD 2.1 autoencoder), 400 Adam steps with noise augmentation, and reads 48 bits with a pretrained DINOv2 encoder and secret direction vectors; no diffusion inversion. Reported PSNR about 31 dB, bit accuracy about 0.93 to 0.97 after VAE and diffusion regeneration, 5 to 6 minutes for two images on an A100.
- **PhaseMark** (Lee, Cho; arXiv 2601.13128, January 2026, preprint). No optimisation: VAE-encode, modulate phases in a mid band of the latent's Fourier transform (radius 10 to 18 of a 44x44 crop), decode. Detection is VAE encoding plus an FFT; no inversion. Reported 34 dB for its quality-centred variant and TPR at 1% FPR of 0.92 to 1.00 after VAE and diffusion regeneration. Aimed at generated images.

## Consequences for this project

1. **The brief's primary recommendation does not fit the proposal as it stands.** A ZoDiac-style method needs diffusion inversion at detection, which the proposal's lightweight extractor excludes (METHOD-08, RQ-03); its published false-positive rates (0.4% to 6.2%) are three to five orders of magnitude above the 1e-6 bound used here; and its fidelity is about 29 dB against the 35 dB level of this project's admissibility rule. It is a comparator candidate, not the method.
2. **"Latent" is not what the surviving methods have in common.** Tree-Ring and Stable Signature are latent or decoder-rooted and are reported as removed by regeneration; StegaStamp is an image-space method and is reported as the most robust. What the surviving methods share is a large, low-frequency change (28 to 34 dB) placed where the autoencoder keeps it. This matches VINE's frequency analysis, and it matches the retained revision-2 result here: a 42 dB mark on 8x8 coefficients with periods of 16 pixels or less, the sampling limit of an f=8 latent, was removed by the VAE round trip alone.
3. **The published band that survives lies below the lowest AC coefficient of an 8x8 block.** PhaseMark's stable band corresponds to image-space periods of about 20 to 35 pixels. An 8x8 block DCT reaches that band only when it is taken on a coarser version of the image.
4. **The published operating points are at 29 to 40 dB.** A regeneration-surviving channel at 42 dB is not supported by any source read here; a fidelity cost has to be planned and reported.
5. **Initial-noise injection (the proposal's phase 2) applies to images the owner generates.** Tree-Ring and Gaussian Shading both read their mark by inversion. For existing photographs the published routes are inversion plus optimisation (ZoDiac), latent optimisation with a neural reader (FreqMark) or trained encoders (VINE, TrustMark, StegaStamp). None reads its mark by block-DCT correlation.
6. **No guarantee exists.** The removability result of Zhao et al. and the WAVES and Liu et al. attacks apply to any mark that leaves the image perceptually unchanged; survival can only be claimed for a stated attack family and dose range.

The brief's remaining guidance (zero-bit detection first, calibration on unmarked images at fixed low FPR, attack compositions, decision gates, reporting the worst slice) is methodological and is taken over in the v5 evaluation plan; it needs no citation.
