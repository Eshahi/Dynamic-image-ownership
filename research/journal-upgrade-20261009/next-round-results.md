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

## Coarse-only descriptor: stable but insufficiently discriminative

The E3-CD1 protocol and script were committed at `3183332` before execution. All 54 cached identities, 24 canonical/full-clean pairs, two complete 552 ordered real-impostor panels and six fixed synthetic sibling controls resolve. Receipt: MAIN `.thesis-build/dev-runs/20261014-stable-instance-cd1/run.json`. Canonical targets and radius 6 remain fixed.

Canonical-to-clean matches are 24/24. SD1.5 and SDXL VAE oracle dual-content checks are 6/6 each; T3 .2 is 18/18 with 6/6 majority, and .4 is 16/18 with 6/6 majority (all 18 h checks match, two native q checks fail). Each real-impostor panel has zero matches for both old and new descriptors. The 24 q-nearest pairs have zero new matches, 23 distances at least 10.

The mandatory synthetic specificity guard **fails**: four pairs rejected by legacy h become matches under h_CD. The improved regeneration numbers cannot overrule this. No robust dual carrier was implemented for CD1. Coarse appearance supplies stability but loses the texture distinctions required by this instance-repair claim. A subsequent fixed amendment must retain that distinction, not silently rename it.

## Equal-energy descriptor: scalar rebalancing still fails

Protocol and implementation were committed at `380a6e8`. Receipt MAIN `.thesis-build/dev-runs/20261014-balanced-instance-bi1/run.json`, duration 28.453 seconds. Native legacy reconstruction and same-hyperplane checks pass; every cached native h agrees with re-extraction. All 24 clean comparisons match; SD1.5/SDXL VAE joint oracle counts are 5/6 and 6/6. T3 .2 improves to 10/18 with 3/6 majority and .4 to 7/18 with 2/6 majority, below the fixed primary gate. Both 552-row real-source panels retain zero matches, all 24 q-nearest distances are at least 10. Sibling distances are 5,8,4,6,8,6 versus legacy 5,11,8,9,8,6; seeds 3 and 4 are newly accepted. The regeneration and sibling gates both fail, so no GPU stage occurs. No weight or projection seed is retried.

Continuous geometry supplies an important limit on interpretation. At .2, actual normalized fine-feature cosine is .5406--.7913 (mean .6614); the six sibling cosines are .0155--.0521. The detail floor is inactive for these pairs. Coarse positive cosine is .9656--.9965, but siblings are even closer at .9957--.9996. Thus coarse-only cannot distinguish them, while fine features still contain distinguishing information. BI1's fixed 32-bit Rademacher compression does not exploit that separation adequately on this panel. This does not prove a compression-only cause, because representation and finite threshold interact. It also does not prove that all instance information has been erased by regeneration.

The scalar-rebalancing protocol is closed. A separately justified representation/capacity hypothesis is being designed before any new feature outcomes, with all increased payload and threshold assumptions disclosed. Historical E3 and M2 remain unchanged.
