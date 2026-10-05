# H3 — mask_power 0.5 at psnr 52 (same stress grid)

Baseline (mask 0): run 20261005-1200: .4 49/58 (84%), .5 37/58 (64%), .6 10/57 (18%), LPIPS mean .0172 max .050.
Mask 0.5: run 20261005-1330: .4 38/58 (66%), .5 23/59 (39%), .6 6/57 (11%), LPIPS mean .0131 max .043.

Δ: .4 -11, .5 -14, .6 -4 at same psnr 52. LPIPS mean -24% (good) but paired T3 down 22% at .4, so fails plan kill criterion "no LPIPS drop ≥15% at equal T3 count". Perceptual mask re-weights pixel budget away from smooth regions (sky 147498) toward texture; encoder gain is spatially agnostic via VAE, so masking degrades latent SNR.

Kill for mask_power>0 at equal psnr on this grid. Option (b) — lower psnr with mask to match F5 r2 LPIPS — is below baseline quality already (F5 r2 LPIPS already ≤ v5), so not a thesis contribution under replacement criteria (requires LPIPS ≤ .0173 and T3 improve). H3 closed without replacement.

Next: H4 binding (calibrated soft threshold / invariant pooling) — bottleneck at .4/.5 is binding (see stress baseline: .4 6/9, .5 14/21).
