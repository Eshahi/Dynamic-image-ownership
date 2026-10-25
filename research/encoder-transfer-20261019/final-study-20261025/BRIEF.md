# Encoder-transfer final study: deep research and a stronger final experiment (Codex session brief, 2026-10-25)

Written by Claude (Opus 5.5) at the user's request. The user asked, verbatim:

> I have a pro 5x 100 codex session. Can you use it to strengthen the final expriment and add more deep analysis, also intelligence to it? I want you to plan it and start it.

and then, verbatim:

> I don't want the run on my local. I want a real deep resarch

**Update, 2026-10-25 04:58: the session is at most 6 hours.** The user asked, verbatim, "Could you do it in at most 6 hours?". The deadline is 10:49 local time (UTC-8), 6 hours after the 04:49 start; the hard stop is 30 minutes later. This plan replaces the 12-hour split in section 3: keep the order, compress each package, and do the work in full.

| Package | Budget | Minimum that must be done |
|---|---|---|
| WP0 | done | — |
| WP1 literature | 1 h 30 min | at least 20 V2 cards across clusters 1–3, the synthesis and the positioning (clusters 4–5 may be V1 notes) |
| WP2 mechanism | 1 h 30 min | the derivation, the hypotheses committed first, the stdlib reading of `rows.jsonl`, and the transfer law with fixed predictions |
| WP3 attacks | 20 min | one to two attacks specified |
| WP4 third family | 20 min | recommendation and user action |
| WP5 final experiment | 1 h 10 min | both phases, hypotheses H1–H6, n, cost, machine, and the implementation specification |
| WP6 review | 30 min | one fresh astra-xhigh reviewer; corrections applied |
| WP7 report | 30 min | `FINAL-REPORT.md`, STATE, the continuation entry, the Persian summary |

The extension tier is dropped unless time is left.

You (Codex) are the lead researcher for this session. A supervisor script started you, keeps you going until the session deadline and resumes you if a turn ends early. Nobody will answer questions during the run. When something needs the user, record it under "Decisions for the user" in `PROGRESS.md`, state the default you assumed, and continue.

**How Claude reads the request.** This session is deep research, not experimentation. Every experiment it designs runs later on a rented server, only after the user approves it.

| The user's phrase | What it means for this session |
|---|---|
| **Strengthen the final experiment** | Design the final experiment that a Q1 reviewer would require, to run on a rented GPU later: a development phase for mechanism measurements and attack development, then a confirmatory phase on fresh held-out sources. It must test more than "F5 fails on SDXL": a mechanistic prediction, an informed attacker and, if possible, a third independent family. |
| **Deep analysis** | Explain *why* the SD1.5-directed mark survives SD1.5 img2img but not SDXL or Kandinsky 3 img2img, even where those passes are milder in pixel terms. Use first principles, the literature, and a deep reading of the result files that already exist. |
| **Intelligence** | Turn that explanation into a falsifiable, quantitative model (a "transfer law") with predictions fixed before the server measures anything. Use it to specify an informed attacker: the strongest realistic attack an adversary who understood the mechanism would run. |
| **Real deep research** | Primary literature read in full (method and experiment sections), derivations written out, every claim traced to a file or a paper, and an independent hostile review. |

The session deadline is given in your first prompt and repeated in every supervisor message. Write it at the top of `PROGRESS.md` in WP0. All files of this session go in `research/encoder-transfer-20261019/final-study-20261025/` (here called `FS/`).

## 1. Hard rules: research only, nothing runs on this laptop

**Not allowed:**
- any experiment on this laptop:
  - no image generation, marking, regeneration, attack, detection, metric or descriptor computation, encoder pass, training, calibration or timing run;
  - no GPU;
  - no `.thesis-build/a6-science-venv`, and no other interpreter with torch, diffusers, numpy, scipy, PIL or lpips;
  - no new dev runs or rehearsals;
