# Method amendment v4: content-bound dual-key DCT watermark (image-domain reference)

Status: **engineering candidate with synthetic checks only, 2026-10-01**. Authority: [method-amendment-decision-20261001.md](method-amendment-decision-20261001.md). Findings that motivated it: [algorithm-review-v3-20261001.md](algorithm-review-v3-20261001.md). This file applies [scope-guard.md](scope-guard.md), [research-contract.md](research-contract.md), [io-spec.md](io-spec.md), [threat-model.md](threat-model.md) and [proposal-aligned-plan-20260930.md](proposal-aligned-plan-20260930.md). It does not rewrite the proposal, the claim ledger, the A5 [method-spec.md](method-spec.md) or the v2/v3 candidates, and it advances no gate.

Reference implementation: [`scripts/revised_watermark_v4.py`](../scripts/revised_watermark_v4.py) (standard library only). Tests: [`scripts/test_revised_watermark_v4.py`](../scripts/test_revised_watermark_v4.py). Profiles: [`configs/revised-watermark-v4.example.json`](../configs/revised-watermark-v4.example.json) (public-derived), [`configs/revised-watermark-v4-keyed.example.json`](../configs/revised-watermark-v4-keyed.example.json), schema [`configs/revised-watermark-v4.schema.json`](../configs/revised-watermark-v4.schema.json). Synthetic comparison: [`scripts/bench_revised_watermark_synthetic.py`](../scripts/bench_revised_watermark_synthetic.py).

## Claim boundary

v4 is an **image-domain** codec. Its role in the study is the labelled pixel comparator for EXP-EMBED and the positive control for the DCT detector. It does not implement latent or initial-noise embedding, so RQ-02, HYP-02, OBJ-02 and METHOD-06 stay open and no v4 result may be cited as support for them. Nothing here has been run on a real image, a JPEG file, a diffusion model or a CLIP encoder. No detector state establishes legal ownership.

## Why v3 was not kept

The v3 review confirmed these defects on synthetic images; details and numbers are in the review file.

- The carrier is unchanged hard-decision QIM at step 4. It loses the payload at noise sigma 2, at contrast x0.8 and after a 3x3 blur. The retained real v2 run shows marked and unmarked images indistinguishable after regeneration, and v3 changes nothing in that mechanism.
- The owner tag is recomputed from the binding of the suspect image, so one flipped binding bit rejects a genuine mark. This is the avalanche that amendment v2 set out to remove.
- The binding reads at most 64 block means through public index arithmetic. A keyless attacker can force a recipient to the donor's binding and transplant the publicly readable payload; the reviewers' probes had such forgeries accepted as authentic.
- The decision is one boolean. The proposal's three states cannot be produced, and a copied mark is indistinguishable from a wrong owner.
- The thresholds 0.75 / 0.75 / 0.65 have no stated false-positive rate; accepting 48 of 64 tag bits gives a forgery probability of about 3.9e-5.
- v3 exists only as a secret-key variant, so the proposal's public-derived profile had disappeared without a decision record.

## Method

The three phases below are the proposal's phases (inputs/proposal-text.md lines 194-216). Symbols follow [notation.csv](notation.csv) where they exist.

### Shared definitions

`pack(f1, f2, ...)` is each byte field preceded by its 4-byte big-endian length. `stream(K, label, n)` is the first `n` bytes of `HMAC-SHA256(K, pack("rw-v4", config, label, uint32be(i)))` for `i = 0, 1, ...`. `config` is the 32-byte `detector_config_id`: SHA-256 of `"rw-v4/config/"` followed by the canonical JSON (sorted keys, compact separators) of the profile fields `schema_version`, `profile`, `security`, `semantic_source`, `minimum_side`, `semantic_frequencies`, `instance_frequencies`, `code_bits`, `tag_bits`. Embedding strength and decision thresholds are not part of it: the detector needs neither.

`K` is `SHA-256("rw-v4/public-derived-profile-key")` in the `public-derived` profile and the caller's 16 to 4096 byte secret in the `hmac-keyed` profile.

