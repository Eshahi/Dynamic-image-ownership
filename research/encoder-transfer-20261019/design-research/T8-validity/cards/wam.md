# Watermark Anything with Localized Messages

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-wam`; citation key: `T8_wam`.
- Authors: Tom Sander; Pierre Fernandez; Alain Durmus; Teddy Furon; Matthijs Douze.
- Year/version/venue: 2024; `2411.07231v2`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2411.07231v2); source type: primary preprint; access: 2026-10-20.
- Inspected: §3 dense extraction/pooling cached532–619; §5.1 setup898–935; §5.3 detection 1158–1208; Table 2a 1221–1345.
- Original cached artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T5-1b\paper-wam.txt`; SHA-256 `7740219ef33108335cec4aea085448f31d14c990b3cf8f5fe8cc78c5cbf03213`.
- Readable artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T5-1b\paper-wam.txt`; SHA-256 `7740219ef33108335cec4aea085448f31d14c990b3cf8f5fe8cc78c5cbf03213`.
- Document licence: CC BY 4.0. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** WAM predicts a per-pixel presence mask and per-pixel message logits. Its image decision uses the fraction of mask pixels crossing a threshold, while message inference averages selected pixel predictions. This makes empty masks and the order of aggregation substantive detector behavior.

**Direct evaluation evidence.** The paper trains 32-bit, 256-pixel COCO models. Section 5.3 gives a nominal 2.6e-4 fair-bit false-positive tail for the other baselines' 16-bit, at-most-one-error rule. WAM instead uses mask fraction>.07 and is described as having an approximately similar empirical COCO FPR; Table 2a reports WAM FPR 0.04% (4e-4), not exactly 2.6e-4. Those weights and population differ from the MIT SA-1B core release. Its own related-work discussion explicitly notes decoded bits need not be equiprobable or independent.

**Limits and contrary evidence.** Neither the paper calibration nor the random-message tail establishes image FPR for the released MIT model. The official semihard raw-logit threshold differs from a tempting sigmoid-mean implementation.

**Agent inference for this experiment.** Preserve native mask rule and release pooling; label common queried-message presence separately and report observed negatives without borrowing paper calibration.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
