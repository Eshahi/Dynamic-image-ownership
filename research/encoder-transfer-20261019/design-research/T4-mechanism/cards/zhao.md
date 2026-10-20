# T4-01: Invisible Image Watermarks Are Provably Removable Using Generative AI

- **Primary source:** [2306.01953v3](https://arxiv.org/html/2306.01953v3); authors: Xuandong Zhao; Kexun Zhang; Zihao Su; Saastha Vasan; Ilya Grishchenko; Christopher Kruegel; Giovanni Vigna; Yu-Xiang Wang; Lei Li.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. Prior T4 source explicitly rechecked for this mechanism topic; the body records the new assumption/endpoint checks.
- **Method locators:** cached `zhao.txt` lines 136-220; Appendix C.6-C.8, 624-635. **Evaluation locators:** 221-240; Figure 2. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** arXiv perpetual non-exclusive, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/zhao.html`. **HTML SHA-256:** `41861c3d032d039a001feb23c58c8a322b0e38c27ad70b382acfc84d96423582`. Text hash and byte counts are in `source-manifest.json`.

## Claim, mechanism and theorem boundary

Theorem 4.3 bounds detection after a common postprocessor applied to an embedding plus **equal, input-independent isotropic Gaussian noise**. For a fixed clean/marked pair, embedding displacement at most L times pixel L2 budget Delta implies FNR >= Phi(Phi^-1(1-FPR) - L Delta / sigma). L is local and watermark-specific. A small pixel budget alone is insufficient if the encoder amplifies the chosen direction. A large ratio weakens the bound; it does not prove any detector succeeds. The theorem concerns distinguishability of marked versus unmarked channels, not recovery of an arbitrary bit string or an ownership credential.

Theorem 4.4 transfers an assumed denoising-quality probability on an unmarked image to its marked counterpart with a changed failure probability. It is not a universal PSNR/LPIPS guarantee at any diffusion strength. Remark C.6 explicitly says the theorem does not directly apply to a VAE with input-dependent posterior noise. That qualification matters for R0/R1; deterministic D1 has no additive-noise certificate at all.

## Evaluation actually inspected

The evaluation uses 500 MS-COCO images and 500 SD2.1-generated images, four post-hoc methods (DwtDctSvd, RivaGAN, StegaStamp, SSL), detection at 1% FPR, and SD2.1/PNDM regeneration over several noise levels. Figure 2 compares a theoretical bound and observed detector error on 500 COCO images. This directly supports those channels and budgets; it is not an experiment on F5, SDXL, or independently trained encoders. Appendix C discusses quantization, low-pass projection and learned embeddings as distinct compression mechanisms.

## T4 use and falsifiability

F5 was designed to increase SD1.5 latent displacement per pixel distortion. The independent-encoder question is whether a different encoder preserves that displacement and whether the regenerated image retains reader-aligned evidence. D1, X1 and R1 separate some stages; none alone identifies a Jacobian. Low C after R1 with high semantic.read but failed content_match would undermine a carrier-erasure interpretation even though overall verification failed. Strong C under an independent channel would weaken a strict SD1.5-only story without contradicting the theorem.

No numerical certificate is claimed for the frozen pipeline. Latent scaling, RGB normalization, posterior covariance and every image-dependent conditioning path must be accounted for before inserting measurements into the bound. No such measurements occurred in Stage1b.
