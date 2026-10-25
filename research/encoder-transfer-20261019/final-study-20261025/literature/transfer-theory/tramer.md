# Transferable subspaces and limits

- Title: The Space of Transferable Adversarial Examples
- Authors: Florian Tramèr; Nicolas Papernot; Ian Goodfellow; Dan Boneh; Patrick McDaniel
- Year / venue: 2017 / arXiv preprint; journal/conference not asserted. DOI: null.
- ID / citation key: arXiv:1704.03453v2 / tramer2017space
- [Primary paper](https://arxiv.org/pdf/1704.03453v2)
- Version: v2, 23 May 2017. Access: 2026-10-25.
- Verification: **V2**. Read §§2–3 (GAAS and experiments), §4 boundary comparison, §5 limits and counterexample. Cache/hash in source-manifest.json.

**Direct evidence.** GAAS searches for orthogonal directions aligned with a first-order loss increase. At L2 norm 5, the MNIST fully connected example averages 44.28 source-adversarial directions and 24.87 transferring directions; the CNN example averages 15.18 and 2.24 (§3.2). §5 provides sufficient conditions for simple model classes and counterexamples to inevitable transfer.

**Author interpretation.** Shared adversarial subspaces and boundary geometry help explain transfer, but nonrobustness alone does not guarantee it.

**Agent inference.** Separately trained autoencoders can share sensitive directions. Conversely, failure to preserve F5 does not prove their entire representations are independent. Future measurements need residual-specific geometry and matched random directions.

**Limit / assumption.** These numerical examples involve classifier errors, not latent signal retention or watermark detection; their perturbation budgets are not this project's image-quality budget. No numerical transfer rate is imported into F5 predictions.
