# GROW access closure — full submission text, partial accepted-version inspection

Prepared 2026-10-25 by Codex agent. Bounded follow-up to `grow-2026-primary.md`; no experiment, science interpreter, install, code/model/image/data download, paid access or remote login. The authoritative main-checkout STATE.md was read once. Only this file was written. After initial web-reader failure, root supplied a paper cached under the brief's paper-cache allowance; this agent read it with the existing Node PDF.js document reader.

## Outcome

**Accepted-version gaps remain; the submission-copy coverage is now complete at text level.** Exact Diff-Pure checkpoint and autoencoder lineage remain unverified. The author-hosted submission's appended supplement was read; it does not supply FPR verification experiments. This does not establish their absence from the final accepted paper or its supplement. Retain the original CVF card's partial-inspection label. No separately linked final-version supplementary-document URL was established.

## New primary discovery and access result

The [coauthor's publications page](https://zexijia.github.io/publications), GROW entry at rendered lines 52–68, links an author-hosted PDF through its **PDF** link (link 17). Actual target:

`https://zexijia.github.io/assets/files/GROW__Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models-2.pdf`

Following that link with the web reader failed with `Content length is too large: 13151080` (tool status 400). This was a reader size limit. The GROW entry presents a PDF link; no GROW supplement link was exposed in that entry. Supplement links elsewhere on the same page belong to other papers. Root subsequently cached this actual linked document under the explicit paper-cache allowance and supplied its path. No range request, proxy or access-barrier workaround was used by this agent.

Local path: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/cache-et-final/papers/grow-coauthor-2026.pdf`. Root-reported size: 13,151,080 bytes. Root-reported SHA-256: `DCBA12B1E58FD203BD28077EE48009D509B025973814113368430B5DE999FDAE`. No redundant hashing was performed.

Text from every PDF page 1–14 was inspected using the existing bundled Node executable and `pdfjs-dist/legacy/build/pdf.mjs`: `getDocument({data,disableFontFace:true,isEvalSupported:false})`, followed by each page's `getTextContent()` and joined text items. No rendering, full-text file, experimental script or scientific library was used. An initial console response truncated part of the output; pages 1,5–9 were separately read to close that gap. Visual graph traces and image contents were not inspected.

An automatically surfaced alphaXiv result associated arXiv:2509.22126 with GROW. Directly inspected [primary arXiv metadata](https://arxiv.org/abs/2509.22126), lines 8–17, identifies **Guidance Watermarking for Diffusion Models**, by Enoal Gesny, Eva Giboulot, Teddy Furon and Vivien Chappelier. Therefore that identifier is not a verified GROW preprint. No content of that different paper is used as GROW evidence.

## Additional primary evidence retained (under 150 new words per source)

**Author-hosted submission PDF (version-specific paraphrase).** Anonymous CVPR2026 submission #8345 has 14 pages, with supplement on PDF pp11–14, unlike the named accepted CVF excerpts. Methods occupy pp3–5. §4.2 p6 identifies SD2.1-base for principal experiments; Figure3 labels Diff-Pure s=.5. Reference[26], p9, is Nie et al.'s adversarial purification paper; the attack checkpoint and AE lineage are unspecified in this text. Supplement §8.1 pp12–13 describes angle-grid and overlapping-patch searches, choosing messages by repeated-bit confidence. §8.2 p13 tests SD1.5 and SDXL generation, not an explicitly specified cross-regenerator matrix. Supplement §§7–8 cover theory, attack strength, models, capacity and visuals; no FPR/ROC/negative-population verification experiment is reported in this submission text. Equivalence to the accepted version is unestablished.

The indexed [CVF primary PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Luo_GROW_Watermark_Generation_with_Progressive_Guidance_for_Diffusion_Models_CVPR_2026_paper.pdf), p.35982, §5.2, specifies Stable Diffusion v2.1-base for the principal experiments. This identifies the generation backbone; the retrieved passage does not separately specify the Diff-Pure attack checkpoint. Re-exposed indexed text from p.35980 mentions theoretical analysis in supplementary material. No new supplementary text, FPR table or attack-model specification was retrieved. Indexed pages 35978 and 35983 were also exposed; no additional scientific claims from them are retained here.

The [author README](https://github.com/luopengchen/GROW) was directly re-opened for discovery. No verified mirror/preprint/supplement link resolving the critical gaps was established there. Repository source code, nested documents and attack implementations were not inspected.

## Local inference, separate from source findings

Principal generation-backbone identity cannot establish the attack backbone's identity or independent-autoencoder status. M-ACC on positive marked images cannot by itself establish false-positive calibration on unmarked images. Geometry search selects among multiple trials and adds cost; the direct extraction timing cannot automatically be treated as the cost or FPR calibration of that search. No bound is derived here because neither its complete trial count nor null confidence distribution was established. The safe article treatment remains: relevant direct-extraction generation-time work, with independently trained cross-regenerator survival and calibrated verification unresolved for the final accepted version. Do not import this submission's supplemental findings into the accepted version without a version-qualified citation.

## Exact discovery log

Queries submitted during this follow-up, in order (2026-10-25):

```text
"GROW" "Progressive Guidance" arxiv supplement
"luopengchen" "GROW" watermark
"GROW" "Watermark Generation" "Diff-Pure" model
"GROW" "Luo" "supplementary" watermark
"Luo_GROW" "verification"
"Luo_GROW" "30]" "Nie"
"GROW" "Pengcheng Luo" arxiv
site:openaccess.thecvf.com/content/CVPR2026/ "GROW" "supplemental"
site:openaccess.thecvf.com "Luo_GROW" "supplementary material"
site:openaccess.thecvf.com "Luo_GROW" "false positive"
site:openaccess.thecvf.com "Luo_GROW" "Diffusion models for adversarial purification"
"GROW: Watermark Generation" "supplementary"
"GROW: Watermark Generation" "verification"
"Luo_GROW_Watermark_Generation_with_Progressive" "30"
"Luo_GROW_Watermark_Generation_with_Progressive" "supplement"
site:zexijia.github.io/assets/files/GROW "Diff-Pure"
site:zexijia.github.io/assets/files/GROW "verification"
site:zexijia.github.io/assets/files/GROW "False"
site:zexijia.github.io "GROW" "supplementary"
"GROW" "Watermark Generation" "Nie"
"GROW" "Watermark Generation" "FPR"
"GROW" "Watermark Generation" "non-watermarked"
"GROW" "Watermark Generation" "DiffPure"
"Watermark Generation with Progressive Guidance for Diffusion Models" supplement PDF
"Pengcheng Luo" "GROW" filetype:pdf
"Luo_GROW" "Supplementary Material"
"Luo_GROW" "[30]"
```

Direct navigation: arXiv metadata URL above (success, different paper); author GitHub README above (success); coauthor publications page above (success); its actual PDF link above (web reader size failure, later root-supplied cached paper read in full as text). No previously failed CVF direct-open variants or OpenReview verification-page attempts were repeated. Third-party summaries and derivative implementations appeared in search but were not used as scientific evidence. Negative search results only describe this search's coverage, not nonexistence of documents or experiments.
