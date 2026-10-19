# Recent journal papers: bounded access closure

Date: 2026-10-19. Agent: Codex completion_recent_papers. Scope: Guo et al. TIP 2025 and Zhao et al. RI-Mark ESWA 2026 only.

**Outcome: neither paper can be upgraded to V2.** Bibliographic identities are verified, but no complete method-plus-evaluation manuscript was obtained. Both remain V1. This closes this bounded lawful-access attempt, not the underlying full-text evidence gap. No paper was downloaded, no experiment was performed, and no code, image, data, or model was acquired.

## What changed

- Guo TIP: the publisher's ordinary PDF/stamp route returned an article HTML page with metadata and abstract, not the PDF. Its embedded metadata identifies DOI 10.1109/TIP.2025.3613958, TIP 34, pages 6386–6401, publication year 2025, and `isOpenAccess: false`. The supplied `pdfUrl` points back to the same stamp route. This is evidence of the response received, not a claim that no lawful manuscript exists elsewhere.
- The previously unresolved Ping Ping homepage at <https://perfectpicture.top/> now opens. It lists the exact TIP title and links to the Hohai institutional profile, DBLP, GitHub, and ORCID, but contains no paper download link. The institutional profile also opens. The linked GitHub account has eight public repositories; their names/descriptions yielded no target manuscript. The homepage repository's complete file-name tree contained no PDF. The terse `C` repository tree returned HTTP 409. No repository source code was downloaded.
- RI-Mark: Crossref and DBLP agree on authors Chengming Zhao, Li Li, Yanli Ren, Guorui Feng, ESWA volume 328, article 132903, DOI 10.1016/j.eswa.2026.132903. Crossref records publication in October 2026. The publisher's indexed preview supplies abstract/highlights, while direct HTML requests failed with 403. The Crossref-listed Elsevier text-mining endpoint returned 429 and did not supply text. Semantic Scholar's exact DOI record returns an empty `openAccessPdf.url`.
- RI-Mark author disambiguation: the Shanghai University Li Li faculty page and DBLP Li Li 0103 bibliography were opened, followed by Chengming Zhao's bibliography. They yielded no manuscript route. DBLP's generic Unpaywall link failed on redirect; its presence alone does not establish an open copy. DBLP flags ORCID ambiguity in the Li Li bibliography, so exact title/DOI and author tuple take precedence over name matching.

## Evidence consequence

The new access information does not change the dossier's V2 total. The two papers cannot support a method novelty exclusion, a quantitative superiority claim, a claim that either lacks content binding, or an assertion that its VAE/regeneration test is equivalent to the thesis protocol. An abstract's author's claim of robustness or imperceptibility remains an unverified empirical assertion for comparison purposes.

For Guo, still unresolved: actual VAE identities and attack implementation, clean quality constraints, reversibility conditions, detector inputs/side information, payload and threshold protocol, sample units, and all attributable comparison numbers. For RI-Mark, still unresolved: exact insertion and recovery algorithm, model/encoder access, training or fitting requirements, detector side information, regeneration protocol, operating points, sample units, and numerical comparability.

## Deliverables and integration

`cards/guo2025robustreversible.md` and `cards/zhao2026rimark.md` are explicit V1 access/evidence cards, not complete V2 paper cards. `matrix-updates.csv` has the same 15-column schema as `02-literature/access-refresh/matrix.csv`; replace the corresponding citekey rows only after parent review, without appending duplicate source counts. `references.bib` carries the verified journal identity, with an explicit not-inspected note. `search-log.md` records every new search and direct route. `metadata-evidence.json` records the inspected metadata fields, including null full-text artifacts.

No shared dossier file, protected state, or bibliography was edited; no commit or push was performed. The literature skill's verified-card synthesis was not run: no full-text-verified input exists, and this session permits the stdlib Python interpreter only for existing-result counting/bounds. No validation success is claimed. CSV parsing, JSON parsing, and link/path existence are checked with PowerShell only.

## Residual route outside this bounded attempt

A lawful publisher subscription/library copy or an author-deposited manuscript would resolve the access dependency. A user-supplied lawful copy may be inspected later. Author contact, institutional login, paid access and external communication were not attempted. Public searches failing to locate a manuscript do not prove its absence.
