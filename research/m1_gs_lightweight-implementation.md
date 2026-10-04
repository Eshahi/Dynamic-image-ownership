# B-LW1 implementation receipt

`scripts/m1_gs_lightweight.py` implements the frozen [terminal-sign design](m1-initial-noise-lightweight-diagnostic.md) in a separate read-only assessor. `research/m1_gs_lightweight-dev.json` freezes its configuration and the generating script/manifest SHA-256 values. Native GS generation, attacks, inversion and scientific behavior remain unchanged. This is an exploratory initial-noise carrier diagnostic, not a dual-key signature, three-state classifier or complete proposal family.

## Boundary and numerical fidelity

The assessor imports only native scalar/array/receipt helpers; it never calls native generation or inversion. Only AutoencoderKL weights are loaded. The image processor is instantiated exactly as the installed StableDiffusionPipeline constructor does: VaeImageProcessor with scale factor derived from the VAE channel blocks. A CPU fixture constructs the actual native pipeline with all model components absent and verifies equal processor configurations and identical preprocessed procedural RGB512 tensors. No hand-written normalization or alternate resize is added.

The saved RGB8 image is encoded once with frozen fp16 posterior mode. Multiplication by the pinned .18215 scaling factor happens in fp16 before a float32 CPU copy. Channel/row/column signs, whitening stream and the existing spatial repetition order are preserved. Votes are strictly >32; matches are >=180. Correct and wrong key readouts reuse the same encoded latent. The detector boundary receives no reference payload, original noise, prompt, native inversion output, attack label or CLIP feature. The evaluator separately compares the recovered 256 bits against the enrolled message.

Rows expose bits, votes, ties, exact messages, integer matches and fixed presence decisions. Zeros before/after fp16 scaling, sign changes, per-channel scaled-latent means/stds, dtypes, shape, finiteness and units are retained. Means and amplitudes are diagnostics, not fitted corrections. Reconstruction of each seeded native fp16 generation input must recover 256/256; its receipt explicitly labels it a deterministic reconstruction, not a tensor retained during the original generation run.

The strict-majority tie bias is included in a fixed-payload conditional binomial calculation. These numbers assume independent fair dewhitened chips and are labeled arithmetic references, not empirical or cryptographic FPRs. Public keys/nonces and enrolled reference messages are generous development side information. The retained native run's historical `secret whitening key` wording is copied unchanged as source metadata; the new detector-side-information field explicitly states public fixtures.

## Inventory and resumability

The fixed inventory contains 112 conditions: four prompts x two arms x 14 channels. Eight original files are provenance artifacts, not extra scored observations. Metadata snapshots include native run, artifacts, rows and row receipt. Native helper validation verifies every receipted image's hash and length, journal hash/count, planned identities and complete-run hashes. Scores, runtime and native NFE are joined unchanged. A missing native row remains an explicit missing condition; corrupt inputs produce a retained failed assessor receipt rather than a replacement image.

Fresh runs write the entire inventory before model loading. The same output may resume only with identical commit, code/config, input receipt hashes and verified assessor conditions/journal hashes. Completed rows are skipped; failed rows may be retried with the same inputs. Rejected resumes leave the prior receipt untouched. Journal entries and conditions are checkpointed after each attempted image; hard interruption between journal and receipt writes may require a versioned recovery because unreceipted bytes are deliberately rejected. Native outputs are never edited. Changes to the native run while an assessor is paused require a new assessor directory.

Native summaries remain visible even where lightweight scoring fails. Channel summaries preserve four-source denominators, missing counts, C1 correct/exact recovery, C0 positives and C1 wrong-key positives. Clean and VAE gates are null unless their conditions are complete. Per-condition paired native-minus-lightweight matches and four-cell presence comparisons are descriptive. Strength groups retain four prompt clusters and 12 repeated C1 attack conditions; there is no pooled headline TPR or threshold fit.

## Timing, resource limits and execution

CUDA is synchronized around encoding and timing. Preprocessing/device transfer is included in encode time; CPU transfer and both inexpensive decodes are included in decode-transfer time. Model loading is separate. First-call status is recorded, and each completed image declares one VAE encode, zero U-Net evaluations and zero text-encoder evaluations. Peak GPU allocation is measured per image. These are retained diagnostic timings, not deployment latency claims.

The local pilot blocks network access and verifies pinned assets before loading the fp16 VAE. Resource limits are 10 GiB GPU allocation, 16 GiB observed process working set, 100 MiB new artifacts and 20 minutes additional wall time. Stage-boundary checks do not preempt a running kernel. An identical bounded continuation preserves missing conditions when the cap is reached. Only retained synthetic images are scored; generation/attack safety checks remain those of the native source experiment. Human judgments stay missing.

After parent commits, use `--manifest research/m1_gs_lightweight-dev.json --input-dir <native-run> --output-dir <fresh-MAIN-dev-runs-dir>`. The optional `--preflight-only` checks metadata and file hashes without writes, model loading or GPU work.

## Verification

Twelve CPU tests pass: all four reconstructed fp16 noise messages; exact native tile/coordinate order and key/nonce behavior; 32/33 votes and zero votes; positive scaling and explicit fp16 underflow zeros; shape/dtype/nonfinite rejection; 179/180 matches and reference separation; actual native constructor preprocessing equivalence; conditional-null values; fixed inventory/missing gates; native visibility when lightweight fails; metadata-only native joins/hash corruption; and failed preflight/rejected-resume preservation. Tests use procedural arrays and temporary opaque artifact bytes only. No GPU score or held-out input was read during implementation.
