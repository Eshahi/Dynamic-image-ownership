# H3 equal-T3 selection rule — 2026-10-05

Baseline: F5 r2 stress `20261005-1200-f5-stress-baseline-f5r2` — C1 semantic .4 49/58 + .5 37/58 = **86/116**, clean LPIPS mean .0172, max .050, PSNR 52 dB budget, `mask_power 0`.

Control: `20261005-1330-f5-H3-mask05` mask 0.5 at PSNR 52 — .4 38/58 + .5 23/59 = 61/117, LPIPS mean .0131 (-24%) but T3 -25 below baseline. Prior kill compared at equal PSNR only, not per plan's equal-T3 criterion.

New test: mask_power 0.5 and 1.0 at reduced PSNR budgets 50 and 48 dB, same stress grid (`.4/.5/.6` x 5 seeds, 20 steps CFG1), same detector (`--binding soft --semantic-views 7`).

Commit-before-run invariant: `scripts/f5_latent_codec.py` and `scripts/f5_stress_gate.py` unchanged for these runs; dirty check passes.

Selection rule (committed before runs):
- Find the PSNR budget at which a masked variant reaches **>=86/116** on `.4+.5` (allow 58-60 denom variation; require >=74% rounded). If none reaches, H3 fails at equal T3 as well.
- If it reaches, compare its clean LPIPS mean and max at that budget vs F5 r2 baseline.
- H3 wins only if LPIPS mean is >=15% lower (or subjective improvement on 147498 sky) **at the equal-T3 budget**, plus T4/T5 stay non-worse (checked later) and C0/wrong-owner 0.
- If a variant matches T3 only at much larger LPIPS or lower PSNR mean (<44 dB), record as not winning — no free quality.

Four ordered runs (cheapest first, commit once):
1. `20261005-HHMM-f5-H3-mask05-psnr50`
2. `20261005-HHMM-f5-H3-mask05-psnr48`
3. `20261005-HHMM-f5-H3-mask10-psnr50`
4. `20261005-HHMM-f5-H3-mask10-psnr48`

Each: `scripts/f5_stress_gate.py --psnr <budget> --mask-power <m> --binding soft --semantic-views 7 --strengths 0.4 0.5 0.6 --seeds 0 1 2 3 4 --num-inference-steps 20 --guidance-scale 1.0`.
