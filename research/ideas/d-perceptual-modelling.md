# Idea d — Perceptual modelling for F5

Scope: F5 r2 (PSNR 52 dB, 150-step PGD through SD1.5 VAE encoder, L2 ball + box, band 4-32, clean LPIPS mean .0173 max .050 on 147498 sky, fine grid-like texture). Codec has `_activity_mask` / `mask_power` (local luminance SD, 5 px, mean-normalised, clipped [0.25,4]). Threats T3/T4/T5 only. Quality must stay <= F5 r2 unless user accepts new visuals. H3 pilot (mask 0.5, equal PSNR 52) gave LPIPS mean .0172 -> .0131 (-24%, max .050 -> .043) but T3 .4 49 -> 38 (-22%), .5 37 -> 23, killed per "no >=15% LPIPS drop at equal T3" rule.

## Why H3 was the wrong comparison

At equal PSNR, masking reallocates L2 from smooth (visible) to textured (masked) pixels. F5's encoder gain is spatially quasi-uniform (convolutional VAE, 8x downsample, RF ~30 px / 4 latent) so latent SNR scales with L2 norm, not LPIPS. H3 therefore bought invisibility by spending less L2 where the encoder still reads it equally — latent SNR fell, T3 fell. The fair question is **equal perceptual quality** (LPIPS mean <= .0173, max <= .050) or **equal T3**: how much extra L2 can masking spend before LPIPS returns to baseline, and what T3 does that buy. That test was not run. H3's -11 at .4 does not imply masking cannot help; it implies equal-PSNR is the wrong axis.

All three proposals below are framed as equal-LPIPS (or equal-T3) tests. Each reuses the existing PGD with `mask * eta` and L2 ball on `delta = mask * eta`.

---

## Proposal D1 — Equal-LPIPS masked PGD (corrected H3)

**Model.** Keep H3's public texture mask `m = ((sd/sd.mean())**p / mean) clipped [0.25,4]` with `p = 0.5` (and optionally 0.8). `sd` = local luminance SD (5 px uniform_filter). PGD budget is `B = 255 * sqrt(N) * 10^{-PSNR/20}` on `||delta||_2`. Instead of fixing PSNR, fix LPIPS: raise PSNR budget (lower PSNR dB) with mask until clean LPIPS mean matches F5 r2 (.0173) and max <= .050 on 147498.

Derivation: H3 at 52 dB gave mean LPIPS ratio 0.76. For small changes LPIPS approx `k * ||delta||_2` locally (first-order) in textured regions and `k_smooth * ||delta||_2` in smooth; masking shifts weight by `E[m^2]=1` so at fixed B, LPIPS scales approx `E[w(x) m(x)]` where `w(x)` is local LPIPS sensitivity. Observed 0.76 at fixed B implies at fixed LPIPS, B can grow by ~1/0.76 ~ 1.32 in LPIPS units, but L2-limited: need `B' = B / 0.76^{1/2..1}` ~ 1.15-1.32x. In dB, `Delta PSNR = -20 log10(B'/B)` ~ -1.2 to -2.4 dB, i.e. PSNR 49.6-50.8 dB with mask matches F5 r2 LPIPS at 52 dB.

Encoder gain is not perfectly uniform: textured patches have higher latent variance and slightly higher `||J_E(x) * delta||` due to encoder's high-frequency boost (probe: latent signal 15.9 at 52 dB vs 26.5 at 46 dB, not strictly linear). Expect partial compensation: equal-LPIPS masked may recover H3's T3 loss and add modest gain if textured regions coincide with higher `||J_E||`.

**Quantitative prediction.** At equal LPIPS (masked PSNR ~50.5 dB vs unmasked 52 dB):

- LPIPS mean .0173 +/- .001, max on 147498 <= .050 (by construction).
- T3 .4: masked 49 +/- 3 vs unmasked 49 (paired, H3 baseline). Null expectation 0 delta; optimistic +3-5 if texture correlates with encoder Jacobian; pessimistic -2 (within noise of 58 identities).
- T3 .2/.5 similarly flat. Claim is LPIPS-neutral T3 preservation, not T3 breakthrough.

**Cheapest decisive test (<=15 min GPU, or CPU for LPIPS sweep).**

