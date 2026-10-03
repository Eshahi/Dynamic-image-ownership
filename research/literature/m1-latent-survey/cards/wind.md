# Hidden in the Noise: Two-Stage Robust Watermarking for Images

Primary source: https://arxiv.org/html/2412.04653v5

Inspected: Sec.3-4/Algorithms1-2; Sec.5.1/Table2; App.D.3/Table7. Full-text artifact/checksum in paper JSON and inventory.

Secret salt and index seed reproducible Gaussian initial-noise identities; Fourier group identifiers reduce candidate search; full variant falls back to full noise bank. Needs owner model, secret salt, index bank and50-step inversion. Main SD2 sampling/inversion50. Table2 original/re-generated/unrelated noise cosine mean .888/.824/.000 (SD .053/.062/.008). Regeneration is Zhao noise-then-denoise attack; Table7 full search among10000 noises gives100% at10-50 repeated regenerations, cosine .493 decreasing to .121. Table1 WINDfull2048 crop/scale .930 versus fast2048 .060.

Limitations: Search bank and inversion cost are essential side information. Paper regen settings do not directly equal local img2img strength .4. Finite/reused initial-noise pool affects multi-query distribution.
