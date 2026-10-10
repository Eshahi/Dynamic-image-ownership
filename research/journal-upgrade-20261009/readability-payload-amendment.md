# Payload-definition correction before the readability screen

2026-10-10. Codex design agent. This amends the payload origin and baseline interpretation in [readability-amendment.md](readability-amendment.md). The separate [readability-compute-amendment.md](readability-compute-amendment.md) remains applicable. No refined candidate result was inspected for this decision. No GPU computation, code change, original embedding replay, threshold change or official gate transition was performed by this author.

## Decision

For each of the same twelve sources, fix **q_target to the original intended semantic code recorded by the frozen F5 embedding report**. Fix **h_target to the native instance code decoded from the saved clean F5 C1 under the frozen combined detector and owner alpha**, requiring that the instance and semantic read flags are true. Store this extraction and its origin explicitly. Hold both targets constant across every configuration, objective branch and final fragile restoration.

The two targets have different provenance. q_target is the known intended original semantic payload. h_target is an operational instance target obtained from the retained image; it is **not a recovered or verified original embedded h**. The amendment subsequently writes this declared q_target/h_target pair, so its exact delivery can be tested prospectively. Do not call this exact retention of the original two-tier payload. Appropriate wording is “repair and channel protection of intended semantic q, with preservation of the declared clean-decoded instance target.”

This is the stronger and identifiable semantic experiment. Replacing q_target with a clean decoder error would reward reproduction of that error and would no longer test recovery of the known intended message. Using the original q is possible without a replay because `embed_rgb` records it. By contrast, `scripts/f5_latent_codec.py:embed_rgb` recomputes h immediately before each fragile write and does not record that h in its embedding report. Saved-image h_now, a previously decoded h, and the original pre-write h are not interchangeable evidence. Do not reconstruct an alleged original h by rerunning the writer or by selecting a value that improves subsequent results.

The frozen clean marks are therefore a control, not a demonstrated feasible point for the stricter exact-payload clean criterion. **Clean exact q on 12/12 and SD1.5 joint exact q on 12/12 remain prospective repair targets.** Their previous description as retention of already satisfied constraints was incorrect and is superseded here. All four configurations, their order, step counts, budgets, objective constants, final restoration, quality constraints, negative controls, transformation conditions, global selector and continuation tests remain unchanged. In particular, the SDXL joint exact-q target remains at least 11/12 despite the lower corrected baseline.

## Retained evidence and corrected baseline

MAIN means `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`. The failed diagnostic is retained at MAIN `.thesis-build/dev-runs/20261010-0943-readability-diagnostic`, commit `5c93b54bb85b1602c35b75a6818078adc2cb0b78`. Its run record reports twelve rows, zero optimization seconds and failures for 6012 and 134882 at the original-q equality assertion. This is an input-assumption failure, not a measured failure of R1–R4. Successful partial diagnostics do not justify reducing the source denominator to ten.

This author independently joined the twelve original `embed-{id}` semantic codes in MAIN `.thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7/rows.jsonl` to every F5 C1 row in MAIN `.thesis-build/dev-runs/20261010-0903-journal-vae/rows.jsonl`, by source ID. The table below uses retained native owner-alpha calls; it performs no new image inference.

| Frozen F5 condition | Native checked semantic acceptance: read and content_match | Exact intended q and read | Joint: exact intended q, read and content_match |
|---|---:|---:|---:|
| Clean | 12/12 | 10/12 | 10/12 |
| SD1.5 VAE | 12/12 | 11/12 | 11/12 |
| SDXL VAE | 10/12 | 3/12 | 3/12 |

All twelve clean calls have both native read flags and `both_match`. This does not imply bit-exact recovery. Clean source 6012 intends `ba84b4b8` but decodes `aa84b4b8`; 134882 intends `b2c0b53c` but decodes `b3c0b53c`. Each differs by one bit. The same 6012 mismatch accounts for the SD1.5 exact deficit. Only 25394, 147498 and 499768 satisfy the SDXL joint exact endpoint. Historical SDXL checked acceptance 10/12 remains correct for its own endpoint; it is not an exact-q baseline.

Freeze this complete payload table before the corrected diagnostic. h values are taken from the retained discovery's clean native combined calls, with both read flags true. Fresh clean extraction must confirm the operational targets; a disagreement requires a reported reproducibility diagnosis rather than silently replacing the table.