1. 4 sources x 1 seed = 4 images per PSNR setting, sweep PSNR 52, 51, 50.5, 50 with `mask_power` 0.5 (16 images x 37s ~ 10 min on 5070 Ti). Compute clean LPIPS (Alex) vs source.
2. Interpolate PSNR that matches LPIPS mean .0173 (linear in `10^{-PSNR/20}`).
3. Full 12-source gate at that matched PSNR with mask 0.5 vs baseline 52 mask 0 (paired T3 stress at .4 only, 12 sources x 3 seeds = 36 identities, ~22 min — split: gate first, T3 on subset if gate passes).

**Kill criterion.** If at LPIPS-matched budget, paired T3 .4 is >=5 below unmasked 52 dB (i.e. masked <=44/58 when unmasked 49/58) **or** worst-case LPIPS on 147498 exceeds .055 despite mean match, kill. Also kill if required PSNR drop exceeds 3 dB to match LPIPS (implies masking too aggressive; would violate fragile tier PSNR 47 budget coupling and visual texture amplification).

**T4/T5 risk.** Low. Mask is public deterministic function of source luminance, applied at donor and not at recipient. T4 residual is `delta Donor`; masking makes it more structured (stronger where donor textured) but still donor-pixel-specific, so copy to recipient remains ineffective (F5 already 0/20 at .5, 1/20 at 1 via encoder specificity). No new cross-image correlation: mask does not introduce key-dependent spatial structure. T5 joint collisions unchanged (mask not keyed). Risk: sky recipient (smooth) receives textured donor residual — even less effective, so T4 may drop further, which is acceptable (still 0/20 combined).

**Worst case 147498.** Smooth sky: `sd` low -> `m ~ 0.25-0.4`, so masked PGD suppresses change there by 2.5-4x vs mean. This is the intended win: max LPIPS .050 -> .043 in H3 shows headroom. At equal LPIPS, extra budget goes to any textured subregion (clouds/horizon); pure sky images have little texture, so `B'` growth is capped by `m` clip at 4 — predicted LPIPS reduction on 147498 is largest, texture amplification minimal.

---

## Proposal D2 — CSF / Watson frequency-weighted L2 (encoder-gain-aware perceptual ball)

**Model.** Replace isotropic L2 ball `||delta||_2 <= B` with Watson / CSF-weighted ball `||W * delta||_2 <= B_w` where `W` is a public, key-independent frequency weighting. Two instantiations, both compatible with `mask * eta` parametrisation:

- (D2a) DCT Watson: 8x8 DCT per channel, weight `w(u,v) = CSF(f) * masking_adjustment`, `f = hypot(u,v)/16` cycles/deg approx, using Watson luminance CSF (Mannos-Sakrison or Ahumada-Peterson) scaled to viewing distance 512 px / 10 deg. F5's pixel change is grid-like (high spatial frequency from latent band 4-32, i.e. 2-16 cycles/image in latent -> 16-128 cycles/image in pixels, i.e. mid-high). CSF peaks at 4-8 cycles/deg, falls at high frequencies — so D2a discounts high-frequency error, allowing larger pixel delta at F5's actual frequencies for same perceptual cost.
- (D2b) LPIPS-weighted ball (practical proxy): Approximate `W` by diagonal of LPIPS (AlexNet) Jacobian or, cheaper, a fixed Laplacian pyramid weighting that correlates with LPIPS (e.g. weights [0.5, 1.0, 1.5] for scales). Implement as `delta_w = conv(delta, w_kernel)` and ball on `||delta_w||`.

Encoder alignment: SD VAE encoder Jacobian `J_E` has gain peaking in mid-high frequencies (probe: encoder route 20-27x natural; natural decoder rendering is low-pass, encoder is not). If `W` discounts exactly where `J_E` amplifies, product `||J_E W^{-1}||` is maximised — more latent signal per perceptual unit.

Derivation: Let latent signal `s = ||J_E delta||`. With weighting, `delta = W^{-1} u`, `||u|| <= B_w`, so `s = ||J_E W^{-1} u||`. Maximising over `u` gives `s_max = sigma_max(J_E W^{-1}) * B_w`. Isotropic gives `sigma_max(J_E) B`. Gain from weighting = `sigma_max(J_E W^{-1}) / sigma_max(J_E) * (B_w / B)` at equal perceptual cost. If `W` attenuates high frequencies by 2x and `J_E` amplifies them by 1.5x, net ~1.3-1.5x.

