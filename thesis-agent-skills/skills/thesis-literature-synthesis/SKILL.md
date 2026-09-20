---
name: thesis-literature-synthesis
description: "Synthesize inspected papers into paper cards, a literature matrix and a claim-to-source ledger that preserves conflicting evidence."
---

# thesis-literature-synthesis

Use for collected literature, not unsupported narrative generation. Populate paper cards with DOI (null if unknown), canonical URL, title, authors, year, venue, access date, source type, stable paper ID and citation key. Mark verification and exactly what was inspected. A search snippet or metadata record is not full-text inspection. Verified sources require a local inspected artifact and checksum; inaccessible papers remain inaccessible.

Separate each evidence entry into direct-evidence, author-interpretation, agent-inference or open-assumption. Include claim text, source ID, exact inspected locator, supporting/contradicting/inconclusive stance, confidence, limitations and explicit assumptions. Record contradictory evidence alongside favorable evidence. Never invent DOI, pages, quotations, findings or bibliography metadata. Keep quotations short and attributed.

Run `validate_literature.py validate` on the response contract, then `synthesize` with an unused topic output directory. Duplicates by DOI, normalized title, canonical URL or citation key require human resolution; do not silently merge distinct versions. The generated BibTeX contains only supplied verified cards; inspect metadata before treating entries as authoritative. Derive gaps/open questions from limitations and disagreements; do not claim absence of work from an incomplete search.

Authorization: local synthesis and validation are permitted within the requested output. Do not acquire restricted papers or publish results on the user's behalf.

## Input/output contract

Inputs must match the strict JSON schemas in `scripts/_runtime/thesis_agents/schemas` after installation, or the bundle's `src/thesis_agents/schemas` during development. research/<topic>/{findings.md,literature-matrix.csv,evidence-ledger.jsonl,open-questions.md,references.bib,papers/<paper-id>.json}.

Use `python scripts/validate_literature.py --help` for the actual argument contract. Errors return nonzero JSON diagnostics. Do not infer success from artifact filenames alone.
