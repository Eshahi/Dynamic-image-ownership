# Execution and approval boundary

`dispatch_experiment.py dispatch MANIFEST --repo REPO --artifacts ARTIFACT_ROOT`
is a dry run. Add `--execute --approval APPROVAL` only after explicit human review.
All wrappers accept their helper's full subcommand syntax; for example
`check_local_gpu.py gpu --fixture FILE` and `validate_approval.py validate-approval MANIFEST APPROVAL`.

The approval schema is distributed in the shared runtime. A human or authenticated
controller records the explicit decision; the runner has no approval-creation command.
Approve the complete canonical JSON manifest SHA-256, exact experiment/run/target,
maximum seconds and USD, issued time, expiry, actor and source message reference.
Approval artifacts must be stored outside an agent-writable directory where practical.
Hashes and actor strings do not authenticate a malicious author; filesystem permissions
and Hermes access controls are the trust boundary. No casual 'looks good' interpretation.

Reviewed Python scripts receive exactly `--manifest FILE --output-dir DIRECTORY`.
The clean repository commit and script checksum must match. No arbitrary command/args/env
fields are accepted. The local child receives a minimal environment without API tokens.
The caller should keep artifacts outside the repository to preserve a clean checkout.
Scripts remain capable code and must be reviewed; use OS isolation for untrusted code.

## RunPod limitation verified during build

RunPod CLI commit `4351fca9ec454b1bdc8572aaad5d3e5a61ead0fa` has no deadline flags.
[PR 330](https://github.com/runpod/runpodctl/pull/330) explains why they were removed:
the backend accepted timers but did not enforce them. Old clients are not a workaround.
Accordingly, live creation and live artifact transfer are deliberately unavailable.
The mock provider implements the full lifecycle and recovery contract, and the REST
adapter implements status/stop/delete for a future reviewed integration. No live cleanup
command is exposed casually. `exact_cleanup` requires persisted exact Pod ID AND run name.

A future provider must establish a genuine bounded deadline before spending, persist
create intent before its API call, reconcile ambiguous creation without creating duplicates,
verify an immutable worker image, transport declared inputs/outputs, obtain actual GPU
and environment provenance, verify hashes, and retain a recovery path. Do not enable it
solely because a newer CLI again advertises flags: verify backend enforcement separately.
