# V2 card: Liu et al. (2025)

- **ID / key:** `liu2025ctrlregen`; **title:** *Image Watermarks are Removable Using Controllable Regeneration from Clean Noise*.
- **Authors:** Yepeng Liu, Yiren Song, Hai Ci, Yu Zhang, Haofan Wang, Mike Zheng Shou, Yuheng Bu. **Year / venue / version:** 2025, ICLR; arXiv:2410.05470v2 (2 March 2025). **DOI:** unverified.
- **Canonical text:** https://arxiv.org/html/2410.05470v2. **Access:** 2026-10-25. **Artifact and SHA-256:** manifest ID `ctrlregen`.
- **Inspected:** §§3.1–3.3, 4.1–4.2/Tables 1 and 3, Appendix A. **Verification:** V2.

**Threat and method — direct evidence (§3):** CtrlRegen trains semantic and spatial conditioning to reconstruct a watermarked image from *fresh Gaussian noise*. CtrlRegen+ allows a controllable partially noised latent. It is a trained generic removal system, with no need for target detector feedback at inference, but training and proxy infrastructure are substantial. Unlike a simple VAE round trip, it can break marks with large image/latent perturbation.

**Checked experiment (§4/Table 1):** 1,000 MIRFLICKR photos for post-hoc marks and generated examples for in-generation marks. §1/§4 reports StegaStamp TPR at 1% FPR falling from 1.00 to 0.01 and Tree-Ring from 0.99 to 0.12 under CtrlRegen. The paper compares removal, bit accuracy and image quality; CtrlRegen+ adjusts noising steps for the tradeoff.

**Limit / inference:** It is more resource-intensive than the thesis's one-pass img2img threat and uses learned conditional controls that may transmit mark information. Results do not establish anything about F5 specifically. **Agent inference:** a server-only full-noise controlled-regeneration arm would test a stronger attack class, but cannot be treated as matched severity without independent quality constraints.
