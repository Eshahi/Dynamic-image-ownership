# F7 as the registry pointer: results

Run by Claude under [REGISTRY-PROTOCOL.md](REGISTRY-PROTOCOL.md), after the user's "Yes, run it". Development data only. **Status: PASS. Stage A passed on 2026-11-06. Stage B, run 2026-11-07 on a rented GPU after the user's "I'll rent it", passed every gate.** Stage B's results are at the end of this file.

## What happened to the data

- **Before the instance was destroyed:**
  - The protocol was frozen (a0ef66c, amendment 0d9046d), and the scorer was written (f871af0).
  - The section 5 futility check passed on the laptop's unmarked seed-0 natives.
- **Instance destroyed:** the user destroyed instance 58795791 before the 510 images were fetched. The F7 natives and the server's copies of the threat images are lost.
- **Amendment 2 (2137fdf, before any registry score of an F7 threat or native):**
  - **Rebuild:** the 112 F7 copy-paste and false-claim images were rebuilt on the laptop with the run's own arithmetic.
  - **Pixel check:** they were verified by pixels, because the laptop's PNG encoder writes different bytes. Each image's mean squared RGB difference to its recipient equals the run's quality-journal value; the largest error was 0.0.
  - **Split:** the gates were divided into stage A (scorable now) and stage B (needs regenerated natives).

Outputs: MAIN `.thesis-build/dev-runs/20261102-f7-registry/` (`proxy/`, `rebuild-2137fdf/`, `stage-a/`, `manifest/`). The first rebuild attempt, which checked bytes only, was overwritten before any score was computed.

## Futility check (section 5)

The frozen rule, without the pointer, was applied to each seed-0 native against the same arm's clean image.

| Cell | Unmarked: pass / 16 | Unmarked: lowest D1 | F5 r2: pass / 16 |
|---|---:|---:|---:|
| SD1.5 .2 | 16 | .585 | 16 |
| SDXL .1 | 16 | .745 | 16 |
| Kandinsky 3 .2 | 16 | .817 | 16 |
| SDXL .2 | 16 | .621 | 16 |
| SD1.5 .4 | 16 | .392 | 15 |

The D1 threshold is .0594. **The registry descriptor survives SDXL and Kandinsky 3 regeneration at 1024 px with a wide margin.** This was the main unknown in the recommendation. One source per cell has D1 abstaining (a plain image) and passed through the B1 ≥ .99 fallback.

## Stage A gates

| Gate | Images | Registry accepts | Status |
|---|---:|---:|---|
| N1 T4 copy-paste (patch 128 and 256, shams, residual .5 and 1.0) | 96 | 0 | pass |
| N2 T5 false claim (recipient unmodified) | 16 | 0 | pass |
| N3 wrong-source, F7 clean queries (the natives are lost) | 16 × 15 records | 0 | pass (partial) |
| N4 C0, local unmarked images (16 clean, 80 seed-0 natives) | 96 × 16 records | 0 | pass (partial) |
| F_R ≥ 12/16 on SD1.5 .2, SDXL .1, Kandinsky 3 .2 | — | — | not evaluable |
| N5 wrong owner | — | — | not evaluable |

The F7 clean images are each accepted against their own record (16/16), as a sanity check.

**The copies that killed F7 are rejected.**
- The pointer did select the donor's record for 32 of the 112 threat images: all 16 residual 1.0 copies, 14 residual .5 copies and 2 patch-256 copies.
- The rule turned every one of them down. Among these 32, the highest D1 is .285 and the highest B1 is .580, against a B1 bar of .90.
- The copies behind the F7 kill (1647→636 and 853→1536, residual .5 and 1.0) score B1 .07-.13 against the donor's record.

## Post-hoc look, not a gate

- **The layout factor does the work.** Over all 112 threat images, 71 have D1 at or above τ1 = .0594: a pasted residual or patch carries the donor's fine detail. B1 rejects every one; the highest is .742, a margin of .16 below .90.
  - D1 alone would have failed copy-paste here.
  - The two-factor rule fixed in round 3 holds, but its copy-paste safety rests on B1.
