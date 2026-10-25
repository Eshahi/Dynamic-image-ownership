# Watermark evidence synthesis — WP1

Research-only inspection, 25 October 2026. Twelve V2 cards inspect primary methods and experiment passages; `source-manifest.json` pins each HTML version, external cache path and SHA-256. V2 denotes inspected evidence, not independent reproduction or endorsement of every claim. Bibliography years follow initial arXiv identifiers; version dates are separately recorded. The requested literature skill's evidence discipline was used; generic helper execution was excluded by the research-only subtask instruction.

## What the evidence changes

**Agent inference, high confidence:** “latent watermark” is too coarse a comparison category. Initial-noise sampling (Tree-Ring, Gaussian Shading, RingID, WIND, PRC, SEAL), intermediate-state insertion (ROBIN), decoder training/plugins (Stable Signature, LaWa, WMAdapter), post-hoc optimization through a frozen generator (ZoDiac), and generation-time feature guidance (Guidance Watermarking) expose different channels and require different detectors. F5 is an image-domain writer optimized through the SD1.5 encoder. It must retain that label.

**Direct evidence that conflicts with a universal own-autoencoder-survival story:** Stable Signature §7.1/Figure 7 finds its own generation autoencoder more effective at removal than other autoencoders. LaWa §4.7/Figure 7 retains 85% bit accuracy under its same KL-f8 autoencoder, against 55% for Stable Signature in that comparison. LaWa also warns that PSNR references differ between the papers. These results support method dependence, not a universal sign of encoder alignment.

**Direct evidence of transfer, with a narrower meaning:** WMAdapter Appendix A.4 explicitly describes applying the SD2.1-trained adapter to the SD1.5 VAE without retraining, but gives no quantitative zero-shot table. Its SDXL and DiT results train separate adapters. This is transfer of a decoder plugin across deployment VAEs, not survival of a fixed marked image under a new regenerator. ZoDiac Figure 4 and Guidance §5 also instantiate writers on several generators; that is multi-backbone applicability.

**Agent inference, high confidence:** The inspected sources do not establish the proposed causal contrast: hold image writer, perturbation budget, detector, regeneration noise, denoiser and decoder fixed while changing only an independently trained encoder. This statement is bounded to the inspected versions/sections; it is not a literature-wide absence or novelty claim. SDXL end-to-end failure remains descriptive because the regenerator changes several mechanisms together.

## Detector resources and endpoint discipline

Initial-noise schemes generally require the original generator's encoder/denoiser for inversion and a pattern, key or candidate-noise construction. WIND adds indexed noise search. SEAL adds caption/embedding models and a private salt. Decoder plugins and Guidance can use a learned image extractor without diffusion inversion, but still require a reference message/feature. No enrolled original image is different from no side information.

RingID demonstrates why watermark-presence AUC and multi-owner identification are different endpoints. ZoDiac Table 3 demonstrates why high WDR without a matched FPR is incomplete. PRC's computational undetectability and random-key FPR theorem are different statements from adaptive fixed-key forgery resistance. Gaussian Shading's analytic 10^-6 FPR is not an empirical million-negative calibration. SEAL measures content-forgery defenses but leaves residual failure: private-model forgery AUC is .708 in Table 2.

For the future server study, compare semantic detection, owner/key recovery and enrolled-record matching separately, with matched null sets and declared detector resources. The registry arm carries enrolled content descriptors, which the non-registry initial-noise methods do not receive. These are design implications, not permission to run anything during this session.

## Search boundary

Recent primary coverage includes SEAL v4 (18 May 2026) and Guidance v2 (7 May 2026). Additional recent names are preserved with lower verification in `search-log.md`; no first-ever, absence-of-work, universal robustness or publication-readiness claim follows from this bounded search. DiffMark and BiSLW names supplied by the parent remain V0 leads without verified primary full text.

See `literature-matrix.csv` for mechanism/transfer classification, `evidence-ledger.jsonl` for explicit stances, the twelve numbered cards for checked numerical anchors, and `open-questions.md` for unresolved questions.

## Package check

Twelve numbered V2 cards, twelve manifest entries, twelve matrix rows, twelve explicit evidence-ledger entries and twelve BibTeX entries were checked for matching source identifiers. All twelve inspected HTML cache files exist and their SHA-256 values match the manifest. Numerical spot-checks revisited WIND/RingID attack rows, Gaussian Shading Table 1, ZoDiac Table 3, LaWa Figure 7 discussion/Table 1, WMAdapter Appendix A.4 and Guidance Table 1. These are document/provenance checks, not experiments or independent result reproduction. No generic synthesis helper was executed, per the subtask constraint.
