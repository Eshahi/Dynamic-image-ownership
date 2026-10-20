# RAVEN : Erasing Invisible Watermarks via Novel View Synthesis

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-raven`; citation key: `T8_raven`.
- Authors: Fahad Shamshad; Nils Lukas; Karthik Nandakumar.
- Year/version/venue: 2026; `2601.08832v1`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2601.08832v1); source type: primary preprint; access: 2026-10-20.
- Inspected: §3 cached481–505; §4 setup1291–1312; evaluation1429–1474.
- Original cached artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-raven.html`; SHA-256 `a0bdfdff7e0c81be8ad4d1aa01d1cd29feac57fa34bbc81ebba5ce0cf14635d6`.
- Readable artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-raven.txt`; SHA-256 `43764fabf06086a49f8579890514205d255b300b7f5ac4959ae46485ff846500`.
- Document licence: CC BY-NC-SA 4.0. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** RAVEN introduces novel-view image transformations with partial inversion and cross-frame attention. Its generative attack can retain a recognizable scene while shifting spatial content enough to disrupt a watermark, so semantic similarity and exact content binding are separate observables.

**Direct evaluation evidence.** Setup includes unknown empty prompts, CFG2.5 and a .15 refiner setting; evaluation reports TPR at 1% FPR. Source pools and generated outputs have different counts, and the paper has unresolved counts of methods across abstract, list and table; no invented unified denominator is supplied.

**Limits and contrary evidence.** Novel-view editing changes geometry and is outside the frozen T3 empty-prompt regeneration grid. Prompt/scene consistency is not proof of image identity or imperceptibility.

**Agent inference for this experiment.** A fixed regenerator pass supports no universal robustness claim over semantic editing; readable-code/content-match decomposition is necessary even when a quality metric stays favorable.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
