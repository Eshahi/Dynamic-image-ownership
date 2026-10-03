# M1 method derivation and discriminating development experiments

Date: 2026-10-03. Status: design recommendation, not experimental evidence or a frozen confirmatory method. Author: independent method-design agent, gpt-6-astra/xhigh. Scope: existing-image route at 512x512, local USD 0 development; no held-out data inspected and no scientific runs performed by this agent. This document changes no protected requirement, source plan, claim ledger or lifecycle verdict. The parent researcher must version any adopted amendment and the actual executable configuration before running it.

## Recommendation

Start with **pure VAE-latent optimization whose saved image is the full decoder output**, using the existing v5 dual-key detector first to isolate placement from coding. Test reconstruction quality before watermark optimization. Then test a one- or two-step image-conditioned diffusion-noise suffix as a more proposal-faithful branch. Preserve the current v5 pixel codec as a comparator. Do not add a decoded residual to the source and call the result a pure latent implementation.

Run a genuinely different **initial-noise Fourier/code family** with its native inversion detector as the published latent baseline. Its image-DCT detector is a separate bridge diagnostic, not the published algorithm. The third recommended family is **progressive latent-symbol guidance with VAE-encoder extraction**, informed by the newly inspected GROW paper. It changes both the embedding mechanism and the detector's observable. **Semantic geometry modulation**, a more speculative CLIP-carrier option, remains a fourth family if needed. These choices test distinct hypotheses about where recoverable information lives; three strengths or three carrier bands of one codec do not count as three design families.

The most likely bottlenecks are cumulative: source reconstruction loss, weak latent-to-DCT channel gain, semantic-code instability, then regeneration noise. No experiment below establishes a global impossibility. A negative result identifies the measured ceiling of its pinned family, model, quality budget and development images.

## Evidence already available and what it establishes

The supplied state and reviewed local specifications establish the following exploratory facts, not new measurements in this document:

- v4 revision 2 at about 42 dB lost the mark even under the deterministic VAE cycle. This rejects that implemented full-resolution midband channel under that budget. A VAE downsampling factor alone is not a mathematical Nyquist theorem for a nonlinear learned encoder; the empirical attenuation is the relevant evidence.
- v5 revision 3, an image-domain method, obtains joint semantic-survival/content-retention counts 10/12, 10/12, 7/12, 3/12 and 0/12 for VAE and img2img strengths .05/.1/.2/.4. Its 12/12 clean result does not establish population sensitivity or a false-positive guarantee.
- Full CLIP geometry is more informative than the current 32-bit sign sketch in the saved comparison: AUC .982 versus .649 on C0, .972 versus .590 on C1. This warrants a coding experiment, not a claim that adding code bits alone solves regeneration.
- v5 already carries its code through segmented key chips; it does **not** require the v4 external helper-data route. Its public segment search and recovered-code confidence still belong in the detector's null and cost accounting.

Local sources: [redesign brief](redesign-brief-20261002.md), [A5 method](method-spec.md), [v5 amendment](method-amendment-v5.md), [semantic geometry diagnostic](v5-semantic-geometry-results-20261003.md), [acceptance](acceptance.md), [scope guard](scope-guard.md), [research contract](research-contract.md). Earlier language saying that development needs another approval is superseded by the autonomous handoff; the claim boundaries remain applicable.

## 1. Observable channel and first-principles constraints

Let `I` be the source, `o` the public OwnerID, `a` a watermark message or pattern, `G(I,a)` the embedding path, `T` a regeneration/transform channel and `F(J)` the detector's observable features. A blind verifier sees only `J=T(G(I,a))`, `o`, the fixed model/configuration and any **explicitly declared** public metadata. It does not see source pixels, source CLIP features, original hashes, generation noise or an enrollment template.

For a locally differentiable path, a small latent displacement gives

```text
delta J approximately equals J_D delta z
delta F_after approximately equals J_F J_T J_D delta z = A delta z.
```

`J_D` is the decoder Jacobian; the diffusion-suffix case replaces it by the Jacobian of suffix plus decoder. A mark can be strong in latent norm and weak in the observable `A delta z`. Changing the domain of the optimized variable does not create channel capacity. Conversely, the observed v4 failure does not imply that every latent direction is weak: optimizing the end-to-end observable can select directions missed by an arbitrary latent carrier.

