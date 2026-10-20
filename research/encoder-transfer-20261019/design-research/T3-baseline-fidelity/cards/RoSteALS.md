# RoSteALS: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **RoSteALS: Robust Steganography using Autoencoder Latent Space**. Version/date: arXiv:2304.03400v1 [cs.CV] 06 Apr 2023. Venue: CVPR 2023 Workshops (CVPRW); official release.

Authors: Tu Bui; Shruti Agarwal; Ning Yu; John Collomosse. Year: 2023. DOI: not established for this inspected version.

Stable ID: `arxiv:2304.03400v1`. Citekey: `T3RoSteALS2304`. Canonical URL: https://arxiv.org/abs/2304.03400v1

Primary full text: https://arxiv.org/html/2304.03400v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/rosteals-reused.txt`
SHA-256: `956e32ea1db3a9d8eacf7b0488c3a57e90ee62701c0409a1de4de8a42d7d6cdb`

Actually inspected: §§3.1–3.2;§§4.1–4.3 and evaluation definitions; official README/license/checkpoint metadata.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A frozen pretrained VQ image autoencoder receives a learned secret-conditioned residual in its latent representation; a ResNet extractor recovers the payload from the decoded image. Existing images can be encoded and marked, so this qualifies as post-hoc.

## Native operating point and detector side information

The reported setting uses 100 bits at 256×256 with a VQ-f4 codec and approximately 300,000 trainable secret-encoder parameters. The decoder is image-only, with an expected message needed for query scoring. The paper's word-accuracy definition allows fewer than 20% bit errors; it is not exact payload recovery. No calibrated universal presence threshold is provided. Release preprocessing and rounding require later adapter verification.

## Code, weights, pinned release and licenses

TuBui/RoSteALS@8c09b022a362ffdf977a86f355e5af339793d9c9, CC BY-NC-SA 4.0. Official 520 MB watermark checkpoint https://kahlan.cvssp.org/data/Flickr25K/tubui/cvpr23_wmf/epoch=000017-step=000449999.ckpt; frozen VQ dependency https://ommer-lab.com/files/latent-diffusion/vq-f4.zip. Neither downloaded; immutable hash and dependency license/version remain unresolved.

## Published evaluation and regeneration conditions

The original evaluation covers conventional distortions and ImageNet-C, not a fully conditioned diffusion-regeneration experiment. It therefore provides no defensible model/strength/sampler/prompt/count/TPR tuple for R1. The method and evaluation are V2-inspected even though regeneration evidence is absent.

## Cost and uncertainty

Training with batch size 4 is reported to fit a 12 GB GPU. This is not measured inference memory. Inference needs the frozen VQ codec plus secret encoder and extractor; checkpoint size is storage, not peak VRAM.

## Limitation and design implication

The explicit latent post-hoc pathway matters for the taxonomy, but the older codec and missing direct regeneration result make it lower priority than P1/P9.

Disposition: **Literature coverage; excluded**
