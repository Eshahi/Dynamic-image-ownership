**Verdict: BLOCK.** There are four blockers: infrastructure faults are recorded as permanent adverse results, the scientific core leaves out code the run executes, the held-out guard depends on a label the plan sets for itself, and the rehearsal tier is not met. The cohort, the query graph and the endpoint arithmetic are correct, and every fix below is small.

Independent review by Claude, who did not write this code, 2026-10-06. Scope: `87af2b8..22e9223` on `claude/m1b-package`. HEAD moved from 6bc4c20 to 22e9223 while I was reviewing, and `research/m1b-package.md` had uncommitted changes when I read it. I ran `python -m unittest tests.test_m1b_coco512_worker` in a6-science-venv: 18/18 OK in 28 s. I opened no held-out image or annotation; the cohort checks used `research/` metadata only.

## Findings

1. **Blocker: infrastructure faults become permanent adverse rows (Q1, Q3).**
   - **Evidence.** `Worker._unit` catches every `Exception` and journals it as `failed` (`scripts/m1b_coco512_worker.py:510-514`). `_image_of` then turns every descendant into `missing_dependency` (520-524, 541, 556, 571). The run still "finishes" with `complete: true` and exit 0 (912), and a resume never re-runs a journaled row (501-502).
   - **Effect.** Any of these would turn the rest of the held-out run into adverse rows within seconds: loss of the CUDA context, a driver reset (TDR), an OOM in LPIPS after a successful embed (547), a full disk in `_save` (482), or an unmounted `W:` drive (375). Nothing could legitimately recover it, because rerun condition 3 needs an incomplete run.
   - **Fix.** (a) After approval and before the first unit, add a preflight that stats and hashes every `raw_path`, hashes the annotation artifact, and checks free disk and CUDA; if it fails, abort without writing a journal row. (b) Classify exceptions. Scientific failures (`OperationFailure`, a safety verdict, a detector or geometry `ValueError`, a canonical hash mismatch) stay journaled as adverse. `torch.cuda` errors, `OSError`, `MemoryError`, and any failure after N (for example 3) consecutive failures should fail-stop with no row, which leaves a resumable journal. (c) Unit-test both paths with the fake runtime.

2. **Blocker: the scientific core leaves out code the run executes (Q3).**
   - **Evidence.** `CODE_FILES` (`worker:50-54`) is the only code bound by `run-context.json`, the resume check (877-881), `core_hash` (`scripts/m1b_prepare_package.py:35-38`) and rerun check 2 (`prepare:100-101`). The worker's actual import closure also loads:
     - `revised_watermark_v4`, the base detector (`_check_image`, `_perceptual_hash`, `_decide`, `_content_status`, used at `f5_latent_codec.py:226-311`);
     - `a6_clip_visual` (CLIP loader, `worker:345`), `m1_latent_reconstruction` (PSNR/SSIM, 420), and `m1_blind_noise`/`m1_blind_noise_core` (VAE output quantization, `m1_confirmatory_image_operations.py:125`);
     - `check_a6_lpips_assets`, `verify_science_assets`, and the asset lock `research/a6-candidate-model-assets.json` (`worker:351`).
   - **Effect.** A rerun commit could change the decision table or a metric and still pass both "same scientific core" and "changed paths are harness". This contradicts the policy's definition of the core ("detector and metric code, input and parent hashes", `research/approval-policy.md:62`).
   - **Fix.** Derive `CODE_FILES` as the transitive `scripts/` import closure and assert it in a unit test. Add the asset lock, external index and schedule hashes to the core. Recompute the core hash before showing it to the user.

3. **Blocker: the held-out guard depends on a self-declared label (Q3).**
   - **Evidence.** The worker asks for approval only when `data_split == "test"` (`worker:868-869`). For any other split, `validate_plan` accepts the frozen test index, `data/raw` paths and the `coco-instances` selector (190-196). I confirmed this: the test plan with `data_split: development` and no `approval_path` validates, with 300 sources under `.../data/raw` and T5 drawn from `instances_val2017.json`.
   - **Effect.** Development runs are delegated and do not go through the official runner (`approval-policy.md:91`). One mislabelled copy of the plan would open held-out images and annotations with no approval.
   - **Fix.** In `validate_plan`, refuse any non-test plan that uses a source UID, group ID or `raw_sha256` from `research/m1-confirmatory-external-index.json`, any path under the `data/raw` root, or the pinned annotation hash. For test plans, require the index sha256 to equal the frozen value. Add tests.

