STATUS: PARTIAL — WP1 has a strict corpus limitation; WP3 and WP4 are incomplete; WP5 was not performed.
FEASIBILITY: CONDITIONAL-GO

# TIFS research session, 2026-10-28

**This verdict supports finishing a bounded research test, not TIFS readiness, experimental success or permission to launch. Stage S is not server-ready.** No new scientific result was produced. The present thesis evidence still does not establish the proposed positive cross-family contribution.

## Selected contribution and reason

The selected primary idea is **F6-noise**, an image-domain writer that optimizes the unchanged F5 reader through finite codec-plus-noise surrogates. Its matched codec-only and generic-distortion controls test whether the noise-stage objective adds something useful beyond codec optimization or generic augmentation. Kandinsky 3 is excluded from this writer's design; a later, prospective SD3.5 Medium family is proposed for fresh confirmation. The preserved F5 failures motivate this hypothesis: held-out source-majority C is 182/200 for SD1.5 .2, 0/200 for SDXL .2 and 61/200 for Kandinsky 3 .2. These old observations cannot confirm today's hypothesis.

The claimed opportunity is a positive, quality-controlled and content-consistent cross-family result with an unchanged reader, supported by matched ablations and T4/T5 tests. Generic robust writing, noise augmentation, soft content binding and a registry pointer are already crowded prior art; none is claimed as new by itself. F6 is not the proposal's latent insertion method, not cryptographic authentication, not proof of original-instance uniqueness and not proof of lawful ownership. The backup is I03, a finite reader-response predictor, requiring a separate decision and budget if the primary fails.

See [selection](04-selection.md), [twelve ideas](03-ideas.md), [hostile review](design/wp2-hostile-review.md), [TIFS evidence bar](01-tifs-bar.md) and [prior-art delta](02-prior-art-delta.md). The hostile WP2 review is complete; it is not the missing WP5 code/protocol review.

## Delivered and missing

| Package | Actual completion | Material limitation |
|---|---|---|
| WP0 | Complete | Starting evidence and scope retained. |
| WP1 | Broad survey and gap analysis delivered | Nine TIFS-linked works include seven direct image studies and two adjacent-domain studies. An eighth directly relevant image study and some final journal full texts were not verified. Do not call this an unqualified eight-image-paper corpus. ForenMark full-text access also remains a prior-art gap. |
| WP2 | Complete | Twelve candidates, derivations, fresh hostile review and selected primary/backup; novelty remains conditional on later evidence and remaining source access. |
| WP3 | Partial | Stage S config and development source manifest exist. Stage C power, family feasibility and committed selection rule exist. The two integrated protocol documents and fresh Stage C identifier-only manifest are missing. |
| WP4 | Partial, NOT READY | Writer, producer, reader, common helpers and bounded tests exist as draft source. Setup, driver, forecast enforcement, analysis and complete integration are missing. |
| WP5 | Not performed | No independent final protocol/code reviewer was commissioned or completed. |
| WP6 | Partial-session closure | This report, progress record, readiness lock and MAIN state note close the elapsed session. No extensions were started. |

The known concrete code blocker is the producer/reader calling `Journal(..., read_only=True)` while the current common helper does not implement that argument. A concurrent reader must not repair/truncate a producer's active journal. Additional interface and scientific correctness defects may remain because integration and independent review are incomplete. The presence of a file named `frozen-config.json` is not certification that the complete study is frozen or executable.

`stage-s/READINESS.json` is INCOMPLETE. Both scientific entrypoints share a guard that refuses execution before importing torch. Do not remove this lock merely to try the program. The retained implementation notes describe intended behavior, not verified end-to-end behavior.

## Proposed Stage S decision and costs

The prospective development screen uses 16 donor sources, 16 other targets and a separate two-donor/two-target rehearsal, all selected from the existing 60 development sources. It does not consume the 200 completed Phase-B sources or their 40 reserves. There are eight arms: F6-noise, F6-codec, F6-generic, F5 r2, v5 r3, WAM, VINE-R and unmarked. Native cells are SD1.5 .2, SDXL .1/.2 and Kandinsky 3 .2, with seeds 0/1/2: 1,536 native output attempts for the screen, plus clean marks, T4/T5 and the separate fixed standard-distortion family.

The selected rule requires both the inherited C endpoint and exact semantic-code/content-consistency J endpoint. Foreign-family source-majority counts must reach at least 12/16; gains over F5 must reach four sources on SDXL and three on K3, and gains over each matched ablation three on SDXL and one on K3. SD1.5 net loss is at most one source. Every new writer must meet strict clean quality on all 16 sources; the frozen clean-binding and relative-distortion conditions also apply. C0/wrong-owner and eligible T4/T5 false-attribution events must be zero, with missing outcomes retained as unresolved. The config contains the full proposed conjunction; no partial inventory can yield GO. These rules need reconciliation into the missing protocol and executable analysis before launch.