The input is a luminance matrix in [0, 255] with both sides at least 160. Only complete 8x8 blocks from the top-left origin are used; a right or bottom remainder of up to seven pixels is neither read nor modified. `M` is the map of block means. `C[b, u, v]` is the orthonormal 8x8 DCT-II coefficient of block `b` (row-major).

A **sign projection** of a vector `x` with label `L` is 32 bits: bit `j` is 1 iff `sum_k r[j,k] * x[k] > 1e-9`, where the Rademacher row `r[j]` is read from `stream(K, pack(L, uint32be(len(x))), 32 * ceil(len(x)/8))`, one bit per entry, least significant bit of each byte first, bit 1 meaning -1. The code is assembled most significant bit first.

### Phase 1: dual signature

- **Perceptual hash `H` (METHOD-03).** `H` is the sign projection, label `perceptual-projection`, of a vector with two parts, each scaled to a fixed share of the energy.
  - *Coarse part, share 0.25.* Area-resample `M` to 32x32. Take its orthonormal 2-D DCT-II and keep the 63 coefficients with `u, v < 8` except DC, ordered by `(u+v, u, v)`. Multiply each by `sqrt(u^2 + v^2)`. This is the input of the classic pHash.
  - *Detail part, share 0.75.* For each of the positions (0,1) and (1,0), in that order, form the map of `C[b, u, v]` over blocks. Subtract from every entry the mean of its 3x3 neighbourhood (edges replicated). Map the result `g` to `sign(g) * a / (a + 8)` with `a = max(0, |g| - 6)`. Append the two maps in row-major order.
  - Each part is divided by its Euclidean norm (a part with norm below 1e-9 becomes zero) and multiplied by the square root of its share; the vector is the coarse part followed by the detail part.

  The detail part is what the proposal asks of `H`: it separates two images that share a composition. The low band of a 32x32 map alone cannot; on a synthetic same-structure family its codes were identical. Positions (0,1) and (1,0) are reserved for the hash and may not appear in a channel's coefficient set.
- **Semantic code `q` (METHOD-02).** `q` is the sign projection, label `semantic-projection`, of the semantic vector `E`. In a profile with `semantic_source = "external:<id>"` the caller supplies `E`; the study profile uses the pinned CLIP ViT-B/32 image embedding. In `proxy-layout-v1` the vector is `M` area-resampled to 8x8 with its mean removed. That proxy is a coarse-layout descriptor for model-free tests. It is not CLIP and carries no semantic meaning.
- **Keys (METHOD-04, METHOD-05).** `Ws = stream(K, pack("ws", OwnerID, q), 16)` and `Wi = stream(K, pack("wi", OwnerID, q, H), 16)`, each read as 128 bits. OwnerID is NFC-normalised UTF-8, 1 to 256 bytes; `q` and `H` are 4-byte big-endian.

Sign projections replace hashing of the raw codes on purpose. Two inputs at angle `theta` differ in each bit with probability `theta/pi`, so a small change in content moves few bits and codes can be compared by Hamming distance. `Ws` and `Wi` are still exact functions of the codes; the tolerance comes from the helper data below, not from weakening the keys.

`H` and the proxy `q` read only block means and the two reserved positions, none of which the embedder changes, so an image and its marked version have the same codes up to rounding and clipping. With an external encoder that invariance is not guaranteed and must be measured.

### Phase 2 (image-domain arm): embedding

Two channels use disjoint coefficient sets, both configurable in the profile:

```text
semantic  F_s = [(1,1), (0,2), (2,0), (1,2), (2,1), (2,2)]
instance  F_i = [(0,3), (3,0), (1,3), (3,1), (2,3), (3,2)]
```

Each channel carries 320 bits: 192 helper chips followed by the 128 key bits (`Ws` on the semantic channel, `Wi` on the instance channel). The helper chips encode the 32-bit code of that channel (`q` or `H`) plus a 4-bit CRC (polynomial x^4+x+1) as six 6-bit symbols of the biorthogonal Reed-Muller code RM(1,5): symbol `(s, i)` becomes the 32 chips `s XOR parity(i AND k)`.

