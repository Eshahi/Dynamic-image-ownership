# SPFM-Net: Semantic-Prior-Guided Frequency-Constrained Mamba for Invisible Watermark Attack

ID: `spfm`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Chunpeng Wang; Yanan Shi; Zhiqiu Xia; Jidong Yang; Suo Gao; Qi Li
Version/date: 2607.27811v1 [cs.CV] 30 Jul 2026. Venue: arXivpreprint; venue not verified.
Primary: [https://arxiv.org/html/2607.27811v1](https://arxiv.org/html/2607.27811v1); [inspected full text](https://arxiv.org/html/2607.27811v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-spfm.html`. SHA-256: `e20712bc1898dc381d76b2ad23247dec90a6248cef3e68c1d2fc58c2abe801e2` (195445 bytes).
Inspected: Method subsections; Experiments/Tables1-4; web-rendered90-157 and158-224.

## Mechanism and attacker access

Partially unfrozen masked autoencoder with90%patch masking, multiscalefrequency module and claimed Mamba globalmodule, trained against paired clean targets with pixel/FFT/Sobel losses.

## Models

MAE24blocks1024dim;3trainableblocks;Mamba-labelledGSFM; learneddecoder

## Strength / noise

Patch16;maskratio.9;trainingGaussian sigma.02;FFTweight.5/edge.3

## Sampler / steps / optimizer

100epochsAdamWlr1e-5,weightdecay1e-6,batch2;diffusionsamplerN/A

## Prompt / guidance

N/A

## Resolution

224x224

## Image counts and units

20kcleanface training images withLSB/DCT/QPHFMs;100testimages eachYu(CelebA-HQ),StableSignature(SDP),HiDDeN(SDXL)

## Metrics

BER;pairedPSNR,SSIM,LPIPS,A-FINE

## Conditioned numerical results

Tables1-2 StableSignatureBER.48/PSNR32.83/SSIM.99/LPIPS.04 versusUnMarker.48/22.22/.55/.29; YuBER.12 versusUnMarker.37;100images/method

## Limits and unresolved conflicts

BER.55 is not established detector rejection; paper overstates universal removal whileYu retains88%bits. GSFM equations show convolution/FFN without sufficient state-space detail. Tiny224px and unequal datasets confound universal claims.

## Consequence for this design

Consider learned reconstruction as separate threat; no training or comparison to strict F5quality without matched resolution.
