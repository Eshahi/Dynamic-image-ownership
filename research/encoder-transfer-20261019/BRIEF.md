# Independent-encoder transfer test (brief, 2026-10-19)

Written by Claude at the user's request. On 2026-10-19 the user reviewed the research-only Q1 dossier with Claude. They said, translated from Persian: "I want Q1 for myself and it is not mandatory. Also, using the server is better." They chose to run the cheapest decisive experiment before anything else.

You (Codex) design the details, run the study on a rented vast.ai server, analyze it and report. Nobody answers questions while you work. Record decisions in `research/encoder-transfer-20261019/PROGRESS.md` and continue. Stop for the user only at the stop point (section 9) or a hard stop in `AGENTS.md`.

## 1. Question and why it decides the article

**Question.** Does F5 r2's regeneration survival transfer to diffusion regenerators whose autoencoders were trained independently of the SD1.5 encoder that F5 writes through?

**Why this question.** The dossier (`research/q1-dossier-20261018/`, especially `02-literature/Q-VAE.md` and `FINAL-REPORT.md`) found that SD2.1-base keeps the SD1.x encoder. The existing "unseen regenerator" result (`research/journal-upgrade-20261009/unseen-regenerator-results.md`, F5 24/24 at .2) therefore does not show transfer across encoders, exactly where F5's mechanism lives. The pointer-plus-registry architecture is pre-empted (DREW, arXiv 2406.02836; soft-binding benchmark, arXiv 2610.04151). So a Q1 route depends on whether F5 itself is a robust method.

**What the answer decides:**
- **Transfers:** a method-led article stays possible. The next step is a matched external comparison and a fresh confirmation.
- **Fails:** F5's robustness is encoder-specific. The method route closes, and the article becomes the bounded empirical one, with this failure reported as a mechanism finding.

**Prior development observation (not evidence for this test).** In the D2 discovery work, F5 kept checked semantic detection on 10/12 sources after an SDXL VAE-only round trip (`research/journal-upgrade-20261009/discovery-report.md`). Full SDXL regeneration was never run, because the laptop GPU did not have the memory (`unseen-regenerator-protocol.md`). That is why this test runs on a rented server.

## 1a. Stage 1: comprehensive design research before freezing (no server, no outcomes)

The user asked on 2026-10-19 for more research with Codex so that the results are more precise. They then said, translated from Persian: "I want a very comprehensive, supplementary and complete research to be done, and it does not matter however long it takes." Stage 1 therefore has **no time limit**. Its quality bar is that a hostile Q1 reviewer could not name a standard setting, baseline, encoder family or validity threat that you did not consider and decide on with reasons.

**Two limits remain, because they protect the validity of the result:**
- **No outcomes before freezing.** No GPU work. No regeneration, detection or scoring of any real mark. No look at any F5 result under the new channels. Research done after outcomes would make the design post-hoc.
- **The user approves money and scope.** Anything that adds cost beyond the base budget (section 5), or adds external baselines beyond WAM and VINE, goes to the user at the stage-1 stop as a costed proposal. You do not freeze it unilaterally.

### Method

- **Sources.** Primary sources only, at verification level V2: method and evaluation sections actually read. Follow the Q1 dossier's integrity rules: search logs, no invented metadata, cache in MAIN `.thesis-build/q1-research-20261018/cache/` and never in git. Reuse the dossier's cards in `research/q1-dossier-20261018/02-literature/`; extend them, do not redo them.
- **Code and model cards.** Read official repositories, model cards, configs and licenses on the web. Downloading weights or code to run is not allowed in stage 1.
- **Sub-agents.** Run the topics below in parallel, at most 3 at a time. Use `gpt-6-astra` at `high`, with a self-contained brief and one output folder each.
  - Each topic folder `research/encoder-transfer-20261019/design-research/T<n>-<slug>/` holds `search-log.md`, cards and `synthesis.md`.
  - You integrate everything into `design-research.md`.
