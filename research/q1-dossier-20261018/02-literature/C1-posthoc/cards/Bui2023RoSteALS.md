# RoSteALS: Robust Steganography using Autoencoder Latent Space

- Citekey: `Bui2023RoSteALS`
- Authors: Tu Bui; Shruti Agarwal; Ning Yu; John Collomosse.
- Year / venue: 2023; CVPR Workshops 2023.
- Version: arXiv v1; CVPRW metadata.
- Primary source: [paper](https://arxiv.org/html/2304.03400v1); arXiv: 2304.03400; DOI: 10.1109/CVPRW59228.2023.00100.
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 3.1 and architecture description, 4.1–4.5 and limitations.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/rosteals.html`; SHA-256: `687ed6e8bb09968bfff2a3c200640c03ac02819a2656696720a426128c6de00a`.
- Setting: Post-hoc existing images; generative extensions separately discussed.
- Detector side information: Trained ResNet50 decoder; no original or inversion.
- Threat: Fourteen ImageNet-C style training distortions.

**Mechanism/payload.** A small learned secret encoder produces a content-independent latent offset; frozen VQGAN encoding/decoding carries it into the image. A learned image decoder recovers a default 100-bit message.

**Evidence.** Training uses 100,000 MIRFlickr images plus 1,000 validation images; evaluation includes CLIC (530), MetFace (1,336) and Stock1K (1,000). Sections 4.1–4.5 compare quality, corruption robustness and ablations. The frozen autoencoder's reconstruction imposes a fidelity ceiling. The inspected conventional-distortion suite does not establish diffusion-regeneration resistance.

**Access/limits.** Detector weights and message are required; no diffusion inversion is used. Generation extensions do not change the classification of the principal existing-image pipeline.

**Thesis inference.** Autoencoder-aware embedding is prior art, although a learned latent offset differs from optimizing input pixels through a frozen encoder. The introduction explicitly motivates a unique identifier for exact provenance-database search: pointer-plus-database alone cannot support novelty.

