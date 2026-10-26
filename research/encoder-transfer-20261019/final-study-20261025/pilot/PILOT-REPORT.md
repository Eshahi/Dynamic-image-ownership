# Final-study Phase-A feasibility pilot: report

Written by Claude (Opus 5.5) on 2026-10-26. The user approved the pilot, verbatim: "start it, and when it ends, stop the instance". This implements the bounded, detector-sealed pilot of `../07-final-experiment.md` section 4 and `../analysis/mechanism-server-spec.md` section 7, on the six fixed development sources. **No detector read any marked output. No scientific setting was chosen. No held-out data was used.**

## Verdict

**Every required path is technically feasible on one RTX 4090, in native fp16 precision.** This covers:
- noise capture and replay;
- the full-chain forward-mode JVP for SD1.5, SDXL and Kandinsky 3;
- the encoder JVPs;
- attacks A and B.

It needs three declared implementation changes in the derivative path, listed below. **One protocol issue needs a decision before Phase A:** the derivative path agrees with the native trajectory to a relative 3×10⁻⁴–1.5×10⁻³ per step. That is above the 10⁻⁴ consistency tolerance the specification fixes, and the specification says to stop an adapter that exceeds it rather than widen the tolerance.

**Projected full study:**

| Phase | Hours (30% margin plus setup and retrieval) | USD at 0.448/h | USD at 0.45–0.60/h |
|---|---|---|---|
| A | ≈ 17.0 | ≈ 7.6 | 7.7–10.2 |
| B | ≈ 44.9 | ≈ 20.1 | 20–27 |

Both are inside the proposed ceilings (A ≤ 40 h, B ≤ 60 h).

## Execution

| Item | Value |
|---|---|
| Machine | vast.ai container 57583551, the stage-2b instance restarted by the user: RTX 4090 24 GB, Ryzen 9 5950X, 62 GB RAM, USD 0.448/h |
| Instance time | started 2026-10-26 07:00:20Z, stopped from inside at about 07:32Z: about 0.53 h, about USD 0.24 (plus storage while stopped) |
| Pilot compute | debug runs (R0 only) about 3 min; main run about 2.2 min; second run (R1, K3) about 1.8 min. Far below the 2-hour pilot cap |
| Code | `scripts/et_final_pilot.py`, branch `claude/et-final-pilot`. Commits 194862b, then f46eadf (main run, sha 518b8e59…), then 2d1df82 (second run, sha 4875064…). The server repository was the stage-2b archive (61904a1) plus this script |
| Environment | torch 2.7.1+cu128, diffusers 0.35.1, transformers 4.53.3, the pinned stage-2b assets already on the instance (no download) |
| Sources | 127, 902, 73, 908, 1637, 471: the first six of the 60 development sources in the protocol's SHA-256 order (`et-final-law-split-v1/`) |
| Run folder | MAIN `.thesis-build/dev-runs/20261026-0705-et-final-pilot/`: `et-pilot-results.tar` (sha fff247f9…), extracted in `results/`. All three journals are kept, failures included |

## Findings by check

### Noise capture and replay: exact

- **Capture.** Every `randn_tensor` draw of a native call was captured in call order:
  - SD1.5 and SDXL: posterior noise, then injection noise;
  - Kandinsky 3: injection noise, then four DDPM step draws.
- **Replay.** Replaying them with a different generator seed reproduced the native RGB8 output bit for bit: **18/18** (6 sources × 3 families, C0, strength .2, seed 12), with every captured draw consumed. The F5 input then ran with C0's draws, shape-checked and never read.

### Schedules: as specified

- **R0 and R1** (DDIM 20, leading, offset 1, scaled-linear):

  | Strength | Executed steps | Starting timestep |
  |---|---|---|
  | .05 | 1 | 1 |
  | .1 | 2 | 51 |
  | .15 | 3 | 101 |
  | .2 | 4 | 151 |
  | .4 | 8 | 351 |

  ᾱ at the start is .9505 at .1 and .8264 at .2.
- **K3 .2:** DDPM with `squaredcos_cap_v2`, timesteps 151, 101, 51 and 1, ᾱ = .9393.

### Full-chain F5 tangent (the H4 path)

The tangent runs around the captured C0 trajectory:
1. the exact paired encoder displacement `d = sf·[(m1−m0)+(s1−s0)·η]` (SD), or the MoVQ latent difference (K3);
2. the injection `a_t·d`;
3. a forward-mode JVP through each native denoiser step (DDPM steps replay their captured draws);
4. one JVP through decode, the Lanczos 1024→512 resize, the F5 reader's fp32 SD1.5 encoder, and the fixed linear chip operator `Layout.projections`.

