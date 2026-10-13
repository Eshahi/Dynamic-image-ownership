# Post-M2 refinement ablation: a ceiling and a quality-selection effect

2026-10-13. Exploratory development evidence on twelve previously used sources. This report does not replace the reviewed 300-source M2 result, infer human acceptance, or establish journal readiness.

## Decision

The extra post-initializer stage **does not pass the prospective useful-refinement screen**. Starting and final images both achieve exact checked-semantic source-majority recovery J on 12/12 sources at strengths .1 and .2. Their paired majority difference is zero at both strengths, with no unavailable positive calls. The required gain of at least two sources at .2 is absent.

There is one additional successful seed-level J call at .2 and one clean-quality improvement. Both occur on source 147498, whose minimax optimizer accepted zero updates and whose final selector contracts the initializer perturbation by .8. Thus the observed binary-endpoint improvement on this panel belongs to quality selection. Seven other sources have actual minimax pixel changes, but none changes J on any scheduled attack identity. This is a measured ceiling on this seen panel and channel, not proof that refinement can never help or permission to remove it from the frozen method.

Do not increase attack strengths on these artifacts to obtain a favorable comparison. Preserve the negative screen. The next development priority is a fresh-source comparison of the full pipeline against its initializer plus the fixed quality selector, followed by a controlled initializer/carrier ablation. Do not lead a paper with an unisolated minimax or error-correction gain.

## Fixed comparison and completed work

The [prospective protocol](post-m2-fair-comparison-protocol.md) fixes source IDs 1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505 and 499768. I is the saved E3-S1 initializer; E is its selected final image; C0 is the common original. Both positive arms use identical supplied q/h, a source-blind BCH reader, unchanged thresholds, soft binding, one claimed owner and seven CLIP views. No construction, supplier, target or threshold was retuned.

Attacks use the pinned SD1.5 DDIM20 pipeline at strengths .1/.2 (two/four effective steps), seeds 6/7/8, empty prompts, guidance 1, eta 0, fp16 and the enabled safety checker. A fresh generator with the same seed is used for each paired identity. These seeds differ from writer seeds 0–2 and M2 seeds 3–5. Sources and model remain familiar; fresh seeds alone do not make this confirmation.

All 252 planned image rows are recorded: 36 clean and 216 attack rows. Four exact I/E pairs allow 28 explicit row aliases, including 24 attack aliases. There were 192 actual regeneration attempts. The final inventory is 248 available rows and four safety-blocked C0 images. Both owner calls are retained for every available row; the eight dependent calls on blocked images are unavailable. No retry or replacement occurred.

Execution at commit `73f8f1529c5f964eeb2c53ced3726c27c581118c` took 557.156 seconds (9 min 17 s), starting 12:56:45 UTC and finishing about 13:06:03 UTC. Maximum measured allocated GPU memory was 3,814,109,696 bytes; process working-set peak was 3,312,791,552 bytes. New run files total 97,346,559 bytes. Additional rental/API cost was USD 0; electricity was not metered.

The original conservative study clock begins 12:47 UTC and ends no later than 13:32 UTC. Probe `inclusive_duration_seconds` is 818.411 seconds measured from the successful census; it excludes earlier failed checks and is not the full study duration. The fixed absolute deadline, which was not extended, is authoritative. Analysis and package review also finish before it; no child process remains after execution.

Two failed CPU census attempts are preserved. The first parsed a hashed group ID instead of the COCO source UID and stopped before scientific image access. The second stopped after two rows because inherited Stage A aliases had different paths. Their RGB arrays were verified identical; a documented design-review amendment allowed a single pathname correction without changing the science or deadline. These failures are not successful observations. The completed census took .782 seconds at `98d6c5e`.

## Recovery and quality results

J means semantic read, exact decoded q, and content match. A source-majority success requires at least two of its three seeds. The source is the unit; seed rows and reused observations are not independent replication.

| Outcome | Initializer I | Final E |
|---|---:|---:|
| Strict clean quality | 11/12 | 12/12 |
| Clean exact Q/H/full acceptance | 12/12 | 12/12 |
| Raw majority J, strength .1 | 12/12 | 12/12 |
| Raw majority J, strength .2 | 12/12 | 12/12 |
| Seed-level J, strength .1 | 36/36 | 36/36 |
| Seed-level J, strength .2 | 34/36 | 35/36 |
| Exact semantic Q, either strength | 36/36 | 36/36 |
| Clean-eligible AND majority J, either strength | 11/12 | 12/12 |
| Full acceptance majority after regeneration, either strength | 0/12 | 0/12 |

Each paired majority table has both-success=12, I-only=0, E-only=0 and neither=0. The missingness-adverse majority difference interval is [0,0]. On the common clean-eligible subset, both achieve 11/11; this diagnostic does not replace the original N=12. The joint endpoint's one-source difference is entirely clean eligibility.

At .2, source 4795 has two successful J seeds in both arms. Source 147498 improves from two to three; its only discordant identity is seed 6. No other J identity differs. All semantic words are recovered exactly, so these failures concern the content-match condition, not message loss. Full acceptance remains a fragile-tier limitation rather than a semantic-recovery gate.

Strict quality requires PSNR >35 dB, SSIM >.9 and LPIPS <.1. I has median/minimum PSNR 41.4695/40.6288 dB and median/minimum SSIM .968812/.956458; E has 41.4421/40.3635 dB and .971069/.956458. Median LPIPS is .041216 for I and .041223 for E. Their maximum LPIPS is .118490 versus .076258. The constraint is shared; achieved distortion is not identical.

