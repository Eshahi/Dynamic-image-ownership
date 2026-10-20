# DistSeal: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **Learning to Watermark in the Latent Space of Generative Models**. Version/date: arXiv:2601.16140v1 [cs.CV] 22 Jan 2026. Venue: arXiv 2026 preprint; the official README citation says 2025, whereas the inspected arXiv v1 is dated January 2026.

Authors: Sylvestre-Alvise Rebuffi; Tuan Tran; Valeriu Lacatusu; Pierre Fernandez; Tomáš Souček; Nikola Jovanović; Tom Sander; Hady Elsahar; Alexandre Mourachko. Year: 2026. DOI: not established for this inspected version.

Stable ID: `arxiv:2601.16140v1`. Citekey: `T3DistSeal2601`. Canonical URL: https://arxiv.org/abs/2601.16140v1

Primary full text: https://arxiv.org/html/2601.16140v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/distseal.txt`
SHA-256: `7462d1e3f1a2236e8e95ae517fc8d2ed26cf4cc1dfe925d786e9957d992921cd`

Actually inspected: §§4.1–4.2,5.1–5.2, Tables 1–3; official README post-hoc image-notebook description/LICENSE.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A learned latent embedder can be used directly or distilled into a generator/decoder. Official post-hoc notebooks explicitly load an existing image, encode it, modify its latent, decode and extract. Only that direct latent path counts here; distilled variants do not add separate methods.

## Native operating point and detector side information

The native message has 64 raw bits. DCAE uses 512-pixel images, latent shape 8×8×128 and epsilon=.5. RAR uses 256 pixels and 16×16×256 latents, with epsilon=.5 after quantization or 1.5 before it. A modified U-Net omits up/downsampling, and ConvNeXt Tiny extracts bits. The matched pixel baseline has no JND mask. No native calibrated presence cutoff is specified; DCAE/RAR codecs, codebooks and expected message are detector dependencies.

## Code, weights, pinned release and licenses

facebookresearch/distseal@d0a71cd272bb29e3b49cdc965bbaf4d24f2684ac has an inspected MIT LICENSE and README explicitly covering code and models. Official loaders, model cards, checkpoint triplets and post-hoc notebooks are available. Selected checkpoint SHA-256 values and all codec dependency pins/licenses remain unresolved. The README citation year 2025 differs from the inspected January 2026 arXiv version.

## Published evaluation and regeneration conditions

Evaluation uses 50,000 generated images per generator. DCAE post-hoc latent embedding gives PSNR 31.06, FID 11.42, IS 98.11, average bit accuracy 95.18% and combined-attack accuracy 84.28%; its matched pixel baseline gives PSNR 43.48, average 97.78% and combined 97.29%. RAR post-quantization latent accuracy averages 93.96% versus pixel 97.27%. Attacks are valuemetric, geometric, compression and combined; no diffusion-regeneration tuple is reported. The native latent quality is below the strict thesis gate.

## Cost and uncertainty

Section 5.2 reports CPU watermark-module embedding times of 3 ms latent versus 63 ms pixel for DCAE, and 17 versus 41 ms for RAR. These exclude a fresh image codec roundtrip or full generator. They are not end-to-end post-hoc CPU measurements. Peak VRAM is unreported.

## Limitation and design implication

Closes a 2026 latent post-hoc release omission. Fast latent-module execution does not establish end-to-end quality or regeneration survival; it remains a literature comparator.

Disposition: **Literature coverage; excluded**
