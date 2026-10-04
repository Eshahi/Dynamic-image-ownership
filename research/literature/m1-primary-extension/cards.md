# M1 primary-source extension (2026-10-03)

Exploratory research; direct source observations below are not reproduced results. Local official-source snapshots and SHA-256 are in `download-records.json`. Existing SEAL card remains preserved; this is a version-specific follow-up, not a replacement.

## GROW — Luo, Jia, Zhong, Zhang, Zhou; CVPR 2026, pp. 35978–35987

Primary PDF: https://openaccess.thecvf.com/content/CVPR2026/papers/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.pdf

Inspected sections 3–5.5, algorithm 1, tables 1–4; table 1 also visually checked. **Direct evidence:** gradients guide predicted clean latent DCT coefficients toward repeated signed symbols, then modify scheduler noise (eqs. 4–7). Detection uses VAE encoding plus latent DCT, without diffusion inversion. Section 5.2 specifies first latent channel, 16 bits, alpha .5, eta 100, 50 steps, r_start .5. Table 1 reports generated-COCO PSNR 27.54, SSIM .85, LPIPS .05, exact-message clean accuracy 1.00 and adversarial .95. Table 3 extraction is .24 seconds on T4. **Limits:** generated-image experiment, secret mask, no dual content keys. Those quality means do not meet our source-image targets. Diff-Pure is not automatically our SD1.5 T3 protocol. **Agent inference:** strong relevant evidence for an explicit VAE-detector amendment; no evidence for image-only block-DCT detection. README defaults differ from paper; paper takes priority. Guidance-time index convention and loss normalization require explicit adapter choices.

## ZoDiac — arXiv 2401.04247v2

Primary text: https://arxiv.org/html/2401.04247v2

Inspected sections 3.1–3.3, 4.1–4.2, table 1. **Direct evidence:** DDIM-invert existing image; constrain last-channel noise Fourier rings; optimize reconstruction through frozen diffusion; adaptively mix generated output with original (eq.7). Native detection uses inversion and a ring-distance statistic. SD2.1-base, 50 steps, at most100 optimization iterations, ring radius10, target SSIM .92. COCO table1 reports PSNR29.41, SSIM.92, LPIPS.09, clean WDR.998 and Zhao23 WDR.988. **Limits:** mixing is a hybrid output and detection uses inversion; it cannot validate our lightweight hypothesis. Attack regimes and detection thresholds differ from our contract. **Agent inference:** optimize reconstruction and disclose any residual mixing explicitly; do not attribute mixed-output quality to a pure decoder image.

## SEAL — arXiv 2503.12172v4

Primary text: https://arxiv.org/html/2503.12172v4

Inspected section3.2 algorithms and section4 experimental tables in this follow-up; preserve existing bibliography identity Arabi2025SEALv4. **Direct evidence:** proxy generation, caption embedding, patch-wise SimHash, secret salt, deterministic Gaussian noise; verifier uses suspect caption embedding and DDIM inversion. Patch matching tolerates semantic feature changes; it does not imply exact whole-vector hash stability. **Limits:** public OwnerID is not the paper secret salt; caption/embedding and inversion are extra models. **Agent inference:** locally sensitive subkeys are more plausible than an avalanche hash of a floating vector, but transferring the design to public keys removes authentication assumptions.

## CtrlRegen — arXiv 2410.05470v2

Primary text: https://arxiv.org/html/2410.05470v2

Inspected sections3 and4.1–4.2/table1. **Direct evidence:** clean initial noise plus DINOv2 semantic and edge spatial conditioning regenerates content; CtrlRegen+ starts from partially noised image latent. Table1 TreeRing TPR at1%FPR drops .99 to .12 with CtrlRegen, versus .87 under Regen; attack-output PSNR is19.32. **Limits:** stronger trained controlled attacker, not our empty-prompt local img2img. Pixel similarity and semantic retention differ; cannot reuse this as an observed local counterexample. **Agent inference:** persistence through mild img2img does not establish survival when an attacker resamples noise while retaining semantic/spatial conditions. Semantic content alone is not proof of an owner-carried signal.

### GROW implementation addendum, 2026-10-04
Parent and method agent inspected pinned upstream6aa69a9c code archived in grow-code-6aa69a9c/. Actual loop guides indices25–49 of50, unlike our declared first-half screen. It guides conditional prediction before CFG; the DCT-named helper is real FFT, unlike our true orthonormal DCT. Defaults also differ (fp32,eta200,all4 channels). These implementation differences do not invalidate published results or convert our candidate into a reproduction. A schedule-only follow-up isolates one change; derivation, exact source links, numerical CPU fixtures and prospective gates are in ../../m1-progressive-diagnosis.md. Original failed screen is retained.
