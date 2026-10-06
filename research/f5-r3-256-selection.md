# F5 r3-256 selection rule (committed before any run) — 2026-10-06

Author: Claude Code (Opus 5.5, supervisor session), at the user's request ("do the 256 bit test"). Development data only (the 12 development sources); held-out data untouched.

## Hypothesis

The binding-ceiling analysis (`research/ideas/binding-ceiling.md` on `claude/f5-ideas`) found that F5 r2's T3 binding loss at .4/.5 comes from the 32-bit CLIP sign sketch. On the same data, a 256-bit sketch reached the ideal CLIP-angle ceiling. r3-256 (`scripts/f5_r3_codec.py`) carries such a sketch:
- **Carrier:** 256 antipodal bit chips over F5's latent band.
- **Owner detection:** a soft-weighted recomputed correlation, a normalised Rademacher sum with the unchanged single-pattern threshold 4.982.
- **Binding:** a soft maximum-likelihood angle from per-bit carrier LLRs and the suspect's projections, with the unchanged radii 6/10 in 32-bit units.
- **Unchanged from F5 r2:** everything else, including the fragile tier, the PSNR budget, the PGD steps and the refine round.

CPU sanity check before any GPU use:
- unmarked latents score mean 0.005, sd 1.04, max 3.31 over 400 draws (threshold 4.982);
- another owner's score stays at about 0;
- on synthetic marks, the estimated angle tracks the true angle at margins 1-8.

## Runs

Both codecs run on the rented GPU (vast.ai RTX PRO 4000 Blackwell), with the same software versions as the local science venv (torch 2.12.1+cu130, diffusers 0.35.1). All 17 assets were verified against the a6 asset lock hashes. GPU outputs are not bit-identical to local runs, so every comparison here is paired on the remote GPU. One GPU job runs at a time.

| run | codec | family |
|---|---|---|
| B1 | r2 (F5 r2, target margin 4.0) | 1: .4/.5/.6 x seeds 0-4, 20 DDIM steps, CFG 1, empty prompt |
| R1 | r3-256 (target margin 4.5, energy-matched: 320 x 4.0^2 ≈ 256 x 4.47^2) | 1 |
| B2 | r2 | 2: same, 50 steps, CFG 7.5, prompt "a photo" |
| R2 | r3-256 | 2 |

Command template:

```
scripts/f5_stress_gate.py --codec <r2|r3-256> --psnr 52 --binding soft --semantic-views 7 --strengths 0.4 0.5 0.6 --seeds 0 1 2 3 4 [--num-inference-steps 50 --guidance-scale 7.5 --caption "a photo"]
```

## Decision

The primary endpoint is C1 semantic success (owner found and content match, owner alpha) on .4 + .5, per family. .6 is reported but not used.

r3-256 **wins** only if all of these hold:
1. **Gain.** The .4+.5 total summed over both families is at least r2's + 8, and r3-256 is not worse than r2 by more than 2 on either family's .4+.5.
2. **Controls.** C0 found 0 and wrong-owner found 0 in every cell.
3. **Clean.** 12/12 clean C1 found with content match. The fragile tier's both_match self-verification is reported.
4. **Quality.** Clean LPIPS mean at most 1.10 x r2's on the same run pair, and clean PSNR mean at least 44 dB.
5. **T4/T5.** These run only if 1-4 pass, and are required before any adoption:
   - T4: 0 false attributions on the residual-transfer pairs;
   - T5: 0 joint semantic+instance collisions among distinct development covers (q256 soft distance ≤ 6 and H ≤ 6).

r3-256 is **killed** if its summed .4+.5 total is at or below r2's.

**Prediction** (binding ceiling; it assumes that the carrier delivers the bits):
- family 1: .4+.5 from about 86 to 95-99;
- family 2: from about 55 to 70-80.

A smaller gain would mean the per-bit carrier reliability, not the sketch, limits r3.
