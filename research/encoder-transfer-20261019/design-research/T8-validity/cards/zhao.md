# Invisible Image Watermarks Are Provably Removable Using Generative AI

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-zhao`; citation key: `T8_zhao`.
- Authors: Xuandong Zhao; Kexun Zhang; Zihao Su; Saastha Vasan; Ilya Grishchenko; Christopher Kruegel; Giovanni Vigna; Yu-Xiang Wang; Lei Li.
- Year/version/venue: 2023; `2306.01953v3`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2306.01953v3); source type: primary preprint; access: 2026-10-20.
- Inspected: §3–4 cached136–220 (Theorem4.3 at 198–205, utility206–220); §5 cached221–240.
- Original cached artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/zhao.html`; SHA-256 `41861c3d032d039a001feb23c58c8a322b0e38c27ad70b382acfc84d96423582`.
- Readable artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/zhao.txt`; SHA-256 `9b990e8a3e30598523ed1d8b0a01bc80c0acee98d9aed2a73454fb600e6a851a`.
- Document licence: arXiv perpetual non-exclusive. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** The attack corrupts an embedding with additive equal-covariance Gaussian noise and applies a common downstream generator. Its detection-error tradeoff is controlled by embedded marked/clean separation relative to noise. The utility result assumes the generator denoises unmarked inputs well; it does not conjure fidelity from a removal bound.

**Direct evaluation evidence.** Experiments use SD2.1 regeneration with PNDM,500 MS-COCO and500 generated sources, and include a theoretical/empirical DwtDctSvd tradeoff illustration. Their binomial bit threshold is a model for a particular null, not a universal media FPR calibration.

**Limits and contrary evidence.** A real VAE posterior has input-dependent mean and variance. Posterior sampling, mode-only D1, changed prompts and preprocessing are not automatically the same theorem. Large encoder gain weakens an impossibility bound; it does not prove survival.

**Agent inference for this experiment.** State the whole attack channel. Interpret independent-SDXL failure as channel susceptibility, and a pass as survival on that channel, without claiming causal isolation or contradiction of the theorem.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