- **Commits.** Commit and push after each topic.
- **Coverage.** For every topic, write a coverage statement: what was searched, what was found, which recent (2025-2026) work was checked, and what remains inaccessible.

### Topics

1. **T1, regeneration attack standards.** Cover every major benchmark and attack paper: W-Bench (VINE), WAVES, Zhao et al. (arXiv 2306.01953), CtrlRegen, UnMarker, rinsing or multi-pass regeneration, DiffPure-style purification, and newer 2025-2026 benchmarks and removals (the dossier lists MarkNull, RAVEN and "Watermarks Attack Watermarks").
   - For each, tabulate models, strengths or noise steps, samplers and step counts, prompts or captions, resolution, number of images, metrics and reported baseline numbers.
   - Decide which settings this test adopts and why. Within the base budget, add at most one or two standard-conforming variants (for example caption-prompted regeneration, or a multi-pass channel) as secondary channels.
2. **T2, independent-encoder landscape.** Map the open text-to-image families and their autoencoders: SD1.x/2.x kl-f8, SDXL, SD3 and SD3.5, FLUX.1 schnell and dev, any newer FLUX, Kandinsky (MoVQ), SANA (DC-AE), PixArt, Playground, Hunyuan-DiT, Qwen-Image and other current ones.
   - For each, record: encoder lineage and whether it is independent of SD1.x and of SDXL; channels and downsampling; license and gating; img2img support in diffusers; memory and time at 1024.
   - Include a pixel-space diffusion regenerator if a permissive, ungated one is feasible.
   - Choose the regenerator panel that gives the widest encoder diversity within the base budget, and justify each choice. Put larger panels in the costed proposals.
3. **T3, faithful baselines.**
   - For VINE (variant, resolution, message length, decoding, threshold) and WAM (official detection rule), fix the exact native configuration and report the native operating point next to our common presence threshold.
   - Survey the other public post-hoc methods robust to regeneration (for example TrustMark, StegaStamp, InvisMark, RoSteALS, ZoDiac and newer ones). Record code and weights availability, license, compute, and published regeneration results.
   - Rank which extra baselines a Q1 reviewer would most expect. These are proposals for the user, not part of the frozen core.
4. **T4, mechanism and predictions.**
   - From Zhao et al.'s bound and the F5 design (`research/f5-encoder-amplified-latent.md`), derive what should happen under an independently trained encoder, and write falsifiable predictions before any data exists.
   - Include an encoder-aware adaptive regenerator (for example regenerating with a robustified or different encoder) as an analyzed threat and a costed proposal.
5. **T5, pipeline technicalities.**
   - SDXL: fp32 VAE upcast, the 1024 policy and resampling, scheduler and strength semantics, determinism, safety checkers and memory.
   - FLUX or its replacement: img2img step semantics.
   - Confirm that every setting in section 2 does what it claims, from official docs and code.
6. **T6, statistics and sample size.**
   - With stdlib, compute the decision rule's operating characteristics: the probability of each label at true F5 rates of .5 to .9, accounting for clustering by source.
   - Choose n between 60 and 120 within budget, with the source rule unchanged.
   - Fix intervals, multiplicity handling for secondary cells, and missing-data treatment.
7. **T7, fair comparison and reporting norms.**
   - How do Q1 venues and benchmarks compare robustness at matched quality (WAVES-style performance-quality curves, TPR at fixed FPR)?
   - Fix the matched-distortion analysis, the figures and the tables you will report.
8. **T8, threats to validity.** List every threat with its mitigation or stated limitation: shared ancestry, resolution resampling, prompt policy, development-data reuse, safety blocks, baseline mis-configuration, multiple channels, and others.

### What the research may change, and what it may not

**May change before freezing, within the base budget:**
- channel settings and up to two literature-standard variants;
- the regenerator panel;
- baseline configuration;
- n, within 60 to 120;
- analysis and reporting details.

**May not change:**
- the question;
- R1 SDXL at strength .2 as the primary cell;
- the proportional decision thresholds: TRANSFERS needs at least .75n, FAILS is below .5n, the margin is .05n;
- external baselines beyond WAM and VINE without user approval.

