# Next step after F6: why F5 is stuck, and F7, a dual-carrier mark

Claude, 2026-11-02, after lean F6 stopped at Stage 1. New measurements here are CPU analyses of saved development data ([analysis/](analysis/)). No server, held-out data or new mark was used. This is a proposal: nothing is fixed or run.

## 1. F5 cannot be pushed further on its own

Five independent walls, each measured:

| Wall | Evidence |
|---|---|
| Its signal belongs to SD1.5 | 89% of F5's energy is above 64 cycles per image and drives the SD1.5 encoder. SD1.5 re-renders it after regeneration (retention .74); SDXL keeps .08 and K3 .17 (Phase A, frequency analysis). |
| The quality bar caps the budget | 46 dB is the largest robust budget that passes strict LPIPS on every image; 42 dB failed on a textured image even at half strength (lean Stage 1). |
| There is no transferable gradient | Gradients through SDXL's noisy codec are uncorrelated between noise draws (cosine about 0), and noise and x0 writers equal the plain budget control (lean probe and Stage 1). |
| The reader is tied to the SD1.5 VAE | Any F5 read on a foreign family depends on a mark that the foreign family does not re-render. |
| Component changes do not help | The 12-component study found no safe gain; every union reader that used the recomputed route failed copy-paste tests. |

So F5 stays the best SD1.5-family mark, and the foreign families need a different carrier.

## 2. Where the other carriers stand

**F5 and v5 fail in opposite places** (development, 60 sources, 3 seeds, source majority C):

| Cell | F5 | v5 | Either, if they did not interfere |
|---|---:|---:|---:|
| SD1.5 .1 | 60 | 47 | 60 |
| SD1.5 .2 | 57 | 27 | 58 |
| SD1.5 .4 | 39 | 3 | 39 |
| SDXL .1 | 0 | 50 | 50 |
| SDXL .2 | 0 | 12 | 12 |
| K3 .2 | 5 | 57 | 57 |

v5 writes a low-frequency pixel block-DCT pattern at about 36.9 dB. It survives independent encoders because it is image content, not encoder-specific. F5 writes an encoder-amplified pattern at about 45 dB, which SD1.5 regenerates faithfully. The held-out Phase B numbers point the same way (F5 182/200 at SD1.5 .2; v5 173/200 at SDXL .1 and 189/200 at K3).

**VINE as a carrier is weaker than its presence score suggests.** VINE-R decodes 100 known bits; a blind payload needs few errors.

| Cell | Median bit errors of 100 | At most 4 errors | At most 10 errors |
|---|---:|---:|---:|
| SD1.5 .2 | 12 | 8% | 43% |
| SDXL .1 | 2 | 74% | 94% |
| SDXL .2 | 10 | 19% | 52% |
| K3 .2 | 1 | 88% | 100% |

VINE-B's radius-4 decode would therefore fail on most SD1.5 .2 and SDXL .2 images. VINE-R also passes PSNR above 35 dB on only 52% of images (median 35.1, minimum 28.8). It is a strong baseline, not a free carrier, and it is not our method.

**Naive superposition costs something** (16 development sources, seed 12, per image). I added the saved F5 and v5 residuals, both before and after regeneration, which is a linear estimate, and read each carrier with its own unchanged reader:

| Cell | Either mark alone | Either carrier, both marks in one image |
|---|---:|---:|
| Clean | 16 | 16 |
| SD1.5 .2 | 14 | 12 |
| SDXL .1 | 9 | 6 |
| SDXL .2 | 2 | 1 |
| K3 .2 | 15 | 14 |

Naive superposition also fails strict quality on 13 of 16 images: median PSNR 35.7, LPIPS max .18. It stacks two second tiers and two full robust tiers, and neither writer sees the other. That is the problem the design below removes.

## 3. F7: one payload, two complementary carriers

**Idea.** Carry the same content-bound code q on both physical carriers. A reader accepts if either carrier reads it and the suspect's content matches. Each carrier covers the other's failure family.

