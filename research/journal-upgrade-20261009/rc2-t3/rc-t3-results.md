# F5-RC1 matched T3 development results

Candidate RC2; measured T3 continuity: **False**. This is a bounded development result, not a full amendment or historical lifecycle verdict.

The analysis recomputes endpoints from full calls against original recorded q and frozen native-clean decoded operational h. Original h is unknown. Stored probe summaries/endpoints are not analysis inputs. Candidate-native calls are the frozen decoder on new candidate pixels; frozen-native enrichment is the old writer/attack baseline.

## Inventory and time

Run: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1041-rc2-t3; commit `d28d7a14f3e0c97c73d1387c7001611f9fade29d`; outcome completed.
Rows 214/214; unique 214; missing 0; duplicates 0; extras 0; failed 0; blocked 8. Actual source IDs: [1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768].
Shared stage 498.297/5400 s (preceding runs counted once); separate cached stage 246.094/1800 s. T4/T5/synthesis time is not yet included.
Reused prior run: None; explicitly shared rows: 0. Controls are shared evidence, not independent n.
Unchanged threshold check: True; frozen S discrepancies: []; call-field errors: [].

## Fixed denominators and endpoints

| Strength | Completed / 36 | S | R | C | Q | J | U | H | D | Full F | Fixed I candidate / frozen / v5 | S continuity | Q/J continuity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 0.1 | 36/36 | 36 | 36 | 36 | 32 | 32 | 0 | 0 | 0 | 0 | 29/29; 29/29; 27/29 | True | False |
| 0.2 | 34/36 | 33 | 33 | 32 | 21 | 21 | 1 | 0 | 0 | 0 | 26/28; 28/28; 18/28 | False | False |

Every success above uses all 36 planned identities; the completed denominator is shown separately. Frozen F has 35 identities at each strength, fixed I has 29/28. Failed/blocked candidate identities never shrink I. Candidate blocks outside I and frozen Q/J-positive obligations permit only coverage-qualified measured continuity; operational failures or missing records cannot pass.

| Strength / endpoint | Frozen positive / 35 | Retained | Lost identities | Gained identities |
|---|---:|---:|---|---|
| 0.1 / S | 35/35 | 35 | none | none |
| 0.1 / R | 35/35 | 35 | none | none |
| 0.1 / C | 35/35 | 35 | none | none |
| 0.1 / Q | 27/35 | 25 | 468505\|0.1\|0, 468505\|0.1\|1 | 4795\|0.1\|0, 4795\|0.1\|1, 4795\|0.1\|2, 134882\|0.1\|0, 134882\|0.1\|1, 134882\|0.1\|2 |
| 0.1 / J | 27/35 | 25 | 468505\|0.1\|0, 468505\|0.1\|1 | 4795\|0.1\|0, 4795\|0.1\|1, 4795\|0.1\|2, 134882\|0.1\|0, 134882\|0.1\|1, 134882\|0.1\|2 |
| 0.2 / S | 35/35 | 33 | 6012\|0.2\|1, 468505\|0.2\|0 | none |
| 0.2 / R | 35/35 | 33 | 6012\|0.2\|0, 468505\|0.2\|0 | none |
| 0.2 / C | 35/35 | 32 | 6012\|0.2\|0, 6012\|0.2\|1, 468505\|0.2\|0 | none |
| 0.2 / Q | 20/35 | 18 | 80932\|0.2\|0, 109798\|0.2\|2 | 4795\|0.2\|0, 4795\|0.2\|1, 190676\|0.2\|1 |
| 0.2 / J | 20/35 | 18 | 80932\|0.2\|0, 109798\|0.2\|2 | 4795\|0.2\|0, 4795\|0.2\|1, 190676\|0.2\|1 |

Full P/F and paired native/new counts, every endpoint, and 72 per-identity arrays are in the statistics JSON. Gains elsewhere never erase a lost frozen-positive identity. H/D/full acceptance are descriptive, with no invented fragile-h diffusion gate.

## Source-majority and quality

