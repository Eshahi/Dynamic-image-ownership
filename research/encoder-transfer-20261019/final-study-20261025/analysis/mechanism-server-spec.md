# Future-server mechanism and forecast implementation specification

Status: research-only design, 2026-10-25. No implementation, experiment, image operation, model import, timing, package installation or server connection was performed. This specification supplements WP5; the final integrated protocol controls sample selection, hypothesis tests and spending. Existing F5 r2, v5 r3, WAM, VINE-R, thresholds and published stage-2 conclusions remain unchanged.

## 1. Work and information boundaries

Phase A uses the 60 already-consulted development sources, sorted by SHA256 of UTF-8 `et-final-law-split-v1/` followed by the canonical decimal source ID; break a hypothetical hash tie by numeric ID. The first 30 are fit sources and the last 30 calibration sources. Pilot first six and mechanism first twelve use that same order. The primary F5 forecast grid is R0/R1 at .1/.2/.4, seeds 12/13/14: **1,080 source-cell-seed tangent measurements**. K3 never enters fitting or calibration. Phase B uses 200 fresh sources, seven cells (the six R0/R1 cells and native K3 .2), three seeds: **4,200 F5 tangent measurements**. Optional frozen FLUX adds 600. These counts exclude C0 generation, input encodings, reader passes, descriptor extraction, quality assessment and the mechanism controls below.

For a forecast, allowed inputs are the clean source, the final stored marked INPUT, their exact attack-encoder displacement, the target's C0 trajectory and its derivatives, C0 chips, C0 seven-view semantic descriptor, explicit noise tensors and frozen reader/profile. Forbidden inputs are **all marked TARGET outputs**, including pixels, qualities, chips, scores, descriptors, decoded words and finite differences obtained by regenerating perturbed inputs. In Phase B, finish and freeze every required law and quality-baseline forecast before producing/releasing any marked target outcome. Creating the marked input is permitted and distinct from creating its regenerated target output.

Use `prediction-contract.md`: `p_hat=b+kappa*v`; one global unconstrained OLS kappa, then a separate global q90 (28th of 30 source-max absolute margin errors, in native score units). Apply the prospective `training-missingness-design.md` coverage floors, original observed-vector weights and infinity for incomplete calibration source maxima. An infinite radius is uninformative but does not alone invalidate the point predictor. No family intercept, strength coefficient, learned descriptor proxy or residual library. Run the unchanged semantic reader on `(p_hat,f0)`. Apply the three-seed majority to its Boolean predictions. This deterministic majority is the Brier forecast, not a calibrated probability. H4 retains <=.10 absolute source-rate error **in every frozen cell** and >=20% Brier improvement over the frozen C0-quality baseline. Missing predictions are never imputed; the final statistical contract permits only explicitly labelled worst-completion support for sporadic abstentions, with incomplete-measurement flags. Structurally unsupported required paths remain disqualifying.

The integrated `quality-baseline-contract.md` supersedes the earlier provisional one-feature comparator: six allowed quality features, source-majority logistic target, training-only standardization, unrestricted slopes and the fixed penalized objective/solver in that contract. Inputs are the three C0-versus-original quality medians and three marked-input-versus-original qualities; no marked target metric is permitted. Fit on the same 30 fit sources/six R0/R1 cells, and freeze before confirmation. Validation weights are 1/9 for each R0/R1 cell and 1/3 for K3; with the optional eighth family, 1/12 for each R0/R1 cell and 1/4 each for K3/FLUX. Outcome-missingness sensitivity bounds from the integrated statistics contract are additional requirements; they do not make missing forecasts valid.

## 2. Native K3 audit: no established codebook obstruction in the pinned path

The pinned [diffusers v0.35.1 K3 pipeline](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/kandinsky3/pipeline_kandinsky3_img2img.py) explicitly encodes with `movq.encode(...)["latents"]`, passes that four-channel tensor into `prepare_latents`, and decodes with `force_not_quantize=True`. The four-channel branch bypasses the helper's posterior-sampling branch. Do not infer K3 sampling from that unused branch or multiply its native latents by a VAE scale merely because a helper docstring mentions scaling.

