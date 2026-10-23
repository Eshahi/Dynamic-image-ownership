# Amendment 1d: stage-2a contract and implementation (pre-outcome)

Written by Claude (Opus 5.5) on 2026-10-23, at the user's request. No stage-2 outcome existed when this was written: no server had been rented, and no study image had been marked, regenerated or read.

## User decisions

The user made these decisions in chat. The first is quoted verbatim:

- **2026-10-21:** "Approve P1 TrustMark, P9 PixelSeal, P4 Kandinsky 3 and P5 smoothing; decline the rest; ceiling 35 instance-hours or USD 30." (BRIEF section 1c.)
- **2026-10-21:** the user approved Claude's lean two-stage plan to cut cost (BRIEF section 1d).
- **2026-10-23:** Claude, not Codex, runs stage 2, and the server work must continue if the SSH connection drops.

## What changes from the reviewed freeze (`e318757`)

The new contract is `stage2a-config.json`, built by `scripts/encoder_transfer_amend_1d.py` from `frozen-config.json`. It records the base file's SHA-256, and `frozen-config.json` itself is unchanged.

**Contract and arms:**
- **Status:** `user-amended-pre-outcome`. The runner accepts it only if the recorded base hash matches the reviewed freeze (`contract_status`).
- **Arms:** F5 r2, v5 r3, WAM, VINE-R, plus TrustMark Q (P1) and Pixel Seal (P9). The new two are limited to their proposal cells:
  - TrustMark Q: clean, D1 and R1 at .2;
  - Pixel Seal: clean and R1 at .2.

**Channels:**
- **R0 and R1:** strength .2 only, seeds 12, 13 and 14, with the frozen pipelines.
- **D1** (SDXL VAE only), **X1 and X2** (resize-only controls): unchanged.
  - X1 and X2 are frozen-core cells that need no GPU. They are kept although section 1d does not list them: they separate the 512-1024-512 resize from the SDXL effect in the primary cell.
- **D3 (new), the P4 AE-only option:**
  - It is a Kandinsky 3 MoVQ round trip at 1024, with fp32 compute from the fp16 weights.
  - It uses `movq.encode(x).latents`, then `movq.decode(z, force_not_quantize=True)`, as `Kandinsky3Img2ImgPipeline` does.
  - It applies to the four core arms and C0.
- **Stage 2b only:** the R1 rinse, strengths .1 and .4, full P4 and P5. R2 and D2 (FLUX) stay disabled.

**Decision and statistics:**
- **Decision rule:** unchanged (section 3, cut 45, fail below 30, margin 3).
  - B is still the maximum of WAM and VINE-R at R1 .2.
  - TrustMark and Pixel Seal are reported next to them but never enter B.
  - The Holm family stays v5, WAM and VINE-R (size 3); comparisons with the new arms are descriptive.
- **Common presence for the new arms:**
  - TrustMark Q needs the native BCH_5 `detected` flag and binomial agreement (P ≤ 1e-4) on the 61 decoded payload bits. The native flag, exact payload and raw 100-bit codeword agreement are reported separately.
  - Pixel Seal uses binomial agreement on the 256 decoded bits.
  - Neither rule is calibrated; reported negatives are observed counts only.

**Budget and environment:**
- **Budget:** 35 instance-hours or USD 30, whichever comes first, for stages 2a and 2b together.
  - If the smoke projection overruns, the declared reduction order is: drop D3, then TrustMark, then Pixel Seal.
  - F5, v5, WAM, VINE-R and C0 at R0 .2 and R1 .2 are protected.
- **Packages:** `lightning` and `torchmetrics` are added, because the pinned TrustMark loader imports them. Their exact versions are those installed on the server, pinned in the contract before the run.
- **Assets** (`stage2a-asset-plan.json`):
  - pinned checkouts: adobe/trustmark@6df5a0a29b51cbec832695fdf02051a1937e37bd and facebookresearch/videoseal@870ca7fb33578b90f14c602016b6c2788096226e;
  - TrustMark Q encoder, decoder and config, which match the loader's hard-coded MD5 values;
  - the Pixel Seal checkpoint (1,237,429,197 bytes; mutable URL, so its SHA-256 is the pin);
  - Kandinsky 3 MoVQ at revision bf79e6c, with the SHA-256 from the stage-1b pin record.

## Implementation

- **`encoder_transfer_test.py`:**
  - per-channel arm scopes (`channel_arms`, `read_methods`);
  - ordered, declared reductions (`reduction_steps`, `apply_reduction`), which keep the legacy core order for the frozen config;
  - the amended execution gate (`contract_status`);
  - analysis that keeps B and Holm on the frozen arms.
- **`encoder_transfer_runtime.py`:**
  - the budget takes its limits from the contract (the default 15 h and USD 15 are unchanged);
  - adapters `TrustMarkQ`, `PixelSeal` and `MoVQ`, with the D3 round trip.
- **`encoder_transfer_reporting.py`:** scoped loops, and operating points for every presence-type arm.
- **`encoder_transfer_assets.py`:** prepares the two checkouts and places the TrustMark weights where its loader checks them.
- **`encoder_transfer_adapter_check.py`:** one clean embed and read for each new adapter, plus one MoVQ round trip, on a reserved smoke source. It only checks the pipeline.
- **`encoder_transfer_server_driver.sh`:** runs under tmux on the server and survives SSH loss.
  - It runs prepare, the adapter check, the smoke test, the stage-2a run with its analysis, and then packs the results.
  - Each phase resumes from its journal.
  - After three failures of one phase it holds and waits for Claude.
  - After the results are fetched, or after a 12-hour window, it stops (never destroys) the instance when vast.ai provides the container key.
- **Tests:** `tests/test_encoder_transfer_amendment_1d.py`, plus the 26 existing tests, which still pass.

## Review

This amendment was not independently reviewed before execution. The user's decisions fixed its scientific content. The one independent review at the end of stage 2 checks that the code follows this document and the frozen design, together with the numbers and the route label. Any implementation-only fix made during the run is recorded through the runner's `--bugfix-note` mechanism.

## Stage 2b

Stage 2b runs only if stage 2a gives TRANSFERS (ROUTE A or B), within the remaining budget. Its settings are those frozen at `e318757`. Its code is written only in that case, and before any stage-2b output exists. Cells not run in stage 2a are reported as "not run by design (stage 2a result)", never as failures.
