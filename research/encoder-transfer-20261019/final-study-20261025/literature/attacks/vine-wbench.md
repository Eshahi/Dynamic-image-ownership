# V2 card: Lu et al. (2025)

- **ID / key:** `lu2025vine`; **title:** *Robust Watermarking Using Generative Priors Against Image Editing: From Benchmarking to Advances*.
- **Authors:** Shilin Lu, Zihan Zhou, Jiayou Lu, Yuanzhi Zhu, Adams Wai-Kin Kong. **Year / venue / version:** 2025, ICLR; arXiv:2410.18775v2 (15 March 2025). **DOI:** unverified.
- **Canonical text:** https://arxiv.org/html/2410.18775v2. **Access:** 2026-10-25. **Artifact and SHA-256:** manifest ID `vine`.
- **Inspected:** §§3.1–3.3 and 4.1–4.4/Table 1. **Verification:** V2.

**Threat and method — direct evidence (§§3–4):** W-Bench covers stochastic/deterministic regeneration, global/local editing and image-to-video. VINE trains a watermark encoder with blur-like surrogate distortions and an SDXL-Turbo generative prior; VINE-Robust adds robustness training. The attacker in W-Bench has image-editing tools rather than watermark secret access.

**Checked experiment (Table 1):** The paper evaluates 11 baseline schemes and two VINE variants. It states image quality averaged over 10,000 images and TPR at 0.1% FPR for each edit averaged over 5,000 images. Table 1 reports VINE-Robust PSNR 37.34 dB, SSIM 0.9934, LPIPS 0.0063; average stochastic and deterministic regeneration TPRs are 99.66% and 99.98% respectively. This is the paper's protocol, not this thesis's VINE-R subset.

**Limit / inference:** Editor mix, payload capacity (100 bits for VINE-Robust), FPR and clean quality differ from F5. It does not prove transfer to every encoder or attack. **Agent inference:** use VINE-R as a positive control for the thesis's SDXL cell but retain its stricter clean-quality caveat from project results.
