# E3-S1 M2 confirmation: completed local continuation

2026-10-13. Codex agent. Scientific execution, collection and [independent evidence review](e3-s1-m2-independent-review.md) are complete. The review passed with no material blockers for the nine qualified claims. Human M2 acceptance remains pending; this document does not advance a Spec Kit lifecycle gate.

The preregistered, clean-admission-gated semantic endpoint favors E3-S1 over native v5 r3 at both regeneration strengths on the fixed 300-source cohort. This is a narrow composite result, not an isolated estimate of regeneration survival: clean endpoint eligibility is 294/300 for E3-S1 versus 159/300 for v5, and the methods use explicitly different h targets (E3 operational h versus v5 native intended h). The separate semantic-detection counts are 287 versus 283 at strength 0.1 and 284 versus 232 at 0.2. Six E3 images miss strict clean quality. Neither method retains source-majority full two-part acceptance after regeneration.

## Execution and completeness

Run `e3-s1-local-confirmatory-r3` finished with official status `completed`, worker status `finished`, exit 0 and no dispatcher errors. Local execution lasted 15,454.774 seconds (4 h 17 min 34.8 s), from 07:33:33.109 to 11:51:07.883 UTC. This was the second and final allowed continuation of the approved study, using the laptop CPU and RTX 5070 Ti. No new pilot, threshold, source, seed, method or attack was introduced.

All 42,031 planned unique records are present: 41,742 completed records, 49 safety-blocked regeneration images and 240 dependent unavailable detector calls. There are no missing, extra or duplicate identifiers. Scientific blocks remain in the fixed denominator; they are not retried or relabelled as observed detections. All 1,200 T4 records and 630 T5 records completed. The T5 selector retained 30 prescribed pairs without replenishment.

The local run appended 26,313 records to the exact 15,718-record parent journal. Its parent remains an exact byte prefix, and both retained parent runs' declared artifacts pass their hashes. The five final declared output files, 50 scientific code files, eight core data/config inputs, plan and source index pass their recorded hashes. Parent r1 remains checkpointed/officially failed (exit 3); parent r2 remains the honest migration interruption (exit -15, missing worker run.json). Neither history was rewritten.

The recorded aggregate worker budget is 49,318.833 seconds including 33,866.648 prior-attempt seconds; it is below the 86,400-second limit. The complete official local attempt was below both the 27,000-second cooperative and 28,800-second official ceilings. Peak process RAM was 4,357,017,600 bytes; peak allocated VRAM was 6,683.964 MiB. Additional local rental/API cost was zero; previously rented disks remain a separate retained-storage charge. The manifest retains its historical USD 7.50 envelope and rate field, which is not a measurement of local expenditure.

## Preregistered primary comparison

A source succeeds only when its clean mark is admitted, passes PSNR > 35 dB, SSIM > 0.9 and LPIPS < 0.1, recovers exact clean Q/H and full acceptance F, and has semantic predicate S on at least two of the three scheduled attacked alpha calls. Missing construction or attack results count adversely. Both methods retain N=300. Strengths are 0.1/0.2, seeds 3/4/5, SD1.5 DDIM20 with the frozen safety checker.

| Strength | E3-S1 composite success | Native v5 composite success | Paired difference | Approximate paired-source 95% interval | Exact one-sided paired p | Holm individual p |
|---|---:|---:|---:|---:|---:|---:|
| 0.1 | 281/300 (93.67%) | 151/300 (50.33%) | +43.33 percentage points | +37.33 to +49.33 pp | 1.91846e-33 | 1.91846e-33 |
| 0.2 | 278/300 (92.67%) | 129/300 (43.00%) | +49.67 percentage points | +43.33 to +55.67 pp | 4.76379e-38 | 9.52758e-38 |

The paired tables (E3 only, v5 only, both, neither) are (136, 6, 145, 13) and (156, 7, 122, 15). Both positive differences and both exact p < 0.05 satisfy the predeclared intersection-union conjunction. The descriptive intervals use 100,000 complete-source bootstrap resamples, PCG64 seed 61010. Inference concerns a hypothetical exchangeable-source model; this fixed, admitted cohort is not a random population sample. Repeated seeds and owner calls are not independent samples.

