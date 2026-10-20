# On the Robustness of Watermarking for Autoregressive Image Generation

ID: `arrobust`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Andreas Müller; Denis Lukovnikov; Shingo Kodama; Minh Pham; Anubhav Jain; Jonathan Petit; Niv Cohen; Asja Fischer
Version/date: 2604.11720v1; 13 Apr 2026. Venue: Verified arXiv preprint version; final venue not verified.
Primary: [https://arxiv.org/abs/2604.11720v1](https://arxiv.org/abs/2604.11720v1); [inspected full text](https://arxiv.org/html/2604.11720v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-arrobust.html`. SHA-256: `905907ffe4a9b4eba0ba1dbe537c6026fba0e5457cf83de6a2d6d04f7dafe94e` (1010686 bytes).
Inspected: Section3; Section4/Table1; Appendix0.A.1-0.A.2/Table4 web322-418.

## Mechanism and attacker access

AR watermark benchmark with VQ token replacement, latent optimization and frequency forgery; white/grey/black model access separated.

## Models

LlamaGenGPT-B/L; RAR-XL; Taming; Anole; Infinity2B; baseline SD2.1

## Strength / noise

Regen60 steps; rinse3 rounds; CtrlRegen+strength.3 guidance2; LatentOpt Linf8/255

## Sampler / steps / optimizer

LatentOpt Adam lr.001,max300,verify every10; target-best iterate selection; Regen/Rinse60 per source wording, precise sampler not named

## Prompt / guidance

ImageNet classes or COCO captions for generation; regeneration prompt not specified in Appendix0.A.2

## Resolution

256/384/512/1024 depending generator

## Image counts and units

100 attacked images per model/watermark from1000 generated per setup;100COCO forgery covers

## Metrics

TPR@1%FPR; medianp;PSNR;LPIPS

## Conditioned numerical results

Table1 aggregate black-box Rinse TPR IndexMark.03/WMAR.02/ClusterMark.29 vsRegen.52/.36/.85; rinsePSNR20.14/21.11/19.95.

## Limits and unresolved conflicts

AR architecture adjacent; model aggregation is not independent trial count; target-best optimization iterate has oracle access despite proxy-model category.

## Consequence for this design

Include benchmark; do not extend AR conclusions to F5 or equate3-round60 with.1+.1.
