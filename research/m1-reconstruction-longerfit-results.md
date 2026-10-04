# Fixed longer-fit reconstruction diagnostic

Exploratory2026-10-04. Completed MAIN `.thesis-build/dev-runs/20261004-0914-reconstruction-longerfit` at `cf373b22ae11ebac216bf0a03c1e584024aad443`,1126.953seconds. Run receipt SHA-256 `8b5a30b5f6266f8ca665c32cb53095da55d84a617c1959cd75b9c7756900da1a`. No watermark is embedded here. This is a bounded optimization diagnostic, not a certified decoder range/fidelity bound.

The prospective manifest `m1-reconstruction-diagnosis-dev.json` selects the best147498 and worst499768 step200 PSNR from the complete12-source inventory, using numeric-ID tie breaking. Both start from hash-verified unmarked step200 latents, exactly reproduce their prior RGB8 pixels, reset Adam to lr.005 and perform400 additional fp32 updates minimizing unclamped decoder RGB MSE. Measurements remain at totalsteps200/300/400/600; no best-checkpoint selection. The declared plateau criterion is PSNR gain400-to600<.25dB. All outputs and10-step restart checkpoints are retained. Parent independently checked checkpoint artifact hashes after completion; the source runner records quality and receipt arithmetic.

| Source/step | PSNR dB | SSIM | LPIPS |
|---|---:|---:|---:|
|147498/200|31.293446|.868160|.054938|
|147498/300|31.446708|.870869|.056124|
|147498/400|31.562847|.873213|.057241|
|147498/600|31.728902|.876238|.059083|
|499768/200|22.836515|.633984|.223965|
|499768/300|22.993035|.642317|.235858|
|499768/400|23.112310|.649371|.241662|
|499768/600|23.265559|.657865|.250156|

Quality admissibility remains0/2 at the fixed endpoint and0/8 measured source-step cells. Gains200-to600 are.435456/.429044dB; gains400-to600 are.166055/.153249dB, so both meet the prespecified operational plateau definition. LPIPS worsens despite improved MSE/PSNR, exposing the objective tradeoff. The recorded peak Torch allocation is6,512,417,280bytes per case; no process-RAM peak was inferred.

This weakens the specific explanation that merely extending the same latent-only pixel-MSE fit from200 to600 steps would meet35dB on these extrema. It does not prove that another optimizer, initialization, decoder, training scheme or additional pixel pathway cannot do so. The two selected extrema are not a random sample, and their diagnostic cannot replace the twelve-source development denominator. The source-bypass A amendment must retain its own clean and threat evidence; it cannot claim a pure decoder-quality result from this exercise. No held-out data, human verdict, hypothesis deletion or lifecycle advancement occurred.
