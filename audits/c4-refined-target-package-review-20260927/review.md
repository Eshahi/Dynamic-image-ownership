# Independent refined-target execution-package review

Reviewer: `/root/b3_intake_review`; author: `/root`.
Exact candidate reviewed: `dd347afb861774f7a86138e7170dba96d4f47044`.
Authority: AGENTS.md and research/approval-policy.md bounded technical delegation.
Scope: prospective package/code/design and metadata binding only. This does not
grant scientific compute, results acceptance, lifecycle advancement or C4 closure.

## Actual evidence inspected

Read refinement_package.py, c4_refinement.py, run_c4_refinement.py,
prepare_c4_refinement.py, their package tests, fixed JSON policy, prospective
experiment spec and execution design; inspected required existing custody,
validation bridge, scientific-component, quality and signature dependencies.
The prior independent component audit remains unchanged. Applied evidence-audit
claim/scope distinctions, not a full-thesis scientific audit.

Independently parsed the external v1 manifest and verified canonical SHA-256
`78bcae98866135714d0f7847a8de7d076f1adea29c20509d8766079d95088683`.
All 46 exact required input pins matched current worktree bytes and their declared
Git blobs, allowing only actual Git CRLF-to-LF normalization. In-memory builder
output matched the external manifest exactly. The official helper's v1-design
execution manifest was canonically identical; its experiment spec also matched
the committed prospective spec. No execution/approval was created or invoked.

Owned/model-free checks actually run:

- Verified explicit Windows interpreter: package suite 6 cases, 5 passed and one
  expected missing CPU-storage-dependency skip.
- Existing pinned WSL clean science interpreter: package plus composition suite
  23 cases, 22 passed and one expected Windows launcher-path skip.

The storage fixture wrote only owned tiny CPU tensors in its own temporary
directory. It verified exclusive safetensors creation, hash/size accounting,
no-pickle format and refusal on quota/name/count/overwrite violations. The worker
environment-failure fixture retained an explicit failed report/journal with all
25 cells pending, before any source/model access. No real study decoding,
learned-model load, image metric, GPU, network, download or installation occurred.

## Blocking findings

None in the declared prospective package scope at this exact candidate.

The fixed recipe checks exact experiment/run/target, seed, nine declared outputs,
metrics, resource/budget/cleanup fields, complete input set and canonical policy.
The historical full C1 config remains hash-bound; the bridge only adds this named
experiment to its allowlist and preserves validation and exact receipt checks.
The launcher uses a fixed offline env-i WSL interpreter and reviewed child, Linux
1140-second timeout with ten-second escalation, parent allowance below the outer
1200-second runner budget, and no approval creation or execution fallback.

The worker verifies environment/custody/receipt/source canonical identity before
model use. Its fixed source is the prior retained development image; no new
dataset access is introduced. Model loading uses the existing checked local
snapshot path and checkpointed frozen profile. The composition preserves distinct
original/refined targets and all historical controls. Exact old-control pixel
replay and original source enrollment must pass, without relabeling on mismatch.

PNG pixels feed safety, source-reference classical/LPIPS measurements and q/h
diagnostics, not a source-assisted detector. Models are released sequentially
before later metric models. All 25 fixed cells are retained with pending/running/
completed/failed status; normal nonconverged inverse arms have no fallback image,
remain explicit missing cells and force final package failure. Exceptions preserve
prior partial PNG/latent/journal evidence and original failure phase. Final
completion requires normal composition return, all cells and the final report;
the previously noted terminal-journal-only completion ambiguity is explicitly
rejected by this worker/spec.

State custody is exclusive bounded safetensors with fsync and digest/path/size
journaling: 4MiB per state, 64MiB aggregate, 1024 states, no retry/deletion.
The 8MiB journal reserves 64KiB for bounded failure records. Initial RAM/disk/VRAM
headroom is measured and durably recorded before refusal; original exceptions
are not masked by best-effort resource telemetry.

## Warnings and scientific limits

