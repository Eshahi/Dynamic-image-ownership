# Independent M2 evidence review

**Verdict: ACCEPT WITH CORRECTIONS.** The retained run supports the measured, narrowly scoped comparison of frozen F5 r2 with v5 r3. No inspected evidence requires discarding or rerunning its scientific results. The report needs the corrections below before it is represented as independently reviewed M2 evidence. This verdict does not accept all proposal hypotheses, grant human acceptance, authorize new experiments, or advance an official lifecycle gate.

Reviewer: Codex independent reviewer `/root/m2_independent_review`, separate from Claude Code, the package and report author. Date: 2026-10-07. Reviewed snapshot: `2a31ed153c4e95e2382bf3c6e9f66304412aa980`, branch `codex/m2-review`. This review covers the result report, frozen protocol and implementation relevant to its claims, and continuation `e26bd4bd92d5cbf2eb7bd1aa5273bee1bd5a2b22`. It changes only this file.

Reviewer model: `gpt-6-astra`, reasoning effort `xhigh`, fresh context. The primary Codex agent separately recomputed the endpoints and verified input hashes. This document is the additive correction record for the unchanged author report: cite the two together. C1-C5 below provide the corrected interpretation; the original report has not been silently repaired, and human M2 acceptance remains pending.

## Evidence and verification

Artifact abbreviations below refer to MAIN `.thesis-build/m1b-confirm/artifacts/M1b-test/`: **R** is `coco512-confirm-rerun-1`, **P** is `coco512-confirm-1`. **E** is `R/metrics/endpoints.json`; **J** is `R/outputs/journal.jsonl`. Report line numbers refer to the reviewed snapshot, before corrections.

I inspected the frozen spec, config, package, both plans, detector and worker/analysis code; the protected claim inventory, contract and scope boundaries; both approval files; parent and continuation manifests, journals, contexts and lineage; and retained remote preparation/dispatcher logs. I independently parsed J, recounted distinct calls and final states, checked the plan differences and parent journal prefix, recomputed the scientific core, and compared every retained parent image file with its continuation copy. I also inspected the parent agent's independent full endpoint recomputation and inventory in MAIN `.thesis-build/m2-review/verification.json` and `endpoints-recomputed.json`. These mechanical checks support traceability and counts, not claim entailment.

The decisive checks are:

- J contains **7,741 unique completed rows**, with no duplicates. The planned inventory and independent recomputation report no missing or extra rows. Every endpoint count/structure matches E; 192 floating-point bound values differ by at most `2.220446049250313e-16` in the Windows recomputation.
- Scientific core is exactly `be2aa5717f47eb66725c8e0de1a10f3e7f258e079531b4e50e0bed5a1284d419`, including 24 code files. Recomputed core equals P's retained `outputs/run-context.json`. R's `run.json` records this core, commit `e26bd4b...`, and plan SHA-256 `3ecfbc307046b87b90eea6c22463bf802b4f901bd5da6eddeaa495579d6d7d68`.
- Plans differ only at `label`, `resume_from`, `resume_parent_approval_sha256`, and `approval_path`. The continuation has depth 1 and names parent approval `d0d1f12c9bd82332ca57dd49a3616427c501cc3ab8d82ee951a30e76f0140f9d`.
- The first 155 continuation lines exactly equal P's journal, SHA-256 `54f6c41a701adcc3f2b36e475fae06bdd1c5a4802081c9f9a1a6f0ecd4f7d50f`. They comprise 15 canonical sources, 28 embeddings, and 112 clean queries: **14 sources fully embedded/tested, plus the next source canonicalized**. All **43/43 parent PNG files are byte-identical** in R. Worker `_unit` skips journaled identities (lines 628-631), `adopt_parent` preserves journal/images (911-935), and saved RGB hashes are checked on load (621-625). There is no evidence of replacing completed embeddings or selecting a favorable rerun.
- R reports `status=finished`, `infrastructure_error=null`, zero dropped torn lines, and 9,625.269 seconds. The continuation dispatcher reports `completed`, exit 0, clean checkout, and no errors. These facts apply to R; they do not establish the parent's termination cause.
- The parent agent's input audit reports 300 unique source groups, all 300 approved raw-file hashes matching, canonical receipts matching those raw hashes, and all four report artifact hashes matching. No fresh visual verdict was performed. The worker checks approval before preflight and image work (`main`, lines 953-975), and fixes thresholds, seeds and schedules before outcomes. T5 selection uses declared category/pHash rules, not detector success (`run_t5`, 768-794).

## Required corrections

### C1 — Correct the clean-negative denominator

Report line 126 attributes **1,800 negative queries** to F5 r2. F5 has **900 distinct clean negative detector calls**: C0 correct, C0 wrong, and C1 wrong, each on 300 sources. Applying `any_found` and `both_match` to the same calls creates six endpoint summaries, not 1,800 calls. There are 1,800 such calls **across both methods**.

