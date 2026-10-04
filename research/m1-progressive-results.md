# Family C: progressive guidance development results

The frozen GROW-inspired SD1.5 candidate completed all planned work but did not recover a qualifying payload: **0/96 C1 conditions met 14/16 bits**, for both native VAE-DCT and image-DCT diagnostic; **0/96 recovered all 16 bits**. Each denominator is six variants × four prompt/seed clusters × four channels, not 96 independent images. C0 also had 0/16 true-payload presence and exact recovery for each extractor. This is a negative exploratory carrier screen, not a faithful GROW reproduction, a universal ceiling or family exhaustion.

## Frozen protocol and provenance

Source: MAIN `.thesis-build/dev-runs/20261004-0031-progressive`, commit `eca1a533a852d988b213ca47ab24f94dcda5b1f0`, duration 172.031 s, outcome `completed`. Four prompts/seeds1000–1003; alpha .1/.3/.5 × eta25/100 plus C0: 28 generations, 112 image conditions, 224 extractor observations. No failed or missing planned rows; each group below retains n=4. Only terminal-VAE decoded outputs are used. Guidance is the explicitly amended first-half, after-CFG, selected-coefficient MSE/128 operator, with sampler eta0. [Design](m1-progressive-design.md) and [CPU parity preflight](m1-progressive-preflight.md) specify the departures and side information.

Analysis: MAIN `20261004-0036-progressive-analysis`, same commit, `completed_descriptive_analysis`; input hashes matched and errors were empty. This report recalculated every aggregate bit-accuracy mean from retained raw rows and matched the analysis CSV. It did not open PNG pixels, run models, fit thresholds or alter retained outputs.

- Source run SHA-256: `c3436690fd0ae549d0a2a3ac71c00e43105d753697f0b26ce61984ccee62ff94`.
- Manifest SHA-256: `4fd655b813cb76455645a6573283ee2ffc57d93b59d425e7881f5878dda1ec65`.
- Journal SHA-256: `06b3a4df24c7ba75742a0f0b05212e70da4545e6373c103444fe47c8ce8d988c`.
- Analysis run SHA-256: `be62a215d3d34a87e7f0386b0371ffad77fd83ba5bff4cd63ac35a95ca682537`.
- Analysis data SHA-256: `3bfeff50faa3dead0c8105749c10e6dfbf3abba0d6911ecd8a617c1dc9073c8c`.
- Summary CSV SHA-256: `2927ac46a3cc6fd5081c0e93c5afc5c9430c1c1048e3cb48a3fab150f82cee52`.
- Raw CSV SHA-256: `6e2f005ec0215f7ce96820b39d3d2f27ffbdc0ec1a570a9bc4d47580741b715d`.

## Recovery in every declared condition

Each accuracy cell is **mean / median / sample SD / min–max**, across four clusters. Presence and exact are 0/4 in every cell below, for both extractors. Native requires one VAE encoder pass plus DCT; diagnostic uses resized RGB luminance DCT and does not represent the native latent carrier.

