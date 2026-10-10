# F5-RC1 matched T3 development results

Candidate RC3; measured T3 continuity: **False**. This is a bounded development result, not a full amendment or historical lifecycle verdict.

The analysis recomputes endpoints from full calls against original recorded q and frozen native-clean decoded operational h. Original h is unknown. Stored probe summaries/endpoints are not analysis inputs. Candidate-native calls are the frozen decoder on new candidate pixels; frozen-native enrichment is the old writer/attack baseline.

## Inventory and time

Run: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1051-rc3-t3; commit `ef00d061aaefa3c6db46088199a152d5389e438b`; outcome completed.
Rows 214/214; unique 214; missing 0; duplicates 0; extras 0; failed 0; blocked 7. Actual source IDs: [1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768].
Shared stage 703.594/5400 s (preceding runs counted once); separate cached stage 246.094/1800 s. T4/T5/synthesis time is not yet included.
Reused prior run: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1041-rc2-t3; explicitly shared rows: 142. Controls are shared evidence, not independent n.
Unchanged threshold check: True; frozen S discrepancies: []; call-field errors: [].

## Fixed denominators and endpoints

| Strength | Completed / 36 | S | R | C | Q | J | U | H | D | Full F | Fixed I candidate / frozen / v5 | S continuity | Q/J continuity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 0.1 | 36/36 | 36 | 36 | 36 | 31 | 31 | 0 | 0 | 0 | 0 | 29/29; 29/29; 27/29 | True | False |
| 0.2 | 35/36 | 34 | 35 | 34 | 19 | 19 | 0 | 0 | 0 | 0 | 27/28; 28/28; 18/28 | False | False |

Every success above uses all 36 planned identities; the completed denominator is shown separately. Frozen F has 35 identities at each strength, fixed I has 29/28. Failed/blocked candidate identities never shrink I. Candidate blocks outside I and frozen Q/J-positive obligations permit only coverage-qualified measured continuity; operational failures or missing records cannot pass.

| Strength / endpoint | Frozen positive / 35 | Retained | Lost identities | Gained identities |
|---|---:|---:|---|---|
| 0.1 / S | 35/35 | 35 | none | none |
| 0.1 / R | 35/35 | 35 | none | none |
| 0.1 / C | 35/35 | 35 | none | none |
| 0.1 / Q | 27/35 | 26 | 468505\|0.1\|1 | 4795\|0.1\|0, 4795\|0.1\|1, 4795\|0.1\|2, 134882\|0.1\|1 |
| 0.1 / J | 27/35 | 26 | 468505\|0.1\|1 | 4795\|0.1\|0, 4795\|0.1\|1, 4795\|0.1\|2, 134882\|0.1\|1 |
| 0.2 / S | 35/35 | 34 | 190676\|0.2\|1 | none |
| 0.2 / R | 35/35 | 35 | none | none |
| 0.2 / C | 35/35 | 34 | 190676\|0.2\|1 | none |
| 0.2 / Q | 20/35 | 18 | 80932\|0.2\|0, 109798\|0.2\|2 | 4795\|0.2\|1 |
| 0.2 / J | 20/35 | 18 | 80932\|0.2\|0, 109798\|0.2\|2 | 4795\|0.2\|1 |

Full P/F and paired native/new counts, every endpoint, and 72 per-identity arrays are in the statistics JSON. Gains elsewhere never erase a lost frozen-positive identity. H/D/full acceptance are descriptive, with no invented fragile-h diffusion gate.

## Source-majority and quality

