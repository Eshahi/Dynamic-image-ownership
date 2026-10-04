# Fixed real-model initialization audit runner

Version `m1-source-initialization-audit-v1`, preparation2026-10-04. This implements the mechanical R1/R2 stages in `m1-end-to-end-initialization-design.md`; it has not been executed on the real VAE. Parent must commit inputs and launch GPU stages sequentially as separately owned workers. Only the pinned FP32 VAE is loaded, with no pipeline, UNet, CLIP or LPIPS. No held-out access, gate authorization or paid work is provided by this runner.

`research/m1-source-initialization-audit-v1.json` freezes source1675, phase seed0,200 updates, interruption100, checkpoint interval10, existing deterministic execution policy,1800s outer/1750s cooperative cap,10GiB requested GPU allocation with512MiB free-memory reserve,16GiB sampled process working-set cap and500MiB artifact cap. Parent-owned process containment enforces the outer1800s timeout; this script only enforces its cooperative limit. Initial free headroom reduces the effective GPU allocation cap and is recorded. No silent CPU substitution, changed optimizer or warning-only deterministic fallback is permitted.

## Execution sequence

Each command is a new process under the parent's owned-worker containment. Use the bundled science Python. Output directories are new children of MAIN `.thesis-build/dev-runs`, never old runs. The script checks all executed source/config dependencies against committed HEAD before creating output. Report-only commits do not affect the scientific-core digest, which hashes the committed executable/config/cohort/asset-lock receipts.

1. `--stage literal --output-dir R1`: independently expressed original reconstruction equations for source1675 through200. The adapter's serialization helper is shared; its encode/observe/update functions are never called by the literal reference.
2. `--stage adapter-prefix --output-dir R2A`: fresh source encoding in another process through100; no R1 tensor is imported.
3. `--stage adapter-resume --prefix-dir R2A --output-dir R2B`: a third process restores the complete R2A step100 receipt and continues through200 without reseeding or re-encoding the source.
4. `--stage compare --reference-dir R1 --prefix-dir R2A --resume-dir R2B --output-dir COMPARISON`: CPU-only comparison of all21 matching10-step states, including mandatory0/50/100/200 observations. No tolerance is fitted. Exact posterior/latent/Adam/RNG/operator/source/runtime/observation fields must agree. Process IDs, elapsed time and serialization file bytes are excluded from scientific equality. Run dependencies must have three distinct process/run identities and the exact R2A receipt must be R2B's dependency.

The three GPU processes collectively perform400 source1675 initializer updates. They are one development source, not three independent images or seeds. Fresh phases seed Python, NumPy and Torch to0 after model loading and immediately before encoding. Resume restores the captured RNG after constructing Adam. All step receipts are after that step's observation, consistent with the new adapter schema; retained legacy receipts are never opened or overwritten. Metrics are evaluated from CPU observations after optimization, with no metric RNG consumption inside the trajectory.

Each GPU run retains the canonical source PNG, raw/canonical/model receipts, scientific hashes, policy/environment/GPU/driver receipts, all required full states, observation quality, checkpoint journal, duration and sampled resource measurements. Outcomes are `completed`, `operational_failed`, or `parity_failed`; no watermark scientific gate is computed. A failed required comparison cannot emit a bridge. Earlier valid receipts remain intact after a failure. Resume in this audit intentionally accepts only the planned completed100 prefix; arbitrary failed/timed-out-stage recovery is a separate worker integration requirement, although complete10-step states are retained for diagnosis.

## Bridge consumed by the end-to-end runner

The passing comparison emits `1675-step200.pt` with the existing loader's `{z,step:200,latent_units}` format, the final reconstruction PNG, and a development `cases` receipt compatible with `m1_dual_latent.reconstruction_latent`. This is a newly audited R2 endpoint, not imported legacy initialization. `u0_bridge` has schema `m1-verified-original200-u0-bridge-v1`, source ID, full initializer-state receipt, legacy-format latent/PNG receipts, initializer scientific-core digest and the explicit requirement to start a fresh independent embedding Adam. The PNG is an observation and must never be re-encoded to obtain `u0`.

After the audit passes, `--stage initialize --source-id 4795 --audit-dir COMPARISON --output-dir NEW_SOURCE` independently performs the same200-update adapter on an admitted development source and exports the same bridge. It requires exact audited scientific files, assets, numerical policy, environment/device/runtime before fitting. The12 allowed IDs come only from the existing reserved development manifest; no arbitrary source path or held-out ID is accepted. This mechanical command is not authority to expand the remaining ten before the end-to-end pilot gate. The parent enforces that scientific queue.

Public API:

```python
from m1_source_initialization_audit import load_development_bridge
u0, provenance = load_development_bridge(run_directory, source_id, source_rgb8_sha256)
```

The caller has already configured deterministic execution and initialized CUDA. The loader rejects an uninitialized CUDA runtime without initializing it. It rechecks all retained audit runs, every required state/dependency, current committed initializer files, current VAE asset bytes, exact runtime and source identity, full200 endpoint and bridge byte equality. All run/bridge dependencies are confined to MAIN development-run directories. It returns CPU FP32 unscaled `u0` and original loader provenance plus `initializer_kind`, `initializer_scientific_core_sha256`, `audit_proof`, `full_initializer_state` and `embedding_optimizer`. The embedding runner must separately pin its own core and use a new optimizer/phase seed; this API imports no initialization moments into embedding. `load_verified_u0(...,expected_core)` is an additional explicit-core compatibility guard.

The loader validates current initializer assets, while actual loaded-model identity remains the embedding runner's responsibility. Checkpoint digests/retained-run receipts detect accidental corruption and stale dependencies; they do not cryptographically authorize a hostile actor. No official held-out capability or scientific authorization is implied.

## CPU validation and outstanding real evidence

Six new CPU tests pass (5.891s) using the bundled science Python: literal/adapter disk-split equality across all21 states; missing/corrupt/dependent receipt rejection; strict tiny latent mismatch detection; process/environment mismatches; development-root/no-overwrite guards; and successful shape-valid synthetic bridge export/import followed by dependency corruption rejection. The successful bridge test uses fabricated shape-valid fixture receipts only to exercise serialization/import guards and explicitly mocks already-initialized CUDA runtime/model-asset checks. It supplies no real-model trajectory, GPU parity or scientific claim. The earlier nine tensor adapter tests remain separate.

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe' -m unittest discover -s tests -p test_m1_source_initialization_audit.py -v
```

Parent still must commit and execute R1/R2A/R2B/COMPARISON, inspect exact equality and resource receipts, then use the verified1675 bridge and fresh4795 bridge in the unchanged100-step embedding pilot. The scientific trigger, full end-to-end gate, later expansion and official containment/recovery rehearsals remain unmeasured. The runner cannot declare the candidate or held-out manifest ready.
