# Worker report — m1b (2026-10-05)

Role: m1b — confirmatory runner + cohort memo. Headless worker on Claude Opus 5. No human in loop. Worktree `C:/Users/Soroush/.codex/worktrees/claude-f5-m1b`, branch `claude/f5-m1b` from `0cfb528`. Time budget wrap 00:05 UTC, end 00:30 UTC.

## What was done

### 1. Runner `scripts/m1b_f5_runner.py` (candidate-agnostic, no new broker/launcher/audit layers)

- **Manifest validation** (pure, CPU): schema `m1b-f5-manifest-v1` / version `m1b-f5-runner-v1`, `config_path`/`profile_path` nonempty, `sources[]` nonempty unique `id` (regex `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`), `owner` nonempty, `wrong_owner` must differ, optional `t4_pairs`/`t5_pairs` unique ids and required fields, `t3_strengths`/`t3_seeds` no duplicates. Rejects duplicates/extra — reused pattern from `m1_confirmatory_endpoints` error handling.

- **Sharding**: `shard_sources` — sort by `id`, round-robin by index modulo `shard_count`. Deterministic, no overlap, covers all sources. Validates `shard_index` range.

- **Journal/resume**: append-only `journal.jsonl` (`append_journal` / `read_journal`). On `resume=True`, completed row `id`s are skipped per source and per T3/T4/T5 row. Truncated last line surfaces as exception (corruption not silently ignored). Never drops failed rows — failures journaled with `outcome` in `failed`/`missing_dependency`/`safety_blocked`.

- **Never substitutes seeds**: `t3_strengths`/`t3_seeds` are exact manifest lists; absent keys fall back to frozen defaults `T3_STRENGTHS=(.05,.1,.2,.4)` / `T3_SEEDS=(0,1,2)` at run time without mutating the manifest. Validation rejects duplicate strength/seed entries.

- **Embedding**: loads `configs/f5-r2.json` (`f5-r2-frozen-v1`) and `experiments/c4-v5-two-tier-regeneration-v1/profile.json`; checks `git status --porcelain` clean on `f5_latent_codec.py` + runner before any GPU work. Creates `f5.Reader` (pinned SD1.5 VAE fp32) and embed via `f5.embed_rgb` with frozen kwargs: `psnr_db 52`, `steps 150`, `target_margin 4.0`, `band (4,32)`, `whitening 1.0`, `refine_rounds 1`, `binding soft`, `semantic_views 7` (from config). Computes CLIP feature as 7-view mean (same as `f5_gate.semantic_feature`), verifies `both_match` on saved PNG.

- **T3 grid**: per source, two arms `C0` (source) and `C1` (marked). Attacks per arm: VAE posterior-mode roundtrip + `strengths x seeds` SD1.5 DDIM img2img (20 steps, CFG 1, eta 0, empty prompt, same semantics as `f5_gate`). Each attack saved as PNG, re-read, then blind `f5.detect_rgb` for correct owner and wrong owner (C1 only; C0 already has clean wrong-owner control). Safety-checker blocks journaled as `safety_blocked`. Never invents a new seed on retry.

- **T4 residual-transfer**: `three_threat_protocol.residual_transfer` at scales `.5` and `1` (donor `C1-C0` residual onto recipient `C0`), plus sham `donor_C0_sham`. For each scale/arm, two claimed roles (`donor_claim` / `recipient_claim`). Cross-shard pairs journaled as `missing_dependency` rather than substituting a pair.

- **T5 pairs**: each pair `a`/`b` queried as `C0` and `C1` against the other endpoint's enrolled owner (`cross_owner`). Up to 120 calls per method (4 per pair). Missing shard sources -> `missing_dependency`.

- **Receipts + run.json + endpoints**: every image gets `{path, sha256, width, height}`; `run.json` records manifest/profile/config SHAs, detector_config_id, shard, `journal_rows`/`completed`/`failed`, duration, outcome, and **per-cell** Clopper-Pearson one-sided 95% + Wilson endpoints via `scripts/m1_confirmatory_endpoints.cell` (candidate-independent). Cells: `clean_C1_correct_both_match` (positive), `clean_wrong_owner_both_match` (negative), `t3_C1_diffusion_{s}_correct` (positive), `t3_C0_correct_both_match` (negative), `t4_donor_claim_both_match` (negative), `t5_cross_owner_both_match` (negative). Missing/failed counts as adverse (`None` in that helper). Shard-local; final aggregation merges journals across shards externally.

### 2. Tests `tests/test_m1b_f5_runner.py` (CPU only, no GPU/images for most)

20 tests, 4 classes, all pass on `.thesis-build/venv` (stdlib):

- `TestValidateManifest` (10): valid minimal, empty sources, duplicate id, bad schema, wrong_owner==owner, duplicate t4 id, missing donor, duplicate strengths, t5 optional, extra-id handling.
- `TestSharding` (4): deterministic sorted, no overlap + cover, bad index, single shard.
- `TestJournalResume` (4): read empty, append+read, truncated last line raises, resume skips completed (coarse probe-id check).
- `TestNeverSubstituteSeeds` (2): manifest strengths/seeds exact, duplicate seeds rejected.

