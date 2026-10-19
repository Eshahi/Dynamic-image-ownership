# TrustMark: Universal Watermarking for Arbitrary Resolution Images

- Citekey: `Bui2023TrustMark`
- Authors: Tu Bui; Shruti Agarwal; John Collomosse.
- Year / venue: 2023; arXiv preprint; revised title published ICCV 2025.
- Version: v1 (2023-11-30); ICCV 2025 metadata and method partially refreshed.
- Primary source: [paper](https://arxiv.org/html/2311.18297v1); arXiv: 2311.18297; DOI: not verified for this inspected version (omitted from BibTeX).
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: v1 Sections 3.1–3.3, 4.1–4.6; 2025 accepted manuscript pp. 1–3 (PDF pp. 2–4).
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/trustmark.html`; SHA-256: `2002a7b13dafa321aa36270b94c00e2bfcb2fd28228c6ab9375f57ee13faae93`.
- Setting: Post-hoc arbitrary-resolution photographs or generated images.
- Detector side information: Public trained decoder; no original, secret key or diffusion inversion.
- Threat: Conventional perturbations; removal and re-watermarking.

**Mechanism/payload.** MUNIT-based image/message embedder, multiple 1×1 post-processing layers, ResNet extractor and spatial/frequency/perceptual objectives; scaled residuals extend fixed-resolution inference. Default message: 100 bits.

**Evidence (v1).** Training uses MIRFlickr100k with 1,000 validation images; evaluation includes CLIC, MetFace and 900 DIV2K training/validation images. Sections 4.1–4.6 study fidelity, common corruptions, resolution, removal and white-box iterative gradient attacks. These tests do not establish general diffusion-editing survival.

**Version limitation.** The final paper is *TrustMark: Robust Watermarking and Watermark Removal for Arbitrary Resolution Images*, ICCV 2025, pp. 18629–18639, DOI 10.1109/ICCV51701.2025.01731. Its accepted manuscript introduction and method were opened, but remaining experiment-page retrieval timed out. V2 here applies to inspected v1, not an asserted full final-version audit; final results are not transcribed.

**Thesis inference.** Public provenance identifiers and resolution scaling are prior art. ReMark's authorized removal use case differs from adversarial ownership verification; a trusted registry still needs independent content binding.

