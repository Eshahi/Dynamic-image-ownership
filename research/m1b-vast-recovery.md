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

## Completed GPU execution (2026-10-06)

Source code commit `acda5e1de03aeaad4b8305b81fb8156bf0573689`; reviewed-code-subset remote snapshot `5390166831e2ceb333604f4d67206f67a2c0128c`. Deployment archive SHA-256 `e4124032c68e9ba9ed6b74bbd4ee89eb294d94523b58f251d0a0f880b930a0e1`. The deployment file links the two identities explicitly. The frozen codec, profile and F5 r2 configuration were not changed.

`/workspace/thesis/codex-m1b-smoke-acda5e1` completed in **241.543926 seconds**, CLI exit 0. Inventory reconciles **100 planned, 100 completed, 0 failed, 0 missing**: 2 embeddings, 8 clean, 78 T3, 8 exploratory T4 and 4 T5 calls. There are no substituted seeds or dropped safety failures. Both clean marked images self-verify as `both_match`; all six clean C0/wrong-owner negative queries have neither channel found.

| Source | Clean PSNR (dB) | SSIM | LPIPS | Embedding seconds |
| --- | ---: | ---: | ---: | ---: |
| dev-1675 | 44.797100 | 0.982493 | 0.020604 | 27.733070 |
| dev-4795 | 45.004160 | 0.989512 | 0.007950 | 26.097570 |

| T3 marked correct-owner arm | Semantic success | Read-and-compared | Recomputed-only |
| --- | ---: | ---: | ---: |
| VAE mode | 2/2 | 2/2 | 0/2 |
| Diffusion .05, seeds 0/1/2 | 6/6 | 6/6 | 0/6 |
| Diffusion .1, seeds 0/1/2 | 6/6 | 6/6 | 0/6 |
| Diffusion .2, seeds 0/1/2 | 6/6 | 6/6 | 0/6 |
| Diffusion .4, seeds 0/1/2 | 6/6 | 6/6 | 0/6 |

These are repeated-condition counts from **two development sources**, not independent-source population estimates. The exploratory T4 donor-claim arm has 0/4 semantic matches and 0/4 full attribution, but **1/4 any-channel detections**; retain this adverse event rather than describing all threat negatives as zero. Cross-owner T5 has 0/4 any-channel detections. Full confirmatory patch/delivery and quality rules are not implemented by this residual smoke.

The copied-output partial-resume rehearsal at `/workspace/thesis/codex-m1b-resume-acda5e1` removed exactly `dev-1675:t3:C1:diffusion:0.1:0:wrong_owner`, leaving 99 journal rows. It finished in **15.746789 seconds**, exit 0, restoring 100 unique completed IDs. All retained rows, both embedding records and the original source journal are unchanged. The restored attack's RGB hash matches the original. The two F5 embeddings were not repeated. This verifies one concrete pending-attack path; it does not establish truncated-journal recovery or a cooperative confirmatory shard guard.

The independent review preceded the final five additional inventory/manifest/filename tests. The final save/quality-failure path now emits the planned embed ID (not an out-of-inventory `embed:save` ID). The real partial-resume probe addresses the review's absence-of-execution-test observation. Its remaining held-out blockers still apply.

## Evidence collection and shutdown

The authenticated user explicitly requested stopping the current instance **after saving results**. The evidence bundle contains the untouched historical failure, both recovery histories and images, journals, run contexts, logs, manifest and deployment archive. Expected bundle: 85,226,746 bytes, SHA-256 `d4a691bd20d2df2dd3c7a76a3d49a1b9e9df353ac33bca55f63ad0e853b14964`, 204 file entries in its collection manifest. Local location: `.thesis-build/vast-recovery/codex-m1b-recovery-evidence.tar.gz`; extracted location `.thesis-build/vast-recovery/collected/`. These large development artifacts are retained locally, not committed to Git.

Local verification completed: all **204 files** match their collection-manifest size/SHA-256 and **196 RGB receipts** across both journals match their saved pixels. All **26** paired T3 C1 correct/wrong-owner outputs also have identical RGB hashes. Machine-readable counts and provenance are committed in `m1b-vast-smoke-result.json`.

At **12:02:01 UTC**, the authenticated management API acknowledged `state=stopped` for **54451380**, and the remote SSH connection immediately closed. Both finite supervisor programs were already EXITED. The stop preserves instance storage; no destroy/recycle was requested. The per-container API credential worked from the instance but returned HTTP 401 from the laptop, so shutdown was issued inside the instance. No private key/API secret was written into research artifacts. Local management receipts are under `.thesis-build/vast-recovery/`.

**Verification limit:** the process was terminated by the shutdown before it could read a final `actual_status=stopped` response. A separate read-only browser check was automatically rejected because Computer Use could not confidently determine the current Windows browser URL; no further UI input was issued. The stop acknowledgment and connection closure are observed, but final console state is not independently verified.

The finite supervisor jobs have `autostart=false`, `autorestart=false`; starting the server later does not automatically repeat the experiment.

For another identical technical replay after explicitly restarting that instance, keep remote snapshot `5390166` and the same manifest/config/profile. Use the existing `scripts/m1b_f5_runner.py` command from `run-smoke.sh` with a **fresh output directory**, or `--resume` only with that directory's unchanged run context. Changing the scientific candidate or execution package requires a new declared run. Do not extend this command to held-out inputs.
