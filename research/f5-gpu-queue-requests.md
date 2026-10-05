# F5 GPU queue requests (claude/f5-ideas, 2026-10-05 21:18 UTC)

GPU lead: git fetch origin claude/f5-ideas && git show origin/claude/f5-ideas:research/f5-gpu-queue-requests.md
One GPU at a time (RTX 5070 Ti 12GB). Science venv: .thesis-build/a6-science-venv/Scripts/python.exe
Repo root: W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5
Selection: T3 improves on stress grid, T4 0/20, T5 0/66, clean LPIPS mean<=.0173 max<=.050

## #1 Phase 0 CPU shootout (0 GPU, or 3 min GPU if p_j not stored)
Goal: pick winner among {A-P3 list+CRC, C-2 soft LDPC, A-P2 weighted} on existing stress images.
Commands:
  .thesis-build/a6-science-venv/Scripts/python.exe scripts/f5_h4_distances.py --input-dir .thesis-build/dev-runs/20261005-1200-f5-stress-baseline-f5r2 --output research/ideas/cpu-shootout-p0.json
  # then CPU rescoring script over h4-soft-distances.json: Chase-3 list and weighted LLR, measure rescue vs FPR 132 pairs
Kill: rescue <+2 at .4 and <+1 at .5 at FPR<=2/114.

## #2 Phase 1 binding pilot (single pilot, ~8 min GPU)
4 sources 1675,6012,147498,468505 x .4/.5 x 5 seeds = 40 rows, PSNR 52, soft 7-view.
If helper-in-carrier winner:
  .thesis-build/a6-science-venv/Scripts/python.exe scripts/f5_gate.py --psnr 52 --binding soft --semantic-views 7 --helper-bits 8 --sources 1675,6012,147498,468505 --output-dir .thesis-build/dev-runs/20261005-21xx-f5-p1-binding
  .thesis-build/a6-science-venv/Scripts/python.exe scripts/f5_stress_gate.py --output-dir .thesis-build/dev-runs/20261005-21xx-f5-p1-binding --psnr 52 --binding soft --semantic-views 7 --strengths 0.4 0.5 --seeds 0 1 2 3 4 --num-inference-steps 20 --guidance-scale 1.0
If detector-side list only: f5_h4_distances.py --list-radius 8 --chase 3 --output research/ideas/p1-list-reread.json
Also: f5_t4.py and f4_t5.py on same pilot dir.
Promote if paired +2 at .4 and +2 at .5 at FPR<=current; kill if T4>0/20 or T5>0/66.

## #2-alt Phase 2 carrier pilot (only if Phase1 leaves .5<45/58 or .6 needed)
Choose ONE: A-P1 concatenated code sim then re-embed OR B-geo2 band reshaping probe then re-embed. See full ranked file for commands.
Kill if delta <+2 at .5 at equal LPIPS or LPIPS max>.050

## #3 Phase 3 perceptual stack (only after #1/#2 locked, at equal LPIPS)
  .thesis-build/a6-science-venv/Scripts/python.exe scripts/f5_gate.py --psnr 50.5 --binding soft --semantic-views 7 --perceptual-weight csf --sources 1675,6012,147498,468505 --output-dir .thesis-build/dev-runs/20261005-21xx-f5-p3-csf
Kill if latent gain <1.15x at LPIPS match or 147498 sky >.055

All pilots: commit code before run, produce run.json, append experiments/dev-log.md, one GPU job, dev data only.
