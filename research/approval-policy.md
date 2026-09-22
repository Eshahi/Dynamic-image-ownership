# Approval and continuation policy

Effective 2026-09-22, from the user's instruction in authenticated task `01a0b9bd-fd47-7cf1-8123-ff77a4ca9dd8`: continue the project, check the milestones, and request the user's approval only where genuinely needed. This project-specific delegation supersedes the earlier scope-only limit for routine technical reviews. It does not grant university authority, unrestricted spending, publication authority, or permission to bypass tool/security boundaries.

## Milestones versus gates

The reviewed `thesis-38` plan contains 38 tasks mapped to all 58 original tasks. It has five milestones: Specification (7 tasks), Data & Literature (6), Implementation (11), Evaluation & Statistics (9), and First Review (5). Milestone acceptance checks remain mandatory, but completing a milestone does not itself require a new user message.

Spec Kit separately has seven lifecycle gates. Keep their evidence checks and state transitions; use the following decision authority rather than treating every gate as a user interruption.

| Gate | Decision authority | Required basis |
| --- | --- | --- |
| Scope acceptance | Existing delegated decision is recorded. Ask the user only for a material new departure. | Original proposal, current scope, conflict list, and feasibility constraints. |
| Evidence review | Delegated technical acceptance after independent review. | Inspected sources, verified metadata/artifact hashes, claim support and contradictions; absent evidence blocks acceptance. |
| Plan acceptance | Delegated technical acceptance within approved scope and resource limits. | Reviewed preregistration, controls, splits, uncertainty and workload estimate. Resource execution approval remains separate. |
| Compute approval | User approves the concrete scientific execution package and any paid/remote budget. | Exact manifest, target, hashes, duration and ceiling. Batch approval may cover its listed runs; no repeated question for each already-covered seed. |
| Results acceptance | Delegated technical acceptance after independent review. | Complete run inventory, failures, reproducible analysis, and documented deviations. Negative results can pass an honest completeness review. |
| Claims acceptance | Delegated technical acceptance after independent evidence audit. | Exact claim/artifact versions; no blocking audit findings or unsupported generalization. No publication or academic certification is implied. |
| Chapter finalization | User. | Concrete final draft, claims, citations, audit and required institutional checks. |

For delegated decisions, record the actual agent identity, this delegation source, exact run/step, current state hash, timestamps, and review artifact references. Never claim that the user typed a verdict they did not type. If a runtime cannot represent the delegated authority honestly, leave that transition pending, report the specific incompatibility, and continue independent authorized work. Do not weaken the validator to manufacture approval.

## Interrupt the user only for a concrete decision

- A material departure from the approved method or research questions, final dataset commitments, or deadline after evidence shows it necessary.
- A ready-to-execute scientific compute manifest requiring the existing runner's approval; paid rental, paid APIs, or a resource ceiling increase. Routine unit tests, mock runs, and document validation do not require repeated approval.
- Credentials/access, restricted/private materials, institutional choices, or an external communication/public submission requiring the user's authority. Never post credentials or upload the private proposal to an external research service by inference.
- Final thesis acceptance, submission, or publication.

Missing evidence, bugs, uncertain parameters, and unfinished task outputs are work to resolve, not automatic approval questions. Ask only if safe in-scope alternatives have been exhausted or the remaining choice belongs to the user. Group related decisions into one concrete package. Continue unrelated ready tasks when one branch is blocked.

## Scope correction from the milestone audit

The immutable plan's Specification checks and A2b scope guard explicitly exclude automatic ownership-transfer/ledger implementation. The earlier delegated scope document made a trusted-registry transfer demo mandatory, creating an avoidable conflict and extra work. Supersede that implementation requirement: no registry/transfer system is required for the three-week system delivery. Retain the proposal's narrative dynamic-ownership requirement as an unresolved institutional/research-scope issue, not an implemented feature or silently deleted commitment. The later research contract must state this limitation; obtain user/supervisor direction if resolving it would materially change the research claim or require implementation.

The original `scope-execution-decision.md` and its hash-bound approval are preserved as historical records. All other constraints remain, including four research questions, source dataset commitments, early latent-to-DCT feasibility checks, and the three-week runnable-system target. In the calendar, replace the mandatory transfer demo with enrollment/owner-verification controls.

## Continued execution and notifications

Continue within this Codex task using one scheduled heartbeat. Inspect Git state, live processes, dependency readiness, and actual artifacts before selecting work. Finish and verify the next bounded task; record English GitHub progress. Do not start a duplicate writer while an existing agent or experiment is active.

Notify the user in Persian only on a meaningful milestone, a material failure/forecast change, completion, or a necessary decision. Routine unchanged status should stay quiet. A pending user decision does not authorize itself with time; keep its dependent branch paused while progressing other eligible work. The computer and app must be available for local scheduled work.

When the system milestone is achieved, or the target date 2026-10-13 is reached, report the actual state and remaining experiments/writing work. Do not automatically broaden the scope beyond that handoff. The heartbeat should take no further substantive action after that completion/deadline report unless the user directs continuation.
