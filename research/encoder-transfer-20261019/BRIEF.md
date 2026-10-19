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

## 2. Fixed design

Freeze all of this in `research/encoder-transfer-20261019/protocol.md`, plus a machine-readable `frozen-config.json`. Commit and push both before any regeneration exists. Implementation details not fixed here are yours to fix in the protocol, before outputs.

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

The primary cell is F5, R1 SDXL, strength .2, source-majority C, n = 60.

| Outcome | Condition |
|---|---|
| TRANSFERS | F5 >= 45/60, and zero C0 and wrong-owner false detections by F5 on R1 outputs |
| FAILS | F5 < 30/60 |
| PARTIAL | anything else |

**External context, part of the outcome label.** Let B be the best external baseline count at R1 .2 (presence, source majority).
- If TRANSFERS and F5 >= B - 3: write **ROUTE A**, a method article is viable.
- If TRANSFERS and B > F5 + 3: write **ROUTE B**. F5 transfers but is not the most robust, so any method claim must rest on a quality, capacity or cost tradeoff at matched distortion.
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

**The user rents the server.** They create the instance on vast.ai with the public key `~/.ssh/vast_ed25519.pub` and give you the SSH connect line in the goal message. You connect only with `~/.ssh/vast_ed25519`. You never handle their vast.ai account, payment or API key.

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

Plan for about one working day:
- protocol and code: 2-4 h;
- server setup and smoke test: 1-2 h;
- run: 4-10 h, depending on the GPU;
- analysis and review: 2 h.

Use the run time for analysis code and the results skeleton.

## 9. Stop point and final message

Stop when the results and review exist and the decision label is written, or when a hard stop applies. If the run is still in progress and the turn must end, leave the server running the journaled job, write the state to `PROGRESS.md`, and continue in the next turn.

Your final message to the user is in Persian, at most 12 lines:
- the decision label;
- the primary numbers (F5 and the baselines at R1 .2, plus the R0 anchor);
- the cost used;
- whether the instance is stopped;
- the path of `results.md`.
