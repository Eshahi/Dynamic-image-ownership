# Gaussian Shading — V2 primary-source card

Source: Zijin Yang, Kai Zeng, Kejiang Chen, Han Fang, Weiming Zhang and Nenghai Yu, *Gaussian Shading: Provable Performance-Lossless Image Watermarking for Diffusion Models*, arXiv:2404.04956v2, 27 April 2024. [Inspected version](https://arxiv.org/html/2404.04956v2). Inspected 25 October 2026. Artifact/hash: manifest key `gaussian-shading`.

**Direct evidence — mechanism (§3).** Repetition-coded message bits are randomized with ChaCha20, then mapped into Gaussian quantile bins to sample the initial diffusion noise. The distribution argument concerns randomized sampling. Detection requires the generator's encoder/denoiser, DDIM inversion, cryptographic key/nonce and message comparison or user mapping; majority decoding handles repeated bits.

**Direct evidence — experiments (§4, Table 1).** Under the stated adversarial transformations, SD1.4/2.0/2.1 give TPR .997/.998/.996 at the modeled FPR of 10^-6; bit accuracy is .9753/.9749/.9724. The reported setting carries 256 bits. Figure 7 studies neural compression and manipulated latent signs. Section 4.5 acknowledges reprompting-based forgery when the recovered latent is reused.

**Limits / transfer.** Very small FPR is an analytic model claim, not a million-negative empirical calibration. Multiple generator results are not a controlled frozen-writer test under independently trained regeneration autoencoders. Sampling distribution preservation alone does not prove content binding or adaptive forgery resistance.

**Agent inference for F5.** This provides a useful distinction between message recovery and semantic ownership. Its initial-noise mechanism and inversion-dependent detector differ from F5.
