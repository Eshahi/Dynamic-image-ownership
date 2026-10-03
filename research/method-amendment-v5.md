# Method amendment v5: two-tier dual-key DCT watermark (image-domain reference)

Status: **engineering candidate, revision 2, 2026-10-02** (revision 1 of the same day is described where it differs; see "Revision 2"). Authority: [method-amendment-decision-20261002.md](method-amendment-decision-20261002.md). It follows the outcome of the retained revision-2 study (`c4-v4r2-three-threat-dev-001`), the Perplexity brief the user supplied and its verification in [redesign-inputs/literature-verification-20261002.md](redesign-inputs/literature-verification-20261002.md). It applies [scope-guard.md](scope-guard.md), [research-contract.md](research-contract.md), [io-spec.md](io-spec.md), [threat-model.md](threat-model.md) and [proposal-aligned-plan-20260930.md](proposal-aligned-plan-20260930.md). It does not rewrite the proposal, the claim ledger, the A5 [method-spec.md](method-spec.md) or the v2, v3 and v4 candidates, and it advances no gate. Nobody but the author has reviewed it.

Reference implementation: [`scripts/revised_watermark_v5.py`](../scripts/revised_watermark_v5.py) (standard library; imports the unchanged primitives of `revised_watermark_v4.py` revision 2). Tests: [`scripts/test_revised_watermark_v5.py`](../scripts/test_revised_watermark_v5.py). Profiles: [`configs/revised-watermark-v5.example.json`](../configs/revised-watermark-v5.example.json) (public-derived), [`configs/revised-watermark-v5-keyed.example.json`](../configs/revised-watermark-v5-keyed.example.json), schema [`configs/revised-watermark-v5.schema.json`](../configs/revised-watermark-v5.schema.json). Optional embedder stage: [`scripts/v5_channel_refine.py`](../scripts/v5_channel_refine.py). Development tooling: [`scripts/dev_v5_channel_probe.py`](../scripts/dev_v5_channel_probe.py), [`scripts/dev_v5_regeneration_check.py`](../scripts/dev_v5_regeneration_check.py), the numpy lab used to design revision 2 ([`scripts/dev_v5_lab.py`](../scripts/dev_v5_lab.py), checked against the codec, with [`dev_v5_lab_run.py`](../scripts/dev_v5_lab_run.py), [`dev_v5_lab_channel.py`](../scripts/dev_v5_lab_channel.py), [`dev_v5_lab_spatial.py`](../scripts/dev_v5_lab_spatial.py), [`dev_v5_lab_view.py`](../scripts/dev_v5_lab_view.py)) and the held-out hosts ([`dev_v5_holdout_hosts.py`](../scripts/dev_v5_holdout_hosts.py)).

## Why v4 revision 2 was not kept as it is

Revision 2 was run on twelve photographs (results in the worktree `claude/v4r2-three-threat-study`, `experiments/c4-v4r2-three-threat-small-v1/results-dev-001.md`). Clean detection and content binding behaved as designed. Regeneration did not: of 121 regenerated marked images none kept a key, and the deterministic VAE round trip alone, with no diffusion step, already brought the scores of marked images down to those of unmarked ones. `semantic_only`, the outcome that the proposal reads as "regenerated", never occurred.

The cause is where the mark sat. Both v4 channels modify 8x8 block-DCT coefficients of the full-resolution image with index 1 to 3, that is, patterns with periods of 16 pixels and less. An autoencoder with a downsampling factor of 8 keeps one latent sample per 8 pixels, so 16 pixels is its sampling limit, and what it reconstructs below that is synthesised texture. The sources checked for this amendment say the same in their own terms: image editing and regeneration remove mid and high frequencies and leave low ones largely alone (VINE), and the published marks that survive regeneration place a large change at low frequencies or directly in the autoencoder's latent (ZoDiac, FreqMark, PhaseMark, StegaStamp).

A development probe on synthetic hosts (see "Engineering evidence") reproduces the failure and shows where a mark would have to sit. Mean response of the block-DCT coefficient to a small added pattern, and the change the channel makes to the unmarked host coefficient, for the VAE round trip:

| Coefficients | Response to a mark | Channel noise (RMS) | Host (RMS) |
| --- | --- | --- | --- |
| 8x8 DCT at full resolution, the v4 positions | 0.02 to 0.21 | 12 to 16 | 16 to 49 |
| 8x8 DCT of the image averaged 4x4, index up to 4 | 0.41 to 0.87 | about 4 | 10 to 120 |
| 8x8 DCT of the image averaged 8x8, index up to 5 | 0.66 to 0.95 | 2 to 3 | 9 to 135 |

After SD 1.5 img2img the response at the 4x4-averaged scale is 0.41 to 0.74 at strength 0.05 (diagonal positions of index 1 to 4), 0.26 to 0.48 at 0.1, 0.16 to 0.24 at 0.2 and 0.07 to 0.19 at 0.4, with noise that grows with the host's own energy. A pattern in the image averaged 4x4 is therefore largely kept by the autoencoder and progressively removed by the denoiser.

Other open items of v4 that this amendment touches: the helper data is weaker than the key it serves (v4 deviation 1), and resizing an image destroyed detection because the carrier was tied to the pixel size (v4 threat table, T1).

## Claim boundary

v5 is an **image-domain** codec, proposed as a candidate comparator. It does not implement latent or initial-noise embedding, so RQ-02, HYP-02, OBJ-02 and METHOD-06 stay open; the optional refinement stage uses a frozen autoencoder and denoiser only to choose a pixel change and is not initial-noise injection either. No detector state establishes legal ownership.

Survival of regeneration is a measured property of one attack family, one model and a dose range. It is not guaranteed and cannot be: the sources checked include a proof that marks which leave the image perceptually unchanged are removable by noise-then-reconstruct attacks (Zhao et al.) and benchmarks in which regeneration at higher strength, repeated regeneration and regeneration by other models remove the surviving schemes too (WAVES; Liu et al.).

No number in this document comes from a photograph. Every measurement is on procedural images or on images generated for this purpose with Stable Diffusion 1.5 from fixed prompts and seeds. They are development observations that chose engineering defaults; they are not results of the thesis.

## What changes relative to v4

