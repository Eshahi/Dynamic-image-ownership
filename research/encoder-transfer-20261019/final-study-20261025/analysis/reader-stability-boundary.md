# Conditional reader stability: from chip approximation to compound C

Author addendum, 2026-10-25. This is outside the completed WP6/E3 independent-review scope. It supplies elementary conditional bounds, not a new mathematical novelty claim, protocol amendment, criterion, measurement requirement or implementation. No experiment, scientific interpreter or model was run. In particular, no chip-error radius, descriptor-error radius or Hessian bound has been measured or certified. All existing thresholds, H4 criteria, fits, prediction-information restrictions and missingness rules remain unchanged.

The authoritative MAIN STATE was read once. Context: [theory-design.md](theory-design.md), [prediction-contract.md](prediction-contract.md), [mechanism-server-spec.md](mechanism-server-spec.md) and [04-mechanism.md](../04-mechanism.md). Their later integrated contracts control the actual study. This note concerns one valid source/cell/seed forecast before the existing majority operation.

## 1. Actual mapping and notation

Source read as text at repository HEAD `b6219f63300514c7ff37426ee0fa641deb666c39`, with no working changes to the two reader files: `scripts/f5_latent_codec.py` (`Layout.projections`, `Reader.encode`, `soft_angle`, `_semantic_status`, `detect_rgb`); `scripts/revised_watermark_v5.py` (`_semantic_table`, `_key_test`, `_decoding_error_rate`, `_channel_result`); and its base `scripts/revised_watermark_v4.py` (`ZERO_PROJECTION`, `_content_status`). The frozen configuration selects F5 r2 soft binding, seven semantic views, and unchanged semantic radii 6/10.

There are K=320 chips, partitioned into 32 disjoint blocks of ten. Block j has two fixed sign vectors w(j,0), w(j,1), each of norm sqrt(10). They are pseudorandom sign patterns; they need not be orthogonal or antipodal, and their distinctness must not be assumed without inspecting the instantiated table. A word q concatenates its selected vectors into w(q), with norm sqrt(K).

For chip vector p with norm above zeta=1e-6, define

`T_q(p) = w(q)'p / ||p||`,

`D(p) = max_q T_q(p) = sum_j max_b w(j,b)'p_j / ||p||`.

The actual reader maximizes separately within each block. An exact tie keeps that block's bit of the recomputed semantic word q_now. This is not an ECC decoder, a nearest valid codeword correction stage or a guaranteed bit-error-correcting code. Below or at zeta, `_key_test` sets both scores to zero and returns q_now.

`read = [D >= tau_search]`, with the unchanged threshold for 2^32 times the roster size. `found` also permits the recomputed-word score to reach its lower, single-pattern threshold. Thus a recomputed-only finding does not imply read or C. C is exactly `read AND content_match`. When read is true, soft binding uses the decoded word, the suspect's continuous semantic projections, and `e(D)` from the unchanged `_decoding_error_rate`. It maximizes log likelihood on the fixed 2,000-angle grid from .001 to pi-.001. The soft distance is `32*theta/pi`: match at distance <=6, uncertain between 6 and 10, mismatch at >=10. Both uncertain and mismatch make C false.

## 2. A conditional normalized-score bound

Let `h = p_hat = p_C0 + kappa*v` and suppose, only conditionally,

`||p-h|| <= epsilon`, and `min(||p||,||h||) >= rho > zeta`.

The second condition excludes the implementation's zero-energy branch. A sufficient forecast-side version is `||h||-epsilon >= rho > zeta`. Normalization gives

`||p/||p|| - h/||h|||| <= 2*epsilon/rho`.

Indeed, add and subtract h/||p||, use the triangle inequality, and use `abs(||p||-||h||) <= ||p-h||`. Consequently, for every fixed word q,

`|T_q(p)-T_q(h)| <= B`, where `B = min(2*sqrt(K), 2*sqrt(K)*epsilon/rho)`.

