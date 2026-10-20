# Robust-Wide: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **Robust-Wide: Robust Watermarking against Instruction-driven Image Editing**. Version/date: arXiv:2402.12688v1 [cs.CR] 20 Feb 2024. Venue: ECCV 2024 (official proceedings citation 2025,pp20–37).

Authors: Runyi Hu; Jie Zhang; Tianwei Zhang; Jiwei Li. Year: 2024. DOI: not established for this inspected version.

Stable ID: `arxiv:2402.12688v1`. Citekey: `T3RobustWide2402`. Canonical URL: https://arxiv.org/abs/2402.12688v1

Primary full text: https://arxiv.org/html/2402.12688v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/robustwide.txt`
SHA-256: `04878080ead4fc22187d7aa8dcc33361a288664c4b9487ab24e089b1cc4cf27f`

Actually inspected: §§3.1–3.5,4.1–4.4, Tables 1/4; official README/LICENSE.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A U-Net image encoder and residual decoder are trained with partial instruction-driven denoising sampling guidance through the last diffusion steps, improving robustness to instruction editing.

## Native operating point and detector side information

The reported operating point is 512×512 with 64 raw bits. No ECC or native calibrated presence cutoff is specified. The encoder takes image and message; the decoder takes the image, with a known query needed for match-based presence. Exact serialized preprocessing and rounding remain unresolved.

## Code, weights, pinned release and licenses

hurunyi/Robust-Wide@6a2ee6c991b27f36f2980a7de5c6d7b064c9fa11 has a verified MIT LICENSE. The official checkpoint folder is https://drive.google.com/drive/folders/1Y67UuFQiWqX5mA_1TBUs9FB4OUvazrZe?usp=drive_link ; immutable artifact hashes remain unverified.

## Published evaluation and regeneration conditions

Training uses 20,000 pairs; the main test uses 1,200 nonoverlapping images. A real-image study uses 30 images × 6 instructions × 8 samples = 1,440 edits. InstructPix2Pix uses Euler 20 steps, text CFG 10 and image CFG 1.5. Table 1 reports BER 2.6579% and quality 41.9142/.9910; real-image BER is 2.6062% with quality 41.4038/.9922. Table 4 specifies Diffusers SDEdit strength .2, null prompt and other defaults: BER 8.6401% before editing, 3.9071% on marked images and 9.3654% after editing. Exact model revision, sampler and default steps are not specified in that attack paragraph. BER is not calibrated TPR.

## Cost and uncertainty

Training through diffusion steps is expensive, but inference uses learned encoder and decoder. No adequately conditioned inference time or peak VRAM was established; no training or runnable installation is proposed.

## Limitation and design implication

A relevant released editing-robust comparator after P1/P9, but Google Drive checkpoint provenance and the mismatch between editing BER and calibrated presence need resolution before expansion.

Disposition: **Literature coverage; excluded**
