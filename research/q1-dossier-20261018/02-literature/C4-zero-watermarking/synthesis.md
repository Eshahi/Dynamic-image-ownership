# C4 — Zero-watermarking and registered ownership claims

Access cutoff: 2026-10-18. Seven unique works reached V2 (method and evaluation inspected); five additional novelty risks remain V1. Versions are deduplicated. This is literature synthesis, not a new experiment or a claim that all relevant work has been found.

## What is already established

Zero-watermarking usually registers an image-derived feature or an ownership share computed from features and an arbitrary logo. Verification combines suspect-image features with that stored information. Zero pixel modification is real, but the external share is detector side information: recovered owner bits need not have travelled through the image channel. [Seenivasagam and Velumani, 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3732617/) already reconstruct patient metadata plus an EHR URL using a server-held share. Therefore neither a content pointer nor a registered feature-to-owner association is new by itself.

Even adding a physical mark to retrieval has old precedent. [Roy and Chang, 2004](https://doi.org/10.1007/s00530-003-0116-1) change image vectors to improve database identification, then use the retrieved index to look up a message. Their introduction explicitly identifies the ambiguity of identical content carrying different intended messages and motivates physical marking to separate it. This is not the thesis's implementation or threat model, but it directly blocks a broad architectural novelty claim.

Deep feature extraction and robust external association are also established: [InvZW, published 2026](https://doi.org/10.3389/frsip.2026.1812987) learns invariant features and reference/projection associations, while [Gharib et al., 2025](https://doi.org/10.1038/s41598-025-09290-7) fuse texture and VGG19 features. Their inspected tests concern conventional distortions. They cannot establish performance under the thesis's regeneration and adversarial enrollment conditions.

## Decisive generative-edit prior art

[Rel-Zero, arXiv v2 / accepted CVPR 2026](https://arxiv.org/abs/2603.17531) is the strongest direct threat. It stores predicted stable patch-pair indices, learned using VAE reconstruction, and compares suspect/enrolled sets. It evaluates deterministic regeneration plus instruction-based and local editing. Broad claims that registered features had not been made robust to generative editing are untenable.

Its reported operating point needs careful interpretation. Appendix F chooses a threshold using independent edge activations with probability 0.5 and a binomial null. The paper separately measures pairwise uniqueness of randomly sampled images. Neither establishes a hard-negative or adaptive-attacker false-attribution guarantee. The fixed-size top-K extraction also calls for justification of the independence model. These are comparison requirements, not reasons to dismiss the work. Its 50 edges are an intrinsic signature, not an owner-chosen 50-bit physical payload.

## Instance ambiguity and competing enrollment

[Roček et al., 2021](https://doi.org/10.1007/s10278-020-00396-0) experimentally show that several medical zero-watermark schemes recover similar watermarks from neighboring slices and different patients. Their result is domain- and method-specific, but makes realistic near-duplicate negatives central rather than optional. Random unrelated-image specificity cannot substitute for them.

For a deterministic intrinsic descriptor, an identical image supplies the same observation regardless of who presents it. Associating that observation with different claimants therefore requires an enrollment policy or an additional observation (our reasoning, not a measured attack on every paper). A trusted timestamp can establish registration order; it does not establish lawful authorship. Encrypting or signing the record authenticates the record or signer, not the causal origin of the image. [Hung and Thanh, 2026](https://doi.org/10.1038/s41598-026-38991-w) explicitly separates feature recovery from protection of externally registered shares; its licensing application remains outside thesis scope.

The thesis's physical owner-conditioned signal is an additional observation, unlike an owner logo encoded only in an external share. Its value must be stated narrowly: performance of a frozen conjunction of physical-signal detection and enrolled-record compatibility under stated access and regeneration conditions. It does not prove legal ownership or make public owner signals cryptographically unforgeable. Exact replay also remains replay of the same observable evidence unless a separate freshness protocol is introduced, which is outside scope here.

## Consequence for the article

Position the contribution as an empirical boundary and controlled comparison: what the physical factor adds over fingerprint-only registration, and where the combined rule still confuses same-shot alternatives. Preserve the held-out E2 failure and qualify E3 by completed-case attacker access. Do not claim the registry architecture, deep feature matching, or generative robustness in general as firsts. Relational or contrastively trained descriptors are proposals for later study, not fixes demonstrated in this session. ZWNet, ConZWNet, Rad-Mark, a 2019 CNN paper, and pseudo-zero watermarking remain explicit access gaps; no absence-of-prior-art conclusion is justified.

Access refresh: ZWNet (li2024zwnet) is now V2 through a publisher-formatted PDF mirror. Its 100-image test set is consulted for early stopping, so reported performance is not untouched held-out confirmation. ConZWNet and Rad-Mark remain V1 after bounded access attempts; no novelty exclusion is inferred.
