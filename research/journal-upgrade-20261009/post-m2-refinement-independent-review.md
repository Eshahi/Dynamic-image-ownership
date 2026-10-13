# Independent review of the bounded post-M2 refinement study

2026-10-13, completed about 13:12 UTC, before the unchanged 13:32 UTC deadline. Reviewer: fresh independent Codex subagent, separate from the package author. **Verdict: PASS for the reported exploratory evidence and no-advancement decision. No material blockers.** This is a technical review, not human M2 acceptance, visual admissibility, or an official lifecycle verdict.

## Scope and independent work

Reviewed the post-M2 changes since the reviewed M2 package `e2ecbe3`: prospective protocol and narrow amendment, census, probe at execution commit `73f8f15`, analysis, post hoc decoder diagnostic at `ade2df7`, result report, compact evidence and revised roadmap. The inference code was not changed during review. Authoritative MAIN state was read once. No models, image generation, held-out inference, protected files or retained outputs were modified.

I recomputed A/S/Q/J/H/F directly from every saved raw semantic/instance call, rather than calling either production endpoint or study-analysis functions. I independently reconstructed the scheduled identity set, source-majority lower/upper bounds, negative source clusters, clean qualification, raw systematic-message equality and encoded-word error counts using standard-library arithmetic. All saved endpoints and material report counts agree. Reported quality summaries were checked against recorded per-image metrics, without rerunning floating-point models.

## Findings

- Inventory is exactly 252 unique prescribed identities: 248 available and four safety-blocked C0 images. There are 192 actual attacks and 28 explicit I/E row aliases. Aliases have identical statuses, raw calls, endpoints and quality records. There are 496 logical observed owner calls, including reused calls; this is not 496 independent observations. The source remains the sampling unit.
- Census has four identical and eight changed I/E pairs. Seven changed sources have accepted minimax updates; source 147498 has zero accepted updates and changes only between saved state and selected final. No alternate source or target was substituted.
- Independently recomputed J majority is 12/12 in both arms at both strengths; paired majority differences and missingness intervals are [0,0]. Seed J is 36/36 in both arms at .1 and 34/36 versus 35/36 at .2. The sole J discordance is source 147498, .2, seed 6. Both calls recover exact q with semantic read; their content-match predicate differs. Thus the observed endpoint change is associated with the contraction-only selection, not accepted minimax updates or correction of a lost message.
- Exact Q is 36/36 per arm and strength. Regenerated H/F have zero seed and majority successes. Clean Q/H/F is 12/12 for both arms; strict quality is 11/12 versus 12/12, with initializer 147498 alone failing LPIPS. The joint clean-eligible majority endpoint consequently changes 11/12 to 12/12 while raw majority remains unchanged. The report correctly separates these quantities and does not replace the cohort with the common eligible subset.
- All observed negative A events are zero. Each C0 owner/strength family has 34 observed calls and two unavailable calls, both from source 6012; its fixed-cohort source bracket is [0,1/12]. Wrong-owner marked families are complete. Unavailable calls are not counted as negative evidence, and there is no population-FPR claim.
- Independent polynomial encoding confirms zero raw coded errors in all .1 positive calls and one single-bit error among 36 calls per arm at .2. Raw systematic q and decoded q are exact in all positive calls, so the post hoc diagnostic's zero message rescues/harms is correct. This diagnostic does not identify equal-rate coding gain or explain E3 versus native v5.
- The prospective useful-screen rule correctly fails: no two-source .2 majority gain and no strictly positive adverse-bound majority gain. Complete execution and a one-seed improvement do not override those failures. The resulting decision is `no_decisive_added_value`, not a new M1/M2 verdict.

Compact analysis and census match the authoritative outputs. Compact decoder evidence intentionally omits per-observation records, and compact run metadata omits its embedded summary and adds provenance labels; shared retained fields agree. Full raw evidence paths remain disclosed.

## Qualifications and recommendation

The report appropriately retains adaptive source selection, matched nominal thresholds rather than calibrated FPR, unequal achieved distortion, missing human judgments and the regenerated instance-tier failure. Its statement about quality selection is limited to the observed binary endpoints on these inputs; it must not become a general claim that minimax is useless or that the 300-source M2 difference is causally explained.

The probe's field named `inclusive_duration_seconds` begins at the successful census, omitting earlier failures and diagnosis. The report explicitly corrects that interpretation and retains the original conservative 12:47–13:32 UTC study clock. This naming issue does not invalidate the completed bounded run. The two failed census attempts and their pre-inference amendment remain disclosed.

The post hoc decoder appendix is scientifically useful in its stated conditional role. Retain its separate unthresholded raw equality, decoded equality, threshold-qualified Q and checked J distinctions. A fresh-development full-pipeline versus initializer-plus-fixed-selector comparison, followed by controlled initialization/carrier comparisons, is a reasonable prospective next question. This review does not authorize or certify a future experiment, method freeze, held-out rerun or external superiority claim.
