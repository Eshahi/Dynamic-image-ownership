# GROW: Watermark Generation with Progressive Guidance for Diffusion Models

- Citekey: `Luo2026GROW`
- Authors: Pengcheng Luo; Zexi Jia; Yijia Zhong; Jinchao Zhang; Jie Zhou.
- Year / venue: 2026; CVPR 2026.
- Version: CVPR 2026 published PDF.
- Primary source: [paper](https://openaccess.thecvf.com/content/CVPR2026/html/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.html); arXiv: not used; DOI: not verified for this inspected version (omitted from BibTeX).
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 3–4; 5.1–5.5; Tables 1–3 (retained final-paper text).
- Artifact: `research/literature/m1-primary-extension/grow-cvpr2026.pdf`; SHA-256: `484969c867bf2b879aa675ca1eec6de4093d10f7225547c301d0ee32bede4fce`.
- Setting: Generation-time diffusion sampling; not post-hoc photo preservation.
- Detector side information: VAE encoder, keyed DCT mask and bit voting; no diffusion inversion.
- Threat: Distortions and diffusion regeneration of generated images.

**Mechanism/payload.** Gradient guidance acts on mid-band DCT coefficients of predicted clean latents during sampling. Extraction VAE-encodes the image and votes coefficient signs. The default experiment repeats a 16-bit message.

**Evidence.** Evaluation generates 1,000 images per prompt dataset, including COCO and SD prompts, principally with SD2.1-base and additional SD1.5/SDXL settings. Table 1's COCO result reports 0.95 message accuracy under DiffPure, conditional on its attack and generation setup. The reported 0.24-second extraction on Tesla T4 includes VAE encoding.

**Access/limits.** The sampler is modified during generation; there is no fidelity-to-an-existing-photograph requirement. The detector is inversion-free but is not DCT-only or model-free. A message does not bind itself to a unique content instance.

**Thesis inference.** Do not claim first inversion-free VAE/frequency decoding. GROW is a boundary comparison, not a matched post-hoc baseline.

**Provenance.** Retained CVPR primary PDF/text, freshly read this session; official CVF metadata refreshed. Existing downloaded artifact reused without executing its associated code.

