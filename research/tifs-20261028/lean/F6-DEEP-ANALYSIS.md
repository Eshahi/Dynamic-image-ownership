# F6 deep analysis: cost, accuracy and a USD 20 plan

Claude (Opus 5.5), 2026-11-01, at the user's request. No server, GPU or new marks were used. All new measurements are CPU analyses of saved development images and journals; scripts are in [analysis/](analysis/). The approved package and receipt f32a322 are unchanged, and nothing here authorizes a run.

Labels: **measured** comes from saved data, **derived** is arithmetic on measured numbers, and **estimate** is my judgment.

## 1. Answer

- **Cost: yes.** A lean version of F6 fits USD 20. It costs about 14 to 27 instance-hours (USD 7.65 to 14.83), or 33.6 h (USD 18.53) with a 25% margin. If the first stage fails, the study stops at USD 3.91 to 5.77. The approved package does not fit: Codex's middle scenario is 126 h, and my earlier anchored figure is 35 to 45 h of raw work.
- **Accuracy: probably on endpoint C at SDXL .1 and Kandinsky 3, possibly at SDXL .2.** The evidence supports a larger robust budget, a surrogate, and a low-cost rendered companion signal. None of them has been run through a real regenerator yet.
- **The gate as written is close to unreachable.** It requires J, exact recovery of the original 32-bit code, on 12 of 16 sources in every foreign cell. J needs a decoded score of about 14. F5 itself misses that bar on its home family.

My estimates for a complete run, conditional on no infrastructure failure:

| Outcome | Estimate |
|---|---|
| An arm beats F5 on SDXL .1 and K3 in Stage 1 | about 70% |
| C at least 12/16 on SDXL .1 and K3, with strict quality | 40-50% |
| C at least 12/16 on all three foreign cells | 15-25% |
| The full C and J gate | under 5% |
| An article edge over VINE-B | at most 5% |

I do not adopt Codex's 35% and 10%. Its gate model explicitly assumes C equals J on every source ([r3-gate-analysis.md](../design/r3-gate-analysis.md)), and section 3 shows that they differ a lot.

F6 would not close the thesis gaps named earlier: latent insertion and a lightweight reader. Its writer also becomes 4 to 8 times slower than F5.

## 2. Why F5 fails on foreign regenerators

**Measured, Stage 2 development journal, 60 sources, F5 reader on F5 marks.** The score is normalized and saturates at the square root of 320, about 17.9. Signal-to-noise per chip follows from it: s/n = cos / sqrt(1 - cos^2), with cos = score / 17.89.

| Cell | Median recomputed score | s/n | Gain needed for C (s/n .42) | Gain needed for J (s/n 1.25) |
|---|---:|---:|---:|---:|
| Clean | 14.99 | 1.54 | | |
| SD1.5 .2 | 11.80 | .88 | none | 1.4x |
| SDXL .1 | 3.52 | .20 | 2.1x | 6.2x |
| SDXL .2 | 1.64 | .09 | 4.6x | 13.6x |
| K3 .2 | 4.03 | .23 | 1.8x | 5.4x |

These are medians. Passing 12/16 needs about 10 to 20% more, because three quarters of sources must cross (derived from the between-source spread).

**Measured, coherent frequency response.** For each mark, I compared the marked-minus-unmarked difference before and after regeneration with the same seed, per spatial band (16 Stage-P tuning sources, 3 seeds). H is the fraction carried through coherently. Chip share is how much of the clean reader signal that band of F5's residual delivers on its own (6 sources).

| Band, cycles per image | F5 energy | F5 chip share | H SD1.5 .2 | H SDXL .1 | H SDXL .2 | H K3 .2 | VINE-R energy | VINE-R H SDXL .2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 8-16 | .8% | .006 | 1.80 | .55 | .47 | .40 | 4.9% | .89 |
| 16-32 | 1.1% | .008 | 1.12 | .43 | .37 | .39 | 12.1% | .71 |
| 32-64 | 4.3% | .079 | 1.16 | .33 | .23 | .40 | 31.8% | .62 |
| 64-128 | 45.9% | .209 | .12 | .46 | .36 | .27 | 32.8% | .60 |
| 128-256 | 43.5% | .358 | .02 | .20 | .13 | .10 | 11.2% | .59 |
| 256+ | 3.7% | .015 | .01 | .00 | .00 | .00 | .1% | .23 |

What this shows:

