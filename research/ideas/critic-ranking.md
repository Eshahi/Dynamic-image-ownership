# Critic ranking — F5 ideas lenses A, C, D

Scope: F5 r2 49/58 @.4, 37/58 @.5, 10/57 @.6. T4 0/20, T5 0/66, clean LPIPS mean .0173 max .050 must hold. GPU: 37s/image, full stress 37 min, 4-source pilot ~10 min.

## Ranking by expected Δ@.5 per GPU minute

| rank | lens | short name | exp Δ .4 | exp Δ .5 | exp Δ .6 | GPU min | risk T4/T5 | conf |
|---:|------|------------|--------:|--------:|--------:|------:|------------|------|
| 1 | A-P2 | UEP / water-filling across q bits | +3 to +5 | +2 to +4 | 0 to +1 | 0 (CPU) | low / low | high |
| 2 | A-P3 | List+CRC soft binding (radius 8 at radius 6 FPR) | +4 to +5 | +3 to +5 | 0 to +2 | 0 CPU / 8 pilot | high w/o CRC, low w/CRC | med |
| 3 | C-2 | Soft LDPC/polar BP, keyed interleave | +3±1 | +6±2 | +2±1 | 3 (CLIP only) | low / low | med |
| 4 | C-1 | BCH syndrome secure sketch (n=63, helper in carrier) | +2±1 | +3 to +5 | +1±1 | 3 (CLIP only) | low / low | med |
| 5 | D2 | CSF/Watson frequency-weighted ball | 0 to +4 | +2 to +5 | +1 to +3 | 7 | low-med / low | low-med |
| 6 | D3 | Luma/chroma split (gamma 2-3) | +2 to +3 | +3 to +5 | +1 to +2 | 7 | low / low | low-med |
| 7 | A-P1 | Concatenated code replacing repetition (rate 0.1) | +2 to +4 | +6 to +9 | +8 to +12 | 15 | med / low | med |
| 8 | C-3 | Two-codebook / PRF binning (coarse + fine) | +2 to +4 | +3 to +4 | 0 to +1 | 5 | low / low | low |
| 9 | D1 | Equal-LPIPS masked PGD (corrected H3) | 0±2 | 0±2 | 0±1 | 10 | low / low | med (null) |

GPU min = cheapest decisive measurement. 0 = CPU post-hoc on existing stress images. Δ = rescue over soft-7-view baseline.

---

## Per-proposal notes

**A-P2 UEP (rank 1).** Exploits measured 7x spread in per-bit |p_j| error (p_e 0.05-0.35 at t~0.45). Reweighting 20% chips from 8 strongest to 8 weakest cuts worst-bit p_e 0.35->0.18, shaving ~0.12 rad soft distance — exactly the 6.2-7.2 margin at .4 where F5 fails. H4 thr-7 already proved 4/6 rescue at .4 via 1-bit slack; UEP achieves same at thr-6 FPR without raising collisions. Zero-GPU kill test (LLR rescaling on stored p_j) so infinite gain-per-minute. No overlap — orthogonal to coding; stacks with any code. Risk minimal (total power unchanged).

**A-P3 List+CRC (rank 2).** Same binding bottleneck as P2/C-1/C-2 but via list decoding: hard radius 6->8 halves BSC error at p=0.28 (0.55->0.27) yet naive H4 thr-8 cost 4->21/132 false pairs (5x). 8-bit CRC pays L*2^-8=0.031 false-accept to recover thr-8 coverage at thr-6 FPR. CPU-testable on existing images (Chase over 3-4 least-reliable |p| flips). Rank 2 not 1 because FPR restoration depends on CRC bits surviving carrier (needs pilot). DUPLICATION FLAG: Functionally identical to C-1/C-2 — all three are list/syndrome decoders of q. Difference is only code family (repetition+CRC vs BCH vs LDPC). Test only the strongest of the trio after CPU sims; do not run two pilots that prove same point.

**C-2 Soft LDPC/polar (rank 3).** Best expected Δ@.5 (+6±2, 37->44-46) because BP treats small-|p| bits as erasures, correcting ~10-12 soft errors on n=63 vs 6 hard — dominates A-P3 hard list. Gain-per-minute 2.3 (3 min CLIP for LLRs) is highest among GPU-requiring proposals. Assumption: |p'| correlates with error post-regeneration. Overlaps A-P3 and C-1 completely on binding theory (secure sketch, syndrome/helper-in-carrier, keyed permutation). Only distinction is soft vs hard and no hard-radius bookkeeping. If this wins CPU sim, kill C-1 and A-P3 pilots as duplicates.

**C-1 BCH syndrome (rank 4).** Canonical Dodis et al. sketch: Hq helper (33b for 63,30 t=6) in carrier, hard BCH corrects 6. CPU-only rescue +3-5@.5, but at n=31 t=3 it rescues ~0 (median 9 errors on 32 bits), so must lengthen to 63 — extra carrier cost and helper-survival risk (helper BER must stay <20% at .5). Strictly dominated by C-2 on soft gain (~2x). Keep only as fallback if parity-BER kills LDPC helper survival or BP false-decode >=3/132. Duplicates A-P3/C-2 — do not pilot both BCH and LDPC; pick winner of CPU sim.

