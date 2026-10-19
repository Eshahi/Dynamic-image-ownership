# zhao2024provablyremovable — V2

Accessed 2026-10-18. Verification denotes primary method and evaluation/proof inspection, not reproduction.

**Metadata.** Xuandong Zhao, Kexun Zhang, Zihao Su, Saastha Vasan, Ilya Grishchenko, Christopher Kruegel, Giovanni Vigna, Yu-Xiang Wang and Lei Li. *Invisible Image Watermarks Are Provably Removable Using Generative AI*. NeurIPS 2024; arXiv 2306.01953v3, 2024-10-31. [Full text](https://arxiv.org/html/2306.01953); [metadata](https://arxiv.org/abs/2306.01953). Inspection: §§3–5, Appendices C and E. DOI not independently verified.

**Setting, mechanism, access.** Removal of invisible marks through embedding, Gaussian perturbation and reconstruction; the attacker need not query the watermark detector. Theory bounds detection after a locally Lipschitz encoder plus prescribed noise. Experiments use diffusion regeneration and learned compression.

**Evaluation.** 500 COCO photographs and 500 generated images; DwtDctSvd, RivaGAN, StegaStamp and SSL. Detection is evaluated at 1% FPR. Strength sweeps matter: stronger removal also changes quality. StegaStamp has a 96-bit payload; other payload lengths must be read per configuration rather than harmonized from inconsistent summaries.

**Limits.** The theorem is conditional on the representation/noise model. Appendix C.6 does not justify applying the same fixed-variance Gaussian bound directly to an arbitrary VAE. The empirical quality curves do not establish impossibility for every watermark or every registry-assisted verifier.

**Thesis implication.** State an operational distortion budget and detector side information before claiming survival or impossibility. F5's registry lies outside a claim about a reference-free detector unless explicitly modeled. This source cannot prove that the observed E2 limitation is inevitable.

