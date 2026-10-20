# Stage-1 progress and decisions

## 2026-10-19 — opened

The active goal is the complete, untimed stage-1 package in BRIEF.md section 1a. The authoritative MAIN STATE.md was read once, followed by the brief. Starting commit: `44c9ad9`; branch: `codex/encoder-transfer-20261019`. The worktree was clean.

No server connection, GPU computation, model/weight download, regeneration, detection, or scoring of a real mark is allowed in this stage. Only documentary research, source-identity/hash inspection, analytic design calculations and software unit tests are permitted. All experimental outcomes remain absent.

T1 attack standards, T2 encoder landscape, and T3 faithful baselines were delegated in parallel to fresh gpt-6-astra/high agents, each with its own output directory. The remaining five topics follow as slots become available. The primary agent integrates the research and implements the portable experiment code. Each finished topic will be committed and pushed separately with an agent-attributed commit and push-log entry.

The literature-synthesis and experiment-design skills provide evidence and preregistration checks. The explicit brief and autonomous development instructions govern the deliverable format and stage boundary; no approval JSON or additional execution infrastructure is being introduced.

Early code inspection confirms that historical endpoint C is `semantic.read and semantic.content_match`, while S also uses `found`. The new runner must call the historical predicate implementation and preserve all endpoints; it must not substitute a newly interpreted C. The frozen writer and detector have no registry-record lookup in this transfer test; their owner/profile/model side information will be stated separately from the registry study.

## 2026-10-19 — integrated review candidate

All eight research topic packages exist and were individually committed/pushed through eb517ed. T6 completed its files before an account usage-limit failure; T7 delivered synthesis and parent completed its evidence package; T8 was completed by the parent after the assigned agent failed. This provenance is explicit and is not an independent-review claim.

The integrated research, protocol, machine configuration, source roster, asset plan, implementation and costed proposals are now written as a review candidate. Retain n60, F5/v5/WAM/VINE-R, R0/R1 .1/.2/.4, D1 and one/two resize controls; add one SDXL .1+.1 rinse. FLUX is excluded because official access is gated. Full schedule is7500 C0-inclusive units, smoke250. Correct topic-local estimates that omitted C0: the integrated budget is10–14 instance-hours under the unchanged15h/$15 cap, contingent on actual timing. Proposals P1–P8 remain excluded and unapproved.

The official SDXL pipeline's partial VAE downcast is overridden so the complete official VAE runs in fp32 for encode/decode. WAM/VINE preprocessing and quantization are preserved natively; side information, structured q/H payloads and native/common thresholds are documented. Negative gate uses historical A, primary positive uses literal C. Three primary paired tests use Holm; no secondary tests. Fixed quality matching is blind to detection labels.

Nineteen CPU-only fake-fixture tests passed in5.033s after adding effective-config validation and complete-smoke inventory checks. No real image/mark was scored. The earlier test process handle disappeared during tool interruption; this successful rerun is the current evidence. Initial reviewer initialization also disappeared with no live agent/file; one fresh Astra/xhigh independent review was dispatched again. Its actual verdict and corrections remain required before frozen status and the stage1 stop. MAIN STATE was updated; no server should be rented yet.

## 2026-10-20 UTC — independent review closed and package frozen

The single fresh Astra/xhigh reviewer accepted the bounded development study with warnings and no open blockers. Three findings were corrected: persisted readouts survive interrupted quality work, wholly unavailable comparisons retain Holm slots without invented p-values, and nonfinite model outputs are rejected before quantization. Per-phase allocated CUDA memory receipts, external native/common/exact source summaries and rinse incremental distortion complete the reporting contract. No scientific setting or arm changed during these fixes.

The author ran the CPU suite with the MAIN a6-science-venv Python: `-m unittest discover -s tests -p test_encoder_transfer_test.py -v`; 24 tests passed in 2.995s, exit 0. The independent reviewer reran all 24 in 2.875s. Author log: MAIN `.thesis-build/q1-research-20261018/cache/transfer-integration/stage1-tests.log`. These are fake fixtures and CPU tensors only; native model loading, server compatibility and throughput remain untested.

The eight topic folders, bibliography/card index and 292 documentary-cache receipts are retained. Package metadata verifies published pins and direct dependency compatibility for Linux x86_64 Python3.11, not a complete installation. The protocol/configuration are now frozen; P1–P8 remain unapproved and excluded. Commit and remote verification follow before the final stage-1 stop. No server, GPU science, weights, real-mark scoring, new outcome or held-out pixels were accessed.

Release preflight found CRLF/LF hash drift between Windows files and the Git index. The source and asset manifests were normalized to the repository's existing LF policy; only byte-format hashes changed, not JSON content. Source SHA is490d3d04efcf6e02a61eeadeacb7494313d2a5607b84fd57a7a2c0e6faea8b72 and asset-plan SHA is e7e742094fa1da7d0536f2f25820b963ce1d14ceb8a9a201687b9ec03ac3df0d. Writers now specify LF. The final suite has25 CPU tests, all passing in3.004s; the same independent reviewer verified this correction and independently reran all25 tests in3.021s, retaining the acceptance verdict in the existing review. Log: MAIN cache/transfer-integration/stage1-tests-final.log.
