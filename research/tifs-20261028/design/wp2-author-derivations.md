# WP2 author derivations: top three and the payload counterexample

Codex authoring escalation, 2026-10-28. Companion to [the twelve ideas](../03-ideas.md), not the hostile review. All calculations below are analytical; no interpreter or scientific experiment was executed. Candidate claims and planning costs are conditional.

## 1. I01: what an injection-aware objective can and cannot establish

Let x be a source in [0,1]^(3HW), delta its optimized pixel residual, w the frozen owner/content chip signs, and P the frozen F5 reader projection. Define signed reader margins m_i(y)=w_i P_i(y), and loss L(y)=mean_i [max(0,4-m_i(y))]^2. For family f with native-resolution resize R_f, return resize S_f, encoder E_f and decoder D_f, define a deterministic-posterior-mode surrogate

    T_f,t,e(y) = S_f D_f(a_f,t E_f(R_f y) + b_f,t e).

E_f includes the family's own latent scaling; decoding reverses it exactly once. a and b come from the actual first native scheduler timestep, not a nominal-strength conversion. Codec-only is a=1,b=0. Mode encoding in both arms isolates injected noise in the objective but intentionally approximates native SD img2img, whose posterior sampling introduces another random draw. No statement that this surrogate equals native regeneration is warranted.

Proposed writer objective:

    min_delta L(x+delta) + E_(f,t,e) L(T_f,t,e(x+delta))
    subject to ||delta||_2 <= sqrt(3HW)*10^(-52/20),
               x+delta in [0,1]^(3HW).

At 512x512 RGB, the initial robust residual budget is approximately 2.23 in total L2, or .002512 RMS per channel. This is not final PSNR: RGB8 rounding, two fragile writes and refinement intervene. Final quality must be measured on the actual saved PNG against x.

This objective has a specific local interpretation. For one smooth margin m and a small pixel update v,

    m(T(x+v)) ≈ m(T(x)) + grad_x[m∘T](x)^T v.

The update therefore favors directions whose **signed reader response** is favorable through the chosen finite channel. In contrast, ||E_f(x+v)-E_f(x)|| can increase along either sign of a reader boundary. Equal encoder energy is not evidence of equal detectability. The local expression explains the optimization direction; it is not the failed full-chain tangent law in new notation, and it supplies no approximation guarantee for native denoising.

Three controls are logically needed. The unchanged F5 writer establishes the historical reference. A matched codec writer determines whether multiple encoders/resolutions alone explain the improvement. A matched generic blur/noise writer tests whether ordinary augmentation already explains the gain. Generic EOT and reader guidance are occupied by Guidance Watermarking and VINE; excluding that control would leave the central novelty claim unidentified.

The generic control must have equal reader-gradient evaluation counts, clean loss, projection budget, source semantics, fragile stages and final quantization. Codec/noisy-codec arms additionally match codec backward counts. Pixel augmentation cannot honestly be declared equal FLOPs merely because it has the same update count; record actual wall time and counts. Equal count, quality and a reader-guided baseline make the scientific comparison meaningful without pretending every graph has identical cost. No post-hoc increase in steps for a losing arm.

A concrete refinement contract is 150 robust surrogate updates plus 50 clean-only refinement updates for all new writer arms, with inherited fragile processing. This is an author recommendation to resolve the ambiguity in the earlier derivation, not an already frozen implementation. One clean and one surrogate reader graph per robust update must be freed sequentially; no denoiser is resident. The unchanged F5 comparator keeps its own exact retained behavior.

**Counterexample to a robustness theorem.** Let the full regenerator be G=N∘T, and let N map every image near the source to a watermark-free reconstruction x0. Then T can have arbitrarily positive margins while P(G(x+delta)) remains the unmarked score. Conversely, a denoiser may reconstruct a robust carrier whose direct noisy decode has poor scores. An objective decrease is thus neither sufficient nor necessary for native acceptance. Native outcomes and the unchanged semantic gate decide.

**Feasibility arithmetic.** Eight arms including C0, 24 sources, four cells and three seeds imply 2,304 native outputs. Three new writers imply 72 new marks. If marking has seven hours total and unchanged F5 alone uses the historical 24*119 seconds ≈.79 hours, fewer than 310 seconds remain per new mark even before v5/WAM/VINE and marking overhead. At 150 surrogate updates plus refinement this is a tight, unmeasured 24-GB workload. Serial active codec graphs may fit memory, but fit and speed are separate questions. The two-source server rehearsal must extrapolate the **complete** eight-arm inventory with 1.5-times per-unit costs and fixed retrieval reserve. If above 15 hours, stop; a new smaller pre-output protocol could be designed, but an incomplete seven-arm run does not test the proposed claim.

