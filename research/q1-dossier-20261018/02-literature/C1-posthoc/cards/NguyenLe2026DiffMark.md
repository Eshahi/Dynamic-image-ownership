# Transferable Multi-Bit Watermarking Across Frozen Diffusion Models via Latent Consistency Bridges

- Citekey: `NguyenLe2026DiffMark`
- Authors: Hong-Hanh Nguyen-Le; Van-Tuan Tran; Thuc D. Nguyen; Nhien-An Le-Khac.
- Year / venue: 2026; TAIGR workshop at ICML 2026 (arXiv acceptance comment).
- Version: v2 (2026-06-02).
- Primary source: [paper](https://arxiv.org/html/2603.20304v2); arXiv: 2603.20304; DOI: 10.48550/arXiv.2603.20304.
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 3.1–3.3, 4.1–4.7; Tables 1–2; v2 latency Section 4.5.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/diffmark-v2.html`; SHA-256: `34905b0e01d56b1370bbbd8eb1f4fa9b8baa1567a97f5a70ed7a510c74c6d3a5`.
- Setting: Generation-time learned perturbation during diffusion sampling.
- Detector side information: VAE encoder and learned decoder; no inversion or original.
- Threat: Regeneration; conventional distortions; grey-box adversarial VAE attack.

**Mechanism/payload.** A learned latent perturbation is repeatedly injected during frozen diffusion sampling. A four-step latent-consistency bridge supplies gradients; full DDIM outputs supervise decoding. Payload: 64 bits.

**Evidence.** Three prompt collections contain 1,000 samples each: COCO2017, DiffusionDB and DALL·E 3. The main DiffusionDB clean condition reports TPR 1.0 at 0.1% FPR and bit accuracy 0.9381. Crucially, Section 4.7 reports zero detection scores for rotation, blur and resized crop, despite broader robustness language elsewhere. Latency includes VAE encoding; it is not a DCT-only detector.

**Access/limits.** Grey-box AdvKL-VAE8 targets the encoder. Generated-image quality is not fidelity to a pre-existing photograph. No registry-based content binding is evaluated.

**Version/provenance.** v1 was first read, then v2 was retrieved and method/experiments re-read. The HTML title block lists four authors; an abstract-page rendering abbreviates inconsistently. Bibliography follows the inspected v2 paper title block. The current arXiv comment reports acceptance at the TAIGR workshop at ICML 2026; this is not a main-conference acceptance.

**Thesis inference.** Treat this as a generation-time boundary, and preserve the reported attack failures rather than citing the abstract as universal resilience.