A useful local experiment estimates signal displacement relative to the matched C0 path and attack residual covariance. For a detector carrier `t`, the squared separation is approximately

```text
SNR(t,delta z) = (t^T A delta z)^2 / (t^T Sigma_T t).
```

The quality constraint is on the **saved RGB8 image against I**, not `||delta z||` and not incremental decoder output. Host coefficients, VAE reconstruction error and attack-induced variation are different noise terms. Matched C0 must traverse the same reconstruction, suffix, quantization and attack path, without keyed terms or watermark optimization.

### The reconstruction bottleneck

For pure decoded outputs, `Iw=D(z)`, and the source-quality target requires some decoder output within MSE `10^(-35/10)=0.000316228` in unit-range RGB. That is about 4.535 levels RMS on an RGB8 channel scale. The ordinary posterior-mode reconstruction need not achieve it. Decoder-inversion optimization may improve it, but finite optimization does not establish the global minimum over z.

Measure posterior mode, 50-step and 100-step source-reconstruction fits before watermarking, on all preselected development images. If these remain below 35 dB, report that measured reconstruction ceiling and its SSIM/LPIPS companions. Do not silently compare Iw to the reconstructed image instead of I. A generated-image baseline whose quality claim is preservation of a sampling distribution is answering a different question from preservation of one existing source.

An alternative `Iw=clip(I + D(z_w)-D(z_ref))` can preserve source detail and uses latent-generated perturbations. It is a legitimate **hybrid latent-origin, image-output** amendment. Its final output includes a source bypass, so its success cannot establish the pure latent/noise-only output hypothesis. It may be worth evaluating after the pure route fails, with its own method ID and pixel comparator. Never apply a final pixel projection, DCT overwrite or source blend inside the pure-latent arm.

### Capacity is finite even with many DCT coefficients

Under a deliberately simplified independent real Gaussian subchannel approximation, total reliable information is bounded by

```text
C approximately equals (1/2) sum_j log2(1 + P_j / sigma_j^2) bits,
subject to the image-distortion budget and the number of usable channel modes.
```

This is a planning model, not a theorem about the nonlinear diffusion channel or the current codec. Correlated coefficients do not give independent repetitions. A useful descriptive effective rank is `(tr Sigma)^2 / tr(Sigma^2)`, estimated only on development data; it is not automatically a channel capacity. With fixed total signal energy E and m equally protected independent symbols, each symbol gets order E/m energy. Going from 32 to 512 bits or continuous coordinates can preserve feature geometry while destroying transmission reliability. Measure both losses separately.

Prioritize **one robust presence bit**, then a short robust semantic payload, then instance payload. A 256-bit cryptographic digest has no advantage if the physical channel reliably carries ten bits. Error correction trades rate for recovery; it cannot repair a channel with insufficient information or authenticate a public embedder.

## 2. Content codes, binding and public forgery

### Hashing a noisy feature is not a robust signature

A5 whole-code SHA-256 has avalanche behavior: source and suspect codes must agree within the explicitly searched neighborhood before the correct carrier is even tested. For independent Gaussian random hyperplanes applied to a fixed normalized feature pair with cosine rho, each bit disagrees with probability `p=acos(rho)/pi`. Thus, in this idealized model:

| cosine rho | bit error p | 32-bit exact agreement | 32-bit radius-1 coverage | 12-bit radius-1 coverage |
| --- | ---: | ---: | ---: | ---: |
| .97 | .0782 | .0739 | .2746 | .7597 |
| .90 | .1436 | .0070 | .0447 | .4689 |

These are calculated illustrations, not estimates of the actual Rademacher-projection code. CLIP anisotropy, the selected projection realization and dependent image pairs matter. The calculation applies to whole-code matching; v5's segmented tolerant key is a different construction. It shows why exact digest recovery can fail even when semantic cosine looks excellent. Larger exhaustive neighborhoods trade stability for candidate count, weaker discrimination and runtime.

