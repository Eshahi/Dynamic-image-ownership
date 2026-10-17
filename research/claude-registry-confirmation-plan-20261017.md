# Held-out confirmation plan: registry verification (draft for the user's approval)

Claude, 2026-10-17, at the user's request: "Prepare the held-out confirmation plan for my approval, and I will confirm the definition with my professor."

This is a plan only. No held-out image has been touched, and nothing runs until the user approves this plan and later the exact run manifest.

**Plan approved by the user on 2026-10-17, verbatim:** "I approve the held-out confirmation plan as written (DIV2K test, endpoints E1-E3, local run). Have Codex build the package and rehearsals; I will approve the exact manifest before the run. My professor has confirmed the definition (or I will tell you if not)." The DiffusionDB arm is not included.

## 1. What the run would confirm

> A regenerated copy of a registered image is matched to its correct owner record, using the F5 watermark as a pointer into the owner's registry, on at least 85% of new photographs (95% lower confidence bound). The regenerations are SD1.5 or SD2.1 image-to-image at strength .2. Unrelated images, copy-paste transfers and look-alikes that differ from the original more than the attack does are never accepted.

**Why it is needed:** round 3 passed only after the user classified synthetic look-alikes as "ambiguous" once the result was known. This run is the first test in which the method, the thresholds and the look-alike definition are all fixed in advance.

## 2. Frozen method (nothing may change after approval)

| Part | Frozen value |
|---|---|
| Watermark (pointer) | F5 r2, the frozen settings of `20261005-0640-f5-gate-soft-views7`, owner alpha; native decoder, owner found and code read, record q within radius 6 |
| Registry record | owner, record ID, q, plus the marked image's D1 (E3 native fine-detail vector) and B1 (32 × 32 grey layout vector) |
| Accept rule | D1 ≥ 0.0594367 and B1 ≥ 0.90. If D1 abstains (plain image), B1 ≥ 0.99. Frozen at `6e3527f` on `claude/registry-research`. |
| "Different image" definition | A look-alike is different only if its grey PSNR to the original is below **18.126 dB**, the 5th percentile of strength-.2 regeneration distances from development. This applies to real and synthetic look-alikes. Closer pairs are "ambiguous" and reported separately. |
| Scoring code | Round-3 scoring (`scripts/claude_round3_two_factor.py --mode evaluate`), changed only for input paths and hash-pinned in the run manifest |

## 3. Held-out data

**Photographs (primary).** All 300 sources of the admitted **DIV2K test split** (300 groups), canonicalized to 512 × 512 RGB8 by the unchanged contract.
- No development run has used DIV2K.
- COCO is not available: both earlier confirmations used all 600 COCO test groups (F5: 300, E3: 300).
- DIV2K differs from the COCO development images (higher-resolution originals, different content), so this is also a genuine generalization test. The frozen numbers may not transfer, and the run is designed to show whether they do.
- DIV2K is licensed for academic research: no redistribution of images.

**Real look-alikes.** 60 new pairs.
- Shots: the next 20 eligible Tears of Steel live-action shots after round 3, in listing order, with at least 289 frames. Pairs are frame 0 against +72, +144 and +288.
- Reserved by metadata only, before download.
- Any frame whose canonical hash matches any development frame is excluded and replaced by the next shot. Round 3 found one such duplicate shot.
- Limitation: they come from the same film as the development look-alikes.

**Synthetic look-alikes.** 12 pairs, seeds 21-32, chosen to avoid the texture seeds 11 and 12. They sit about 26.6 dB apart, so they are ambiguous by definition and are reported, not scored.

**Optional second domain, not included unless the user asks.** DiffusionDB test, for AI-generated images: one primary image per group from the first 300 groups in fixed hash order. It adds about 8 hours.

## 4. Attacks (T3, T4 and T5 only)

- **T3 regeneration.** SD1.5 and SD2.1-base (revision `4e63672c`) DDIM20 img2img at strengths .1, .2 and .4, seeds 15/16/17, empty prompt, guidance 1, SD1.5's safety checker as before. Marked (C1) and unmarked (C0) copies: 10,800 regenerations.
- **T4 copy-paste.** Residual transfer at scales .5 and 1.0, cyclic donor-to-recipient pairs in fixed hash order: 600 transfers.
- **Attribution after regeneration (T5-style).** An attacker regenerates the owner's image (.2 and .4, both regenerators), registers the copy under another owner, and queries with the copy and with a further regeneration.
- **Negatives.** Every suspect image against every other record (about 3.4 million unrelated pairs), T4 transfers against the donor's record, and all look-alike pairs.

## 5. Success criteria (all must hold)

| ID | Endpoint | Pass condition |
|---|---|---|
| E1 | Registry acceptance F_R at strength .2, majority of 3 seeds, per source | At least **266/300** on SD1.5 **and** on SD2.1, i.e. one-sided 95% Clopper-Pearson lower bound ≥ 0.85 |
| E2 | False accepts on "different" negatives (unrelated pairs, T4 transfers, real look-alikes below 18.126 dB) | **Zero** observed. Reported with the source-clustered 95% upper bound (about 1.0% at 0/300). |
| E3 | Attribution after regeneration | **Zero** wrong-owner attributions. The original-owner rate is reported against fingerprint-only matching. |

**Expected power for E1:** at a true rate of 97.5% (round 3), a pass is near-certain. At 92% the chance of passing is 98%, and at 90% it is 81%.

**Reported, not scored:**
- strengths .1 and .4;
- ambiguous look-alikes and synthetic look-alikes;
- D1-only and fingerprint-only arms;
- F5 mark quality (PSNR, SSIM, LPIPS);
- runtime, registry storage and the side information used.

## 6. How it would run

1. **After plan approval, Codex builds the package.** It extends the existing official runner and worker for this protocol and freezes the config and hashes. It writes a metadata-only held-out index, adds tests, and runs rehearsals on synthetic and development data only, never held-out pixels. One independent review follows.
2. **The user then approves the exact run manifest** (second approval), as the project rules require for held-out data.
3. **Run.** Local laptop GPU at USD 0, about 10-12 hours, resumable. Rough breakdown: F5 marks about 4.3 h, regenerations and detector calls about 4-5 h, descriptors and scoring about 1-2 h. A rented GPU would be used only with the user's separate approval, since it costs money. Disk use is about 15 GB, within the disk rule.
4. **M2.** Inventory, analysis with the frozen scoring code, a claims audit and one independent review.

## 7. What a pass would and would not show

**It would show:** registry attribution of SD-family regenerations at strength .2 on new real photographs, under a trusted registry and the stated look-alike definition, with zero observed false accepts against unrelated images, copy-paste transfers and clearly different look-alikes.

**It would not show:**
- robustness to other regenerators (SDXL, flow models);
- robustness to adaptive or white-box attacks;
- robustness at strength .4. F5's pointer is the weak point there; E3's pointer was stronger in development.
- an untrusted registry, legal ownership or ownership transfer (the last is product scope, per the supervisor);
- performance on generated images, unless the DiffusionDB arm is added.

## 8. Decisions needed

1. **The professor confirms the look-alike definition:** below 18.126 dB counts as different, applying to synthetic pairs too.
2. **The user approves this plan:** DIV2K test as the held-out set, endpoints E1-E3, local run.
3. **Optional:** add the DiffusionDB arm.

After the package is built, the user approves the exact manifest before the run starts.
