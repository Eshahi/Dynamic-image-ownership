# Balanced-instance amendment: E3-BI1

Prospective method decision, 2026-10-14. This document selects **one fixed equal-energy coarse/detail blend**, followed by the unchanged full CPU gate. It does not select a favorable projection seed, weight or threshold from the next results. No science execution was performed to write this document. The parent owns execution, receipts and shared state.

## Evidence and decision

The retained unmodified-h oracle screen completed all 54 cached identities. Its joint oracle counts were clean 6/6, SD1.5 VAE 3/6, T3 .2 6/18 with one source majority, and .4 4/18. E3-CD1 completed in 19.609 seconds: all 24 canonical/full-clean comparisons matched; joint oracle counts were clean 6/6, both VAEs 6/6, .2 18/18 and .4 16/18. The .4 losses came from q, while its coarse h matched all 18. Both 552-row real-source impostor panels had zero matches; 23/24 q-nearest pairs had distance at least 10. Nevertheless CD1 failed: texture-sibling seeds 2,3,4,5 changed from legacy distances 11,8,9,8 to zero. Seeds 1 and 6 already matched under legacy, at distances 5 and 6. Do not pretend legacy solves every sibling case.

These results expose a real allocation question. Legacy reserves up to three quarters of feature energy for local detail; CD1 reserves none. CD1's .2 coarse cosines are approximately .9656 to .9965, whereas sibling coarse cosines are .9957 to .9996. Coarse content alone actually puts these impostors closer than many valid regenerations. A new projection seed or more coarse bits cannot repair that underlying ordering reliably.

Select **BI1: half coarse energy and up to half native detail energy**, with the existing detail floor. This is a symmetric allocation to the two already implemented content channels and the midpoint of their extreme energy allocations 0 and 1; it is not a fit to an observed best weight. Relative to legacy it doubles coarse energy and retains two thirds of the permitted detail energy. It tests whether regeneration retains enough native detail that the original 75% allocation was excessive. It does not assume that middle-scale structure distinguishes arbitrary redrawn texture. A new frequency band would add a second representation hypothesis, so this experiment does not introduce one.

A success would justify a carrier feasibility experiment. A failure closes this **one-shot scalar-rebalancing repair protocol**; do not follow it with .4/.6 weights or another projection stream. It would not prove that all feature representations, all weights, or jointly optimized future pixels are impossible. The next scientific question would have to change the representation or directly test information lost by regeneration, with its own prospective rationale.

## Exact representation and target

Reuse `revised_watermark_v4._perceptual_hash` feature extraction exactly. Let c be its 63 weighted non-DC DCT coarse coefficients normalized to unit norm. Let g be its concatenated `_local_detail` outputs, in exactly the native position/block order. Set F = `HASH_DETAIL_FLOOR * sqrt(len(g))` and f = g / max(norm(g), F), reproducing the native `_unit` zero-vector behavior below 1e-9. Thus norm(f) is at most one and may be substantially smaller; do not renormalize a weak-detail image to full detail energy.

The sole new vector is:

`z_BI = concat(sqrt(0.5) * c, sqrt(0.5) * f)`.

Use the resolved public profile key/config and **the existing literal projection label `b"perceptual-projection"`**, 32 bits, original feature width, native stream, sign tolerance and bit order. This deliberately keeps exactly the old hyperplanes: only the two channel amplitudes change. BI1 is an experiment name, not a new projection-domain label. A new seed would confound the energy intervention. Descriptor computation does not mutate the global native coarse-share constant or change retained E3 calls.

Require coarse norm >=1e-9; otherwise BI1 is unavailable and the complete gate cannot pass. This differs from returning a common zero word, and matches CD1's explicit unavailable policy. Preserve all detail floor/dead-zone/knee constants. Output the legacy h as a comparator and verify it against every available native cached call.

Compute the BI1 target once from **canonical unmarked RGB**, as in CD1. Never target a marked image or retarget after optimization. The canonical-target convention is a disclosed change from old operational h. Keep old operational-h oracle outcomes and add canonical-to-canonical-feature legacy distances so target convention is not mistaken for the effect of energy allocation. Native q targets and native J remain unchanged.

## Geometry, information and a falsifiable prediction

There are still 32 descriptor bits, radius 6 and far distance 10. Transport stays BCH(59,32,t=5); no carrier capacity or error-correction capacity is added. At an ideal independent uniform 32-bit impostor word, the radius-six ball has 1,149,017 members, probability about .000267526 and about 11.87 bits of rejection information. This is an illustrative combinatorial calculation, not a calibrated natural-image or adaptive-adversary FPR. BCH repairs transmission errors; it cannot recover absent content discrimination. Equal feature energy does not imply equal entropy, independence or equal influence of each bit.

For a source x and suspect y, store a = dot(c_x,c_y), b = dot(f_x,f_y), r_x = norm(f_x), r_y = norm(f_y). Under detail energy alpha, the exact continuous feature cosine is:

`rho(alpha) = ((1-alpha)*a + alpha*b) / sqrt((1-alpha+alpha*r_x^2)*(1-alpha+alpha*r_y^2))`.

This identity is valid for the actual floor-aware concatenation. For BI1, evaluate it only at alpha=.5 and check it against a direct normalized-vector dot product. Also report normalized detail cosine `b/(r_x*r_y)` when both norms are nonzero, and report unavailable otherwise. Treat zero-detail pairs explicitly, not as cosine one.

