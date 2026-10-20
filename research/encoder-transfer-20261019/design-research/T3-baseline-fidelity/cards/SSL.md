# SSL: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **Watermarking Images in Self-Supervised Latent Spaces**. Version/date: arXiv:2112.09581v1 [cs.CV] 17 Dec 2021. Venue: ICASSP 2022, official README citation.

Authors: Pierre Fernandez; Alexandre Sablayrolles; Teddy Furon; Hervé Jégou; Matthijs Douze. Year: 2021. DOI: not established for this inspected version.

Stable ID: `arxiv:2112.09581v1`. Citekey: `T3SSL2112`. Canonical URL: https://arxiv.org/abs/2112.09581v1

Primary full text: https://arxiv.org/html/2112.09581v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/ssl.txt`
SHA-256: `22b58c938f21799cfec9b2ffc89c26030c86b053e085fa8bafc925ce65c69575`

Actually inspected: §§3.1–3.4,4.1–4.3; official README/LICENSE and DINO/normalization asset listing.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

Image optimization moves a frozen self-supervised feature representation into a secret detection cone or toward keyed bit carriers. Whitening statistics and the chosen DINO network are detector dependencies.

## Native operating point and detector side information

The zero-bit cone test has a theoretical target FPR of 10^-6 under its feature-distribution model. The distinct multi-bit experiment uses 30 carriers in a 2,048-dimensional feature space. Reported optimization uses 100 Adam iterations, learning rate .01 and a PSNR constraint. The code distinguishes YFCC and COCO whitening; substituting statistics changes the detector.

## Code, weights, pinned release and licenses

facebookresearch/ssl_watermarking@3e65334bd28ecbc66756f0179def9dc4c88a6acc, CC BY-NC 4.0 (actual LICENSE inspected). Official dino_r50_plus.pth and out2048_yfcc_orig.pth under https://dl.fbaipublicfiles.com/ssl_watermarking/; README distinguishes resized YFCC and COCO whitening. Immutable weight hashes unresolved; no download.

## Published evaluation and regeneration conditions

The original paper reports zero false detections on 100,000 YFCC images and one on 1,281,167 ImageNet images for the zero-bit setting, but no matched diffusion-regeneration tuple. VINE's 30-bit comparison reports quality 41.77/.9796/.0351 and stochastic/deterministic TPR .76/9.70% at .1% FPR. Those are different endpoints and use VINE's attack/count conditions.

## Cost and uncertainty

VINE Table 7 reports 2.1938 seconds and 1,072 MB on Quadro RTX6000 for a 1,000-image mean. Per-image optimization makes this slower than the feed-forward comparators; no target-server timing exists.

## Limitation and design implication

Keep analytic feature-cone FPR, empirical image FPR and queried-message recovery separate. Its detector side information and optimization cost make it a literature control, not a new core arm.

Disposition: **Literature coverage; excluded**
