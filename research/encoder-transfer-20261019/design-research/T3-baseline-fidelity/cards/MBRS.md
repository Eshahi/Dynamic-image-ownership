# MBRS: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **MBRS : Enhancing Robustness of DNN-based Watermarking by Mini-Batch of Real and Simulated JPEG Compression**. Version/date: arXiv:2108.08211v1 [cs.CV] 18 Aug 2021. Venue: ACM Multimedia 2021 oral, official README.

Authors: Zhaoyang Jia; Han Fang; Weiming Zhang. Year: 2021. DOI: not established for this inspected version.

Stable ID: `arxiv:2108.08211v1`. Citekey: `T3MBRS2108`. Canonical URL: https://arxiv.org/abs/2108.08211v1

Primary full text: https://arxiv.org/html/2108.08211v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/mbrs.txt`
SHA-256: `aa8e81d5f9cdc45cbd158c985a430d31c44d1529e03930ce06211e5c340e3f54`

Actually inspected: §§3.1–3.3,4.1–4.2; official README, repository tree and release metadata.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A neural image encoder and decoder train with mini-batches containing real JPEG, simulated JPEG and identity corruption, allowing gradients to flow on only the differentiable branches.

## Native operating point and detector side information

The original paper studies 64 bits at 128×128 and 625 bits at 400×400. Official released configurations include 30 bits at 128 and 256 bits at 256; these cannot be treated as one interchangeable payload. No universal image-presence cutoff is published. Exact clamp, serialization and normalization must be tied to the selected release.

## Code, weights, pinned release and licenses

jzyustc/MBRS@2bab0df66480f66cfdef534d38c851354ee2c6aa. Official code and Google Drive weights folder https://drive.google.com/drive/folders/1A_SAqvU2vMsHxki0s9m9rKa-g8B6aghe?usp=sharing. No LICENSE file in inspected tree/API license null; license unverified, not MIT by assumption. Checkpoint hashes/immutable revisions unresolved.

## Published evaluation and regeneration conditions

Original training uses 10,000 ImageNet images and evaluation 5,000 COCO images. The paper reports BER below .01% at JPEG quality 50 with PSNR above 36 dB, but no original diffusion-regeneration evaluation. VINE's 30-bit MBRS baseline has quality 27.37/.8940/.1877 and stochastic/deterministic TPR 99.53/99.35% at .1% FPR. That result uses VINE's attack scripts and unresolved source-count statements, not the original paper's native quality or a matched SDXL test.

## Cost and uncertainty

VINE Table 7 reports .0053 seconds and 938 MB on Quadro RTX6000, mean over 1,000 images. This is a third-party configuration and hardware measurement, not a local estimate.

## Limitation and design implication

A strong illustration of quality/robustness confounding: its high regeneration TPR in VINE comes with very low clean quality. Missing license evidence also blocks a ready-to-run proposal.

Disposition: **Literature coverage; excluded**
