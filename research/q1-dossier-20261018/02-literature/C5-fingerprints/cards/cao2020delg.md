# cao2020delg — V2

Bingyi Cao, André Araujo, Jack Sim. *Unifying Deep Local and Global Features for Image Search*. ECCV 2020, pp. 726–743. Inspected arXiv 2001.05027v4 (2020-09-15). DOI not verified. Accessed 2026-10-18. [Primary full text](https://arxiv.org/html/2001.05027v4).

**Mechanism / access.** DELG shares a backbone for a global GeM descriptor and attentive local features, compressing locals with an autoencoder and controlling gradients. Stored global/local reference descriptors and coordinates are side information. Top-100 retrieval candidates undergo affine RANSAC reranking by inlier count; no embedded payload.

**Evidence.** Read §3, §4.1 and §4.2/Table 5. Training uses 1.2 million landmark images. Oxford has 4,993 database images and 70 queries. R101 Oxford Medium mAP rises from 73.2 global-only to 78.5 with local reranking under the reported multiscale configurations (three global scales; default seven local scales).

**Boundary / relevance.** Geometric verification is established retrieval practice. A shared background across nearby frames can retain many geometric inliers. Landmark gains neither prove frame discrimination nor transfer through diffusion; local coverage/residual hypotheses remain untested here.
