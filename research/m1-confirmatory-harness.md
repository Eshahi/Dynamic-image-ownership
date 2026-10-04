# M1 synthetic lifecycle harness

Status: infrastructure implemented; scientific candidate **UNRESOLVED**. This is a reusable launcher/child-worker journal scaffold, not an adopted confirmatory protocol or a certified scientific launcher. It reads generated JSON fixtures only. It contains no image loader, annotation reader, model, detector, scientific threshold, approval writer or lifecycle-gate API. No held-out content was accessed and no official execution was performed.

## Inspected interface

The contract follows `research/m1-confirmatory-interface.md` and preserves the prospective scope in `research/m1-confirmatory-draft.md`. The installed runner's `execution.schema.json`, `compute.py` (`check_execution`, `dispatch`) and `common.py` (`object_digest`) were inspected. `scripts/rehearse_v4_saved_evaluation.py` is an existing stage inventory, not evidence that this new worker passes its stages.

`scripts/m1_confirmatory_harness.py` accepts the official worker interface:

```powershell
& $python scripts/m1_confirmatory_harness.py --manifest $syntheticManifest --output-dir $rehearsalOutput
# Only after an interrupted/timeout/failed attempt with an intact final receipt:
& $python scripts/m1_confirmatory_harness.py --manifest $syntheticManifest --output-dir $rehearsalOutput --recover
```

These commands are for generated fixture plans, never a scientific manifest. The default output directory must be contained in `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/rehearsal/`. Unit tests use an explicitly injected worktree rehearsal root. Temporary test directories are removed after their assertions.

The manifest uses the official schema fields exactly, with these narrower fixed values:

| Field | Harness requirement |
| --- | --- |
| `reviewed_script` | `scripts/m1_confirmatory_harness.py`, exact current byte SHA256 |
| `git_commit` | Exact checkout HEAD; an official execution would additionally enforce tracked code and a clean commit |
| `execution_target`, `cleanup_policy` | `local`, `stop-for-recovery` |
| `datasets` | `[{"id":"m1-synthetic-lifecycle","version":"1","license":"generated-fixture","split":"synthetic"}]` |
| `inputs` | Exactly one `{path, sha256}` receipt for a generated JSON plan under the checkout's `.thesis-build/rehearsal/` |
| `seeds` | Sorted distinct uint64 seeds from units, represented as Python integers |
| `metrics` | `["synthetic_units_completed"]` |
| `outputs` | `outputs/results.json`, `outputs/heartbeat.json`, `checkpoints/journal.json`, `outputs/harness-run.json` |
| `budget` | Integer `max_seconds` 1–3600; `max_usd=hourly_usd=0` |
| `resources` | `vram_mib=0`, positive RAM ≤1024 MiB and disk ≤100 MiB |

Identifiers and remaining required fields follow the installed schema. A fixture builder exists in `tests/test_m1_confirmatory_harness.py`; it derives current hashes and HEAD rather than supplying invented receipts. Manifest preparation creates no approval record. Canonical object hashes use the runner's UTF-8, sorted-key, compact JSON convention with `ensure_ascii=False` and `allow_nan=False`; file receipts hash actual bytes, including their line endings.

The plan is deliberately small:

```json
{
  "schema_version": "m1-harness-plan-v1",
  "mode": "synthetic-only",
  "candidate_status": "UNRESOLVED",
  "unit_timeout_seconds": 2,
  "units": [
    {"id": "fixture-0", "seed": 0, "delay_seconds": 0, "action": "complete"},
    {"id": "fixture-1", "seed": 1, "delay_seconds": 0.2, "action": "complete"}
  ]
}
```

There must be 1–1000 uniquely identified units. A unit's delay is bounded to 0–60 seconds; its action is `complete` or a prespecified `fail`. The internal subprocess writes a deterministic JSON token derived from unit ID and seed, never a scientific observation. A `fail` unit remains a failure under recovery; changing its plan would change provenance and require a new directory. Dataset, candidate-status and input-path checks reject scientific/test use before reading or hashing any proposed non-rehearsal input.

## Journal and recovery contract

One exclusive PID lock prevents concurrent writers. Each attempt gets a distinct `outputs/units/<id>-attempt<N>.json` and `logs/<id>-attempt<N>.log`. The complete journal is written atomically through a flushed/fsynced temporary file and replacement before starting a child and after completion. Each completed unit has an artifact SHA256; its contents, identity and exact seed are verified before reuse. Atomic file replacement is not a transaction across several files: a crash between updates can cause a receipt mismatch, which is preserved and refused.

`outputs/harness-run.json` records command, PID, duration, synthetic status, outcome and a fingerprint binding canonical manifest, canonical plan, exact worker bytes and commit. It also binds the final journal's byte hash and, on success, the result file's hash. A completed invocation validates every completed unit, the planned inventory, journal receipt and result receipt before returning idempotently. It does not rerun or overwrite a corrupted artifact. Failed/interrupted units retain their attempt rows and unique artifact/log paths; recovery adds another attempt and never duplicates completed units.