The following paired LPIPS values are from the fresh clean evaluations. Paths, pixel differences, PSNR/SSIM and inherited provenance are in the census and raw rows.

| Source | Accepted minimax updates | Final branch | I LPIPS | E LPIPS |
|---|---:|---|---:|---:|
| 1675 | 0 | retain, identical | .049604 | .049604 |
| 4795 | 4 | retain | .029378 | .029459 |
| 6012 | 1 | retain | .012513 | .012650 |
| 25394 | 0 | retain, identical | .031302 | .031302 |
| 80932 | 1 | retain | .032828 | .032843 |
| 109798 | 0 | retain, identical | .070464 | .070464 |
| 134882 | 3 | retain | .055450 | .062075 |
| 147498 | 0 | contract .8 | .118490 | .076258 |
| 177015 | 0 | retain, identical | .024269 | .024269 |
| 190676 | 3 | retain | .054280 | .056324 |
| 468505 | 1 | retain | .054068 | .054903 |
| 499768 | 2 | retain | .029242 | .031377 |

The retained records attribute 357.11 seconds in total to refinement. That is historical stage time, not a measured net runtime saving from a deployed simplified method. Such a comparison must include initialization, selection and any required evaluations consistently.

Median attack-to-input LPIPS at .1 is .161652 for I and .161220 for E; at .2 it is .221560 and .220626. Maximum values are .223860/.224279 and .296504/.295643, respectively. All positive attacks have LPIPS <=.30, but this is only a declared proxy. No human admissibility judgment is available. Continuous PSNR/SSIM/LPIPS against marked inputs and canonical C0 are retained, plus paired attacked-C0 metrics when that output is available.

## Negative observations and unavailable results

All four clean negative families have zero observed A events on 12/12 sources. Wrong-owner calls for I and E after regeneration have zero events on all 36 calls per arm and strength. Each C0 owner family has zero events among 34/36 observed calls per strength; source 6012 is unresolved because seeds 7 and 8 were safety-blocked at both strengths. Those four blocked images are not negative observations.

For each C0 owner/strength family, the fixed-cohort source event-rate bracket is [0,1/12], reflecting unresolved calls, not a confidence interval. Even a complete zero-event sample of twelve independent sources would have an individual hypothetical 95% upper bound around 22.1%. This adaptive panel establishes neither a population FPR nor a cryptographic security bound. Negative families are not pooled.

## Explicitly post hoc decoder diagnostic

The systematic BCH encoder stores q in the high 32 bits of the 59-bit word (`q << 27` plus low-bit parity). We compared `raw_received_word >> 27` with the target, then compared decoded q, threshold-qualified Q and checked J on the same saved signals. This diagnostic was added separately, changes no prospective refinement criterion, and uses no additional inference.

For each arm, raw systematic q, decoded q and qualified Q are exact in all 72/72 attack observations and 12/12 clean observations. There are zero raw-message rescues or harms from decoding in this sample. Each arm has one received parity-bit error at .2; the raw message is already correct. This does not show that BCH is unnecessary at harder channels: it shows that error correction is not repairing message errors in this particular panel. A raw systematic equality diagnostic is not an implemented uncoded detector with matched thresholds, code rate, quality or FPR.

## Revised development sequence

1. **Test a simpler construction on fresh development sources.** Compare full E3 against the same initializer plus its fixed quality selector, sharing targets and attack identities. Reserve sources by a written metadata-only rule before observing outcomes. Keep native v5 as a separately labelled end-to-end comparator. Measure construction time consistently. This result supplies a candidate simplification, not a frozen method amendment.
2. **Identify the initialization mechanism.** Separately manipulate the carrier/code, latent optimization objective and supplier, under common payload capacity, targets and quality constraints. The present panel has a message-recovery ceiling. Choose any wider channel grid prospectively on new development sources; do not hunt for a winning setting on these saved images.
3. **Establish whether combining bindings adds value.** Use delivered T4/T5 pairs with fixed attempt budgets and same-call component decisions. Seek admissible component disagreement in development and preserve all attempted/failed deliveries. If both individual and combined checks reject everything, report redundancy on that domain.
4. **Then run fair external comparisons.** Follow the existing pinned WAM feasibility work, then feasible FreqMark/ZoDiac comparators. Separate native operating curves from matched quality and calibrated-FPR comparisons; published percentages alone do not establish superiority.
5. **Complete human admissibility and fresh confirmation.** Prepare a blinded assessment after the method and comparisons are stable. A future held-out experiment requires its own fixed design and user milestone decision. Leave all completed M2 observations unchanged.

## Reproduction and review

Primary run: MAIN `.thesis-build/dev-runs/20261013-e3-initializer-ablation`; completed census: MAIN `.thesis-build/dev-runs/20261013-post-m2-refinement-census-completion`. Analysis: MAIN `.thesis-build/analysis/post-m2-refinement-20261013`. MAIN means `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`.

The committed scripts are `scripts/post_m2_refinement_census.py`, `scripts/post_m2_refinement_probe.py`, `scripts/post_m2_refinement_analysis.py` and `scripts/post_m2_decoder_diagnostic.py`. The two analysis commands take `--run-dir` and `--output` and perform no inference. Compact evidence is saved beside this report in `post-m2-refinement-evidence/`. Synthetic arithmetic checks cover fixed inventory, paired source-majority, adverse missingness, unresolved negatives and decoder-rescue/read-threshold distinctions.

The [independent review](post-m2-refinement-independent-review.md) reconciles raw calls, inventory and claims. Human M2 acceptance, visual admissibility and official lifecycle advancement are not inferred from this technical review.
