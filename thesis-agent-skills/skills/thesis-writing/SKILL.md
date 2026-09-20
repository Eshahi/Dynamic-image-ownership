---
name: thesis-writing
description: "Draft or revise bounded Markdown or LaTeX thesis sections using approved evidence, preserving citations and explicit unsupported-claim markers."
---

# thesis-writing

Use for a requested chapter or section with an approved scope, synthesis, experiment analysis and independent audit. If these materials are absent, produce a supported outline or marked draft, never invented thesis content. Read existing approved/user-authored text first; revise only the requested span and preserve unrelated prose.

Use claim inventory records with author ID, evidence IDs, exact run IDs, analysis output paths and result/interpretation/limitation/future-work kind. Preserve existing citation keys and approved bibliography entries verbatim. Missing support must be visible as TODO:CITATION or TODO:EVIDENCE. Report negative/inconclusive findings and reproducibility limits, not only favorable results. Methods must identify actual code, data versions, splits, seeds, environment and preregistered criteria.

The deterministic helper assembles already-authored claims into Markdown or LaTeX and retains a thesis-level claim inventory. It refuses an existing chapter path; use a distinct section/revision output for a requested revision and review the diff before merging. LaTeX claim text must already be reviewed for LaTeX syntax; the helper does not compile or rewrite user notation.

Finalization is refused when blocking audit findings remain or claims lack verified traceability. Even a clear audit does not imply human approval: `--final` needs explicit human acceptance bound to the exact audit and claim-set hashes and chapter name. Never create that acceptance yourself. Before final submission, independently verify citations, university formatting and whether cited evidence actually supports the prose.

Authorization: local draft generation/revision within the user's requested scope; no publication or chapter-final approval on behalf of the user.

## Input/output contract

Inputs must match the strict JSON schemas in `scripts/_runtime/thesis_agents/schemas` after installation, or the bundle's `src/thesis_agents/schemas` during development. thesis/{chapters,figures,tables,references.bib,evidence/claim-inventory.jsonl}.

Use `python scripts/write_section.py --help` for the actual argument contract. Errors return nonzero JSON diagnostics. Do not infer success from artifact filenames alone.