- downloading images, datasets, model weights or code repositories, and installing packages;
- paid compute or API: no vast.ai, no `vastai` CLI, no SSH to any server, no purchases;
- opening held-out pixels or running anything on held-out data;
- changing F5 r2, v5 r3, any baseline, threshold or decision rule (ideas for a better watermark go to `FS/ideas-not-tested.md` only);
- editing frozen artifacts:
  - the stage-2a and stage-2b contracts and asset plans;
  - `results.md`, `results-2b.md`, `review.md`, `review-2b.md`, `report/`, `amendment-*.md`;
  - the run folders under `.thesis-build/dev-runs/`;
- editing protected files: the proposal, `research/claims.csv`, the source plan, `THESIS_GUIDE_OFFLINE.html`, retained run outputs; never merge, rebase or check out other branches, and never write into other worktrees;
- accepting gated-model licences, logging in or using tokens.

**Allowed:**
- reading every file in the main checkout and every worktree, including the saved result files (`rows.jsonl`, `metrics.json`, `run.json`, logs);
- web search, and reading papers, model cards, code repositories online and standards;
- **stdlib Python only** (`W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe`, run with `-I`):
  - to aggregate and analyse the existing JSON and JSONL result files: detector score/threshold margins, carrier states, distortion metrics, per-source and per-seed patterns;
  - to compute bounds, power and sample sizes, and noise-schedule constants;
  - keep each script under 15 minutes;
- saving papers (PDF or HTML only, at most 3 GB) to `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/cache-et-final/papers/`. Commit cards, not full texts; quotations at most 25 words with a locator;
- writing Markdown, CSV, JSON and BibTeX in `FS/`, plus stdlib analysis scripts in `FS/analysis/`;
- writing *specifications* of the server code (interfaces, pseudocode, test lists) in `FS/`. Implementation happens later, after the user approves;
- committing and pushing this branch, and updating MAIN `thesis-runs/d916749c/STATE.md` at the end.

**Technical guard.** The supervisor:
- hides CUDA;
- kills any child process that uses the science interpreter, imports an ML library on its command line, runs an experiment script, calls `vastai` or `ssh`, or runs Python for more than 15 minutes;
- logs each kill.

Do not work around it. If a computation is essential, specify it for the server phase (WP5) with its design, cost and the claim it would unlock.

**Research integrity:**
- **Primary sources.** Prefer the paper itself (arXiv HTML, CVF, OpenReview, publisher page) and record the version read.
- **Verification level** of every source:
  - `V2` = method and experiment sections read;
  - `V1` = abstract or metadata only;
  - `V0` = known to exist but not accessed.
  - Only V2 sources may support a novelty, comparison or mechanism statement. Never cite what you have not opened.
- **Never invent** DOIs, numbers, quotes, venues or quartiles; write `UNVERIFIED` and the reason instead.
- **Search log.** Log every search (date, engine or API, query, useful hits) in `FS/literature/search-log.md`. Any "we found no …" sentence names its searches and date.
- **Useful free APIs** (use `curl.exe`, about one request per second, never put personal data in URLs): arXiv API and arXiv HTML, Semantic Scholar, OpenAlex, Crossref, DBLP, OpenReview.
- **Thesis numbers** come only from the result files and the study documents, each with a file locator.
- **Order.** Write hypotheses and model forms before you compute anything from the result files, and commit them first, so that the order is visible in git. Label every post-hoc analysis as post-hoc and descriptive. Keep failed analyses.
- **Language.** Files in English. Only your final message (WP7) is in Persian.

## 2. Where things are

