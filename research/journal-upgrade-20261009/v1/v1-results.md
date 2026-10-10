# D2-V1 cached Stage A results

Exploratory development evidence on twelve correlated sources. Targets are used only by this evaluator; operational h is a frozen clean-decoded target, not a known original embedded h.

Stage A fails; the fixed V1 rule closes immediately. This is not M1a/M1b, independent confirmation, or a substantially different design-family failure.

Inventory: 72/72 unique image identities; 108/108 unique calls. Missing images/calls 0/0; failed images/calls 0/0; duplicates 0. Strict inherited clean quality 12/12. Scalar/summary discrepancies: 0.

| Condition | checked semantic | exact checked q | D2 exact checked q | exact h | both match | lost D2 joint IDs | gained IDs |
|---|---:|---:|---:|---:|---:|---|---|
| clean | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 | [] | [] |
| sd15_vae | 12/12 | 12/12 | 12/12 | 0/12 | 0/12 | [] | [] |
| sdxl_vae | 12/12 | 8/12 | 10/12 | 0/12 | 0/12 | [25394, 468505] | [] |

Observed any-channel negative detections: 0/72 planned calls. Any-channel is recomputed as semantic found OR instance found and checked against watermark_found. No nominal FPR or independence claim is inferred.

The selected word is independently reconstructed from logged normalized-gap medians and ties. Full scalar score thresholds, content distances/statuses and both-match outcomes are recomputed; original carrier pixels/features are not rerun. See statistics.json for all changed IDs, per-view errors, target-only word diagnostics, inventory and discrepancy details.

- 6012 sdxl_vae: errors q0/qV/view1/view2 = [1, 2, 2, 2]; changed 1 bits; joint False -> False.
- 25394 sdxl_vae: errors q0/qV/view1/view2 = [0, 1, 1, 1]; changed 1 bits; joint True -> False.
- 134882 sdxl_vae: errors q0/qV/view1/view2 = [1, 1, 2, 1]; changed 2 bits; joint False -> False.
- 468505 sdxl_vae: errors q0/qV/view1/view2 = [0, 1, 1, 1]; changed 1 bits; joint True -> False.

Reported inclusive runtime 95.64000000001397 seconds; allocated CUDA peak 1382866944 bytes. Resource gate passes. Parent external wall timing is a separate receipt.

Run: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1405-v1-readout-screen`; run code `2498da4c266db7eff183d16a62ac3dfc6797088e`; D2 comparator: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1212-native-writer\rows.jsonl`. Analysis code commit `d0038c569949da0c8d672804c8ac625e11a4c0fd`; analysis source `C:\Users\Soroush\.codex\worktrees\journal-roadmap\THESIS_GUIDE_OFFLINE_v5\scripts\journal_multiview_analysis.py`.
