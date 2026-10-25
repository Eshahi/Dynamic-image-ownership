# Distribution fidelity does not determine paired fidelity or readable direction

Status: bounded author derivation, 2026-10-25; outside the WP6/E3 package. This note changes no method, attack, baseline, threshold, protocol or empirical verdict. It claims no mathematical novelty. No experiment, fitting or scientific interpreter was used. All logarithms are natural and divergences are in nats.

## 1. Preserve the fixed-pattern calculation

The [SERUM author manuscript](https://adam-dziedzic.com/static/assets/papers/serum.pdf#page=16), Appendix B.1–B.3, PDF page 16, explicitly treats a fixed normalized pattern $a\in\mathbb R^d$, $\|a\|^2=d$. For $P=N(0,I_d)$, independent fresh $Z\sim P$, and $0<\alpha<1$, its insertion gives

\[
 Z'=\sqrt{1-\alpha}Z+\sqrt\alpha a,
 \quad Q_a=N(\sqrt\alpha a,(1-\alpha)I_d).
\]

Gaussian KL yields

\[
 D(Q_a\Vert P)=\tfrac12[-\alpha d+\alpha\|a\|^2-d\log(1-\alpha)]
 =-\tfrac d2\log(1-\alpha).
\]

Thus $\alpha=1/2,d=16384$ gives $8192\log2\approx5678$. The appendix's spatial GaussMarker comparator is the Gaussian restricted to a fixed orthant: $Q_O(dx)=2^d1_O(x)P(dx)$, giving $D(Q_O\Vert P)=d\log2$. These are correct conditional distribution calculations. Their ordering needs no correction. “Lower” is comparative; thousands of nats do not supply a small-divergence guarantee.

## 2. A smaller input KL does not rank output KL

Fix the prompt and all other supplied conditions $c$. If the same generator is a Markov kernel $K_c$ for both laws, data processing establishes

\[
 D(QK_c\Vert PK_c)\le D(Q\Vert P).
\]

This is an individual upper bound, not an ordering theorem for competing inputs. An exact two-dimensional counterexample uses $P=N(0,I_2)$, $Q_1=N((1,0),I_2)$, $Q_2=N((0,2),I_2)$, and $K(x_1,x_2)=x_1$. Input divergences are $1/2<2$, whereas output divergences are $1/2>0$. The channel discards the direction accounting for the larger input discrepancy.

Consequently, the SERUM input comparison alone cannot establish a lower output KL or lower FID. FID introduces a separate feature/moment functional, and neither that functional nor same-image distortion follows from the displayed inequality. This logical limit does not dispute any measured FID result. If prompts or side inputs differ between arms, even the common-kernel premise needs restoration by specifying their joint laws.

## 3. Marginal fidelity leaves source coupling unspecified

Let a one-dimensional source $U$ be uniform on $\{-1,+1\}$. Two outputs $Y_1=U$ and $Y_2=-U$ have exactly the same marginal distribution as $U$. Both output-to-source-marginal KL divergences are zero, but

\[
 \mathbb E(Y_1-U)^2=0,\qquad \mathbb E(Y_2-U)^2=4.
\]

The distinction is the joint source-output coupling. A distribution-level guarantee therefore cannot replace paired fidelity measurements. Likewise, equal latent KL need not imply equal reader behavior: under $N(1,1)$ and $N(-1,1)$, KL to $N(0,1)$ equals $1/2$, while a fixed positive-threshold reader responds differently. Magnitude lacks the signed direction that a specified reader uses. These are abstract counterexamples, not models of measured SERUM outputs.

## 4. Fixed secret and key-marginal laws answer different questions

Let $A\sim\pi$ be a random secret, $Q_a=\mathcal L(Z'\mid A=a)$, and $Q=\int Q_a\pi(da)$. For finite expected KL and a common reference $P$, splitting $\log(dQ_a/dP)=\log(dQ_a/dQ)+\log(dQ/dP)$ and averaging proves

\[
 \mathbb E_A D(Q_A\Vert P)=I(A;Z')+D(Q\Vert P).
\]

An idealized example takes **unnormalized** independent $A,Z\sim N(0,I_d)$ in the same insertion formula. Then $Q=P$, yet $I(A;Z')=-d\log(1-\alpha)/2>0$. Averaging over secrets hides the marginal shift while preserving secret-observation dependence. A fixed secret reused across images is not independently resampled per image; the joint multi-image law must retain that shared variable.

This idealization is not actual normalized SERUM. Section 3, PDF page 4, [defines centering and standardization before fixing the pattern](https://adam-dziedzic.com/static/assets/papers/serum.pdf#page=4). Across hypothetical random pattern draws, normalized coordinates are dependent, their sum is zero, and their squared norm is fixed under Appendix B's convention. They are not iid Gaussian. Indeed, projection onto the normalized all-ones direction gives variance $1-\alpha$ for $Z'$, not the reference variance one. The exact Gaussian-marginal conclusion cannot be imported.

The companion [conditional-information note](conditional-information-bound.md) makes the corresponding operational requirement explicit: name every condition and side-information path. A fixed-pattern detector, a detector supplied a secret, and an observer averaging over unknown secrets have different observation models. Distribution similarity, paired content preservation and readable carrier survival remain separate quantities; none establishes lawful ownership.
