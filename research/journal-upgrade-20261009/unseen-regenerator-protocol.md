# Step 1 protocol: frozen transfer comparison

Prospective 2026-10-16; authoritative design is NEXT-GOAL-20261014.md. Step 1a is explicitly post-hoc, read-only analysis of retained M2 endpoints. Step 1b uses exactly the 24 development sources from fresh-development-selection.md. E3 saved full marks, frozen F5 r2 supplier marks if settings match, freshly embedded native v5 r3. Quality is unmatched. All clean PSNR/SSIM/LPIPS and construction time distributions are reported.

SD1.5 DDIM20 with frozen safety checker and SD2.1-base revision 4e63672c03103b6c636b8fb4119ba982469b2955 without safety checker; empty prompt, guidance 1, eta 0, strengths .1/.2/.4, seeds 12/13/14. Nominal 20 steps (2/4/8 effective). Compare full VAE weights and encoder tensors to disclose shared encoding. Only pinned safe tensors/configs downloaded, about 2.415 GB new.

SDXL full regeneration is omitted prospectively: the desktop has 10.67 GiB free GPU memory; its roughly 7 GB fp16 base parameters plus fp32 1024-pixel VAE activation peak, resident reader and GPU workspaces do not establish safe fit within this 12 GB shared desktop GPU. No offload/tiling implementation experiment is allocated within the fixed budget. This is conservative feasibility omission, not a measured OOM. Existing SDXL VAE-only control remains in step 2.

Own-owner C1, wrong-owner C1 and shared regenerated C0 read by all three unchanged detectors. Frozen M2 predicates S,C,Q,J,H,F,A; full source denominator 24, missing/safety-blocked positives fail, missing negatives unresolved. Source majority is at least 2 of exactly 3 assigned seeds. Source is the paired unit; paired one-sided exact sign tests for E3>F5, E3>v5 and F5>v5 are exploratory, with Holm correction across all 18 model/strength/comparator tests. No significance test overrides the selection rule.

Primary selection: E3 remains only if SD2.1 .2 source-majority C exceeds F5 by at least 3/24. Otherwise F5 primary. All other cells descriptive. Report SD1.5-minus-SD2.1 C transfer drop. All C0/wrong-owner A counts clustered by source; no rare population FPR claim.

Local USD 0, maximum 5 GPU-hours total including prepare, resumable per-image journals and immutable completed outputs, no held-out execution. Scientific errors retained, implementation repairs documented without retuning. Run code committed before use. One final independent review for steps 1 and 2, none per round.
