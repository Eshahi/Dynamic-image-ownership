# V2 card: An et al. (2024)

- **ID / key:** `an2024waves`; **title:** *WAVES: Benchmarking the Robustness of Image Watermarks*.
- **Authors:** Bang An, Mucong Ding, Tahseen Rabbani, Aakriti Agrawal, Yuancheng Xu, Chenghao Deng, Sicheng Zhu, Abdirisak Mohamed, Yuxin Wen, Tom Goldstein, Furong Huang. **Year / venue / version:** 2024, ICML; arXiv:2401.08573v3 (7 June 2024). **DOI:** unverified.
- **Canonical text:** https://arxiv.org/html/2401.08573v3. **Access:** 2026-10-25. **Artifact and SHA-256:** manifest ID `waves`.
- **Inspected:** §§3.1–3.2/Table 2/Figure 3, 4.1–4.5/Table 3 and Appendix G regeneration discussion. **Verification:** V2.

**Threat and method — direct evidence (§3):** WAVES evaluates a watermark against distortions, single regeneration, repeated diffusion “rinsing,” and adversarial attacks. It treats image-quality degradation and detector degradation jointly, with detection and user-identification tasks. Its repeated regeneration is an attack family with multiple diffusion passes, not a single `strength` setting.

**Checked experiment (§§3–4):** The benchmark states 26 attacks, eight quality metrics and three datasets. §3.2/Figure 3 says two-pass diffusion rinsing harms Tree-Ring TPR at 0.1% FPR while preserving more quality than deeper rinsing; longer rinses further lower detection with marked quality cost. §4.1 compares Stable Signature, Tree-Ring and StegaStamp; the paper explicitly disputes Zhao et al.'s claim of Tree-Ring robustness to regeneration in their tested setting.

**Limit / inference:** Attack depth, image quality, detector FPR and watermark implementation must be aligned before comparing this with Zhao or F5. Figure 3 is a curve, not a single portable rate. **Agent inference:** include a frozen low-strength multipass arm and report every pass's distortion and score, rather than claiming a universal rinse effect.
