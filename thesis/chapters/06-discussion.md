# Chapter 6. Discussion, limitations and conclusions

Status: **draft for human review**, 2026-10-07. This chapter interprets the reviewed M2 evidence. Future experiments are recommendations, not authorized held-out execution, accepted hypotheses, or completed work.

## 6.1 Answers to the four research questions

<!-- claim=M2-D-001; kind=interpretation; evidence=EV-REVIEW,EV-ENDPOINTS; status=partial; proposal=RQ-02,HYP-02 -->
The principal measured result is stronger semantic-tier survival for the complete frozen F5 r2 system than for v5 r3 under the declared SD1.5 regeneration protocol. At strengths .20 and .40, F5 succeeds on 30 and 21 of 30 sources, while v5 succeeds on 22 and 5. The checked-only comparison retains an advantage of 27 versus 10 and 17 versus 3. This provides a useful, bounded result about the implemented systems. It leaves the original carrier-location hypothesis unresolved because the systems also differ in semantic pooling, matching and embedding. **TODO:EVIDENCE — isolated carrier-location causality remains untested.**
<!-- /claim -->

Table 6.1. Question-level conclusions from this evidence set. “Partial” describes the original question, rather than uncertainty about whether a reported count was reproduced.

| Question | Current conclusion | Evidence boundary |
|---|---|---|
| RQ1: combined signature | Untested as a controlled comparison | No semantic-only ablation; cross-owner T5 results retain owner conditioning |
| RQ2: embedding location and regeneration | Partially supported | Whole-system gain on one pinned regenerator; several components changed |
| RQ3: competitive, faster DCT detection | Untested | No matched neural-decoder/inversion benchmark; full detector includes VAE and CLIP |
| RQ4: original versus copied watermark | Partially supported | No false full attribution in the fixed T4 test; low donor delivery prevents a binding-mechanism conclusion |

<!-- claim=M2-D-002; kind=limitation; evidence=EV-REVIEW,EV-CLAIM-LEDGER; status=verified; proposal=RQ-01,HYP-01,RQ-03,HYP-03 -->
RQ1 and RQ3 cannot be answered by implementation alone. A combined signature exists in the system, but its incremental discrimination benefit was not measured against semantic-only and perceptual-only alternatives. Likewise, DCT extraction without diffusion inversion does not establish a computational advantage over a neural decoder. These questions need their own controlled comparisons and predetermined performance margins. **TODO:EVIDENCE — the required ablations and efficiency benchmarks are absent.**
<!-- /claim -->

<!-- claim=M2-D-003; kind=interpretation; evidence=EV-REVIEW,EV-ENDPOINTS; status=partial; proposal=RQ-04,HYP-04,PROB-03 -->
RQ4 has a favourable rejection count but incomplete mechanistic evidence. The test yields no false full donor attribution in 29 different-owner pairs, yet only four F5 pairs show donor delivery and no F5 donor query reports `content_mismatch`. Rejection without a delivered signal is compatible with mark destruction. T5 likewise has no false match in 27 different-owner pairs, but owner conditioning can account for rejection without demonstrating the extra value of content binding. These results support the measured thresholded behaviour while leaving comparative binding efficacy open. **TODO:EVIDENCE — binding-disabled and signature-only comparisons with adequate delivery are missing.**
<!-- /claim -->

## 6.2 What the surviving evidence means

<!-- claim=M2-D-004; kind=interpretation; evidence=EV-ENDPOINTS,EV-REVIEW,EV-PACKAGE; status=verified; proposal=METHOD-09,RQ-02 -->
Semantic-tier survival and original-instance authentication are different endpoints. No T3 correct-owner query retains `both_match`, including the VAE cycle. Reporting 30/30 semantic successes at strength .20 as 30 authenticated originals would erase this distinction. The fragile tier's loss is consistent with its intended response to regeneration, but a `semantic_only` state is evidence under a specific detector rule, not proof of the processing history or attack cause. The thesis should report the tier and event rule alongside every robustness number.
<!-- /claim -->

<!-- claim=M2-D-005; kind=interpretation; evidence=EV-ENDPOINTS,EV-REVIEW; status=verified; proposal=RQ-02,METHOD-09 -->
Checked-only reporting is especially informative for this comparison. At strength .20, 8 of F5's 87 semantic-positive rows and 32 of v5's 62 are recomputed-only responses. A response based on the current content-conditioned pattern does not itself recover the embedded semantic code. The checked-only advantage shows that the reported F5 gain is not solely an artefact of that fallback rule, while the total-versus-checked distinction remains necessary for both systems.
<!-- /claim -->

