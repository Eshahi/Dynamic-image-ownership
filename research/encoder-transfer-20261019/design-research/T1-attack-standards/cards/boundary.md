# Removal Attack and Defense on AI-generated Content Latent-based Watermarking

ID: `boundary`. Verification: **V2, own T1 method and evaluation recheck**. Conservative direct floor: **included**.

Authors: De Zhang Lee; Han Fang; Hanyi Wang; Ee-Chien Chang. Version/date: 2509.11745v3; 12 Nov 2025. Venue: arXiv v3 preprint; CCS 2025 accepted-list search lead, but venue not independently verified in retrieved full page. DOI: not independently verified. Citation key: `T1_boundary`. Accessed 2026-10-20.

Primary: [https://arxiv.org/abs/2509.11745v3](https://arxiv.org/abs/2509.11745v3); [inspected full text](https://arxiv.org/html/2509.11745v3).

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-boundary.html` (502337 bytes). SHA-256: `43ebc1cb2074d56682e7e2d4754c139cd4701cce6acdb47bccd4830cb8fbe710`. Derived text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-boundary.read.txt`; SHA-256 `bdef2f99133a49f15812f7e98b7d46af5a3c58012a2f829ebab472683ec376cb`.

Inspected: Own T1 recheck: Sections 4.1--4.3 stealthy/minimum-distortion methods; defense statement/assumptions; Sections 6.1--6.2, Tables 2--3; Appendix C.1--C.2, Table 4. Cached lines 1665--1940, 3865--4460 and 5025--5220.

## Mechanism and attacker access

Boundary-aware latent attack sorts low-magnitude coefficients and flips signs under distortion budget, exploiting PRC sign boundaries without a secret key. Ideal or DDIM inversion access; regenerated with original/null prompt. Secret orthonormal defense has pseudorandomness/well-behaved-code assumptions.

## Models

PRC target; attack uses SD2.1, with additional SD1.5/SDXL evaluation. Gaussian Shading construction is discussed; the main measured detector is PRC.

## Strength / noise

Additional latent L2 epsilon = 4/6/8/10/12 beyond inversion error; synthetic message lengths 500/1,000/1,500/2,000; SDXL message length 3,000.

## Sampler / steps

50 generation timesteps; DDIM inversion under AC2/AC3. Exact sampler/default scheduler revision and separate inversion step count NR; do not fill from library defaults.

## Prompt / guidance

AC1: ideal inversion and original prompt; AC2: DDIM inversion and original prompt; AC3: DDIM inversion and null prompt. Detector uses null-prompt inversion. Numeric CFG NR.

## Resolution

SD2.1/SD1.5: 512-square images, latent 4 x 64 x 64. SDXL: 1024-square images, latent 4 x 128 x 128.

## Image counts and units

SD2.1: 100 random SDP prompts/images per each of six attack-capability setups. SDXL: 30 images under AC3. The published 10,000-pair collection describes illustrative availability, not Table 3 sample size. Table 4 aggregation/repetitions are unexplained: several reported ASRs cannot be rounded binary counts out of 30.

## Metrics

Native PRC ASR (no-watermark verdict), bit flips, paired RMSE/SSIM; PRC parameter f = .01. No empirical FPR bank reported in the inspected setup.

## Conditioned numerical results

Table 3, SD2.1 AC3, epsilon = 8: stealthy ASR .31, RMSE .0008, SSIM .92; white noise .03/.0009/.91 (n = 100 per setup). Table 4, SDXL AC3, epsilon = 8: .19/.0033/.79 versus .03/.0030/.80 (stated n = 30; unexplained rate aggregation). The fifteen-fold distortion claim concerns 5% synthetic bit flips, not image ASR.

## Limits and conflicts

Same-pipeline inversion and optional original prompt differ from our independent, query-free regeneration; no empirical image-level FPR guarantee. The ideal-inversion/synthetic 15x claim is not a universal image gain. Printed Algorithm 4.2 uses budget 2|s|^2 <= epsilon although squared L2 cost of a sign flip is 4s^2; indexing also appears ambiguous. Preserve paper labels rather than silently implementing a correction. Appendix C figure labels say MSE while tables say RMSE. Table 4 rates .19/.01/.12 cannot all be two-decimal rounded binary counts out of the stated 30 images; repetitions or averaging are not explained, so no integer success counts are reconstructed.

## Consequence for this study

Indistinguishability does not alone imply removal resistance. Record untested boundary-aware adaptive threat; no change to frozen F5 study.

The settings and numbers above are direct evidence from the named locators; the consequence is agent inference. Native claims of semantic preservation, distribution preservation or general robustness retain the stated assumptions and were not reproduced. No outcome from our study exists.
