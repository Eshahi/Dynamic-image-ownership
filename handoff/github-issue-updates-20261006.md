# GitHub issue updates proposed on 2026-10-06 (Claude Code, Opus 5.5)

Repository: Eshahi/Dynamic-image-ownership. Evidence links are pinned to commit e26bd4b (branch `claude/m1b-package`, pushed 2026-10-06) unless stated otherwise.

B = `https://github.com/Eshahi/Dynamic-image-ownership/blob/e26bd4b`

The tracker was last updated on 2026-09-27. Since then:
- the method was amended: v4, then v5, then the M1 families, then F5;
- F5 r2 passed the M1a regeneration gate;
- the M1b package was built and rehearsed;
- the single approved confirmatory run started on 2026-10-06.

The issue templates name output paths from the original plan. Where the substance is met at different paths, the comment maps it and closes the issue as completed. Where the work is still ahead, the issue stays open with a status note.

## Close as completed

**#18 [C4] Embedding module.**
> Status 2026-10-06: done in substance; closing. The embedding module is F5 r2, the encoder-amplified latent carrier:
> - code: `scripts/f5_latent_codec.py` (`embed_rgb`), frozen as `configs/f5-r2.json`;
> - spec: `research/f5-r2-spec.md`;
> - design and results: `research/f5-encoder-amplified-latent.md`;
> - tests: `tests/test_f5_latent_codec.py` (weight-key independence, null symmetry, projection cache, soft-angle recovery).
>
> Shapes, ranges, clipping and quality (PSNR/SSIM/LPIPS) are logged in every gate and stress run.
>
> **Deviations, recorded:**
> - The outputs live at these paths, not `src/embedding/proposed.py`.
> - GPU embedding is not bit-reproducible: normalized-gradient PGD through the fp32 VAE encoder. This is documented in `research/m1b-package.md` §4.7; the confirmatory result is a single recorded realization.
> - The earlier latent-refinement route (draft PR #67) was superseded by the method amendments before M1a.
>
> Links: B/scripts/f5_latent_codec.py, B/research/f5-r2-spec.md, B/research/f5-encoder-amplified-latent.md

**#19 [C5] Detector and validation-only calibration.**
> Status 2026-10-06: done; closing.
> - **Detector:** `f5_latent_codec.detect_rgb`, with the v5 r3 comparator `scripts/revised_watermark_v5.py`.
> - **Thresholds are analytic, with no data-driven calibration:** a Bentkus-Dzindzalieta bound at a false-positive target of 1e-6 gives the inclusive recomputed threshold 4.982 and the decoded threshold 8.259 (radii 6/10). No test or held-out data influenced them.
> - **Controls:** clean, C0 and wrong-owner controls are recorded in every development run and are planned endpoints of the confirmatory run (`research/m1b-package.md` §3).
>
> Links: B/scripts/f5_latent_codec.py, B/research/m1b-package.md

**#20 [C6] Key stability and collision study.**
> Status 2026-10-06: development study done; closing. The confirmatory collision endpoint is tracked in #29.
> - **Semantic key stability** under regeneration: stress grids (.4/.5/.6 x 5 seeds, two sampler families) with the failure split into carrier loss and binding drift. See `research/stress-baseline-20261005.md` and `research/f5-r3-256-result.md` (branch `claude/f5-r3-256`).
> - **Collisions:** T5 among the 12 development covers gave 0/66 joint near collisions (`scripts/f4_t5.py` on F5 r2). Inter-image CLIP-angle distribution: `research/ideas/binding-ceiling.md` (branch `claude/f5-ideas`).
> - **Owner separation:** wrong-owner detections were 0 in every run.

**#21 [C7] Classical DCT positive control.**
> Status 2026-10-06: done; closing. The classical DCT control is the v5 r3 two-tier image-domain DCT codec (`scripts/revised_watermark_v5.py`, `research/method-amendment-v5.md`).
> - It was measured on the development sources (C4 v5 study dev-001) and used as the comparator at the M1a gate.
> - It is carried as the paired comparator into the confirmatory run, on the same sources and attacks with its own frozen profile.
> - Draft PR #68 (bounded pixel-DCT comparator) is superseded by this.

**#23 [C9] Latent-to-DCT bridge test.**
> Status 2026-10-06: done; closing.
> - **Accepted bridge:** F5 writes a keyed DCT-band pattern in the SD1.5 VAE latent, by PGD through the encoder, and reads it back from the suspect's own latent.
> - **Criteria:** it was accepted under the pre-declared M1a regeneration gate. Paired C1 semantic success at .1/.2/.4: 29/28/23 vs v5's 27/18/2, with zero C0 and wrong-owner detections.
> - **Rejected bridges** are recorded with their gate numbers: the A-C dual-latent family, phase residual, initial-noise and other M1 families, and F4 (chroma). See `research/m1a-regeneration-gate-ac-20261004.md` and `research/f5-encoder-amplified-latent.md`.

**#24 [C10] Integrated tests, end-to-end smoke and technical gate.**
> Status 2026-10-06: done; closing.
> - **Technical gate:** M1a passed by F5 r2 (above).
> - **End-to-end smoke** with real models on development sources: 339/339 rows (`research/m1b-package.md` §5).
> - **Rehearsal tier through the official dispatcher on synthetic, test-shaped data** (§8):
>   - refusal without approval;
>   - injected CUDA fault, giving an infrastructure stop;
>   - timeout kill;
>   - full run of 926 rows, whose re-analysis is identical;
>   - two continuations with lineage.
> - **Tests:** 32 worker tests plus the codec, endpoint and schedule suites pass (`tests/test_m1b_coco512_worker.py`).

**#25 [D1] Method freeze and evaluation preregistration.**
> Status 2026-10-06: done; closing.
> - **Method frozen:** `configs/f5-r2.json` and `research/f5-r2-spec.md`.
> - **Evaluation preregistered:** `research/m1-confirmatory-draft.md` and `research/m1b-package.md`. They fix the datasets (narrow COCO512: 300 MS-COCO test representatives), conditions, endpoints, adverse missing-row counting, seeds, cohort tags and stopping.
> - **Executable plan:** `research/m1b-coco512-test.m1b-plan.json`, with execution manifest 95ac3183… and scientific core be2aa571… at commit 711d2f3. These were committed before any held-out result existed.
> - **Labelled deviation:** continuation-1 (e26bd4b) moves the interrupted run to a rented GPU with the same scientific core.

## Close as not planned

**#27 [D3] Benign attack grid.**
> Closing as not planned. On 2026-10-05 the user limited the thesis to three threats: T3 regeneration, T4 copy-paste and T5 semantic collision (`AGENTS.md` "Threat scope", `research/threat-model.md`). Benign transforms (JPEG, crops, grayscale and so on) are out of scope and are noted only as a limitation.

## Keep open, with a status comment

**#26 [D2], #28 [D4], #29 [D5]** (the same comment on each):
> Status 2026-10-06: in progress. The single approved confirmatory run (F5 r2 vs v5 r3, narrow COCO512, 300 sources) started on 2026-10-06 at 22:17 UTC. It covers:
> - clean quality and runtime (D2);
> - T3 regeneration with SD1.5 DDIM img2img .05/.1/.2/.4 x 3 seeds plus a VAE cycle, on 30 sources (D4);
> - T4 copy-paste (30 pairs) and T5 semantic collision (up to 30 pairs) with wrong-owner and C0 negatives (D5).
>
> It is being continued on a rented GPU as infrastructure-only continuation 1 (same scientific core). Results will be linked here after the run, in M2.

**#22 [C8] Reference latent-watermark reproduction.**
> Status 2026-10-06: not done. The thesis now watermarks existing photographs. Generation-time latent watermarks (Tree-Ring, Gaussian Shading, PRC and others) do not apply to existing photos without inversion, and the comparator became v5 r3 (#21). I suggest closing as not planned; this needs the owner's decision.

**#30 [D9] Preregistered ablation.**
> Status 2026-10-06: open. Development ablations of F5 were run and kept as negative results, each with a selection rule committed first:
> - H1 band and matched filter;
> - H3 texture mask, killed at equal T3 (masking is anti-robust to regeneration);
> - H4 threshold relaxation;
> - r3-256, a 256-bit semantic sketch, killed (`research/f5-r3-256-result.md`).
>
> There is no confirmatory ablation in the frozen protocol.

**#31 [D6], #32 [D7], #33 [D8]:**
> Status 2026-10-06: these are M2 items, after the confirmatory run. The frozen protocol computes:
> - per-cell exact Clopper-Pearson and Wilson intervals at the independent unit (source or pair; repeats clustered);
> - adverse counting of missing rows;
> - a paired exact sign test for F5 vs v5 at T3.
>
> A bootstrap and Holm correction are not part of the frozen protocol. Whether to add them as labelled secondary analyses is decided in M2.

**No change:** #13 (B6; draft PR #59 is still relevant), #34-#38 (writing, E1-E5).

## Draft PRs

Proposed: close #67 (C4 latent refinement), #68 (C7 pixel-DCT comparator) and #69 (C6 pair ledger) as superseded by the method amendments. Keep #59 (thesis outline).