| Aspect | v4 revision 2 | v5 |
| --- | --- | --- |
| Where `Ws` is embedded | 8x8 DCT at full resolution, six positions of index 1 to 2 | **Robust tier**: 8x8 DCT of the image area-averaged to 128x128, 24 positions of index up to 4 (for a 512x512 image: 32x32-pixel blocks, periods of about 16 to 64 pixels) |
| Where `Wi` is embedded | 8x8 DCT at full resolution, six positions of index up to 3 | **Fragile tier**: unchanged |
| Statistic on the robust tier | none | coefficients whitened by frequency and normalised per block; every slot weighted by the share of the mark the embedder puts there, recomputed from the suspect image (revision 2) |
| Embedding budget | one PSNR target, split 60:40 | robust tier: a texture mask that caps every block's change, a pixel-level shaping that keeps flat strips free, and a PSNR floor as the only global limit (revision 2); fragile tier: a PSNR target |
| Thresholds | Hoeffding's bound | the tight Gaussian bound for weighted random signs (Bentkus and Dzindzalieta), at the same false-positive target (revision 2) |
| Keys | 128 bits each, a pseudorandom function of the whole code | 320 chips each, **32 segments** of 10 chips; segment `j` is a pseudorandom function of bit `j` of the code or codes |
| Tolerance to drifted code bits | Reed-Muller helper data carrying `q` and `H` | the segment-wise key itself; no helper data |
| Carried code | decoded from the helper chips | decoded from the key chips, segment by segment |
| Carrier of `Ws` | depends on the image size in pixels | fixed for the 128x128 grid, so a resized image is still read |
| Perceptual hash | read from parts the embedder never touches | computed after the robust tier, which moves what the hash reads |
| Decision table | six outcomes | the same six outcomes |

The intended reading of the proposal's three states becomes mechanical. An untouched or mildly processed marked image keeps both tiers: *authentic*. A regenerated one loses the fragile tier and keeps the robust one: *regenerated* (`semantic_only`). A mark moved to other content is read with a code that disagrees with the image: *copy-paste* (`content_mismatch`).

## Revision 2

Revision 1 (committed as `f9087a2` on `claude/v5-two-tier-study`) kept the semantic key through the VAE round trip on only 9 of 16 synthetic development hosts at its default budget, and through img2img at strength 0.1 on 4. On the user's instruction of 2026-10-02 to continue until the result is acceptable, revision 2 was designed the same day, before any photograph was marked with either revision. It changes the robust tier only; the fragile tier, the keys, the codes, the decision table and the false-positive target are those of revision 1.

Design method. A numpy model of the robust tier (`scripts/dev_v5_lab.py`, checked against the codec to 1e-9 for revision 1 and to 1e-7 for revision 2) marked the sixteen development hosts with each variant; the outputs went through the VAE round trip and img2img (seed 0, strengths 0.05, 0.1, 0.2) and were read with the variant's own detector. The robust tier alone was marked (no fragile tier), so these PSNR values are about 0.3 dB above the full codec's. Twenty further synthetic hosts were generated as a held-out set and used only once, for the final check of the chosen configuration.

What changed, and what each change was worth in the lab (hosts whose semantic key was found after the VAE round trip, median score after it, and hosts found at 0.1 and 0.2; threshold 4.98):

| Step | VAE | Median after VAE | 0.1 | 0.2 | RGB PSNR of the robust tier, dB |
| --- | --- | --- | --- | --- | --- |
| Revision 1 (equal slot weights, whitening 1, visibility RMS 1, block cap 1.5, floor 36 dB) | 9/16 | 6.4 | 5/16 | 2/16 | 36.8 to 48.6 |
| Slot weights from the embedder's allocation, exponent 0.5 | 12/16 | 8.2 | 6/16 | 4/16 | 37.2 to 50.4 |
| and whitening 2 | 14/16 | 10.3 | 9/16 | 6/16 | 37.3 to 52.7 |
| and per-block caps of 2 with a 35.5 dB floor in place of the visibility RMS | 16/16 | 13.9 | 14/16 | 9/16 | 35.5 to 41.0 |
| and pixel shaping (window 3, 75th percentile), fill measured after shaping (revision 2) | 16/16 | 13.9 | 14/16 | 9/16 | 35.5 to 41.0 |

1. **Informed slot weights** (deviation 25). The equal-weight correlation of revision 1 collected the channel noise of every slot, including the many where the embedder had put almost nothing. Each slot now counts with the weight `(mask * w * g / n)^(2 gamma)`, `gamma = 0.5`, the square root of the share the visibility plan gives it. The weight is recomputed from the suspect image and never depends on the key, so for an unmarked image the statistic is still a weighted sum of independent random signs. Exponents 0.25, 0.75, 1 and 2 were worse.
2. **Whitening exponent 2** instead of 1. 1.5 gave a median of 9.7, 2 gave 10.3, 2.5 gave 10.2 with one host fewer; 0.5 and 0 were clearly worse (6.3 and 5.5).
3. **A block-wise visibility budget** (deviation 27). Revision 1 bounded the RMS over blocks of each block's change relative to its mask, an aggregate with no perceptual model behind it, and left most hosts far above any PSNR floor (up to 48 dB). Revision 2 treats the mask as a just-noticeable level: every block may change by up to `block_ratio_cap` (2) times its mask, RMS over the block, and the PSNR floor (35.5 dB for the robust tier, which leaves the full codec at 35.2 dB or more) is the only global limit. The plan still fixes the shape of the change and its host rejection; the fill then scales every block as far as its cap and the floor allow. With whitening 2, a cap of 1.5 kept all 16 hosts through the VAE but only 11 at 0.1 and 7 at 0.2, and limited the largest block change to 7.5 grey levels RMS against 10; with whitening 1, caps of 1.25 and 1.5 kept 15 through the VAE and 8 and 10 at 0.1.
4. **Pixel shaping** (deviation 28). The inspection of the lab outputs at three times magnification showed a defect that revision 1 already had in fainter form: a flat strip narrower than one 8x8 cell inside a busy block (the edge of a flat rectangle on a procedural host) takes the block's full change and shows as blotches. The block mask cannot see it, because every 8x8 cell of the block holds texture. Each pixel now gets a just-noticeable level from the flattest 3x3 window that contains it, and takes `min(1, level / reference)` of the planned change, the reference being the 75th percentile of the levels in its coarse block. The fill is measured on the shaped change. This removes the blotches at no cost in score.
5. **Tight tail bound** (deviation 26). Bentkus and Dzindzalieta (Bernoulli 21(2), 2015) proved that a weighted sum of independent random signs with `sum a_i^2 <= 1` exceeds `t` with probability at most `c * P(Z >= t)`, `c = 1 / (4 P(Z >= sqrt 2)) = 3.1787`, and that this constant is optimal. It holds for the same statistic as Hoeffding's `exp(-t^2/2)` and gives 4.98 instead of 5.26 for one pattern and 8.26 instead of 8.48 for 2^32 patterns at `alpha = 1e-6`.
6. **The mask fields move into `robust`**, because the detector now uses the mask; they enter `detector_config_id`.

Tried and rejected in this round (same lab, same hosts):

