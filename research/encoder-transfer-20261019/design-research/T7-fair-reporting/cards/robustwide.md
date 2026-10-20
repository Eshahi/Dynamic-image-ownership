# Robust-Wide: Robust Watermarking against Instruction-driven Image Editing

Stable ID: t7_robustwide. Citation key: T7_robustwide_2024. ECCV 2024; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Runyi Hu; Jie Zhang; Ting Xu; Jiwei Li; Tianwei Zhang.

Canonical venue: https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/3220_ECCV_2024_paper.php
Full text actually inspected: https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/03220.pdf
Revision: ECCV 2024 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\robustwide-paper.pdf`; SHA-256 `33171a8b6d26ec2292c5e8904aad9342f10f9ff4fbe362355fc020779d171860`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\robustwide-paper.txt`; SHA-256 `7913743971cd04fec99b24f0a97a988885a1a7242ac0d6443bbf19df865305a5`.

Method locator: Final ECCV PDF §§3.1–3.5. Evaluation locator: §4 setup and§§4.1–4.2, Tables1–3. Personal reinspection windows (cached text, 1-based lines): [(276, 450)].

## Mechanism and threat model

[direct-evidence] U-Net embedder/residual-block extractor trained through last-k-step partial instruction-driven denoising sampling guidance, with pixel/VAE fidelity and clean/edited extraction losses.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: 1,200 held-out image-instruction samples; additional30 real images (6 types×5), each6 instructions×8 generations=1,440 edited outputs. The latter are30 sources, not1,440 independent originals.

[direct-evidence] Metrics: BER, PSNR, SSIM, CLIP-I and CLIP-T editability measures.

[direct-evidence] FPR operating point: No fixed image-FPR point or image detection test in inspected evaluation. Unmarked BER around50% (Table3) is not a measured image false-positive rate.

[direct-evidence] Quality practice: Released model capacities/resolutions differ; CIN resized128→256→128, MBRS/SepMark native256, default proposed512. Reports64/256-bit variants. Comparable visual quality is author's interpretation, not exact matching.

[direct-evidence] Baselines: DWT-DCT, DWT-DCT-SVD, RivaGAN, MBRS, CIN, PIMoG, SepMark; PIMoG trained from official code because no weights.

[direct-evidence] Conditional numbers: Table1 Robust-Wide64 at512: edited BER2.6579%, PSNR41.9142, SSIM.9910;256-bit BER4.1867%, PSNR39.1842, SSIM.9844. Removing PIDSG raises64-bit BER50.1558% while PSNR55.3710; this clean-quality increase does not establish superior robustness.

## Interpretation and limits

[agent-inference] Explicitly list native capacities/resolutions and repeated outputs, and jointly report clean quality plus robustness. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Training editor InstructPix2Pix is also default evaluation editor; robustness to it is not independent-encoder transfer. Capacity and preprocessing differ across baselines.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
