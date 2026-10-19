# Independent M2 review: held-out registry confirmation

**Verdict: ACCEPT WITH CORRECTIONS for reporting this completed run as a bounded, negative overall confirmation. The experiment does not pass as a whole.** E1 satisfies the frozen numerical rule; E2 fails; E3 has zero observed wrong-owner accepts under the approved pre-result complete-case interpretation. This review is not a human gate decision, lifecycle advancement, or publication approval.

Reviewer: Codex independent reviewer, distinct from Claude, the results-note author. Review date: 2026-10-18. Scope: the existing run `registry-div2k300-confirm-01`, retained JSON/JSONL, protocol documents, and source-code inspection. No images, arrays, model weights, descriptors, experiment code, scorer, or Claude verifier were executed or opened as image data. Computation used only the permitted stdlib interpreter. The accompanying [recount JSON](01b-heldout-registry-recount.json) records the fields, procedures, denominators, and hashes.

## Sources and verification depth

Path abbreviations below are exact:

- `R` = `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/registry-package/artifacts/M1b-test/registry-div2k300-confirm-01`.
- `S` = `R/metrics/frozen-scorer-1792330103671103400/scoring/run.json`.
- `C` = `C:/Users/Soroush/.codex/worktrees/claude-registry-research/research`.

Read `C/claude-registry-confirmation-plan-20261017.md`, `C/claude-registry-heldout-gap-note-20261017.md`, `C/claude-registry-heldout-results-20261018.md`, and `C/claude-round3-frozen-20261017.json`; also `R/manifest.json`, `R/execution-manifest.json`, `R/metrics/endpoints.json`, `R/outputs/journal.jsonl`, `R/outputs/run.json`, and relevant metadata in `R/outputs/run-context.json`. Read, but did not run, this worktree's `scripts/m1b_registry_analysis.py`, `scripts/m1b_registry_scorer.py`, `scripts/claude_round3_two_factor.py`, and Claude's verifier.

The five output-artifact SHA-256 hashes in the final manifest match the retained files, including the journal and endpoints. The execution-manifest canonical JSON digest matches `a8ef7edc7b10873c34a11c289719976b48323adda487c712367061e38540e574`; its ordinary byte hash differs because serialization differs, not because the semantic comparison failed. Manifest fields report commit `c58a9ca8c48b8afd78a05bbab341bd062596f6e2`, `git_dirty=false`, test split, seeds 15/16/17, completed status, exit 0, and approval reference `c7868dfbb1b5df79d21720d027c6dfde002933b9b8c010fe4a385a77adfee4f9`. This is a retained-artifact consistency check, not independent authentication of a human approval or a replay of the entire execution environment.

The frozen parameters in `S.frozen` exactly equal the separately read frozen JSON. No threshold change is visible in these artifacts. The documented complete-case interpretation was approved after the run began but before descriptor scoring/endpoints, according to the contemporaneous gap note. That chronology is supported by the supplied documents; original chat authorization was not independently re-authenticated in this bounded review.

**Recount limits:** E1's final joint pointer-plus-descriptor decisions and E2's individual pair scores are not retained as JSON decision rows in the inspected artifacts. Therefore E1 success numerators and E2 accept numerators were cross-checked between saved summaries, not independently recomputed from image features. E2 availability denominators, real-pair/shot classification from saved PSNR values, and E3 attributions from 2,400 saved rows were independently recounted. E3 evaluability was reconstructed from journal completion, descriptor-cache metadata, native-call status, and record-code availability; descriptor cache contents were not opened. Do not describe this review as an independent pixel-level reproduction.

## Endpoint accounting

### E1: source-majority acceptance at strength .2

Source: `R/metrics/endpoints.json:E1`, cross-checked against `S:summary.round3.cells[model/0.2].F_R_source_majority`. Gaps remain misses; denominator remains 300, rather than the 297 successfully marked sources.

| Regenerator | Saved successes / planned sources | Independently recomputed one-sided 95% CP lower bound | Frozen numerical criterion |
|---|---:|---:|---|
| SD1.5 | 277/300 | 0.89313049 | Pass |
| SD2.1-base | 280/300 | 0.90459802 | Pass |

These bounds exactly reproduce the endpoint file. This is a majority-of-three-seeds source outcome, not 277 or 280 successful individual regenerations, not success on every seed, and not a rate on all diffusion models. Treat the two model results as separate marginal intervals; two simultaneous 97.5% lower bounds also exceed .85 (recorded in JSON). The protocol fixes only these generators/settings.

### E2: false accepts

Source: `R/metrics/endpoints.json:E2.families`, `E2.missing_rows`, `E2.unknown_pairs`, `S.look_alike_psnr`, and journal unit outcomes. **The unrelated-pair denominator in Claude's prose needs correction.**

