# Future component-identification contract for F1/F2

Authored by Codex, 19 October 2026. **Future-only conceptual design; NOT RUN, not a preregistration, execution contract, manifest, approval, or independent milestone review.** This document refines the scientific identification question in [F1/F2](07-gap-closure-plan.md); it changes neither the frozen historical method nor its results. New external baselines remain closed until the user explicitly reopens them. No pixels, descriptors, models, experiments, simulations, timing, count computations, downloads, or Python were used for this document.

The clock at this bounded follow-up's start was `2026-10-19T04:52:55.2135445-08:00`. The original `2026-10-19T04:04:04.3769833-08:00` deadline had expired; the parent relayed the user's continuation instruction. No deadline is reset. Only this file is authored here.

## 1. Question and correction to F1

The defensible question is whether a specified extra decision condition improves **correct-record recovery versus any-wrong-record risk** at a useful operating point, on a declared population and bank. It is not whether adding a gate reduces accepted records: that follows mechanically from conjunction. Neither a favorable component result nor a new control establishes method novelty, cryptographic binding, lawful ownership, or active-forgery security.

The earlier F1 proposal contrasted the full pipeline with owner detection plus the same descriptor check. That contrast changes **both successful message reading and code-distance selection**. It cannot identify the code-distance increment alone. The minimal additional control is owner detection plus readable valid code plus the unchanged descriptor rule, **without testing that code against the record**. Full versus this control isolates code-distance selection in the decision rule. The comparison is a paired algorithmic deletion analysis, not a causal intervention on the writer, image or data-generating process. F1 and the manuscript now incorporate this correction.

The saved-output observation [EV-77](01d-e3-owner-gate-audit.md) is motivation, not new component evidence: completed historical beta calls already had `found=false` and `read=false`, so none reached q or content checks. This post-hoc Boolean observation does not estimate q's incremental value, prove it is useless, or cover unavailable queries or active beta re-marking. The frozen overall result and complete-bank qualification remain as recorded in the [evidence ledger](01-evidence-ledger.md) and [theory note](05-theory-security.md).

## 2. Objects, flags and the preserved full rule

Let `i` index a scheduled query, `a` an owner, and `r` a record in a prospectively fixed bank `B`. Each record has an immutable record identifier, owner, expected content-derived code `q_r`, reference descriptors and declared enrollment provenance. A public owner identifier is not an authenticated identity. The bank, owner candidate list, record-to-owner mapping, and expected positive target must be fixed independently of test outcomes.

| Symbol | Definition | Boundary |
|---|---|---|
| `O_ia` | The completed native call's `semantic.found` flag, by itself. | This is pure owner detection. Do not redefine it as `found AND read` or infer it from a later accepted record. |
| `R_ia` | The completed native call's `semantic.read` flag, by itself. | This flag is a decoding outcome, not record correctness. Preserve the joint O/R table, including unexpected combinations. |
| `V_ia` | A decoded code is present and valid under the frozen representation/schema. | This is observability/validity bookkeeping, not a new threshold. A malformed code or contradictory call is an invalid output, not a successful read, a q mismatch, or an imputed negative. |
| `Q_ir` | `d_H(qhat_ia,q_r) <= 6`, where `a=owner(r)`, when both codes are valid. | It is record-dependent. The content-derived code is not assumed uniform, independent of F, random, secret, or unique. Without a valid read it is not evaluated. |
| `F_ir` | The unchanged frozen descriptor decision on query and reference. | It includes the valid D1-abstention branch. Missing/invalid artifacts are not that branch. |

For valid observations, the preserved full acceptance predicate is `O AND R AND Q AND F`. Explicit V notation below merely makes the existing requirement for an evaluable decoded code visible: it does not alter the old `native_q`/`qmatch` rule. Source text inspected: `scripts/m1b_registry_analysis.py`, `native_q`, `qmatch`, `attribution`, and `vector`; no source function was executed.

F remains: when D1 similarity is available, accept only if `D1 >= .0594367 AND B1 >= .90`; when D1 is unavailable through the **explicitly valid native abstention path**, use `B1 >= .99`. Required B1, reference data and validity checks must still exist. Missing files, failed extraction, malformed vectors, absent status, and corrupt cache cannot trigger fallback. The exact versioned old implementation governs any finer distinction; a later incompatibility is disclosed rather than silently repaired in this study. The historical thresholds, Hamming radius, operational negative labels and original outcomes are unchanged.

