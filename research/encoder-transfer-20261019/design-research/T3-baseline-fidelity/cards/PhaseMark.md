# PhaseMark: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **PhaseMark: A Post-hoc, Optimization-Free Watermarking of AI-generated Images in the Latent Frequency Domain**. Version/date: arXiv:2601.13128v1 [cs.CV] 19 Jan 2026. Venue: ICASSP 2026; official README DOI 10.1109/ICASSP55912.2026.11463051.

Authors: Sung Ju Lee; Nam Ik Cho. Year: 2026. DOI: not established for this inspected version.

Stable ID: `arxiv:2601.13128v1`. Citekey: `T3PhaseMark2601`. Canonical URL: https://arxiv.org/abs/2601.13128v1

Primary full text: https://arxiv.org/html/2601.13128v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/phase.txt`
SHA-256: `070d6755e25462c303e2a8e128912127868ddb013024ad2cf990ec0688c222b7`

Actually inspected: §§2.1–2.3,3.1–3.3, Tables 1–2; official code README/LICENSE.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A training-free SD2.1 VAE latent watermark modifies phases in a central Fourier annulus. Antipodal phase modulation, phase-constrained quantization, iterative phase synchronization and spatial phase synchronization are separately evaluated variants.

## Native operating point and detector side information

The method uses 32 bits per latent channel (128 total) in a 44×44 latent region, annulus radii 10–18, 2×2 Hermitian groups and APM phases ±pi/2. SPS uses gamma=.8. The paper's detection threshold uses a binomial alpha=.01; identification at N=10^6 applies a Bonferroni adjustment. Wording that matches 'exceed' the threshold and an inclusive binomial tail must be reconciled before any adapter. The VAE and expected message are side information. Native quantization/preprocessing must come from the pinned source.

## Code, weights, pinned release and licenses

thomas11809/PhaseMark@dfe42ad0449459e26fe1579957c6d05ccdee9b92 is the verified official repository, licensed CC BY-NC 4.0. There are no learned watermark weights, but an SD2.1 VAE dependency remains necessary. The README uses a Manojb mirror; the immutable dependency pin and licensing still need resolution.

## Published evaluation and regeneration conditions

Tables 1–2 use 1,000 SD2.1-generated 512-pixel images. APM TPR at 1% FPR is .996 for VAE-B, .997 for VAE-C and 1.000 for Diff. Attack definitions use bmshj/cheng quality 3 and Zhao23 diffusion regeneration at 60 steps. DDIM 50 and CFG 7.5 describe source generation, not necessarily the attack sampler. Exact attack revision, prompt and empirical negative calibration are incomplete. PCQ quality is PSNR 34.156 versus a VAE reconstruction ceiling of 36.4193; no 1e-4 detection result is established.

## Cost and uncertainty

Table 2 reports .142 seconds embedding and .050 seconds decoding; hardware/phase scope is not sufficiently established for a target-server claim. Full VAE roundtrips and actual peak memory must be included in future timing.

## Limitation and design implication

P3 is retained as a proposal because the mechanism differs from learned pixel residuals. Its native quality and alpha=.01 endpoint are materially unequal to the thesis gate; do not tune them on development outcomes to manufacture comparability.

Disposition: **P3 preserved; proposed/deferred behind P1 and P9; excluded.**
