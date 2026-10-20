# BrushOff: Stroke-Based Re-rendering as a Watermark Removal Attack on Paintings

ID: `brushoff`. Verification: **V2, own T1 method and evaluation recheck**. Conservative direct floor: **included**.

Authors: Hao Chen; Junnan Xu. Version/date: 2610.26682v1; 19 Oct 2026. Venue: arXiv preprint; final venue not independently verified. DOI: not independently verified. Citation key: `T1_brushoff`. Accessed 2026-10-20.

Primary: [https://arxiv.org/abs/2610.26682v1](https://arxiv.org/abs/2610.26682v1); [inspected full text](https://arxiv.org/html/2610.26682v1).

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T8-1b\brushoff.html` (176946 bytes). SHA-256: `af33f29ecdcf4d761015133bdecefcb6eb682a37f2e33b4c0d26cc7839cf2c01`. Derived text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T8-1b\brushoff.read.txt`; SHA-256 `ef49588148f39302dadcf82872370895317cb895c9010081dd719b7defb6831c`.

Inspected: Own T1 recheck: Sections III-A--III-C and IV-A--IV-E; Tables I--II; V-A--V-E; VI-A--VI-C and VII. Cached text lines 155--633; numerical Table II 388--477.

## Mechanism and attacker access

Query-free Paint Transformer re-rendering copies input colors into eight-parameter strokes. Border pass retains the released all-strokes behavior; stroke size and placement matter as well as count.

## Models

Paint Transformer; SD2.1-base img2img; VINE-R (100 bits), TrustMark-Q (61 payload bits + 35 BCH parity bits + 4 header bits), RivaGAN (32 bits), DwtDctSvd (32 bits).

## Strength / noise

Canvas sizes 512/1024/2048 give 6/7/8 levels. Regeneration strengths 0/.1/.2/.3/.5, plus .6/.7/.8 for VINE; strength 0 is VAE-only.

## Sampler / steps

Regeneration uses 50 scheduled steps; sampler and numeric seed not reported (NR); seed is fixed. Renderer is feed-forward without tuning. Actual reverse-update count NR.

## Prompt / guidance

Empty regeneration prompt; CFG disabled. Repainting needs no prompt.

## Resolution

512-square center crop; bicubic upsample to 1024/2048, antialiased downsample to 512.

## Image counts and units

500 WikiArt images = 100 per style across 5 styles, with fixed-seed eligible sampling. VINE: n = 500. RivaGAN excludes 15 clean failures (n = 485). Non-VINE 2048-canvas runs use 100 source images (first 20 per style), before watermark-specific clean exclusions. DwtDct detects only 349/500 clean images and is omitted from attacks. Fixed common payload.

## Metrics

Detection uses fair-independent-bit theoretical FPR <= 1e-3 thresholds: 26/32 or 66/100; TrustMark uses native ECC. Zero clean false positives among 500; 2,000 image-bootstrap samples. DISTS, DreamSim, MUSIQ and PSNR refer to the clean painting; fidelity is measured only on VINE.

## Conditioned numerical results

Table II, RP 2048/L6: VINE detection rate .018 (n = 500); TrustMark 0, RivaGAN .226, DwtDctSvd .180 (100-source subset before watermark-specific clean exclusions). DISTS .349, DreamSim .265, MUSIQ 58.2, PSNR 19.9 dB. Regeneration at .5: VINE .474, DreamSim .256; at .8: .018 and .559.

## Limits and conflicts

Painting domain only, one renderer, fixed payload and outcome-selected operating-point discussion. Nominal binomial FPR assumes fair independent null bits; 0/500 is not empirical proof of 1e-3. Borrowing VINE fidelity for other marks is a pilot-based assumption. The reported 27 seconds per 2048-canvas image on an unnamed consumer GPU is not our cost estimate. Probe decoder changed after clean failure and is exploratory.

## Consequence for this study

Document non-generative re-rendering as an untested limitation; do not add this attack or a new F5 variant to the frozen encoder-transfer study.

The settings and numbers above are direct evidence from the named locators; the consequence is agent inference. Native claims of semantic preservation, distribution preservation or general robustness retain the stated assumptions and were not reproduced. No outcome from our study exists.
