# DREW: Towards Robust Data Provenance by Leveraging Error-Controlled Watermarking

T8 own V2 card, independently rechecked 2026-10-20. V2 is inspection depth, not arXiv revision.

- Stable ID: `T8-drew`; citation key: `T8_drew`.
- Authors: Mehrdad Saberi; Vinu Sankar Sadasivan; Arman Zarei; Hessam Mahdavifar; Soheil Feizi.
- Year/version/venue: 2024; `2406.02836v2`; arXiv preprint; final venue not independently verified. DOI: null (not independently verified).
- Canonical primary: [versioned paper](https://arxiv.org/html/2406.02836v2); source type: primary preprint; access: 2026-10-20.
- Inspected: §3.3 Algorithm2/§3.4 cached120–178; §4.1–4.2 cached431–461; AppendixC675–690.
- Original cached artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\C6\drew2406v2.html`; SHA-256 `d0d998083d31e9409064b6c1fe1ec2d8e80c502e51abda3ba2ea70cca48fcb42`.
- Readable artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T8-1b\drew.read.txt`; SHA-256 `bda03736bee7714a47e03227cea42a2b1798753e62e86c9074ff55637241bdcf`.
- Document licence: arXiv perpetual non-exclusive. Paper document licence only; code/model/media licences are separate. Local scholarly inspection; no checkpoint/media redistribution or new use rights inferred.

**Direct method evidence.** DREW assigns database records to error-corrected watermark clusters and retrieves a continuous descriptor within the decoded cluster. Unreliable decoding triggers full-database retrieval. The reference database and retrieval threshold are detector side information, unlike the current reference-free core.

**Direct evaluation evidence.** Experiments use100-bit marks,10 cluster bits,1024 clusters,768-dimensional DINOv2/CLIP features, six datasets and1000 queries per dataset/modification. Diffusion modification is included. AppendixC considers descriptor evasion while wrong-cluster spoofing remains future robustness work.

**Limits and contrary evidence.** Retrieval success is not authenticity, exclusive ownership or secure content binding. This paper is direct prior art for a registry hybrid, so an unqualified first-hybrid claim is untenable; it does not authorize adding a registry here.

**Agent inference for this experiment.** State that the current experiment measures owner/content evidence under fixed side information. Do not substitute prior or future registry results for independent encoder transfer.

**Open assumption.** The pinned implementation and selected development cohort may behave differently. This card contains no reproduction, new detector call or outcome.
