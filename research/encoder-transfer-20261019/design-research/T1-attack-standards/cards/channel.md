# Optimizing and Securing the Modern Watermarking Channel for Images

ID: `channel`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Enoal Gesny; Eva Giboulot
Version/date: 2609.34744v1; 28 Sep 2026. Venue: Verified arXiv preprint version; final venue not verified.
Primary: [https://arxiv.org/abs/2609.34744v1](https://arxiv.org/abs/2609.34744v1); [inspected full text](https://arxiv.org/html/2609.34744v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-channel.html`. SHA-256: `738ac34cae9baff58d9f699377cea3f7fd6a18a81dbda9ba791149165c81fdde` (494130 bytes).
Inspected: Sections4,6;AppendixH.2/Table6;web217-243,285-333,782-808.

## Mechanism and attacker access

SNW secret semiorthogonal signal/noise channel; alignment,isotropy andquality objectives; attack comparisons test whitening and capacity.

## Models

SNW,PixelSeal,VideoSeal,TrustMark;SANA regeneration;WMForger

## Strength / noise

Clean watermark power48dB;SANA8/20step examples;WMForger50/100

## Sampler / steps / optimizer

SANA lasttsteps; exact checkpoint/sampler not supplied in AppendixH.2

## Prompt / guidance

Not reported forSANA baseline in AppendixH.2

## Resolution

1024x1024

## Image counts and units

MainFigure4 says1000MFlickr;AppendixH.2/Table6 says200: unresolved. CleanqualityN1000;whitening1millionMFlickr.

## Metrics

Normalizedrate;capacityfromBA underindependence;LPIPS

## Conditioned numerical results

Table6 SNW SANA8 rate.145/cap111.5bits vsPixelSeal.076/19.4;SANA20 .001/.8 vs.003/.8;WMForger100 .139/106.5 vs.280/71.8.

## Limits and unresolved conflicts

Denominator conflict; uncorrelated whitening is not proof of independent bit errors; SANA baseline calledDiffPure differs fromoriginal.

## Consequence for this design

Supplementarybenchmark comparison only; cannot import capacity/FPR into this test.