In pinned [VQModel](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/models/autoencoders/vq_model.py), `force_not_quantize=True` bypasses nearest-codebook quantization when `lookup_from_codebook=False`; otherwise it requests codebook lookup. The local installed source was also read as text and shows the same native decode flag and conditional branches. `scripts/encoder_transfer_runtime.py:383-407` uses bypassed decoding for D3, and its R3 wrapper invokes the native pipeline. Thus **R3 quantizes while D3 does not is not supported by this audit**. The future adapter must assert the loaded configuration and executed branch; no model was loaded here. A direct online read of the abbreviated model-revision configuration failed, so checkpoint-specific configuration is a preflight check, not a fact established here.

Require `lookup_from_codebook=False`, deterministic four-channel MoVQ input latents, exact decode kwargs, source revision `bf79e6c219da8a94abb50235fdc4567eb8fb4632` and the approved loaded-file identities. Record executed quantizer/lookup call counts; both must be zero. If an authorized native adapter actually requires hard quantization, the literal derivative is piecewise zero (boundary behavior is discontinuous); a training straight-through gradient is not its mathematical derivative. Keep that native endpoint and explicitly name any no-quantizer floating surrogate. Do not silently certify the law with it. Unexpected quantization is an adapter mismatch; unresolved JVP compatibility makes the relevant family forecast unsupported. Native-versus-surrogate chip residuals, margin errors and C disagreements remain falsifiers.

K3 uses native DDPM reverse randomness. The [pinned DDPM step](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_ddpm.py) can clip the predicted original sample and inject a draw at each positive timestep. Its predicted-variance branch, if used by the loaded configuration, is part of the differentiable step. Preserve these operations and all actual timestep indices; four nominal updates do not imply four interchangeable SNR levels.

## 3. Minimal additions to the existing runner

Reuse `encoder_transfer_test.py::plan`, `unit_id`, `Journal`, `majority`, the detection wrappers and `encoder_transfer_runtime.py` model loaders, budget checks, release and memory reporting. Reuse the immutable-base/hash pattern of `encoder_transfer_amend_2b.py`, asset pinning, and `encoder_transfer_adapter_check.py` preflight-report pattern. The historical loader accepts development only and n<=120: introduce an explicit final-study schema/phase validator, **do not relax its historical contract in place**. Do not copy inherited historical outcomes into a fresh-source experiment.

Add only small adapter/forecast helpers, an explicit forecast stage and additional journal fields. No new broker, authority service, job system or confirmation infrastructure is needed. Proposed interfaces below are specifications, not runnable code:

```text
InputPair(source_id, source_rgb8_ref, final_mark_rgb8_ref, arm, split)
CellSpec(id, family, exact_strength, native_shape, schedule_config_hash,
         ordered_timesteps, precision_spec, preprocess_spec, posterior_kind)
NoiseBundle(source_id, cell_id, seed, posterior_eta_or_null,
            injection_epsilon, ordered_reverse_innovations,
            tensor_shapes_dtypes_hashes, native_generator_state_receipt)
C0Trace(unit_key, native_output_ref, native_primal_states_ref,
        surrogate_primal_states_ref, noise_bundle_ref, adapter_fingerprint)
ForecastInputs(pair, cell, noise_bundle, c0_trace, frozen_reader_ref)
ForecastRow(key, b[320], v[320], p_hat[320], f0_ref,
            predicted_read, predicted_content_match, predicted_C,
            decoded_margin, interval, baseline_quality, validity, reason)

make_noise_bundle(cell, source_id, seed) -> NoiseBundle
encode_input_pair(pair, cell, noise_bundle) -> {z0,z1,d,posterior_terms}
trace_c0(source_input, cell, noise_bundle) -> C0Trace
transport_jvp(c0_trace, d, cell, frozen_reader) -> {v,stage_gains,diagnostics}
predict(forecast_inputs, frozen_kappa_q90) -> ForecastRow
freeze_forecasts(all_required_keys, rows, baseline_rows, model_hash) -> receipt
evaluate_after_freeze(receipt, outcome_rows) -> scores_and_diagnostics
```

`ForecastInputs` cannot accept a generic result journal or target-output path. Native generation/evaluation and prediction have separate entry points. One ordinary immutable forecast file plus a content hash, expected-key inventory and timestamp/commit receipt is sufficient. The target-outcome stage checks that receipt before starting. Do not trust a timestamp alone: compare key coverage, model/config hashes and stored forecast-file hash on resume.

