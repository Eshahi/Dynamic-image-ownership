# Evidence synthesis

This report preserves reported evidence; source hashes establish identity, not scientific truth.

- B2-ZODIAC-EXISTING-LATENT: ZoDiac starts from an existing image and optimizes a watermarked diffusion latent with a reconstruction objective. [zodiac-neurips2024; supporting; direct-evidence; confidence high]. Limitations: Method described by the authors; not independently reproduced.

- B2-ZODIAC-INVERSION: The ZoDiac detector uses DDIM inversion, latent Fourier transformation and a statistical test rather than image-domain DCT extraction. [zodiac-neurips2024; supporting; direct-evidence; confidence high]. Limitations: This describes the paper method, not the precise behavior of the published code.

- B2-ZODIAC-DOMAINS: The authors evaluate 500 sampled images each from MS-COCO, DiffusionDB and WikiArt. [zodiac-neurips2024; supporting; direct-evidence; confidence high]. Limitations: Dataset version and image identities were not verified here.

- B2-NOVELTY-BOUND: Existing-image latent embedding and two-domain real/generated evaluation cannot individually be claimed as unique to the thesis candidate because ZoDiac already describes both. [zodiac-neurips2024; contradicting; agent-inference; confidence high]. Limitations: This narrows two novelty claims; it does not establish or refute originality of the exact dual-signature image-DCT combination.
