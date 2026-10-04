# M1 scientific authority verifier

Date: 2026-10-04. Design review: gpt-6-astra, xhigh. Status: implemented, CPU verified; genuine M1 decisions remain pending. This document implements the authority portion of `research/m1-scientific-launch-contract.md`. It creates no user verdict, approval record, lifecycle transition or raw-data capability. The candidate and complete scientific launch remain conditional on the M1 evidence and independent review.

## Implemented boundary

`scripts/m1_scientific_authority.py` verifies a concrete join between the unchanged installed official `approval_check`, the official running-child envelope, the exact adopted packet, a host-recorded user message and consumed real Spec Kit decisions. Missing future records fail with `AuthorityDenied`; the production path contains no unconditional denial stub. The verifier neither opens source images/annotations nor resolves their locations. Source, index and schedule are exact hashes at this layer.

The authoritative evidence boundary is the existing trusted desktop host and its user-task history, plus the real controller's records. **This is host-recorded provenance, not cryptographic attestation of a human.** A hash or `actor=user` in an arbitrary JSON file is insufficient. Conversely, no local Python verifier can distinguish a malicious process with the same account's write access from the legitimate host if that process forges all host stores and controller records. The private Python object seal prevents accidental receipt substitution in the reviewed process; it is not isolation from arbitrary Python execution. The implementation does not prove physical keyboard input or exclude all authorized app automation. These are explicit trust limits, not claimed security properties.

The supported host format was inspected directly: `state_5.sqlite`, `thread_history_1.sqlite`, and the corresponding host-owned session rollout. No credentials are read. The policy freezes the desktop root task, creator-identity digest, working directory and metadata roots. Host-format changes or missing history fail closed; there is no fallback to actor text, an assistant message, a copied transcript or a standalone rollout.

## Public interface and broker integration

```python
scope = ExpectedScope(
    scientific_core_sha256=...,
    source_contract_sha256=...,
    external_index_sha256=...,
    schedule_sha256=...,
    attempt_plan_sha256=...,
)
policy = AuthorityPolicy(
    codex_home=...,
    trusted_thread_id=...,
    creator_identity_sha256=...,
    trusted_cwd=...,
    controller_project=...,
    controller_run_id=...,
    controller_workflow_sha256=...,
    decision_store_root=...,
    artifact_root=...,
    # official_runtime_root defaults to the inspected installed runtime.
)
authority = verify_authority(
    output_root / "execution-manifest.json", output_root,
    policy=policy, scope=scope,
)
require_verified_authority(
    authority, scope=scope,
    manifest_sha256=canonical_execution_digest, output_root=output_root,
)
```

All five scope values are lowercase SHA-256 strings. Paths are absolute fixed roots. `creator_identity_sha256` is the official canonical JSON object digest of the host's `creator_user_id` and `creator_account_id`; the launch configuration need not disclose either raw identifier. The inspected root task is `01a103e1-6cc9-7610-abb8-d0e5056fef0d`, and its identity digest is `38c43701a52586c58b762a91a3b2b41e2945ac8560960bdc7ba9bfd92d611fa7`. The controller project is MAIN and its run is `d916749c`. These observations are prospective policy inputs, not approval.

The reviewed launcher must obtain policy and scope from its frozen, hash-bound configuration. User-selectable command-line overrides for trust roots, thread, expected scope or evidence provider are unsupported. `verify_authority` constructs its own host evidence reader. Its only manifest path is the official `execution-manifest.json` in the exact `<artifact_root>/<stage_id>/<run_id>` output directory. It checks the adjacent running `manifest.json`, exact IDs/commit/manifest digest, clean-checkout flag, official executor identity, start time and approval reference.

The parent broker retains `VerifiedAuthority` in memory. `authority.to_dict()` is audit metadata only: it contains scope, manifest/packet/approval and consumed-decision hashes, source reference, expiry, run identity, aggregate limits and selected host/controller receipt hashes. It does not serialize the seal. Passing that dictionary, an uninitialized object or a fixture-mode object to `require_verified_authority` fails. Child IPC receives only the reviewed protocol's scoped verified bytes; it cannot reconstruct authority from a boolean, digest or receipt file.

