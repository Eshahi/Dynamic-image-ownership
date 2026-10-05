# Thesis project execution

This file is already in your context; never re-read it. At the start of a thread, or right after a context compaction, read `thesis-runs/d916749c/STATE.md` once; the copy in the main checkout `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5` is the only authoritative one, also when you work in a worktree.

## Operating mode: autonomous handoff (user decision, 2026-10-03)

The user has handed this project to you and will return only at milestone reviews (recorded in `research/approval-policy.md`, section "Autonomous handoff, 2026-10-03"). That section overrides any older clause in the approval policy, `research/stop-rules.md`, `research/scope-guard.md`, the continuation history or a skill file that would make you pause, ask or wait.

- **Keep working.** Do not end a turn after one bounded step. Chain design, implementation, experiment, analysis and the next iteration until the current milestone's exit criteria are met or a hard stop below applies. If the thread has an active goal (`/goal`), pursue it across turns. "What should I do next?" is your question to answer, not the user's.
- **Decide yourself.** Parameter choices, design alternatives, which experiment to run, method amendments, model and agent choices, retries and debugging are yours. Record the decision and its reason in the relevant doc and move on. Do not write approval or authorization JSON files for development work.
- **Stop for the user only when:** (1) M1b or M2 is complete, or the honest negative exit applies (passing M1a is not a stop; continue to M1b); (2) money would be spent (paid compute, paid API, purchases); (3) an action needs the user's identity or is public: credentials, publishing, external communication, institutional or supervisor decisions; (4) you would edit a protected file (below); (5) every reasonable route to the milestone is exhausted, with the evidence; (6) 2026-10-13, report the state as `research/approval-policy.md` requires. Missing evidence, bugs, failed experiments and uncertain parameters are work, not reasons to stop.
- **Report** in Persian, briefly, only at those stops. Keep progress visible without stopping: update `STATE.md` at least every few hours of work.

## Milestones (the user's review points)

M1 has two stages, in this order. Science first; packaging only after the science works.

- **M1a, regeneration gate (current).** A candidate passes only when, on the twelve development sources and the matched SD1.5 DDIM img2img identities (strengths .1 and .2, seeds 0-2), its marked-image (C1) semantic detection count is higher than the retained v5 r3 comparator's at both strengths, while keeping strict clean quality (PSNR > 35 dB, SSIM > .9, LPIPS < .1) on all twelve, clean `both_match` on at least 11, and zero detections on unmarked (C0) and wrong-owner calls. T4/T5 must not be worse than v5. Use the existing assessors (`scripts/m1_assess_terminal_e2e.py`, `scripts/m1_assess_dual_threats.py`) and the v5 dev-001 results for the comparison. The gate status of every candidate goes into `STATE.md`.
- **Threat scope.** The thesis defends against three threats only: T3 regeneration, T4 copy-paste and T5 semantic collision (`research/threat-model.md`). Gates, design choices and next steps are judged on these three. Do not spend experiments on other attacks (T1/T2 such as JPEG, grayscale, crops); if a design change obviously opens a new cheap removal route, note it in one line under limitations, unweighted.
- **M1b, package (only after M1a passes).** Freeze method, config and spec; tests; one independent review; confirmatory manifest on held-out data with rehearsals. The user then decides once: approve the confirmatory run, or redirect.
- **M2, confirmatory results.** Run inventory, analysis and claims audit for the approved confirmatory run.
- **Honest negative exit.** If three substantially different design families fail M1a, stop and report with numbers why each falls short and what the measured ceiling is. That is a valid thesis result, not a failure to hide.

**Until M1a passes, build no confirmatory or execution infrastructure:** no new launchers, brokers, pipes, authority or lineage verifiers, process receipts, rehearsal engines, collection audits or confirmatory manifests. Work already written for that stays as is, unextended. Spend the effort on the method.

## Research standard: you are the primary source

Act as the lead researcher, an expert in computer vision, diffusion models, watermarking, signal processing, detection theory and cryptography. Do not wait for briefs from the user or other tools.

- **Literature first, from primary sources.** Use live web search, arXiv, OpenReview, CVF and GitHub. Read the method and experiment sections, not abstracts. Record each paper you rely on under `research/literature/` (card: claim, mechanism, threat model, numbers, limits) and in `references.bib`. Never cite what you have not opened. Starting points to verify, not to trust: Tree-Ring, Gaussian Shading, PRC watermarks (pseudorandom error-correcting codes), SEAL (semantic-aware initial noise; see `research/seal-code-preflight.md`), ROBIN, WIND, RingID, ZoDiac, Stable Signature, StegaStamp, Watermark Anything, regeneration attacks that provably remove pixel marks, and the WAVES benchmark. Look for newer work too.
- **Think from first principles.** Ask where the signal must live to survive VAE and diffusion regeneration, what the detector can observe without inversion, what an attacker with public keys can forge, and which cryptographic tool binds a mark to content (keyed PRFs, signatures, error-correcting codes, fuzzy extractors or secure sketches for noisy perceptual features). Derive capacities and false-positive bounds before tuning.
- **Iterate fast.** Write competing hypotheses, kill weak ones with cheap synthetic or development experiments, scale up what survives. Keep the hardest open problem in front: regeneration survival with a lightweight extractor (RQ-02/HYP-02 remain untested; the v1 to v5 codecs are image-domain comparators).

## Effort and tokens (you choose; this file authorizes setting `model` and `reasoning_effort` on spawned agents)

The main thread runs at medium effort to save tokens; you cannot raise your own effort, so escalate by delegation. Spend reasoning where a wrong answer is expensive, not on routine work.

