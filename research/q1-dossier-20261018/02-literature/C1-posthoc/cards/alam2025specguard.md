# alam2025specguard — V2

Inzamamul Alam, Md Tanvir Islam, Simon S. Woo and Khan Muhammad. *SpecGuard: Spectral Projection-based Advanced Invisible Watermarking*. ICCV 2025; inspected arXiv2510.07302v1 (8 October 2025), accessed 18 October 2026. [Primary text](https://arxiv.org/html/2510.07302v1). Locators: §§3–4, Tables 1–3 and 9, Appendix §12. Conference-version identity was not independently established.

Existing-image encoder/decoder inserts message features into wavelet high-frequency bands using FFT spectral projection and learned extraction thresholds. Detector needs learned model and embedding parameters; no content registry. Training uses 25,000 COCO images; evaluation names COCO, DiffusionDB and DALL-E3, but main attack-test counts are unclear; social/filter subset is 200.

Table 2 reports 128-bit clean PSNR42.89/SSIM.99/BRA.99. Table 3 reports average performance .982 for Regen-Diff and .993 for Rinse-2xDiff, not source-level attribution at a stated fixed FPR. Appendix lists multiple VAEs, rinsing and encoder/adversarial attacks. Payloads and quality differ across tables; average quality and strength curves cannot be equated to the thesis gate.

Relevance: strong post-hoc regeneration prior art and attack-suite norm. Spectral embedding is established; learned-threshold robustness is not a cryptographic ownership guarantee. Do not use its reported averages as a matched head-to-head result.
