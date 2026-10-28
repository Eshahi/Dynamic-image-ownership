# Eighth direct-image TIFS study: primary indexed-text completion

Audit date: 2026-10-28. Disposition: **method and experiment sections inspected through substantive indexed primary text; live PDF unavailable**. This supersedes the access-only result in `tifs-eighth.md` for this candidate. It does not alter that historical access ledger or claim that a PDF was downloaded, hashed, or visually inspected.

## Identity

Xiangli Xiao, Yushu Zhang, Zhongyun Hua, Zhihua Xia, Jian Weng. *Client-Side Embedding of Screen-Shooting Resilient Image Watermarking*. IEEE Transactions on Information Forensics and Security **19 (2024), 5357–5372**, 16 journal pages. DOI [10.1109/TIFS.2024.3397043](https://doi.org/10.1109/TIFS.2024.3397043). Metadata independently checked against the [coauthor's institutional publication record](https://faculty.jnu.edu.cn/wlkjaqxy/xzh2/list.htm), item 2024 [9].

## Compact evidence card

[Primary author-hosted article](https://huazhongyun.github.io/pdf/Client-Side_Embedding_of_Screen-Shooting_Resilient_Image_Watermarking.pdf), inspected via indexed section text:

| Field | Inspected evidence |
|---|---|
| Method | Client decryption embeds a screen identifier; DCT coefficient ordering, I-SIFT regions, confidential pattern/default watermark. Extraction corrects distortion, cross-validates regions, majority-votes and BCH-decodes. Management center knows pattern and assigned identities. |
| Comparators/data | One external family, Fang et al., with two timing configurations. Three visual examples; benchmark dataset, total image n and repeated-trial n UNKNOWN. Seven image sizes; screen-count scaling to 5000. |
| Experiments | Bit-identical Fang control under matched settings; Gaussian noise on encrypted transmission; stage/computational/communication overhead. 24 payload bits encoded to 63; seven-error correction. Table II: 1024-square encryption .4477s, decryption .0282s, extraction .6357s. |
| Theory/ablations/quality | Security analysis inspected only in part; no independently verified security theorem. Scaling/parameter sweeps; complete component-ablation inventory UNKNOWN. Visual quality examples; PSNR/SSIM aggregate, human study and calibrated attribution FPR UNKNOWN. |
| Limits/code | Robustness inheritance is not a new physical capture benchmark. No diffusion evidence established. [Author Matlab code](https://github.com/XIAO-Xiangli/SW) observed. |

Article locators: IV-A p5361; IV-D Algorithms 5–6/Eq19; VI-A–C p5367, Figs7–9/Tables I–II; VI-C Tables III–IV; VI-D Tables VI–VII.

## Access evidence and reproducible retrieval

Direct `open` of the PDF and of its search-result reference returned HTTP404. Targeted web searches nevertheless returned long, coherent indexed excerpts from the same author-hosted URL, including algorithms, equations, section headings, full experiment tables, and journal page headers. These were read, not inferred from a repository summary. The distinction matters: this closes substantive method-plus-experiments inspection, but not saved-artifact or full-PDF visual verification. A future reader may find that the search index has changed.

The following exact search strings recovered the relevant primary-text portions (use the complete PDF URL's filename as the site path):

```text
site:huazhongyun.github.io/pdf/Client-Side_Embedding_of_Screen-Shooting_Resilient_Image_Watermarking.pdf "Image Encryption" "Algorithm 1"
"Client-Side Embedding of Screen-Shooting" "watermark extraction" "B."
"Client-Side Embedding of Screen-Shooting" "B. Robustness"
site:huazhongyun.github.io/pdf/Client-Side_Embedding_of_Screen-Shooting_Resilient_Image_Watermarking.pdf "TABLE III" "TABLE IV"
"Client-Side Embedding of Screen-Shooting" "VI." "TABLE"
```

The first query exposed construction; the second exposed extraction; the third exposed substantive experiment prose and tables; the fourth and fifth exposed further experiment tables. The corpus admission does not depend on an abstract-only search hit. The code link was opened separately; no code, model, image, dataset, package, or paper file was downloaded locally, and no experiment ran.

## Required integration edits for the parent

1. In `01-tifs-bar.md`, change nine distinct / seven core to **ten distinct / eight core**, retaining the two adjacent studies and every existing preprint/final-version caveat. State that one core article was inspected through indexed primary section text while its live PDF returns404. Do not claim ten saved PDFs or eight verified final-journal fulltexts.
2. Add the compact card above as the eighth core row, with its access caveat and UNKNOWN fields. Reference this file alongside the A/B/C cards. Preserve the narrow baseline count; scaling configurations are not separate external methods.
3. Replace the final unfilled-slot disposition with this qualified completion. Keep Imprints, visible-watermark and style-transfer/re-parameterization as uninspected leads. Preserve `tifs-eighth.md` as the earlier access history.
4. Replace any dossier-wide statement that the eight-direct-image **inspection count** is incomplete. Do not remove source/version limitations, and do not imply that literature-count completion establishes TIFS readiness.
5. Add the BibTeX entry below to the dossier's chosen bibliography, avoiding a duplicate DOI. This agent did not edit any shared bibliography.

```bibtex
@article{Xiao2024ClientSideScreen,
  author = {Xiao, Xiangli and Zhang, Yushu and Hua, Zhongyun and Xia, Zhihua and Weng, Jian},
  title = {Client-Side Embedding of Screen-Shooting Resilient Image Watermarking},
  journal = {IEEE Transactions on Information Forensics and Security},
  volume = {19},
  pages = {5357--5372},
  year = {2024},
  doi = {10.1109/TIFS.2024.3397043},
  url = {https://doi.org/10.1109/TIFS.2024.3397043},
  note = {Method and experiments inspected from indexed author-hosted primary section text; live author PDF returned HTTP 404 on 2026-10-28}
}
```

Interpretation by this agent: the study usefully broadens the evidence bar toward deployment cost and detector side information. Its scope does not resolve the new writer's prospective regeneration or ownership claims. It should not be used as an excuse to lower the selected protocol's scientific gates.