Source-majority means at least two successful seeds out of three, over the fixed twelve sources. Blocked/missing/failed seeds count as no success. These are descriptive development counts, not independent seed or sample inference.
- 0.1 candidate_RC: S 12/12; C 12/12; J 10/12.
- 0.1 candidate_native: S 12/12; C 12/12; J 10/12.
- 0.1 frozen_native: S 12/12; C 12/12; J 9/12.
- 0.1 statuses: {'ok': 36}; missing 0.
- 0.1 quality_input: psnr_db n=36, mean=23.730394718146087, range=18.932123864317155–25.908310067311803; ssim_rgb n=36, mean=0.6329530927810816, range=0.4211306997395152–0.7468616500655434; lpips n=36, mean=0.1241693560861879, range=0.09047210216522217–0.20298098027706146.
- 0.1 quality_source: psnr_db n=36, mean=23.74567960602395, range=18.933085077614–25.934297900922864; ssim_rgb n=36, mean=0.6393307803617098, range=0.42514647388082755–0.753652417940705; lpips n=36, mean=0.13584047535227406, range=0.09418627619743347–0.20890146493911743.
- 0.1 quality_input_lpips_le_0.2: qualified 35/36; S/C/J successes 35/35/30 over 36 planned and 35 qualified; unavailable 0.
- 0.1 quality_input_lpips_le_0.3: qualified 36/36; S/C/J successes 36/36/31 over 36 planned and 36 qualified; unavailable 0.
- 0.1 quality_source_lpips_le_0.2: qualified 34/36; S/C/J successes 34/34/29 over 36 planned and 34 qualified; unavailable 0.
- 0.1 quality_source_lpips_le_0.3: qualified 36/36; S/C/J successes 36/36/31 over 36 planned and 36 qualified; unavailable 0.
- 0.2 candidate_RC: S 12/12; C 12/12; J 6/12.
- 0.2 candidate_native: S 12/12; C 12/12; J 6/12.
- 0.2 frozen_native: S 12/12; C 12/12; J 8/12.
- 0.2 statuses: {'ok': 35, 'safety_blocked': 1}; missing 0.
- 0.2 quality_input: psnr_db n=35, mean=22.231597534051065, range=18.061391498063998–24.72074186048485; ssim_rgb n=35, mean=0.584415349565653, range=0.3649062513079564–0.7137750325650862; lpips n=35, mean=0.1788215526512691, range=0.12727127969264984–0.2776953876018524.
- 0.2 quality_source: psnr_db n=35, mean=22.243024086745425, range=18.0623168460987–24.742419880799645; ssim_rgb n=35, mean=0.5918786191418294, range=0.36928713502141103–0.7288123260804594; lpips n=35, mean=0.1872593207018716, range=0.12988081574440002–0.2823391258716583.
- 0.2 quality_input_lpips_le_0.2: qualified 28/36; S/C/J successes 27/27/15 over 36 planned and 28 qualified; unavailable 1.
- 0.2 quality_input_lpips_le_0.3: qualified 35/36; S/C/J successes 34/34/19 over 36 planned and 35 qualified; unavailable 1.
- 0.2 quality_source_lpips_le_0.2: qualified 27/36; S/C/J successes 26/26/15 over 36 planned and 27 qualified; unavailable 1.
- 0.2 quality_source_lpips_le_0.3: qualified 35/36; S/C/J successes 34/34/19 over 36 planned and 35 qualified; unavailable 1.

Distortion is measured against marked input and original source. LPIPS .20/.30 subsets are descriptive proxies; all attempts and failures remain in planned denominators. Human visual/semantic admissibility remains missing.

## Negatives and limits

- rc shared_C0: 0/264 observed any-channel detections; 288 planned; 24 unavailable.
- rc candidate_C1: 0/213 observed any-channel detections; 216 planned; 3 unavailable.
- native shared_C0: 0/264 observed any-channel detections; 288 planned; 24 unavailable.
- native candidate_C1: 0/213 observed any-channel detections; 216 planned; 3 unavailable.

C0 has 288 planned calls; six retained blocked rows leave 24 unavailable slots and 264 observable calls. C1 wrong-owner calls have 216 planned slots and three calls per available candidate row. No missing decision is synthesized as zero; zero observed calls do not establish zero/504 or population FPR.
Four separate owner calls use roster_size=1. They reuse sources, attacks and sometimes pixels. The frozen numerical thresholds and legacy bound fields are not a routed-system FPR certificate.
T4/T5 and the new six-pair candidate payload-origin arm are not yet run. The inherited all-alpha T5 geometry cannot identify false attribution between distinct legitimate owners. No complete amendment pass, fresh calibration, held-out confirmation or retroactive change to historical M1/M2 is claimed.
