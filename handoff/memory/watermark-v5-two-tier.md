---
name: watermark-v5-two-tier
description: "v5 two-tier codec (2026-10-02/03), now revision 3 (embedder only): design, where code/docs/package live, synthetic results, measured limits, what the user must decide"
metadata:
  node_type: memory
  type: project
  originSessionId: d1bce69e-28e0-43b9-bbe9-67cfb5d9780b
  modified: 2026-10-03T15:14:09.378Z
---

On 2026-10-02 the user (unavailable, "ask nothing") asked Claude to improve the algorithm from a Perplexity brief; later "continue", "continue until you reach an acceptable result", and on 2026-10-03 "continue improving the algorithm with the same (complete) permissions". Result: `scripts/revised_watermark_v5.py` REVISION 3, DETECTOR_REVISION 2 (main checkout, untracked), `research/method-amendment-v5.md` (sections "Revision 2", "Revision 3", "Engineering evidence"), decision record `research/method-amendment-decision-20261002.md` (judgement calls 1-10). Package: worktree `C:/Users/Soroush/.codex/worktrees/v5-study/...`, branch `claude/v5-two-tier-study`, local commits f9087a2 (r1), a1c2d71 (r2), baeb218 (r3), `experiments/c4-v5-two-tier-regeneration-v1/runbook.md`.

**Why:** v4 r2 marks vanished at the VAE round trip; r1 kept the robust key through the VAE on only 9/16 synthetic hosts; r2 fixed VAE/0.05 but img2img 0.1-0.4 stayed below the 9-in-10 target.

**How to apply / facts worth keeping:**
- r2 design (robust tier): informed slot weights (mask*w*g/n), whitening 2, caps 2 x mask + fill to 35.5 dB, pixel shaping, Bentkus-Dzindzalieta thresholds 4.98 / 8.26.
- r3 (embedder only, same detector config id): design_gain 0.5 -> 0.2 (less host rejection, more key pattern; matches img2img retention ~0.2-0.3), fill_order 2 (quiet blocks first), embed_rgb colour "proportional" (constant chromaticity, offset 10) with the PSNR floor on RGB error. With dg 0.5 / fill 0 / equal it reproduces r2 bit for bit.
- r3 vs r2 paired (same keys): score up for 80-93% of outputs, +9-15% at 0.1, +13-19% at 0.2; counts move a few hosts. 9-in-10 still only VAE and 0.05. Strong arm 33 dB: 18/20 at 0.1 but 3/20 admissible.
- Measured limits (lab, dev hosts): retention flat (~0.3 at 0.1), regeneration noise grows with texture (4.7 vs 14.3 raw), so quiet blocks are ~10x more valuable per error but cap-limited; oracle reallocation <= 1.22; smooth carriers retained better but same score per RMS; texture-energy marks host-interference-limited. Conclusion: gap at 0.1-0.4 is the 35 dB / visibility budget.
- Rejected in r3: detector without mask, normaliser-ordered fill, luminance-masked caps, clipped robust reading, wider bands (max5-7), whitening 1.5/2.5, two-pass, min-norm colour (tints), raised caps in busy blocks (visibility risk, not adopted).
- Side effects: within-composition whole-mark copy test now content_uncertain (was mismatch); blur/JPEG occasional content_uncertain.
- Lab tools: `dev_v5_lab.py` (variant keys positions, colour, cap_hi, value_mask, mask_power, clip_tau), `dev_v5_lab_compare.py` (all-seed counts), `dev_v5_carrier_probe.py`; held-out sets `holdout` (seeds 2000/200) and `holdout2` (3000/300); check dirs `check-r3-*` under `.thesis-build/rehearsal/v5-channel-dev/`. The check script prefixes "check-" to --tag.
- Open user decisions: is r3 acceptable; adoption; judgement calls 1-10; real study approval (manifest at the r3 commit). Supervisor: deviations 17, 18, 20, 27, 29. No independent review yet.

Related: [[watermark-v4-candidate]], [[v4r2-three-threat-run]], [[thesis-project-layout]]
