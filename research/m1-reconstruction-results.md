# Pure VAE reconstruction diagnostic: twelve development photos

Exploratory results, 2026-10-03. No watermark is embedded. A frozen SD1.5 VAE decodes an unscaled latent optimized against the canonical 512x512 source with RGB MSE. The measured output is clamped, rounded, saved and reopened RGB8. The schedule is posterior mode followed by 50, 100 and 200 Adam updates; the final fixed endpoint is 200, not a selected best checkpoint.

The authoritative output root is `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/`. Source attempts are `20261003-1455-latent-reconstruction` at `3dbc6a6` and `20261003-2255-latent-reconstruction-recovery` at `34f5ca0`. The former was interrupted by the user after four completed cases; its stale root status is qualified by `research/m1-pause-artifacts-20261003.json`. The latter completed eight cases in 2244.25 seconds, including a fresh initialization of the interrupted case. The recovery-aware analysis is `20261003-2333-reconstruction-analysis` at `d619add`; its JSON/CSV inventories retain the incomplete attempt and select whole completed cases by the declared recovery rule. There are twelve sources, not thirteen independent attempts.

| Fixed step | Observed/planned | Mean PSNR dB | Mean RGB SSIM | Mean AlexNet LPIPS | All three quality conditions |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | 12/12 | 25.3091 | .70131 | .07006 | 0/12 |
| 50 | 12/12 | 27.5843 | .76394 | .08154 | 0/12 |
| 100 | 12/12 | 28.1213 | .78054 | .09599 | 0/12 |
| 200 | 12/12 | 28.5508 | .79348 | .11296 | 0/12 |

The conjunction is source-relative PSNR >35 dB, SSIM >.9 and LPIPS <.1. Step-200 PSNR spans 22.8365–31.2934 dB; SSIM spans .63398–.89037. No image reaches either the PSNR or SSIM target. MSE optimization improves PSNR/SSIM averages while LPIPS worsens; the loss did not optimize perceptual similarity, and PSNR improvement is not a guarantee of perceptual improvement. Human assessments remain absent.

## Next diagnosis and interpretation

The predeclared longer-fit test selects the best and worst step-200 PSNR from the complete twelve-case inventory, with numeric-ID tie breaking: 147498 and 499768. It resets Adam to .005 for 400 more updates, measures fixed total steps 200/300/400/600, and reports the final endpoint and late gain. This adaptively selected diagnostic is not a population sample and cannot replace the full twelve-source result.

The current numbers show a substantial quality obstacle for this particular pure-decoder initialization/model/optimizer budget before adding a watermark. They do not prove an optimal reconstruction bound, that all VAE models fail, or that terminal-latent watermarking is impossible. In particular, the generated-image setting of several published latent methods is different from preserving arbitrary photographs. Family A's source-bypass hybrid must remain separately labeled and measured; it does not turn these failures into a pure-decoder success. The bounded watermark pilots and longer-fit diagnosis remain necessary before deciding the practical route.