**Writer, in order, all from existing frozen code:**
1. Compute q from the original's 7-view CLIP features, as F5 does.
2. Run v5's writer with those 7-view features, writing the pixel block-DCT carrier and its second tier. Lower its fill target from 35.5 to 36 dB to leave room for F5.
3. Run F5's 52 dB encoder PGD on the v5-marked image, then F5's second tier, refinement and final second tier. F5's PGD treats the v5 pattern as part of the host, so it compensates for it. The second tier is written once, not stacked.

Expected clean quality (derived): about v5 plus F5's robust share, a median near 36.7 dB and a minimum near 35.1 dB on development sources. LPIPS should rise by about .005 over v5 (F5's robust-tier LPIPS is .0054). This must be measured.

**Reader.** Both unchanged readers run on the suspect, v5's with 7-view features. Carrier C requires decoded score at least **8.34**, the frozen bound at 1e-6 over 2^33 patterns, plus content match. F7's C is carrier-F5 C or carrier-v5 C. Under the frozen null the union stays at or below 1e-6. There is no recomputed-only route; that route caused N3 and killed reader O.

**Secondary reader, exploratory only.** Both carriers use the same per-segment chip tables, so their segment scores can be added before decoding, a form of diversity combining. Where both carriers are weak, as at SDXL .2 and SD1.5 .4, it may read where neither does alone. With three tests at 1e-6/3 its threshold is 8.39. It is reported only, unless a later test fixes it as primary.

## 4. What F7 can and cannot do

**Likely gains**, from a rough estimate: SDXL .1 and K3 go from F5's 0 and 5 of 60 toward v5's 50 and 57, minus some interference. SD1.5 .2 stays near F5's level. That would make F7 the first own method that covers SD1.5, SDXL .1 and Kandinsky 3 at strict quality.

**Not fixed:**
- SDXL .2: the ceiling is 12/60 even without interference. Only VINE-R survives it, at a lower PSNR.
- SD1.5 .4: not improved, beyond whatever diversity combining adds.
- Two readers make extraction heavier, not lighter.
- J, latent insertion and human visual review are unchanged.

**Risks:**
- Interference on SDXL .1 could push it below 12/16; the naive estimate drops 9 to 6 per image.
- v5's carrier travels with copy-paste more readily than F5's (key delivered 18/20 in early v5 tests). Content binding stopped false attribution there, but the union must be tested on T4.

**My estimate:** about 40-50% for C at least 12/16 on SD1.5 .2, SDXL .1 and K3 together, with strict quality and zero false events. The chance on SDXL .2 is low.

**Novelty:** complementary carriers are a known idea. The contribution would be the measured complementary failure modes of encoder-amplified and pixel carriers, plus an error-controlled, content-bound union reader. That is thesis-level, not TIFS-level.

## 5. A cheap decisive test

- **Reuse:** the lean F6 server code, which is tested and ran cleanly. F7 adds one arm kind (two writers in sequence) and one reader dispatch (two readers).
- **Data:** Stage S screen of 16 donors with 16 targets, plus the 2+2 rehearsal; seeds 0-2.
- **Arms and cells:** F7, F5 r2, v5 r3 and unmarked. Cells SD1.5 .2 and .4, SDXL .1 and .2, K3 .2.
- **Threats:** T4, T5 and the 8 distortions on every arm.

**Gates, fixed before outputs:**
- **Core:** C at least 12/16 on SD1.5 .2, SDXL .1 and K3. F7 at least the better single carrier minus 2 in each core cell.
- **Always required:** strict quality 16/16; clean F at least 15/16; zero C events on C0, wrong owner and eligible T4/T5.
- **Reported:** SDXL .2, SD1.5 .4 and the combined reader.

**Cost:** F7 writes take about 25 s per image, so the whole run is about 2 hours including setup, roughly USD 1. The current RTX 4090 24 GB server works if it is restarted; it has 24 GB free disk with the models already in place.

## 6. Recommended next step

Run this one test, then stop the method search and write up: F5 as the SD1.5-family method; F7 if it passes; F6 and VINE-B as measured negatives with their causes. Further carrier ideas would need trained encoders, which is beyond this budget.
