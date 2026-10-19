# RAVEN — V2 source card

- **ID / key:** arXiv:2601.08832 / `Shamshad2026RAVEN`.
- **Title:** RAVEN: Erasing Invisible Watermarks via Novel View Synthesis.
- **Authors:** Fahad Shamshad; Nils Lukas; Karthik Nandakumar.
- **Year / venue:** 2026; CVPR 2026, pages 82–91, metadata verified. Scientific evidence below is pinned to arXiv v1, 13 January 2026, the only version shown on the current abstract page. Final proceedings fulltext was not inspected and equivalence is not asserted.
- **DOI:** 10.48550/arXiv.2601.08832 (preprint); final proceedings DOI unverified/null.
- **Primary fulltext:** https://arxiv.org/html/2601.08832v1 ; history https://arxiv.org/abs/2601.08832 . Accessed 19 October 2026.
- **Metadata cross-check:** CVF landing page https://openaccess.thecvf.com/content/CVPR2026/html/Shamshad_RAVEN_Erasing_Invisible_Watermarks_via_Novel_View_Synthesis_CVPR_2026_paper.html and DBLP https://dblp.org/pid/243/3102.html (`conf/cvpr/ShamshadLN26`) agree on authors/title/year/pages. CVF HTML retrieved through PowerShell; browser-tool final PDF requests failed.
- **Inspection:** V2 depth: §§3–6, Tables 2–5, Appendix results and references. No reproduction or visual assessment.

**Direct evidence, supporting, high confidence.** §4 combines partial latent noising, spatial translation, reference-guided attention and color/contrast transfer. §5 uses a frozen refiner, empty prompts, strength .15, 50 steps and A100; victim detection access is unnecessary. Sources use SD2.1-generated images from COCO, DiffusionDB and SD-Prompts; detection uses 1000 pairs. Table 2 has six TPR and eight bit-accuracy columns: MS-COCO mean TPR .026, TrustMark BA .476. Table 3 gives FID 40.18. Reference [5] is old TrustMark 2311.18297; [16] is SynthID 2510.09263. The latter is introductory, not an evaluated victim.

**Agent audit / inference.** The abstract says fifteen watermarkers, §5.1 enumerates fourteen, and quality/results prose says sixteen. Use the explicit Table 2 population and keep the discrepancy visible; do not average across incompatible detection and bit-recovery outcomes. FID and prompt alignment do not establish instance identity, strict per-image quality, or lawful ownership. Global latent translation should not be described as validated 3D scene reconstruction. The paper motivates a potential active removal gap but supplies no F5 or registry experiment. Multiple Stable Diffusion checkpoints do not establish independent-encoder transfer. Passive EV77 enrollment rejects beta at the owner gate, so its zero-beta outcome neither tests RAVEN nor identifies q/content benefit. Final-version differences remain an access gap.

**Citation classification:** exact old-TrustMark and SynthID edges; TrustMark work-family relevance only for the final ICCV target. DREW, RelZero and soft-binding target edges were not found in this v1. No final-version edge inferred.

**Local inspected artifact:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/shamshad2601v1.html`; 441801 bytes; SHA256 `A5149D96EC0823507127E2E33410130766D9EB158334771EC24D983BA6388589`. HTML only; linked images not fetched. CVF metadata HTML is cached separately as `raven-cvf.html`.