Journal keys include phase, source, arm, cell, seed, stage and direction, so stage records cannot overwrite native outcomes. Preserve append-only state transitions and last-row-per-ID reduction. A `generated` transition followed by `ok` is one unit. Retain terminal scientific errors and safety blocks, and torn-tail evidence; do not retry them to obtain a favorable endpoint. A technical preflight fix requires a recorded pre-outcome revision and repetition of affected preflight checks, not deletion of its failure.

## 4. Explicit coupling, including the sampled posterior

Generate the C0 random draws in the same order/dtype/device as the pinned native adapter from seed 12, 13 or 14; capture the actual tensors and replay them for all C1 arms within that source/cell/seed. The seed is a label, not the evidence of coupling. For mode interventions, reuse the native bundle's corruption/reverse draws even though no posterior sample is consumed. This fixes the historical mode-versus-sampled RNG-consumption confound. Distinct families may have different shapes and draws; do not claim identical cross-family noise.

For an SD-family encoder with native scaling included, record `m0,m1,s0,s1,eta`. The exact paired input displacement is

`d = (m1-m0) + (s1-s0)*eta`.

Mode sets the second term to zero. Native MoVQ is deterministic and has no invented posterior eta. For DDIM/DDPM injection, `u0=a_t*z0+b_t*epsilon` and `du=a_t*d`. Common epsilon cancels only in this initial paired difference; it still determines the C0 trajectory and its derivative. If a reverse innovation coefficient depends on the state/model prediction, differentiate that coefficient too. Even for state-independent coefficients, reverse noise changes subsequent primal states and therefore subsequent Jacobians. Reusing one initial epsilon without all reverse innovations is insufficient.

Make the bundle from C0 before marked target generation. Reject missing, extra, reordered, shape-mismatched or dtype-mismatched draws. Float precision and kernel ordering can change native random consumption; verify the captured/replayed adapter against its unchanged native call in the development pilot. Snapshot explicit tensors on the server; IDs/hashes plus the pinned generator contract support resume, but a seed-only receipt does not establish bitwise noise equality.

## 5. Tangent propagation without 320 backpropagations

The forecast is a floating-path approximation to an RGB8 pipeline. Literal integer rounding is locally constant and is not differentiated. Preserve native weight files, input conversions when forming exact `d`, continuous normalization, resize kernels, clipping and denoising arithmetic; state exactly which casts/rounding and implementation kernels are replaced by a differentiable real-valued surrogate. Native C remains evaluated on the original saved RGB8 path. The background b and semantic proxy f0 come from its native C0 output. Record the floating C0 chips separately: their discrepancy from b is part of the approximation, never silently absorbed by a fitted family offset.

Preferred JVP is one forward tangent through one tensor-valued step, not a full Jacobian or 320 coordinate gradients. Scheduler state is part of the state tuple, including prior model outputs for a multistep solver. Treat conditioning and the replayed noise bundle as fixed inputs. Use cached/recomputed C0 primals, free each step's graph, and preserve the tangent between steps:

```text
state, tangent = C0_initial_state, (a_t*d, zero_scheduler_state_tangents)
for step_index,t in ordered_native_timesteps:
    primal = C0_surrogate_state[step_index]
    next_state, tangent = JVP(
        pure_native_step(state, t, fixed_conditioning, fixed_noise[step_index]),
        primal, tangent)
    assert next_state agrees with cached surrogate C0 next_state
    discard this step's AD graph
image_float, image_tangent = JVP(floating_decode_and_resize, final_primal, tangent)
chips_float, v = JVP(frozen_F5_encode_and_chip_operator, image_float, image_tangent)
p_hat = native_C0_chips + kappa*v
prediction = unchanged_semantic_reader(p_hat, native_C0_semantic_descriptor)
```

The main law uses the **exact finite input-encoder displacement d**, not an encoder JVP. This avoids approximating that permitted input difference. Differential control experiments below use encoder JVPs deliberately, with a different label. The downstream JVP remains around C0 in both cases. A recurrent state implementation must not detach an intermediate tangent or omit scheduler/history coordinates. A parameter-gradient disabled model can still allow derivatives with respect to inputs; an enclosing inference-mode/no-grad wrapper cannot be assumed compatible with the chosen AD method.

