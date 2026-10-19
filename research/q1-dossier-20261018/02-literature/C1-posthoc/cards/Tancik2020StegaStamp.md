# StegaStamp: Invisible Hyperlinks in Physical Photographs

- Citekey: `Tancik2020StegaStamp`
- Authors: Matthew Tancik; Ben Mildenhall; Ren Ng.
- Year / venue: 2020; CVPR 2020.
- Version: CVPR published PDF; inherited inspection 2026-10-03.
- Primary source: [paper](https://openaccess.thecvf.com/content_CVPR_2020/papers/Tancik_StegaStamp_Invisible_Hyperlinks_in_Physical_Photographs_CVPR_2020_paper.pdf); arXiv: not used; DOI: not verified for this inspected version (omitted from BibTeX).
- Access / inspection date: 2026-10-18; inherited method/experiment inspection 2026-10-03.
- Verification: V2 — explicit inherited primary inspection; version-specific, not a quality endorsement.
- Exact inspection locators: PDF pp. 3–7, Sections 3–5, Tables 1–2.
- Artifact: `research/literature/m1-primary-extension/stegastamp-cvpr2020.pdf`; SHA-256: `ab57fbc1ae99931590165fca9df88dff996fcc9e80b4621a8983c7bb1f0a22cf`.
- Setting: Post-hoc digital images intended for print/display recapture.
- Detector side information: Learned decoder; localisation/rectification for photographs; no original.
- Threat: Physical recapture and conventional distortions; not diffusion removal.

**Mechanism/payload.** A residual U-Net embeds 100 encoded bits in 400×400 images; spatial-transformer-assisted decoding recovers the message. A separate segmentation/localization stage supports physical photographs. Error correction reduces useful payload below the encoded length.

**Evidence.** Inherited primary inspection records 1,890 physical captures across six display/print conditions and three cameras, with mean 98.7% bit recovery after manual cropping/rectification. Table 2 evaluates 500 images with 100-bit messages: PSNR 28.50 dB, SSIM 0.905 and LPIPS 0.101. These are this physical-watermark protocol's results, not a diffusion benchmark.

**Access/limits.** Rectification assumptions and image resizing matter. The physical experiment does not show robustness to modern diffusion regeneration or content-transfer forgery.

**Thesis inference.** An invisible short identifier resolving to external information is old. The thesis contribution must concern the specific regeneration/record-binding problem, not the existence of a semantic pointer.

**Inherited provenance.** `research/literature/m1-primary-extension/cards-additional.md`, StegaStamp entry, inspected 2026-10-03 using retained primary PDF. This session verified the artifact hash; no new full-paper reading is claimed.

