# Autoresearch applicability assessment

Date: 2026-10-09. Scope: read-only planning assessment; no new experiment, installation, repository execution, or method amendment. Recommendation: borrow a small manual research-loop discipline, without adopting the package or building another runner.

## Inspected primary source

The official repository was resolved through the GitHub API to commit `228791fb499afffb54b46200aca536f79142f117`. README, program, preparation and training code, dependency declaration, Python version, and relevant lockfile entries were inspected. Exact file bytes and API metadata are retained in `autoresearch-source/`; `source-manifest.json` gives source URLs, revision, byte counts and SHA-256 values. The README declares MIT. The pinned root has no dedicated LICENSE file and GitHub's license metadata is null: a full license instrument was not available for inspection. This assessment does not reuse its code.

## What the repository actually does

Autoresearch is a compact agent-directed search over single-GPU GPT pretraining derived from nanochat, rather than a generic scientific discovery platform. The agent changes one training file; preparation and evaluation remain fixed. Its scalar target is lower validation bits per byte (`val_bpb`), and the README describes a nominal five-minute training budget on an NVIDIA GPU, tested on H100. It does not supply a watermark, threat model, cryptographic binding mechanism, independent replication protocol, or thesis claim audit. [Pinned README](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/README.md).

The program asks for a baseline, committed candidate edits, redirected logs, and a keep/discard/crash table. It treats memory as a soft constraint, keeps scalar improvements, resets to the previous commit for equal/worse results, and continues until interrupted; a run exceeding ten minutes is failed. Those are experiment instructions to an external agent, not a packaged scheduler or proof that evaluation cannot be manipulated. Its permission and indefinite-continuation advice is not authority for this project. [Pinned program](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md).

Preparation uses a fixed last validation shard of climbmix, an 8,192-entry BPE tokenizer, 2,048-token contexts, and approximately 21 million evaluation tokens. Its BPB calculation accumulates target cross entropy and target byte counts, excluding zero-byte special tokens. A fixed evaluator is useful, but repeatedly consulting its output makes that shard adaptive development feedback. It is not an untouched final test. [Pinned preparation/evaluator](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/prepare.py).

Training uses seed 42, bf16 CUDA, compiled model and optimizer operations, and dynamically selected Flash Attention kernels. The budget accumulates synchronized step durations only after steps 0–10; it ends at a step boundary after reaching 300 seconds. Setup, the initial steps, and final evaluation contribute to total elapsed time outside that counter. Thus five minutes is not an exact end-to-end cost cap or an equal-FLOP comparison. No repeated-seed aggregation or selection-adjusted uncertainty is built into the inspected script. [Pinned training code](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/train.py).

## Thesis fit and incompatibilities

The authoritative STATE, read once for this task, says F5 r2 is frozen and M2 scientific review accepted with corrections; no new experiment is scheduled. It records development T3 successes of 29/28 versus v5's 27/18 and an already completed confirmatory package with known quality and attribution limits. Autoresearch must not silently revise that historical freeze, optimize the observed held-out results, or relabel v5 as the proposal's latent method. F5 uses VAE-guided pixel optimization and latent extraction; it is not an initial-noise generative watermark. Any future extension would be a separately scoped study, not a silent repair of reported M2 science.

| Reusable discipline | Thesis-specific adaptation |
| --- | --- |
| One small editable candidate surface | Specify method/config files allowed to change; retain an interpretable scientific hypothesis, not arbitrary edits throughout the system. |
| Baseline before search | Use the declared comparator and matched identities; avoid new baseline runs unless necessary for the authorized study. |
| Short decisive evaluation | Choose the smallest complete development threat grid that can falsify the hypothesis; do not substitute a truncated grid for a gate. |
| Commit before executing | Existing development `run.json` and `experiments/dev-log.md` already supply this; add no parallel receipt system. |
| Explicit keep/discard/crash decision | Preserve every candidate commit, log, outcome and failed seed; label rejected candidates without deleting scientific evidence. |
| Fixed evaluator | Freeze assessor code, thresholds, negative calls, source-selection rule and threat identities; never let search edit them. |

The thesis is a constrained vector-valued problem. Better T3 survival cannot compensate for false owner detections, degraded clean quality, T4/T5 regression, or a heavier detector that violates its declared resource contract. First filter by all hard constraints; then retain the Pareto set for detection at each strength, image quality, extraction cost and complexity. Where tradeoffs remain, describe them explicitly. A weighted scalar score would conceal a violated gate.