Do not describe +43.33/+49.67 pp as pure semantic survival gains. Clean eligibility and target conventions contribute to this composite. No conditional successful-source subset replaces the planned denominator, and no post-result matched-FPR claim is introduced.

## Clean coverage and regeneration limits

| Clean quantity, denominator 300 | E3-S1 | Native v5 |
|---|---:|---:|
| Returned final images | 300 | 300 |
| Native admission | 294 | 300 |
| Joint strict quality | 294 | 298 |
| Exact Q | 300 | 296 |
| Exact H | 300 | 162 |
| Full acceptance F | 300 | 299 |
| Complete clean eligibility for primary Y | 294 | 159 |

E3 minimum PSNR is 39.868744 dB and minimum SSIM is 0.929261. LPIPS median/maximum are 0.047652/0.184441. All six strict-quality failures are LPIPS >= 0.1: source suffixes 248752, 452122, 343937, 182021, 365385 and 425227. They remain in every planned denominator. Native v5 has two LPIPS failures (452122 and 365385), minimum PSNR 35.188512 dB, minimum SSIM 0.962029 and LPIPS median/maximum 0.018316/0.102785. Thus strict quality on every fresh source is false for both methods. Full measurements and failure UIDs are retained in `quality-failures.json` in the evidence bundle.

The following are predeclared descriptive source-majority counts, each over all 300 sources, before the primary clean-eligibility gate:

| Predicate | E3 at 0.1 | v5 at 0.1 | E3 at 0.2 | v5 at 0.2 |
|---|---:|---:|---:|---:|
| Semantic S (found and content match) | 287 | 283 | 284 | 232 |
| Checked semantic C (read and content match) | 287 | 243 | 284 | 112 |
| Exact semantic payload Q | 294 | 81 | 297 | 17 |
| Exact checked semantic J | 287 | 80 | 284 | 17 |
| Exact instance payload H | 0 | 0 | 0 | 0 |
| Both exact payloads D | 0 | 0 | 0 | 0 |
| Full acceptance F | 0 | 0 | 0 | 0 |

These secondary counts do not independently establish new significance claims. In particular, the 0.1 S difference is only four sources. Zero majority H/D/F means the retained evidence does not support regeneration-robust full two-part ownership. E3's clean H uses its operational target; v5 H uses its original intended intermediate payload, as fixed prospectively. Their exact-H counts are not target-equivalent calibration results.

## Negative calls

Neither method has an observed any-detection event A in the fixed clean or regeneration negative-call family. Clean evaluation is complete on all 300 sources for each method: 0/300, with a hypothetical one-sided 95% source-level upper bound of 0.993608%. This is not a 0.1% population-FPR claim and does not use thousands of correlated calls as independent evidence.

For T3, E3 has 290 completely evaluated sources and 10 unresolved source families; v5 has 297 complete and three unresolved. Their planned-cohort event-rate brackets are respectively [0, 3.3333%] and [0, 1.0000%]. Conservative one-sided 95% source-model upper bounds are 5.588474% and 2.564139%. Safety blocks are unobserved outcomes, not demonstrated positives or negatives. The methods are not compared at a matched false-positive rate.

## Copy-paste and semantic-collision transfers

Each row below has 30 planned and observed pairs. Q/H/D are exact donor delivery from the native none-mode call; F is full acceptance in the combined call. Conditions are kept separate and are not pooled as independent trials.

| Challenge | E3 Q / H / D | E3 F | v5 Q / H / D | v5 F |
|---|---:|---:|---:|---:|
| T4 residual 0.5 | 2 / 0 / 0 | 0/30 | 13 / 3 / 2 | 0/30 |
| T4 residual 1.0 | 6 / 2 / 2 | 0/30 | 17 / 7 / 5 | 0/30 |
| T4 public projection | 30 / 30 / 30 | 0/30 | 27 / 23 / 22 | 0/30 |
| T5 public projection | 30 / 30 / 30 | 0/30 | 29 / 22 / 21 | 0/30 |

For E3 public transfer, both payloads arrive on all 30 T4 and all 30 T5 pairs, yet all are rejected by combined F. This is observed rejection conditional on delivery for these prescribed challenges, not rejection inferred from failed delivery. The two panels cannot be pooled: selection and overlap restrict independence. E3 residual-0.5 conditional binding is undefined because no pair delivers D. Residual-1.0 has only two delivered E3 pairs. Native v5 rejects all observed delivered pairs too; no comparative full-acceptance advantage is established.

