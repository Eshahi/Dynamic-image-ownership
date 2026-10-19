# Parent metadata and integration notes

E2, 19 October 2026. The initial bibliography has 87 entries; the matrix also has 87 rows, but these are not the same set. `Bui2023TrustMark` is an explicitly retained predecessor version of the separately listed final TrustMark work. Matrix-only `fierce2019cnn` is V1 and was absent from the merged bibliography. No manuscript citation was unresolved, and every citation in the full E1 sections matched a V2 matrix row.

The parent checked the omitted matrix entry using [Crossref](https://api.crossref.org/works/10.1109%2FIWBF.2019.8739245) and [DBLP](https://dblp1.uni-trier.de/rec/conf/iwbf/Fierro-RadillaN19.html), accessed 19 October. Crossref was retrieved through PowerShell after the browser tool could not open its API URL; selected source fields are saved in `parent-extra-metadata.json`. The DBLP mirror opened successfully. The [UNAM institutional record](https://produccion.siia.unam.mx/Publicaciones/ProdCientif/PublicacionFrw.aspx?id=535484) corroborates abbreviated author names and the DOI, but is not the method/evaluation full text.

| Field | Crossref record | Decision |
|---|---|---|
| Title | A Robust Image Zero-watermarking using Convolutional Neural Networks | Matches matrix apart from harmless capitalization. |
| Authors | Atoany Fierro-Radilla; Mariko Nakano-Miyatake; Manuel Cedillo-Hernandez; Laura Cleofas-Sanchez; Hector Perez-Meana | Add complete five-person list from Crossref. DBLP authority adds initial N. to Atoany and accents to two names; not a distinct authorship claim. |
| Year | 2019; published-print May 2019 | Matches matrix. UNAM's January placeholder is not used as publication date. |
| Venue | 2019 7th International Workshop on Biometrics and Forensics (IWBF) | Add verified venue and pages 1–5. |
| DOI | 10.1109/iwbf.2019.8739245 | Same DOI, case-insensitive. |

`parent-extra.bib` adds an 88th metadata entry, retaining the existing opaque key to avoid breaking references. It does not upgrade V1 to V2, add evidence for an algorithm claim, or change the unique-work count. Final bibliography count will therefore differ from the 87-entry assignment count; the audit consists of the original 87 plus this independently checked addition.

## Integration policy

1. Preserve citation keys and inspected-version notes. A final DOI or venue does not establish full-text identity with an inspected preprint.
2. Correct substantive title/author/identifier errors using an opened named record. Cosmetic accent, name-authority and punctuation differences are logged without manufacturing an authorship change.
3. A missing DOI is not equivalent to a nonexistent DOI. Add one only when its record matches the intended version.
4. Standards and project documentation may not be indexed in Crossref, DBLP or arXiv. Record the attempted check and official-source verification; do not label every field as indexed verification.
5. Preserve all original source snapshots in the three `assigned.bib` files. Integrate corrected entries into the master bibliography only after reading each audit. Cluster bibliographies are historical package snapshots; the merged bibliography and E2 audit govern current manuscript metadata.
6. Fulltext verification counts are unchanged by metadata corrections. Consequential inaccessible publications remain explicitly incomplete.
