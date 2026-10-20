# MarkNull : Model-Agnostic Watermark Removal in AI-Generated Images via On-Manifold Latent Manipulation

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-marknull`; citation key: `T8_marknull`.
- Authors: Jie Cao; Qi Li; Zelin Zhang; Xiaodong Wu; Lingshuang Liu; Xiangman Li; Jianbing Ni.
- Year/version/venue: 2026; `2608.10166v1`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2608.10166v1); source type: primary preprint; access: 2026-10-20.
- Inspected: §3 NLAS/perceptual training cached722–765; §4 setup1236–1280; evaluation2430–2475.
- Original cached artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-marknull.html`; SHA-256 `522723a9664b1226762fda200c4b758a2b16476f6552d27c1e081b124bf1ff32`.
- Readable artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-marknull.txt`; SHA-256 `3bde4c2ad7a121631e79303cf5d5dee9024ec75c290107c68c5a7c022d7e58b4`.
- Document licence: arXiv.org perpetual non-exclusive license. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** MarkNull constructs a latent near-orthogonality/perceptual objective and amortizes removal in a learned network. The paper interprets orthogonality as independence; that interpretation is not a general probabilistic theorem and is not imported into this analysis.

**Direct evaluation evidence.** Nine watermark baselines use100 images per method. Generative methods use SD2.1 images; post-hoc methods use SDXL images, with an SD1.5 proxy for parts of removal. Multi-bit bit accuracy and zero-bit TPR are reported as different tasks.

**Limits and contrary evidence.** This is an adaptive trained attacker with method/dataset choices, not the frozen honest SDXL regenerator. Cross-method averages can mix different clean hosts and endpoint classes.

**Agent inference for this experiment.** Keep current causal scope narrow and do not compare F5 C directly to literature mean BA as if the denominators, payloads and attacker access matched.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