The broker must still enforce exact input acquisition, owned child identity, aggregate time and recovery counters, cancellation, checkpoint lineage and immutable outputs. The authority module verifies the approved limits, not consumption of those limits. Rechecking the parent object checks expiry and scope, but does not monitor subsequent user messages or revocation; the launcher must obey actual user cancellation and its lifecycle checks.

## Fixed approval lookup and exact user evidence

The canonical manifest digest selects `<decision_store_root>/<digest>/approval.json`. Its structured `source_ref` selects `<decision_store_root>/packets/<packet_digest>/packet.json`. Neither lookup accepts an arbitrary filename from the worker. The reference format is:

```text
codex-user-v1:<thread UUID>/<turn UUID>/<item UUID>/<packet SHA-256>/<exact message SHA-256>
```

The future milestone UI/message can offer one explicit acknowledgment, `approve M1 <packet SHA-256>` or `تأیید M1 <packet SHA-256>`. The verifier accepts exactly either text after outer whitespace removal. The message digest nevertheless covers the original UTF-8 bytes, including any final newline. It does not infer authorization from “continue,” a quoted approval, old delegated development permission, or an ambiguous natural-language reply. This prospective mechanical acknowledgment is part of the single M1 decision, not an additional gate per experiment or failure.

The native reader performs these joins:

1. The fixed root-thread row must have the inspected desktop source, `thread_source=user`, `originator=Codex Desktop`, no agent path, paginated history, exact creator identity and working directory. The session metadata must agree.
2. The exact thread/turn/item must exist in the host history database as a `userMessage` with a desktop client ID. The reader uses the host's turn byte offset and item rollout ordinal to locate the completed `UserMessage` event in the allowed sessions directory.
3. Database and rollout must agree on thread, turn, item, client ID, text and millisecond timestamps. Exact original text must hash to the reference and acknowledge the referenced packet. Future-dated evidence fails.
4. Official approval actor must equal `codex-user:<host creator_user_id>`, and its issuance cannot predate that actual event. Both consumed controller decisions must use the same actor and source reference.

SQLite connections are read-only with `query_only=ON` and close explicitly. JSON metadata rejects duplicate keys and nonfinite values. Metadata paths reject raw components, traversal outside fixed roots, links, junctions and multiply linked files; ordinary file reads verify the opened handle and stable file identity. Bounded reads avoid unbounded history scans. These checks reduce accidental redirection under the stated trusted-host boundary; they are not a separate hostile-host security boundary.

## Adopted packet and the noncircular manifest set

Packet version is `m1-scientific-decision-packet-v1`. Canonical hashing uses the unchanged official JSON convention: sorted keys, compact separators, UTF-8, `ensure_ascii=False`, and no nonfinite numbers. The exact packet fields are:

| Field | Required value |
| --- | --- |
| `version` | Packet version above |
| `scope` | The five exact `ExpectedScope` fields |
| `controller` | Exact `run_id`, `workflow_id=thesis-lifecycle`, `workflow_sha256`, `adoption_step_id=plan-acceptance`, `compute_step_id=compute-approval` |
| `adoptions` | Ordered list: `narrow-coco512-scope-v1`, `exact-extracted-annotations-v1`, `public-owner-seed-v1`, `same-code-bounded-recovery-v1` |
| `execution_manifests` | Finite unique entries with `run_id`, canonical `sha256`, integer `max_seconds`, numeric `max_usd=0` |
| `limits` | Integer `max_seconds_per_attempt` in 1..3600, finite integer `max_seconds_total` at least the per-attempt limit, numeric `max_usd=0`, integer `exceptional_recovery_limit` in 0..2 |
| `expires_at` | Timezone-aware expiry no earlier than any effective approval expiry |

The selected execution must be present with its exact budget. All listed per-attempt budgets must fit the packet cap. Only local USD0 execution is supported. This module does not loosen the official approval's exact run, experiment, target, manifest, budget or time checks.

The packet is outside the execution manifest's input closure, so its list of final execution digests does not create a hash cycle. It is prepared only after the finite manifest set is finalized. The `attempt_plan_sha256` binds the separately reviewed logical dependency/recovery plan. Future checkpoint hashes remain output receipts selected and verified by the recovery resolver from approved logical predecessor attempts. They are not unknowable preapproval inputs. At most two exceptional recovery attempts package-wide can be admitted by the packet; their actual counter and allowed predecessor edges are launcher obligations.

