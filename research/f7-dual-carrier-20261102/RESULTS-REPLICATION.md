# F7 registry replication on fresh sources (f7c): results

Run by Claude on 2026-11-08 under [REPLICATION-PROTOCOL.md](REPLICATION-PROTOCOL.md), frozen 2026-11-07 before any output. The user restarted vast instance 59588200 and sent its SSH line. Development data, not held-out.

**Status: PASS on every gate. The pre-registered H-fix hypothesis is supported.**

## Run

- **Server:** vast 59588200 (RTX 5000 Ada 32 GB, 251 GB RAM, 32 threads), restarted by the user. Its models from stage B were still on disk, so setup took 33 s.
- **Timeline (UTC):**
  - 08:47 container start; 09:03 driver start, after the fresh sources were uploaded and hash-checked;
  - rehearsal finished, fit check passed at 09:08 (forecast 4.2 h in total, under the 6 h stop rule);
  - screen 09:09-11:08, FINISHED with no stop and no failed unit;
  - instance stopped from inside at 13:33, not destroyed.
- **Time and cost:** about 4.8 instance-hours, about USD 2.9 at an assumed USD .60/h (the price was not given). About 2 h of that went to retrieval.
- **Code:** archive of `claude/f7-confirm-20261107` at 83d8539 (SHA-256 3834b608…). Git blob ids of the driver, scorer and manifest matched on the server.
- **Sources:** 128 fresh photos in `f7c-sources.tar` (8d53af22…). All 132 manifest PNGs passed the hash check on the server.
- **Units:**
  - 64/64 F7 clean marks were written; every one carries the same q on both carriers.
  - 1,898 of 1,920 natives; SD1.5's safety checker blocked 22.
  - 896/896 threat images and 2,922 reads.
- **Blocked units:** F7 natives blocked were R0-0.2 sources 7740 and 7789 (all three seeds), 4189 (seed 1) and 7934 (seed 1); R0-0.4 source 7740 (seeds 0 and 2). Under the protocol they count as misses.

**Retrieval deviation, recorded here.** The link from the laptop to the server ran at about 17 KB/s per connection, while the server itself uploaded at about 42 MB/s. The registry was therefore first scored on the server: `scripts/f7c_remote_score.py` (1ce0b23) ran the unchanged scorer, with the distractor records' D1 and B1 vectors computed on the laptop.
- **Feature check:** on three distractor images, the server's own features matched the laptop's exactly (largest difference 0.0).
- **Full archive:** the 1.32 GB archive (SHA-256 96e4be9a…) was then fetched over 64 parallel HTTP streams from a temporary token-path file server on the instance. Every part passed its checksum and the whole file matched.
- **Laptop rescoring:** the protocol's own path, `scripts/f7c_registry_score.py` on the fetched images (each checked against its journal SHA-256), gives the same result as the server: 0 differing fields and 0 differing rows out of 960.

Data: MAIN `.thesis-build/dev-runs/20261108-f7c-replication/` (`unpacked/`, `score-server/`, `score-laptop/`, `extra/`, `distractor-features.json.gz`).

## Gates (section 5)

The owner's registry held 64 fresh records and 284 distractor records; none was dropped.

| Gate | Bar | Result | Status |
|---|---|---|---|
| F_R under P2, SD1.5 .2 | ≥ 55/64 | 62 (the 2 misses are the fully blocked sources) | pass |
| F_R under P2, SDXL .1 | ≥ 55/64 | 64 | pass |
| F_R under P2, Kandinsky 3 .2 | ≥ 55/64 | 64 | pass |
| N1 T4 copy-paste | 0 | 0 of 384, under P1 and P2 | pass |
| N2 T5 false claim | 0 | 0 of 64 | pass |
| N3 wrong source | 0 | 0 of 1,014 queries × 347 other records (10 blocked) | pass |
| N4 C0 | 0 | 0 of 1,012 unmarked images × 348 records (12 blocked) | pass |
| N5 wrong owner | 0 | 0 in all five cells (317 evaluable copies) | pass |