For a coding amendment, compare three representations on saved development features before adding another GPU optimization: current 32 sign bits, a fixed 128-coordinate real projection, and the full normalized 512-vector. The real projection should be generated once with a pinned seed, normalized consistently, and evaluated by cosine rather than converted back into a hash. Measure same-instance drift, same-semantic distinct-instance separation and unrelated separation independently. These are code representations within a family, not additional embedding families.

A blind transport variant can carry an owner-mixed semantic vector or its real sketch, plus the pHash, and compare the recovered vector with the suspect's recomputed vector. For example `v_s=R_o P e(I)` and `v_i=(v_s, signed_bits(H(I)))`, where `R_o` is a public domain-separated orthogonal mixing/sign-permutation map. This explicitly changes `f` from a whole-feature cryptographic hash to a geometrically stable encoding; it is not secretly the same key definition. Carrier decoding confidence and content similarity are separate thresholds. Prototype at 32/128 coordinates, and retain 512 as a feature-only diagnostic until capacity is demonstrated.

The source pHash can be changed by the mark itself. Use one frozen signing order (source features, or post-robust-stage instance features as in v5), record it, and check the final saved image against that order. Recomputing and re-signing repeatedly until a favorable fixed point appears is a different algorithm, with its own bounded iteration rule and failure inventory.

### Public keys and what they cannot prove

If every input to `Embed(I,o)` is public and the legitimate embedder is available, an attacker can run it on a chosen image under someone else's public owner string. The resulting distribution can be exactly that of a legitimate enrollment. This is a direct constructive forgery route; collision resistance of SHA-256 does not block it. T4 resistance to a **fixed donor residual** does not imply T6 resistance to re-embedding, optimization against a public detector, or impersonating enrollment.

A keyed PRF can restrict production of a template to parties holding a secret, but changes the threat model. A digital signature can authenticate a payload against a trusted verification key, but key-to-identity trust remains external; no registry product is needed for the experiment. An exact pixel digest is fragile to regeneration. A signed perceptual code authenticates only the code's accepted equivalence class, including its measured collision/adversarial weaknesses. Signature bits and synchronization/ECC have a real payload cost. Public secure sketches/fuzzy extractors do not turn publicly observable image content into a secret signing key. These are optional separately labeled constructions, not security claims for the public-derived proposal.

## 3. Three decision states need an abstention and precise meaning

Neither two binary component detections nor full access to J generally identifies how the image was produced. JPEG, benign editing, deliberate removal and regeneration may all erase an instance component while preserving a semantic component. Regeneration may preserve both. A donor mark outside the suspect's candidate-code neighborhood may look exactly like absence of any mark.

More formally, if two histories induce distributions P and Q over all verifier observations, the optimal equal-prior binary error is `(1-TV(P,Q))/2`. If their output distributions coincide, no decision rule based only on those observations identifies the history. The public re-embedding attack above supplies a concrete case of indistinguishable legitimate and forged enrollment. This does not rule out useful discrimination for the **specific controlled T3/T4 populations**; it rules out a universal causal interpretation.

Freeze operational outputs as follows; retain the three requested interpretations as explicitly qualified names:

| Conditions, in order | Operational result | Permitted interpretation |
| --- | --- | --- |
| Valid presence; semantic agreement; instance agreement; common payload/candidate consistency | `both_match` | consistent with authentic/untouched binding |
| Valid semantic presence and semantic agreement; instance absent or fails its presence criterion | `semantic_only` | consistent with regeneration or another instance-channel loss |
| Reliable recovered mark/payload; robustly measured content disagreement outside an uncertainty zone | `content_mismatch` | consistent with content transfer/copy-paste under the tested threat model |
| Weak decoding, threshold gray zone, incompatible component candidates, or an instance-only mark | `content_uncertain` | abstain from the three interpretations |
| No reliable presence | `neither_match` | no detected evidence, not proof of an unmarked source |
| Invalid image/model/config or runtime failure | `invalid` | no scientific decision |

