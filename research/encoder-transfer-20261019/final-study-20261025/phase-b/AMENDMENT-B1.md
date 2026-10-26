# Amendment B1: Phase-B execution after the Phase-A freeze

Written by Claude (Opus 5.5) on 2026-10-26, after the Phase-A freeze ([PHASE-A-FREEZE.json](../phase-a/PHASE-A-FREEZE.json)) and **before any Phase-B pixel is acquired**.

**User decisions, given in chat on 2026-10-26:**
- "میخوام فاز B رو هم اجرا کنیم" (run Phase B).
- Law derivatives "فقط SD1.5" (SD1.5 only, as a declared exploratory amendment).
- A server cap of 50 instance-hours, including the rehearsal.
- Approval of the held-out acquisition: the 240 POTD identifiers may be downloaded to the server and used, after the code has been rehearsed on development sources.

This file and [amendment-b1.json](amendment-b1.json) are committed before acquisition. Nothing below is chosen from a Phase-B outcome.

## 1. Confirmatory family: unchanged

The 13-slot Holm family at α = .05 stays as frozen in [confirmatory-statistics.md](../analysis/confirmatory-statistics.md). Two parts of it are already settled by the Phase-A freeze:

- **H4: `UNEVALUATED_PREREQUISITE_FAILURE`, p4 = 1.** The six-feature comparator is `BASELINE_UNAVAILABLE`, and an unavailable primary baseline prevents primary H4 evaluation. The pooled law is also falsified on development data.
- **H5 (eight slots): p = 1.** Both attacks are `INACTIVE_QUALITY_INELIGIBLE`.
- **Live slots:** H1, H2, H3 and H6, with their frozen estimands, endpoints, missingness rules (Y, Y⁺ and the H3 joint indicator) and exact binomial p-values.
- **Negative gates:** unchanged (section 7 of the statistics contract). For F5 and v5 the event is any-carrier A; for WAM and VINE-R it is known-message presence. The source-any battery covers every executed cell, seed and control.

## 2. What is executed, and what is not

| Block | Phase B | Reason |
|---|---|---|
| Clean: four marks + C0 on 200 sources | executed | protocol |
| Native cells R0 .1/.2/.4, R1 .1/.2/.4, K3 .2; seeds 12/13/14; five inputs | executed | protocol (4,200 trajectories, 21,000 outputs) |
| A, A-first, B, B-fidelity | **not executed** | inactive by the frozen quality rule; no fallback |
| B-codec control (five inputs, one output each) | executed | selection-free control, descriptive and in the negative battery |
| Pooled-κ law forecasts for all 4,200 trajectories | **not computed** | H4 is unevaluable and the pooled law is falsified; the result would be a constant no-survival forecast |
| B1 exploratory law for the 1,800 R0 trajectories | computed and sealed before marked outputs | user decision (section 3) |
| Comparator probabilities | not computed | `BASELINE_UNAVAILABLE` |

## 3. The B1 exploratory law (outside the Holm family)

- **The law.** p̂ = b + κ_R0 · v on the three SD1.5 cells only. v is the full-chain JVP tangent around the C0 trajectory, using the exact paired encoder displacement of the F5 marked input; b is the C0 output's chips. The forecast is read through the unchanged soft-binding semantic reader with the C0 seven-view descriptor as the proxy, using C = read and content match, then the three-seed majority.
- **Fitted values** (frozen estimator, weights and coverage rules, restricted to R0; [amendment_b1.py](amendment_b1.py)):
  - **κ_R0 = 0.935623** (`FIT_QUALIFIED_INCOMPLETE`; 88/87/88 of 90 vectors, every triplet ≥2/3).
  - **q90_R0 = 8.6565** native decoded-score units (`RADIUS_CONSERVATIVE_FINITE`; 28/30 complete calibration sources).
- **Development agreement** (descriptive; source majorities, law vs actual):

  | Split | R0 .1 | R0 .2 | R0 .4 |
  |---|---|---|---|
  | Fit | 26 vs 30 | 21 vs 29 | 7 vs 17 |
  | Calibration | 28 vs 30 | 21 vs 28 | 5 vs 22 |

  The amended law already underpredicts survival at .2 and .4 on development data. This was known when B1 was frozen.
- **Phase-B reporting** (descriptive only): per-cell prediction-rate error mean(a − Y), worst-case mismatch count, the 0/1 Brier score, and per-trajectory margin coverage |M_actual − M̂| ≤ q90_R0.
- **What B1 cannot claim:** it cannot be called a confirmed or validated law. It cannot enter, replace or rescue H4. It cannot be refitted on Phase B.

## 4. Acquisition and canonicalization

Acquisition follows [heldout-selection-rule.md](../heldout-selection-rule.md) and 07 section 2, on the server only.

1. **Download.** Fetch each identifier's original file from its manifest URL in frozen order, with a descriptive user agent and about one request per second. Verify the byte size and SHA1 against the manifest, then record the raw SHA256.
2. **Licence persistence.** Re-query the Commons API for each file's licence label. A changed or missing reusable licence is an acquisition failure.
3. **Canonicalization.** Use **`m1b-canonical-rgb512-v2`**, the development sources' canonicalization: EXIF transpose, ICC to sRGB, receipted conversion of L/P/CMYK/YCbCr, Pillow BICUBIC 512×512 without crop. An undecodable or unsupported file is an acquisition failure.
4. **Exact-identity exclusion.** Compare the raw SHA256, canonical PNG SHA256 and RGB8 SHA256 against every recorded 64-hex SHA256 in the project's development and held-out ledgers. Also check for duplicates within the new pool.
5. **Reserves and freeze.** A failure is replaced by the next reserve in frozen order. Once the clean marking starts, no replacement is allowed. The final 200 and every failure reason are frozen in `phase-b-sources.json`, before any marking.
6. **Identifiers and storage.** Source IDs are Commons page IDs. Phase-B canonical sources live in their own assets folder, never mixed with development sources. Pixels are not viewed by the agent.

## 5. Execution order and sealing

1. **Clean.** Marking of the 200 sources (stage-2 adapters, configuration and payloads), plus clean-embedding quality d(u, x).
2. **Forecast.** For all 4,200 trajectories:
   - the C0 native output with every random draw recorded (option-(a) kernels), with the noise tape stored on the server;
   - for R0, the B1 tangent, chips and descriptor, and the per-seed forecast.
   The stage ends with `forecast-seal.json`, which holds the SHA256 of the forecast journal and the complete inventory.
3. **Outcome.** This stage refuses to start without a valid seal. It produces the four marked outputs per trajectory, replaying C0's tape, plus the B-codec control.
4. **Detector release and quality.** Detection runs on clean, native and control outputs: each arm with its own detector, and C0 with all four. Quality is computed as T7 d(y, u) and d(y, x).
5. **Retries and stop rule.**
   - At most two retries, with the identical request, for recognized transient infrastructure errors.
   - Safety blocks, deterministic out-of-memory errors and invalid outputs are recorded and never bypassed.
   - If the 50-hour cap would be exceeded, execution stops with an incomplete, reported result; no cell is selectively dropped.

## 6. Rehearsal

Before acquisition, the complete chain is run on the two reserved development smoke sources (1790 and 1822). Its outputs stay in a separate folder and are not part of any result. The rehearsal may fix code; it cannot change a frozen choice.
