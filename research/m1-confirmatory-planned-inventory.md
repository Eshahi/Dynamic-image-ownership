# Metadata-only full confirmatory planned inventory

Status 2026-10-04: candidate-independent preparation; candidate **UNRESOLVED**, source contract pending, scientific unlock/authorization false. No image, annotation, feature, model or scientific outcome was opened. This is not an official execution manifest, candidate freeze, source adoption or approval receipt.

`scripts/m1_confirmatory_inventory.py` takes only the two declared contained metadata JSON inputs. The CLI pins the exact frozen schedule bytes and records the external-index bytes, builder, draft/interface and structural dependency/selector code hashes. It refuses an existing output and outputs only a new contained research JSON. The pure `build_inventory(schedule, external_index)` function performs no path operations or I/O, and never follows external paths carried in acquisition metadata. Input error inventories survive as blockers without reducing planned rows.

The generated `m1-confirmatory-planned-inventory.json` has byte SHA256 `a43a95ac2db0774019a49182beb0171c44761017d55e120f8a85f902f5961657` (13,092,067 bytes), structural payload SHA256 `94f9f3cdf57d59e25e332bd70fd1d7748bf3b370ce3f8ced4bf79796c2ff7035`. The structural digest excludes `payload_sha256` and the command/receipt `provenance` envelope, permitting deterministic structural comparison of fresh metadata rebuilds. Exact schedule input SHA256 is `83c023bc3e0acb2a38142e8ef6e6a27f9216b7dacb5d885ab778b8799469f35d` and external-index input SHA256 is `8521b783324b62c9394081f0f7f0d8e5162b6592b9bf3256dddf0d400e28b88a`. Code/input hashes are preparation receipts, not a frozen scientific-core declaration.

## Fixed accounting

| Axis per method | Image units | Detector query rows | Operational cluster accounting |
| --- | ---: | ---: | --- |
| Clean | 900 (300 canonical C0-source, 300 matched C0, 300 C1) | 1200 (source correct, matched correct, C1 correct, C1 wrong) | 300 sources |
| T3 | 780 (30 sources x2 arms x13 channels) | 1170 (C0 correct only, C1 correct/wrong) | 30 source clusters; repeated severities/seeds/arms |
| T4 | 120 (30 pairs x2 sizes x2 donor arms) | 240 (donor/recipient claim roles) | 30 graph pairs, 60 distinct endpoints; reused groups remain dependent |
| T5 | No additional materialized image unit before selection | At most120; actual count null | At most30 disjoint selected pairs from44850 dependent metadata candidates |

The candidate and v5 inventories remain separate on the same cohort. Across both methods there are **3600 image units, 5220 query rows and 300 candidate initialization stage nodes =9120 materialized planned units**. A canonical source unit is repeated by method for explicit receipts/accounting, not another independent image. Candidate initialization/config/operator and v5 matched-adapter implementation remain unresolved until actual freeze; no step count or scientific candidate parameters were invented.

Every unit retains a unique condition ID, artifact namespace, source UID, final group, method, arm, claim owner, exact uint64 seed hex, dependencies, kind and planned reason. The identity/dependency field projection is checked with the existing `m1-worker-contract-v1` validator for the bounded DAG. Its synthetic-only validation mode is merely a structural check: the emitted inventory does not contain an executable fixture plan or scientific plan. Downstream adapters must verify the actual source byte receipts only after authorized unlock and journal missing/failed units rather than dropping them. Candidate initialization failure blocks that source's C0/C1 descendants; source/candidate failures propagate to relevant T3/T4 queries.

T3 starts independently from each saved untouched C0/C1, with one posterior-mode VAE channel plus4 strengths(.05/.1/.2/.4)x3 seeds(0/1/2),20 DDIM steps, CFG1, eta0, empty prompts and retained safety checking. Strength/seed is query metadata distinct from the embedding uint64 seed. T4 image dependencies are donor C1 or donor C0 sham plus recipient canonical C0-source; both claim roles remain separate even if their public roster OwnerIDs coincide. Neither row counts nor two methods multiply independent N.

## T5 deferred construction

All44850 unordered fixed300 pairs have metadata-only ledger IDs, ordered source indices and null `eligibility`/`selected`. No category, pHash, CLIP or annotation values appear. The frozen post-unlock selector remains identical nonempty noncrowd COCO category sets, distinct final groups, source pHash Hamming>=8, deterministic tagged pair ranking and at most30 disjoint pairs, with no replacements or lowered thresholds. The full universe is a prospective eligibility ledger, not44850 assessed negatives or independent observations.

The parent explicitly clarified the draft's unmarked endpoint prospectively as **canonical C0-source**: each C0-source and C1 endpoint is queried against the other endpoint's enrolled owner (four query slots per selected pair per method). This tests the original content and its marked counterpart; matched C0 reconstruction remains a separate clean negative. Pair selection is unchanged. Selected pair IDs, actual T5 query count and human verdicts stay null. Post-unlock worker construction must preserve requested30, selected/evaluated counts, eligibility failures and any shortfall.

The annotation receipt alternative now appears precisely in draft/interface: extracted `instances_val2017.json`, SHA256 `e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f`,19,987,840 bytes; COCO2017 release/source URL and annotation CC-BY-4.0 attribution retained. Archive SHA256/revision are null; page revision is not archive identity. Missing ZIP identity alone does not negate this exact extracted-artifact receipt. Adopting its source contract and reading bytes still require the real milestone decision/unlock.

## Reproduce and test

Use the stdlib interpreter and a fresh research output filename:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' scripts/m1_confirmatory_inventory.py --schedule research/m1-confirmatory-schedule-draft.json --external-index research/m1-confirmatory-external-index.json --output research/m1-confirmatory-planned-inventory-rebuilt.json
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -m unittest discover -s tests -p test_m1_confirmatory_inventory.py
```

Nine meaningful synthetic tests pass: image/query/stage totals, exact uint64s/index joins, locked flags, source/group duplicates/subsets/foreign schedules, dependency absence/cycles/duplicate IDs, T3 untouched-source/query asymmetry, same-owner T4 claim-role retention, complete deferred T5 ledger, retained receipt errors and deterministic builder execution under path read/stat/resolve traps. Only metadata builder execution occurred; no scientific run or rehearsal occurred. Statistical endpoint logic belongs to the separate endpoint helper; this builder supplies inventory and dependency provenance only.
