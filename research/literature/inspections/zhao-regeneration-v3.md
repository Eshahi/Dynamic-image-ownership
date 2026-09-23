# Regeneration source inspection

Inspected 2026-09-23 UTC by /root: https://arxiv.org/html/2306.01953v3
Metadata: https://arxiv.org/abs/2306.01953
Title: Invisible Image Watermarks Are Provably Removable Using Generative AI.
Authors: Xuandong Zhao; Kexun Zhang; Zihao Su; Saastha Vasan; Ilya Grishchenko; Christopher Kruegel; Giovanni Vigna; Yu-Xiang Wang; Lei Li.
First submission 2023; inspected v3 dated 2024-10-31. DOI 10.48550/arXiv.2306.01953.

Section 2.2: attacker lacks detector queries. Algorithm 1 adds latent noise then reconstructs. Theorem 4.3 assumes bounded L2 invisibility and a local embedding bound; utility in Theorem 4.4 is conditional on denoising quality. Appendix E reports Tree-Ring resilience with changed image appearance and prompt/caption-based generation.

Targeted reading only (2.2, 3, theorem statements 4.3/4.4, E); proofs and code unverified. Neither universal removal nor the thesis's latent-over-pixel hypothesis follows. Notes hash protects this observer record, not remote text. An initial attempted v4 URL returned 404; actual revision is v3.