Record every change, with its source, in `design-research.md`.

### Independent review of the design

Before the stop, one fresh agent (`gpt-6-astra`, `xhigh`, `fork_turns: "none"`) reviews `design-research.md`, the frozen protocol and the costed proposals. It checks coverage gaps, fidelity to the sources, internal consistency and pre-registration hygiene, and writes `design-review.md`. Fix what is fixable and list the rest.

### Stage 1 deliverables and stop

Deliver:
- `design-research.md` and the topic folders;
- `design-review.md`;
- the frozen `protocol.md` and `frozen-config.json`;
- the code with passing unit tests;
- `budget-and-proposals.md`: the projected hours and cost of the frozen core, plus each costed proposal (extra baselines, extra regenerators, adaptive arm) with its cost and your recommendation.

Commit and push all of it, then **stop and report to the user in Persian.** Claude reviews the frozen protocol and the proposals before any money is spent. The user then approves or declines each proposal and rents the server. They send its SSH line, and that message starts stage 2 (sections 5 and 6). If a proposal is approved, record the approval in the protocol as a pre-outcome amendment before stage 2 runs.
## 1b. Stage 1 deepening (user request, 2026-10-20)

**Why.** Claude checked the stage-1 session logs, and the research was thinner than section 1a asked for:
- the main thread was active for about 1 hour, with an 8.8-hour pause for a usage limit;
- each topic agent worked 3 to 13 minutes;
- the eight topics have 19 cards in total (T2 has none, T8 one), and their search logs have 9 to 26 lines each.

The user asked for a very comprehensive, complete research effort, whatever it takes. Deepen stage 1 before any server is rented. The frozen package `c2384e7` stays in history. Any change it leads to is a pre-outcome amendment, because no outcomes exist yet.

### Minimum coverage per topic

These are floors, not targets. Each source counts once, must be at least V2 (method and evaluation sections actually read), and needs its own card in the topic's `cards/` folder. Cards from the Q1 dossier count only if the topic folder gets a card that says what was re-checked for this design question.

| Topic | Minimum |
|---|---|
| T1 attack standards | 15 benchmark or attack sources. Include every 2025-2026 regeneration or removal benchmark you find. Each gets a row in a settings table: models, strengths or noise steps, sampler and steps, prompt policy, resolution, image counts, metrics. |
| T2 encoder landscape | 15 model families, one card each: paper or model card, autoencoder lineage evidence, channels and downsampling, license and gating, diffusers img2img support, memory at 1024. |
| T3 baselines | 12 post-hoc methods, one card each: code, weights, license, native settings and thresholds, published regeneration results with their conditions, and run-cost notes. |
| T4 mechanism | 8 theory or mechanism sources, plus written falsifiable predictions for every channel in the frozen core and in each proposal. |
| T5 pipelines | For each of SD1.5, SDXL, Kandinsky 3, VINE, WAM and TrustMark: the exact code path in the pinned versions, cited by file and line, for every setting the protocol relies on. |
| T6 statistics | Operating characteristics of the decision rule, including sensitivity to between-seed correlation and to missing units, for n = 60, 90 and 120. |
| T7 reporting norms | 12 recent (2024-2026) evaluation sections from Q1 journals or top venues, tabulated: image counts, metrics, FPR operating points, matched-quality practice, baselines. |
| T8 validity | 25 distinct threats, each with its mechanism, its mitigation or stated limitation, and a source or argument. |

**Search breadth.** Every topic logs at least 10 distinct queries across at least three of these: web search, the arXiv API, Semantic Scholar or OpenAlex, and official repositories or model hubs. Each topic writes a coverage statement and a section "what we might still have missed", with reasons.

### Process rules

