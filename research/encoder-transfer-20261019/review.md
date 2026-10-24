# Stage 2a independent review

**Verdict: ACCEPT WITH CORRECTIONS.** I recomputed the label from the raw journal: it is **FAILS, ROUTE C**. No finding blocks the label. Twelve corrections to `results.md` (numbers, wording, provenance and reporting coverage) should be made before it is cited.

Reviewer: a fresh Claude (Opus 5.5) agent with no access to the run conversation, 2026-10-24 (about 19:40Z). Document under review: the untracked `results.md` on `claude/encoder-transfer-stage2` (HEAD b4b2810). I wrote nothing else.

## What I recomputed and how

- **Journal integrity.** `rows.jsonl` has 14,014 lines, no malformed lines, and 3,840 unique ids. I kept the last record per id. That matches the 3,840 planned units, and every row's `source_id` is one of the 60 in `source-list.json` (SHA 490d3d04…, smoke ids 1790 and 1822 disjoint). `stage2a-results.tar` hashes to d5669bee…, and each of its 15 members is byte-identical to the extracted copy I read.
- **Internal endpoints.** I imported the literal `m1b_e3_s1_analysis.predicates`, stubbing numpy and scipy, which the function does not use. I applied it to every persisted `raw` detector result:
  - owner alpha with the row payload, for marked rows;
  - payload `None`, for the C0 and wrong-owner (beta) calls.
  - The persisted `endpoints` agree with the recomputation on every call (0 mismatches).
- **External endpoints.** I regenerated each source's message with SHAKE256 (seed 20261019). I re-derived k from the exact binomial tail: WAM 27/32, VINE-R 69/100, TrustMark 46/61, Pixel Seal 159/256. Then I counted bit matches in each raw `decoded_message`; TrustMark also needs `native_detected`. 0 mismatches with the persisted `presence`.
- **Statistics.** Source majority means at least 2 of seeds 12/13/14, with missing or blocked calls counted as failures. I recomputed the Clopper-Pearson intervals by my own bisection, and the exact sign tests and Holm adjustment (family v5, WAM, VINE-R).
- **Contract.** The repo `stage2a-config.json` hashes to 87e4142f…. That equals `manifest_sha256` in the smoke and full `run.json`. The contract, `effective-config.json` and both `run.json` `config` blocks are identical, and `projection.dropped` is `[]`. `extras/stage2a-config.before-av.json` differs only by `packages.av`.
- **Commits and timing.** I read `git show` for cb634d5, 90f9888 and b4b2810, then aligned the git timestamps with `driver.log`, both `run.json` files and the file mtimes.

## Decision, recomputed

| Input (R1 SDXL, strength .2) | Recomputed | Note |
|---|---|---|
| F5 source-majority C | **0/60**, CP95 [0, .0596] | 0 missing calls; optimistic 0 |
| F5 C0 calls, A | 0/180 | 180 observed |
| F5 wrong-owner calls, A | 0/180 | 180 observed |
| WAM common presence | 2/60 | — |
| VINE-R common presence | 60/60 | B = 60 |

Since 0 < 30, the label is **FAILS → ROUTE C**, and B does not enter the label. The label cannot depend on missingness: R1 has no safety checker, and all 10 blocked units are R0. TrustMark Q and Pixel Seal (both 0/60) are outside both B and the Holm family, in the code and in `metrics.json`. The stage-2b cells are absent from the journal, and `metrics.json` lists them in `not_run_by_design`. **Confirmed.**

## Other numbers I recomputed (they match `results.md` unless a finding says otherwise)

- **Primary table:**
  - R1: v5 12/60 [.108, .323]; WAM 2/60 [.004, .115]; VINE-R 60/60 [.940, 1]; TrustMark Q 0/60; Pixel Seal 0/60.
  - R0: F5 57/60 [.861, .990] (3 blocked, optimistic 58); v5 27/60 [.321, .584] (1 blocked, optimistic 28); WAM 18/60 [.188, .432] (2 blocked, optimistic 19); VINE-R 60/60 (2 blocked).
- **F5 diagnostics, S/C/Q/A:**
  - clean 60/60/52/60; X1 60/60/46/60; X2 60/60/41/60;
  - D1 60/55/31/60; D3 60/55/35/60;
  - R0 58/57/38/59; R1 0/0/0/30.
- **Carrier states:**
  - F5 R1: all 180 calls `not_found`.
  - v5 R1: 64 `not_found`, 74 `found_not_read`, 4 `read_content_mismatch`, 38 `C_success`.
  - `read_without_found` is 0 everywhere.
