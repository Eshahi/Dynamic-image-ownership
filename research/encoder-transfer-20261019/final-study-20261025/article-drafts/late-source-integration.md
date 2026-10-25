# Late-source integration bridge for future article development

Author: Codex author contributor, 2026-10-25. Supplementary author material only; this file is outside the accepted E3 article-review scope. It does not revise the reviewed manuscript, bibliography, protocol or review verdict. Proposed wording below remains a draft; no new measurement, experiment or source search was performed for this bridge. Reading coverage refers to the supplied primary-source cards, not replication or certification of their claims.

## Reading versions that must travel with the prose

| Source | Qualified technical evidence available | Boundary to retain |
|---|---|---|
| Shallow Diffuse | V2/full relevant text: **arXiv 2410.21088v5**, §§2.2–5, Appendices C.1/E. NeurIPS 2025 identity verified separately. | Do not assert conference-text equivalence. Both generation-time and post-generation insertion are covered. Mutable-main code observations are not pinned reproductions. |
| Intrinsic limits | V2: **arXiv 2610.08178v1**, methods, experiments and proof appendices inspected. | Preprint; local mathematical objections are author derivations, not published refutations or measured counter-results. |
| Semantic forgery | V2: **arXiv 2412.03283v3**, methods, experiments and Appendix F. | CVPR identity verified; publisher-text equivalence unverified. Use v3's corrected quality processing if retaining numbers. |
| Residual transferability | V2: **arXiv 2609.32241v1**, §§2–5 and Appendices A–G. | Preprint; image-to-image residual transplantation differs from cross-regenerator transfer. |
| GROW | Accepted CVF paper: selected primary method/experiment excerpts; **anonymous CVPR2026 submission #8345**, coauthor-hosted PDF, all 14 pages read as text. | Continuous accepted-version coverage and final supplement remain gaps. Full submission text must not fill them silently. |
| DistSeal | V2/full arXiv text: **2601.16140v1**; official README detection example inspected. ICML2026 metadata separately verified. | Proceedings full text/equivalence remain V1/unknown. |

See the [closure index](../literature/source-closure-index.md), [Shallow Diffuse card](../literature/shallow-diffuse-primary.md) and [GROW version closure](../literature/grow-access-closure.md). Original Semantic Imprinting remains **V1 identity/topic only**; inherited DiffMark/BiSLW leads remain V0. Neither status supports technical manuscript assertions. V2 denotes inspected primary technical text, not demonstrated truth.

## Priority insertion: derivative/subspace overlap

**Destination:** [related-work.md](related-work.md), after the initial insertion-site discussion, with a cross-reference from [mechanism.md](mechanism.md), immediately before “A full-chain local decomposition.”

