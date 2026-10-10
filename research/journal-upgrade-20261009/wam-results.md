# WAM SA-1B MIT exploratory results

2026-10-10. Official SA-1B MIT checkpoint; not the COCO checkpoint evaluated in the paper. The retained development run completes the fixed clean/VAE protocol, with no training or outcome-dependent tuning.

Run: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-0948-wam-vae`. Committed adapter `5c93b54bb85b1602c35b75a6818078adc2cb0b78`. Official revision `2c08af04d037d5667c02f6ddebbda9ff04581c3e`; checkpoint SHA-256 `90ef232384e023bd63245eb0c131abd69d2afc7b8f17a71ccedceb542bf009e2`.

Inventory: 12 unique planned development IDs; 144/144 retained image rows; 0 failed, 0 missing, 0 extra. Source IDs: 1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768.

Whole-image embedding uses fixed public 32-bit source-ID messages and complement wrong messages. Native w=2 and predeclared attenuation w=.5 are separate arms. Official predicted mask cutoff is sigmoid>.5; upstream default semihard decoding compares selected-pixel mean **raw bit logits with .5**, unchanged. Empty mask means no decoded message. No calibrated global presence threshold was supplied.

| Arm / condition | Exact message / 12 | Empty mask / 12 | Nonempty mean bit accuracy | All-source zero-scored mean | Strict source quality / 12 |
|---|---:|---:|---:|---:|---:|
| native_w2/clean | 12/12 | 0/12 | 1.000000 | 1.000000 | 12/12 |
| native_w2/sd15_vae | 5/12 | 0/12 | 0.937500 | 0.937500 | 0/12 |
| native_w2/sdxl_vae | 7/12 | 1/12 | 0.974432 | 0.893229 | 0/12 |
| quality_w0p5/clean | 10/12 | 0/12 | 0.976562 | 0.976562 | 12/12 |
| quality_w0p5/sd15_vae | 0/12 | 10/12 | 0.828125 | 0.138021 | 0/12 |
| quality_w0p5/sdxl_vae | 0/12 | 8/12 | 0.843750 | 0.281250 | 0/12 |

Strict clean quality is PSNR>35 dB, SSIM>.9 and LPIPS<.1 on delivered PNGs. Both arms pass clean quality on all twelve; attenuation loses two clean exact messages and all VAE exact recovery. After-VAE strict quality relative to original source is diagnostic, not an attack admissibility requirement. Native VAE recovery is 5/12 SD1.5 and 7/12 SDXL. These VAE-only results do not establish diffusion robustness.

Bit accuracy conditional on nonempty masks excludes unreadable sources. All-source means assign zero to empty, failed or missing sources; source IDs, failure/readability categories and distributions are preserved in `wam-statistics.json`. SDXL native empty-mask source: 6012.

## Delivered quality distributions

Entries are n; mean / median / [minimum, maximum]. PSNR aggregates finite values only, with infinite counts explicit. Each C1 row is one source per condition. Source quality compares original canonical photo; attack-input quality compares delivered clean marked PNG against delivered attacked PNG.

| Arm / condition / reference | PSNR dB | SSIM | LPIPS |
|---|---|---|---|
| native_w2/clean / source | n=12; 38.3221 / 38.2035 / [37.1088, 41.2893]; infinite=0 | n=12; 0.9772 / 0.9821 / [0.9419, 0.9915] | n=12; 0.0290 / 0.0289 / [0.0068, 0.0591] |
| native_w2/clean / attack input | no finite values; infinite=12 | n=12; 1.0000 / 1.0000 / [1.0000, 1.0000] | n=12; 0.0000 / 0.0000 / [0.0000, 0.0000] |
| native_w2/sd15_vae / source | n=12; 25.1054 / 25.1916 / [19.6037, 27.3275]; infinite=0 | n=12; 0.6855 / 0.7274 / [0.4894, 0.7963] | n=12; 0.0887 / 0.0819 / [0.0631, 0.1588] |
| native_w2/sd15_vae / attack input | n=12; 25.0295 / 25.1475 / [19.5770, 27.2731]; infinite=0 | n=12; 0.6825 / 0.7222 / [0.4874, 0.7933] | n=12; 0.0813 / 0.0750 / [0.0592, 0.1420] |
| native_w2/sdxl_vae / source | n=12; 26.4082 / 26.3025 / [20.6941, 28.6777]; infinite=0 | n=12; 0.7281 / 0.7758 / [0.5377, 0.8335] | n=12; 0.0855 / 0.0772 / [0.0546, 0.1407] |
| native_w2/sdxl_vae / attack input | n=12; 26.3038 / 26.2390 / [20.6483, 28.5717]; infinite=0 | n=12; 0.7250 / 0.7693 / [0.5340, 0.8242] | n=12; 0.0760 / 0.0631 / [0.0504, 0.1389] |
| quality_w0p5/clean / source | n=12; 49.6448 / 49.5055 / [48.4863, 52.8069]; infinite=0 | n=12; 0.9972 / 0.9982 / [0.9890, 0.9992] | n=12; 0.0021 / 0.0020 / [0.0005, 0.0059] |
| quality_w0p5/clean / attack input | no finite values; infinite=12 | n=12; 1.0000 / 1.0000 / [1.0000, 1.0000] | n=12; 0.0000 / 0.0000 / [0.0000, 0.0000] |
| quality_w0p5/sd15_vae / source | n=12; 25.3012 / 25.3381 / [19.6924, 27.4744]; infinite=0 | n=12; 0.7000 / 0.7346 / [0.4965, 0.8147] | n=12; 0.0713 / 0.0684 / [0.0472, 0.1272] |
| quality_w0p5/sd15_vae / attack input | n=12; 25.2922 / 25.3309 / [19.6897, 27.4679]; infinite=0 | n=12; 0.6991 / 0.7339 / [0.4961, 0.8123] | n=12; 0.0712 / 0.0687 / [0.0480, 0.1261] |
| quality_w0p5/sdxl_vae / source | n=12; 26.7211 / 26.5436 / [20.8607, 29.0393]; infinite=0 | n=12; 0.7433 / 0.7825 / [0.5506, 0.8603] | n=12; 0.0645 / 0.0570 / [0.0378, 0.1193] |
| quality_w0p5/sdxl_vae / attack input | n=12; 26.7079 / 26.5332 / [20.8568, 29.0279]; infinite=0 | n=12; 0.7426 / 0.7817 / [0.5501, 0.8570] | n=12; 0.0644 / 0.0570 / [0.0386, 0.1204] |

## Numerical attack coverage

LPIPS <=.20/.30 versus attack input are numerical sensitivity/primary proxies, with human admissibility missing. Coverage does not change the twelve-source primary denominator or authorize a favorable subset claim.

| Arm / condition | LPIPS <=.20 sources (exact) | LPIPS <=.30 sources (exact) |
|---|---:|---:|
| native_w2/clean | 12/12 (12) | 12/12 (12) |
| native_w2/sd15_vae | 12/12 (5) | 12/12 (5) |
| native_w2/sdxl_vae | 12/12 (7) | 12/12 (7) |
| quality_w0p5/clean | 12/12 (10) | 12/12 (10) |
| quality_w0p5/sd15_vae | 12/12 (0) | 12/12 (0) |
| quality_w0p5/sdxl_vae | 12/12 (0) | 12/12 (0) |

## Negative diagnostics and scope

C0 arm repeats have identical recorded decoding and quality fields: True. There are 36 distinct C0 source-condition cells reusing 12 photos, not 72 independent unmarked images. All C0 expected-message exact counts and all C1 complement-message exact counts are zero. These are small development diagnostics, not empirical FPR calibration, security bounds or statistical superiority. A nonempty mask is diagnostic only.

WAM native exact 32-bit recovery is not F5 checked semantic recovery or full content binding. F5 SDXL checked 10/12 is therefore not a comparable exact-message endpoint. No F5/WAM ranking, controlled-FPR superiority, isolated carrier benefit, ownership guarantee, T4/T5 result or full-diffusion result is inferred. The public payload schedule is experimental and confers no cryptographic authorization.

## Feasibility and reproduction

Total full run 75.594s; WAM initialization 1.562s; peak overall CUDA allocation 2095677440 bytes (includes loaded VAEs, not WAM-only memory). Timing is exploratory; repeated per-condition embed timing is one shared clean embedding execution. Distinct clean C1 embedding distributions and detector distributions are in JSON. The earlier one-source clean smoke is a feasibility check on the same development source, not additional evidence.

Reproduce without reading images or executing GPU code:

```text
python scripts/journal_wam_analysis.py --run-dir <retained 20261010-0948-wam-vae> --output-dir research/journal-upgrade-20261009
```

The analysis reads only `run.json` and `rows.jsonl`, recomputes the inventory and all aggregates, and writes this report plus `wam-statistics.json`. No held-out data or historical result is modified.