**D2 CSF/Watson (rank 5).** Only perceptual proposal with plausible encoder-alignment argument (J_E peaks mid-high where CSF dips). Predicted +2-5@.5 at equal LPIPS, 25-35% LPIPS cut at equal T3 — would be valuable if true. Ranked mid because evidence is indirect (probe gain 15.9->26.5 non-linear, no direct sigma_max(J_E W^-1) measurement) and heavier (DCT weighting, risk of block artefacts on 147498 sky, max LPIPS > .050 kill). Gain-per-minute 0.7. Stacks with coding but must not be tested before binding winners are locked — otherwise confounds Δ attribution.

**D3 Chroma split (rank 6).** Similar to D2 but smaller theory risk: gamma 2.5 gives ~1.6-2.1x latent gain if encoder chroma-sensitive. F4 chroma family already explored; quality-matched pick failed, post-hoc r5 passed only with 2.3x LPIPS — caution. Predicted +3-5@.5 at equal LPIPS depends on unproven per-channel J_E equality. GPU 7 min, gain-per-minute 0.57. Low T4/T5 risk. Stacks with D2. Test after D2; kill if latent gain <1.15x at LPIPS-matched point or 147498 shows colour blotches.

**A-P1 Concatenated code (rank 7).** Largest raw Δ at .6 (+8-12, 10->18-22) and +6-9@.5 — the only proposal attacking the carrier-limited .6 regime (depth .6 fails ~38/47 carrier). Ranked low on per-minute (0.47) because 15-min pilot with code-aware PGD is prerequisite; capacity headroom is real (320 chips: ~210b@.4, ~100b@.5, only 32b payload) but H1 already showed optimal a/v weighting buys only 1.1 dB — coding must supply the other 2-3 dB and survive hetero variance (0.12-0.35). If thesis only requires T3/T4/T5 (not .6), defer; if .6 matters, promote to rank 3 after binding layer is fixed.

**C-3 Binning / two-codebook (rank 8).** Bin-confirmation lets d0 relax 6->8 only when coarse b agrees (Pr true d1<=3 ~0.9, false ~0.02), rescuing ~3-4@.5. Standalone gain subsumed by C-2/A-P3; best use is as stacking FPR-reducer on top of a list decoder, not standalone. Needs PCA on E (fragile if p_coarse not << p_fine). Gain-per-minute 0.8 but confidence low. Duplicates C-2 gating logic — if C-2 distance spectrum already holds FPR, C-3 adds nothing. Kill if combined rescue <=2/14 over C-2 alone.

**D1 Equal-LPIPS mask (rank 9).** Null expectation: H3 at equal PSNR lost 11@.4; equal-LPIPS merely recovers to 0±2 by construction (B' grow 1.15-1.32x). Within noise of 12-source pilot, expected Δ~0. Yet costs 10 min sweep and couples fragile-tier budget. Value is methodological — proves H3 comparison was wrong — but not a T3 breakthrough. Ranked last; do only if D2/D3 need a calibrated baseline. Kill if LPIPS-matched PSNR must drop >3 dB or 147498 texture exceeds clip bounds.

---

## Top-3 recommendation — order to test

1. **A-P2 UEP (CPU now, 0 GPU).** Rescale LLRs on existing stress p_j dumps, measure rescue vs FPR (132 ordered clean pairs, T5 66). If >=+2@.4 at thr-6 FPR, promote to 4-source pilot with UEP-weighted PGD loss (10 min). Highest confidence, zero risk, stacks with everything.

2. **Joint CPU shootout: A-P3 vs C-1 vs C-2 (3 min GPU for fresh LLRs + <1 min CPU decode).** Run Chase-2 BCH, BCH-63 hard, LDPC/polar BP on same LLRs. Pick single winner by Δ@.5 at fixed FPR (>=+3@.5, false-decode <=2/132). One pilot only for the winner (8 min for A-P3/C-1 helper-embed, or 3 min validation for C-2 parity survival). This resolves the duplicated list/syndrome family in one pass — do not pilot two.

3. **A-P1 concatenated code (15 min pilot) IFF binding layer leaves .6 gap or thesis needs .6.** Requires winner of (2) to be fixed so inner code and helper budget are known. CPU sim first (10k synth codewords with H1 a_i/sigma_i) to confirm >=2 dB at BLER 5%; if fails, never embed.

Defer D2/D3 until after (1)-(2) lock: perceptual gains are orthogonal but confound binding measurement if run concurrently. D1 only as D2 equal-LPIPS calibrator.

---

## Kill-now

- **Do not pilot more than one of {A-P3, C-1, C-2}** — they are the same list/syndrome idea with different code instantiations. CPU sim picks one; the other two are killed as duplicates even if CPU sim is marginally positive. Similarly, **C-3 is killed standalone** — keep only if it stacks >=+2@.5 on top of the shootout winner; otherwise its bin logic is redundant with the winner distance property.

- **D1: kill as breakthrough proposal.** Approve only as 4-image calibration for D2 if D2 proceeds; do not run full 12-source stress on D1 alone — expected gain within noise (0±2), so full stress wastes 37 min for no decision.

- **Any proposal whose CPU (or 3-min CLIP) rescue <+2@.5 and <+3@.4 is killed before re-embedding.** Thresholds: A-P2 <+2@.4, A-P3/C-1 <+3@.4 or <+2@.5, C-2 <+2/14@.5, C-3 bin rescue <=1/14@.5, D2/D3 latent gain <1.15x at LPIPS match.

- **Any proposal raising T4 both_match >=1/20 or T5 joint >=1/66 (or distinct-label pairs >4/132 at thr-6-equivalent) is killed irrespective of T3 gain.** A-P3 naive without CRC is pre-killed on this rule (H4 21/132).
