# Unified saved-image development assessment

This prospectively fixed assessor applies the retained v5 threats to family A's saved RGB8 outputs. It does not fit detector thresholds, choose eligible images, or make a human visual judgment. Pilot outputs with two available IDs still have the full twelve-image denominator. The operator explicitly freezes either `pure-decoder` or `hybrid-source-bypass`; their results must remain separate. Enrollment must actually use `qim-pilot-owner-alpha`; an existing mark under another OwnerID cannot be relabelled.

## Freeze and execute

After the enrollment run stops, prepare a new manifest inside `research/` using metadata-only hashing:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' scripts/m1_assess_dual_threats.py --prepare --input-dir '<retained enrollment directory>' --route pure-decoder --manifest research/m1-dual-threat-pure-pilot.json
```

Commit the assessor, its dependency files, and the prepared manifest before execution. The template is explanatory and is intentionally not executable. Preparation verifies reserved raw source hashes, source/C0/C1 artifact hashes, owner, route and the frozen semantic-label hash; it copies the exact enrollment detector profile without changing it. The source run.json, raw-byte implementation hashes, and Git committed blobs are locked. Execution validates all these before model loading; changing an enrollment run.json requires a new assessment manifest/run. No hidden held-out paths are enrolled.

Repeat `--input-dir` in declared chronological order to aggregate disjoint family-A enrollment shards, for example one initialized from the first reconstruction run and another from its recovery run. Every run.json receipt and hash is retained in that order. Any duplicate enrolled ID is rejected, including incomplete IDs; no implicit best-result or replacement selection occurs. The selected route, actual owner and exact profile must match. All committed script and asset-lock receipts must match across shards; commits may differ solely because different shard manifests were committed. Each source commit is retained. Initialization receipts remain in the hashed enrollment records; aggregation does not erase their different reconstruction provenance.

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe' scripts/m1_assess_dual_threats.py --manifest research/m1-dual-threat-pure-pilot.json --output-dir 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/<timestamp>-dual-pure-threats'
```

`--resume` accepts the same output directory only with the same commit and manifest. Completed rows are reused only if their output PNG hash still matches. Attack images persisted before interruption are evaluated without rerunning the attack. Failed rows are retried on explicit resume; every earlier failed attempt stays in the append-only journal. A missing/deleted/changed completed artifact is regenerated, with a unique new filename preserving earlier files. No exact continuation of an interrupted image operation is claimed.

## Fixed inventory: 489 conditions

| Axis | Planned conditions | Protocol |
|---|---:|---|
| Clean | 24 | Twelve reserved development IDs, C0 matched to the selected route and C1 |
| T3 | 312 | All twelve, both controls, deterministic VAE posterior-mode round trip plus four strengths × three seeds |
| T4 | 80 | Original ten IDs, offsets 1 and 5 (20 directed pairs); donor residual scales .5/1, public projection, C0 unmarked projection sham |
| T5 | 66 | All unordered twelve-ID pairs, frozen agent labels: seven same, two uncertain, 57 different |
| T5 transfer | 7 | One directed public projection per frozen same-topic pair |

T3 extends the retained v5 schedule from its original ten T3 sources to all twelve reserved IDs. No C2 strong-profile or supplementary ordinary-operation arm is included. T4 pairing, residual arithmetic and public projection are reused unchanged from `three_threat_protocol` and `v5_study_protocol`. Residual transfer uses saved C1 minus saved matched C0, applied to the recipient's matched C0. Public projection transports actual donor C1 projections; the sham transports actual donor C0 projections. Both remain public, zero-query constructions. In the pure route C0 is a decoded generation counterfactual, so C1-versus-C0 quality alone does not establish source-photo imperceptibility. Source-PNG comparison is separately retained.