The final chip map need not be differentiated through NumPy. `f5_latent_codec.py::Layout.projections` is a fixed linear float64 DCT/slot/weight/sign/reduction operator A. Obtain the SD1.5 reader-encoder latent tangent with AD, then apply the existing A to that tangent directly: `v=A(z_tangent)`. This preserves the frozen chip ordering and normalization and avoids a silent gradient break at the native tensor-to-NumPy conversion. Compare the same A on primal latents in the server pilot. The discrete decode, soft-binding search and majority are applied only after chip prediction; no derivative through those decisions is required.

Attention/SDPA kernels, custom operations, offload hooks and mixed precision may not support forward AD. Freeze a deterministic attention implementation during the pilot; a math-attention fallback must pass primal-equivalence checks and be fingerprinted. If forward AD fails, an exact AD reverse-over-reverse JVP may be tried within the same pilot cap; measure its memory and count its extra derivative work. It is not 320 independent backwards. Do not switch to finite differences, straight-through codebook/rounding gradients, quantized weights, shortened schedules or a different checkpoint to make H4 run. Unsupported adapters leave H4 unresolved. fp32 denoiser/tangent variants are separately declared surrogates, not native fp16 claims. A 4090 fit is **not established** by these interfaces; all-forward generation timings do not predict AD feasibility.

After release, compare actual chip change against v and kappa*v; report normalized vector error, direction cosine, decoded margin residual and compound C errors. Also evaluate `C(actual_chips,f0)` against native C to separate proxy disagreement from carrier-prediction disagreement, preserving their joint error table. Neither diagnostic may repair a Phase-B forecast.

## 6. Bounded twelve-source mechanism module

Take the first twelve development sources in the fixed identifier-hash order, before new measurements. All four marked arms enter encoder-gain and stage-primal measurements. The F5 transfer-law reader and full-chain differential controls are F5-only; reading another method's residual with F5 does not measure that method's native payload retention. No additional watermark writers are introduced.

For each final residual `delta=(mark_rgb8-source_rgb8)/255`, use five directions: actual delta, two independent norm-matched Gaussian controls, two independent Fourier-phase controls. All directions use the common 512 RGB coordinate system; each encoder's native preprocessing is subsequently applied. Controls are **differential directions, not synthesized valid marked images**. This avoids clipping, which would otherwise destroy claimed norm/spectrum matching.

Exact construction on the future server:

1. Compute per-channel spatial mean mu and zero-DC component `r=delta-mu`. Preserve mu in every control. Thus randomized components have exactly zero DC, while full controls retain the real residual's DC. This is deliberate: forcing full controls to zero DC would not exactly match a nonzero-mean residual's spectrum/norm. Record the DC-energy fraction and state this convention.
2. For each of two Gaussian replicates, draw independent standard normal entries, subtract each channel's spatial mean, and normalize each nonzero channel to `||r_channel||_2`. Add mu. A zero-energy channel has a zero randomized component. This matches per-channel AC energy and full residual norm, without a Gaussian distribution claim after normalization. Distinct draws are independent; they are not an antithetic pair.
3. For each phase replicate, take an orthonormal full 2-D DFT of each real r channel. Partition frequencies into conjugate pairs under `(k,l)->(-k mod H,-l mod W)`. Set DC exactly zero. For every non-self-conjugate pair choose one uniform phase in [0,2*pi), assign `|F(k,l)| exp(i*phase)` at its canonical representative and the complex conjugate at its mate. At self-conjugate Nyquist bins choose a real independent sign times the original magnitude. The inverse must be real to numerical tolerance. Add mu. This preserves the per-channel Fourier magnitude including the retained DC and hence norm by Parseval. Do not randomize redundant `rfft` boundary entries independently; that breaks Hermitian symmetry.
4. Derive control RNG seeds from SHA256 of the literal UTF-8 string `et-final-mechanism-v1|source_id|arm|control_kind|replicate`, taking the first eight digest bytes unsigned little-endian. Use a pinned CPU PCG64 generator and float64 construction on the server. Store generator/library versions and final direction hashes. No candidate seed search.
5. Never clip or rescale the constructed controls after the matching step. Report what fraction of `x+direction` would leave [0,1]. If a separate image illustration is ever approved, a clipped version must get a new ID with its effective direction, norm and spectrum error; it cannot replace the differential control or be described as exactly matched. Actual stored delta remains the law input throughout.

