# Implemented A-C end-to-end candidate

Status: development candidate `m1-terminal-continuous-e2e-v1`; final M1 selection and milestone review remain pending. This document consolidates already frozen operations, rather than choosing a new design from outcomes. The normative development config is `m1-terminal-e2e-dev.json`; the path-free implementation interface is `m1-candidate-adapter-interface.md`. The original component, deterministic execution, original200 initialization and owner/seed amendments remain explicit dependencies. Historical component results using retained legacy initializers are not end-to-end validation of the new initializer.

## Inputs, descriptors and public claim

The canonical source is RGB8, 512 by 512, obtained after raw-byte receipt validation, EXIF transpose, ICC-to-sRGB conversion when present, and bicubic resizing. `scripts/m1_canonical_source.py` accepts already verified immutable bytes; it does not authorize access. Development source membership and raw hashes are fixed by the development config. Held-out inputs remain locked.

The semantic descriptor E is the normalized 512-dimensional output of the pinned CLIP ViT-B/32 image encoder. H is the pinned profile's 32-bit image-DCT perceptual hash. The public OwnerID selects deterministic coordinate/sign/projection maps. The core admits the four retained pilot owners and sixteen `thesis:owner:00` through `15` identities, with exact old-owner map parity. It rejects arbitrary or normalized aliases. Development embeds alpha and queries all four pilot owners; the proposed confirmatory interface uses the separate frozen sixteen-owner schedule. The latter's uint64 seed is metadata only: this deterministic candidate has fresh phase seed zero and restores execution RNG on continuation. This is a declared amendment, not an assertion of compliance with the older seed-consuming protocol.

This candidate replaces discontinuous semantic-code hashing with continuous full-CLIP templates. It also replaces a pixel-DCT detector by VAE posterior-mode readout. H is still a DCT perceptual hash, but the extracted carrier is not a pixel midband DCT watermark. These differences must be accepted explicitly if the user adopts the candidate at M1.

## Two templates and observable scores

`scripts/m1_blind_noise_core.py` is normative for framing, SHA-256 sorting, SHAKE-256 signs, C-order layout and normalized Sylvester transforms. N=16384 latent coordinates are divided into two disjoint sets of M=8192 using public OwnerID maps. The semantic unit vector is an isometric Hadamard embedding of E. The instance unit vector is a normalized, signed subsampled Hadamard projection of `E tensor b(H)`, where each of the 32 hash bits becomes a sign divided by sqrt(32). Both receive independent owner-dependent row signs. There is no learned extractor or inversion.

For a suspect image J, recompute E(J), H(J) and the scaled latent `z=.18215*mode(VAE_fp16.encode(J))`. For channel c, with its coordinate set K, template v and signs r, the score is

`score_c = sum(z[K] * v * r) / norm(z[K] * v)`.

All scoring and map algebra is CPU float64. A zero or nonfinite denominator remains invalid; no fitted stabilizer is inserted. The threshold is inclusively 4 for both channels. This is a development engineering threshold, not a certified population false-positive quantile. Source descriptors, initialization latents, enrollment records, target messages and nonces are absent from `detect(suspect_rgb8, public_owner, pinned_models_and_profile)`. Source-template diagnostics are separately labeled oracle observations.

| Semantic threshold | Instance threshold | Result |
| --- | --- | --- |
| reached | reached | `both_match` |
| reached | not reached | `semantic_only` |
| not reached | not reached | `neither_supported` |
| not reached | reached | `ambiguous_instance_only` abstention |
| either invalid | any | `invalid_measurement` abstention |

These states express measured public content-template consistency. They do not identify which attack happened, prove legal ownership, verify a private signature or certify provenance. Public maps permit an attacker to reproduce templates; no secret PRF, digital signature or secret owner credential is implemented. The uncompressed instance kernel is `cos(E1,E2)*(1-2*HD(H1,H2)/32)` before the documented finite projection/normalization effects. Consequently semantic similarity and hash drift impose a continuous discrimination/stability tradeoff; a hash-distance cutoff alone cannot certify rejection.

## Initialization, embedding and saved-image boundary

Initialize the unscaled latent from the frozen FP32 VAE posterior mode and minimize RGB-float reconstruction MSE for exactly 200 Adam updates, learning rate .02, using `m1_source_initialization.py`. This unmarked reconstruction has its own optimizer. The new complete deterministic initializer was checked against the literal original operation and independent-process prefix/resume; the associated evidence is separate from watermark efficacy.

Start a fresh embedding Adam at the final initialization latent u0, learning rate .01, betas (.9,.999), epsilon 1e-8, for exactly 100 updates. Freeze every model weight. With `D(u)=clip((VAE_fp32.decode(u)+1)/2,0,1)`, optimize only u and form the residual `R(u)=D(u)-D(u0)`. The differentiable image is `clip(I+beta*R(u),0,1)`, with `beta=min(1,10^(-35.2/20)/RMS(R))` and the declared zero-residual branch.

The loss and sequential gradient accumulation are exactly those in `m1-terminal-continuous-design.md`: squared hinge targets 6 semantic and 8 instance on the clean image, normalized distortion weight .01, and semantic target 6 after the float VAE cycle on even update indices. Source E/H are fixed objective inputs; blind suspect recomputation supplies the independent endpoint. There is no descriptor-gradient optimization, success-based early stopping, dose search or best-step selection.

At update 100, use the raw residual and the fixed 36-iteration scalar, quality-only cap to emit RGB8 at the 35.2-dB PSNR cap. Save and reload the PNG before primary detection. The final composition has an explicit original-source bypass. It is latent-variable optimization with a decoded residual, not pure VAE output and not an initial-noise generation method. Pure decoded quality is diagnostic only. Clean C0 is the canonical source; matched unmarked reconstruction is reported separately.

Both phases retain full latent/Adam/RNG/config/runtime/source/model/core bindings at ten-update checkpoints. Fresh phases reset execution RNG to zero; continuation restores the saved state under identical verified dependencies. Deterministic algorithms are enforced, TF32 and cuDNN benchmarking are disabled, and CUBLAS workspace is fixed. No tolerance-based replay waiver is allowed. The path-free candidate adapter requires a caller-verified scientific-core hash; a supplied string alone does not establish that verification.

## Evidence and comparison boundaries

The frozen original two-source end-to-end gate requires both clean quality conjunctions, both clean `both_match`, both VAE semantic successes and all 28 negative channel checks. Only a passing gate triggers unchanged expansion to the other ten fixed development sources and the full common 489-condition threat/control inventory. Expanded failures remain in the inventory. Human visual assessments stay null. Neither a two-source pass nor twelve successes establishes the acceptance document's population bounds.

Development comparisons retain the v5 image-domain comparator's own thresholds and source/attack identities. Published initial-noise baselines are characterized within their feasible generated-image/enrollment scope, not relabeled as source-free existing-photo attribution. Native projection, residual transfer, semantic-collision diagnostics and their delivery controls are specified separately in `m1-terminal-continuous-expansion-design.md`; no attack success is inferred solely from detector rejection.

Terminal optimization and lightweight VAE readout have prior art, including the inspected latent methods in `m1-terminal-reader-prior-art.md`. This package makes no standalone novelty claim for those operations. Final M1 selection, measured frontiers, exact execution manifests, candidate-identical rehearsals and independent review must be attached before this document can support the user's single confirmatory-run decision.