| Family, strength | Unit time (projection basis) | Per-step JVP | Decode + reader JVP | Peak allocated |
|---|---|---|---|---|
| R0 SD1.5 .4 (8 steps) | 2.73 s | 0.18–0.28 s | 0.27 s | 5.0 GB |
| R1 SDXL .4 (8 steps) | 7.11 s | 0.55–0.65 s | 1.17 s | 15.3 GB |
| R1 SDXL .1 (2 steps) | 3.19 s | 0.56 s | 1.15 s | 15.3 GB |
| K3 .2 (4 steps) | 3.65 s | 0.26–0.27 s | 2.10 s | 16.6 GB |

- **Starting state:** it reproduces the native first UNet input exactly (relative error 0) in all three families, once the SDXL input follows the native fp16 rounding before the fp32 encode.
- **Tangents:** they are finite in every successful chain, all in native precision. The fp32 fallbacks were never needed.
- **Tangent norms** (`‖v‖`, chip units): R0 8.2 and 22.1; R1 .4 40.9 and 28.1; R1 .1 23.0; K3 9.2 and 6.0. These are technical diagnostics, not outcomes.

**Declared implementation changes in the derivative path only.** Native generation is unchanged.

1. **Attention.** PyTorch's flash SDPA kernel has no forward-mode derivative, and its math kernel returns fp32 for fp16 inputs under forward AD. The JVP path therefore uses diffusers' classic `AttnProcessor` (bmm/softmax).
2. **LayerNorm.** fp16 `nn.LayerNorm` emits an fp32 tangent under forward AD. The JVP path uses an explicit LayerNorm that computes in fp32 and casts back.
3. **Unit tangent.** The raw tangent overflows fp16, which in the first runs gave NaN in the SDXL UNet and in the SD1.5 decoder. Each step and the decode therefore propagate a unit-norm tangent, rescaled in fp32 afterwards. This is exact by linearity of the JVP.

**The protocol issue.** Relative state error against the captured native states, per step:

| Family | Range |
|---|---|
| R0 | 3.0×10⁻⁴ to 8.4×10⁻⁴ |
| R1 | 2.6×10⁻⁴ to 1.5×10⁻³ |
| K3 | 5.7×10⁻⁴ to 9.5×10⁻⁴ |

The gap comes from the attention kernel and LayerNorm differences in fp16, and grows along the trajectory. The specification fixes 10⁻⁴ and says to "record mismatch and stop that adapter rather than widening the tolerance". By that rule the H4 adapter does not pass as written. Options, to be decided before Phase A and recorded as a pre-outcome technical amendment:
- **(a) Recommended.** Generate the C0 and marked trajectories of the new study with the same deterministic attention and LayerNorm implementations as the derivative path. Primal identity then holds by construction (to be verified by replay in Phase A), and the new study's native pipeline differs from stage 2's default kernels only at fp16 rounding level.
- **(b)** Pre-register a justified wider tolerance (for example 2×10⁻³), stating the kernel cause.
- **(c)** Declare H4 unsupported and run the core without the law.

**Floating against RGB8 reader path.** On C0 only, the chips of the floating decode path differ from the chips read from the native RGB8 output by 1.6–7% of the chip norm (relative):

| Family | Relative difference |
|---|---|
| R0 | 1.6–3.4% |
| R1 | 3.8–5.3% |
| K3 | 5.3–7.1% |

Sources: rounding to RGB8, the float Lanczos surrogate and the kernel differences.
- **Lanczos surrogate:** against PIL on a real 1024 image, max absolute .013 and mean .001 in [0,1] units; 86.8% of values equal after rounding.
- **Effect on the law:** it uses the native RGB8 chips as the background b and the float path only for v. This discrepancy bounds how exactly v can describe RGB8 chip changes, and Phase A must report it. Nothing here was used to choose anything.

### Encoder JVPs (mechanism module)

Unit directions along the actual F5 residual:

| Encoder | Time | Gain (native units, descriptive) |
|---|---|---|
| SD1.5 fp32 at 512 | 0.13 s | 17.6, 78.3, 10.2 |
| SDXL fp32 at 1024 | 0.56 s | 566, 1476, 241 |
| MoVQ fp16 at 1024 | 0.77 s | 4.1, 15.0, 3.2 |

