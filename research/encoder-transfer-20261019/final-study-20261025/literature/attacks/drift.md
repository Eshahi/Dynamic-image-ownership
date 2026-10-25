# V2 card: Bao et al. (2026)

- **ID / key:** `bao2026drift`; **title:** *DRIFT: Removing Diffusion Watermarks by Deflecting the Generative Trajectory*.
- **Authors:** Rui Bao, Zheng Gao, Xiaoyu Li, Xiaoyan Feng, Yang Song, Jiaojiao Jiang. **Year / venue / version:** 2026, arXiv:2609.08213v1 (8 September 2026), preprint. **DOI:** unverified.
- **Canonical text:** https://arxiv.org/html/2609.08213v1. **Access:** 2026-10-25. **Artifact and SHA-256:** manifest ID `drift`.
- **Inspected:** §§3.1–3.4, 4.1–4.3, 5.1–5.4/Table 1 and Appendix E. **Verification:** V2.

**Threat and method — direct evidence (§3):** Base DRIFT is a query-free attack using a public latent diffusion model that may differ from the marked generator. It combines partial forward noising with stochastic reverse resampling. Its *adaptive* and fidelity-refinement variants, however, use binary verifier feedback to choose a strength and retain only rejected candidates. These variants therefore have materially stronger attacker access than this thesis's proposed no-feedback informed attack.

**Checked experiment (§5/Table 1):** Nine watermark families. Table 1(b) reports fixed-strength DRIFT 100.0% ASR but PSNR 14.31 dB and LPIPS 0.528; adaptive without refinement 99.7% ASR, PSNR 23.72 dB, LPIPS 0.168; full adaptive with verifier-gated refinement 100.0% ASR, PSNR 24.01 dB, LPIPS 0.154. The table's own contrast shows why ASR alone is inadequate.

**Limit / inference:** Watermarks are principally diffusion-generation families, not F5's image-domain writer. Adaptive results require verifier queries; none of the listed fidelity averages meet a strict PSNR>35 dB image-quality gate. **Agent inference:** stochastic versus deterministic reversal is a useful controlled server measurement, but the reported ASR is not an admissible estimate of attack success under the thesis threat or clean-quality gate.
