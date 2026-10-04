# Initial-noise watermark with an inversion-free terminal-sign diagnostic

Design version **`m1-gs-terminal-sign-v1`**, 2026-10-03; method decision at **xhigh**, before the first Gaussian Shading GPU run. This file specifies a new measurement only. It does not change the GS script/config, execute a model, alter family A, or report a human verdict. Family A's hybrid result must be considered separately before any A amendment.

## Decision and M1 accounting

**Native Gaussian Shading alone is a published latent-noise baseline, not evidence that the proposal's lightweight extractor works.** Its 50 inverse U-Net evaluations violate that constraint. Add a bounded, honestly named candidate **B-LW1: GS initial-noise embedding with direct terminal-VAE-sign readout** on the exact same saved images. This is a real initial-noise embedding; it is not a pixel comparator relabeled as latent. One VAE encode and sign/repetition decoding amend the proposal's image-DCT extractor and must be labeled as such.

After execution, B-LW1 may be inventoried as an attempted initial-noise/lightweight **carrier candidate** with an explicit minimum-recovery test. It is not a complete dual-key/three-state method. Native success must never substitute for B-LW1 success, and a deliberately simple readout's failure must not be called exhaustion of initial-noise methods. For conservative M1 exit accounting, retain B-native as the required literature comparator and B-LW1 as a component diagnostic; do not use their existence alone to assert three adequately investigated proposal families. The A/C/D candidates still need their own meaningful retained experiments, with failures at necessary clean/channel conditions explaining any curtailed threat evaluation. The final independent review must see this distinction.