- **Pointer alone on the F7 positives** (saved detect rows, source majority):
  - Core cells: SD1.5 .2 16, SDXL .1 14, Kandinsky 3 .2 15.
  - Reported cells: SDXL .2 1, SD1.5 .4 15.
  - This is the upper bound on F_R. With the futility check passing at 16/16, stage B is likely to clear the 12/16 bar. That is a forecast, not a result.

## What stage A means

The registry does what the in-mark content check could not: it stops copy-paste while the F7 pointer reads where F5's cannot. Whether F7 natives pass the rule against their own record (F_R), and the wrong-owner case, still need regenerated F7 natives (stage B).

## Limits

- **Overlap:** 10 of the 16 sources were round-3 calibration sources of the frozen rule (listed in the protocol), so the negatives may be somewhat optimistic for those donors.
- **Scale:** this is a 16-source development screen, not a confirmation.
- **Not retested:** the look-alike limitation (E2) belongs to the rule and is not retested here.
- **Method domain:** F7 is an image-domain mark, not the proposal's latent method.
- **Human review:** human visual review is missing.

# Stage B (2026-11-07): PASS

## Run

- **Server:** vast instance 59588200, rented by the user. RTX 5000 Ada 32 GB, Threadripper PRO 3955WX, 251 GB RAM, 107 GB disk.
- **Clock:**
  - The container came up about 15:00 UTC.
  - Setup ran 15:13-16:09; it downloaded every model again.
  - The rehearsal and fit check finished at 16:19. The 16-source screen ran 16:19-17:26.
  - After the fetch, Claude stopped the instance from inside at 17:35 UTC; it was not destroyed.
  - Total about 2.6 h, about USD 1.55 at an assumed USD .60/h. The price was not given.
- **Code:** an archive of commit 06545ee, unchanged since the F7 run (SHA-256 8c16098e…; sources 8ff80ebf…). File hashes matched git on the server. The driver was the same F7-mode `f6l_driver.sh`.
- **Retrieved:** a 345 MB archive (SHA-256 946f4ee6…) of both runs' journals and logs, plus all 735 images of the F7 and unmarked arms. Folder: MAIN `.thesis-build/dev-runs/20261107-f7-registry-stage-b/`, with `unpacked/`, `extra/`, `score/` and `score-9030064/`.
- **New images:** none of the F7 marks or natives, and none of the unmarked natives, is byte-identical to the first run's; a different GPU gives small numeric differences. Only the threat images built without the F7 mark (shams, unmodified) are identical.

**F7 screen replication.** The driver's own F7 decision is again SCIENTIFIC_KILL, with the same numbers as on 2026-11-02:
- C 16/13/15, losses 0/1/1;
- strict quality 16/16, F 16;
- C0 0, wrong owner 0;
- 3 eligible T4 events.

The F7 result replicates on new hardware.

## Registry gates (full protocol, sections 2-4)

| Gate | Bar | Result | Status |
|---|---|---|---|
| F_R, SD1.5 .2 | ≥ 12/16 | 16 | pass |
| F_R, SDXL .1 | ≥ 12/16 | 14 | pass |
| F_R, Kandinsky 3 .2 | ≥ 12/16 | 15 | pass |
| N1 T4 copy-paste | 0 | 0 of 96 | pass |
| N2 T5 false claim | 0 | 0 of 16 | pass |
| N3 wrong-source | 0 | 0 of 256 queries × 15 records | pass |
| N4 C0 | 0 | 0 of 255 images × 16 records (1 blocked by the safety checker) | pass |
| N5 wrong owner | 0 | 0 in each core cell | pass |

No negative was unknown.

## Detail

