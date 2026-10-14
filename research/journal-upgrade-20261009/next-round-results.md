# Reopened development round, 2026-10-14

The user explicitly requested another autonomous scientific round. The October 13 closure remains a historical allocation, not a prohibition on this new work. Existing E3/M2/RC1 outcomes and thresholds are unchanged. All new evidence uses already consulted development sources; no held-out data, paid compute or human judgments enter.

## Reissue implementation diagnosis

Committed saved-pixel analysis `a403a31`, MAIN `.thesis-build/dev-runs/20261014-reissue-residual-diagnosis/run.json`, covers every RC1 image. The six RR canonical LPIPS values change from .0887/.0203/.0319/.0088/.0728/.0665 in the original full marks to .2581/.0547/.0729/.0209/.1729/.1904 after reissue. Original RGB8 MSE is 2.95--6.40 and final MSE 10.34--14.62. Each first PGD stage adds approximately 1.71 MSE; the remaining branch adds .47--.62. Total increments have positive cosine .42--.59 with the old residual.

The native PGD stops moving when its hinge gradient is zero, but its budget is anchored to each new input. The fragile spread-spectrum writer also recalculates host-dependent targets. RC1 omits full E3's canonical quality selection. Accumulation is consistent with these observations; the saved stages do not isolate which operation causes the perceptual loss. The LPIPS implementation loads the pretrained trunk and learned weights and uses the correct input normalization; no metric bug was found. RC1's failed quality gate remains failed.

## Instance descriptor ceiling: transport alone is insufficient

The [prospective design](next-round-mechanism-design.md) and analysis were committed at `f5395ee` before computing the new outcomes. Receipt: MAIN `.thesis-build/dev-runs/20261014-instance-ceiling/run.json`. All 54 C-arm identities are resolved, with the original operational h target and radius 6. This counterfactual supplies perfect h transport while retaining actual checked exact-q recovery; it is not an executable detector.

| Cached condition | Actual checked q | Perfect-h dual-content ceiling | Actual exact h / full acceptance |
|---|---:|---:|---:|
| Clean | 6/6 | 6/6 | 6/6 / 6/6 |
| SD1.5 VAE | 6/6 | 3/6 | 0/6 / 0/6 |
| SDXL VAE | 6/6 | 6/6 | 0/6 / 0/6 |
| T3 .2 | 18/18 | 6/18 | 0/18 / 0/18 |
| T3 .4 | 16/18 | 4/18 | 0/18 / 0/18 |

At .2 only one of six source groups has a majority ceiling success; at .4 two do. The frozen advance gate fails on SD1.5 VAE, .2 count and .2 majority. Therefore E3-DV1 with the unchanged descriptor is rejected before GPU implementation. This ceiling applies to the saved pixels, not every possible future optimized image. Detail-heavy descriptor drift and destroyed transport are separate problems. Any replacement descriptor needs a fresh fixed stability-and-discrimination test; widening the old radius would not resolve the scientific question.

Primary-source updates are in [the three new paper cards](../literature/dual-carrier-20261014/primary-cards.json). Dual spectral watermarking is prior art; two carriers alone are not a novelty claim. Current E3 remains retained.
