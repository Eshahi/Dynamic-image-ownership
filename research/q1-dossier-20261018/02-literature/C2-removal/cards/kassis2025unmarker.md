# kassis2025unmarker — V2

Accessed 2026-10-18. Verification denotes primary method and evaluation/proof inspection, not reproduction.

**Metadata.** Andre Kassis and Urs Hengartner. *UnMarker: A Universal Attack on Defensive Image Watermarking*. IEEE Symposium on Security and Privacy 2025, pp. 2602–2620; DOI [10.1109/SP61157.2025.00005](https://doi.org/10.1109/SP61157.2025.00005). Read arXiv 2405.08363v2, 2024-11-22: [full text](https://arxiv.org/html/2405.08363v2). Publication metadata cross-checked against [DBLP](https://dblp.uni-trier.de/rec/conf/sp/KassisH25.html). Inspection: §§IV–VI, Tables I–III, Appendix D; final version differences not checked.

**Mechanism/access.** Query-free spectral disruption through high- and low-frequency optimization, filtering and cropping, without a watermark detector or surrogate diffusion model.

**Evaluation.** 100 images per scheme for seven schemes; data depend on method. Bit-decoding thresholds target a binomial-null probability below .01; Tree-Ring uses a different 2% FPR calibration. Table IIIb's complete attack has 43% StegaStamp detection with LPIPS .08 and 40% Tree-Ring detection with LPIPS .10.

**Limits.** These quality and detection numbers are scheme-specific; the paper's interpretation of sub-50% detection as unusable is not a theorem adopted here. Finite samples and differing thresholds constrain comparisons.

**Thesis implication.** A public encoder is not the only possible removal route. Cropping/spectral attacks partly fall outside the present threat scope; record that limitation without silently adding experiments or counting those attacks as T3 evidence.