4. **Blocker: the rehearsal tier is not satisfied (Q4).**
   - **The rule.** A package "may be presented to the user only after every rehearsal stage has passed at the same clean commit", using the identical launcher and generated synthetic images (`approval-policy.md:60`).
   - **The evidence falls short.** It spans three earlier commits (smoke at ba75609, stop at 354c42f, resume at 346143d), not the final one. It ran on development images, not synthetic ones. Each run was started directly or with an emulated `safe_env()`, never through `dispatch --execute`. The dispatcher preview at 22e9223 only checks hashes.
   - **The stated reason does not hold.** §4.5 says `--execute` "cannot be rehearsed without a human approval". The rehearsal tier needs no user approval, so a synthetic manifest can carry a manifest-bound approval record whose actor is a labelled delegated rehearsal; `approval_check` checks the scope and the hash, not who the actor is.
   - **Why it matters.** The held-out run would be the first real dispatcher execution, and this path has already failed once (the stop rehearsal crashed with the `pwd` error, fixed at 354c42f). What is missing is listed under Q4 below.

5. **Should-fix: resume reuses evidence that the rerun allowance says must not be reused (Q2, Q3).**
   - **The conflict.** Package §4.4 calls a `resume_from` continuation an infrastructure-only rerun. Policy condition 3 requires the previous evidence to be "preserved and not reused" (`approval-policy.md:68`), but the worker copies and reuses the previous journal and images (`worker:877-883`).
   - **`rerun-check` is too weak.** It does not test for reuse (`prepare:104`). Check 1 compares only the science digest and check 2 only intersects `CODE_FILES` (98-101); in the rehearsal output, the held-out plan file itself was counted as a "harness" change (`.thesis-build/rehearsal/m1b-rerun-check.json`). It does not check the approval expiry or the two-rerun limit.
   - **Provenance gaps.** The inherited journal is trusted as it is; the only check is the image hashes stored in that same journal (488-493). §6 fixes `approval_path` to the user's own file but does not say where a delegated rerun approval goes.
   - **Fix.** Add "up to 2 continuations that reuse the journal of the interrupted approved run" to the approval question explicitly. Require that `resume_from` contains the dispatcher's `manifest.json`, with an `approval_reference` equal to the original approval digest. Record the inherited journal's sha256 and line count in `run.json`. Give each rerun approval its own path and never overwrite the user's. Make `rerun-check` compare `core_hash` and the full code closure.

6. **Should-fix: partial held-out endpoints are written at a checkpoint (Q3).**
   - **Evidence.** On `Stop`, `main` still writes the full `run.json` and `metrics/endpoints.json` (`worker:898-907`).
   - **Effect.** After a 7.5 h stop, partial outcomes would be visible before anyone decides whether to continue. That is an optional-stopping risk.
   - **Fix.** When `status == "checkpointed"`, write only the inventory, and compute endpoints only for `finished`.

7. **Should-fix: analysis can crash after the run, and fixing it changes the core (Q1).**
   - **Evidence.** `_finite` turns NaN into `None` (91-95). `analyse` then evaluates `q["ssim_rgb"] > 0.9`, `q["lpips"] < 0.1` and `max(...)` on `None` (722-728), which raises, so `run.json` is never written. Any fix to `analyse` changes the worker hash, and so the core. Separately, `joint` passes `psnr_db is None` even when `psnr_infinite` is false (725).
   - **Fix.** Move `analyse` into a separately hashed pure module that can be re-run on the retained journal. Make every predicate None-safe, so that None fails the target, and test with None/NaN rows. If analysis fails, still write `run.json` with an `analysis_error` field.

8. **Should-fix: the same-owner pair is counted in two T4 negative cells (Q1).**
   - **Evidence.** In pair 5 the donor and recipient owners are equal (I checked). `recipient_claim_any_found_rows` and `donor_semantic_consistent_rows` use `all_k` (`worker:759-761`).
   - **Effect.** The donor's own mark, found under the identical recipient claim, counts as a false detection. This contradicts the 2026-10-04 clarification (`research/m1-confirmatory-draft.md:88`).
   - **Fix.** Restrict both cells to `diff` and report the same-owner pair separately, as `false_donor_attribution` already does (756-757).

9. **Should-fix: deviations from the draft that §4 does not declare (Q2).**
   - (a) T5 collision descriptors are not recorded for selected pairs (draft:53): CLIP cosine, semantic code distance and instance/pHash code distance. The two code distances can be partly derived from the C0 rows, but CLIP cosine cannot. `Runtime.clip_vector` (381) is never called.
   - (b) There are no T3 per-seed cells, only pools per strength (draft:39 asks to "report each severity/seed").
   - (c) The draft's ≤3600 s shards, 3500 s cooperative deadline and external guard (draft:80) are replaced by a single 8 h dispatcher run with a cooperative stop at 27,000 s.
   - (d) There are no VRAM or disk receipts (draft:37) and no T4 seam measures (draft:45).
   - (e) The T5 "annotation-valid" count is merged with canonical validity (`worker:636-642`).
   - **Fix.** Implement (a), (b) and (e); all three are computed after selection and do not affect it. Declare (c) and (d) in §4 with a rationale.