These Fourier controls match each channel's marginal power spectrum, not the cross-channel phase/coherence or full joint color spectrum. The independent phase draws intentionally alter that structure; label this limit instead of calling them identical-spectrum controls without qualification.

For each encoder report the directional gain `||J_E(x)u||/||u||` with native input/latent scaling and dimensions. For actual delta also report exact finite gain `||E(x+delta)-E(x)||/||delta||`; those are different estimands. For F5 at native .2, propagate all five directions through the complete surrogate around shared C0 trajectories and report `||v||`, signed alignment `e'v`, and `e'v/||u||`, with `e=w(original_q)/sqrt(320)`. Norm gain without orientation is not read survival. Undefined zero denominators stay null with reasons, not fabricated zeros.

### Stage isolation and count ledger

Use source, seed, conditioning, preprocessing, precision and explicit random bundle consistently. At .2, retain these stage outputs for C0 and all four real marks; no control directions become images:

| Stage | Definition | Scheduled primal outputs in 12-source module |
|---|---|---:|
| Preprocess | Native resize/normalize/inverse conversion with no model; record once per distinct path | 60 per distinct path; shared paths reused |
| Mode codec | Native encoder mode/deterministic MoVQ, then native decoder | 12 x 5 inputs x 3 families = 180 |
| Sampled codec | SD1.5/SDXL sampled posterior using paired eta, no corruption/reverse steps | 12 x 5 x 2 x 3 seeds = 360 |
| Noise-only direct decode | Decode `a_t*z_sample+b_t*epsilon`, omit all reverse steps; K3 z deterministic | 12 x 5 x 3 x 3 = 540 |
| Mode plus noise plus native reverse | Mode input; same epsilon/reverse innovations as native sampled path | 12 x 5 x 2 SD families x 3 = 360; K3 reuses native |
| Native sampled/deterministic full path | Unchanged R0/R1/K3 .2 with explicit paired draws | 12 x 5 x 3 x 3 = 540; 360 R0/R1 outputs already in main Phase A |

Noise-only direct decode is an off-distribution diagnostic, not a useful attack or a pure causal intervention that preserves quality. Its contrast with the matching sampled full path isolates adding the specified reverse program, conditional on these inputs/draws. Mode-versus-sampled full paths isolate the posterior draw under shared downstream noise. Different families still change many components together; no row establishes encoder-training independence as the cause.

The stage module adds **1,620 primal outputs** beyond R0/R1 main-grid reuse (180+360+540+360+180), plus distinct preprocessing controls. Count encode/decode/denoiser work separately; these are output counts, not equal-cost units. Reuse matching C0/input encodings and scalar stages. No three-seed duplication is invented for deterministic mode codecs.

Directional workload: **720 mode-encoder JVPs** (12 x 4 arms x 3 encoders x 5 directions). Full-chain directional workload is F5-only **540 JVPs** (12 x 3 families x 3 seeds x 5 directions), not 2,160 for all four arms. The 72 actual-direction R0/R1 law measurements already exist in the 1,080 main Phase-A budget, but their exact-input-displacement tangent is not identical to the differential-encoder tangent. Therefore count conservatively: **540 additional differential full-chain JVPs** unless the implementation explicitly reuses only the downstream primal work; do not subtract 72 scientific measurements with different initial directions. K3 .2 diagnostic directions stay outside kappa/q90 fitting. This is the cheapest fixed subset here; extending full-chain controls to all methods or strengths requires a later design, not automatic scaling.

## 7. Future CPU test specification and server adapter pilot

No tests were run here. Implement CPU tests with tiny analytic arrays/stubs after approval, before renting substantive compute:

