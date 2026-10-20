# ProxyEraseAgent: Blind Watermark Removal in the Wild

ID: `proxyerase`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Jun Yao; Chao Wang; Yupeng Qiu; Zehua Ma; Weiming Zhang; Bin Liu; Han Fang
Version/date: 2610.11290v1; 08 Oct 2026. Venue: Verified arXiv preprint version; final venue not verified.
Primary: [https://arxiv.org/abs/2610.11290v1](https://arxiv.org/abs/2610.11290v1); [inspected full text](https://arxiv.org/html/2610.11290v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-proxyerase.html`. SHA-256: `d915143174d5f943f4a8a8f2058af81501fa929a1f8a2bd6e2fe2d4550a23447` (225664 bytes).
Inspected: Section3;Section4/Table1-2;Appendix6.1-6.5.

## Mechanism and attacker access

Calibrated proxydecoder retrieval andPareto beamsearch;targetdecoderexcluded until finalevaluation;uses otherpublicencoders/decoders.

## Models

11posthoc systems;Cheng2020-anchor;UnMarker-inspiredfilters

## Strength / noise

VAEquality1-6;JPEG90-30;TPS.00025-.002;lowfrequencyoptimization50/100/200;baseline diffusionnoise0/5/10/20/40/60/80

## Sampler / steps / optimizer

Beamwidth3,depth4,top3proxies;LPIPSselection.05;diffusioncheckpoint/sampler absent fromAppendix6.4

## Prompt / guidance

N/Aforsearch operations;baseline regenerationprompt unreported

## Resolution

128x128afterembedding;someinternalmodels256 thenresized

## Image counts and units

100COCOimages each11systems=1100 correlated system-image cases

## Metrics

cASR:BER>=.1 andAlexNetLPIPS<=.05;notnative calibratedTPR

## Conditioned numerical results

Table2depth4 cASR94.82%,BER.3745,LPIPS.0421,PSNR29.46;depth1 83.91%. Table1 fixedRegenDiff17.0%,UnMarkerHL42.64%.

## Limits and unresolved conflicts

128resize can change watermarkstrength;10%BER success allows90%correctbits; noFPR/ecc equivalence.

## Consequence for this design

Document proxyadaptive threat separately; noautomaticsearch in fixedtransferstudy.
