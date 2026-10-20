# InvisMark: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **InvisMark: Invisible and Robust Watermarking for AI-generated Image Provenance**. Version/date: arXiv:2411.07795v2 [cs.CR] 19 Nov 2024. Venue: WACV 2025, pp. 909–918; inspected arXiv v2.

Authors: Rui Xu; Mengya Hu; Deren Lei; Yaxi Li; David Lowe; Alex Gorevski; Mingyu Wang; Emily Ching; Alex Deng. Year: 2024. DOI: not established for this inspected version.

Stable ID: `arxiv:2411.07795v2`. Citekey: `T3InvisMark2411`. Canonical URL: https://arxiv.org/abs/2411.07795v2

Primary full text: https://arxiv.org/html/2411.07795v2

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/invis-reused.txt`
SHA-256: `e45a3b5375de5c9ae3f04aca3e10146b0474aada3476bcde89d8a692a435e7d0`

Actually inspected: §§2.1–2.4; §§3.1–3.5, Tables 2–3, Figure 4 and UUID extension.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A learned high-resolution residual encoder and ConvNeXt decoder optimize visual quality and distortion robustness. The training set includes 100,000 privately generated DALL-E 3 images.

## Native operating point and detector side information

The main paper uses 100-bit messages. Its separate 256-bit BCH extension carries a 128-bit UUID; these are different capacities and operating points. High-resolution evaluation is established, but the inspected paper text does not establish the exact released encoder input size. Native clamp, interpolation, serialization and an image-presence threshold need release verification. Pixel Seal reports six fixed bits in the 100-bit implementation, implying only 94 varying bits in that comparison; this is a third-party observation, not a newly measured result.

## Code, weights, pinned release and licenses

microsoft/InvisMark@8d5ce55705ada1c2daf642c97f7ff3ae6dbd1825, MIT repository. Official README OneDrive checkpoint folder available as a pointer; immutable revision/hash and durable direct artifact access not verified. Private 100k DALL-E 3 training images unavailable; do not replace weights with retraining and call it native.

## Published evaluation and regeneration conditions

Section 3.3/Figure 4 evaluates SD2.1 regeneration at noise settings 1, 3, 5, 10, 20, 60 and 100 on 10 images. Bit accuracy approaches chance near attacked PSNR 25 dB. Per-setting bit accuracy is graphical and was not digitized; no exact scalar is invented. Sampler, prompts, seed replication and exact count per condition are incompletely reported. Table 2 reports clean PSNR 51.4 and SSIM .998 on 900 DIV2K and 900 DALL-E 3 images. High clean quality does not establish regeneration detection.

## Cost and uncertainty

A released feed-forward encoder/decoder would avoid per-image optimization. No adequately conditioned target inference time or peak memory was established; any future estimate must include the high-resolution residual path and actual checkpoint.

## Limitation and design implication

A useful high-quality comparator for later work, but checkpoint provenance, fixed-bit structure and regeneration weakness prevent treating it as a turnkey replacement for a core arm.

Disposition: **Literature coverage; excluded**
