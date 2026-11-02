# Lean F6: probe and Stage 1 results

Run by Claude on 2026-11-02, under [PROTOCOL.md](PROTOCOL.md) and the user's receipt (C as the pass bar). Development sources only. **Status: SCIENTIFIC_STOP at Stage 1.** No arm reached the read threshold on SDXL .1 and Kandinsky 3, so the fixed rule ended the study. Stages 2 and 3 did not run.

## Run

- **Server:** vast container 58795791, RTX 4090 24 GB, EPYC 7Y83, 76 GB disk.
- **Clock:** start taken as 08:55 UTC (container up at 08:59). Setup finished 09:32; the instance was stopped, not destroyed, at 11:11 UTC, about 2.3 instance-hours. The price was not given, so the cap used a conservative USD .60/h.
- **Code:** commit b510c6d on `claude/f6-lean-20261101`.
- **Retrieved:** MAIN `.thesis-build/dev-runs/20261102-f6-lean/f6l-results.tgz`, SHA-256 94694dee…7cc6b2, unpacked beside it. Native images other than the seed-0 sample of F5 and C0 stay on the stopped instance's disk.

## Probe

Exact native capture and replay and first-step parity passed in all four cells. The writer policy came only from timing and gradients:

| Measure | Value |
|---|---|
| Reader gradient | .067 s, not the .52 s assumed. Most of F5's write time is CPU work |
| SDXL graph: noise, x0 | 1.39 s, 1.91 s |
| Agreement between noise-draw gradients, median cosine | −.03 to +.07 (noise), −.01 to +.07 (x0) |
| SDXL against SD1.5 surrogate gradient, cosine | about 0 |
| bf16 against fp32 gradient, cosine | .005 to .025 |
| Surrogate over clean gradient norm | 340 to 1,180 |
| Peak memory | about 24.7 of 25.3 GB with checkpointing; out of memory without it |

The policy turned momentum on for noise and x0, and kept bf16 off and checkpointing on. **The SDXL surrogate gradient behaves like noise from draw to draw**, which matches Phase A's finding that SDXL tangents are almost orthogonal to the real change.

## Stage 1

Four tuning sources (544, 1355, 902, 599), seed 0. "Dec" is the mean decoded score, with a read threshold of 8.26. C is the count of sources that read. J was 0/4 in every foreign cell for every arm.

| Arm | SD1.5 .2 dec (C) | SDXL .1 dec (C) | SDXL .2 dec (C) | K3 .2 dec (C) | Median LPIPS (max) | Min PSNR |
|---|---|---|---|---|---|---|
| F5 r2 | 12.15 (4) | 4.89 (0) | 3.55 (0) | 5.43 (0) | .014 (.088) | 42.2 |
| F5-budget 46 | 14.44 (4) | 6.31 (0) | 4.12 (0) | 6.41 (0) | .028 (.086) | 40.8 |
| Generic 46 | 14.34 (4) | 6.38 (0) | 4.39 (0) | 7.17 (1) | .030 (.085) | 40.8 |
| Noise 46 | 14.33 (4) | 6.25 (0) | 4.20 (0) | 6.39 (0) | .028 (.088) | 40.8 |
| x0 46 | 14.36 (4) | 6.27 (0) | 4.31 (0) | 6.23 (0) | .028 (.089) | 40.8 |
| Render 38 | 12.46 (4) | 5.78 (0) | 4.24 (0) | 5.80 (0) | .021 (.085) | 36.6 |
| Render 36 | 12.09 (4) | 5.47 (0) | 4.22 (0) | 5.61 (0) | .020 (.089) | 36.6 |
| Noise 46 + render 38 | 14.71 (4) | **7.56 (2)** | 5.06 (0) | 7.04 (1) | .034 (.091) | 36.1 |

The clean gate removed F5-budget 42, generic 42 and 38, and noise 42. Each failed strict quality on source 902, even with the residual scaled to half (LPIPS .10 to .13). Every arm had clean F 4/4, and there was no C0 or wrong-owner event.

## What this shows

1. **The surrogate adds nothing.** Noise 46 and x0 46 match the F5-budget 46 control within ±.2 decoded points in every cell. The gain over F5 comes from the larger budget alone. This is the result the probe predicted: single-draw gradients through SDXL carry no consistent direction, and averaging them with momentum over 100 updates did not recover one.
2. **The budget is capped by quality, not PSNR.** 46 dB adds about 1.4 decoded points on SDXL .1 and 1.0 on K3. 42 dB already fails the strict LPIPS bar on one textured image. This confirms the analysis estimate that 46 dB is about the ceiling for F5-style energy.
3. **The rendered companion helps only together with the budget.** Alone it adds .6 to .9 on SDXL .1. On top of the 46 dB budget it adds 1.3 on SDXL .1 and .65 on K3, at the cost of PSNR near 36 dB.
4. **The best arm is still short.** Noise 46 with render 38 averages 7.56 on SDXL .1 (2 of 4 read) and 7.04 on K3 (1 of 4), against a threshold of 8.26. On SDXL .2 it averages 5.06, far below. Reaching 12/16 would need well over 1 more decoded point on SDXL .1 and K3 and about 4 more on SDXL .2. Nothing measured here supplies that within strict quality.
5. **J is unreachable, as expected:** 0 in every foreign cell, even at C 2/4.

## Limits

Four development sources and one seed: a screen, not an estimate of population rates. The stop is the fixed rule, not a judgment after seeing the numbers. Surrogate gradients were tested only with this writer, its fixed reader and these budgets. A trained encoder, such as VINE, is a different mechanism and is not addressed. K3 was excluded from the gradients. Human visual review is missing.

## For the thesis

This closes F6 as a development negative. Optimizing a fixed-reader pixel mark through an independent regenerator's noisy codec or one-step denoiser does not improve its survival beyond the extra distortion budget, because the gradient through SDXL's encoder is uninformative at this scale. This supports, with a writer-side test, the Phase A finding that encoder amplification transfers while survival does not. A larger budget helps a little but is capped by LPIPS, so F5's SD1.5-only regeneration result stands.
