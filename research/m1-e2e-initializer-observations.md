# Fresh initializer observations

Exploratory development evidence, 2026-10-04. This comparison describes the original fixed200 initializer under the new deterministic execution contract. It neither changes a parameter nor licenses reuse of retained legacy latents. The exact literal/prefix/resume audit is a separate object: MAIN `.thesis-build/dev-runs/20261004-1102-initializer-comparison` verifies21/21 full checkpoints, including optimizer and RNG state.

The two descriptive comparisons use `scripts/m1_initializer_legacy_comparison.py` and retain complete input/state hashes in MAIN `.thesis-build/dev-runs/20261004-1118-initializer-legacy-1675` and `20261004-1122-initializer-legacy-4795`. They compare fresh initialization against retained `20261003-1455-latent-reconstruction`. At posterior-mode step0, both sources have exactly equal dtype, values and bytes. Step200 differs:

| Source | Latent delta L2 | RMS | Maximum absolute delta | Fresh PSNR | Legacy PSNR |
|---|---:|---:|---:|---:|---:|
|1675|0.1085127386|0.0008477558|0.0198378563|31.0031777845|31.0032656277|
|4795|0.1233327563|0.0009635372|0.0598349571|28.0590955466|28.0591906060|

Latent differences are calculated in float64 without a closeness tolerance. Fresh minus legacy reconstruction-objective differences are3.4982804209e-8 and3.7252902985e-9, respectively. Fresh SSIM is0.8903713539 and0.7112658342; legacy SSIM is0.8903681379 and0.7112745510. New initializer LPIPS was not measured and remains null; the legacy values cannot fill that missing field. These are unmarked reconstructions, not the quality of final source-plus-residual watermarked outputs.

The near-equal recorded quality does not prove equal optimization trajectories or interchangeable initialization. Every new end-to-end source therefore receives a fresh audited200-step initialization followed by the separately seeded100-step watermark phase. The original two-source gate and subsequent fixed expansion remain unchanged. Old component results are retained as component evidence and are not relabelled as validation of this complete path.
