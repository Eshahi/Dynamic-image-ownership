# Small v5 study: does the two-tier codec keep the semantic key through regeneration?

Prospective and exploratory. It applies `research/research-contract.md` and `research/scope-guard.md` and is linked to issue 18. It tests the v5 codec (`research/method-amendment-v5.md`) as an image-domain comparator only: not latent embedding, not legal ownership. RQ-02 and HYP-02 stay open. **Prepared on 2026-10-02; not approved and not run.**

## Why this study

The revision-2 study (`experiments/c4-v4r2-three-threat-small-v1/results-dev-001.md`) found that no regenerated marked image kept a key, the VAE round trip alone removing the mark. v5 moves the semantic key to the block DCT of a 128x128 average of the image, where an f=8 autoencoder keeps a pattern, and keeps the instance key in the full-resolution block DCT, where regeneration removes it. On synthetic development hosts this gives `semantic_only` after the VAE round trip and at low img2img strength for most hosts (`research/method-amendment-v5.md`, "Engineering evidence"). Whether it does on photographs is what this study asks.

## What is identical to the revision-2 study

Cohort (12 clean and T5 sources, 10 T3 and T4 sources) and canonicalisation; owners and binding modes; T3 doses (VAE mode round trip; SD 1.5 img2img, DDIM, 20 steps, eta 0, guidance 1, empty prompt, strengths 0.05, 0.1, 0.2, 0.4, seeds 0, 1, 2) with matched C0 and C1; the 66 frozen T5 pairs and the seven same-semantic transfers; the clean-donor residual arm at scales 0.5 and 1; the suspect-only CLIP vector as semantic source; numeric admissibility (PSNR > 35, SSIM > 0.9, LPIPS < 0.1); models, assets, runtime inventory, watchdog and resource ceilings. `three_threat_protocol.py`, `three_threat_models.py`, `v4_study_models.py` and `v4_study_boundary.py` are unchanged.

## What differs

1. **Codec and profile.** `scripts/revised_watermark_v5.py` (version 5, revision 1) with `profile.json` here: the shipped public-derived v5 profile with `semantic_source` set to the study's CLIP vector. No other field differs from `configs/revised-watermark-v5.example.json`.
2. **Transfer arms.** The patch arms and the band arm of revision 2 are dropped: none of their 120 outputs was admissible, so they could not test binding. `public_projection` is re-specified for two tiers in `v5_study_protocol.transfer`: the donor's 320 robust and 320 fragile public projections are imposed on the recipient at least squared error. `unmarked_projection_sham` is new: the same procedure with the unmarked donor, a control for detections created by the procedure itself.
3. **Supplementary ordinary-processing axis (T1s).** JPEG at quality 75 and a Lanczos resize to 384x384, for the ten T3 sources, C0 and C1. It carries no pass rule; it documents the two properties the amendment states (both keys through JPEG; the semantic key through a resize) and their negatives.
4. **Secondary arm at a second quality level (control C2).** The ten T3 sources are also marked with `profile-strong.json`, which differs from `profile.json` in two embedding fields only (`visibility` 2.0 instead of 1.0, `min_robust_psnr_db` 33 instead of 36) and is read by the same detector configuration. Its marked images go through the same T3 doses and seeds. On the development hosts this profile gave 33 to 40 dB, so most of its images are expected to miss the PSNR > 35 admissibility rule. The arm is descriptive: it shows how survival moves with the quality budget, at about the fidelity at which the published regeneration-robust methods operate, and it cannot support a survival claim.
5. **Inventory.** 617 rows and 2,204 detector calls: clean 34 rows (24 and the ten C2 images), T4 80, T3 390 (130 per control), T1s 40, T5 66 and 7 transfers.
6. **Identity.** Experiment `c4-v5-two-tier-regeneration-v1`, run `c4-v5-two-tier-dev-001`.

The optional refinement stage (`scripts/v5_channel_refine.py`) is not part of this study. It needs gradients through the autoencoder and denoiser, which the worker's deterministic mode does not allow, and its surrogate channel is the attack model itself; it would need its own design.

## Prediction recorded before any photograph is processed

On the sixteen synthetic development hosts the default profile kept the semantic key in 12 of 16 VAE round trips, 33 of 48 img2img outputs at strength 0.05, 15 of 48 at 0.1, 8 of 48 at 0.2 and none at 0.4, with no detection on any unmarked control. The four hosts that failed the VAE round trip were the most textured. Those runs used the layout proxy as semantic source; here the CLIP vector is recomputed from every suspect image, and its code can drift under regeneration, which lowers the recomputed score in proportion to the drifted bits. The author therefore expects, on photographs: a majority, not all, of VAE-mode rows `semantic_only`; a lower rate at 0.05; few at 0.1 and 0.2; none at 0.4; and so a **failure of the survival criterion at every img2img strength and possibly at the VAE stratum**. The criteria below are the revision-2 criteria and were not lowered to fit that expectation.

## Rehearsal, execution and approval

`run_v5_study.py` and `v5_study_worker.py` have a rehearsal mode that runs the identical stages on twelve generated synthetic images under `.thesis-build/rehearsal/` (approval policy, 2026-10-02 section). The package may be presented for approval only after a rehearsal has passed at the same clean commit; the rehearsal record is cited in `research/method-amendment-decision-20261002.md` or the state file.

The study itself needs the user's manifest-specific approval and is launched by the user through the official dispatcher. No independent reviewer has checked this package; the approval policy asks for one. A failed attempt is preserved, never rewritten. Visual principal-content assessments by two independent humans are required by the criteria for T3 and for the marked images.
