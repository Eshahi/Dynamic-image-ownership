# RingID: Rethinking Tree-Ring Watermarking for Enhanced Multi-Key Identification

Stable ID: t7_ringid. Citation key: T7_ringid_2024. ECCV 2024; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Hai Ci; Pei Yang; Yiren Song; Mike Zheng Shou.

Canonical venue: https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/4104_ECCV_2024_paper.php
Full text actually inspected: https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/04104.pdf
Revision: ECCV 2024 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\ringid-paper.pdf`; SHA-256 `09a2be633d53dda926f0bae2677fdb6c107f0791375b0fed655e56b52dcb046b`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\ringid-paper.txt`; SHA-256 `a6e5e5c43eab052450777e71d41c38dac77626752b4ab267133f34e584801c96`.

Method locator: Final ECCV PDF §§4–5. Evaluation locator: §§6.1–6.2 and Tables1–2. Personal reinspection windows (cached text, 1-based lines): [(246, 315), (411, 515)].

## Mechanism and threat model

[direct-evidence] Reexamines Tree-Ring distribution shift and proposes heterogeneous channel watermarks, discretization, lossless imprinting and rotation-oriented changes to improve multi-key identification.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: Verification:1,000 marked and1,000 unmarked images; generation-quality FID:5,000 generated images against COCO2017 training. Identification trials' image count not explicitly stated in inspected§6.1/Table2.

[direct-evidence] Metrics: Verification ROC-AUC; multi-key identification accuracy; CLIP score and FID.

[direct-evidence] FPR operating point: Main verification table reports ROC-AUC, not a fixed low-FPR TPR. AUC1.0 clean is not a calibrated image-FPR guarantee.

[direct-evidence] Quality practice: Same SD-v2 model,50 generation/inversion steps, fixed distortion settings. Distributional generation quality compared with Tree-Ring; no paired source-to-mark fidelity caliper.

[direct-evidence] Baselines: Tree-Ring in main verification/identification tables.

[direct-evidence] Conditional numbers: With2,048 keys, RingID mean identification accuracy.819 including crop&scale, .942 excluding it (Tree-Ring.066/.077). RingID crop&scale identification.080 despite verification crop&scale AUC.987. CLIP.365/FID26.13 versus Tree-Ring.364/25.93.

## Interpretation and limits

[agent-inference] Keep detection, exact identity and content binding distinct; never hide a difficult cell by reporting an attack-excluded average alone. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Official ECVA title is Rethinking Tree-Ring Watermarking for Enhanced Multi-Key Identification; RingID is the method/paper alias. Main identification averages excluding C&S must be labelled. FID is not equal paired distortion.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