**Proposed paragraph:** Shallow Diffuse is direct prior art for diffusion-derivative and subspace reasoning about watermark placement. Its posterior-mean-predictor Jacobian motivates shallow-timestep insertion; it supports both generation-time watermarking and post-generation DDIM-inversion insertion. Detection also uses inversion, a key and a timestep. Thus its overlap with the present question cannot be dismissed by calling it generation-only. The distinction here is the proposed derivative's object and endpoint: transporting a fixed image writer's exact encoder displacement through a target reverse path, decoder and reader toward signed chips and compound detection. This remains an unmeasured prediction task, rather than a new insertion algorithm. [Inspected arXiv v5, §§2.2–4](https://arxiv.org/html/2410.21088v5).

**Evidence boundary:** Its exact-linearity, bounded-Jacobian and random-direction premises do not establish arbitrary foreign-regeneration survival. FLUX adaptation does not establish that one fixed mark transfers between independently trained autoencoders. Do not claim first use of Jacobians, low-dimensional geometry or post-generation diffusion watermarking. Preserve the paper's structured-pattern/nonlinear-execution qualification in the [card](../literature/shallow-diffuse-primary.md).

## Mechanism insertion: component bounds versus signed forecasts

**Destination:** [mechanism.md](mechanism.md), after the rank/direction paragraph; cite also in related work's reconstruction discussion.

**Proposed paragraph:** Component-level analysis also appears in On the Intrinsic Limited Robustness of Latent-Based Watermarking, which studies an extraction chain and includes regeneration experiments. Such analysis motivates tracking intermediate changes, but a product of component upper bounds does not specify the signed response of a particular readable direction. For an exact Gaussian-observation posterior mean, the derivative is a posterior covariance divided by noise variance and is positive semidefinite; a universal contraction bound needs additional assumptions. Conditional invertibility arguments should therefore be separated from directional amplification and operational detection claims. [Inspected arXiv v1, §§3–4 and Appendices B–C](https://arxiv.org/html/2610.08178v1).

**Evidence boundary:** These mathematical qualifications come from the [local assumption analysis](../literature/intrinsic-limits-2026-primary.md), which preserves valid exact-MMSE PSD and conditional-invertibility conclusions. An exceeded sufficient robustness bound is not a rejection certificate or a maximum actual robustness radius. This reasoning neither validates our predictor nor contradicts the paper's empirical observations. Avoid describing its experiments as RST-only.

## Threat-model insertion: forgery and lineage

**Destination:** [threat-model.md](threat-model.md), after “Objects and adversarial objective”; related work's autoencoder-provenance discussion may cross-reference it.

**Proposed paragraph:** Black-Box Forgery Attacks on Semantic Watermarks demonstrates why watermark presence and provenance binding require separate evaluation. Its proxy-latent imprinting and reprompting attacks concern Tree-Ring and Gaussian Shading, rather than F5's compound endpoint. Appendix F additionally reports closely matching Common Canvas and SD2.1 VAE weights despite independently trained-generator descriptions. Generator labels consequently cannot substitute for autoencoder provenance. These observations motivate the threat distinction and lineage audit, without establishing encoder-only causation or an adaptive-forgery result for F5. [Inspected arXiv v3, §3, §4 and Appendix F](https://arxiv.org/html/2412.03283v3).

**Evidence boundary:** Do not infer an operational detector-query-free stopping rule from this text; the [card](../literature/semantic-forgery-2025-primary.md) records periodic evaluation and stopping ambiguity. Ordinary C0/wrong-owner controls remain specificity evidence, not an adaptive-security certificate.

## Threat-model insertion: what transfers and what is accepted

**Destination:** [threat-model.md](threat-model.md), after “Endpoints are not interchangeable.”

**Proposed paragraph:** Residual Transferability in Neural Image Watermarking studies transplantation of an image residual, or its estimate, onto another image. Its source and target are image roles, rather than independently trained regeneration encoders. Its CoverLock construction illustrates that residual recovery, message presence and content-compatible acceptance can differ. It is consequently relevant to copy transfer and binding, while supplying no direct result for this study's T3 cross-pipeline survival. Neither an assumed-bit false-positive tail nor a content-derived XOR wrapper establishes adaptive forgery resistance or lawful ownership. [Inspected arXiv v1, §§2–5 and appendices](https://arxiv.org/html/2609.32241v1).

**Evidence boundary:** Exact-residual diagnostics use clean originals; practical estimates have different access. Zero observed negatives and model-based tails must remain distinct. Do not infer near-duplicate safety or transplant CoverLock's protection onto F5. See the [card](../literature/residual-transferability-2026-primary.md).

## Related-work insertion: extraction alternatives

**Destination:** [related-work.md](related-work.md), after decoder-based methods; keep these as alternatives with different endpoints.

**Proposed paragraph:** GROW uses progressive generation-time latent-frequency guidance with direct VAE/DCT extraction; DistSeal learns a latent embedder with a pixel-domain bit extractor and optional model distillation. These methods show different insertion and extraction resources from F5. GROW's multi-generator experiments do not alone establish fixed-mark cross-regenerator survival, and DistSeal's inspected decoder-switch experiments do not establish independently trained-encoder regeneration robustness. Message recovery and bit accuracy remain distinct from F5's compound content-compatible C. [GROW accepted-paper excerpts](https://openaccess.thecvf.com/content/CVPR2026/papers/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.pdf); [DistSeal inspected arXiv v1](https://arxiv.org/html/2601.16140v1).

**Evidence boundary:** Cite GROW's [full submission-copy closure](../literature/grow-access-closure.md) explicitly for its geometry search; final-version searched-verification/FPR gaps persist. DistSeal technical assertions refer to arXiv, not uninspected proceedings text. Extraction timings are not searched-verifier cost guarantees.

## Assembly boundary

Any future comparison table should separate insertion site, verifier information, transfer meaning, inspected version and unresolved evidence. It is an author-planned synthesis table, not a new empirical result. All forecast, stage-transport and attack tables remain **hypothetical/prospective** until the authorized server study runs. None of these additions supports universal novelty, causal attribution to encoder training, publication readiness or extension of E3 acceptance to this supplement.
