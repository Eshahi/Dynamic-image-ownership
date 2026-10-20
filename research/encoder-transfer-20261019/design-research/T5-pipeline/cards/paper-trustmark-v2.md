# TrustMark: Robust Watermarking and Watermark Removal for Arbitrary Resolution Images

[Primary source](https://openaccess.thecvf.com/content/ICCV2025/papers/Bui_TrustMark_Robust_Watermarking_and_Watermark_Removal_for_Arbitrary_Resolution_Images_ICCV_2025_paper.pdf). Verification level **V2: methods and evaluation inspected**. Recheck date2026-10-20.

**V2 recheck completed:** final ICCV2025 paper, methods §3.1/§3.3/Algorithm1 and evaluation §4.1–4.2, pages3–5. Cached final-paper page transcripts were reread rather than treating the2023 abstract as the final publication.

**Mechanism:** learned residual watermarking at fixed network resolution, spatial/spectral/perceptual objectives, residual scaling to arbitrary resolution. The learned100bit channel and a deployable BCH payload are distinct layers.

**Evaluation reread:** MIRFlickr100k training/1k validation; CLIC, MetFace and DIV2K training+validation images for evaluation. Authors use PSNR and bit accuracy, with resolution scaling generally applied to baselines. DIV2K PSNR42.39dB is reported;125/25ms encode/decode are author RTX3090 timings, not measurements here.

**Audit use / limits:** final paper is the evidence for claimed quality/robustness tradeoff, not a pin for the current Python runtime. Its fixed256 description must not override Python Q decoder245 at the pinned commit. Native BCH-validity is neither expected-payload equality nor a Binomial100 image detector. Proposed P1 stays outside the core until amended.

**Read locations:** `trustmark-final-page-003.txt`, `004`, `005` (OCR text, publisher pagination18631–18633); no precision-critical new formula inferred from OCR.
