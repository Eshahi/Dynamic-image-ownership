# F5-RC1 matched T3 development results

D2 descriptive characterization; candidate eligibility: **False**; M1a pass: **False**. Diagnostic: **diffusion-aware signal worth preserving, SDXL prerequisite still failed**. Complete within inclusive time/GPU budget: True.

The retained SDXL joint screen is 10/12 and failed its prerequisite. D2 remains ineligible regardless of these results. The attack identities were used in optimization: evidence is in-sample. No T4/T5 expansion, new candidate or lifecycle transition follows.
GPU allocation peak 3814109696 bytes / 10737418240 bytes; within cap: True. Cached screen costs are retained separately and cannot restore eligibility.
The analysis recomputes endpoints from full calls against original recorded q and frozen native-clean decoded operational h. Original h is unknown. Stored probe summaries/endpoints are not analysis inputs. Candidate-native calls are the frozen decoder on new candidate pixels; frozen-native enrichment is the old writer/attack baseline.

## Inventory and time

Run: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1330-d2-descriptive-t3; commit `acdebdbc5af40bb22fd64815882a9e763a0541e0`; outcome completed.
Rows 214/214; unique 214; missing 0; duplicates 0; extras 0; failed 0; blocked 7. Actual source IDs: [1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768].
T3 stage 206.516/900 s; prerequisite stage 947.765/3300 s. Descriptive D2 900 seconds inclusive of imports, prerequisite validation, fresh attacks and final summaries; inherited evidence cost excluded. T4/T5 are not established by this assessment.
Reused prior run: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1051-rc3-t3; explicitly shared rows: 142. Controls are shared evidence, not independent n.
Unchanged threshold check: True; frozen S discrepancies: []; call-field errors: [].

## Fixed denominators and endpoints

| Strength | Completed / 36 | S | R | C | Q | J | U | H | D | Full F | Fixed I candidate / frozen / v5 | S continuity | Q/J continuity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 0.1 | 36/36 | 36 | 36 | 36 | 36 | 36 | 0 | 0 | 0 | 0 | 29/29; 29/29; 27/29 | True | True |
| 0.2 | 35/36 | 35 | 35 | 35 | 31 | 31 | 0 | 0 | 0 | 0 | 28/28; 28/28; 18/28 | True | True |

Every success above uses all 36 planned identities; the completed denominator is shown separately. Frozen F has 35 identities at each strength, fixed I has 29/28. Failed/blocked candidate identities never shrink I. Candidate blocks outside I and frozen Q/J-positive obligations permit only coverage-qualified measured continuity; operational failures or missing records cannot pass.

| Strength / endpoint | Frozen positive / 35 | Retained | Lost identities | Gained identities |
|---|---:|---:|---|---|
| 0.1 / S | 35/35 | 35 | none | none |
| 0.1 / R | 35/35 | 35 | none | none |
| 0.1 / C | 35/35 | 35 | none | none |
| 0.1 / Q | 27/35 | 27 | none | 4795\|0.1\|0, 4795\|0.1\|1, 4795\|0.1\|2, 6012\|0.1\|0, 6012\|0.1\|1, 134882\|0.1\|0, 134882\|0.1\|1, 134882\|0.1\|2 |
| 0.1 / J | 27/35 | 27 | none | 4795\|0.1\|0, 4795\|0.1\|1, 4795\|0.1\|2, 6012\|0.1\|0, 6012\|0.1\|1, 134882\|0.1\|0, 134882\|0.1\|1, 134882\|0.1\|2 |
| 0.2 / S | 35/35 | 35 | none | none |
| 0.2 / R | 35/35 | 35 | none | none |
| 0.2 / C | 35/35 | 35 | none | none |
| 0.2 / Q | 20/35 | 20 | none | 4795\|0.2\|0, 4795\|0.2\|1, 4795\|0.2\|2, 80932\|0.2\|2, 109798\|0.2\|1, 134882\|0.2\|0, 177015\|0.2\|0, 190676\|0.2\|1, 468505\|0.2\|0, 468505\|0.2\|1, 468505\|0.2\|2 |
| 0.2 / J | 20/35 | 20 | none | 4795\|0.2\|0, 4795\|0.2\|1, 4795\|0.2\|2, 80932\|0.2\|2, 109798\|0.2\|1, 134882\|0.2\|0, 177015\|0.2\|0, 190676\|0.2\|1, 468505\|0.2\|0, 468505\|0.2\|1, 468505\|0.2\|2 |

Full P/F and paired native/new counts, every endpoint, and 72 per-identity arrays are in the statistics JSON. Gains elsewhere never erase a lost frozen-positive identity. H/D/full acceptance are descriptive, with no invented fragile-h diffusion gate.

## Native readable q-word errors

Hamming error histograms use only native readable 32-bit words against original q. Unreadable, missing, invalid and unavailable words have null errors, never zero errors. Signed bit margins are not exposed by the retained full-call API and are not invented.

