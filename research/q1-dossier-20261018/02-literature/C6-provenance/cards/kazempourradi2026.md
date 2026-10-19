# Kazempourradi et al. — soft-binding benchmark

- **Title:** Watermarks and Fingerprints as Soft Bindings for Content Provenance: An Open-Licence Benchmark for Images, Audio and Video.
- **Authors:** Seyedmahdi Kazempourradi; Ramtin Mojtahedi; Behrang Mohseni.
- **Year/venue/version:** 2026; arXiv preprint; 2610.04151v1, 2 October. Only v1 exists in the inspected submission history; V2 below is verification depth, not arXiv version.
- **URL/DOI:** https://arxiv.org/html/2610.04151v1 ; 10.48550/arXiv.2610.04151 (landing page labels DOI registration pending).
- **Access/verification:** 2026-10-18; V2, current-session primary method and results inspection; no reproduction.
- **Locators:** §§3.1, 3.3.2–3.3.8, 5.2, 5.6, 6, 7; Tables 14, 19.

**Direct evidence.** Post-hoc watermark recovery and registry fingerprint retrieval share attacked queries. Registry descriptors, reference identities, calibrated thresholds and sometimes expected payloads are side information. Image retrieval uses 2,000 ABO sources and 98,985 references; calibration negatives are source-disjoint from evaluation. Table 19 gives TrustMark-Q/DINOv2-S watermark success .62, fingerprint success .61, intersection .55 and union .69. The union is explicitly not deployed-cascade accuracy. Image fingerprints use a calibrated pair-level FPR target of 1e-7, not a guaranteed query-level rate. Near-copy catalogue variants substantially change operating points; geometric verification did not improve detection at matched false-binding calibration. The watermark track excludes regeneration and adversarial attacks; fingerprint security is separately attacked.

**Inference/relevance.** Strong novelty threat to hybrid provenance and near-copy diagnosis. It does not establish the thesis's particular regeneration attribution claim. Treat the paper's commercial authorship and unreviewed preprint status as context, not grounds for dismissal.

**Artifact:** `kazempourradi2610v1.html`; SHA-256 in `source-artifacts.json`.
