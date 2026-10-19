# WOUAF — V2 new inspection

- Authors: Changhoon Kim; Kyle Min; Maitreya Patel; Sheng Cheng; Yezhou Yang.
- Title: *WOUAF: Weight Modulation for User Attribution and Fingerprinting in Text-to-Image Diffusion Models*. CVPR 2024:8974–8983; arXiv 2306.04744v3.
- Primary: https://arxiv.org/html/2306.04744v3 ; https://openaccess.thecvf.com/content/CVPR2024/html/Kim_WOUAF_Weight_Modulation_for_User_Attribution_and_Fingerprinting_in_Text-to-Image_CVPR_2024_paper.html . DOI: 10.48550/arXiv.2306.04744. Access: 2026-10-18.
- Mechanism/access: payload-dependent VAE-decoder weight modulation; jointly trained mapping and RGB extraction networks. Requires model-distributor control; no inversion.
- Side information/payload/data: learned extractor and user fingerprint database; default 32 bits. COCO Karpathy-split training, disjoint COCO/LAION-Aesthetics evaluation; Euler 20, guidance 7.5.
- Evidence/count: §4.1 defines “user attribution accuracy” as **per-bit** matching; Table 1 .99 is not exact-owner success. Separately §4.4 reports zero false assignments against a million-entry database for five external sources, 1,000 images/source, about 30/32 matching-bit threshold.
- Threat/limits: §4.6 ordinary transformations; §5.2 autoencoder compression and §5.3 model purification. No matched diffusion-regeneration sweep establishes strict natural-photo transfer.
- Relevance/inspection: user registry and lightweight learned extraction are prior art, but the registry is user-ID based, not enrolled-image descriptor verification. Fresh §§3.2–5.3/Tables 1–2. V2, no reproduction.