| Alpha | Eta | Channel | Native accuracy | Image-DCT accuracy |
|---:|---:|---|---|---|
| 0.1 | 25 | clean | 0.3906 / 0.3750 / 0.1288 / 0.2500–0.5625 | 0.3906 / 0.4062 / 0.1288 / 0.2500–0.5000 |
| 0.1 | 25 | vae | 0.3438 / 0.4062 / 0.1488 / 0.1250–0.4375 | 0.4062 / 0.4062 / 0.1488 / 0.2500–0.5625 |
| 0.1 | 25 | t3-0.1 | 0.4531 / 0.4688 / 0.1721 / 0.2500–0.6250 | 0.4688 / 0.4688 / 0.1488 / 0.3125–0.6250 |
| 0.1 | 25 | t3-0.4 | 0.5625 / 0.5625 / 0.1021 / 0.4375–0.6875 | 0.4375 / 0.4688 / 0.1531 / 0.2500–0.5625 |
| 0.1 | 100 | clean | 0.4531 / 0.4688 / 0.0598 / 0.3750–0.5000 | 0.4688 / 0.5000 / 0.1875 / 0.2500–0.6250 |
| 0.1 | 100 | vae | 0.4375 / 0.4375 / 0.1531 / 0.2500–0.6250 | 0.4688 / 0.5000 / 0.1875 / 0.2500–0.6250 |
| 0.1 | 100 | t3-0.1 | 0.5156 / 0.5312 / 0.2001 / 0.3125–0.6875 | 0.4062 / 0.4375 / 0.1875 / 0.1875–0.5625 |
| 0.1 | 100 | t3-0.4 | 0.5781 / 0.5625 / 0.0312 / 0.5625–0.6250 | 0.4375 / 0.4688 / 0.1840 / 0.1875–0.6250 |
| 0.3 | 25 | clean | 0.4219 / 0.4062 / 0.1562 / 0.2500–0.6250 | 0.4062 / 0.4375 / 0.1197 / 0.2500–0.5000 |
| 0.3 | 25 | vae | 0.3906 / 0.4062 / 0.1067 / 0.2500–0.5000 | 0.4219 / 0.4375 / 0.1386 / 0.2500–0.5625 |
| 0.3 | 25 | t3-0.1 | 0.4531 / 0.4688 / 0.1721 / 0.2500–0.6250 | 0.4688 / 0.4688 / 0.1488 / 0.3125–0.6250 |
| 0.3 | 25 | t3-0.4 | 0.5938 / 0.5625 / 0.0625 / 0.5625–0.6875 | 0.4219 / 0.4688 / 0.1795 / 0.1875–0.5625 |
| 0.3 | 100 | clean | 0.5625 / 0.5000 / 0.1250 / 0.5000–0.7500 | 0.4844 / 0.5000 / 0.2065 / 0.2500–0.6875 |
| 0.3 | 100 | vae | 0.5781 / 0.5625 / 0.1386 / 0.4375–0.7500 | 0.4688 / 0.5000 / 0.1875 / 0.2500–0.6250 |
| 0.3 | 100 | t3-0.1 | 0.5938 / 0.5938 / 0.0807 / 0.5000–0.6875 | 0.4531 / 0.4688 / 0.1721 / 0.2500–0.6250 |
| 0.3 | 100 | t3-0.4 | 0.6406 / 0.6250 / 0.0312 / 0.6250–0.6875 | 0.4844 / 0.5000 / 0.1386 / 0.3125–0.6250 |
| 0.5 | 25 | clean | 0.4531 / 0.4375 / 0.1866 / 0.2500–0.6875 | 0.4219 / 0.4375 / 0.1386 / 0.2500–0.5625 |
| 0.5 | 25 | vae | 0.4531 / 0.4375 / 0.1288 / 0.3125–0.6250 | 0.4375 / 0.4688 / 0.1531 / 0.2500–0.5625 |
| 0.5 | 25 | t3-0.1 | 0.4688 / 0.5000 / 0.1875 / 0.2500–0.6250 | 0.4688 / 0.4688 / 0.1488 / 0.3125–0.6250 |
| 0.5 | 25 | t3-0.4 | 0.6094 / 0.5625 / 0.1386 / 0.5000–0.8125 | 0.4375 / 0.4688 / 0.1976 / 0.1875–0.6250 |
| 0.5 | 100 | clean | 0.6719 / 0.6562 / 0.1067 / 0.5625–0.8125 | 0.4844 / 0.5000 / 0.2065 / 0.2500–0.6875 |
| 0.5 | 100 | vae | 0.6562 / 0.6250 / 0.1083 / 0.5625–0.8125 | 0.4844 / 0.5312 / 0.1795 / 0.2500–0.6250 |
| 0.5 | 100 | t3-0.1 | 0.6719 / 0.6875 / 0.0938 / 0.5625–0.7500 | 0.4531 / 0.4688 / 0.1721 / 0.2500–0.6250 |
| 0.5 | 100 | t3-0.4 | 0.6719 / 0.6562 / 0.0598 / 0.6250–0.7500 | 0.5000 / 0.5000 / 0.1443 / 0.3750–0.6250 |

C0 controls (four distinct prompt/seed clusters, with repeated channels):

