> Historical stage1b discovery grouping. Superseded by individual source cards and evidence-records.json; excluded from all counts and current claims. Earlier incomplete extraction is not current evidence.

# Benchmark extensions: VINE / W-Bench and WAVES

These extend [VINE](../../../../q1-dossier-20261018/02-literature/C1-posthoc/cards/Lu2025VINE.md) and [WAVES](../../../../q1-dossier-20261018/02-literature/C2-removal/cards/an2024waves.md). Inspected 2026-10-19, V2; source hashes in the manifest.

## W-Bench

[VINE v2](https://arxiv.org/html/2410.18775v2): §§3.3, 4.1–4.3, Table 1, Appendices D and G.2. Read official `stochastic_regeneration.py`, `utils_sto_regeneration.py`, `deterministic_inversion.py` at `d72f11a93f8de9bc45ef61202b9c8dda2a70cc77`.

The paper uses VP noise times 60:20:240, not that many UNet evaluations. Source uses DDIM, 50 scheduled steps and `head_start_step=50-max(noise_step//20,1)`; therefore 3–12 executed denoising steps. It samples the VAE posterior, uses an empty caption dictionary and guidance 7.5; default DDIM eta is zero. Stochastic model is `stabilityai/stable-diffusion-2-1` (non-base); deterministic DPM order-2 uses `...-2-1-base`, 15/25/35/45 steps. Checkpoint revisions are not reproducibly pinned by the paper.

Table 1 reports VINE-R stochastic/deterministic TPR@0.1%FPR 99.66/99.98%; StegaStamp 91.09/92.13%; TrustMark 9.22/34.20%. These aggregate severities, not SDXL .2 results. The caption's 5,000-image-per-edit statement and §4.2's 1,000 distinct-source allocation must not become 5,000 independent sources.

## WAVES

[WAVES v3](https://arxiv.org/html/2401.08573v3): §§3–4, Appendix D.1, E.4 and F.2–F.3; official `regeneration/regen.py` at `1477635d306d6f8c77a588e6441bd4ba301a1f7a`.

Single-pass SD1.4 uses noise times 40–200; 2x uses 20–100 per pass; 4x uses 10–50. Appendix prose accidentally says “two” under the 4x heading; the official function loops four times. Known-generation-prompt regeneration is a separate attack. The inspected public helper always appends an empty prompt despite accepting `captions`; do not claim this helper reproduces the prompted arm.

The paper reports performance-quality tradeoffs and TPR@0.1%FPR, not just bit accuracy. Appendix E.4 averages normalized metrics within four categories and then averages categories: flat averaging eight metrics is not equivalent. The detector and data differ from this study; scores are not a leaderboard for F5.
