# Two-factor instance check and the near-duplicate limit (Claude, 2026-10-17)

This is development evidence. The protocol is `claude-two-factor-instance-protocol-20261017.md`, frozen at commit `4049844` before any step-2b evaluation outcome was read. Thresholds were frozen at `909d56c` from the calibration split only.

**Runs:** MAIN `.thesis-build/dev-runs/20261017-1059-claude-two-factor-calibrate/` and `20261017-1100-claude-two-factor-evaluate/` (CPU, 24 s + 134 s, USD 0).

**Inputs:**
- D1 vectors and pointer outcomes from Codex's step-2b cache and evaluation scoring;
- the layout descriptor B1, computed here from the PNGs.

No held-out data were used.

## Result on the untouched evaluation split (40 sources, 13 near-duplicate pairs)

Frozen rule: D1 ≥ 0.0594367 **and** B1 (32 × 32 grey layout cosine) ≥ 0.98. The baseline is D1 alone at Codex's frozen τ = .586548.

| Source-majority F_R out of 40 (pointer and descriptor) | Two-factor | D1 alone (τ .587) |
|---|---|---|
| SD1.5 .1 | 35 | 35 |
| SD1.5 .2 | **35** | 30 |
| SD1.5 .4 | 11 | 7 |
| SD2.1 .1 | 37 | 37 |
| SD2.1 .2 | **35** | 32 |
| SD2.1 .4 | 12 | 8 |

**Negatives** (descriptor level, i.e. fingerprint-style, with no pointer required):

| Family | Pairs | Two-factor accepts | D1-alone accepts |
|---|---|---|---|
| Wrong source | 59,280 | 0 | 0 |
| T4 residual transfers | 80 | 0 | 0 |
| Synthetic siblings | 6 | 0 | 0 |
| Real near-duplicates (3 s apart) | 13 | **3** | 4 |

The real near-duplicate pairs are unmarked, so the registry arm, which needs the pointer, accepts none of them.

**Verdict:** the two-factor rule improves on D1 at .2 (+5 and +3 sources) and at .4 (+4 sources each). It still **fails** the development bar of 36/40 at .2 with zero observed false accepts:
- it reaches 35/40 on both regenerators;
- 3 of 13 near-duplicate pairs are accepted at descriptor level.

My recount of Codex's D1-alone numbers (30 and 32 at .2; 7-8 at .4; 4 near-duplicate accepts) matches its frozen evaluation exactly.

## Why no descriptor can fix this

| Pixel distance (grey PSNR) | Value |
|---|---|
| Accepted near-duplicate pairs (tos-03_2j, 04_1a, 04_2b, 04_3b) | 23.0 / 26.4 / 26.4 / 28.2 dB (SSIM .84-.94) |
| Rejected near-duplicate pairs | 13.0-21.3 dB |
| Regenerated copy vs its record, strength .1 | median 25.8 dB (5-95%: 19.0-29.4) |
| Same, strength .2 | median 24.1 dB (18.1-27.5) |
| Same, strength .4 | median 20.7 dB (16.5-24.7) |

A strength-.2 regeneration moves an image as far as re-filming a nearly still scene three seconds later; at .4 it moves it further. Any content-based instance check therefore faces the same choice:
- accept the regenerated copies and with them the closest recaptures, or
- reject the recaptures and with them many regenerated copies.

This is the stability-against-specificity trade-off the descriptor round met at 32 bits. It persists with unlimited registry capacity, so it is a property of the problem definition, not of D1, B1 or compression.

## Why the two-factor rule misses at .2 (post-hoc diagnostic; informs the next protocol only)

Run: MAIN `.thesis-build/dev-runs/20261017-1106-claude-two-factor-diagnostic/run.json`. Failing evaluation sources and their causes under the frozen thresholds:

| Cell | Failing sources | Cause |
|---|---|---|
| .2, both regenerators | 1637, 1655, 1670 | D1 abstains on every seed (native weak-detail floor; plain images). They also fail at .1, so this is descriptor availability, not regeneration loss. |
| .2, both regenerators | 1737, 2315 | B1 just below 0.98 on every seed |
| .2, SD1.5 | none | 2 pointer-loss seeds, below source-majority level |
| .4 | most | B1 < 0.98 (56-57 of 120 seeds), pointer loss (16-18) and the same three abstentions |

**Implications for a next, freshly validated round:**
- a declared fallback for D1-abstaining images, for example B1 plus D2, would address 3 of the 5 misses at .2;
- the 0.98 layout threshold is too tight for .4.

Both changes are hypotheses formed on consulted data and need new images to test.

## Consequences

1. **Report it as a measured limit.** "Instance identity after regeneration is bounded by natural recapture similarity." Show the curve of regeneration strength against the closest rejectable near-duplicate distance.
2. **Make "different instance" an explicit definition, not a dataset accident.** Three-second pairs from near-static shots are, in pixel terms, closer than the attack. A defensible definition ties the near-duplicate negatives to a measured distance larger than the declared attack budget, for example frame pairs below the 5th-percentile PSNR of strength-.2 regenerations. Both the definition and the threshold must be fixed before fresh data are seen. This is a user and supervisor decision.
3. **The watermark's role is confirmed.** The ambiguity concerns unmarked look-alikes and only affects fingerprint-only matching. The registry arm needs the recovered pointer and accepted no near-duplicate pair. The regenerate-and-enroll scenario shows the pointer naming the original owner where fingerprints match both.
4. **Next step if pursued:** freeze the definition and the two-factor rule (or D1) and replicate on fresh development images and new near-duplicate shots. Only then decide on a held-out confirmation, which needs the user's approval.
