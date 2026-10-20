# T4-02: Raising the Cost of Malicious AI-Powered Image Editing

- **Primary source:** [2302.06588v1](https://arxiv.org/html/2302.06588v1); authors: Hadi Salman; Alaa Khaddaj; Guillaume Leclerc; Andrew Ilyas; Aleksander Madry.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. Prior T4 source explicitly rechecked for this mechanism topic; the body records the new assumption/endpoint checks.
- **Method locators:** cached `photoguard.txt` lines 151-172; 499-542. **Evaluation locators:** 173-225; 499-542. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** arXiv perpetual non-exclusive, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/photoguard.html`. **HTML SHA-256:** `976b222d9cdd221cd88b3bc2546b08dccf3a1dcef8fc14fcce9bd913cc01ff8e`. Text hash and byte counts are in `source-manifest.json`.

## Claim and mechanism

The encoder attack solves a projected pixel-space optimization that drives a latent representation toward a target such as a gray image. The diffusion attack differentiates through parts of generation toward a target output. Networks stay frozen. This is a concrete antecedent for high local encoder sensitivity under small visible perturbations, not a construction of an owner payload or watermark detector.

F5's shared ingredient is a pixel perturbation optimized through a frozen VAE. Its target is signed latent DCT evidence, not failed editing. The local linear approximation gives delta approximately J_encoder-transpose times a target direction; transfer depends on another encoder's response to that particular delta. Architecture similarity or dissimilarity does not mathematically establish that response.

## Evaluation actually inspected

Section 4 evaluates malicious image editing. The appendix specifies SD1.5, 512 pixels, CFG7.5, 100 steps, eta1, and encoder PGD with Linf budget 16/255, step 2/255 and 200 iterations. Quantitative comparisons include 60 edits, text/image alignment and reconstruction/perceptual metrics. Seeds were selected to obtain realistic edits on originals before paired comparisons. That process differs from the fixed-seed, empty-prompt, CFG1, DDIM20 transfer protocol. Its budgets, images and endpoint do not yield a quantitative F5 forecast.

## Threat, side information and T4 use

The defender knows the editor model and changes a published input to frustrate editing. The evaluator measures editing quality. There is no secret-key attribution experiment, same-quality cross-encoder watermark survival theorem, or lightweight extractor result. The full diffusion attack also has a different cost from one VAE-gradient writer.

This source supports encoder sensitivity as a plausible mechanism, not the assertion that all surviving F5 evidence is adversarial or nonsemantic. If R0 retention is high but R1/D1 fail after X1 survives, the observation is compatible with specialization, but decoder/reconstruction and resolution remain confounders. Comparable R1 retention weakens the strongest specialization hypothesis. Read/content decomposition is required before calling a failure carrier removal.
