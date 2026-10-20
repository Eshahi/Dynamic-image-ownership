# UnMarker: A Universal Attack on Defensive Image Watermarking

ID: `unmarker`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Andre Kassis; Urs Hengartner
Version/date: 2405.08363v2 [cs.CR] 22 Nov 2024. Venue: Author version explicitly marked to appear at IEEE S&P 2025; this card inspects arXiv v2, not final proceedings.
Primary: [https://arxiv.org/abs/2405.08363v2](https://arxiv.org/abs/2405.08363v2); [inspected full text](https://arxiv.org/html/2405.08363v2). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-unmarker.html`. SHA-256: `f7cf99c1482bdd9df24b712855c33bff6a8ec8db4466157db02ac5bda9b52002` (596813 bytes).
Inspected: Sections IV-VI cached508-628,730-755,801-872; TablesII-III and1095-1130; AppendixA hyperparameters2054-2062 and2334-2346 re-read.

## Mechanism and attacker access

Query-free attack combines spectral high-frequency optimization, learned low-frequency filters and10% crop; it does not require target detector gradients.

## Models

No generative model; optimized filters

## Strength / noise

Crop10% plus spectral objective constraints; low-frequency9 filters (21,5),(5,5),(17,33),(7,7),(47,5),(33,17),(17,17),(5,5),(3,3); color sigma.05; FRL weight5,L2 weight.00025; low DVLthreshold.001(<=256),.003(larger); high Alex.0005(128),DVL.04(256),.0001(larger)

## Sampler / steps / optimizer

No diffusion. AppendixA high-frequency Adam lr2e-4, 2,000 iterations at256x256 and5,000 below/above; binary search2 steps at<=256x256,4 above; halve lr after10 improvements<=1e-4; gradient clipping DVL.005/Alex.05. Low-frequency500 iterations, one binary step, Adam filterlr.01/modifierlr.002; decay.99 after10 improvements<=.05; gradientclip1.

## Prompt / guidance

N/A

## Resolution

StegaStamp400x400; HiDDeN/Yu128x128; scheme-native others

## Image counts and units

100 randomly chosen images per each of7 schemes

## Metrics

Detection under scheme thresholds; LPIPS,FID; multibit binomial p<.01; Tree-Ring2%FPR

## Conditioned numerical results

TablesII-III full CHL attack detects43/100 StegaStamp (LPIPS.08) and40/100 Tree-Ring (LPIPS.10); HL yields Stable Signature9% and PTW6% detection

## Limits and unresolved conflicts

Includes crop and spectral manipulation outside this T3-only experiment. Author criterion below50% detection is not a universal chance-level guarantee; schemes use different FPRs.

## Consequence for this design

Explain spectral localization as a plausible removal route without adding T1/T2 attack experiments.
