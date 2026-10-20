# MarkCleaner : High-Fidelity Watermark Removal via Imperceptible Micro-Geometric Perturbation

ID: `markcleaner`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Xiaoxi Kong; Jieyu Yuan; Pengdi Chen; Yuanlin Zhang; Chongyi Li; Bin Li
Version/date: 2602.01513v1 [eess.IV] 02 Feb 2026. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2602.01513v1](https://arxiv.org/abs/2602.01513v1); [inspected full text](https://arxiv.org/html/2602.01513v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-markcleaner.html`. SHA-256: `3979395bbc8258cbe805972fa79196c8dc135d888ba998e27d41949bd19f4f2b` (397247 bytes).
Inspected: Method cached122-196; evaluation setup443-471; Figure2 diagnostic; mainTable1 cached197-442 and AppendixG.1 cached976-982.

## Mechanism and attacker access

Trained U-Net plus2D Gaussian renderer makes small spatial warps, with frequency/spatial targets and DINO alignment; a learned geometric attack rather than generic diffusion.

## Models

Learned U-Net/2D Gaussian renderer; SD2.1 for generated images

## Strength / noise

Diagnostic7-pixel translation and5-degree rotation; learned fields have distinct settings

## Sampler / steps / optimizer

GenerationDDIM50,CFG7.5; attack diffusion sampler N/A

## Prompt / guidance

Attack promptN/A; source captions used for generation

## Resolution

512x512

## Image counts and units

5,000 COCO training;1,000 paired DiffusionDB test images

## Metrics

TPR@1%FPR; PSNR,SSIM,LPIPS and runtime

## Conditioned numerical results

Table1 learned MarkCleaner mTPR.014/mDeltaA.094; VINE TPR.063/ACC.554; TreeRing TPR.001/ACC.795, RingID.003/.802, HSQR.022/.766 at1%FPR on1,000 paired DiffusionDB images. NFPA row mTPR.061/mDeltaA.154. Figure2 geometry diagnostic is separate, not main result.

## Limits and unresolved conflicts

Section5.1 says15 watermark methods but Table1 has12 columns; count conflict unreconciled. Low calibrated TPR coexists with TreeRing ACC.795/RingID.802/HSQR.766, so not all bit evidence is randomized. AppendixG.1 NFPA reimplementation25 purification steps differs from NFPA original10; do not attribute baseline differences to attack principle alone. Runtime not transferable.

## Consequence for this design

Geometric sensitivity warrants fixed resize diagnostics, not an outcome-driven attack search.