## Real controller bridge and pending work

At inspection the real controller was paused at `plan-acceptance`; the older scope and evidence decisions were completed. Those historical development decisions do not adopt this M1 package. The installed workflow canonical digest is `772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51`.

The installed gate-decision schema contains run, step, verdict, state fingerprint, timestamps, actor and source reference. It has no dedicated source-contract adoption field or packet digest field. The existing official approval checker also treats actor/source-reference as strings; it does not resolve them to an authenticated user event. The minimal bridge therefore uses the existing `source_ref` to bind **both** the genuine future `plan-acceptance` and `compute-approval` decisions to the same exact user acknowledgment of the packet. That packet explicitly covers source, scope, seed/owner amendment and finite recovery. This preserves the existing workflow and previous decisions; it creates neither a new research gate nor a retroactive verdict.

After the genuine single user decision, the existing authenticated workflow-control procedure can materialize its exact gate decisions and per-manifest official approval records. Only the real controller consumes the gate decisions against its current state. This verifier does not perform that materialization or transition. Preparation here produced no such records. The concrete remaining integration is to present the finalized packet, capture the real acknowledgment's host IDs and exact bytes, and let the authorized workflow-control procedure reference those facts. If those genuine records are absent, production remains pending; their absence is not replaced by an agent-authored assertion of consent.

For each future consumed gate the verifier checks schema, exact actor/reference, digest-derived archive filename, successful controller state and input verdict, a unique completion log event within the gate decision's original validity interval, and the official pre-gate state fingerprint. It supports the inspected successful linear workflow. A changed workflow, retry branch or ambiguous duplicate archive fails and needs an explicit reviewed compatibility change. It does not require an already consumed historical gate decision to remain unexpired; the separate official compute approval and packet must still be current.

The pre-gate reconstruction was checked against the existing real `scope-acceptance` decision: both produced `541ce02d0acbc523100e564f44edef69dee586286078cea0214316cd4046ba96`. The inspected current plan pre-state fingerprint was `0a8f97039a3718114aa33f7623f51ac0fbe198c6a609a1d3b633cc413dfcb50b`. These metadata observations validate the join mechanics; neither is a new decision.

The module pins the inspected official runtime and approval/execution/gate schemas by byte hash before importing the unchanged checker. It also compares the run workflow snapshot with the installed workflow. Version changes fail closed rather than silently relaxing the trust contract. `OFFICIAL_PINS` is the exact implementation receipt; the runtime's `compute.py` hash is `4b98e5429d57bda48dbe7b239602b1c7ef60c7cbb19058e17136b29a09437d30`.

## Validation and limits of this evidence

The targeted test command is:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -m unittest discover -s tests -p 'test_m1_scientific_authority.py' -v
```

The generated fixtures exercise the unchanged official checker; complete positive algebra; rejection of dictionaries, uninitialized and fixture authority; wrong manifest/budget/expiry; actor-only records; assistant/subagent/other-identity messages; mismatched rollout; a correctly hashed “continue”; changed scope or packet; missing/old/stale/duplicate controller decisions; historical gate expiry; fixed lookup; numeric budget types; and read-only SQLite/rollout joins. Approval and gate fixtures remain in-memory dictionaries. No approval JSON or verdict file is written, even by tests. Positive fixtures are explicitly `generated-fixture` and cannot authorize the production broker. Temporary fake official envelopes and synthetic host stores contain no scientific data.

The initial 20-test run had two Windows cleanup errors in the fixture because the SQLite context manager commits but does not close. The fixture now uses `contextlib.closing`; production already closed connections explicitly. The repaired 20-test run passed. Two further boundary tests were then added (boolean USD0 rejection and an uninitialized receipt). Final targeted validation: **22 tests passed in 0.474 seconds**, exit 0.

A separate read-only native smoke joined the current real root task's existing `continue` item across its database and rollout. The exact IDs and identity matched; `_check_user_evidence` returned `no_human_approval`, as required. No production authority was issued. Genuine future M1 approval, live gate consumption and a scientific raw unlock have deliberately not been exercised; only the actual user decision can supply that evidence. CPU success establishes the verifier implementation and pending path, not completion of M1 or permission to access held-out content.