- **One agent per topic.** Use `gpt-6-astra` at `xhigh` for T2, T3 and T4, and at `high` for the others. Run at most 3 at a time. Give each a self-contained brief that includes its minimum.
- **Check minimums before accepting.** The parent counts the cards and the search-log entries before accepting a topic. A topic below its floor goes back to a fresh agent with the gap list. The parent never fills a topic hastily itself.
- **Usage limits.** If an agent fails or a usage limit interrupts, wait, then resume or re-brief. Shortening the topic is never the fix.
- **Commits.** Commit and push after each accepted topic.
- **Then:**
  - revise `design-research.md`;
  - record any pre-outcome amendment (within the limits of section 1a) in `protocol.md` and `frozen-config.json`;
  - update `budget-and-proposals.md`, keeping P1-P8, revising them and adding new ones where the research supports it.

### Second independent review and re-freeze

1. A fresh agent (`gpt-6-astra`, `xhigh`, `fork_turns: "none"`), different from the first reviewer, writes `design-review-2.md`. It must first audit the coverage table above, with counts per topic. **It fails the package if any floor is unmet.** Then it reviews the design and its amendments as in section 1a.
2. Fix what it finds.
3. Re-freeze with a new commit and push.
4. Stop and report in Persian, as in section 9 stage 1. Add the per-topic counts and what the deepening changed.

## 2. Fixed design

Freeze all of this, as amended by stage 1 within its limits, in `research/encoder-transfer-20261019/protocol.md`, plus a machine-readable `frozen-config.json`. Commit and push both before any regeneration exists. Implementation details not fixed here are yours to fix in the protocol, before outputs.

### Sources
n = 60 development sources:
- the 24 sources of `research/journal-upgrade-20261009/fresh-development-selection.json`;
- plus the first 36, by sorted `source_id`, of `registry-fresh-development-selection.json` that are not among those 24;
- if fewer than 36 are usable, fill from `round3-development-selection.json` by the same rule.

Exclude anything that matches a held-out or test index by ID or hash. Record the final list and its SHA-256 in the protocol. These sources are consulted development data: this is a development study, not a confirmation.

### Arms
Embed every arm on the server, on the same hardware, with native settings and no tuning:
- **F5 r2:** the frozen `F5_PARAMS` and owner and profile keys used by `scripts/registry_step1_transfer.py`.
- **v5 r3:** internal comparator, frozen.
- **WAM:** the released MIT SA-1B checkpoint pinned in `research/journal-upgrade-20261009/wam-download.json`, with a native 32-bit message.
- **VINE (VINE-R):** official code and weights, with a native 100-bit message.
  - **USER APPROVAL: APPROVED.** The user answered in chat on 2026-10-19: "Yes, include VINE as the external baseline in this test."
  - Run this arm only if the line says APPROVED and the license permits research use; otherwise skip it and record why.
  - It reopens external baselines for this test only.

WAM and VINE messages are fixed pseudo-random bits per source, from a recorded seed. They are never optimized.

E3 is excluded (closed line of work). T4 and T5 are not re-tested: this test concerns T3 regeneration only.

### Channels
- **R0, SD1.5 img2img (anchor):** the historical schedule. DDIM 20 steps, empty prompt, guidance 1, eta 0, frozen safety checker, at 512 pixels.
- **R1, SDXL base 1.0 img2img (primary):**
  - `stabilityai/stable-diffusion-xl-base-1.0` at a pinned revision, no refiner;
  - the official VAE, decoded in fp32 (upcast); do not substitute the fp16-fix VAE;
  - upscale 512 to 1024 with Lanczos, regenerate at 1024, then Lanczos back to 512 for detection;
  - DDIM 20 steps, empty prompt, guidance 1 (no classifier-free guidance), eta 0.
- **R2, FLUX.1-schnell img2img (secondary, descriptive):**
  - same 1024 resolution policy, empty prompt, guidance 0;
  - 10 inference steps, so that every strength takes at least one step;
  - run it only if the model is downloadable without a gated license and fits the budget; otherwise skip it and record why.
- **D1 and D2, diagnostics:** deterministic VAE-only round trips at 1024 for SDXL and for FLUX (if R2 runs). One per source and arm, with no seeds.

