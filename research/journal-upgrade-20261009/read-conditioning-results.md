# Cached F5-RC1 read-conditioning results

Exploratory paired decoder intervention on reused development pixels. Full detector fields are independently reduced by the stdlib analysis script; stored endpoint summaries are not inputs.

## Inventory and provenance

- screen: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1035-rc-screen; commit `4e7c707a173c7851c0370c898dc601373e7cb5c7`; completed; 36/36 unique planned rows, 0 failed, 0 missing, 0 duplicates; 173.859 s; USD 0.
- binding: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1040-rc-binding; commit `8fce9762c200fd06e97efaf03d2cbcb0f6a99f70`; completed; 31/31 unique planned rows, 0 failed, 0 missing, 0 duplicates; 72.235 s; USD 0.

Shared cached-stage duration: 246.094/1800 s; within cap: True. Routing checks cover every new screen positive/negative/compatibility call and all binding modes. No alternate-code search is evaluated.

## Screen

| Configuration | Quality | Strict clean exact q/h + acceptance | Joint q clean / SD1.5 / SDXL | C0 / wrong-owner any detections | Min VAE fixed-q score | Mean clean LPIPS | Cached eligible |
|---|---:|---:|---|---|---:|---:|---|
| RC2 | 12/12 | 12/12 | 12/12/12 of 12 | 0/36; 0/36 | 8.954981 | 0.021873 | True |
| RC3 | 12/12 | 12/12 | 12/12/12 of 12 | 0/36; 0/36 | 8.952951 | 0.021390 | True |

Ranking uses SDXL J, minimum VAE fixed-q score, lower clean LPIPS, then RC2. Both configurations and binding must be complete before advancement.
Ranked screen survivors: RC2, RC3. Cached advancement ready: True. This is not a T3 or full T5 pass.

| Configuration / condition | Native H → new H | Native D → new D | Native S → new S | Native F → new F |
|---|---|---|---|---|
| RC2 / clean | 9 → 12 | 9 → 12 | 12 → 12 | 12 → 12 |
| RC2 / sd15_vae | 0 → 0 | 0 → 0 | 12 → 12 | 0 → 0 |
| RC2 / sdxl_vae | 0 → 0 | 0 → 0 | 12 → 12 | 0 → 0 |
| RC3 / clean | 9 → 12 | 9 → 12 | 12 → 12 | 12 → 12 |
| RC3 / sd15_vae | 0 → 0 | 0 → 0 | 12 → 12 | 0 → 0 |
| RC3 / sdxl_vae | 0 → 0 | 0 → 0 | 12 → 12 | 0 → 0 |

Frozen clean compatibility: full acceptance native/new 12/12 of 12; exact D native/new 10/6 of 12. The q target is original recorded intended q; h is the frozen clean-decoded operational target. Original embedded h is unknown; compatibility does not recover historical intent.

## Cached binding compatibility

| Arm | Completed / planned | Native Q / D / F | New Q / D / F | F among Q | F among D | Semantic / own-h rejection among D |
|---|---|---|---|---|---|---|
| donor_positive | 6/6 | 6/6/6 | 6/3/6 | 6/6 | 3/3 | 0/3; 0/3 |
| recipient_sham | 6/6 | 0/0/0 | 0/0/0 | undefined (0 delivered) | undefined (0 delivered) | undefined |
| residual_0.5 | 6/6 | 0/0/0 | 0/0/0 | undefined (0 delivered) | undefined (0 delivered) | undefined |
| residual_1.0 | 6/6 | 0/0/0 | 0/0/0 | undefined (0 delivered) | undefined (0 delivered) | undefined |
| public_donor_synthesis | 6/6 | 5/5/0 | 5/5/0 | 0/5 | 0/5 | 5/5; 5/5 |
| public_recipient_authorization_demo | 1/1 | 1/1/1 | 1/1/1 | 1/1 | 1/1 | 0/1; 0/1 |

The original five exact public-donor deliveries retained with same-signal disabled read controls: 5/5. Newly accepted previously rejected non-demo rows: 0/24. Cached binding continuity: True.

Own-h predicates are recomputed from corrected h distance before semantic-status propagation. Disabled controls reuse the combined extraction; binding modes are also verified to use identical routing and extracted signals. Mode outcome tables and all 31 row endpoints are retained in the compact statistics JSON. Missing/failed rows remain in planned denominators; zero delivered denominators yield undefined conditionals.

The public-recipient row is a separate authorization counterexample. Donor target q/h remain the original cached decoded-donor targets, including any difference from intended q. They are not replaced by whichever payload decodes successfully.

Among the 5 exact donor deliveries, combined checking adds 0 observed rejections beyond semantic checking alone. Own-h rejection also occurs on 5/5; this panel cannot establish a combined-predicate benefit.

## Interpretation limits

The samples are small, previously seen development sources and transformed/cached pixels. Paired changes describe these calls, not population FPR, generalization or a causal decomposition of total system performance. Legacy bound fields remain unvalidated for the routed system. Quality is reused from exact cached pixels with source-record links; no new optimization or model inference occurs in this analysis.

VAE round trips are not diffusion regeneration. Matched T3, new candidate-origin donor synthesis and T4 continuity remain subsequent measurements. The inherited all-alpha T5 geometry panel has zero distinct-owner marked pairs and cannot certify literal T5 false-attribution continuity. Historical frozen M1a/M2 and original failed R1–R4 screens remain unchanged.