| Strength / decoder | Readable error count: number of words | Word statuses |
|---|---|---|
| 0.1 / candidate_RC | 0: 36 | {'readable': 36} |
| 0.1 / candidate_native | 0: 36 | {'readable': 36} |
| 0.1 / frozen_native | 0: 27; 1: 4; 2: 4 | {'readable': 35, 'unavailable': 1} |
| 0.2 / candidate_RC | 0: 31; 1: 3; 2: 1 | {'readable': 35, 'unavailable': 1} |
| 0.2 / candidate_native | 0: 31; 1: 3; 2: 1 | {'readable': 35, 'unavailable': 1} |
| 0.2 / frozen_native | 0: 20; 1: 9; 2: 4; 4: 2 | {'readable': 35, 'unavailable': 1} |

Per-identity Hamming errors and all source-level three-seed endpoints are in the statistics JSON.

## Source-majority and quality

Source-majority means at least two successful seeds out of three, over the fixed twelve sources. Blocked/missing/failed seeds count as no success. These are descriptive development counts, not independent seed or sample inference.
- 0.1 candidate_RC: S 12/12; C 12/12; J 12/12.
- 0.1 candidate_native: S 12/12; C 12/12; J 12/12.
- 0.1 frozen_native: S 12/12; C 12/12; J 9/12.
- 0.1 statuses: {'ok': 36}; missing 0.
- 0.1 quality_input: psnr_db n=36, mean=23.71513101209744, range=18.93657227412659–25.908310067311803; ssim_rgb n=36, mean=0.6311578859379584, range=0.42099068506987364–0.7470017434729069; lpips n=36, mean=0.12460945546627045, range=0.09303479641675949–0.20284759998321533.
- 0.1 quality_source: psnr_db n=36, mean=23.731506014876885, range=18.937721031427962–25.934297900922864; ssim_rgb n=36, mean=0.6376044886147274, range=0.42504673073498694–0.7537964851744359; lpips n=36, mean=0.1370758598463403, range=0.0984245091676712–0.20890602469444275.
- 0.1 quality_input_lpips_le_0.2: qualified 35/36; S/C/J successes 35/35/35 over 36 planned and 35 qualified; unavailable 0.
- 0.1 quality_input_lpips_le_0.3: qualified 36/36; S/C/J successes 36/36/36 over 36 planned and 36 qualified; unavailable 0.
- 0.1 quality_source_lpips_le_0.2: qualified 34/36; S/C/J successes 34/34/34 over 36 planned and 34 qualified; unavailable 0.
- 0.1 quality_source_lpips_le_0.3: qualified 36/36; S/C/J successes 36/36/36 over 36 planned and 36 qualified; unavailable 0.
- 0.2 candidate_RC: S 12/12; C 12/12; J 10/12.
- 0.2 candidate_native: S 12/12; C 12/12; J 10/12.
- 0.2 frozen_native: S 12/12; C 12/12; J 8/12.
- 0.2 statuses: {'ok': 35, 'safety_blocked': 1}; missing 0.
- 0.2 quality_input: psnr_db n=35, mean=22.221062700871204, range=18.063327254364417–24.72074186048485; ssim_rgb n=35, mean=0.5826746122724933, range=0.3649361654933695–0.7137750325650862; lpips n=35, mean=0.17885322655950273, range=0.13159990310668945–0.27665969729423523.
- 0.2 quality_source: psnr_db n=35, mean=22.233535798444, range=18.064426442358773–24.742419880799645; ssim_rgb n=35, mean=0.5903188689221927, range=0.3694686968572377–0.7288123260804594; lpips n=35, mean=0.18762359533991133, range=0.13580426573753357–0.28135061264038086.
- 0.2 quality_input_lpips_le_0.2: qualified 28/36; S/C/J successes 28/28/24 over 36 planned and 28 qualified; unavailable 1.
- 0.2 quality_input_lpips_le_0.3: qualified 35/36; S/C/J successes 35/35/31 over 36 planned and 35 qualified; unavailable 1.
- 0.2 quality_source_lpips_le_0.2: qualified 27/36; S/C/J successes 27/27/23 over 36 planned and 27 qualified; unavailable 1.
- 0.2 quality_source_lpips_le_0.3: qualified 35/36; S/C/J successes 35/35/31 over 36 planned and 35 qualified; unavailable 1.

Distortion is measured against marked input and original source. LPIPS .20/.30 subsets are descriptive proxies; all attempts and failures remain in planned denominators. Human visual/semantic admissibility remains missing.

## Negatives and limits

- rc shared_C0: 0/264 observed any-channel detections; 288 planned; 24 unavailable.
- rc candidate_C1: 0/213 observed any-channel detections; 216 planned; 3 unavailable.
- native shared_C0: 0/264 observed any-channel detections; 288 planned; 24 unavailable.
- native candidate_C1: 0/213 observed any-channel detections; 216 planned; 3 unavailable.

C0 has 288 planned calls; six retained blocked rows leave 24 unavailable slots and 264 observable calls. C1 wrong-owner calls have 216 planned slots and three calls per available candidate row. No missing decision is synthesized as zero; zero observed calls do not establish zero/504 or population FPR.
Four separate owner calls use roster_size=1. They reuse sources, attacks and sometimes pixels. The frozen numerical thresholds and legacy bound fields are not a routed-system FPR certificate.
T4/T5 and the new six-pair candidate payload-origin arm are not yet run. The inherited all-alpha T5 geometry cannot identify false attribution between distinct legitimate owners. No complete amendment pass, fresh calibration, held-out confirmation or retroactive change to historical M1/M2 is claimed.