An empty initial directory is accepted. The exact official runner prelaunch envelope is also accepted: `execution-manifest.json`, root `manifest.json` and four `contract.json` files under logs/metrics/checkpoints/outputs. The worker validates matching identity, commit, running status, clean flag, manifest digest, exact snapshot and declared outputs; it never modifies these runner-owned files. Any other unjournaled file is refused. This proves interface compatibility only; accepting a fixture envelope is not an authorization mechanism.

SIGINT, SIGTERM, a worker exception or a cooperative timeout records `interrupted`, `failed` or `timeout`, preserves the journal and terminates/reaps the active child (terminate, then kill after two seconds). A bounded shard reserves up to three seconds inside its outer deadline; per-unit timeouts are ≤60 seconds. `--recover` is mandatory for a retained noncompleted attempt whose final receipt is intact. No best-result selection occurs.

Hard termination/host loss is deliberately fail closed: a stale lock, `started` journal entry, malformed/truncated journal or inconsistent final receipt is not automatically repaired, skipped or retried. Preserve the directory, establish process termination and prepare a separately reviewed recovery receipt/new attempt directory. The scaffold does not yet automate that receipt. The installed official runner uses `subprocess.run(timeout=...)` without proven process-tree containment; these CPU tests do not certify Windows Job Object/host-loss containment. A forcibly killed launcher could leave the bounded fixture child alive temporarily. This limitation must be resolved for a scientific/model worker before execution readiness.

## Verification performed and rehearsal still required

The stdlib suite runs through real small child subprocesses:

```powershell
& 'C:/Users/Soroush/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -m unittest discover -s tests -p test_m1_confirmatory_harness.py -v
```

Eleven tests passed: completion and verified idempotence; interruption with retained partial attempts and explicit recovery; unit timeout; deliberate child failure; corruption refusal; truncated journal preservation; changed-plan/stale-lock refusal; forbidden test input rejected before read/hash; scientific dataset/frozen-candidate refusal; official-envelope acceptance; and bad-envelope/unexplained-file refusal. Separately, a generated fixture passed the installed runner's read-only `check_execution` and `dispatch(..., execute=False)` schema/hash/budget preview; its canonical digest matched `object_digest` and no output directory was created. This is CPU infrastructure evidence, with result `scientific_verdict=NOT_EVIDENCE`, not M1 method evidence. Current source is not yet committed by this author; parent handles the commit.

Before a frozen candidate can be presented as executable-ready, use its identical launcher/worker/journal/guard/heartbeat at one clean commit to pass the project's synthetic generated-image rehearsal stages: real, scale, kill, term, finalterm, timeout-early, timeout-unit and hostloss. Add full/degenerate checks where the frozen metrics require them. The present JSON tests cover meaningful lifecycle primitives but do not claim those full stages passed, generated-image parity, GPU cleanup, storage pressure or process-tree cleanup. No official execution, approval validation, gate mutation or scientific execution is part of this preparation.

## What must be filled when the method freezes

1. A reviewed scientific adapter and source/config/runtime hash bundle: exact CLIP/DCT/OwnerID derivation or documented amendment, embedding, three detector states, lightweight/native side information, paired C0/C1/wrong-owner behavior, v5 comparator and feasible latent baseline. Replace the synthetic-only rejection only through an explicit reviewed adapter contract; do not reinterpret fixture tokens as scores.
2. An adopted statistical/scope protocol: fixed development-derived thresholds without test fitting, the prospective COCO512 restriction and deterministic group schedule, 300 clean groups, distinct 30-source T3 schedule, 30-recipient T4 graph and bounded T5 annotation pairing after authorization. Keep missing meaningful pairs and missing human quality verdicts explicit. The draft does not alter protected source/acceptance plans.
3. Metadata-bound source paths and existing receipts, checked against bytes only after scientific unlock; annotation access only after approval. Test content must remain inaccessible during template preparation. Successful source groups, attack seeds and owner calls remain separate accounting units.
4. Measured development runtime/RAM/VRAM/disk, pinned science interpreter/model licenses/dependencies, real shard limits ≤about one hour, worker progress and external process-tree guard. Extend the output contract to inventory every required scientific artifact or bundle/hash it in a declared inventory.
5. Complete development evidence and independent M1 package review, all same-commit synthetic rehearsals, strict manifest preview and the user's exact confirmatory approval through the official runner. Official retries use fresh directories and the approved recovery policy; this standalone `--recover` flag does not bypass that policy.

Recommendation: this delivers a reusable, tested **interface scaffold**. M1 can be template-ready while candidate science remains unresolved; it is not executable-ready until the items above and the approval/rehearsal prerequisites are satisfied.
