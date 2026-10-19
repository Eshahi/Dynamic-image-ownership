# Next-study statistical design: decisions completed

19 October 2026, user-authorized research-only follow-up R10. **No study, simulation, acquisition, calibration or experiment was performed.** Scientific choices below are made by the researcher as the user requested; they are not attributed to a supervisor or represented as approval to execute. The original ten-hour deadline is unchanged.

The next study asks whether the frozen record-code matching condition adds useful same-owner record discrimination to the existing registry verifier. Compare Full with ORVF on identical outputs; only Q is deleted. This is one local component study, not the entire F1/F2 publication campaign. [Full statistical specification](design-core.md) is authoritative for this selected study and supersedes the still-provisional population, margins, sampling and precision fields in document 23. Broader external comparisons, independent-encoder studies and active attacks remain separate.

| Decision | Selected value and reason |
|---|---|
| Target | Equal-weight finite frozen frame of eligible Commons real-camera creator/production components. This supports design-based inference to that frame, not all online photographs. |
| Primary sampling unit | One disjoint creator/production component with its own eight-record bank; no shared sources or references across blocks. Three seeds are repeated observations within a block. |
| Sample | 1,200 blocks, uniform sampling without replacement after frame/labels/roles are frozen. Require N>=1,200; no output-dependent replacements or adaptive enlargement. |
| Bank | Two fixed public test-owner profiles, four records each, from four distinct capture groups. A1 is the original target; B1 is a same-owner distinct capture 0.5–1.0 seconds later. |
| Schedule | SD1.5 and SD2.1-base, strength .2, DDIM20, empty prompt, guidance 1, seeds 15/16/17; preserve their existing safety-checker configurations. Both checkpoints must satisfy the criterion. |
| Benefit H | ORVF has a same-owner wrong-record episode over the three seeds and Full has no wrong-record acceptance over them. Require frame proportion at least .05. This also lower-bounds reductions in any-wrong and same-owner-wrong incidence. |
| Loss L | At least one seed loses intended-record recovery solely through Q. Require frame proportion at most .02; this is stricter than a two-point mean per-seed loss budget. |
| Absolute recovery G | Full delivers intended-original inclusion on at least two of three seeds. Require frame proportion at least .85. This prevents universal abstention from satisfying the utility claim. |
| Inference | Exact hypergeometric-tail inversion using actual future N. Twelve directional bounds, each tail .05/12, give simultaneous coverage of at least 95% without checkpoint independence. |
| Planning adequacy | At least 95% joint assurance targeted within the explicit strong alternative H>=.10, L<=.002, G>=.95 in both checkpoints, fully observed. The analytic conservative bound is 96.84%; it is not measured power or a forecast. |
| Missingness | All attempts stay. Use joint logical completion bounds for H/L, count failed delivery as a G miss, and report underlying recovery bounds separately. Unknown errors are never imputed as observed rejections. |
| Bank claim | Primary support is robust to all compatible completions of the planned eight-record bank. Fully observed bank certification is a separate flag. Historical strict E3 remains failed and unchanged. |
| Decision | Support requires all three simultaneous inequalities in both checkpoints. Refute only with a strict contrary simultaneous bound on at least one condition. Otherwise unresolved. No interim efficacy/futility or success-driven sample change. |

The 5%/2%/85% utility specification is a documented researcher judgment for this thesis question, not a validated deployment requirement. The size calculation is deliberately conditional: a weaker real effect, more missingness or a higher loss rate can leave the study unresolved. The [analytic justification and sensitivity table](analytic-justification.md) make that dependence explicit.

**Feasibility is not established.** The design needs 9,600 enrolled references and 7,200 primary regeneration slots, plus 2,400 clean/unmarked diagnostic queries, before any additional routine writer-internal computations. These are design counts, not completed work or runtime estimates. The previous F1/F2 300-photo/100-group acquisition targets and 48–120-hour campaign allowance do not budget this larger selected design. No new cost estimate is asserted. Rights, provenance, the frozen frame's actual size, real blinded labelers and exact available implementation identities must be supplied in later authorized work. If the frame is too small, this design is infeasible; a new pre-outcome plan is required instead of pretending more pairs create more sampling units.

The study can establish a narrow useful or non-useful component result. It cannot establish cryptographic/legal ownership, novelty, large-registry error control, independent-encoder transfer, active-adversary resistance or Q1 readiness. Exact canonical duplicates between distinct captures remain visible; the identity task must not be described as universally perceptual difference.

Files: [statistical specification](design-core.md), [analytic justification](analytic-justification.md), [formula inputs/results](analytic-planning-values.json), [implementation inheritance](implementation-inheritance.md), and [primary-source access log](search-log.md). There is no runnable script, new run manifest, selected asset list or generated outcome in this folder.
