# Independent A4 documentary closure review

Date: 2026-09-23. Issue: [#5](https://github.com/Eshahi/Dynamic-image-ownership/issues/5). Author: `/root`. Independent, read-only reviewer: `/root/a4_closure_audit`. The reviewer made no file, GitHub, or controller changes and did not run a scientific experiment. The author transcribed the reviewer's report into this record; this is not presented as a reviewer-authored file.

| Reviewed artifact | SHA-256 |
| --- | --- |
| `research/acceptance.md` | `9f29020aa923f39fa48c8738b069d6db790aab33a16ad69b6eecb0fb18d1de5e` |
| `research/sample-size.md` | `8941fc017462d379fa5bf987c99acd4f96e9ab1dd96a28a8cb8c501b7c8eb5b9` |
| `research/stop-rules.md` | `9a4aea670d88d77d468a9a82df043ec0ab4a5b44c3cba98539608a82dafe2860` |
| `scripts/a4_protocol_reference.py` | `9b66795b2a80371e80c1c57b19712864bf0df3b0a03b1cf89408c02f48952197` |
| `scripts/test_a4_protocol_reference.py` | `8e8d42ae5de548d53d81ba6ab62e83a3822c7313bd94599b792c67bbc8090cb6` |

## Finding and disposition

The reviewer first found one blocking mismatch: the registry combined two pairs of fields and had eight columns, while the immutable A4 output schema in `thesis-runs/d916749c/guide-plan-38.json` requires ten. The author split `metric_definition` from `criterion` and `direction` from `practical_margin`; the reviewer then inspected the **new exact bytes** and found no remaining documentary blocker. All 42 original claim IDs occur exactly once and all rows have ten nonempty fields. The 12-cell primary objective, draft 80% TPR/1% FPR bounds, strict per-image quality targets, 6,900 planned-source allocation, independent-unit accounting, and negative-versus-technical stop distinction remain coherent. The reviewer ran `python -m unittest discover -s scripts -p 'test_*.py'` (33 passing tests) and `git diff --check` (clean). The author separately reproduced the 33-test pass using the verified Windows project interpreter.

Recommendation: issue #5 may be closed as a **DOCUMENT** deliverable after these exact artifacts are integrated. This does not assert a frozen executable protocol, dataset/rights/split readiness, GPU/model compatibility, comparator or remaining attack implementation, resource measurement, scientific efficacy, compute authorization, or Spec Kit `plan-acceptance`. The scalar T1 reference's double-versus-float32 parity must still be resolved and tested before production attack execution; no production-parity claim follows from the documentary review. Any change to a hashed artifact requires a fresh review for this exact closure record.
