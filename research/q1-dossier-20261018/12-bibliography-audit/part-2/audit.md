# Bibliography metadata audit: part 2

Audit access date: 2026-10-19. Scope: 29 assigned entries. All original citekeys and inspection notes retained. This audit checks metadata only, does not reopen experimental outputs and does not upgrade an evidence grade or claim final full-text inspection.

26 entries have a successfully inspected Crossref, DBLP or arXiv metadata record. Three are explicit exceptions: pHash and C2PA are official webpage/standard sources; the USENIX 2026 paper is corroborated by official publisher BibTeX but no matching indexed record was successfully located. The latter is a coverage gap, not a proved lack of indexing.

Status vocabulary: match means substantive equivalence after BibTeX escaping, capitalization, punctuation, accents and explicitly documented author authority variants; mismatch means conflicting version identity; absent means a supplied field is missing despite located metadata (or an explicit byline is absent); N/A means no observed DOI or publication-year/venue field is appropriate to that source kind. Missing fields are not proof that a work has no DOI or final venue.

There is one DOI/publication-version mismatch (SEAL), six missing DOI fields with now-verified additions, and one missing specification release year (C2PA). No missing authors or author-order errors were found. pHash personal author attribution is only copyright corroboration, not a verified byline. The DINOv2 2024 year is defensible for the specifically inspected v2 revision; initial preprint year is 2023.

The corrected file keeps preprint citations for WMCopier, DINOv2 and Fairoze rather than importing final author/title/venue metadata into inspected preprints. Metadata on finals is reported as a caveat and candidate citation upgrade, without claiming the final text was read.

## Actionable entry notes

1. **arabi2025seal** — Use final-publication DOI 10.1109/ICCV51701.2025.01503 for this inproceedings citation. Preserve arXiv v4 inspection: updated 2026-05-18, later than ICCV 2025; the two texts were not declared identical. Add final pages 16196--16205. Source: [Crossref](https://api.crossref.org/works/10.1109%2FICCV51701.2025.01503); accessed 2026-10-19.

2. **dong2025wmcopier** — Keep the inspected preprint title, which contains Image. Final NeurIPS 2025 metadata omits Image and has DOI 10.52202/085713-4608; do not silently substitute that final title into the inspected preprint citation. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2503.22330v3); accessed 2026-10-19.

3. **soucek2025oneshot** — All five requested fields match. Add volume 38 and pages 55967--55990 if desired; the initial Crossref 429 was resolved on retry. Source: [Crossref](https://api.crossref.org/works/10.52202%2F085713-1675); accessed 2026-10-19.

4. **thietke2025crypto** — Requested fields match preprint v1. Its arXiv comment says WMark@ICLR, which is workshop evidence, not a main-conference publication claim. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2503.11404v1); accessed 2026-10-19.

