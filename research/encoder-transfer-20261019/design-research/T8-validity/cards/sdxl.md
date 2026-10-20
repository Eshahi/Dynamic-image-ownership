# SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-sdxl`; citation key: `T8_sdxl`.
- Authors: Dustin Podell; Zion English; Kyle Lacey; Andreas Blattmann; Tim Dockhorn; Jonas Müller; Joe Penna; Robin Rombach.
- Year/version/venue: 2023; `2307.01952v1`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2307.01952v1); source type: primary preprint; access: 2026-10-20.
- Inspected: §2.4/Table3 cached1093–1164; §2.5 preference evaluation1190–1289; header114–127.
- Original cached artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sdxl-paper.txt`; SHA-256 `f50bf5a2c55213b90feb5c37d3059ea60d7509ed181ce78ef496df3753082efd`.
- Readable artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T5-1b\sdxl-paper.read.txt`; SHA-256 `e0f0e615b71bf00cfe64b2101ac73a3154d57e9b2ead21af22193719cca7df4b`.
- Document licence: CC BY 4.0. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** SDXL explicitly trains its autoencoder from scratch while retaining the SD1/SD2 architecture class; larger batch256 versus 9 and EMA are described. In contrast SD2 fine-tunes the decoder with the SD1 encoder retained. Architecture family and trained-weight ancestry are separate axes.

**Direct evaluation evidence.** Table3 evaluates reconstruction on COCO2017 validation at 256 pixels; the subsequent synthesis preference study includes model/refiner conditions. These measurements do not evaluate watermark retention at the core1024 img2img path.

**Limits and contrary evidence.** The paper establishes a different autoencoder training run, not independence of training data, learned features, latent directions or generative priors. The core excludes the refiner, so its behavior cannot inherit complete base-plus-refiner preference claims.

**Agent inference for this experiment.** Call R1 an independently trained SDXL autoencoder pipeline, retain the shared latent architecture/prior caveat, and do not turn R0/R1 into a clean causal experiment on encoders alone.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
