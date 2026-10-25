# V2 card: Kassis and Hengartner (2025)

- **ID / key:** `kassis2025unmarker`; **title:** *UnMarker: A Universal Attack on Defensive Image Watermarking*.
- **Authors:** Andre Kassis, Urs Hengartner. **Year / venue / version:** 2025, IEEE Symposium on Security and Privacy; arXiv:2405.08363v2 (22 November 2024), author version. **DOI:** unverified.
- **Canonical text:** https://arxiv.org/html/2405.08363v2. **Access:** 2026-10-25. **Artifact and SHA-256:** manifest ID `unmarker`.
- **Inspected:** §§III–V (threat/model and two spectral optimizations), VI-A–VI-B/Table I and discussion. **Verification:** V2.

**Threat and method — direct evidence (§§III–V):** The adversary sees output images, has no watermark internals or detector queries and does not train a diffusion model. For non-semantic marks, UnMarker optimizes Fourier amplitude change with perceptual constraints. For semantic marks, it optimizes spatial filters to perturb low frequencies; mild cropping is combined in the final attack. The paper's claim that all robust carriers must live in spectral amplitude is its design argument, not a general theorem established for F5.

**Checked experiment (§VI):** Seven schemes, 100 images per scheme, 1% FPR bit-match threshold except the Tree-Ring distance threshold. §VI-B reports final StegaStamp detection 43% and Tree-Ring 40%; §VI discussion reports ordinary diffusion attack leaves both much less affected in its setup. These rates depend on the combined spectral and crop attack.

**Limit / inference:** Its strongest settings are per watermark category, and low-frequency changes may modify image identity. The seven schemes omit F5. **Agent inference:** a frequency-targeted generic arm is relevant but need not be the strongest informed attack if F5's residual gain is geometric rather than Fourier-localized.
