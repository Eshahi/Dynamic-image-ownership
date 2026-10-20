# Watermark Anything with Localized Messages

[Primary source](https://arxiv.org/html/2411.07231v2). Verification level **V2: methods and evaluation inspected**. Recheck date2026-10-20.

**V2 recheck completed:** §3 and Equations1–2; §5.1 and §5.3 evaluation/calibration, independently reread from cached full paper text.

**Mechanism:** learned embedding plus dense message/localization extraction permits per-pixel masks and localized messages. Equation1 thresholds the fraction of pixel positives; Equation2 aggregates message estimates over detected regions. Code's exact raw-logit aggregation remains separately authoritative for the released adapter.

**Evaluation reread:** reported training uses COCO118k,256 inputs and32bits. §5.3 uses image-score>.07, evaluated on10k first COCO-validation images and DIV2K; the nominal bit-null comparison is approximately2.6e−4, while Table2a reports empirical COCO FPR0.04%. Transform-specific performance/calibration is conditional on that setup.

**Audit use / limits:** native image-presence rule and known-message recovery are different endpoints. The study uses MIT SA-1B release weights, not the COCO-trained model behind that paper calibration. Transfer .5 pixel/.07 image thresholds without claiming its published FPR transfers. Common27/32 agreement is not an image-level false-positive guarantee.

**Read locations:** `paper-wam.txt:532–619,898–935,1158–1208`.