For T4 and T5 public shams, both methods have A=0/30 and F=0/30; donor delivery is inapplicable. On the same combined-call predicates, E3 semantic-only acceptance is 1/30 for T4 public and 9/30 for T5 public, while perceptual-only and combined acceptance are both zero. E3 therefore does not demonstrate an advantage of combined over perceptual-only binding. Native mode switches are routing controls, not isolated binding ablations. Native v5 has T5 same-call semantic-only/perceptual-only/combined counts 9/1/0, which remain descriptive.

A zero-F panel of 30 selected pairs has a hypothetical one-sided 95% upper bound about 9.50%, not 1%. LPIPS <= 0.2/0.3 proxy subsets and source-content diagnostics remain descriptive in the frozen endpoint artifact; human visual or semantic admissibility is still unassessed. T5 means source-selected operational similarity, not human-confirmed semantic equivalence or reference-specific same-owner identification.

## Claims and next milestone decision

The defensible result is a completed, positive, preregistered composite comparison on fresh sources and evaluation seeds, together with strong exact semantic-payload recovery in this pinned channel and measured rejection of delivered public transfers. The limitations above are part of that result. This is an alpha-only image-domain method; it does not prove the proposal's latent insertion, lightweight extraction, arbitrary-owner security, unseen diffusion robustness, cryptographic authorization, reference-specific same-owner attribution, combined-binding superiority, matched-FPR external superiority or general journal readiness.

Freeze and retain this confirmation. Do not tune thresholds, repair the six quality failures, replace sources, expand the attack set or rerun this held-out cohort as development. A future paper must foreground the clean-target asymmetry and failed full-ownership survival. Broader method work would need a separately scoped development study and fresh confirmation; no such experiment is started here. Human admissibility review and human M2 acceptance remain outstanding. Journal acceptance or quartile suitability is not established by this run.

## Evidence and reproducibility

The Windows evidence bundle is `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/analysis/e3-s1-local-r3-20261013/`. It contains the five declared artifacts under `run-r3/`, original official/execution manifests, `verification.json`, `result-summary.json`, `quality-failures.json`, and frozen design/plan/index/analysis copies. Original images and every run remain under WSL `/workspace/thesis/artifacts/M1b-test/`. The original recovered ZIP remains in MAIN. This private research package does not redistribute dataset images; source-image rights remain pending.

Frozen commit: `ae06b2979b64b445a2279b0b2a17dd76fcf103cc`.
Scientific core: `b55d19edd2ce5be256a1026f6286e5ed34fb5df0cd26e456942c5e0f6cebc9c5`.
Execution manifest: `8a0af683abf183bdcc42c5481a2c9d3d53e62ec58e6ca9acfeacb5fb1e5e81da`.
Final journal: `454674f2f7d81c8c7da7697437bf8ae7acbb1df31aa65de159cb1547f0980255`.
Final endpoints: `95f228c4d56f4c1089a44462a51eca3dfe5e8a010ff466ac72972af45eead80b`.

The frozen `m1b_e3_s1_analysis.py` produced the endpoints after the worker completed, using only the retained journal. The read-only collection helper `.thesis-build/vast-deployment/collect-local-r3.py` verified declared hashes, frozen inputs, planned IDs and parent preservation without rerunning inference or changing statistics. `verification.json` records its script hash and copied artifact hashes. The old transfer check's mutable Git-index metadata exception and expired original approval remain documented in the recovery receipts; fresh delegated local authority is separately recorded in `local-r3-authorization-receipt.json`. No human exact-hash verdict was fabricated. The study spans retained Vast observations and this laptop continuation; no bit-exact cross-hardware replay claim is made.

The fresh Astra/high reviewer independently reconstructed the planned IDs, raw-journal counts, primary paired tests and bootstrap intervals, quality failures, source-clustered negatives and transfer summaries, and checked source/code/output hashes and parent preservation. All nine claims were verified within their stated scope. The reviewed numerical and scientific text is unchanged; only this review status and reference were added. The compact evidence JSON files are versioned in `e3-s1-m2-evidence/`; `package-provenance.json` there records their hashes and the retained evidence location.
