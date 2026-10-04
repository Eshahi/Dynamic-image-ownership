# Original-A binding-ablation development result

Completed CPU supplement, 2026-10-04. This report checks retained development evidence, not an independent milestone review. No method, threshold or old output was changed; no GPU/model generation, held-out access or new scientific scoring was performed for this report. Human verdict and security verdict remain missing.

## Exact receipts and bounded inventory

Run: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261004-1000-A-binding-ablation`, commit `96b9b66ed116514db3fba882f38300c904c6b015`, outcome completed, duration212.281s. All87savedPNG conditions and348correct-owner calls completed, zero failures. There are80T4 conditions and7T5-transfer conditions, four binding modes each. No new wrong-owner query was run. Same public owner-alpha and unchanged original-A full-CLIP v5 thresholds/profile/radii apply throughout.

| Receipt | SHA256 |
| --- | --- |
| run.json | c35eee2d2f805b86f761b5fdbc421fd53091fb442ec6d2b82377d9531fd75290 |
| manifest.json | 9bfaeabf1878e51dbd0586d49f9e97b8dba2ea089d25dfd8e395559d45e4bb9b |
| conditions.json | 416f716f18d541abb4a59ee260771f126dd05530bfbdf1b0c5ff972946a4877d |
| journal.jsonl | fda1ab41d7a0079736cef92508677bded22d3ba156f4faf5be143cf0d2d025a6 |

Source threat run0900 remains incomplete472/489 with17safety failures. Its runSHA is `7929d9cbbf7a9314f7959d85144fe26d99324ffd7ecc10e40455f5f623ce07a6`; conditionsSHA `404aefbe30d934b8405732cf62a3765da4550fba30e5ee7f4030a11eeb5a5b4e`. The supplement uses the complete80T4+7T5-transfer subset; it neither repairs nor hides17missing other threat conditions. Its four chronological enrollment receipts remain the original12-source collection, not348independent sources.

Read-only checks verified every declared output hash, source run/conditions hashes, all87canonical source-row hashes, all87transferPNG and87recipient-source receipt references, and allfour enrollment run hashes. Exactly four distinct mode calls exist per condition. CPU arithmetic independently rechecked stored strict quality and fixed-donor delivery flags from saved numeric fields; reconstructed summary equals run summary. The retained worker reports87/87exact old-combined numerical parities and87/87exact suspect-CLIP receipts. It recomputed CPU CLIP; report inspection did not rerun CLIP, LPIPS or detector. Original LPIPS measures remain retained/hash-bound rather than newly inferred.

## Presence, content binding and delivery

| Axis/mode | both_match | semantic_only | instance_only | content_mismatch | content_uncertain | neither_match |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T4 combined | 0 | 5 | 0 | 25 | 6 | 44 |
| T4 none | 16 | 18 | 2 | 0 | 0 | 44 |
| T4 semantic_only | 3 | 5 | 2 | 13 | 13 | 44 |
| T4 perceptual_only | 0 | 18 | 0 | 18 | 0 | 44 |
| T5-transfer combined | 0 | 1 | 0 | 4 | 2 | 0 |
| T5-transfer none | 4 | 3 | 0 | 0 | 0 | 0 |
| T5-transfer semantic_only | 2 | 1 | 0 | 1 | 3 | 0 |
| T5-transfer perceptual_only | 0 | 3 | 0 | 3 | 1 | 0 |

Carrier presence is invariant across four modes: T4semantic34/80, instance18/80, dual16/80; T5semantic7/7, instance4/7, dual4/7. Binding-none both_match means both owner carriers are found with content unchecked. It is not a blind donor identity match: every donor uses the same public owner. The donor-delivery witness instead compares readable decoded codes to frozen donor enrollment q/h with original corrected-distance/radius rules. Those donor receipts are evaluator side information; they never reach the primary blind verifier. Shams are excluded from delivery even if a carrier happens to be found.

| T4 arm | outputs | strict recipient quality | quality+semantic donor delivery rows | quality+dual donor delivery rows |
| --- | ---: | ---: | ---: | ---: |
| clean donor residual | 40 | 38 | 10 | 1 |
| public projection | 20 | 19 | 17 | 11 |
| unmarked projection sham | 20 | 19 | 0 | 0 |

Across T4, strict quality76/80; semantic donor delivery covers10distinct recipient source clusters, dual donor delivery only8/10. Thus the prespecified minimum10T4 dual-delivery coverage fails. The12quality-admissible dual-delivery rows all yield combined content_mismatch. This demonstrates rejection for those delivered rows, but cannot promote the whole T4 condition to adequate dual-delivery coverage or secure forgery resistance. The20shams are controls, not successful attacks.

For T5-transfer, strict quality7/7; quality+semantic delivery7rows/fourrecipient clusters, quality+dual delivery4rows/threeclusters. Of those four adequate dual-delivery rows, combined returns three content_mismatch and one content_uncertain. All seven combined false full-attributions are zero. This is a small paired transfer supplement to the original semantic-pair study, not enough independent delivery coverage for a global T5/security pass; the existing66pair semantic-label evidence is unchanged.

## Recipient quality and limits

Ranges and means below include every completed PNG, including shams and quality failures; repeated doses/modes do not create new image/source samples. Strict quality is PSNR>35, SSIM>.9, LPIPS<.1. CLIP>=.85 remains exploratory semantic-retention proxy, not human quality or a fitted decision threshold.

| Axis/metric | minimum | mean | maximum |
| --- | ---: | ---: | ---: |
| T4 PSNR dB | 34.496585 | 42.452979 | 48.016872 |
| T4 SSIM | .935234 | .977371 | .995528 |
| T4 LPIPS | .001865 | .024757 | .169930 |
| T4 CLIP cosine | .957223 | .993556 | .999794 |
| T5-transfer PSNR dB | 43.676890 | 45.407021 | 46.331537 |
| T5-transfer SSIM | .987279 | .990539 | .993401 |
| T5-transfer LPIPS | .002819 | .007459 | .013830 |
| T5-transfer CLIP cosine | .995960 | .998285 | .999594 |

Four T4 quality failures remain: residual6012→147498scale1 LPIPS.169930; residual134882→147498scale1 LPIPS.130914; public projection499768→6012 PSNR34.496585; its unmarked sham PSNR34.682502. All87CLIP cosine values exceed.85, which does not override those four failures. Detector calls total158.186s for T4 and13.798s for T5, versus212.281s whole-run wall time including receipts/model/feature/quality work; CPU caching and repeated-mode timing are not cold-start extraction benchmarks. U-Net/model-generation calls and GPU model calls are zero.

The controls separate owner-carrier presence, donor-code delivery and content consistency. They supply measured binding benefit on delivered rows, while the frozen dual-delivery coverage shortfall remains. Public-derived keys, shared owner, only12development enrollment sources, repeated donor-recipient graph, missing human assessments and the original run's other17failures prevent stronger attribution/security/population claims.