Strengths are .1, .2 and .4, with seeds 12, 13 and 14 (the step-1 values). The source is the paired unit. "Source majority" means at least 2 of its 3 seeds.

### Detection and negatives
- **F5 and v5:** the frozen M2 predicates exactly as in step 1 (S, C, Q, J and the others). The primary is source-majority C.
- **WAM and VINE:** presence at a fixed bit-agreement threshold k, chosen so that the exact binomial tail P(X >= k) <= 1e-4 for a random message of their native length. Compute k with stdlib and write it in the protocol before outputs. Report bit-accuracy distributions too.
- **Negatives:** each source's unmarked image goes through every channel with the same seeds (C0) and is read by every detector. F5 and v5 also get the step-1 wrong-owner calls. Report observed false detections; make no FPR claim beyond the observed counts.
- **Achieved distortion:** for every regenerated output, compute PSNR, SSIM and LPIPS against its marked input at 512. Report medians per channel and strength, so that severity can be compared across channels. Equal numeric strength is not equal severity.
- **Clean quality:** PSNR, SSIM and LPIPS of every arm's marks against the source, plus F5's strict gate.

## 3. Pre-registered decision rule

The primary cell is F5, R1 SDXL, strength .2, source-majority C, with n sources (60 unless stage 1 sets it between 60 and 120). The thresholds below scale with n; the numbers in brackets are for n = 60. Let m = ceil(.05n) be the baseline margin [3].

| Outcome | Condition |
|---|---|
| TRANSFERS | F5 >= ceil(.75n) [45], and zero C0 and wrong-owner false detections by F5 on R1 outputs |
| FAILS | F5 < .5n [30] |
| PARTIAL | anything else |

**External context, part of the outcome label.** Let B be the best external baseline count at R1 .2 (presence, source majority).
- If TRANSFERS and F5 >= B - m: write **ROUTE A**, a method article is viable.
- If TRANSFERS and B > F5 + m: write **ROUTE B**. F5 transfers but is not the most robust, so any method claim must rest on a quality, capacity or cost tradeoff at matched distortion.
- If FAILS: write **ROUTE C**, the bounded empirical article.
- If PARTIAL: write **ROUTE UNDECIDED** and stop for the user.

**Reporting rules:**
- All other cells (.1, .4, R0, R2, D1 and D2) are descriptive.
- Paired exact sign tests and Clopper-Pearson intervals are exploratory; no test overrides the rule.
- Missing or safety-blocked positives count as failures; missing negatives are unresolved.
- Report everything, including failures.

## 4. Code

- Write a new script `scripts/encoder_transfer_test.py`; do not modify the historical step-1 script. Reuse its loading, journal, resume and predicate code, and the WAM adapter in `scripts/journal_wam_probe.py`.
- Add VINE and FLUX adapters only as the arms allow.
- Add unit tests for the endpoint logic, the binomial thresholds and the decision rule, and run them.
- Commit and push code and protocol before the server run, so that the commit hash identifies what ran.
- The run writes `run.json` and `rows.jsonl` (resumable, one row per unit, with every failure kept) and a final metrics JSON.

## 5. Server

**The user rents the server after the stage-1 stop.** They create the instance on vast.ai with the public key `~/.ssh/vast_ed25519.pub` and send you its SSH connect line in the message that starts stage 2. You connect only with `~/.ssh/vast_ed25519`. You never handle their vast.ai account, payment or API key.

**Budget:** at most 15 instance-hours, or USD 15 at the instance's hourly price, whichever comes first, for setup plus run.
- After the smoke test, project the full run time.
- If the projection exceeds the budget, drop in this order: R2 FLUX, then D2, then strength .1.
- Never drop R1 at .2 or .4, or the R0 anchor. Record what was dropped and why.

