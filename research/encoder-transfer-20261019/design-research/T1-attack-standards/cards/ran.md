# RAN: A randomness-anchored watermark attacking network with stealth and effectiveness

ID: `ran`. **V2 own T1 method/evaluation reading; direct removal floor included.**

Authors: Fan Li; Du Li; Kunqi Li; Yanyu Jiang; Yanlin Leng; Kai Zhou; Yong Tang. Scientific Reports 16, article 21334 (2026). Published 09 May 2026; Scientific Reports 16, article 21334. DOI `10.1038/s41598-026-52298-w`. Citation key `T1_ran`. Accessed 2026-10-20.

Primary: [https://www.nature.com/articles/s41598-026-52298-w](https://www.nature.com/articles/s41598-026-52298-w).

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-1b-ran-gap\ran.html` (392049 bytes), SHA-256 `215e56e99633bd9b7b2f645d3d1a0c101338257162ea6fdc91eb75ebd3635e9e`. Derived text `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-1b-ran-gap\ran.html.txt`, SHA-256 `ac9145a1dae6e42dd900f58c131bbfa5b59377031d7b67f1d1d4fd431ba7dd5d`.

Inspected: Methods: architecture/losses, Equations 1--6; Experiments: datasets/training/metrics, Equations 7--11; Results and Discussion. Cached main text lines 78--163; all rows of separately cached official Tables 1--3.

## Mechanism and access

A 17-layer 54.4M-parameter U-Net learns to preserve input pixels while making the extracted watermark match uniform-random targets, using MSE or KL-divergence watermark loss. Training uses an extraction-dependent loss; lack of original payload knowledge is not proof of a decoder-free or universal black-box attack.

## Models

DWT(Haar, one level)-DCT(LL)-SVD watermark images; transfer evaluation on Watermark Anything Model (WAM) with 32-bit strings. No SD1.5, SDXL, diffusion model or independently trained diffusion autoencoder is evaluated.

## Strength and noise

Learned attack: alpha=1; beta=1e-6 for MSE or 1 for KLD. Uniform-random watermark targets; their exact numeric support NR. Comparators: average3x3, Gaussian5x5, median3x3, salt-pepper SNR=.95, Gaussian variance=.005, JPEG Q30/50/70.

## Sampler and training

No diffusion sampler/timesteps: one feed-forward attack. Pretrain pixel MSE 50 epochs/batch40/lr1e-5, then30 epochs/batch30/Adam/lr1e-4; four-fold cross-validation model selection. No inference severity sweep reported.

## Prompt

Not applicable; natural cover images, no text conditioning or guidance.

## Resolution

512x512 RGB covers; binarized32x32 CIFAR10 watermark images (1,024 pixels); additional32-bit WAM strings.

## Counts and units

5,000 randomly selected ImageNet covers and5,000 CIFAR10 watermark images; 4,000 training/1,000 independent test covers. Table3 WAM uses the described testing evaluation, but a separate WAM-specific denominator and number of repetitions are NR; Table1 is one turtle image.

## Metrics

Mean(SD) SSIM/PSNR, watermark NC/BER; per-RGB-channel PSNR for one example. No calibrated FPR, image-level TPR/ASR, owner/payload verdict, LPIPS or uncertainty interval. SD is dispersion, not a confidence interval.

## Conditioned numerical results

Table2 DWT-DCT-SVD: KLD SSIM.987(.018)/PSNR37.060(3.658)dB/NC.240(.485)/BER.240(.189); MSE .987(.018)/37.152(3.707)/.550(.346)/.206(.178). Gaussian5x5 .705(.127)/24.784(3.840)/.010(.032)/.412(.121); JPEG30 .865(.035)/30.778(2.685)/.342(.105)/.298(.111). Table3 WAM: KLD .973(.021)/37.383(3.677)/BER.494(.066); MSE .973(.022)/37.488(3.740)/.060(.046); JPEG30 .873(.039)/30.833(2.823)/.096(.084).

## Limits and conflicts

Only two embedding schemes; traditional mean BER.240 does not establish random/chance decoding despite the randomness objective. WAM near-.5 mean BER is not calibrated image-level removal. Captions of Tables2--3 identify I_co versus I_a, while the metric definitions and narrative use I_w versus I_a: quality-reference conflict unresolved. Exact WAM checkpoint/native settings, random support/seeds, extractor-gradient handling and WAM-specific n are NR. No forensic stealth test; no F5 or independent-encoder transfer evidence; reported inference .022s on their setup is not a server cost estimate.

## Consequence for this study

Include as a recent non-diffusion removal benchmark and an untested learned-attack limitation. Do not import BER as our endpoint or add an attack, baseline, proposal or compute cost to the frozen SDXL study.

## Table artifacts

- [Official Table1](https://www.nature.com/articles/s41598-026-52298-w/tables/1), `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-1b-ran-gap\ran-table1.html`, SHA-256 `367bf3ab83849796ed4940d96d76446515be9fbeb6bd83b9e8317b0972a4474d`; derived SHA-256 `1dc643d5b6eabc55f77225b0a4485c5b15a55f982fc1fddb9ff16959eb530d32`.
- [Official Table2](https://www.nature.com/articles/s41598-026-52298-w/tables/2), `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-1b-ran-gap\ran-table2.html`, SHA-256 `abf11943630ced9aeeef97e7434ddb4216a40d698834caf6b0ef91c3bee1890c`; derived SHA-256 `d8d6ff507a22d1b7eecb6d027c2228e165424062702b0c928a3f945dd3458856`.
- [Official Table3](https://www.nature.com/articles/s41598-026-52298-w/tables/3), `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-1b-ran-gap\ran-table3.html`, SHA-256 `4a5f6f07b40cc4c2cbb0dba512863057dde713c3087f3c9ea0391ffa9c39a06a`; derived SHA-256 `1c357259a5666fa3c5a3fecfc96d51c62f43f0752ccfe0c149d390064ca0c33a`.

Direct evidence is the reported method/settings/table values. Generalization claims are author interpretation; the consequence for this study is agent inference. No project outcome exists.
