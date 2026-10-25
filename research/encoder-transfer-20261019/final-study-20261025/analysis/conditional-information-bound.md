# A conditional Gaussian-channel bound for watermark information

Status: proposed theory-author contribution, 2026-10-25. This is not an independent review, an empirical result, a protocol amendment, or a claim of mathematical novelty. No experiment or scientific interpreter was run. The derivations below are this session's own arguments. All logarithms are natural; information is in nats.

## 1. Precisely bounded reading of the motivating paper

[Ni et al., arXiv:2511.10933v1, 14 November 2025](https://arxiv.org/html/2511.10933v1), §§3–5, was opened and inspected. Its bounded additive model and content-bottleneck argument motivate the question, but do not establish a finite-strength guarantee for this study. Theorem 3.3 invokes information continuity after distributional convergence without stating sufficient continuity conditions. Assumption 3.4's conditional independence does not itself establish unconditional content independence. Algorithm 1 and §3.2 subtract the gradient of negative detection confidence, locally increasing that confidence; implementation clarification is needed. Section 4 declares 500 COCO plus 200 ImageNet images, whereas §5.1 uses a 500-image denominator without identifying that subset. Section 4 assigns 64×64 latents to 256×256 SD1.5 images; a resize or different autoencoder would need specification. Sections 4–5 describe strong regeneration and decoder guidance, not a controlled independent-encoder comparison. These are limits on interpretation and reproducibility, not evidence of misconduct or proof that reported measurements are false. No reported performance numbers are imported here.

The SD1.5 author-written model card, preserved in the [maintained checkpoint mirror](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5#training), specifies spatial downsampling by eight; consequently an unresized 256×256 input gives 32×32 spatial latents. The [checkpoint VAE configuration](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/main/vae/config.json) was also opened. The mirror explicitly disclaims Runway affiliation; this observation concerns the documented standard architecture, not proof of the paper's actual implementation.

## 2. Exact proposition

Let M be a finite-valued payload, C the complete side information furnished outside the noisy latent, and Z in R^d the clean latent. Assume:

1. M and Z are conditionally independent given C. M need not be independent of C, and need not be uniform.
2. Delta = delta(M,Z,C) is a measurable perturbation with E||Delta||² ≤ rho² < infinity. Dependence on the clean latent is explicitly allowed. An almost-sure norm bound implies this weaker energy condition.
3. X = a(Z + Delta) + sigma epsilon, where a is a fixed real scalar, sigma > 0, and epsilon is standard Gaussian independent of (M,Z,C,Delta).
4. The output Y is obtained by a Markov kernel K(dy|X,C) which is the same for every M and Z. In particular, the generator has no additional clean/marked-image reference, payload, correlated random seed, registry lookup, or feedback containing those variables outside (X,C). Its fresh randomness is conditionally independent of them given (X,C).

Then

\[
 I(M;Y\mid C)\le I(M;X\mid C)
 \le I(M;X\mid Z,C)
 \le {a^2\,\mathbb E\|\Delta\|_2^2\over 2\sigma^2}
 \le {a^2\rho^2\over 2\sigma^2}=:b.
\]

Also I(M;Y|C) ≤ H(M|C), so min{H(M|C), b} is the useful ceiling. No moment bound on Z itself is needed: conditioning fixes the host and removes its energy from the comparison. This is an average-over-C bound, not automatically a bound for every source. A sourcewise statement requires the corresponding conditional energy bound for almost every c.

### Proof

Assumption 4 gives conditional data processing. For the second step, use conditional independence and the chain rule:

\[
 I(M;X\mid C)\le I(M;X,Z\mid C)
 =I(M;Z\mid C)+I(M;X\mid Z,C)
 =I(M;X\mid Z,C).
\]

For each (z,c), choose the comparison distribution Q_{z,c} = N(az, sigma² I_d). Its mean depends on the host but not on the payload. Write P_{m,z,c} for the conditional law of X. The information-radius identity gives

\[
 \mathbb E_{M\mid z,c}D(P_{M,z,c}\Vert Q_{z,c})
 =I(M;X\mid Z=z,C=c)
 +D(P_{X\mid z,c}\Vert Q_{z,c}).
\]

The last divergence is nonnegative. Equal-covariance Gaussian KL gives

\[
 D(P_{m,z,c}\Vert Q_{z,c})
 ={a^2\|\delta(m,z,c)\|^2\over2\sigma^2}.
\]

Averaging proves the bound. Finite perturbation energy ensures the displayed KL upper bound is finite and avoids any appeal to continuity of mutual information under weak convergence.

Randomized writers are also covered: allow Delta to be random conditional on (M,Z,C), retaining Gaussian-noise independence. Convexity of KL bounds the divergence of the resulting Gaussian mixture by the conditional average of the same squared-shift divergence. Independence between writer randomness and M is not required.

For comparison, weak convergence alone cannot justify information continuity: if M is an equiprobable binary variable and V_n=M/n, then (M,V_n) converges in distribution to (M,0), yet I(M;V_n)=log 2 at every finite n. This counterexample is not the Gaussian-channel model above; it explains why a separate quantitative argument is appropriate.

### Extensions and the exact costs of missing assumptions

If M and Z are not conditionally independent, the same proof gives

\[
 I(M;Y\mid C)\le I(M;Z\mid C)+b.
\]

For discrete M, this can again be capped by H(M|C). An unconditional statement is

\[
 I(M;Y)\le I(M;Y,C)
 \le I(M;C)+I(M;Z\mid C)+b.
\]

Thus a small b does not erase information already present in the host or externally supplied condition. An extra conditioning variable S can be included by replacing C with (C,S), but independence and the perturbation bound must then be checked under that enlarged conditioning; conditioning can create dependencies. Calling a reference image “content” does not remove its information.

For an exact variance-preserving forward channel, a²=alpha_bar and sigma²=1-alpha_bar, yielding b=alpha_bar E||Delta||²/[2(1-alpha_bar)]. If the energy is uniformly bounded and alpha_bar tends to zero, the conditional MI tends to zero. This is a noise-level limit, not a statement that increasing reverse-solver steps at fixed input noise erases information. No finite-strength number is supplied without the actual latent convention, schedule, timestep and energy.

## 3. Content-derived payloads and carrier presence are different targets

If M=h(C), then H(M|C)=0 and I(M;Y|C)=0 for every possible Y. The proposition is therefore vacuous about recovery of this payload. Unconditional recovery can remain perfect: let C be a binary semantic label, M=C, and Y=C, generated entirely from C while ignoring X. Then I(M;Y)=H(M)>0 even when a=0 and the perturbation channel carries nothing.

This example separates persistence of a content label from persistence of an embedded signal. It does not prove that any real content-derived payload is recoverable: actual content extraction may be unstable, lossy, or different from the chosen C. If M=h(Z) and C is only a coarse description, conditional independence generally fails and the I(M;Z|C) term cannot be discarded.

Likewise, I(M;C|I_clean)=0 supplies no general bound on I(M;C). If C and M both equal a binary I_clean, the former is zero while the latter is log 2. Semantic preservation alone is not a statistical independence assumption.

For an owner-and-content payload, distinguish the owner/key-dependent portion from the content-derived portion. Any theorem for the residual payload must condition on all detector and generator side information and establish its independence from the clean host. A cryptographic pseudorandomness assumption is computational, whereas the displayed mutual-information bound is information-theoretic; one cannot silently substitute the former for the latter. A fixed payload across every observation has zero entropy and cannot support a message-information analysis.

## 4. A separate binary carrier-detection statement

Let B indicate whether a fixed writer was applied. Under B=0, X_0=aZ+sigma epsilon. Under B=1, X_1=a(Z+Delta)+sigma epsilon. Assume the same law of (Z,C) in both arms, fresh independent Gaussian noise, the same downstream kernel K(dy|X,C), and finite energy for the marked-arm Delta. Delta may depend on (Z,C) and a fixed or randomized payload. Let P_1 and P_0 be the induced laws of (Y,C). Gaussian KL, mixture convexity, and data processing give

\[
 D(P_1\Vert P_0)\le {a^2\mathbb E\|\Delta\|^2\over2\sigma^2}.
\]

Consequently, for any fixed acceptance rule using only (Y,C), Pinsker's inequality gives

\[
 |\Pr(\mathrm{accept}\mid B=1)-\Pr(\mathrm{accept}\mid B=0)|
 \le \operatorname{TV}(P_1,P_0)
 \le \min\left\{1,{|a|\sqrt{\mathbb E\|\Delta\|^2}\over2\sigma}\right\}.
\]

Proof detail: compare the two joint laws of (Z,C,Delta,X), augmenting the unmarked arm with the same unused Delta law. Their KL is the expected equal-covariance Gaussian shift KL. Apply the common channel to Y and discard Z and Delta. This bound does not require a random message or message independence. It controls a statistical marked-versus-unmarked advantage, not the probability of full-payload recovery, false ownership, transfer, or legal ownership. It is only as useful as its often loose energy bound.

With a uniform k-ary M independent of C and Z conditionally as above, the separate payload result also gives |P_succ-1/k| ≤ min{1,sqrt(b/2)} for a decoder of (Y,C). This follows by comparing P_{M,Y,C} with P_M P_{Y,C}, whose KL equals I(M;Y,C)≤b, and applying Pinsker to the correct-decoding event. It is a sufficient near-chance bound, not an estimate of actual performance. It does not apply to M=h(C).

## 5. Applicability to the proposed server study

- An image-domain writer followed by a nonlinear encoder can always define Delta_j=E_j(I_marked)-E_j(I_clean), but a pixel distortion budget does not automatically give a useful bound on this latent energy. A Lipschitz bound or direct future server measurement would be needed. Stochastic posterior encoding additionally requires an explicit coupling or a distributional argument; unmatched encoder draws confound writer displacement with encoder noise.
- Each encoder family has its own latent scaling, dimension and noise convention. Raw norms cannot be compared across families as information quantities without those conventions. The conditional bound is deliberately independent of the family label and says nothing by itself about signed detector alignment.
- Real img2img pipelines may carry prompt, reference-image, inversion, skip, safety or detector-feedback information outside X. Identify every such path before claiming the Markov condition. A reference depending on the marked input can make the content-only interpretation false or the enlarged conditional bound uninformative.
- Registry-assisted verification requires the registry's side information to be declared in the observation model. It cannot be compared with an image-only channel by applying the same bound without changes.
- The theory supplies neither a ranking of SD1.5 versus independently trained encoders nor a causal explanation of the retained transfer failure. It cannot replace the proposed stage-resolved server measurements. No threshold, method, empirical verdict, or experimental allocation is changed by this note.

## 6. Proposed limitations language

Our information argument concerns an explicitly specified Gaussian latent bottleneck with fresh noise and no undeclared downstream access to the marked input. It bounds residual payload information conditional on all supplied side information; it does not prove that practical diffusion editing removes every watermark at a finite strength. For content-derived payloads, preserved content may preserve the payload even after the embedded carrier is lost, so payload agreement and carrier detection require separate controls. Latent perturbation energy, generator conditioning paths, and encoder-specific scaling remain empirical or implementation assumptions. The bound is a sufficient ceiling and does not establish the mechanism of cross-encoder transfer failure.

## Sources opened

1. [Ni et al., v1 primary manuscript](https://arxiv.org/html/2511.10933v1): §§3.1–3.3, Definitions/Assumptions 3.1–3.4, Theorems 3.3/3.6, Lemma 3.5, Algorithm 1; §§4–5 and Appendix B. Paper-derived discussion is confined to section 1 above and kept below 200 words; no quotations or empirical numbers are reused as study evidence.
2. [SD1.5 model card, maintained mirror](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5#training): architecture/downsampling statement and mirror disclaimer.
3. [SD1.5 VAE config, same mirror](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/main/vae/config.json): four encoder blocks and four latent channels; inspected online, not downloaded or executed.