<!-- claim=M2-D-006; kind=limitation; evidence=EV-SPEC,EV-PACKAGE,EV-REVIEW; status=verified; proposal=METHOD-06,METHOD-08,NOVELTY-01 -->
The implemented F5 carrier is a VAE-encoder-assisted pixel perturbation, with DCT reading in the encoder latent. The original proposal instead describes a diffusion latent/noise route and image-domain 8 × 8 DCT extraction. The implemented route must be stated explicitly in the method chapter. Extraction without inverse diffusion and the presence of a binding computation are supported implementation properties; neither establishes comparative binding efficacy or novelty. The present results do not justify substituting this implementation silently for every original method commitment.
<!-- /claim -->

## 6.3 Quality and computational trade-offs

<!-- claim=M2-D-007; kind=interpretation; evidence=EV-ENDPOINTS,EV-REVIEW,EV-SPEC; status=verified; proposal=METRIC-01,METRIC-02,METRIC-03 -->
Higher F5 mean PSNR, 44.49 versus 37.53 dB, coexists with a slightly higher mean LPIPS, .02176 versus .02073, and two LPIPS threshold failures. These observations measure different aspects of the perturbation; the favourable PSNR does not negate the LPIPS shortfall. F5 attains all three proposal quality thresholds on 298/300 sources, and the stricter development LPIPS limits fail to transfer to held-out data. This is a measured generalization limit of the frozen configuration. The two images remain in all relevant denominators.
<!-- /claim -->

<!-- claim=M2-D-008; kind=limitation; evidence=EV-REVIEW,EV-ENDPOINTS,EV-SPEC; status=verified; proposal=METRIC-03 -->
Human acceptance of the earlier development visual comparison cannot stand in for missing held-out visual and semantic verdicts. PSNR, SSIM and LPIPS counts provide quantitative evidence, while this run supplies no human assessment of whether the marked images preserve acceptable appearance and meaning. The chapter consequently leaves that assessment unresolved rather than inferring a verdict from automated metrics. **TODO:EVIDENCE — no held-out human verdict has been supplied.**
<!-- /claim -->

<!-- claim=M2-D-009; kind=interpretation; evidence=EV-ENDPOINTS,EV-REVIEW,EV-SPEC; status=verified; proposal=RQ-03,METRIC-07 -->
F5's mean embedding time is approximately ten times v5's in the retained run. Its detector also requires the VAE encoder and seven CLIP views. This resource footprint qualifies any description of the method as lightweight. A fair efficiency claim would measure full verification, including feature computation, model loading policy and candidate handling, under matched hardware and a prespecified accuracy margin. The current embedding observations cannot answer that comparison.
<!-- /claim -->

## 6.4 Statistical and experimental validity

<!-- claim=M2-D-010; kind=limitation; evidence=EV-ENDPOINTS,EV-PACKAGE,EV-REVIEW; status=verified; proposal=METRIC-05,METRIC-06 -->
The threat experiments are descriptive. Thirty T3 sources, 29 different-owner T4 pairs and 27 different-owner T5 pairs provide substantially less precision than the 300-source clean cells. Zero observed errors correspond to upper bounds of approximately 9.5%, 9.8% and 10.5%, respectively. They do not establish an error rate below 1%. Three seeds, two patch sizes and repeated queries increase observations within a unit, not the number of independent source or pair units. The 900 clean negative calls per method also reuse 300 sources across three cells; their per-cell bounds must not be replaced by a pooled independent-call bound.
<!-- /claim -->

<!-- claim=M2-D-011; kind=limitation; evidence=EV-PACKAGE,EV-ENDPOINTS,EV-REVIEW; status=verified; proposal=RQ-02,HYP-02 -->
The retained analysis includes unadjusted paired sign tests, but no frozen multiplicity correction or powered causal component comparison. Small p-values at the stronger doses accompany useful whole-system effect counts; they do not remove architectural confounding or extend the claim to other regenerators. The manuscript uses the original source aggregation and thresholds. It adds no post hoc bootstrap, adjusted test or acceptance threshold, and makes no claim that a secondary analysis has been completed.
<!-- /claim -->

<!-- claim=M2-D-012; kind=limitation; evidence=EV-PACKAGE,EV-REVIEW,EV-CLAIM-LEDGER; status=verified; proposal=DATA-01,DATA-02,DATA-03,SCOPE-02 -->
External validity is limited to the narrowed held-out COCO512 cohort and the declared T3/T4/T5 constructions. Only the pinned SD1.5 VAE cycle and DDIM img2img settings were evaluated. Other diffusion checkpoints, prompts and editing pipelines remain untested. DIV2K, DiffusionDB and existing generated-image inputs were not evaluated, so the run cannot establish the proposal's camera-originated and generated-image generalization claim. The metadata-defined held-out selection and unchanged thresholds protect this comparison from deliberate outcome-based selection; they do not make it representative of every image domain.
<!-- /claim -->

