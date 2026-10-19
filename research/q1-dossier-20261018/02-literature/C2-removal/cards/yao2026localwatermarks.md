# yao2026localwatermarks — V2

Accessed 2026-10-18. Verification denotes primary method and evaluation/proof inspection, not reproduction.

**Metadata.** Kai Yao, Bence Szilágyi, Sebestyén Kamp, Máté Poór, Máté Szilveszter, Matyas K. Zsoldos and Marc Juarez. *What Breaks Local Watermarks? A Robustness Benchmark for Local Invisible Image Watermarking*. arXiv 2609.16832v1, 2026-09-15; metadata states accepted AISec 2026, final DOI unverified. [Full text](https://arxiv.org/html/2609.16832v1). Inspection: §§3–4, particularly §4.5 and Appendix A.1.

**Setting/mechanism.** Five local or adapted global methods—MaskWM, WAM, OmniGuard, TrustMark and PixelSeal—with and without synchronization, under 55 transformations. Blind image decoding, not registry-based ownership verification.

**Evaluation.** 200 images from each of COCO 2017, SA-1B, DIV2K and MIRFLICKR: 800 per method. Payloads differ (64, 32, 100, 100 and 256 bits). One fixed random realization is used per image/transformation. A binomial-null evidence score uses a threshold of three decimal orders.

**Finding/limit.** Global reconstruction during inpainting can damage marks outside the nominal edit mask; restoring the outside region changes the outcome. The binomial tail is a modeled single-attempt score, not an empirically established deployment-wide FPR.

**Thesis implication.** T4 needs an exact compositing/reconstruction definition. Localization and untouched-region survival are distinct from binding a recovered owner pointer to the correct registered image.

