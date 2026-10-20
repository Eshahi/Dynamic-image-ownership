# Robust Watermarking Using Generative Priors Against Image Editing: From Benchmarking to Advances

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-vine`; citation key: `T8_vine`.
- Authors: Shilin Lu; Zihan Zhou; Jiayou Lu; Yuanzhi Zhu; Adams Wai-Kin Kong.
- Year/version/venue: 2024; `2410.18775v2`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2410.18775v2); source type: primary preprint; access: 2026-10-20.
- Inspected: §3.1–3.3 and §4.1; cached375–513; §4.2–4.3/Table1 cached730–793.
- Original cached artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-vine.html`; SHA-256 `f6fb25d7b27ec0e95f883674e2e08a41a9075f5929e76287f02330e339e049dd`.
- Readable artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-vine.txt`; SHA-256 `46787d558a32df39faa09346ec501f618c75cbb7b080743b1e96bcbf45b2844e`.
- Document licence: arXiv.org perpetual non-exclusive license. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** VINE uses a generative-prior image writer, residual adaptation to higher resolution, a 100-bit extractor, and blur/noise augmentation as a proxy for regeneration. W-Bench distinguishes stochastic regeneration, deterministic inversion, global/local editing and video. The paper describes an SDXL-Turbo prior, while the inspected official released constructor uses SD-Turbo; preserve that disagreement.

**Direct evaluation evidence.** OpenImages training uses 256-pixel inputs and testing applies residuals at 512. Section4.2 partitions 10,000 UltraEdit sources into 1k stochastic,1k deterministic,1k global,5k local,1k video,1k distortion; Table1 instead says5,000 images per edit. Both denominators remain recorded rather than repaired. TPR at fixed empirical FPR is more specific than mean bit accuracy or AUROC.

**Limits and contrary evidence.** This is an author evaluation, not a native universal cutoff. Training on editing proxies and paper/release lineage mismatch limit the inference of unseen encoder transfer.

**Agent inference for this experiment.** Use the pinned VINE-R release, retain its own writer quality and public expected-message side information; native and common presence results need distinct labels.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
