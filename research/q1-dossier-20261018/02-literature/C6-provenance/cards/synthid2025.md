# Gowal et al. — SynthID-Image

- **Title:** SynthID-Image: Image watermarking at internet scale.
- **Authors:** Sven Gowal et al.; complete 26-author metadata in `cluster.bib`.
- **Year/venue/version:** 2025; arXiv preprint 2510.09263v1, 10 October; no later version listed.
- **URL/DOI:** https://arxiv.org/html/2510.09263v1 ; 10.48550/arXiv.2510.09263.
- **Access/verification:** 2026-10-18; V2 current method/evaluation reading; no tool access or reproduction.
- **Locators:** §§2.2–2.3; §7, “Combination with search and C2PA”; §§8.1–8.2, Tables 1–3.

**Direct evidence.** Post-hoc neural encoder/decoder; payload and watermark-presence detection are distinct tasks. Section 7 explicitly proposes requiring a correct payload AND a stored-embedding match to mitigate forgery. That combined system uses an internal database; its evaluation is not reported as an end-to-end hybrid experiment. SynthID-O uses 136-bit payloads at 512×512. Robustness evaluates 10,000 ImageNet validation images under 30 ordinary transformations; aggregated-worst detection is 99.72% at calibrated mean FPR .1%. Payload bit accuracy is a different metric. Quality uses 1,000 Imagen images and 10,000 ratings/model. Private models, internal secrets and service access distinguish its deployment threat settings.

**Inference/relevance.** Particularly close conceptual antecedent for conjunctive verification. Its ordinary-transformation result cannot rank it against thesis diffusion-regeneration attribution. The HTML limitations heading lacks body text; no claims are attributed to that unread section.

**Artifact:** `synthid2510v1.html`; SHA-256 in `source-artifacts.json`.