**Practical falsifier.** If the generic augmentation arm matches the noisy-codec arm on SDXL/K3, the native-injection interpretation loses support even if both beat F5. If noise beats codec but loses clean quality, the constrained improvement claim fails. If K3 improves, call it optimization-excluded transfer; its historical outcomes already informed this idea. A genuinely unobserved family remains a Stage C requirement.

## 2. I03: why reader response is more informative than injection energy

Write the additive channel z_t=a E(x)+b epsilon, with epsilon standard Gaussian. Under the same epsilon for clean/marked inputs,

    z_t(x_w)-z_t(x) = a [E(x_w)-E(x)].

Noise cancels in the pair difference. Its norm is therefore not a sample estimate of stochastic cancellation. A dimensionless energy ratio must at least divide by the specified b and use a declared coordinate/whitening convention. More fundamentally, energy discards the sign and orientation seen by the reader.

Consider a linear readout r(z)=u^T z-c. The perturbed latent gives

    Pr[r(a(z+v)+b epsilon)>0]
      = Phi((a*u^T(z+v)-c)/(b*||u||)).

Two equal-energy residuals v and -v have the same SNR norm but opposite effects on acceptance; a residual orthogonal to u has no effect at all. This elementary counterexample establishes what a norm-only predictor omits. It does not prove that a noisy-codec reader is a sufficient statistic for the nonlinear full pipeline.

For each reader a, freeze an affine score normalization at its operational threshold. For discrete bit readers, a normalized matched-bit margin is available; for F5, use its existing raw semantic/carrier score and retain the compound gate separately. Normalization must be fit only on the declared training/calibration partition. Candidate features are clean margin, codec margin, mean finite noisy-codec margin and its variance from four predetermined draws. For F5, forecast carrier and compound C separately: a predicted chip score cannot silently replace suspect-side semantic binding.

Use one fixed small logistic model/penalty, with no after-the-fact family-specific expansion. Prespecified controls include an intercept/base rate, family plus native-noise coordinates, clean margin, encoder gain and proxy distortion. These controls can use family identifiers where operationally available; the proposed reader-response model must beat them within observed families, while its leave-family test cannot manufacture a fitted intercept for an unseen family. Native output LPIPS is not a cheap pre-run feature: a comparator using it must be labelled an outcome-informed diagnostic rather than a deployable forecast.

**Formal limit.** Two generators can use the same E,D,a,b and hence identical finite features but different denoisers N1 and N2. Let N1 preserve a carrier and N2 erase it. The feature map is identical but labels differ; no deterministic predictor of those features can be correct on both. Therefore a general theorem of method-agnostic survival is impossible without assumptions on the denoiser. Empirical incremental prediction in a specified model population remains testable.

**Prospective design.** Source partitions are 30 fit, 10 calibration and 20 locked evaluation, all development. Every arm, cell and seed of a source stays in the same partition. Fit on design-family outcomes only for leave-family prediction; do not use K3 fit labels and then describe its evaluation as excluded. Seal numeric forecasts, code/config hashes and prediction timestamps before native outcome release. Historical knowledge means this is prospective outcome sealing, not untouched scientific discovery. New seeds are not new independent sources.

The primary comparison is paired Brier loss aggregated first within source, then over the 20 sources. A .05 improvement threshold is a practical screen; with only 20 independent source units, a confident population generalization may remain unavailable. Family/method subgroups are necessary stress tests and not separate independent replicates. A rigorous Stage C needs new sources and a new family selected without outcome-based redesign.

**Feasibility.** At one fixed cell per family, four readers, 60 sources and three seeds yield 2,160 marked native outputs, with C0 separately budgeted. Four proxy draws add reader/VAE work but no full denoiser trajectories. Reusing retained clean development marks avoids new-writer optimization. A 10–15-hour standalone screen is plausible; existing timing does not certify it. If the predictor needs full native trajectories or output quality to win, it has failed the proposed cheap-observable claim.

## 3. I05: separating carrier delivery from false attribution

Let D identify a donor record, T a distinct target record, and y be an attack candidate. Define:

    E(y,T) = quality eligible and target distinctness established;
    M(y,D) = donor carrier delivered under its frozen criterion;
    B(y,D) = donor content/record consistency criterion;
    F(y,D,T) = E(y,T) AND M(y,D) AND B(y,D).

