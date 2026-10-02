# Method amendment v4: content-bound dual-key DCT watermark (image-domain reference)

Status: **engineering candidate, revision 2, 2026-10-01**. Authority: [method-amendment-decision-20261001.md](method-amendment-decision-20261001.md). Findings that motivated it: [algorithm-review-v3-20261001.md](algorithm-review-v3-20261001.md). Independent review of v4 itself: [`audits/v4-independent-review-20261001/`](../audits/v4-independent-review-20261001/review.md). Independent verification of revision 2: [`audits/v4-revision-2-verification-20261001/`](../audits/v4-revision-2-verification-20261001/review.md). This file applies [scope-guard.md](scope-guard.md), [research-contract.md](research-contract.md), [io-spec.md](io-spec.md), [threat-model.md](threat-model.md) and [proposal-aligned-plan-20260930.md](proposal-aligned-plan-20260930.md). It does not rewrite the proposal, the claim ledger, the A5 [method-spec.md](method-spec.md) or the v2/v3 candidates, and it advances no gate.

Reference implementation: [`scripts/revised_watermark_v4.py`](../scripts/revised_watermark_v4.py) (standard library only). Tests: [`scripts/test_revised_watermark_v4.py`](../scripts/test_revised_watermark_v4.py). Synthetic hosts and distortions: [`scripts/watermark_synthetic.py`](../scripts/watermark_synthetic.py). Profiles: [`configs/revised-watermark-v4.example.json`](../configs/revised-watermark-v4.example.json) (public-derived), [`configs/revised-watermark-v4-keyed.example.json`](../configs/revised-watermark-v4-keyed.example.json), schema [`configs/revised-watermark-v4.schema.json`](../configs/revised-watermark-v4.schema.json). Synthetic comparison: [`scripts/bench_revised_watermark_synthetic.py`](../scripts/bench_revised_watermark_synthetic.py).

## Revisions

| Revision | Where | What |
| --- | --- | --- |
| 1 | Commit `0e91bd2` on `codex/18-v4-three-threats`; file SHA-256 `5c5dd3e2...` | The first complete v4. Another agent committed this snapshot and ran it as `c4-v4-three-threat-dev-001` (see "Real-image observations"). |
| reviewed state | Working tree at the time of the independent review; file SHA-256 `d7e2b893...` | Revision 1 plus the undecided zone in the decision and strict profile validation, made after a first, cut-off review round. Same `detector_config_id` as revision 1. The independent review measured this state. |
| 2 | The working tree described here | Changes after that review: the detail part of the perceptual hash is floored, so noise-level detail on smooth images is no longer inflated; a found instance key with an undecided hash reads `content_uncertain`, and `no_watermark` became `not_detected`; the byte-rounding loss is budgeted; the semantic code is scale-free; a featureless suspect image is a negative; results carry no key fingerprint. An independent verification measured this state (file SHA-256 `a5b6c02d...`). Changes followed it and are listed in the verification record: numerical tolerances in the helper decoder and the score, which change reported scores, decoded candidates, candidate counts and `helper_check_ok` on flat, piecewise-constant and block-periodic images, where projections are zero or tied to within rounding, also when the band has energy; the rounding allowance on the colour path; and a decision function that ignores the status of a key that was not found. The final file is SHA-256 `723773c7...`. |

Revisions 1 and 2 derive different `detector_config_id` values, so neither reads the other's marks and their results cannot be confused. The changes made after the verification leave the luminance embedder's output and the reading of marked textured images as they were: nothing differed on textured hosts in a reviewer's 797 detections, and the synthetic benchmark output, which records outcomes and PSNR but no scores, is byte-identical before and after. On plain and degenerate images reported scores and candidates differ, and in that reviewer's 1,931 synthetic detections one outcome changed: a residual copy onto a plain host after requantisation at step 16 read `content_mismatch` before and reads `neither_match` now, and the earlier reading depended on floating-point summation order. `REVISION` and the `detector_config_id` did not change, so results of the verified state and of the final state can be told apart only by the file hash. The colour wrapper now plans a slightly smaller signal and writes different pixels.

## Claim boundary

v4 is an **image-domain** codec. Its proposed role is a candidate pixel comparator for EXP-EMBED and a positive control for the DCT detector; whether the thesis adopts it is undecided (see the decision record). It does not implement latent or initial-noise embedding, so RQ-02, HYP-02, OBJ-02 and METHOD-06 stay open and no v4 result may be cited as support for them. No detector state establishes legal ownership.

No number in this document comes from a real image, a diffusion model or a CLIP encoder, except in the section "Real-image observations", which reports a run made by another agent with revision 1, and the band-RMS and PSNR ranges of that run quoted for comparison in "Limits of this evidence" and in Phase 2. The only JPEG figures are the reviewers' and verifiers' PIL-encoded synthetic images.

## Why v3 was not kept

The v3 review confirmed these defects on synthetic images; details and numbers are in the review file.

- The carrier is unchanged hard-decision QIM at step 4. It loses the payload at noise sigma 2 and after a 3x3 blur, and on four of six hosts at contrast x0.8. The retained real v2 run shows marked and unmarked images indistinguishable after regeneration, and v3 changes nothing in that mechanism.
- The owner tag is recomputed from the binding of the suspect image, so one flipped binding bit rejects a genuine mark. This is the avalanche that amendment v2 set out to remove.
- The binding reads at most 64 block means through public index arithmetic. A keyless attacker can force a recipient to the donor's binding and transplant the publicly readable payload; the reviewers' probes had such forgeries accepted as authentic.
- The decision is one boolean. The proposal's three states cannot be produced, and a copied mark is indistinguishable from a wrong owner.
- The thresholds 0.75 / 0.75 / 0.65 have no stated false-positive rate; accepting 48 of 64 tag bits gives a forgery probability of about 3.9e-5.
- v3 is keyed-only; the proposal's public-derived profile survives only in the untouched v2 file, and no decision record covers the change.

## Method

Phases 1 and 3 follow the proposal's phases (inputs/proposal-text.md lines 194-216). Phase 2 below is not the proposal's latent embedding; it is the image-domain substitute used as comparator. Symbols follow [notation.csv](notation.csv) except that the perceptual hash is written `H` (there `H_p`) and the correlation score is written `z` (there `z` is the latent state).

### Shared definitions

Text fields are UTF-8; a string secret is its UTF-8 bytes. `pack(f1, f2, ...)` is each byte field preceded by its 4-byte big-endian length. `stream(K, label, n)` is the first `n` bytes of `HMAC-SHA256(K, pack("rw-v4", config, label, uint32be(i)))` for `i = 0, 1, ...`.

`config` is the 32-byte `detector_config_id`: SHA-256 of the ASCII bytes `rw-v4/config/r2/` followed by the canonical JSON (sorted keys, compact separators, ASCII) of the profile fields `schema_version`, `profile`, `security`, `semantic_source`, `minimum_side`, `semantic_frequencies`, `instance_frequencies`, `code_bits`, `tag_bits`. The constant fields are `schema_version = "revised-watermark-v4"`, `profile = "image-domain-dual-key-dct-iss"`, `code_bits = 32`, `tag_bits = 128`; `security` is `public-derived` or `hmac-keyed`; frequency positions are JSON arrays `[u, v]`. Embedding strength and decision thresholds are not part of the identifier: the detector needs neither. The thresholds have their own `decision_id`: SHA-256 of the ASCII bytes `rw-v4/decision/` followed by the canonical JSON of the profile's `decision` object, with numbers written as Python's `json` module writes them (`1e-06` for the default `false_positive_target`).

The key `K` is `SHA-256("rw-v4/public-derived-profile-key")` when `security` is `public-derived` and the caller's 16 to 4096 byte secret when it is `hmac-keyed`.

The input is a luminance matrix in [0, 255] with both sides at least `minimum_side` (160 or more). Only complete 8x8 blocks from the top-left origin are used. A right or bottom remainder of up to seven pixels carries no mark and is not read by the hash or the carrier; its values are range-checked, its size enters the carrier through the image dimensions, and when the output is rounded to bytes it is rounded like the rest of the image. The luminance of an RGB pixel is `0.299 R + 0.587 G + 0.114 B` without gamma linearisation. `M` is the map of block means. `C[b, u, v]` is the orthonormal 8x8 DCT-II coefficient of block `b` (row-major), with `u` the vertical and `v` the horizontal frequency index.

Area resampling of a map to `n x n` is the exact area-weighted average of the source cells overlapped by each target cell, in both directions, also when the target is larger than the source.

A **sign projection** of a vector `x` of length `n` with label `L` is 32 bits. The Rademacher matrix is read from `stream(K, pack(L, uint32be(n)), 32 * ceil(n/8))`: row `j` is bytes `j*ceil(n/8)` to `(j+1)*ceil(n/8) - 1`, and entry `k` of a row is bit `k mod 8`, least significant first, of byte `k div 8`; bit 1 means -1. Bit `j` of the code is 1 iff `sum_k r[j,k] * x[k] > 1e-9`. The code is assembled most significant bit first.

### Phase 1: dual signature

