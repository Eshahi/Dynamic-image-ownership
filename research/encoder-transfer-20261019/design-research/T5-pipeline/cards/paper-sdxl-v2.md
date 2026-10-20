# SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis

[Primary source](https://arxiv.org/html/2307.01952v1). Verification level **V2: methods and evaluation inspected**. Recheck date2026-10-20.

**V2 recheck completed:** §2.4 autoencoder, §2.5 training/refiner; Table3 and the generation evaluation/user-study passages were independently reread.

**Mechanism:** the authors state the SDXL autoencoder is trained from scratch with the same architecture as Stable Diffusion's, larger batch256 versus9 and EMA. This is positive training-lineage evidence for an independently trained autoencoder, not independent training images or a different architecture. Native1024 conditioning and optional separate refiner are distinct choices.

**Evaluation reread:** Table3 reports reconstruction on COCO2017 validation resized256; §2.5 reports a1024-capable training progression and generation preference study. Reported48.44% preference for base+refiner versus36.93% base alone concerns those displayed generation comparisons, not watermark robustness.

**Audit use / limits:** justify SDXL as an independent-autoencoder transfer challenge and keep base-only/no-refiner explicit. Reconstruction metrics at256 do not measure1024 fp32-VAE peak memory or the efficacy of R1/D1. Paper statements do not justify replacing official fp16 checkpoint values with fp16-fix weights.

**Read locations:** `sdxl-paper.read.txt:1093–1163,1190–1350`.
