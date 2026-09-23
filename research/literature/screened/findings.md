# Evidence synthesis

This report preserves reported evidence. Hashes identify local observer records, not remote paper authenticity or scientific truth. No experiment or proof was reproduced.

- B1-SEAL-METHOD: SEAL v4 uses caption embeddings, SimHash and inverse-diffusion detection. [seal-v4; supporting; direct-evidence; confidence high]. Limitations: Only method description checked; no implementation execution.

- B1-DCT-BRIDGE: The inspected SEAL v4 detector does not establish the thesis's latent-to-image-DCT bridge. [seal-v4; supporting; agent-inference; confidence high]. Limitations: This inspected mechanism does not establish that bridge; it does not prove infeasibility.

- B1-WU-METHOD: The abstract describes semiblind DWT-SVD watermarking with chaotic maps. [wu2024; supporting; direct-evidence; confidence high]. Limitations: Description only; reported robustness not independently verified.

- B1-MAREEN-METHOD: The abstract describes HiDDeN-based neural watermark encoding and decoding with geometric noise layers. [mareen2024; supporting; direct-evidence; confidence high]. Limitations: Description only; reported robustness not independently verified.

- B1-DASGUPTA-METHOD: The preprint abstract describes cross-attention embedding and invariant-domain learning. [dasgupta2023; supporting; direct-evidence; confidence high]. Limitations: Description only; reported robustness not independently verified.

- B1-INVISMARK-DECODER: InvisMark uses a trained ConvNeXT-base decoder. [invismark-v2; supporting; direct-evidence; confidence high]. Limitations: Source-specific description, not reproduced performance or general security guarantee.

- B1-INVISMARK-DATA: InvisMark evaluates DIV2K; this qualifies but does not refute the proposal's concern about comprehensive real-image evaluation. [invismark-v2; supporting; agent-inference; confidence high]. Limitations: Source-specific description, not reproduced performance or general security guarantee.

- B1-INVISMARK-FORGERY: Authors report residual-transfer forgery under public encoder access. [invismark-v2; supporting; author-interpretation; confidence high]. Limitations: Source-specific description, not reproduced performance or general security guarantee.

- B1-PROXY-FORGERY: Imprinting and reprompting use a proxy diffusion model and a reference watermarked image. [muller-forgery-v1; supporting; direct-evidence; confidence high]. Limitations: Source-specific description, not reproduced performance or general security guarantee.

- B1-OPERATING-POINTS: Table 1 is not automatically a matched-FPR comparison. [muller-forgery-v1; supporting; agent-inference; confidence high]. Limitations: Source-specific description, not reproduced performance or general security guarantee.

- B1-REGEN-METHOD: The attack noises an embedding and reconstructs without detector queries. [zhao-regeneration-v3; supporting; direct-evidence; confidence high]. Limitations: Conditional source-specific evidence; not a reproduced thesis result.

- B1-REGEN-BOUND: Removal and utility guarantees have explicit perturbation, embedding and denoising conditions. [zhao-regeneration-v3; supporting; direct-evidence; confidence high]. Limitations: Conditional source-specific evidence; not a reproduced thesis result.

- B1-REGEN-DEFENSE: Reported Tree-Ring resilience does not establish the thesis's matched-quality latent advantage. [zhao-regeneration-v3; supporting; agent-inference; confidence high]. Limitations: Conditional source-specific evidence; not a reproduced thesis result.

- B1-FORGERY-DEFENSE: Geometric pre-verification offers a conditional defense, not universal forgery immunity. [lee-geometric-v1; supporting; author-interpretation; confidence medium]. Limitations: No reproduction or proof audit; finite-dimensional overlap remains possible.
