# 2026 removal extensions

Inspected 2026-10-19; all scientific versions below are arXiv v1. V2 records reading, not endorsement.

## MarkNull

Extends [dossier card](../../../../q1-dossier-20261018/14-forward-citation-sweep/synthid-relzero/cards/cao2026marknull.md). [2608.10166v1](https://arxiv.org/html/2608.10166v1), §§5, 7.1–7.3/Table 2 and Appendix B. Proxy SD1.5 inversion followed by latent orthogonality/perceptual optimization; MarkNull-A amortizes it into a trained network. Appendix B: Adam .05, 50 gradient steps, loss weights 1/20/1.5/3. §7.2 reports mean multibit accuracy 53.14%; Tree-Ring TPR@1%FPR 43% (MarkNull), 63% (A). These are different endpoints. Orthogonality alone does not imply statistical independence for arbitrary distributions; do not import the prose as a general theorem. SynthID testing is a small service-specific experiment, not internal-detector access. The paper's placement of VINE in “fine-tuning-based” methods does not change VINE's post-hoc task status.

## RAVEN

Extends [dossier card](../../../../q1-dossier-20261018/14-forward-citation-sweep/active-removal/cards/Shamshad2026RAVEN.md). [2601.08832v1](https://arxiv.org/html/2601.08832v1), §§4–5, Tables 2–3. Uses latent translations, reference attention, color/contrast transfer. §5.1 names “Image-to-Image Stable Diffusion Refiner,” 50-step DDIM inversion, .15 strength, CFG 2.5, empty prompts, diagonal shifts ±24–32 pixels. Exact checkpoint identity/revision is not supplied there: do not silently identify it as a particular SDXL release. Table 2 RAVEN Tree-Ring TPR .025; VINE bit accuracy .600. Narrative counts conflict; retain table-specific populations. Final CVPR text was not version-compared.

## Watermarks Attack Watermarks

Extends [dossier card](../../../../q1-dossier-20261018/14-forward-citation-sweep/active-removal/cards/Bulychev2026WAW.md). [2605.16796v1](https://arxiv.org/html/2605.16796v1), §§3.3–7, Tables 1–4/7, Appendix C. A trained method classifier chooses public same-method re-embedding or ZoDiac. No victim-key or detector query is needed at inference, but access/training exceed generic regeneration. Appendix C selects top 500 aesthetic images per dataset. §6 reports Tree-Ring TPR 28% after classifier errors; WAM/RoSteALS retain detection while bit accuracy falls below 75%. Payload corruption, original detection and attacker-payload recovery must remain separate. Its regeneration comparators use WAVES-style prompts/rinsing; the main WAW attack is not another sampler setting.

## DRIFT

New September-2026 source: [2609.08213v1](https://arxiv.org/html/2609.08213v1). Read method §§3–4/Algorithms 1–2, experiments §5/Tables 1–2 and Appendix E. SD2.1 re-noising plus stochastic reversal; optional family identification, detector-query ladder and DPPO refinement. Table 1b reports fixed .70 strength ASR 100%, PSNR 14.31 dB versus adaptive-no-refinement 99.7%, 23.72 dB. These are author-reported, not our outcomes. §5.2 compares three deterministic with three stochastic samplers, 100 images/cell; §5.4 uses 300/family. Fixed-strength and query-adaptive results are distinct. The ladder guarantee assumes monotonic realized decisions/distortions; it is grid-relative. This motivates reporting stochastic-sampler exclusion, not silently adding an adaptive optimizer to core.