5. **roy2004retrieval** — No requested-field correction. Source: [Crossref](https://api.crossref.org/works/10.1007%2Fs00530-003-0116-1); accessed 2026-10-19.

6. **seenivasagam2013qr** — No requested-field correction; Crossref itself supplies initials V. and R., so complete listed authors verified, expanded forenames not established. Source: [Crossref](https://api.crossref.org/works/10.1155%2F2013%2F516465); accessed 2026-10-19.

7. **rocek2021critical** — No requested-field correction. The 2020 string in the DOI is not the publication year; Crossref published date is 2021-01-07. Source: [Crossref](https://api.crossref.org/works/10.1007%2Fs10278-020-00396-0); accessed 2026-10-19.

8. **gharib2025hybrid** — No requested-field correction. Source: [Crossref](https://api.crossref.org/works/10.1038%2Fs41598-025-09290-7); accessed 2026-10-19.

9. **hung2026signcryption** — No requested-field correction. Whole-name braces preserve Vietnamese display order; do not infer family-name segmentation from Western order. Source: [Crossref](https://api.crossref.org/works/10.1038%2Fs41598-026-38991-w); accessed 2026-10-19.

10. **tanvir2026invzw** — No requested-field correction. Published version verified; retain the explicit earlier-arXiv relationship. Source: [Crossref](https://api.crossref.org/works/10.3389%2Ffrsip.2026.1812987); accessed 2026-10-19.

11. **chen2026relzero** — Requested fields match inspected preprint v2. CVPR acceptance is an arXiv comment. No final-proceedings DOI or pagination was verified in this audit. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2603.17531v2); accessed 2026-10-19.

12. **thanh2022pseudo** — No requested-field correction. Whole-name braces preserve Vietnamese display order; metadata inspection does not upgrade paywalled full-text access. Source: [Crossref](https://api.crossref.org/works/10.1007%2Fs11042-022-12079-9); accessed 2026-10-19.

13. **pizzi2022sscd** — Add verified final DOI 10.1109/CVPR52688.2022.01413. CVF author parsing is Roy, Sreya Dutta and Ravindra, Sugosh Nagavara; all names and author order already match. Preserve CVF pages 14532--14542; IEEE/Crossref/DBLP uses 14512--14522. These are alternative publisher paginations, not an established error. Source: [Crossref](https://api.crossref.org/works/10.1109%2FCVPR52688.2022.01413); accessed 2026-10-19.

14. **oquab2024dinov2** — Keep 2024 as the inspected v2 revision year, explicitly record initial preprint year 2023, and add arXiv DOI. Normalize accents and Huy Vo to the inspected arXiv author string. Final TMLR 2024 exists, with Mido Assran rather than arXiv Mahmoud Assran; Huy V. Vo, Hervé Jégou and authority expansions also differ. These are authority/version variants, not missing or reordered authors. Do not mix final author names with inspected preprint metadata. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2304.07193v2); accessed 2026-10-19.

15. **singhi2025dinohash** — Add arXiv-issued DOI 10.48550/arXiv.2503.11195. Preserve note label V2 as dossier evidence grade; actual arXiv version is v1. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2503.11195v1); accessed 2026-10-19.

16. **struppek2022neuralhash** — Requested fields match final publication. Inspected arXiv v5 is dated 2024-07-16, later than FAccT 2022; retain that caveat. Source: [Crossref](https://api.crossref.org/works/10.1145%2F3531146.3533073); accessed 2026-10-19.

17. **leblancalbarel2026blackbox** — Official USENIX BibTeX corroborates all supplied fields and pages 1907--1926. Expand booktitle to include (USENIX Security 26). No indexed metadata record was successfully located; this remains an explicit audit coverage gap, not an unindexed-standard exception. Source: [official publisher; indexed check unresolved](https://www.usenix.org/conference/usenixsecurity26/presentation/leblanc-albarel); accessed 2026-10-19.

18. **cao2020delg** — Add final DOI 10.1007/978-3-030-58565-5_43. Crossref spells André Araujo; arXiv spells Andre. Keep the inspected-preprint author spelling and version note. Source: [Crossref](https://api.crossref.org/works/10.1007%2F978-3-030-58565-5_43); accessed 2026-10-19.

19. **wang2024icdiff** — No requested-field correction. Crossref container includes 37, already represented by separate volume=37. Source: [Crossref](https://api.crossref.org/works/10.52202%2F079017-0460); accessed 2026-10-19.

20. **madden2024practicalhashing** — Add arXiv-issued DOI 10.48550/arXiv.2406.00918. The exact inspected v2 metadata corroborates Third Workshop on New Frontiers in Adversarial Machine Learning at NeurIPS 2024; this is workshop publication, not main NeurIPS. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2406.00918v2); accessed 2026-10-19.

21. **chen2026admcd** — Add arXiv-issued DOI 10.48550/arXiv.2603.13070. No final venue is present in inspected metadata. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2603.13070v1); accessed 2026-10-19.

22. **papakipos2022isc** — Keep publisher publication year 2022 despite DBLP event year 2021. Normalize Zoë and Ondřej. DBLP authority forms Tomás Jenícek and Cristian Canton-Ferrer differ from PMLR display strings; no missing or reordered authors. PMLR exports Ferrer, Cristian Canton; use that parsed form in corrected BibTeX. Source: [DBLP + official PMLR](https://dblp.org/rec/conf/nips/PapakiposTJPYWS21.html); accessed 2026-10-19.

23. **phashdesign** — Use exact page heading Design & Validation, retaining pHash context. Preserve personal attribution only as site copyright attribution; there is no explicit article byline. Leave publication year absent: copyright 2008--2010 does not establish publication date. DOI not applicable to the observed webpage. Source: [official undated webpage; non-paper exception](https://www.phash.org/docs/design.html); accessed 2026-10-19.

24. **kazempourradi2026softbindings** — All requested fields match inspected arXiv v1. Current landing page explicitly lists arXiv-issued DOI via DataCite and no longer displays registration pending. Preserve historical inspection note while appending current check. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2610.04151v1); accessed 2026-10-19.

25. **saberi2024drew** — No requested-field correction. arXiv inserts a space before colon in DREW :; this is harmless punctuation. No final venue established. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2406.02836v2); accessed 2026-10-19.

26. **fairoze2025publicwatermark** — Requested preprint fields match. Official final AISTATS 2025 publication verified, PMLR 258:1891--1899; this metadata check does not establish that the final full text was inspected. Keep preprint citation and append final-publication link. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2502.04901v2); accessed 2026-10-19.

27. **gowal2025synthidimage** — All 26 authors match in order, including Kaczmarczyck and Kaskasoli as spelled in arXiv v1. Title capitalization differs only: Image watermarking at internet scale. No missing-author correction. Source: [arXiv Atom API + landing](https://arxiv.org/abs/2510.09263v1); accessed 2026-10-19.

28. **c2pa24contentcredentials** — Add year 2026 and month April for specification release 2.4, supported by official version-history section 5.3.1. Preserve exact ContentCredentials page title and URL. Corporate author is corroborated by official specification developer statement; no DOI or indexed-record claim. Source: [official standard; non-paper exception](https://spec.c2pa.org/specifications/specifications/2.4/specs/ContentCredentials.html); accessed 2026-10-19.

29. **chandra2024nist1004** — Keep official NIST title and six-author list. Crossref has singular risk and omits all authors; this is a Crossref metadata defect, not evidence that the supplied authors are wrong. NIST official publication page supports supplied wording, authors and 2024-11-20 date. Source: [Crossref + official NIST (authority for title/authors)](https://api.crossref.org/works/10.6028%2FNIST.AI.100-4); accessed 2026-10-19.

## Source and access limitations

- Exact requested fields and full author lists are in audit.csv; compact API records are in arxiv-metadata.json, crossref-metadata.json, crossref-additional.json and sscd-crossref.json. arxiv-doi-landings.json separately corroborates arXiv-issued DOIs, which are not the external-publication DOI field in the Atom API.
- Crossref-searches.json records USENIX title-search nonmatching results and DNS failures for pHash/C2PA. dblp-metadata.json records search attempts; null hits are unusable API responses and are not treated as zero results. Direct DBLP paper records were inspected with the web reader for SSCD, DINOv2 and ISC.
- A candidate DOI 10.1109/CVPR52688.2022.01415 was checked and rejected because its title is CAD: Co-Adapting Discriminative Features for Improved Few-Shot Classification. It is retained only in the retrieval log crossref-additional.json and is never used in audit.csv or corrected.bib.
- Pizzi pagination is source dependent: [CVF official BibTeX](https://openaccess.thecvf.com/content/CVPR2022/html/Pizzi_A_Self-Supervised_Descriptor_for_Image_Copy_Detection_CVPR_2022_paper.html) gives 14532--14542, whereas [Crossref DOI metadata](https://api.crossref.org/works/10.1109%2FCVPR52688.2022.01413) and [DBLP](https://dblp.org/rec/conf/cvpr/PizziRRGD22.html) give 14512--14522. Corrected file preserves the originally cited CVF pagination.
- [DINOv2 final DBLP record](https://dblp.org/rec/journals/tmlr/OquabDMVSKFHMEA24.html) is TMLR 2024, no DOI displayed, and uses Mido Assran and Huy V. Vo. The inspected arXiv v2 list uses Mahmoud Assran and Huy Vo. Both lists have the same 26 positions/identities; no author was dropped.
- [WMCopier final record](https://proceedings.neurips.cc/paper_files/paper/2025/hash/c972859a984a21658432d7320c7df385-Abstract-Conference.html) has title WMCopier: Forging Invisible Watermarks on Arbitrary Images, unlike the inspected preprint, DOI 10.52202/085713-4608, NeurIPS 38 (2025), pages 153114--153144. The preprint remains cited under its own title.
- [Fairoze final PMLR record](https://proceedings.mlr.press/v258/fairoze25a.html) is Proceedings of the 28th International Conference on Artificial Intelligence and Statistics, PMLR 258:1891--1899 (2025). Final author display preserves the same five identities/order. No final DOI was established here.
- [C2PA version history](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html) section 5.3.1 explicitly dates release 2.4 to April 2026. This establishes the specification release date, not a separate revision date for the ContentCredentials subpage.
