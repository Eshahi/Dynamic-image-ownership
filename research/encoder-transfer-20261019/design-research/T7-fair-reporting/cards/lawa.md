# LaWa: Using Latent Space for In-Generation Image Watermarking

Stable ID: t7_lawa. Citation key: T7_lawa_2024. ECCV 2024; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Ahmad Rezaei; Mohammad Akbari; Saeed Ranjbar Alvar; Arezou Fatemi; Yong Zhang.

Canonical venue: https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/12460_ECCV_2024_paper.php
Full text actually inspected: https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/12460.pdf
Revision: ECCV 2024 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\lawa-paper.pdf`; SHA-256 `735711486683ed3389fa1c350449cccb8710b3d29b23d7de57756f71538c4fcb`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\lawa-paper.txt`; SHA-256 `aeac7c82e9efbb42156429d0656653f3b5ab5b0d0d232f68073ee4f76953c188`.

Method locator: Final ECCV PDF §§3.1–3.4. Evaluation locator: §§4.1–4.2 and4.6, Table1 and Figure6. Personal reinspection windows (cached text, 1-based lines): [(191, 265), (330, 429), (450, 456), (581, 660)].

## Mechanism and threat model

[direct-evidence] Inject message-conditioned residual modules before upsampling stages of a frozen latent decoder; train extractor plus quality/perceptual/adversarial losses. Can operate in-generation or post-generation.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: 1,000 generated512×512 images from COCO/MagicPrompt-SD prompts, each watermarked with10 messages; CLIC428 test images (long dimension resized1024). Detection analysis uses1,000 images with one fixed48-bit message. Attribution: 50,000 messages × 2 images = 100,000 generated images; this is a different experiment, not the 1,000-source robustness cohort.

[direct-evidence] Metrics: PSNR/SSIM/LPIPS/SIFID, bit accuracy, embedding time, detection TPR and theoretical FPR, attribution accuracy versus user count.

[direct-evidence] FPR operating point: §4.6 computes FPR_det from Eq.7 binomial/message-null formula, while TPR is empirical on1K positives; supplementary validation is referenced. Claims at1e-15 or1e-9 are not finite-negative empirical resolution.

[direct-evidence] Quality practice: 32/48-bit strata, quality and bit accuracy jointly shown; RoSteALS retrained with same data/attacks, other baselines native pretrains. No per-source PSNR/SSIM/LPIPS matching.

[direct-evidence] Baselines: Stable Signature, HiDDeN, RivaGAN, RoSteALS, SSL, FNNS, DCT-DWT.

[direct-evidence] Conditional numbers: Table1 generated LaWa-in-generation32: PSNR34.25, SSIM.89, LPIPS.03, SIFID.01, average bit.99;48-bit version PSNR33.52, SSIM.86, LPIPS.04, average bit.97. §4.6 >95% crop10% TPR and >83% combined TPR at nominal1e-9 FPR apply to48-bit detection analysis.

## Interpretation and limits

[agent-inference] Keep arbitrary-message capacity separate from detection and attribution; report independent sources rather than image×message trials as n. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Ten messages per image are repeated measures. Theoretical tails, post-/in-generation modes and32/48-bit capacities must not be pooled. Final PDF contains stray template text; only identified scientific sections support claims.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