When both detail norms equal one, rho(.5)=(a+b)/2. Under an *ideal isotropic random-hyperplane expectation heuristic*, six mismatches out of 32 corresponds to rho = cos(6*pi/32), approximately .83147. With coarse agreement near one, BI1 would need detail cosine roughly above .663 to keep expected positive mismatch below six, while a sibling would need detail cosine below roughly .663 to be separated in expectation. More precisely the pair-specific boundary is b = 2*.83147-a. This is the decisive empirical question: **does the existing fine channel preserve more distinguishing information on genuine regenerated positives than on redraw siblings?** If it does not, balancing is unlikely to help.

The implementation uses public Rademacher directions, not isotropic Gaussian hyperplanes. Neither the angle/pi mismatch identity nor binomial concentration is an exact theorem for these coordinates. Thirty-two fixed bits can also cross the gate despite an unfavorable expectation. Accordingly continuous angles are an explanatory diagnostic only: no angular condition replaces a Hamming gate and no claimed universal impossibility follows from crossing .83147. Do not infer component angles from legacy Hamming distances; measure the components, including their floors.

Report component measurements for all positives and all six siblings, with aggregate ranges for the real-source panels. Report signed BI1 projection margins and which bits change relative to canonical legacy hashing. Do not compute a best alpha, select bits, whiten with panel statistics or use these diagnostics as a second decision rule.

## One CPU screen, identical full gate

Use the exact cached data and inputs in `stable-instance-amendment.md` and `journal_stable_instance.py`: all 24 Stage A canonical sources and full-E3 clean images; the fixed C arm IDs 30,72,73,89,127,165 with six clean, 12 VAE and 36 T3 .2/.4 seed9/10/11 suspects; both ordered 552-pair impostor panels; the same q-only nearest-neighbor rule and tie break; six synthetic sibling seeds 1..6 with size512, texture12 and detail seeds11/12. Regenerate those deterministic synthetic inputs only. No new real source, attack image, held-out observation, source selection or GPU computation enters this screen.

Reuse cached actual native J, supplying oracle BI1 transport only to compute `O_BJ = J AND (d_BI <= 6)`. Record every identity and comparator, including the failed legacy and CD1 outcomes. This is a content ceiling on those saved pixels, not a deployable detector or a robustness result for newly marked BI1 pixels.

Advance only when all of the following pass together:

1. All 24 canonical/full-clean BI1 comparisons match; all six C-clean O_BJ pass; SD1.5 VAE O_BJ >=5/6; T3 .2 O_BJ >=15/18 and source majority >=5/6. SDXL and .4 remain descriptive.
2. Zero BI1 matches in both complete 552-row real-source impostor panels. All 24 q-nearest pairs have distance >6, with at least 20/24 at distance >=10.
3. No legacy-rejected synthetic sibling becomes BI1-accepted. In particular seeds 2,3,4,5 must each have BI1 distance >6. Keep all six rows, including the two already accepted by legacy. The protected set is determined by the fixed legacy implementation, never by BI1.
4. Every planned image and calculation resolves. Missing artifacts and runtime/resource interruptions are inconclusive, never a pass.

Keep 0..6 match, 7..9 uncertain and >=10 mismatch. A sibling at 7 is not accepted but is uncertain; disclose that rather than calling it a confident rejection. Preserve the strict gate even if only one bit or one sibling causes failure.

CPU-only budget: 600 seconds inclusive, one ordinary committed probe and a new dev-run receipt. Cached native feature extraction can be shared within the run. Retain every result, including failures. No framework, launcher, new learned model, download or confirmatory machinery is needed. Before execution, mechanical checks must show that alpha=.25 reconstructs native `_perceptual_hash` on already loaded inputs and that BI1 uses the exact same projection material. Those checks validate implementation and do not score .25 as another candidate.

## Conditional carrier stage and claim limits

Only after the entire CPU conjunction passes, execute the already specified E3-DV1 two-bank mechanism from `next-round-mechanism-design.md`, replacing its h with canonical BI1 and naming the new candidate E3-BI1. Carry forward the full construction, quality, negative-control and resource requirements from that document and `stable-instance-amendment.md`: native q bank intact; 320 q-conditioned orthogonal h chips; the same weighted-coordinate orthogonality check and geometry fallback; BCH, margin4, 200 steps, canonical 43dB budget, fixed [1,.8] selector, conservative score convention and no expected-word fallback. The inference detector recomputes BI1 from the suspect and observes no canonical reference.

Keep the 450-second first-two-source subcap and 2,400-second total GPU cap; all-six strict clean quality and exact q/h/content admission; SD1.5 VAE dual exact/content >=5/6 before diffusion; then all 18 new .2 seed9/10/11 identities, requiring J18/18, dual exact/content >=12/18 and majority >=5/6. Observe all prescribed negatives, including cached C0 references and wrong-owner calls, with zero detections and complete denominators. No accumulated rewrite of an existing full-marked image. New marks require new transformed outputs; cached C1 pixels establish only the CPU ceiling.

A conditional GPU success still requires the prescribed M1a development identities and existing T4/T5 assessors against retained comparators. BI1 cannot advance by dropping instance discrimination or renaming the endpoint. A public 32-bit content sketch is approximate measured instance consistency, not exact identity or private authorization; public self-reissuance remains possible. Human visual assessments remain missing. No frozen E3/M2 output, protected file, claim ledger or held-out manifest is changed by this amendment.
