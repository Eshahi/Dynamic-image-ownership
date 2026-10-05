# H4 — Soft binding distance analysis (stress baseline 12×5, CFG 1 20 steps)

Source: stress baseline `20261005-1200` re-detected for soft/hard distances (`scripts/f5_h4_distances.py`, `research/h4-soft-distances.json`).
Re-detection with exact codec (soft, 7-view) vs hard on same attacked PNGs.

## Per-strength success

| strength | soft (found&&match) | hard | n | soft succ median (p90) | soft fails median (min) |
|---|---|---|---|---|---|
| 0.4 | 49/58 | 42/58 | 58 | 4.03 (6.14) | 6.66 (6.22) |
| 0.5 | 37/58 | 35/58 | 58 | 5.03 (10.29) | 9.09 (7.03) |
| 0.6 | 10/57 | 10/57 | 57 | 7.83 (10.78) | 8.54 (6.86) |

Soft vs hard: +7 at .4, +2 at .5, 0 at .6 — already baked into F5 r2.

## Fail distances (bits, soft_distance = θ·32/π)

- .4 fails (6 values, 3 carrier+3? actually 5 carrier? See stress baseline carrier 3 binding 6 — on this 6-value subset 1 carrier is missing threshold): [6.22, 6.43, 6.62, 6.70, 7.21, 11.59]
- .5 fails (14 values): min 7.03, max 11.40, median 9.09
- .6 fails (9 values): min 6.86, max 12.07, median 8.54

## Threshold relaxation trade-off

Clean C1 pairwise soft distances among the 12 sources (ordered 132 pairs, same code family):
mean 10.48, min 5.50, p5 6.69. Pairs ≤6: 4/132, ≤7: 10/132, ≤8: 21/132, ≤10: 62/132.

Rescued fails if semantic_radius raised:
- .4: thr 7 → 4 of 6 rescued (→ 53/58), thr 8 → 5/6 (→ 54/58)
- .5: thr 7 → 0/14 (→ 37/58), thr 8 → 4/14 (→ 41/58)
- .6: thr 7 → 1/9 (→ 11/57), thr 8 → 4/9 (→ 14/57)

Cost: raising 6→7 multiplies clean false pairs 2.5× (4→10), 6→8 5× (4→21). Direct T5 joint check at 6 is 0/66; at 7/8 would create joint collisions (needs h>6 filter, but q≤7 already introduces cross-label matches beyond plan limit ≤2/114). Plan kill: "no gain at .5 at equal FPR (different-label ≤2, T5 0)".

## Verdict

- Threshold relaxation alone is a kill for H4c at equal FPR: no gain at .5 selector (0 rescued at 7), and .4 gain is paid with 2.5× false pairs.
- Extra invariance pooling beyond 7 views was already screened in the original binding experiment: hard+7 views raised different-label matches to 6 (fails rule), soft+7 views rescued only 5 of 6 .4 fails. Further views (tested ad-hoc) do not move .5/.6 fails (their distances 7–11).
- Longer code (H4a) raises Hamming separation but also raises required redundancy; capacity is ample, but binding drift is angular (~30–50° at .5) and scales with code length — not a free gain.

**H4 closed: no replacement.** Bottleneck at .4 is partly thresholds but at .5/.6 carrier attenuation dominates (38/47 at .6 are carrier failures). Next carrier-side leverage is H2 (attack-aware PGD) or band/payload rebalancing, not binding thresholds.

## Next

Attempt H1 band re-embed probe (2–3 sources, bands 8–28/6–24 vs 4–32) to see if denoiser keeps narrower band better, then queue H2 pilot (K=1 UNet step) if band shows no headroom. Three consecutive kills (H1 filter, H3 mask, H4 threshold) approaching hard stop 1 — one more well-founded carrier experiment before readiness report.
