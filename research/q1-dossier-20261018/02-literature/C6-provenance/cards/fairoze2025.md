# Fairoze et al. — public detection and deferred storage

- **Title:** On the Difficulty of Constructing a Robust and Publicly-Detectable Watermark.
- **Authors:** Jaiden Fairoze; Guillermo Ortiz-Jiménez; Mel Vecerik; Somesh Jha; Sven Gowal.
- **Year/venue/version:** 2025; arXiv preprint 2502.04901v2, 26 April; final venue unverified.
- **URL/DOI:** https://arxiv.org/html/2502.04901v2 ; 10.48550/arXiv.2502.04901.
- **Access/verification:** 2026-10-18; V2, current construction and empirical evaluation inspection.
- **Locators:** §§5.3–5.4, Theorem 5.1; §§6.2–6.3; Figure 4.

**Direct evidence.** The construction signs a robust embedding and watermarks embedding-plus-signature; verification requires signature validity and content similarity. Deferred storage replaces the payload with a database reference, assuming database availability. Public verification exposes the method except signing secrets. Security depends on collision-resistant robust embeddings; ordinary similarity quality is insufficient. Copydays original/strong pairs evaluate native normalized embeddings under 20-step momentum PGD. Best clean DINOv2/SSCD ROC AUCs are .990/.986; SSCD drops to .057 at L-infinity 4/255. The inspected §6.2 gives no explicit pair count; do not invent one. This is component evaluation, not a successfully instantiated end-to-end secure deployment.

**Inference/relevance.** Decisive antecedent for pointer-to-descriptor storage. The thesis cannot inherit its conditional cryptographic theorem: the trusted registry and empirical descriptor rule are different assumptions. Availability, enrollment trust and adaptive embedding collisions remain separate questions.

**Artifact:** `fairoze2502v2.html`; SHA-256 in `source-artifacts.json`. The initially cached v1 is superseded and not the card basis.
