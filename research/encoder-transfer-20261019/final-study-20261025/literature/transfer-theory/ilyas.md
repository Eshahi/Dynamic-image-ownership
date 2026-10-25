# Shared nonrobust features

- Title: Adversarial Examples Are Not Bugs, They Are Features
- Authors: Andrew Ilyas; Shibani Santurkar; Dimitris Tsipras; Logan Engstrom; Brandon Tran; Aleksander Madry
- Year / venue: 2019 / NeurIPS 32. DOI: null (not verified).
- ID / citation key: arXiv:1905.02175 / ilyas2019features
- [Primary final paper](https://proceedings.neurips.cc/paper/2019/file/e2c420d928d4bf8ce0ff2ec19b371514-Paper.pdf)
- Version: NeurIPS proceedings PDF. Access: 2026-10-25.
- Verification: **V2**. Read §2 definitions, §3.1–3.3 construction/experiments, Table 1 and Figure 3, §4 Gaussian model. Cache/hash in source-manifest.json.

**Direct evidence.** The study constructs relabeled adversarial training datasets and tests resulting classifiers on natural examples. Table 1 reports CIFAR-10 test accuracy 63.3% for the random-target dataset and 43.7% for the deterministic-target dataset. Figure 3 relates learning from nonrobust features to transfer across five architectures. The formal definition and empirical constructions are explicitly distinguished.

**Author interpretation.** Models may learn shared, predictive, brittle features even when trained independently.

**Agent inference.** Independent encoder training cannot justify assuming isotropic or orthogonal watermark residuals. That assumption is a null approximation to test, not a fact established by architectural lineage.

**Limit / assumption.** Classification features are not F5 carrier coordinates. The study does not establish latent-autoencoder gain, the denoiser's response to a mark, or content-bound detection after regeneration. Its argument is one explanation of adversarial vulnerability, not an exclusion of alternatives.