| Channel | Native accuracy | Image-DCT accuracy |
|---|---|---|
| clean | 0.3438 / 0.3438 / 0.1301 / 0.1875–0.5000 | 0.4531 / 0.4688 / 0.1067 / 0.3125–0.5625 |
| vae | 0.3281 / 0.3438 / 0.1067 / 0.1875–0.4375 | 0.4375 / 0.4375 / 0.1141 / 0.3125–0.5625 |
| t3-0.1 | 0.4219 / 0.4375 / 0.1866 / 0.1875–0.6250 | 0.4531 / 0.4375 / 0.1386 / 0.3125–0.6250 |
| t3-0.4 | 0.5781 / 0.5938 / 0.1067 / 0.4375–0.6875 | 0.4531 / 0.4688 / 0.1288 / 0.3125–0.5625 |

## Generated-pair quality

Quality compares each clean C1 with its matched generated C0. The conjunction remains strictly PSNR>35 dB, SSIM>.9, LPIPS<.1. Both generations share prompt and initial Gaussian seed; this describes a generation counterfactual. It supplies no evidence that marking an existing photograph preserves that photograph, and cannot replace the fixed12 photographic development assessment. GS uses changed initial-noise signs, so shared prompts permit context but do not make its paired pixels the same source as C.

| Alpha | Eta | Quality conjunction | PSNR mean [range], dB | SSIM mean [range] | LPIPS mean [range] |
|---:|---:|---:|---|---|---|
| 0.1 | 25 | 4/4 | 38.9641 [35.4895–46.1239] | 0.9889 [0.9788–0.9968] | 0.0069 [0.0015–0.0138] |
| 0.1 | 100 | 1/4 | 31.9603 [26.1343–37.1641] | 0.9610 [0.9346–0.9849] | 0.0237 [0.0099–0.0382] |
| 0.3 | 25 | 3/4 | 37.3739 [34.5935–41.2523] | 0.9869 [0.9768–0.9928] | 0.0080 [0.0040–0.0148] |
| 0.3 | 100 | 1/4 | 31.6879 [26.0476–36.4014] | 0.9597 [0.9351–0.9821] | 0.0243 [0.0124–0.0366] |
| 0.5 | 25 | 3/4 | 37.6385 [34.8043–41.7644] | 0.9873 [0.9762–0.9931] | 0.0076 [0.0037–0.0152] |
| 0.5 | 100 | 1/4 | 30.7282 [24.2658–35.0083] | 0.9495 [0.9074–0.9768] | 0.0296 [0.0172–0.0487] |

Only alpha.1/eta25 satisfies generated-pair quality on all four clusters, while its native clean mean is .390625 with 0/4 presence. Alpha.5/eta100 has the highest clean native mean (.671875), but only1/4 meets generated-pair quality and none meets presence. These observations describe a tradeoff in this screen, not a chosen winner or an estimated upper bound.

Attack quality is separately against the same-arm clean image. The numerical CLIP cosine remains an exploratory semantic-retention proxy, not a human judgment. All 112 conditions have the proxy recorded; clean self-cosines near1 can slightly exceed1 from numerical rounding. Human assessments remain missing.

| Channel | Same-arm CLIP mean [range], n=28 | Native presence AND CLIP>=.85 |
|---|---|---|
| clean | 1.0000 [1.0000–1.0000] | 0/28 |
| vae | 0.9971 [0.9952–0.9986] | 0/28 |
| t3-0.1 | 0.9934 [0.9880–0.9978] | 0/28 |
| t3-0.4 | 0.9698 [0.9497–0.9888] | 0/28 |

## False hypotheses and runtime

The fixed complementary wrong word produced one native finding: alpha.1/eta25, VAE, seed1003, true accuracy2/16 and complement14/16. No image-DCT complement was found. The 64 SHAKE hypotheses produced **7/7168 native** and **4/7168 image-DCT** false findings; these are hypothesis–word queries on 112 reused outputs, not 7168 independent negatives. Native C0 contributes1/1024 and image C0 contributes1/1024; C1 contributes6/6144 and3/6144 respectively. No population FPR, key security or ownership authentication follows.

| Cluster seed | Native wrong-query findings /1792 | Image-DCT wrong-query findings /1792 |
|---:|---:|---:|
| 1000 | 1 | 1 |
| 1001 | 5 | 0 |
| 1002 | 1 | 3 |
| 1003 | 0 | 0 |

Fixed64 hypotheses, complementary words, six variants and four channels all share four source clusters and extracted words. These repetitions are retained descriptively; no bootstrap interval, significance test, or independent-trial confidence bound is reported.

