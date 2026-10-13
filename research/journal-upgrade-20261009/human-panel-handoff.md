# Human panel: ready for independent ratings

Prepared 2026-10-13 at build commit `a2007e4`. Three separate offline packets contain 84 pairs each: the census of 72 existing H1 development attacks and 12 unchanged controls. No human ratings have been collected. This is descriptive development annotation under the [frozen protocol](human-development-panel-protocol.md), not fresh confirmation or a Q1-readiness result.

## Coordinator action

Arrange three adult raters who did not develop the method or inspect its automated results. Give each person only their own ZIP, without explaining the methods, hypotheses or detector outcomes. Applicable institutional decisions remain with the researcher; no recruitment or contact was performed by Codex.

- [Rater 1 ZIP](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/analysis/human-development-panel-20261013/rater1.zip>)
- [Rater 2 ZIP](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/analysis/human-development-panel-20261013/rater2.zip>)
- [Rater 3 ZIP](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/analysis/human-development-panel-20261013/rater3.zip>)

Each ZIP is approximately 84.5 MB (80.6 MiB). Send only the individual ZIP, not the containing directory, this coordinator note, protocol or private manifest.

Participant instructions to pass along: extract the entire ZIP, keep the assets folder beside `index.html`, and open `index.html` in a desktop browser. Read the instructions, work independently, take breaks as needed, and export the responses JSON before closing. Do not open the HTML directly inside the compressed ZIP. No Python, server, GPU or Internet connection is needed after extraction. Browser storage is a convenience; keep the exported JSON as a backup. Return that JSON through the human-arranged collection channel. No completion-time estimate has been measured.

Keep the three returned files unchanged in a new `human-responses` folder in the project and identify which packet each person used. Record the collection arrangement and prior familiarity without adding unnecessary personal identifiers. Missing ratings remain missing; do not replace them with machine judgments or remove disagreements. Apply the frozen analysis only after receiving the actual files.

## Verification and limits

The [independent review](human-panel-independent-review.md) passed with no material blockers. Structural checks confirmed the exact population, frozen order and sides, neutral public metadata, all 504 PNG byte copies, unchanged controls and all ZIP contents. Browser checks verified loaded images, equal zoom, navigation, and export/import with every answer blank. Screenshot capture timed out; no screenshot-based visual signoff is claimed. The empty QA export is explicitly named `QA-ONLY-empty-export-NOT-HUMAN-DATA.json` and must never enter human analysis.

Build and verification artifacts are under MAIN `.thesis-build/analysis/human-development-panel-20261013`. Private-manifest SHA-256: `409a6c45125f9c6f2e5d5f831bcf6f95b79093e377919843f01058e9b5197cad`. Keep that linkage private from raters. `packet-validation.json` records each archive hash; `ui-checks.json` records software checks and the visual-capture limitation.

The serial FreqMark attempt is closed without a numerical comparison or photographic result because deterministic CUDA resize backward was unsupported. Its record does not establish baseline failure or justify a larger GPU. The closest-baseline comparison, independent transfer, contribution novelty and supervisor alignment with the original proposal remain unresolved. Human assessment can resolve one validity gap; it cannot resolve those other gaps by itself. See the [article roadmap](plan.md).