10. **Should-fix: the primary clean negative rule is not named (Q2, Q3).** §3 reports clean false attribution under both `both_match` and `any_found` (`worker:715-717`) without saying which one carries the ≤1% conjunction, and choosing after seeing results would be a forking path. **Fix:** name the primary rule, and mark the other as secondary, before approval.

11. **Should-fix: a direct invocation is not bound to the approved manifest (Q3).**
    - **Evidence.** The worker checks only the plan hash (847-850) and that `CODE_FILES` are committed (870-872). It does not check `HEAD == manifest.git_commit`, its own sha against `script_sha256`, the other manifest inputs, or that the whole tree is clean. A plan key `official_runtime` (835) can redirect which `approval_check` gets imported, and it sits outside the science digest (I checked).
    - **Fix.** For test plans, enforce all four bindings inside the worker. Hard-code the runtime path and pin the sha256 of `compute.py`.

12. **Should-fix: durability on a laptop.**
    - **Evidence.** Journal appends are flushed but never fsynced (304-306), PNGs are not fsynced (482), and the torn-line repair rewrites the journal non-atomically (286-288).
    - **Effect.** A power loss can leave a journaled row whose PNG is empty. `_load` then crashes on resume, and the only way forward would be to edit the journal.
    - **Fix.** For each unit, fsync the PNG and then the journal, and make the repair an atomic rewrite.

13. **Notes.**
    - `started_utc` is taken at the end of the run (903).
    - The module docstring says C0-reconstruction identity is "checked by hash" (21-23), but no such check exists. Remove the claim or add a development test.
    - `meets_numerical_target` is also emitted for the descriptive T3/T4/T5 cells (`m1_confirmatory_endpoints.py:52-53`). Mark it as not applicable there.
    - `safety_blocked` is assigned by matching a substring (513), so "Required pipeline safety components missing" would be mislabelled.
    - The paired sign test uses only the `semantic` rule (792), while most of v5's .2 successes in the smoke were recomputed-only. Add the `semantic_checked` table.
    - §6 step 3 says `python`. Give the absolute a6-science-venv interpreter path instead, because the dispatcher reuses `sys.executable` (`compute.py:141`).

## Verified as correct
- **Cohort.** The plan's T3/T4 lists equal the schedule draft and my own recomputation of the `m1-coco512-t3-v1`/`t4-v1` hash ranks over the 300 index UIDs. The clean order equals the `confirm-v1` rank. T4 uses 60 distinct UIDs in 60 distinct groups. Owners are recomputed per UID (`worker:150-153`), and the annotation sha256 equals the one in the draft.
- **Query graph, per method.** Clean 4 x 300; T3 39 x 30 = 1170; T4 8 x 30 = 240; T5 8 per pair. Claims and owners are right on every branch (552-559, 581-591, 596-623, 650-663). T3/T4 inputs are reloaded from the saved untouched PNGs with a hash check, and the shared C0 attacks and shams treat both methods the same way.
- **Endpoints.** Denominators are planned units. Missing positives count as misses and missing negatives as errors (`m1_confirmatory_endpoints.py:46-49`, `worker:701-702`). Majority means at least 2 of 3 seeds. The sign-test arithmetic is correct, and the F5 embed and detect arguments match `configs/f5-r2.json`.
- **Data access.** For a correctly labelled test plan, nothing reads annotations or raw images before `check_approval` (`worker:860-869`). T5 selection sees only categories, group IDs and source pHash.

## Q4: Is the evidence enough to present the package? No.
**What the current evidence leaves untested.** The unit tests use a fake runtime, and the real-model smoke used four 512 PNGs that were already canonicalized. No run has exercised the `coco-instances` path, JPEG/EXIF/ICC/grayscale canonicalization at scale, the test-split approval branch end to end, or the dispatcher's `--execute`.

**The missing rehearsal.** All runs below are at the final clean commit, under `.thesis-build/rehearsal/`, on synthetic data only.
1. **A synthetic test-shaped package.** Use 300 generated JPEGs (mixed sizes, EXIF orientations, an ICC profile, grayscale and CMYK cases), a synthetic index, a synthetic COCO-format annotation file, and `data_split: test`. Launch it with `dispatch_experiment.py dispatch --execute`, the a6 interpreter and a rehearsal approval. The worker must refuse without the approval, then complete with about 7,700 planned rows and the 44,850-pair ledger, recording the timing.
2. **Fault injection through the real runtime.** Inject a missing raw file, a wrong annotation hash, and a forced CUDA error or `OSError` mid-run. Expect a fail-stop with a resumable journal, not adverse rows (finding 1).
3. **Kills and resumes.** Kill the run once by dispatcher timeout (budget set below the cooperative stop) and once in the middle of a unit. After each, resume through a new manifest, `rerun-check`, and a delegated rerun approval stored at its own path.
4. **Re-analysis.** Run the separated analysis module on a retained full-size journal and confirm it reproduces the in-run endpoints.