For the first pure-latent experiment **reuse v5's exact existing six-outcome detector and frozen thresholds unchanged**; this table constrains its wording, not a hidden threshold alteration. A proposed strict A5 blind matcher without a recovered payload has no independent T4 presence witness and therefore cannot emit the third causal label reliably. Any source-template oracle, stored enrollment vector or supplied donor template belongs in a diagnostic column only. A public pilot helps measure presence but is itself forgeable; a pilot alone cannot establish which semantic payload was transplanted.

Do not enforce an instance-only state by adding an instance-erasure loss to the attack outputs during embedding. That would optimize a desired label rather than demonstrate naturally distinct channel survival. Record actual component transitions and attack ground truth separately.

## 4. False-positive accounting

For fixed coefficients c and an independent iid Rademacher template t, the standardized statistic `Z=(sum t_j c_j)/||c||_2` has the conditional bound `P(Z>=lambda)<=exp(-lambda^2/2)`. With M tested templates, union bounding gives `lambda=sqrt(2 ln(M/alpha))`; M=442 and alpha=.01 gives approximately 4.625. This is an illustrative null model, not a replacement for the v5 statistic or its bound. Centering/normalization, informed slot weights, sign selection, payload decoding, owner search and all candidate maxima must match the actual proof assumptions.

In particular, keys derived from the very image being tested are not automatically independent random templates. Treating a public hash as a random oracle yields a modeling argument over a key/hash ensemble, not an unconditional guarantee for a fixed public configuration and adaptive image search. Disjoint frequency bands also do not prove independent component false positives. Do not multiply component FPRs without a justified joint model.

Report each C0-source, C0-matched-reconstruction and C2 wrong-owner stratum. Include K tested owners, candidate counts, decoding hypotheses and any key/config versions tried. A no-false-match result on 12, 48 or 300 independent images has one-sided 95% upper bound respectively .2209, .0605 or .00994. Multiple seeds from one source are not additional independent sources. The 12-image pilot can kill a design, locate failures and rank exploratory candidates; it cannot pass the confirmatory 80%/1% contract by assertion.

## 5. Family A: decoder-manifold DCT transport

**Hypothesis:** optimizing an actual VAE latent selects output directions that are reconstructible, and an explicit VAE-cycle/short-denoising loss retains more semantic-channel signal than the v5 pixel allocation at comparable source quality. **Amendment:** A0/A1 use the terminal VAE latent instead of initial Gaussian noise; A2 below restores a short initial-noise suffix. DCT detection is retained. A v5-derived detector still inherits v5's documented signature and low-resolution-DCT amendments.

### A0: reconstruction diagnostic, first executable task

Use pinned SD1.5 VAE, batch size one, posterior mode, and canonical RGB8 inputs. Optimize only scaled latent z; freeze model weights. Initialize `z=s_vae*E_vae(I).mode`, evaluate `D_vae(z/s_vae)`, and use the same clamp/PNG/redecode policy as A5. Use source MSE only for this diagnostic. Adam beta=(.9,.999), epsilon=1e-8, learning rate .02 in scaled-latent coordinates, 100 fixed steps, no noise resampling. Keep checkpoints 0/50/100 with every quality metric; final checkpoint is the outcome, and checkpoint maxima are explicitly exploratory diagnostics. If numerical scaling is wrong, fix the implementation and retain the failed run; do not interpret overflow as scientific infeasibility.

Order the existing 12 development IDs lexicographically; test the first four for engineering fit, then all 12 without outcome-based replacement. Record baseline PSNR/SSIM/LPIPS and latent norm/delta norm. A second deterministic retry with learning rate .005 and 200 steps is a predeclared optimization diagnosis if the first fit plateaus or diverges. These are finite measured reconstruction fits, not a certified manifold bound. Do not spend a full diffusion optimization run before this diagnostic.

Implementation receipt added after the parent launched reconstruction: the actual `m1_latent_reconstruction.py` diagnostic at commit `3dbc6a6` uses **unscaled** VAE posterior coordinates, learning rate .02, and checkpoints 0/50/100/200 on 12 sources. For scaling factor .18215 this corresponds to a scaled-coordinate displacement learning rate of approximately .003643 (apart from Adam epsilon/numerics). That is an explicit engineering adaptation of the recommendation above. The run's own manifest is authoritative; the recommendation must not be represented as its exact preregistration.

