# Drift Kernel: inspected primary source and predictor boundary

Author contribution, 2026-10-25. Research only; no experiment or protocol amendment. This document is outside the completed independent-review scope.

## Identity and exact read receipt

**ID / citation key:** `ram-elavazhagan-2026-drift-kernel` / `Ram2026DriftKernel`. **Authors:** Gokul Srinath Seetha Ram; Rashmi Elavazhagan. **Title:** *The Drift Kernel: Why Diffusion Models Change Even When Told Not To*. **Venue/year:** CVPR 2026, pp. 43281–43289. **DOI:** not verified; null.

**Primary sources:** [CVF main paper](https://openaccess.thecvf.com/content/CVPR2026/papers/Ram_The_Drift_Kernel_Why_Diffusion_Models_Change_Even_When_Told_CVPR_2026_paper.pdf) and its linked [CVF supplement](https://openaccess.thecvf.com/content/CVPR2026/supplemental/Ram_The_Drift_Kernel_CVPR_2026_supplemental.pdf). Accessed 2026-10-25. Browser fetch returned 403; ordinary public PowerShell HTTP retrieval succeeded without authentication or challenge bypass. Only these papers were downloaded.

Local inspected artifacts reside under `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/cache-et-final/papers/`:

| File | Bytes | SHA-256 |
|---|---:|---|
| `drift-kernel-cvpr2026.pdf` | 5,755,052 | `CD423D46DD8B2B4CBE048D4B76D56BCCE09142B55B433AE1AE51E663F111A391` |
| `drift-kernel-cvpr2026-supplement.pdf` | 1,665,478 | `A7997910835C3B2756F648C52540EE7E27272EE84376676884B8DEFF5F31439C` |

Bundled Node/PDF.js extracted text in memory. Read all nine main-paper pages, with pages 4–5 separately reread after an output truncation, and all nine supplement pages. Inspected equations, methods, tables, captions and extracted figure labels; did not visually inspect raster figures, download code/data, execute reproduction scripts or inspect raw results. Main STATE read once. Verification means source inspection, not independent result reproduction.

## Source digest: direct evidence and author interpretation

**Direct evidence; high confidence in transcription, supporting prior-work relevance:** the paper studies no-op image drift using 120,000 baseline comparisons and 9,600 ablation outputs. Settings include 15 DDIM steps, guidance 5, seed 42 and strengths .1–.4 (main §4; supplement §0.8). Its decoder expansion yields `K ≈ Tr(J_D J_D^T) σ²+c` (main §3.1.1; supplement §0.1). Main abstract reports aggregate R²=.97 and per-model R²=.10–.26; Table 3 gives aggregated null/copy fits around .96–.98. Supplement §0.6 supplies synthetic decoder checks, not real-pipeline Jacobian measurements. **Author interpretation; not independently established:** decoder geometry explains prompt-independent drift.

**Inconclusive details:** native strength and Gaussian standard deviation share σ without a demonstrated conversion. Main Figure 7 and supplement §0.6 specify different curved decoders. Supplement §0.16 says slope differences stay within .006, whereas Table 7's SD21 difference is .0116. These details require raw-release clarification before quantitative reuse. Supplement §0.8.4 documents native-resolution inference followed by resizing for metrics; the pipeline therefore includes more than a decoder.

This digest is under 200 words; there are no direct quotations. The following analysis is an independent mathematical assessment, not additional source findings.

## First-principles assessment: conditions the proposed study must not assume

**Agent inference; high confidence under stated smoothness assumptions; qualifying the decoder-only interpretation.** Let `L_s` be the actual post-denoising latent at native strength `s`, and let `x` be the input image. Independently of any Gaussian assumption,

`E||D(L_s)-x||² = ||E D(L_s)-x||² + Tr Cov[D(L_s)]`.

This is an exact bias–variance identity. Define `μ_s=E L_s`, `η_s=L_s-μ_s`, `Σ_s=Cov L_s`, `b_s=D(μ_s)-x`. Locally linearizing only the decoder gives

`E||D(L_s)-x||² ≈ ||b_s||² + Tr[J_D(μ_s) Σ_s J_D(μ_s)^T]`.

Recovering a single decoder trace times `s²` requires, among other conditions, `Σ_s=s²I`, suitably constant decoder Jacobian and baseline bias, and small nonlinear remainder. Those are open assumptions for an actual diffusion pipeline. A native strength selects a timestep and a schedule-dependent corruption amplitude; denoising then changes both mean and covariance. A source's dependence on its conditioning also changes the point at which the decoder Jacobian is evaluated. Therefore even a fixed decoder does not imply prompt-independent sensitivity.

**Agent derivation; curvature qualification.** For centered isotropic Gaussian noise `η=σξ`, with fixed expansion point, write the second-order decoder approximation as `D(μ+η)-x ≈ b+Jη+H[η,η]/2`. Its squared-error expectation contains

`||b||² + σ²||J||_F² + σ² b·h + (σ⁴/4) E||H[ξ,ξ]||²`,

where `h_i=Tr(H_i)`. Odd Gaussian moments remove the linear–quadratic cross term. Thus curvature can change the quadratic coefficient through baseline bias and introduce fourth-order terms; it is not generally a strength-independent intercept. The displayed fourth-order contribution is for the truncated second-order expansion, not a complete fourth-order Taylor law: third derivatives contribute further terms. Nonzero-mean perturbations introduce additional bias cross terms. Correlated noise sources require their cross-covariances inside `Σ_s`, rather than an independence assumption.

**Agent inference; normalization boundary.** An unnormalized squared Euclidean norm and mean squared pixel error differ by output dimension. Resizing and feature-based metrics introduce their own operators; a pixel-decoder trace cannot be transferred unchanged to LPIPS, CLIP or reader scores.

## Consequence for the existing full-chain transport predictor

Generic Jacobian-based drift prediction is unavailable as an unqualified novelty claim. This paper is close prior work, although it does not establish our proposed marked-versus-unmarked directional reader response.

For an exact fixed-noise chain `G_s` and mark displacement `δ`, a signed reader response is locally `∇r(G_s(x))^T J_G_s(x)δ`. A total sensitivity such as `||J||_F²` cannot recover that sign: `J` and `-J` have identical traces but opposite directional responses. Nor can aggregate image drift establish content binding or operational detection.

The frozen study already proposes a privileged full-chain chip JVP, observed C0 baseline and fitted global κ; none has been measured. Keep those definitions and qualifications. Do not replace its chain derivative with decoder sensitivity, import the paper's σ convention, add a fitted curvature offset, or treat aggregate R² as evidence for per-source predictive accuracy. Native-cell calibration and finite-remainder limitations remain essential. This source narrows positioning; it supplies neither a validated replacement predictor nor a reason to change the protocol.
