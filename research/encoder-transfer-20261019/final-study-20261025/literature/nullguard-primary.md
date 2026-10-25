# NullGuard: primary-access closure and dimensional audit

Recorded 2026-10-25 by Codex agent. **Evidence grade: V1-plus, indexed primary excerpts only; not V2.** Direct paper/forum opens return OpenReview browser verification. Methods and experimental passages were inspected through the search engine's indexed primary PDF, but full-paper/appendix coverage and a stable version/date were not obtained. This card cannot support a definitive novelty exclusion or a reproduced-method claim.

## Identity and status

Title: *NullGuard: Null-Space Embedding for Driftless Invisible Image Watermarking*. The author-maintained [publication page](https://tanvirnwu.github.io/pages/publications), lines 27–37, names Inzamamul Alam, Md Tanvir Islam, Juhun Lee, Sangtae Ahn and Simon S. Woo, and self-reports BMVC 2026 acceptance. Its Paper link leads to [OpenReview cNEshxVcWg](https://openreview.net/forum?id=cNEshxVcWg). The inspected anonymous PDF header says ICLR 2026 under review. BMVC acceptance is an author claim, not independently verified proceedings metadata; ICLR acceptance is unsupported. Search-engine relative dates are not version dates.

## Paper digest (under 200 words)

Indexed primary passages describe EOS-text sensitivity, SVD directions, keyed rotation, masked latent insertion, scalar refinement and forward-score verification. Methods/experiments locators: pp.3–7, equations 1–6, Algorithms 1–2, Tables 1–3. Algorithm 2 uses a channel slice replicated spatially. Verification explicitly mentions DDIM-inverted latents. Table 3 reports FPR .060 at its default setting. Table 1 reports Zhao23 WDR .990/.994 on COCO/DiffusionDB. These are reported values, not independently checked evidence of independent-encoder regeneration transfer.

## Local mathematical audit of the printed excerpts

These are our deductions from incomplete printed specifications, not allegations about unseen implementation.

1. **Coordinate contract unresolved.** A scalar mean-noise derivative with respect to an EOS embedding acts on text perturbations in R^d_e. A VAE residual instead lives in R^(C h w). Equal numerical length, or slicing text coordinates to C and repeating over h,w, cannot establish a differential correspondence. Even if B maps text vectors into latent coordinates, the implication J_e w = 0 does not imply J_z B w = 0. One needs the latter operator or a proved intertwining identity. Concatenation across backbones also needs explicit handling of unequal text dimensions. The printed aggregate orientation and selection of right singular vectors must agree: a d_e-by-N matrix has N-dimensional right vectors, whereas an N-by-d_e matrix has d_e-dimensional right vectors. The card does not silently repair that ambiguity. Spectral shaping and masking can also leave a nullspace unless the relevant operator commutes with those transforms or the result is reprojected.

2. **Scalar-refinement degeneracy.** Taking the printed binary-mask construction literally, set r = alpha (M elementwise w) and D = diag(1-M). Then Dr = 0 exactly, hence J^T D r = 0 for every J. With positive regularization the printed scalar update is zero. A nontrivial optimizer would need a different residual, support, or forward nonlinear map. This is an algebraic consequence of the displayed algorithm, not an executed test; omitted implementation detail could change it.

3. **Detection and security claims require separate closure.** The printed verification does not justify calling the detector inversion-free. Suspect VAE encoding, a model/scheduler, keyed text perturbations, a fixed basis and calibration are material resources. Full original-image independence and exact deployment cost remain unverified without the appendix. Random-key calibration on a suspect and a Gaussian test do not by themselves prove population false-positive control. Rotating within a fixed subspace does not establish unforgeability, ownership, or content binding; a cryptographic reduction or explicit attacker experiment is needed.

4. **Transfer limitation.** A Zhao23 column is an attack label, not a documented encoder-independence test. Its exact attack assets, noise schedule, strength and encoder lineage were not recovered. The targeted searches below did not expose an SDXL/FLUX independent-encoder grid; this access-limited statement is not proof that the complete paper lacks one.

## Relation to the frozen F5 study (local inference)

The local [mechanism](../04-mechanism.md), lines 104–157, and [theory design](../analysis/theory-design.md), sections 6–7, forecast signed reader-chip transport along the unmarked C0 full target trajectory, then apply a declared C0 semantic proxy. That is a target-specific prediction about a fixed final RGB residual; NullGuard's indexed description is a construction/detection method. An EOS sensitivity nullspace neither proves nor disproves this signed full-chain forecast. Local differentiability and semantic preservation also do not entail regeneration survival. Our law remains unmeasured, privileged and computationally unresolved. This lead motivates a coordinate-space caveat only; it adds no baseline, protocol amendment or novelty claim.

## Primary locators and search receipt

- [Supplied hash-addressed PDF](https://openreview.net/pdf/d9a4e7d3814a2b9c5b9c1b05d1a4e5ab45ce7392.pdf): direct verification wall; search-indexed pages 3–7 exposed.
- [ID-addressed PDF](https://openreview.net/pdf?id=cNEshxVcWg): same title/method in indexed excerpts; direct verification wall. Byte identity between these URLs is unverified.
- [Author-maintained publication page](https://tanvirnwu.github.io/pages/publications): identity and self-reported later venue; Paper link targets the above forum.
- Search engine: web search tool, 2026-10-25. Queries: `"NullGuard" watermark nullspace`; supplied PDF hash; `"NullGuard" "EOS"`; then `site:openreview.net/pdf "NullGuard"` paired with `EXPERIMENT`, `rotation z`, `regeneration`, `forward Verification`, `Verification threshold`, `Wk embedding`, `Experimental Setup`, `SDXL`, `Stable Diffusion Settings`, `Implementation Details`, `Null-Space SVD`, and `regeneration SDXL`. Useful hits were primary PDF excerpts for nullspace construction, both algorithms, verification and Tables 1–3. Non-primary aggregator/LinkedIn hits were discovery aids only, not method evidence. No paper/code/model/data was downloaded and nothing was executed scientifically.
