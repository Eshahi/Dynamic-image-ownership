# Pixel Seal: Adversarial-only training for invisible image and video watermarking

- Citekey: `Soucek2025PixelSeal`
- Authors: Tomáš Souček; Pierre Fernandez; Hady Elsahar; Sylvestre-Alvise Rebuffi; Valeriu Lacatusu; Tuan Tran; Tom Sander; Alexandre Mourachko.
- Year / venue: 2025; arXiv preprint.
- Version: v1 (2025-12-18).
- Primary source: [paper](https://arxiv.org/html/2512.16874v1); arXiv: 2512.16874; DOI: 10.48550/arXiv.2512.16874.
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 3.1, 4.1–4.4, 5.1–5.3; Figure 1.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/pixelseal.html`; SHA-256: `cb6d43ca864a9c6a73e27fa1d7e0f1d97e0e23bc712e7d7a9f19d33de1ea7554`.
- Setting: Post-hoc images and video frames.
- Detector side information: Learned ConvNeXt-v2-tiny decoder; no original or inversion.
- Threat: Conventional transformations and combined image degradations.

**Mechanism/payload.** A U-Net embedder and ConvNeXt-v2-tiny extractor are trained using adversarial and message losses without MSE/LPIPS objectives. Three-stage training, local JND attenuation and simulated high-resolution inference manage quality. Declared payload: 256 bits.

**Evidence.** Training uses SA-1B and 600,000 steps. Image evaluation includes 1,000 Meta AI images at 1280×1280 and 100 real SA-1B images; separate video experiments are outside this cluster's focus. Figure 1 illustrates combined brightness 0.5, 50% crop and JPEG quality 40. No diffusion-regeneration result was established in the inspected sections, so ordinary corruption resilience is not promoted to T3 evidence.

**Access/limits.** A learned perceptual/JND regressor relies on internal user-study data. Uniform decoded-bit null assumptions used for p-values require scrutiny when transferred to low-FPR registry attribution.

**Thesis inference.** High capacity and perceptual quality are not novel aims by themselves. This is a useful current fidelity/throughput comparator, with an explicit gap for matched regeneration and adversarial transfer evaluation.

