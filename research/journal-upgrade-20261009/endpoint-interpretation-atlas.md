# Endpoint interpretation and manuscript evidence map

Working analysis, Codex agent, 2026-10-13. This document reorganizes already reviewed results. It introduces no threshold, experiment, held-out selection, significance test or human judgment. It is not the protected claim ledger or a finalized thesis section.

## The research question that remains

When regeneration changes an image, which of payload readability, agreement with its content, exact-instance identity and final acceptance survives? The current study measures these separately. Whether their empirical separation adds enough knowledge beyond existing watermarking work to justify an article remains open. Definitions alone are not a contribution.

The strongest present observation is exact recovery of E3's content-conditioned semantic payload in one pinned regeneration channel. The evidence does not establish general ownership verification, matched-FPR superiority or a new causal explanation of robustness.

## Keep the decisions separate

| Endpoint | Question answered | What it does not establish |
|---|---|---|
| S: found semantic signal and content match | Does the native semantic detection rule accept? | Exact recovery of the intended payload |
| Q: readable exact semantic payload | Does the unchanged reader declare the message readable and recover the evaluator's intended bits exactly? | Agreement with the attacked image's content, authorization or instance identity |
| J: exact checked semantic payload | Is Q true and does the content-agreement rule pass on that call? | Independent human judgment of semantic preservation |
| H: exact instance payload | Are the operational/native instance bits recovered? | Target equivalence between methods or a cryptographic ownership certificate |
| F: full acceptance | Does the complete native decision accept? | General security outside the stated owner, reference and attack access |
| Y: original primary composite | Does clean eligibility pass and does a majority of attacked S calls pass? | Isolated regeneration survival or an externally calibrated operating point |

J implies Q on the same call. Majority J therefore implies majority Q when the same three scheduled calls and adverse missing-outcome convention are used. Q includes the frozen readability rule; it is not a new unthresholded raw-bit endpoint. Q and S are not interchangeable. Clean eligibility is a separate gate; do not draw a sequential waterfall that subtracts it from attack counts as if all failures occurred on nested sets.

## Observed separation in the frozen study

These counts are transcribed from the independently reviewed [M2 report](e3-s1-m2-results.md), with all 300 planned sources retained. The first four columns are predeclared descriptive source-majority outcomes; the last is an explicitly post hoc arithmetic decomposition.

| Method / SD1.5 strength | S | Q | J | F | Majority Q without majority J |
|---|---:|---:|---:|---:|---:|
| E3 / .1 | 287 | 294 | 287 | 0 | 7 |
| E3 / .2 | 284 | 297 | 284 | 0 | 13 |
| Native v5 / .1 | 283 | 81 | 80 | 0 | 1 |
| Native v5 / .2 | 232 | 17 | 17 | 0 | 0 |

The last column is Q minus J, valid because of the implication above. It describes source-level decision disagreement. It does not identify the exact failed seeds, prove semantic drift, or establish that the content predicate made an error. Equal aggregate E3 S and J counts also do not prove that their success sets coincide.

The large E3-v5 primary composite differences (+43.33 and +49.67 percentage points) coexist with different clean eligibility (294 versus 159) and different instance-target conventions. They must remain labelled composite differences. At .1, raw S differs by only four sources, whereas exact Q differs by 213. Endpoint choice materially changes the apparent comparison; no additional p-values or retrospective primary endpoint are introduced here.

The native methods do not operate at independently matched FPRs, and only alpha was established as an owner. This table motivates fair follow-up work; it cannot rank E3 against external methods.

## A traceable development failure case

The fixed [H1 experiment](fresh-mechanism-results.md) supplies a cleaner example at the individual-call level. Both chipwise and symbol-average objectives return exact q on all 36 regeneration identities per arm. Checked J fails on the same two identities: source 72, strength .4, seed 9; and source 165, strength .4, seed 10. These are content-agreement rejections despite exact payload recovery. Human semantic assessment is missing, so neither identity is classified as a detector false rejection or as a valid semantic-preserving attack.

The intervention lowers clean within-symbol heterogeneity on all six paired sources yet yields no checked-recovery advantage. This rejects the proposed benefit on this panel; it does not prove the objectives equivalent at every setting. Do not select stronger attacks or showcase images after outcomes to turn the negative screen into a positive claim.

## Manuscript structure supported by this evidence

Working title: **Semantic payload recovery and instance acceptance under diffusion regeneration**. This is a scope label, not an assertion of publication novelty.

1. State the existing-image setting, three threats and detector side information. Distinguish recovery, content agreement, identity and authorization before introducing metrics.
2. Describe the actual image-domain E3 writer and VAE/CLIP reader. Keep the original proposal's latent/lightweight obligations explicitly unresolved.
3. Present the frozen 300-source study with its original primary endpoint, complete denominators, quality misses, safety blocks and descriptive endpoint table.
4. Present development evidence separately: refinement saturation, the failed 25% median-cost screen and the valid but negative H1 intervention. These constrain the mechanism story rather than establish one.
5. Add external comparisons, independent transfer and human admissibility only after those studies exist. Until then, mark these sections as missing evidence, not anticipated positive results.
6. Explain the measured limits: no post-regeneration full acceptance, no demonstrated added combined-binding value, limited owner scope and uncalibrated error tails.

An empirical article would additionally need a reproducible, consequential finding across relevant methods and channels. Repackaging this table as a novel taxonomy or assuming that more samples create novelty would be unsupported. A methods article still requires a distinct mechanism or useful quality/robustness/cost tradeoff that survives fair controls.

## Human evidence boundary

A future blinded admissibility panel must sample by a fixed rule, include successes and failures, and keep raters unaware of method and detector outcomes. It should separately ask about preserved entities/actions/scene and acceptable visual change, with a prespecified disagreement policy. It must not ask whether an image "contains the watermark" or use the detector's own CLIP score as the human answer. No ratings or institutional decision are fabricated here.

This atlas is complete as a bounded local analysis deliverable. It does not authorize a new held-out run, freeze an article claim, amend the proposal or imply human M2 acceptance.