Across112 observations, native extraction mean .05483 s, median .062 s, range .046–.063 s; image diagnostic mean .00347 s, median0, range0–.016 s. Recorded clock resolution explains zero diagnostic measurements; they do not prove zero cost. CUDA synchronization is included. Extraction excludes generation/inversion and uses pinned VAE weights. Maximum recorded C1 allocator peak was3,442,508,800 bytes (~3.206 GiB), below10 GiB; this is Torch allocation, not total system/GPU residency.

## Mechanistic interpretation and next diagnosis

Partial native alignment rises with alpha at eta100, but even its strongest mean does not qualify and the image-DCT diagnostic remains near chance. The preflight verified the exact orthonormal analytic gradient and scheduler wiring with CPU fixtures. It did not establish that early guidance remains in terminal latent coefficients after the un-guided half or after decode/re-encode. Current receipts retain no intermediate coefficient losses or final-predecode word, so this run cannot localize loss between guidance, subsequent denoising and the VAE roundtrip.

C0 native accuracy rises from .34375 clean to .578125 after T3 .4; several C1 means also rise after stronger regeneration. This contradicts interpreting every increase as watermark survival: regeneration can move an unmarked output toward this fixed public word. Eta25 low-alpha clean scores below chance and the complementary false finding also require care. The evidence supports an implementation/mechanism diagnosis, not an automatic conclusion that GROW itself fails or that all progressive guidance is exhausted.

A fresh astra design escalation should decide the next bounded diagnostic before any algorithm amendment: inspect the independently verified eta25/.609375 and eta100/−.5625 selected-coefficient contraction, early versus late guidance, terminal clean-latent retention, and exact VAE encode/decode loss. Do not refit14/16, select prompt seeds or silently switch to faithful GROW naming. Family C remains an empirically tried negative configuration with an unmeasured broader ceiling. This report adds no content/OwnerID binding, T4/T5 result, photographic-source result or held-out evidence.

## Extracted words for every cluster and channel

Word order within each cell is **clean / VAE / T3 .1 / T3 .4**; target is `1011010001101001`. These are the actual sixteen-bit strings, including all C0 and every C1 variant.