## 3. Minimal control lattice and identification

All record-valued local controls use the **same query, record bank, native call outputs, reference representations, F scores and thresholds**. They do not independently fit thresholds, choose a favorable record, rerun the writer, or adapt bank membership. A later study must make the needed stage outputs available regardless of short-circuit execution; a stage that was never evaluated is not an observed rejection.

| Arm | Accepted record set, when inputs are valid | Purpose |
|---|---|---|
| Owner-only | No record set; owner set `{a: O_ia}` | Pure owner discrimination. Record correctness is **not applicable**. |
| F | `{r: F_ir}` | Identical frozen fingerprint-only control. |
| OF | `{r: O_i,owner(r) AND F_ir}` | Owner detection plus content, without reading or q selection. |
| ORVF — **required additional control** | `{r: O AND R AND V AND F_ir}` | Readable-code availability plus content, without q selection. |
| ORVQ | `{r: O AND R AND V AND Q_ir}` | Pointer stage without content verification. |
| Full | `{r: O AND R AND V AND Q_ir AND F_ir}` | Unchanged full method. |

ORV need not be a separately deployed arm: it is a stage diagnostic obtainable from the same declared calls. R and V must be reported separately so a schema fault is not attributed to decoder behavior. If every completed `read=true` call has a valid code, ORVF is exactly the desired owner-plus-read-plus-F control. Otherwise the pointwise code-distance decision is identifiable only where its inputs are well defined; **the primary estimand still includes all scheduled attempts**, with invalid/missing outcomes handled by the bounds below. A valid-input-only estimate is secondary, and the apparent benefit of rejecting malformed output is not credited to q.

The required paired contrasts are:

1. **Code-distance increment:** Full versus ORVF. Only Q is deleted.
2. **Read-availability increment:** ORVF versus OF, with separate disclosure of invalid/missing V. This is the combined readable-code prerequisite if validity failures occur; it must not be called pure decoding benefit then.
3. **Content-check increment:** Full versus ORVQ. Only F is deleted, including its fallback branch.
4. **Composite candidate-gate increment:** Full versus F, and OF versus F. These describe joint/owner contributions; neither is evidence of q-specific synergy.

Under common valid inputs and the same bank, `Full ⊆ ORVF ⊆ OF ⊆ F` and `Full ⊆ ORVQ`. Consequently, any-wrong-record acceptance cannot increase along those subset relations, but inclusion of the correct record cannot increase either. Exclusive correct attribution can increase by removing wrong co-acceptances, or decrease by removing the correct record. A statistically nonzero reduction in wrong acceptance alone is insufficient. Do not multiply marginal error probabilities or infer independent factors. Missingness or arm-specific recalibration can break an apparent nesting comparison; such a comparison does not isolate this component.

The study does not require a larger factorial sweep, retraining, new q variants or descriptor redesign. An owner-only arm must never be converted into a fictitious correct record by selecting the first or best record owned by that owner.

## 4. Task, labels and bank contract

The prospective label policy in [20-fresh-data-plan/README.md](20-fresh-data-plan/README.md) controls provenance, grouping, consumed-pool exclusions and untouched assignment. This file adds no asset IDs, cohort selection, numerical eligibility cutoffs, split seed or sample-size adequacy claim. COCO/DIV2K test and known Tears of Steel outcomes cannot select a new held-out operating point.

The primary component task must include owners with several distinct records, same-owner wrong-record opportunities, and legitimate positive regenerations. Otherwise owner separation can appear to solve record identification by construction. Fix records per owner, owner count, distractor composition, same-source derivatives, candidate visibility, positive target and bank completion requirements before outcomes. Distinct records may have the same q; retain such records rather than deduplicate favorable collisions away. Preserve all accepted records and owners; a displayed `best_record` is not the decision.

For each query define, before method outputs, an admissible correct-record set `T_i` and the intended original record `r*_i` for positive recovery. Prefer one intended original record for the primary task. If multiple references are scientifically equivalent, fix that equivalence and report exact-original recovery separately; do not expand T after observing a false acceptance. A genuinely out-of-bank negative has `T_i=empty`. Passive beta enrollment is a competing claim: beta's derived copy is not silently added to the acceptable original-attribution set. This is a task convention about the original registered record, not proof of legal ownership.

