# M1b package: F5 r2 confirmatory run on narrow COCO512

Status 2026-10-06: **prepared for the user's single M1b decision; not run on held-out data.** Branch `claude/m1b-package` (from Codex's `codex/f5-m1b-vast-recovery` 87af2b8). No test image, test annotation or test feature was opened to build this package; the held-out plan was generated from the frozen metadata schedule and external index only.

## 1. What the user decides

1. **Approve or redirect** the single confirmatory run below (manifest hash and scientific-core hash are printed by the prepare script at the final commit, section 6).
2. **Accept the protocol clarifications** in section 4 (all are declared before any outcome).
3. **Where it runs.** The official runner supports only local execution, and the project rule keeps held-out data off the rented GPU. The estimated run is about 4.5 hours on the laptop RTX 5070 Ti (section 5). Running it on vast.ai would need an explicit exception to that rule and is not prepared.

Already decided (2026-10-05/06): F5 r2 is the frozen candidate; its visual quality was accepted; the cohort is narrow COCO512 (300 MS-COCO test representatives).

## 2. Frozen science

- **Candidate:** F5 r2, `configs/f5-r2.json` (sha256 in the plan), `scripts/f5_latent_codec.py`, profile `experiments/c4-v5-two-tier-regeneration-v1/profile.json`. Detector side information: public OwnerID, profile, pinned CLIP ViT-B/32 (seven views), pinned SD1.5 VAE encoder (fp32).
- **Comparator:** v5 r3 image-domain codec at the same profile, single-view CLIP, through the unchanged `m1_confirmatory_image_operations.V5Comparator`. It marks the same canonical sources.
- **Cohort:** the 300 MS-COCO test representatives of `research/m1-confirmatory-schedule-draft.json` (metadata-only ranking `m1-coco512-confirm-v1`), raw files bound by hash in `research/m1-confirmatory-external-index.json`. Public owners from the A4 16-owner roster; the wrong owner is the next roster identity. T3 cohort: first 30 by `m1-coco512-t3-v1`; T4: 30 donor/recipient pairs by `m1-coco512-t4-v1`.
- **Canonicalization:** `m1_canonical_source.canonicalize` (hash check before decode, EXIF transpose, ICC to sRGB, Pillow bicubic 512x512).
- **Attacks (Q = 0, no retries):** VAE posterior-mode cycle; SD1.5 DDIM20 img2img at strengths .05/.1/.2/.4 with seeds 0/1/2, empty prompts, CFG 1, eta 0, safety checker kept; actual DDIM timesteps recorded and checked. T4: centered 128x128 and 256x256 RGB patch from donor C1 into recipient C0-source, plus the C0-donor sham; donor and recipient claims. T5: bounded disjoint 30-pair selection from identical noncrowd COCO category signatures, distinct groups, source pHash distance >= 8, hash-ranked by `m1-coco512-t5-v1`; C0 and C1 of each endpoint queried against the other endpoint's owner.
- **Thresholds:** fixed inclusive v5 thresholds (decoded 8.259326826136963, recomputed 4.982033056390042, false-positive target 1e-6, roster 1). No calibration, no threshold or seed selection on test.

## 3. Endpoints (computed by `analyse` in the worker, per method)

- **Clean (300 independent sources):** C1 correct-owner `both_match` (TPR; one-sided 95% Clopper-Pearson lower bound, target >= .80); false attribution on C0 correct, C0 wrong-owner and C1 wrong-owner claims, under `both_match` and the stricter `any_found` (one-sided upper bound, target <= .01, which needs 0/300). Quality: PSNR > 35 dB, SSIM > .9, LPIPS < .1 counts (separately and jointly), means and LPIPS max.
- **T3 (30 sources, descriptive):** per dose, row counts of semantic success (split into read-and-compared and recomputed-only) and `both_match`; the **source-level majority** endpoint (a source succeeds at a strength when at least 2 of its 3 seeds do) with intervals over 30 sources; wrong-owner and C0 negatives per source. Paired F5-vs-v5 source table per strength with an exact sign test.
- **T4 (30 pairs, descriptive):** false donor full attribution (`both_match` on the donor claim of the marked splice, per pair over both sizes; same-public-owner pairs excluded from this rate and reported separately: 1 of 30), delivery witness, donor semantic consistency, sham and recipient-claim negatives, and the distribution of final states.
- **T5 (up to 30 pairs, descriptive):** false full match and any-found per pair on C0 and on C1, different-owner pairs only; the full pair ledger with every rejection reason. Fewer than 30 eligible pairs is reported as insufficient evidence, not as a pass.
- Missing or failed rows count adversely (a miss for positives, an error for negatives); observed-valid rates are reported beside them. Repeats (seeds, sizes, claims) never add independent units.

## 4. Protocol clarifications declared before any outcome

1. **Matched C0 reconstruction is the identity for both methods.** F5 and v5 add a pixel-domain change to the canonical source; with the watermark objective disabled the change is zero, so C0-reconstruction is byte-identical to C0-source and a separate call would duplicate it. The C0-reconstruction cells therefore equal the C0-source cells. In place of the duplicate, each source gets a C0 wrong-owner query, so each method still has 4 clean queries per source (C0 correct, C0 wrong, C1 correct, C1 wrong; 1200 per method).
2. **Shared unmarked outputs.** C0 attack outputs and T4 shams are computed once and read by both methods' detectors (identical images; fewer GPU calls, same planned queries per method).
3. **T3 C0 arm:** correct-owner claim only (draft: "C0 correct-owner plus C1 correct/wrong-owner = 1170 detector calls per method").
4. **Recovery:** one journal row per unit; a cooperative stop (`max_wall_seconds`) or a crash leaves a resumable journal. A continuation is a new manifest whose plan adds `resume_from`; the scientific core (plan science fields and code hashes) must be unchanged, which the worker enforces. Under `research/approval-policy.md` this is an infrastructure-only rerun (at most 2, reviewer-checked with `m1b_prepare_package.py rerun-check`). A torn final journal line is dropped and that unit runs again; corruption anywhere else stops the run.
5. **Rehearsal scope.** The worker, its journal, stop/resume and endpoint code were rehearsed on development images with the real models (section 5) and on a fake runtime in unit tests. The dispatcher's `--execute` path cannot be rehearsed without a human approval; its preview (schema, script and input hashes) passes. The approval check inside the worker is unit-tested on a synthetic fixture.
6. **Patch-attack quality** is reported against the recipient source; attack quality against the immediate input and the canonical source for T3. No visual-admissibility filtering.

## 5. Development evidence for this package

(filled from the runs below)

## 6. How the run is started (after approval)

(filled at the final commit)

## 7. Limitations (unchanged from the spec)

T3/T4/T5 have 30 independent units: zero errors give a 9.5% upper bound, so these are descriptive. Only the pinned SD1.5 regenerator is tested; other regenerators and pixel pre-filters before encoding are untested. Public-derived keys: no cryptographic unforgeability. Image rights for the COCO test photos remain pending (local research use only). Human visual and semantic verdicts on test images stay missing.