- **Safety blocks:** 10 units, all R0: C0 2, F5 3, v5 1, WAM 2, VINE-R 2.
- **Negatives:**
  - Every R1 negative is 0/180 with nothing unresolved, on every predicate for F5 and v5 (C0 and wrong owner) and for C0 presence of all four external arms.
  - R0: F5 C0 has 2 unresolved and F5 wrong-owner 3; v5 C0 has 2 and v5 wrong-owner 1; WAM and VINE-R C0 have 2 each. Positives are 0 everywhere.
  - Clean, D1, D3, X1 and X2: all 0/60.
- **Sign tests:**
  - F5 vs v5: 0 wins, 12 losses; raw p .000488, Holm .000977.
  - F5 vs WAM: 0 wins, 2 losses; Holm .5.
  - F5 vs VINE-R: 0 wins, 60 losses; Holm 5.2e-18.
- **Clean quality:** all six median rows match. F5 embedding takes a median 118.7 s per image (1.98 h total).
- **External diagnostics:** WAM is 60/60 on D1, D3, X1 and X2; TrustMark is 58/60 on D1; VINE-R's median bit accuracy at R1 is .90; Pixel Seal's is .5195.
- **Execution:**
  - full run 14:31:22Z to 19:19:26Z (17,280 s);
  - projection 23,477 s against 48,396 s available;
  - budget clock 93,084 s (25.9 h), USD 14.48.
- **Step 1:** SD1.5 F5 22/24 and v5 5/24; SD2.1 F5 24/24 and v5 5/24. These match `unseen-regenerator-results.md`.

## Post-freeze changes (after 6bbcd2d; all times are 2026-10-24 UTC)

| Change | When | Could it change a scientific outcome? |
|---|---|---|
| cb634d5, PyAV pin | committed 14:09:59; the smoke record (server 384d975) was created 14:11:06 with it | No. Only `packages.av` changed. PyAV is needed only to import VideoSeal, because Pixel Seal runs in image mode with an Identity augmenter. It enables a descriptive arm only. |
| 90f9888, `is_junction` fallback | 14:14:20; server 1f4b388 recorded as a bug fix 14:14:49 | No. A `getattr` fallback on Python 3.11 (Linux has no junctions); the symlink rejection is unchanged. |
| CLIP package d05afc4, `--no-deps` | freeze file 14:16; logged 14:17:08; smoke attempt 3 started 14:17:04 and ran all 128 units | No. `a6_clip_visual` checks the bytes of `clip.py` and `model.py` and the checkpoint SHA at every load, and executes only the verified `model.py`. The freeze diff adds only `clip`. |
| b4b2810, smoke projection | 14:30:15; server 19b322c recorded 14:31:17 | No. It is timing code only: blocked R0 units stay terminal, and analysis and decision code are untouched. A projection of 6.52 h against 13.44 h available cannot trigger a reduction under any timing rule. |

The first study output is the full journal. Its `run.json` was created at 14:31:23.9Z, after all four changes. Smoke outputs, on reserved sources only, existed before b4b2810, but that fix reads unit status and timing, never scores. All four changes are implementation-only.

## Findings

**Blocking:** none.

**Corrections:**

1. **Image copy is stated as done, but it is not.**
   - Evidence: `results.md` says `stage2a-images.tar` was "copied in 17 hash-checked parts". At about 19:40Z only parts 00, 01, 14 and 15 were complete locally; they match `parts.sha256`. Parts 02 and 13 were still being written. No reassembled tar exists, and `parts.sha256` lists **16** parts (00 to 15; 15 × 104,857,600 + 99,686,400 = 1.67 GB).
   - Fix: finish the copy, check all 16 parts and the reassembled tar against f02701c5…, then write "16 parts".
2. **Achieved-distortion rounding.** Three cells are rounded wrongly:
   - R1 F5 PSNR is **24.90** (24.9046), not 24.91;
   - X1 C0 PSNR is **44.45** (44.4547), not 44.46;
   - X2 F5 PSNR is **40.26** (40.26500 rounds down), not 40.27.
   - All other cells match.
3. **"The semantic carrier is absent" overstates the data.**
   - Evidence: at F5 R1, semantic score/threshold has median .33 (IQR .17 to .48) and maximum .97. At R1 C0 it has median −.05 and maximum .52. 171 of 180 F5 calls exceed the C0 median, and 39 exceed the C0 maximum.
   - Fix: say "below the semantic threshold in all 180 calls (not mis-bound)", and call any residual shift descriptive.
4. **"SDXL's diffusion step at .2 does [remove F5]" contradicts the protocol's compound-contrast caveat.**
   - Evidence: `protocol.md` says the D1/R1 contrast is compound. D1 uses the posterior mode with direct fp32 input; R1 samples the posterior after fp16 input rounding, then denoises.
   - Fix: write "the full SDXL img2img pipeline at .2", and state that caveat next to the D1/D3 bullet.