- **Perceptual hash `H` (METHOD-03).** `H` is the sign projection, label `perceptual-projection`, of a vector with two parts.
  - *Coarse part.* Area-resample `M` to 32x32. Take its orthonormal 2-D DCT-II and keep the 63 coefficients with `u, v < 8` except DC, ordered by `(u+v, u, v)`. Multiply each by `sqrt(u^2 + v^2)`. This is the input of the classic pHash. Divide the part by its Euclidean norm and multiply by `sqrt(0.25)`.
  - *Detail part.* For each of the positions (0,1) and (1,0), in that order, form the map of `C[b, u, v]` over blocks. Subtract from every entry the mean of its 3x3 neighbourhood, centre included, edges replicated. Map the result `g` to `sign(g) * a / (a + 8)` with `a = max(0, |g| - 6)`. Append the two maps in row-major order, `N` entries in all. Divide the part by `max(norm, 0.4 * sqrt(N))` and multiply by `sqrt(0.75)`.
  - A part whose norm is below 1e-9 is zero. The vector is the coarse part followed by the detail part.

  The detail part is what the proposal asks of `H`: it is meant to separate two images that share a composition, which the low band of a 32x32 map cannot do. The floor `0.4 * sqrt(N)` matters on smooth images. There almost no entry exceeds the dead zone; without the floor the few that do would be scaled up to three quarters of the vector and the hash would be decided by noise. With the floor a smooth image is hashed mainly by its coarse part. Positions (0,1) and (1,0) are reserved for the hash and may not appear in a channel's coefficient set.
- **Semantic code `q` (METHOD-02).** `q` is the sign projection, label `semantic-projection`, of the semantic vector `E` divided by its largest absolute entry. In a profile with `semantic_source = "external:<id>"` the caller supplies `E` (16 to 65536 finite entries, the largest absolute entry at least 1e-12); the study profile uses the pinned CLIP ViT-B/32 image embedding. In `proxy-layout-v1` the vector is `M` area-resampled to 8x8, read row-major, with its mean removed. That proxy is a coarse-layout descriptor for model-free tests. It is not CLIP and carries no semantic meaning.
- **Keys (METHOD-04, METHOD-05).** `Ws = stream(K, pack("ws", OwnerID, q), 16)` and `Wi = stream(K, pack("wi", OwnerID, q, H), 16)`, each read as 128 bits, most significant bit of each byte first. OwnerID is NFC-normalised UTF-8, 1 to 256 bytes; `q` and `H` are 4-byte big-endian.

Sign projections replace hashing of the raw codes on purpose. Two inputs at angle `theta` differ in each bit with probability approximately `theta/pi` (random-hyperplane hashing; exact for Gaussian hyperplanes, approximate for the Rademacher rows used here when the vectors are dense). A small change in content therefore moves few bits and codes can be compared by Hamming distance. `Ws` and `Wi` are still exact functions of the codes; the tolerance comes from the helper data below, not from weakening the keys.

`H` and the proxy `q` read only block means and the two reserved positions, none of which the embedder changes, so an image and its marked version have the same codes up to rounding and clipping. With an external encoder that invariance is not guaranteed and must be measured.

### Phase 2 (image-domain arm): embedding

Two channels use disjoint coefficient sets, both configurable in the profile:

```text
semantic  F_s = [(1,1), (0,2), (2,0), (1,2), (2,1), (2,2)]
instance  F_i = [(0,3), (3,0), (1,3), (3,1), (2,3), (3,2)]
```

Each channel carries 320 bits: 192 helper chips followed by the 128 key bits (`Ws` on the semantic channel, `Wi` on the instance channel). The helper chips encode the 32-bit code of that channel (`q` or `H`) plus a 4-bit CRC. The CRC is the remainder of `code * x^4` divided by x^4+x+1 over GF(2): the register starts at zero, takes the code most significant bit first and has no final XOR, so the CRC of the code 1 is 3. The 36-bit word `code * 16 + CRC` is cut, most significant first, into six 6-bit symbols; in each symbol the top bit is `s` and the low five bits are `i`. A symbol becomes the 32 chips `s XOR parity(i AND k)` for `k = 0..31`: the biorthogonal Reed-Muller code RM(1,5). The codes travel in the mark in clear, protected only by this code; this is not a fuzzy commitment and hides nothing from a party who can compute the carrier.

**Carrier.** For channel `c`, where `c` is the single ASCII byte `s` (semantic) or `i` (instance), list the slots block by block (row-major) and, within a block, in the order of `F_c`. Draw one 8-byte big-endian word per slot from `stream(K, pack("carrier", c, OwnerID, uint32be(height), uint32be(width)), 8 * slots)`, where height and width are the full image dimensions in pixels. Sort slots by `(word >> 1, slot index)`; the slot at rank `r` carries channel bit `r mod 320`. Its sign is +1 if the word is odd, else -1. The **projection** of bit `b` is `p[b] = sum(sign * C) / sqrt(count_b)` over its slots. A channel needs at least 1280 slots. The carrier depends on the key and the owner, so different owners use nearly orthogonal directions. It is the same for all images of one size, key and owner.

**Improved spread spectrum.** Let `e[b]` be +1 for bit 0 and -1 for bit 1. The embedder moves every projection from its host value `p` to

```text
p* = (1 - lambda) * p + A * e
```

by adding `(p* - p) / sqrt(count_b) * sign` to each slot of the bit. The target distortion is `MSE = 255^2 / 10^(target_psnr_db/10)` per pixel over the whole image; when the output is rounded to bytes, by the luminance embedder or by `embed_rgb`, 1/12 is subtracted first, because rounding spends that much by itself (never leaving less than a quarter of the target). Channel `c` gets the share `semantic_energy_share` (semantic) or its complement (instance), and its per-bit budget is `D = MSE * height * width * share_c / 320`. `S` is the mean of the 320 squared host projections of the channel. `lambda` is the smallest value in {0, 0.01, ..., 1} with `D - lambda^2 S > 0` that maximises `(D - lambda^2 S) / ((1 - lambda)^2 S + design_noise_std^2)`, and `A = sqrt(D - lambda^2 S)`. The luminance embedder rounds and clips its output to [0, 255] inside the loop; `embed_rgb` only clips the luminance inside the loop and rounds the three channels afterwards, so the later passes do not correct its rounding. The loop runs `passes` times against the same targets; the later passes matter only where clipping removed part of the change. The cost `A^2 + lambda^2 S` is an average over the key pattern: for one image, key and owner the realised PSNR scatters around the target by a few tenths of a dB (41.82 to 42.32 dB over twelve key and owner pairs on one synthetic host; 41.65 to 42.37 dB on the twelve photographs of the revision-1 run).

**Self-verification.** The embedder runs the real detector on its output. If the outcome is not `both_match` it raises `EmbeddingError` carrying the full report (or returns it with `strict=False`). A mark that cannot be verified is a recorded embedding failure, never a silently weak mark. With an external encoder the embedder verifies with the semantic vector of the source image, because it cannot run the encoder. The report then carries `verification_features = source-features-supplied-by-caller`, and the mark counts as verified only after the caller repeats detection with the vector recomputed from the saved marked image.

`projection_targets()` exports the slots, signs, host projections and targets, planned with the budget that byte rounding leaves. Any embedder that drives the projections of its output to those targets is read by this detector. That is the interface a diffusion-latent embedder would need to be read by the same detector; no such embedder exists in this amendment (see deviation 13).

### Phase 3: detection

Inputs: the suspect image, the claimed OwnerID, the profile, the secret key when `security` is `hmac-keyed`, and `E(J)` in an external-encoder profile. No original image, enrolment record, prompt or seed.

The detector rejects, with an error rather than an outcome: an image smaller than `minimum_side` or with rows of unequal length; a value outside [0, 255]; a profile that fails validation; a secret outside 16 to 4096 bytes; an external vector with fewer than 16 or more than 65536 entries, a non-finite entry or a largest absolute entry below 1e-12; a vector supplied in `proxy-layout-v1` or missing in an external profile; a missing or unwanted key; an OwnerID outside 1 to 256 bytes; a roster size outside 1 to 1,000,000; an unknown `binding_mode`; and a configuration that differs from the caller's `expected_config_id`. These raise `ValueError`; an argument of the wrong type raises `TypeError`. A harness must record such inputs as not evaluable and count them separately. In `proxy-layout-v1` a suspect image whose 8x8 layout is constant (every mean-removed entry below 1e-9 in absolute value) is not an error: its semantic code is the all-zero code. The embedder does reject such an image, because there is nothing to bind.

