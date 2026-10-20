# WAVES: Benchmarking the Robustness of Image Watermarks

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-waves`; citation key: `T8_waves`.
- Authors: Bang An; Mucong Ding; Tahseen Rabbani; Aakriti Agrawal; Yuancheng Xu; Chenghao Deng; Sicheng Zhu; Abdirisak Mohamed; Yuxin Wen; Tom Goldstein; Furong Huang.
- Year/version/venue: 2024; `2401.08573v3`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2401.08573v3); source type: primary preprint; access: 2026-10-20.
- Inspected: §3.1–3.2, §4–4.1; cached text 699–929; quality/detection and dataset setup.
- Original cached artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-waves.html`; SHA-256 `238ffa869b2b8424a92aeeef27e39d7b7909b33ed487a3d4e794e7e6f67e7a08`.
- Readable artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-waves.txt`; SHA-256 `690276accbb6797976feb292164895da991323a791f98f28b5e933fdf3ce915c`.
- Document licence: CC BY 4.0. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** WAVES separates presence detection from message identification, measures TPR at 0.1% FPR, and combines eight fidelity measures into dataset-dependent normalized quality. Its attack families include reconstruction, partial-noise diffusion, repeated regeneration and stronger access conditions. Repeated settings share the original sources. These are actual benchmark choices, not interchangeable definitions of survival.

**Direct evaluation evidence.** Three watermarks and three image sources are evaluated across 26 attacks. Reported aggregate performance over severities is not the detection count at a single frozen channel. Similar versus different autoencoder experiments motivate a transfer question but cannot determine F5 behavior.

**Limits and contrary evidence.** The normalization and attack grids are benchmark-specific. No F5 result, theorem of encoder independence, or calibrated SDXL operating point is supplied.

**Agent inference for this experiment.** Keep attack fidelity, total fidelity and fixed survival endpoints separate; a broad benchmark motivates explicit scope limits rather than copying its aggregate score.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