T3 uses pinned local SD1.5 img2img, explicitly configured DDIM, 20 requested inference steps, empty positive/negative prompts, CFG1, eta0, strengths .05/.1/.2/.4 and seeds0/1/2. A fresh CUDA generator with the same seed is used independently for paired C0/C1 attacks. VAE mode uses the same pipeline VAE, deterministic unscaled posterior mode and direct decoder output. Every generated image must pass the pipeline's pinned safety checker; blocked or failed images remain failed planned conditions. There is no residual composition in an attack. Model networking is blocked and assets are checked against the existing seventeen-file manifest. GPU allocations are capped at 10 GiB per process. CPU transfer operations finish before the diffusion model is loaded; all attack PNGs are saved before the CPU-only CLIP/LPIPS/detection loop.

## Detection and quality

Each of the 423 image conditions gets the unchanged `m1_dual_latent.blind_detect` verifier for alpha and the three wrong owners beta/gamma/delta: 1,692 planned calls. CLIP is recomputed on each saved suspect on CPU. Its vector is cached only across that suspect's four OwnerID calls; no source features, source key, original image or inversion enters verification. The helper preserves all v5 six detector outcomes and proposal states, with its qualified operational mapping (including abstention). Four independent calls use the helper's unchanged default per-call roster size 1; there is no family-wide or population false-positive bound from these descriptive wrong-owner counts. Detection times exclude CLIP extraction; the stage architecture intentionally makes evaluator cost distinct from attack generation.

For clean C1 retain both matched-C0 paired-family quality and original source-photo quality. PSNR strictly above35 dB, RGB SSIM strictly above.9, and LPIPS strictly below.1 form the existing quality conjunction; infinity for identical images is explicit. Attack rows additionally retain same-arm preattack and source comparisons. Numerical CLIP cosine ≥.85 is an exploratory semantic-retention proxy only, not a preregistered success condition or human verdict. Human judgments remain null. T5 records C0/C1 semantic and instance Hamming distances and CLIP cosine, plus the frozen agent label; clean C1 also records component drift from its own matched C0. No label or threshold is revised from outcomes.

## Retention and interpretation

run.json records commit, command, frozen manifest hash, configuration/profile, seeds, development split, environment/assets, duration, outcome and journal hashes. `rows.jsonl` preserves every status update; `conditions.json` is the latest complete planned inventory for aggregation. Each condition can be planned, missing_enrollment, attack_persisted, failed or completed. Terminal status is incomplete whenever any planned condition is missing/failed/uncompleted. A provenance/load failure leaves the planned inventory and failure receipt. Quality does not gate inclusion in attacks or detection. A two-ID pilot cannot supply the missing T4 pairs or the full T5 denominator and cannot be reported as a twelve-ID study. Semantic labels describe agent topic judgments and do not certify real-world identity. Detector states do not identify causal history or cryptographic ownership.

## Reproducible descriptive aggregation

`scripts/m1_analyze_dual_threats.py --assessment-dir ASSESSMENT --output-dir FRESH_MAIN_DEV_RUNS` reads metadata only. It hashes run.json, conditions.json, both journals and the assessment manifest, retaining source statuses and parse/provenance errors. Source records without the development assessment receipt are refused before conditions are read. `conditions.csv` contains all 489 planned rows; `summary.csv` groups clean controls, T3 dose/strength across all seeds, T4 arm/scale and T5 labels; `missing-or-failed.csv` includes missing conditions and incomplete detector/quality receipts. Duplicate/unplanned condition IDs are errors, never a mechanism to choose an outcome.

Counts include all observed detector outcomes/qualified states for the correct and three wrong owners, semantic/instance found and content-match counts, runtime distributions, clean paired/source quality conjunctions, and T3 semantic-match with same-arm quality. The semantic-match AND CLIP≥.85 joint count is separately labelled exploratory. T5 component-distance ranges/means remain grouped by frozen agent label. Summaries report planned, completed-source and complete-record denominators separately; missing calls/metrics cannot make analysis complete. All thresholds remain fixed; no human verdict, population false-positive rate or causal-state validation is inferred. Analysis manifest and run.json retain commit, command, configuration, development split, duration, outcome and input/output hashes.
