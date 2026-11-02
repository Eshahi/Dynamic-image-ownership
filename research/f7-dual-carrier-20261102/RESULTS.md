# F7 dual-carrier test: results

Run by Claude on 2026-11-02, under [PROTOCOL.md](PROTOCOL.md) and the user's receipt ("Yes, build and test"). Development Stage S sources only. **Status: SCIENTIFIC_KILL.** Every regeneration, quality, C0 and wrong-owner gate passed. The one failure was the copy-paste gate: 3 eligible T4 C events, all from the v5 carrier.

## Run

- **Server:** vast container 58795791 (restarted), RTX 4090 24 GB, EPYC 7Y83, 76 GB disk.
- **Clock:** container up at 13:05:10 UTC. Setup finished 13:12 (it reused the verified models). The rehearsal finished 13:23, the screen decided 14:34, and the instance was stopped, not destroyed, at 14:41 UTC. That is about 1.6 instance-hours. The price was not given, so the cap used USD .60/h, which puts the cost at about USD 1.
- **Code:** commit 06545ee on `claude/f7-dual-20261102`. File hashes matched on the server.
- **Retrieved:** MAIN `.thesis-build/dev-runs/20261102-f7-dual/f7-results.tgz`, SHA-256 30e20121…b313b1a6, with logs in `f7-extra.tgz`, unpacked beside them. Native images other than the seed-0 samples of the unmarked and F5 arms stay on the stopped instance's disk.
- **Rehearsal:** 2 sources, every unit ok. The fit check needed 2.75 h of the 31.2 h cap, so the screen started.

## Gates (16 screen sources, 3 seeds, source majority)

| Gate | Bar | F7 | Status |
|---|---|---|---|
| C, SD1.5 .2 | ≥ 12 | 16 | pass |
| C, SDXL .1 | ≥ 12 | 13 | pass |
| C, Kandinsky 3 .2 | ≥ 12 | 15 | pass |
| Loss to the better single mark (16, 14, 16) | ≤ 2 | 0, 1, 1 | pass |
| Strict clean quality | 16/16 | 16/16 | pass |
| Clean F | ≥ 15 | 16 | pass |
| C0 events under the F7 reader | 0 | 0 | pass |
| Wrong-owner events | 0 | 0 | pass |
| Eligible T4 and T5 C events | 0 | **3** | **fail** |

## C by arm and cell

Each arm is read by its own reader. SDXL .2 and SD1.5 .4 are reported only.

| Cell | F5 r2 | v5 r3 | F7 | F7, F5 carrier | F7, v5 carrier | F7, combined reader |
|---|---:|---:|---:|---:|---:|---:|
| SD1.5 .2 | 16 | 8 | 16 | 16 | 3 | 16 |
| SDXL .1 | 0 | 14 | 13 | 1 | 13 | 14 |
| Kandinsky 3 .2 | 0 | 16 | 15 | 2 | 15 | 15 |
| SDXL .2 | 0 | 0 | 1 | 0 | 1 | 1 |
| SD1.5 .4 | 14 | 1 | 14–15 | 14–15 | 0 | 12 |

The union works as designed. F7 keeps F5's SD1.5 reads and v5's SDXL .1 and Kandinsky 3 reads, losing at most one source to the better single mark. SDXL .2 stays unsolved, as expected. The exploratory combined reader is no better than the union. J, reported only: 12, 0, 7, 0 and 9 in the order of the table.

## Quality and distortions

| Arm | PSNR median (min) | LPIPS median (max) | SSIM median |
|---|---|---|---|
| F5 r2 | 45.1 (42.8) | .024 (.062) | .981 |
| v5 r3 | 37.8 (35.2) | .021 (.046) | .977 |
| F7 | 37.5 (35.06) | .033 (.073) | .971 |

The writer put the same code on both carriers for 16/16 images. Five needed the v5 residual scaled to .9; none went lower. F7's distortion is close to v5's, and well above F5's.

Secondary distortions, C out of 16: F7 reads 16 under blur, brightness, contrast, JPEG 50 and 90, noise and resize. F5 alone reads 10, 7 and 13 under blur, JPEG 50 and noise. Every arm reads 0 after the 90% crop.

## Why it failed

The three events are full and half residual copies onto the most similar hosts in the pair list: 1647→636 at residual .5 and 1.0, and 853→1536 at residual 1.0. These pairs have CLIP cosines of .70 and .75, the third-highest and highest of the 16. In all three the v5 carrier read and its content check matched. The F5 carrier did not read: decoded 3.3–4.6 against 8.34.

v5 alone shows the same weakness on the same screen: 4 eligible events, on 1647→636, 853→1536 (twice) and 1359→1786. F5 alone has none. F7 inherited v5's copy-paste behaviour, a risk the proposal named.

**Post-hoc look, not a result.** The copied v5 residual is read on almost every host (decoded 8–15). The only guard is the content check. It accepts a 32-bit sketch distance up to about 5.3 bits after correction. Genuine regenerated reads use that whole range, up to 5.29 on Kandinsky 3. The copies onto near-duplicate hosts landed at 3.28–5.0 for F7, and one v5 copy landed at 2.28.

No tolerance separates the two. A tolerance below 3.2 would have removed F7's three events here, but it would cut v5's majority reads in F7 to 11/16 on Kandinsky 3 and 12/16 on SDXL .1. It would still not have stopped v5's 2.28 copy. A tolerance chosen on these outputs would not be admissible anyway.

The limit is structural: a 32-bit content sketch cannot tell a regenerated original from a residual copied onto a host with similar content. This matches the earlier finding that the binding loss is set by the 32-bit sketch.

## What this means

- **The carrier half of the F7 idea works.** On fresh development sources, the two carriers' failures are complementary, and one shared code and second tier make the union usable, at v5's quality cost.
- **The binding half does not.** Any carrier that survives regeneration as well as v5's also survives a copy onto a similar host. The current content binding cannot stop that.
- **A successor needs a stronger binding**, not a stronger carrier. Examples: a longer or differently derived content sketch, a sketch tied to fine structure that a copy does not bring along, or F5-style latent binding applied to the v5 code. It would need a new protocol with the T4 gate unchanged, and fresh sources.
- **The pair distinctness labels are still missing**, so a human has not checked whether 636 and 1536 are near duplicates of their donors. That question is open; it is not a rescue. The gate counts these events, as fixed before outputs.

## Claim limits

This is a development screen, not a confirmation. The writer works in the image domain, not by latent insertion. Two readers mean heavier extraction. Human visual review is missing. VINE was not run.