- *A fitted table of per-position retention* in the detector weights: the VAE keeps low frequencies better (retention 0.77 to 0.87 at index 1, 0.29 at (4,4)), but the table raised the median by about 1% and would have added 24 fitted constants.
- *A finer flatness measure in the block mask* (4x4 cells): it lowered the mask of busy blocks and lost a host at the VAE stage, and shaping by 4x4 cells left the blotches, because the cells that straddle the strip's edge hold texture. A 25th-percentile reference left them too, because the strip filled a quarter of its block and the reference fell inside it.
- *No host rejection* (VAE median 11.9 against 13.9) and *a second pass that chooses the rejection for the scale the fill reaches* (12.9; 12 of 16 at 0.1 against 14): the strong rejection that results from scaling the plan helps after the channel.
- *A high-pass filter across blocks in the detector*: the channel noise of neighbouring blocks is correlated by less than 0.2 at most positions and by 0.37 at most (`dev_v5_lab_spatial.py`), so it would remove a few percent of the noise.

## Method

Phases 1 and 3 follow the proposal's phases; phase 2 is the image-domain substitute, as in v4. Symbols follow [notation.csv](notation.csv) with the exceptions stated in the v4 amendment.

### Shared definitions

`pack` and `stream` are those of [method-amendment-v4.md](method-amendment-v4.md), unchanged, including the ASCII bytes `rw-v4` inside the HMAC input: v5 calls the same function, and its streams differ from v4's through `config`. `config` is the 32-byte `detector_config_id`: SHA-256 of the ASCII bytes `rw-v5/config/r2/` (`r1/` in revision 1) followed by the canonical JSON of the profile fields `schema_version`, `profile`, `security`, `semantic_source`, `minimum_side`, `robust_frequencies`, `instance_frequencies`, `robust`, `code_bits`, `segment_chips`, `canonical_side`. The constants are `schema_version = "revised-watermark-v5"`, `profile = "two-tier-dual-key-dct"`, `code_bits = 32`, `segment_chips = 10`, `canonical_side = 128`. The six numbers of `robust` (`floor`, `whitening`, `weight_exponent`, `mask_base`, `mask_weber`, `mask_cap`; revision 1 had the first two) are written as JSON floats. Embedding parameters and decision thresholds are not part of the identifier. `decision_id` is SHA-256 of `rw-v5/decision/` followed by the canonical JSON of `decision`.

The key `K` is `SHA-256("rw-v5/public-derived-profile-key")` when `security` is `public-derived` and the caller's 16 to 4096 byte secret when it is `hmac-keyed`.

The input is a luminance matrix in [0, 255] with both sides at least `minimum_side` (256 or more). Luminance of an RGB pixel, area resampling, the block DCT `C[b, u, v]`, the map of block means `M` and sign projections are as in v4.

### Phase 1: codes and keys

- **Semantic code `q`** (METHOD-02): as in v4, the 32-bit sign projection of the semantic vector, or of the 8x8 layout in `proxy-layout-v1`.
- **Perceptual hash `H`** (METHOD-03): the v4 hash. It is computed on the image **after the robust tier has been embedded and before the fragile tier is**. The robust tier changes block means and the (0,1) and (1,0) coefficients, which the hash reads; the fragile tier does not. In the tests the hash of an image and of its robust-marked version differ by a few bits at most.
- **Keys** (METHOD-04, METHOD-05). Each key is 320 chips of +1 or -1 in 32 segments of 10. Segment 0 belongs to the most significant code bit. With `b(x, j)` bit `j` of a code:

  ```text
  Ws segment j = first 10 bits of stream(K, pack("ws", OwnerID, bytes(j, b(q, j))), 2)
  Wi segment j = first 10 bits of stream(K, pack("wi", OwnerID, bytes(j, b(q, j), b(H, j))), 2)
  ```

  read most significant bit first, bit 1 meaning -1. `Ws` binds owner and semantics, `Wi` additionally binds the instance, as in the proposal. Two codes at Hamming distance `d` share `32 - d` segments exactly; their other segments are independent patterns. The correlation of a mark with the key of a nearby code is therefore reduced by about `d / 32` instead of collapsing, which is the tolerance that v4 obtained from helper data.

### Phase 2 (image-domain arm): embedding

**Robust tier.** `G` is the luminance area-resampled to 128x128, cut into 256 blocks of 8x8 (row-major). Its positions are the 24 pairs `(u, v)` with `u, v <= 4` except (0,0), in row-major order of `(u, v)`. For block `b` and position `k`:

```text
w[k]    = (u^2 + v^2) ^ (whitening / 2)                    whitening = 2 (1 in revision 1)
n[b]    = sqrt(floor^2 + mean_k (w[k] * C[b, k])^2)        floor = 12
x[b, k] = w[k] * C[b, k] / n[b]
d[b, k] = (mask[b] * w[k] * g[k] / n[b]) ^ (2 * gamma)     gamma = weight_exponent = 0.5 (0 in revision 1)
```

The weight `w` emphasises the upper part of the band; the normaliser makes busy and quiet blocks count alike, and its floor stops a flat block, where only channel noise is left, from being amplified. `mask[b]` is defined in step 1 below and `g[k]` in step 2. The carrier is the v4 carrier construction with channel byte `r` and the dimensions 128 and 128 in place of the image size, over the 6144 slots (block-major, positions in the order above): each slot gets one of 320 chips and a sign, and chip `c` has the projection `p[c] = sum(d * sign * x) / sqrt(sum d^2)` over its slots. The slot weight `d` is the square root of the share of a chip's move that the visibility plan of step 2 puts into the slot, so the projection is close to a matched filter for the embedder's own allocation. The detector recomputes `d` from the suspect image; it never depends on the key. With `gamma = 0` every weight is 1 and the projection is that of revision 1.

The embedder moves the projections towards the key and spends the change where the image hides it.