Source-majority means at least two successful seeds out of three, over the fixed twelve sources. Blocked/missing/failed seeds count as no success. These are descriptive development counts, not independent seed or sample inference.
- 0.1 candidate_RC: S 12/12; C 12/12; J 10/12.
- 0.1 candidate_native: S 12/12; C 12/12; J 10/12.
- 0.1 frozen_native: S 12/12; C 12/12; J 9/12.
- 0.1 statuses: {'ok': 36}; missing 0.
- 0.1 quality_input: psnr_db n=36, mean=23.72580826465796, range=18.914041583807546–25.90771206083773; ssim_rgb n=36, mean=0.6321643947932789, range=0.42056750380039787–0.7467304942881013; lpips n=36, mean=0.12486797819534938, range=0.0908084511756897–0.20241090655326843.
- 0.1 quality_source: psnr_db n=36, mean=23.740866725679812, range=18.915167434088467–25.933422941186343; ssim_rgb n=36, mean=0.6384775892577371, range=0.42466491958786834–0.7534019660393673; lpips n=36, mean=0.13650114834308624, range=0.09468474984169006–0.20742495357990265.
- 0.1 quality_input_lpips_le_0.2: qualified 34/36; S/C/J successes 34/34/30 over 36 planned and 34 qualified; unavailable 0.
- 0.1 quality_input_lpips_le_0.3: qualified 36/36; S/C/J successes 36/36/32 over 36 planned and 36 qualified; unavailable 0.
- 0.1 quality_source_lpips_le_0.2: qualified 34/36; S/C/J successes 34/34/30 over 36 planned and 34 qualified; unavailable 0.
- 0.1 quality_source_lpips_le_0.3: qualified 36/36; S/C/J successes 36/36/32 over 36 planned and 36 qualified; unavailable 0.
- 0.2 candidate_RC: S 11/12; C 11/12; J 7/12.
- 0.2 candidate_native: S 11/12; C 11/12; J 7/12.
- 0.2 frozen_native: S 12/12; C 12/12; J 8/12.
- 0.2 statuses: {'ok': 34, 'safety_blocked': 2}; missing 0.
- 0.2 quality_input: psnr_db n=34, mean=22.27646675929454, range=18.04369131726397–24.728544483903555; ssim_rgb n=34, mean=0.5825002293506164, range=0.3649722404294847–0.7133904000321099; lpips n=34, mean=0.17921211395193548, range=0.12613162398338318–0.27463749051094055.
- 0.2 quality_source: psnr_db n=34, mean=22.287830598817088, range=18.04486791600807–24.749581810648593; ssim_rgb n=34, mean=0.5896862551100093, range=0.36997003866319456–0.7282650608307266; lpips n=34, mean=0.18768033955027075, range=0.12898439168930054–0.2787054777145386.
- 0.2 quality_input_lpips_le_0.2: qualified 27/36; S/C/J successes 26/25/17 over 36 planned and 27 qualified; unavailable 2.
- 0.2 quality_input_lpips_le_0.3: qualified 34/36; S/C/J successes 33/32/21 over 36 planned and 34 qualified; unavailable 2.
- 0.2 quality_source_lpips_le_0.2: qualified 25/36; S/C/J successes 24/23/15 over 36 planned and 25 qualified; unavailable 2.
- 0.2 quality_source_lpips_le_0.3: qualified 34/36; S/C/J successes 33/32/21 over 36 planned and 34 qualified; unavailable 2.

Distortion is measured against marked input and original source. LPIPS .20/.30 subsets are descriptive proxies; all attempts and failures remain in planned denominators. Human visual/semantic admissibility remains missing.

## Negatives and limits

- rc shared_C0: 0/264 observed any-channel detections; 288 planned; 24 unavailable.
- rc candidate_C1: 0/210 observed any-channel detections; 216 planned; 6 unavailable.
- native shared_C0: 0/264 observed any-channel detections; 288 planned; 24 unavailable.
- native candidate_C1: 0/210 observed any-channel detections; 216 planned; 6 unavailable.

C0 has 288 planned calls; six retained blocked rows leave 24 unavailable slots and 264 observable calls. C1 wrong-owner calls have 216 planned slots and three calls per available candidate row. No missing decision is synthesized as zero; zero observed calls do not establish zero/504 or population FPR.
Four separate owner calls use roster_size=1. They reuse sources, attacks and sometimes pixels. The frozen numerical thresholds and legacy bound fields are not a routed-system FPR certificate.
T4/T5 and the new six-pair candidate payload-origin arm are not yet run. The inherited all-alpha T5 geometry cannot identify false attribution between distinct legitimate owners. No complete amendment pass, fresh calibration, held-out confirmation or retroactive change to historical M1/M2 is claimed.
