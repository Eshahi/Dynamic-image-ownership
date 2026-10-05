# H3 equal-T3 result — 2026-10-05 (closed: kill)

Selection rule: `research/f5-H3-equalT3-selection.md` (6ceb11b, committed before the runs). Runs: queue jobs 001-004 (`scripts/f5_queue.py`, journal `research/f5-queue.json`). Same stress grid as the baseline: .4/.5/.6 x 5 seeds, 12 development sources, 20 steps, CFG 1, soft binding, 7 views. Analysis by Claude Code (Opus 5.5, supervisor session) after the Opus 5 workers stopped on gateway quota.

## Results

C1 semantic success (both carrier and binding):

| run | mask | budget | .4 | .5 | .6 | .4+.5 | PSNR mean | LPIPS mean / max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline F5 r2 `1200-f5-stress-baseline-f5r2` | 0 | 52 | 49/58 | 37/58 | 10/57 | **86/116** | 44.71 | .0172 / .050 |
| control `1330-f5-H3-mask05` | 0.5 | 52 | 38/58 | 23/59 | 6/57 | 61/117 | 44.64 | .0131 / .043 |
| `2100-f5-H3-mask05-psnr50` | 0.5 | 50 | 47/58 | 31/59 | 11/57 | 78/117 | 43.72 | .0165 / .049 |
| `2101-f5-H3-mask05-psnr48` | 0.5 | 48 | 44/58 | 33/59 | 20/57 | 77/117 | 42.60 | .0216 / .057 |
| `2102-f5-H3-mask10-psnr50` | 1.0 | 50 | 11/57 | 4/56 | 0/58 | 15/113 | 43.72 | .0133 / .043 |
| `2103-f5-H3-mask10-psnr48` | 1.0 | 48 | 21/58 | 12/57 | 3/57 | 33/115 | 42.62 | .0166 / .050 |

C0 and wrong-owner were 0 in every run. Denominators vary by 1-4 because the pipeline's safety checker blacked out some outputs; those rows are excluded, as in the baseline.

Failure split for C1 at .4 / .5 / .6. "Carrier" means the owner was not found; "bind" means found, but the content did not match.

| run | carrier | bind |
|---|---|---|
| baseline | 3 / 7 / 38 | 6 / 14 / 9 |
| mask 0.5 at 52 dB | 17 / 31 / 49 | 3 / 5 / 2 |
| mask 0.5 at 50 dB | 4 / 18 / 38 | 7 / 10 / 8 |
| mask 0.5 at 48 dB | 2 / 7 / 24 | 12 / 19 / 13 |
| mask 1.0 at 50 dB | 46 / 52 / 58 | 0 / 0 / 0 |
| mask 1.0 at 48 dB | 35 / 45 / 54 | 2 / 0 / 0 |

## Decision under the pre-declared rule

- No masked variant reaches 86/116 on .4+.5 at any budget tried.
- The closest one (mask 0.5 at 50 dB, 78/117) has no LPIPS advantage: .0165 vs .0172, -4%, below the 15% needed.
- **H3 fails at equal T3 as well as at equal PSNR. Closed.**

## What it shows

1. **Texture masking is anti-robust to regeneration.**
   - The more the change is concentrated in textured regions (mask power 0 → 0.5 → 1.0), the more of the carrier the regenerator removes: carrier losses at .5 go 7 → 31 → 52 at 52/50 dB.
   - Diffusion img2img re-synthesises texture, so energy placed where it is least visible is also the energy the denoiser replaces.
   - This is the regeneration analogue of the classic perceptual-masking trade-off, and a thesis-worthy negative result: perceptual masking and regeneration robustness pull in opposite directions.
2. **More pixel budget helps the carrier, not the binding.**
   - At 48 dB, mask 0.5 halves the carrier losses at .6 (38 → 24) and doubles .6 success (10 → 20).
   - At .4/.5, however, binding failures dominate and even grow (6 → 12, 14 → 19, partly because more rows now reach the binding test).
   - This confirms independently that .4/.5 are limited by binding and .6 by the carrier (see `research/ideas/binding-ceiling.md` on `claude/f5-ideas`).