No negative was unknown.

## Detail by cell (source majorities out of 64)

| Cell | F_R P2 | F_R P1 | Presence | P1 pointer | Rule alone | Sources only P2 recovers | Lowest D1 | Lowest B1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SD1.5 .2 | 62 | 62 | 62 | 62 | 62 | 0 | .460 | .928 |
| SDXL .1 | 64 | **36** | 64 | 37 | 64 | 28 | .626 | .991 |
| Kandinsky 3 .2 | 64 | 58 | 64 | 58 | 64 | 6 | .730 | .978 |
| SDXL .2 (reported) | **32** | 2 | 32 | 2 | 64 | 30 | .458 | .973 |
| SD1.5 .4 (reported) | 59 | 49 | 63 | 53 | 59 | 10 | .259 | .796 |

- **H-fix:** on SDXL .2, P2 recovers 30 sources that P1 misses and loses none (exact one-sided McNemar p = 9.3e-10). It is supported.
- **P2 never lost a source to P1 in any cell.** P2 never accepted a second record either, fresh or distractor ("other-record accepts" 0 in every cell).

## What the replication shows

1. **The registry design replicates on unseen images.** The frozen round-3 rule accepts every regenerated copy against its own record:
   - 64/64 on SDXL .1, Kandinsky 3 .2 and SDXL .2;
   - 62/62 unblocked on SD1.5 .2;
   - 59 on SD1.5 .4, where B1 falls to .80 for one source.

   D1 survives the independent encoders with a wide margin: the lowest is .46, against τ1 .059.
2. **The old pointer did not replicate on SDXL .1.** Stage B had 14/16; here it gives 36/64. The 16-source development estimate was optimistic. With P1 alone, the replication would have failed its SDXL .1 bar.
3. **The presence fallback is what makes the system pass.**
   - Presence was positive in 64/64 sources on SDXL .1 and Kandinsky 3, and in 32/64 on SDXL .2 (P1: 2).
   - It never fired on the 1,012 unmarked images or on the 64 false-claim recipients.
   - It never fired under the attacker's key in 317 copies.
4. **Copy-paste stays blocked by the record check.**
   - Presence fired on 143 of the 384 copy-paste images, since they carry the donor's real mark.
   - The rule accepted none of them against any of the 347 records other than the recipient's. Fingerprint-only accepts were 0 too.
5. **Wrong owner:**
   - Fingerprint-only matching names the attacker's enrolled copy in every evaluable case (62, 64, 64, 64 and 63).
   - The pointer registry never does.
   - The original owner is the unique attribution in 62, 64, 64, 36 and 58.

## Quality of the F7 marks (reported)

63 of 64 pass strict clean quality (PSNR > 35 dB, SSIM > .9, LPIPS < .1):
- PSNR 35.07-44.70 dB, median 36.61;
- SSIM at least .944;
- LPIPS median .027.

One mark ended at the writer's weakest v5 scale (.7) with LPIPS .131. Stage B had 16/16. This does not gate the registry test, but it is a writer limit to report.

## Limits

- **Not a held-out confirmation.** The 128 photos were never used before in this project, but they are development-reserved. A held-out confirmation still needs the user's approval and a new cohort.
- **P2 was designed on stage-B outputs.** This run is its first test on unseen images, and it passed.
- **Registry scale:** 348 records. P2's false-accept exposure grows with the owner's record count. No unrelated record was accepted here (0 of about 350,000 comparisons for N3, 0 of about 352,000 for N4), but larger registries are untested.
- **Presence false positives:** 0 in 1,012 unmarked images and 0 in 317 wrong-key reads. That is not a population bound below about 0.3%.
- **Bounds on zero counts:** zero of 384 copy-paste images bounds the per-image rate below about 0.8% (one-sided 95%), ignoring the clustering by source.
- **Gaps:**
  - SDXL .2 is half solved (32/64).
  - Look-alikes (E2) and further regeneration are untested.
  - One mark misses strict quality.
- **Method domain:** an image-domain mark, not the proposal's latent method. Human visual review is missing.