### A1: latent-to-DCT bridge and channel-aware stage

For the first bridge reuse the **exact v5 revision-3 feature, carrier, detector and decision profile**. Do not simultaneously change the semantic code. Derive source semantic targets as v5 does; optimize z with a differentiable Torch implementation of the corresponding semantic score. After the robust stage, compute the frozen instance signature according to v5 signing order, then optimize the second stage while retaining the robust losses. Final extraction runs the existing blind implementation on saved/redecoded RGB8, with no target tensor or source feature passed to it.

Candidate fixed engineering loss, with `d=MSE(D(z),I)/10^(-35.2/10)`:

```text
L = d + 100*relu(d-1)^2
  + 8 * [relu(6.0-Zs(clean))/6.0]^2
  + 8 * [relu(5.5-Zs(VAEcycle(clean)))/5.5]^2
  + 4 * [relu(6.0-Zi(clean))/6.0]^2.   # second stage only
```

`Zs` and `Zi` must be the actual standardized v5 component statistics, not cosine scores plugged into these numeric margins. If exact differentiable parity is not available, use a fixed carrier-projection surrogate and call the run a **bridge optimization diagnostic**; only the actual blind detector decides success. The source-quality penalty is a search aid, not an admissibility guarantee. Evaluate PSNR >35, SSIM >.9 and LPIPS <.1 on the actual saved result. The final result at the frozen iteration cap counts even when it violates a constraint. No final pixel correction is allowed.

Use Adam .005, 100 robust steps then 50 joint steps as the initial bounded setting; compute VAE-cycle gradients every fourth step (fixed schedule), clean terms every step. Keep the optimized source-reconstruction latent as the start. The parent may choose different settings before first execution if implementation scaling demands it, but must record the actual pre-run settings; these defaults are engineering proposals, not validated parameters.

Cheap kill order: clean C1/C0/C2 scores and saved quality; one deterministic VAE cycle; then img2img .1 and .2 with one fixed seed on all four engineering images; only surviving configurations expand to all 12 and the existing complete .05/.1/.2/.4, three-seed grid. If even source-template oracle scores after VAE do not separate C1 from matched C0 at the quality budget, more semantic-code tuning cannot rescue that physical channel. If oracle separation exists but blind detection fails, inspect feature drift and code recovery rather than immediately increasing power.

**A2, within-family proposal-faithful branch:** parameterize the image-conditioned suffix start as `z_t=sqrt(alpha_bar_t)*z_ref + sqrt(1-alpha_bar_t)*(epsilon0+u)`; only u is optimized through a deterministic one- or two-step DDIM suffix and the frozen decoder. Use a fixed empty prompt and guidance 1, and keep the same image-space objective/controls. Record t, alpha, exact suffix timesteps and seed. There is no inversion at detection. An image-conditioned short suffix is not the same as modifying an unconditional z_T at full generation time. A1 and A2 test different placement choices within the same DCT-transport family and must not be counted as two substantially different families.

GPU implementation: fp32 optimized tensor/Adam state, frozen weights, batch one, sequential transform losses with gradient accumulation, checkpoint the decoder/encoder if required, and time the first image before expanding. Frozen model weights must not accidentally detach the input gradient. Test a finite-difference directional derivative on a tiny synthetic case. If fp16 VAE produces nonfinite output, use fp32 VAE rather than silently clipping it. Avoid unrolling a full 20-step UNet graph on the first trial. Serial latent/VAE optimization is feasible to attempt within 12 GB; actual peak memory and wall time are measured, not promised here.

### Optional A-hybrid after the pure route

If pure source quality repeatedly fails, evaluate the source-bypass construction above under a distinct profile, same detection and equal source-quality budgets. Require matched C0 to include the bypass formula, and compare it with v5 at equal PSNR/SSIM/LPIPS. This can show whether a latent-generated perturbation helps the channel, but cannot close the pure-latent proposal without an explicit output-route amendment.

## 6. Family B: actual initial-noise spectral/code watermark

**Hypothesis:** ownership evidence can live in recoverable generation randomness even when the output DCT projection has little signal. Use a published implementation/algorithm and its native detector first. This family differs from A because it encodes the noise distribution/pattern directly instead of optimizing an image-DCT observable.

