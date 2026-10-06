# Codex takeover of the Vast M1b development smoke

Started 2026-10-06 11:42 UTC. Branch `codex/f5-m1b-vast-recovery` from Claude's `471b7c5`. The authenticated user asked Codex to continue Claude's GPU work and inspect its documentation. This is authorization to repair and resume the already queued two-development-source smoke on the existing rented instance; no new rental, changed scientific candidate, or held-out execution is inferred.

## Discovered state

- Existing SSH identity `~/.ssh/vast_ed25519` authenticates successfully; no new credential is needed. Do not copy its private contents into artifacts.
- Live instance ID `54451380`, label `C.54451380`, GPU RTX PRO 4000 Blackwell, 24,467 MiB. This differs from the historical stopped instance `54395023` in STATE. Use the live identity for any management decision.
- Existing environment `/workspace/thesis/venv` has torch `2.12.1+cu130`; a CUDA tensor operation succeeds. SD1.5, CLIP and AlexNet assets are already present; no download/install is needed.
- Claude's smoke `/workspace/thesis/m1b-smoke` finished in 13.279 seconds: zero completed rows, 14 failed/dependency rows. Both embedding attempts failed on nonexistent `three_threat_models.clip_feature_wrapper`. The old top-level `completed` state described control flow, not successful scientific execution.

## Recovery scope declared before outcomes

Run `research/m1b-vast-development-smoke.json` with runner v3 at a clean committed code snapshot. Use only dev-1675 and dev-4795, the original fixed owners, frozen F5 r2 config/profile, T3 strengths .05/.1/.2/.4 and seeds 0/1/2 plus VAE, the original residual-transfer smoke and cross-owner pair. Expected inventory: 100 rows (2 embeddings, 8 clean calls, 78 T3 calls, 8 T4 calls, 4 T5 calls). Keep failures/adverse missingness and original seed identities. This smoke's residual transfer is exploratory and does not replace the frozen confirmatory patch protocol.

Bound the process with GNU `timeout` at 1800 seconds, TERM followed by KILL after 30 seconds. Run as a finite supervisor job with no automatic restart, so loss of the SSH client does not terminate the job or launch another attempt. Preserve the original failed smoke in place and collect both histories locally. Do not recycle or destroy the instance. A separate copied-output partial-resume rehearsal may remove one existing T3 record from the copy and fill that exact record, retaining the intact source run; give that probe a 300-second timeout. Stay with the active job until it finishes.

Deployment uses an archive of reviewed scripts/configs/tests/profile and the development manifest only, committed as a clean remote snapshot. Record both the local source commit and the remote snapshot commit plus the archive hash; the remote snapshot is not mislabelled as the full local repository. No proposal, protected source plan, credentials or held-out pixels are transferred.

## Repair and verification

V3 shares the actual frozen `f5_gate.semantic_feature` function, invokes the normative four-argument residual helper, declares all planned endpoint IDs before failures, separates C0/C1 negative cells, reports incomplete inventory honestly with a nonzero CLI status, reloads saved source/mark on resume without skipping pending attacks, rejects changed resume context, checks saved RGB hashes, and uses Windows-compatible PNG names. Clean PSNR/SSIM/LPIPS are measured on saved RGB. Threat intervals are explicitly development row summaries without independent-source verdicts. Only development manifests are accepted while the held-out protocol gaps remain.

Before launch, 29 CPU unit tests pass. A fresh independent reviewer inspected the recovery diff and identified no blocker for this single-shard development smoke; its held-out blockers are in `m1b-vast-independent-review.md`.

## Next gate

No held-out execution is authorized by this takeover. The narrow COCO512 cohort choice is recorded by Claude, but the exact confirmatory execution package is still absent. Align patch attacks, v5 comparator, matched C0 reconstruction, complete quality, cluster summaries and pair-safe shards before presenting an exact package for the user's one M1b decision. Never label a successful two-image smoke as completion of M1b/M2.
