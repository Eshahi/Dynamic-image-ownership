# SNW: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **Optimizing and Securing the Modern Watermarking Channel for Images**. Version/date: arXiv:2609.34744v1 [cs.CR] 28 Sep 2026. Venue: arXiv September 2026 preprint; no verified final venue.

Authors: Enoal Gesny; Eva Giboulot. Year: 2026. DOI: not established for this inspected version.

Stable ID: `arxiv:2609.34744v1`. Citekey: `T3SNW2609`. Canonical URL: https://arxiv.org/abs/2609.34744v1

Primary full text: https://arxiv.org/html/2609.34744v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/snw.txt`
SHA-256: `fabf24603a312b094fe4a959aba3a2b45b760b67b980ea8842a6f0b42999cb3f`

Actually inspected: Sections 2 through 4, 5, 6.1 through 6.2; Appendix C.1, F, G and H.2; Table 6. Method, evaluation and security scope were read, not only the abstract.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

The authors adapt PixelSeal's U-Net embedder and ConvNeXt extractor to a 768-dimensional continuous unit-vector channel. A keyed semi-orthogonal matrix rotates a codeword into a secret subspace, with an orthogonal Gaussian component. Alignment, isotropy and quality losses train the channel; a separate anti-spoof loss targets residual transfer. It explicitly marks existing images. Continuous messages are allowed by the formulation, but the reported evaluation uses binary codewords.

## Native operating point and detector side information

The channel dimension L is 768. Evaluation uses M'=L and alpha=1, so the tested physical codeword has 768 bits. Abstract maximum capacity 656 and table-specific capacities are different quantities. All compared methods are rescaled to 48 dB PSNR, and decoder features are whitened using statistics from one million unmarked MFlickr images. This is a modified operating point and extra calibration side information. The key, codebook and expected codeword support attribution. No universal numerical image-presence cutoff, empirical FPR or implemented practical ECC recovery is established. Reported Shannon capacity is derived from empirical bit accuracy under an independent-bit assumption; it is not recovered useful payload or TPR.

## Code, weights, pinned release and licenses

No official implementation, checkpoint or corresponding code/model license was established from the inspected paper and exact-name release searches. The arXiv document license is not a code license. A faithful implementation would be new work, not a runnable native release. PixelSeal's official release does not release SNW-specific learned weights or whitening statistics.

## Published evaluation and regeneration conditions

General evaluation uses 1,000 MFlickr images at 1,024 pixels and COCO training; at 48 dB, reported LPIPS is .0047 for SNW versus .0034 for PixelSeal, .0025 for VideoSeal and .0010 for TrustMark. Appendix H.2/Table 6 instead uses 200 MFlickr images. Its entries are rate/capacity bits, NOT bit accuracy: SNW identity .892/684.7, VAE .495/380.3, Sana 2 steps .479/368.1, 4 steps .388/298.3, 8 steps .145/111.5, 10 steps .068/52.2 and 20 steps .001/.8. PixelSeal gives identity .939/240.5, VAE .555/142.0, Sana 2 .519/132.8, 4 .357/91.3, 8 .076/19.4, 10 .025/6.4 and 20 .003/.8. The text describes a frozen-VAE roundtrip and DiffPure inversion of the last t steps followed by regeneration. Exact checkpoint/VAE, strength, sampler, prompts and seed replication are not established; Sana step labels must not be mapped to our SDXL strengths. These capacity estimates are neither calibrated detections nor a native PixelSeal result. Appendix G's 200-image residual-transfer experiment reports spoofed capacity 86.5 bits for vanilla SNW and .2 for anti-spoof training, versus identity 678/682.2. This is a specific attack, not a general forgery guarantee.

## Cost and uncertainty

No adequately conditioned end-to-end inference time or peak VRAM was established. The PixelSeal-family backbone plus key transforms and whitening suggests feed-forward inference, but this is an architectural inference, not measured target-server cost. Training cost and parameter storage cannot replace that measurement.

## Limitation and design implication

A recent distinct post-hoc method closes a search gap and supplies qualified third-party PixelSeal regeneration evidence. The covariance/PCA security statement is conditional on its statistical model; Section 2.3 explicitly separates adversarial robustness from its security scope. Capacity, whitening and attack settings limit transfer to our study. No extra proposal or core arm is added.

Disposition: **Literature coverage; excluded**