| Source ID | q_target: recorded intended q | Frozen clean decoded q | h_target: operational clean decoded h |
|---:|---|---|---|
| 1675 | 2aa4173c | 2aa4173c | 8ba0e08b |
| 4795 | aa440fb8 | aa440fb8 | ea8ed24f |
| 6012 | ba84b4b8 | aa84b4b8 | a003e39f |
| 25394 | cbc5a678 | cbc5a678 | 86cb5f8a |
| 80932 | 2aeda634 | 2aeda634 | e1f646ea |
| 109798 | f1c4b464 | f1c4b464 | a60af130 |
| 134882 | b2c0b53c | b3c0b53c | a4f15337 |
| 147498 | dbc49634 | dbc49634 | fc782e31 |
| 177015 | aa4d2938 | aa4d2938 | e636c60e |
| 190676 | 32c6a524 | 32c6a524 | c09047e1 |
| 468505 | 0beda430 | 0beda430 | f5671a81 |
| 499768 | bad2bc3c | bad2bc3c | 252e7b79 |

## Frozen detector semantics and instance coupling

Keep `detect_rgb` unchanged. It recomputes q_now and h_now from the suspect, decodes the semantic tier, and checks content using the existing soft rule. It chooses the instance-table conditioning code q_bound as decoded semantic q only when the found semantic code has a content mismatch; otherwise it uses q_now. Therefore h extraction is conditional on the native q_bound, and q_bound need not equal either the decoded semantic q or our fixed q_target in every suspect image.

The operational h_target above is a value decoded under that frozen clean native procedure. Restoring the instance pattern using q_target/h_target does not guarantee that the native reader will later use the same conditioning code. Recomputed semantic features or the status switch can cause an instance-read failure even if a forced-q diagnostic would decode h. Such a failure counts against the declared clean criterion. Do not force q_target into the detector, substitute original source features, alter the conditional branch, disable binding for primary evaluation, or accept a forced-q read as native delivery. Any auxiliary forced-code analysis must be clearly separate and cannot rescue a failed row.

For the corrected run, preserve the full native fields needed to identify this distinction: q_now (`semantic_code`), h_now (`perceptual_hash`), decoded q/h, read/found/content flags, semantic content status and the inferred native q_bound with its rule. q_target and h_target are evaluation/embedding side information only. The detector must still consume only its existing suspect-image inputs and declared public side information.

## Required correction and diagnostic rerun

1. Change payload initialization so a unique original embedding record supplies q_target. A clean decoded-q mismatch is recorded with its Hamming distance and does not abort. Continue requiring a unique source record, expected dimensions and both clean native read flags. Obtain h_target from the frozen operational extraction, with explicit `h_origin` and `original_h_known=false`; retain original intended q, clean decoded q/h and extraction in the run record.
2. Commit the implementation and this amendment before running. Start a **new** diagnostic output directory and retain the failed run and its rows unchanged. Do not append repaired rows to the failed run as if its protocol had been unchanged.
3. Rerun the prescribed finite-difference diagnostic on **all twelve** sources and all three conditions, reusing the same saved discovery C0/C1 pixels. Recompute fixed-q patterns, correct-versus-alternative gaps and scores against q_target, including both previously aborted sources. Preserve signed host and displacement terms and native exact/read/checked results. Do not reuse a successful partial result as evidence that a mismatched target was tested.
4. Produce the complete baseline table above from the joined records in the corrected diagnostic output. Also record per-source Hamming errors, native h-target equality and clean joint q/h exactness. Clean native joint q/h exactness is 10/12 under these targets because h_target is defined by the clean extraction and both read flags are true. Confirm that native checked counts and strict clean quality remain the existing retained measurements, without turning them into exact-recovery claims. Reusing existing quality measurements is sufficient for this unchanged-pixel diagnostic.
5. If fresh extraction and the retained table agree and the all-source diagnostic completes, execute the already declared R1–R4 screen. Use q_target for every semantic objective and fixed-q endpoint and q_target/h_target for the single final fragile write. Do not tune a fifth configuration, remove either difficult source, replace a failed refined image with the frozen mark or change an acceptance threshold in response to this correction.

The final clean criterion remains all twelve with PSNR >35 dB, SSIM >.9, LPIPS <.1, both native read flags, exact q_target and h_target, and native `both_match`. The VAE screen remains zero negative detections, SD1.5 joint exact-q 12/12 and SDXL joint exact-q at least 11/12. Report gains relative to the correctly labelled baseline 10/11/3, alongside historical checked baseline 12/12/10. The selector and all subsequent matched T3, T4/T5 and delivered-binding checks remain as declared. Whenever a later donor-delivery experiment uses a different payload origin, state that origin and do not silently relabel its historical decoded-donor baseline as original-intended delivery.

## Scientific status

This correction reveals a genuine limitation of the frozen writer: readable, content-matching output can contain semantic bit errors. It invalidates the earlier assertion that frozen clean marks already meet the new exact-payload criterion. It does not retroactively invalidate historical M1a or M2, whose native tolerant endpoints did not require exact original q, and it does not establish failure of an unexecuted refinement family. No official gate is changed. If R1–R4 subsequently fail the stricter declared screen, retain those failures and report their measured ceiling under the existing kill route; do not use this correction as a post-result exemption.
