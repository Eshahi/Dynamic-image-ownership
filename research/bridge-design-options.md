# A5 bridge and recomputation design analysis

2026-09-23; issue #6; author `/root`. Status: **PARTIAL DESIGN ANALYSIS, NOT A5 COMPLETION**. No model execution, experiment, parameter freeze, compute authorization or feasibility result. This document applies [research-contract.md](research-contract.md), [scope-guard.md](scope-guard.md), and the detector knowledge boundary in [io-spec.md](io-spec.md). It preserves the original proposal and all dataset/claim commitments.

## Scope and evidence

The immutable A5 task requires an implementable Pattern -> Noise -> Image -> DCT link and stable recomputation, not just compatible shapes. The source method derives semantic and instance signatures from the input and public OwnerID, inserts a pattern into initial diffusion noise, and compares image-block DCT coefficients with candidate-key templates. The inspected-source gap is recorded in `evidence-gap-assessment.md`; none of that literature is treated as validation of the proposed bridge.

The equations below are author-derived design analysis, not attributed literature findings. They isolate two independent obligations: (1) obtain the same candidate pattern from a modified image, and (2) make an initial-noise perturbation visible to the specified image-domain statistic. Success on either alone does not establish the other. No assertion of impossibility for diffusion watermarking is made.

## 1. Exact signature recovery is stronger than feature similarity

Let `e(I)` be a normalized semantic feature, `q(e)` a deterministic bit quantizer, and `h(I)` the perceptual bit code. For a candidate whole-code-hash design, define:

```text
Ws(I,o) = Hash(Serialize(domain_s, q(e(I)), CanonicalOwner(o)))
Wi(I,o) = Hash(Serialize(domain_i, q(e(I)), h(I), CanonicalOwner(o)))
```

Serialization must be unambiguous (versioned, length-delimited fields), with distinct component domains. This is a candidate specification family, not a selected hash/quantizer/configuration. No secret is present. Ignoring hash collisions, equality of the exact serialized inputs is required for the same seed/signature. Nearby vectors or a small bit distance do not imply the same hash-derived pseudorandom template.

For sign projections `q_k(e)=1[a_k^T e >= 0]`, a sufficient bit-stability condition for perturbation `d=e(J)-e(I)` is `|a_k^T e(I)| > ||a_k||_2 ||d||_2` for every k. This follows from Cauchy-Schwarz and excludes zero-margin boundaries. It is sufficient, not necessary; actual feature perturbations and margins have not been measured. A joint exact-match rate cannot be inferred from cosine similarity. If bit survival were independent with common probability p, all-bits survival would be `p^b`; independence is only a hypothetical illustration, not a data model adopted for this thesis.

`Wi` has the additional exact pHash requirement, so semantic stability alone cannot rescue its template. The first diagnostic must separate `q` equality, pHash equality, signature equality and final scores for I versus untouched Iw, then benign transformations. Retain all failures. Reference signatures belong to the evaluator/oracle route, not the core detector.

Alternatives remain explicit rather than silently repairing a failed method:

- Fixed quantization followed by whole-code hashing preserves the source key structure, but stability is a falsifiable requirement, not guaranteed by choosing fewer bits. Coarser quantization can reduce instance/semantic discrimination.
- Enumerating nearby codes adds candidate trials and runtime; a frozen search rule, hard cap, tie handling, and any-of-candidates false attribution calibration are required. It must not consume the original code or select a radius from test results. This is not selected here.
- Per-bit carrier matching or a stored-reference/fuzzy-helper construction changes the signature or information contract. Treat it as a separately analyzed alternative, not a transparent implementation of whole-code hashing. Stored enrollment information is forbidden in the core route under the current contract.

## 2. Why reshaping one random pattern does not define the bridge

For fixed image I, model/configuration and conditioning c, write `F_I,c(z)` for the entire differentiable suffix from the chosen initial noise state through denoising and image decoding. Let `z` have n scalar entries and the output image m. This notation does not select a model, noise schedule, inversion, or image-conditioning algorithm. Let `D: R^m -> R^r` be a fixed linear color projection, 8x8 block DCT and coefficient selection for an untransformed fixed-size image. Clipping, quantization and geometric changes are outside this local linear analysis and must be tested separately.

For latent perturbation p and small scalar alpha:

```text
x(alpha) = D F_I,c(z + alpha p)
x(alpha) - x(0) ~= alpha A p
A = D J_F(z)                         # shape [r,n]
```

With an image-domain template t of shape `[r]`, the first-order change in its unnormalized correlation is `alpha t^T A p`. Sharing a random seed between p and t, or merely reshaping/truncating p into t, supplies no constraint on this inner product. For example, a linear map can project p to zero or to a vector orthogonal to t; it can also align them. These examples disprove a general inference from matching seeds/shapes, not the feasibility of a particular decoder.

