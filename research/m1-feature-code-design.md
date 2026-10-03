# M1 feature coding diagnostic, frozen before execution

Exploratory saved-development-feature analysis; no held-out data, new images or trained parameters. This implements the independent method derivation's recommendation to distinguish feature geometry from code transport. It is not another embedding family.

Reuse all 24 validated C0/C1 CLIP vectors and all 66 frozen source pairs in the existing v5 development output, pinned by SHA256 `58766c579377f344770887e6cad8bf4ed779ee207c2b6872b4a24ac4a90b9b4d`. Labels remain earlier agent topic judgments, not human ground truth. Seven same-topic and 57 different-topic pairs enter descriptive AUC; two uncertain pairs remain in the exported pair table. Preserve failed parent conditions separately.

Compare original 32-bit v5 code, full 512-dimensional cosine, 32- and 128-dimensional real Gaussian projections, and their sign quantizations, plus 512-bit Gaussian signs. Fix PCG64 seeds 20261003, 20261004, 20261005 before running; retain every realization, never choose a winner. Each seed draws one 512-by-512 normal matrix; smaller representations use its first rows. Normalize projected vectors before cosine. No centering, fitting, threshold calibration or label-aware projection. Report per-arm pair AUC and paired C0/C1 source drift. All results are descriptive and correlated; no population error rate or p-value.

This isolates coding geometry only. A real vector costs far more payload than its sign code; no delivery channel is modeled, and better AUC cannot establish a useful watermark. A prospective carrier test is necessary before adopting any representation. The frozen projection seeds can be replaced only under a new declared method, preserving this full result.
