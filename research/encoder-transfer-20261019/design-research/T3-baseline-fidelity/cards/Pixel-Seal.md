# Pixel-Seal: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **Pixel Seal: Adversarial-only training for invisible image and video watermarking**. Version/date: arXiv:2512.16874v1 [cs.CV] 18 Dec 2025. Venue: arXiv 2025; a later venue is not verified here.

Authors: Tomáš Souček; Pierre Fernandez; Hady Elsahar; Sylvestre-Alvise Rebuffi; Valeriu Lacatusu; Tuan Tran; Tom Sander; Alexandre Mourachko. Year: 2025. DOI: not established for this inspected version.

Stable ID: `arxiv:2512.16874v1`. Citekey: `T3PixelSeal2512`. Canonical URL: https://arxiv.org/abs/2512.16874v1

Primary full text: https://arxiv.org/html/2512.16874v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/pixelseal.txt`
SHA-256: `fc7ff923bef9b1dee0989e93b57f83d59868c11ea1bda5d7f594f65092f30a68`

Actually inspected: §§4.1–4.4,5.1–5.3, Tables 1–2; official VideoSeal README/LICENSE and pinned pixelseal.yaml.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

Pixel Seal is a post-hoc learned image embedder and extractor released within VideoSeal. The model preserves the original image through residual upsampling and perceptual attenuation.

## Native operating point and detector side information

The pinned pixelseal.yaml sets 256 bits, processing resolution 256, scaling_w=.2, scaling_i=1, JND jnd_1_1 and additive blending. A nested template mentions 16 bits; a future adapter must verify that the loader applies the explicit 256-bit override. This is a native 256-bit baseline, not an arbitrary truncation to 32 or 100 bits. Query log-p values use a binomial convention, but no universal numerical native presence cutoff or empirical image-FPR guarantee is established.

## Code, weights, pinned release and licenses

facebookresearch/videoseal@870ca7fb33578b90f14c602016b6c2788096226e has an inspected MIT LICENSE and README explicitly licensing code and models under MIT. The pinned videoseal/cards/pixelseal.yaml points to https://dl.fbaipublicfiles.com/videoseal/pixelseal/checkpoint.pth. This is a mutable artifact URL; SHA-256 and size are unverified because no weights were downloaded.

## Published evaluation and regeneration conditions

The paper evaluates 1,000 MetaAI images at 1,280 pixels and also 100 SA-1B images. At the selected 256-bit point, MetaAI quality is PSNR 48.9, SSIM .9905, LPIPS .0013 and JND .34. Its conventional-distortion evaluation provides no direct diffusion-regeneration model/strength/sampler/prompt/count/TPR tuple. Robustness to JPEG or cropping cannot fill that gap. New third-party evidence: SNW Appendix H.2/Table 6 tests 200 MFlickr images at 1,024 pixels, with all methods rescaled to 48 dB PSNR and decoder features whitened. PixelSeal rate/capacity is .939/240.5 bits for identity, .555/142.0 for VAE, .519/132.8 for Sana 2 steps, .357/91.3 for 4, .076/19.4 for 8, .025/6.4 for 10 and .003/.8 for 20. Rate is NOT bit accuracy: these are independent-bit Shannon-capacity estimates, not exact payload recovery or calibrated TPR. The attack model revision, sampler, prompts, seeds and correspondence to our SDXL strength are unresolved. This does not supply a result for the native P9 operating point.

## Cost and uncertainty

The paper lists about 43.8M embedder and 33.4M extractor parameters. No target-server peak memory or runtime exists. P9 proposes only 60 clean marked images and 180 R1 strength-.2 regenerations, with shared C0 outputs reused. Assuming 8–20 seconds per regeneration and .15 hours for marking/readout gives .55–1.15 hours; planning allowance .55–1.25 hours. This is an explicit workload estimate, not a measurement.

## Limitation and design implication

P9 remains the second additional proposal because the native release is modern, permissively licensed and high quality. The original paper has no direct regeneration result; the separate SNW study supplies conditional third-party evidence at a rescaled, whitened operating point. Neither establishes SDXL transfer for P9. It remains excluded from the core.

Disposition: **P9 Pixel Seal: proposed, rank 2 among additions; excluded from core.**
