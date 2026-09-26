# Independent C4 local-loader and output-custody review

Recorded 2026-09-26T17:03:24Z. Author `/root`; actual independent reviewer `/root/b3_intake_review`, delegated under AGENTS.md and research/approval-policy.md. This is a **narrow partial software checkpoint**, not C4 closure, a human verdict, scientific acceptance or permission to execute.

## Exact artifacts and retained finding

Base component checkpoint independently accepted at `2e475a192f6540b79271bf7759b960e7a9e0a9cb`; main base `19c704a10d9d88f5d249eea0a57f98d0df00c19b`. New loader/output checkpoint `61df1cbf6e49ae08fc29cbe12a6e28650557a277` was **not accepted**: the reviewer independently reproduced a candidate produced under conflicting static/full/optimization configuration being saved under the trial's unrelated configuration identity. Shape, seed and supplied raw-source identity were insufficient.

Reviewer also warned that a completed first-image safety result could disappear when the second checker failed before the final pair receipt. Neither finding involved real assets or scientific inference.

Repair and exact independently re-reviewed code: **`fc270989b5d0ee93a57da1393380b60cc11ec728`**. Reviewed artifacts include src/embedding/{proposed,config_binding,local_assets,output}.py, tests/{c4_fixtures,test_c4_local_assets,test_c4_output}.py and research/c4-local-loader-output-20260926.md, against C1/A5/B5 contracts. The repair binds actual float32 source-tensor bytes, full raw config, current schema, static detector ID, complete settings and seed before learned-component encoding; TrialStore independently derives and compares the binding before PNG writes. Each saved PNG identity and completed safety row is fsynced before continuing to the next output.

## Actual independent checks and disposition

Reviewer reproduced the original conflicting config-hash case and a genuinely different loss/config candidate: both now reject **before either PNG is written**. It checked source-tensor, settings, seed, schema and static-ID binding. Its separate first-image **true safety flag / second-image exception** reproduction retained the first completed safety row and both PNG identities; hashes matched the actual persisted files.

Reviewer WSL owned CPU component/output suite: 20 tests, 19 passed / one documented JSON Schema skip. Two targeted Windows tests passed, including actual C1 validation of the owned full-shaped configuration. Diff check passed. Actual final message: original blocker and journal warning resolved; **no remaining blocker for this narrow loader/output implementation checkpoint**.

Root final exact code checks: WSL embedding/local-assets/output 27 tests, 25 pass / two expected JSON Schema skips; Windows embedding/local-assets/output/instance/owner/runtime 52 tests, 32 pass / 20 expected missing-Torch/NumPy/symlink skips; legacy scripts 185 tests, 174 pass / 11 expected skips. Neither environment has pytest; unittest substitution is explicit. Earlier synthetic teardown/duplicate-discovery, incorrect `/dev/null` diagnostic and nonexistent Windows `tests.test_owner_protocol` discovery failure are retained in the implementation note; only corrected distinct suites are counted.

## Boundaries and delegated decision

Author `/root` accepts this **partial software checkpoint only** following the actual independent re-review. #18 remains OPEN and PR #67 remains draft. The development embedding manifest remains header-only with zero executions. Full C1 schema validation remains an external prerequisite; typed fixtures do not confer validation or approval. The science venv still lacks `jsonschema`; an honest validation bridge or separately authorized minimal dependency must precede a real worker. Bindings are trusted-worker provenance guards, not authentication against fabricated Python objects or a hostile concurrent OS writer.

All tests used owned synthetic pixels, tiny text stand-ins and author-defined CPU tensor components. Mock loader factories intercepted the loading API before real checkpoint parsing. No actual candidate assets were copied, rehashed or loaded; no CLIP enrollment, study-image inference, safety-model inference, GPU use, downloads, installations, dataset mutation, scientific runner invocation or paid compute occurred. The prior C2 one-shot authorization is consumed.

Remaining C4: approved-run worker and explicit model/staging/activation budgets, actual validated config/parameter rationale, measured native image-conditioned gradient/VRAM and saved matched outputs, native quality and complete blind verification. Publisher custody/rights limitations remain. No numerical parity, feasibility or method success follows from the mocks. Official controller read remains d916749c paused at plan-acceptance, null choice, workflow SHA-256 `772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51`; no lifecycle decision or state write.