**Quantitative prediction (equal LPIPS).**

- LPIPS reduction at equal T3 (i.e. equal `s`): 25-35% (Watson literature reports ~30% JND reduction for similar masking; F5's grid texture is exactly Watson's target).
- Or T3 gain at equal LPIPS: +4 to +7 on .4 (49 -> 53-56/58) if CSF dip aligns with encoder peak. Conservative: +2-3. At .2, +2-4 (already near ceiling 37/58 at .5).
- Pixel PSNR will drop 1-2 dB (e.g. 52 -> 50.5 dB) but LPIPS holds.

**Cheapest decisive test (CPU + <=15 min GPU).**

- CPU: Compute `W` weights analytically (no GPU). Verify `W` is public and key-independent.
- GPU: 4-source, 2-seed pilot: run PGD with weighted ball: replace `delta.norm()` check with `||W delta||` (implement `W` as 8x8 DCT weighting via dct2 per block, ~5% overhead). Sweep `B_w` to match clean LPIPS mean .0173 (binary search 3 points, 4 images each, ~12*37s ~7 min). Compare latent signal `||J_E delta||` (from probe) and T3 .4 on 12 identities (4 sources x 3 seeds).

Baseline is D1's equal-LPIPS point; D2 wins if LPIPS-matched T3 > D1 by >=3 or LPIPS at equal T3 is >=20% lower.

**Kill criterion.** If at LPIPS-matched `B_w`, (a) T3 .4 is not >= unmasked baseline -2 (i.e. no gain and no loss) **and** worst-case 147498 shows CSF ringing or block artefacts (DCT quantisation texture visible at x1, LPIPS max > .050 or user visual fails), kill. Also kill if `sigma_max(J_E W^{-1})/sigma_max(J_E) < 1.05` measured via probe (weighting does not align with encoder gain).

**T4/T5 risk.** Medium-low. `W` is image-independent (CSF) or image-dependent via LPIPS weights but non-keyed. No new keyed structure, so T5 unchanged. T4: weighted `delta` is more high-frequency, so donor residual is even less transferable to smooth recipient (T4 stays 0/20). Risk: if `W` is image-adaptive (D2b Laplacian), donor-adaptive high-frequency boost may create donor-specific texture that, when copied, is more visible on recipient — but still not keyed, so combined `both_match` remains 0.

**Worst case 147498.** Sky is low-frequency, low-contrast -> CSF sensitivity high (peak 4 cpd), so `W` penalises change there heavily — good, suppresses sky artefacts. High-frequency grid in sky will be discounted only if sky has no texture to mask; Watson luminance masking term `max(1, |c|/T)^{0.2}` will be ~1 in sky, so weighting remains CSF-only, still beneficial. Check 147498 crop at x1 for block boundaries if DCT weighting used — prefer smooth CSF over block DCT if artefacts appear.

---

## Proposal D3 — Luminance/chroma split with chroma-carrier boost (colour masking)

**Model.** Split RGB `delta` into YUV (or Lab): `Y = 0.299R+0.587G+0.114B`, `U,V` chroma. Human CSF for chroma is 3-5x lower than luma at mid-high frequencies (chroma subsampling principle; F4 chroma family exploited this but quality-matched pick failed). Apply separate balls: `||delta_Y|| <= B_Y`, `||delta_UV|| <= B_C` with `B_C = gamma * B_Y`, `gamma = 2-4`. PGD jointly optimises `delta_Y, delta_UV` via `mask * eta` per channel, but with channel-weighted norm: `||delta||_W^2 = ||delta_Y||^2 + (||delta_UV||/gamma)^2`. Equivalent to allowing larger chroma L2 at same perceptual cost.

Why F5-specific: F5's change is "fine, grid-like texture with small coloured clusters" — chroma carries part of the signal. Encoder gain is per-channel (4 latent channels mix RGB via learned encoder, but probe shows encoder gain is similar across RGB). Boosting chroma 3x raises latent signal by `sqrt((1+gamma^2)/2)` ~ 2.0x at same luma LPIPS, because LPIPS (and Watson) is dominated by luminance.