The [primary Gaussian Shading method, Sections 3.2–3.3 and 7.1](https://arxiv.org/html/2404.04956v3), encrypts a repeated payload into noise quantile intervals and retrieves it after DDIM inversion. Its majority rule resolves equal votes to zero. Our inspected [native adaptation](m1-gs-adaptation.md) changes model, sampler implementation and whitening; no exact reproduction or inherited security theorem is claimed.

## Frozen generating experiment and causal contrast

The existing source is `scripts/m1_gaussian_shading.py` and `research/m1-gs-synthetic.json` last changed at **`72db24b041117900963709542582f223c0c15127`**. Inspected working-file SHA-256 values are respectively **`5249122b9493d33869f24f9cae99eac87d3eec69ecd2f561938a28a809c6cd92`** and **`88ef9fa1caabbeb3f5db7ea35212244144ed7778ab8463abb3bf4a4a5bfcdd89`**. A future implementation records its own committed code and actual native run commit; this design does not assert those future hashes.

Keep the four prompts/seeds 1000–1003, SD1.5 assets, 512x512 images, 50 generation steps, CFG 7.5, eta zero, C0/C1 shared half-normal magnitudes, 256 message bits with 64 spatial repetitions, and the declared SHAKE256 whitening unchanged. Native detection remains 50 inverse steps, empty prompt, CFG 1. The full paired grid is:

- Four prompt/seed cases, each with C0 and C1.
- Fourteen channels per arm: clean; one posterior-mode VAE roundtrip; and strengths .05/.1/.2/.4 at attack seeds 0/1/2 with DDIM20, CFG1, eta0.
- **112 scored images**: 56 C1 and 56 C0. The additional eight saved `original` files are provenance sources, not eight more independent conditions.

For each image, native and lightweight readouts use the same correct key, wrong key, nonce, reference payload and saved PNG hash. Do not generate a separate B-LW1 population, change the watermark, select better prompts or use recovered native noise to improve the lightweight output. C1 versus C0 generation quality is a counterfactual comparison, not preservation of an existing photograph.

## B-LW1 measurement, exactly defined

1. Reopen the condition's hash-verified RGB PNG. Apply exactly the native `pipe.image_processor.preprocess(image)` transformation from the pinned diffusers installation. Record preprocessing configuration and package version. Do not introduce another resize, centering, channel standardization or image transform.
2. Use the same frozen fp16 VAE weights and posterior **mode**, with batch one and no posterior sampling: `u = VAE.encode(x_fp16).latent_dist.mode()`, shape `1x4x64x64`. This is the terminal image latent, not initial diffusion noise.
3. Form `z0 = u * VAE.config.scaling_factor` with the same fp16 multiplication as native inversion initialization, then copy `z0.float()` to CPU. Record the scaling factor (expected .18215; verify against assets), units `scaled-terminal-VAE-latent`, shape, finite status, and actual dtypes. No inverse scheduler step, text encoder, U-Net call or original generation prompt is permitted.
4. Apply the existing `decode(z0, key, nonce)` rule unchanged. Flatten in C order `(channel,row,column)`, threshold each of 16,384 values with strict `>0`, XOR with the identical whitening bitstream, reshape to `(4,8,8,8,8)`, sum axes `(1,3)`, and output one for a vote count strictly greater than 32; otherwise zero. This produces `(4,8,8)` bits. Repeat only the inexpensive dewhitening/vote step for the fixed wrong key; do not re-encode.
5. The evaluator compares all 256 decoded bits with the existing `payload_for(generation_seed)`. Preserve the pre-run .7 cutoff exactly: **presence iff integer matches >=180**. Record integer counts, bit accuracy and exact-message recovery. Do not fit a threshold to C0, invert the result bits, select channels, search shifts/permutations, subtract learned means, normalize amplitudes or tune a projection.

The encoder/decoder boundary is `terminal_sign(image, vae, key, nonce) -> extracted_bits, vote_counts, diagnostics`. The **reference payload is evaluator side information**, not a detector input that may influence extracted bits. Native inversion results, original noise, clean reference images, CLIP features and attack labels are unavailable to this boundary. Key/nonce are public development fixtures; calling the manifest's development key a real secret would be inaccurate. Per-image nonce and reference-message availability are generous enrollment assumptions, not blind recovery from public OwnerID alone.

Positive rescaling preserves signs in exact arithmetic. Because fp16 underflow can create zeros, record zero counts before/after scaling and the number of sign differences between `u` and `z0`; do not choose whichever units score better. Neither scaling nor amplitude whitening makes a terminal image latent a sample of the initial-noise variable. A nonfinite latent is a recorded measurement failure, never a forced negative or a passing replacement.

## Cheap diagnostics and output contract

This design favors a **separate read-only assessor** after native artifact generation, rather than altering the frozen GS generation/inversion algorithm. A future `scripts/m1_gs_lightweight.py` and versioned manifest may implement it. It reads the original receipts and writes a unique new development directory; it never edits native output. It needs only the local VAE, not the full diffusion pipeline. The assessor must demonstrate preprocessing equivalence to the native image processor in a CPU fixture before execution.

Before GPU use, test: exact recovery from freshly constructed marked initial noise; preserved coordinate/tile order; the 32/33-vote boundary; keys/nonces; positive-scale invariance apart from explicitly tested floating-point zeros; finite/shape validation; 179/180-match decision boundary; and a boundary test showing payload/reference changes do not change extracted bits. An all-zero vote tensor must decode to zero, demonstrating the declared tie rule. These tests validate code, not channel survival.

At generation time, a cheap source-noise self-check should decode the actual fp16 tensor supplied to generation and retain its matches/zeros. It must recover 256/256; otherwise investigate the adapter before interpreting either readout. This optional new receipt does not change supplied noise. If implemented as a later assessor, regenerate only that deterministic source tensor from the committed seed/code for this diagnostic and label it reconstructed input, not a retained tensor from the original run.

Use the original `artifacts.json`, `rows-receipt.json`, final `run.json` and row hashes for joins on `(case,arm,channel,image_sha256)`. Copy raw input metadata snapshots and their hashes into the new run. Require exactly the declared 112 identities for a completed comparison, retaining explicit missing/error records if the native run is incomplete. Never replace a missing image or borrow another seed. Completed native rows may be assessed incrementally in a separate output, but the expected denominator remains 112 and no interim success claim closes the study.

Each new row must include:

- Source run/row identity and image hash; case, generation seed, arm, channel, strength and attack seed.
- `readout_id=m1-gs-terminal-sign-v1`, scale/units/dtypes, VAE/hash receipt, key/nonce identifiers, reference-payload hash, and preprocessing identity.
- All 256 extracted correct-key and wrong-key bits, their 256 vote counts, tie counts, integer matches, accuracies, exact-message flags, and fixed presence decisions.
- Zero/sign-change diagnostics, per-channel latent mean/std, finite status, tensor shape, and failure reason where applicable. These statistics are descriptive, not inputs to a corrected detector.
- Standalone elapsed encode/decode/total time, measured peak GPU allocation, **VAE encodes=1, U-Net evaluations=0, text-encoder evaluations=0**; native scores/runtime/NFE joined unchanged from their source row.

Synchronize CUDA around GPU timing; separate one-time model loading and record first-call status. Do not claim deployment speed from unsynchronized kernel launches or subtract differently warmed measurements. Raw bits/votes allow review without retaining all latent tensors. Keep the existing safety checks on generation/attacks; scoring retained images neither changes those checks nor supplies a human quality verdict.

Run locally with verified cached assets, network disabled, float16, batch one, a 10 GiB GPU cap, 16 GiB RAM cap, at most 100 MiB new artifacts, and 20 minutes of additional wall time as a conservative budget. These are unmeasured caps. Journal each completed image and support resuming only identical code/config/input receipts; native GPU time is outside this incremental budget. If the cap is reached, retain the missing rows and schedule an identical bounded continuation rather than weakening the protocol.

## Prespecified analysis and escalation rule

Primary screening asks whether the fixed zero-inversion decoder recovers the embedded message well enough for the existing presence decision. Report for **each of the 14 channels and each decoder**: C1 presence numerator/4, exact payload numerator/4, all four accuracies and mean; C0 positives/4; C1 wrong-key positives/4; missing counts. For each strength also report 12 attack outcomes while keeping the four prompt clusters visible. The attack seeds are repeated conditions, not 12 new independent generated images. Do not pool all conditions into a headline TPR or count 112 independent subjects.

Also report paired per-image `native_matches - lightweight_matches` and a four-cell presence table (both/native-only/lightweight-only/neither). These are descriptive comparisons. There is no powered significance claim with four prompts, and no best-strength selection.

The B-LW1 clean gate requires **4/4 C1 presence**, **0/4 C0 positives** and **0/4 C1 wrong-key positives**; the VAE gate requires the same counts after the additional cycle. Retain the complete T3 grid even if those gates fail: it already exists for the native comparator and the additional readout is inexpensive. Passing both gates warrants a separately designed content-bound/noise-to-lightweight method; it does not establish the three states. Failure of either gate rejects this exact unmodified GS plus terminal-sign recipe as a ready candidate. Do not tune a new readout in this run.

Interpret native results first. If source-noise self-checks pass but native clean recovery fails, the published-method adaptation/inversion needs diagnosis before it can function as a validated baseline. The lightweight measurements remain observations but cannot establish that a native-to-lightweight tradeoff caused the failure. If native succeeds and B-LW1 fails, the strongest justified statement is: **the enrolled signal is recoverable by this inverse procedure, but the direct terminal-sign readout does not recover it at the fixed cutoff on these cases.** Native success actually supports retained information in the image; it does not support information-theoretic erasure.

## Capacity and false-positive limits

There are 16,384 physical sign positions but only 256 distinct payload bits, each repeated 64 times. Repetition trades information rate for tolerance; it does not yield 16,384 independent identity bits. Before repetition, a 32-bit semantic code and 32-bit instance code could fit in 256 bits with room for other fields, but there is no evidence that a terminal-sign detector transports even those bits. High-dimensional semantic AUC cannot be substituted for measured coded-channel reliability. This pilot contains neither semantic binding nor a fragile instance tier, so T4/T5 identity-state claims remain outside its scope.

Even an idealized fair-chip null does not yield exactly fair decoded bits under this finite strict-majority rule. Let `t=C(64,32)/2^64=.09934675375` and `q=(1-t)/2=.45032662313`. If all dewhitened input chips were independent fair bits, a decoded bit would equal one with probability q. For a fixed payload containing w ones, the match count would follow

`X = Binomial(w,q) + Binomial(256-w,1-q)`, with independent summands.

The four frozen SHAKE-derived payloads give the following **conditional arithmetic references**, computed before image evidence by finite binomial sums:

| Seed | Payload ones w | Ideal mean agreement | Ideal P(matches >=180) |
| --- | ---: | ---: | ---: |
| 1000 | 132 | .498447707 | 1.9407882e-11 |
| 1001 | 135 | .497283487 | 1.5120879e-11 |
| 1002 | 119 | .503492659 | 5.6494634e-11 |
| 1003 | 128 | .500000000 | 2.7023851e-11 |

The simpler fair-decoded-bit binomial tail is 3.3404684e-11, but it is not the exact fixed-payload/strict-majority calculation. More importantly, **none of these is a validated FPR for B-LW1**: image latents are structured, the fixed public whitening streams are not fresh independent secret masks, repeated attacks are correlated, and adaptive forgery violates the null. Keep the native cutoff as a predeclared experimental rule rather than retrofit a security interpretation. C0 and wrong-key queries are separate empirical false-positive controls; zero errors among four clean C0 images has a one-sided 95% binomial upper limit about 52.7% even under independence, not evidence for an extremely small FPR. Searching additional owners, nonces, alignments or decoders would introduce multiplicity and must be declared separately.

Public keys and the absence of semantic binding permit re-embedding or transferring identity evidence; no secret-signature guarantee arises from either readout. Three causal labels cannot be inferred from a single recovered owner/message indicator. An absence may be an unmarked image, attack, readout error or unsupported content; a presence may be a copied or newly forged mark.

Finally, coordinate signs are just one nonlinear projection of the final latent. Diffusion can transport the initial code into other coordinates, amplitudes, phases, feature interactions or semantics. B-LW1 failure does not bound the mutual information available to a learned extractor, prove every DCT projection fails, certify an optimal detector, or exhaust initial-noise embedding. A learned/distilled inverse-free reader, altered placement/code, or jointly trained carrier-reader would require a new design, independent development training/validation, resource estimates and explicit proposal amendments. They remain untested possibilities; this diagnostic neither promises their success nor fabricates their rejection.
