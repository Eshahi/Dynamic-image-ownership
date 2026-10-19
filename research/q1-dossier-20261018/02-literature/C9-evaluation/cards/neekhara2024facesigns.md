# neekhara2024facesigns — V2 preprint; final journal evaluation V1

Paarth Neekhara, Shehzeen Hussain, Xinqiao Zhang, Ke Huang, Julian McAuley and Farinaz Koushanfar. *FaceSigns: Semi-fragile Watermarks for Media Authentication*. ACM TOMM20(11),337,2024; DOI[10.1145/3640466](https://doi.org/10.1145/3640466). Inspected predecessor [arXiv2204.01960v1](https://arxiv.org/html/2204.01960v1), §§3–5 and Tables1–2, accessed18 October2026. Final publisher text access failed; numerical equivalence to the 2024 revision is NOT asserted.

Existing face photographs: U-Net encoder/decoder plus discriminator jointly train128-bit recovery under benign transforms and fragility under facial tampering. Verification requires the expected secret/model; encryption is suggested, not a proved content-binding construction.

Preprint setup:1,000 CelebA test images; remaining images split80/20 training/validation,256². Semi-fragile clean PSNR36.08/SSIM.975; AUC.996 for distinguishing benign transforms from tested face swaps, with HiDDeN, StegaStamp and DCT comparisons. No diffusion-regeneration or competing-registry evaluation.

Evaluation norm: distinguish desired rejection after malicious edits from desired survival after regeneration; record image-level decisions separately from bit recovery and AUC. The published venue establishes topical fit, while this old preprint cannot certify current journal evaluation details.