Stage S has a **15 instance-hour ceiling including rehearsal**, approximately **USD 6.75–9.00** at the brief's assumed USD .45–.60/hour. These are budget-envelope arithmetic, not a current rental quote or measured F6 forecast. The planned launch test is measured one-time cost plus 1.5 times complete-inventory variable cost plus a one-hour retrieval reserve within that ceiling. It has not been implemented or measured. A 24 GB fit, gradients, native timestep agreement, saved-PNG readback and replay remain server rehearsal obligations. Do not rent compute until the package is complete.

Stage C proposes n=120 fresh sources with 40 reserve identifiers, six Holm slots and a **50 instance-hour ceiling**, approximately **USD 22.50–30.00** under the same assumed rates. Exact analytical planning gives about .9165 power for a .85 source-success probability against .70 at the worst .05/6 threshold, and .9589 paired power for discordances p10=.25 and p01=.05. A modest .10 paired gain is much harder to establish. These are design calculations, not empirical results. Zero events in 120 independent sources only gives a one-sided 95% upper bound of about .0247; it does not support a cryptographic false-accept claim.

The fresh-source selection rule was committed as `3cdbb11` before any metadata draw. **The draw was never executed and no fresh held-out manifest exists.** Cached metadata had insufficient creator diversity for the proposed 120+40 rule. SD3.5 Medium requires later user licence/access action, an exact revision and a fresh disk plan; the old 76 GB volume is not assumed adequate. Independence of released weight initialization is unverified, so the defensible description is a prospectively excluded family. Stage C still needs a complete protocol, safety/missingness policy and approval after Stage S.

## What Claude should do first

**Finish and review the code locally without running scientific code; there is no runnable server handoff yet.** The ordered completion checklist is in [the incomplete runbook](stage-s/RUNBOOK.md). Complete the two protocols and all code/analysis/driver/setup gaps, test the pure logic, obtain the fresh WP5 review and apply its corrections. Only then release the readiness lock in a committed change. The first later scientific action is the prescribed two-source server rehearsal, with the instance-hour clock and retrieval reserve already running. A rehearsal/resource failure is a stop for repair or a resource NO-GO, not a reason to silently shrink the scientific inventory.

## Remaining TIFS submission gap and user decisions

- No positive F6 result exists. Stage S can kill the direction; it cannot establish a publication claim. Stage C requires new approval and fresh data after a successful screen.
- Strong external presence baselines remain necessary. Their presence endpoint cannot be presented as interchangeable with content binding; comparable endpoints, distortion and side information must be explicit.
- T4/T5 evaluation remains limited. Original/marked pair access for residual transfer is a separate stronger-access scenario, and acceptance of a real copied patch differs from false attribution of the entire recipient. Human near-duplicate labels and human quality ratings remain missing.
- Novelty checks, accessible final journal versions, threat scope, source diversity, bounded specificity and an honest manuscript/figure package are still needed. Standard distortions remain an article-only secondary family and cannot select the primary contribution.
- The later decisions are whether to fund completion/rehearsal, whether to grant SD3.5 access and disk capacity, and—only after evidence—whether to approve Stage C. No licence, spending, publication or held-out-run approval was inferred today.

## Validation and deadline accounting

Allowed validation was syntax compilation and standard-library pure-logic work only. At 20:20 UTC, syntax compilation passed for all nine new `scripts/tifs_*.py` files, including the final readiness lock. The power module's six tests and identifier module's seven tests passed in their bounded checks. Five non-filesystem common tests passed; five filesystem-dependent common tests remained unverified after temporary-directory permission failures. No clean full-suite pass or runtime integration pass is claimed. Writer gradients, memory, timing, models, image quality and survival were not executed or measured.

The desktop session began at 13:56:06.7876054 UTC and its six-hour deadline was 19:56:06.7876054 UTC. A required approval for writing Git metadata outside the worktree remained pending from approximately 15:33 UTC until the identifier commit completed at 20:13:35 UTC. Bounded subagents completed draft files during that interval, but the root did not complete integration, WP5 or the planned pre-deadline wrap-up. The next clock check at 20:14 UTC exposed the overrun. Subsequent work was restricted to truthful partial closure, preservation, the readiness lock and state/report updates. This is elapsed-time accounting, not six hours of active science and not a claim that all work packages were completed.

No local marking, regeneration, attacks, detection, metrics, model passes, training, timing rehearsal, asset downloads, package installation, SSH or paid compute occurred. Existing protected results and scientific files were not edited. Unfinished source is retained so a later explicitly resumed session can complete it without losing the work.
