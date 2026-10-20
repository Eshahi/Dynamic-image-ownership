# UnMarker: A Universal Attack on Defensive Image Watermarking

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-unmarker`; citation key: `T8_unmarker`.
- Authors: Andre Kassis; Urs Hengartner.
- Year/version/venue: 2024; `2405.08363v2`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2405.08363v2); source type: primary preprint; access: 2026-10-20.
- Inspected: §4 high-frequency cached508–560; low-frequency730–755; §6 setup801–872; evaluation1095–1130.
- Original cached artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-unmarker.html`; SHA-256 `f7cf99c1482bdd9df24b712855c33bff6a8ec8db4466157db02ac5bda9b52002`.
- Readable artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-unmarker.txt`; SHA-256 `9f714df1fd412d702a34b8a1e0c35496ea3a23f7c70792ccc90a2ed490837c18`.
- Document licence: CC BY-NC-ND 4.0. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** UnMarker uses spectral/perceptual optimization with high-frequency and low-frequency stages, without requiring a target VAE or watermark detector queries. This supplies a materially different attack path from fixed partial-noise diffusion.

**Direct evaluation evidence.** The evaluation uses 100 images per method and different detector operating rules (including modeled bit thresholds and Tree-Ring calibration). Quality includes LPIPS-VGG, deliberately different from the optimization loss. The authors use an operational detection/security rule that must not be substituted for this study's fixed source-majority rule.

**Limits and contrary evidence.** Broad universal-removal language exceeds what a finite method/grid evaluation can prove. Selected losses and image sets are still conditional choices. No exact attack was run against F5 here.

**Agent inference for this experiment.** A transfer pass leaves adaptive spectral and query-free attacks unresolved. Metric agreement is evidence about fidelity, not a human verdict or a security guarantee.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
