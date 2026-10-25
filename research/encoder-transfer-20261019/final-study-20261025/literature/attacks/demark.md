# V2 card: Song et al. (2026)

- **ID / key:** `song2026demark`; **title:** *DeMark: A Query-Free Black-Box Attack on Deepfake Watermarking Defenses*.
- **Authors:** Wei Song, Zhenchang Xing, Liming Zhu, Yulei Sui, Jingling Xue. **Year / venue / version:** 2026, arXiv:2601.16473v1 (23 January 2026), preprint. **DOI:** unverified.
- **Canonical text:** https://arxiv.org/html/2601.16473v1. **Access:** 2026-10-25. **Artifact and SHA-256:** manifest ID `demark`.
- **Inspected:** §§IV-A–IV-B (threat and method), V-A–V-D/Tables II–IV. **Verification:** V2.

**Threat and method — direct evidence (§IV):** A black-box, query-free attacker can see watermarked images but not the watermark model or detector. DeMark trains a sparse encoder and reconstruction network, using an ℓ1 latent sparsity term and SSIM/LPIPS reconstruction losses; the hoped-for effect is discarding watermark-bearing latent components while preserving image structure. This is a learned removal model trained on generic images, not per-image regeneration.

**Checked experiment (§V):** §V-A states 50,000 OpenImages and 40,000 COCO images for training. Eight schemes include VINE-B and VINE-R. §V-B reports average bit accuracy falling from 100.0% to 64.7% and detection accuracy from 100.0% to 32.9% with the stated default α=10, β=0.1. These are pooled over its schemes and protocol; no F5 result is reported.

**Limit / inference:** Requires training data and a learned network. VINE-R's inclusion makes it relevant to the thesis control arm, but its pooled accuracy cannot predict the thesis's source-majority endpoint. **Agent inference:** a trained sparse-proxy attack is a plausible extension after the cheaper generic attacks, not a basis for causal explanation of SDXL transfer.
