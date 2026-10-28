# Toward an IEEE TIFS article: research, creative design and server-ready code (Codex session brief, 2026-10-28)

Written by Claude (Opus 5.5) at the user's request. The user asked, verbatim:

> I have a full 100% session of codex pro 5x. Could you use it for the making the thesis acceptable for the TIFS journal? The research and experiment and also creativity. Then we run the code on vast ai with your observation. If you find it is possible or not.

**Desktop mode (2026-10-28 05:10).** The user moved the session to a Codex desktop thread with `/goal`. Claude stopped the CLI supervisor at 05:10, after WP0 (`ebd4465`, pushed) and part of WP1. There is no supervisor in this mode:
- **Deadline.** Run `Get-Date` first. The deadline is that time plus 6 hours, unless the goal says otherwise. Rewrite the deadline at the top of `PROGRESS.md`; the table's old times belong to the stopped CLI run.
- **Pace.** Check the clock at the start of every package. Keep the split of section 2, scaled to the time left.
- **Wrap-up.** Do WP6 when less than 40 minutes remain.
- **Where to resume.** Claude's commit `333b413` (the standard-distortion decision) is not pushed yet. The CLI turns left uncommitted WP1 work: `PROGRESS.md`, `02-prior-art-delta.md`, `design/` and `literature/`. Run `git status`, keep and commit what is correct, and continue WP1 from those files.
- **Guard.** A lighter desktop guard may run. It kills the thesis science interpreter, thesis experiment scripts, `vastai`, and SSH that uses the vast key, and it keeps the laptop awake. CUDA is not hidden in this mode, so the rules of section 1 rest on you, and they apply in full.
- **Reasoning effort.** The user chooses the thread's effort in the app; that choice overrides the AGENTS.md effort rules for this thread. Reviewer agents use the brief's settings.

You (Codex) are the lead researcher for this session. (In desktop mode, read the next sentence as "the goal keeps you going until the deadline".) A supervisor script started you, keeps you going until the session deadline and resumes you if a turn ends early. Nobody will answer questions during the run. When something needs the user, record it under "Decisions for the user" in `PROGRESS.md`, state the default you assumed, and continue.

All files of this session go in `research/tifs-20261028/` (here called `TD/`), except server code, which goes in `scripts/` with the prefix `tifs_`. The session deadline is in your first prompt and in every supervisor message; write it at the top of `TD/PROGRESS.md`.

## How Claude reads the request

| The user's phrase | What it means for this session |
|---|---|
| **Acceptable for TIFS** | Find, design and prepare the strongest contribution that an IEEE Transactions on Information Forensics and Security reviewer could accept, derived from this thesis ("Dynamic Image Ownership With Robust Neural Watermarking"). Acceptance cannot be promised; the target is a submission whose central claim is new, security-relevant and confirmed. |
| **Research** | Establish the TIFS bar from recent TIFS papers, update the prior-art map since 2026-10-25, and measure exactly where our evidence falls short. |
| **Creativity** | Generate genuinely new contributions, not another failure table. Use the mechanism evidence we already measured. Kill ideas that prior work pre-empts. |
| **Experiment** | Design a cheap development screen (Stage S) that decides go/no-go, then a confirmatory study (Stage C) on fresh held-out sources, both for a rented GPU. |
| **Then we run the code on vast.ai with your observation** | Write Stage S as complete, server-ready code with a rehearsal mode and a runbook. Claude runs it on vast.ai later and observes; you never run it. |
| **If it is possible or not** | End with an honest feasibility verdict: GO, CONDITIONAL-GO or NO-GO for TIFS, with the evidence, the kill criteria and the cost. NO-GO is a valid, useful outcome. |

## 0. Starting evidence (read these, do not re-derive)

Read MAIN `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/thesis-runs/d916749c/STATE.md` once. Then, in this worktree:
- `research/encoder-transfer-20261019/final-study-20261025/phase-b/PHASE-B-REPORT.md`: the held-out confirmatory result (200 Wikimedia Commons POTD sources, 2026-10-28).
- `.../final-study-20261025/phase-a/PHASE-A-REPORT.md`: the mechanism measurements and why the transfer law failed.
- `.../final-study-20261025/FINAL-REPORT.md`, `venue-fit.md`, `article-drafts/README.md`, `article-drafts/close-prior-art-map.md`, `01-literature-synthesis.md`: the 2026-10-25 research dossier (prior art, venue fit, article frame). Read the literature cards under `.../literature/` only as needed.
- `research/f5-encoder-amplified-latent.md` and `research/threat-model.md`.
- The Q1 dossier on branch `codex/q1-research-20261018` (read with `git show codex/q1-research-20261018:research/q1-dossier-20261018/FINAL-REPORT.md`): its verdict was "not Q1-ready, and writing alone cannot fix it"; DREW (arXiv 2406.02836) and Kazempourradi et al. 2026 (arXiv 2610.04151) pre-empt the registry novelty.

