# PhotoGuard — V2 reused/refreshed

Salman et al., *Raising the Cost of Malicious AI-Powered Image Editing*, arXiv 2302.06588v1 (2023). [Primary](https://arxiv.org/html/2302.06588v1). Existing dossier card `C1-posthoc/cards/Salman2023PhotoGuard.md` retains metadata/cache. Inspected §3 encoder/diffusion attacks, §4 and Appendix A material, 2026-10-19.

The encoder attack moves pixels within an L-infinity constraint toward a chosen encoded target. The stronger method differentiates through diffusion. It evaluates editing disruption on SD1.5, not payload recovery; 60-edit evaluation and PGD details are retained in the existing card. Encoder-gradient exploitation therefore predates F5. It supplies no cross-encoder watermark-transfer guarantee. Public encoder access and differentiability are necessary for this attack, unlike a detector-query-free fixed regeneration benchmark. No models loaded or perturbations computed.
