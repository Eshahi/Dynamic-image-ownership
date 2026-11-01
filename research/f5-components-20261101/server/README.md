# Future server diagnostics

JUDGMENT: These runners implement the two entries in [SERVER-QUEUE](../SERVER-QUEUE.md). They have **not executed a writer, regenerator or server reader**. Local validation consists of stdlib plans, synthetic pure-logic tests and static inspection. This is preparation for a separate user decision, not approval, a runtime rehearsal or evidence that either hypothesis works. F6 is unchanged.

## Plans and local checks

Run from the repository checkout with its existing stdlib interpreter:

```text
python -I research/f5-components-20261101/server/q_res.py --plan
python -I research/f5-components-20261101/server/q_stage.py --plan
python -I research/f5-components-20261101/server/q_res.py --self-test
python -I research/f5-components-20261101/server/q_stage.py --self-test
python -I research/f5-components-20261101/server/test_runners.py
```

DERIVED: Saved plan outputs are [q-res-plan.json](q-res-plan.json) and [q-stage-plan.json](q-stage-plan.json). Each enumerates the fixed identities and cost assumptions. [validation.json](validation.json) records the actual local commands, exit status, duration and normalized source hashes. No scientific runtime is imported by those commands. Tests use synthetic dictionaries and byte files under this directory; they never decode an image or read a development/held-out outcome.

## Later execution inputs

SOURCE/JUDGMENT: A future approved GPU server needs the pinned existing Stage-2b runtime and assets, the retained Stage-2a and Stage-2b `rows.jsonl` plus `images/`, and this committed checkout. There is no installation, download, server provisioning or SSH code here. The shared helper checks the original source/config/profile identities, exact package versions, required model-file hashes and local asset receipt; it blocks network before importing scientific runtime. Missing assets fail rather than download. It rejects the current `CUDA_VISIBLE_DEVICES=-1` session guard. Do not clear that guard to run this session.

SOURCE: Both execution parsers require all of `--assets`, `--stage2a`, `--stage2b`, `--out`, `--instance-start` (actual timezone-aware server start), `--hourly`, `--max-hours` and `--max-usd`, as well as `--execute`. The output directory must be separate from retained inputs. No prior F6, Stage-2 or historical price/cap is inherited. The budget includes time since the actual start and reserves 1,800 seconds for retrieval/stop; it checks remaining budget between units. Model loading and a single in-flight unit cannot be preempted by these checks, so a later operator must monitor the paid clock. The runners never stop or destroy an instance automatically.

JUDGMENT: Execution first retains the fixed first-DESIGN-source pilot as part of the full inventory. A later explicit `--continue-after-pilot` invocation uses the measured projection and the actual paid ceiling. A failed pilot remains failed; no source replacement, threshold adjustment, extra quality-match search or automatic replay of failed scientific attempts is allowed. An interrupted started attempt is recorded as unsuccessful. Unstarted fixed units may be resumed with the same manifest; a changed protocol/input/code identity fails closed. A torn journal is refused for explicit inspection, not silently repaired. Continuation conservatively reserves the full projected post-pilot work even on a partial continuation resume; this can stop an otherwise affordable remainder and is not permission to raise the ceiling.

## Scientific contracts and limits

SOURCE/DERIVED: Q-RES reuses existing marks. It enumerates 1,440 new outputs and 3,240 reader calls. Its SD1.5 adapter preserves native generation arguments and safety checks while validating the declared 1,024 geometry instead of the old hardcoded 512. SDXL retains the original 1,024 size-conditioning variables at 512 working pixels. Both resize in/out with the frozen LANCZOS convention and read at 512. VINE has only native 100-bit presence; semantic/instance/B endpoints are N/A. The original VINE quality failures are retained. B is a failed diagnostic, not the new acceptance rule.

SOURCE/DERIVED: Q-STAGE instruments the original F5 implementation without choosing a new iterate. Arm A includes both fragile writes and the intermediate refinement. Arm B makes one robust-only attempt at Arm A's realized total MSE allowance. The fixed grid has 24 marks, 132 snapshots, 3,600 initial-PGD scalar trace rows, 324 regenerated images, 600 native reader calls and 108 additional snapshot probes. The original writer's internal verification uses source features and is retained as a writer diagnostic; it does **not** replace native clean reading from the final image's own features. Float arrays preserve their preclip values; their clipped encoder projection is labelled diagnostic. Source-hash and instrumentation checks establish only code structure, not empirical bit identity on a GPU. Numerical fidelity and actual costs remain unmeasured until a separately approved pilot.

JUDGMENT: Both runners preserve raw scores, frozen C/J, Bs/Bi/B and the unsafe union sensitivities independently, including failures and missing-as-success upper bounds. Source success requires two of the three fixed seeds. Negative calls are shown independently and never absorbed into an efficacy aggregate. The queue's prospective kills are applied without changing cutoffs. No h-based reader, allocation change, new code, threshold or safe ownership claim can be promoted from these diagnostics. Q-STAGE omits new T4/T5 testing and uses only six EVALUATE sources; even survival of every diagnostic kill leaves safety and comparative efficacy unresolved. Human visibility is MISSING.