Recommended baseline options: Tree-Ring-Rings with published mask/key construction, or Gaussian Shading's repeated-sign/quantile scheme. The parent has already begun the Gaussian Shading adapter, so finish that native path first rather than duplicate implementation effort. Use the pinned local SD1.5 model as an explicitly disclosed model adaptation and empty-prompt DDIM inversion. Use the native recovered-noise score/message decoder, then apply the DCT core separately to the same outputs. The baseline detector knows the enrolled watermark key and model, requires inversion and does not satisfy the proposed lightweight detector. Do not replace its native detector with the DCT test and then report the baseline as failing.

First four fixed prompts/seeds may check implementation, noise recovery and the native score, but cannot evaluate preservation of the existing photos. For source-preserving comparison, invert the existing development I first, imprint the spectral pattern on its estimated noise, regenerate and compare to I; pair with the identical inversion/regeneration without the mark. This is a labeled real-image adaptation, not an unchanged published benchmark. Report failures of source preservation. Dual semantic/instance signatures can later seed two disjoint noise masks, but that is our extension with interference and capacity tests, not Tree-Ring's published result.

Cheap kill sequence: native clean detection versus matched unmarked generation and wrong keys; native post-VAE and .1/.2 regeneration; source-preservation quality for the four fixed development photos; then blind image-DCT bridge. Native detector success plus DCT failure is evidence that the shortcut loses the useful statistic, not that initial-noise embedding failed. If the baseline survives the attacks only at unacceptable source distortion, keep that tradeoff explicit.

Tree-Ring, Gaussian Shading and PRC are alternate members of this initial-noise distribution family. They are not additional independent design families just because their code differs. Published message capacities do not transfer to the lightweight DCT extractor; their recovery path matters.

## 7. Family C: progressive latent-symbol guidance, VAE-encoder detector

**Hypothesis:** guiding predicted clean latents throughout denoising makes target latent-DCT signs observable through a single VAE encode of the output, eliminating inversion while avoiding the image-DCT bridge. This differs from A's final image-DCT optimization and B's initial-noise pattern recovery. **Amendment:** robust extraction is `VAE.encode(J) -> latent DCT`, not `image J -> 8x8 image DCT`; embedding uses repeated denoising guidance rather than only initial-noise injection. A VAE is an additional neural component even if it is not a trained watermark decoder.

Use a GROW-inspired local adapter as the first pilot. The inspected paper's Eq.4-7 construct masked latent-DCT targets, alter the predicted clean latent by a loss gradient, and convert that change back into the scheduler noise prediction. Its section 5.2 defaults are alpha=.5, eta=100, 50 steps, start ratio .5, and 16 bits in the first latent channel. The paper reports COCO PSNR27.54, SSIM.85 and LPIPS.05 in Table1; these do not meet our source-quality targets and are not a source-photo reconstruction guarantee. See the full-paper inspection receipt below.

**Implementation ambiguity to resolve before claiming reproduction:** the prose says MSE, whereas Eq.5 writes a squared norm. A sum over masked coefficients, a mean over masked coefficients, and a mean over the full latent array yield different effective eta. Record the exact reduction and denominator, and match the author's code if it is inspected. Also record guidance by an explicit list of loop indices and diffusion timesteps: Alg.1 uses descending t with `t>T*r_start`, while prose descriptions of an earlier/later start can be misread. Do not silently substitute README defaults for paper defaults. An adapter with deliberately resolved choices is useful evidence, but its provenance label must say adaptation.

For a cheap channel feasibility test a fixed public 16-bit message is sufficient. It is **not** the dual-key final method. Check latent-DCT recovery on the final latent, on `VAE.encode(saved Iw)`, after a VAE cycle and after .1/.2 regeneration. That separates failures in guidance, the decoder/encoder round trip and the attack. Test wrong messages/owners and matched C0; a naive independent fair-bit bound for exact 16-bit agreement is 2^-16, but actual latent signs are neither established independent nor fair, and a public fixed message is forgeable. Its true development false-match counts must be shown.

