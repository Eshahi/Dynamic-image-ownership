# T4-09: Certified Adversarial Robustness via Randomized Smoothing

- **Primary source:** [1902.02918v2](https://arxiv.org/html/1902.02918v2); authors: Jeremy Cohen; Elan Rosenfeld; J. Zico Kolter.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. New Stage1b T4 card, with method and evaluation inspected.
- **Method locators:** cached `smoothing.txt` lines 192-227; 276-327. **Evaluation locators:** 337-389. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** arXiv perpetual non-exclusive, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/smoothing.html`. **HTML SHA-256:** `495222299e2d790810117a64717bfb8110ea7fa7f1ff346ebdce0a6e5b4e287c`. Text hash and byte counts are in `source-manifest.json`.

## Claim and theorem

Randomized smoothing defines a classifier by the most probable label of a base classifier under Gaussian perturbations. The certified L2 radius is sigma/2 times the difference of inverse-normal class-probability bounds. The theorem requires valid bounds for top and competitor classes; Monte Carlo certification supplies confidence-controlled estimates and can abstain. It does not say that averaging continuous encoder outputs necessarily shrinks a Jacobian.

For affine E(u)=Au+b and unclipped antithetic perturbations, the average of E(u+eta) and E(u-eta) is exactly E(u). Watermark response A delta is unchanged. A smooth nonlinear encoder adds an order-sigma-squared curvature term whose derivative can increase or decrease sensitivity. Clipping near boundaries adds bias. These are algebraic deductions, not SDXL measurements.

## Evaluation actually inspected

The paper trains/evaluates smoothed CIFAR-10 and ImageNet classifiers, reporting certified accuracy versus radius. Its practical routine selects a class with 100 samples and uses 100,000 samples for certification at alpha 0.001; ImageNet evaluation uses 500 images. These confidence-controlled classification quantities have no counterpart in eight antithetic SDXL posterior modes.

## T4 implications for P5

P5 remains a proposed fixed exploratory attacker: four public Gaussian arrays and their negatives, sigma 2/255 in [0,1] RGB at the 1024 input, clipping to [0,1], and the arithmetic mean of eight posterior modes before strength 0.2 regeneration. The same arrays apply to all sources and arms; eight means four pairs. For 300 source/input combinations, 2400 smoothing encodes can be cached across the three diffusion seeds. Exact seed/RNG and precision still require a pre-outcome proposal amendment. Direct-mode D1 helps, but the old 900-output proposal lacks mode-initialized unsmoothed regeneration as a matched control: ordinary R1 samples the posterior. The recommendation adds 900 matched diffusion outputs and 300 cached unsmoothed mode encodes, giving 1800 diffusion outputs and 2700 total encodes. This requires additional paid budget and is not authorized. The cheaper old comparison tests the compound attacker, not smoothing alone.

If smoothing removes narrow nonlinear sensitivity exploited by F5, C/read should fall relative to matched mode control at usable quality. Unchanged or increased read/C, especially with unchanged already-logged carrier evidence, disconfirms that working mechanism. That is compatible with the smoothing theorem. A reduction does not establish a certificate, learned robust encoder or robustness against a writer adapted to smoothing. No empirical gain is claimed.
