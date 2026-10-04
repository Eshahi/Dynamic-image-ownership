# M1 confirmatory interface preparation

Status 2026-10-03: **interface/template ready; candidate package not executable-ready**. This document records inspected runner code, schemas, preregistration and reservation metadata. It creates no manifest, approval, gate decision or human verdict. No held-out image bytes, image previews, embeddings, perceptual features or method scores were read. Historical private canonical/feature bridge files were not opened; their recorded hashes were read only from metadata. No scientific run or rehearsal was launched.

## Exact interfaces inspected

Working checkout: `C:/Users/Soroush/.codex/worktrees/v5-study/THESIS_GUIDE_OFFLINE_v5`.

Installed official runner:

- Entry point: `C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/dispatch_experiment.py`.
- Execution schema: `C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/_runtime/thesis_agents/schemas/execution.schema.json`.
- Approval schema: same directory, `approval.schema.json`; retained run schema: `run.schema.json`.
- Implementation: installed `scripts/_runtime/thesis_agents/compute.py` and `common.py`; installed `references/execution.md`.
- Repository copies: `thesis-agent-skills/skills/thesis-compute-runner/scripts/_runtime/thesis_agents/`.

`dispatch --help` was inspected successfully. The reviewed Python worker receives exactly `--manifest FILE --output-dir DIRECTORY`, launched with the interpreter running the dispatcher (`sys.executable`), a sanitized environment and a duration bound. A scientific worker therefore needs the pinned science interpreter directly, or a reviewed launcher for that interpreter. The development manifests for `m1_dual_latent` and other adapters are not automatically official execution manifests.

## Strict execution manifest contract

Every following top-level field is required; additional fields are rejected:

| Field | Contract |
| --- | --- |
| `schema_version` | Exactly `"1.0"` |
| `experiment_id`, `run_id`, `stage_id`, `task_id` | Identifier pattern `[A-Za-z0-9][A-Za-z0-9_-]{0,127}` |
| `execution_target` | `local`, `mock` or `runpod`; no scope-changing CLI override |
| `reviewed_script` | Contained repository-relative `.py` path, tracked at execution |
| `script_sha256`, `git_commit` | Exact lowercase 64/40 hex respectively |
| `seeds` | Nonempty integer list; no duplicates; preserve uint64 scheduling without JavaScript rounding |
| `datasets` | List of strict objects with `id`, `version`, `license`, `split` strings |
| `inputs` | List of strict `{path, sha256}` objects, contained repository-relative paths verified by dispatcher |
| `outputs` | Nonempty distinct paths under `logs/`, `metrics/`, `checkpoints/` or `outputs/` |
| `metrics` | Nonempty string list |
| `budget` | Strict `max_seconds` integer 1–86400, `max_usd` and `hourly_usd` nonnegative; estimated cost must fit cap |
| `resources` | Strict `vram_mib` nonnegative integer, positive `ram_mib` and `disk_mib` |
| `cleanup_policy` | `delete-after-verified` or `stop-for-recovery` |

Optional `remote` is a strict object with `image`, `gpu_type`, `gpu_count` (1–8), `artifact_base_url`, `terminate_after_seconds`. It is required for remote execution. Current live RunPod creation/transfer is deliberately unavailable because deadline enforcement is not established; local USD0 is the feasible route.

There is no arbitrary `args`, `env`, `command` or embedded candidate `config` field. Put candidate config, schedule, split metadata and statistical analysis plan in versioned files listed in `inputs`; the reviewed worker finds them through its explicit interface. Raw datasets live outside the checkout and cannot be declared as arbitrary external `inputs` paths. A contained metadata index can bind those external raw paths and their existing expected hashes; the worker must enforce that binding only after authorized scientific unlock. Do not hash held-out image bytes in an approval-free prepare step.

