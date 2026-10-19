# TrustMark — ICCV 2025 version update

- ID/citekey: `Bui2025TrustMark`; same work as older `Bui2023TrustMark`.
- Title: *TrustMark: Robust Watermarking and Watermark Removal for Arbitrary Resolution Images*.
- Authors: Tu Bui; Shruti Agarwal; John Collomosse.
- Venue/version: ICCV 2025, pp.18629–18639; CVF open-access accepted version, **V2**, read 2026-10-18. DOI: `10.1109/ICCV51701.2025.01731`.
- [Inspected final paper](https://openaccess.thecvf.com/content/ICCV2025/papers/Bui_TrustMark_Robust_Watermarking_and_Watermark_Removal_for_Arbitrary_Resolution_Images_ICCV_2025_paper.pdf).
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/access-refresh/trustmark-iccv2025.pdf`; 6,840,136 bytes.
- SHA-256: `94BE2A50E08356B321C4F64A56579EEB63EA4676634AC9C019E3C76F6C5726F5`.

**Direct evidence, high confidence.** Sections 3–4, pp.18631–18636: learned post-hoc embedder, public decoder, resolution-scaled residual, and ReMark removal. Table 1: alpha=27.5 DIV2K PSNR 42.39±1.46 dB, bit accuracy .95±.09 under its protocol. Table 3: ReMark PSNR 48.48 dB, bit accuracy .553; this is not a thesis-matched regeneration test.

**Direct prior-art evidence, high confidence.** Practical Uses and Limitations, §4.5, p.18636 explicitly recognizes provenance-identifier spoofing and checking the watermarked content against a fingerprint or thumbnail in recovered metadata. References [17] and [19], p.18637 identify earlier Adobe/IEEE provenance work; those references were identified, not independently inspected here.

**Agent inference, contradicting broad novelty.** Identifier retrieval plus record-content checking cannot be claimed as a new architecture. The inspected final does not establish performance on the thesis's regenerate-and-enroll or real-look-alike protocol. Additional retrieved fingerprints/thumbnails are detector side information.