1. *Mask.* The texture of a block is the smaller of two measures. Coarse scale: the smallest, over its four 4x4 quadrants of `G`, of the RMS that remains after the quadrant's best-fitting plane is removed; a smooth gradient therefore counts as flat, and a block with one edge next to a flat area keeps the value of the flat part. Fine scale: the second smallest standard deviation among the 8x8 pixel cells of the full-resolution image under the block; a block with a flat patch larger than one cell counts as flat however busy the rest of it is. `mask[b] = min(mask_cap, sqrt(mask_base^2 + (mask_weber * texture[b])^2))` in grey levels, with `mask_base` 0.4, `mask_weber` 0.35 and `mask_cap` 5. The **ratio** of a block is the RMS grey-level change the embedder makes in it divided by its mask. The detector computes the same mask for its slot weights.
2. *Plan.* Two budgets shape the change: a **visibility budget**, RMS over blocks of the ratio at most `visibility` (1.0), and an **error budget**, luminance PSNR of the robust change at least `min_robust_psnr_db` (35.5; 36 in revision 1). Moving `x[b, k]` by one unit changes block `b` by `E = (n[b] / (w[k] * g[k]))^2 / 64` in mean squared grey level, with `g[k]` the factor by which area-averaging shrinks the rendered basis function (0.82 to 0.99 at 512x512); that costs `E / mask[b]^2` of the first budget and `E` of the second. Every chip's move is spread over its slots in proportion to `d / cost`, with `cost` a weighted sum of the two costs, each scaled to its budget: the cheapest way to move the weighted projection at that weighting. With `e` the key chips, the projections are moved by `A * e - lambda * p`: improved spread spectrum, as in v4, where `A` follows from `lambda` and the budget. `lambda` is taken from {0, 0.025, ..., 1} and the weight from {1, 0.9, ..., 0} to maximise `design_gain * A / sqrt((1 - design_gain * lambda)^2 * mean(p^2) + design_noise^2)`; a weight other than 1 (visibility alone) is taken only if it promises at least 1% more. `design_gain` (0.5) says that the channel is expected to return about half of the added pattern. The plan fixes the shape of the change and its host rejection, not its size.
3. *Shaping* (revision 2). The planned change is rendered (step 5) and multiplied pixel by pixel by a factor in (0, 1]. Each pixel gets the level `sqrt(mask_base^2 + (mask_weber * s)^2)`, with `s` the standard deviation of the flattest `shape_window` x `shape_window` window (3) that contains the pixel, and the factor `min(1, level / reference)`, with `reference` the `shape_percentile`-th percentile (75, linear interpolation) of the levels of the pixels of its coarse block. Pixels as busy as most of their block keep the full change; a flat strip at least three pixels wide inside a busy block keeps almost none of it right up to its edge.
4. *Fill* (revision 2; revision 1 scaled the plan to the tighter of the two budgets and clipped single blocks at 1.5 times the visibility). Measured on the shaped change, every block may reach `block_ratio_cap` (2) times its mask, RMS over the block, and the whole change may reach the PSNR floor. One scale factor `s` is applied to all blocks, each block clipped at its own cap, and `s` is the largest value with the PSNR at or above the floor; if every block reaches its cap first, the change stops there. The report says which limit bound (`bound_by`). Blocks the plan used lightly are therefore raised further than blocks it used heavily, which approximates filling the most valuable blocks first; the host rejection of a block scales with it. At the defaults no block changes by more than 10 grey levels RMS and the robust tier alone stays at 35.5 dB or above, the full codec at 35.2 dB or above on the development hosts.
5. *Rendering.* A coefficient change is realised by the continuous extension of its 8-point DCT basis function over the pixels of its coarse block, so the change is smooth inside a block (for 512x512 these are the low 32-point DCT basis functions of a 32x32 block). The block means of `G`, and with them the 64-pixel layout that the proxy code reads, do not move except through the shaping, which is small where it acts.

**Fragile tier.** The v4 instance channel: positions `[(0,3), (3,0), (1,3), (3,1), (2,3), (3,2)]` of the 8x8 block DCT at full resolution, the v4 carrier with channel byte `i` and the image size, improved spread spectrum against a target PSNR of `instance_psnr_db` (47), with the rounding allowance and the passes of v4. Its 320 chips are `Wi`.

**Order.** Robust tier on the source image; `H` from that intermediate image; fragile tier; then rounding as in v4. The embedder runs the real detector on its output and raises `EmbeddingError` with the full report when the outcome is not `both_match` (or returns it with `strict=False`).

**External embedders.** `robust_plan()` exports the slot layout and weights, the key chips, the masks, the shaping factors, the closed-form change after the fill and the budget it spent. `embed_with_report(..., robust_change=...)` accepts a robust change computed elsewhere, renders and shapes it, refuses it when a block exceeds its cap by more than 2% or the PSNR falls below the floor by more than that, and never scales it up. `scripts/v5_channel_refine.py` uses this: starting from the closed-form change it ascends the weighted key correlation measured after the frozen SD 1.5 autoencoder, and after one noising and denoising step at timestep 100, by 30 Adam steps projected onto the same budget. It is optional, needs a GPU and the model, and its surrogate channel is the same model family as the regeneration attack of the study; it was measured with revision 1 only.

### Phase 3: detection

Inputs as in v4: the suspect image, the claimed OwnerID, the profile, the key in the keyed variant, the semantic vector in an external profile. No original image, no enrolment record, no model. The detector computes two block DCTs (of the image and of its 128x128 average), the mask of the 128x128 blocks for the slot weights, and two sets of 320 projections. In the standard-library reference it takes about 0.2 s for a 512x512 image.

For each key the detector makes two tests on its 320 projections `p`. With `e(c)` the key chips of a code `c`:

```text
z(c) = sum(e(c) * p) / sqrt(sum(p^2))
```