Derivation: Let `delta = delta_Y + delta_C` (orthogonal in YUV). `s = ||J_E delta|| ~ sqrt(s_Y^2 + s_C^2)` (encoder mixes but roughly). With isotropic budget `B`, optimal splits equally. With chroma-boost `gamma`, `s_C` can be `gamma`x larger at same perceptual budget -> `s_total` gain `sqrt(1+gamma^2)/sqrt(2)` ~ 1.58 for `gamma=2`, 2.12 for `gamma=3`. Friction: encoder `J_E` may be less sensitive to chroma (learned RGB->latent weights); measure via probe per-channel.

**Quantitative prediction (equal LPIPS).**

- At equal LPIPS (matched via `B_Y`), allow `gamma=2.5`: LPIPS mean holds .0173 while RGB PSNR drops ~1.5 dB (chroma PSNR 6 dB lower). Pixel change becomes visibly more colourful but less luminance-noisy — LPIPS (luma-weighted) improves 15-20% at equal `s`, or T3 at equal LPIPS gains +3-5 at .4 (49 -> 52-54/58). Chroma boost also helps 147498 sky: blue sky tolerates larger chroma delta (sky chroma variance low, but JND high).
- At equal T3, predicted LPIPS reduction 15-25% (less than D2 because only chroma dimension).

**Cheapest decisive test (<=15 min GPU).**

- 4-source pilot, `gamma=2` and `3`, PSNR 52 baseline: run PGD with YUV-weighted norm (convert `delta` to YUV per pixel, compute weighted norm, scale `delta` to ball; ~2% overhead). Measure clean LPIPS and latent signal. Binary search `B_Y` to match LPIPS .0173 (3 points, 4 images each).
- If latent signal at matched LPIPS >=1.3x baseline, proceed to 12-source T3 .4 spot check (12 identities). Else kill.
- Visual check: 147498 crop at x1 — acceptable if colour speckle not objectionable (F4 showed colour artefacts are less visible than luma grain; user verdict on F5 already accepted coloured clusters).

**Kill criterion.** If at LPIPS-matched `gamma=2.5`, (a) latent signal gain <1.15x (encoder not chroma-sensitive), or (b) 147498 shows visible colour blotches at x1 (chroma JND exceeded, LPIPS max > .055 or visual fail), or (c) T3 .4 <= baseline, kill. Also kill if T4 `both_match` becomes >0/20 (unlikely — chroma residual even less transferable — but if `gamma` creates large chroma that survives copy-paste on similar sky recipients, would be a T4 regression).

**T4/T5 risk.** Low for T5 (chroma not keyed). T4: chroma delta is more image-specific (chroma depends on donor palette), so transfer to recipient with different palette is poor; combined `both_match` expected to stay 0/20 (F5 already 0/20). Risk is T4 marginal `semantic key delivered` might rise from 0/20 to 1-2/20 if recipient shares sky-blue palette (147498-like pairs) — check 20 pairs. If >2/20, reduce `gamma`.

**Worst case 147498.** Sky is near-uniform blue (Y high, UV moderate). Chroma JND is high in uniform regions (chroma masking weak when chroma variance low), but blue channel has higher CSF tolerance. `gamma=2-3` should be invisible at x1; verify with LPIPS and visual crop. If sky shows colour mottling, cap `gamma` at 1.5 for flat images via `sd`-gated `gamma(x)=1+(gamma-1)*tanh(sd/sigma)` — smooth regions get less chroma boost.

---

## Cross-cutting notes

- All three keep detector unchanged (public OwnerID, profile, CLIP, SD VAE encoder, DCT band 4-32 weights). No key-dependent perceptual weighting.
- Interaction: D1 (spatial mask) x D3 (chroma) compose multiplicatively (`mask * W_chroma`); D2 (frequency) subsumes D1's texture preference but via frequency not space. Test order: D1 first (cheapest, already coded), then D3 (one-line YUV norm), then D2 (heaviest).
- Fragile tier coupling: all assume fragile luma tier at 47 dB on top of robust image; LPIPS matching must include fragile change (as gate did). If robust PSNR drops to 50.5 dB, total PSNR remains ~44.7 dB (gate mean) — fragile adds ~0.3 dB.
- Decision rule for any proposal to replace F5 r2: paired T3 at .4 (and .2) not worse than F5 r2 at equal LPIPS (mean <=.0173, max <=.050 on 147498) and T4/T5 not worse than v5 (T4 both_match 0/20, T5 joint 0/66). User visual acceptance required if change visible at x1 on 147498.
