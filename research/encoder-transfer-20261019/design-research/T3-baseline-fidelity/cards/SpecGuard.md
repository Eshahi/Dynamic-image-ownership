# SpecGuard: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **SpecGuard: Spectral Projection-based Advanced Invisible Watermarking**. Version/date: arXiv:2510.07302v1 [cs.CV] 08 Oct 2025. Venue: ICCV 2025, official repository title.

Authors: Inzamamul Alam; Md Tanvir Islam; Simon S. Woo; Khan Muhammad. Year: 2025. DOI: not established for this inspected version.

Stable ID: `arxiv:2510.07302v1`. Citekey: `T3SpecGuard2510`. Canonical URL: https://arxiv.org/abs/2510.07302v1

Primary full text: https://arxiv.org/html/2510.07302v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/specguard.txt`
SHA-256: `4fd1371cea06309cc8f53bf4cdb16cd3bb596df499f229c04cc0ee877799a3d5`

Actually inspected: §§3.1–3.3 including Eqs. 13–17/Algorithm 1;§§4.1–4.6; Appendix 12.2/Table 9 attack settings.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

Spectral watermarking learns how to modify wavelet high-frequency components using a compact convolutional network and a learned extraction threshold. It is applied to an existing image.

## Native operating point and detector side information

The inspected setting uses radius 100, 32 convolution channels, watermark strength 20 and theta initialized to .001 and learned. Payloads include 48/64/128/256 bits; Table 1 also compares 30-bit variants at 256/512/1024 resolutions. Algorithm 1's learned theta is a bit-extraction threshold, not calibrated image presence. The main 128-bit clean result is PSNR 42.89, SSIM .99 and BRA .99; do not assume identical quality across capacities.

## Code, weights, pinned release and licenses

inzamamulDU/SpecGuard_ICCV_2025@eebe26e12c0647f7aebb060e7fabf90d4931783e has a verified MIT LICENSE. The inspected tree contains README/assets/license while full code, baseline and model-weight checklist items remain TODO; the README says the codebase is not fully updated. A runnable official model is therefore unverified.

## Published evaluation and regeneration conditions

Reported WAVES-style AvgP is .982 for Diff, .982 for DiffP, .995 for VAE, .990 for KLVAE, .993 for rinse-2 and .992 for rinse-4. These are the paper's AvgP/AvgQ operating-point metrics, not TPR at 1e-4. Appendix attack settings include diffusion 40–200 steps, compression qualities 1–7, KL-VAE factors 4/8/16/32, SD1.4 rinse twice at 20–100 steps and four times at 10–50. Exact evaluation counts, model revisions, sampler, prompt and negative calibration are not fully given.

## Cost and uncertainty

Training uses 25,000 COCO images, multiple RTX2080 GPUs and 300 epochs. Those are training resources, not inference costs. Runtime and peak memory for an official released checkpoint are unavailable.

## Limitation and design implication

The modern spectral mechanism and rinse evidence are relevant, but missing executable release and incompatible detection metrics keep it outside the proposed core.

Disposition: **Literature coverage; excluded**