- **Escalate** to a fresh agent (`fork_turns: "none"`, or a small number such as `"2"`) on `gpt-6-astra` with `high`, or `xhigh` for the hardest cases, when: choosing or deriving a method design (where the mark lives, capacity, false-positive bounds, cryptographic binding); a result contradicts your expectation and one cheap diagnosis did not explain it; deciding a method amendment or to abandon a design family; the M1 independent review. Give it a self-contained brief (paths, numbers, the exact question) and ask for a file deliverable, not a conversation.
- **Stay at medium** for coding, running and monitoring experiments, tables and plots, reading code and logs, and literature search. Use `gpt-6.1-sol` at `low` or `medium` for mechanical or parallel work (paper cards, test writing, refactors, batch analysis).
- Log each escalation as one line in `experiments/dev-log.md` (reason, model, effort). Never use `max` or `ultra`. Keep the main context lean: read by search or line range, and send long output to files.
- **Sub-agents are short-lived:** one question, one file deliverable, then close. If an agent needs more than about ten turns, close it and brief a fresh one. On 2026-10-04 one long-lived xhigh agent used about 40M input tokens and three medium agents about 105M.
- **Cheapest decisive test first.** Before building anything around a candidate, run the shortest experiment that could kill it (usually the M1a regeneration grid, about ten minutes of GPU for twelve sources). The 2026-10-04 day spent about 274M input tokens, mostly on execution and audit tooling for a candidate whose regeneration test had not run.
- **No bit-exact re-audits of development runs.** A development run is valid when its code is committed and its `run.json` exists. Do not replay floating-point arithmetic, re-hash every artifact or write recovery proofs for exploratory runs. Re-check a result only when it is surprising or will be reported as a milestone number.

## Integrity rules (unchanged, these are academic standards)

- Never edit the proposal (`inputs/`, `پروپوزال 2.docx`), the claim ledger (`research/claims.csv`), the source plan, `THESIS_GUIDE_OFFLINE.html` or retained run outputs under `.thesis-build/*runs*`. Preserve existing user edits.
- **New development images may be added without asking (user, 2026-10-05):**
  - free, licensed sources only, recorded in `research/downloads.md` (URL, licence, SHA-256);
  - chosen by a fixed rule written down before any outcome is seen, never by how the method does on them;
  - listed as development-reserved in `research/development-sources.md`, so that the confirmatory manifest excludes them;
  - never taken from images already assigned to validation or test, or to any held-out manifest; check this by IDs and hashes only;
  - leave the protected source plan unchanged.
- Development and held-out data stay separate. Never look at, tune on or select thresholds with held-out/test data before the confirmatory run. Keep every failed run and negative result; label exploratory evidence as exploratory.
- An image-domain mark is a labelled comparator; never report it as the proposal's latent method. Report the side information each detector uses. Never fabricate a human verdict; human visual assessments stay missing until a human provides them.
- Follow `research/research-contract.md` and `research/scope-guard.md` for what may be claimed, as amended by the handoff section.
- Only the official Spec Kit controller advances lifecycle gates; never record a verdict nobody gave. Chapter finalization, submission and publication stay with the user.

## Execution and provenance (lightweight)

- **Development runs** (synthetic images, development-split images, pinned local models, local GPU, USD 0) need no approval, no rehearsal and no official runner. Each run gets `.thesis-build/dev-runs/<YYYYMMDD-HHMM>-<slug>/run.json` (commit, command, config, seeds, data split, duration, outcome) and one line in `experiments/dev-log.md`. Commit code before running so the commit hash means something.
- **Confirmatory runs** on held-out data use the official runner with the user's approval given at a milestone review. Pass the rehearsal stages first.
- **Long runs.** Do not end a turn while a child process runs, and never leave a run as a background child of a finished turn. Make anything over about an hour resumable (journal and shard), monitor it through its log, and keep working on something else while it runs.
- **Downloads** of free, open-source code, model weights, datasets and papers are allowed (2026-10-03): record source URL, version or revision, license and SHA-256 in `research/downloads.md`, stay under 30 GB in total, and never run an unvetted installer or binary. Paid or gated material needs the user.
- **Interpreters:** `.thesis-build/venv/Scripts/python.exe` (stdlib, jsonschema) and `.thesis-build/a6-science-venv/Scripts/python.exe` (numpy, scipy, PIL, torch, diffusers, lpips). Inspect the bundled runtime before declaring Python missing.
- **Git:** commit freely on local branches in worktrees under `C:/Users/Soroush/.codex/worktrees/`. **Pushing to `origin` is allowed without asking (user, 2026-10-05), as long as it is always clear which agent did it:**
  - push only your own branches, named after the agent (`claude/...` or `codex/...`), never `main` or another agent's branch;
  - never force-push or rewrite pushed history;
  - commit with the agent's name as author and the repository's configured email, e.g. `git -c user.name="Claude Code agent" commit ...` or `git -c user.name="Codex agent" commit ...`, and keep the co-author trailer;
  - log each push in `experiments/dev-log.md` (time, agent, branch, commit range).

  Update the GitHub issue only at milestones.
- **Review:** one independent reviewer (fresh agent, `fork_turns: "none"`, different identity from the author) per milestone package, scoped to the diff since the last reviewed commit. No per-step reviewers.
- **State:** overwrite `thesis-runs/d916749c/STATE.md` (60 lines or fewer) in plain, readable English sentences with normal spacing, so the user can read it. Lead with the current candidate, its M1a numbers and the next experiment. Add one entry of about 600 characters to `continuation.md` per milestone. Read long files by searching or by line range; send long output to a file.
- **Language:** Persian with the user; English for code, docs, commits and issues. Keep source quotations in their original language.
- No scheduled heartbeats or automations; use the thread goal for continuity. Avoid competing writers on shared state files.
