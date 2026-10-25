# Scope of the MSAT-LDM uniform generalization bound

Author supplement, 2026-10-25. This is original mathematical analysis, outside the completed WP6/E3 review; it changes no protocol and reports no experiment.

## Inspected statement

Source: Lu Zhang and Liang Zeng, [MSAT-LDM, official AAAI-26 PDF](https://ojs.aaai.org/index.php/AAAI/article/download/40921/44882), Section 4.1, Theorem 1, Eq. (11), PDF page 4 / printed page 36051. Its displayed statement puts every hypothesis inside one probability-at-least-1−δ event over an iid sample. Under bounded loss of range width G and K-Lipschitz dependence on the input, it gives

\[
R_t(h)\leq\widehat R_n(h)+G\sqrt{\log(1/\delta)/(2n)}+K W_1(\mu_t,\mu_z).
\]

No class-complexity term or sample-independence restriction on the selected hypothesis appears there. Any final-version supplementary proof remains uninspected. The following addresses the displayed statement as written.

Version-separated check: [SAT-LDM, arXiv:2501.00463v2, 17 February 2025](https://arxiv.org/html/2501.00463v2), Appendix A.2, was inspected. This older, differently titled manuscript repeats the simultaneous quantifier, then applies ordinary Hoeffding concentration to h and combines it with transport. That proof supplies no step controlling all hypotheses simultaneously. It supports the fixed-h result below, but cannot substitute for the final MSAT-LDM supplementary proof.

## Counterexample to simultaneous coverage

Take latent space Z=R with Euclidean distance, singleton message space M, and identical training and target distributions uniform on A={1,…,2n}. Before sampling, fix the hypothesis class indexed by every nonempty subset S of A with |S|≤n. Define its losses, on all real z, by

\[
\ell_S(z)=\min\{1,\operatorname{dist}(z,S)\}.
\]

Distance to a nonempty set is 1-Lipschitz; clipping at 1 preserves that property. Every loss lies in [0,1], with range width G=1 and common K=1. The measures have finite first moments, and their Wasserstein distance is zero. This satisfies the stated abstract assumptions with a fixed, finite hypothesis class.

For any sample of size n, let S be its distinct observed values. That S already indexes a member of the fixed class. Its empirical loss is zero. At every unobserved point of A, the distance to S is at least one, so

\[
\widehat R_n(h_S)=0,\qquad
R_t(h_S)=\frac{2n-|S|}{2n}\geq\frac12.
\]

For n=100 and δ=.05, the proposed deviation allowance is approximately .1224. Thus every possible sample contains a violating hypothesis: the simultaneous event has probability zero, rather than at least .95. No hypothesis class was constructed after observing the sample; only its member was selected afterward, precisely what a simultaneous guarantee must permit. This refutes the general theorem under its listed assumptions, not an architecture-specific theorem with additional restrictions.

## Statements that survive

For each fixed h, the bounded-loss iid concentration inequality gives the same deviation allowance with probability at least 1−δ. It also applies conditionally when h was fitted using data independent of the evaluation sample. It does not automatically cover a hypothesis fitted on that same sample.

Separately, Kantorovich–Rubinstein duality and the common independent message distribution give the deterministic inequality

\[
|R_t(h)-R_z(h)|\leq K W_1(\mu_t,\mu_z).
\]

This transport inequality holds for all admissible h; it introduces no empirical concentration claim. Combining it with fixed-h concentration is valid. For a fixed finite class of N hypotheses, a union bound instead supplies simultaneous coverage with deviation G√[log(N/δ)/(2n)]. Other classes require suitable complexity, stability, or equivalent additional control.

## Consequence for this dossier

Distribution alignment remains a valid population-risk mechanism under the Lipschitz assumptions. The displayed complexity-free term cannot certify a trained model's generalization uniformly. This mathematical scope issue neither invalidates the paper's measured empirical results nor establishes failure of its method. Any claim of guaranteed superiority also needs justified distribution-distance comparisons and control of the remaining risk terms.
