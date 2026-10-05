# F5 revision 2 — frozen specification (M1b)

Status: **frozen** at `f06e0d8` / `configs/f5-r2.json` (profile sha256 `25f9cb188368be04cd8d2b95ea1066872d3ca70908bd554af01ff93a53b40723`). No held-out data accessed to freeze. Threat scope T3/T4/T5 only.

## 1. What is frozen

- **Code:** `scripts/f5_latent_codec.py` (FAMILY `f5-encoder-amplified-latent`, REVISION 2, BAND (4,32), WHITENING 1.0, LATENT 64, SCALE 0.18215, LABEL `f5-latent`).
- **Robust tier:** VAE posterior-mode latent (pinned SD1.5 VAE fp32), orthonormal DCT per channel, 3272 slots (radius 4–32) → 320 chips, public weight `radius/4`, keyed signs by v4 carrier. Embedding 150-step normalized-gradient PGD through the encoder, squared-hinge target margin 4.0, L2 ball at PSNR budget 52 dB, [0,1] box, RGB8 rounding, fragile luminance tier (v5, 47 dB) + one short refinement at PSNR+6 dB. Detector reads same latent.
- **Semantic binding:** CLIP ViT-B/32 vector E = mean over 7 fixed views (full, mirror, four corners, centre at 7/8), renormalized; 32-bit code q = signs of keyed Rademacher projections of E; soft maximum-likelihood angle `Phi(c p cot t)` vs Hamming, same radii (6/10) and v5 decision table.
- **Profile:** `experiments/c4-v5-two-tier-regeneration-v1/profile.json` (two-tier-dual-key-dct, public-derived, `false_positive_target 1e-6`, roster 1). Frozen hash above.
- **Invocation:** `scripts/f5_gate.py --psnr 52 --binding soft --semantic-views 7` (gate); stress selector `scripts/f5_stress_gate.py --strengths 0.4 0.5 0.6 --seeds 0 1 2 3 4` (development only).
- **Side information:** public OwnerID, profile, pinned CLIP weights, pinned SD1.5 VAE encoder (must be accepted at M1).
- **Quality bar:** PSNR mean ≥44 dB, LPIPS mean ≤.0173 max ≤.050, 12/12 `both_match` clean; human verdict on `20261005-0420` images: "کیفیت بصری قبوله".

This spec owns no change to the protected proposal/source plan/claims.csv/`THESIS_GUIDE_OFFLINE.html`.

## 2. What is not claimed

- Gain is property of pinned SD1.5 VAE encoder (T3 family). Other encoders/UNets or a pixel pre-filter before encoding (T2 composition) untested — one-line limitation.
- Seven CLIP passes per detection is explicit cost.
- No cryptographic unforgeability; public-derived security.
- Held-out confirmation required before any population claim; exploratory 12-source counts only.

## 3. Evidence that justifies freeze (development only)

- M1a gate vs v5 r3 (paired, 3 seeds): .1 29/29 vs 27, .2 28/28 vs 18, .4 23/28 vs 2. Stress baseline (5 seeds): .4 49/58 (84%), .5 37/58 (64%), .6 10/57 (18%). T4 0/20 both_match (semantic delivered 0/20 at .5), T5 0/66 joint collisions, C0/wrong-owner 0. Three follow-on families (H1 carrier geometry, H3 texture mask, H4 threshold relax) killed per `research/f5-research-plan.md` criteria — plateau `research/f5-plateau-20261005.md`.
- Tests `tests/test_f5_latent_codec.py` (7 passed): weight-key independence, null symmetry, projection Rademacher/cache, soft-angle recovery.
- Visual comparison `20261005-0420/compare-source-v5-f5.png` (147498 sky worst LPIPS .050) accepted by user.

## 4. Confirmatory intent (no execution)

Cohort: MS-COCO test source groups, 512×512 canonical, metadata-only freeze from `data/splits.csv`; 300 representatives ranked by `m1-coco512-confirm-v1` tag, T3 30×(VAE+.05/.1/.2/.4×3 seeds×2 arms), T4 30 donor-recipient pairs (128/256 patches, sham), bounded T5 up to 30 pairs (identical category signatures, pHash≥8). Thresholds fixed inclusive (decoded 8.259…, recomputed 4.982…). Manifest and synthetic rehearsals prepared under `research/m1b-f5-confirmatory-manifest.md`; no held-out pixels opened.