**Carrier.** For channel `c`, list the slots block by block and, within a block, in the order of `F_c`. Draw one 8-byte word per slot from `stream(K, pack("carrier", c, OwnerID, uint32be(height), uint32be(width)), 8 * slots)`. Sort slots by `(word >> 1, slot index)`; the slot at rank `r` carries channel bit `r mod 320`. Its sign is +1 if the word is odd, else -1. The **projection** of bit `b` is `p[b] = sum(sign * C) / sqrt(count_b)` over its slots. The carrier depends on the key and the owner, so different owners use nearly orthogonal directions.

**Improved spread spectrum.** Let `e[b]` be +1 for bit 0 and -1 for bit 1. The embedder moves every projection from its host value `p` to

```text
p* = (1 - lambda) * p + A * e
```

by adding `(p* - p) / sqrt(count_b) * sign` to each slot of the bit. The distortion budget is `MSE = 255^2 / 10^(target_psnr_db/10)` over the whole image, split between the channels by `semantic_energy_share`. For a per-bit budget `D` and mean host power `S`, `lambda` in {0, 0.01, ..., 1} maximises `(D - lambda^2 S) / ((1 - lambda)^2 S + design_noise_std^2)` and `A = sqrt(D - lambda^2 S)`. The output is rounded to integers and clipped to [0, 255] inside the loop; the loop runs `passes` times against the same targets so rounding and clipping losses are corrected.

**Self-verification.** The embedder runs the real detector on its output. If the outcome is not `both_match` it raises `EmbeddingError` carrying the full report (or returns it with `strict=False`). A mark that cannot be verified is a recorded embedding failure, never a silently weak mark.

`projection_targets()` exports the slots, signs, host projections and targets. Any embedder that drives the projections of its output to those targets is read by the same detector. That is the interface a diffusion-latent embedder needs for a fair latent-versus-pixel comparison with one shared detector; no such embedder exists in this amendment.

### Phase 3: detection

Inputs: the suspect image, the claimed OwnerID, the profile, the secret key in the keyed profile, and `E(J)` in an external-encoder profile. No original image, enrolment record, prompt or seed.

