# The Forensic Cost of Watermark Removal

ID: `forensiccost`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Gautier Evennou; Ewa Kijak
Version/date: 2604.25491v1 [cs.CV] 28 Apr 2026. Venue: arXiv preprint; template conference and XXXX DOI in text are placeholders and are NOT valid venue metadata.
Primary: [https://arxiv.org/abs/2604.25491v1](https://arxiv.org/abs/2604.25491v1); [inspected full text](https://arxiv.org/html/2604.25491v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-forensiccost.html`. SHA-256: `ac150b4613f501513c065a3996b81757eba05972e258663dd71bd5ede4b8ac4f` (136624 bytes).
Inspected: Method cached89-109; evaluation110-120,170-220 and Table2.

## Mechanism and attacker access

Benchmarks forensic traces left by removing TrustMark/VideoSeal; separate ConvNeXt classifiers discriminate attack residue.

## Models

TrustMarkQ,VideoSeal1.0; FLUX.1-dev DiffPure;SANA VAE;CtrlRegen;WMForger

## Strength / noise

DiffPuret.1;CtrlRegen sigma.1/.2/.3

## Sampler / steps / optimizer

WMForger500iterations lr.05; FLUX/SANA sampler counts unspecified

## Prompt / guidance

Prompt policy unspecified

## Resolution

256x256 images; detector resize224

## Image counts and units

5,000COCO covers x2 watermark systems; about80k augmented outputs;70/10/20 source split

## Metrics

BA; ASR under rho>1e-6 rejection; PSNR; forensicTPR@1%

## Conditioned numerical results

Table2 DiffPure TrustMarkPSNR29.7/BA.504/ASR.981; VideoSeal29.6/.640/.833. ForensicTPR@1% TrustMarkDiffPure.675 versusWMForger.998; test source split20% of5k covers

## Limits and unresolved conflicts

Template DOI/venue invalid. Detector may recognize benign regeneration rather than malicious intent; requires benign-generative controls. Excluded from strict direct-removal floor as adjacent forensic study.

## Consequence for this design

Do not equate detectability of editing with ownership evidence.
