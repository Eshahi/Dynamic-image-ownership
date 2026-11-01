# Lean F6 protocol

Fixed by Claude on 2026-11-01, before any F6 mark or regeneration exists. Rules are in [lean-config.json](lean-config.json), and the user's decision is in [decisions/lean-user-choice.json](decisions/lean-user-choice.json). The evidence behind each choice is in [F6-DEEP-ANALYSIS.md](F6-DEEP-ANALYSIS.md). This is a development screen on 60 development sources. It uses no held-out data and authorizes no spending. The run starts only when the user starts the instance.

## Question and endpoint

Can an image-domain writer, with the F5 reader unchanged, make the semantic read survive SDXL and Kandinsky 3 regeneration at strict clean quality without false attribution?

**C is the pass bar:** semantic read and content match, as in Phase B and M2. **J, exact recovery of the original code, is reported for every arm and cell and enters no rule.** A pass therefore claims a content-bound read, not exact recovery of the original code. The 12/16 bar, the strict quality limits and the reader do not change.

## Writer changes against the approved F6

| Change | Reason | Effect on the reader |
|---|---|---|
| Rendered companion signal, in the render arms | Measured at low LPIPS | None |
| Clean and surrogate gradients get equal weight | SDXL's input gain is about 26x SD1.5's (Phase A) | None |
| Momentum .9 if the probe finds disagreeing noise draws | Noisy gradients waste the budget | None |
| SDXL .2 gets two of every three surrogate updates, instead of .1 and .2 | .1 is the easier cell | None |
| Per-image residual scaling, at most down to .5, until a quality cushion holds | Larger budgets may exceed the strict bar on some images | None; a failure stays a failure |
| No CPU offload; bf16 and no checkpointing only if the probe rule allows | Cost only | None |

All other writer settings are inherited: 150 robust and 50 refinement updates, margin 4, refinement at 58 dB, two second-tier writes, posterior mode. K3 stays out of the gradients but is seen by selection, so it is never called unseen. The approved package's `f6-codec` ablation and Stage P's noise-52 arm are dropped. Noise-52 is dropped because noise-46 against F5-budget-46 answers the same question at a usable budget.

## Stages

Each stage has its own folder and shares one unmarked regeneration per source and seed through the existing replay tape.

| Stage | Sources | Seeds | Arms |
|---|---|---|---|
| Probe | Tuning 1-2 (544, 1355) | 0 | Unmarked only: native capture and replay, first-step parity, gradient checks and timings |
| 1 | Tuning 1-4 | 0 | F5 r2; F5-budget 46, 42; render 38, 36 (with the 52 dB F5 objective); generic 46, 42, 38; noise 46, 42; noise 46 with render 38; x0 46 |
| 2 | Tuning 5-16 | 0, 1, 2 | Top 2 from Stage 1, matched control for each, F5 r2 |
| 3 | Stage S rehearsal 2+2, then screen 16+16 | 0, 1, 2 | Winner, its matched control, F5 r2, v5 r3, VINE-R, VINE-B, with T4, T5 and 8 distortions |

Native cells are SD1.5 .2, SDXL .1, SDXL .2 and K3 .2 throughout. Stage P's eight check sources stay untouched. The retained F5 reader is applied to F5 r2 and to all lean arms; F5 r2's read of the shared unmarked images serves all of them.

## Fixed rules

**Probe.** Inputs are timing, memory and gradients only, so no native outcome can influence them.

- A non-finite or zero gradient, failed replay, or out-of-memory error stops the run.
- Momentum: on for a variant if the median cosine between noise-draw gradients is below .1.
- bf16 on the surrogate path: on if time ratio is at most .7 and gradient cosine at least .95.
- No checkpointing: only if it fits with 6 GiB free and time ratio is at most .8.

**Clean gate.** A lean arm that fails strict quality on any source gets no regeneration in Stage 1. It stays listed as removed. An arm whose image or quality row is missing cannot regenerate either, but it is listed as incomplete, not failed.

**Stage 1.** An arm is eligible with strict quality on 4/4, clean F on 4/4, no wrong-owner C or F event, and mean decoded score at or above the read threshold 8.2593 on SD1.5 .2, SDXL .1 and K3. Rank by the lowest mean decoded score across the three foreign cells, then their sum, then SD1.5 .2, then lower median LPIPS, higher PSNR, higher SSIM, then arm name. Keep the top 2. Stop if none is eligible.

**Stage 2.** A finalist is eligible with strict quality on 12/12, clean F on at least 11/12 and no wrong-owner event. Rank by lowest foreign C count, their sum, SD1.5 .2 C, then the same quality order. Stop if the top arm has C below 9/12 on SDXL .1 or K3, below 9/12 on SD1.5 .2, or loses more than 1 source to F5 on SD1.5 .2. There is no runner-up.

**Stage 3.** Counts are source majorities of 3 seeds. Missing seeds give a lower and an upper count.

| Gate | Bar |
|---|---|
| C, SDXL .1 and K3 | At least 12/16 each |
| C, SDXL .2 | At least 12/16 |
| Gain over F5, SDXL .1 / .2 / K3 | At least 4 / 4 / 3 |
| Gain over the matched control, if the winner has a surrogate | At least 4 / 4 / 3, otherwise the gain is credited to the budget |
| SD1.5 .2 | C at least 12/16; loss to F5 at most 1 |
| Clean quality | Strict on 16/16 |
| Clean F | At least 15/16 |
| C0 and wrong-owner C or F | Zero |
| T4 and T5, combined mode, quality-eligible images | **Zero C events** (D and F is also reported) |

Labels:

- **FULL_GO:** every gate passes.
- **CORE_GO:** every gate passes except those on SDXL .2.
- **SCIENTIFIC_KILL:** a gate outside SDXL .2 fails.
- **INCOMPLETE** or **RESOURCE_STOP:** missing work decides the result. These are never scientific results.

The T4 and T5 gate is stricter than round 3, which counted only D and F. With C as the bar, a C event on a copy-paste image is the false attribution that matters. Human labels of operational distinctness stay missing, so the binding claim stays limited.

**Article question.** VINE-B and VINE-R results are reported beside the winner. This protocol issues no article verdict; the Round 2 article rule stays as written.

## Money

Cap: the smaller of 34 instance-hours and USD 18.7 at the actual price, on one clock from the instance start. The last hour is reserved for retrieval, and each unit checks the clock first. Before Stage 2 and again before Stage 3, measured unit times must show the remaining work times 1.25 fits; otherwise the study stops with RESOURCE_STOP and keeps what it has. There is no extension, and no source, seed or arm is cut to fit. Every stage also checks for at least 10 GB of free disk and stops with RESOURCE_STOP below that; no output is deleted to make room. A stop still writes the phase's decision file from what exists.

## What this cannot claim

No latent insertion, lightweight reader, cryptographic or legal ownership, confirmation on held-out data, universal independent-encoder survival, or human invisibility. Scales near .5 in the quality control would be reported, since they change the effective budget per image.
