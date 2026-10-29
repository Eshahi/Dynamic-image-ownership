# Stage P implementation and server contract

This is unexecuted server code and metadata. No source image, model, attack,
detector, quality metric or scientific timing was run on the laptop. The only
local execution is standard-library unit tests on synthetic JSON and opaque
byte fixtures. No selected configuration or user decision receipt is created.

## Files and reuse

`scripts/tifs_stage_p.py` owns immutable plan materialization, the bounded pure
selector and the saved-journal reader. `scripts/tifs_stage_p_select.py` provides
the metadata CLI. `scripts/tifs_stage_p_driver.sh` serially invokes the existing
Stage S producer/reader and its native paired-tape implementation. There is no
second image experiment framework. `search-config.json` records the exact
eight candidates and allocation; the protocol remains authoritative for its
scientific interpretation. No T4/T5, secondary attack, external baseline or
binding ablation is available in Stage P.

The runtime integration is owned by the main session. It maps Stage P sources
to donors and leaves targets empty, prepares the full immutable partition,
filters actual clean/native/read inventories by the cumulative fixed prefix,
and prevents a check read before nomination. Preparation of tuning metadata or
all16 tuning originals never permits preparation of any check original. The
standard setup and global instance-clock/resource guards remain required.

## Stable function interface

- `load_manifest(path)` validates the exact-byte SHA256 sidecar, development
  status, sixteen/eight source counts, disjoint identity/hash fields and fixed
  rung allocation. It reads JSON metadata only.
- `materialize(base_path, manifest_path, receipt_path, trial_id,
  partition="tune", nomination=None)` returns a complete immutable config with
  full16/full8 sources. It requires the externally recorded prospective Claude
  receipt and the same base-config hash. Check permits only the nominated
  candidate, shared retained F5 and its one budget control. It never creates a
  human approval or interprets its output as authorization.
- `active_sources(config, count=None, calibration=False)` returns a committed
  prefix without changing configuration identity. Tuning permits4/8/16;
  check permits8 only. Calibration permits2 only for retained-f5,
  f6-noise-p52 and f6-x0-p52, on tuning sources only.
- `summarize_trial(out, config, source_rows=None, count=None,
  calibration=False)` reads runtime journals, not aggregate success labels.
  The config is stored at `out/config.json`; runtime identity must bind those
  exact bytes and the source manifest. `prepared.json` contains every source
  of that immutable partition, its source hashes and full donor order, with
  no targets. Source images are never decoded by this function.
- `select_rung(summaries, retained, budget_controls, n, profile, entrants)` is
  pure. Its maxima are8→4,4→2,2→1. Unknown potentially eligible contenders stop
  allocation; they cannot be silently ranked away. The full final controls
  and12/16 futility screen precede nomination.
- `check_winner(summary, retained, budget, profile)` evaluates one fixed
  nominated candidate on all8 check sources; six foreign endpoints and R0
  each require6/8. Its only positive check status is `PASS`; it cannot select
  a replacement.

Configuration IDs are `f6-noise-p52/p46/p42/p38` and
`f6-x0-p52/p46/p42/p38` (with each full prefix repeated), `retained-f5`, and
`f5-budget-p52/p46/p42/p38`. Each trial has exactly two arms: its marked arm
and `unmarked`. The parameters hash includes the complete writer configuration,
native cells/seeds, owners, payload and parent config; robust budget and
surrogate are the only scientific search axes. Native K3 is selection-seen and
optimization-excluded throughout.

## Raw evidence and missingness

Every expected clean/native image needs a successful, hash-verified producer,
the appropriate F5-reader calls under alpha and beta, and a quality row bound
to the same output hash and source. Marked native payload/input must match its
clean producer. Raw detector results are independently translated to distinct
C/J/F endpoints. Stored endpoint labels cannot supply a result. Every seed0/1/2
is required even if two seeds already fix a majority. Missing negative calls,
references, metrics, tape receipts, artifacts or seeds remain incomplete.

Marked native rows must save `replay_tape_receipt` equal to the C0 row's existing
`tape_receipt`, plus `replay_tape_consumed: true`. Shared-control comparisons
require identical source hashes/order, owners, native cells/seeds, profile,
reader/native code/package identity and per-source/cell/seed tape receipts.
Different target budgets never establish achieved-quality parity; paired
saved-RGB8 metrics do. C0 clean identity metrics may use the established
explicit infinite-PSNR flag; marked clean PSNR must be finite.

Candidate strict quality, clean F and observed forbidden C/F events determine
candidate rejection. Retained-control clean performance and false events are
reported diagnostics and never become an undisclosed threshold. The proposed
profile additionally requires the budget control's strict clean quality/F
and achieved paired quality/gain conditions. Both controls need complete finite
evidence before final nomination/check even if a condition is diagnostic under
round1. The one profile is taken from the prospective external choice; an
observed round1 failure cannot switch profiles.