| Seed | Arm/variant | Native words | Image-DCT words |
|---:|---|---|---|
| 1000 | C0 | 0110011110000010 / 1101011110000010 / 1111010011000010 / 0100010011000010 | 1101000010000010 / 0101000010000010 / 0101000010010010 / 0111001010011010 |
| 1000 | C1 alpha0.1/eta25 | 0110011110000000 / 1101011110000000 / 1111010111000010 / 0100010011000010 | 0101100010000010 / 0101100010000010 / 0101000010010010 / 0011001010010010 |
| 1000 | C1 alpha0.1/eta100 | 0111010110000000 / 1101011110000000 / 1111010011000000 / 1000010011000010 | 1101100010000010 / 1101100010000010 / 0101100010000010 / 0011001010011010 |
| 1000 | C1 alpha0.3/eta25 | 0111011110000000 / 1101011110000000 / 1111010011000010 / 1000010011000010 | 1101100010000010 / 1101100010000010 / 0101000010000010 / 0011001010010010 |
| 1000 | C1 alpha0.3/eta100 | 0111010110000000 / 1111010110100000 / 1111010011000000 / 1001010011000010 | 1101100010000010 / 1101100010000010 / 0101000010000010 / 0011001010011010 |
| 1000 | C1 alpha0.5/eta25 | 0111010110000000 / 1101011110000000 / 1111010011000010 / 1000010011000010 | 1101100010000010 / 1101100010000010 / 0101000010000010 / 0011001010010010 |
| 1000 | C1 alpha0.5/eta100 | 1111010111000000 / 1111010110100000 / 1111010011100000 / 1001010011000010 | 1101100010000010 / 1101000010000010 / 0101000010000010 / 0001001010011010 |
| 1001 | C0 | 0000010010010001 / 0000000010010001 / 0000010010000000 / 0010000011101000 | 0110000000001010 / 0110000000001010 / 0110000000001010 / 0110000000001000 |
| 1001 | C1 alpha0.1/eta25 | 0010010010010001 / 0000000010011000 / 0010010010000001 / 0010000011101000 | 0110000000001010 / 0110000000001010 / 0110000000001011 / 0110000000001000 |
| 1001 | C1 alpha0.1/eta100 | 0010000010011000 / 0010000010101000 / 0010010010101000 / 0010000011001000 | 0110000000101011 / 0110000000101011 / 0110000000100011 / 0010000000001011 |
| 1001 | C1 alpha0.3/eta25 | 0010010000010001 / 0000000000011000 / 0010010010000000 / 0010000011101000 | 0110000000001010 / 0110000000001011 / 0110000000001011 / 0110000000001000 |
| 1001 | C1 alpha0.3/eta100 | 0010010010101001 / 0010010000101000 / 0010010010001000 / 0000010001001000 | 0110000000101011 / 0110000000101011 / 0110000000101011 / 0010000000001011 |
| 1001 | C1 alpha0.5/eta25 | 0010010000011001 / 0000010000011001 / 0010010010000001 / 0010010001101000 | 0110000000001010 / 0110000000001011 / 0110000000001011 / 0010000000001000 |
| 1001 | C1 alpha0.5/eta100 | 0010010000101001 / 0010010000101001 / 0010010000001001 / 0010010001001000 | 0110000000101011 / 0110000000101011 / 0110000000101011 / 0010000000001011 |
| 1002 | C0 | 0100001011000000 / 0100101011000000 / 1100101011001100 / 1100011011101101 | 1000000011111100 / 1000000011111100 / 1000000001111100 / 1000001011001000 |
| 1002 | C1 alpha0.1/eta25 | 0100001011000000 / 0100101011001000 / 1100101011001100 / 1100111011101101 | 1000000011111110 / 1000000011111100 / 1000000001111100 / 1000001011001000 |
| 1002 | C1 alpha0.1/eta100 | 0100001011001000 / 1100001011000000 / 1100101011000100 / 1100111011101101 | 1000000001111100 / 1000000001111100 / 1000000001011100 / 1000101011001000 |
| 1002 | C1 alpha0.3/eta25 | 0100001011000000 / 0100101011001000 / 1100101011001100 / 1100111011101101 | 1000000011111110 / 1000000011111110 / 1000000001111100 / 1000001011001000 |
| 1002 | C1 alpha0.3/eta100 | 0100011011001000 / 1100001011001000 / 1100111011001000 / 1110111011101101 | 1000010001111100 / 1000000001111100 / 1000000001011100 / 1000101011001001 |
| 1002 | C1 alpha0.5/eta25 | 0100001011000000 / 0100001011001000 / 1100101011001100 / 1100111111101101 | 1000000011111100 / 1000000011111100 / 1000000001111100 / 1000001011001000 |
| 1002 | C1 alpha0.5/eta100 | 1100011011001000 / 1100011011001000 / 1100110011001000 / 1110110011101101 | 1000010001111100 / 1000000001111100 / 1000000001011100 / 1000100011001001 |
| 1003 | C0 | 0000011110010110 / 0000011110010110 / 0000011110010110 / 0001011001010101 | 0010100000010110 / 0010100000010110 / 0010100000000110 / 0110100000000110 |
| 1003 | C1 alpha0.1/eta25 | 0000011100010110 / 0000001110010110 / 0001011110010110 / 0001011001010101 | 0010100010010110 / 0010100010010110 / 0010100000000110 / 0110100000010110 |
| 1003 | C1 alpha0.1/eta100 | 1000011100110110 / 1000001100010110 / 0000011000110110 / 0001011000000101 | 0010100010010110 / 0010100010010110 / 0000100010010110 / 0100100000010110 |
| 1003 | C1 alpha0.3/eta25 | 0000011100010110 / 0000011100010110 / 1000011110010110 / 0001011001010101 | 0010100010010110 / 0010100010010110 / 0010100000010110 / 0100100000010110 |
| 1003 | C1 alpha0.3/eta100 | 1010010100110110 / 1001011100010010 / 1001011000110100 / 0001011001000101 | 0010100010010110 / 0010100010010110 / 0010100010010110 / 0000000000010110 |
| 1003 | C1 alpha0.5/eta25 | 0000011100010110 / 1000011100010110 / 1000011110010110 / 0001011001010101 | 0010100010010110 / 0010100010010110 / 0010100000010110 / 0100100000010110 |
| 1003 | C1 alpha0.5/eta100 | 1011010100110000 / 1001011000110000 / 1011011000110100 / 0001011001000101 | 0010100010010110 / 0010100010010110 / 0010100010010110 / 0010000000010110 |
