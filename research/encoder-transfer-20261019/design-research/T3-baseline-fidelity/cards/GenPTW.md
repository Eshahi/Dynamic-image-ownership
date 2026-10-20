# GenPTW: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **GenPTW: Latent Image Watermarking for Provenance Tracing and Tamper Localization**. Version/date: arXiv:2504.19567v2 [cs.CR] 21 Jan 2026. Venue: AAAI 2026, 40(5):4085–4093, DOI 10.1609/aaai.v40i5.37412; the inspected evidence version is arXiv v2.

Authors: Zhenliang Gan; Chunya Liu; Yichao Tang; Binghao Wang; Shiwen Cui; Weiqiang Wang; Xinpeng Zhang. Year: 2025. DOI: 10.1609/aaai.v40i5.37412.

Stable ID: `arxiv:2504.19567v2`. Citekey: `T3GenPTW2504`. Canonical URL: https://arxiv.org/abs/2504.19567v2

Primary full text: https://arxiv.org/html/2504.19567v2

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/genptw-latest.txt`
SHA-256: `4b361ce0840afc49746f97b5cca8e8d5d32da5a178ca25f366033bfe27f9756c`

Actually inspected: Method: Overall Framework, Multiscale Latent Embedding, CAF/SF, Tamper-Aware Extractor; Experimental Setup, Tables 1–3, Comparison with Deep Watermarking.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A shared latent watermark framework supports both in-generation and post-hoc use, with multiscale insertion, cross-attention fusion, skip fusion and a tamper-aware extractor. Only the existing-image post-hoc path contributes to this count.

## Native operating point and detector side information

Post-hoc evaluation uses 64 raw bits at 512 pixels, a pretrained autoencoder with inserted trained modules and a ConvNeXt multiscale extractor. No ECC or universal calibrated presence threshold is specified. Localization F1/AUC is a separate endpoint. Exact checkpoint preprocessing and quantization remain unavailable.

## Code, weights, pinned release and licenses

Exact-title web search found no verified official GenPTW code or weights. Source pin, artifact hash and implementation license are unresolved. The AAAI entry and inspected arXiv v2 establish publication/evaluation evidence, not runnable availability.

## Published evaluation and regeneration conditions

Table 2's post-hoc quality is PSNR 35.56, SSIM .864, LPIPS .077 and DISTS .002. Post-hoc bit accuracies are .963 for Prompt-to-Prompt, .975 for SDIP+ regeneration, .998 for SDIP and .997 for LaMa. The in-generation quality 39.56/.892 belongs to another operating point. The study uses 5,000 natural COCO images and 1,000 SD-v2-generated images, with UltraEdit prompts/masks for attacks. Exact attack strength, sampler, steps and revisions are unreported; a training prompt of None must not be presented as the test prompt. No calibrated TPR is provided.

## Cost and uncertainty

No adequately conditioned post-hoc inference time or peak memory was established. An autoencoder roundtrip and extractor are required; in-generation incremental cost cannot stand in for post-hoc end-to-end cost.

## Limitation and design implication

Closes an important recent latent post-hoc omission and exposes the need to separate generation and post-hoc quality. The reported SSIM fails the thesis's strict clean gate; no new core arm is proposed.

Disposition: **Literature coverage; excluded**
