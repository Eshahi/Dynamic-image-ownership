# Stage S producer and reader implementation

**Integration implemented; readiness lock remains INCOMPLETE pending root final review.** Driver and conservative forecast are now delivered. The common Journal read-only compatibility fix is owned and validated by the analysis integration task. Both scientific entrypoints remain locked by `READINESS.json` until the root review release; no server run is authorized by this note.

Static implementation record, 2026-10-28. No images, scientific libraries,
experiments, models, timing probes or GPU work were executed on the laptop.
Validation comprises `py_compile` and seven pure-logic forecast tests using MAIN stdlib Python with `-I`. The installed `bash.exe` is a Windows WSL launcher; a `bash -n` request hung without output and was interrupted. Bash syntax validation remains unverified here.
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


## Driver and measured launch gate

`scripts/tifs_stage_s_driver.sh ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD [rehearsal|full]`
requires setup to have been completed separately by the authorized server operator.
It creates `RUN_ROOT/rehearsal` and `RUN_ROOT/screen`; no source acquisition or
setup is embedded. It schedules one GPU process at a time: prepare, clean,
native (internally K3/R0/R1), threats, secondary, manifest, each detector method,
and quality. Rehearsal includes every arm, threat condition, native cell/seed,
and secondary transform on the two fixed donors and two fixed targets. The default
mode stops after rehearsal and forecast; `full` explicitly continues the screen.

Every successful C0 native rehearsal unit replays its recorded random tape and
requires exact RGB8 equality and complete draw consumption. This checks native
capture/replay, not equality of the deliberately approximate writer surrogate
with a full denoising trajectory. Each rehearsal donor also has a hashed writer
receipt covering clean projection parity and every frozen surrogate gradient.
Failed diagnostics cannot authorize a screen.

`--instance-start-utc` must be the actual rental start, including paid setup,
asset preparation, rehearsal and idle time. Forecast requires complete successful
producer and reader inventories, source identity, original code hashes, writer
receipts, native parity, and valid per-operation/invocation timing. Persistent
START/END and MODEL_READY receipts account cumulative process/loading overhead
across interruptions and resumes; the forecast scales variable
work by 16/2, including preparation; then requires current elapsed instance time
+ measured one-time overhead + 1.5 times full variable work + 3600 seconds for
retrieval <= 54000 seconds. A rerun rechecks current epoch time; a stale GO file
never authorizes a later launch. Measured per-operation and load maxima, multiplied
by 1.5, are sealed for screen checkpoint estimates. An interrupted invocation
without an END receipt is conservatively charged through the next start or current
time. Missing, failed or inconsistent timing is INCOMPLETE, never partial GO.

Initial rehearsal setup binding rehashes the pinned asset inventory once and
records baseline source hashes. Later invocations verify file identity metadata
and the unchanged setup receipt, source/asset plans, requirements and exact direct
package pins. This guards accidental changes, not a malicious administrator.
The capacity gate includes constructor and stage memory peaks as well as per-unit
telemetry, rejects measured demand above 24 GiB, and reserves a 20% filesystem
margin beyond conservatively projected output/tape storage.

Exit 3 stops immediately and preserves RESOURCE_STOP. Exit 4 retains incomplete
science and allows remaining fixed stages to finish; no failed unit is silently
retried. Other dependency/load errors stop the driver. The frozen analyzer is
the sole final source of GO/SCIENTIFIC_KILL/INCOMPLETE; rehearsal does not apply
the screen's scientific thresholds. Baseline failures remain visible and never
cause arm removal. Runtime identity now also pins the asset root and the driver,
forecast and analyzer code, alongside producer/reader/writer/common and retained
adapters. Reader rows preserve producer cell/seed/family/target/condition metadata.
No thresholds, selected arms or selected sources were changed.
