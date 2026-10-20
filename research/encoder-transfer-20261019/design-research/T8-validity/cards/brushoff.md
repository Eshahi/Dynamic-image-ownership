# BrushOff: Stroke-Based Re-rendering as a Watermark Removal Attack on Paintings

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-brushoff`; citation key: `T8_brushoff`.
- Authors: Hao Chen; Junnan Xu.
- Year/version/venue: 2026; `2610.26682v1`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2610.26682v1); source type: primary preprint; access: 2026-10-20.
- Inspected: §III–IV cached171–240; IV-C–E271–324; Table II/results325–365,540–554,600–661.
- Original cached artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T8-1b\brushoff.html`; SHA-256 `af33f29ecdcf4d761015133bdecefcb6eb682a37f2e33b4c0d26cc7839cf2c01`.
- Readable artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T8-1b\brushoff.read.txt`; SHA-256 `ef49588148f39302dadcf82872370895317cb895c9010081dd719b7defb6831c`.
- Document licence: arXiv perpetual non-exclusive. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** BrushOff converts images into a sequence of painted strokes using PaintTransformer, renders at different canvas sizes, and downsamples. This is a non-diffusion, stroke bottleneck relevant to image-domain marks. IV-C uses an independent, uniform decoded-bit null at 10^-3 plus0/500 empirical clean positives; neither certifies population image FPR.

**Direct evaluation evidence.** Five hundred WikiArt paintings span five styles. IV-C drops15 RivaGAN clean failures, predominantly flat Color Field images; this changes the attack denominator. Table I separately shows a DwtDct variant with 349 clean detections versus 500 for DwtDctSvd, which must not be conflated. Non-VINE2048 canvases use a100-image subset. IV-E measures attacked-to-clean fidelity only on VINE and applies it to other methods after a pilot assumption.

**Limits and contrary evidence.** Painting-only domain, one renderer, fixed payload, changed probes after results and visible texture changes limit generality. VINE-only quality does not prove cross-arm distortion equivalence. No F5 output was attacked.

**Agent inference for this experiment.** Keep fixed clean-failure denominators and arm-specific quality references in our core. Flag the new T1 attack-coverage gap; parent will commission its separate setting row/card. This card does not close that gap or add an experiment.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
