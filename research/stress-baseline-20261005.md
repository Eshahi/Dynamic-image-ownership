# Stress baseline — F5 r2 (20 steps, CFG 1, 12 sources × 5 seeds)

Run: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261005-1200-f5-stress-baseline-f5r2` (commit 1a2536c, psnr 52 dB, soft/7-view, band 4–32).
Attack: pinned SD1.5 DDIM img2img, 20 steps, empty prompt, guidance 1.0. Seeds 0–4.

## Results (C1, semantic_success = found && content_match)

| strength | completed | semantic | both_match | missing (safety) | carrier fails | binding fails |
|---|---|---|---|---|---|---|
| 0.4 | 58/60 | 49 (84%) | 0 | 2 | 3 | 6 |
| 0.5 | 58/60 | 37 (64%) | 0 | 2 | 7 | 14 |
| 0.6 | 57/60 | 10 (18%) | 0 | 3 | 38 | 9 |

Scores (median): .4 score 10.2 thr 8.26 rec 8.7; .5 score 8.5 thr 8.26 rec 6.3; .6 score 4.2 thr 4.98 rec 4.2.
Outcomes distribution (alpha only, all .4–.6 pooled): semantic_only 108, neither 48, content_uncertain 20, content_mismatch 9. both_match never on attacked (instance tier fragile by design; expected).

C0: 0 false at all strengths/controls. Quality: PSNR mean 44.7 min 43.3, LPIPS mean .0172 max .050, self_verified 12/12.

## Headroom vs gate

Gate (.1 29/29, .2 28/28, .4 23/28 on 3 seeds) vs stress (.4 49/58 on 5 seeds): consistent (~84%). .5 and .6 are unsaturated selectors. Gate remains non-regression; stress is the selector per plan §0+16.

## Reading for next hypotheses

- .4 bottleneck still binding (6/9); .5 also binding-heavy (14/21); .6 flips to carrier (38/47). So H4 (binding) targets .4/.5, H1/H2 (carrier) needed for .6.
- both_match 0 confirms instance tier not a selector — T3 decision is semantic_only under regeneration, as intended.
- Matched-filter (H1) on this baseline predicts +1.1 dB only — not enough to move .5 counts materially.

Next: H3 mask sweep, H4 calibrated soft threshold, then band sweep if needed.
