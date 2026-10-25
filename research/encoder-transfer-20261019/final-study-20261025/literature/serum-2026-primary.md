# SERUM (ICLR 2026): primary-source closure and scope correction

Research-only card, inspected 2026-10-25. This late author-source addition sits outside the WP6/E3 evidence package. It adds no baseline, changes no protocol, and authorizes no execution. No paper download was needed.

## Identity and inspected sources

**Title:** SERUM: Simple, Efficient, Robust, and Unifying Marking for Diffusion-based Image Generation. **Authors:** Jan Kociszewski, Hubert Jastrzębski, Tymoteusz Stępkowski, Filip Manijak, Krzysztof Rojek, Franziska Boenisch, Adam Dziedzic. The [official ICLR 2026 proceedings entry](https://proceedings.iclr.cc/paper_files/paper/2026/hash/7444ca5ef9b57c70fb2b91b90e9583a0-Abstract-Conference.html) independently establishes conference identity. [arXiv metadata](https://arxiv.org/abs/2603.13396) gives v1, 2026-03-11 14:20:10 UTC, and acceptance as an ICLR 2026 Poster. The author-hosted document has no separately verified revision date.

Inspected the 26-page [author PDF](https://adam-dziedzic.com/static/assets/papers/serum.pdf), particularly §3, §4.1–4.4, Tables 1–2 and Appendices C–G. The [proceedings PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/7444ca5ef9b57c70fb2b91b90e9583a0-Paper-Conference.pdf) returned the same extracted page/line structure; byte identity was not checked. The [authors' April 25 explanation](https://sprintml.com/blog/2026-04-25-serum/) supplies [OpenReview forum AiBUm6iKBf](https://openreview.net/forum?id=AiBUm6iKBf); direct forum/PDF access met a browser challenge. No reviews or decision text were inspected. Proceedings identity suffices; access retries stopped.

## Mechanism and compact numerical evidence

The [author explanation](https://sprintml.com/blog/2026-04-25-serum/) describes initial-noise watermark injection, an unchanged generator, and a trained external detector receiving image latents from the diffusion encoder. Detection avoids diffusion inversion. Transformation training uses an adaptive sampler. Thus SERUM is a watermarking method; classifying it as a watermark-removal algorithm would invert its purpose.

The following compact record comes from the [paper, §3–4 and Appendices C/E](https://adam-dziedzic.com/static/assets/papers/serum.pdf#page=4):

- Injection: η′=√(1−α)η+√α A′; A′ is fixed normalized Gaussian noise; α=.5.
- Models: SD1.4/2.0/2.1; training uses the evaluation generator. Test: 5,000 prompts, paired marked/unmarked, 10,000 images. Perturbation thresholds are computed separately.
- Table 2 TPR@1%FPR (%): VAE 99.88; Regen-12 99.72; Rinse-4×8 99.38; Regen-30 88.50; Rinse-2×25 90.76; CtrlRegen 99.64; I2V 58.20. Evaluation: 10,000 samples; I2V 2,000; attacks absent from detector training.
- VAE attack: Ballé factorized-prior quality1. Regen/Rinse: unconditional Guided Diffusion256, down/upscaling, DDIM50; Regen uses last12/30 updates; Rinse repeats8 updates four times or25 twice. CtrlRegen uses fresh noise and semantic/spatial guidance; I2V detects frame19 of Stable Video Diffusion.
- Appendix E compares transformed-image latent distances before/after inversion: 103.18→117.47, n=1,000 SD2.1 images.
- Checkpoint hashes, encoder-training independence, and a crossed independent-autoencoder removal experiment are not established by these descriptions.

Appendix G.2 also supplies a different, fixed-threshold check on real images: the threshold is frozen from clean synthetic images, and reported FPR is .24% on LAION-2B and .00% on COCO. Its text describes 5,000 randomly sampled images from those datasets. This evidence must be retained alongside the perturbation-specific ROC qualification; the paper does not use adaptive thresholds in every evaluation. Neither the observed zero nor these datasets certify rare-event or adversarial specificity. Appendix G.3 explicitly attributes the SD3.0 results to model-specific detector training.

## Interpretation for the present study

**Scope correction.** The same-image transformed-latent comparison is a diagnostic of inversion sensitivity, not an optimization objective for an attacker. A distance between representations does not identify which component carries a mark. It contains host variation as well as any mark response. Consequently, this diagnostic cannot establish a signed watermark-transport law or justify using latent distance as a removal certificate. The numerical increase also needs its own coordinate normalization and variability before being compared across systems; it should not become a universal amplification constant.

**Attacker access inference.** Regen/Rinse, as described, can consume the published image and public reconstruction machinery without a clean original, owner secret, target-reader gradient, or detector feedback. This is an inference about the stated transformations, not a verified execution audit. CtrlRegen similarly separates reconstruction initialization from the marked latent, but the content guidance still carries information about the input. Fresh Gaussian initialization alone therefore cannot prove that every watermark-relevant dependence has disappeared. No attack described here earns a stronger access label solely because it uses another model.

**Overlap with attack A.** Repeated reconstruction is already the organizing principle of Rinse. The dossier's SDXL→SD1.5 chain cannot claim novelty merely from performing two passes. Its defensible distinction is a fixed mixed-family composition and the associated source-paired, fidelity-constrained comparison. Different reconstruction families introduce more changes than encoder identity, so any observed improvement would remain a pipeline result. Pass-count matching does not automatically match computational work or image damage. A floor after the first pass must remain visible rather than being presented as additional two-pass success.

**Overlap with attack B.** Encoding into a public proxy latent is a shared primitive, but a primitive does not define an attack. B's decorrelation objective and bounded optimization are separate constructions. The transformed-image diagnostic provides no direct validation that reducing B's cosine removes the owner's signal. In particular, the proxy reference need not align with the target reader, and optimization can move host content while preserving a readable mark. B therefore retains its codec and fidelity-only controls and its possibility of honest failure; this card supplies no reason to alter the frozen objective.

**Evaluation limits.** A ROC operating point selected for a known perturbation answers a different question from deploying one previously frozen threshold against unknown attacks. A finite negative sample also cannot certify population FPR zero. Aggregate TPR is not a content-binding or ownership result. For this dossier, the useful citation is narrower: strong generative-attack robustness can coexist with a detector that encodes images but avoids diffusion inversion. That observation motivates examining the complete insertion/transport/readout chain; it does not show that F5 shares SERUM's mechanism or should inherit its performance. Likewise, evaluating several generators does not by itself demonstrate transfer of one fixed detector across independently trained encoders.

## BibTeX for integration

Additional root inspection of Appendix B.1–B.3 preserves its fixed-pattern Gaussian KL calculation and fixed-orthant comparison. The separate [distribution-fidelity note](../analysis/distribution-fidelity-boundary.md) explains why that valid input comparison does not alone order output KL, FID or same-source fidelity, and why fixed-secret and key-marginal laws differ. These are author derivations, not empirical counter-results or a criticism of the reported measured FID.

```bibtex
@inproceedings{kociszewski2026serum,
  title={{SERUM}: Simple, Efficient, Robust, and Unifying Marking for Diffusion-based Image Generation},
  author={Kociszewski, Jan and Jastrz{\k{e}}bski, Hubert and St{\k{e}}pkowski, Tymoteusz and Manijak, Filip and Rojek, Krzysztof and Boenisch, Franziska and Dziedzic, Adam},
  booktitle={The Fourteenth International Conference on Learning Representations},
  year={2026},
  url={https://openreview.net/forum?id=AiBUm6iKBf}
}
```

Author-blog BibTeX identity, cross-checked against proceedings authors/title; OpenReview content remains access-limited. No uninspected review claim is used.
