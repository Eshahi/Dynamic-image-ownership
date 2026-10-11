# E3-S1 Vast Linux deployment freeze

2026-10-11 13:06 UTC. Codex agent, gpt-6-astra/high. Bounded metadata amendment on `codex/vast-s1-deploy`, based on portability commit `ee9e2618f967732d07873a66e6ef10a2b2a79eb2`. Remote instance 55389808, machine 107776; parent reports Ubuntu 24.04, Python 3.12.14 at `/venv/main/bin/python`. This file grants no execution approval.

Separate Linux files preserve the Windows originals: `e3-s1-linux-environment-lock.json`, `e3-s1-linux-sdxl-lock.json`, and `e3-s1-linux-test.m1b-plan.json` in this directory. The plan binds checkout `/workspace/thesis/repo`, A6 `/workspace/thesis-assets/a6`, SDXL `/workspace/thesis-assets/journal-sdxl-vae-6f5909a7`, COCO root `/workspace/thesis-data/coco2017`, annotations at its `annotations/instances_val2017.json`, and approval `/workspace/thesis/ops/e3-s1-confirmatory-approval.json`. Official runtime remains `/workspace/thesis-runtime/scripts/_runtime`.

Static checks passed: all 300 source/group/raw-hash identities and order agree with the Windows index after only raw-path translation; schedule digest remains `fada9a67f066f2dc4bde5931d46911eb11bb10cb6e6bebcaa7abf33192cac9d0`; methods, owners, configuration hashes, T4/T5 selection, strengths .1/.2, seeds 3/4/5 and 27,000-second cooperative limit are unchanged. Metadata-only `validate_plan` accepts 300 sources under mocked Linux selection. Every referenced config/lock/index/schedule hash was checked. No pixels or annotations were opened.

All 14 locked scientific package versions match the server freeze exactly; environment changes are only platform and interpreter. The complete genuine pip freeze is preserved separately; Linux extras and the unresolved `packaging` build-local entry do not justify an unmeasured full dependency-equivalence claim. No dependency artifact hashes were supplied or invented. All 20 model download receipt rows agree with the original locked hashes and sizes (3,675,250,110 bytes). These are comparisons against parent-provided server receipts, not a new remote asset check. Sources/licenses/hash references are recorded in `research/downloads.md`.

Remote GPU pilots/rehearsals are waived by the user and skipped, not passed. The existing 8-hour manifest, 7.5-hour cooperative and 24-hour aggregate scientific ceilings are retained; the parent separately binds USD 0.4037037037037037/hour, USD 7.50 cap and instance rental supervision. The parent must prepare and authorize the actual Linux manifest/scientific core before execution. No approval file, manifest, official gate verdict, server command or scientific run was created here. Prior synthetic Windows evidence is not same-core Linux continuation evidence.

| File | SHA-256 |
| --- | --- |
| `e3-s1-linux-environment-lock.json` | `ff2785e584884ea94d871367ca303ce58cf4e37769d5142d6c1735377c0ce277` |
| `e3-s1-linux-sdxl-lock.json` | `79e3e4bbf68a9ada9798a7274cb76bb90eab58d1be864699fc739c117b63aa81` |
| `e3-s1-linux-test.m1b-plan.json` | `688899cb2f0fb9a110f3c05883038b3ce4d7dc9b1c8d1124015bbbeaf4738535` |
| `e3-s1-linux-external-index.json` | `091bad0fae4092ed8332ca64e44873cafcabd88ebfa8636957d5104be7a80a0f` |
| `e3-s1-linux-model-downloads.jsonl` | `a2a376467ba57a9cef9447ff992da5f0aa17f26a0c3bb8bcc83a1f914d9aa61a` |
| `e3-s1-linux-environment-freeze.txt` | `4ae8d45d137d2b3b9e80cc5db3c0d800b32ce0491e1e3647a7fd66964ce985fc` |

Focused CPU verification: `python -m unittest tests.test_e3_s1_portability`, 6/6 passed in 0.455 seconds; `git diff --check` passed. This checks metadata and bounded manifest logic, not native Linux execution.
