# RingID: Rethinking Tree-Ring Watermarking for Enhanced Multi-Key Identification

Primary source: https://arxiv.org/html/2404.14055v2

Inspected: Sec.4.2-4.4; Sec.5; Sec.6.1/Table2. Full-text artifact/checksum in paper JSON and inventory.

Combines discretized concentric rings on latent channel3 with noise-pattern watermark on channel0; spatial shift, centered real-conjugate-symmetric imprinting and rounder drawing improve rotation. DDIM inversion50 and candidate-key channel-normalized minimum L1 matching identify keys. Detector requires diffusion model and candidate pattern bank. Table2 with2048 keys: RingID clean1.000, rotation .860, crop/scale .080, average .819; Tree-Ring clean .200, average .066. Sec4 finds discarding imaginary FFT component creates a distribution shift aiding presence verification but not key identification.

Limitations: Severe crop/scale identification failure remains. Larger key spaces reduce robustness/quality. No content-bound identity or image-only DCT extraction.
