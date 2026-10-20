# WAVES: Benchmarking the Robustness of Image Watermarks

Stable ID: t7_waves. Citation key: T7_waves_2024. ICML 2024; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Bang An; Mucong Ding; Tahseen Rabbani; Aakriti Agrawal; Yuancheng Xu; Chenghao Deng; Sicheng Zhu; Abdirisak Mohamed; Yuxin Wen; Tom Goldstein; Furong Huang.

Canonical venue: https://proceedings.mlr.press/v235/an24a.html
Full text actually inspected: https://arxiv.org/html/2401.08573v3
Revision: arXiv 2401.08573v3 (official PDF transport failure). Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\waves-reused.html`; SHA-256 `238ffa869b2b8424a92aeeef27e39d7b7909b33ed487a3d4e794e7e6f67e7a08`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\waves-reused.txt`; SHA-256 `690276accbb6797976feb292164895da991323a791f98f28b5e933fdf3ce915c`.

Method locator: arXiv 2401.08573v3 §§3.1–3.2; Appendix E.1–E.6. Evaluation locator: §§4.1–4.3; Appendix D.1 and E.2–E.6. Personal reinspection windows (cached text, 1-based lines): [(646, 730), (851, 945), (2546, 2602)].

## Mechanism and threat model

[direct-evidence] Benchmark, rather than a new watermark: evaluate detection and user identification separately; vary attack strengths and plot detection performance against image degradation.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: 5,000 reference images/prompts per DiffusionDB, MS-COCO and DALL·E3 dataset (15,000 references total); the large set of attack outputs is not 15,000 independent sources per attack family.

[direct-evidence] Metrics: TPR at 0.1% FPR; identification accuracy; PSNR, SSIM, NMI, FID, CLIP-FID, LPIPS, aesthetics and artifact scores; normalized quality degradation (NQD).

[direct-evidence] FPR operating point: Empirical ROC-based TPR@0.1% FPR; Appendix C separately discusses nominal message-null p-values. A high AUROC or message accuracy is explicitly insufficient.

[direct-evidence] Quality practice: Multiple attack strengths; joint performance–quality plots. NQD uses 10th/90th quantiles over the benchmark's attack distribution and four metric categories. This is not per-source three-metric caliper matching.

[direct-evidence] Baselines: Stable Signature, Tree-Ring, StegaStamp in the main benchmark; other methods in extensions.

[direct-evidence] Conditional numbers: Three main watermark methods, 26 attacks, three datasets and eight quality metrics. Appendix E ranks quality at TPR 0.95 and 0.7, and reports unattained intersections explicitly.

## Interpretation and limits

[agent-inference] Keep joint quality–robustness panels, explicit operating points and unattained/sparse cells; retain separate PSNR/SSIM/LPIPS rather than naming their average WAVES NQD. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: The inspected full text is arXiv v3, not the failed official proceedings PDF. Official ICML 2024 identity is verified separately. Its larger, filtered source distribution and attack normalization cannot be imported into n=60 development data.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
