# Supplemental primary inspections

Access date: 2026-10-18. These sources are not counted among the nine core cards.

## V2: papakipos2022isc

Zoë Papakipos et al., *Results and findings of the 2021 Image Similarity Challenge*, PMLR 176:1–12, 2022 (NeurIPS 2021 competition proceedings). DOI not verified. [Venue record](https://proceedings.mlr.press/v176/papakipos22a.html), [paper](https://proceedings.mlr.press/v176/papakipos22a/papakipos22a.pdf).

Read §§1–3, pp. 5–9/Table 1. More than 200 participants competed in descriptor and unrestricted matching tracks. Instance contrastive learning, score normalization, regional features and global retrieval followed by pairwise/SIFT matching were already used. Separate-mt2 reranked concatenated image pairs with a ViT classifier; ImgFp used SIFT. The measured benchmark concerns transformed source copies, not diffusion-regenerated positives against same-shot negatives. It establishes that adding a second matching stage is architectural precedent, not sufficient novelty. Side information includes reference images/features and, for normalization, background scores; there is no payload.

## V1: official pHash design documentation

Evan Klinger and David Starkweather, undated documentation (site copyright 2008–2010), [Design & Validation](https://www.phash.org/docs/design.html). Read sections “Fixed Length MH Image Hash,” “DCT Image Hash,” and “Hash Storage.” Describes 64-bit DCT and 72-byte Marr-wavelet hashes with Hamming matching and stored-hash search. Corpus size, adversarial collision protocol and same-shot/diffusion operating points are not supplied in the textual documentation; embedded plots were not opened. Treat as mechanism documentation, not V2 quantified evidence or a validated universal threshold. No pHash collision attack paper reached V2 in this bounded search.
