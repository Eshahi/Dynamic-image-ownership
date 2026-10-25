# SEAL — V2 primary-source card

Source: Kasra Arabi, R. Teal Witter, Chinmay Hegde and Niv Cohen, *SEAL: Semantic Aware Image Watermarking*, arXiv:2503.12172v4, 18 May 2026. [Inspected version](https://arxiv.org/html/2503.12172v4). Inspected 25 October 2026. Artifact/hash: manifest key `seal`.

**Direct evidence — mechanism (§3, Algorithm 1).** A proxy image is captioned and semantically embedded. Patchwise SimHash values and a secret salt derive seeds for Gaussian initial noise, from which the final image is generated. Detection captions/embeds the suspect and compares its semantics with inverted noise patches. Required information includes caption/embedding models, private salt and diffusion inversion, without an enrolled original image.

**Direct evidence — experiments (§4).** Table 1 reports edit-detection AUC .551 for SEAL and .982 with the spatial test under Cat Attack. Table 2 reports .708 AUC against private-model reprompt forgery; the tested initial-noise comparators give .000. Appendix §13.3/Table 6 reports 98% watermark detection accuracy under the cited regeneration attack. Transformation-averaged AUC is .896 (§4).

**Limits / transfer.** Lemma 3.3 is conditional on semantic patch-distance separation (Assumption 3.1). Section 5 acknowledges stronger forgery routes. No controlled independently trained autoencoder transfer experiment is established by the inspected sections.

**Agent inference for F5.** Semantic binding is an existing research direction, with measurable residual failure. A registry-based content check changes detector information and must be compared separately from SEAL's regenerated semantic evidence.