The facts that matter most:

| Fact | Numbers |
|---|---|
| F5 r2 survives its own encoder family (SD1.5 img2img), held-out | source-majority C 186/182/140 of 200 at strength .1/.2/.4 (H2 supported, Holm) |
| F5 r2 does not survive SDXL img2img | 19/200 at .1, 0/200 at .2 and .4 (H1 inconclusive only because .1 is .095 against a .10 bar) |
| Kandinsky 3 img2img .2 | F5 61/200, v5 189, WAM 132, VINE-R 200 |
| Ranking reverses between families | SD1.5 .4: F5 140, v5 28, WAM 7; SDXL .1: F5 19, v5 173, WAM 136 |
| Not explained by more distortion | on 193 of 200 sources SDXL .1 output is closer to the marked input than SD1.5 .2 on LPIPS, PSNR and SSIM, yet F5 is lost (H3 .815, inconclusive against .80) |
| Codec round trips alone keep F5 (development) | SDXL VAE 55/60, MoVQ 55/60 |
| Where SDXL loses it (Phase A, development) | F5's residual is the most amplified encoder direction in SD1.5, SDXL and K3 (1.6-3.1x controls), but SDXL retention drops from .66 after the codec to .08 at noise injection |
| First-order transfer law | falsified: SDXL tangents 8-15x too large and nearly orthogonal (cos .02); the SD1.5-only law underpredicts survival by .10/.22/.52 |
| VINE-R (external, published) | survives in every cell (158-200 of 200; lowest at SD1.5 .4) but has a held-out wrong-message event and no owner/content binding |
| F5 binding (development) | T4 copy-paste false attribution 0/20, T5 semantic collision 0/66; VINE-R and WAM only report message presence |
| Quality | F5 has the largest median LPIPS of the four marks in every cell; clean F5 PSNR 45.1 dB, LPIPS .035; VINE-R clean LPIPS .008; no human study |
| Specificity | F5, v5, WAM: 0 false events observed in held-out Phase B; gates incomplete because of 134 SD1.5 safety blocks |

**Claude's prior view, to test, not to trust.** The present evidence supports a bounded negative-result paper, not a TIFS paper. A TIFS-level contribution probably needs one positive, security-relevant claim confirmed on fresh data, for example: a mechanism-guided writer that keeps content-bound ownership evidence across encoder families, including a family never used in its design; or a general, validated account of regeneration survival that applies to published watermarks, not only to F5. The biggest risks are pre-emption by 2024-2026 work (VINE/W-Bench, WAVES, MarkNull, rinsing, transfer and latent-proxy attacks) and the strength of VINE-R as a baseline.

## 1. Rules

**Nothing runs on this laptop.**
- No image generation, marking, regeneration, attack, detection, metric, encoder pass, training or timing run; no GPU.
- No `.thesis-build/a6-science-venv` and no other interpreter with torch, diffusers, numpy, scipy, PIL, lpips or open_clip.
- No downloads of images, datasets, model weights or code repositories, and no package installs. Reading code online is fine.
- No paid compute, no vast.ai, no `vastai` CLI, no SSH, no purchases. Accept no licence, log in nowhere, use no tokens.

**Allowed.**
- Reading every file in the main checkout and every worktree, including saved result files (`rows.jsonl`, journals, `phase-b-results.json`, `metrics.json`).
- Web search; reading papers, model cards, code and standards online; saving papers (PDF or HTML, at most 3 GB) to MAIN `.thesis-build/cache-tifs/papers/`. Commit cards, not full texts; quotations at most 25 words with a locator.
- Stdlib Python only (`W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe -I`) for analysing saved results, bounds, power and costs, `py_compile` of new code, and unit tests of pure-logic modules (journals, manifests, decision rules, statistics). Keep each run under 15 minutes.
- Writing server code in `scripts/tifs_*.py` and `scripts/tifs_*.sh`, and docs, CSV, JSON and BibTeX in `TD/`.
- Committing and pushing this branch (`git push -u origin codex/tifs-20261028` the first time), and adding a short section to MAIN `thesis-runs/d916749c/STATE.md` at the end.