The same B bounds `|D(p)-D(h)|`: for any family of functions, the difference between two maxima is at most the largest pointwise difference, and the bound is uniform in q. D is therefore stable away from zero even when its maximizing word changes. This fact is useful precisely because it does not assume decoder-word stability.

A read=false certificate is `D(h)+B < tau_search`; a read=true certificate is `D(h)-B >= tau_search`. The inequalities respect the reader's inclusive threshold. Otherwise this bound does not determine the read outcome. Large relative error when rho is small is a real limitation, not a reason to normalize epsilon by an arbitrary larger quantity. At a possible crossing of zeta, use of this smooth normalized-score bound alone is invalid.

The global fitted q90 is not epsilon. It calibrates decoded-score residuals on a specified source/grid distribution, not a uniform chip-vector error bound, descriptor bound or conditional guarantee. Nothing here turns q90 into one.

## 3. Decoded-word stability requires segment margins


Let q_hat be the word decoded from h and the C0 descriptor, and define the raw winning gap

`g_j = [w(j,q_hat_j)-w(j,1-q_hat_j)]'h_j`.

If `||p_j-h_j|| <= epsilon_j`, then the change in this gap is at most

`||w(j,1)-w(j,0)|| * epsilon_j`.

Thus `g_j > ||w(j,1)-w(j,0)||*epsilon_j` for every block is sufficient for exactly the same decoded word at p, irrespective of the recomputed-word tie preference. One may conservatively use epsilon_j=epsilon when only the global bound is assumed; no independence between blocks is required. If the two patterns differ at Hamming distance d_j, their difference norm is `2*sqrt(d_j)`, rather than an assumed orthogonal-pattern constant.

The strict inequality matters. An arbitrarily small perturbation can change a bit at a zero gap; an exact tie can also change when the descriptor's recomputed bit changes, even with identical chips. If the two patterns are identical, the bit is always tied and a chip-only strict-gap certificate cannot exist for that block. Stability then requires the descriptor's recomputed bit to remain unchanged. Failure of a sufficient condition is inconclusive, not evidence of actual instability.

The decoder's inferred e(D) is a model-based error-rate calculation from the searched score. It is not an observed bit-error fraction, an ECC guarantee, or permission to treat different blocks as independent Bernoulli trials.

## 4. Content binding is a separate conditional obligation

A stable readable word does not establish binding to the marked output's descriptor. The actual descriptor f and forecast proxy f0 can lie on opposite sides of the soft-binding decision even when p=h exactly. Moreover, with a stable word and descriptor, a change in D changes e(D), which can move the maximizing grid angle. A carrier certificate must account for this pathway too.

For clarity, the following supplies a finite-grid sufficient certificate, not a request to compute another study endpoint. Treat f and f0 as normalized, nonzero descriptor vectors. Suppose additionally `||f-f0|| <= delta`. Let R contain the actual fixed semantic-projection rows, let r=Rf, r0=Rf0, and let c_j=+1 for a decoded one bit and -1 for zero. Assume the word-stability condition above, so c is common to the two calls. For grid angle theta_l, the native likelihood term is

`L_lj = e + (1-2e)*Phi(c_j*r_j*cot(theta_l))`,

`ell_l = sum_j log(max(L_lj, 1e-300))`.

Let e_hat=e(D(h)), and define the analytical modulus

`eta = sup {|e(t)-e_hat| : |t-D(h)| <= B and t is a feasible readable score}`.

This definition uses the unchanged scalar function, including its numerical conventions; it does not suppose a derivative or empirical calibration of e. Since e is in [0,.5], the normal CDF has derivative at most 1/sqrt(2*pi), and `|r_j-r0_j| <= ||R_j||*delta`, a sufficient likelihood-error bound is

`u_lj = eta + |cot(theta_l)|*||R_j||*delta/sqrt(2*pi)`.

The term multiplying eta is at most one. Each R row is a sign row with norm sqrt(descriptor dimension); retaining its actual norm avoids a false unit-row assumption. The small endpoint angles can make this conservative bound large.

