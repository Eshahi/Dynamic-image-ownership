# Amendment 2b: stage-2b extension (prepared, not run)

Written by Claude (Opus 5.5) on 2026-10-24 at the user's request. **Nothing in this amendment has run.** The contract (`stage2b-config.json`) is built on the new server after the Kandinsky 3 files are downloaded, as for stage 2a. Execution needs the user's go-ahead, which the builder records verbatim.

## User decisions

- **2026-10-21, verbatim:** "Approve P1 TrustMark, P9 PixelSeal, P4 Kandinsky 3 and P5 smoothing; decline the rest; ceiling 35 instance-hours or USD 30." (BRIEF section 1c.)
- **2026-10-21:** the lean two-stage plan (BRIEF section 1d), under which stage 2b ran only if stage 2a gave TRANSFERS.
- **2026-10-24, after the stage-2a label FAILS, ROUTE C, verbatim:** "Prepare the stage-2b extension amendment (strength curve, rinse, full Kandinsky 3, smoothing) with its exact cost and the new server plan, without running it."

## What this changes, and what it does not

**The stage-2a label is final: FAILS, ROUTE C.** Stage 2b is descriptive. It serves the ROUTE C article's gaps: a strength curve, a second independent family, and the mechanism. Its analysis must reproduce the stage-2a label from the inherited rows; the runner refuses to finish otherwise.

**Outcome hygiene:**
- The decision to run stage 2b was taken after seeing the stage-2a results. That is a scope decision.
- Every stage-2b setting was fixed before any stage-2 output existed:
  - R0/R1 at .1 and .4 and the R1 rinse are frozen at `e318757`;
  - P4 and P5 are approved as specified in `budget-and-proposals.md` at `e318757`.
- The implementation details this amendment adds (Kandinsky 3 steps and scheduler, the P5 noise seed) copy the frozen R0/R1 path or are public constants. None was chosen from an output.
- No F5, v5, threshold or decision-rule change.
- No SDXL output from stage 2a was used to choose anything.

### Cells (core arms F5 r2, v5 r3, WAM, VINE-R, plus C0; 60 sources)

| Cell | Settings | Units |
|---|---|---|
| R0 SD1.5 img2img .1 and .4 | frozen R0 (DDIM 20, empty prompt, CFG 1, seeds 12/13/14); 2 and 8 executed steps | 1,800 |
| R1 SDXL img2img .1 and .4 | frozen R1 (1024, fp32 VAE) | 1,800 |
| R1 rinse | frozen: the R1 .1 output passed again at .1, seeds 112/113/114 | 900 |
| R3 full Kandinsky 3 img2img .2 (P4) | revision bf79e6c; native DDPMScheduler as shipped; 20 scheduled steps (4 executed); empty prompt without guidance; fp16 variant; 1024 Lanczos in and out | 900 |
| R1-smooth (P5) | SDXL posterior mode averaged over 4 antithetic Gaussian pairs (σ = 2/255, clip to [0, 1]), then R1's .2 path | 900 |
| R1-mode (P5 matched control) | the posterior mode of the unperturbed input, then the same .2 path | 900 |
| **Total new** | | **7,200** |

**Scope:**
- **TrustMark Q and Pixel Seal:** they stay in their approved cells (P1, P9); a new `arms_by_strength` scope keeps them out of R1 .1 and .4.
- **Declined proposals:** P2, P3, P6, P7, P8 and P10 stay declined.
- **FLUX:** stays excluded (gated).

### Inheritance instead of rerunning
- **No cell is rerun:** the stage-2a full journal (3,840 units) is copied byte for byte into the stage-2b run (`scripts/encoder_transfer_seed_2b.py`).
- **Input checks:** every clean image that a new unit reads is checked against the SHA-256 its stage-2a row recorded.
- **Smoke:** it starts empty, because the stage-2a smoke images were not kept, and reruns the two reserved smoke sources, for timing and pipeline checks only.

**Check on the real stage-2a rows** (laptop, 2026-10-24): the stage-2b analysis code reproduces exactly:
- the label (FAILS, ROUTE C);
- all 131 stage-2a cells;
- the paired tests;
- all 40 quality blocks.

The F5 negative gate becomes the frozen full-grid gate, 540 C0 and 540 wrong-owner calls at R1 .1/.2/.4. It cannot change FAILS.

### Implementation (code; tests on CPU, 44 pass)
- **`encoder_transfer_test.py`:**
  - `channel_arms(config, channel, strength)` with `arms_by_strength`;
  - per-strength plans and analysis;
  - the R1 negative gate counts only planned calls;
  - grouped reductions (`channel:A,B`).
- **`encoder_transfer_runtime.py`:**
  - the `kandinsky3` regenerator: the empty-prompt embedding is computed once by the pipeline's own `encode_prompt(_cut_context=True)`, then the 21.7 GB text encoder leaves the GPU; output quantization is diffusers' `numpy_to_pil`, with a non-finite guard;
  - P5 `posterior_mode` and the latent-given img2img path;
  - `p5_perturbations`, which is hash-checked against the contract;
  - inherited cells are neither timed nor charged in the projection;
  - the full run refuses to start unless they are seeded.
- **`encoder_transfer_assets.py`:** the download allowance comes from the asset plan. It is 60 GB for stage 2b: the frozen 40 GB reserve plus the approved 28.4 GB Kandinsky 3 assets, rounded.
- **New scripts:**
  - `encoder_transfer_amend_2b.py` (the builder);
  - `encoder_transfer_seed_2b.py`;
  - `encoder_transfer_cost_2b.py`;
  - `encoder_transfer_server_setup_2b.sh`;
  - a `--stage 2b` mode in the adapter check (one R3, one R1-smooth and one R1-mode output on the smoke source);
  - stage-2b variables in the server driver.
