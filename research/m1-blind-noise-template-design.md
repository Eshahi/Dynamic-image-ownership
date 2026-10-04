# B3-C: blind continuous content templates in initial noise

Version **`m1-blind-noise-template-v1`**, 2026-10-04; method escalation **gpt-6-astra/xhigh**. This is a prospective development design following the exploratory B-LW1 carrier result. No B3-C model run, threshold selection, scientific success or human assessment is reported here. Parent researcher owns implementation, commit, execution and shared state. The experiment-design skill informs the contract; the autonomous handoff authorizes bounded local development without a human approval artifact.

**Decision: implement this bounded blind candidate before treating the initial-noise family as adequately investigated.** It uses full CLIP geometry to construct an analog matched-filter template instead of requiring exact recovery of a quantized semantic message. B-LW1-P1 remains the independent implementation probe, and B2-R remains an optional enrolled comparator; neither substitutes for this reference-free content-binding experiment. Leave family A unchanged until its frozen 12-source threat assessment finishes.

## Hypothesis and explicit method amendment

An owner-dependent spread of a continuous content descriptor may survive initial-noise transport sufficiently for a terminal-VAE matched filter, while its source-preserving residual remains small. This is plausible, not established by GS: the observed GS message accuracy uses repetition, generated images and a reference payload. A weak analog signal can accumulate coherently over thousands of coordinates without exact recovery of hundreds of independent bits.