Keep panels separate: positive regeneration, same-owner distinct capture, cross-owner look-alike, unrelated negative, clean/unmarked/wrong-owner controls, copy transfer, and passive competing enrollment. Active beta re-marking belongs to F4 and remains unexecuted and separately authorized. The historical gray-PSNR relation and new blinded provenance/identity labels are distinct endpoints. Uncertain labels remain uncertain, not relabeled to improve specificity. A fixed schedule of pairs/seeds is essential because the chance of at least one error grows with the number of opportunities.

The entire planned bank remains the reference for each scheduled query. If a record is unavailable, the observed sub-bank is disclosed but is not renamed the planned bank. Correct-record inclusion may be assessable with other records missing, while exclusivity, no-wrong-record acceptance and certified abstention may not be. Any population extension across banks needs separate bank sampling/replication and its own estimand; a single fixed-bank result does not establish registry-size-independent risk.

## 5. Outcomes that preserve utility and error

Let `M_hi` be arm h's accepted-record set and `A_hi` its owner projection. On completely known decisions, define:

| Outcome | Predicate | Interpretation |
|---|---|---|
| Correct original included, C | `r*_i in M_hi` | Positive recovery, even if a wrong record also passes. |
| Exclusive original recovery, X | `M_hi = {r*_i}` | Usable unique exact-record attribution; stricter than C. |
| Any wrong record, E | `M_hi \ T_i` is nonempty | Includes wrong co-acceptance when the correct record also passes. |
| Same-owner wrong record | Some accepted record is outside T but has the intended owner's identifier. | Detects failure hidden by owner-only accuracy. |
| Any wrong owner | Some accepted owner is outside the predeclared legitimate owner set. | Includes correct-plus-wrong-owner ambiguity; not only unique beta. |
| Record / owner ambiguity | `|M_hi|>1` / `|A_hi|>1` | Report both; record ambiguity can occur within one owner. |
| Certified abstention | All planned record decisions are known and `M_hi` is empty. | Distinct from missing/invalid/incomplete output. |

Report wrong-only output as well as C-plus-E, but never replace E with wrong-only. On out-of-bank negatives, any record acceptance is an error. Owner-only reports owner sensitivity, any wrong owner, owner ambiguity and abstention; C, X, same-owner record risk and record ambiguity are not applicable.

**All-attempt operational recovery** counts a scheduled attempt as delivered correct recovery only when a usable output establishes C (or X for its stricter endpoint). Failed marking, blocked/unavailable query, missing required code/descriptor, or unreturned decision contributes no delivered recovery and remains in the denominator with its reason. This is a service-yield convention, not an assertion that the unobserved scientific decision is negative. Report both operational yield and missing-outcome bounds for the underlying decision; do not count unavailable outputs as observed zero false accepts. The full risk/utility vector and availability rates accompany any scalar headline.

## 6. Paired estimands and inference assumptions

These definitions are prospective proposals, not choices approved by a human. Let `c` identify the conservative creator/production dependency component, `s` its source/capture group, and `J+_cs`, `J-_cs` fixed scheduled positive and error-opportunity slots. All arms use the same slots and bank. For each arm define source recovery `C_hcs` as the mean C over the scheduled positive slots and source risk `E_hcs` as the indicator that at least one E occurs over the scheduled negative/competing slots. The latter has a fixed opportunity count; it cannot be compared across sources with varying pair counts without a declared interpretation. Report positive-channel wrong-record incidence separately too; good specificity on negatives does not certify exclusive positive recovery.

For the proposed equal-creator, equal-source-within-creator target, weights are `w_cs = 1/(K n_c)`, where K is the number of included creator components and n_c the fixed number of included source groups in component c. Then `C_h = sum w_cs C_hcs` and `E_h = sum w_cs E_hcs`. These are finite-cohort summaries unless a justified sampling model extends them to a population. Creator weighting prevents prolific creators silently dominating; an alternative source-weighted or deployment-weighted target is legitimate only if selected before outcomes and labeled separately. The exact target population and weighting are still open scientific decisions. Ordinary-photo and temporal-negative populations are not pooled merely to enlarge N.