- F5 puts 89% of its energy above 64 cycles per image, and the reader signal comes from there too. SDXL carries only .13 to .36 of it.
- On SD1.5 the input's high-band pattern does not pass through coherently (H .02 to .12), yet the reader keeps .758 of a clean margin of about 1.01. SD1.5 turns the mark into a latent pattern and renders it again as new image content, with H above 1 below 64 cycles per image. SDXL does not do this for F5's pattern. H therefore measures coherence with the input, not reader signal, and the two can differ.
- **VINE-R carries .59 to .60 through SDXL in these same high bands.** Frequency alone therefore does not decide survival; the structure of the residual does. This is the best evidence that a surrogate could help: raising F5's H there to VINE-R's level would be roughly 2x to 4x on the main signal (derived, not demonstrated, and subject to the caveat above).
- I tested one explanation for VINE-R, that it follows the image's own structure. The image-like part of F5's residual does survive better (H .53 against .24 at SDXL .2), but it is only 2.8% of the energy. VINE-R's image-like share is only 14%, and its remainder still has H .64. So this does not explain VINE-R; the cause is unknown.
- After SDXL .2, the kept reader margin is .076, against about 1.01 clean. It sits mainly at 32-256 cycles per image (.019, .027, .017). Bands below 32 give only 15% of it.

**Posterior sampling is not the cause** (measured): SDXL with the posterior mode has total H .243, against .247 with sampling. SDXL's codec alone keeps total H .54, and K3's codec .63.

## 3. The J bar

**Measured, all F5 rows in Stage 2.**

| Decoded score | P(C) | P(J) |
|---|---:|---:|
| 8-10 | .71 | .02 |
| 10-12 | .89 | .25 |
| 12-14 | .94 | .54 |
| 14-16 | .99 | .98 |
| 16-18 | 1.00 | 1.00 |

J per attempt is already .87 on clean F5 marks, .63 at SD1.5 .2 and .52 after the SDXL codec alone. At source level F5 has J 20/30 at SD1.5 .1 and .2, below the 75% that 12/16 requires. Weak code segments make this worse: distances between the two bit patterns range from 2 to 8 of 10 chips, and error rates are higher at low distance (.035 against .009 at SD1.5 .2).

**J is about 3x harder than C in signal amplitude** (derived). In a simple error model ([jmodel.py](analysis/jmodel.py)), rebalancing the writer toward weak segments saves about .9 dB at 80% exact recovery, so it does not rescue the bar. A code with all segments at distance 10 saves about 3.7 dB, but it changes the reader.

C is the endpoint used in Phase B and M2. **Decision for the user before any output:** make C the pass bar and report J separately, or keep both and accept that the likely result is a J failure. Changing it narrows the claim to a content-bound read, without exact recovery of the original code.

## 4. Quality budget

**Measured, 6 sources.** F5's final residual has RMS 1.59. Its gray part (equal in R, G and B, which includes all of the second tier) has RMS 1.51 and LPIPS .0262. The chroma part, which only the robust tier writes, has RMS .51 and LPIPS .0019. The full mark has LPIPS .0299. So the second tier causes most of F5's LPIPS, and the 52 dB robust tier is a small part of it.

**Measured earlier, robust tier only, 12 sources, 8-16 c/i pattern (`research/f5-encoder-amplified-latent.md`).**

| Robust budget | LPIPS median (max) | Clean signal | Score after SD1.5 .4 |
|---|---|---:|---:|
| 52 dB | .0054 (.015) | 15.9 | 18.8 |
| 46 dB | .020 (.068) | 26.5 | 37.4 |

LPIPS grows nearly with the square of amplitude (exponent about 1.9, derived). Extrapolating: about .048 at 42 dB and about .113 at 38 dB, before the second tier is added. So for F5-style high-frequency energy, **46 dB is about the ceiling** under "every source LPIPS below .1", and 42 and 38 dB should fail unless the surrogate moves energy elsewhere. PSNR is not the limit: 38 dB robust still gives about 37 dB final (derived). Half of Stage P's search is likely to fail on quality alone. SDXL scaling at higher budgets is unmeasured.

**Measured, decoder-rendered companion signal.** I rendered the reader's own chip pattern through the SD1.5 decoder and added it to the original, with no optimization.

| Variant | Mean margin | Recomputed score | LPIPS mean (max) |
|---|---:|---:|---|
| F5 full mark | +1.013 | 14.61 | .0299 (.0888) |
| Render, all radii, 38 dB | +.225 | 4.68 | .0085 (.0191) |
| Render, all radii, 36 dB | +.283 | 5.79 | .0137 (.0322) |
| Render, radius below 16, 38 dB | +.055 | 1.02 | .0069 (.0169) |

