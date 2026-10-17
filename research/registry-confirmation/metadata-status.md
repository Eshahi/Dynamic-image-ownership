# Held-out metadata package, 2026-10-17

Complete metadata reservation. No held-out image/EXR/raw bytes were opened, downloaded, decoded, canonicalized or scored. Raw paths were checked by existence only. This is not a scientific unlock or an approval.

DIV2K: all 300 admitted test sources, 300 groups, all primary representatives, all recorded raw paths present. Recorded raw SHA-256 joins agree between the split and source receipt. Exact UID/raw-hash/group comparisons show zero overlap with 3,000 admitted development/calibration rows and zero scientific-use/reservation matches in 702 metadata inventories from MAIN, journal and the admission worktree, including both earlier COCO confirmation plans and retained run/config/receipt metadata. Full inspected-file pins and classifications are in `div2k-exposure.json`. Exclusion lists and admission/transport inventories contain the test hashes by design; these are explicitly distinguished from scientific exposure. This cannot certify undocumented human or external exposure, and historical admission/canonicalization is already disclosed.

Tears of Steel: the next 20 eligible shots strictly after round3's final shot `04_5n`, preserving upstream listing order, are reserved, using earliest frame plus 72/144/288 (60 pairs, 80 unique frame URLs). The selected shots start at `05_1a` and end at `08_3a`. All 32 subsequent numbered shot listings were inspected: six unavailable (HTTP 404), three short/empty, and 23 eligible. **Only three replacement shots remain in this listing: `08_4a`, `08_4c`, `09_1a`, in that order.** Exhausting these during approved duplicate preflight must stop the run, without changing the rule. Listings, including unavailable responses, are retained for offline replay. All new frame hashes remain null until the approved preflight. Same-film scene dependence remains a limitation.

The prior development footage digest index contains 160 pair-frame receipts, 120 distinct frame URLs and 118 distinct RGB8 hashes. Its two acquisition inventories are pinned. Round3 retained the `04_5b` overlap with prior `02_3d`; it was not replaced. The new preflight must exclude any shot containing a canonical duplicate against all these recorded development frames, replacing whole shots in reserve order and journaling the replacement. It must also preserve the broader development source exclusions in the package.

Inputs: admission worktree `data/splits.csv` SHA-256 `60ff11ae5a81698446573c5f7fbd9d3067a5a2619abdf29ac2389931de1e1b9f`; `data/b4-admission-20260926/source-manifest.csv` SHA-256 `40bfeca7c589b8352f93535070bc74fca70c6458216ea5422f0dc173f57110c4`. Prior shot-selection JSON and both original selection scripts are pinned in the shot index; HTTP root/listing identities are retained there and in the listing cache. Frame provenance is original Xiph Tears of Steel live-action footage, CC BY 3.0, attribution `(CC) Blender Foundation | mango.blender.org`, with inherited rights limitations.

All paths below are relative to `C:/Users/Soroush/.codex/worktrees/journal-roadmap/THESIS_GUIDE_OFFLINE_v5/`:

| Deliverable | SHA-256 |
|---|---|
| `scripts/registry_confirmation_metadata.py` | `da6a3617b9a4ae0315d27feb2c348383793fbeb70341fbb09132efee235fb340` |
| `research/registry-confirmation/div2k-heldout-index.json` | `4bae6786295bd79f1a6ff5544e2c7e331cfc5d8b97ccc9a2c3b01fe6d65c2695` |
| `research/registry-confirmation/div2k-exposure.json` | `5036fc0a1f6af4e36111045e379f2250a91751de58520b3943f7af58ddcdee9c` |
| `research/registry-confirmation/tears-of-steel-shots-index.json` | `7a12e93e764827d7d5b474d48b2ce64bfff024f5d59bbb3d822b3a60f3b9668c` |
| `research/registry-confirmation/tears-of-steel-shots-listings.json` | `3edb7ee33673e4c95ea2dafbba0d9bc7e17516c683f6664617d50ed08aedbc15` |
| `research/registry-confirmation/development-frame-exposure-index.json` | `1d4b2d7ec5264e4a0f7dc879124be117ec6240cfcf2f9f836890958ae1124122` |

Reproduce: run MAIN's `.thesis-build/venv/Scripts/python.exe scripts/registry_confirmation_metadata.py` in the journal worktree. Default uses cached directory metadata; `--refresh-listings` explicitly refreshes HTML only. Offline replay with network access replaced by a raising stub passed, reproducing every index byte-identically. Checks confirmed 300 unique test UIDs/groups, 20 shots with four frames/three pairs each, and three reserve shots. No commit or shared state edit was made. A future metadata rebuild may change the exposure-inventory pin if other agents add or amend historical metadata.
