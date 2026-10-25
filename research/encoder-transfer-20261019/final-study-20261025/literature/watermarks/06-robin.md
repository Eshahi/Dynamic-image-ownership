# ROBIN — V2 primary-source card

Source: Huayang Huang, Yu Wu and Qian Wang, *ROBIN: Robust and Invisible Watermarks for Diffusion Models with Adversarial Optimization*, arXiv:2411.03862v2, 3 April 2025. [Inspected version](https://arxiv.org/html/2411.03862v2). Inspected 25 October 2026. Artifact/hash: manifest key `robin`.

**Direct evidence — mechanism (§3).** ROBIN inserts a Fourier watermark into an intermediate diffusion state after semantic structure emerges. It optimizes watermark strength and a hiding prompt. Detection inverts with an empty prompt to the insertion timestep, using the generating model and watermark pattern. It is therefore intermediate-state generative watermarking, not initial-noise-only sampling or a standalone image extractor.

**Direct evidence — experiments (§4).** Evaluation includes SDv2 latent diffusion and ImageNet pixel diffusion; verification uses 1,000 positive and 1,000 negative samples. Appendix C.2, Table 7 reports ROBIN AUC .998 under Bmshj2018, .999 under Cheng2020 and .997 under diffusion reconstruction; corresponding Tree-Ring values are .992/.993/.996. Other experiments examine six common transformations and generation quality.

**Limits / transfer.** Learned compression and diffusion reconstruction are tested, but the inspected experiments do not isolate a frozen writer's transfer across independently trained SDXL/FLUX autoencoders. Prompt optimization and insertion timestep are additional method dependencies (§3.4).

**Agent inference for F5.** A useful reminder that robustness may follow where along generation the signal enters, rather than a single latent/image dichotomy. Its inverse-model detector must be declared in comparisons.