The fixed 64-update, normalized step-one, zero-prior profile is an explicitly
exploratory engineering budget, not literature-reproduced or outcome-optimized
hyperparameters. NFE257 equals initial1 plus64*(gradient1+maximum3 trials).
Radius80 exceeds the nominal sum64 of step lengths; the strict measured rounded
radius guard remains binding. Continuous MSE tolerance0.0003 is below10^-3.5 but
does not guarantee quantized PNG PSNR, SSIM or LPIPS. The fixed-point pair32-NFE/
per-arm128-NFE/absolute1e-5 residual budget permits attempts, not convergence.

The 9GiB Torch allocator ceiling is not whole-GPU memory certification; 12GiB RAM
is an estimate, not an enforced process-memory cap, and the 4GiB disk plan relies
on the stated headroom checks and bounded known snapshot/output writes. Prior
localization resource/time observations do not establish
fit for 64 backwards and two inverse paths. Actual quality, convergence, elapsed
time, learned-model parity and fit remain unverified. External timeout may leave
only partial evidence: missing terminal reports must remain interrupted/incomplete.
Disk/OS failures can prevent a final report; they must not be relabeled completed.

Primary arm-wise quantities are retained for later explicit comparisons; no
population CI is supported by one source's six dependent arms. This is not a
watermark test, blind detection, ownership/rights clearance, GNRI/REED reproduction,
native2K coverage, whole-dataset fit or a method-success verdict. Source rights and
redistribution restrictions remain unchanged. All prior approvals stay consumed.

## Disposition and next boundary

No narrow launch-design blocker. The candidate can proceed to a separately
verified final clean-commit binding and then a precise actual user approval
request. Adding this audit changes the checkout state; the current v1 manifest
must not be treated as the later final binding. No approval or scientific
execution follows from this review. C4 remains open and C5 dependent.

## Final isolated execution binding, independently checked

The existing isolated c4-localization-exec checkout is clean at exact
`dd347afb861774f7a86138e7170dba96d4f47044`. Its external
`v2-isolated-manifest.json` equals v1 and the in-memory builder canonically,
with unchanged SHA-256
`78bcae98866135714d0f7847a8de7d076f1adea29c20509d8766079d95088683`.
All 46 isolated worktree pins and their Git blob identities were independently
rechecked, including the unchanged implementation/spec/resources/output recipe.
The author checkout's new audit file does not alter this separate clean execution
checkout. Thus no new scientific-input rebind is needed for this isolated package.

Independently read/hashed installed helper entrypoints:

- compute runner dispatch_experiment.py:
  `b383af48b6c04ecde8d03e3f903419d6b733c90e3babc0e5acd7e8cd5f97c7e2`;
- design_experiment.py:
  `13376a113e4b2e6a4ecab87a32dd1ac3f0cc0404187cd596d3df739bb9c27d49`.

These identify the entrypoints, not a new whole-runtime/source-parity certification.
Additional installed runner runtime/schema byte hashes independently matched:
compute `4b98e5429d57bda48dbe7b239602b1c7ef60c7cbb19058e17136b29a09437d30`,
common `0c5bbcba998cf58d76961c4ba62674788d27e50882dd0740e114899ca3b84749`,
design `363c7f52ef2fa2821c16bcbb9684107fe5b4aeef1328d13bd0c78e050c2c985e`,
runpod `971cc5c3f24ff861c159653d8d063d3c05aa9b9a1b751f1449b82d5fae2ff163`,
execution schema `bb935080e74a657adb9f23e2c3ed3b9ce93968768bcc13635baac161267d27ed`,
approval schema `a4e58ad1dbff5d0135784ea236b1ba2a3f78a5812ddf34f4162f185be9daad33`.
The initial reviewer looked for the two helper scripts under the stable project's
scripts directory, where they do not exist; those read-only lookups failed. The
installed skill script locations were then discovered and verified, rather than
inventing a project helper or changing tooling. An initial audit-append patch
failed to match its context and made no edit; the exact tail was read and the
append repaired. No author source or execution artifact was changed.

Using the verified Windows interpreter, independently invoked only the official
runner's dry dispatch against v2 and this isolated root. It returned dry_run=true,
target=local, the exact preceding manifest digest and requires_approval=true.
No --execute or approval argument was supplied; no worker/model/GPU operation was
invoked. The official helper's already-inspected canonical manifest/spec agree.

Final binding disposition: no narrow blocker to presenting this exact isolated
package for a new actual user decision. No such decision is granted by this audit;
all prior scientific approvals remain consumed.