**Integrity.**
- Do not modify F5 r2, v5 r3, any baseline, frozen threshold, frozen protocol, amendment, report, result file or run folder (`.thesis-build/dev-runs/`). A new method gets a new name (for example F6) and its own spec.
- Never edit the proposal, `research/claims.csv`, the source plan, `THESIS_GUIDE_OFFLINE.html` or retained outputs. Never merge, rebase or check out other branches, and never write into other worktrees.
- **Data.** Development data are the 60 encoder-transfer development sources and their documented spares. The 200 Phase-B sources are consumed by a completed confirmation; using them as development data in Stage S is a decision for the user (default: design Stage S so it works with the 60 alone, and make the 200 an optional, flagged extension). The 40 Phase-B reserve identifiers stay untouched. Stage C needs a fresh held-out pool: write its selection rule and an identifier-only manifest (`NOT_DOWNLOADED`), disjoint by identifier from every earlier pool; hashes are checked later on the server.
- Every Stage S decision rule and every Stage C hypothesis, threshold, n and analysis is fixed in a committed file before any output exists. Nothing is tuned on held-out data.
- **Threat scope (the user's rule, amended for the article on 2026-10-28).** The thesis judges designs on T3 regeneration, T4 copy-paste and T5 semantic collision only (`research/threat-model.md`). That stays unchanged for thesis gates, verdicts and the primary article claim. **For the TIFS article only**, the user decided to add standard-distortion tests. Claude asked whether to add JPEG and crop tests as a cheap secondary article section while the three-threat rule stays for the thesis; the user answered, verbatim, "برای تصمیم :‌اضافه کن" ("for the decision: add them"). Include a small, fixed grid (for example JPEG, resize/crop, Gaussian noise, blur, brightness/contrast, at the strengths that recent TIFS papers and benchmarks such as WAVES or W-Bench use) in the Stage S and Stage C designs and code. Apply it to the clean marked images of every arm, with no diffusion. Report it as a separate secondary family that is fixed in advance. Keep its cost small (target at most about 1-2 instance-hours in Stage C), and never let it steer the choice of the primary contribution.
- An image-domain watermark stays a labelled pixel comparator; never present it as the proposal's latent method (RQ-02/HYP-02 remain open). A candidate that tests RQ-02 directly is welcome if it is the best contribution.

**Compute envelope for designs.** One RTX 4090-class vast.ai instance at about USD .45-.60/h. Stage S at most about 15 instance-hours; Stage C at most about 50. If a design needs more, say so and give the cheaper fallback. The stopped Phase-B instance (76 GB disk) still holds SD1.5, SDXL, Kandinsky 3, WAM and VINE-R assets and the run code; new model families must fit the disk or be planned for a new instance. Gated models (licence acceptance) are user actions: list them.

## 2. Work packages (6 hours)

Check the clock at the start of every package, scale to the time left, commit and push after each. When less than 40 minutes remain, go to WP6.

| Package | Budget | Must deliver |
|---|---|---|
| WP0 start | 15 min | `TD/PROGRESS.md` with the deadline and a package log; the starting evidence read |
| WP1 TIFS bar and gap | 50 min | `TD/01-tifs-bar.md`, `TD/02-prior-art-delta.md` |
| WP2 creative contributions | 80 min | `TD/03-ideas.md`, `TD/04-selection.md` with a hostile review |
| WP3 design | 50 min | `TD/05-stage-s-protocol.md` + `TD/stage-s/frozen-config.json`, `TD/06-stage-c-design.md` |
| WP4 Stage S code | 100 min | `scripts/tifs_*`, tests, `TD/stage-s/RUNBOOK.md` |
| WP5 review | 25 min | `TD/07-review.md`, corrections applied |
| WP6 report | 30 min | `TD/FINAL-REPORT.md`, STATE section, Persian summary |

### WP1: the TIFS bar and the gap
- Inspect at least eight TIFS papers from 2023-2026 on image watermarking, provenance, regeneration robustness or ownership verification (method and experiment sections). Tabulate what each contains: number and kind of baselines, datasets and n, attacks, theory, ablations, quality and user studies, false-positive analysis, code release, page count.
- Write the gap table: each element of that bar against our current evidence (present, partial, missing), with the cost to close it.
- Update the prior-art map from the 2026-10-25 dossier with work published since (arXiv and venues 2025-2026): regeneration-robust watermarks, cross-model or cross-VAE transfer, latent and encoder-aware watermarks, content-bound ownership and soft binding, regeneration attacks. For each close paper say what it pre-empts.

### WP2: creative contributions
- Generate at least 12 distinct candidate contributions across kinds: new method, mechanism or theory, attack, evaluation methodology, ownership protocol. Include at least these seeds and at least six of your own:
  1. A mechanism-guided cross-family writer: keep F5's content binding, but optimise the residual for survival through each regenerator's noise injection (the measured failure point), for example a multi-encoder consensus objective with expectation over injection noise, evaluated on a family never used in design.
  2. Content-bound ownership on a robust carrier: bind owner and content (F5's sketch and owner key) to a carrier that survives regeneration across families, and show that presence-only carriers such as VINE-R do not give ownership under T4/T5.
  3. A method-agnostic, cheap survival predictor (for example latent signal-to-noise at the injection step in the regenerator's own latent space) validated prospectively across published watermarks and families against a quality-only comparator.
  4. The proposal's latent-space method (RQ-02): what the cheapest decisive test would be.
- For each candidate: the claim in one sentence; the three closest prior works and why it is still new; the experiment that would show it; cost in instance-hours; failure modes; a kill criterion; TIFS fit (1-5) and probability of a positive dev result (your honest estimate).
- Deepen the top three with derivations and stdlib back-of-envelope checks on saved data where possible.
- **Hostile review.** Spawn one fresh reviewer agent (gpt-6-astra, reasoning effort xhigh, no prior context) to attack the top three for novelty, feasibility and TIFS fit. Apply its findings, then select one primary contribution (and at most one backup) in `TD/04-selection.md`, with the reasons and what would make you switch.

### WP3: design
- **Stage S (development screen, run by Claude on vast.ai).** Arms, cells (regenerator family x strength), n, seeds, metrics, the comparators that a TIFS reviewer would expect (at least VINE-R and WAM; justify others), and a go/kill decision rule with fixed numbers. It must answer, cheaply, whether the selected contribution can work, including on a family excluded from design if the claim needs one. Include a 2-source rehearsal, the expected run time per stage (from Phase A/B timings in the reports and journals) and a disk estimate.
- **Standard distortions (article-only secondary section, user decision 2026-10-28).** Fix the grid, the endpoints and the reporting family in both stage designs (section 1, threat scope).
- **Stage C (confirmatory, held-out; runs only after the user approves).** Hypotheses with Holm, n and power, the fresh held-out pool and its selection rule, families (including one never used in design), baselines, quality and specificity reporting, safety-block handling (decide in advance whether blocked outputs are retried with a different seed, counted as missing or avoided by a declared prompt policy; never silently bypassed), budget and user actions. Specification only; code is an extension item.

### WP4: Stage S code
- Implement Stage S completely in `scripts/tifs_*.py` plus a driver `scripts/tifs_stage_s_driver.sh`. Reuse the Phase-B infrastructure instead of rewriting it: `scripts/et_final_phase_b.py`, `et_final_phase_b_read.py`, `et_final_phase_b_driver.sh` and the arm codecs they import (journals where the latest row per id wins, resumable stages, detector release in parallel with GPU work, quality metrics, output hashing).
- Server assumptions: Linux, one RTX 4090 (24 GB; plan for 24 GB even though the last instance reported more), CUDA, Python 3.10+, the repo cloned from GitHub on the server. A setup script installs packages and downloads model weights and baseline code on the server only, pinned by revision and hash.
- Include the standard-distortion stage (clean marked images, every arm, the fixed grid) as its own resumable stage with its own tables.
- Must have: `--rehearsal` (2 development sources), per-stage resumability, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, release of model objects between families, safety blocks recorded and never bypassed, a manifest of output hashes, an analysis script that applies the frozen decision rule and writes tables and JSON, and clear log lines that Claude can watch (`STAGE_START`, `STAGE_DONE`, counts, rates).
- Tests: stdlib unit tests for every pure-logic module, and `py_compile` of every new file. Do not execute model code here.
- `TD/stage-s/RUNBOOK.md` for Claude: setup commands, rehearsal, full run, expected durations, what to check at each checkpoint, what to fetch, and how to stop safely.

### WP5: review
- Spawn one fresh reviewer agent (gpt-6-astra, xhigh) on the Stage S protocol and code: correctness against the protocol, leakage of held-out data, decision rules fixed before outputs, failure handling, server pitfalls from the Phase A/B reports, and rule compliance. Apply the corrections and record dispositions in `TD/07-review.md`.

### WP6: final report
- `TD/FINAL-REPORT.md`. First line `STATUS: COMPLETE` (or `STATUS: PARTIAL` followed by the missing packages). Second line `FEASIBILITY: GO`, `FEASIBILITY: CONDITIONAL-GO` or `FEASIBILITY: NO-GO`. Then: the selected contribution and why; what Stage S must show for GO; costs and time; the remaining gap to a TIFS submission (manuscript, baselines, user study, threat-scope question); decisions for the user; what Claude should run first.
- Add a section of at most eight lines to MAIN `thesis-runs/d916749c/STATE.md` (headed "TIFS session (Codex, 2026-10-28)"), commit, push.
- End with a short Persian summary for the user.

### Extension tier (only if FINAL-REPORT.md is complete before the deadline)
- E1: Stage C code, with tests and a runbook.
- E2: a TIFS manuscript skeleton in `TD/manuscript/`: section plan, contribution statements conditional on Stage S/C outcomes, figure and table list, page budget.
- E3: second-ranked contribution worked out to a Stage S design.
