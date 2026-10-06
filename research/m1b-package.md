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
7. **One realization, no replay promise.** F5 embedding on the GPU is not bit-reproducible (section 5). The confirmatory result is the single realization recorded in the journal; no unit is ever re-run, and a resumed run reuses the saved C1 images. Borderline rows (soft semantic distance near the radius at strength .4) can differ between realizations; this is part of the descriptive T3 uncertainty, not a reason to rerun.

## 5. Development evidence for this package

All on development sources (the first four of the twelve M1a sources), local RTX 5070 Ti Laptop GPU, USD 0. Outputs under MAIN `.thesis-build/`.

| Run | Commit | Result |
| --- | --- | --- |
| Unit tests `tests/test_m1b_coco512_worker.py` (fake runtime) | final | 18 pass: plan validation, inventory counts, adverse missing rows, failure propagation without replacement, cooperative stop then resume equal to an uninterrupted run, torn last journal line, earlier corruption refused, changed saved image refused, event rules, sign test, COCO signature parser, approval check fails closed (synthetic fixture). With the existing runner/codec/endpoint/T5/image-operation/schedule tests: 78 pass. |
| Real-model smoke `dev-runs/20261006-1313-m1b-worker-smoke` | ba75609 | 339/339 planned rows completed, 0 failed, 373 s (46 s model load). Both methods: clean C1 `both_match` 4/4, zero C0/wrong-owner detections, T4 false donor attribution 0/4, T5 2 pairs selected (synthetic categories), zero false matches. T3 source-majority semantic at .4: F5 1/2, v5 0/2; v5's .2 successes were mostly recomputed-only (1 of 5 read-and-compared) while all F5 successes were read-and-compared. Quality: F5 PSNR mean 44.9 dB, LPIPS mean .011; v5 37.3 dB, .014. |
| Stop rehearsal `rehearsal/m1b-stop-attempt1-failed-pwd` | b5ffa2a | **Failed, kept.** Run exactly as the dispatcher runs the worker (`safe_env()`, cwd = repo): the sanitized environment has no USERNAME, torch's inductor cache called `getpass.getuser()` and the import failed (`No module named 'pwd'`). The held-out run would have crashed at start. Fixed in 354c42f (inductor cache inside the run). |
| Stop rehearsal `rehearsal/m1b-stop` | 354c42f | `max_wall_seconds=120`: exit 3, status `checkpointed`, 24 rows completed, 299 not attempted, inventory honestly incomplete. |
| Rerun check `rehearsal/m1b-rerun-check.json` | 346143d | Stop and resume manifests differ (`resume_from`) but have the same scientific-core hash; changed paths are harness only; previous attempt incomplete and preserved. |
| Resume rehearsal `rehearsal/m1b-resume` | 346143d | New manifest with `resume_from`, same `safe_env()` launch: exit 0, 339/339 completed in 217 s; the 24 rows of the stopped run were carried over unchanged and not re-run; F5 embeddings of the stopped run were not repeated. |
| Repeatability (smoke vs stop+resume) | — | Canonical sources, v5 embeddings, every C0 and v5 attack output and every C0 splice are byte-identical across the two runs. **F5 embeddings are not bit-reproducible on the GPU** (normalized-gradient PGD through the fp32 VAE encoder; PSNR differs in the third decimal, e.g. 45.040 vs 45.034 dB), so their descendants differ. 235 of 236 detection states agree; the one flip is a borderline T3 row (source 4795, strength .4, seed 2: soft semantic distance 7.10 vs 2.60 against radius 6). |
| Dispatcher preview (`dispatch` without `--execute`) | final | (pending at final commit) |

**Runtime on the laptop (development p95 per operation):** F5 embed 36.9 s, v5 embed 2.7 s, F5 detection 0.62 s, v5 detection 0.47 s, attack 0.85 s, splice 0.74 s; model load 46 s; bookkeeping overhead under 1%. Full held-out plan: 300 x 43.4 s (sources) + 30 x 61 s (T3) + 30 x 11 s (T4) + about 2 min (T5) + load = **about 4.3 hours** (5.3 h with the 1.25 planning factor). Budget: dispatcher `max_seconds` 28,800 (8 h); the worker stops cooperatively at 27,000 s. Disk about 1 GB of PNGs; GPU memory 7.7 GB of 12 GB; GPU at 99% utilization and about 51-58 C during the smoke.

## 6. How the run is started (after approval)

(filled at the final commit)

## 7. Limitations (unchanged from the spec)

T3/T4/T5 have 30 independent units: zero errors give a 9.5% upper bound, so these are descriptive. Only the pinned SD1.5 regenerator is tested; other regenerators and pixel pre-filters before encoding are untested. Public-derived keys: no cryptographic unforgeability. Image rights for the COCO test photos remain pending (local research use only). Human visual and semantic verdicts on test images stay missing.
