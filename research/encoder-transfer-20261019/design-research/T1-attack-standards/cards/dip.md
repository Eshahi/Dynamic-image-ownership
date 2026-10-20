# A Baseline Method for Removing Invisible Image Watermarks using Deep Image Prior

ID: `dip`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Hengyue Liang; Taihui Li; Ju Sun
Version/date: 2502.13998v2 [eess.IV] 02 Jul 2025. Venue: TMLR reviewed version linked from full text; inspected arXiv v2, exact acceptance date not reverified.
Primary: [https://arxiv.org/html/2502.13998v2](https://arxiv.org/html/2502.13998v2); [inspected full text](https://arxiv.org/html/2502.13998v2). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-dip.html`. SHA-256: `b40b04cb654d44b085633f858ce66df92b60b37a4d702ccbab17f662ce114213` (372418 bytes).
Inspected: Section3/Algorithm1; Section4/Table2; AppendixB Table6 cached compact3328-3425; AppendixC runtime; official repository root inspected, recursive tree API403 and folder web error.

## Mechanism and attacker access

Untrained skip CNN fits one watermarked image by MSE; select an intermediate reconstruction using target yes/no decoder queries. Its best-quality evaluation exhaustively searches hyperparameters and successful iterates.

## Models

Original DIP skip CNN; comparison DiffPure/Diffuser/Cheng2020VAE

## Strength / noise

Table6 grids: brightness/contrast .01-1 step.01 default.5; Gaussian sigma.01-1 step.01 default.1; JPEG1-100 step1 default50; BM3D sigma.1-5 step.05 default.1; DiffPure noise.1-1 step.1 default.1-.3; Diffuser inverse steps10-100 step10 default60; Cheng2020 quality1-6 default3; DIP iterations1-500 grid10

## Sampler / steps / optimizer

Adam; benchmark maximum500 iterations (Table6), not generic discussion of roughly1000. Successful-iterate/quality selection uses decoder feedback. Learning rate absent from inspected main method and AppendixB; official recursive repository tree returned403 and folder retrieval failed. Diffusion sampler N/A forDIP.

## Prompt / guidance

N/A forDIP

## Resolution

512x512

## Image counts and units

2,000 randomCOCO+2,000DiffDB;2,000generatedTree-Ring; clean qualityTable1 only100 sampled

## Metrics

Detection under gamma.55/.65/.75/.85;PSNR,SSIM,90th-percentilepixelerror

## Conditioned numerical results

Table2 COCO DwtDctSVD gamma.75: DIP35.85dB/.96/6.4 versusVAE33.47/.90/9.2; cleanTPR.99/FPR.01. Pool2,000; table masks methods failing >=90%evade, and exact successful-subset count is not printed

## Limits and unresolved conflicts

Quality-optimal output selection is oracle-assisted/query-dependent. Different gamma values imply different FPRs across methods. Do not describe this evaluation as query-free merely because CNN needs no target parameters.

## Consequence for this design

Preserve fixed query-free attack strength and report failures; DIP is a distinct follow-up threat, not a replacement control.
