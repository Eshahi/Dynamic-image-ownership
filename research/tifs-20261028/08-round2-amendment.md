# Round 2 pre-output amendment

Date: 2026-10-29. Base reviewed implementation: `665b4dd`; Round 2 begins at `071c8ec` after Claude's two brief commits. No Stage S scientific output exists. This file records prospective changes before the later server rehearsal. All retained methods, thresholds and outputs stay unchanged. Paid execution and held-out confirmation are not authorized by this amendment.

## R2-3: activation memory and measured capacity

Enable native diffusers 0.35.1 non-reentrant gradient checkpointing only for the F6 writer's gradient scopes, on the SD1.5 reader VAE and lazily loaded SDXL VAE, both frozen and in eval mode. Primary-source inspection confirms encoder and decoder gate on gradient mode rather than `.training`. The objective, steps, precision and native generation settings do not change. Flags are restored after normal/exceptional exit before final native verification. See `design/r2-memory.md` and `stage-s/writer-implementation.md`.

Replace the hard 24 GiB peak ceiling with the measured device total minus **1.5 GiB**. Minimum hardware is 24 GB class; fit remains unproven until rehearsal. Forecast receipts require identical device totals. Initial screen launch and every resume validate the measured total and reserve policy. Larger cards may qualify when the measured peak exceeds 24 GiB. Disk margin, 15-hour cap, complete-inventory forecast and OOM RESOURCE_STOP remain unchanged. Checkpoint recomputation cost is included in the later measured forecast.

## R2-2: bound-carrier control and separate article rule

Add `vine-b` to the full Stage S grid, retaining all previous arms. Its 100 bits are q32, owner/q public tag36 and q-conditioned masked h32. Radius-four unique decoding acts on q/tag68 only; h is raw after unmasking, so h errors cannot erase C/J. All targets are original pre-embed values; no oracle message or registry reaches the operational reader. Reuse the retained VINE adapter, seven-view F5 semantic functions, soft/h-distance status functions and decision table without changing retained files. Public-derived keys provide check redundancy, not owner authentication. The changed carrier statistics, conditional h read and target basis are explicit. Full rationale, capacity bound and rejected joint-code alternative are in `design/r2-binding-design.md`.

VINE-B gets both owner/C0 queries, all native cells, combined T4/T5 and all eight secondary transforms. WAM-B is omitted because its native 32 bits cannot retain q32+h32 plus owner check; WAM presence stays. Report C/Q/J/H/D/F/A and raw payload/field delivery separately. The full screen now has 1,728 native, 144 clean, 1,008 threat and 1,152 secondary producers, 7,168 reader rows and 4,032 quality rows. Rehearsal has one eighth of each; F6 marks remain 48+6.

Keep every F6 numerical thesis gate. Freeze a separate article comparison: both C/J lower-minus-comparator-upper ≥−1 in all four cells, paired median LPIPS delta ≤.005 and PSNR delta ≥−1 dB, plus either C/J gains ≥3 in the same foreign cell or LPIPS improvement ≥.002 AND PSNR improvement ≥1 dB. All sixteen paired values and complete inventory are required. VINE-B viability and reverse comparison are reported separately; a baseline failure does not automatically give F6 an edge. Thresholds are development margins, not inferential noninferiority. `scripts/tifs_article_decision.py` implements the config labels and never overrides the thesis verdict.

Generic bound-carrier novelty is pre-empted by inspected primary methods. A VINE-B win therefore becomes `F6_KILL_VINE_B_VIABLE_NOT_NOVEL` or the applicable F6-GO baseline-dominance label, not an automatic article pivot. Any conditional F6 article GO still requires prior-art clearance, fresh confirmation and human evidence where claimed.

## R2-4: full-inventory resource accounting

Keep the 15-instance-hour cap. The added carrier raises the full screen to 4,032 producer identities, 7,168 detector rows and 4,032 quality rows; its 1,792 owner queries require up to 74,276,608 candidate checks. Remove cross-item decode caching because rehearsal working sets could fit the cache while full-screen sets evict, biasing linear timing forecasts. Within-item shared network/features remain. No scientific timing or speed claim is made. `stage-s/round2-cost.md` and its JSON give exact counts and the unchanged conservative paid-time inequality. A failed measured forecast must return RESOURCE_STOP and the measured required cap, without reducing the design or increasing spending. Stage C needs a subsequent comparative amendment and new budget before approval.

## R2-1: inspected prior art

Seven primary-method checks are recorded in `literature/r2-prior-art-check.md`, with claim-specific pre-emption in `02-prior-art-delta.md` and `04-selection.md`. Generic semantic binding and optimization through fixed readers are not novel. The narrow F6 construction remains untested and does not have a firstness certificate. ForenMark was still missing at the 13:18 UTC cutoff on 2026-10-29 and is recorded as full-text UNINSPECTED under BRIEF-R2. No preview is substituted for inspection; novelty clearance against that paper remains unresolved.

## R2-5: bounded review corrections

The independent review found missing exact-code references could leave the VINE-B article result falsely complete. Require original marked q/h/100-bit references even after a valid no-read, all applicable positive-owner endpoints, and decode/delivery metadata. Preserve target-free C0/wrong-owner queries. Delivery receipts explicitly identify missing/invalid records. Also close the adjacent missing-run-identity path so it cannot leave an article GO after the package becomes INCOMPLETE. These are evidence-completeness corrections, not changes to a scientific threshold or decode rule.

Expose the original F6 `numerical_thesis_gate_status` separately from package status, and export the promised baseline quality/security, numerical parity and human-quality fields. No partial package can become GO. The review and closure status are recorded in `07-review.md` and `design/r2-independent-review.md`. The Round 1 numerical F6 thesis gates are not amended.

## R2-6: preparation release

The final report, readiness record and server runbook incorporate all nine arms, the separate article comparison, corrected evidence handling and measured-capacity rule. Preparation is COMPLETE with FEASIBILITY CONDITIONAL-GO. The independent review is accepted, 100 pure-logic tests and 22 Python compilations passed, and no scientific code changed after the reviewed correction commit `201f757`. The authoritative MAIN TIFS section was replaced with eight lines while preserving all preceding bytes. ForenMark access, server scientific compatibility, human evidence and later confirmation remain explicit limitations; no execution or publication authorization is created.