For the primary q contrast, define benefit `B_Q = E_ORVF - E_Full` and recovery loss `L_Q = C_ORVF - C_Full`. Both are nonnegative under fully observed nested sets. Define analogous B/L contrasts for readable-code availability and F. Report the paired change in X as well: C can remain high while outputs are ambiguous. The correct-record recovery loss and wrong-record benefit are evaluated on their respective declared positive/negative populations, not misrepresented as a single paired positive-negative observation. Within each population, differences are paired across arms at the source and creator levels.

The inferential target must be stated as one of: the fixed observed cohort/bank; future transformations of these fixed enrolled sources; or future source/creator and bank populations. Each requires different assumptions. Replicated seeds are repeated measurements, not independent creators. Query/reference reuse and a shared bank may couple otherwise distinct query groups. Conditioning on the bank does not automatically produce independent creator draws, especially when those creators supplied its records. A later protocol must choose a defensible design/interval method for that dependence—potentially independent bank/cohort blocks, or an explicitly narrower conditional target—before outcomes. Blindly bootstrapping pairs or applying binomial intervals to all comparisons is excluded.

A proposed interval analysis must retain paired arm differences and the highest supported dependency components, account for query/reference reuse, and state its finite-cluster/rare-event limitations. The existing V2 [Cameron–Miller card](02-literature/C8-theory/cards/cameron2015cluster.md) motivates this requirement; its regression formulas are not a ready-made zero-event bound. The [Brown–Cai–DasGupta card](02-literature/C8-theory/cards/brown2001binomial.md) supports binomial-model limits, not independent-pair assumptions. No interval algorithm, achieved precision, prospective power or adequate sample size is claimed here. If the dependence design cannot support the desired inference, retain descriptive paired summaries and mark the broad decision unresolved.

### Margins and multiplicity

The inherited proposal of a **5-percentage-point useful reduction** and **at most 5-point recovery loss** is provisional, not approved or justified by this document. Denote the future useful-risk margin by `delta_E>0` and allowable recovery loss by `delta_C>=0`; select them for the declared incidence/mean-recovery scales and use case before confirmation. The margins need separate justification; equal numbers do not imply equal scientific importance. If development baseline risk is below delta_E, the corresponding improvement requirement may be infeasible and must be reconsidered before test outcomes, never relaxed afterward.

The proposed primary claim requires **both** `B_Q >= delta_E` and `L_Q <= delta_C`, using a prospectively valid simultaneous or explicitly justified joint decision procedure. Recovery noninferiority is not established by a nonsignificant difference, by comparing point estimates alone, or by losing few observed positives after unavailable cases were discarded. Fix one-sided confidence conventions, boundary equality and missingness handling in advance. No margin is declared passed in this file.

Suggested hierarchy for later selection: first primary q benefit plus recovery, then prespecified read/F component questions, then task-compatible external comparison/replication. This is a proposal; exact families, alpha allocation or gatekeeping, channels, label definitions, bank sizes, fallback strata and success criteria must be frozen. If multiple models/cells support a joint claim, provide simultaneous coverage or another justified multiplicity procedure; if a claim is per cell, say so. Correlated cells do not excuse multiplicity. Exploratory stage diagnostics remain labeled exploratory, regardless of p values. Do not promote a favorable secondary contrast after the primary is unresolved.

## 7. Missingness and invalid-output hierarchy

Preserve separate statuses for administrative ineligibility before evaluation, marking failure, query unavailable/policy block, owner call absent or invalid, valid `found=false`, valid `read=false`, code malformed/missing, valid D1 abstention, descriptor absent/invalid, reference unavailable, label uncertain, and complete evaluable decision. No successful-output replacements. Administrative exclusions require an outcome-independent rule; all post-assignment operational failures remain accounted for.

Use three-valued scientific decisions: known accept, known reject, and unknown. A conjunction is known false if an observed required gate is false, even when an irrelevant later input is unavailable. It is known true only if all required gates are known true. Otherwise it is unknown. Thus `O=false` can logically reject that owner's full record decisions without inventing F values; F-only remains unknown when F is missing. Record unreachable stages as not evaluated, not failed. Owner-list/bank omissions must themselves be represented, not hidden outside the loop.

For a query, let `Mminus` contain known accepted records and `Mplus` contain known or possibly accepted records in the planned bank. Then the actual complete-data set lies between these sets. This yields purely logical bounds:

- C lower is membership of the intended record in Mminus; C upper is membership in Mplus.
- E lower is whether a wrong record is in Mminus; E upper is whether one is in Mplus.
- X lower requires known acceptance of the intended record and known rejection of every other record; X upper requires possible acceptance of the intended record and no known accepted other record.
- Certified abstention requires Mplus empty. An empty Mminus with nonempty Mplus is incomplete/unknown, not certified abstention.

Aggregate lower/upper outcomes through the fixed source and creator weights. For paired effects, take extrema over **jointly consistent completions** that preserve shared flags, common F values and arm nesting; do not independently assign incompatible best cases to different arms. Crude separate-arm bounds may be shown as conservative outer bounds, labeled as such. No missing-at-random assumption is made by default. Conditional complete-case analyses and stage-conditioned analyses are secondary diagnostics and disclose their selection mechanism; conditioning eligibility on successful O/R/Q cannot replace the all-attempt estimand.

Distinguish identification bounds from sampling intervals. A later inferential claim must address both, at the selected error level and hierarchy. If the conclusion changes across allowed missing outcomes, label it unresolved. A complete-bank claim additionally requires every scheduled required record/comparison to be accounted for under the prespecified rule; a favorable observed subset cannot restore that claim. A wrong-record event already observed remains an error even with other records missing.

## 8. Fixed conceptual mapping for external methods

This section defines comparison labels, not implementation work or permission to reopen baselines. Evidence is the inspected V2 [DREW card](02-literature/C6-provenance/cards/drew2024.md), especially v2 §3.3 Algorithms 1–2, and [SSCD card](02-literature/C5-fingerprints/cards/pizzi2022sscd.md), §§2–5.4. Those cards were read here; no new full-text access or literature search occurred. Existing verification levels are not upgraded.

| Method/task label | Enrollment and side information | Native output and fallback | Valid comparison |
|---|---|---|---|
| Local frozen full / controls | Published alpha marked image; passive beta derived enrollment where assigned; trusted q/D1/B1 records and public owner-specific native profiles. | All accepted records/owners; valid D1 fallback preserved. | Primary paired component identification on shared local outputs. |
| **Native DREW** | Native enrollment marks each registered item; stored embeddings, cluster assignments, watermark/ECC information and threshold. Fix the post-enrollment published image and queried channel. | Thresholded top-1 retrieval; native ECC-triggered whole-database retrieval fallback retained. | Native record retrieval/rejection under supported enrollment. Map returned record to owner only using the fixed registry relation. Its singleton output is not evidence of low set ambiguity. |
| **Adapted DREW candidate-set analysis** | Explicit proposed deviation from native DREW; exact routing, scores, threshold, bank access and fallback must later be specified and justified. | Any all-record/all-owner output is a study adaptation, not Algorithms 1–2 performance. | At most a separately labeled task-alignment analysis. If a faithful meaningful adaptation is unavailable, mark not applicable; do not silently alter the native arm. |
| **SSCD native descriptor/retrieval** | Public encoder and reference descriptors; any score-normalization background collection adds side information and must be declared. No watermark or native owner authentication. | Similarities/ranking; attribution decisions require a wrapper. | Descriptor/retrieval results, not owner authentication or a native all-owner decision. |
| **SSCD study attribution wrapper** | Same fixed logical record/owner/target mapping, declared stored image and bank; a disjoint development operating point. | Prespecify either top-1/reject or all-above-threshold set; label separately if both are retained. No implicit owner/q gate. | Common record recovery/error/rejection outcomes where the task is compatible; set ambiguity only for the set wrapper. |

Native DREW's marked beta enrollment cannot stand in for the local **passive unmarked-by-beta** E3 task. Do not suppress DREW's fallback to force pointer failure, or present a passive unsupported configuration as native DREW evidence. Conversely, changing local beta enrollment to re-marked would change the threat game; it belongs to the separately labeled active panel only after authorization. The shared endpoint labels do not erase different publication images, payloads, quality costs, training requirements, retrieval access or candidate semantics.

Native top-1 systems can be represented as singleton/empty output for common recovery and wrong-record metrics, but their absence of output ambiguity is structural, not equivalent evidence that alternatives were rejected. Report their ranking/tie/rejection policy and candidate uncertainty separately. A common top-1 projection of the local set method would also be a new analysis wrapper and must not overwrite its native all-accepted-set result.

