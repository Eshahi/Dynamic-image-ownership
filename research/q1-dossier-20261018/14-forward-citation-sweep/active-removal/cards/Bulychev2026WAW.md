# Watermarks Attack Watermarks — V2 source card

- **ID / key:** arXiv:2605.16796 / `Bulychev2026WAW`.
- **Title:** Watermarks Attack Watermarks: Re-Watermarking as a Generic Removal Strategy.
- **Authors:** Maria Bulychev; Neil G. Marchant; Benjamin I. P. Rubinstein.
- **Year / venue:** 2026; arXiv preprint (CoRR). No peer-reviewed venue verified.
- **DOI:** 10.48550/arXiv.2605.16796 (preprint DOI).
- **Inspected version:** v1, 16 May 2026; current abstract page lists only v1. Accessed 19 October 2026.
- **Primary:** https://arxiv.org/html/2605.16796v1 ; version history https://arxiv.org/abs/2605.16796 .
- **Metadata cross-check:** DBLP author record https://dblp.org/pid/198/0542.html confirms title, authors, year and CoRR record `journals/corr/abs-2605-16796`; direct record/XML attempts were blocked and are not metadata evidence.
- **Inspection:** V2 means method plus evaluation reading, not arXiv version 2. Read §§3–7, Tables 1–5/7, Appendix C filtering, G cost and H limitations; searched full reference list. No reproduction or pixel inspection.

**Direct evidence, supporting, high confidence.** §§3–6 route an image through a trained method classifier, then reuse the predicted post-processing encoder or ZoDiac for in-processing marks. Inference needs encoder access, not victim keys/queries. Eight victims and six attack encoders are evaluated on two filtered datasets. Table 4 reports MS-COCO RoSteALS BA .749 but TPR .992, WAM .707/.862, and Tree-Ring TPR .280; corruption and detection are distinct. Table 2 measures replacement-watermark recovery. Appendix G gives ZoDiac approximately ten GPU-hours per dataset–victim pair. Appendix H conditions rankings on thresholds and quality metrics.

**Citation edge.** Reference [4] cites final ICCV 2025 TrustMark, pages 18629–18639, through Table 5's similarity annotation for Pixel Seal. TrustMark is not one of the eight tested victims. Other target edges were not found in this inspected version.

**Agent inference, inconclusive for thesis security.** This motivates separating active replacement, victim detection, message recovery and competing-record acceptance. Recovering an attacker's payload alone does not authenticate lawful ownership, defeat a trusted registry, or establish a whole-pipeline forgery. F5 was not tested. EV77's beta-owner rejection in passive enrollment cannot establish resistance to this active intervention or identify added q/content benefit. The blanket description of the attack as cheap should not be transferred to the ZoDiac route. The abstract's broad removal language should not conceal persistent detection in Table 4. No new baseline or experiment is authorized.

**Local inspected artifact:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/bulychev2605v1.html`; 375780 bytes; SHA256 `DC9A0E3DB08E4948E0A0E514A63E70C41A3C6E35CDD91F596217A4F91B319A4A`. HTML only; linked image assets were not fetched.
