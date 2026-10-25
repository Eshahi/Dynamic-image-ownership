# V2 card: Zhao et al. (2024)

- **ID / key:** `zhao2024invisible`; **title:** *Invisible Image Watermarks Are Provably Removable Using Generative AI*.
- **Authors:** Xuandong Zhao, Kexun Zhang, Zihao Su, Saastha Vasan, Ilya Grishchenko, Christopher Kruegel, Giovanni Vigna, Yu-Xiang Wang, Lei Li. **Year / venue / version:** 2024, NeurIPS; arXiv:2306.01953v3 (31 October 2024). **DOI:** unverified.
- **Canonical text:** https://arxiv.org/html/2306.01953v3. **Access:** 2026-10-25. **Artifact and SHA-256:** `source-manifest.json`, ID `zhao-provable`.
- **Inspected:** §§2.2–2.3, 3.1–3.3/Algorithm 1, 4.1–4.2/Theorems 4.3–4.4, 5/Table 1/Figures 4–5, Appendix E/Table 2. **Verification:** V2.

**Threat and method — direct evidence (§§2.2,3):** The attacker sees a watermarked image, no embedding secret, no detector queries. It encodes, injects Gaussian noise, then reconstructs by VAE or diffusion. Theorem 4.3 is a detector-independent tradeoff *conditional on* an ℓ2 `Δ` invisibility bound and local embedding gain `L`; its governing ratio is `LΔ/σ`. Theorem 4.4 also assumes the denoiser reconstructs the noisy *unmarked* image sufficiently well. These are explicit conditions, not an unconditional impossibility result.

**Checked experiment (§5 and Appendix E):** 500 MS-COCO photos and 500 SD2.1-generated images; four post-hoc pixel schemes. §5.1 states >99% removal for DwtDctSvd, RivaGAN and SSL with regeneration, while StegaStamp requires more noise. Table 1 gives un-attacked MS-COCO StegaStamp PSNR 28.50 dB versus SSL 41.79 dB. Appendix E Table 2 gives Tree-Ring TPR at 1% FPR of 1.000 on COCO and 0.998 on generated images after a 60-step diffusion attack.

**Limit / inference:** The study does not test F5, independently trained autoencoder transfer, or attack quality matching to this thesis. Its Tree-Ring result conflicts with An et al.'s later WAVES rinsing result under a different protocol; do not flatten them into a universal survival statement. **Agent inference:** F5 can be studied via encoder gain `L`, but the paper does not establish its value.