Keep the local frozen threshold unchanged. External method thresholds, wrapper rules, ties and optional normalization must be fixed on disjoint development data with a declared quality/calibration objective before confirmation. If feasible operating points cannot be aligned, report the incompatibility or predeclared tradeoff panels; do not hand-pick a held-out threshold. Cross-method differences can reflect writers, descriptors and decision policies together. They support operational comparison, not causal attribution specifically to local q.

## 9. Falsifiable decisions and outstanding fields

**Support for a useful q increment** requires the predeclared joint interval/bounds criterion to clear the useful E reduction and recovery-loss limits on the Full-versus-ORVF comparison, with usable X/ambiguity/availability disclosed. Claim only the declared population, channel, bank and enrollment access. Broad empirical framing additionally needs the prospectively specified compatible external comparison or independent replication. A reduction confined to unread/invalid outputs supports a different mechanism, not q-distance discrimination.

**Refutation of the proposed useful increment** requires adequate evidence that the upper bound on B_Q is below the predeclared useful margin, or that the lower bound on L_Q exceeds the tolerated loss, under the chosen inferential/missingness convention. It refutes that utility claim at that operating point, not all uses of q. A precise no-useful-increment result is publishable evidence if scientifically relevant; a nonsignificant or imprecise result is not a precise negative. Do not continue calling extra q/content synergy established if O/R already explains the useful discrimination.

**Unresolved** applies when intervals/bounds span useful and non-useful tradeoffs, same-owner opportunities are absent, code/descriptor states are invalid, too few independent creator/bank units support inference, label ambiguity prevents target definition, complete-bank coverage fails, or external tasks cannot be aligned. Preserve the result and narrow the claim; no outcome-driven threshold, margin, bank or label repair. Descriptor specificity replication alone does not settle the full component question, and full-pipeline rejection alone does not show descriptor specificity.

Before any later study, the following must be fixed in one prospective protocol; this document invents no human decision:

| Unresolved field | Required pre-outcome specification |
|---|---|
| Authorization/scope | Whether any acquisition/experiment is authorized; explicit reopening of external baseline work; passive versus active claim boundary. |
| Population and identity | Creator/source populations, licensing/provenance coverage, correct-record relation, separate historical/new labels, blinded rubric and adjudication. |
| Bank and task | Owner count and records per owner, source/reference reuse, intended targets, distractors, enrollment/publication/query images, candidate visibility, ties, complete-bank policy. |
| Data assignment | Untouched sources, conservative dependency graph, development/confirmation separation, deterministic membership and scheduled opportunities, administrative exclusions. |
| Method compatibility | Frozen local versions; DREW native versus adapted feasibility; SSCD wrapper and normalization; stored image and quality/calibration conventions. |
| Estimands and margins | Primary risk and recovery populations, source/creator weights, fixed opportunity count, delta_E/delta_C and practical justification, X/ambiguity reporting. |
| Inference and precision | Finite-cohort versus population target, source/bank dependence design, paired interval procedure, multiplicity families/hierarchy, missing-outcome bounds, a justified precision target and feasibility check. |
| Integrity and stopping | Invalid-state semantics, no output-dependent replacements, label/overlap breach policy, analysis freeze, predeclared support/refute/unresolved boundaries and stop rule. |

The inherited acquisition ambitions in F1/F2 are not evidence that these precision requirements can be met. No sample-size calculation or simulated prospective power is supplied. The central next scientific decision is **which conditional or population-level recovery/risk tradeoff, for which fixed bank and creator/source distribution, is important enough to test**. Only then can feasible margins, dependency handling and precision be justified.

## 10. Read-only provenance for this contract

Read MAIN `thesis-runs/d916749c/STATE.md` once; dossier BRIEF, F1/F2, the theory/security note, EV-77 owner-gate audit, fresh-data plan, the four linked V2 cards, and the named analysis source functions as text. The `thesis-experiment-design` skill supplied principles for falsifiability, outcomes, units, leakage and negative-result policy only. BRIEF and the parent's bounded assignment override its execution helper/contracts/output instructions. No web query was made, so no search-log entry is required. No numeric evidence was recomputed, no retained output changed, and no approval or human verdict was fabricated.
