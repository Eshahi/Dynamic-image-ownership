# Agarwal2026Signpost

**Source:** Shruti Agarwal, Vishal Asnani, John Collomosse. *Signpost Watermarking: Joint Optimization for Visual Watermark Coexistence*. [arXiv:2608.10091v1](https://arxiv.org/html/2608.10091v1), 10 August 2026. Accessed 2026-10-19. **V2:** §§1–4, Tables 1–4 and references inspected.

**Verified edge:** reference [7] cites final TrustMark, ICCV2025, pp.18629–18639.

**Direct evidence:** §1 proposes a 32-bit signpost identifying watermark technologies and routing to their decoders. Its registry enumerates technologies, not enrolled original images. §3 trains a residual encoder/decoder to decode the signpost after frozen secondary watermark encoders overlay it. §4 evaluates 1,000 MIRFlickr images, conventional augmentations and separate video settings. Table 4's SP-first noise bit accuracy with TrustMark-P overlay rises from .841 without coexistence loss to .960 with all losses; PSNR changes 53.0→52.3 dB.

**Interpretation:** authors advocate explicitly optimized coexistence. My inference: this is relevant architecture prior art, but its ablation concerns a different writer and channel. Table 3 reverses insertion order; Table 4 cannot alone causally explain that opposite-order result. No diffusion, hard-lookalike registry attribution or owner/q/content ablation is established here.

**Artifact:** MAIN `.thesis-build/q1-research-20261018/cache/signpost-2608.10091v1.html`; SHA256 `90316A1D6A5DF4345FD07B9B7B556BF3999ADB13B625D1DC3A8AB40ACBEAEAFF`.
