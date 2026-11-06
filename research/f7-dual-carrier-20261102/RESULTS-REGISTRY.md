# F7 as the registry pointer: results

Run by Claude under [REGISTRY-PROTOCOL.md](REGISTRY-PROTOCOL.md), after the user's "Yes, run it". Development data only, laptop CPU, USD 0. **Status: STAGE_A_PASS. Stage B (the regeneration gates F_R and N5) has not been run.**

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
