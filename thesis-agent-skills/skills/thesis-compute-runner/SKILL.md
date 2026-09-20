---
name: thesis-compute-runner
description: "Preview and execute approved version-controlled experiments locally or through a mock RunPod provider with exact-run provenance and recovery."
---

# thesis-compute-runner

Use only after experiment design and human review. Read [provider and approval contract](references/execution.md) before consequential execution. Run `dispatch_experiment.py dispatch ...` without `--execute` for a preview. No keys, GPU or cloud are needed for previews. `gpu --fixture` tests NVIDIA CSV parsing; `gpu` inspects actual hardware.

Actual local, mock-provider and remote execution require `--execute`, a matching non-expired human approval, the exact clean Git commit and the reviewed script hash. The approval binds experiment ID, run ID, target, entire manifest hash, decision, timestamp and cost/duration limits. Never author the approval on behalf of the human. An override that changes target is rejected; revise and reapprove the manifest.

Local scripts are executed as an argument array with a sanitized environment and bounded duration. They must consume the execution manifest and write declared outputs to the provided artifact directory. Review subprocess behavior of the script itself; this tool is not an OS sandbox. Do not run arbitrary generated shell text.

RunPod is isolated behind a provider interface. FakeProvider supports create/status/collection/stop/delete and failure injection. Live creation refuses before any request because current upstream stop/termination timers are broken. Never bypass that refusal with old flags or a direct API call. RUNPOD_API_KEY belongs only in the environment; never print it or save it in manifests.

Artifacts include manifest, summary, logs, metrics, checkpoints and outputs. Verify all declared output hashes before exact-ID deletion. On collection failure, stop only the recorded Pod after verifying exact ID and run name; persist recovery instructions and retain evidence. Similar names never authorize cleanup. Stopped storage may still incur charges. Failed and interrupted runs remain in the evidence history.

Authorization: dry-run is default. Expensive, destructive or external operations require explicit scope at execution time; global discovery stays enabled.

## Input/output contract

Inputs must match the strict JSON schemas in `scripts/_runtime/thesis_agents/schemas` after installation, or the bundle's `src/thesis_agents/schemas` during development. artifacts/<stage-id>/<run-id>/{manifest.json,summary.md,logs,metrics,checkpoints,outputs}; recovery.json on failed remote collection.

Use `python scripts/dispatch_experiment.py --help` for the actual argument contract. Errors return nonzero JSON diagnostics. Do not infer success from artifact filenames alone.