### 3. End-to-end rehearsal on two development images (never held-out)

Sources: canonical dev cleans from `scripts/f4_transfer_probe.py:SOURCES` — `dev-1675` and `dev-4795` (`W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261004-1102-e2e-1675/1675-C0-clean.png` and `20261004-1122-e2e-4795/4795-C0-clean.png`). Never held-out.

- **CPU parts run here**: manifest validation (`research/m1b-rehearse-two/manifest.dev-two.json`, sha `7bc9dc2…`), sharding into 2 shards, journal append/read + truncated-journal corruption surfacing, no-seed-substitution invariant. Report at `research/m1b-rehearse-two/report.json`. Held-out not touched.
- **Endpoints verified** in science venv: `bounds(0,300)` upper `0.009936…`, `bounds(1,300)` upper `0.0157…` — matches `research/m1-confirmatory-endpoints.md`.
- **GPU part** (short, development only) requested in `research/f5-gpu-queue-requests.md` for the GPU lead: exact command, selection rule, frozen `configs/f5-r2.json` through `scripts/f5_latent_codec.py` on the same two dev images, verifies `both_match` self-verification. No held-out manifest queued. Output expected in `research/m1b-rehearse-two/gpu-smoke.log` after GPU lead runs it.

### 4. Cohort memo `research/m1b-cohort-decision.md`

One-page decision memo, no choice made. Compares:

- **Narrow COCO512** — 300 COCO test group representatives (metadata-only freeze, `m1-coco512-confirm-v1` tag) + T3/T4/T5 30-unit descriptive slices, same thresholds (decoded 8.259…, recomputed 4.982…, FPR 1e-6, roster 1), 1200 clean calls + 1170 T3 calls per method. Wilson/zero-FP table: 30->9.5% upper bound (descriptive), 300->0.994% (needs 0/300; 1 FP ->1.57%), 600->0.498%. Thesis sentence supported is single-domain only; native-2K / cross-model generalization not claimed.
- **All-domain** (`research/sample-size.md`) — 3,900 locked-test groups (600 COCO + 300 DIV2K + 3,000 DiffusionDB), per-domain 300-block T1 benign profile, T3/T4/T5 protocols still `BLOCKED_PROTOCOL`. Tighter bounds on large DiffusionDB (3,000->0.100%), but requires clearing `BLOCKED_DATA/PROTOCOL/RESOURCE`, pinning releases/licenses/grouping/rights/hashes, freezing T2–T6 severity/admissibility/pairing/comparator/margins, and handling DiffusionDB group shortfall and storage (1.6 TB PNG subset / 6.5 TB Large). Cost ~13x clean units; runtime worksheet still pending p95 receipts.

Prerequisites for either: M1 side-information acceptance (pinned SD1.5 VAE encoder + 7 CLIP passes), independent M1 review passes, synthetic rehearsals pass, user approves exact manifest, official runner single held-out run.

Reports, specs and manifests own no change to protected proposal/source plan/claims.csv/THESIS_GUIDE_OFFLINE.html.

## Numbers

- Tests: 20/20 pass (m1b runner).
- Endpoints boundary identities: 0/300 upper 0.009936..., 1/300 upper 0.0157... (verified).
- Rehearsal: 2 development sources, manifest valid, 2 shards deterministic, journal resume works, truncated journal raises.
- GPU smoke: pending GPU lead execution (development only).

## What is verified / what is open

- Verified (CPU): manifest validation, sharding, resume, no seed substitution, truncated-journal surfacing, endpoint helpers on synthetic counts, rehearsal manifest integrity.
- Open: GPU smoke output (needs GPU lead), full 300-source held-out run (needs user approval — not queued here), runtime p95 worksheet for shard sizing, and the user's cohort choice (memo makes no choice).

## Recommended next step

1. GPU lead runs the queued smoke (two dev images, frozen 52 dB soft 7-view) and appends receipt to `research/m1b-rehearse-two/gpu-smoke.log`.
2. User reviews `research/m1b-cohort-decision.md` and decides narrow COCO512 amendment vs all-domain plan.
3. On approval, freeze the exact held-out manifest + schedule (600→300 ranking, 30-unit T3/T4/T5 slices) and run the official runner shards; aggregate journals for per-cell endpoints — no seed substitution.

## Branch / commits

- Branch: `claude/f5-m1b` from `0cfb528`.
- This push: `scripts/m1b_f5_runner.py`, `tests/test_m1b_f5_runner.py`, `research/m1b-cohort-decision.md`, `research/m1b-runner-progress.md`, `research/f5-gpu-queue-requests.md`, `research/m1b-rehearse-two/*`, this report.

## Progress file & pushes

- `research/m1b-runner-progress.md` updated ~20:52, 21:30, 22:05, 22:10 UTC.
- Push log: branch `claude/f5-m1b` pushed at ~22:30 UTC (commit range `0cfb528..HEAD`), author `Claude Code agent (Opus 5 worker)`, trailer `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