Let Lhat_lj be the proxy likelihood, `a_lj=max(1e-300,Lhat_lj-u_lj)`, and `beta_l=sum_j u_lj/a_lj`. Clipping is nonexpansive and log has derivative at most 1/a_lj over the possible clipped interval, so `|ell_l-ellhat_l| <= beta_l`. This bound can be extremely loose; its existence is not a practical certification claim.

Partition grid indices into A, where `32*theta_l/pi <= 6`, and N, all remaining indices. Define lower and upper values using ellhat_l minus/plus beta_l. Then

`max_(l in A)(ellhat_l-beta_l) > max_(l in N)(ellhat_l+beta_l)`

is sufficient for match. Reversing A and N is sufficient for nonmatch. These compare decision regions rather than requiring the identical winning angle. Strict separation avoids reliance on `np.argmax`'s first-index tie convention; the actual reader retains that convention unchanged.

Together, a read=true certificate, stable decoded word, valid descriptor bound and the match-region likelihood separation imply `C_actual=C_hat=true`. A read=false certificate alone implies C_actual=false, independent of descriptors. A read=true certificate plus the nonmatch separation implies C_actual=false. There is no claim that any of these conditions holds for the retained data or proposed forecasts. Hard-binding corrected-Hamming rules are not substituted for the frozen soft branch.

## 5. Why scalar accuracy and re-decoded score differences are insufficient

**Word-changing equal-score construction.** In any block with distinct options, write a=w(j,1)-w(j,0). The orthogonal reflection `S=I-2*a*a'/||a||^2` exchanges the two option vectors because their norms are equal. Apply S only to that chip block. The full chip norm and the maximum of its two block scores are unchanged, so D is exactly unchanged, while a strict winning bit is reversed. This uses the implemented two-option rule without assuming antipodal or orthogonal patterns. It proves that zero scalar D error does not imply zero word error. A scalar error bound therefore cannot establish the inputs to binding.

**Binding-changing equal-score construction.** Consider the reader-space case with distinct options in every block, choose a descriptor f0 whose semantic projections are all nonzero, let q be its recomputed sign word, and set p=h=w(q). The decoded score is sqrt(K), the inferred e is below .5 (at its zero-error saturation in exact arithmetic), and the word is strictly q. With descriptor f0 every signed projection c_j*r0_j is positive, so the soft likelihood is maximized at the smallest angle: match. Keep exactly the same chips but give the binding stage descriptor -f0. Every signed projection is negative; its maximum is at the largest angle: mismatch. Read remains true under the frozen single-owner threshold, while C changes from true to false with exactly zero chip and scalar-score error. This is a constructive input-space counterexample permitted by the reader mapping, conditional on the stated table/descriptor properties; it does not assert that either pair is realized by an actual image, or that all options in the instantiated study table have been checked for distinctness. It establishes the missing logical obligation, not an empirical attack. The construction describes the mathematical likelihood; finite-precision saturation can create additional ties and is another reason not to claim an executed detector result.

**Re-decoding changes the quantity being compared.** For any common fixed word q,

`D(p1)-D(p0) = [T_q(p1)-T_q(p0)] + [D(p1)-T_q(p1)] - [D(p0)-T_q(p0)]`.

Each bracketed selection excess is nonnegative, but their difference has either sign. Therefore a C1-minus-C0 difference of separately re-decoded scores is not the transported correlation with one fixed message. Background alignment, altered word selection and normalization all enter. Searching over words increases each score relative to a fixed-word score; it does not guarantee that their difference is upward biased in a particular direction. Even fixed-word normalized differences contain denominator changes, so they are not simply `w(q)'(p1-p0)` divided by a common constant.

The existing scientific conclusion remains conditional: the vector law may predict D well while failing words, semantic binding or compound C. The planned C0-proxy diagnostic and the frozen C endpoint already test distinct parts of that chain. These bounds explain why they cannot be replaced by scalar accuracy; they add no new requirement and supply no new pass verdict.
