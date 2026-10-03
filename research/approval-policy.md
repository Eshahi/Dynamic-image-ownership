# Approval and continuation policy

Effective 2026-09-22, from the user's instruction in authenticated task `01a0b9bd-fd47-7cf1-8123-ff77a4ca9dd8`: continue the project, check the milestones, and request the user's approval only where genuinely needed. This project-specific delegation supersedes the earlier scope-only limit for routine technical reviews. It does not grant university authority, unrestricted spending, publication authority, or permission to bypass tool/security boundaries.

## Model-selection delegation, 2026-09-30

The authenticated user explicitly authorized autonomous model selection in the agent's authority and plan for all thesis tasks. The agent may choose an available assistant/reviewer model and supported reasoning effort according to task complexity, risk, modality, latency and resource efficiency without asking for each choice. Later explicit user model choices take precedence. Use only models and controls actually exposed by the environment; this does not imply the ability to switch the running parent chat's model. Apply model choices to delegated subtasks where supported and otherwise authorized. Model-selection permission alone does not authorize spawning agents, starting paused tasks or creating new chats.

Use proportionate capabilities: lightweight models for bounded mechanical work; stronger reasoning for scientific design, difficult implementation and synthesis; a different reviewer identity for required independent reviews. Record actual model/effort when exposed, role and a short rationale for substantive delegated work. Never invent an unavailable model identity or substitute model strength for verification.

For models inside the research algorithm or comparators, candidate inspection and recommendation are permitted within existing scope. Adoption retains checkpoint/runtime/rights provenance and the experiment contract. This delegation does not authorize downloads/installs, paid APIs/remote compute, budget increases, private-data uploads, security bypasses, material method/scope changes, scientific execution without exact runner authorization, publication or final acceptance. Existing gates and user pauses remain binding.

Apply this rule across all 38 tasks through `research/model-selection-plan-addendum-20260930.md`, preserving the original hash-bound plan and dependency graph.

## Milestones versus gates

The reviewed `thesis-38` plan contains 38 tasks mapped to all 58 original tasks. It has five milestones: Specification (7 tasks), Data & Literature (6), Implementation (11), Evaluation & Statistics (9), and First Review (5). Milestone acceptance checks remain mandatory, but completing a milestone does not itself require a new user message.

Spec Kit separately has seven lifecycle gates. Keep their evidence checks and state transitions; use the following decision authority rather than treating every gate as a user interruption.

| Gate | Decision authority | Required basis |
| --- | --- | --- |
| Scope acceptance | Existing delegated decision is recorded. Ask the user only for a material new departure. | Original proposal, current scope, conflict list, and feasibility constraints. |
| Evidence review | Delegated technical acceptance after independent review. | Inspected sources, verified metadata/artifact hashes, claim support and contradictions; absent evidence blocks acceptance. |
| Plan acceptance | Delegated technical acceptance within approved scope and resource limits. | Reviewed preregistration, controls, splits, uncertainty and workload estimate. Resource execution approval remains separate. |
| Compute approval | User approves the concrete scientific execution package and any paid/remote budget. | Exact manifest, target, hashes, duration and ceiling. Batch approval may cover its listed runs; no repeated question for each already-covered seed. Amended 2026-10-02: see "Rehearsal tier and infrastructure-only reruns" below. |
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

Continue when the user sends a message; there is no scheduled heartbeat and none may be created. Inspect Git state, live processes, dependency readiness, and actual artifacts before selecting work. Finish and verify the next bounded task; record English GitHub progress. Do not start a duplicate writer while an existing agent or experiment is active.

Notify the user in Persian only on a meaningful milestone, a material failure/forecast change, completion, or a necessary decision. Routine unchanged status should stay quiet. A pending user decision does not authorize itself with time; keep its dependent branch paused while progressing other eligible work.

When the system milestone is achieved, or the target date 2026-10-13 is reached, report the actual state and remaining experiments/writing work. Do not automatically broaden the scope beyond that handoff. Take no further substantive action after that completion/deadline report unless the user directs continuation.

## Rehearsal tier and infrastructure-only reruns, 2026-10-02

Decided by the user on 2026-10-02 after three harness failures each consumed an approval. This section amends the "Compute approval" row above; every other gate is unchanged. The official runner, its approval check and the approval schema are not modified, and every execution still carries a runner approval bound to its exact manifest hash, so `research/scope-guard.md` remains satisfied.

**Rehearsal tier.** A rehearsal runs the identical launcher, worker, journal, guard and heartbeat end to end on generated synthetic images. It may hash the pinned weight files and load the pinned local CLIP and LPIPS models. It reads no study image, writes only under `.thesis-build/rehearsal/`, marks every output as synthetic, produces no scientific evidence, and needs no user approval or independent review. A scientific package may be presented to the user only after every rehearsal stage has passed at the same clean commit.

**Scientific core.** The scientific core of a package is the hash computed by its prepare script over the profile and configuration, detector and metric code, input and parent hashes, schedule, seeds, datasets, metrics, acceptance criteria, execution settings, target, and resource and budget ceilings. Files outside the core are harness and are listed in the package's hashed core definition.

