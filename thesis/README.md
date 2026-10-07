# M2 writing package

Status: draft, 2026-10-07, author Codex agent. The user authorized continuation after the independent M2 review. This package applies that review to reporting and prepares bounded results/discussion prose; it records no human M2 acceptance, chapter finalization or official lifecycle transition.

Start with [Chapter 5: results](chapters/05-results.md), then [Chapter 6: discussion](chapters/06-discussion.md). The chapters follow RQ1–RQ4 and keep untested comparisons, quality failures and provenance limitations explicit. [The writing map](m2-writing-map.md) connects the current experiment to the unchanged proposal and the preserved earlier outline. The [corrected results report](../research/m2-coco512-results.md) contains the full operational audit; the original report remains at `2a31ed1` and its independent review at `e01d63c`.

## Traceability

- [Claim inventory](evidence/claim-inventory.jsonl): separate writing claims with author, evidence IDs, exact run ID and analysis paths. It does not edit `research/claims.csv`.
- [Evidence bindings](evidence/m2-evidence-bindings.json): source locations and checksums; retained run files remain in the authoritative MAIN checkout.
- [Writing projection](evidence/m2-claim-projection.json): maps the independent review to this prose. It is an author projection, not a second independent review or acceptance verdict.
- [Exhibit provenance](evidence/m2-exhibits-provenance.json): tables and plot use frozen endpoint counts and existing bounds; no new inferential analysis, tuning or raw-image inspection.
- [Writing validation](evidence/m2-writing-validation.json): schema, source/figure/table links and numerical presentation checks.

The figure is supplied as PNG, vector PDF and SVG. Tables have CSV and Markdown versions. The bibliography is copied verbatim from the repository for future citation assembly; these chapters introduce no uninspected external-paper claims or head-to-head literature performance comparisons.

## Reproduce the exhibits and writing inventory

The plotting-only packages are isolated under MAIN `.thesis-build/m2-writing-python`; the science environment was not changed. Exact wheel URLs, versions, licences and hashes are recorded in `research/downloads.md` and [the plotting receipt](evidence/plotting-downloads.json). The first pip attempt timed out before installation; the successful attempt used pinned wheels and reused the existing NumPy/Pillow installations.

Run `scripts/build_m2_exhibits.py` with the science Python interpreter, `--endpoints` set to MAIN `.thesis-build/m1b-confirm/artifacts/M1b-test/coco512-confirm-rerun-1/metrics/endpoints.json`, `--out` set to this `thesis` directory and `--plotting-site` set to the isolated plotting directory. It refuses an input other than the retained endpoint checksum. Run `scripts/sync_m2_claims.py --thesis <this directory> --schema C:/Users/Soroush/.codex/skills/thesis-writing/scripts/_runtime/thesis_agents/schemas/claims.schema.json` with the stdlib/jsonschema interpreter to update the writing inventory after a requested draft revision.

The chapters were also passed through the thesis-writing helper in a scratch directory without `--final`; the [helper receipt](evidence/m2-helper-receipt.json) records draft status and unresolved extensions. The scratch assembly is a validation aid; the readable chapter files are the edited source.

## Boundaries before finalization

The [institutional format checklist](format-checklist.md) remains unresolved; no official university template is supplied. No Word formatting, front-matter approval pages or submission-ready manuscript is inferred. Final results acceptance, institutional scope decisions, human held-out quality verdicts and chapter finalization remain with the user. Future experiments in Chapter 6 are proposals; no new held-out or paid run was launched for this package.
