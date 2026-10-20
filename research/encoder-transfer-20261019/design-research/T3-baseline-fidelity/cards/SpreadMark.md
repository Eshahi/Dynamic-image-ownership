# SpreadMark: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **SpreadMark: Robust Image Watermarking via Spread-Spectrum Embedding**. Version/date: arXiv:2608.03165v2 [cs.CR] 18 Aug 2026. Venue: arXiv 2026 preprint; v2 inspected and differs numerically from v1.

Authors: Wei Song; Yuxin Cao; Zhenchang Xing; Liming Zhu; Jin Song Dong; Yulei Sui; Jingling Xue. Year: 2026. DOI: not established for this inspected version.

Stable ID: `arxiv:2608.03165v2`. Citekey: `T3SpreadMark2608`. Canonical URL: https://arxiv.org/abs/2608.03165v2

Primary full text: https://arxiv.org/html/2608.03165v2

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/spreadmark-v2.txt`
SHA-256: `d12bf733f7f9094c7e847dd10ac29082e42b5f41fc47a7b204d7e00d26b97b24`

Actually inspected: Method 'Spread-Spectrum Embedding', 'Receiver', SA-AT; experimental setup, Tables 1–2, Ablations and Discussion; v1-to-v2 diff inspected.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A spread-spectrum image encoder and receiver use a secret codebook, learned embedding and synchronization-aware adversarial training. The method marks existing images.

## Native operating point and detector side information

The evaluated setting has 30 bits at 128×128. Detection uses an analytic 1% binomial criterion, without verified empirical image-FPR calibration. The secret fixed codebook is side information; chosen-message behavior and key-estimation resistance are not established. Quantization and exact preprocessing await an official release.

## Code, weights, pinned release and licenses

Exact-title web and GitHub searches found no verified official repository or weights. Code/model license, release pin and artifact accessibility are unresolved. The inspected v2 is authoritative for this card; v1 numbers are not silently copied.

## Published evaluation and regeneration conditions

The v2 main table reports COCO bit/detection accuracy .78/.77 and DIV2K .73/.60 under WAVES SD1.4 img2img strength .25 at 512 pixels, followed by resizing back to 128. Training uses 4,500 COCO images; testing states 500 COCO and 500 DIV2K validation images, the latter conflicting with the standard 100-image DIV2K validation split. Quality is 30.1/.874/.014 for COCO and 29.4/.891/.012 for DIV2K. At 256 pixels, reported detection approaches zero. The .85 bit-accuracy value belongs to another version/ablation, not the current main result. Exact sampler, steps, prompts and replication are incomplete; only one training seed is reported.

## Cost and uncertainty

A learned feed-forward implementation could be modest, but no verified official checkpoint or inference time/memory exists. Small 128-pixel training cannot be treated as a measured 512-pixel runtime.

## Limitation and design implication

New direct regeneration evidence, but low quality, resolution sensitivity, count ambiguity and unreleased artifacts make this a coverage result rather than a proposed arm.

Disposition: **Literature coverage; excluded**