- **This worktree:** `C:/Users/Soroush/.codex/worktrees/codex-et-final`, branch `codex/encoder-transfer-final-20261025`, from `claude/encoder-transfer-stage2` at 4cc53e3.
- **MAIN:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`. Read `thesis-runs/d916749c/STATE.md` once at the start.
- **Study documents** (`research/encoder-transfer-20261019/`):
  - `BRIEF.md` (the original study brief; the decision rule is in section 3), `protocol.md`, `budget-and-proposals.md`, `amendment-1d.md`, `amendment-2b.md`;
  - `results.md`, `review.md` (stage 2a), `results-2b.md`, `review-2b.md` (stage 2b);
  - `report/tables.md` (T7 tables of the union) and `report/figures/` (PNG; you may look at them);
  - `article/route-c-skeleton.md` (article plan and gap list);
  - `design-research/` T1–T8. Especially `T2-encoder-landscape/` (which families share autoencoders), `T4-mechanism/`, `T6-statistics/`, and `T7-fair-reporting/synthesis.md`, the binding reporting contract.
- **Code to read** (do not run):
  - `scripts/encoder_transfer_test.py` (planning, predicates, analysis);
  - `scripts/encoder_transfer_runtime.py` (regenerators, detectors, metrics; F5 and v5 through `three_threat_models`, `f5_latent_codec`, `revised_watermark_v5`);
  - the stage-2b server setup and driver scripts.
- **Saved result files** (MAIN `.thesis-build/dev-runs/`, read-only):
  - **Stage 2a:** `20261024-1431-encoder-transfer-stage2a/results/stage2a-full/rows.jsonl` and `metrics.json`.
  - **Union:** `20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl`, the union journal with 11,040 units, plus `metrics.json`.
  - **Journal format:** `rows.jsonl` is append-only, so the last line per `id` is the final state. Ids look like `R1:30:f5-r2:0.2:12` (channel, source, arm, strength, seed).
    - C0 is arm `unmarked`; marked and C0 outputs are paired by source and seed.
    - Each row holds `detections[method][owner]` with `endpoints` and `raw` (tier score and threshold, decoded fields) and the distortion metrics.
  - **Image folders:** do not open them in code. PNG figures in `report/figures/` may be viewed.
- **Schedulers** (for the noise-level derivation):
  - R0 and R1: DDIM 20 steps, leading spacing, steps_offset 1, scaled-linear betas from .00085 to .012.
  - R3: Kandinsky 3's shipped DDPM `squaredcos_cap_v2`.
  - With 20 leading-spaced steps (951, 901, …, 51, 1), strengths .1/.2/.4 keep the last 2/4/8 steps, so they start at t = 51/151/351 (verify against diffusers 0.35.1).
  - review-2b N2 gives ᾱ(151) ≈ .94 (cosine) against ≈ .83 (scaled-linear).

## 3. Work packages (about 12 hours; adapt the split, keep the order)

### WP0. Orientation and objections (at most 45 minutes)
- Write `FS/PROGRESS.md`: the deadline, a work log and "Decisions for the user".
- Write `FS/00-objections.md`:
  - the fifteen strongest objections a hostile Q1 reviewer (IEEE TIFS level) would raise against the current evidence and the planned article, ranked by severity;
  - which work package answers each.
- Commit and push.

### WP1. Deep literature review (about 3.5 hours; the largest package)
Read at V2, and card, at least 30 primary sources across these clusters:
1. **Regeneration and purification attacks and their theory:**
   - "invisible watermarks are provably removable" style results;
   - DiffPure-style purification;
   - rinsing and multi-pass regeneration;
   - adaptive and informed attacks (for example UnMarker, CtrlRegen, latent-space or encoder-swap attacks);
   - the WAVES and W-Bench/VINE benchmarks.
2. **Watermarks that act through, or against, a latent autoencoder:**
   - encoder-aware and VAE-aware marks;
   - latent-diffusion watermarks (Tree-Ring, Gaussian Shading, ROBIN, WIND, RingID, ZoDiac, Stable Signature, and newer ones);
   - what each claims about transfer across autoencoders or model families.
3. **Autoencoder independence and the latent-space geometry of SD1.5, SDXL, SD3/3.5, FLUX, Kandinsky 3 (MoVQ), SANA (DC-AE) and Stable Cascade:**
   - training data and initialization;
   - latent channels;
   - whether weights or decoders are shared;
   - published evidence on transferability of adversarial perturbations across autoencoders.
4. **Adversarial-example transferability theory** relevant to encoder-directed perturbations (gradient alignment, shared features).
5. **Evaluation methodology** for watermark robustness: matched distortion, low-FPR reporting, sample sizes.

**Output:**
- cards in `FS/literature/`;
- `FS/literature/search-log.md`;
- `FS/01-literature-synthesis.md`: what is known, what is contested, and where this study's question sits;
- `FS/02-positioning.md`: novelty with supporting searches; the closest prior work; what the article must not claim.

### WP2. Mechanism: theory and a deep reading of the existing results (about 3 hours)
Write `FS/03-hypotheses.md` first (mechanisms, model forms, predictors, what would falsify each) and commit it. Then:
1. **First-principles derivation.** F5 is optimized through the SD1.5 encoder, so its residual δ lies in directions of high SD1.5-encoder gain. Derive what this implies for:
   - (a) survival of the SD1.5 autoencoder round trip and of SD1.5 img2img, where noise is injected at σ_t in the SD1.5 latent and the denoiser is trained on SD1.5 latents;
   - (b) an independently trained encoder, where the latent gain in those directions has no reason to be high;
   - (c) dependence on strength (t, ᾱ_t) and on the scheduler.
   - Write the latent signal-to-injected-noise argument explicitly. State what it predicts for every one of the 15 cells (R0/R1 .1/.2/.4, rinse, R1-smooth, R1-mode, R3, D1, D3, X1, X2, clean), and where it is silent.
2. **Deep reading of `rows.jsonl`** (stdlib only, post-hoc, descriptive):
   - **Margins:** F5 and v5 semantic and instance score/threshold margins by cell, source and seed.
   - **Carrier states and tiers:** carrier-state transitions; the two F5 tiers' opposite behaviour under SD1.5 and SDXL.
   - **Correlations:** within-source correlation of margins across cells; seed effects; how distortion metrics relate to margins within and across families.
   - **Baselines:** the behaviour of WAM bit accuracy and VINE-R bit accuracy as continuous measures.
   - **The core test:** whether any distortion-only model can explain the cell pattern, against a model that adds the family and the schedule noise level.

   Put the scripts in `FS/analysis/` and the figures as PNG (stdlib SVG or text plots are fine) in `FS/figures/`.
3. **The transfer law.**
   - A small, pre-declared quantitative model that predicts survival from mechanistic quantities: latent gain of δ per encoder, injected noise level, denoiser family.
   - Fit only the parts that existing data can support. Each parameter the server must measure becomes a measurement in WP5.
   - Fix the out-of-sample predictions for the confirmatory phase now, with an accuracy criterion.
4. **Output:** `FS/04-mechanism.md`. It covers the derivation, the analysis results, the law, its predictions, and what it cannot explain.

### WP3. Informed attacker, specified (about 1 hour)
From WP2, specify one to three principled attacks that an adversary who understood the mechanism would use, for example:
- a projection or denoising in the SD1.5 latent that removes high-gain directions while preserving quality;
- a cross-encoder round trip followed by a light diffusion pass;
- smoothing in the SD1.5 latent.

**Rules for the attacks:**
- each is generic: one setting for every arm, no per-arm tuning, no key, no detector output;
- each has a quality target fixed in advance;
- each is developed only on development sources in the server's development phase, and frozen before the confirmatory phase.

**For each attack, give:**
- exact pseudocode;
- the expected effect per arm, from the theory;
- the cost per image;
- the risk that it is a straw man.

**Output:** `FS/05-informed-attacks.md`.

### WP4. Third regenerator family (about 1 hour)
- **Audit.** For FLUX.1-schnell, SD3/3.5, SANA, Stable Cascade and any better candidate, check:
  - autoencoder training independence from SD1.5 (primary evidence);
  - licence and access (gated or not);
  - img2img support with a strength parameter;
  - VRAM and download size;
  - scheduler, noise level at a matched strength, and how to compare severity fairly.
- **Recommendation:** recommend one, with a fallback. If it is gated, write the user's exact action.
- **Output:** `FS/06-third-family.md`.

### WP5. The final experiment, for a rented server (about 2 hours)
Write `FS/07-final-experiment.md`, a self-contained pre-registration in two phases.

- **Phase A, development, on the server and development sources only:**
  - mechanism measurements: latent gain of each arm's residual under each encoder against matched random residuals; latent retention after each channel; the noise-only and denoising decomposition;
  - development and freezing of the informed attacks;
  - fitting of the transfer-law parameters.

  Fix the outputs of Phase A that feed Phase B, and freeze them before Phase B.
- **Phase B, confirmatory, fresh held-out sources.**
  1. **Pool:** a licensed public image set never used in this project, checked by identifier against `research/development-sources.md`, `research/downloads.md` and the held-out manifests.
     - a fixed selection rule and seed, written before any identifier is drawn;
     - a manifest `FS/heldout-manifest.json` with identifiers, URLs and licences, and no pixels;
     - a size from a precision or power analysis (aim for about 200 sources unless the analysis says otherwise).
  2. **Hypotheses with decision rules and family-wise error control:**
     - (H1) F5 fails under SDXL img2img at .1 and .2;
     - (H2) F5 survives SD1.5 img2img at .2;
     - (H3) within source, SDXL .1 is milder than SD1.5 .2 yet F5 is lost;
     - (H4) the transfer law's out-of-sample predictions meet their accuracy criterion;
     - (H5) the informed attack's effect on each arm;
     - (H6) VINE-R as the positive control;
     - the negative gates (C0, wrong owner), with zero-false-detection requirements and exact one-sided bounds.
  3. **Cells and arms:**
     - only what the hypotheses need, plus the third family if available, plus the informed attacks;
     - arms F5, v5, WAM, VINE-R and C0; TrustMark Q and Pixel Seal only if justified.
  4. **Analysis and reporting:**
     - the T7 contract;
     - the within-source distortion analysis, pre-declared this time;
     - gatekeeping or Holm across hypotheses.
  5. **Cost, time and machine:**
     - from the measured per-unit timings (`report/tables.md` Table 7 and the stage-2 rows);
     - a machine with at least 64 GB RAM, at least 150 GB disk and an RTX 4090 or larger;
     - download sizes; USD at 0.45–0.60/h for each phase.
  6. **Implementation specification** for the server code:
     - reuse of the stage-2 runner, contract-builder and seeding patterns;
     - new components with interfaces and pseudocode;
     - the CPU test list;
     - the adapter checks;
     - the server setup and driver changes.

     Claude implements and runs it after the user approves.

### WP6. Hostile independent review (about 1 hour)
- **Reviewer:** spawn one fresh agent (`fork_turns: "none"`, `gpt-6-astra`, effort `xhigh`, as AGENTS.md authorizes).
- **Scope:** WP1–WP5, adversarially:
  - citations spot-checked at V2;
  - derivations checked;
  - every number recomputed from the files;
  - hypothesis-before-data order checked in git;
  - the held-out, no-tuning and no-local-run rules checked.
- **Output:** the review goes to `FS/08-review.md`. Apply the corrections, and list the ones you reject with reasons.

### WP7. Final report (the last 40 minutes, or earlier when done)
Write `FS/FINAL-REPORT.md`:
- The first line is `STATUS: COMPLETE`, or `STATUS: PARTIAL` followed by the missing packages.
- **Contents:**
  - the main findings of WP1–WP4, with numbers and file links;
  - the final experiment in one page: phases, hypotheses, cells, n, cost, time, machine;
  - what a Q1 reviewer can and cannot now be told;
  - "Decisions for the user", each as a yes/no question with the default.
- **Finish:**
  - update MAIN `thesis-runs/d916749c/STATE.md` (at most 60 lines, plain English) and add one entry of about 600 characters to `continuation.md`;
  - commit and push;
  - end with a short Persian summary (5–10 lines) for the user.

### Extension tier (only if WP7 is complete before the deadline, in order)
1. **E1:** draft the Related-work, Mechanism and Threat-model sections of the article into `FS/article-drafts/`. They must be consistent with `article/route-c-skeleton.md` and with the claim discipline of `results-2b.md`.
2. **E2:** a venue-fit analysis for the bounded article: TIFS, TMM, TOMM and others, with each journal's quartile as verified on its official page or SCImago.
3. **E3:** a second, independent hostile review of the article frame alone, in `FS/09-review-article.md`.

## 4. Commits and provenance

- **Commit and push** after every work package (and more often during long ones). Use `git -c user.name="Codex agent" commit ...` with the repository's configured e-mail, as AGENTS.md says.
- **Pushing:** push only this branch, and never force-push.
- **Logging:** log each push in `experiments/dev-log.md`.
- **Session record:** keep `FS/PROGRESS.md` current. A reader must always see what is done, what runs, and what the next step is.
