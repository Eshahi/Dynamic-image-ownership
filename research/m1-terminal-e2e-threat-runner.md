# Conditional end-to-end development threat implementation

This implements the frozen `m1-terminal-continuous-expansion-design.md` for candidate `m1-terminal-continuous-e2e-v1`. It is implementation readiness only. No assessment was launched, no held-out data were accessed, and no M1 or security target is asserted.

`scripts/m1_assess_terminal_e2e.py` prepares a source-bound manifest on CPU and executes one bounded partition. `scripts/m1_analyze_terminal_e2e_threats.py` independently replays receipts, byte operators, score math and evaluator controls on CPU. `research/m1-terminal-e2e-threat-schedule.json` freezes all 489 logical conditions. Existing embedding/reader/threat modules are imported unchanged, with no monkeypatch of their scientific globals.

## Admission and missing lineage

Prepare requires exactly twelve entries in the fixed candidate source order and a passing original two-source end-to-end pilot receipt. Every available source must pass the full endpoint/initializer integrity audit and share one candidate method-core hash. Expanded clean scientific failures remain eligible and visible. An operationally absent source instead requires an explicit retained development terminal-attempt receipt, its matching source ID, and a reason. The first two pilot sources cannot be missing. Every dependent clean, regeneration, transfer, component, control and diagnostic slot retains its planned denominator and missing status.

An ordered source-inventory JSON contains available run-directory strings or records of this form:

```json
{"id":6012,"status":"missing","reason":"bounded initialization attempt failed","source_run":{"path":"ABSOLUTE_MAIN_DEV_RUN/run.json","sha256":"EXACT_SHA256"}}
```

Use `--prepare --source-inventory INVENTORY --pilot-receipt PILOT_RUN_JSON --manifest PATH_IN_WT`. Alternatively provide twelve ordered `--source-dir` arguments. The prepared manifest must be committed before execution; workers reject uncommitted or changed dependency bytes, including the manifest. Method-core, assessment-core, current HEAD, committed file hashes and immutable input receipts are separate fields.

## Operators, partitions and recovery

The inventory is 24 clean, 312 regeneration, 80 T4, 66 component-pair, and seven T5-transfer conditions: 423 images and 1692 primary four-owner queries. Clean and deterministic VAE-mode rows alias the previously audited candidate PNG/readout arrays. Diffusion uses the original pinned local SD1.5 img2img/DDIM operator, 20 configured steps, CFG1, empty prompts, eta0 and paired fresh CUDA generators for seeds0/1/2 at strengths .05/.1/.2/.4. Both configured scheduler timesteps and actual UNet forward timesteps/NFE are retained.

Original RGB8 donor-residual transfers retain byte units and ties-to-even rounding. Native projection and its unmarked-donor sham implement the fixed analytic minimum-norm two-channel displacement and the frozen precision clarification in `m1-native-projection-precision.md`. There are zero adaptive detector-decision queries. Supplied donor/recipient images reach the public observation API; clean enrollment latents do not replace these observations. Float64 donor/recipient/target arrays, decoded residual R, float64 unscaled decoder inputs, actual flat FP16 decoder-input arrays, conversion errors, postcast projection residuals, clipped decode hashes and the quality-only cap receipt are retained. The analyzer recomputes conversion and cap arithmetic; it does not rerun VAE decoding.

Run `--run --manifest MANIFEST --partition shard-0 --output-dir FRESH_MAIN_DEV_DIRECTORY` through the owned development launcher. Partitions `shard-0` through `shard-5` each contain 56 clean/regeneration conditions for two fixed sources; `transfers` contains 87 transfer images and 66 component conditions. Each process has a cumulative 1800-second, 16GiB RAM, 500MiB artifact budget and GPU allocation of at most10GiB or available memory minus512MiB reserve. No GPU is initialized by schedule generation, preparation, analysis or tests.

Condition JSON and an append-only journal are persisted after image generation and again after readout. One continuation may use `--resume-from PRIOR_DIRECTORY` into a fresh directory, only with identical scientific identity. Previous time/artifact use counts toward the same partition budget. Saved attack PNGs survive a subsequent readout failure and are reused, never regenerated; completed and safety-blocked conditions are terminal. Operational cap failures remain failures, not missing-data security success. Generated models are released before public readout models load. Model-call counts account for public-reader caching separately from logical score queries.

## Analysis and interpretation

Invoke the CPU analyzer with the same manifest, one final `--input-dir` per partition, and a fresh MAIN development output directory. It verifies full output inventories, partition identities, retained source receipts, PNG pixel hashes, pHash, score/decision replay, quality predicates and pixel metrics. CLIP and LPIPS observations remain retained inference evidence; CPU analysis does not silently rerun them.

All 1164 diagnostic slots, 876 geometry slots, and 1437 logical negative slots are explicit and separate from primary queries. Fixed donor-C1/recipient-C0 DD/DR/RD/RR controls expose background and existing semantic compatibility; their H-independent semantic equality is checked. Delivery requires enrolled donor positivity, DD positivity of the attacked image, DD background negativity, and strict recipient quality. T5 additionally retains the continuous semantic-challenge predicate. Reports separate delivery from blind production acceptance, preserve per-arm coverage and missing outcomes, and leave `security_pass` null. The dependent query counts are not independent sample sizes or an empirical FPR estimate. Human visual verdict remains missing.

CPU verification command:

```text
MAIN/.thesis-build/a6-science-venv/Scripts/python.exe -m unittest discover -s tests -p test_m1_terminal_e2e_threats.py -v
```

The tests cover exact inventories/pairs/seeds, projection minimality and units, unchanged residual/cap arithmetic, no decision queries in attack construction, delivery/background/quality gates, missing denominators and anchor slots, immutable one-continuation recovery, and the frozen decoder conversion including an explicit cast-order counterexample. Actual GPU execution and conditional admission remain unperformed until the parent establishes the required pilot evidence.
