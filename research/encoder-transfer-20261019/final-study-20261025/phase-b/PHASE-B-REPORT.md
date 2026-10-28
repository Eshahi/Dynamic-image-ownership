# Final study, Phase B: report

Written by Claude (Opus 5.5) on 2026-10-28, from the completed Phase-B run on 200 held-out sources. Phase B ran under [AMENDMENT-B1.md](AMENDMENT-B1.md), which was frozen before acquisition. The user's approval is quoted there: run Phase B, law derivatives on SD1.5 only, a cap of 50 instance-hours, and the held-out acquisition after a rehearsal on development sources.

- The analysis output is copied unchanged into [phase-b-tables.md](phase-b-tables.md) and [phase-b-results.json](phase-b-results.json).
- The frozen source list is [phase-b-sources.json](phase-b-sources.json).
- Nothing in this report was refitted, re-thresholded or reselected after an outcome was seen.

## 1. What ran

**Machine.** vast.ai instance 57877693: RTX 4090 (49,140 MiB reported; peak use about 19 GB), Xeon Gold 6338 (16 effective cores), 76 GB disk, USD .551/h.
- It was up from 2026-10-26 22:11Z and stopped (not destroyed) at 2026-10-28 01:22:48Z, after retrieval. That is 27.2 instance-hours, about USD 15.0.
- An earlier instance was used for part of the setup before it was stopped; by the session notes that was about 2–2.5 h.
- The total stays well inside the 50-hour cap. The vast.ai bills are authoritative.

**Code.** The server ran branch `claude/et-final-pilot` at 3afb06b. Every Phase-B script and amendment file on the server was hash-identical to the committed version (`scripts/et_final_phase_b.py`, `_read.py`, `_driver.sh`, and the six files in this folder).

**Timeline** (`driver.log`, UTC):

| Stage | Start | End | Rows |
|---|---|---|---|
| Rehearsal (development sources 1790 and 1822, separate folder) | 10-26 | before 10-27 01:21 | passed; not part of any result |
| Acquisition, first start | 10-27 01:21 | 01:23 | stopped on Wikimedia HTTP 429 (exit 1) before any source list was frozen |
| Acquisition (paced, Retry-After honoured) | 01:25 | 06:52 | 240/240 downloaded and checked; first 200 frozen, 0 failures, 0 replacements |
| Clean marking (six shards) | 06:52 | 13:44 | 1,000 ok (4 marks + C0 × 200) |
| Forecast and seal | 13:44 | 17:03 | 4,200 C0 trajectories: 4,180 ok, 20 safety-blocked; 1,800 R0 B1 forecasts sealed |
| Outcome | 17:03 | 10-28 00:22 | 17,800: 17,686 ok, 114 safety-blocked, 0 errors |
| Detector release | parallel | 00:27 | 36,606 ok, 0 errors |
| Quality | parallel | 00:27 | 21,866 ok, 0 errors |
| Analysis | 00:27 | 00:27 | `PHASE_B_COMPUTE_DONE` |

**Integrity.** Before the instance was stopped, every output file was hashed against its journal row: 1,000 clean, 4,180 C0 and 17,686 marked/control files, all matching. The files were then fetched as deterministic tar batches, each checked against a server-side SHA256 (section 9).

**Safety blocks.** These are recorded and never bypassed or retried. All are in SD1.5 (R0); there are none in R1, K3 or the control.

| Cell | C0 | Marked outputs (all arms) |
|---|---|---|
| R0 .1 | 9 | 44 |
| R0 .2 | 7 | 40 |
| R0 .4 | 4 | 30 |

**Engineering changes during the run.** No change touched a frozen choice, a threshold or a scientific setting.

- **Acquisition** (47f06a1, fcd37b1): honours Wikimedia's HTTP 429 Retry-After and paces original downloads at 20 s. A network failure now stops the stage instead of consuming reserves. The first attempt stopped before any source list was frozen.
- **Clean marking** (af71124): optional sharding (six processes), merged before forecasting.
- **Detector threads** (8b338e0): thread counts come from environment variables.
- **Parallel F5/v5 detector readers** (3afb06b), added during the outcome stage. One F5 reader took about 1.9 s per row on a fraction of the cores. Four hash-partitioned reader processes raised detector throughput from .53 to 1.24 rows/s.
  - Rehearsal check before deployment: 167 F5/v5 rows were re-read with the new code. All were ok, with zero differences in any discrete field (only timing fields differ).
  - A CUDA out-of-memory error in a reader would be journaled as `transient_retry` at most twice per id, then `error_terminal`. None occurred.
  - The old single reader process was stopped to switch over. A row is written only after its read completes, so the interrupted read was simply redone and no completed row was lost.

## 2. Confirmatory family (Holm, α = .05, 13 slots)

