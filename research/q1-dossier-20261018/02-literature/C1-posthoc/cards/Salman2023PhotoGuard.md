# Raising the Cost of Malicious AI-Powered Image Editing

- Citekey: `Salman2023PhotoGuard`
- Authors: Hadi Salman; Alaa Khaddaj; Guillaume Leclerc; Andrew Ilyas; Aleksander Madry.
- Year / venue: 2023; arXiv version inspected.
- Version: v1 (2023-02-13).
- Primary source: [paper](https://arxiv.org/html/2302.06588v1); arXiv: 2302.06588; DOI: not verified for this inspected version (omitted from BibTeX).
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Section 3 encoder/diffusion attacks; Sections 4.1–4.2; Appendix A.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/photoguard.html`; SHA-256: `976b222d9cdd221cd88b3bc2546b08dccf3a1dcef8fc14fcce9bd913cc01ff8e`.
- Setting: Image-domain protective perturbation; not a watermark.
- Detector side information: White-box diffusion encoder or pipeline at protection time; no watermark detector.
- Threat: Disrupt malicious diffusion editing rather than survive it.

**Mechanism/payload.** An encoder attack optimizes a bounded input perturbation to make the encoded representation approach a target latent; a stronger diffusion attack differentiates through generation. No message or ownership detector is provided.

**Evidence.** The encoder implementation uses projected gradient descent with an L-infinity bound of 16/255, 200 iterations and step size 2/255. Evaluation includes 60 SD1.5 edits with CLIP/quality measures and qualitative editing examples. These are disruption measurements, not watermark recovery rates.

**Access/limits.** Protection requires model gradients. Generalizing across editing models and transformations is distinct from retaining a reliable attribution signal after regeneration. Failure of an editor to obey its prompt does not prove content ownership.

**Thesis inference.** The basic idea that small image-domain changes can strongly steer a frozen diffusion encoder is established. Any F5 novelty claim must specify the carrier objective, decodability and record-binding rule, rather than claiming encoder-gradient sensitivity itself.

