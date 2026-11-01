# Judge's preliminary findings

Claude (Opus 5.5), 2026-11-01. Written before any Codex research on this question. Exploratory, development data only (Stage 2 union, 60 sources, seeds 12-14). Scripts and JSON are beside this file. These are hypotheses to attack, not conclusions. A strong refutation is as useful as a confirmation.

## F5 is a defensible base, not the best method on every cell

F5 and v5 share everything except the robust tier (`scripts/f5_latent_codec.py:1-9`), so their difference is a natural test of the carrier components.

Source-majority C, /60 on development:

| Method | SD1.5 .1 | .2 | .4 | SDXL .1 | .2 | .4 | K3 .2 | Median PSNR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| F5 r2 | 60 | 57 | 39 | 0 | 0 | 0 | 5 | 44.96 |
| v5 r3 | 47 | 27 | 3 | 50 | 12 | 0 | 57 | 36.85 |

Frozen held-out Phase B, /200: F5 186/182/140, 19/0/0, 61. v5 163/122/28, 173/47/0, 189. F5 wins on SD1.5 and quality. v5 wins on the families the writer did not target.

## Finding 1: on foreign regenerators F5 loses the carrier, not the binding

Every seed-level call on a marked image, in one class ([loss_budget.py](loss_budget.py)):

- **C:** read succeeded and the content check matched.
- **binding:** read succeeded, content check did not match. Descriptor, code or decision stage.
- **undecoded:** key found only with the code recomputed from the suspect. Carrier alive, too weak to decode.
- **lost:** neither test passed. Carrier gone.

| Arm, cell | C | binding | undecoded | lost | missing | Median decoded margin |
|---|---:|---:|---:|---:|---:|---:|
| F5 SD1.5 .2 | 170 | 3 | 4 | 0 | 3 | 5.15 |
| F5 SD1.5 .4 | 117 | 25 | 26 | 10 | 2 | 2.27 |
| F5 SDXL .1 | 0 | 3 | 23 | 154 | 0 | -2.75 |
| F5 SDXL .2 | 0 | 0 | 0 | 180 | 0 | -3.95 |
| F5 SDXL .4 | 0 | 0 | 0 | 180 | 0 | -4.34 |
| F5 K3 .2 | 16 | 6 | 46 | 112 | 0 | -2.21 |
| v5 SD1.5 .2 | 82 | 8 | 54 | 35 | 1 | 0.00 |
| v5 SD1.5 .4 | 7 | 3 | 28 | 140 | 2 | -2.63 |
| v5 SDXL .1 | 140 | 6 | 32 | 2 | 0 | 1.59 |
| v5 SDXL .2 | 38 | 4 | 74 | 64 | 0 | -1.08 |
| v5 K3 .2 | 167 | 6 | 6 | 1 | 0 | 4.14 |

Hypothesis: the carrier space and encoder model (K4, K5) own the foreign-family failure. Binding (K1, K2, K10) is a small T3 budget: a perfect content check would add at most 8 sources (F5 SD1.5 .4, 39 to 47), and 3 or fewer elsewhere. Those components still matter for T4 and T5.

## Finding 2: searching all 2^32 codes may cost more than the content check gains

The frozen reader searches every code (threshold 8.26), then rejects any code outside the content radius. Testing only codes within Hamming radius r of the code recomputed from the suspect spends the false-positive budget only on codes that could be accepted ([reader_ball.py](reader_ball.py)). Thresholds at 1e-6 per claim: r=0 4.98, r=1 5.62, r=2 6.08, r=3 6.45, r=4 6.75, r=6 7.21.

Source-majority counts, /60. Each is a lower bound from saved scores; no writer change:

| Arm, cell | Frozen C | Binding perfect | r=0 | r=3 |
|---|---:|---:|---:|---:|
| F5 SD1.5 .4 | 39 | 47 | 57 | 48 |
| F5 K3 .2 | 5 | 7 | 23 | 11 |
| F5 SDXL .1 | 0 | 1 | 7 | 1 |
| F5 SDXL .2 | 0 | 0 | 0 | 0 |
| v5 SD1.5 .2 | 27 | 30 | 47 | 36 |
| v5 SDXL .1 | 50 | 50 | 59 | 57 |
| v5 SDXL .2 | 12 | 14 | 40 | 21 |

**Warnings.** This changes the endpoint, so it can never be reported as frozen C. r=0 is the old "recomputed only" route, whose content check is implicit and weak on a strong clean mark. A lower threshold could raise T4 and T5 acceptance, which is not measured here. Whether the binding stays adequate is the whole question.

## Finding 3: most of F5's distortion goes to a tier that cannot survive regeneration

The profile fixes the fragile tier at 47 dB and F5's robust tier at 52 dB (`experiments/c4-v5-two-tier-regeneration-v1/profile.json:31`, `research/f5-r2-spec.md:8`). Against F5's median total of 44.96 dB (MSE 2.08), that is MSE 1.30 fragile (about 60%) and .41 robust (about 20%). These shares are derived from budgets, not measured separately. After regeneration `both_match` is 0/90 by design (M2, `research/m2-coco512-results.md` on `claude/m2-coco512-results`).

Hypothesis: at the same total PSNR a robust-only writer could raise robust amplitude about 2.2 times. F5's median SDXL .2 decoded score is about 4.3 against 8.26, so a linear reading would just clear it. Phase A found SDXL nonlinear, so this may well fail. F6 Stage P sweeps the robust budget but keeps the fragile tier. Removing or shrinking the tier has a T4 and instance-binding price that must be measured.

## Finding 4: what a change looks like affects how much survives

Saved marks, luma band 64-96 ([coarse-lattice PROPOSAL](../../coarse-lattice-20261030/PROPOSAL.md)): at SD1.5 .2 image content keeps .74, VINE-R .44, v5 .29, while F5 is amplified 1.76 times. At SDXL .2: content .82, VINE-R .62, v5 .33, F5 .35. Chroma regeneration noise is 3-4 times below luma. Metrics can miss visible flaws: a chroma lattice with PSNR 39.9, SSIM .994 and LPIPS .028 showed blotches on flat areas at 3x zoom.

## My prior ranking, by loss budget

1. K4 carrier space and K5 encoder model: largest loss on foreign families.
2. K9 reader test and K3 payload coding: the undecoded pool, potentially the cheapest gain.
3. K8 fragile tier and K7 quality budget: distortion spent where it cannot help T3.
4. K6 optimizer: no evidence yet that it limits anything.
5. K1, K2, K10 binding: small T3 budget, large T4/T5 role.
6. K11 keys and K12 evaluation: limits on what may be claimed.
