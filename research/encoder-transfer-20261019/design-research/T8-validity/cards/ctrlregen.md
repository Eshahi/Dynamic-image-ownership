# Image Watermarks are Removable Using Controllable Regeneration from Clean Noise

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-ctrlregen`; citation key: `T8_ctrlregen`.
- Authors: Yepeng Liu; Yiren Song; Hai Ci; Yu Zhang; Haofan Wang; Mike Zheng Shou; Yuheng Bu.
- Year/version/venue: 2024; `2410.05470v2`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2410.05470v2); source type: primary preprint; access: 2026-10-20.
- Inspected: §3 cached74–120 including semantic/spatial controls; evaluation cached301–330.
- Original cached artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/ctrlregen.html`; SHA-256 `8167b5480d5f4a71a9ec4b298c9c00e26d6b9c9dab98e0935af42a0e071d14df`.
- Readable artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/ctrlregen.txt`; SHA-256 `5fad65c1fc3d6f3ed8677189b04575e6d53af73ff908909a1be0a9d48832ed58`.
- Document licence: CC BY-NC-SA 4.0. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** CtrlRegen starts from fresh noise and conditions generation on DINOv2 semantic features and image edges; CtrlRegen+ also uses a partially noised image latent with adaptive strength. The conditioning channels can retain image details and are part of the attacker, not evidence of a watermark-free latent by definition.

**Direct evaluation evidence.** Evaluation uses 1000 MIRFLICKR real images and1000 DiffusionDB generated images. The trained control model uses an SD1.5 backbone and substantial training hardware; inference cost and training cost are different quantities. Empty text prompts do not remove image conditioning.

**Limits and contrary evidence.** This is not pixel diffusion or a ready independently trained replacement for the current SDXL path. Its strong conditional control and trained/adaptive attack are outside core.

**Agent inference for this experiment.** Record unresolved attack-family coverage without silently adding training or a new baseline. A surviving carrier need not be a semantic code, and preserving scene descriptors need not preserve the carrier.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