**Infrastructure-only rerun allowance.** The approval question put to the user shows the manifest hash, the scientific-core hash and the words "up to 2 infrastructure-only reruns"; the transcribed approval records all three, so the user's typed reply covers them. A rerun is covered only when all of the following hold:

1. its scientific-core hash equals the approved one;
2. every path changed since the approved commit is in the approved harness list;
3. the previous attempt did not complete, and its evidence is preserved and not reused;
4. the previous failure was not raised by scientific validation (a changed input, a non-finite metric, a roster or geometry mismatch are not infrastructure failures);
5. a reviewer with a different identity from the author confirms items 1 to 4 from the prepare script's rerun check and the retained failure record;
6. resource and budget ceilings and the approval expiry are unchanged, and no more than two reruns have used this core hash.

The rerun approval file names its actor as `delegated:<agent identity> under user standing decision 2026-10-02`, never as the user, and its source reference cites the original approval digest, the scientific-core hash, the rerun ordinal, the review receipt and the rerun-check output. Anything that fails a condition needs a new decision from the user.

**Launch.** The user starts scientific runs from their own terminal through the official runner. Agents prepare, review and monitor; they do not leave a scientific run as a background process of a finished turn.

## Autonomous handoff, 2026-10-03

**Source.** The user's message in Claude Code session `306009c7-f156-43a4-a6a7-e543c6058349` on 2026-10-03, transcribed verbatim by Claude (Anthropic), not by the user:

> من احساس میکنم که کدکس خیلی کند پیش میره و همش منتظر تایید من میمونه. حقیقت اینه من درگیر پروژه های دیگه ای هستم و نیاز دارم که این مورد رو کاملا handoff کنم به کدکس و فقط در پایان مراحل مهم، مثلا تکمیل الگوریتم پیشنهادی، بیام و اونو بررسی کنم و این بررسی ها الان خیلی خیلی زیاده. حس میکنم کدکس خنگ شده و از تمام قابلیت هاش در زمینه computer vision و رمزنگاری و ریسرچ استفاده نمیکنه. میخوام که منبع اصلی خودش باشه. ببین چه تغییراتی میتونی بدی تا ایده آلی که من دنبالشم بهش نزدیک بشیم.

English translation: "I feel Codex moves very slowly and keeps waiting for my approval. I am busy with other projects and need to hand this over to Codex completely, coming back only at the end of important stages, for example completion of the proposed algorithm, to review it; these reviews are far too many now. Codex seems to have become dumb and does not use its full capabilities in computer vision, cryptography and research. I want it to be its own primary source. See what changes you can make to bring us closer to this ideal."

In the same session the user chose, from offered options: downloads of free open-source code, model weights and papers are allowed with a size cap and license record; quality is preferred over token cost (main model at the highest practical reasoning effort, larger context before compaction).

**Effect.** This section supersedes every contrary clause above, in `research/stop-rules.md`, `research/scope-guard.md`, `research/proposal-aligned-plan-20260930.md`, the continuation history and skill files, for the remainder of the project unless the user changes it. `AGENTS.md` carries the operating rules.

1. **Continuation.** The handoff is a standing instruction to keep working. Agents continue across turns (a thread goal set with `/goal` is the mechanism) until a milestone is complete or a hard stop applies. "Continue when the user sends a message" and "finish the next bounded task" no longer limit a turn.
2. **Milestones are the review points.** M1 (proposed algorithm complete) and M2 (confirmatory results), as defined in `AGENTS.md`, plus the 2026-10-13 report above. Everything between milestones is delegated, including design choices, method amendments, experiments, retries, model and agent selection.
3. **Development compute is delegated.** Experiments on synthetic or development-split data with local hardware and USD 0 need no approval, no rehearsal, no official runner and no per-run review. The 45-minute ceiling of 2026-10-03 applied to the official runner package and does not limit development runs; runs over about an hour must be resumable. Provenance is the lightweight run record in `AGENTS.md`. Development results are exploratory evidence only.
4. **Confirmatory compute** on held-out data keeps the "Compute approval" row: the user approves the exact package at a milestone review; the rehearsal tier and infrastructure-only rerun allowance of 2026-10-02 still apply to it.
5. **Method amendments** no longer pause work. Record each one (source requirement, evidence, the alternative, effect on questions, data and claims) in a method amendment document and continue; the user reviews adoption at M1. Research questions and hypotheses are never deleted or relabelled; contradicted hypotheses are reported as contradicted.
6. **Independent review** is required once per milestone package, not per step or per package of development work.
7. **Downloads.** Free, open-source code, model weights, datasets and papers from their official sources (GitHub, Hugging Face, arXiv, project pages) are allowed. Record URL, revision, license and SHA-256 in `research/downloads.md`; total under 30 GB; no unvetted installers or binaries; gated, paid or license-incompatible material needs the user.
8. **GitHub** progress is recorded at milestones only.

Not granted: paid compute, paid APIs or purchases; pushing, publishing or any external communication; credentials; edits to the proposal, claim ledger, source plan, `THESIS_GUIDE_OFFLINE.html` or retained run outputs; use of held-out data before the confirmatory approval; fabricated human verdicts or Spec Kit transitions; chapter finalization, submission or publication acceptance.