Each journal row remains retained. Compute reports count every newline-committed
attempt, including superseded terminal/resource failures, marked writes and
duplicated C0 clean/native work. `seconds` is summed per unit. Invocation wall
seconds and model-load seconds are also reported separately, including IDs of
unfinished invocations; these overlapping measurements must not be added to
one another. Per-directory cost is counted once in the final report, rather
than once at every cumulative rung. Logs/global clock retain setup, idle and
other paid work outside those journal-unit counters.

## CLI and ordered server driver

All CLI commands require `--run-root RUN_ROOT --user-choice CHOICE_JSON`.
Optional `--base-config`, `--source-manifest` and final `--destination` support
explicit paths. The default final destination is the protocol's
`stage-p/selected-config.json`; there is no placeholder winner.

1. `plan` creates only immutable tuning configs and the search-plan metadata.
2. `calibration` prints three fixed trial IDs. The driver runs their first2
   tuning sources with `--stage-p-count 2 --stage-p-calibration`, then requests
   the existing forecast CLI with `--stage-p-root RUN_ROOT`. These outputs are
   reused at rung1 and consume no additional source allocation. No Stage S
   donor, target or rehearsal source is usable for calibration. This is the
   prospective integration correction to the initial runtime reuse plan.
3. `entrants --count N` (N =4/8/16) yields the exact entrants authorized by successful
   preceding rung records. Run shared retained F5 once per new source prefix.
   Each candidate directory resumes its old rows and adds only new sources.
4. After rung2 fixes two finalists, `finalist-controls` materializes only their
   distinct budget controls on all16 tuning sources. `advance --count 16`
   validates those controls before nominating one winner.
5. Each `advance` reads all raw journals, writes a latest decision/inventory
   for failures too, and freezes successful progression records. Prior-rung
   evidence digests are rechecked when later promotions are requested. The
   nomination records UTC time, full tuning-config hash, parameter hash,
   source/plan/choice hashes and tuning-row/progression digests.
6. Only `plan-check` after a valid nomination creates three check configs.
   The nominated writer and both controls then run their eight fixed sources.
7. `finish` writes the final search report for every outcome, but writes
   `selected-config.json` only on `PASS`. It records all eight planned IDs,
   actual attempts, every rung's candidates/status/reasons, evidence hashes,
   achieved controls, check outcome and actual work. It sets
   `execution_authorized: false`. Failed/incomplete/resource-stopped searches
   cannot silently fall back to the original Stage S default.

Example after external choice and approved server setup:

```sh
bash scripts/tifs_stage_p_driver.sh ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD CHOICE_JSON
```

Scientific stops use exit2, resource stops3, incomplete inventories4; successful
metadata advancement/check uses0. A malformed/tampered identity is a hard
error, never scientific success. Existing runtime per-unit terminal failures
may finish the rest of the fixed inventory; resource/dependency errors stop
immediately. A later invocation uses the same global paid-session start.

## Local validation

The reused producer/reader now resolves the external choice before sources or
models, reconstructs each immutable Stage P config, and validates promotion
or nomination before a larger prefix or check is usable. `prepared.json`
always retains the whole16/8-source identity, while preparation, production
and reading use only the active fixed prefix. Stage P bypasses CLIP assignment
and rejects Stage S rehearsal, threats and secondary stages. Calibration
checks each candidate's own writer variant, native RGB8 replay, and R0/R1
first-step conditioning parity; marked native rows record the consumed C0
tape receipt. Every process uses a Linux alarm against the same instance clock
and collection reserve, including the initial calibration. Later work requires
the frozen GO forecast bound to choice, base config, all three calibration
identities, source manifest, code, profiles, packages and measured GPU device.

The standard-library suite `scripts/tifs_test_stage_p.py` covers source/prefix
immutability, fixed calibration IDs, candidate cardinality/ranking and distinct
J, missing contenders/negative calls/seeds, strict quality, source/tape pairing,
profile-specific controls, tuning/check futility, raw endpoint recomputation,
artifact hashes, torn tails, full CLI promotion/nomination/check lifecycle and
refusal to overwrite an earlier selection after contradictory check evidence.
Mocks are deterministic and are not scientific observations. Numerical writer
parity, native conditioning/replay, scientific metrics, memory/time feasibility
and the actual selection remain server verification items.
`scripts/tifs_test_stage_p_runtime.py` additionally checks routing, immutable
prefix preparation using opaque fixture bytes, no source enlargement without
promotion, exact forecast bindings and resource-stop persistence using pure
mocks. The combined Stage P, runtime, launch and runtime-binding suites passed
36 tests locally; producer/reader and runtime test files also compiled.