For historical continuity, the completed M1a gate was: improvements at both .1 and .2 on the twelve development sources with matched DDIM seeds 0–2; all-source PSNR >35 dB, SSIM >.9, LPIPS <.1; clean both_match on at least 11; zero C0 and wrong-owner detections; no T4/T5 regression. Use the existing terminal and dual-threat assessors and declared comparator results for continuity checks. The new journal roadmap adds stronger cross-model and checked-detection targets; it does not retrospectively change M1a.

## Adaptive search and uncertainty

The following are statistical deductions and recommendations, not claims demonstrated by the autoresearch repository. Selecting the best noisy result among many trials inflates the apparent gain: the winner benefits from favorable noise and repeated feedback. Even if all candidates have identical true performance, independent noise with standard deviation sigma gives a rough maximum scale of sigma times sqrt(2 log K) over K trials under Gaussian assumptions. Trials in this project are correlated, so that expression is an intuition rather than a correction formula or confidence interval.

Count candidate queries, threshold queries, subset checks, failed runs and repairs that expose performance. Reusing one seed controls some comparison noise but says little about robustness across seeds. Before any future authorized search, declare a finite candidate-query budget and a fixed complete matched seed panel, record paired source-level outcomes, and reserve a separate development-only replication panel for the few surviving hypotheses. Repeated seeds on the same source are clustered observations, not extra independent images. A tiny improvement is not decisive if source/seed variability covers it. Include every attempted seed in analysis; retry technical failures transparently without dropping hard cases. New query budgets and independent panels need a study plan before any outcome is seen.

Held-out confirmation is a final evaluation of a frozen candidate, not an input to the optimization loop. Current M2 data have already been inspected and cannot become fresh held-out confirmation for an amended F5. Do not tune evaluators, detector thresholds, exclusions, attacks or source selection to improve known results. Development performance and exploratory selection remain labelled as such; zero observed negatives alone is not a proof of negligible population false-positive probability.

## Resources and Windows

The dependency declaration pins torch 2.9.1 to the CUDA 12.8 index and lists kernels, numpy, pandas, matplotlib, pyarrow, requests, rustbpe and tiktoken; the lock resolves kernels 0.12.1. It is a separate language-training stack, not a useful dependency bundle for the existing diffusion environment. [Pinned dependency declaration](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/pyproject.toml), [pinned lockfile](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/uv.lock).

Windows execution was not tested. The lock includes Windows torch wheels but marks Triton as Linux-only; the source invokes compiled CUDA paths and fetched attention kernels. A Windows fork link in the README is not evidence that the official implementation runs unchanged here. Shell examples also assume tools such as sh/grep/tail. No fork, installer, binary, kernel, weights or dataset was downloaded, and no portability work is necessary for borrowing the workflow.

For a future local development study under the standing handoff, state caps before starting: one already available local GPU, USD 0, a fixed candidate/seed query budget, peak VRAM ceiling, total GPU time, end-to-end wall time including setup/evaluation/retries, and an agent token budget. Numerical ceilings should be chosen from the existing local grid's measured duration and resources, not H100 throughput or the README's approximate twelve experiments/hour. Stop at the first exhausted cap and report the frontier reached. Log hardware/model revisions and total cost; do not silently rent compute, call a paid API, install the LLM-training stack, or run indefinitely. A cutoff during a complete grid produces an incomplete exploratory run, not a passing candidate.

## Minimal proposed adaptation

For the next development extension under the standing handoff, use an ordinary short hypothesis entry in existing documents: mechanism, why it might survive T3, predicted observation, failure criterion, allowed code changes, fixed source/seed identities, query budget and resource caps. Commit the bounded implementation; execute through the existing local development command; retain `run.json`, logs and failed results; read the existing assessors; write one evidence-based keep/reject/uncertain decision. Advance only a feasible Pareto candidate to independent development replication and then the required freeze/review/approval process. No new launcher, broker, reset loop, scheduler, confirmation manifest or audit infrastructure is proposed here.

For the current journal-upgrade planning task, the deliverable is this assessment and inspected source archive only. The useful contribution of autoresearch is disciplined bounded iteration; it supplies no new watermark evidence. Local development authorization comes from the standing user handoff; fresh confirmatory or paid work retains the project's review boundaries.