Rendering is much cheaper in LPIPS per unit of distortion and takes seconds. 41% of its energy lies below 32 c/i, where H is higher. **It has not been run through any regenerator.** Stronger low-frequency content may also carry over more easily in copy-paste (v5's key was delivered in 18/20 T4 tests), so T4 must be measured.

## 5. Where the money goes

**Measured.**

| Operation (RTX 4090) | Time |
|---|---:|
| F5 write | 118.7 s |
| v5 write | 6.0 s |
| Native SD1.5 .2 / SDXL .1 / SDXL .2 / K3 .2 | .41 / .81 / 1.30 / 1.29 s |
| SDXL codec forward, 1024 px | .68 s |
| Overall native rate in Phase B, with overhead | 1.48 s per image |
| F5 detector row, one process | 1.6 s |

- **Parallel writers do not help.** In Phase B, six parallel writers took 732 s each, which is 122 s per write. Writing is GPU limited. The detector is CPU limited: four processes raised it from .53 to 1.24 rows/s.
- **Codex's time assumptions are wrong in both directions** (derived). The UNet graph is cheaper than assumed (about .7 to 1.5 s against 3 to 20 s). The SDXL VAE graph is dearer than its fast scenario (about 2.5 to 6 s against 1 s).
- **x0 costs about 20% more than noise, not 2 to 3 times more.** Anchored writer estimates: generic 201 s, noise 468-838 s, x0 548-1,013 s. No GPU backward pass has been timed yet; Stage 0 measures them.
- **The per-update CPU offload should be unnecessary on this 48 GB card**, which removes up to 11,100 UNet round trips. The probe must confirm that peak memory fits.

**How the study shrinks.**

| Item | Approved package | Lean plan | Why it is safe |
|---|---:|---:|---|
| Configurations searched | 8, all at full cost | 12 cheap-first arms on 4 sources | Measured quality limits; cheap arms run first |
| F6 writes, all surrogates | 144 | at most 70 | Cheap arms and early stops |
| Native images | 5,640 | about 2,440 | See the next two rows |
| Seeds while tuning | 3 | 1 in Stage 1 | In the four F6 cells, one-seed majority error is at most 3.4% for F5 and 13.3% for v5 (measured) |
| Repeated unmarked regeneration | 136 units | one per source | Same tape; deterministic |
| Final screen arms | 11 | 7 | Mechanism ablations and WAM carry no primary gate; Phase B has WAM numbers |
| Native parity replays | 96 | one source | A code check, not a science result |
| Sources in final screen | 16 + 2 rehearsal | 16 + 2 rehearsal | Unchanged |

## 6. Accuracy levers, ranked

| # | Lever | Evidence | Expected effect | Added cost |
|---|---|---|---|---|
| 1 | Robust budget 52 to 46 dB | Measured on SD1.5 | 1.7x to 2x, if SDXL scales alike | None |
| 2 | Surrogate through SDXL (F6 itself) | VINE-R's H shows the route exists | Up to 2x to 4x on the main signal; may be far less | Write 4x to 7x slower |
| 3 | Rendered companion at 36-38 dB | Clean reader and LPIPS measured | +.10 to +.17 kept margin (assumes H .45 to .6) | About 5 s per write |
| 4 | Per-image quality control | M2 worst LPIPS is .104 at 52 dB | Lets larger budgets pass on every source | One extra pass when needed |
| 5 | Optimizer suited to noisy gradients | SDXL tangent is nearly orthogonal to the real change, cos .02 (Phase A); F5's step rule assumes a steady gradient | Unknown; Stage 0 measures it | None for momentum |
| 6 | Sample SDXL .2 twice as often as SDXL .1 | SDXL .1 is the easier cell (measured) | Small | None |
| 7 | Low-pass limit on the writer | Measured H and chip share give about 1.6x per unit RMS for 64-128 over 128-256; [Sharma et al.](https://arxiv.org/abs/1903.00073) report a related effect in classifier attacks | About 1.6x at best | None |

Momentum is an established way to improve transfer in iterative attacks ([Dong et al.](https://arxiv.org/abs/1710.06081)). I read only the abstracts of these two papers, and neither studies watermarks or diffusion.

**Not useful:** more parallel writers, sampled instead of mode posterior, and restricting a rendered pattern to very low radii (measured margin .055).

**Linear forecast (derived, unmeasured).** Median-source s/n, starting from the kept margins at SDXL .1, SDXL .2 and K3 of .169, .076, .200, with chip noise .76. The budget row uses 1.67x. The render row assumes H .6, .45 and .49. C needs .42.

| Writer | SDXL .1 | SDXL .2 | K3 .2 |
|---|---:|---:|---:|
| F5 r2 | .22 | .10 | .26 |
| Budget 46 dB | .37 | .17 | .44 |
| Budget 46 dB + render 38 dB | .55 | .30 | .58 |
| + surrogate doubling retention (K3 1.3x) | .92 | .47 | .72 |

C could pass everywhere only if all levers work. J (1.25) stays out of reach in every row.

## 7. The USD 20 plan

Hardware and price assumed: vast 57877693, RTX 4090, USD .5512/h, which is the last known price and not a quote. USD 20 buys 36.3 h. Hard cap: **34 h or USD 18.7, then stop the instance**. Storage fees are extra. Source partitions stay as committed, and Stage C stays out.

| Stage | Work | Hours | USD |
|---|---|---:|---:|
| Setup | Check instance, disk, code hashes | 1.5-3.0 | .83-1.65 |
| Probe | Time every graph, including bf16 on the SDXL VAE; gradient agreement between noise draws | .75 | .41 |
| 1 | First 4 tuning sources, 1 seed, 12 arms, 4 native cells | 3.8-5.7 | 2.11-3.15 |
| 2 | Next 12 tuning sources, 3 seeds: top 2 arms, matched budget control, F5, C0 | 2.9-8.4 | 1.57-4.60 |
| 3 | 16 + 2 Stage-S sources, 3 seeds: winner, budget control, F5, v5, VINE-R, VINE-B, C0; T4, T5, distortions | 4.0-8.1 | 2.18-4.46 |
| Retrieval | Journals, marks and a sample of images only | 1.0 | .55 |
| **Total** | | **13.9-26.9** | **7.65-14.83** |

**Stage 1 arms:** F5 r2; F5-budget 46 and 42; generic 46, 42 and 38; F5 plus render 38 and 36; noise 52, 46 and 42; x0 46. Cheap arms run first. An arm that fails strict clean quality gets no native run. Generic is included as a candidate because it needs no SDXL graph.

**Rules to fix before any output:**

- **Probe:** a non-finite gradient or out-of-memory stops the run. If the median agreement between noise-draw gradients is below cos .1, noise and x0 use momentum throughout.
- **Stage 1:** rank arms with strict quality on 4/4 by the lowest mean decoded score across SDXL .1, SDXL .2 and K3. Stop if no arm reaches mean decoded 8.26 on both SDXL .1 and K3.
- **Stage 2:** use the committed lexicographic ranking, restricted to the chosen endpoints. Stop if the winner has C below 9/12 on SDXL .1 or K3.
- **Stage 3:** C at least 12/16 is reported per cell. A full GO also needs gains over F5 of 4, 4 and 3, strict quality on every source, clean F at least 15/16 and zero qualifying negative events. A winner that uses a surrogate must also gain over the matched budget control; otherwise the gain is credited to the budget. Missing work stays RESOURCE_STOP or INCOMPLETE, never a scientific result.
- **No lowering of 12/16, and no threshold or reader changes.**

**Code changes needed, none of them run yet:** drop per-update offload; one shared C0; a one-seed mode; the render and per-image quality options in the writer; momentum; new arm list and stage drivers; updated forecast and tests. A new receipt replaces f32a322 before any output.

## 8. Limits of this analysis

- H and chip share describe the current marks. They do not predict what a new writer will reach, and the forecast assumes linear scaling that Phase A contradicts for SDXL tangents.
- All band and render tests use small samples: 16 sources for H, 6 for the reader tests. One-step and render numbers are not PGD results.
- Sources: H and CPU tests used only Stage-P tuning sources. The score, J and seed tables are aggregates over all 60 development sources, including Stage-S partitions, which already have a development history. No per-source outcome from these tables selects anything. No Stage-S source was used to choose an arm.
- Phase B: I read only write durations from its marking logs. `PHASE_B_JOURNALS` stays off, and no held-out result or journal was read.
- T4 and T5 under stronger marks are unmeasured and are the main safety risk. Human visual review is missing.
- GPU times for F6 graphs are estimates until the probe.

## 9. Reproduction

Scripts in [analysis/](analysis/); run with `.thesis-build/a6-science-venv/Scripts/python.exe`, with the GPU hidden for the VAE tests (`CUDA_VISIBLE_DEVICES=-1`). Saved outputs are in [analysis/outputs.md](analysis/outputs.md) and `analysis/spectral.json`.

| Script | Produces |
|---|---|
| `spectral.py` | Frequency response per arm and cell |
| `coherence.py` | Image-like share and its survival |
| `bandgain.py` | Reader signal and LPIPS by band; gray and chroma split |
| `bandmap.py` | One-step reader response by band |
| `render.py` | Surviving signal by band; rendered companion |
| `scores.py`, `jcode.py`, `jmodel.py`, `seedvar.py` | Scores, J and code distance, code model, seed agreement |
| `timing.py` | Measured write and native times |
| `lean_cost.py` | The cost table |
