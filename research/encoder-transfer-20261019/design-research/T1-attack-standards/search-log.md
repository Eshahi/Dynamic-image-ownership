# T1 search and inspection log

Date: 2026-10-19. Stage 1 only: no GPU, model weights, executable third-party checkout, image inspection, attack execution or outcomes. Author: Codex T1 research agent. Textual papers and official source files are cached only in MAIN `.thesis-build/q1-research-20261018/cache/`, using `T1-` filenames. `source-manifest.json` records URL and SHA-256. Code files were read as text, never imported or executed.

The authoritative MAIN STATE and this branch's BRIEF were read. Existing cards were located with `rg` in `02-literature` and the dossier's `14-forward-citation-sweep`. These are extensions, not replacement cards.

| Search / route | Finding and disposition |
|---|---|
| Existing dossier: `MarkNull`, `RAVEN`, `Watermarks Attack Watermarks`, `rinsing`, `CtrlRegen`, `WAVES`, `W-Bench`, `VINE`, `DiffPure` | Reused prior V2 cards and their version caveats; fetched primary text for setting-level inspection. |
| Live web: `"MarkNull" watermark`; `"RAVEN" watermark removal`; `"Watermarks Attack Watermarks"` | Primary arXiv and CVF routes; unrelated commercial and social results discarded. Named 2026 papers inspected at the dossier versions. |
| Live web: `site.arxiv.org image watermark removal benchmark 2026 regeneration` and corresponding `2025` query | Found SemanticRegen 2505.08234, challenge winner 2508.21072, Ni 2510.05978, DRIFT 2609.08213, and official competition report. DRIFT and SemanticRegen receive additional cards; Ni remains quarantined. |
| Live web: `site.github.com NVlabs DiffPure watermark diffusion 2205.07460` | Official DiffPure repository; arXiv metadata establishes only v1. Read v1 full HTML, including method, evaluation and implementation appendix. |
| Official VINE and WAVES repositories, recursive Git tree then raw selected source at tree SHA | Read regeneration entry points and VINE stochastic utility. No cloning or execution. VINE source exposes SD2.1 non-base stochastic checkpoint, 50-step schedule with partial execution; deterministic path uses SD2.1-base. |

Inspection locators are in `cards/` and the setting matrix in `synthesis.md`. Primary caches: VINE v2, WAVES v3, Zhao v3, CtrlRegen v2, UnMarker v2, MarkNull v1, RAVEN v1, WAW v1, DiffPure v1, DRIFT v1, SemanticRegen v1, challenge winner v1. Inspecting V2 means reading method/evaluation, not validating or reproducing claims.

Access issues: Zhao v4 URL did not resolve; inspected existing verified v3 instead. DiffPure guessed v3/v4 HTML routes returned 404; metadata identified v1, successfully read. PMLR PDF web extraction failed due to size; v1 HTML supplied method/evaluation. RAVEN final CVF fulltext remains unverified here; use v1, retaining prior final-version gap. One exploratory `2503.01805v1` fetch is excluded from the evidence manifest and all claims because its identity was not verified. Ni was rechecked against the dossier quarantine and remains excluded from positive evidence. No source is called final solely from a venue label.

Coverage is systematic for the named topic, with a targeted 2025–2026 sweep through 2026-10-19. It is not an exhaustive census of all image editing/removal papers. NFPA, Imprint and NoisePrints are leads cited by MarkNull, not independently V2 claims in this folder. They require separate inspection if promoted to costed execution proposals. No scientific claim here relies on search snippets or secondary sites.
