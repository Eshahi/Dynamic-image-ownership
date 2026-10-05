# H1 — band 8–28 vs 4–32 (4 sources pilot, psnr 52, same stress grid)

Run: `20261005-1500-f5-H1band-8-28` (4 sources: 1675,4795,6012,25394, 5 seeds) vs baseline subset 4–32 on same 4 sources.

| band | quality psnr/lpips | .4 | .5 | .6 |
|---|---|---|---|---|
| 4–32 baseline subset | 44.71 / .0172 (full) | 13/18 | 10/18 | 2/17 |
| 8–28 | 45.06 / .0107 | 13/17 | 9/18 | 1/16 |

Delta at .4 0, .5 −1, .6 −1 (within noise of 18 identities). LPIPS lower (narrower band spreads less into high-latent frequencies), but no T3 gain. Denoiser keeps 4–32 well; narrowing to 8–28 removes low-frequency chips that survive best (h1-probe: low band kept fraction .51 at .4 vs .34 for natural). Kill for band retuning as selector.

Combined H1: matched filter +1 dB and band retuning both killed. No carrier geometry gain without attack-aware optimization (H2, high cost, deferred).