| Slot | Claim | Observed | p | Holm threshold | Status |
|---|---|---|---|---|---|
| H2 | F5 R0 .2 source-majority C retention > .80 | 182/200 = .91 | 1.8 × 10⁻⁵ | .05/13 = .0038 | **SUPPORTED** |
| H6 | VINE-R known-message presence > .90 in each of R0 .2, R1 .1, R1 .2 | 194, 200, 200 | 1.5 × 10⁻⁴ | .05/12 = .0042 | **SUPPORTED** |
| H3 | Joint dominance-and-loss event on > .80 of sources | 163/200 = .815 | .335 | .05/11 = .0045 | INCONCLUSIVE |
| H1 | F5 possible-majority retention < .10 at both R1 .1 and R1 .2 | 19/200 = .095; 0/200 | .466 | .05/10 = .005 | INCONCLUSIVE |
| H4 | Law beats the quality comparator | – | 1 | | UNEVALUATED (comparator `BASELINE_UNAVAILABLE`, fixed in Phase A) |
| H5 × 8 | Attacks A/B remove each mark | – | 1 | | UNAVAILABLE (attacks quality-ineligible, fixed in Phase A) |

The Holm procedure rejects H2 and H6 and stops at H3.

- **H2.** F5 survives SD1.5 img2img at strength .2 on 91% of held-out sources. The lower end of the exact one-sided 95% bound is above .80.
- **H6.** The VINE-R positive control survives in all three cells.
- **H3.** The point estimate (.815) is just above the .80 null, but far from significant. Its components:
  - R1 .1 loss (Y⁺ = 0): 181;
  - R0 .2 retention (Y = 1): 182;
  - all six quality triples complete: 195;
  - R1 .1 strictly milder than R0 .2 on LPIPS, PSNR and SSIM: 193.
  The binding components are the two detector events, not quality.
- **H1.** R1 .2 is at 0/200. **R1 .1 is at 19/200** (55 of 600 seed calls positive, no unresolved call), just under the .10 boundary, so the null (some rate ≥ .10) cannot be rejected. Development had 0/60 at R1 .1 (section 7).

## 3. Negative gates

No stratum passes the frozen gate, because the gate needs **zero events and zero unresolved sources**. Every stratum has 4–8 unresolved sources, all from the safety-blocked outputs above; a missing negative call is unresolved, not negative.

| Stratum | Events f | Unresolved u | Gate | Complete count lies in |
|---|---|---|---|---|
| F5 C0 / wrong owner | 0 / 0 | 4 / 8 | incomplete | [0, 4] / [0, 8] |
| v5 C0 / wrong owner | 0 / 0 | 4 / 6 | incomplete | [0, 4] / [0, 6] |
| WAM C0 / wrong message | 0 / 0 | 4 / 5 | incomplete | [0, 4] / [0, 5] |
| VINE-R C0 / wrong message | 0 / **1** | 4 / 8 | incomplete / **failed** | [0, 4] / [1, 9] |

- **F5, v5 and WAM:** no false event was observed in any executed cell, seed or control. With the unresolved sources counted as events, the conservative one-sided 95% upper bounds are 4.5% (C0, u = 4) and 5.2–7.1% (wrong query, u = 5–8). A complete zero would have given 1.5%.
- **VINE-R:** one wrong-message event on held-out data. Together with the historical development C0 event (69/100 at threshold 69), there is no clean specificity claim for VINE-R. As the contract says, this does not affect H6, which is a retention claim.

## 4. Source majorities (descriptive)

Each arm is read by its own detector; Y is all-attempt and Y⁺ is possible-majority.

| Cell | F5 r2 | v5 r3 | WAM | VINE-R |
|---|---|---|---|---|
| R0 .1 | 186 / 190 | 163 / 166 | 120 / 123 | 195 / 200 |
| R0 .2 | 182 / 186 | 122 / 124 | 51 / 54 | 194 / 198 |
| R0 .4 | 140 / 142 | 28 / 30 | 7 / 8 | 158 / 161 |
| R1 .1 | 19 / 19 | 173 / 173 | 136 / 136 | 200 / 200 |
| R1 .2 | 0 / 0 | 47 / 47 | 20 / 20 | 200 / 200 |
| R1 .4 | 0 / 0 | 0 / 0 | 0 / 0 | 174 / 174 |
| K3 .2 | 61 / 61 | 189 / 189 | 132 / 132 | 200 / 200 |
| clean | 196 | 199 | 200 | 200 |
| B-codec control | 194 | 194 | 167 | 200 |

The held-out pattern is the development pattern:
- Under SD1.5, F5 keeps more than v5 and WAM. Under SDXL and Kandinsky 3, it keeps the least of the four.
- v5 and WAM degrade with strength under both families.
- VINE-R keeps the most everywhere.

