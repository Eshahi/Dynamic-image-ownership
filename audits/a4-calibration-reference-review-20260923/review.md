# Independent A4 reference-code review

Date: 2026-09-23. GitHub issue #5. Author: `/root`; independent read-only reviewer: `/root/a4_code_review`. This report is the author's transcription of the reviewer's findings, not a claim that the reviewer edited it. The reviewer made no file, GitHub or controller changes and gave no gate or human verdict.

| Final reviewed artifact | SHA-256 |
| --- | --- |
| `scripts/a4_protocol_reference.py` | `8EB7C85094CC6C84A9AADC7C6823148A4E783560A1C976731F68FA875D101D57` |
| `scripts/test_a4_protocol_reference.py` | `6EC8994B5B766867550FE26531E832D9E96904CE83B372470BBF620DB0D0FC7F` |
| `research/acceptance.md` | `8551642DA845933FFA2BC59A35BB39D0B9B25720853CA7EF656D1D06C54F82A1` |

The initial read-only review found a **blocking** malformed-score path: a vetoed semantic score skipped validation of an invalid instance score, making a malformed C2 row appear to be a clean negative. The author changed `_eligible_pairs` to validate every non-`None` component before applying the semantic veto, and added NaN/text/huge-integer regression cases. The focused re-review reproduced that malformed rows now raise `ValueError`; explicitly classifying the failed C2 output as `None` then applies the adverse negative-cell rule. The reviewer found no remaining blocker within this reference-code scope.

The reference matches the written 101×101 grid, common-q strict match, integer negative-cell eligibility, macro-TPR/tie order and owner/seed parity vector on synthetic inputs. Nine A4 synthetic tests and the full 27-test repository suite passed with the explicit Windows interpreter; Python compile checks passed. These are ordinary arithmetic/guard tests only: precomputed score rows are supplied by a caller, and the caller still must establish source eligibility, data/split provenance, correct invalid-output classification, A5 detector parity, runtime fitness and complete scientific manifest. No model, dataset, baseline or scientific run was used. A4 and `plan-acceptance` remain open.