| Cell | F_R | Pointer alone | Rule alone | F_R via F5 carrier | F_R via v5 carrier | Lowest D1 | Lowest B1 | D1 abstained (seeds) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SD1.5 .2 | 16 | 16 | 16 | 16 | 2 | .549 | .983 | 2 |
| SDXL .1 | 14 | 14 | 16 | 1 | 14 | .722 | .997 | 0 |
| Kandinsky 3 .2 | 15 | 15 | 16 | 2 | 15 | .789 | .992 | 3 |
| SDXL .2 (reported) | 1 | 1 | 16 | 0 | 1 | .578 | .992 | 2 |
| SD1.5 .4 (reported) | 14 | 15 | 15 | 14 | 0 | .381 | .951 | 3 |

Counts are source majorities out of 16. The rule accepts every regenerated F7 copy against its own record in every cell; at SD1.5 .4 it misses one source.

**The pointer is now the only limit.** Each carrier covers different cells, as in the F7 screen, and the union gives the pointer everywhere except SDXL .2.

**Single-mark baselines, pointer alone (an upper bound on their F_R):**
- F5 r2: 16, 0 and 0 on the three core cells, so registry verification with F5 fails on SDXL and Kandinsky 3, as known.
- v5 r3: 8, 14 and 15; it fails SD1.5 .2.

Only the dual carrier passes all three.

**Copy-paste.**
- The pointer selected the donor's record for 31 of the 112 threat images (16 residual 1.0, 13 residual .5, 2 patch 256). The rule rejected all 31: highest D1 .285, highest B1 .579.
- Over all 112 threat images, 71 reach D1 ≥ τ1, but B1 stays at or below .742. As in stage A, B1 is what stops copies.

**Wrong owner (N5).**
- The attacker enrolled each seed-0 copy under their own key. Fingerprint-only matching attributes the copy to the attacker's record in 16 of 16 sources per cell.
- The pointer registry never does: the attacker's key found no pointer in any copy.
- The original owner is the unique attribution in 16, 14 and 16 sources. The two SDXL .1 sources without attribution are seed-0 pointer misses, not wrong attributions.

**Unmarked images (N4).** The pointer never fired, and no F7 record was accepted through it. Fingerprint-only matches 253 of 255 unmarked images to their own source's record; this is expected, because the content is the same.

## Scorer bug, found and fixed before reporting

The first stage-B scoring (`score/`, commit 9e10ad1) labelled owners with `owner[-5:]`. That gives "-beta", so a beta match could never count as a wrong owner, and N5 was vacuous. The sign: fingerprint-only matching showed 0 beta matches, although the attacker's record is the query image itself.

Commit 9030064 fixes the labels. The rescoring (`score-9030064/`) is identical in every other field and gives the N5 result above. Both outputs are kept.

## What this means

- **The registry result extends to SDXL and Kandinsky 3.** With F7 as the pointer, the frozen round-3 registry rule clears every gate on SDXL .1 and Kandinsky 3 .2, where F5's pointer gives nothing, and on SD1.5 .2.
- **It closes F7's failure.** F7 alone failed only on copy-paste. The registry removes that failure: 0 of 112 copy-paste and false-claim images, and 0 wrong-owner attributions, where fingerprint-only matching is fooled every time.
- **The two parts complement each other:** the dual carrier supplies a pointer that survives three regenerators, and the enrolled record supplies the binding that a 32-bit in-mark sketch cannot.

## Limits

- **Scale:** this is a development screen on 16 sources. It is not a confirmation, and it is underpowered for rare false accepts. Zero of 96 T4 images bounds the per-image rate below about 3% (one-sided 95%).
- **Calibration overlap:** 10 of the 16 sources were round-3 calibration sources of the frozen rule.
- **Not covered:**
  - SDXL .2 stays unsolved, because the pointer is missing there.
  - The look-alike limitation (E2) belongs to the rule and is not retested.
  - The further-regeneration attribution case is not covered.
- **Method domain:** F7 is an image-domain mark, not the proposal's latent method. Human visual review is missing.
- **Next step:** a claim for the thesis would need a pre-registered round on fresh sources never used in calibration. A held-out confirmation also needs the user's approval and a new held-out cohort, because COCO test and DIV2K test are already used.
