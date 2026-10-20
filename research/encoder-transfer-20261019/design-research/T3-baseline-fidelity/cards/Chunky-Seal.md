# Chunky-Seal: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **We Can Hide More Bits: The Unused Watermarking Capacity in Theory and in Practice**. Version/date: arXiv:2510.12812v1 [cs.CR] 07 Oct 2025. Venue: arXiv 2025 preprint; venue not verified.

Authors: Aleksandar Petrov; Pierre Fernandez; Tomáš Souček; Hady Elsahar. Year: 2025. DOI: not established for this inspected version.

Stable ID: `arxiv:2510.12812v1`. Citekey: `T3ChunkySeal2510`. Canonical URL: https://arxiv.org/abs/2510.12812v1

Primary full text: https://arxiv.org/html/2510.12812v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/chunkyseal.txt`
SHA-256: `a3f23c62ff925b4b5519f604eef09f9157229712c5ed6201c292b19a4f08e6f1`

Actually inspected: §5 model architecture/training/Table 3;§6 discussion and Appendix I.1 contextual evaluation.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A scaled VideoSeal-family image embedder and extractor write 1,024 bits in chunks. This is a separately trained, high-capacity post-hoc model, rather than another release counted as another method.

## Native operating point and detector side information

The pinned chunkyseal.yaml sets 1,024 bits, processing size 256, additive blending, scaling_w=.2, scaling_i=1 and JND jnd_1_1. It selects unet_chunky and convnext_chunky with no final sigmoid in the extractor; exact loader, residual interpolation and serialization still need adapter verification. Paper embedder/extractor sizes are approximately 1,022.7M/773.7M parameters. No universal calibrated presence threshold is established. High capacity must remain visible instead of truncating the message.

## Code, weights, pinned release and licenses

Correction to the initial search: the official VideoSeal README advertises ChunkySeal and its model zoo links a dedicated model card and checkpoint. facebookresearch/videoseal@870ca7fb33578b90f14c602016b6c2788096226e has an inspected MIT LICENSE and README explicitly covering code and models. The pinned videoseal/cards/chunkyseal.yaml points to https://dl.fbaipublicfiles.com/videoseal/chunkyseal/checkpoint.pth. The URL is mutable; bytes, SHA-256 and weight identity were not verified, and no weights were downloaded. The paper document license is separate from this official implementation license.

## Published evaluation and regeneration conditions

Table 3 at original SA-1B resolution reports PSNR 45.32±2.16, SSIM .995±.006, LPIPS .0085±.0067, identity bit accuracy 99.74±.28% and overall conventional-distortion accuracy 99.15±.63%. Distortions include rotation up to 10 degrees, resize 71–95%, crop 77–95%, brightness/contrast .5–1.5, JPEG 50–80 and blur kernel up to 9. The exact image count was not established from the inspected table. No direct diffusion-regeneration or calibrated TPR tuple is provided.

## Cost and uncertainty

At four bytes per parameter, 1,796.4M parameters imply approximately 7.19 GB of parameter storage alone. This is a derived lower bound, not measured VRAM; activations and runtime dependencies add memory. Inference time is unverified.

## Limitation and design implication

This closes a genuine released high-capacity omission. Large parameter storage and absent direct diffusion-regeneration evidence keep it outside the cheapest decisive study; no additional proposal is made.

Disposition: **Literature coverage; excluded**
