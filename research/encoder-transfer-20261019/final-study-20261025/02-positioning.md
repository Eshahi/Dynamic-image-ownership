# Positioning and claim boundary

WP1, 2026-10-25. Search scope: [root queries R01–R13 and delegated cluster logs](literature/search-log.md), with inspected versions in each source manifest. No exhaustive literature search or first-ever claim is made. This document is a research decision, not a publication-readiness verdict.

## Proposed contribution

The defensible target is a **stage-resolved, prediction-tested account of the transfer failure of an encoder-directed image watermark under generative reconstruction**. Its value would come from a successful or cleanly falsified prediction, a useful counterexample to a simpler explanation, and a reproducible evaluation with explicit detector information and quality constraints. F5 is a case study, supported by v5, WAM and VINE-R comparison arms. The existing development data alone support only a bounded empirical account.

A provisional article question is: *Why can a mark survive a foreign autoencoder round trip yet disappear under a mild full regeneration, and can measured signal transport predict that transition on unseen sources and a new family?* “Independent-encoder robustness” can name the operational test, provided every conclusion states that complete pipelines differ. It cannot name an identified encoder-only cause.

## Closest prior work and the necessary separation

| Prior work | Overlap | What our proposed study would have to add |
|---|---|---|
| [Zhao](literature/attacks/zhao-provable.md), [WAVES](literature/attacks/waves.md), [VINE](literature/attacks/vine-wbench.md) | Regeneration removal, benchmarks, fidelity tradeoff, regeneration-resilient marks | A predeclared explanatory prediction beyond another robustness table. |
| [MarkNull](literature/attacks/marknull.md) | Proxy latent manipulation and transfer | Measurement of fixed F5 residual transport under independently trained AEs, with separate native denoising and readout effects; no theorem borrowed outside its assumptions. |
| [Stable Signature](literature/watermarks/02-stable-signature.md), [LaWa](literature/watermarks/08-lawa.md) | Autoencoder reconstruction as an attack and method-dependent retention | Distinguish decoder-trained insertion from F5's image-space optimization through an encoder; do not generalize a direction of the effect across insertion sites. |
| [PhotoGuard](literature/transfer-theory/photoguard.md), [Demontis](literature/transfer-theory/demontis.md), [Tramèr](literature/transfer-theory/tramer.md) | Optimized perturbations, gradient alignment and transfer failure | A detector-specific generative-channel model whose quantities can be measured without using the target confirmation outcomes. |
| [Jeon et al.](literature/transfer-theory/jeon-limits.md) | Latent signal/noise tradeoff through a fixed renderer | State which assumptions fail for this public content-derived watermark; use a conditional local model, not an information-theoretic security claim. |
| [Unresolved rank-ratio lead](literature/transfer-theory/rank-ratio-unverified.md) | Direction scrambling and apparent cross-VAE fragility | Resolve primary provenance before any priority claim. Our proposed full-pipeline conditional transport is distinct from a pure round-trip model, but that alone does not prove novelty. |

## Three possible outcomes, fixed before new computation

**Predictive mechanism outcome.** Measurements on development images support a small model; frozen parameters predict held-out source outcomes and an excluded family with useful improvement over simple quality-only and noise-only comparators. This supports a conditional mechanism account within tested pipelines. It still does not identify “independent training” as a randomized cause.

**Bounded empirical outcome.** The transfer model fails, is not identifiable, or does not improve held-out prediction, while the source-level pipeline contrast replicates. Retain ROUTE C: report the failure, round-trip/full-pipeline distinction and limits. Do not replace the model after seeing confirmation and call the replacement confirmed.

**Failed confirmation or inadequate feasibility.** The fresh cohort, quality gate, negative gate, required model access or power condition fails. Report that outcome and do not claim the existing development pattern generalizes. Missing a third family limits out-of-family H4; it must not silently turn into an easier in-family test.

## Claims the article must not make

- “The independently trained encoder causes removal.” The current interventions change multiple components, and statistical independence of learned mappings is unproved.
- “High latent energy guarantees robustness.” Readout direction, background displacement, posterior noise, denoiser transport and nonlinear decisions can dominate energy.
- “Equal strength means equal severity,” or “lower LPIPS proves human-equivalent quality.” Schedule, latent scale, resolution and distortion support differ.
- “F5 outperforms or underperforms all latent watermarks.” It is an image-domain comparator with different payload, detector resources, quality and endpoints.
- “Zero false positives,” without denominator, source population and uncertainty bound. Zero observations do not establish zero probability or cryptographic security.
- “Semantic verification proves ownership,” “a public owner string is a secret key,” or “a random-code tail proves adaptive forgery resistance.” None follows.
- “The proposal's latent insertion/lightweight extractor is validated,” “T4/T5 are resolved,” “the registry passed,” or “Q1 acceptance/readiness is established.” These are unsupported or contradicted by the retained project record.

## Minimum scientific improvement required

WP2 must expose at least one falsifiable contrast between norm-only, quality-only and signed-readout transport explanations. WP5 must commit to source-disjoint evaluation, frozen attack selection, fixed H1–H6 decisions, explicit multiplicity and useful uncertainty. The law's parameters must be measured in Phase A, and its predictions saved before Phase B target outcomes are read. If only family intercepts explain the development grid, call that a descriptive fit and retain the negative mechanistic result.
