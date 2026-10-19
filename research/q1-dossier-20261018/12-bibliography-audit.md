# Bibliography metadata audit

Extension E2, 19 October 2026. Scope: every entry in the merged WP2 bibliography, checked against Crossref, DBLP or arXiv where indexed, with official publisher corroboration for conflicts and unindexed documentation. This is a metadata audit, not another method/evaluation reading. The original 87 entries were divided into three disjoint sets of 29; the parent additionally checked the matrix-only V1 entry `fierce2019cnn` before adding it as entry 88.

## Coverage and source policy

The original inputs are preserved as `12-bibliography-audit/part-{1,2,3}/assigned.bib`. Each part supplies a row-level CSV, a human-readable discrepancy report, a corrected BibTeX file and compact retrieved metadata. The parent extra record and source fields are in `parent-extra-audit.json` and `parent-extra-metadata.json`. See [parent integration notes](12-bibliography-audit/parent-notes.md) for source URLs and the distinction between 87 matrix works and a retained predecessor-version bibliography record.

Metadata fields are evaluated separately: title, complete author list/order, year, venue and DOI. A preprint's year or author list can legitimately differ from its final publication. The intended cited object and inspected version govern the correction. A DOI known only for the final article is not evidence that an inspected preprint is textually identical. No fulltext verification level is upgraded because an index confirms a title or publication venue.

The merged `02-literature/references.bib` is the manuscript bibliography. Cluster `cluster.bib` files preserve earlier package snapshots and may retain superseded metadata; use this audit and the merged bibliography for current citations. Existing citekeys remain stable even when their embedded year is historical. Standards and project documentation not indexed in the three services retain explicit official-source or unresolved status; an attempted query is not reported as successful indexed verification.

## Material distinctions for manuscript use

1. **Inspected version versus latest record.** Exact-version URLs are necessary when a newer arXiv revision has changed title, authors or argument. The forensic-stealth entry is pinned to the inspected v1; no v2 claims are silently imported.
2. **Preprint versus final authorship.** SpecGuard's preprint and final author ordering differs. Dual Defense's final publication has a different author list/order from the inspected preprint. DINOv2's versions also require a declared cited object. Preserve the inspected-version caveats rather than presenting mismatched metadata as a single verified final paper.
3. **Official pagination disagreements.** SSCD's CVF page range and the Crossref/DBLP deposited range disagree. The final-paper source used for reading governs the retained CVF pagination, and the discrepancy remains logged. Brown et al.'s indexed wrapper includes discussion/rejoinder pages beyond the main article; retain the main article's page range with that distinction.
4. **Resolvable missing metadata.** The fuzzy-extractors DOI and Cameron–Miller final pagination can be supplied from retrieved records without rereading or changing their substantive argument. Venue corroboration for SERUM can be strengthened from the official proceedings without claiming its final full text was inspected.
5. **V1 remains V1.** The addition of the early CNN zero-watermarking citation fills a bibliography omission only. The inaccessible journal papers, publisher versions and project documentation listed in the access-gap report remain constrained by their actual inspection level.

## Integration result

All original **87/87 entries** have a row-level audit; the checked matrix-only addition brings the master bibliography and normalized audit to **88 entries**. Of the original set, **82** have directly retrieved Crossref, DBLP or arXiv identity records. Three are explicit non-paper official-source exceptions (pHash, C2PA and Adobe documentation); two papers (GROW and the USENIX 2026 perceptual-hash paper) have publisher corroboration but unresolved direct-index retrieval. The extra CNN paper has Crossref and DBLP verification, so **83/88** final entries have direct index records. These are coverage counts, not a claim that every optional DOI or publication field exists.

The parent read all three discrepancy reports and integrated their corrected entries. Previously absent DOI fields were supplied where a matching selected-version record was verified; see the row-level field record rather than aggregating unlike preprint and final-publication additions. The SEAL final citation now uses its final-publication DOI while retaining the inspected-arXiv caveat. Complete authorship was checked; initial/authority variants and genuine preprint-versus-publication ordering differences remain distinguished. The final exact count of nonempty DOI fields is recorded in integration-check.json.

For consistency, the parent selected **first arXiv release year for pure preprint citations** and publication year for publication citations. Accordingly, VINE and WAM use 2024, DINOv2 uses 2023, PRC and WIND use 2024, WOUAF uses 2023, and MetaSeal uses 2025 in the merged preprint entries; their inspected revisions and later venues remain explicit. This harmonizes the three auditors' initially different defensible year conventions. It does not assert that the later conference/issue years were false. Keys remain unchanged, and the literature matrix retains its work/version context.

The C2PA release year and fuzzy-extractors DOI were also propagated to the matrix/card; Cameron's final page range was resolved in its card. No V1 source was upgraded at E2. **At that checkpoint**, 79 V2 matrix items comprised 77 research-paper items and two standards/guidance items. E4 later raised the current total to90 V2, as documented below; the older TrustMark bibliography entry remains version history, not an additional unique work.

- [Normalized audit of all 88 entries](12-bibliography-audit/all-entries.csv)
- [Part 1 discrepancy report](12-bibliography-audit/part-1/audit.md), [Part 2](12-bibliography-audit/part-2/audit.md), [Part 3](12-bibliography-audit/part-3/audit.md)
- [Integration checks](12-bibliography-audit/integration-check.json)

Parent retries of both DBLP mirrors for GROW's known record key also failed on 19 October; the direct-index gap remains. No failed fetch is reported as proof of non-indexing.

## Limits

The audit resolves bibliographic identity and source-version errors, not the scientific quality of indexed publications. Crossref and DBLP can contain authority-name, date and pagination artifacts; agreement between indexes is not always independent confirmation. Some source records expose no publication venue or no DOI. These absent fields are recorded without inventing a value. Current publication metadata does not retroactively turn a research preprint into a peer-reviewed source at the date of the evaluated experiment.

The core novelty verdict remains unchanged by metadata corrections: watermark-to-record linkage and watermark-plus-fingerprint verification have direct prior art. The unresolved question is a sufficiently identified empirical contribution under compatible tasks and fresh negative evidence.

## E4 metadata extension

The 88-entry totals above describe the completed E2 checkpoint. E4 adds eleven separately checked works, bringing the current master to 99 entries. Their title, author sequence, year, cited object and DOI qualifications are logged in `14-forward-citation-sweep/bibliography-additions-audit.csv` and the linked lane identity records. Each addition has an arXiv, DBLP or Crossref identity check; NRGMark's title, five authors, year, venue, DOI and pages were additionally retrieved directly from Crossref by the parent. Thus 94 of the current 99 entries have direct index identity records; the same three official-source exceptions and two publisher-corroborated direct-index gaps remain. E2 snapshot JSON files are historical, not current total assertions. RAVEN's final proceedings DOI is still unverified and omitted; its scientific reading remains a preprint.