[NoisePrints v1, Sections 3.3–4 and Appendices E/G](https://arxiv.org/html/2510.13793v1) already studies correlation between initial noise and the final image's VAE encoding. [OSI v1, Appendix D.1](https://arxiv.org/html/2602.09494v1) explicitly reports strong message recovery at Step-0, the encoder output, for spatial repetition eight. These are inspected primary precedents for the carrier observation, not novelty or performance guarantees for this candidate. Parent-owned literature cards retain their detailed mechanisms and limits.

Define `Ks = f_s(E, OwnerID)` and `Ki = f_i(E,H,OwnerID)` as **continuous public templates**, not secret cryptographic keys. `E` is the normalized full 512-dimensional pinned CLIP ViT-B/32 embedding. `H` is the same 32-bit DCT perceptual hash used in family A, with its existing public v5 profile. A fixed owner map spreads these features into an initial-noise perturbation. The detector recomputes both features from the suspect image, then performs one VAE encode and two inexpensive correlations. It receives **no clean image, enrollment record, original descriptor/hash, message, source noise, image-specific nonce, prompt, generation seed or inversion output**.

This amends the proposal in three material ways: tolerant analog templates replace exact derived bit keys; extraction adds one VAE encode to CLIP plus image-DCT feature extraction; the primary existing-photo output has an explicit source-pixel bypass. Embedding performs diffusion inversion and forward diffusion; extraction performs neither. The pure forward-decoded output is separately measured. Public recomputation gives no cryptographic authenticity or proof of authorship.

## Frozen deterministic maps

Flatten every latent in C-order `(channel,row,column)`, shape `(4,64,64)`, length `N=16384`. Let `m=8192`, `L=16384`, and `U_n[a,b]=(-1)^popcount(a&b)/sqrt(n)` be the normalized Sylvester Walsh–Hadamard matrix in its natural integer order. Implement a float64 CPU FWHT; no dense matrix is necessary. All templates are computed in float64 and only the final supplied diffusion tensor is rounded to model dtype.

Numerical convention frozen before execution: reject E unless it has exactly 512 real finite entries and its norm differs from one by at most `1e-6`; divide an accepted vector by its float64 norm to remove normalization roundoff only. Reject arbitrarily scaled input rather than silently repairing it. H is an integer in `[0,2^32)`, excluding booleans. Wrong shapes/nonfinite score inputs yield an explicitly retained invalid measurement. The maps and thresholds remain unchanged by these implementation guards.

For reproducible public randomness, use exact UTF-8 owner bytes, without Unicode normalization; this pilot accepts its four fixed ASCII owners only. Define `frame(s)=uint32_be(len(UTF8(s))) || UTF8(s)` and `prefix(d,o)=frame("m1-blind-noise-template-v1") || frame(d) || frame(o)`. `perm(d,o,n)` sorts integers `0..n-1` by `(SHA256(prefix(d,o)||uint32_be(index)), index)`. `signs(d,o,n)` takes the first `n` MSB-first bits of `SHAKE256(prefix(d,o)).digest(ceil(n/8))`, mapping zero to -1 and one to +1. Hash collisions use the index tie-break. The distinct domain strings below are literal; no seed or permutation search is allowed. The statistical discussion idealizes these domain-separated public hashes as independent randomness, rather than proving it for their fixed outputs.

Use `perm("coordinates",o,N)[:m]` for semantic coordinates `S_o`, and its remaining entries, in that order, for instance coordinates `I_o`. This is a partition, not two overlapping masks. The complete owner roster is `qim-pilot-owner-alpha`, `qim-pilot-owner-beta`, `qim-pilot-owner-gamma`, `qim-pilot-owner-delta`. Only alpha embeds; all four are queried.

**Semantic template.** Select columns `C_s=perm("semantic-columns",o,m)[:512]`. Place `E[j]` at position `C_s[j]` in an otherwise zero length-m vector and apply `U_m`. Call the result `v_s(E)`. Set `r_s=signs("semantic-row-signs",o,m)` and `t_s(E)=sqrt(m) r_s*v_s(E)`, where `*` is elementwise. The vector has squared norm m. In exact arithmetic,

`cos(t_s(E),t_s(E')) = E dot E'`.

This exact template-geometry guarantee follows from orthonormal selected columns and a fixed sign diagonal. It is not a guarantee about distorted images, their rederived CLIP vectors, matched-filter scores or attack discrimination.

**Instance template.** Let `b(H)[k]=(2*((H>>(31-k))&1)-1)/sqrt(32)`, `k=0..31`, and flatten `x(E,H)=E[:,None]*b(H)[None,:]` in C-order. It has dimension L and unit norm. Its uncompressed kernel is exactly

`x(E,H) dot x(E',H') = (E dot E') * (1 - 2*HD(H,H')/32)`.

Set `d_i=signs("instance-pre-signs",o,L)` and `R_i=perm("instance-rows",o,L)[:m]`. Compute `p_i=sqrt(L/m)*(U_L(d_i*x))[R_i]`, `v_i=p_i/||p_i||`, and `t_i=sqrt(m)*signs("instance-row-signs",o,m)*v_i`. Reject zero/nonfinite norms; do not substitute another map. Compression to 8192 dimensions is **not isometric** on all 16384-dimensional product features. Its actual error must be reported; it is not legitimate to retain the product-kernel equality after compression without this qualification.

For a pair of fixed product features x,y, condition on their fixed pre-sign diagonal and put `u=U_L(d_i*x)`, `w=U_L(d_i*y)`, `a_k=u_k*w_k`, and `g=x dot y`. Ideal uniform sampling of m rows without replacement gives the exact identities

`g_hat=(L/m)*sum_{k in R_i} a_k`, `E[g_hat]=g`,

`Var(g_hat)=L^2*(1-m/L)*S_a^2/m`, with `S_a^2=sum_k(a_k-g/L)^2/(L-1)`.

The same formula with `a_k=u_k^2` estimates the projected squared norm. Chebyshev gives `Pr(|g_hat-g|>=epsilon)<=min(1,Var/epsilon^2)` under that sampling model; it can be weak. No favorable coherence, universal JL guarantee or independent latent-coordinate assumption is silently supplied. For actual projected norms A,B, set `delta=max(|A-1|,|B-1|)` and `epsilon_g=|g_hat-g|`. If `delta<1`, a deterministic normalization-error bound is

`|g_hat/sqrt(A*B)-g| <= (epsilon_g + |g|*delta)/(1-delta)`.

Always report the actual normalized error too. For delta>=1 retain the direct error and mark this bound uninformative. Log kernel/norm errors for every source-to-own-suspect comparison and for the source pair under all four owners. Do not pick an owner/map with the smallest error. Two images do not establish semantic-collision separation. A CPU fixture with 32 independently generated normalized feature/hash pairs, NumPy PCG64 seed0, additionally checks these algebraic identities without image/model evaluation; it is a code diagnostic, not image evidence.

## Reference-free scores and three operational states

For suspect RGB8 image J, obtain its own E(J), H(J), and VAE posterior-mode terminal latent `z=.18215*mode(encoder(2*J/255-1))` using the pinned SD1.5 VAE and the same preprocessing as B-LW1. Retain the actual model scaling factor and reject a mismatch to the expected .18215. Use the pinned fp16 VAE arithmetic; convert its scaled output to CPU float64 before scoring. One encode serves all four owner queries.

For j in {s,i}, take z on the appropriate coordinate subset and define, using v before the final row-sign multiplication,

`score_j = sum_k z_k*r_jk*v_jk / sqrt(sum_k z_k^2*v_jk^2)`.

A zero denominator, nonfinite model/feature value, wrong shape or failed input receipt yields `invalid_measurement`, never a coerced negative. Freeze **both thresholds at 4.0, inclusive >=**, before the first B3-C output. There is no subtraction of a reference-image score, data-fitted offset, sign reversal or selection of a better template variant.

| Semantic flag | Instance flag | Operational outcome |
| --- | --- | --- |
| pass | pass | `both_match` |
| pass | fail | `semantic_only` |
| fail | fail | `neither_supported` |
| fail | pass | `ambiguous_instance_only` — abstain outside the three substantive states |

All raw scores/flags and abstentions remain in the denominator. These states describe only alignment with recomputed content templates. In particular, low scores **cannot distinguish missing carrier from a carrier bound to different content**. `both_match` does not imply no regeneration; `semantic_only` does not identify regeneration; `neither_supported` does not identify copy-paste. An instance-only response is not forcibly mapped into one of those stories. No cryptographic ownership or causal attack label is emitted.

For a fixed image independent of randomly chosen owner row signs, condition on its z, E, H and all other map randomness. The numerator is a sum of independent signed fixed coefficients; with the declared denominator its Rademacher moment bound gives `Pr(score>=tau)<=exp(-tau^2/2)`. At tau4 this is .000335463 per template, or at most .002683702 by a union bound for four owners and two templates **on one fixed null image**, in the ideal random-map model. Correlated VAE coordinates are allowed in this conditional argument.

This is not an empirical FPR certificate for the fixed four public owners. CLIP and VAE are both content representations; raw C0 alignment can be nonzero. The randomized row signs explain an ideal fixed-image null, not automatic decorrelation of a particular photograph with a particular public owner. Report native C0 scores for both pure and source-bypass routes; report every wrong-owner score. Reusing images across doses/channels does not create independent null samples. Images selected or optimized after seeing the owner, public re-embedding, map search and content-adaptive forgery violate the independent-image premise. An attacker can compute the same templates and run the same embedder. There is no possession secret, signed external record or authenticated origin. Public records in B2-R likewise require separate integrity protection against record replacement; they are not needed here.

## Frozen two-source experiment

Use only reserved development sources **1675 and 4795**, original input paths and SHA-256 values in `research/m1-reconstruction-dev.json`, with the identical canonical 512x512 RGB8 preprocessing. These are previously examined development photographs, not independent confirmation. Do not open held-out images. Pin and receipt the source manifest, public v5 hash profile, preprocessing helpers, CLIP assets, SD1.5 assets, scheduler configs, code and this design. Dataset license/version records remain those of the existing COCO development inventory; the source-image license is not inferred from a model license.

For each source I, freeze E(I), H(I) before embedding. Use the existing GS DDIM inversion implementation, empty prompt, CFG1, 50 inverse U-Net calls and eta0 where applicable, starting from its posterior-mode VAE latent. Denote the resulting **scaled diffusion-state** tensor by n0. It is an inverted photograph, not an iid Gaussian draw; neither Gaussian Shading's distribution-preservation argument nor its generated-image performance transfers. Run the matching 50-step empty-prompt/CFG1 deterministic forward scheduler once to obtain clipped, unquantized decoder RGB float D0. Record the actual timestep arrays and actual U-Net call counts in both directions.

Assemble T by placing `t_s(E(I))` on S_alpha and `t_i(E(I),H(I))` on I_alpha. T has RMS1 over the entire noise tensor. Freeze the **only amplitude grid** to `alpha in [0.025,0.05,0.10]`, applied equally to the two templates in scaled diffusion-state units. Supply `cast_fp16(float32(n0)+alpha*float32(T))` to each 50-step forward call. Retain the supplied tensor hashes and actual perturbation norm/rounding error. Do not renormalize after fp16 rounding or select amplitudes by a preliminary detector run. The grid spans a small-signal regime around the prospective aggregation threshold; it is an engineering hypothesis, not a power calculation for this unknown channel.

Let D_alpha be the clipped float decoder output. Save and assess both routes:

- **Pure:** `J_pure=RGB8(D_alpha)`; matched C0 is `RGB8(D0)`.
- **Primary photo candidate, initial-noise-generated residual with source bypass:** `J_hybrid=RGB8(clip(I/255 + D_alpha-D0,0,1))`; matched C0 is I.

Here `RGB8(F)=uint8(rint(255*clip(F,0,1)))`, composed in CPU float64 from the pipeline's retained float decoder outputs. Do not difference already rounded PNGs. No fitted pixel correction, score-dependent blending, quality-normalizing gain or latent optimization is added. The bypass is an explicit amendment, not a pure decoder result, and pure/hybrid variants are not two different design families. The trainable/changed scientific input is initial noise passed through all 50 denoising steps; this is substantively different from A's terminal-latent optimization and from the v5 image codec. Retain safety checks and record blocked outputs as failures.

For each route/amplitude, score matched C0 and C1 both clean and after the existing posterior-mode VAE roundtrip. This is **2 sources x 3 amplitudes x 2 routes x 2 arms x 2 channels =48 logical rows**, with 192 owner queries. Duplicate C0 artifacts may be reused and explicitly marked; they are not extra independent controls. There are two independent source clusters. Save source-to-final CLIP cosine, Hamming distance, semantic/instance template cosine and projection errors as **evaluator-only** drift diagnostics, after the blind readout. Never replace the suspect's features with the source's in the primary detector. Optional source-template scores must be named oracle diagnostics and cannot count toward passing.

This construction avoids an exact post-render cryptographic fixed-point requirement: Ks/Ki depend on the original source, while detection tolerates changes through continuous feature similarity. It does **not** guarantee feature invariance. CLIP drift, pHash bit flips, nonlinear diffusion transport and residual cancellation can all defeat the primary blind detector. An ECC64 payload could help hard-bit recovery but does not by itself repair loss of full-feature geometry, descriptor drift or the render/descriptor circularity. It is therefore deferred, not declared impossible.

## Outcomes, stopping and implementation contract

Primary clean quality remains source-referenced **PSNR>35 dB, SSIM>.9, LPIPS<.1** on saved RGB8. Human visual assessment remains missing. Report the three metrics separately as well as the joint gate. Main carrier/binding gate for a fixed route/amplitude: both sources are `both_match` clean; both retain semantic pass after VAE; all matched C0 and wrong-owner queries for that route/amplitude are below both thresholds; no invalid/ambiguous case is dropped. VAE instance pass is reported, not required or artificially weakened to force a regeneration label.

Promote the **smallest** amplitude satisfying both clean quality and that carrier/binding gate in the primary hybrid route, if any; freeze that deterministic rule now. Report every amplitude and the pure route, including contrary results. If no hybrid dose passes, retain all failures and diagnose transport versus source-feature drift before another documented amendment; do not silently widen the grid or call all noise-domain designs exhausted. A pure passing dose would be a separately promising finding and requires its own subsequent selection amendment, not substitution into the primary pilot verdict.

Promotion means expand the same frozen candidate to the remaining ten reserved sources, then run the common T3 regeneration, T4 transfer and T5 semantic-collision grid against v5 and the latent baselines. This pilot contains no T4/T5 success evidence and cannot finish M1. The intended T5 mechanism is semantic similarity near one with lower hash agreement reducing the instance kernel; the actual corpus may not supply that separation, and a 32-bit pHash has collisions. T4 whole-mark transfer likewise cannot be inferred from paired VAE survival. B3-C matched filtering alone remains unable to distinguish missing carrier from mismatched content even if the threat frequencies later differ.

Create a separate entrypoint and manifest with fixed `--manifest` and `--output-dir`, parent-reviewed and committed before use. Code SHA-256, commit and output directory are execution-time fields, not fabricated now. Expected model work: two 50-step inversions plus eight 50-step forward calls, **500 U-Net evaluations** at CFG1, with small VAE/feature evaluation overhead. Cap at **900 seconds, 10 GiB GPU allocation (or lower measured free memory minus headroom), 16 GiB system RAM, 500 MiB new outputs, USD0**. Execute only after the existing GPU task releases memory. These are local budget estimates, not measured runtime promises. No downloads or paid services are needed.

Retain per-case started/completed/failed entries, full48-row inventory with explicit missing records, source/float/tensor/PNG hashes, configuration and dependency receipts, runtime/precision/NFE, four-owner raw outputs, quality metrics and failure tracebacks in a unique development run. Flush each completed case; never overwrite earlier A/B/D outputs. On budget exhaustion stop with missing rows retained. No numerical result is a three-state success unless it came from the declared image-only interface `detect(image_rgb8, owner_id, pinned_public_profile_and_models)`.

Before GPU execution, CPU tests must cover owner serialization/domain separation, deterministic permutations, FWHT orthonormality, semantic cosine equality, exact uncompressed tensor-product kernel, projected-kernel/error arithmetic, template norms and disjoint placement, zero/nonfinite guards, 4.0 inclusive decisions and instance-only abstention, reference-free detector argument boundary, RGB8 bypass identity at alpha0, and manifest row uniqueness/counts. Tests validate implementation; only the retained experiment can establish channel survival. No learned extractor, global false-positive theorem, legal ownership claim or global impossibility conclusion follows from this pilot.

## CPU implementation handoff

`scripts/m1_blind_noise_core.py` implements only the frozen mathematics and has no image/model/GPU imports. `template(E,H,owner)` returns `coords_s`, `coords_i`, `v_s`, `v_i`, `r_s`, `r_i`, `T`, and `projection`. Coordinate arrays are int64; templates and signs are float64. The v arrays precede the final row signs. `projection` includes `input_dim`, `output_dim`, `sampling_scale`, `norm_sq`, `norm`, `variance_norm`, `template_rms`. Only immutable owner maps are cached; source/suspect features, hashes and templates are never cached.

`scores(zflat,E,H,owner)` returns raw `s`, `i`, `flags={s,i}`, `state`, `denominators={s,i}`, and `errors`. Unavailable numeric values/flags are null. `projection_diagnostic(E,H,E2,H2,owner)` returns `kernel_exact`, `kernel_projected_raw`, `kernel_projected_normalized`, `norm_sq_1`, `norm_sq_2`, `inner_error`, `normalized_error`, `delta`, `normalization_error_bound`, `variance_inner`, `variance_norm_1`, `variance_norm_2`, `sampling_fraction`. Its error bound is null for delta>=1. Diagnostics are evaluator-only and must not influence the primary score.

The 12 tests in `tests/test_m1_blind_noise_core.py` passed on the science Python with GPU visibility disabled. They include 32 fixed PCG64-seed0 product-projection pairs, independently expressed Hadamard/hash/variance references, all four owners, exact threshold boundaries, invalid/zero cases and cache/API boundaries. This is algebraic verification only. The parent-owned GPU wrapper still needs its RGB8 composition, inventory/provenance and model integration checks before execution; the core tests do not claim those checks passed.
