# pizzi2022sscd — V2

Ed Pizzi, Sreya Dutta Roy, Sugosh Nagavara Ravindra, Priya Goyal, Matthijs Douze. *A Self-Supervised Descriptor for Image Copy Detection*. CVPR 2022, pp. 14532–14542. Inspected arXiv 2202.10261v2 (2022-03-25). DOI: not verified. Accessed 2026-10-18. [Primary full text](https://arxiv.org/html/2202.10261v2); [venue record](https://openaccess.thecvf.com/content/CVPR2022/html/Pizzi_A_Self-Supervised_Descriptor_for_Image_Copy_Detection_CVPR_2022_paper.html).

**Mechanism / access.** Contrastive copy-specific CNN descriptor, GeM pooling, retained projection, entropy regularization and strong/mixed augmentations. Public encoder; reference descriptors required; optional score normalization adds a background collection. No embedded payload or owner authentication.

**Evidence.** Read §§2–5.4, Tables 2–3. DISC validation has one million references and 50,000 queries, including 10,000 copies. Table 2's 512-dimensional SSCD DISC advanced-augmentation model reports micro-AP 61.5, or 72.5 with score normalization. These measure ranking across benchmark transformations, not regeneration acceptance at fixed false binding.

**Boundary / relevance.** §2 defines copies by a shared two-dimensional source and explicitly separates nearby video frames from that strict identity task. This makes SSCD a principled comparator for frame specificity; it supplies no demonstrated same-shot/regeneration operating point for this thesis.