1. Compute `q(J)` and `H(J)`, the block DCT, and the 320 projections of each channel.
2. Decode the helper chips of each channel by soft maximum-likelihood decoding (fast Walsh-Hadamard transform per symbol) to obtain the carried codes `q^` and `H^`.
3. **Semantic key.** Candidates are `Ws(q(J))` ("recomputed", the proposal's route) and, if different, `Ws(q^)` ("decoded"). For each, compute

   ```text
   z = sum(e[b] * p[b]) / sqrt(sum(p[b]^2))        over the 128 key bits
   ```

   and keep the larger. The key is **found** if `z >= sqrt(2 ln(m K / alpha))`, where `m` is the number of candidates, `K` the roster size and `alpha` the profile's `false_positive_target`.
4. **Instance key.** The same test with `Wi(q, H)` over `q` in {the code that verified `Ws`, or both candidates if none did} and `H` in {`H(J)`, `H^`}.
5. Content distances are the Hamming distances between the code that verified each key and the code recomputed from the suspect image.

| Semantic key | Instance key | Content codes | `outcome` | `proposal_state` |
| --- | --- | --- | --- | --- |
| found | found | both within radius | `both_match` | `authentic` |
| found | not found | semantic within radius | `semantic_only` | `regenerated` |
| found, or instance found | any | a verified key's code is outside its radius | `content_mismatch` | `copy_paste` |
| not found | found | within radius | `instance_only` | `unclassified` |
| not found | not found | n/a | `neither_match` | `no_watermark` |

`outcome` is the observation. `proposal_state` is the label that the proposal's decision table (lines 212-214) assigns to it. Neither is ground truth: whether an image was regenerated or forged is known only from attack provenance, and the evaluation must score these labels against that provenance (SC-03).

`content_mismatch` is new relative to io-spec.md. It resolves IO-06 for this candidate: a key that verifies through the codes carried in the mark is a presence witness that does not depend on the current content, so "a mark of this owner is present but bound to other content" becomes observable and distinct from "no mark".

`binding_mode` (`combined`, `semantic_only`, `perceptual_only`, `none`) switches the content checks off selectively. These are the C6 ablations; `none` is the binding-disabled control.

## Statistical basis

For fixed projections `p` and a pattern `e` of independent fair signs, Hoeffding's inequality gives `P(z >= t) <= exp(-t^2 / 2)`. The bound needs no assumption about the image. It needs the pattern to be independent of the projections it is tested against. That holds under the PRF assumption for an unmarked image, a wrong owner, a wrong key, and a mark made for different codes, because the tested pattern is then an HMAC output over an input unrelated to those projections. Helper chips and key bits occupy disjoint slots.

The threshold is therefore derived, not tuned: `alpha = 1e-6` with one candidate gives 5.26, with two candidates 5.39, and the maximum attainable score is `sqrt(128) = 11.31`. The result reports `log10_false_positive_bound` for the observed score, the number of candidates, and the roster size. `identify()` tries a roster and applies the same correction.

Three limits apply. The bound is conservative, so the realised false-positive rate is lower than `alpha` and must still be confirmed on unmarked (C0) and wrong-owner (C2) validation images before any rate is quoted. The content radii (6 of 32 bits by default) are engineering defaults; for independent uniform codes `P(distance <= 6) = 2.7e-4`, but real codes are neither independent nor uniform, so collision rates must be measured (T5). And every default in `decision` is uncalibrated until A4 freezes it on validation data.

## Profiles and threat coverage

| Profile | Secret | What a party without the secret can do |
| --- | --- | --- |
| `public-derived` (default, proposal profile) | none | Compute every code, key and carrier. Re-embedding for any OwnerID (T6) is possible by design. Detection shows a public-profile mark bound to this content, not who placed it. |
| `hmac-keyed` (keyed variant) | 16+ bytes | Cannot compute the projections, codes, keys or carrier. Only key holders can embed or verify; a leaked key enables forgery. |

Results of the two profiles are never pooled. The keyed variant changes the detector's knowledge profile (io-spec.md, `secret_ref`) and needs its own wrong-key control (C3) and table.

| Threat | What v4 does | What is not claimed |
| --- | --- | --- |
| T4 copy-paste | A transferred mark either fails to verify (`neither_match`) or verifies through its carried codes and is reported as `content_mismatch`. In the keyed profile the codes are keyed sign projections of image-wide content, so they cannot be targeted without the key. | An attacker who makes the recipient's content codes match the donor's is accepted. In the synthetic test, importing the donor's block means was not enough; importing its block means and its (0,1) and (1,0) coefficients was, at under 20 dB against the recipient. A cheaper targeted edit may exist and has not been searched for. The public profile offers no protection against a method-aware attacker (T6). No real-image measurement exists. |
| T5 semantic collision | The instance key binds `H` in addition to `q`. Two images with the same semantic code but different `H` are separated; the `semantic_only` ablation accepts the same forgery. In two synthetic same-composition families (40 images each, 780 pairs) the fraction of distinct pairs within the instance radius was 0.4% and 0.8%. | Those rates are far above the 2.7e-4 of independent codes and come from synthetic families only. Whether real same-subject photographs have distinct `H` and equal `q` under CLIP is unmeasured (HYP-01 stays open). |
| T3 regeneration | The semantic channel sits in the lower band and the correlation statistic is invariant to gain, so it degrades gradually instead of failing at a noise cliff. `semantic_only` is a reachable state. | Survival of real diffusion regeneration. Published benchmarks report hand-crafted transform-domain marks at about 40 dB removed almost completely by regeneration; expect the image-domain arm to fail at the strengths used in the retained run until a new run shows otherwise. |
| T1 benign processing | Tolerates the synthetic noise, contrast, blur and requantisation levels in the table below. | Crop, resize, rotation and pixel shift: the carrier is tied to the image size and a fixed block grid. |
| T2 removal | Removal without the key requires disturbing the whole band. | Resistance to removal; any distortion that destroys the band removes the mark. |
| T6 re-embedding | Blocked for parties without the key in the keyed profile. | Anything in the public profile. |
| T7 oracle or white-box | None. | Scores must not be exposed to untrusted callers; a detector oracle allows hill-climbing. |

Competing claims are not resolved. An adversary can search for an (OwnerID, key) pair whose patterns happen to pass on a given image; the work per channel is about `1 / alpha` detections, and both channels together about `1 / alpha^2`. Resolving such claims needs key commitment or enrolment, which the scope guard excludes from the required implementation (SC-01, SC-04).

## Traceability to the proposal

| Claim ID | v4 status |
| --- | --- |
| METHOD-02 semantic vector | Interface only: sign projection of a supplied vector. CLIP stays outside the codec; the proxy is not CLIP. |
| METHOD-03 DCT pHash | Implemented (keyed sign projections of the low DCT band). |
| METHOD-04, METHOD-05 dual keys | Implemented. |
| METHOD-06 latent embedding | **Open.** Not implemented; only the target-projection interface exists. |
| METHOD-07 recompute candidate keys | Implemented; a second candidate from carried codes is an addition. |
| METHOD-08 8x8 mid-band correlation | Implemented. |
| METHOD-09 decision states | Implemented as observations plus decision-table labels. |
| OBJ-01, RQ-01, HYP-01 | Mechanism implemented; the empirical claim is open (needs CLIP and real same-subject pairs). |
| OBJ-02, RQ-02, HYP-02, METRIC-05 latent arm | **Open.** v4 can only be the pixel arm. |
| OBJ-03, RQ-03, HYP-03, METRIC-07 | Detector and per-stage timing fields exist. Comparators (neural decoder, inversion-based) are open; pure-Python timings are not the efficiency evidence. |
| OBJ-04, RQ-04, HYP-04, METRIC-06 | Mechanism and continuous scores (`z`, code distances) exist for ROC/AUC; no real evaluation. |
| METRIC-01..03 | PSNR helper only; SSIM and LPIPS stay in the evaluation harness. |
| METRIC-04 | Supplementary; synthetic stand-ins only. |
| DATA-01..03, SCOPE-02, SCOPE-03 | Untouched and open. |

## Additions and deviations

Each is a method choice to be validated, not a result.

1. **Helper data.** The codes `q` and `H` travel in the mark, protected by RM(1,5). The proposal recomputes candidate keys from the suspect image only. The addition removes the one-bit avalanche, replaces the 13 x 33 candidate enumeration of method-spec.md with at most two and four candidates, and supplies the presence witness of IO-06.
2. **Keyed pseudorandom function.** HMAC-SHA256 replaces plain hashing in both profiles; the public profile uses a published constant as key, which is equivalent to a public hash.
3. **Sign-projection codes and a detail-aware hash.** Random-hyperplane codes replace the median-threshold pHash and the 12-bit projection of method-spec.md, so that the keyed profile hides which statistics define the code. `H` adds block-gradient detail to the classic low-band input, because the low band alone does not separate images of one composition. The shares, the dead zone and the knee are engineering defaults chosen on synthetic families.
4. **Frequency sets.** The semantic channel uses lower positions than method-spec.md's `F_s`. This follows published evidence that editing removes mid and high frequencies first; it is a validation-selectable parameter and an ablation factor.
5. **Embedding domain.** Image-domain improved spread spectrum instead of latent/noise embedding. This is the declared pixel comparator, not a replacement.
6. **Colour.** `embed_rgb` adds the luminance change equally to R, G and B and verifies the rounded RGB output.

## Engineering evidence (synthetic only)

`unittest discover -s scripts` passes 77 tests with the verified Windows interpreter; 26 belong to v4. The v4 tests cover: clean round trip and quality budget; determinism; wrong owner, wrong key and unmarked images; separation of the two profiles; an unmarked population (12 images x 5 owners) against the stated null; sizes that are not multiples of eight, low-contrast, gradient and flat-tone hosts; noise, contrast, blur and requantisation; a comparison with v3 under the same distortions; band transplant with the binding-disabled control; residual and patch copies; forcing the content codes; drift tolerance; two images of one composition; a shared semantic vector with different instances; loss of the instance band; hash stability and key dependence; helper decoding; the false-positive bound over 20,000 random patterns; roster correction; the projection contract; profile validation and the example files; malformed input; a host-dominated failure; saturation; and the colour wrapper.

Benchmark `scripts/bench_revised_watermark_synthetic.py`, six procedural 256x256 hosts with texture amplitudes 6, 12 and 20, counts out of 6 accepted as authentic:

| Condition | v3 (QIM step 4) | v4 at matched PSNR | v4 default budget |
| --- | --- | --- | --- |
| Mean PSNR (dB) | 50.44 | 49.87 | 41.85 |
| No distortion | 6 | 3 | 6 |
| Noise sigma 2 | 0 | 3 | 6 |
| Noise sigma 5 | 0 | 3 | 6 |
| Noise sigma 10 | 0 | 3 | 6 |
| Noise sigma 20 | 0 | 0 | 6 |
| Contrast x0.8 | 2 | 3 | 6 |
| Box blur 3x3 | 0 | 2 | 5 |
| Box blur 5x5 | 0 | 0 | 0 |
| Requantise step 8 | 0 | 3 | 6 |
| Requantise step 16 | 0 | 2 | 6 |
| Requantise step 24 | 0 | 0 | 5 |
| Blur 3x3 + noise 4 | 0 | 0 | 5 |
| Blur 5x5 + noise 6 | 0 | 0 | 0 |
| Unmarked accepted | 0 | 0 | 0 |
| Band transplant accepted as authentic | 0 | 0 | 0 |
| Band transplant, mark found | 6 | 3 | 6 |
| Residual copy accepted as authentic | 0 | 0 | 0 |
| Residual copy, mark found | 0 | 2 | 4 |

The same benchmark with six 512x512 hosts (`--size 512`):

| Condition | v3 (QIM step 4) | v4 at matched PSNR | v4 default budget |
| --- | --- | --- | --- |
| Mean PSNR (dB) | 50.49 | 49.84 | 41.86 |
| No distortion | 6 | 6 | 6 |
| Noise sigma 2 | 0 | 6 | 6 |
| Noise sigma 5 | 0 | 6 | 6 |
| Noise sigma 10 | 0 | 6 | 6 |
| Noise sigma 20 | 0 | 3 | 6 |
| Contrast x0.8 | 2 | 6 | 6 |
| Box blur 3x3 | 0 | 4 | 6 |
| Box blur 5x5 | 0 | 0 | 0 |
| Requantise step 8 | 0 | 6 | 6 |
| Requantise step 16 | 0 | 6 | 6 |
| Requantise step 24 | 0 | 3 | 6 |
| Blur 3x3 + noise 4 | 0 | 4 | 6 |
| Blur 5x5 + noise 6 | 0 | 0 | 0 |
| Unmarked accepted | 0 | 0 | 0 |
| Band transplant accepted as authentic | 0 | 0 | 0 |
| Band transplant, mark found | 6 | 6 | 6 |
| Residual copy accepted as authentic | 0 | 0 | 0 |
| Residual copy, mark found | 0 | 4 | 6 |

Reading the tables:

- At its default budget v4 survives every tested distortion except the 5x5 blur, where v3 survives none beyond contrast on two hosts. v4 spends 8.6 dB more distortion to do so and stays 6.9 dB above the proposal's 35 dB target.
- At v3's own distortion level the comparison depends on image size. At 512x512 v4 verifies all six clean hosts and keeps most of its robustness. **At 256x256 v4 is worse than v3 on clean images**: it verifies only the three low-texture hosts. Spread-spectrum embedding pays to cancel the host's own energy in the band, and at 50 dB the budget does not cover textured hosts of that size. This is the method's operating envelope, not a tuning problem.
- A residual copy also delivers the mark in most v4 cases (it is an additive transfer) and is likewise reported as `content_mismatch`. The content binding, not the modulation, is what rejects it.
- A band transplant delivers the mark in every v4 case and is reported as `content_mismatch` every time. For v3, "mark found" means the public payload is readable on the recipient; the transplant is rejected only because the attacker did not also force the block-mean binding, which the review showed is cheap.
- The 5x5 blur rows are failures and stay in the table.

**Operating envelope.** The clean score is about `sqrt(E_tag / host power)` when the host dominates, where `E_tag` is the energy spent on the 128 key bits of a channel. It grows with the square root of the pixel count. At 42 dB the semantic channel reaches a clean score of 9 for a band RMS of roughly 28 at 256x256 and 56 at 512x512. Smaller or more textured images fail self-verification and are reported as embedding failures. The pathological sawtooth pattern used by the v2/v3 unit tests (band RMS about 148 at 160x160) is such a failure and is kept as a test. A lattice modulation (spread-transform dither modulation) rejects the host at no cost and would widen the envelope, but in the scratch prototypes it lost the gain invariance that matters under blur and it needed the detector to estimate the step; it is recorded as a possible later ablation, not adopted.

Pure-Python timing on the development machine, 256x256: embedding about 0.2 s, detection about 40 ms. These figures describe the reference implementation only.

## What must happen before any scientific use

1. Independent review of this exact amendment and code (reviewer differs from author).
2. A wrapper that passes canonical RGB8 PNG pixels and the pinned CLIP embedding, with per-profile receipts.
3. A4 preregistration for this candidate: frequency sets, PSNR budget, `alpha`, radii, roster, attack inventory, and the adaptive-transplant arm that actually delivers the mark at admissible quality (the retained T4 arms did not).
4. For T3, a dose-response design (VAE round trip alone, then low strengths) so that survival is a curve rather than one 0/N, with the analytic expectation of failure recorded beforehand.
5. The existing runner's manifest-specific authorization. No run is authorized by this document.

## Sources

Verification status is as recorded by the literature review of 2026-10-01: "read" means the paper text or abstract was fetched in that session, "metadata" means only the citation was confirmed, and no number below is transferred to this codec.

- Malvar and Florencio, "Improved spread spectrum: a new modulation technique for robust watermarking", IEEE TSP 51(4), 2003, DOI 10.1109/TSP.2003.809385 (abstract read): host-interference rejection in the correlation detector.
- Chen and Wornell, "Quantization index modulation", IEEE TIT 47(4), 2001 (read): spread-transform dither modulation; private-key versus no-key systems.
- Eggers, Bauml, Tzschoppe and Girod, "Scalar Costa scheme for information embedding", IEEE TSP 51(4), 2003 (read): spread spectrum is preferable to quantisation embedding under very strong attacks; repetition coding is inefficient.
- Fridrich and Goljan, "Robust hash functions for digital watermarking", ITCC 2000, DOI 10.1109/ITCC.2000.844203 (read): key-dependent projection hashes; public patterns let an attacker change hash bits.
- Arabi, Witter, Hegde and Cohen, "SEAL: Semantic aware image watermarking", arXiv:2503.12172v4 (read): SimHash of a semantic embedding.
- Fernandez et al., "The Stable Signature", arXiv:2303.15435 (read): closed-form false-positive rate and multi-key correction.
- An et al., "WAVES", arXiv:2401.08573 (read): TPR at 0.1% FPR as the reporting standard.
- Zhao et al., "Invisible image watermarks are provably removable using generative AI", arXiv:2306.01953v3 (read): conditional bound and empirical removal of low-perturbation marks.
- Lu et al., "Robust watermarking using generative priors against image editing" (W-Bench/VINE), arXiv:2410.18775 (read): classical transform-domain marks at about 40 dB fall to a few percent TPR under regeneration; low-frequency patterns survive editing better.
- Kutter, Voloshynovskiy and Herrigel, "Watermark copy attack", Proc. SPIE 3971, 2000, DOI 10.1117/12.384991 (metadata); Barr, Bradley and Hannigan, ICASSP 2003, DOI 10.1109/ICASSP.2003.1199109 (metadata); Juels and Wattenberg, "A fuzzy commitment scheme", ACM CCS 1999, DOI 10.1145/319709.319714 (metadata); Charikar, STOC 2002, DOI 10.1145/509907.509965 (metadata); Hoeffding, "Probability inequalities for sums of bounded random variables", JASA 58(301), 1963 (not fetched).