Unconditional false attribution is Pr(F). The binding diagnostic is Pr(B | E AND M), with its actual numerator and denominator. The identity

    Pr(F) = Pr(E AND M) * Pr(B | E AND M)

shows why “zero false attributions” is uninformative about binding when the attack almost never delivers an eligible donor carrier. Conversely, high conditional acceptance among one or two rare deliveries is not a high unconditional attack success rate. Report both, with source-pair clustering. Conditioning is descriptive here, not proof of a causal binding effect.

The binding-on/off comparison must read the **same saved images**. Choosing different candidate images for each defense confounds attack search with the binding gate. A fixed candidate grid shared across defenses supports a paired comparison. If a defense-specific adaptive attack is added, give every defense the same query ceiling, include rejected queries and publish the query-success curve; it is a separately labelled stronger attack.

**Endpoint discipline.** For F5, C means semantic read plus recomputed content match; it does not demand exact donor q. A donor-attribution event needs exact donor q (Q) together with the content gate (J), and any claimed original-instance identity additionally needs the corresponding h endpoint. Report C/Q/J/h separately. For VINE, known donor-message presence is M; it is not B. A registry wrapper needs an explicitly enrolled record, and fingerprint-only verification needs no carrier. None establishes legal ownership.

**Threat access.** Primary T4 uses a marked donor image and target image; fixed patch transplantation needs no clean donor, key, decoder gradient or hidden original. Subtracting donor original from donor marked image is a stronger known-source residual attack and must be labelled separately. Primary T5 is the unmanipulated, operationally distinct target queried under the donor claim. Regenerated transplants are T4/composed diagnostics, not silently redefined T5 cases. Documented near-copy distinctions must precede outcomes; uncertain human labels stay missing.

**Feasibility.** With 24 pair units, six fixed candidates, two families and three watermark carriers, the native attack inventory is 864 outputs before controls; a fourth carrier gives 1,152. Same-output verification adds reads, not new native attacks. Patch area, blend coefficients, seeds, source pairing and the recipient-relative attack-quality gate must be fixed before output. The protocol must keep marking quality separate from attack eligibility. The existing public baseline assets fit an 8–12-hour planning envelope, but applicable external **binding** defenses may require unsupported assets or tasks. That limitation can kill this as the primary TIFS contribution even if the local attack works.

**Counterexample to the desired interpretation.** If y is simply the donor image, M and B can both be true, but E is false: this is not a false recipient attribution. If y is an independent target whose descriptor genuinely lies inside the advertised equivalence class, acceptance may expose an unsuitable task definition rather than a broken cryptographic primitive. Exact record labels and tolerated transformations must resolve that before interpreting results.

Twenty-four zero-event source-pair units have one-sided 95% binomial upper bound 1-.05^(1/24), approximately .117. Repeated scales/seeds do not turn them into hundreds of independent negatives. A successful screen needs positive attack evidence or an adequately powered later defense comparison, not a tiny zero count presented as security.

## 4. Supporting result I09: known-message acceptance is not arbitrary payload decoding

The retained VINE rule accepts an expected 100-bit message if at least 69 positions agree, equivalently within Hamming radius 31. This is a **known-message test**. If an unknown payload is uniquely decoded with guaranteed correction of every 31-error pattern, its code must have minimum distance at least 63.

For a binary code of length n and minimum distance d>n/2, the elementary Plotkin bound is M<=floor(2d/(2d-n)). One derivation sums pair distances: each of n coordinates contributes at most M^2/4 differing unordered pairs, whereas the minimum distance gives at least d*M*(M-1)/2. Rearranging yields M<=2d/(2d-n). At n=100,d=63 this is M<=floor(126/26)=4.

This worst-case guarantee supports at most four codewords, not an arbitrary 100-bit authenticated payload. It does **not** imply VINE has only two bits of average-channel capacity, nor that its stated presence test is invalid. Typical error patterns, erasures, a smaller correction radius, side information or registry-assisted known-message verification can permit different operating points. Those require a specified code, decoder, channel assumptions and measurement.

An independent-bit illustration makes a separate point: even per-bit accuracy .98 gives exact recovery of all 100 bits with probability .98^100≈.133. Real bit errors may be correlated, so this is not a forecast. A signature or MAC normally requires an exact authenticated bitstring after decoding; a public owner identifier does not act as a MAC key. Payload claims must include descriptor, pointer, authentication and ECC overhead. This is why I02 cannot borrow VINE's carrier result and declare self-contained cryptographic ownership.