- **Tests:** `tests/test_encoder_transfer_amendment_2b.py` (8 tests).
- **Not yet verified:** nothing has run on a GPU. The adapter check and the smoke on the new server are the first GPU checks, as in stage 2a.

### Packages
- **Unchanged:** the stage-2a pins exactly, including av 18.1.0 and the CLIP package at d05afc4.
- **Added:** `sentencepiece` and `protobuf`, because the Kandinsky 3 tokenizer is a SentencePiece T5Tokenizer. They are pinned at the installed versions by the builder.

## Cost (from the timings measured in stage 2a)

`scripts/encoder_transfer_cost_2b.py` reuses each arm's measured stage-2a time per unit. Generation at .4 is doubled, and Kandinsky 3 is bracketed at 2–8 s per output because it is unmeasured. The output is saved in `stage2b-cost-projection.json`.

| | Low | High |
|---|---:|---:|
| Raw compute | 7.2 h | 8.7 h |
| The runner's own projection (+30%, +900 s) | 9.6 h | 11.6 h |
| Setup, downloads, input upload, adapter check, smoke, model loads, return of 3 GB of images | 1.4 h | 3.1 h |
| **Instance hours** | **11.0 h** | **14.6 h** |
| **Dollars at $0.45–0.65/h** | **$5.0–7.2** | **$6.6–9.5** |

Raw compute by cell (Kandinsky 3 at 5 s):

| Cell | Raw compute |
|---|---:|
| R0 .1 | 0.58 h |
| R0 .4 | 0.68 h |
| R1 .1 | 0.81 h |
| R1 .4 | 1.13 h |
| rinse | 0.91 h |
| R3 | 1.73 h |
| R1-smooth | 1.26 h |
| R1-mode | 0.86 h |

The smoke projection on the server replaces these figures before the run.

**Budget:** the ceiling is 35 h / USD 30 for stages 2a and 2b together. The builder sets stage 2b's limits to that ceiling minus stage-2a consumption.
- **The conservative stage-2a clock** reads 25.9 h / $14.48, because it counts the period when the instance was stopped. That leaves 9.1 h, which is not enough. The runner would then apply the declared drop order: P5 first, then P4 (R3), then strength .1 with its rinse.
- **The real billed stage-2a GPU time is lower,** because a stopped instance bills storage only. For example, about 17 billed hours (about $9) would leave about 18 h / $21, which covers the high estimate.
- **The exact figure comes from the vast.ai billing page,** and the user supplies it.

## Server plan

**Machine** (the stage-2a instance is destroyed by the user):

| Requirement | Why |
|---|---|
| GPU ≥ 24 GB (RTX 4090 or larger) | Kandinsky 3's text encoder is 20.3 GiB in fp16 and is loaded alone on the GPU, once; stage 2a's peak was 11.1 GB |
| RAM ≥ 64 GB | the whole Kandinsky 3 pipeline (28.4 GB fp16) is loaded on the CPU first |
| Disk ≥ 120 GB | assets about 50 GB, environment about 10 GB, about 0.2 GB of stage-2a inputs, about 3.5 GB of new outputs |
| Fast CPU, good download, reliability ≥ .99 | detector reads dominate, and about 50 GB of assets are downloaded |

**Steps:**
1. **Rent and reach the server.** The user rents it and sends the SSH line and the actual hourly price. Hotspot Shield stays off, because it intercepts SSH.
2. **Ship the code.** The repository is private, so a byte-identical `git archive` of the pushed commit is shipped, as for stage 2a, and blob-checked on the server.
3. **Upload the stage-2a inputs:**
   - the full `rows.jsonl` (51 MB);
   - the 300 clean core and C0 images (about 130 MB), to `/workspace/runs/stage2a-full/images/`, the paths their rows record.

   Every hash is verified.
4. **Run the setup.** `scripts/encoder_transfer_server_setup_2b.sh <spent-hours> <spent-usd> "<approval>"`:
   - environment;
   - Kandinsky 3 download;
   - contract build;
   - tests.

   The two new JSON files are then committed and pushed from the laptop, and committed on the server.
5. **Start the driver in tmux:**
   `TAG=stage2b MANIFEST=research/encoder-transfer-20261019/stage2b-config.json ADAPTER_STAGE=2b ADAPTER_OUT=/workspace/runs/adapter-check-2b.json SEED_FROM=/workspace/runs/stage2a-full bash scripts/encoder_transfer_server_driver.sh <instance-start-utc> <hourly>`

   It chains prepare, the 2b adapter check, the smoke, the seed, the run (with any declared reductions), and packing. It holds on a failure, and stops (never destroys) the instance after FETCHED.
6. **Monitor.** Claude watches every 5 minutes, so that a HOLD is answered at once.
7. **Bring the results home and stop.** The results and images are copied home in hash-checked parts, verified per image against the journal, and the instance is stopped. The user destroys it.
8. **Analyze.** This produces:
   - `results-2b.md`;
   - one independent review;
   - the report script rerun on the union, so that the T7 tables and figures gain the stage-2b cells;
   - STATE and dev-log updates.

**Timeline:** about 11–15 instance hours from rental to stop, about $5–10.

## Before the run, the user decides

1. **Go-ahead.** The go-ahead for stage 2b, in words; the builder records it verbatim.
2. **Stage-2a consumption.** The stage-2a instance hours and dollars from the vast.ai billing page. Alternatively, accept the conservative 25.9 h / $14.48, which means P5 and possibly P4 are dropped by the declared order.
3. **Machine.** The machine (per the table above) and its hourly price.