1. Compute `q(J)` and `H(J)`, the block DCT, and the 320 projections of each channel.
2. Decode the helper chips of each channel by soft maximum-likelihood decoding to obtain the carried codes `q^` and `H^`. Per symbol, take the Walsh-Hadamard transform `t[i] = sum_k (-1)^parity(i AND k) * p[k]` of its 32 projections. If the largest `|t[i]|` is at most 1e-6 the symbol is an erasure and decodes to symbol 0. Otherwise every `i` whose `|t[i]|` lies within `max(1e-9 * largest, 1e-9)` of the largest counts as tied, the lowest such `i` wins, and `s = 1` iff `t[i] < 0`. The tolerances are there so that the decoded code does not follow the floating-point summation order of an implementation: projections of a mark are several luminance units, rounding residue about 1e-12. Computed in four numerically different ways, the detector decoded the same codes on all 900 detections of a reviewer's tie-prone images and, in the author's re-run of that reviewer's near-flat probe with the absolute floor, on all 71 image cases, where 24 had disagreed without the floor. Scores of near-flat images, whose band energy is close to zero, can still differ beyond 1e-9 between implementations; no outcome was affected. The CRC is not a gate. The decoded code is used as a candidate whenever it differs from the recomputed code, whether or not its CRC verifies. `helper_check_ok` is a report field: true when the CRC of the decoded word verifies and no symbol was an erasure. An unmarked image therefore normally has two semantic and four instance candidates.
3. **Semantic key.** Candidates are `Ws(q(J))` ("recomputed", the proposal's route) and, if different, `Ws(q^)` ("decoded"). For each, compute

   ```text
   z = sum(e[b] * p[b]) / sqrt(sum(p[b]^2))        over the 128 key bits
   ```

   If `sqrt(sum(p[b]^2))` is at most 1e-6, the image has no energy in the band and `z` is 0. Keep the larger score; on equal scores the recomputed candidate wins. The key is **found** if `z >= sqrt(2 ln(m R / alpha))`, where `m` is the number of candidates, `R` the roster size and `alpha` the profile's `false_positive_target`.
4. **Instance key.** The same test with `Wi(q, H)` over `q` in {the code that verified `Ws`, or both candidates if none did} and `H` in {`H(J)`, `H^`}. Candidates are ordered `q` recomputed before decoded, then `H` recomputed before decoded, and the first of equal scores wins. The reported `candidate` of the instance key names the source of `H` only; `candidate` is null for a key that was not found.
5. **Content status.** For each key that was found, take the Hamming distance `d` between the code that verified it and the code recomputed from the suspect image. The status is `match` if `d <= radius`, `mismatch` if `d >= mismatch_distance`, and `uncertain` in between. The semantic comparison uses `semantic_radius` and `semantic_mismatch_distance`. For the instance key, the `H` comparison uses `instance_radius` and `instance_mismatch_distance`, its `q` comparison uses the semantic pair, and its status is the worse of the two. The undecided zone exists because heavy but harmless processing moves a few bits of `H`; without it a noisy genuine image would be reported as a transferred mark.

| Semantic key | Instance key | `outcome` | `proposal_state` |
| --- | --- | --- | --- |
| not found | not found | `neither_match` | `not_detected` |
| any found key has status `mismatch` | | `content_mismatch` | `copy_paste` |
| found, `match` | found, `match` | `both_match` | `authentic` |
| found, `match` | not found | `semantic_only` | `regenerated` |
| not found | found, `match` | `instance_only` | `unclassified` |
| any other combination: a found key is `uncertain` | | `content_uncertain` | `unclassified` |

Rows are applied top to bottom.

`outcome` is the observation. `proposal_state` maps three outcomes to the labels of the proposal's decision table (lines 212-214): `both_match` to authentic, `semantic_only` to regenerated, `content_mismatch` to copy-paste. `not_detected` and `unclassified` are additions of this amendment; `not_detected` means only that no key of the claimed owner and profile reached its threshold, which is also what a wrong owner, a wrong key or a weakened mark gives. Neither field is ground truth: whether an image was regenerated or forged is known only from attack provenance, and the evaluation must score these labels against that provenance (SC-03).

`content_mismatch` and `content_uncertain` are new relative to io-spec.md. The first is a candidate presence witness for IO-06: a key that verifies through the codes carried in the mark does not depend on the current content, so "a mark of this owner is present but bound to other content" becomes observable and distinct from "no mark". Its error rates in both directions are unmeasured on real data. The second is an explicit abstention, which the proposal's three-state table does not define.

`binding_mode` selects the content comparisons for the C6 ablations. `semantic_only` keeps the `q` comparisons and skips the `H` comparison; `perceptual_only` keeps only the `H` comparison; `none` skips both and is the binding-disabled control. A skipped comparison is reported as `unchecked` and treated as a match. When one of the instance key's two comparisons is skipped and the other matches, the reported status is that of the `H` comparison: `unchecked` under `semantic_only`, `match` under `perceptual_only`.

## Statistical basis

For fixed projections `p` and a pattern `e` of independent fair signs, Hoeffding's inequality gives `P(z >= t) <= exp(-t^2 / 2)`. The probability is taken over the pseudorandom pattern, that is over keys, OwnerIDs and codes, for a fixed image. It is not a rate over images at one fixed key and owner. The bound needs the pattern to be independent of the projections it is tested against. That holds under the PRF assumption for an unmarked image, a wrong owner, a wrong key, and a mark made for different codes, because the tested pattern is then an HMAC output over an input unrelated to those projections. Helper chips and key bits occupy disjoint slots, so choosing the decoded candidate does not use the key projections. In the public-derived profile the key is published, so the argument rests on HMAC behaving as a random function of its input and on the image not having been constructed with the public derivation; re-embedding (T6) is outside it.

The threshold is therefore derived, not tuned: `alpha = 1e-6` with one candidate gives 5.26, with two candidates 5.39, with four 5.51, and the maximum attainable score is `sqrt(128) = 11.31`. A profile may set `alpha` between 1e-20 and 1e-2 and a roster may hold up to 1e6 owners, which keeps every threshold below that maximum. `alpha` applies to each channel separately. For an unmarked image the probability that either key is found, and so of any outcome other than `neither_match`, is at most `2 alpha` per tested owner. The result reports `log10_false_positive_bound` for the observed score, the number of candidates, and the roster size. `identify()` tries a roster and applies the correction; a caller who loops `detect()` over owners must pass `roster_size`.

Four limits apply. The bound is conservative: in the reviewers' null probes the scores followed the normal tail, which at 5.26 is about 7e-8. Validation sets of a few hundred negatives can show the absence of gross violations but cannot confirm a rate near 1e-6; that figure remains an analytic bound. The content distances (match up to 6, mismatch from 10, of 32 bits) are engineering defaults; for independent uniform codes `P(distance <= 6) = 2.7e-4` and `P(distance <= 9) = 1.0e-2`, but real codes are neither independent nor uniform, so collision rates must be measured (T5). And every default in `decision` is uncalibrated until A4 freezes it on validation data.

## Profiles and threat coverage

| Profile | Secret | What it gives |
| --- | --- | --- |
| `public-derived` (default; the proposal's key model) | none | Every code, key and carrier is computable by anyone. Re-embedding for any OwnerID (T6) is possible by design, and a mark can be subtracted. Detection shows a public-profile mark bound to this content, not who placed it. |
| `hmac-keyed` (keyed variant) | 16+ bytes | A party without the key cannot derive the carrier, the projection directions or the keys, and cannot create a fresh mark or run the detector. It can still move an existing mark (T4, T5) and can estimate the carrier from several marked images of one owner and size (T2). Any key holder can mark any image for any OwnerID, so a keyed detection attributes the mark to the key-holding operator, not to the named owner. A leaked key enables forgery. |

Results of the two profiles are never pooled. The keyed variant changes the detector's knowledge profile (io-spec.md, `secret_ref`), has no research contract yet, and needs its own wrong-key control (C3) and table; until then its results are engineering diagnostics. Keys should be random and at least 128 bits; nothing else protects a keyed profile against guessing. Detection results carry no key fingerprint; `key_fingerprint()` computes a deliberately slow one on request (the first 16 hex digits of PBKDF2-HMAC-SHA256 of the key with salt `rw-v4/fingerprint` and 200,000 iterations). Results do carry `semantic_code` and `perceptual_hash`, which in the keyed profile are keyed functions of the image, and any marked image lets a guess be tested by running the detector, so a weak key can be tested offline by anyone who holds a marked image or a published result. Both shipped profiles use the `proxy-layout-v1` stand-in for the semantic vector (deviation 15).

| Threat | What v4 does | What is not claimed, and what is known to fail |
| --- | --- | --- |
| T4 copy-paste | A mark moved onto an unrelated image by replacing the band, by a residual copy or by a patch of a quarter of the image either fails to verify or verifies through its carried codes and is reported as `content_mismatch`. | The content codes are functions of the pixels. An attacker who also copies or imitates the features the hash reads makes the codes match, **in either profile and without the key**: the key hides the projection directions, not the features. On an unrelated recipient this costs about 17 to 28 dB against the recipient in the reviewers' probes, which amounts to importing the donor's coarse layout. Copying only the semantic band is flagged unless the two semantic codes lie closer than the mismatch distance: with the layout proxy 0.23% of unrelated synthetic pairs lie within the radius (independent codes: 0.027%), where the result reads `semantic_only` at about 36 dB, and a further 2.6% lie in the undecided zone, where it reads `content_uncertain`. Large patches and blends are sometimes accepted; the scheme is not a tamper detector. No real-image measurement exists. |
| T5 semantic collision | The instance key binds `H` in addition to `q`. For most pairs of images of one composition a plain transplant is reported as `content_mismatch` or `content_uncertain`; the `semantic_only` ablation accepts every one. | Three failures are known on synthetic same-composition families. A pair whose hashes lie within the instance radius is accepted as authentic after a plain transplant (11 of 288 trials in the verification of revision 2). An informed attacker who also copies or edits the recipient's (0,1) and (1,0) coefficients is accepted as authentic without the key at 24 to 36 dB against the recipient, depending on the texture of the composition; on weakly textured families the forgery sits at about 36 dB, above the proposal's 35 dB level. And copying the semantic band alone yields `semantic_only`, the "regenerated" label, at 26 to 38 dB, with no other edit. Whether real same-subject photographs have distinct `H` and equal `q` under CLIP is unmeasured (HYP-01 stays open). |
| T3 regeneration | The correlation score is invariant to gain and degrades gradually instead of failing at a noise cliff. `semantic_only` is a reachable outcome. | Survival of real diffusion regeneration. The cited benchmarks lead us to expect that the image-domain arm fails at the strengths used in the retained run. Benign blur, noise and requantisation also produce `semantic_only`, so that outcome indicates a degraded or transferred mark and does not identify regeneration. The order in which the keys fail is host-dependent: on smooth hosts the semantic key outlasts the instance key, on textured hosts it has the smaller margin. |
| T1 benign processing | Keeps both keys under the synthetic noise, contrast, blur and requantisation levels reported as fully authentic in the tables below. | Crop, resize, rotation and pixel shift: the carrier is tied to the image size in pixels and to a fixed block grid, so removing even an unmarked border strip destroys detection. The perceptual hash is not gain-invariant, because its dead zone and knee are absolute: strong contrast reduction moves a genuine image to `content_uncertain` (29 of 450 rows at contrast x0.5) or `content_mismatch` (6 of 450). Additive noise gives genuine images the `content_mismatch` label: in the verification of revision 2 it appeared on 1 of 450 rows at sigma 5, on 23.5% of plain-host and 3.7% of textured-host rows at sigma 10 (the textured cases all at the weakest texture), and on 51% and 12.5% at sigma 20. The undecided zone reduces this label and does not remove it. |
| T2 removal | In the keyed variant a party without the key cannot derive the carrier; with a single marked image it has to disturb the band as a whole, with many it can estimate the carrier. Neither was tested as a removal attack. | Resistance to removal. In the public profile the carrier is computable and the mark can be subtracted. The carrier is reused across an owner's images of one size; the reviewers recovered most of it from 64 marked plain images, which lowers the distortion of a transplant to embedding level. |
| T6 re-embedding | Not possible through the public derivation for a party without the key, under the PRF assumption for HMAC-SHA256 and key secrecy; only a wrong-key control was tested. | Anything in the public profile. |
| T7 oracle or white-box | None. | Scores must not be exposed to untrusted callers; a detector oracle allows hill-climbing. |

Competing claims are not resolved. An adversary can search for an (OwnerID, key) pair whose patterns happen to pass on a given image; the work per channel is at least `1 / alpha` detections and at least `1 / alpha^2` for both channels, and under a normal approximation about 1.4e7 and 2e14 at the defaults. Resolving such claims needs key commitment or enrolment, which the scope guard excludes from the required implementation (SC-01, SC-04).

## Traceability to the proposal

| Claim ID | v4 status |
| --- | --- |
| TITLE-FA, TITLE-EN, SCOPE-01, GOAL-01 | Untouched. |
| SCOPE-02, SCOPE-03, DATA-01..03 | Untouched and open. |
| PROB-01 copy-paste | Mechanism only; see T4, including the known failures. |
| PROB-02 regeneration | Open. The pixel arm is expected to fail; see T3. |
| PROB-03 semantic collision | Mechanism only, with synthetic collision data and known failures; see T5. |
| METHOD-01 three phases | Phases 1 and 3 implemented in the image domain; phase 2 open. |
| METHOD-02 semantic vector | Interface only: sign projection of a supplied vector. CLIP stays outside the codec; the proxy is not CLIP. |
| METHOD-03 DCT pHash | Implemented as sign projections of block-DCT content at two scales (keyed in the hmac-keyed variant, public in the default profile): the classic low-band input plus block-gradient detail. |
| METHOD-04, METHOD-05 dual keys | Implemented, 128 bits each. |
| METHOD-06 latent embedding | **Open.** Not implemented; only the target-projection interface exists. |
| METHOD-07 recompute candidate keys | Implemented; a second candidate from carried codes is an addition. |
| METHOD-08 8x8 mid-band correlation | Implemented with a declared band deviation: the semantic channel uses the lowest AC positions after the two reserved for the hash, not the mid band; the instance channel is low to mid band. |
| METHOD-09 decision states | Implemented as observations plus decision-table labels, with two added outcomes and one declared mapping deviation (deviation 12). |
| OBJ-01, RQ-01, HYP-01 | Mechanism implemented; the empirical claim is open (needs CLIP and real same-subject pairs). |
| OBJ-02, RQ-02, HYP-02, METRIC-05 latent arm | **Open.** v4 can only be the pixel arm. |
| OBJ-03, RQ-03, HYP-03, METRIC-07, CLAIM-01 | Detector and per-stage timing fields exist. Comparators (neural decoder, inversion-based) and any cost comparison are open; pure-Python timings are not the efficiency evidence. |
| OBJ-04, RQ-04, HYP-04, METRIC-06 | Mechanism and continuous scores (`z`, code distances) exist for ROC/AUC; no real evaluation. |
| METRIC-01..03 | PSNR helper only; SSIM and LPIPS stay in the evaluation harness. No quality target is claimed as met. |
| METRIC-04 | Supplementary; synthetic stand-ins only. Crop is expected to fail by design. |
| NOVELTY-01 | No novelty is claimed for v4; its components are standard. |

## Additions and deviations

Each is a method choice to be validated, not a result. Cost and schedule consequences have not been assessed. Adoption as comparator is the user's decision; deviations 3, 4, 7, 12 and 14 change how the proposal's method is read and are for the supervisor. Issue: #18.

1. **Helper data.** The codes `q` and `H` travel in the mark, protected by RM(1,5). The proposal recomputes candidate keys from the suspect image only. The addition tolerates a few drifted code bits where the key score is high, replaces the 13 x 33 candidate enumeration of method-spec.md with at most two and four candidates, and supplies the candidate presence witness of IO-06. Its limit: each helper symbol integrates 32 projections against 128 for a key, so at key scores near the threshold the helper is less reliable than the key test and a drifted code is then often not recovered.
2. **Keyed pseudorandom function.** HMAC-SHA256 replaces plain hashing in both profiles; the public profile uses a published constant as key, which is equivalent to a public hash.
3. **Sign-projection codes and a detail-aware hash.** Random-hyperplane codes replace the median-threshold pHash and the 12-bit projection of method-spec.md, so that in the keyed variant the projection directions, though not the statistics they read, are hidden. The hash input is a block-mean map with area resampling and frequency weighting instead of a bilinear resize, and it adds block-gradient detail. The shares, the dead zone, the knee and the floor are engineering defaults chosen on the synthetic families used in the benchmark, so the benchmark's collision figures are in-sample.
4. **Frequency sets.** Both sets differ from method-spec.md (`F_s = [(1,2),(2,1),(2,2),(1,3)]`, `F_i = [(3,1),(2,3),(3,2),(1,4)]`) and have six positions instead of four: the semantic set gains (1,1), (0,2) and (2,0) and gives (1,3) to the instance set, which also gains (0,3) and (3,0) and loses (1,4). This follows published evidence that editing removes mid and high frequencies first; the sets are validation-selectable and an ablation factor.
5. **Embedding domain.** Image-domain improved spread spectrum instead of latent/noise embedding. This is the proposed pixel comparator, not a replacement.
6. **Colour.** `embed_rgb` adds the luminance change equally to R, G and B, plans with the rounding allowance, and verifies the rounded RGB output. A channel at 0 or 255 cannot take its share, which the report states as `clipped_fraction`.
7. **Detection statistic and thresholds.** The self-normalised projection correlation with thresholds derived from `alpha` replaces method-spec.md's mean-centred cosine score and the validation-selected `tau_s`, `tau_i` of acceptance.md. The A4 threshold grid does not apply to v4 and has to be re-specified.
8. **Key length.** 128 bits instead of 256.
9. **Geometry.** Only complete blocks from the top-left origin and a minimum side of 160; method-spec.md pads by edge replication and accepts 32.
10. **Self-verification with an external encoder** uses the source image's vector, not the vector of the marked output; the caller must repeat it.
11. **Content comparison.** Hamming distance with a match radius and a mismatch distance, and an undecided zone between them.
12. **Decision table.** One mapping differs from the proposal's table: a matching semantic key with a mismatching instance hash is labelled copy-paste, where the proposal's recompute-only detector would see the semantic key alone. In addition `not_detected`, `unclassified`, `content_mismatch` as an outcome of its own, and `content_uncertain` do not exist in the proposal.
13. **Shared detector.** Using v4's detector for a latent arm would change the A5 detector of method-spec.md and needs its own decision; otherwise the two arms are read by different detectors.
14. **Pattern construction.** method-spec.md derives a full-length template from each candidate key. v4 modulates the 128 key bits onto a carrier derived from the profile key, the OwnerID and the image size. The carrier is the same for all of an owner's images of one size, which is what the carrier-estimation attack uses (T2).
15. **Default semantic source.** The shipped profiles use the `proxy-layout-v1` stand-in. The proposal's CLIP vector enters only through an `external:` profile, which no shipped configuration and no synthetic table uses.
16. **Error reporting.** Invalid inputs raise exceptions instead of io-spec.md's `invalid_input` and `unsupported_configuration` outcomes, and results carry no diagnostic reason field; a harness has to map them.

## Engineering evidence (synthetic only)

`unittest discover -s scripts` passes 95 tests with the verified Windows interpreter; 44 belong to v4. They are engineering checks. They include known-answer vectors for Phase 1, the carrier, detection of one unmarked image and one embedding plan with the hash of its marked image; a table of every decision combination; image-level properties repeated over three keys and three scenes, and three tests that pin known failures so they stay visible: the semantic key alone transfers within a composition, an informed transplant within a composition is accepted, and a host-dominated image cannot be marked.

Mutation testing of the final v4 code against the final test module, run by the author: the first reviewers' harness (142 of its 164 mutants still apply), a verifier's re-targeted set (32 of 34 apply) and 16 mutants written for the changes made after the verification, 190 in all. 185 were killed and 5 survived: a comparison no test image reaches, two guards made redundant by other checks, the content checks during self-verification, and a redundant literal hook. They are explained in the verification record.

Every table below was produced by `scripts/bench_revised_watermark_synthetic.py` with one fixed test key per keyed column, one OwnerID, and one noise realisation per host position and distortion row, shared by the four columns and by both host groups (in a column with embedding failures the mapping of hosts to realisations shifts). "42 dB" is the PSNR budget, not a profile. Each cell is `authentic / neither authentic nor flagged / flagged as bound to other content`. For v3 the first number is `present=True`; v3 has no third state. "Textured" hosts have texture amplitudes 6, 12 and 20; "plain" hosts are a low-contrast image, a gradient, three flat tones and smooth waves.

**256x256** (`--hosts 6 --size 256`), six textured hosts:

| Condition | v3 (QIM step 4) | v4 keyed, 42 dB | v4 keyed, PSNR matched to v3 | v4 public-derived, 42 dB |
| --- | --- | --- | --- | --- |
| Embedding failures | 0 | 0 | 2 | 0 |
| Mean PSNR (dB) | 50.44 | 41.98 | 50.37 | 42.05 |
| No distortion | 6 / 0 / 0 | 6 / 0 / 0 | 4 / 0 / 0 | 6 / 0 / 0 |
| Noise sigma 2 | 0 / 6 / 0 | 6 / 0 / 0 | 4 / 0 / 0 | 6 / 0 / 0 |
| Noise sigma 5 | 0 / 6 / 0 | 6 / 0 / 0 | 2 / 2 / 0 | 6 / 0 / 0 |
| Noise sigma 10 | 0 / 6 / 0 | 6 / 0 / 0 | 1 / 3 / 0 | 5 / 1 / 0 |
| Noise sigma 20 | 0 / 6 / 0 | 3 / 2 / 1 | 0 / 4 / 0 | 5 / 1 / 0 |
| Contrast x0.8 | 2 / 4 / 0 | 6 / 0 / 0 | 4 / 0 / 0 | 6 / 0 / 0 |
| Box blur 3x3 | 0 / 6 / 0 | 6 / 0 / 0 | 2 / 2 / 0 | 6 / 0 / 0 |
| Box blur 5x5 | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 4 / 0 | 0 / 6 / 0 |
| Requantise step 8 | 0 / 6 / 0 | 6 / 0 / 0 | 2 / 2 / 0 | 6 / 0 / 0 |
| Requantise step 16 | 0 / 6 / 0 | 6 / 0 / 0 | 1 / 3 / 0 | 6 / 0 / 0 |
| Requantise step 24 | 0 / 6 / 0 | 4 / 2 / 0 | 0 / 4 / 0 | 4 / 2 / 0 |
| Blur 3x3 + noise 4 | 0 / 6 / 0 | 5 / 1 / 0 | 0 / 4 / 0 | 6 / 0 / 0 |
| Blur 5x5 + noise 6 | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 4 / 0 | 0 / 6 / 0 |
| Unmarked source | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 |
| Marked, wrong owner | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 4 / 0 | 0 / 6 / 0 |
| Marked, wrong key | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 4 / 0 | n/a |

256x256, four plain hosts:

| Condition | v3 (QIM step 4) | v4 keyed, 42 dB | v4 keyed, PSNR matched to v3 | v4 public-derived, 42 dB |
| --- | --- | --- | --- | --- |
| Embedding failures | 0 | 0 | 1 | 0 |
| Mean PSNR (dB) | 49.62 | 41.97 | 50.42 | 41.88 |
| No distortion | 1 / 3 / 0 | 4 / 0 / 0 | 3 / 0 / 0 | 4 / 0 / 0 |
| Noise sigma 2 | 0 / 4 / 0 | 4 / 0 / 0 | 3 / 0 / 0 | 4 / 0 / 0 |
| Noise sigma 5 | 0 / 4 / 0 | 4 / 0 / 0 | 3 / 0 / 0 | 4 / 0 / 0 |
| Noise sigma 10 | 0 / 4 / 0 | 0 / 3 / 1 | 0 / 2 / 1 | 1 / 1 / 2 |
| Noise sigma 20 | 0 / 4 / 0 | 0 / 2 / 2 | 0 / 3 / 0 | 1 / 1 / 2 |
| Contrast x0.8 | 1 / 3 / 0 | 4 / 0 / 0 | 3 / 0 / 0 | 4 / 0 / 0 |
| Box blur 3x3 | 0 / 4 / 0 | 4 / 0 / 0 | 3 / 0 / 0 | 4 / 0 / 0 |
| Box blur 5x5 | 0 / 4 / 0 | 1 / 3 / 0 | 0 / 3 / 0 | 2 / 2 / 0 |
| Requantise step 8 | 0 / 4 / 0 | 3 / 1 / 0 | 1 / 2 / 0 | 4 / 0 / 0 |
| Requantise step 16 | 0 / 4 / 0 | 1 / 3 / 0 | 0 / 3 / 0 | 1 / 3 / 0 |
| Requantise step 24 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 3 / 0 | 0 / 4 / 0 |
| Blur 3x3 + noise 4 | 0 / 4 / 0 | 4 / 0 / 0 | 0 / 3 / 0 | 4 / 0 / 0 |
| Blur 5x5 + noise 6 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 3 / 0 | 0 / 4 / 0 |
| Unmarked source | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| Marked, wrong owner | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 3 / 0 | 0 / 4 / 0 |
| Marked, wrong key | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 3 / 0 | n/a |

256x256, outcomes behind the `v4 keyed, 42 dB` column:

| Condition | Textured hosts | Plain hosts |
| --- | --- | --- |
| No distortion | both_match 6 | both_match 4 |
| Noise sigma 2 | both_match 6 | both_match 4 |
| Noise sigma 5 | both_match 6 | both_match 4 |
| Noise sigma 10 | both_match 6 | content_mismatch 1, content_uncertain 3 |
| Noise sigma 20 | both_match 3, content_mismatch 1, content_uncertain 2 | content_mismatch 2, content_uncertain 1, semantic_only 1 |
| Contrast x0.8 | both_match 6 | both_match 4 |
| Box blur 3x3 | both_match 6 | both_match 4 |
| Box blur 5x5 | neither_match 2, semantic_only 4 | both_match 1, semantic_only 3 |
| Requantise step 8 | both_match 6 | both_match 3, semantic_only 1 |
| Requantise step 16 | both_match 6 | both_match 1, neither_match 3 |
| Requantise step 24 | both_match 4, semantic_only 2 | neither_match 4 |
| Blur 3x3 + noise 4 | both_match 5, instance_only 1 | both_match 4 |
| Blur 5x5 + noise 6 | neither_match 3, semantic_only 3 | neither_match 1, semantic_only 3 |

256x256, transfers of a mark onto the next textured host (a different, unmarked image):

| Codec | Transfer | Outcomes | Mean PSNR against the recipient (dB) |
| --- | --- | --- | --- |
| v3 (QIM step 4) | band transplant | payload_readable 6 | 34.8 |
| v3 (QIM step 4) | residual copy | neither_match 6 | 50.4 |
| v4 keyed, 42 dB | band transplant | content_mismatch 6 | 29.8 |
| v4 keyed, 42 dB | residual copy | content_mismatch 4, neither_match 2 | 42.0 |
| v4 keyed, 42 dB | semantic band only | content_mismatch 6 | 30.1 |
| v4 keyed, PSNR matched to v3 | band transplant | content_mismatch 2, neither_match 2 | 30.3 |
| v4 keyed, PSNR matched to v3 | residual copy | neither_match 4 | 50.4 |
| v4 keyed, PSNR matched to v3 | semantic band only | content_mismatch 2, neither_match 2 | 30.6 |
| v4 public-derived, 42 dB | band transplant | content_mismatch 6 | 29.8 |
| v4 public-derived, 42 dB | residual copy | content_mismatch 4, neither_match 2 | 42.1 |
| v4 public-derived, 42 dB | semantic band only | content_mismatch 6 | 30.1 |

| Codec | `binding_mode` | Band transplant outcomes |
| --- | --- | --- |
| v4 keyed, 42 dB | `combined` | content_mismatch 6 |
| v4 keyed, 42 dB | `none` | both_match 6 |
| v4 keyed, 42 dB | `perceptual_only` | content_mismatch 6 |
| v4 keyed, 42 dB | `semantic_only` | content_mismatch 6 |
| v4 keyed, PSNR matched to v3 | `combined` | content_mismatch 2, neither_match 2 |
| v4 keyed, PSNR matched to v3 | `none` | both_match 2, neither_match 2 |
| v4 keyed, PSNR matched to v3 | `perceptual_only` | content_mismatch 2, neither_match 2 |
| v4 keyed, PSNR matched to v3 | `semantic_only` | content_mismatch 2, neither_match 2 |
| v4 public-derived, 42 dB | `combined` | content_mismatch 6 |
| v4 public-derived, 42 dB | `none` | both_match 6 |
| v4 public-derived, 42 dB | `perceptual_only` | content_mismatch 6 |
| v4 public-derived, 42 dB | `semantic_only` | content_mismatch 6 |

256x256, distinct images of one composition (keyed, layout proxy; pairs of hashes within the instance radius or in the undecided zone, for two keys; then marks moved from each of up to twelve images onto the next):

| Family | Pairs | Within radius, key 1 | Undecided, key 1 | Within radius, key 2 | Undecided, key 2 | Band transplant to the next image | Semantic band only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| object on flat background | 780 | 11 | 103 | 6 | 68 | content_mismatch 10, content_uncertain 2 | semantic_only 12 |
| same structure, texture 14 | 780 | 12 | 120 | 3 | 58 | content_mismatch 8, content_uncertain 4 | semantic_only 12 |
| same structure, texture 6 | 780 | 26 | 193 | 10 | 109 | content_mismatch 8, content_uncertain 4 | semantic_only 12 |
| unrelated scenes | 780 | 0 | 11 | 0 | 7 | content_mismatch 12 | content_mismatch 12 |

**512x512** (`--hosts 6 --size 512 --family 24`), six textured hosts:

| Condition | v3 (QIM step 4) | v4 keyed, 42 dB | v4 keyed, PSNR matched to v3 | v4 public-derived, 42 dB |
| --- | --- | --- | --- | --- |
| Embedding failures | 0 | 0 | 0 | 0 |
| Mean PSNR (dB) | 50.49 | 41.96 | 50.48 | 42.05 |
| No distortion | 6 / 0 / 0 | 6 / 0 / 0 | 6 / 0 / 0 | 6 / 0 / 0 |
| Noise sigma 2 | 0 / 6 / 0 | 6 / 0 / 0 | 6 / 0 / 0 | 6 / 0 / 0 |
| Noise sigma 5 | 0 / 6 / 0 | 6 / 0 / 0 | 6 / 0 / 0 | 6 / 0 / 0 |
| Noise sigma 10 | 0 / 6 / 0 | 6 / 0 / 0 | 6 / 0 / 0 | 5 / 1 / 0 |
| Noise sigma 20 | 0 / 6 / 0 | 4 / 1 / 1 | 0 / 6 / 0 | 4 / 1 / 1 |
| Contrast x0.8 | 2 / 4 / 0 | 6 / 0 / 0 | 6 / 0 / 0 | 6 / 0 / 0 |
| Box blur 3x3 | 0 / 6 / 0 | 6 / 0 / 0 | 4 / 2 / 0 | 6 / 0 / 0 |
| Box blur 5x5 | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 |
| Requantise step 8 | 0 / 6 / 0 | 6 / 0 / 0 | 6 / 0 / 0 | 6 / 0 / 0 |
| Requantise step 16 | 0 / 6 / 0 | 5 / 1 / 0 | 5 / 1 / 0 | 6 / 0 / 0 |
| Requantise step 24 | 0 / 6 / 0 | 4 / 2 / 0 | 3 / 3 / 0 | 6 / 0 / 0 |
| Blur 3x3 + noise 4 | 0 / 6 / 0 | 6 / 0 / 0 | 4 / 2 / 0 | 6 / 0 / 0 |
| Blur 5x5 + noise 6 | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 |
| Unmarked source | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 |
| Marked, wrong owner | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 |
| Marked, wrong key | 0 / 6 / 0 | 0 / 6 / 0 | 0 / 6 / 0 | n/a |

512x512, four plain hosts:

| Condition | v3 (QIM step 4) | v4 keyed, 42 dB | v4 keyed, PSNR matched to v3 | v4 public-derived, 42 dB |
| --- | --- | --- | --- | --- |
| Embedding failures | 0 | 0 | 0 | 0 |
| Mean PSNR (dB) | 49.83 | 41.87 | 50.70 | 41.87 |
| No distortion | 1 / 3 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| Noise sigma 2 | 0 / 4 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| Noise sigma 5 | 0 / 4 / 0 | 3 / 1 / 0 | 3 / 1 / 0 | 3 / 1 / 0 |
| Noise sigma 10 | 0 / 4 / 0 | 1 / 3 / 0 | 1 / 3 / 0 | 4 / 0 / 0 |
| Noise sigma 20 | 0 / 4 / 0 | 0 / 1 / 3 | 0 / 4 / 0 | 0 / 4 / 0 |
| Contrast x0.8 | 1 / 3 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| Box blur 3x3 | 0 / 4 / 0 | 4 / 0 / 0 | 3 / 1 / 0 | 4 / 0 / 0 |
| Box blur 5x5 | 0 / 4 / 0 | 2 / 2 / 0 | 1 / 3 / 0 | 2 / 2 / 0 |
| Requantise step 8 | 0 / 4 / 0 | 4 / 0 / 0 | 1 / 3 / 0 | 4 / 0 / 0 |
| Requantise step 16 | 0 / 4 / 0 | 1 / 3 / 0 | 1 / 3 / 0 | 0 / 4 / 0 |
| Requantise step 24 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 1 / 3 / 0 |
| Blur 3x3 + noise 4 | 0 / 4 / 0 | 4 / 0 / 0 | 3 / 1 / 0 | 4 / 0 / 0 |
| Blur 5x5 + noise 6 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| Unmarked source | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| Marked, wrong owner | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| Marked, wrong key | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | n/a |

512x512, outcomes behind the `v4 keyed, 42 dB` column:

| Condition | Textured hosts | Plain hosts |
| --- | --- | --- |
| No distortion | both_match 6 | both_match 4 |
| Noise sigma 2 | both_match 6 | both_match 4 |
| Noise sigma 5 | both_match 6 | both_match 3, content_uncertain 1 |
| Noise sigma 10 | both_match 6 | both_match 1, content_uncertain 3 |
| Noise sigma 20 | both_match 4, content_mismatch 1, content_uncertain 1 | content_mismatch 3, content_uncertain 1 |
| Contrast x0.8 | both_match 6 | both_match 4 |
| Box blur 3x3 | both_match 6 | both_match 4 |
| Box blur 5x5 | semantic_only 6 | both_match 2, semantic_only 2 |
| Requantise step 8 | both_match 6 | both_match 4 |
| Requantise step 16 | both_match 5, content_uncertain 1 | both_match 1, neither_match 2, semantic_only 1 |
| Requantise step 24 | both_match 4, content_uncertain 2 | content_uncertain 1, neither_match 3 |
| Blur 3x3 + noise 4 | both_match 6 | both_match 4 |
| Blur 5x5 + noise 6 | semantic_only 6 | semantic_only 4 |

512x512, transfers of a mark onto the next textured host (a different, unmarked image):

| Codec | Transfer | Outcomes | Mean PSNR against the recipient (dB) |
| --- | --- | --- | --- |
| v3 (QIM step 4) | band transplant | payload_readable 6 | 34.8 |
| v3 (QIM step 4) | residual copy | neither_match 6 | 50.5 |
| v4 keyed, 42 dB | band transplant | content_mismatch 6 | 29.6 |
| v4 keyed, 42 dB | residual copy | content_mismatch 6 | 42.0 |
| v4 keyed, 42 dB | semantic band only | content_mismatch 6 | 29.9 |
| v4 keyed, PSNR matched to v3 | band transplant | content_mismatch 4, neither_match 2 | 29.8 |
| v4 keyed, PSNR matched to v3 | residual copy | content_mismatch 4, neither_match 2 | 50.5 |
| v4 keyed, PSNR matched to v3 | semantic band only | content_mismatch 4, neither_match 2 | 30.1 |
| v4 public-derived, 42 dB | band transplant | content_mismatch 6 | 29.6 |
| v4 public-derived, 42 dB | residual copy | content_mismatch 6 | 42.1 |
| v4 public-derived, 42 dB | semantic band only | content_mismatch 6 | 29.9 |

| Codec | `binding_mode` | Band transplant outcomes |
| --- | --- | --- |
| v4 keyed, 42 dB | `combined` | content_mismatch 6 |
| v4 keyed, 42 dB | `none` | both_match 6 |
| v4 keyed, 42 dB | `perceptual_only` | content_mismatch 6 |
| v4 keyed, 42 dB | `semantic_only` | content_mismatch 6 |
| v4 keyed, PSNR matched to v3 | `combined` | content_mismatch 4, neither_match 2 |
| v4 keyed, PSNR matched to v3 | `none` | both_match 4, neither_match 2 |
| v4 keyed, PSNR matched to v3 | `perceptual_only` | content_mismatch 4, neither_match 2 |
| v4 keyed, PSNR matched to v3 | `semantic_only` | content_mismatch 4, neither_match 2 |
| v4 public-derived, 42 dB | `combined` | content_mismatch 6 |
| v4 public-derived, 42 dB | `none` | both_match 6 |
| v4 public-derived, 42 dB | `perceptual_only` | content_mismatch 6 |
| v4 public-derived, 42 dB | `semantic_only` | content_mismatch 6 |

512x512, distinct images of one composition (keyed, layout proxy; pairs of hashes within the instance radius or in the undecided zone, for two keys; then marks moved from each of up to twelve images onto the next):

| Family | Pairs | Within radius, key 1 | Undecided, key 1 | Within radius, key 2 | Undecided, key 2 | Band transplant to the next image | Semantic band only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| object on flat background | 276 | 6 | 64 | 3 | 43 | content_mismatch 8, content_uncertain 4 | semantic_only 12 |
| same structure, texture 14 | 276 | 2 | 15 | 2 | 32 | content_mismatch 10, content_uncertain 2 | semantic_only 12 |
| same structure, texture 6 | 276 | 7 | 61 | 2 | 51 | content_mismatch 8, content_uncertain 4 | semantic_only 12 |
| unrelated scenes | 276 | 0 | 4 | 1 | 2 | content_mismatch 12 | content_mismatch 12 |

Reading the tables:

- **512x512, 42 dB, textured hosts.** The keyed column is authentic on all six hosts with no distortion, under noise up to sigma 10, contrast x0.8, the 3x3 blur with or without noise and requantisation at step 8; on five at step 16; on four at step 24 and at noise sigma 20. v3 is authentic only on clean images and on two of six at contrast x0.8.
- **The 5x5 blur defeats v4 on textured hosts.** No textured host is authentic; at 512x512 all six read `semantic_only`, so a blurred genuine image gets the label "regenerated". At 42 dB one or two of the four plain hosts stay authentic; at the matched budget one of four at 512x512 and none of the three marked hosts at 256x256.
- **Wrong labels on genuine images.** At noise sigma 20 one textured host in six is flagged as bound to other content, in both profiles at 512x512. On the plain hosts the flag appears on three of four at sigma 20 (512x512, keyed) and already at sigma 10 at 256x256 (one of four keyed, two of four public-derived). Those hosts have almost no block-level detail, so noise of that size dominates the detail part of the hash, although three of the four have strong large-scale content (pixel standard deviation 40 to 57). A genuine smooth image with visible noise can therefore be labelled copy-paste; population rates are given under the verification of revision 2 below. No other distortion in the tables produces the flag.
- **Matched distortion.** With the PSNR budget set to v3's measured mean on the textured hosts (50.4 to 50.5 dB), v4 at 512x512 is authentic on all six clean textured hosts and keeps that up to noise sigma 10; v3 is not authentic under any noise level in the table. **At 256x256 v4 is worse than v3 on clean textured hosts**: it cannot mark two of the six at that budget. On the plain hosts it cannot mark one of four, while v3 verifies only one of four; that column is not matched there, because v3's PSNR on the plain hosts (49.6 and 49.8 dB) is 0.7 to 0.8 dB below the budget v4 is given and 0.8 to 0.9 dB below what v4 realises there. Spread-spectrum embedding pays to cancel the host's own energy in the band, and at 50 dB the budget does not cover those hosts at that size. This is the method's operating envelope, not a tuning problem.
- **Plain hosts lose the mark under coarse requantisation.** At step 16 and above most plain hosts end as `neither_match`: the per-coefficient amplitude of the mark is below the quantiser step and nothing in a smooth host carries it across.
- **Transfers onto an unrelated image.** In none of the trials in these tables was a forged image authentic. Whenever the mark was delivered it was flagged, and with `binding_mode="none"` the same band transplant was accepted every time, so the content comparison is what rejects it. On these unrelated pairs the band transplants cost about 30 dB against the recipient, below the proposal's 35 dB quality target; within a composition that does not hold (T5). The residual copy stays near 42 dB but needs the donor's unmarked source, a stronger access regime than the default T4 attacker.
- **v3 transfers.** The transplanted payload is readable on all six recipients and is rejected only because the attacker did not also force the block-mean binding, which the v3 review showed to be cheap.
- **Images of one composition.** With the two benchmark keys, 0.4% to 3.3% of distinct pairs fall inside the instance radius and a further 5% to 25% in the undecided zone; independent codes would give 0.03% and 1%. These are per-key samples, not bounds: with two other keys the verification of revision 2 measured 0.0% to 8.5% and 2.8% to 33%. Plain band transplants to the next image of a family were flagged in 8 to 10 of 12 cases and undecided in the rest; none was authentic in these runs, but a pair inside the radius is, and in the verification 11 of 288 such transplants were accepted. Copying the semantic band alone gave `semantic_only` in 12 of 12 cases in every same-composition family.
- **Profiles.** The public-derived column differs from the keyed one by one to three hosts in several rows (512x512 plain hosts: 4 against 1 of 4 authentic at noise sigma 10; none against 3 of 4 flagged at sigma 20). The columns use different keys and the same noise, so this is presumably key-to-key variation; no run here separates the key from the profile.

**Limits of this evidence.** Each cell is six or four hosts with one key and one noise realisation; a count of 6/6 is compatible with a true rate as low as 61% (95% Wilson interval) and 0/6 with one as high as 39%. PSNR is the only quality measure; SSIM and LPIPS were not measured and no proposal quality target is claimed as met. JPEG files, resize and crop are not part of the benchmark. No ROC curve and no TPR at a fixed empirical false-positive rate are reported. The synthetic textured hosts have a semantic-band RMS of 8 to 28 and an instance-band RMS of 3 to 6, against 25 to 44 and 15 to 32 on the twelve photographs of the real-image run, so the 256x256 tables say little about photographs of that size.

**What the independent review measured (before revision 2).** The reviewers ran larger synthetic populations on the reviewed state. Figures that do not depend on the hash carry over; the hash-dependent ones are superseded by the verification below and are kept for the record.

- False positives: 8,320 detections on 416 unmarked images of 13 families and 6 sizes, 10 owners and both profiles; none found, largest score 4.14 against thresholds of 5.39 and 5.51. Wrong owner, wrong key and wrong profile: none found in 1,200.
- Embedding: 6 of 240 hosts failed self-verification at 256x256, all with a semantic-band RMS of 40 or more; none of 100 failed at 512x512.
- Hash-dependent, PIL-written JPEG files of synthetic luminance, authentic at 512x512 / 256x256: 82% / 72% at quality 30 and 59% / 20% at quality 20; Gaussian blur 32% / 2% at sigma 2.0; noise sigma 10 82% / 85%; resize to 0.5 and back 100% / 85%; a one-pixel shift 83% / 54%; an eight-pixel crop 0%, as declared.
- A spec-only re-implementation written from the document as it then stood reproduced the detector's codes, thresholds and outcomes exactly and both scores to 3e-14 on 258 cases, once two gaps in the text were closed (the channel label bytes and the role of the CRC); both are now stated above.
- Keyless forgery within a composition, repeated by the author against revision 2 with the reviewers' unchanged attack: 5 of 6 accepted as authentic at 31.6 dB against the recipient.

**What the independent verification of revision 2 measured.** Three verifiers that did not write the code worked on file SHA-256 `a5b6c02d...`, on synthetic images only. The record, every finding and the probes are in `audits/v4-revision-2-verification-20261001/`. The genuine-image rows share hosts across two keys and the public profile, so they are not independent samples and intervals computed from them would be too narrow.

- *Specification parity.* A detector written from this document as it stood at the verified state reproduced the config id, both codes, thresholds, candidate counts, both found flags, the semantic content status and the outcome in 5,184 of 5,184 cases and on 88 of 88 featureless or degenerate images, and both scores to 5e-12 in 5,140 cases. Two reporting conventions differed and are now stated in Phase 3: the instance status label under `binding_mode=semantic_only` (160 cases) and the candidate label of a key that was not found. An embedder written from the text reproduced the marked image exactly in 192 of 192 runs. In the other 44 cases, all flat or piecewise-constant negatives, the scores depended on floating-point summation order. The tolerances now stated in steps 2 and 3 are meant to remove that: in the author's re-run of the verifier's probe the reference gives the same scores under two summation orders in 156 of 156 detections, where 81 of 120 detections on flat images had differed. The spec-only detector was not re-run against the final text; a later reviewer checked the changed rules one by one against the code.
- *False positives.* No key was found in 9,456 detections on 394 unmarked images of 15 families and 9 sizes with 8 owners, two keys and the public profile; the largest score was 3.95 against thresholds of 5.39 and 5.51. Wrong owner, wrong key and other profile on 450 marked images: none found in 1,200. The empirical tail follows the normal reference and stays at 4% to 22% of the Hoeffding bound for scores of 2 and more.
- *Genuine images at 42 dB: 75 hosts per size at 256x256 and 512x512, 450 rows.* No embedding failed. Every row was `both_match` at noise sigma 2, JPEG quality 90, contrast x0.8 and resize to 0.75 and back. `content_mismatch` did not occur at JPEG quality 90 to 50, Gaussian blur sigma 1.0 to 2.0, contrast x0.8 or the resize (0 of 450 each) and occurred once at noise sigma 5. Under stronger noise genuine images are labelled copy-paste: at sigma 10 on 3.7% of textured rows (all at texture 6) and 23.5% of plain rows; at sigma 15 on 5.1% and 45.3%; at sigma 20 on 12.5% and 51.3%. Contrast x0.5 gave 6 of 450 and JPEG quality 30 gave 2.
- *JPEG and blur at 512x512 (225 rows).* JPEG 50: 107 of 108 textured rows authentic, 24 of 117 plain rows (90 `semantic_only`). JPEG 30: 106 of 108 textured, 11 of 117 plain. Gaussian blur: 224 of 225 at sigma 1.0, 221 at 1.5 and 105 at 2.0 (textured 19 of 108, with 87 `semantic_only` and 2 `content_uncertain`). At 256x256 the textured rows are authentic on 73 of 108 at JPEG 30 and on none at blur sigma 2.0. The plain-host losses read mostly `semantic_only` or `neither_match` (at JPEG 30: 19 and 78 of 117, with 7 `content_uncertain` and 2 `content_mismatch`).
- *Transfers onto unrelated images (240 trials each; the informed attack 180).* Band transplant: flagged in 240. Residual copy: flagged in 191, not found in 49. Neither was ever authentic. Semantic band only: flagged in 234, undecided in 4 and `semantic_only` in 2, at 36 dB. The informed attack that imports block means and the hashed coefficients reached `both_match` on every unrelated pair at 11 to 28 dB against the recipient.
- *Images of one composition (six families, two further keys, 288 trials per attack).* Hashes within the instance radius: 0.0% to 8.5% of pairs; undecided: 2.8% to 33%. Plain band transplant to the next image: authentic 11, undecided 43, flagged 234. Semantic band only: `semantic_only` in 288 of 288 at 26 to 37 dB. Copying the two hashed coefficients with the band: authentic in 288 of 288 at 24 to 34 dB. The optimised hash edit with an additive band: authentic in 251 of 288 at 27 to 36 dB, and on the two texture-6 families in 91 of 96 at about 36 dB.
- *Embedding envelope at 42 dB.* At 256x256 all hosts verify up to a semantic-band RMS of 34, 14 of 16 at 41.5, half at 48.5 and none from 68. At 512x512 all verify up to 80, half at 104 and none at 123.
- *Colour path.* `embed_rgb` planned without the rounding allowance and landed 0.4 to 0.8 dB under a 50.5 dB target in the verifiers' probes (49.71 to 50.08 dB). It now reserves the allowance; the author's re-run on one 512x512 host gives 50.60 dB at a 50.5 dB target and 42.07 dB at 42 dB.
- *Claims audit.* The test counts, all 478 benchmark cells, the mutation figures and every statistical figure reproduced. Nineteen findings, one high and eight medium, concerned the description: the state of the real-image run, two numbers that did not reproduce, undeclared deviations, untested changes and wording. They are corrected in this text and listed with their dispositions in the verification record.

**Operating envelope.** The clean score is about `sqrt(E_tag / host power)` when the host dominates, where `E_tag` is the energy spent on the 128 key bits of a channel. It grows with the square root of the pixel count. At 42 dB the semantic channel reaches a clean score of 9 for a band RMS of roughly 28 at 256x256 and 56 at 512x512. Smaller or more textured images fail self-verification and are reported as embedding failures. The pathological sawtooth pattern used by the v2/v3 unit tests (semantic-band RMS about 160 at 160x160) is such a failure and is kept as a test. A lattice modulation (spread-transform dither modulation) rejects the host at no cost and would widen the envelope; in unrecorded exploratory prototypes it lost the gain invariance that matters under blur and needed the detector to estimate the step. No artifact of those prototypes is retained, so this is a design note, not evidence.

Pure-Python timing on the development machine, 256x256: embedding about 0.2 s, detection about 45 ms, of which about a quarter is carrier derivation that depends only on owner and size. These figures describe the reference implementation only.

## Real-image observations (revision 1, another agent's run)

Run `c4-v4-three-threat-dev-001` was prepared and dispatched by another agent from the revision-1 snapshot under the user's manifest-specific approval (`.thesis-build/v4-three-threat-user-decision-20261001.json`). It was not authorized by this amendment's decision record. Before it started, its package had an independent review by the other agent's reviewer (`.thesis-build/v4-three-threat-final-review-20261001.json`: exact commit, manifest, input hashes and tests). That is not the algorithm review of item 1 of the next section, and the A4 preregistration of item 3 did not exist. The run used its own RGB8 and CLIP wrapper, which repeats detection with the vector of the saved image, and its own dose design (a VAE round trip, then strengths 0.05 to 0.4); neither has been reviewed against items 2 and 4 here.

The run stopped after about 21 minutes. Its last output was written at 03:53:48 local time with 96 of 1,884 planned detector calls complete, all on the clean axis; 16 regeneration outputs were blocked by the safety checker, 377 attacked images were saved without detection, and 54 regeneration and 66 collision rows were never run. Its official manifest still says `running`. That flag is stale: the other agent's partial audit of 2026-10-01T13:35:51Z (`thesis-runs/d916749c/continuation.md`) records that no worker exists, that the cause is undetermined and that the run must not be resumed or replayed. The run is exploratory, not preregistered under A4, and decided with the revision-1 rule. It supports no claim here.

As read on 2026-10-01 at 11:27 local time, the other agent's notes record a follow-up: an evaluation-only package for the 401 saved images of that run (`c4-v4-saved-evaluation-001`), approved by the user together with a model-free host preflight. The preflight ran and was stopped at an execution-identity check of the runner; the evaluation was not dispatched and no new scientific result exists. Any result of that package would be a revision-1 result.

What its clean axis shows, public-derived profile with the pinned CLIP ViT-B/32 vector, twelve MS-COCO development sources at 512x512:

- Marked images, correct owner: 12 of 12 `both_match`, scores 10.94 to 11.31 on both channels; luminance PSNR of the rounded RGB output 41.65 to 42.37 dB.
- Three wrong owners per marked image: 36 of 36 `neither_match`. Unmarked sources, four owners each: 48 of 48 `neither_match`, largest semantic score 2.86.
- Marking moved the CLIP-derived semantic code by 0 to 4 bits (non-zero on 4 of 12 images) and the hash by 1 bit on one further image; on those five images the affected key verified through the carried code.
- Semantic-band host RMS 25 to 44, instance-band 15 to 32; host rejection 0.85 to 0.96.

Its regeneration, copy-paste and collision rows have no detector outcome.

## What must happen before any further scientific use

1. Independent review of the exact files to be used (reviewer differs from author). The record has three layers, each by reviewers who did not write the code: the first review of the reviewed state (`audits/v4-independent-review-20261001/`), the verification of revision 2 on file SHA-256 `a5b6c02d...`, and a review of the changes made after it on file SHA-256 `d3938cc9...` (both in `audits/v4-revision-2-verification-20261001/`). The last review proposed an absolute floor for the tie window of the helper decoder. That change of one line, with its tests, was made afterwards and has been checked by the author only, with that reviewer's probes; the final file is SHA-256 `723773c7...`. A study must bind the hash of the file it uses.
2. A wrapper that passes canonical RGB8 PNG pixels and the pinned CLIP embedding, with per-profile receipts, and that repeats verification with the vector of the saved marked image. The wrapper of the revision-1 run does this; it was written for revision 1 and has not been reviewed for this amendment.
3. A4 preregistration for this candidate: frequency sets, PSNR budget, `alpha`, the four content distances, roster, attack inventory and reporting (TPR at a fixed false-positive rate, ROC, intervals over independent sources). The attack inventory must include the transfers that actually deliver the mark: the band transplant, the semantic-band-only transplant, the informed transplant that also edits the hashed coefficients, and a multi-image carrier-estimation arm. T4 and T5 are to be reported as attack cost per access regime, not as a single rejection count.
4. For T3, a dose-response design (VAE round trip alone, then low strengths) so that survival is a curve rather than one 0/N, with the analytic expectation of failure recorded beforehand.
5. The existing runner's manifest-specific authorization. No run is authorized by this document.

## Sources

Verification status is as recorded by the literature review of 2026-10-01: "read" means the paper text or abstract was fetched in that session, "metadata" means only the citation was confirmed. No number below is transferred to this codec.

- Malvar and Florencio, "Improved spread spectrum: a new modulation technique for robust watermarking", IEEE TSP 51(4), 2003, DOI 10.1109/TSP.2003.809385 (abstract read; the cost expression used in the code is derived here, not quoted): host-interference rejection in the correlation detector.
- Chen and Wornell, "Quantization index modulation", IEEE TIT 47(4), 2001 (read): spread-transform dither modulation; private-key versus no-key systems.
- Eggers, Bauml, Tzschoppe and Girod, "Scalar Costa scheme for information embedding", IEEE TSP 51(4), 2003 (read): spread spectrum is preferable to quantisation embedding under very strong attacks; repetition coding is inefficient.
- Fridrich and Goljan, "Robust hash functions for digital watermarking", ITCC 2000, DOI 10.1109/ITCC.2000.844203 (read): key-dependent projection hashes; public patterns let an attacker change hash bits.
- Arabi, Witter, Hegde and Cohen, "SEAL: Semantic aware image watermarking", arXiv:2503.12172v4 (read): SimHash of a semantic embedding.
- Fernandez et al., "The Stable Signature", arXiv:2303.15435 (read): closed-form false-positive rate and multi-key correction.
- An et al., "WAVES", arXiv:2401.08573 (read): TPR at 0.1% FPR as the reporting standard.
- Zhao et al., "Invisible image watermarks are provably removable using generative AI", arXiv:2306.01953v3 (read): conditional bound and empirical removal of low-perturbation marks.
- Lu et al., "Robust watermarking using generative priors against image editing" (W-Bench/VINE), arXiv:2410.18775 (read): classical transform-domain marks at about 40 dB fall to a few percent TPR under regeneration; low-frequency patterns survive editing better.
- Kutter, Voloshynovskiy and Herrigel, "Watermark copy attack", Proc. SPIE 3971, 2000, DOI 10.1117/12.384991 (metadata); Barr, Bradley and Hannigan, ICASSP 2003, DOI 10.1109/ICASSP.2003.1199109 (metadata); Juels and Wattenberg, "A fuzzy commitment scheme", ACM CCS 1999, DOI 10.1145/319709.319714 (metadata); Charikar, "Similarity estimation techniques from rounding algorithms", STOC 2002, DOI 10.1145/509907.509965 (metadata; the theta/pi statement above is from general knowledge); Hoeffding, "Probability inequalities for sums of bounded random variables", JASA 58(301), 1963 (not fetched).
