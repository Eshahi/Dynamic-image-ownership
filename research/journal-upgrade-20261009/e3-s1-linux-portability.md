# E3-S1 Linux portability amendment

2026-10-11. Codex agent. Bounded deployment amendment to scientific commit cb550673e1740705c932203f03c5ae8e78e21a98. No method, model revision/hash, owner, threshold, cohort eligibility, seed, attack schedule, endpoint, statistical test or scientific-failure rule changes. This document is not execution approval or a lifecycle verdict.

## Changed files and contract

- `scripts/thesis_deployment_paths.py` is a small code-bound Windows/Linux path map, imported by the existing worker and scientific import closure. It has no environment or caller overrides. Unsupported platforms refuse.
- `scripts/f4_transfer_probe.py` and `scripts/journal_vae_probe.py` use the mapped A6 and SDXL paths. Their scientific operations are unchanged.
- `scripts/m1b_coco512_worker.py` imports the official runtime path and protects both historical Windows and actual Linux held-out roots for non-test plans. Official `thesis_agents/compute.py` SHA-256 stays `4b98e5429d57bda48dbe7b239602b1c7ef60c7cbb19058e17136b29a09437d30`; approval checks and dispatcher stay intact.
- `scripts/m1b_e3_s1_runtime.py` binds the Linux test index to its exact path/hash while retaining the Windows contract. It also requires the verified SDXL lock root to equal the loader root. All previous file hashes, sizes, dtype/revision, source identity and schedule checks remain.
- `research/journal-upgrade-20261009/e3-s1-linux-external-index.json` copies the frozen index with only each `external_raw_path` translated. UID, group, raw hash, entry order, owners and every other value are identical. The copied `raw_path_exists` fields are historical metadata, not a remote existence check. The worker still checks actual raw presence/hash after approval.
- `scripts/m1b_prepare_package.py` accepts bounded paid-budget CLI fields without changing the dispatcher or approval checker.
- `tests/test_e3_s1_portability.py` verifies the path map, exact path-only metadata translation, frozen schedule, source identity preservation, platform-specific index refusal/acceptance, non-test boundaries and code closure.
- Parent-provided escalation line in `experiments/dev-log.md` is included; this agent did not edit shared STATE or append its own shared log entry.

| Binding | Linux value |
| --- | --- |
| Checkout / MAIN | `/workspace/thesis/repo` |
| A6 assets / plan.assets_root | `/workspace/thesis-assets/a6` |
| SDXL VAE / sdxl_lock.root | `/workspace/thesis-assets/journal-sdxl-vae-6f5909a7` |
| Existing official scripts | `/workspace/thesis-runtime/scripts` |
| Imported official runtime | `/workspace/thesis-runtime/scripts/_runtime` |
| Held-out boundary including annotations | `/workspace/thesis-data/coco2017` |
| Source JPEG directory | `/workspace/thesis-data/coco2017/val2017` |
| Test sources.index.path | `research/journal-upgrade-20261009/e3-s1-linux-external-index.json` |
| Test sources.index.sha256 | `091bad0fae4092ed8332ca64e44873cafcabd88ebfa8636957d5104be7a80a0f` |

The schedule remains `research/journal-upgrade-20261009/e3-s1-schedule.json`, SHA-256 `fada9a67f066f2dc4bde5931d46911eb11bb10cb6e6bebcaa7abf33192cac9d0`. The original Windows plan/index remain unchanged. Keep the Linux source index tracked under the exact relative path above; deployment plans, locks, approval and output bookkeeping may use `/workspace/thesis/ops` as bound by the parent.

## Validation and limits

Six new CPU metadata/manifest-budget tests pass, including validation of both 300-source contracts without opening raw files or annotations. Existing regression suite plus the first four portability tests: 65/65 pass in 263.060 seconds. Final focused portability/budget suite: 6/6 pass in 0.460 seconds (67 unique CPU tests in total). Commands used the authoritative MAIN `.thesis-build/a6-science-venv/Scripts/python.exe` with `-m unittest tests.test_e3_s1_portability tests.test_m1b_coco512_worker tests.test_m1b_e3_s1_worker tests.test_m1b_e3_s1_analysis tests.test_m1b_e3_s1_budget tests.test_m1b_e3_s1_main`, then the final focused module after adding the contract/budget cases. `git diff --check` passes. No Linux process, GPU, model loader, scientific pilot, failure rehearsal, raw preflight, installation, download, SSH or paid action was run by this agent. Remote pilots/rehearsals are explicitly waived by the user and must be reported as skipped, not passed. Existing local rehearsal evidence and completed failures remain untouched. Windows CPU checks with mocked platform selection do not establish native Linux integration behavior.

## Exact remaining deployment inputs

The parent must bind the actual Linux plan, environment lock (platform `linux`, Python 3.12.14 and every inspected package version), SDXL root lock, annotation path, actual interpreter, commit, inputs and remote scientific-core/manifest hashes. Preserve locked model hashes/revisions and fixed index/schedule identities. Official runtime must be copied intact and pass its unchanged compute hash. Check metadata/assets statically without held-out pixel/annotation access until the actual approval contract permits it.

The existing prepare script now accepts `--hourly-usd` and `--max-usd`, retaining zero defaults. Use `--hourly-usd 0.4037037037037037 --max-usd 7.50` for this deployment; both fields flow into the manifest and its displayed approval template. Nonfinite, negative, one-sided paid fields and per-attempt costs above the cap refuse. This template remains a template, never an approval. Provider elapsed-time billing and the aggregate rental cap still require the parent's external supervision; the per-attempt check is not a provider billing guarantee. Do not represent USD 0 as remote paid accounting. Parent binds instance 55389808, inspected hourly price and USD 7.50 cap, absolute ops approval/output paths, and retained continuation limits. No new approval, manifest, package versions or cost contract is fabricated here. Final remote code/core honestly differs from the local frozen core; synthetic local journals cannot become same-core remote continuation.
