# M1b confirmatory manifest — F5 r2 (prepared and rehearsed, NOT run on held-out)

Status: **prepared** 2026-10-05 in `claude/f5-research`, frozen code `f06e0d8` / `configs/f5-r2.json`. No held-out pixels, test features, COCO annotation values or method outcomes on held-out were opened. Rehearsals are synthetic (generated images / no-image arithmetic) only.

## 1. What is frozen

- **Candidate:** `scripts/f5_latent_codec.py` F5 r2 (encoder-amplified latent, band 4–32, whitening 1.0, PSNR 52 dB, 150 steps, soft binding, 7-view CLIP). Profile `experiments/c4-v5-two-tier-regeneration-v1/profile.json` sha256 `25f9cb188368be04cd8d2b95ea1066872d3ca70908bd554af01ff93a53b40723`, detector thresholds inclusive decoded 8.259326826136963 / recomputed 4.982033056390042, `false_positive_target 1e-6`, roster 1.
- **Comparator:** v5 r3 image-domain two-tier at same profile (frozen).
- **Cohort (metadata only):** MS-COCO `study_split=test`, `domain=ms-coco`, ranked by `m1-coco512-confirm-v1` tag → first 300 group representatives without opening paths. T3 30, T4 30 donors + 30 recipients, bounded T5 up to 30 disjoint pairs (identical nonempty category signatures, pHash≥8). Distinct 16-owner roster `thesis:owner:00..15`, public. See `research/m1-confirmatory-draft.md` and `research/m1-confirmatory-interface.md` for schedule tags, seed roles, and source-preservation quality protocol.
- **Attack grid:** pinned `runwayml/stable-diffusion-v1-5` DDIM img2img strengths .05/.1/.2/.4, seeds 0–2, 20 steps, CFG 1, eta 0, empty prompt, safety checker retained, fixed 512, plus VAE posterior-mode roundtrip. 780 outputs + 1170 detector calls per method (plus cleans). Sharded ≤3600 s/shard, cooperative 3500 s stop, 1.25 overhead factor.
- **Decisions:** per-cell Clopper-Pearson one-sided 95% and Wilson 95% via `scripts/m1_confirmatory_endpoints.py` (candidate-independent); T3/T4/T5 descriptive with clustered repeats, clean cells require ≤1% upper bound (needs 0/300) and TPR lower ≥80% (needs large n). Missing/invalid counts as adverse; no best-seed/threshold selection.

## 2. Rehearsals (synthetic, no held-out)

- **Endpoint arithmetic:** `tests/test_m1_confirmatory_endpoints.py` (4 tests) — boundary identities (0/300 → .009936, 1/300 → .0157), Wilson symmetry, adverse missingness, duplicate/extra ID rejection.
- **Inventory/resumption/topology:** `tests/test_m1_assess_dual_threats.py` / `tests/test_m1_candidate_lifecycle.py` / `tests/test_m1_candidate_rehearsal_worker.py` — 489-row inventory, shard overlap/code-version guards, truncated journal, checkpoint resume (existing harness, not extended for F5 until M1b approval).
- **F5 unit:** `tests/test_f5_latent_codec.py` (7 passed) — weight-key independence, null symmetry, projection cache, soft-angle recovery.
- **Scientific-core hash:** path-free adapter `research/m1-candidate-adapter-interface.md` requires caller-verified hash; no held-out-dependent intermediate artifacts emitted.

No held-out images were loaded, no test scores simulated, no thresholds tuned on reserved data.

## 3. What still needs the user's single decision

- Adopt the narrow COCO512 amendment vs protected all-domain plan (scope guard).
- Accept detector side information now includes pinned SD1.5 VAE encoder + 7 CLIP passes.
- Approve the synthetic-rehearsed manifest for a single held-out run (the user starts it from their terminal via the official runner). Until then, no scientific execution on held-out.

## 4. How to run (after approval)

The user (not the agent) launches shards from their terminal via the official runner: `scripts/m1_candidate_rehearsal_worker.py` / `scripts/m1_scientific_*` harness at the frozen commit. Shard outputs under `.thesis-build/runs/<run_id>/`, journals and receipts retained; failed shards preserved, no seed substitution. Original M1b review (fresh sub-agent) passes before results acceptance.

## 5. Limitations declared

Descriptive T3/T4/T5 with 30 independent sources/pairs: zero errors → 9.5% upper bound, far from 1%. Other regenerators / T2 pre-filter compositions untested. No generative-model comparison is relabelled as existing-photo attribution. Human visual verdict for held-out stays missing.