## 5. Exploratory B1 law (outside Holm)

| Cell | Identified | Law positive | Actual positive | Rate error | Worst mismatch | Brier | Margin coverage at q90_R0 |
|---|---|---|---|---|---|---|---|
| R0 .1 | 197 | 166 | 186 | −.102 | 27 | .122 | .974 |
| R0 .2 | 198 | 139 | 182 | −.217 | 50 | .237 | .964 |
| R0 .4 | 198 | 38 | 140 | −.515 | 110 | .545 | .973 |

- **Direction.** The SD1.5-only law, κ_R0 = .935623, underpredicts survival, and more so at higher strength. This is the same direction it already showed on development data when it was frozen.
- **Margins.** The per-trajectory margin interval at q90_R0 covers about 97% of actual margins, above its nominal 90%. The band is conservative, but the majority forecast is biased.
- **Limits.** Under B1 this result cannot be called a validated law and cannot enter H4. It was not refitted.

## 6. Quality (descriptive)

**Clean embedding, d(u, x)** (medians, n = 200 each):

| Mark | LPIPS | PSNR (dB) | SSIM |
|---|---|---|---|
| F5 r2 | .035 | 45.1 | .982 |
| v5 r3 | .030 | 36.5 | .976 |
| WAM | .033 | 38.4 | .987 |
| VINE-R | .008 | 34.7 | .995 |

**In every cell, including the codec control, F5's outputs have the largest median LPIPS of the five inputs.** This holds both against the marked input, d(y, u), and against the original, d(y, x). For example at R0 .2:

| Input | d(y, u) | d(y, x) |
|---|---|---|
| unmarked | .154 | .154 |
| F5 | .187 | .214 |
| v5, WAM, VINE-R | .159–.172 | .166–.172 |

So the regenerators change F5-marked images more than unmarked ones. That is consistent with F5 placing its residual in the most amplified encoder direction, but this table does not test it. Median PSNR differs by less than 1 dB between arms in every cell. Full medians are in [phase-b-tables.md](phase-b-tables.md).

## 7. Held-out against development (descriptive, not a test)

| F5 source-majority C | Development | Held-out |
|---|---|---|
| R0 .1 / .2 / .4 | 60 / 57 / 39 of 60 (1.00 / .95 / .65) | 186 / 182 / 140 of 200 (.93 / .91 / .70) |
| R1 .1 / .2 / .4 | 0 / 0 / 0 of 60 | 19 / 0 / 0 of 200 (.095 / 0 / 0) |
| K3 .2 (stage 2b R3 .2, same configuration) | 5 of 60 (.083) | 61 of 200 (.305) |

- **SD1.5.** Within sampling error of development.
- **Foreign families.** F5 keeps more on the held-out Commons Picture-of-the-Day photographs than on the development sources: 19/200 at SDXL .1 against 0/60, and .305 against .083 at Kandinsky 3 .2.
- **Interpretation.** The two source pools differ in more than one way, so this is a population difference, not a mechanism finding. It is also the reason H1 is inconclusive: its .10 boundary was chosen when development showed no SDXL retention at all.

## 8. What Phase B supports

**Supported at family-wise α = .05:**
- F5 retains its content-bound C on more than 80% of held-out sources under native SD1.5 img2img at .2 (H2).
- VINE-R is a working positive control in R0 .2, R1 .1 and R1 .2 (H6).

**Observed but not established:**
- F5's near-total loss under SDXL: .095 at .1 (H1 inconclusive), 0 at .2 and .4.
- The joint "milder distortion yet loss" reversal on 81.5% of sources (H3 inconclusive).

**Not evaluable:**
- the mechanism forecast (H4);
- the informed attacks (H5).

**Specificity:**
- No false F5, v5 or WAM event was observed in any executed cell, seed or control. The zero-event gates are nonetheless incomplete, because of the SD1.5 safety blocks.
- VINE-R fails its wrong-message gate (1 event).

In the terms of the statistics contract (section 8), this is a reproducible transfer limitation with a failed mechanism forecast, not a validated law or a general ownership guarantee.

- F5's robustness belongs to the writer's own encoder family.
- SDXL at .1 removes F5 on 181 of 200 sources, although on 193 sources its outputs are closer to the marked input than SD1.5 at .2, which F5 survives on 182.
- That reversal is observed but, at the frozen .80 bar, not established (H3).

## 9. Retrieval

Everything is in MAIN `.thesis-build/dev-runs/20261027-0121-et-final-phase-b/`, with hashes in its `run.json`:
- `xfer/<group>/` holds tar batches of at most about 48 MB. Each tar's SHA256 matches the server manifest, and the groups together list all 27,576 files of the run folder.
- `results/` holds the unpacked journals, logs and analysis.
- `xfer/rehearsal/` holds the rehearsal folder as one verified tar.
