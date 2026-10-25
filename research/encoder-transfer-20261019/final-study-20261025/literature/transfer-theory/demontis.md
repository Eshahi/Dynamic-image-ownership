# Gradient alignment and attack transfer

- Title: Why Do Adversarial Attacks Transfer? Explaining Transferability of Evasion and Poisoning Attacks
- Authors: Ambra Demontis; Marco Melis; Maura Pintor; Matthew Jagielski; Battista Biggio; Alina Oprea; Cristina Nita-Rotaru; Fabio Roli
- Year / venue: 2019 / 28th USENIX Security Symposium, pp.321–338. DOI: null (not verified).
- ID / citation key: USENIX 236234 / demontis2019transfer
- [Primary final paper](https://www.usenix.org/system/files/sec19-demontis.pdf)
- Version: USENIX proceedings PDF. Access: 2026-10-25.
- Verification: **V2**. Inspected §3.1, §4 Eq.16–18 and three metrics, §5.1.1 setup/Figs.5–8 and §5.1.2 setup. Cache/hash in source-manifest.json.

**Direct evidence.** The first-order L2 transfer analysis includes target gradient size, surrogate–target gradient cosine, and loss-landscape variability. Eq.18 expresses the alignment factor; raw gradient size is not directly comparable across learning algorithms. MNIST89 experiments use ten splits, disjoint target/surrogate training sets of 5,900 each, and 1,000 test points, with L2 budgets up to 5. Regularization/complexity and gradient alignment are evaluated against observed attack errors.

**Author interpretation.** These quantities explain important variation in transferability beyond shared task labels.

**Agent inference.** An F5 transfer predictor should include signed readout alignment, not only encoder residual norm. A latent coordinate system must be normalized before any cross-model magnitude comparison.

**Limit / assumption.** This is classification evasion/poisoning theory, not a diffusion-watermark theorem. Applying its first-order reasoning to a nonlinear, stochastic regeneration chain requires new measurements; shared training or independent initialization alone determines neither transfer nor nontransfer.
