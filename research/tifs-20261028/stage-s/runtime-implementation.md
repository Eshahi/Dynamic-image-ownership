# Stage S producer and reader implementation

**Partial-session closure: INCOMPLETE, DO NOT RUN.** The driver and forecast enforcement described below are required future integration, not delivered behavior. `Journal(read_only=True)` remains incompatible with the common helper. Both scientific entrypoints are locked by `READINESS.json`; see `../FINAL-REPORT.md` and `RUNBOOK.md`.

Static implementation record, 2026-10-28. No images, scientific libraries,
experiments, models, timing probes or GPU work were executed on the laptop.
The only execution validation was `py_compile` using MAIN stdlib Python with `-I`.
Actual gradients, PNG readback, replay, memory fit and complete runtime remain
server rehearsal obligations; syntax success supplies no evidence for them.

`scripts/tifs_stage_s.py` supplies prepare, clean, native, threats, secondary and
manifest. `scripts/tifs_stage_s_read.py` supplies detect and quality. Every CLI
requires assets, out, immutable instance-start-utc and hourly-usd. Use separate
out directories for rehearsal and screen; both receive the same rented-instance
start instant so paid rehearsal and idle time consume the same 15-hour budget.
The screen must pass the driver rehearsal forecast before full launch.

The source manifest contains historical metadata, not machine-local paths.
Put the already authorized canonical PNGs at `ASSETS/sources/SOURCE_ID.png`, or
supply canonical_path entries in a newly frozen source manifest before any
output. Preparation checks PNG and RGB8 hashes against the development manifest,
loads CLIP on CPU, computes original seven-view features, then seals greedy
donor-to-unused-target pairs before marking. Numeric target IDs break exact
cosine ties. Human distinctness labels remain missing.

Identity pins producer, reader, writer, common helpers and retained code,
retained config, profile, source manifest, package versions, price, instance
start and rehearsal status. Resume rejects any change. Existing successful
artifacts and saved noise tapes are verified before work resumes. The source
files remain references to immutable original hashes, verified in preparation.

Each unit checks wall-clock budget with a retrieval reserve and estimated next
unit cost. Native families run serially K3, R0, R1. No GPU reader/writer/quality
object is intentionally retained across stages or families. Family-ready
markers record actual device/free/allocated/reserved memory and explicitly do
not authorize concurrent readers. The default reader is one serial worker.
Explicit i/k readers own disjoint shard journals and never share append files.

Native C0 runs first per cell/source/seed, captures diffusers posterior and
injection draws, saves a hashed CPU tape even on an authentic blocked output,
then each marked arm replays it. All draws must be consumed. Only the exact
exception message `safety_checker_blocked_output` counts as a safety block.
Other errors remain terminal missing outcomes. No prompt/seed replacement or
OOM fallback occurs; an OOM records RESOURCE_STOP and prevents automatic resume.

F6 reads explicitly dispatch as `f5-r2`. Internal reads report ALPHA/BETA,
frozen C/Q/J/H/D/F/A and D_and_F, raw thresholds, and donor-carrier Q. Threat
reads additionally report the fixed binding modes. Donor payloads are evaluator
references only; the detector derives semantics from the suspect. External
arms preserve their original known-message and wrong-message presence rules.
T4 uses centered published donor patches and geometry-matched unmarked shams;
known-clean residual transfer remains separately labelled. T5 reads the untouched
recipient under the donor claim. Recipient-relative quality governs eligibility.

Quality reports clean-vs-original, native/secondary-vs-input and vs-original,
and T4/T5-vs-recipient separately. The eight fixed secondary transforms include
all arms and use a source-derived common Gaussian draw across arms. No detector
result selects sources, targets, candidates, transforms or seeds.

The producer manifest verifies expected clean/native/threat/secondary IDs and
hashes every existing successful artifact/tape, retaining missing and blocked
outcomes as incomplete. A stage with missing/blocked/error outputs exits 4 and
never emits STAGE_DONE. Reader completion is explicitly only a snapshot of the
currently available producer outputs. Final completeness requires the root
driver to merge disjoint shards and check the full frozen inventory; an active
producer snapshot is never a final scientific verdict.
