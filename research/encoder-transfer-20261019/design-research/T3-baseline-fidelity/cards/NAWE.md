# NAWE: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **NAWE: Digital Watermarking with Neural-Assisted Watermark Extraction**. Version/date: arXiv:2609.25972v1 [cs.CV] 22 Sep 2026. Venue: arXiv 2026 preprint; venue unverified.

Authors: Roman Chaban; Vitaliy Kinakh; Lilian Rouzaire; Slava Voloshynovskiy. Year: 2026. DOI: not established for this inspected version.

Stable ID: `arxiv:2609.25972v1`. Citekey: `T3NAWE2609`. Canonical URL: https://arxiv.org/abs/2609.25972v1

Primary full text: https://arxiv.org/html/2609.25972v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/nawe.txt`
SHA-256: `a17025bad8105b739e66753a051a54a8e76b1074d4e609773f2b8678fb579222`

Actually inspected: §§3.1–3.3,4.1–4.4, robustness grid and OFAT evaluation.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A training-free denoising-residual carrier uses a pretrained denoiser, synchronization and error correction to recover a keyed payload from an existing image.

## Native operating point and detector side information

Native 512-pixel encoding uses 48 payload bits plus 16 CRC bits, Polar coding to 256 bits at rate 1/4, and 68 synchronization bits. The reported s2 setting uses GS-DRUNet sigma 18 and PSNR target 40. Key/nonce, synchronization search, RANSAC and CRC are detector-side information. Multiple candidate searches make a naive single-test CRC or binomial FPR unjustified. Exact rounding and serialization remain unverified.

## Code, weights, pinned release and licenses

Exact web and GitHub searches found no verified official NAWE implementation or weights. Public denoiser dependencies are not a NAWE release. License, immutable pin, preprocessing and artifact hashes remain unknown.

## Published evaluation and regeneration conditions

The robustness grid uses 100 COCO images; the one-factor-at-a-time evaluation covers 156 arms in 34 families on 100 images. These are conventional geometric/photometric distortions, not diffusion regeneration. OFAT BER .07 is computed on returned messages, whereas WER accounts for all messages; the conditioning matters. There is no direct regeneration model/strength/sampler/prompt/calibrated-TPR tuple.

## Cost and uncertainty

Training-free does not mean free inference: denoising, synchronization and candidate search are required. No sufficiently conditioned runtime or peak memory was established for the proposed server.

## Limitation and design implication

Relevant to synchronization and structured-payload false positives, but absent direct regeneration evidence and release prevent immediate addition.

Disposition: **Literature coverage; excluded**
