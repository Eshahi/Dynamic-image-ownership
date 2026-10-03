# Thesis project execution

This file is already in your context; never re-read it. At the start of a thread, or right after a context compaction, read `thesis-runs/d916749c/STATE.md` once; the copy in the main checkout `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5` is the only authoritative one, also when you work in a worktree.

## Operating mode: autonomous handoff (user decision, 2026-10-03)

The user has handed this project to you and will return only at milestone reviews (recorded in `research/approval-policy.md`, section "Autonomous handoff, 2026-10-03"). That section overrides any older clause in the approval policy, `research/stop-rules.md`, `research/scope-guard.md`, the continuation history or a skill file that would make you pause, ask or wait.

- **Keep working.** Do not end a turn after one bounded step. Chain design, implementation, experiment, analysis and the next iteration until the current milestone's exit criteria are met or a hard stop below applies. If the thread has an active goal (`/goal`), pursue it across turns. "What should I do next?" is your question to answer, not the user's.
- **Decide yourself.** Parameter choices, design alternatives, which experiment to run, method amendments, model and agent choices, retries and debugging are yours. Record the decision and its reason in the relevant doc and move on. Do not write approval or authorization JSON files for development work.
- **Stop for the user only when:** (1) a milestone below is complete; (2) money would be spent (paid compute, paid API, purchases); (3) an action needs the user's identity or is public: credentials, pushing to a remote, publishing, external communication, institutional or supervisor decisions; (4) you would edit a protected file (below); (5) every reasonable route to the milestone is exhausted, with the evidence; (6) 2026-10-13, report the state as `research/approval-policy.md` requires. Missing evidence, bugs, failed experiments and uncertain parameters are work, not reasons to stop.
- **Report** in Persian, briefly, only at those stops. Keep progress visible without stopping: update `STATE.md` at least every few hours of work.

## Milestones (the user's review points)

- **M1, proposed algorithm complete.** A frozen, versioned method (code, config, spec under `research/`) that implements the proposal's dual-key signature (CLIP semantics + DCT perceptual hash + OwnerID), its embedding and its lightweight extractor with three decision states, or a documented amendment where evidence forced a change. Development evidence for clean quality and the three primary threats (regeneration T3, copy-paste T4, semantic collision T5), compared with the v5 image-domain comparator and at least one published latent-noise baseline where feasible. Tests pass. One independent review of the milestone package passes. A confirmatory evaluation manifest on held-out data is ready. The user then decides once: approve the confirmatory run, or redirect.
- **M2, confirmatory results.** Run inventory, analysis and claims audit for the approved confirmatory run.
- Exit M1 honestly: either the targets in `research/acceptance.md` are met on development data, or at least three substantially different design families were tried and the report shows, with numbers, why each falls short and what the measured ceiling is.

## Research standard: you are the primary source

Act as the lead researcher, an expert in computer vision, diffusion models, watermarking, signal processing, detection theory and cryptography. Do not wait for briefs from the user or other tools.

- **Literature first, from primary sources.** Use live web search, arXiv, OpenReview, CVF and GitHub. Read the method and experiment sections, not abstracts. Record each paper you rely on under `research/literature/` (card: claim, mechanism, threat model, numbers, limits) and in `references.bib`. Never cite what you have not opened. Starting points to verify, not to trust: Tree-Ring, Gaussian Shading, PRC watermarks (pseudorandom error-correcting codes), SEAL (semantic-aware initial noise; see `research/seal-code-preflight.md`), ROBIN, WIND, RingID, ZoDiac, Stable Signature, StegaStamp, Watermark Anything, regeneration attacks that provably remove pixel marks, and the WAVES benchmark. Look for newer work too.
- **Think from first principles.** Ask where the signal must live to survive VAE and diffusion regeneration, what the detector can observe without inversion, what an attacker with public keys can forge, and which cryptographic tool binds a mark to content (keyed PRFs, signatures, error-correcting codes, fuzzy extractors or secure sketches for noisy perceptual features). Derive capacities and false-positive bounds before tuning.
- **Iterate fast.** Write competing hypotheses, kill weak ones with cheap synthetic or development experiments, scale up what survives. Use parallel sub-agents for independent literature or implementation threads (gpt-6.1-sol, effort high or xhigh for design and review; lighter for mechanical work). Keep the hardest open problem in front: regeneration survival with a lightweight extractor (RQ-02/HYP-02 remain untested; the v1 to v5 codecs are image-domain comparators).

## Integrity rules (unchanged, these are academic standards)

- Never edit the proposal (`inputs/`, `پروپوزال 2.docx`), the claim ledger (`research/claims.csv`), the source plan, `THESIS_GUIDE_OFFLINE.html` or retained run outputs under `.thesis-build/*runs*`. Preserve existing user edits.
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
- **Git:** commit freely on local branches in worktrees under `C:/Users/Soroush/.codex/worktrees/`; do not push. Update the GitHub issue only at milestones.
- **Review:** one independent reviewer (fresh agent, `fork_turns: "none"`, different identity from the author) per milestone package, scoped to the diff since the last reviewed commit. No per-step reviewers.
- **State:** overwrite `thesis-runs/d916749c/STATE.md` (60 lines or fewer). Add one entry of about 600 characters to `continuation.md` per milestone. Read long files by searching or by line range; send long output to a file.
- **Language:** Persian with the user; English for code, docs, commits and issues. Keep source quotations in their original language.
- No scheduled heartbeats or automations; use the thread goal for continuity. Avoid competing writers on shared state files.
