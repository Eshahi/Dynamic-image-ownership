# Towards A Correct Usage of Cryptography in Semantic Watermarks for Diffusion Models

- Citation key: `thietke2025crypto`
- Authors: Jonas Thietke; Andreas Müller; Denis Lukovnikov; Asja Fischer; Erwin Quiring.
- Year / venue: 2025; WMark workshop at ICLR 2025; arXiv version inspected.
- Version: 2503.11404v1, 2025-03-14.
- Primary source: [full text](https://arxiv.org/html/2503.11404v1).
- DOI: 10.48550/arXiv.2503.11404. arXiv: 2503.11404v1.
- Access date: 2026-10-18.
- Verification: **V2 (formal security analysis)**. Primary full-text formal security game, reduction and nonce-reuse counterexample inspected; V2 formal-analysis route, not an independent experimental audit.
- Inspection locators: Sections 3.1–3.2; Figure 1; Equations 1–7; key-management comparison.
- Cache: `thietke-v1.html`; path and SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Generation-time Gaussian Shading and PRC cryptographic deployment.
- Mechanism: Nonce-respecting IND$-CPA game and reduction under stream-cipher security; repeated nonces expose matching recovered ciphertext structure.
- Threat and attacker access: Multi-image watermark distinguishability from nonce reuse; multiple marked samples and inversion capability, but no secret key.
- Detector side information: Secret encryption key and nonce handling; Gaussian Shading may require stored nonce enumeration; PRC embeds nonce robustly.
- Payload / capacity: Inherited watermark message; nonce transmission/storage has additional deployment cost.
- Datasets and counts: Formal result does not require an empirical dataset; Appendix B performance setup not audited.
- Attacks / regenerators: Inversion-assisted multi-image distinguisher. No registry enrollment experiment.
- Conditional numbers / result: No empirical number used. Security conclusion is conditional on nonce-respecting queries and the assumed cipher/sampler behavior.
- Limits: Undetectability is a different game from authenticity or unforgeability; fresh nonces do not prove resistance to copied marks.

## Thesis relevance

Prevents cryptographic overclaiming. A public owner identifier or a Gaussian-looking mark is not authentication.

No new experiment was performed; this card supports only the specified formal security distinction.

