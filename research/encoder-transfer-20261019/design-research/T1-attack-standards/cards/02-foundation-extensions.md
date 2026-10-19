# Foundation and controlled-removal extensions

Inspected 2026-10-19; V2 method/evaluation inspection, not replication. Full setting matrix and source hashes accompany this file.

## Zhao et al.

Extends [existing card](../../../../q1-dossier-20261018/02-literature/C2-removal/cards/zhao2024provablyremovable.md). [2306.01953v3](https://arxiv.org/html/2306.01953v3), §§3–5 and Appendix C.6: encoding, Gaussian perturbation and reconstruction; the bound is conditional on representation/noise assumptions, not a proof about arbitrary registry verification. §5 uses SD2.1 with PNDM and times 10/30/50/100/150/200, corresponding reported noise standard deviations .10/.17/.23/.34/.46/.57. Payload settings name 32-bit SSL, whereas the evaluation paragraph also mentions a 48-bit threshold: retain this internal ambiguity rather than harmonizing silently. Figures 4/7 are curves; no point was digitized.

## CtrlRegen / CtrlRegen+

Extends [existing card](../../../../q1-dossier-20261018/02-literature/C2-removal/cards/liu2025ctrlregen.md). [2410.05470v2](https://arxiv.org/html/2410.05470v2), §3, §4/Table 1, Appendix A. DINOv2-giant semantics plus Canny spatial control condition frozen SD1.5; text is empty. CtrlRegen starts from clean random noise; plus-version starts from a noised suspect latent. This requires trained adapters, not merely a new sampler. Table 1 StegaStamp TPR@1%FPR is .99 Regen, .94 Rinse, .01 CtrlRegen; respective PSNR 22.34/21.31/19.10 dB. Strong removal does not preserve exact identity by implication.

## UnMarker

Extends [existing card](../../../../q1-dossier-20261018/02-literature/C2-removal/cards/kassis2025unmarker.md). [2405.08363v2](https://arxiv.org/html/2405.08363v2), §§IV–VI, Tables I–III, Appendix D. Query-free high/low-frequency optimization and filtering plus cropping; no generative checkpoint or prompt. Table IIIb reports complete-attack detection 43% StegaStamp (LPIPS .08), 40% Tree-Ring (LPIPS .10). Different detector calibrations prevent direct comparison to a common 1e-4 bit-null operating point. This is an active spectral/geometric threat, not an independent-encoder regeneration test. Keep the prior final-version caveat.

## DiffPure

New focused card: [2205.07460v1](https://arxiv.org/html/2205.07460v1), §3.1–3.2, §5.1, Tables 1/3/14 and Appendix B.1/C.2. Add Gaussian forward noise, then reverse-time SDE purification; Euler–Maruyama dt=.001. Models: Score-SDE CIFAR10, unconditional Guided Diffusion 256 for ImageNet, SDEdit DDPM CelebA-HQ. Times .1 (CIFAR10) and .15 (ImageNet); typically 512 attacked samples. It reports classifier standard/robust accuracy under adaptive attacks, not watermark survival. There is no original DiffPure watermark TPR to import. A pixel-space DiffPure-style arm would test a valuable different mechanism, but resizing 512→256 and model-domain bias must be controlled and costed separately.
