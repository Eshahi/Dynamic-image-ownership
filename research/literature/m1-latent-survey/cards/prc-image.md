# An undetectable watermark for generative image models

Primary source: https://arxiv.org/html/2410.07369v2

Inspected: Sec.3.2/Theorems1-2; Sec.4.1,4.3-4.4; App.A.2,C.3. Full-text artifact/checksum in paper JSON and inventory.

PRC codeword sets initial-noise signs; independently sampled Gaussian magnitudes preserve marginal prior. Model inversion recovers noisy signed observations, detector uses weighted parity evidence; belief propagation decodes messages. Main SD2.1 uses CFG3, DPM-Solver50, exact DPM inversion50/order0. AppA.2 diffusion regeneration uses SD2.1 at diffusion steps10,20,30,50,80,100,150,200; VAE regeneration uses CompressAI Bmshj2018/Cheng2020 factors1-6. Sec4.3 says tested attacks do not drive TPR below .99 while FID<70; JPEG20 gives .94 at degraded quality. 512-bit decoder is weaker than detector; clean capacity reaches2500. Theorem2 probability is over independent random watermark keys for a fixed image.

Limitations: Sec3.2/C.3 finite experimental parameters do not satisfy strict pseudorandomness proof bounds. Detection is inversion dependent. FID is distributional, not paired perceptual preservation.