Replace the statement with: “F5 r2 has zero detections in 900 clean negative queries, comprising three cells of 300; v5 r3 also has zero in its 900 queries. The secondary both-match rule reuses those calls.” Preserve the per-cell bound and dependence caveats. Evidence: analysis lines 134-137; J clean rows; `verification.json/independent_recount/*/negative_queries`. This correction does not change a rate or confidence bound.

### C2 — Separate numerical lineage validity from unverified historical and policy assertions

The scientific continuation is valid on the evidence above. An unconditional statement that every standing-policy condition was independently satisfied is unsupported:

1. **P has no `outputs/run.json`.** Its `outputs/contract.json` declares that file, but it was never finalized. Its dispatcher manifest remains `running`, with null end/exit fields and `errors=[]`. The rerun-check item `4_failure_record` points to a nonexistent file. The plan label and approval `source_ref` attribute the stop to the user's move request. These records are consistent with a manual interruption and show no retained scientific-validation failure; they cannot independently prove “no crash.” Change report line 170 and equivalent summaries to state this evidence boundary. Do not create or repair a parent failure record.
2. Policy lines 64-73 require unchanged expiry and a delegated actor/review receipt for the standing rerun route. Parent approval expires `2026-10-13T22:17:11Z`; continuation approval expires `2026-10-14T09:21:20Z`, uses actor `Soroush`, and transcribes a separate user-directed move. The run ended well before the **original** expiry, so the extension did not enable any observed computation. Nevertheless, `6_same_budget_and_unexpired_approval=true` is not proof of unchanged approval expiry or complete policy compliance. The independent review also occurs after execution.
3. The approval and dispatcher retain `execution_target=local` and `max_usd=0` while the report correctly describes execution on a rented server. Those fields describe the dispatcher route/budget check, not proof that actual remote expenditure was zero. The recorded user exception and pre-run review waiver must remain explicit. The original approval expressly permits journal reuse, whereas the older blanket policy says prior evidence is not reused; cite the specific continuation authorization rather than claiming literal compliance with every older clause.

Describe this as a **scientifically unchanged continuation under the recorded direct user exception, with retrospective independent review and a missing finalized parent stop record**. The reviewer has not authenticated the original chat/stop command or paid-resource decision beyond the transcribed references. This is a provenance limitation, not evidence that the measured outputs are false. This review confirms rerun-check items 1-3 and numerical continuation integrity; item 4 is supported only to the bounded extent above. It supplies the independent review required by item 5 retrospectively, not a fabricated pre-run receipt.

### C3 — Make the held-out quality shortfall explicit

“All primary clean endpoints pass” is correct for the frozen **detection** endpoints. It must not become “all quality requirements” or an unqualified overall method pass. F5 quality is PSNR/SSIM 300/300 but joint quality and LPIPS **298/300**. Failing source IDs are `553094` (LPIPS `0.10222657024860382`) and `134886` (`0.10419527441263199`). Mean LPIPS is `0.021758933338181425`; mean PSNR is `44.488476251352665`.

The development freeze bar in `research/f5-r2-spec.md` section 1 and `configs/f5-r2.json/quality_gate` lists LPIPS mean <= .0173 and max <= .050. Neither carries over to held-out results. The approved package section 3 declares confirmatory quality **counts** against proposal targets, not an all-sample quality acceptance gate. Add that explicit distinction and the fact that universal LPIPS < .1 was not achieved. Do not retrospectively alter thresholds or exclude either image. The report already gives the correct table; the correction resolves interpretation, rather than changing its numbers.

### C4 — Limit RQ-02/HYP-02 to a whole-system comparison

Report sections 3.2 and 4 correctly disclose a VAE-encoder-assisted pixel modification and the initial-noise deviation. Add that this experiment does **not isolate moving the carrier to the latent**: F5 simultaneously uses seven-view CLIP, soft semantic matching, different carrier/embedding machinery, and different perturbation strength; v5 uses a single CLIP view and its original matching/embedding. Evidence: package lines 15-20; worker lines 490-503, 520-535; F5 `detect_rgb` lines 268-299.

Classify the original causal latent-versus-pixel hypothesis as **partially supported**, with descriptive evidence for the frozen F5-versus-v5 systems on one pinned SD1.5 regenerator. Do not imply that the mark-location change alone is proven responsible. Both systems modify pixels; F5 targets and reads the encoder latent. This remains a useful result even with the METHOD-06 and METHOD-08 deviations.

### C5 — Distinguish no false attribution from demonstrated binding efficacy