If the channel works, extend to source-derived semantic and instance messages under public OwnerID in disjoint masks. Use the same segmented-code binding/uncertainty logic as A where possible, and increase payload only after measuring its quality and bit-error cost. Blind extraction must decode or test the suspect's own candidate messages; feeding the source message at verification is the native baseline knowledge profile, not the proposed blind extension. Use no source image or source features in the core verifier. Whether one channel becomes selectively fragile is an empirical result, not guaranteed by choosing a higher-frequency band.

To evaluate existing images, start from a fixed image-conditioned noisy latent or a declared inversion, and compare the full decoded output to I and to matched unguided reconstruction. This extension inherits the source-reconstruction bottleneck. A source bypass is a separately named hybrid here too. The controlled first test can establish feasibility even if it fails source quality; it cannot be reported as passing the proposal. Expand only after clean native detector separation, final-image recovery and quality are known. The exact adaptive schedules, mask, target, decoder scaling and guidance clipping become part of the method ID.

## 8. Optional family D: semantic-geometry carrier plus DCT instance binding

**Hypothesis:** a low-dimensional owner signal deliberately placed in the same coarse semantic representation that survives regeneration may outlive reconstructed local texture. **Amendment:** the robust semantic mark is extracted from CLIP coordinates, while the instance mark remains a DCT channel. This keeps CLIP, DCT and OwnerID but changes the proposed robust DCT-only watermark observable. It is inversion-free, not model-free or equivalent to the original detector.

Freeze a public orthogonal decomposition of normalized 512-D CLIP space into content coordinates and a small carrier subspace. Use m=8 carrier coordinates initially; derive a coarse content code only from the orthogonal content coordinates and a public owner-pattern t from `(content_code,OwnerID)`. Center carrier coordinates by a fixed development-fit mean; do not fit on a suspect image or held-out data. Optimize the pure latent z so `t^T carrier(E(D(z)))` has a target margin, while penalizing movement in content coordinates and enforcing source quality. Add the clean fragile DCT instance term only after a robust semantic signal is measurable. Enumerate the same bounded content-code neighborhood at detection or carry a content sketch explicitly; disclose that choice and its candidate count.

A public owner-derived carrier does not authenticate the owner. More seriously, CLIP-targeted optimization may create brittle adversarial feature changes rather than stable image semantics. Therefore the cheap experiment must compare clean, VAE-cycle, resize/JPEG and .1/.2 diffusion scores. Use the already fixed CLIP content-retention measure plus independent LPIPS/SSIM and, if a second pinned encoder is available, its feature drift as a diagnostic. Never describe an optimized CLIP score alone as human semantic preservation.

Kill criteria for this first variant: no clean correct-owner separation at source-quality targets, or a VAE cycle removes the margin despite apparently high clean CLIP score. If only the optimized encoder retains it and regeneration/another encoder does not, characterize this as model-specific feature bias, not semantic robustness. Parameter variants m=8/16 or EOT losses are within-family. This is lower priority than A because CLIP directions may be both low-capacity and easy for a public attacker to optimize.

## 9. Common development decision plan and M1 report

Use an immutable development manifest and commit code/config before running. Never look at held-out images to settle a carrier, threshold, prompt or strength. The first four engineering images are a fixed prefix of the existing development roster, not a favorable subset; every attempted output and failure stays in its run inventory.

For every family report: source/output quality, matched C0 quality, full detector side information, component scores and transitions, full verification runtime, negative cells, T3 dose/seed/source counts, T4 admissibility/presence/false attribution, and T5 same-semantic distinct-instance results. Test public re-embedding separately from residual transfer. Parent-source grouping determines denominators; do not pool all seeds or donor trials as independent N.

The initial six-outcome rule and inherited v5 thresholds are frozen for the first A run. A new detector family needs a pre-run calibration protocol and then one threshold configuration frozen on development/validation, with calibration-selection bias disclosed. The existing A4 acceptance contract remains authoritative for the later confirmatory manifest unless an explicit versioned amendment is adopted. Source-template oracle and enrollment-reference scores are mechanisms diagnostics only.

Recommended execution order:

1. A0 reconstruction on four, then 12 existing development images; examine source-quality ceiling.
2. A1 channel bridge with unchanged v5 detector; separate oracle physical-channel failure from blind coding failure. Test A2 only after gradients and memory are established.
3. B native baseline and source-preserving adaptation, preserving detector/model differences in the comparison.
4. C progressive latent-symbol guidance with its VAE-encoder detector, retaining all source-quality and detector changes. Try D only if a genuinely different semantic hypothesis remains useful after these measurements.
5. Only after a usable physical channel exists, replace the weak sign sketch using the feature-only geometry comparison and a capacity-aware payload experiment.
6. Freeze one final method/config/code version, or produce the three-family negative report with all measured tradeoffs. Obtain the required fresh independent M1 review and prepare the held-out manifest without executing it.

The M1 exit criterion's development route must not be summarized as satisfying the confirmatory 80%/1% bounds from 12 images. If targets are not reached, the honest package is the alternative exit: three substantially different families tried, with numeric quality and survival ceilings and the remaining amendment choices. Missing human visual assessments remain missing.

## 10. Primary-source inspection notes for literature integration

These compact notes identify methods actually opened while deriving this recommendation. They are not a substitute for the parent task's required standalone paper cards and central bibliography update. No downloaded artifact was created by this agent. The counts below belong to the papers, not this thesis's runs.

**Tree-Ring, Wen et al., 2023.** Inspected [arXiv v3, sections 3 and 4, Tables 1/2](https://arxiv.org/html/2305.20030v3). Fourier patterns modify initial noise; verification uses model inversion and a key. SD experiments use 50 generation/inversion steps, empty detection prompt and radius 10. Table 1 reports Rings clean AUC/TPR@1%FPR 1.000/1.000, attack-average .975/.694. Attacks are six image augmentations, not the current SD regeneration grid. The reported null assumes Gaussian recovered coefficients. This supports a latent-noise comparator, not a DCT shortcut or source-photo preservation claim.

**Gaussian Shading, Yang et al., CVPR 2024.** Inspected [arXiv v3, sections 3.2/3.3 and 4.1/4.2](https://arxiv.org/html/2404.04956v3). Repeated bits are randomized and used to sample Gaussian quantile intervals. DDIM inversion, inverse sampling and voting recover the message. Main configuration is 256 bits in 4x64x64 latents, with 50-step generation/inversion. Table 1 gives SD2.1 attack-average TPR .996 and bit accuracy .9724 at their stated 1e-6 FPR. Those nine attacks and native detector differ from this experiment; the distributional quality claim is not per-source PSNR preservation.

**PRC image watermark, Gunn, Zhao and Song, 2024.** Inspected [arXiv v2, sections 3.1/3.2, 4.3/4.4](https://arxiv.org/html/2410.07369v2). A keyed pseudorandom code determines initial Gaussian signs; detection uses approximate randomness recovery, including an inversion method, then a PRC test. The paper reports robust 512-bit messages and up to 2500 bits without removal attacks. Its practical finite parameters are explicitly not recommended for undetectability-critical applications. These results motivate capacity-aware coding and a separate secret-key comparator; they do not prove our public-derived construction secure or bypass latent recovery.

**GROW, Luo et al., CVPR 2026.** After the parent's primary-source discovery, inspected the downloaded full-paper text [local extraction](literature/m1-primary-extension/grow-cvpr2026.txt), sections 4.2, 5.2, Tables 1/2, from the [CVPR paper page](https://openaccess.thecvf.com/content/CVPR2026/html/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.html). This is now a verified nearest-method source for family C, not just a repository lead. Native extraction uses a VAE encoder, latent DCT and repeated-bit voting. The parent owns its download/source receipt and bibliography card. Paper/adaptation parameter and quality limits are stated in section 7; neither its reported robustness nor timing transfers automatically to SD1.5 and our attack grid.

Bibliographic identifiers for parent integration: `wen2023treering` arXiv:2305.20030; `yang2024gaussianshading` arXiv:2404.04956; `gunn2024prcimage` arXiv:2410.07369. Preserve version and access-depth notes in the paper cards. No evidence here asserts novelty or the absence of stronger newer work.
