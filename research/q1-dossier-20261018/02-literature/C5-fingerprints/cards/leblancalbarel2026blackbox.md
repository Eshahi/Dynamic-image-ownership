# leblancalbarel2026blackbox — V2

Diane Leblanc-Albarel, Bart Preneel. *Breaking Widely Deployed Perceptual Hash Functions: Black-Box Collisions in Apple NeuralHash and Microsoft PhotoDNA*. USENIX Security 2026, pp. 1907–1926. Venue version inspected; DOI not listed/verified. Accessed 2026-10-18. [Primary venue record](https://www.usenix.org/conference/usenixsecurity26/presentation/leblanc-albarel); [full paper](https://www.usenix.org/system/files/usenixsecurity26-leblanc-albarel.pdf).

**Mechanism / access.** Hash-oracle attacks exploit structured image cohorts and distributional bias without encoder internals. Reference hashes and oracle queries are available; no watermark payload or authenticated owner claim.

**Evidence.** Read §§2–4/Tables 2–3 and §5.1. Table 3 compares 202,599-image cohorts: unblurred faces produce 12 illegitimate NeuralHash collision groups involving 24 images; highly blurred faces produce 270 groups involving 588 images; the nonhuman cohort has zero. The table's FPR divides involved images by cohort size, not by all possible pairs.

**Boundary / relevance.** Content-conditioned structure can defeat independent-bit intuition even for exact hashes. Results concern these hash implementations/cohorts, not D1, F5, adjacent-frame negatives or a universal probability bound. Blur-conditioned findings should not be presented as regeneration evidence.
