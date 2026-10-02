# Small v4 revision-2 study of the three proposal threats

This is a prospective exploratory repeat of `experiments/c4-v4-three-threat-small-v1` with the revision-2 codec. It applies `research/research-contract.md` and `research/scope-guard.md` and is linked to issue 18. It tests revision 2 as an image-domain pixel comparator only: not latent embedding, not legal ownership. RQ-02 and HYP-02 stay open.

## Why a repeat

Revision 1 was the only v4 codec ever run on study images (`c4-v4-three-threat-dev-001`, killed after 96 of 1,884 detector calls; none of its attack images were evaluated). Revision 2 changes the perceptual hash (detail part floored, not unit-normalised), makes the semantic code scale-free, adds `content_uncertain` and `not_detected` to the decision table and plans embedding with the byte-rounding budget (`research/method-amendment-v4.md`). It derives a different `detector_config_id`, so revision-1 images cannot be evaluated with it: every image has to be embedded and attacked again.

## What is identical to the revision-1 plan

Everything in `experiments/c4-v4-three-threat-small-v1/plan.md` except the four items below: cohort (12 clean/T5 sources, 10 T3/T4 sources), canonicalisation, the 537-row and 1,884-call inventory, owners, binding modes, T3 doses (VAE mode round trip; SD 1.5 img2img DDIM 20, strengths .05/.1/.2/.4, seeds 0/1/2), T4 arms (public patch 128/256, unmarked patch sham, clean-donor residual .5/1, public band, unmarked band sham, public projection), T5 labels and transfers, numeric admissibility (PSNR>35, SSIM>.9, LPIPS<.1), analysis rules and claim limits. The attack code (`three_threat_protocol.py`, `three_threat_models.py`, `v4_study_protocol.py`, `v4_study_models.py`, `v4_study_boundary.py`) is unchanged. The acceptance criteria are copied unchanged.

## What differs

1. Codec: `scripts/revised_watermark_v4.py` revision 2, copied byte-identically from the main repository working tree (sha256 `723773c7672ebdaa1a6c460f156d578fc0de13d9d50ec27c4d3e56ba477d1b9b`); its synthetic verification is in `audits/v4-revision-2-verification-20261001/` of the main repository.
2. Profile: `profile.json` here is the revision-1 study profile plus the two revision-2 decision fields `semantic_mismatch_distance` and `instance_mismatch_distance`, both 10 (the revision-2 example default). All embedding and radius constants are unchanged.
3. Worker: `scripts/v4r2_study_worker.py` is `v4_study_worker.py` with the new identity, a revision check, a progress log line per stage, results written at most every 30 s and at every stage boundary (revision 1 rewrote the full results file after every detector call), and a byte counter instead of a directory scan for the disk guard. No scientific step changed.
4. Identity: experiment `c4-v4r2-three-threat-small-v1`, run `c4-v4r2-three-threat-dev-001`.

## Execution and approval

The user approved this run in chat on 2026-10-02 (recorded in `.thesis-build/v4r2-three-threat-user-decision-20261002.json`) and asked Claude Code, not Codex, to design and run it while they are away. It runs through the official dispatcher on a clean commit, local GPU, USD 0, no downloads. A failed attempt is preserved, never rewritten. Visual principal-content assessments by two independent humans are still required by the criteria; any visual notes made by Claude are labelled as a single non-independent assessment.
