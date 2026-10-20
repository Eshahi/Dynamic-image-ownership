# A Technical Report on "Erasing the Invisible": The 2024 NeurIPS Competition on Stress Testing Image Watermarks

ID: `competition`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Mucong Ding; Tahseen Rabbani; Bang An; Chenghao Deng; Anirudh Satheesh; Souradip Chakraborty; Mehrdad Saberi; Yuxin Wen; Kyle Sang; Aakriti Agrawal; Xuandong Zhao; Mo Zhou; Mary-Anne Hartley; Lei Li; Yu-Xiang Wang; Vishal M. Patel; Soheil Feizi; Tom Goldstein; Furong Huang
Version/date: Official NeurIPS2025 proceedings32-page PDF; exact publication day not stated. Venue: NeurIPS2025 Datasets and Benchmarks Track; event was2024.
Primary: [https://proceedings.neurips.cc/paper_files/paper/2025/file/15389039ccef67b6bed9b2df8414400f-Paper-Datasets_and_Benchmarks_Track.pdf](https://proceedings.neurips.cc/paper_files/paper/2025/file/15389039ccef67b6bed9b2df8414400f-Paper-Datasets_and_Benchmarks_Track.pdf); [inspected full text](https://proceedings.neurips.cc/paper_files/paper/2025/file/15389039ccef67b6bed9b2df8414400f-Paper-Datasets_and_Benchmarks_Track.pdf). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-competition.pdf`. SHA-256: `2e3a9ba346d706334b39a11bcc2045a572f4c67944b1ade41c010ca3c3edcebf` (27435657 bytes).
Inspected: Section2 pp2-4; Section3 pp4-6; AppendixA p20; AppendixE pp22-23; winning methods pp28/30; Tables5-6 and conflicting metric definition visually checked pp30/23.

## Mechanism and attacker access

Crowdsourced removal benchmark with known-family beige-box and confidential mixed-watermark black-box tracks, adaptive leaderboard feedback, and organizer human quality re-ranking. Superposed marks count detected if either survives.

## Models

SourceSD2.1 andFLUX.1-dev; winning attacksVAE,SDXLrefiner,FLUX+ControlNet,CtrlRegen+,rinsing

## Strength / noise

Participant-specific adaptive shifts7/8pixels,entropy-dependentstrengths; no universalstrength

## Sampler / steps / optimizer

Participant-specific; report does not fix common sampler/steps

## Prompt / guidance

Participant captions/denoise/dehaze/clean prompts vary

## Resolution

Common image resolution not established in inspected report

## Image counts and units

300images/track;beige150+150;black6groupsx50;10,000unmarked calibration/type;2,722submissions are not independent sources

## Metrics

MaintextA=TPR@.1%FPR;8-metricQ;humanquality;AppE contradictoryA=1-TPR

## Conditioned numerical results

Table5 winningblack machineQ.1363,A.0433,prioroverall.1430;humanQ.1420/final.1485. Table6 winnerPRCASR88%=44/50 andGaussianShading+JigMark90%=45/50,overall300images

## Limits and unresolved conflicts

Visually confirmed: mainp4 A=TPR butAppE p23 A=1-TPR while minimizing score. AppA says strengths uncalibrated;AppE says tuned. Appendix calls GaussianShading TreeRing in places. Winner paper overlaps results; do not double-count as independent evidence.

## Consequence for this design

Use raw detection and quality metrics with clear denominators; never copy benchmark scores or claim its human verdict for this study.
