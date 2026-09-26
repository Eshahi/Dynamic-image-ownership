# Post-run002 resource route: no cloud launch

Observed failure and limits are in reports/dev/c4-embedding-dev-002/result.md.
Both local attempts failed within their separately authorized8GiB Torch profile.
Idle residency reduced live allocations, but iteration0 decoding with a retained
gradient path still failed. Exact physical-GPU minimum and backward demand are
unknown; neither an assertion that12GiB is impossible nor a guaranteed24GiB cure
is supported. No run/source/dtype/cap substitution or retry is authorized.

Safe independent next work is inspecting graph liveness and method-preserving
gradient checkpointing with owned numerical tests. This is prospective software
work; changed compute must be packaged/reviewed/approved separately. A larger-GPU
candidate can be prepared in parallel, not rented or enabled by implication.

## Official-source refresh, inspected 2026-09-26

- [Runpod billing overview](https://docs.runpod.io/accounts-billing/billing)
  describes real-time resource charging, at least one hour of configuration
  credit before Pod deployment, an hourly account spend limit, and continuing
  network-volume charges while Pods are stopped. These are not an exact20-minute
  per-run execution deadline or a guarantee of zero residual storage cost.
- [Official runpodctl PR330](https://github.com/runpod/runpodctl/pull/330) records
  removal of stop-after/terminate-after flags after backend timer enforcement
  problems. It is historical evidence supporting the pinned runner's refusal,
  not proof that every contemporary Runpod product is intrinsically unsafe.
- [Official Pod management documentation](https://docs.runpod.io/pods/manage-pods)
  is public workflow guidance, not an independently verified termination-bound
  receipt for this project. No API call, paid Pod or backend enforcement test was
  performed, so no new provider clearance is inferred from documentation alone.

The installed thesis-compute-runner still rejects live creation and transfers.
Do not bypass its refusal using old flags, direct API or a user-created billable
Pod used as an inferred workaround. A supported future route must establish an
actual bounded deadline, exact intent/Pod identity/reconciliation, reviewed worker
image/environment and asset transport/custody, immutable hashes, budget and
collection/recovery/stop behavior. Existing model mirror rights/source custody
limitations and local-only image handling remain constraints on remote transfer.

User may prepare their own account access, but **no billable deployment or paid
budget is requested yet**. No password/token/session cookie in chat. Determine a
concrete supported manifest, current GPU quote plus storage and setup costs,
duration/ceiling, required remote asset permissions and exact approval before
asking for a Pod. Public research does not grant paid or external data-transfer
authority. Do not claim this route is executable simply because an account exists.
