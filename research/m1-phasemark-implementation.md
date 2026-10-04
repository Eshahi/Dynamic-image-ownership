# PhaseMark terminal-latent pilot implementation

This implements the adopted [feasibility protocol](m1-phasemark-feasibility.md), not a faithful reproduction of the original SD2.1 generation experiment. It is a two-image SD1.5 terminal-latent carrier screen. It does not implement semantic binding, cryptographic ownership, regeneration inversion, or the proposal's three decision states.

## Attribution and changes

The layout, APM/IPS modulation and shifted Hermitian restoration are adapted from PhaseMark by Sung Ju Lee and Nam Ik Cho, copyright 2026 Seoul National University, at [revision dfe42ad0449459e26fe1579957c6d05ccdee9b92](https://github.com/thomas11809/PhaseMark/tree/dfe42ad0449459e26fe1579957c6d05ccdee9b92). Their retained LICENSE and source hashes are checked at preflight. This adaptation retains [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) attribution and noncommercial restrictions. No upstream module is imported or initialized.

Changes are explicit: SD1.5 posterior-mean terminal latents, fixed public SHAKE payloads, saved RGB8 extraction, CPU LPIPS/CLIP assessment, float RGB quality metrics, corrected integer binomial acceptance boundary, and complete run receipts. PCQ and SPS are excluded. A pure VAE decoder creates each output; there is no source bypass or pixel residual composition. No diffusion pipeline or safety checker is invoked because this screen performs only VAE encoding/decoding, not text generation; no safety verdict is asserted.

## Exact conventions

The scaled latent has shape 1 x 4 x 64 x 64. Each channel's central spatial crop [10:54,10:54] uses ordinary FFT2 with backward normalization. The upstream 22 x 22 radius-ordered greedy layout yields 32 nonoverlapping 2 x 2 blocks per channel, for 128 bits. APM preserves magnitude and assigns phase +pi/2 or -pi/2. IPS preserves row-major anchors 1 and 3, setting entries 2 and 4 to the anchor phase or its pi offset. The upstream shifted authoritative-right-half Hermitian repair is retained, with FFT dimensions explicitly restricted to the two spatial axes. The untouched latent exterior is restored exactly. Inverse imaginary residuals are recorded and values above 1e-5 fail the arm. Pre-decoder spectral and spatial displacement energies are recorded; their Parseval divisor is 44 squared = 1936.

Native APM extraction tests phase sum > 0; native IPS extraction tests the sum of two wrapped phase-difference cosines > 0. Ties map to zero. Zero magnitude is a surfaced limitation: torch's zero phase produces APM bit zero, but IPS bit one with score 2. Every extracted block records its zero-magnitude coefficient count. Neither an erasure rule nor an amplitude filter is silently introduced. CPU synthetic nondegenerate latents demonstrate exact 128-bit round trips, but this does not establish survival through decoded RGB or VAE cycles.

## Inventory, quality and decisions

The manifest fixes development IDs 1675 and 4795, both arms, both C0/C1 controls, and clean/VAE-cycle outputs: 16 conditions, each queried against the same four public owner payloads. C0 is pure D(E(source)); C1 is pure D(phase-modulated E(source)). The cycle re-encodes the saved RGB8 output using the posterior mean. Each suspect is saved and reopened before extraction. PNG, RGB8 and original source hashes are retained; no source image is needed by the detector.

Each condition records quality against the canonical source and same-arm clean image. Clean C1 additionally records paired C0 quality. The quality conjunction remains PSNR > 35 dB, SSIM > .9 and LPIPS < .1. CPU CLIP cosine >= .85 is only an exploratory numerical retention proxy; human judgments stay missing. The carrier gate requires every clean and cycle C1 correct-owner query present, every wrong-owner query absent, and every C0 roster query absent. The source-quality gate is separate and requires both clean C1 images. Incomplete arms have null gates, never an implied pass.

Presence is fixed at >=82 matching bits. Counts at 78 and 81 are descriptive alternatives, not threshold selection. Fair independent-bit binomial tails are reference calculations, not measured false-positive rates: blocks, channels, related images and roster queries may be dependent. Four public payloads do not establish key secrecy or forgery resistance.

## Execution and failure semantics

The CLI accepts `--manifest` and `--output-dir`, with a fresh output under MAIN's `.thesis-build/dev-runs`. It refuses existing directories. Run, manifest snapshot, conditions and append-only journals are created before model loading; preflight failures retain all 16 planned conditions, the error and available provenance. Committed code/config/helper/source receipts, model assets and LPIPS learned weights are pinned; network access is blocked before loading local models. No models are downloaded. CPU-only execution is refused for the scientific pilot.

The pilot uses seed 0, batch 1 and fp32, with TF32 disabled. Resource checks enforce 10 GiB allocated GPU memory, 16 GiB observed process working set, 250 MiB artifacts and 900 seconds. These checks occur at stage boundaries, so the wall-time bound is not a preemptive kernel timeout. An error or stop preserves completed conditions and marks unfinished conditions explicitly. There is no within-directory resume or automatic best-output selection; any retry must use a fresh run directory, retaining the failed receipt.

## CPU verification

Nine tests cover exact layout against isolated pinned scalar definitions; shifted Hermitian restoration against its isolated pinned tensor definition; conjugacy and real inverse; nondegenerate all-zero/all-one/three deterministic payload round trips for both arms; exterior and Parseval invariants; magnitude/IPS-anchor preservation; wrap, ties and zero-magnitude bias; integer-tail boundaries; float PSNR; frozen manifest validation; and failure receipts with the fixed denominator. Tests use procedural tensors and temporary metadata only. No development photograph, pretrained model, GPU experiment or scientific score was read or run during implementation verification.
