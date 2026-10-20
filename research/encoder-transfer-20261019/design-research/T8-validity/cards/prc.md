# An undetectable watermark for generative image models

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-prc`; citation key: `T8_prc`.
- Authors: Sam Gunn; Xuandong Zhao; Dawn Song.
- Year/version/venue: 2024; `2410.07369v4`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2410.07369v4); source type: primary preprint; access: 2026-10-20.
- Inspected: Construction cached165–210 and232–267; experiments268–281,383–407.
- Original cached artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/prc.html`; SHA-256 `e7f8017500b50dfcebf62d9899346fbfebff5162dab0b62d132b60b6facb776b`.
- Readable artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/prc.txt`; SHA-256 `b3c2f6f7eb04a72663825b1fe783bdf65a9d869da284ea4a5a4ef624babe77af`.
- Document licence: arXiv perpetual non-exclusive. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** PRC watermarks encode pseudorandom-code signs in initial generative latents and recover them through inversion. Theoretical undetectability is computational and assumption/parameter dependent. The false-positive theorem quantifies over a random independent key for a fixed image; it is not a fixed public-key image-distribution theorem.

**Direct evaluation evidence.** The authors evaluate500 SD2.1 images and512-bit message decoding with GPU inversion, report TPR at 1% FPR and distinguish more robust detection from less robust decoding. Larger unattacked payload demonstrations do not establish robust capacity. The authors expressly warn their finite experimental parameters do not meet all asymptotic proof bounds.

**Limits and contrary evidence.** Public deterministic F5 chips, content-derived codes and expected-message checks do not inherit PRC secrecy, undetectability, unforgeability or random-key quantifiers.

**Agent inference for this experiment.** Use the paper to clarify the missing assumptions behind cryptographic claims; this is a measured development carrier/binding study, not a proof of legal ownership or adversarial authenticity.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
