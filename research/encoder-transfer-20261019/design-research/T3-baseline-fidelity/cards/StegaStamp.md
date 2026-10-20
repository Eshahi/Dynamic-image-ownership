# StegaStamp: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **StegaStamp: Invisible Hyperlinks in Physical Photographs**. Version/date: arXiv:1904.05343v2 [cs.CV] 26 Mar 2020. Venue: CVPR 2020.

Authors: Matthew Tancik; Ben Mildenhall; Ren Ng. Year: 2019. DOI: not established for this inspected version.

Stable ID: `arxiv:1904.05343v2`. Citekey: `T3StegaStamp1904`. Canonical URL: https://arxiv.org/abs/1904.05343v2

Primary full text: https://arxiv.org/html/1904.05343v2

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/stegastamp.txt`
SHA-256: `4c06b800c078acaae1cfb45c0adbe2b7e06633bda49903c21d319777631ba4d4`

Actually inspected: §§4.1–4.4 encoder/decoder/BCH and print-camera pipeline; §§5.1–5.5 and Table 2; official README/LICENSE.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A U-Net residual encoder and spatial-transformer CNN decoder learn robustness to the print-camera channel. Photograph localization may use a separate segmentation model; it is not a calibrated arbitrary-image watermark detector.

## Native operating point and detector side information

Native images are 400×400 with 100 physical bits. The public text encoder accepts at most 7 bytes (56 useful bits), adds BCH parity and padding; arbitrary 100-bit research payloads are a distinct operating point. Preserve RGB conversion, resizing and native TensorFlow quantization if proposed. No universal numerical image-presence threshold is published. The detector needs an expected message for queried-message presence; BCH decoding alone is a different endpoint.

## Code, weights, pinned release and licenses

tancik/StegaStamp@c984446048b826587ca1875027b0a1dc1885fb30, MIT code. README references saved_models/stegastamp_pretrained; exact stable checkpoint artifact/hash not verified. TensorFlow 1.13-era execution dependency; no install attempted and no port is counted as faithful release.

## Published evaluation and regeneration conditions

The original paper evaluates physical print-camera corruption: 1,890 photographs from 105 samples across 18 conditions, mean bit accuracy 98.7%. Its 500-image quality evaluation reports PSNR 28.50, SSIM .905 and LPIPS .101 for 100 bits. VINE Table 1 instead reports stochastic/deterministic regeneration TPR 91.09/92.13% at .1% FPR, with quality 29.65/.9107/.0645; use the VINE card's 512-pixel preprocessing, attack scripts and unresolved count conflict. ZoDiac Table 15 uses 96 bits and threshold 61/96, with observed FPR .056: at 40/60/80/100/120/140/160/180/200 denoising steps, WDR is .588/.286/.098/.032/.010/.002/.002/0/0. That is neither native 100-bit+BCH nor equal-FPR evidence. Exact attack model revision, sampler and prompt are not fully specified there.

## Cost and uncertainty

VINE Table 7 reports .0672 seconds and 1,984 MB on Quadro RTX6000, averaging 1,000 images. Target-server timing and peak VRAM remain unmeasured; legacy TensorFlow compatibility creates engineering uncertainty.

## Limitation and design implication

P2 remains a recognizable historical comparator, but its native quality is below the thesis's strict clean gate. Keep its quality failure visible instead of rescaling it after seeing outcomes. It is a proposal only.

Disposition: **P2 retained, deferred until artifact and faithful runtime preflight; excluded.**
