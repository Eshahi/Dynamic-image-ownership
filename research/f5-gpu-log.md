# f5-gpu progress — 2026-10-05

## 20:50 UTC — resume at xhigh
- Branch `claude/f5-gpu` at 6ceb11b (H3 equal-T3 selection). WT clean. Previous session had enqueued nothing; queue script missing — creating it now.
- Plan: H3 equal-T3 (4 runs), second stress family (50 steps CFG 7.5), longer semantic code (64/128-bit), H2 pilot. Queue `scripts/f5_queue.py` with journal `research/f5-queue.json`, detached PowerShell so jobs survive.

## 20:58 UTC — queue infra
- Wrote `scripts/f5_queue.py` (journal + single-GPU loop). Committing next.

## Baseline reference
- Stress baseline F5 r2 `20261005-1200-f5-stress-baseline-f5r2`: C1 semantic .4 49/58, .5 37/58, .6 10/57, clean LPIPS .0172, PSNR 44.7 mean.
- Control H3 mask0.5@52 `20261005-1330-f5-H3-mask05`: .4 38/58, .5 23/59, .6 6/57, LPIPS .0131.

## Selection (committed 6ceb11b)
- H3 equal-T3 needs >=86/116 on .4+.5. Four runs at PSNR 50/48 × mask 0.5/1.0.

## Queue
- (to be filled after commit)
