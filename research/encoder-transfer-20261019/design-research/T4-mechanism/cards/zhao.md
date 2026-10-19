# Zhao et al. — V2 refresh

*Invisible Image Watermarks Are Provably Removable Using Generative AI*, arXiv 2306.01953v3, 2024-10-31. [Primary](https://arxiv.org/html/2306.01953v3). Reuses dossier `C2-removal/cards/zhao2024provablyremovable.md`. Inspected 2026-10-19: §§3–5, Theorem 4.3, Appendices A/C/D.

Gaussian corruption after an embedding restricts attainable FPR/FNR through embedding separation divided by noise standard deviation. The local constant is watermark-and-source-specific. Shared covariance matters; native input-dependent VAE posterior variance is an explicit caveat. Large encoder sensitivity does not guarantee survival. The experiment uses 500 COCO and 500 generated images, four pixel-mark methods and 1% FPR. F5 is absent.

New correction: standardizing N(μ,σ²I) divides separation by σ, matching Theorem 4.3; some displayed Appendix D equations contain inconsistent σ². This does not justify reinterpreting the theorem. Artifact and SHA256: source-manifest.json. No new reproduction.
