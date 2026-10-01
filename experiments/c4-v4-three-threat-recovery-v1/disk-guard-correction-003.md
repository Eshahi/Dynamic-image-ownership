# Fresh003 package after the output disk-scan correction

Related issue #18 / draft PR #67. This document binds ordinary preparation, not a scientific result or execution approval.

## Retained failure and narrow correction

Evaluation002 officially failed during VERIFYING_INPUTS at 2026-10-01T21:54:59.714406Z. FileNotFoundError named `outputs/.pending-cuppse_c`; zero new detector calls, evaluated rows, seals or journal records were produced. All five declared outputs and six indexed artifacts verified. Original immutable receipts, consumed approval and parent scientific evidence remain retained outside this checkout. The failure is infrastructure-only, not a method verdict.

The source supports a temporary-file race between the disk guard's enumeration/stat and the heartbeat's atomic replace; no historical traceback proves the exact failing stack. User-provided clean commit `069344b5fc6dd853f3e67ef4e2b2da0ea77c992b` added `tree_bytes()`. Only a disappearing `.pending-*` FileNotFoundError is skipped. Existing pending files count; other missing paths and I/O errors propagate; scientific input hashes remain fail-closed. The 2,000 MiB polled output guard is unchanged.

Fix-only independent review found no blocker. Its non-blocking concurrent-test weakness is now addressed: capture writer exceptions, require at least two successful writes, verify the final heartbeat and bounded thread termination. Ordinary tests contain fake adapters only; they are not scientific execution or actual official-preflight evidence.

## Fresh exact identities and immutable boundaries

This preparation uses `c4-v4-recovery-host-check-003` and `c4-v4-saved-evaluation-003`, never the consumed002 run IDs. The fixed host allowlist, entrypoints, worker, metadata builder and corresponding tests bind those identities. No algorithm/model/threshold, source/seed, scientific schedule, safety disposition or acceptance rule changes.

The complete clean commit and both metadata-built manifests must receive bounded independent exact-package review. Present their full canonical hashes and resource envelopes for one actual authenticated batch decision. A generic assent before those hashes exist is not that decision; no approval is created here. Official validators and the unmodified runner remain mandatory.

After an actual exact decision, launch003 harmless preflight once. Verify declared hashes, request/readiness/ACK/acceptance chain, matching actual startup/completion identity, and successive progress while its initiator is absent. Recheck clean inputs/resources/no competing writer before a single dependent scientific evaluation. A failed prerequisite or worker stops the branch; never overwrite receipts or auto-retry.

## Unchanged scope and resources

CPU-only, USD0, no CUDA/generation/reembedding/download/install/public push. Preflight: RAM128MiB/disk16MiB/60-second safety watchdog. Evaluation: RAM6144MiB/VRAM0/disk2048MiB/86400-second total safety watchdog, 1800 seconds per unit. Unmeasured 2–8-hour planning estimate is not a completion promise. Guards are polled, not OS allocation caps.

Evaluate 401 existing images and 66 component comparisons, retaining16 inherited safety failures:209units/483rows. Preserve96 inherited clean calls; up to1508 new suspect-only calls. Original1884 denominator remains96+1508+64safety-missing+212withheld+4unresolved. The53 downstream generation candidates and ambiguous `t3-190676-0.4-1-C1` remain withheld/quarantined, with no retry or false terminal receipt. Three primary threats remain Regeneration, Copy-Paste and Semantic Collision. Phase sealing is not whole-study completion, joint support, original latent-method validation or native2K/6900-source fulfillment.

All unrelated work stays paused; C4open/C5dependent. Spec Kit plan-acceptance remains separately paused/null. Publication decision remains separate. No lifecycle verdict is fabricated by this preparation.
