# Nemecek et al. — provenance and watermark inconsistency

- **Key/title:** `Nemecek2026IntegrityClash`; Authenticated Contradictions from Desynchronized Provenance and Watermarking.
- **Authors:** Alexander Nemecek; Hengzhi He; Guang Cheng; Erman Ayday.
- **Inspected version:** arXiv2603.02378v2, 18April2026; first release2March2026. V2 verification depth, read19October2026. Acceptance at CVPR2026 APAI workshop is stated on arXiv; final CVF fulltext fetch failed, so no final/preprint equivalence is asserted.
- **Primary:** https://arxiv.org/html/2603.02378v2 ; https://arxiv.org/abs/2603.02378 ; DOI10.48550/arXiv.2603.02378.
- **Metadata cross-check:** https://dblp1.uni-trier.de/rec/journals/corr/abs-2603-02378.html confirms title, four authors, year and preprint DOI. Final-proceedings DOI remains unverified.
- **Locators:** §§3–5.2, Tables1–3, §6.2; references[5] and[20].

**Mechanism and conditions.** A rule checks manifest validity/disclosure against expected-payload watermark detection. The adversary controls signing assertions without breaking signatures. Evaluation uses500 SDXL sources, PixelSeal's256-bit payload, bit-accuracy threshold.75 and self-signed research certificates. The paper reports100% classification over3500 pipeline instances, including routine perturbations; these reuse500 sources. Q3 is expressly not instantiated. Issuer warnings persist in the demonstrated verifier. Removal/regeneration resistance and lawful ownership are not established.

**Relevance/inference.** Primary references confirm edges to final TrustMark[5] and SynthID-Image[20]. This pre-empts a broad claim that jointly inspecting inconsistent provenance signals is new. It studies declared synthetic origin, not our registered-instance decision. Omitted AI disclosure is not logically the same assertion as exclusively human creation; preserve this semantic distinction instead of adopting the paper's strongest terminology as a theorem.

**Audit caution.** §5.1's baseline mean/minimum alone cannot prove every score below threshold; report the authors' table-level classification claim, not a reproduced score audit. No raw outputs, images or code were inspected here. The single-watermarker, controlled-signing and limited platform conditions constrain external validity.

**Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/nemecek2603v2.html`;176456bytes; SHA256`C40179525E5D686F96784FBACA9550A7D1CB96A27A72D7B1B21EF39FCED70664`. Only HTML was downloaded; no linked image assets.
