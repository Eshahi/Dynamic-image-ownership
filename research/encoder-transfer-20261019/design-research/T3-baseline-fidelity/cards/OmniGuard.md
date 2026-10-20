# OmniGuard: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **OmniGuard: Hybrid Manipulation Localization via Augmented Versatile Deep Image Watermarking**. Version/date: arXiv:2412.01615v2 [cs.CV] 01 Mar 2025. Venue: CVPR 2025, pp. 3008–3018; inspected arXiv v2.

Authors: Xuanyu Zhang; Zecheng Tang; Zhipei Xu; Runyi Li; Youmin Xu; Bin Chen; Feng Gao; Jian Zhang. Year: 2024. DOI: not established for this inspected version.

Stable ID: `arxiv:2412.01615v2`. Citekey: `T3OmniGuard2412`. Canonical URL: https://arxiv.org/abs/2412.01615v2

Primary full text: https://arxiv.org/html/2412.01615v2

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/omniguard.txt`
SHA-256: `f0e0aa3ff71deff02222a9deb83af3e2d53d98cdad0c82614dbec0636904228b`

Actually inspected: Sections 3.1–3.6 and 4.1–4.4; Tables 2–5; Appendix A.1–A.4 and B–C; official README, API metadata and app.py.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A proactive dual-watermark network combines an adaptive localization watermark with a robust bit encoder; a passive degradation-aware transformer extracts tamper masks without the original localization reference. Training simulates global editing with frozen SD1.5 VAE reconstruction and local removal, each with probability .5. Only the robust-bit path is relevant to this T3 study.

## Native operating point and detector side information

The paper evaluates 100 raw bits at 512×512, both alone and jointly with a localization image. A MUNIT-based U-Net encoder and ResNet50 sigmoid extractor use resolution scaling; the mask network pads to 1024 and uses window size 14. No numerical calibrated image-presence threshold or ECC is specified. Exact encoder/decoder internal size, quantization and normalization need a faithful release adapter. Unlike EditGuard, mask extraction is blind to the original localization image, but localization accuracy is still a separate endpoint.

## Code, weights, pinned release and licenses

xuanyuzhang21/OmniGuard@2e3c86b3650cb904d2a8a112c640a78895aa93eb. README offers checkpoint.zip through PKU Disk and Google Drive https://drive.google.com/file/d/1khdBDUDIRIhPIKlV0ictcbTdWLh-WFY_/view?usp=sharing and says full training/testing will be released later. No LICENSE in inspected root; official API license is null. The inspected app.py loads a WAM model from a hard-coded local path as well as OmniGuard modules; this demo is not evidence of a self-contained faithful 100-bit adapter. Checkpoint identities/hashes and code/model licenses remain unresolved.

## Published evaluation and regeneration conditions

Table 3 uses 1,000 512×512 UltraEdit images with paired prompts. Bit-only quality is PSNR 42.33/SSIM .992 and BA .981 for InstructPix2Pix, .989 for SD Inpaint* regeneration, .996 for local SD Inpaint. Dual watermark quality is 41.78/.989 with BA .979/.988/.995 respectively. SD Inpaint* regenerates conditioned on a mask, whereas local SD Inpaint preserves untouched pixels. Exact attack strength, sampler, steps and model revisions are not supplied; this is not an empty-prompt SDXL img2img test or a calibrated TPR. Separate localization testing uses 1,000 COCO examples, so those counts/endpoints must not be merged.

## Cost and uncertainty

The paper reports training iteration time .16 seconds per sample versus Robust-Wide 3.675 seconds, and says training can fit an 11 GB GTX1080Ti. General experiments used a 3090Ti server. These are training statements, not inference time or peak VRAM. No target-server measurement exists.

## Limitation and design implication

This is a strong relevant omission to close: it shows VAE-surrogate training and global regeneration results in a post-hoc dual-watermark method. A later expanded benchmark should resolve its partial release, WAM demo dependency and licensing first; no new proposal or core arm is added.

Disposition: **Literature coverage; excluded**