5. **The "allowed article frame" overreaches.**
   - Evidence: "fails across encoder families" generalises from one SDXL setting. T7's binding allowed conclusion says ROUTE C is "bounded to the tested SDXL configuration". `budget-and-proposals.md` P4 calls MoVQ's separate training "qualified".
   - Fix: bound the frame to SDXL img2img at .2, and qualify "independently trained" for MoVQ.
6. **The R0 replication is not on a "new" cohort.**
   - Evidence: all 24 step-1 sources are among the 60. On those 24, R0 gives F5 22/24 and v5 5/24, identical to step 1. On the 36 new sources, F5 is 35/36 and v5 22/36.
   - Fix: report the 24 and 36 split. Optionally add F5 R1 0/24 on the 24 sources where SD2.1 gave 24/24.
7. **The VINE-R claim is worded loosely and quality is reported selectively.**
   - "Same R1 outputs" should read "same R1 channel": each arm regenerates its own marked image.
   - "Better clean LPIPS (.006 against .020)" needs the other side too: PSNR is 35.14 against 44.96, and the strict clean gate passes for VINE-R on 31/60 against F5's 60/60.
   - Add the strict-gate counts that the protocol requires: F5 60, v5 60, WAM 58, VINE-R 31, TrustMark 60, Pixel Seal 60.
8. **WAM's median bit accuracy (.625 at R1) has no denominator.** It is computed over 44 non-abstaining calls; 136 of 180 calls had an empty mask. At R0 the median is .8125 over 120 calls, with 58 abstentions. State both denominators.
9. **The run commit is not identified in the repository.**
   - Evidence: 19b322c, 1f4b388 and 384d975 do not exist in the pushed branch (`git cat-file` fails), and the run folder holds nothing that shows content identity with b4b2810. BRIEF section 4 requires the commit hash to identify what ran.
   - Fix: record the tree of `19b322c^{tree}` from the server and compare it with b4b2810's tree (7bae3dcff9f451238e5a446dfe1454b290daacde), or push the server commits.
10. **Part of the binding T7 reporting plan is missing.** The protocol says the T7 eight-table, seven-figure plan is binding.
    - Evidence: `results.md` has no Table 3 per-output k/180 grid, no Table 5 ROC, no Table 6 matched distortion and no Table 7 per-arm extraction time and memory, and none of the Figures 1 to 7.
    - The matched analysis matters for the sentence "R1 .2 is milder… therefore not explained by the size of the distortion": the pre-specified R0-versus-R1 within-arm matching found **0 pairs** (not estimable) for every arm.
    - Fix: add these items, or list them as deferred with pointers into `metrics.json`. Either way, soften "therefore not explained" to "not accounted for by larger median pixel distortion".
11. **The negatives sentence is scoped incompletely.** "0/180, none unresolved" for WAM, VINE-R, TrustMark and Pixel Seal holds for R1 only. At R0, WAM and VINE-R C0 each have 2 unresolved calls. The protocol also asks for optimistic counts, but only F5's is shown: add v5 28, WAM 19 and VINE-R 60 at R0.
12. **Bug-fix provenance is worded too broadly.** cb634d5 is not in the smoke `bug_fixes`: it is the smoke's base commit, 384d975. It is recorded in `amendment-1d.md` and `driver.log`. Say so.

**Notes:**

- **N1.** b4b2810 times the 5 R0 cells blocked on smoke source 1790 from source 1822 alone, not from the "slower of two sources". This is a disclosed deviation with no consequence.
- **N2.** `clip` is absent from `requirements-stage2.txt` and from the contract's `packages`. The runtime pin check therefore does not cover it; the hash checks do.
- **N3.** The smoke `run.json` keeps a stale `error` traceback next to `outcome: smoke_completed`.
- **N4.** The A = 30/60 reading is acceptable as descriptive. It would be clearer with three facts:
  - per source, 24 sources are 3/3, 6 are 2/3, 8 are 1/3 and 22 are 0/3;
  - of the 92 instance-found calls, the instance content is 47 match, 17 mismatch and 28 uncertain;
  - the instance tier sits near threshold at R1 (median ratio 1.00) but near null at R0 (.06), while the semantic tier shows the reverse.
  - No claim should rest on it.
- **N5.** The "may not be claimed" list should add: no claim that VINE-R dominates F5 at matched quality, because clean quality is unmatched.
- **N6.** D3 covers the four core arms plus C0 (300 round trips, as in the approved P4 AE-only proposal). BRIEF 1d says "every arm". X1 and X2 were kept. Both choices are disclosed in the amendment.
- **N7.** BRIEF section 6 names a `gpt-6-astra` xhigh reviewer; this is a Claude review. The user should accept the substitution.
- **N8.** Four other items are still open:
  - the run folder name lacks HHMM;
  - `results.md` is uncommitted;
  - the dev-log, STATE and instance-stop status are not yet recorded.
