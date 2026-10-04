# Prospective descriptive A-C / v5 comparison

`scripts/m1_compare_terminal_v5.py` is a CPU-only, Python-standard-library receipt reader. It never imports inference code, decodes images, reads held-out data, or alters retained artifacts. Execute after the independent terminal threat analyzer completes without integrity errors. `scientific_complete=false` is allowed: adverse and missing conditions retain their denominators. This is exploratory evidence only.

The retained v5 image-domain comparator is pinned to `C4-v5-two-tier-development/c4-v5-two-tier-dev-001/outputs/results.json`, SHA-256 `58766c579377f344770887e6cad8bf4ed779ee207c2b6872b4a24ac4a90b9b4d` (617 rows). The script requires an externally supplied candidate-analysis `run.json` hash, validates the exact output hash inventory, and checks manifest, partition-run and source-run JSON receipt hashes. It checks candidate source RGB8 hashes against the baseline clean-C0 pixel hashes; disagreements reject pairing, unavailable source receipts are explicitly reported. Hashes refer to retained receipt metadata; this tool does not independently decode source pixels.

Prospectively selected C1 owner-alpha observations:

| Group | Source clusters | Planned rows |
|---|---:|---:|
| Clean, EXPANDED_IDS | 12 | 12 |
| VAE posterior-mode, ORIGINAL_IDS | 10 | 10 |
| Diffusion strength 0.1, seeds 0/1/2 | 10 | 30 |
| Diffusion strength 0.2, seeds 0/1/2 | 10 | 30 |
| Diffusion strength 0.4, seeds 0/1/2 | 10 | 30 |

Total: 112 rows per method, joined by exact source/control/dose/strength/seed condition ID. Dose comes from the frozen manifest schedule because verified analyzer rows omit it. Strength 0.05 and the two additional T3 sources are excluded from the common subset before looking at new outcomes. C0 all-owner and C1 wrong-owner observations on these same selected conditions provide 784 descriptive negative slots per method, with missing slots retained. These slots and seeds are dependent; no independent-sample FPR estimate is made.

A-C's semantic/instance indicators are continuous blind scores >=4. The script independently checks their threshold/state parity. v5's semantic/instance indicators are `content_match` after discrete decoding/correction. v5 `found` and `watermark_found` are separate fields, reported separately. Its four-owner recomputed threshold is 5.243804105290349 and decoded threshold is 8.423231196698145, checked in each observed selected detection. Its one-owner embedding verification is not substituted for the retained four-owner suspect detections.

Each group preserves planned, observed, missing/adverse and outcome counts, per-method both counts and the paired descriptive 2x2 both table. Raw retained quality values accompany per-condition results; human visual ratings remain missing. Pairing establishes source and dose correspondence, not identical marked/attacked image bytes or equal statistical operating points. No superiority, inferential significance, confirmatory claim or adaptive security conclusion follows. T4/T5 transfer operators and delivery criteria differ and are excluded from pooling.

Detector side information: A-C observes suspect RGB8, public OwnerID, pinned CLIP/VAE models and public profile/maps; v5 observes suspect RGB8, the suspect CLIP feature, public OwnerID and the image-domain profile/codec. No source feature or source-template oracle contributes to the compared owner-alpha decisions.

Run from the worktree after committing the implementation; substitute the independently generated analysis directory and its measured receipt hash:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe' scripts/m1_compare_terminal_v5.py --analysis 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/ANALYSIS/run.json' --analysis-sha256 ANALYSIS_SHA256 --output-dir 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/NEW-COMPARISON'
```

Outputs are fresh `comparison.json` and `run.json`; an existing output directory is refused. The run receipt records commit, command, configuration, seeds, duration and script hash. Record the run in the development log. Tests use fabricated fixtures to exercise distinct decision semantics, threshold boundaries, missing/adverse denominators, source/schedule mismatch, duplicate detection IDs and receipt/output-hash rejection. No GPU or external data is needed.

A read-only JSON compatibility smoke check against the pinned baseline found owner-alpha observed counts 12/12 clean, 10/10 VAE, 29/30 strength 0.1, 28/30 strength 0.2 and 28/30 strength 0.4. Baseline negative slots were 733/784 observed. These counts are baseline inventory checks only; no A-C outcome comparison has yet been executed. Their missing observations must remain visible in the final descriptive tables.