- Schema rejects Phase-B outcome fields/paths as forecast inputs; a fake accessor proves no predictor opens outcome files. Freeze fails on a missing/extra key, stale config/model hash or modified forecast file.
- Hash-order splitting is stable under input-list permutation; source/group exclusion, 30/30 assignment and 12/6 subsets are disjoint or nested exactly as declared. Duplicate source IDs cannot inflate n.
- Journal replay keeps only the final state per identity, preserves torn-tail evidence and cannot count generated/ok twice. Terminal scientific failures remain terminal.
- Majority tests include two successes plus missing, one success plus two missing, all missing, duplicate seeds and an unexpected seed. Forecast missingness is distinct from observed attempt failure.
- The sampled-encoder toy example checks both mean and variance displacement; explicit-noise replay still works when a mode path consumes no posterior draw. Mutating/reordering any reverse draw is detected.
- Analytic two-step linear and nonlinear recurrent toy systems check full JVP/state-history propagation, shared stochastic increments and state-dependent noise coefficients. A zero tangent stays zero. No image finite-difference predictor test is introduced.
- Schedule fixtures assert actual timestep arrays, initial alpha/sigma, final-step conventions and exact update count for every frozen native cell. A mismatched scheduler cannot pass because its strength label matches.
- Reader fixtures check decoded-versus-recomputed branching, tie rules, zero chip norm, content mismatch despite read=true, and the unchanged 6/10 content radii. C is `read AND content_match`, never a score-only endpoint or A.
- kappa OLS checks original source/cell weights, zero denominator, negative kappa and the exact coverage-qualified incomplete-fit boundaries. q90 checks the 28th order statistic of all 30 source maxima, with incomplete maxima represented by an explicit positive-infinity sentinel; test zero through three incomplete sources and reject conversion of q90 into a probability.
- Gaussian/phase toy arrays verify retained DC, zero-DC randomized component, norm/spectrum identities, conjugate pairs, real Nyquist values, independent seeds and zero-energy channels. Bounds violations are reported without clipping.
- Native rounding fixtures include half-integer ties and clipping endpoints; each path retains its pinned rounding rule. A floating derivative cannot be labelled RGB8 derivative. Quantizer/lookup stubs cause the required adapter failure instead of an implicit straight-through fallback.
- Brier aggregation uses source-majority labels, fixed family/cell weights, every-cell rate errors, B_Q=0 handling and the exact A/Q/S worst-completion bounds. Test structural unavailable-path/fit invalidity separately from sporadic forecast abstentions, preserve undefined point scores as NA and test the distinct full-delivery flag. A floor predictor and a deliberately failing single cell ensure pooling cannot hide failure.

On the **future authorized server only**, use the first six fixed development sources (never held-out) for a maximum **two-hour** feasibility pilot inside WP5's approved total ceiling. Existing adapter checks become stronger checks of native-versus-replayed C0 outputs, tensor coupling, configured precision and model source identity. Check .1/.2/.4 schedule boundaries; one end-to-end F5 tangent at the longest SD path; K3 decode branch and native DDPM replay; reader float/RGB8 discrepancy; memory and stepwise graph release; and the frozen attack adapters separately. Use native/surrogate relative state-error tolerance 1e-4 where arithmetic/kernels are stipulated identical; if a precision/kernel surrogate exceeds it, record mismatch and stop that adapter rather than widening the tolerance. Native RGB8 replay should match exactly under identical deterministic execution settings; otherwise record and diagnose before any study release. Tolerances certify implementation consistency, not prediction accuracy.

The pilot may inspect technical state and timing, not choose scientific settings from marked target detection. Stop at two hours or the budget reserve, whichever comes first. If JVP does not fit/support the declared path, freeze `unsupported` for that family and preserve H4 as unresolved. Do not replace it with marked-target finite differences. Core empirical endpoints may still be worthwhile, but the protocol must disclose the lost mechanism claim before Phase B approval.

## 8. Handoff and evidence limits

The later implementer must supply a committed final-study contract, explicit per-phase key inventory, frozen model/reader/adapter fingerprints, Phase-A fit/calibration outputs and the attack freezes. Phase B cannot start until the user's required approval and these artifacts exist. The main integrated protocol supplies exact machine choice, total money/hour ceiling, download consent and stopping/retrieval reserve; this note grants none of them.

Source access in this contribution: the authoritative MAIN STATE was read once; the theory, prediction and reader contracts, WP3 attacks, WP4 family choice, BRIEF, existing runtime/planner, amendment builder and adapter-check code were read as text. Direct web opens on 2026-10-25 inspected the three pinned primary code URLs above; no search query or code download was made. Local installed K3/VQModel source was read without invoking its interpreter. The failed Hugging Face configuration URL is preserved here as an unresolved access check. No raw result journal or held-out image was opened. Proposed interfaces, counts, Fourier controls and tests are design work, not measurements.
