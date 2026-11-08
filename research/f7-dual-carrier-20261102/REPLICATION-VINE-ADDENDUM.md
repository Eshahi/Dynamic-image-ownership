# VINE-R + registry baseline on the f7c sources (f7v): frozen addendum

Claude, 2026-11-08. Frozen before any f7v output exists, and after the f7c result ([RESULTS-REPLICATION.md](RESULTS-REPLICATION.md)). The user asked for the VINE-R comparison ("prepare it") after Claude estimated its server time.

## Purpose

f7c showed that F7 as the pointer, together with the frozen round-3 registry rule, passes every gate on 64 fresh sources. A reviewer will ask whether a published regeneration-robust watermark would do as well with the same registry. This run answers that on identical data: the same 64 donors, 64 copy-paste hosts and donor-target pairs, the same cells, seeds and threats, the same distractor records, and the same rule and gates. Only the mark and its pointer change.

VINE-R is the external baseline already used in the encoder-transfer stage 2 and Phase B (VINE-R checkpoint and adapter `encoder_transfer_runtime.Vine`, unchanged). It is not a new baseline.

## Run

- **Driver:** `bash scripts/f6l_driver.sh /workspace/assets /workspace/runs/f6l START PRICE f7v`, from an archive of `claude/f7-confirm-20261107`. f7v differs from f7c only in its arms.
- **Arms:** VINE-R and unmarked.
- **Manifest:** `replication/source-manifest.json` (ee997470…).
- **Cells and seeds:** SD1.5 .2, SDXL .1, SDXL .2, Kandinsky 3 .2 and SD1.5 .4; seeds 0-2.
- **Threats:** T4 and T5 built from the VINE-R marks. There is no distortion stage.
- **Marks:** VINE-R embeds each source's public 100-bit message, `message(source, 100, 20261019)`, as in stage 2.

## Pointer and registry

- **Records:** the owner's registry holds the 64 VINE-R clean marks, each with its message, plus the same 284 distractor records (no message).
- **Pointer V:** record r is selected when the decoded message agrees with r's message in at least K = 69 of 100 bits. That is VINE-R's frozen threshold, `binomial_threshold(100)`: exact P[Bin(100, .5) ≥ 69] ≤ 1e-4 per record.
- **Rule:** the frozen round-3 rule then decides the pair, as for F7.
- **No owner-level fallback:** VINE-R's message is the record identifier, so it has no counterpart to F7's owner-presence fallback P2.
- **Wrong owner:** the attacker enrols each seed-0 copy under a record whose message is `message(source, 100, 20261020)`, the stage-2 wrong-owner message. That record is selected only if the copy decodes to it.

## Endpoints

1. **Gate label for the baseline system:** PASSES_GATES or FAILS_GATES. It uses the f7c bars:
   - F_R ≥ 55/64 on SD1.5 .2, SDXL .1 and Kandinsky 3 .2;
   - zero accepts for N1 T4 (384), N2 T5 (64), N3 wrong source, N4 C0 (1,024 unmarked) and N5 wrong owner (five cells).

   It describes the baseline. It is not a verdict on F7.
2. **Paired comparison per cell (pre-registered):** source-majority F_R of VINE-R + registry against F7 + registry (P2, from the f7c rows), on the same 64 sources, with an exact two-sided McNemar test.
   - A difference is claimed only where the Holm-adjusted p over the five cells is below .05.
   - Otherwise it is reported as no detected difference.
3. **Strict clean quality** of the VINE-R marks (PSNR > 35 dB, SSIM > .9, LPIPS < .1), against F7's 63/64, with medians.
4. **Reported:**
   - pointer-alone and rule-alone counts;
   - the median own-message agreement per cell;
   - pointer firings on negatives (fingerprint-only accepts are reported too).

**Expectation, written before outputs.** In stage 2, VINE-R read SDXL .1 in 60/60 and Kandinsky 3 in 60/60, but only 31/60 of its marks passed strict quality. So it may reach further than F7 on SDXL .2 and look worse.

The unmarked arm is regenerated again with the same seeds and read with the VINE-R decoder for C0.

## Cost and stops

- **Estimate:** about 2-2.5 h on the restarted 59588200, which already has the VINE-R weights; setup takes about a minute.
- **Stop rule:** Claude stops the run if the fit check forecasts more than 4 h in total.
- **Scoring:** on the server with `scripts/f7v_registry_score.py --distractor-features …` (the laptop-computed distractor features from f7c). The images are fetched over parallel HTTP for a laptop rescoring if the link allows.
- **Instance:** stopped from inside afterwards, never destroyed.

## Plumbing check before freezing

The scorer was run on a synthetic 8-source f7v screen built from f7c data, with the decoded message set to the source's own message exactly where F7's presence fired. It reproduced F7's P2 counts (8, 8, 8, 2 and 7), zero negatives and zero paired differences. Script: session scratch `synth_vine.py`. This checks the code path only, not VINE-R.

## Limits

- **Pointer error rate:** VINE-R's pointer works at 1e-4 per record, against F7's 1e-6. Over 64 records a chance pointer has a probability of about 6e-3 per query. The registry rule must then reject it, and N4 tests this directly.
- **Quality is not matched:** each mark runs at its own published or frozen strength. The quality difference is reported, not equalized.
- **Development data,** 64 sources. It has the same E2, registry-scale and human-review limits as f7c.
