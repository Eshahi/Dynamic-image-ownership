# ZoDiac: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **Attack-Resilient Image Watermarking Using Stable Diffusion**. Version/date: arXiv:2401.04247v2 [cs.CV] 28 Oct 2024. Venue: NeurIPS 2024 main track; official proceedings verified; numerical evidence is inspected arXiv v2.

Authors: Lijun Zhang; Xiao Liu; Antoni Viros Martin; Cindy Xiong Bearfield; Yuriy Brun; Hui Guan. Year: 2024. DOI: not established for this inspected version.

Stable ID: `arxiv:2401.04247v2`. Citekey: `T3ZoDiac2401`. Canonical URL: https://arxiv.org/abs/2401.04247v2

Primary full text: https://arxiv.org/html/2401.04247v2

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/zodiac-reused.txt`
SHA-256: `3711f3a711ecdba59e4d05d677216029d1398584330fba1d5a046b4ab1647488`

Actually inspected: §§3.2–3.3,4.1; Appendix B.6/Table 15,B.7/Table 16 and Appendix D timing/memory.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

Per-image optimization writes a Fourier-ring watermark into an image's diffusion latent using DDIM inversion and a structural-similarity constraint. Verification requires diffusion inversion and a keyed ring test; this is a zero-bit post-hoc method.

## Native operating point and detector side information

The default uses SD2.1-base at 512×512, ring radius 10 in the last latent channel, 100 Adam iterations, 50 denoising steps and target SSIM .92. The stated default detection condition is 1-p>.9. It is not a multi-bit payload, and the expected ring/key and generator are detector side information. The published thresholds have percent-level measured FPR, far above the study's analytic common-query target.

## Code, weights, pinned release and licenses

zhanglijun95/ZoDiac@89f864d2e4f6f33663dc69b4d99bee49073e194c. Code inspected; no repository license verified (public accessibility is not a license). Requires SD2.1-base; weight/dependency permissions and full reproducible pin not resolved for a proposed run. No checkpoint download or inference performed.

## Published evaluation and regeneration conditions

The evaluation uses 500 images from each of MS-COCO, DiffusionDB and WikiArt. Default learned-compression attacks use bmshj/cheng quality 3; Zhao23 regeneration uses 60 steps. Appendix Table 15's COCO strength study reports, at p*=.95 and observed FPR .032, WDR .980/.974/.950/.940/.924/.912/.894/.866/.818 for 40/60/80/100/120/140/160/180/200 steps. At p*=.90 and FPR .062, the corresponding values are .988/.988/.964/.970/.952/.946/.938/.926/.898. Attack PSNR falls from 27.15 to 22.44. The prose says .998 to .898 whereas the first table entry is .988; preserve the discrepancy. Exact attack revision, sampler and prompt are incompletely specified.

## Cost and uncertainty

Appendix D reports RTX8000 fp32 peak memory 15,552 MiB and model storage 5,308 MiB. Embedding is 255.94/159.47/65.35/45.41 seconds with 50/30/10/1 steps. Table 16 gives quality 29.41/.92/.09. These reported costs and quality differ substantially from a feed-forward high-quality baseline.

## Limitation and design implication

Useful counterevidence to sweeping removal claims, but its detector cost, side information, image quality and high FPR preclude a fair substitution into the cheap core.

Disposition: **Literature coverage; excluded**

## Parent bibliographic correction, 2026-10-20

The official [NeurIPS 2024 proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/43d33182360378d5c8e69dd706c24f2f-Abstract.html) establishes the venue. The earlier ACM Multimedia label was incorrect. This metadata correction does not substitute final-paper numbers for the explicitly inspected arXiv v2 evaluation. Cache receipt: `venue-correction.json`.
