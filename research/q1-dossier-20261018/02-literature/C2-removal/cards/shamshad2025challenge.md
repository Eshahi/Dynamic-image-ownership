# shamshad2025challenge — V2

Accessed 2026-10-18. Verification denotes primary method and evaluation/proof inspection, not reproduction.

**Metadata.** Fahad Shamshad, Tameem Bakr, Yahia Shaaban, Noor Hussein, Karthik Nandakumar and Nils Lukas. *First-Place Solution to NeurIPS 2024 Invisible Watermark Removal Challenge*. arXiv 2508.21072v1, 2025-08-28. [Full text](https://arxiv.org/html/2508.21072v1). This is a challenge-solution preprint, not a verified NeurIPS main-track paper. Inspection: §§3.1–3.2 and Tables 1–4.

**Mechanism/access.** The beige-box attack fine-tunes a VAE on opposite-payload pairs, then applies per-image optimization and color/contrast adjustments; Tree-Ring also uses a pixel shift. Black-box attacks use artifact-based grouping and caption-conditioned regeneration. The competition permits five leaderboard queries per day.

**Evaluation.** 300 images per track, with 150 StegaStamp and 150 Tree-Ring images in beige-box. Reported detection rates are .043 (black-box) and .037 (beige-box) at target .1% FPR. The StegaStamp-specific quality row reports PSNR 28.061 dB, SSIM .823 and LPIPS .078.

**Limits.** Track-wide detection and a method-specific quality row are not one joint operating point. Feedback, training pairs and task adaptation differ from a frozen blind attacker.

**Thesis implication.** Known-encoder adaptive removal belongs in the future gap plan. This source does not substantiate a generic robustified-encoder attacker, nor justify importing its leaderboard rate as a matched F5 baseline.