Preview checks manifest schema, script hash, declared input hashes, output paths and budget consistency. **Preview success does not establish a clean commit, tracked script, sufficient free GPU, method review, split acceptance or scientific correctness.** Actual execution additionally requires an exact clean Git commit, tracked worker, matching approval and measured local GPU availability. Artifact destination is fresh `<artifact-root>/<stage_id>/<run_id>` and contains manifest snapshots, logs, outputs and summary with verified declared artifact hashes. Store manifests/artifacts outside the checkout to keep it clean.

## Reservation metadata and sample sizes

Current B3/B4 metadata is in the separate preserved checkout:

`C:/Users/Soroush/.codex/worktrees/b3-coco-release-audit/THESIS_GUIDE_OFFLINE_v5/`

| Metadata path there | SHA-256 inspected |
| --- | --- |
| `data/splits.csv` | `60ff11ae5a81698446573c5f7fbd9d3067a5a2619abdf29ac2389931de1e1b9f` |
| `data/sample-size-check.json` | `58200f3c2b88fd27b2c864ebaa2d8f291eabe04d3edc509d26d933c2431f7bac` |
| `data/holdout.json` | `ec5d84ec30e127e02b04d133cd2020374f4bb3079cf2fdfe58f0b3d0c3dd08e4` |
| `configs/splits-admitted-v2.json` | `02cab97279eb657dfe52c34a5fa987c375fac40b137b098b646754f7cfeb0bc3` |
| `data/dev-ids.json` (original 32 development reservation) | `7cc2a4c827fd1c64b2f6d529a3726b843a0c635077982deb87725fbc3ac7f0bc` |

The admitted configuration points to `data/b4-admission-20260926/source-manifest.csv` (recorded SHA256 `40bfeca7c589b8352f93535070bc74fca70c6458216ea5422f0dc173f57110c4`) and `development-reservation.json` (recorded SHA256 `0bfd4178a1929e26d12401000c1eda0c549034c348458844e72f0c5b0a8f79ae`). These recorded values are not claims of newly verifying those files. `data/manifest.csv` is the earlier acquisition index, not a substitute for the admitted source manifest.

| Domain | Development images/groups | Calibration images/groups | Test images/groups |
| --- | ---: | ---: | ---: |
| MS-COCO | 200/200 | 200/200 | 600/600 |
| DIV2K | 300/300 | 300/300 | 300/300 |
| DiffusionDB | 1000/259 | 1000/251 | 3000/757 |
| Total | 1500/759 | 1500/751 | 3900/1657 |

Groups are finite operational leakage-screen components, **not certified independent population units**. The latest metadata retains all 6900 images but explicitly records the DiffusionDB group shortfall. One prospective representative per domain component is the inference unit; other members are retained for coverage/cluster sensitivity, never extra independent N. Do not quote the old draft's 3000 independent DiffusionDB test images.

`sample-size-check.json` says `engineering_split_locked=true`, `final_scientific_split_accepted=false`, `scientific_compute_authorized=false`, `planned_independent_counts_met=false`. Its explicit prerequisites are method conformance/calibration review, exact-manifest user compute approval and separate future pair/attack protocols. `holdout.json` preserves the 100 original DIV2K validation images and linked components for test only; this is a source-partition holdout, not established OOD or cross-model generalization. The original32 development reservation is 10 COCO/10 DIV2K/12 DiffusionDB and cannot be relabeled as test.

The MAIN `.thesis-build/b4-admitted-staging-history-20260926/` copies are historical staging records: use the current reference checkout above for preparation; do not silently substitute historical sample counts. MAIN raw images are under `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/` and remain unopened until the authorized run.