<!-- claim=M2-D-013; kind=limitation; evidence=EV-REPORT,EV-REVIEW,EV-VERIFICATION; status=verified; proposal=DATA-01 -->
The evidence is one recorded realization spanning a laptop and a rented server. Fourteen sources were embedded on the laptop and 286 on the server, with F5 GPU embedding known to be non-bit-reproducible. Independent inspection verifies unchanged scientific core, preserved journal prefix, retained parent images and complete endpoints. Historical termination cause and complete standing-policy compliance are more limited: the finalized parent stop record is missing, and the user exception, review waiver, approval-expiry change and rented-resource accounting must remain explicit. These custody limits qualify provenance claims without changing the reproduced scientific counts.
<!-- /claim -->

## 6.5 Owner attribution and security boundary

<!-- claim=M2-D-014; kind=limitation; evidence=EV-SPEC,EV-PACKAGE,EV-REVIEW,EV-CLAIM-LEDGER; status=verified; proposal=SCOPE-01,SCOPE-03 -->
The experiment evaluates a technical detector conditioned on a supplied public OwnerID. Its keys are public-derived, and a query concerns a specified owner rather than a search over an entire owner roster. The run does not establish cryptographic unforgeability, authenticated legal ownership, authorization to transfer ownership, revocation, or an owner-history protocol. The dynamic-ownership title and proposal remain preserved; the results must not imply that those narrative commitments have been implemented or validated.
<!-- /claim -->

<!-- claim=M2-D-015; kind=limitation; evidence=EV-REVIEW,EV-PACKAGE; status=verified; proposal=DATA-01 -->
COCO test-image rights remain pending for release beyond local research use. The writing package contains derived aggregate tables, a plot and traceable claims, rather than raw test images or private approval records. Scientific reproducibility and public redistribution are separate obligations; no publication or institutional acceptance is created by this draft.
<!-- /claim -->

## 6.6 Remaining work, ordered by unresolved evidence

<!-- claim=M2-D-016; kind=future-work; evidence=EV-REVIEW,EV-CLAIM-LEDGER; status=partial; proposal=RQ-02,HYP-02 -->
A controlled component study would address the causal form of RQ2: hold semantic views, matching rules, quality budget, candidate handling and the regenerator fixed while varying the carrier route. Source-level pairing and declared survival tiers should be retained. Any such study needs a separately specified design and fresh evaluation data; tuning or selecting a revised method using these confirmatory outcomes would turn a follow-up into exploratory work. **TODO:EVIDENCE — this study is proposed, not executed.**
<!-- /claim -->

<!-- claim=M2-D-017; kind=future-work; evidence=EV-REVIEW,EV-CLAIM-LEDGER; status=partial; proposal=RQ-01,HYP-01,RQ-04,HYP-04,PROB-03 -->
A T4/T5 mechanism study would compare combined, semantic-only, perceptual-only and binding-disabled designs under the same owner conditioning. It should separately measure delivery of a detectable donor signal, content mismatch and false full attribution; otherwise destruction of the mark can mask a failed binding mechanism. The present F5 delivery count of 4/30 is a reason to resolve delivery before making a stronger binding claim. **TODO:EVIDENCE — these comparisons and their success criteria remain to be specified and tested.**
<!-- /claim -->

<!-- claim=M2-D-018; kind=future-work; evidence=EV-REVIEW,EV-CLAIM-LEDGER; status=partial; proposal=RQ-03,HYP-03,METRIC-07 -->
A full-verification benchmark would address RQ3 using an inspected neural-decoder comparator and the separate inversion-comparison obligation, with common hardware, input knowledge, timing boundaries and a predetermined accuracy margin. Human quality assessment and broader domain validation remain distinct obligations. These additions would extend the evidence; they are not prerequisites for reporting the current negative and partial conclusions honestly. **TODO:EVIDENCE — no benchmark or new confirmatory run is represented as completed here.**
<!-- /claim -->

## 6.7 Bounded conclusion

<!-- claim=M2-D-019; kind=interpretation; evidence=EV-REVIEW,EV-ENDPOINTS; status=partial; proposal=GOAL-01,RQ-01,RQ-02,RQ-03,RQ-04 -->
This study supplies a reproducible comparison of two frozen systems on a narrow COCO512 cohort. F5 improves semantic survival under the specified SD1.5 regeneration, attains clean full-tier detection on 299/300 sources, and produces no observed false full attribution in the declared copy-paste and collision tests. Its universal LPIPS target is not met, donor-delivery evidence is weaker than v5's, and the experiment does not settle signature ablations, lightweight-decoder efficiency, carrier-location causality, binding efficacy or dynamic ownership. The defensible contribution is the measured system behaviour and its limits. **TODO:EVIDENCE — the unresolved proposal hypotheses remain open; human M2 and chapter acceptance are pending.**
<!-- /claim -->