| Family | Planned | Observed/evaluable | Saved false accepts | Independent units / uncertainty |
|---|---:|---:|---:|---|
| Wrong source | 3,408,600 | **3,343,081** | 0 | 300 query-source clusters have some observed comparisons; every cluster also has missing comparisons |
| T4 residual transfer | 600 | 594 | 0 | 297 observed donor clusters; conditional zero-error CP upper 0.01003594 |
| Real look-alikes below cutoff | 45 | 45 | 3 | 2 affected shots / 16 eligible shots; CP upper 0.34382520 |
| Ambiguous real look-alikes | 15 | 15 | 2 | Reported, not scored by E2; 1 affected shot / 6 |
| Ambiguous synthetic siblings | 12 | 12 | 4 | Reported, not scored by E2 |

The frozen wrong-source `n=3,408,600` includes `missing=65,519`. Inspection of `claude_round3_two_factor.report()` shows that it increments `n` for every planned pair before checking missingness. The independent journal recount reconstructs 38 query units per source (clean unmarked, marked, and 36 model/strength/seed/arm regenerations), each against the other 299 records: `300 × 38 × 299 = 3,408,600`. Requiring both query and compared record to have completed gives 3,343,081. Missing counts decompose into 33,825 record-only gaps, 31,433 query-only gaps, and 261 gaps on both sides. These are absent comparisons, not observed rejections.

T4's six absent rows are the two scales for donors 38, 463, and 821. They are listed separately in `E2.missing_rows`; the family-level `T4.missing=0` does not mean all 600 planned transfers existed. The frozen bound uses 300 donor clusters; the observed-case denominator is 297. Both round to roughly 1%, but the distinction must remain explicit.

The three accepted real pairs are `tos-05_4h-o072` (17.23795413 dB), `tos-05_4h-o144` (17.67512947 dB), and `tos-07_1c-o144` (16.89217345 dB). All lie below frozen cutoff 18.126065828471827 dB. The 45-pair and 16-shot denominators were independently counted from the saved PSNR dictionary; accepted pair IDs reproduce 3 pairs and 2 shots. Individual D1/B1 scores in Claude's prose were not independently reproduced here. The 3/45 pair estimate is 6.67%, while 2/16 shot incidence is 12.5%; neither is a universal collision probability.

Wrong-source zero incidence gives a one-sided binomial upper bound of 0.00993608 **for observed-comparison cluster outcomes, under independent-source sampling and the tested registry**. It cannot establish a less-than-1% risk for a complete registry: every query cluster has some unknown comparisons, the same record bank is reused, and query/record dependence remains. All-pair tests are not 3.34 million independent Bernoulli trials. The shot interval likewise assumes independent shots; the single-film sampling restriction remains.

### E3: regenerate-and-enroll attribution

Source: `R/metrics/endpoints.json:E3.rows[*].arms`, joined to `R/outputs/journal.jsonl` by source/cell. The approved complete-case conditions require the query, its native calls, its own original-owner record, and its own attacker record. Missing original marks are sources 38, 463, 821 in every cell. Additional SD1.5 exclusions are listed in the JSON; they vary by strength and further-regeneration availability.

| Cell | Evaluable / planned | Pointer original / none / any attacker | Fingerprint ambiguous / unique attacker / none | Fingerprint any attacker |
|---|---:|---:|---:|---:|
| SD1.5 .2 exact | 294/300 | 280 / 14 / 0 | 293 / 1 / 0 | 294 |
| SD1.5 .2 further | 294/300 | 242 / 52 / 0 | 285 / 8 / 1 | 293 |
| SD1.5 .4 exact | 294/300 | 201 / 93 / 0 | 266 / 28 / 0 | 294 |
| SD1.5 .4 further | 293/300 | 81 / 212 / 0 | 188 / 75 / 30 | 263 |
| SD2.1 .2 exact | 297/300 | 282 / 15 / 0 | 296 / 1 / 0 | 297 |
| SD2.1 .2 further | 297/300 | 249 / 48 / 0 | 289 / 7 / 1 | 296 |
| SD2.1 .4 exact | 297/300 | 199 / 98 / 0 | 266 / 31 / 0 | 297 |
| SD2.1 .4 further | 297/300 | 81 / 216 / 0 | 190 / 75 / 32 | 265 |

Every displayed count agrees with the saved rows and journal-derived complete-case inclusion. The frozen definition is **any accepted beta record, including an alpha-plus-beta ambiguous result**. Thus “up to 75 wrong” refers only to *unique attacker attribution*, while E3 failures for fingerprint-only include the much larger ambiguous category. Ambiguous means multiple owners matched, not that the implementation silently selected the attacker. Do not conflate `best_record` ranking with attribution, which retains all matching owners.

For the pointer arm, zero errors among 293–297 sources yields per-cell one-sided 95% CP upper bounds of **1.0036%–1.0172%**, conditional on evaluability and the observed record bank. Eight Bonferroni-adjusted bounds are approximately 1.7% and are provided in JSON. **Do not pool eight repeated cells into thousands of independent samples.** The same sources recur. A zero-error claim must retain abstention: at .4 further regeneration, only 81/293 and 81/297 receive original-owner attribution (27.65% and 27.27%).