The new contained metadata index is `research/m1-confirmatory-external-index.json`: it joins the fixed300 schedule to existing admitted raw receipts without following any external raw path. Its annotation input alternative is the exact extracted `instances_val2017.json` artifact, SHA256 `e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f`, 19,987,840 bytes, at the lexically bound `data/raw/annotations_trainval2017/annotations/instances_val2017.json` under MAIN. This identity comes from the existing acquisition receipt, not a new annotation read/hash. COCO2017 release, the recorded upstream archive URL and annotation CC-BY-4.0 attribution are retained; image rights remain separate. Original ZIP SHA256/revision remain null, and the recorded download-page revision is not an archive revision. The exact extracted artifact can be proposed for adoption at M1 review without requiring unavailable original ZIP provenance. Metadata readiness does not accept the source contract or unlock images, annotations or features; all scientific flags remain false.

## Statistical and threat contracts available before freeze

`research/acceptance.md`, `sample-size.md`, `research-contract.md` and `scripts/a4_protocol_reference.py` provide documentary rules. Primary clean endpoint is `both_match` on encoded, re-decoded untouched C1, with separately reported C0-source, matched C0-reconstruction and C2 wrong-owner negatives. Every eligible attempted source remains in coverage; positive invalid/missing outputs count as misses, negative missing outputs count adversely for the conservative bound, alongside valid-output rates and failures.

Synthetic public roster is `thesis:owner:00`–`15`; enrolled and next-index wrong owner and one uint64 embedding seed are deterministically derived from frozen source UID using the documented SHA256 tags. K=1 is not many-owner search or authentication. The existing calibration contract searches the 101x101 semantic/instance threshold grid with strict `>` comparisons, integer empirical ≤1% negative-cell eligibility, macro-TPR maximization and fixed tie breaks. Freeze on calibration alone before test. A new candidate with different score semantics or extractor must document the amendment and parity rather than silently reuse incompatible thresholds. Draft joint objective is per-domain one-sided95% TPR lower bound≥80% and every negative upper bound≤1%; no measured achievement is implied.

Available threat groups:

- T1 documentary fixed JPEG/resize/crop-restoration/noise profile: 300 test groups/domain, four transforms; 3600 marked outputs and7200 correct/wrong-owner calls minimum. Group selection is metadata-only deterministic before outcomes. Failure and quality accounting remain explicit.
- T3 regeneration, T4 donor/recipient transfer and T5 semantic hard negatives are M1's primary development threats, but the old preregistration still marks their confirmatory severity/admissibility/pairing protocols blocked. Development v5 schedules are reusable implementation examples, not approved held-out schedules. Freeze exact attacks, seeds, Q/K, component states, baseline side information, content-retention/admissibility and union-of-reused-group analysis before execution.
- T2 removal and T6 public spoofing are separate; do not pool T6 with T4. No confirmatory attack sample-size or pair-power claim is currently supplied for T3–T5. Seeds/attacks/owners do not multiply source N.

The narrow draft's T5 unmarked endpoint is explicitly canonical `C0-source`, paired with each marked `C1` endpoint and queried against the other endpoint's enrolled public owner. Matched C0 reconstruction remains separately evaluated in clean rows. This prospective input clarification changes no pair selector, threshold or authorized-access status. `research/m1-confirmatory-planned-inventory.json` reserves the complete image/query/dependency inventory with unresolved candidate initialization and post-unlock T5 eligibility; it is not an official execution manifest.

## CLI and rehearsal/approval sequence

These are **parameterized interface examples**, not commands authorized to run scientific data. Set the variables to final external files and the exact clean candidate checkout after freeze.

```powershell
$runner = 'C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/dispatch_experiment.py'
$sciencePython = 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe'
& $sciencePython $runner dispatch $manifestPath --repo $candidateRepo --artifacts $artifactRoot
& $sciencePython 'C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/validate_approval.py' validate-approval $manifestPath $approvalPath
# User launch only after milestone approval and all prerequisites:
& $sciencePython $runner dispatch $manifestPath --repo $candidateRepo --artifacts $artifactRoot --execute --approval $approvalPath
```

