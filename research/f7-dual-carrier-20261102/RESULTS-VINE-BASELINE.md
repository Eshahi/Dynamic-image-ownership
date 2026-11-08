# VINE-R + registry baseline on the f7c sources (f7v): results

Run by Claude on 2026-11-08 under [REPLICATION-VINE-ADDENDUM.md](REPLICATION-VINE-ADDENDUM.md), frozen before any output. The user restarted vast 59588200 again after saying "prepare it". Development data, not held-out.

**Result:**
- **VINE-R + registry passes every gate** (PASSES_GATES), as F7 + registry did in f7c.
- **Paired comparison:**
  - The two systems are equal on SD1.5 .2, SDXL .1 and Kandinsky 3 .2.
  - VINE-R recovers far more on SDXL .2 (64 against 32, Holm p 2e-9).
  - On SD1.5 .4, F7 recovers more (59 against 51), but not significantly after Holm (p .086).
- **Strict clean quality:** F7 63/64, VINE-R 37/64. VINE-R's failures are PSNR just under 35 dB; its SSIM and LPIPS are better than F7's.

## Run

- **Server:** vast 59588200, restarted at 14:31 UTC.
- **Code:** archive of `claude/f7-confirm-20261107` at 62f3467 (SHA-256 0b5b4c6c…). Six key files matched their git blobs.
- **Timeline (UTC):** setup 14:36-14:37; rehearsal and fit check 14:39 (forecast 2.3 h in total, under the 4 h stop rule); screen 14:40-15:21, FINISHED with no stop.
- **Speed:** VINE-R embeds in about 0.3 s per image and reads in about 0.02 s (F7: 30 s and 3.5 s).
- **Units:**
  - 64/64 VINE-R marks, 1,899 of 1,920 natives (21 safety-blocked, all SD1.5), 896/896 threat images and 2,923/2,923 reads OK;
  - every read keeps the full 100-bit decoded message.
- **Scoring:** on the server with `scripts/f7v_registry_score.py`, using the laptop-computed distractor features from f7c and the f7c F7 rows for the pairing.
- **Laptop check:** the 1.29 GB archive (SHA-256 e813eaba…) was fetched over 62 parallel HTTP streams; every part and the whole file matched. The laptop rescoring of the fetched images gives the same result as the server: 0 differing fields and 0 differing rows out of 960.
- **Stopped:** the instance was stopped from inside at 16:42:52 UTC, not destroyed. That is about 2.2 instance-hours, about USD 1.3 at an assumed USD .60/h; about 1 h of it was retrieval.

Data: MAIN `.thesis-build/dev-runs/20261108-f7v-vine-baseline/`.

## Gates (same bars as f7c)

| Gate | Bar | VINE-R + registry | F7 + registry (f7c) |
|---|---|---|---|
| F_R, SD1.5 .2 | ≥ 55/64 | 62 | 62 |
| F_R, SDXL .1 | ≥ 55/64 | 64 | 64 |
| F_R, Kandinsky 3 .2 | ≥ 55/64 | 64 | 64 |
| N1 T4 copy-paste (384) | 0 | 0 | 0 |
| N2 T5 false claim (64) | 0 | 0 | 0 |
| N3 wrong source | 0 | 0 of 1,015 | 0 of 1,014 |
| N4 C0 (1,012 unmarked) | 0 | 0 | 0 |
| N5 wrong owner (five cells) | 0 | 0 of 317 | 0 of 317 |

No negative was unknown.

## Paired comparison (pre-registered; source majorities out of 64, the same sources)

| Cell | VINE-R + registry | F7 + registry (P2) | Only VINE-R | Only F7 | McNemar p | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| SD1.5 .2 | 62 | 62 | 0 | 0 | 1 | 1 |
| SDXL .1 | 64 | 64 | 0 | 0 | 1 | 1 |
| Kandinsky 3 .2 | 64 | 64 | 0 | 0 | 1 | 1 |
| SDXL .2 | 64 | 32 | 32 | 0 | 4.7e-10 | 2.3e-9 |
| SD1.5 .4 | 51 | 59 | 1 | 9 | .021 | .086 |

The only difference that survives Holm is SDXL .2, in VINE-R's favour.

**Own-message agreement** (median per cell, out of 100, threshold 69):

| Cell | Median |
|---|---:|
| SD1.5 .2 | 88 |
| SDXL .1 | 97 |
| Kandinsky 3 .2 | 98 |
| SDXL .2 | 89 |
| SD1.5 .4 | 73 |

VINE-R is weakest under SD1.5 at .4. The rule alone accepts 59 sources there, but VINE-R's pointer reaches 56 and F_R 51.

## Pointer errors on negatives (the rule rejected all of them)

| Query set | VINE-R pointer fired | F7 presence fired |
|---|---:|---:|
| Unmarked images (1,012) | 5 | 0 |
| False-claim recipients, unmarked (64) | 2 | 0 |
| Copy-paste images, which carry the donor's real mark (384) | 132 | 143 |
| Wrong-owner message or key (317) | 0 | 0 |

**Why VINE-R's pointer fires by chance.** Its pointer works at 1e-4 per record, so with 64 records a chance match has a probability of about 6e-3 per query, about 6 expected among 1,012. The 5 observed fit that. F7's presence tests run at about 1e-6 and never fired.

**The rule stopped every one.** In this registry, VINE-R's chance pointers did not become accepts: an unmarked image only matches its own source's record, and a chance pointer almost never picks that record. A registry with many more records per owner would see more chance pointers.

## Quality of the marks (reported)

| | Strict pass | PSNR median | SSIM median | LPIPS median |
|---|---:|---:|---:|---:|
| VINE-R | 37/64 | 35.23 dB | .996 | .004 |
| F7 | 63/64 | 36.61 dB | .972 | .027 |

- **PSNR:** VINE-R's strict failures come from PSNR at or just below 35 dB.
- **SSIM and LPIPS:** VINE-R is clearly better than F7 on both.
- **Verdict:** under the project's strict gate F7 is the cleaner mark, but under perceptual metrics VINE-R is. Quality was not matched between the two; each ran at its own frozen strength. Human visual review is missing for both.

## What this means

1. **The registry result does not depend on F7.** With the same frozen round-3 rule, a published regeneration-robust watermark used as the pointer passes the same gates on the same fresh images. The registry layer is what gives zero copy-paste, false-claim and wrong-owner accepts, for both marks.
2. **F7 is not the stronger pointer under SDXL .2.** VINE-R reads 64/64 there, F7 32/64. F7 holds up better under SD1.5 .4 (59 against 51), but that difference is not significant.
3. **F7's advantages are narrower:**
   - a keyed owner (VINE-R's messages are public);
   - a lower chance-pointer rate (0 against 5 of 1,012);
   - better PSNR, so it passes the strict gate (63 against 37 of 64);
   - it was developed in this project.

   VINE-R's advantages: reach under strong SDXL regeneration, better SSIM and LPIPS, and about 100 times faster embedding and reading.
4. **For the thesis and an article, the contribution is the registry verification** (owner pointer plus an enrolled record checked by a frozen two-factor rule), shown to work with two different pointers. It should not be framed as F7 being a better watermark than VINE-R.

## Limits

- Development data, 64 sources per system; not a held-out confirmation.
- Quality was not matched between the marks.
- The registry has 348 records. VINE-R's chance-pointer rate grows with the owner's record count; so does P2's exposure for F7.
- The look-alike (E2) and further-regeneration cases are untested.
- Image-domain marks only; human visual review is missing.