The original frozen `E3.pass_` remains false, with all 2,400 entries flagged unknown because each cell has unavailable records. The approved reading is a distinct, pre-outcome availability amendment. It supports a conditional result; it does not establish that missing records or excluded queries would never cause an error. Removing a beta record can remove a potential wrong-owner acceptance. E2 tests against the original record bank are not a proof about every missing regenerated attacker record.

## Numbered findings

### Blocking corrections before article or thesis headline reuse

1. **Correct the unrelated denominator and missingness statement.** Replace “zero of 3,408,600 observed unrelated pairs” with “zero of 3,343,081 evaluable comparisons; 65,519 of 3,408,600 planned comparisons were unavailable.” Preserve the frozen `n` in tables with a planned label. This is a numerical reporting correction, not a threshold amendment.
2. **Qualify E3 confirmation and preserve the frozen failure.** State “zero observed attacker accepts among 293–297 evaluable sources per cell under the approved pre-result complete-case interpretation.” Retain `pass_=false`, `plan_view_E1_E2_pass=false`, `E2.pass_=false`, and `E3.pass_=false`. The unqualified phrase “E3 confirmed on held-out data” overstates complete-registry evidence unless this qualification is adjacent. The overall confirmation remains failed independently of completeness because of the 3 real-look-alike accepts.
3. **Use the same error semantics in the fingerprint comparison.** Report unique attacker attribution separately from ambiguity, and compare E3's `wrong_owner_present` across arms. “Fingerprint-only makes up to 75 wrong-owner calls” is incomplete as an E3 comparison; ambiguity also fails the declared criterion. Conversely, do not label all ambiguous results as unique wrong-owner assignments.
4. **Keep effective denominators and bounds honest.** Use 297 observed donors for T4 complete-case bounds, 16 shots for the primary look-alike cluster interpretation, and 293–297 sources separately in E3. The wrong-source bound is conditional on partial observed clusters and the reused record bank. Do not infer an independent-pair false-accept bound from millions of correlated comparisons.

### Nonblocking findings and explicit limitations

5. **Full raw rescoring is outside this review's permitted scope.** The retained summaries support E1's stated counts, and the bounds reproduce exactly, but independent reconstruction of joint descriptor acceptance was not possible from the inspected JSON alone without prohibited scoring/pixel use. E2 acceptance decisions likewise remain saved scorer outputs. This limitation must accompany any claim that every number was independently reproduced by this reviewer.
6. **Quality is descriptive and not uniformly within the earlier strict gate.** Quality exists for 297/300 marks. PSNR min/median/max: 41.8551/44.3333/45.4611 dB; SSIM: .929167/.985054/.997852; LPIPS: .000846884/.0182147/.149810. Only 291/297 satisfy PSNR>35, SSIM>.9, LPIPS<.1 together; six exceed the LPIPS limit, and three sources failed marking. The registry plan does not make that old gate an endpoint, so this does not retrospectively change E1, but prohibits claiming all held-out marks satisfy it. Human visual ratings remain absent.
7. **Operational counts match, with accounting distinctions.** Journal has 53,580 unique rows: 53,053 completed, 53 scientific failures (3 marking failures and 50 safety blocks), and 474 input-unavailable. `outputs/run.json` reports 43,401.126 s (12.0559 h), USD 0. Its `completed_units=53580` is total journal units, not successful units. Summed unit durations are 40,498.779 s and differ from run duration; do not substitute one for the other. No isolated end-to-end deployment latency was measured by this review.
8. **Interpretation stays narrow.** This is a trusted-registry, two-owner scenario using F5 as a pointer and D1+B1 as record side information; it does not establish legal ownership, adaptive-attack security, arbitrary registry scale, generated-image generality, a lightweight detector, or transfer across distinct autoencoders. E2 look-alikes are the frozen descriptor-only stress test, not evidence that all three were accepted by a fully evaluated pointer-plus-record pipeline.

## Recommended result sentence

“On 300 held-out DIV2K source groups, the frozen pointer-plus-registry rule met the strength-.2 source-majority criterion for SD1.5 (277/300) and SD2.1-base (280/300), with unavailable outputs counted as misses. The overall confirmation failed: the descriptor check accepted 3/45 clearly different same-film look-alike pairs from 2/16 eligible shots. No accepts were observed in 3,343,081 evaluable unrelated comparisons or 594 transfers, with 65,519 planned unrelated comparisons and six transfers unavailable. Under a pre-result approved complete-case interpretation, the pointer arm accepted no attacker record in any of eight regenerate-and-enroll cells (293–297 evaluable sources per cell), with substantial abstention after stronger further regeneration.”

The review accepts this bounded reporting after corrections; it does not convert the negative overall confirmation into a pass or authorize a held-out retest.
