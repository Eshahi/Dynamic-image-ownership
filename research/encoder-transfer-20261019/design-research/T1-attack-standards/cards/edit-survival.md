# Latent Watermarks under Generative Editing: A Benchmark and Analysis of Detection Survival

ID: `edit-survival`. Verification: **V2, own T1 method and evaluation recheck**. Conservative direct floor: **supplemental only**.

Authors: Sung Ju Lee; Nam Ik Cho. Version/date: 2610.09702v1; 07 Oct 2026. Venue: arXiv preprint; final venue not independently verified. DOI: not independently verified. Citation key: `T1_edit_survival`. Accessed 2026-10-20.

Primary: [https://arxiv.org/abs/2610.09702v1](https://arxiv.org/abs/2610.09702v1); [inspected full text](https://arxiv.org/html/2610.09702v1).

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-edit-survival.html` (718738 bytes). SHA-256: `92ee050f2d969f77db7f6b00c87cc8c2e252884d4cf6c8edb0c993b8874825b9`. Derived text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-edit-survival.read.txt`; SHA-256 `ea056173dc417966c0e888a39faa5ef5ccfdc0198b44224c2d4fc9560cfb5b71`.

Inspected: Own T1 recheck: Sections 3--4, Tables 1--2; limitations/reproducibility; Appendix E.1--E.5, Table 19; Appendices F--G, Table 21 and threshold sensitivity summary. Cached lines 155--298, 2558--2663 and 2718--2793.

## Mechanism and attacker access

Ordinary targeted semantic edits without watermark optimization; separately reports edit-only survival and seven independent post-edit distortions. Blind latent detectors; clean score separation is an empirical diagnostic, not a causal carrier proof.

## Models

SD2.1-base sources, P2P and P2P+NTI; LCM DreamShaper v7 for InfEdit; SD3 Medium / FLUX.1-dev for FlowEdit; eight latent watermark methods.

## Strength / noise

s = .7/.4/.2/0; larger s is closer to reconstruction. P2P attention tau = s. FlowEdit SD3 nmax = 15/30/40/50; FLUX nmax = 9/17/23/28. Main setting .4, except FLUX .2 (nmax = 23). These are not img2img noise strengths.

## Sampler / steps

Source DDIM 50 steps, CFG 7.5, except Gaussian Shading uses its official sampler. P2P: 50 inversion + 50 editing steps; NTI: 50 steps x 10 inner iterations; InfEdit: 15 LCM steps; FlowEdit: SD3 T = 50 / FLUX T = 28, nmin = 0.

## Prompt / guidance

Fixed 500 source-target pairs = 100 captions x 5 categories; source seed 42 + index is shared across categories. P2P CFG 7.5; InfEdit target/source guidance 2/1; FlowEdit SD3 source/target guidance 3.5/13.5; FLUX 1.5/5.5.

## Resolution

512 x 512 sources; native editor output resolution not separately stated. LPIPS uses 256-square VGG v0.1.

## Image counts and units

100 source-caption identities per cell; 160 method-editor-strength cells x 5 categories. Of 800 category cells, 786 have n = 100 and 14 InfEdit cells have n = 99. Missing outputs are omitted from TPR. Repeated edits/distortions are not independent images. Quality uses 2,500 pairs per editor from five original methods.

## Metrics

TPR at nominal 1% FPR: seven empirical strict 99th-percentile rules; Gaussian Shading analytic threshold >= 147/256. LPIPS, DINOv2, DeltaCLIP/BLIP2; source/null d-prime. Recalibration and cross-fit checks.

## Conditioned numerical results

Table 1, P2P main setting .4, 100 sources x 5 categories: Tree-Ring edit-only TPR .632 / post-distortion mean .356; ZoDiac .996/.818; HSTR 1/.934; HSQR 1/.991. FlowEdit FLUX quality: LPIPS .187 / DeltaBLIP2 .064, versus SD3 .205/.321; native budgets differ.

## Limits and conflicts

Conservative adjunct: ordinary editing rather than fixed regeneration/removal; seven of eight composite terms are added distortions. Native severity and semantic edits are not perceptually matched. Gaussian Shading/TAG limit d-prime analysis. Missing outputs are omitted. Code/artifacts are planned, not a verified release. This new study is distinct from the taxonomy, rather than independent confirmation of its reused tables.

## Consequence for this study

Retain score distributions alongside fixed decisions and source-level denominators. Do not replace our endpoint with the composite or add semantic edits.

The settings and numbers above are direct evidence from the named locators; the consequence is agent inference. Native claims of semantic preservation, distribution preservation or general robustness retain the stated assumptions and were not reproduced. No outcome from our study exists.
