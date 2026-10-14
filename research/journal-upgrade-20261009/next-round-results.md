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

The scalar-rebalancing protocol is closed. Historical E3 and M2 remain unchanged.

## Fine-only 128-bit Gaussian sketch: stability improves, a real-source collision remains

The [fixed FG128 protocol](descriptor-capacity-amendment.md) and implementation were committed at `f7c9c97` before execution. Receipt: MAIN `.thesis-build/dev-runs/20261014-fine-gaussian-fg128/run.json`. All inputs and native legacy-h checks resolve in 20.922 seconds. Native fine features alone, with an explicit weak-detail abstention, are projected onto 128 deterministic Gaussian hyperplanes. The match radius is 44 and mismatch begins at 51. The ideal independent-uniform-bit ball mass at 128/44 is .000257892 versus .000267526 at old 32/6. This is not matched natural-image FPR: relative tolerance increases from .1875 to .34375, payload grows fourfold, projection distribution and representation also change. These interventions are not causally isolated.

All 24 clean pairs match. Both VAE oracle counts are 6/6. T3 .2 oracle dual-content succeeds on **17/18** with all six source majorities; .4 is 9/18 with three majorities. The sole .2 miss is source 73, seed 9, distance 45. All 24 q-nearest pairs are nonmatches and have distance at least 51. The six texture-sibling distances are 54,57,50,49,53,53: none matches and none is a new acceptance. Uncertain distances 49/50 are not claimed as confident mismatches.

The mandatory real-impostor gate nevertheless **fails**. The canonical panel has 2/552 ordered matches, both directions of the single pair 30/544 at distance 44; the canonical-to-marked panel has 0/552, minimum distance 46. Legacy h rejects this pair at distance 13. Its uncompressed fine-feature cosine is .01019995, giving hypothetical Gaussian expected distance 63.5844, but the one fixed finite sketch yields 44. This observation is a descriptor collision, not a measured full-system false acceptance; the two directions are not independent events. Neither the finite-panel result nor the ideal random-hyperplane formula calibrates population FPR.

No radius was lowered after seeing the collision, no alternate projection seed or larger sketch was tried, and no GPU carrier was built. The prospectively conditional four-block BCH/960-projection carrier therefore has no measured quality, capacity or attack result. Gaussian stream SHA-256 is `9642d00d9141a185b1e78dc0cb3a21de19628f4136de7a3b133eb2b3dc22b8fd`; exact construction and hypothetical-null checks are stored in the receipt.

## Round comparison and permitted conclusion

These are perfect-transport descriptor screens on consulted development pixels, not four deployable watermark systems. Positive and specificity criteria form one conjunction; a high positive count does not compensate for a failed guard.

| Screen | SD1.5 VAE oracle | T3 .2 oracle | Source majority .2 | New sibling matches | Real-impostor matches, canonical / marked | Decision |
|---|---:|---:|---:|---:|---:|---|
| Unchanged operational h | 3/6 | 6/18 | 1/6 | Not newly measured | Not newly measured | Reject transport-only repair |
| CD1 coarse-only, 32 bits | 6/6 | 18/18 | 6/6 | 4/6 | 0/552 / 0/552 | Reject lost texture discrimination |
| BI1 equal-energy, 32 bits | 5/6 | 10/18 | 3/6 | 2/6 | 0/552 / 0/552 | Reject stability and specificity |
| FG128 fine-only Gaussian | 6/6 | 17/18 | 6/6 | 0/6 | 2/552 / 0/552 | Reject real-source collision |

The round identifies two separate obstacles: transporting h would not cure the old descriptor's instability, while tested stable replacements either discard distinguishing texture or retain finite-sketch collisions. The FG128 positive result establishes a promising but incomplete combined representation/capacity observation. It does not prove that regeneration destroys all instance information, that 128 bits are inherently inadequate, that all possible methods fail, or that any new candidate meets M1a. E3 remains the retained method, with its original strengths and limitations.

## Independent review and allocation

The fresh Astra/high [independent review](descriptor-round-independent-review.md) **passes the evidence package**, with no material blocker, and recommends closing these fixed descriptor/dual-carrier protocols. Every candidate's scientific gate remains failed. No additional image experiment, threshold rescue, projection selection or conditional carrier is allocated from this evidence. This is not a count of three independent failed design families and does not invoke the original three-family honest-negative rule. Future method work needs a concrete new mechanism or consequential transferable comparison with evidence and a falsifier, rather than a numerical rescue of these consulted cases. Q1 readiness remains unestablished.

Two non-blocking implementation notes are corrected for future use: the native Rademacher docstring no longer asserts the Gaussian angle/pi identity, and the ceiling script captures its start timestamp before computation. Neither edit changes scientific calculations or rewrites prior receipts; the original timestamp limitation remains disclosed in the review. The residual receipt's absent start timestamp is retained as recorded.

The receipt-derived, visually inspected comparison figure and editable SVG are in MAIN `.thesis-build/analysis/descriptor-round-20261014/`; `scripts/plot_descriptor_round.py` reproduces them. Plotting packages are isolated from the experiment environments, with acquisition metadata in the downloads ledger. The figure is an exploratory comparison, not a matched-resource performance benchmark.