- **Units differ** by resolution and latent scaling, so these gains are not comparable across encoders without the normalization the specification requires.
- **MoVQ** needed the unit direction (the raw direction overflowed fp16).
- **Control directions** (two Gaussian, two Fourier-phase; CPU, 0.16 s) matched the residual norm to 1×10⁻¹¹ and the per-channel Fourier magnitude to 1.2×10⁻¹¹. 4.7–4.8% of `x + direction` would leave [0, 1]; reported, not clipped.

### Attack adapters (timing only, outputs never read)

- **A (SDXL then SD1.5, equal strengths):** per chained output 0.68 s at .05, 0.76 s at .1, 0.84 s at .15 and 0.92 s at .2.
- **B (one fixed setting, ε = .075, λ = 1):**
  - cached 20-step DDIM inversion: 0.44 s (timesteps 1…951 as specified);
  - 20 optimization steps with fp32 decoder backward and float LPIPS: 2.5–2.6 s;
  - peak 8.6 GB;
  - codec control: 0.004 s.
- **Optimizer movement at this one setting** (technical diagnostic, not a selection input): the proxy cosine moved little, .716 → .701 and .520 → .492. Phase A's quality-only grid will show whether the larger ε and λ settings move it. No setting was chosen here.

### Memory

- **Peaks:** SDXL chain 15.3 GB; K3 chain 16.6 GB.
- **One K3 out-of-memory** occurred in the first main run (21.1 GB allocated, fragmentation after an earlier chain). It did not recur with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, which the full study must set.
- **Model load:** K3's full pipeline needs about 21 GB on the GPU during the one prompt encode, as in stage 2b.

### Storage

- **Per law unit:** captured draws plus the native states are about 0.3 MB (R0), 1.4 MB (R1 .4) and 1.2 MB (K3).
- **Phase B:** about 5 GB if kept. They should stay on the server with hashes and receipts, not be retrieved.
- **Saved outputs:** about 0.41 MB each. That is about 5 GB in Phase A and 12.7 GB in Phase B, which at the measured home download rate (about 0.85 MB/s) takes about 1.6 h and 4.2 h.

## Projection of the full study

From `projection.json` (`project_schedule.py` on the merged valid journal). Basis:
- maximum measured path times;
- the planned counts of 07, 05 and the mechanism specification;
- Codex's historical native and detector subtotals from the stage-2 journals;
- a 30% margin;
- setup and loading 1.5 h per phase;
- retrieval 2.0 h (A) and 4.5 h (B).

| Component (hours, before margin) | Phase A | Phase B |
|---|---|---|
| Historical native, clean and quality/detector assessment | 5.80 | 23.59 |
| F5 law JVPs (1,080 / 4,200 units) | 1.01 | 3.97 |
| Mechanism: 720 encoder JVPs, 540 differential chain JVPs, 1,620 stage outputs | 0.10 + 0.49 + 0.59 | — |
| Attack A (grid 2,880 / selected 3,000) | 0.64 | 0.77 |
| Attack B (grid 2,160 + fidelity; selected 1,000 + fidelity 1,000) | 1.77 | 1.58 |
| **Compute** | **10.4** | **29.9** |
| **With margin, setup and retrieval** | **≈ 17.0** | **≈ 44.9** |

**Limits of this projection:**
- **Not the law's real workload.** The JVP unit times are from two sources per family and one strength each. Other strengths scale by measured per-step cost.
- **Historical subtotals.** The native and detector parts are historical stage-2 subtotals, not re-measured here.
- **Not included:**
  - quality metrics for the attack grids beyond those subtotals;
  - reruns after failures;
  - the waiting time between phases (instances stopped, storage only).

## What this pilot does not establish

- **No prediction accuracy.** It says nothing about whether the transfer law predicts anything; no prediction was made.
- **No attack effect.** It says nothing about whether attacks A or B remove any mark.
- **No numerical equivalence** of the derivative path to the native fp16 kernels within 10⁻⁴: it is not established, and needs the decision above.
- **No FLUX:** FLUX was not tested (gated, optional).

## Decisions for the user

1. **Primal-consistency issue:** option (a) recommended, (b), or (c)?
2. **Phase A:** approve it, at about 17 instance-hours, about USD 7.6 at 0.448/h, on the same or an equivalent RTX 4090 machine (≥ 64 GB RAM; the 76 GB disk of this instance fits Phase A's assets and outputs)?
3. **Phase B:** remains a separate decision after the Phase-A freeze, at about 45 instance-hours, about USD 20.
