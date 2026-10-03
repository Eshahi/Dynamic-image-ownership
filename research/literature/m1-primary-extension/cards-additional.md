# Additional primary-paper cards for M1

Inspected 2026-10-03 from the existing artifacts below; no new downloads or experiments. SHA-256 values and source URLs are in `download-records.json`. Each card contains fewer than 200 source-derived words. The three HTML headers explicitly state CC BY 4.0, more specific than the generic rights language in that inventory. StegaStamp's CVF PDF is a research reading copy; no blanket reuse license is inferred. Bibliography additions are scoped to `references-additional.bib`.

## Stable Signature — Fernandez et al., 2023

Source: [arXiv v2](https://arxiv.org/html/2303.15435v2), local `stable-signature-v2.html`. Inspected §§3–4, §§5–7, Table 1, Fig. 7 and Appendix A.

Mechanism: pretrain a HiDDeN image extractor with simulated transformations, discard its encoder, PCA-whiten extractor outputs, then fine-tune the LDM VAE decoder to emit a fixed 48-bit signature. Detector observes RGB and the reference signature plus learned extractor; it requires no diffusion inversion. The binomial false-positive calculation assumes independent unbiased decoded bits; multiple users increase false-positive opportunity (§3).

Evidence: decoder tuning uses 100 iterations, batch four (§4.2). Table 1 text-to-image results: paired-generator PSNR 30.0 dB, SSIM .89, bit accuracy .99 clean/.95 crop/.97 brightness/.92 combined. These are generation differences, not distortion of an existing photograph.

Failure: the original model's autoencoder removes the signature at PSNR above 29 dB (§7.1/Fig. 7). A leaked extractor enables adversarial removal and unauthorized signature embedding. A learned lightweight extractor is feasible in principle, but this changes embedding to a trained decoder and does not bind content to OwnerID.

## Watermark Anything — Sander et al., 2025 version

Source: [arXiv v2](https://arxiv.org/html/2411.07231v2), local `wam-v2.html`. Inspected §§3–5, Figs. 4–5, Appendices D–E and G.3/Table 9.

Mechanism: an image autoencoder and message lookup produce an additive residual; JND scaling reduces visibility. A ViT and pixel decoder output a detection mask and 32 message probabilities per pixel. Training splices marked/unmarked regions and later multiple messages. Extraction averages detected pixels or DBSCAN-clusters local messages; no reference image or diffusion inversion is required (§§3–4).

Evidence: §5.4 recovers approximately 31/32 bits from a marked 10% region of a 256-square image, about 25 bits when that marked fraction survives a 25% crop. Five distinct 32-bit messages in disjoint 10% regions yield 85% mIoU and over 95% bit accuracy after flip plus contrast (§5.5); accuracy counts discovered clusters only. Adding JPEG causes failure.

Regeneration limit: Table 9 DiffPure bit accuracy is 100/99.4/71.3/49.1% at PSNR 30.1/28.4/27.0/24.9 dB; VAE accuracy is 100/99.8/98.6/53.7% at 32.9/32.4/28.6/25.5 dB. Useful T4 localization architecture, not proof of T3 survival or cryptographic ownership.

## WAVES benchmark — An et al., 2024 version

Source: [arXiv v2](https://arxiv.org/html/2401.08573v2), local `waves-v2.html`, titled *Benchmarking the Robustness of Image Watermarks*. Inspected §§3–4, Table 3, Appendix D and E.2.

Mechanism: benchmark three marks under 26 attacks across three datasets; measure detection TPR at 0.1% FPR jointly with eight quality metrics. Detector side information follows each mark: message/extractor for StegaStamp and Stable Signature, model/inversion/key for Tree-Ring.

Regeneration: target SD2.1, attacker SD1.4; single diffusion uses 40–200 noising/denoising timesteps. Other channels include CompressAI bmshj2018 quality 1–7, KL-VAE bottlenecks 4/8/16/32, repeated diffusion, known-prompt regeneration and diffusion followed by VAE (§3.2.2/E.2). These timestep definitions cannot be equated with local img2img strength .4.

Evidence: Table 3 single Regen-Diff mean TPR@0.1%FPR is .612 Tree-Ring/.001 Stable Signature/.943 StegaStamp, averaged across tested strengths and datasets; corresponding normalized quality degradation .323/.300/.327. These averages hide individual severe failures. Low-FPR detection curves and quality-conditioned attack results are needed; bit accuracy or AUROC alone cannot establish reliable detection. No general theorem about all watermarks follows from these three implementations.

## StegaStamp — Tancik et al., CVPR 2020

Source: [CVF paper](https://openaccess.thecvf.com/content_CVPR_2020/papers/Tancik_StegaStamp_Invisible_Hyperlinks_in_Physical_Photographs_CVPR_2020_paper.pdf), local `stegastamp-cvpr2020.pdf`. Inspected PDF pp. 3–7, §§3–5, Tables 1–2; extracted with bundled pypdf.

Mechanism: a U-Net residual embeds 100 bits in 400-square RGB images. A spatial-transformer convolutional decoder recovers bits. Training simulates perspective, blur, color, noise and JPEG with message/perceptual/adversarial losses. Wide-field detection requires a separately trained BiSeNet segmenter, quadrilateral fit and homography rectification (§4); the decoder alone does not localize a stamp.

Evidence: 1,890 physical captures across six display/print methods and three cameras average 98.7% bit recovery (§5.2/Table 1). This controlled experiment uses manually cropped and rectified images. Table 2, 500 images: 100-bit payload PSNR 28.50 dB, SSIM .905, LPIPS .101; 200 bits degrade to 21.79/.793/.184. BCH reduces 100 transmitted bits to at least 56 recoverable information bits under the stated accuracy estimate (§5.4).

Limits: detector can miss video frames (§5.1); occlusion examples are qualitative, not a calibrated T4 ownership test. Physical-channel robustness provides no diffusion-regeneration guarantee, and payload presence alone is not authenticated content binding.
