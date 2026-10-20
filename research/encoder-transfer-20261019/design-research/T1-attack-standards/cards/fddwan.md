# FDDWAN: A Frequency-Decoupled Diffusion Network for Watermarking Attack

ID: `fddwan`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Chunpeng Wang; Yuxin Li; Xiaoyu Wang; Jidong Yang; Suo Gao; Qi Li
Version/date: 2607.27800v1; 30 Jul 2026. Venue: Verified arXiv preprint version; final venue not verified.
Primary: [https://arxiv.org/abs/2607.27800v1](https://arxiv.org/abs/2607.27800v1); [inspected full text](https://arxiv.org/html/2607.27800v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-fddwan.html`. SHA-256: `f942ef5b92d335d5bb0dd2d4fe68aa07fa89439ecb7150006e260bbd788f211d` (189931 bytes).
Inspected: Method web85-203; evaluation204-230/Table1.

## Mechanism and attacker access

Frequency-decoupled wavelet reconstruction followed by residual diffusion; training requires paired watermarked/clean data.

## Models

FDDWAN; DCT/PHFM/HiDDeN/StegaStamp

## Strength / noise

Training T1000; paired residual corruption

## Sampler / steps / optimizer

DDIM eta0,K10 per branch; training Adam500k iterations,lr1e-4,batch2

## Prompt / guidance

N/A unconditional residual reconstruction

## Resolution

256x256

## Image counts and units

CelebA and ImageNet; test image count not reported in inspected setup/Table1

## Metrics

BER,PSNR

## Conditioned numerical results

CelebA StegaStamp39.84dB/BER.5333 vsUnMarker30.05/.3536; ImageNet StegaStamp38.81/.4667. Test denominator missing.

## Limits and unresolved conflicts

Unavailable denominator excludes floor; paired training changes access; BER above.5 can remain informative under inversion.

## Consequence for this design

No claim that BER.5333 establishes watermark absence.