**Setup:**
- Clone the pushed branch from GitHub on the server; the repository is public. The user's upload is slow (about 40-100 KB/s), so never upload bundles.
- Create a venv (uv is fine) and install the packages the code needs at pinned versions. Use CUDA 12.8-compatible torch for Blackwell GPUs.
- Download the models from Hugging Face at pinned revisions. Record URL, revision, license and SHA-256 in `research/downloads.md`.
  - The SD1.5 files must match the existing locks by SHA-256.
  - Keep total downloads under 80 GB.
- Download the development images on the server from their recorded source URLs and verify their SHA-256. Upload only what cannot be re-downloaded.

**Smoke test** on 2 extra development sources that are not among the 60. It checks only that the pipeline runs, the memory it needs and the time it takes. After the smoke test, only bug fixes are allowed, never design changes. Record every fix.

**Full run:**
- Run under tmux or nohup with the resumable journal, so that it survives a lost SSH connection or a laptop sleep.
- Monitor through the log. Keep working on the analysis code while it runs.

**Results home:** copy `run.json`, `rows.jsonl`, the metrics, the logs and all regenerated images (or, if they exceed 10 GB, all images for 10 fixed sources plus SHA-256 manifests for the rest) into MAIN `.thesis-build/dev-runs/<YYYYMMDD-HHMM>-encoder-transfer/`. Verify the hashes after copying.

**Then stop the instance.** From inside, use `vastai stop instance $CONTAINER_ID --api-key $CONTAINER_API_KEY` if those variables exist; otherwise ask the user in your final message to stop it. Never destroy it.

## 6. Analysis and outputs

All files go in `research/encoder-transfer-20261019/`:
- `protocol.md` and `frozen-config.json`, committed before the run;
- `PROGRESS.md`: log, decisions, budget use and dropped cells;
- `results.md`, which contains:
  - every endpoint with its denominator, Clopper-Pearson interval and the outcome of the decision rule;
  - an achieved-distortion table;
  - clean-quality and cost tables;
  - negatives;
  - a comparison with step 1, SD1.5 versus SD2.1 versus SDXL;
  - what may and may not be claimed;
- `review.md`: one independent review by a fresh agent (`gpt-6-astra`, `xhigh`, `fork_turns: "none"`). It checks protocol adherence, the numbers against `rows.jsonl`, and the decision label.

Then:
- add one line to `experiments/dev-log.md` and write `run.json` per `AGENTS.md`;
- update MAIN `thesis-runs/d916749c/STATE.md`;
- commit and push.

## 7. Integrity

- Development data only. Held-out and test pools never go to the server and are never touched.
- No tuning on SDXL or FLUX outputs: do not change F5, v5, thresholds or the decision rule after the protocol commit.
- Keep every failed unit and every negative result.
- Image-domain F5 stays a labelled image-domain method, never the proposal's latent method.
- The supervisor's scope rulings and the T3/T4/T5 threat scope still hold.

## 8. Time

Plan for about one working day plus a checkpoint:
- stage 1 comprehensive design research: no time limit (expect roughly 8-16 h of agent work);
- protocol and code: 2-4 h;
- then the stage-1 stop and Claude's protocol check, before the server is rented;
- server setup and smoke test: 1-2 h;
- run: 4-10 h, depending on the GPU;
- analysis and review: 2 h.

Use the run time for analysis code and the results skeleton.

## 9. Stop point and final message

There are two stops:
- **Stage 1:** stop when the frozen protocol, design research, design review, code and `budget-and-proposals.md` are pushed. Report in Persian (at most 15 lines): what the research changed, the final n, channels and baselines, the projected hours and cost of the core, and each proposal awaiting the user's decision, with its cost and your recommendation.
- **Stage 2:** stop when the results and review exist and the decision label is written, or when a hard stop applies. If the run is still in progress and the turn must end, leave the server running the journaled job, write the state to `PROGRESS.md`, and continue in the next turn.

Your final message to the user is in Persian, at most 12 lines:
- the decision label;
- the primary numbers (F5 and the baselines at R1 .2, plus the R0 anchor);
- the cost used;
- whether the instance is stopped;
- the path of `results.md`.