T4 reports **0/29 false donor full attributions**, but F5 reveals a donor mark in only **4/30 pairs** and produces **zero `content_mismatch` states** in the 60 marked donor claims (56 neither, 3 semantic-only, 1 uncertain). Most rejection can therefore result from lost/undelivered signal; these observations do not establish HYP-04's particular mechanism of exposing a copied watermark by a content mismatch. v5 delivery is 8/30. Preserve this negative comparison.

T5's **0/27** is valid for the declared different-owner pair test; pairs 9, 20, 29 were excluded as planned. Public owner conditioning can explain rejection without establishing that semantic/perceptual binding reduces collision relative to a semantic-only design. No such ablation exists. Add these limitations to sections 3.3/4. Describe OBJ-04/RQ-04/HYP-04 as partially supported by the measured rejection endpoint; HYP-01 and general binding improvement remain untested. In NOVELTY-01 replace unqualified “binding ... hold” with “the binding computation is implemented; comparative binding efficacy and novelty are not established.” No new experiment is required to preserve the present evidence.

## Numerical and claim assessment

| Item | Classification and supported interpretation |
|---|---|
| Clean detection | **Verified:** F5 299/300 both-match; v5 300/300. Both meet frozen lower-bound target .80. Each of three negative cells is 0/300 per method; the upper bound is approximately .009936. Secondary rules reuse observations. |
| T3 measured comparison | **Verified:** source-majority F5/v5 at .1: 30/29, .2: 30/22, .4: 21/5; checked-only .1: 30/24, .2: 27/10, .4: 17/3. Report row counts and sign tests agree with E and the independent recomputation. VAE/.05 successes are 30/30 sources for both. Both-match is zero on all T3 correct-owner rows, including VAE. |
| T3 original hypothesis | **Partially supported:** stronger semantic-tier survival for the complete F5 system on the declared SD1.5 doses, not general regeneration robustness, full instance authentication, or an isolated latent-location effect. Descriptive, unadjusted tests and 30 source units remain explicit. |
| T4/T5 | **Verified** thresholded counts; **partially supported** mechanism and broader robustness claims, for C5's reasons. Bounds approximately .098/.105 cannot establish error below 1%. |
| Strict quality on every source | **Conflicting** with universal LPIPS attainment: two failures. Reported separate/joint counts are **verified**. Development mean/max LPIPS limits were not retained on held-out data. |
| METHOD-09 | **Partially supported:** implemented decision table is exercised; it is not a validated classifier of attack cause. F5 T3 states 357 semantic-only, 21 uncertain, 11 neither, 1 mismatch are verified; v5 283, 13, 91, 3. An output label alone does not prove an image was regenerated or forged. |
| Lightweight extraction, RQ-03/HYP-03, SEAL comparison | **Unsupported by this run**, correctly marked untested. Detection uses a GPU VAE encoder and seven CLIP views plus DCT, without diffusion inversion. Logged timings do not establish superiority to a neural decoder or SEAL. |
| Combined-signature advantage, ownership transfer/history, DIV2K/DiffusionDB/general generated-image coverage | **Unsupported by this run**, correctly retained as untested/not addressed; no change to protected obligations. |
| Unforgeability/ownership | **Unsupported** as a security or legal ownership claim. Public-derived keys and one supplied owner per query do not demonstrate adversarial anti-forgery or all-roster error control. “No cryptographic unforgeability” must remain. |
| Novelty, historical no-crash/approval transcript, human held-out visual/semantic verdict | **Unverifiable in the reviewed evidence**. No independent novelty literature assessment or original human verdict/transcript was supplied for these assertions. |

## Non-blocking qualifications and residual limits

- Self-verification 300/300 is not a second independent clean result. F5 `embed_rgb` passes the source semantic features to its verification (line 254), whereas runtime detection recomputes them from the suspect pixels (worker 530-534). The clean miss is source `399205`, `content_uncertain`, soft semantic distance `6.041361413639602` above radius 6. Preserve the actual primary 299/300 and consider a footnote beside self-verification.
- Same SD1.5 family for carrier and attack, only 30 T3 sources, no human semantic-admissibility verdict, fixed nonadaptive attacks, and public keys limit generalization. Row repetitions do not increase independent sample size; per-cell intervals do not give simultaneous coverage. The report already states most of these limits appropriately.
- Fixed hashes and code ordering provide positive evidence against threshold/seed/outcome selection in this run. They cannot prove that no person or process ever accessed held-out data earlier. No such leakage or post-outcome method change was identified in the inspected record; do not turn this into an exhaustive historical access certification.
- Preserve P, R, all failed development/rehearsal evidence, the present approvals, and their inconsistencies. Correct the narrative additively; do not rewrite retained evidence to make it conform to policy. No science rerun, test tuning, protected-file edit, or retroactive approval is a remedy required by this review.

The scientific evidence is suitable for the user's M2 milestone review once C1-C5 are reflected in the report or a clearly linked correction addendum. Acceptance of the milestone and any further analyses remain the user's decision.
