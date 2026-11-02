# F7 dual-carrier test protocol

Fixed by Claude on 2026-11-02, before any F7 mark exists, at the user's instruction ("Yes, build and test"). The receipt is [decisions/f7-user-choice.json](decisions/f7-user-choice.json), and the design reasons are in [PROPOSAL.md](PROPOSAL.md). This is a development screen; no held-out data is used.

## Method

**Writer:**
1. Compute q from the original's 7-view CLIP features.
2. Run the unchanged v5 r3 writer with those features. It writes v5's pixel block-DCT carrier and its second tier, with its profile unchanged.
3. Run the unchanged F5 r2 writer on that image with the same features: 52 dB encoder PGD, second tier, refinement, final second tier. Its second tier replaces v5's, so the image carries one second tier.
4. If the result misses a small cushion over strict quality (PSNR above 35.05 dB, SSIM above .901, LPIPS below .098), scale the v5 residual by .9, .8, then .7 and repeat step 3. A failure after .7 is kept and counted as a failure.

Both carriers carry the same q, because both writers take the same features.

**Reader.** The unchanged F5 reader and the unchanged v5 reader both run on the suspect, each with 7-view features. A carrier reads at α/2 if its decoded score is at least **8.341671**, the frozen bound at 1e-6/2 over 2^32 patterns, its read flag is set, and its content matches. **C for F7 is either carrier reading at α/2.** The family-wise false-positive bound stays at 1e-6. There is no recomputed-only route. F, H and A count either reader, because both read the one shared second tier, which the F5 path writes last; D is H and J.

**Combined reader (exploratory, reported only).** Let a and b be the F5 and v5 chip projections, each normalized to unit length. The frozen key test runs on c = a + b, normalized as usual by the length of c. This keeps the statistic a normalized weighted sum of independent keyed signs, so the frozen bound applies, here at 1e-6/3. Content status uses F5's soft binding. This reader enters no gate.

## Inventory

- **Sources:** Stage S, the 2+2 rehearsal first, then the 16+16 screen.
- **Arms:** unmarked, F5 r2, v5 r3, F7.
- **Cells:** SD1.5 .2 and .4, SDXL .1 and .2, Kandinsky 3 .2.
- **Seeds:** 0, 1 and 2, with shared C0 tapes.
- **Threats and distortions:** T4, T5 and the 8 secondary distortions on every arm.
- **Reads:** every arm is read by its own reader; F7 reads C0 with the F7 reader.

## Gates, fixed before outputs

Counts are source majorities of 3 seeds. Missing seeds give a lower and an upper count.

| Gate | Bar |
|---|---|
| C, SD1.5 .2, SDXL .1 and K3 .2 | At least 12/16 each |
| Against the better single mark (F5 or v5) in those three cells | F7 loses at most 2 sources |
| Clean quality | Strict on 16/16 |
| Clean F | At least 15/16 |
| C0 and wrong-owner C or F, under the F7 reader | Zero |
| T4 and T5 C events, combined mode, quality-eligible images | Zero |

Labels: **GO** if all gates pass; **SCIENTIFIC_KILL** if one fails; **INCOMPLETE** or **RESOURCE_STOP** if missing work decides it, never a scientific result.

**Reported, entering no gate:** SDXL .2 and SD1.5 .4; J; each carrier alone at α; the combined reader; secondary distortions; VINE is not run.

## Money and stop

The run uses the lean F6 code, setup, cap and disk floor. The cap is the smaller of 34 instance-hours and USD 18.7 at the actual price. The rehearsal must finish without implementation errors before the screen starts. When the run ends, Claude packs and fetches the results, then stops the instance. No source, seed or arm is cut to fit.
