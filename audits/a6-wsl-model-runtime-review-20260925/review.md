# Independent A6 WSL model-runtime review (2026-09-25)

**Actor:** `/root/a6_wsl_model_review`, distinct from the receipt author `/root`. **Mode:** bounded, read-only review of `research/a6-wsl-bounded-model-runtime-20260925.md`, the two cited scripts, pinned asset metadata and A5 method constraints. The reviewer did not load a model, download an asset, run an experiment or alter files. The verdict applies only to the exact receipt and task transcript, not to A6/#7 or a Spec Kit gate.

## Verdict

No blocking error was found in reporting the two one-time offline WSL checks as **local compatibility observations**, assuming the raw exit codes, JSON and warnings shown in the authenticated task transcript. The reviewer independently confirmed by class-only import in the clean WSL venv (no model load) that `CLIPTextModel.config_class` is `CLIPConfig` / `clip`, while the pinned `text_encoder/config.json` is `clip_text_model`. The receipt correctly treats this as an unresolved text-conditioning risk, not proof of a failed or valid scientific method.

## A6 acceptance blockers and provenance limits

- Empty-prompt text conditioning has not been numerically checked against the declared method (`research/a6-wsl-bounded-model-runtime-20260925.md`, Results; `research/method-spec.md`, text-conditioning requirement).
- The LPIPS synthetic pair gives approximately `5.45e-8` on CPU and `5.95e-8` on CUDA, too close to zero for a strong relative-parity conclusion; the checker enforces finiteness, not a discriminating tolerance (`scripts/check_a6_metric_parity.py`, synthetic pair and score checks).
- Full image-conditioned DDIM reverse-suffix gradient and memory fit, and SD publisher/rights chain, remain unproven.
- Raw stdout/stderr and timeout records were not saved as a durable log; the receipt is a transcript-based summary with explicit process exit states, not a standalone execution trace.
- The **executed pre-repair version** of `scripts/check_a6_local_model_load.py` verified bytes against the supplied asset lock but did not pin the lock file's SHA-256 internally. The receipt records that exact script digest and Git state; this is a limitation of the historical run, not evidence that its lock was changed.

## Narrow post-run repair re-review

After the first review, the author added `_read_pinned_lock` to the SD helper to hash the raw lock bytes against the pre-existing A6 pinned digest before JSON parsing or asset verification, with model-free tests for the current 17-file lock and a modified lock. The repository suite then ran **98 tests, four expected skips**. The same independent reviewer re-read the exact diff and current lock digest without loading models or editing files and found **no blocker for this replay-integrity repair**. The original receipt's SHA-256 still exactly matches the executed pre-repair Git blob; the new guard improves only future invocations and is not retroactive evidence. Importing the shared digest from the LPIPS helper is a minor maintainability concern, not a validity blocker.

**Decision:** retain A6/#7 and the official Spec Kit technical gate open. No scientific approval, dataset acquisition or further model run follows from this review.