Even if `t^T A p > 0`, the blind detector scores absolute coefficients containing host content `D F_I,c(z)`, not a clean subtracted residual. A residual-only positive result is an oracle diagnostic. Content-derived templates and host coefficients may be dependent, so independence-based null-score/FPR claims are not justified. Use unmarked inputs and matched unmarked reconstructions with the full recomputation detector.

## 3. Two explicit latent-only candidate families

### L0: direct seed-derived noise injection

Generate independent, domain-separated latent carriers `ps,pi` from Ws/Wi and deterministic image templates `ts,ti` from the same respective keys. An eventual exact design must fix carrier generation, normalization, latent mask and scaling:

```text
z_w = z + alpha_s M_s ps + alpha_i M_i pi
Iw = F_I,c(z_w)
```

Neither the image pixels nor image DCT coefficients are overwritten. The detector needs only J, OwnerID and frozen public configuration. This is a concrete family to falsify, not a justified successful bridge: unless a measured transfer relation exists, independent image templates can have no useful response. It needs a matched unmarked `F_I,c(z)` control and full Iw-versus-I reconstruction-quality reporting. It may fail before attack testing. No strength, masks or generator have been selected here.

### L1: image-objective-guided initial-noise optimization

At embedding only, construct public, key-derived image templates t. Adjust **only the initial noise perturbation** delta while retaining the fixed denoising/decoding map. The image-domain objective guides the latent variable; no post-decoding pixel watermark is added. A candidate objective family is:

```text
min_delta  Lquality(F_I,c(z+delta), I)
         + lambda_s Lmark(D_s F_I,c(z+delta), ts)
         + lambda_i Lmark(D_i F_I,c(z+delta), ti)
subject to ||delta||_2 <= rho, with a fixed optimization budget
```

For one *unnormalized linear* template objective `t^T D F`, its local ascent direction is `A^T t`; the first-order score change from `delta=eta A^T t` is `eta ||A^T t||_2^2 >= 0` for eta>0. It can be zero. This is only a local derivative identity, not a finite-step, normalized-score, quality, two-component, or robustness guarantee. The two objectives can interfere, the generator may be locally insensitive, and an optimizer may fail within its memory/time budget.

Unlike L0, L1 supplies an explicit mechanism relating a public detection template to initial-noise modification. Templates remain reconstructible without I, z, c, model decoder, or enrollment state at detection. Yet they must be recomputed from J: if q or h changes during embedding, the intended template may no longer be the one tested. Treat this as a hard recorded failure or define a reviewed bounded stability constraint; do not secretly provide source keys, re-sign the final output, or retry indefinitely. Final PNG/other declared encoding and range conversion must be included in verification, not just differentiable floating outputs.

L1 is an **unselected design candidate** under A5's existing-image optimization allowance. Review exact compatibility with initial-noise placement before adoption; optimizing a decoded latent only and calling it initial diffusion noise would be a deviation. Embedding gradients do not require gradients or inversion at detection. Differentiating through denoising may exceed local resources; no fit/runtime claim is made. L1 does not imply that latent marks survive regeneration better than spatial comparators. If it can only work by adding a pixel residual or a different detector, that replacement requires a material decision.

## 4. Decision and next bounded work

Do not freeze L0 as a working bridge on dimensional intuition. Develop the exact L1 existing-image candidate next, with L0 as a possible separately budgeted comparison, but do not select either as scientifically validated. This author recommendation is not acceptance of A5 or plan-acceptance.

Before authoring final `method-spec.md` and `method.schema.json`:

1. Inspect a pinned existing-image diffusion implementation, licensing and its actual noise-injection/differentiation path. Determine exactly which state is optimized, shapes/dtypes, conditioning source and fixed schedule. Prefer a model compatible with the available hardware, but do not download or execute it yet. Record whether any proposed signing step is outside the source route.
2. Specify a single full candidate: feature checkpoint/preprocess, normalized representation, deterministic quantization and pHash, canonical OwnerID encoding, exact seed/carrier/template functions, disjoint component coefficient layout or explicit interference handling, DCT/channel/edge/synchronization rules, normalized statistic, and bounded embedding optimization/failure rules. Separate rationale-backed design choices from validation-calibrated thresholds.
3. Keep the default core API recomputation-only and public-derived. No ownership authentication, general presence witness, regeneration attribution, native prompt-only route, or successful initial-noise-to-DCT transfer is claimed.
4. Independently review the exact design; then A4 specifies endpoints, calibration, negative controls, sample size and stopping. Unit/shape tests are ordinary engineering checks; image/model feasibility trials still need an exact approved scientific manifest.

Remaining status: IO-01..05 are not closed by this analysis; IO-06/07 and SC-01/03/04 retain their explicit limits. Dataset commitments and separate neural/inversion comparator obligations are unchanged. The official run remains paused at plan-acceptance. No user decision is needed solely to continue this bounded design work; a material method departure or a ready scientific compute package would require one.
