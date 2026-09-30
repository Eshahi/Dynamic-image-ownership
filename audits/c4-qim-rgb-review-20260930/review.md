# Independent exact-artifact and retained-output audit

Date: 2026-09-30. Author: /root. Independent reviewer: /root/qim_component_review, invoked under AGENTS.md bounded technical-review delegation. This transcribes actual reviewer findings; it is not a fabricated human decision.

## Before execution

The unchanged supplied algorithm/profile hashes were checked. Eight supplied synthetic tests passed. Component review demonstrated that approximate public owner matching can accept a selected wrong owner (wrong-owner-590 against owner-alpha, owner accuracy .75, valid CRC). It also identified a nonmultiple-of-eight padding boundary mean change and runtime profile validation drift. The pilot binds the exact canonical profile and preserves these limitations; it does not silently change the supplied algorithm.

Initial whole-package review at aea3a4225d1bb4318348f9b44f06efad80a4831e found two blockers: non-atomic checkpoint writes and missing C0 calls concealed by zero-positive summaries. Both were repaired. Final clean reviewed/executed commit 2e05d926ec9eb889116a60be19fe5345211b512b uses atomic checkpoint replacement and explicit completed/missing call accounting. Four owned synthetic tests passed. Reviewer verified all 18 manifest inputs, launcher binding and 1877 external runtime file hashes against canonical manifest 5532fe6fc5f7c88de4535a3d097fdda566e409dee1a8baf483c90c59b3f98b42. No narrow execution/reporting blocker remained. No scientific worker or study pixels ran during that review.

## Retained results

Actual reviewer verdict: **no blocking inconsistency found**. No scientific rerun, image decoding, model call or mutation occurred in the retained-result review.

Reviewer independently verified results SHA256 11132dc4363d4a2ec22f1754cd1291a96b4c83e85ea07d5a6bda686438b6945a, retained canonical manifest, clean executed commit and official completed/exit-zero/error-free receipt. Ten distinct frozen cohort sources completed with 130 unique expected condition/control/owner calls. All 130 referenced PNG file hashes matched. Primary joint outcome recomputed to 10/10. C1 counts recomputed to native10, noise10, resize9, JPEG0, shift0 out of ten each; resize failure source499768. All 50 C0 calls completed with zero positives, and the three fixed native wrong owners yielded zero positives in 30 calls.

Independent recomputed descriptive means: PSNR50.34637688473825dB and SSIM0.9962389085597125. Minima50.0805055527171dB and0.9935502139693143. Stored PSNR values agree with stored MSE arithmetic. LPIPS markers are consistently NOT_RUN. Stored summaries match recomputation. Retained files occupy approximately67.2MiB and worker elapsed approximately60.2seconds. Pixel hashes and quality were **not** independently recomputed by decoding pixels; the review verifies file integrity, completeness and stored arithmetic, not an independent codec/SSIM replication.

Warnings retained: prominently report JPEG/shift failures; previously accessed development census is not held-out generalization or calibrated global FPR; repeated controls/owners are not independent samples; three negative owner strings do not negate demonstrated approximate-tag collision. LPIPS, authentication, regeneration, learned comparisons and forgery resistance remain unmeasured. Disk budget was an estimate, and standard-library/OS runtime libraries are receipt-only rather than part of the byte inventory.

This is bounded integrity/completeness review of exploratory evidence, not method acceptance, compute authority, publication approval or Spec Kit gate acceptance. One actual user-authorized local experiment was executed; its authorization is consumed.
