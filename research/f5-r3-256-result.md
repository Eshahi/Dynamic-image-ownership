# F5 r3-256 result — 2026-10-06 (kill under the pre-declared rule)

Rule: `research/f5-r3-256-selection.md` (9c9520d, committed before the runs).

**Setup.**
- Rented vast.ai RTX PRO 4000 Blackwell; software matches the local science venv; all 17 assets hash-verified.
- Remote snapshot of the code: a2d958f.
- Outputs copied to MAIN `.thesis-build/dev-runs/20261006-0800-remote-pro4000/`.
- After the instance was stopped, nothing remains on it except its disk.

## Results (family 1: .4/.5/.6 x 5 seeds, 20 steps, CFG 1; 12 development sources)

| run | .4 | .5 | .6 | .4+.5 | C0 / wrong-owner | PSNR / LPIPS mean (max) | clean self-verified |
|---|---:|---:|---:|---:|---|---|---:|
| B1 r2, remote | 49/58 | 36/58 | 10/57 | **85** | 0 / 0 | 44.69 / .0173 (.0502) | 12/12 |
| R1 r3-256, remote | 39/58 | 26/57 | 2/57 | **65** | 0 / 0 | 44.70 / .0171 (.0507) | 12/12 |

- B1 reproduces the local laptop run (49/37/10) within one sample, so the remote GPU is a faithful stand-in.
- C1 failure split at .4 / .5 / .6:

  | run | carrier | bind |
  |---|---|---|
  | r2 | 2 / 8 / 39 | 7 / 14 / 8 |
  | r3 | 3 / 21 / 50 | 16 / 10 / 5 |

**Decision.**
- Family 1 alone is 20 below r2 on .4+.5, so the rule's "not worse than r2 by more than 2 on either family" already fails. **r3-256 is killed.**
- The queue was stopped after R1 to save rented GPU time. B2 (r2, family 2) was interrupted partway, and R2 never ran.

## Why the prediction failed (diagnosis on the same rows)

1. **r2's .5 success leans on unchecked binding.**
   - 17 of r2's 36 successes at .5 are owner found by the recomputed pattern only. A mark too weak to be read "counts as carrying the recomputed code", so its content is never compared. At .4 that applies to only 1 of 49.
   - Counting only successes whose content was actually compared:

     | strength | r2 | r3-256 (always compares) |
     |---|---:|---:|
     | .4 | 48 | 39 |
     | .5 | 19 | **26** |

   - So under strict binding, r3 is better at .5 and worse at .4.
2. **The carrier is weaker for owner detection.**
   - r3's antipodal bits subtract when the suspect's sketch bit flips (expected factor 1 - 2θ/π, against r2's 1 - θ/π), and the soft weights lower the score further.
   - r3 owner scores at .5 have median 5.45 against a threshold of 4.98, so 21 carrier losses against r2's 8.
3. **Per-bit carrier noise biases the angle.**
   - The 256 bits get about 12-13 slots each, and the embedded margin median is about 1.5.
   - Even with no regeneration, the estimated distance is 0-2 bits on clean images and about 2 after VAE round trip. At .4 the median is 4.6, so 16 rows cross 6.
   - The binding-ceiling simulation assumed noiseless sketch bits. That assumption, not the CLIP side, is what failed: the carrier cannot deliver 256 reliable bits at a 52 dB budget.

## What this leaves

- The ceiling analysis still holds for the information the sketch carries. The bottleneck is carrier capacity per bit.
- A sketch longer than 32 bits needs either more carrier energy per bit or fewer, better-protected bits (64-128). It also needs owner detection that does not lose score to flipped bits:
  - a code-independent pilot;
  - or r2-style orthogonal options in place of antipodal bits.
- r2's .5 numbers should be reported with the split between read and recomputed-only successes. The recomputed-only path is an assumed match, not a checked one. That matters for how strongly the thesis can state binding under T3.