- **Recomputed** (the proposal's route): `z_r = z(code recomputed from the suspect image)`. One pattern.
- **Decoded**: `z_d = max over all 2^32 codes of z(c)`, and the code that attains it. Because segments do not overlap, the maximum is found segment by segment: each segment takes the bit whose pattern correlates better; on a tie it keeps the recomputed bit.

A key is **found** if `z_r >= t(R)` or `z_d >= t(2^32 R)`, where `t(N)` is the smallest score with `3.1787 * N * P(Z >= t) <= alpha` and `R` is the roster size: 4.98 and 8.26 for `alpha = 1e-6` and one owner, against a largest possible score of `sqrt(320) = 17.9`. (Revision 1 used `t(N) = sqrt(2 ln(N / alpha))`: 5.26 and 8.48.)

A key that passes the second test has been **read**: its decoded code is compared with the recomputed one. Their Hamming distance `d` contains decoding errors. Under the model that a segment's correct pattern scores `N(mu, 1)` and its other pattern `N(0, 1)` in the segment's noise units, the decoded score has mean `sqrt(32) * m(mu) / sqrt(1 + mu^2 / 10)` with `m(mu) = mu * Phi(mu / sqrt 2) + exp(-mu^2 / 4) / sqrt(pi)`; this is inverted for `mu`, the error rate of a segment is `r = Q(mu / sqrt 2)`, and the **corrected distance** is `(d - 32 r) / (1 - 2 r)`, limited to 0 to 32. For a strong mark it equals `d`. A key found by its recomputed pattern alone is too weak to be read and counts as carrying the recomputed code (distance 0).

The content status of a found key is `match`, `uncertain` or `mismatch` from the corrected distance and the profile's radius and mismatch distance, as in v4. The instance key is tested with the recomputed `q`, unless the semantic key was read and its status is not `match`, in which case the decoded `q` is used; the instance key inherits the worse of its own status and the semantic one. The decision table and the meaning of `outcome` and `proposal_state` are those of v4:

| Semantic key | Instance key | `outcome` | `proposal_state` |
| --- | --- | --- | --- |
| not found | not found | `neither_match` | `not_detected` |
| any found key has status `mismatch` | | `content_mismatch` | `copy_paste` |
| found, `match` | found, `match` | `both_match` | `authentic` |
| found, `match` | not found | `semantic_only` | `regenerated` |
| not found | found, `match` | `instance_only` | `unclassified` |
| any other combination | | `content_uncertain` | `unclassified` |

`binding_mode` selects the comparisons for the ablations as in v4.

## Statistical basis

For fixed projections and a pattern of independent fair signs, `z` is a weighted sum of random signs with squared weights summing to 1. Bentkus and Dzindzalieta proved `P(z >= t) <= c * P(Z >= t)` for every such sum, with the optimal constant `c = 1 / (4 P(Z >= sqrt 2)) = 3.1787` (equality is reached at `t = sqrt 2` by two equal weights); revision 2 uses this bound, revision 1 used Hoeffding's `exp(-t^2 / 2)`, which holds for the same sums and is looser for every `t` above about 0.7. The recomputed test uses one pattern per owner. The decoded score is the largest of `2^32` patterns; the union bound gives `P(z_d >= t) <= 2^32 c P(Z >= t)`, which is where the second threshold comes from. The tests check the bound exhaustively on small weighted sums. Both hold over the pseudorandom patterns for a fixed image, under the same PRF assumption and with the same reservations as in v4: the public profile's patterns are computable by anyone, and an image constructed with the derivation is outside the argument. The slot weights of revision 2 are functions of the suspect image and the profile only, not of the key or the owner, so they are part of the "fixed projections" and the argument is unchanged. For an unmarked image the probability that either key is found is at most `4 alpha` per tested owner.

Three limits are specific to v5.

- The second threshold costs strength: a mark must reach 46% of the largest score to be read, 28% to be found by its recomputed pattern.
- A lower reading threshold also reads weaker marks, whose decoded code carries more decoding errors. With revision 2 the fragile key of some blurred images (Gaussian sigma 1.5) is read at a decoded score of about 8.4 and compared with a perceptual hash that the blur has moved by a few bits; the corrected distance then falls between the radius and the mismatch distance and the outcome is `content_uncertain` (2 of 16 development hosts, 0 and 3 of 20 held-out hosts with the proxy and the CLIP vector). Revision 1 did not read these keys and reported `both_match`.
- A mark that is found but not read is assigned the recomputed code by convention. A mark transferred from content whose code lies 7 to 9 bits away can fall into that case in a narrow range of strengths and is then reported as matching where a read mark would be reported as uncertain. For a code 10 or more bits away the expected recomputed score is at most about 0.61 of the decoded score once the gain from decoding is counted. With the revision-1 thresholds (ratio 0.62) such a mark passed the first threshold while failing the second only through noise; with the revision-2 thresholds (4.98 and 8.26, ratio 0.60) it can do so in expectation, in the range of decoded scores from about 8.2 to 8.26, and is then reported as matching.
- About half the segments of an unrelated code agree by chance, so the recomputed pattern of unrelated content scores about half of the full score and passes the first threshold on a strong mark. That is why a read code decides and the recomputed test alone does not.

The corrected distance rests on a model, checked against simulation in the tests (predicted and observed error counts agree within 0.6 of a bit over the tested strengths). It is an estimate with a spread of two to three bits near the reading threshold; it is rounded to six decimals so that a strong mark keeps its plain distance; the radius and mismatch distance are uncalibrated defaults, as in v4.

## Threat coverage

Only what differs from the v4 table is listed; everything else there still applies, including that the public profile lets anyone embed for any OwnerID and subtract a mark.

| Threat | What v5 changes | What is not claimed, and what is known to fail |
| --- | --- | --- |
| T3 regeneration | The semantic key sits where an f=8 autoencoder keeps it. With revision 2, on the 20 held-out synthetic hosts at admissible quality, it survives the VAE round trip on 20 of 20 hosts with the layout proxy and 18 of 20 with the CLIP vector, and img2img at strength 0.05 on 20 and 17 of 20 hosts on all three seeds, reading `semantic_only`; see "Engineering evidence". | Survival on photographs is unmeasured. Survival falls with strength: about half the hosts at 0.1, two fifths at 0.2, almost none at 0.4 on all seeds; the preregistered rate of 9 in 10 is reached on these hosts only for the VAE round trip and 0.05. Textured images fail first: the autoencoder resynthesises their texture, and a larger budget helps them little (at 33 dB the weakest held-out host still scored 5.1 after the VAE). At 0.4 one genuine regenerated image read `content_mismatch` in the strong arm. Repeated regeneration, other models, prompts and samplers are untested. Ordinary low-pass processing gives the same `semantic_only` outcome, so the outcome does not identify regeneration. |
| T1 benign processing | JPEG at quality 75 and 50 kept both keys on all synthetic hosts. A resized image keeps the semantic key, because the robust carrier is tied to the 128x128 grid and not to the pixel size. | Crop, rotation and shift are still unsupported: the grid is anchored to the image frame. A resized image loses the instance key and reads `semantic_only`. Blur with sigma 1.5 gives `content_uncertain` on a few hosts with revision 2 (see "Statistical basis"). |
| T4 copy-paste | A whole mark moved onto unrelated content is read and reported as `content_mismatch`. | The coarse part of a mark alone carries the semantic key: copied onto another image of the same composition it reads `semantic_only`, the "regenerated" label (pinned by a test). This is v4's known limit in a new place. The narrow unread-mark case above. |
| T5 semantic collision | Unchanged in mechanism: the instance key binds `H`. | Unchanged; additionally `H` now moves by a few bits when the robust tier is embedded. |
| T2 removal | Nothing. | The robust change is low-frequency and public in the default profile; it can be subtracted, and the carrier is the same for all of an owner's images of any size. Segment patterns for both bit values can be collected from a few marked images of one owner. |

## Traceability to the proposal

Rows that differ from the v4 amendment:

| Claim ID | v5 status |
| --- | --- |
| PROB-02 regeneration | Mechanism implemented; development observations on synthetic hosts only. Open on photographs. |
| METHOD-04, METHOD-05 dual keys | Implemented as segment-wise keys of 320 chips (deviation 17). |
| METHOD-06 latent embedding | **Open.** The optional refinement stage passes the image through a frozen autoencoder and denoiser while embedding, but the mark is a pixel change and the route is not initial-noise injection. |
| METHOD-07 recompute candidate keys | Implemented; the second candidate is decoded from the key instead of from helper data. |
| METHOD-08 8x8 mid-band correlation | The semantic key is read from the 8x8 block DCT of a 128x128 average of the image, not from the mid band at full resolution (deviation 18). The instance key is read as in v4. |
| METHOD-09 decision states | As v4. `semantic_only` is now reachable after regeneration. |
| OBJ-03, RQ-03, HYP-03 lightweight extraction | The detector still loads no model and runs no inversion. It computes two block DCTs instead of one, and a block mask. |
| METRIC-01..03 quality | Revision 2 spends the admissibility margin: on the 36 synthetic hosts RGB PSNR is 35.2 to 41.7 dB (median about 36), against about 42 dB for v4 and 36 to 45 dB for revision 1; SSIM is 0.96 or higher and LPIPS 0.07 or lower. |

## Additions and deviations

Numbering continues that of the v4 amendment; its items 2, 3, 5 to 12, 15 and 16 apply unchanged. Each item is a method choice to be validated, not a result. Adoption is the user's decision; items 17, 18, 20 and 27 change how the proposal's method is read and are for the supervisor.

17. **Segment-wise keys** replace keys that are a pseudorandom function of the whole code, and the helper data of v4 (its deviation 1) is dropped. The key is still a keyed function of owner and codes, but it is locality-sensitive: this is what the tolerance needs, and it is also what lets a holder of several marked images of one owner collect both patterns of a segment.
18. **Robust tier.** The semantic key is embedded in and read from the block DCT of a fixed-size average of the image. The proposal names the 8x8 mid band of the image itself.
19. **Normalised statistic.** The robust projections are taken after frequency whitening and per-block normalisation, both fixed functions of the suspect image.
20. **Quality budget.** The robust tier is sized by a texture mask with a PSNR floor (36 dB in revision 1, 35.5 dB in revision 2), in place of a 42 dB target. The mask constants were chosen by the author's inspection of a handful of synthetic images and are uncalibrated.
21. **Two thresholds and a corrected distance** replace the candidate list of v4.
22. **Hash after the robust tier.**
23. **Size-independent robust carrier**, minimum side 256.
24. **Optional refinement stage** through a frozen model, outside the reference codec and off by default.
25. **Informed slot weights** (revision 2). The robust projections weight every slot by a function of the suspect image's mask, normaliser and frequency, the square root of the embedder's allocation.
26. **Tight tail bound** (revision 2). Thresholds follow Bentkus and Dzindzalieta's bound instead of Hoeffding's at the same false-positive target; the decision becomes more sensitive, and the side effects stated under "Statistical basis" follow.
27. **Block-wise visibility and a fill to the PSNR floor** (revision 2). Visibility is a per-block just-noticeable limit and the admissibility level of the study (35 dB) is approached on purpose: the codec spends the quality margin that revision 1 left unused. This is a choice about the operating point, for the supervisor.
28. **Pixel shaping** (revision 2). The robust change is no longer exactly the planned coefficient change: flat neighbourhoods inside busy blocks receive less of it.

## Engineering evidence (synthetic only)

`unittest discover -s scripts` passes 132 tests in the main checkout with the verified Windows interpreter; 37 belong to v5. They include known-answer vectors for the identifiers, the segment keys, the robust carrier, the mask input, the slot weights, the local flatness and shaping factors and one marked image; the thresholds and an exhaustive check of the tail bound on small weighted sums; the statistic on constructed projections, with a simulation check of the decoding-error model and of the null scores; the null distribution of the weighted statistic on a real image with strongly unequal weights; profile validation, including rejection of revision-1 profiles; the texture measure; the shaping of a flat strip narrower than one cell inside a busy block; marked images over two keys and two scenes with their declared limits; both ways the fill can bind; negatives; ordinary processing; the tier split under loss of fine detail and under resizing; the external-embedder contract and its budget check; and transfers, including one pinned known limit. The study package adds 5 harness tests (`scripts/test_v5_study.py` on the study branch).

**Development hosts.** Sixteen 512x512 images: four procedural colour fields and twelve images generated with SD 1.5 from fixed prompts and seeds (`dev_v5_channel_probe.py`). Their VAE round-trip PSNR is 22 to 35 dB; the twelve photographs of the revision-2 study were at about 25 dB. The channel settings are those of that study: VAE mode round trip; img2img with DDIM, 20 steps, eta 0, guidance 1, empty prompt, strengths 0.05 to 0.4, three seeds. The safety checker stays on.

**Held-out hosts.** Twenty further 512x512 images, generated once after the revision-2 configuration was fixed and never used to choose it: the sixteen prompts with seeds 2000 to 2015 and four procedural fields with seeds 200 to 203 (`dev_v5_holdout_hosts.py`; none was blocked by the safety checker).

**Revision 2 results** (the full codec, three seeds, runs `check-r2-default`, `check-r2-holdout`, `check-r2-holdout-clip` and `check-r2-holdout-clip-strong` under `.thesis-build/rehearsal/v5-channel-dev/`). "Kept" means `semantic.found` with `content_match`; a host counts when its key was kept on all three seeds. Outputs blocked by the safety checker are counted as not kept for the host and listed.

| Measure | Revision 1, development hosts, proxy | Revision 2, development hosts, proxy | Revision 2, held-out, proxy | Revision 2, held-out, CLIP vector | Strong arm (cap 3, floor 33 dB), held-out, CLIP |
| --- | --- | --- | --- | --- | --- |
| Hosts | 16 | 16 | 20 | 20 | 20 |
| RGB PSNR, median (range), dB | 40.1 (36.4 to 44.9) | 36.3 (35.2 to 40.1) | 36.0 (35.2 to 41.6) | 36.0 (35.2 to 41.7) | 33.2 (32.8 to 38.9) |
| SSIM, lowest; LPIPS, highest | 0.974; 0.060 | 0.969; 0.065 | 0.961; 0.043 | 0.962; 0.043 | 0.939; 0.069 |
| Admissible (PSNR > 35, SSIM > 0.9, LPIPS < 0.1) | 16/16 | 16/16 | 20/20 | 20/20 | 2/20 |
| Largest block change, grey levels RMS | 7.6 | 10.1 | 10.1 | 10.1 | 15.1 |
| Clean: `both_match` | 16/16 | 16/16 | 20/20 | 20/20 | 20/20 |
| VAE round trip: hosts kept | 9/16 | 16/16 | 20/20 | 18/20 | 20/20 |
| img2img 0.05: outputs; hosts | 27/48; 9/16 | 47/48 (1 blocked); 15/16 | 60/60; 20/20 | 52/60; 17/20 | 59/60; 19/20 |
| img2img 0.1 | 14/48; 4/16 | 38/48; 12/16 | 35/60; 10/20 | 34/60; 11/20 | 47/60; 15/20 |
| img2img 0.2 | 6/48; 1/16 | 23/48; 7/16 | 27/60; 8/20 | 27/60; 8/20 | 33/60; 9/20 |
| img2img 0.4 | 0/48; 0/16 | 10/48; 3/16 | 9/60; 0/20 | 9/60; 2/20 | 17/60; 3/20 |
| Regenerated outputs not read as `semantic_only` or `neither_match` | none | 1 `content_uncertain` (0.2) | 1 `content_uncertain` (0.1) | none | 1 `content_uncertain` (0.2), 1 `content_mismatch` (0.4) |
| Unmarked controls with any key found | 0/224 | 0/224 | 0/280 | 0/280 | 0/280 |
| Wrong owner: any key found | 0/16 | 0/16 | 0/20 | 0/20 | 0/20 |
| JPEG 75 / JPEG 50 | `both_match` all | `both_match` all | `both_match` all | `both_match` all | `both_match` all |
| Gaussian blur, sigma 1.5 | `both_match` 14, `semantic_only` 2 | `both_match` 12, `semantic_only` 2, `content_uncertain` 2 | `both_match` 16, `semantic_only` 4 | `both_match` 11, `semantic_only` 6, `content_uncertain` 3 | `both_match` 12, `semantic_only` 5, `content_uncertain` 3 |
| Resized to 384 / to 384 and back | `semantic_only` / `both_match` all | the same | the same | the same | the same |

The held-out hosts behave like the development hosts, so the configuration is not tuned to the sixteen it was chosen on. Every held-out host keeps the key through the VAE round trip and 0.05 with the layout proxy. With the CLIP vector two held-out hosts lose it at the VAE stage and three at 0.05. The CLIP code moved by at most three bits between the marked image and its VAE output (none on the two failed hosts), so the loss is not code drift. It is the spread of the post-channel score of the weakest hosts: their scores after the VAE are 5 to 8, and a different code draws a different random key, which moves such a score by up to about three points (holdout-generated-01: 7.7 with the proxy's key, 4.8 with the CLIP key). On these hosts the preregistered rate of 9 in 10 is met for the VAE round trip and strength 0.05 and missed at 0.1, 0.2 and 0.4. The strong arm shows that a larger budget buys survival at 0.1 (15 of 20) but not admissibility (2 of 20).

**Revision 1 results** (file SHA-256 `962b5a9a...`, runs `check-r1-default` and `check-r1-strong`). Layout proxy as semantic source, one owner. "Kept" means `semantic.found` with `content_match`; every kept regenerated output read `semantic_only`.

| Measure | Default profile | Strong profile (visibility 2, floor 33 dB) |
| --- | --- | --- |
| RGB PSNR, median (range), dB | 40.1 (36.4 to 44.9) | 35.0 (33.0 to 41.5) |
| SSIM, median (range) | 0.987 (0.974 to 0.991) | 0.975 (0.951 to 0.978) |
| LPIPS, median (range) | 0.008 (0.005 to 0.060) | 0.018 (0.011 to 0.068) |
| Largest block change, grey levels RMS | 7.6 | 15.0 |
| Clean: `both_match` | 16/16 | 16/16 |
| VAE round trip: semantic key kept | 9/16 | 16/16 |
| img2img 0.05: kept; hosts kept on all 3 seeds | 27/48; 9/16 | 46/46 (2 outputs blocked by the safety checker); 15/16 |
| img2img 0.1 | 14/48; 4/16 | 38/48; 12/16 |
| img2img 0.2 | 6/48; 1/16 | 16/48; 5/16 |
| img2img 0.4 | 0/48; 0/16 | 4/48; 0/16 |
| Unmarked controls with any key found | 0/224 | 0/224 |
| Wrong owner: any key found | 0/16 | 0/16 |
| JPEG 75 / JPEG 50 | `both_match` 16 / 16 | `both_match` 16 / 16 |
| Gaussian blur, sigma 1.5 | `both_match` 14, `semantic_only` 2 | `both_match` 14, `semantic_only` 2 |
| Resized to 384x384 | `semantic_only` 16 | `semantic_only` 16 |
| Resized to 384 and back to 512 | `both_match` 16 | `both_match` 16 |

The default profile keeps the semantic key where the host leaves room for it: all four procedural hosts and the generated images with large quiet areas survive the round trip and the lowest strength, the seven most textured generated images do not (their round-trip scores are 3.3 to 5.2 against the threshold of 5.26). The strong profile, at about the fidelity at which the published regeneration-robust methods operate (29 to 40 dB, literature verification), survives the round trip on every host and strength 0.1 on most; it misses the 35 dB admissibility level on about half of the hosts and changes single blocks by up to 15 grey levels RMS.

**Paired comparisons at an earlier mask** (runs `check-final3-*`; `mask_cap` 5, `block_ratio_cap` 2, no fine-scale texture measure; RGB PSNR 35.9 to 43.8 dB). Each changes one factor against the same baseline.

| Kept (VAE; 0.05; 0.1; 0.2; 0.4) | Baseline, layout proxy | Study's CLIP vector, recomputed from every suspect | Refinement stage (30 steps through the VAE and one denoising step) |
| --- | --- | --- | --- |
| Outputs | 12/16; 33/48; 15/48; 8/48; 0/48 | 13/16; 40/48; 14/48; 5/48; 0/48 | 13/16; 39/48; 15/48; 10/48; 0/48 |

With the CLIP vector the code recomputed from a regenerated image drifts, yet at low strength the outcome was no worse than with the proxy; at 0.2 it was slightly worse. The refinement stage raised the post-round-trip score by a median factor of 1.16 within the same budget and moved a few outputs over the threshold; it is not the large gain the brief's emphasis on attack-in-the-loop optimisation suggests.

**The same two comparisons with the final codec** (runs `check-r1-clip` and `check-r1-refined`, started at the user's word on 2026-10-02).

| Kept (VAE; 0.05; 0.1; 0.2; 0.4), outputs; hosts on all 3 seeds | Baseline `check-r1-default` | Study's CLIP vector | Refinement stage |
| --- | --- | --- | --- |
| VAE round trip | 9/16 | 12/16 | 12/16 |
| img2img 0.05 | 27/48; 9/16 | 31/48; 9/16 | 33/48; 11/16 |
| img2img 0.1 | 14/48; 4/16 | 13/48; 4/16 | 14/48; 4/16 |
| img2img 0.2 | 6/48; 1/16 | 4/48; 1/16 | 10/48; 2/16 |
| img2img 0.4 | 0/48 | 0/48 | 0/48 |
| RGB PSNR, median (range), dB | 40.1 (36.4 to 44.9) | 40.1 (36.6 to 44.9) | 40.8 (38.0 to 44.0) |
| Unmarked controls with any key found | 0/224 | 0/224 | 0/224 |
| Ordinary processing, not `both_match` | blur: 2 `semantic_only` | JPEG 50: 1 `content_uncertain`; blur: 2 `content_uncertain`, 1 `semantic_only` | blur: 2 `semantic_only`, 1 `instance_only` |

The CLIP run is not better than the proxy run in any real sense. The semantic code selects the key, and each code draws a different random key, which moves the score of a host by one to two points either way (for example generated-01: 3.67 with the proxy, 5.27 with CLIP; generated-10: 5.02 and 3.81). Twelve against nine on sixteen hosts is within that spread. What the CLIP run does show is a weakness: under JPEG 50 or blur the CLIP code of the three weakest hosts drifted, and with their weak mark the corrected code distance came to 6.8 to 7.1, just over the semantic radius of 6, so the outcome was `content_uncertain`. The layout proxy gave no such case. The refinement stage again helps a little at the cost of under-spending the PSNR budget on textured hosts.

**Tried and rejected during development** (same hosts; prototype code not kept):

- *Chrominance carriers.* The probe's ratio of channel gain to host energy per unit of RGB error is two to three times that of luminance, because the host is weak there. On neutral areas they show as colour tints (author's inspection), and at the scale used the chrominance gain was low, so the tier uses luminance only.
- *Unmasked embedding at a fixed 38 dB* (least-squared-error allocation). It kept the key through strength 0.1 in 28 to 30 of 32 trials and through 0.2 in 21 to 27 of 32, depending on the band, but it puts the change into flat regions, where it is plainly visible as mottling. The mask costs most of that margin.
- *A lower band* (8x8 DCT of the image averaged 8x8, 64-pixel blocks) with edge-free rendering. On the host tried it was no less visible in flat regions and its clean score was about half at equal visibility.
- *Multiplicative embedding read in the log-magnitude domain.* A host-proportional change is returned by the channel 1.4 to 2.5 times better than an additive one, but the magnitude statistic lost far more than that; with the linear statistic, host-proportional shaping was worse than the least-cost allocation at equal PSNR.
- *Normalising by position only*, without the block normaliser: the weakest host lost about 40% of its score after the VAE round trip.
- *A texture mask without the fine-scale measure and with a larger block cap* (`block_ratio_cap` 2). Blocks whose quadrants all held some coarse texture but which contained a smooth patch (a white drawer front, snow at the edge of a forest, bare wood) changed by up to 10 grey levels RMS and showed as lighter or darker rectangles at three times magnification. The fine-scale measure and the lower block cap remove that at the cost of score on the most textured hosts. A `mask_cap` of 4 was also tried and cost the most textured hosts more score than its visual gain seemed to justify; 6 left faint rectangles on smooth wood.
- *Inversion-based detection* in the manner of ZoDiac or Tree-Ring: excluded by the proposal's lightweight extractor, and its published false-positive rates and fidelity are outside this project's limits (see the literature verification).

## Limits of this evidence

- Synthetic hosts only; generated images pass the autoencoder of their own generator more easily than photographs do, and the procedural ones are not natural images. The held-out set guards against tuning to sixteen images, not against the difference between generated images and photographs.
- One model, one sampler, no prompt, single regeneration. The design of revision 2 used the attack model's own outputs (on synthetic images) to choose constants; the refinement stage is tuned on the same model that attacks.
- One owner and one key per host and run; the spread of a weak host's score over keys is large (about three points), so per-host outcomes near the threshold are partly luck of the key. Negatives are 224 to 280 unmarked calls and 16 to 20 wrong-owner checks per run, which can show the absence of gross errors and nothing about a rate near 1e-6.
- Visibility was judged by the author on a screen, on a few images per revision, including the most-changed block of each, magnified three times; with revision 2 the change was not visible on snow, rock, sky and brick, and a faint grain from the fragile tier (unchanged since revision 1) was visible in a flat sky at that magnification. No human assessment exists. The mask constants, the block cap of 2, the shaping constants and the 35.5 dB floor are engineering defaults. The change is continuous inside a block but not across block borders, which the mask and the shaping keep faint and do not remove.
- Two runs per revision used the study's CLIP vector; the others used the layout proxy, whose code does not drift under regeneration.
- The author wrote the codec, the tests and this document. No independent review has taken place.

## What is still to run

The user stopped GPU runs on 2026-10-02 and later the same day said to continue ("ادامه بده"), then to continue until the result is acceptable. Since then: the CLIP and refinement checks of revision 1 ran (reported above), revision 2 was designed and checked on development and held-out hosts, and the study package was moved to revision 2. Commands are in `experiments/c4-v5-two-tier-regeneration-v1/runbook.md` on the study branch.

1. The rehearsal of the study package at its revision-2 commit on synthetic images (no approval needed under the 2026-10-02 policy; about 30 to 60 minutes).
2. Only then: the manifest of the real study, an independent review, its approval by the user and its launch by the user.

## What must happen before any scientific use

1. An independent review of this amendment, the codec and the tests, by a reviewer other than the author.
2. The user's decision on adoption and, for deviations 17, 18, 20 and 27, the supervisor's.
3. A preregistered study on the reserved photographs through the official runner with a manifest-specific approval. A package is prepared in `experiments/c4-v5-two-tier-regeneration-v1/`; it has not been run.
4. Human visual assessment of marked images, flat regions in particular.

## Sources

Checked on 2026-10-02; see [redesign-inputs/literature-verification-20261002.md](redesign-inputs/literature-verification-20261002.md) for what was read of each and for the errors found in the brief's citations.

- X. Zhao, K. Zhang, Z. Su, S. Vasan, I. Grishchenko, C. Kruegel, G. Vigna, Y.-X. Wang, L. Li. Invisible Image Watermarks Are Provably Removable Using Generative AI. NeurIPS 2024. arXiv 2306.01953.
- B. An et al. WAVES: Benchmarking the Robustness of Image Watermarks. ICML 2024. arXiv 2401.08573.
- Y. Liu et al. Image Watermarks are Removable Using Controllable Regeneration from Clean Noise. ICLR 2025. arXiv 2410.05470.
- L. Zhang et al. Attack-Resilient Image Watermarking Using Stable Diffusion (ZoDiac). NeurIPS 2024. arXiv 2401.04247.
- S. Lu et al. Robust Watermarking Using Generative Priors Against Image Editing: From Benchmarking to Advances (VINE). ICLR 2025. arXiv 2410.18775.
- Y. Guo et al. FreqMark: Invisible Image Watermarking via Frequency Based Optimization in Latent Space. NeurIPS 2024. arXiv 2410.20824.
- S. J. Lee, N. I. Cho. PhaseMark. arXiv 2601.13128 (preprint, 2026).
- H. S. Malvar, D. A. F. Florencio. Improved Spread Spectrum: A New Modulation Technique for Robust Watermarking. IEEE Transactions on Signal Processing, 2003 (as cited in the v4 amendment; not re-read today).
- V. Bentkus, D. Dzindzalieta. A tight Gaussian bound for weighted sums of Rademacher random variables. Bernoulli 21(2), 1231 to 1237, 2015. doi:10.3150/14-BEJ603 (statement and constant checked on 2026-10-02 against the publisher's abstract; used for deviation 26 and checked exhaustively on small sums in the tests).