Approval binds complete canonical JSON manifest SHA256 (runner `object_digest`, not pretty-file bytes), experiment/run/target, approve decision, issue/expiry times, limits, actor and authenticated source reference. Agents do not fabricate this record. Changes to scientific core require renewed review/decision before confirmatory use. The 2026-10-03 handoff permits USD0 development freely but explicitly preserves confirmatory user approval and rehearsal.

`research/approval-policy.md` requires identical launcher/worker/journal/guard/heartbeat rehearsals using synthetic generated images only, outputs exclusively under `.thesis-build/rehearsal/`, with every stage passed at the same clean commit before presenting a scientific package. Rehearsal is approval-free and provides no scientific evidence. Existing `scripts/rehearse_v4_saved_evaluation.py --id rehearsal-<id> --stage all` implements stages `real`, `scale`, `kill`, `term`, `finalterm`, `timeout-early`, `timeout-unit`, `hostloss`; additional stages `full`, `degenerate` exist. It is a v4 saved-evaluation harness, **not a ready rehearsal for the forthcoming M1 candidate**. Adapt the contract to the new worker; do not claim existing v4 passes certify it. `prepare_v5_study.py --rehearsal` is another metadata-only builder example; its ordinary mode hashes study image bytes and must not be called on held-out paths before approval.

Infrastructure-only reruns, if included explicitly in milestone approval, require unchanged scientific-core hash, changes exclusively in the approved harness list, failed prior attempt retained, non-scientific failure cause, independent reviewer receipt, unchanged ceilings/expiry and at most two reruns. Do not implement approval records or trigger such a rerun during preparation.

## Concrete remaining pieces for executable readiness

1. Freeze candidate code/config/spec and detector's three states, actual dual-key derivation, OwnerID binding, embedding domain, latent/model path and side information. Explain any neural/DCT/amendment difference. Include comparator v5 and native latent baseline scope without calling synthetic-only GS existing-photo attribution.
2. Complete M1 development evidence and independent milestone review. Determine whether acceptance targets were met or report three substantially different families' measured limitations. No reviewer/human verdict is supplied by this document.
3. Resolve calibration access/protocol and produce a frozen calibration receipt on the disjoint reserved calibration split under applicable authorization. No test-driven threshold, severity, seed or baseline selection. A negative no-admissible-threshold result remains valid.
4. Accept the metadata/source/group/rights contract through the applicable real process, explicitly retain DiffusionDB conditional-N shortfall, and create a versioned contained metadata-only selection index from frozen test UIDs/groups. Preserve original sourceplan; no resizing/native2K claim by implication. Record config/input provenance without opening test images.
5. Freeze T3/T4/T5 schedules, paired source/target graph, query/candidate budgets, scientific metrics, quality policies, practical comparison margins/multiplicity and analysis plan. Select groups without features or outcomes; semantic labels needed for T5 require a prespecified source/annotation route, not exploratory test CLIP mining.
6. Build the reviewed official launcher/worker plus atomic journal/checkpoint/failure inventory, time/space guards and heartbeat. Produce outputs only in declared contract paths. Adapter verifies metadata-pinned bytes and eligibility at authorized execution, computes features then, and preserves failures without replacements.
7. Pin all model/runtime/checkpoint hashes and licenses, worker dependencies and source metadata in scientific core. Measure duration/VRAM/RAM/disk on development, choose bounded shards/resume policy, USD0 local budget. Do not assume the 86400-second schema maximum is acceptable project scheduling.
8. Prepare strict manifest outside checkout with actual unique IDs, clean commit, worker SHA256, input receipts, dataset descriptions, seed inventory and outputs. Current A5 `thesis-runs/d916749c/experiments/a5-latent-dct-feasibility/execution-manifest.json` is intentionally `BLOCKED_NOT_EXECUTABLE`, not a usable template accepted by strict schema.
9. Pass all candidate synthetic rehearsals at the same clean commit, validate/preview the exact package, present M1 once for user confirmatory approval, then use the official runner. Keep held-out test locked until that authorization; no official lifecycle transition is created here.
