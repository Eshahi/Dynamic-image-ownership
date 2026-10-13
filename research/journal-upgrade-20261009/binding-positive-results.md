# E3-RC1 constructed-positive and component-control results

Exploratory development evidence, 2026-10-13. The prospective [protocol](binding-positive-protocol.md) is unchanged. This is a public initializer rewrite study, not admitted full-E3 output or human assessment.

Construction commit: `99128f08e57b02ae35d16c80afe138e8cb076732`. Outcome: **completed**. Inclusive duration: **862.625000 s**. Completed native PGD steps: **3000/3000**; forward attempts: 3000. Deadline overrun: 0.000000 s. Local USD 0.

The same-source RR controls have exact delivery in 6/6, combined acceptance in 6/6, and strict quality against both references in 3/6. There are 3 quality-qualified primary component witnesses. Individual witnesses do not override the all-six positive-control gate.

The six pairs, four cells and thresholds were fixed before execution. All branches start from the same retained recipient. Targets come from pre-intervention public q and native h; detection receives only the rewritten suspect. Original images enter quality evaluation only. Supplied q/h enter endpoint comparison outside the detector.

## Fixed-denominator results

N=6 planned images per cell. Q/H are exact readable supplied payloads; D=Q and H; F is full acceptance. None-mode D checks physical delivery. Mode decisions are paired and share extraction. Quality must pass PSNR >35 dB, SSIM >.9 and LPIPS <.1 against both recipient and canonical source. Missing calls are separately counted, never successful rejection.

| Cell | Completed /6 | Quality vs recipient /6 | Quality vs canonical /6 | Both quality /6 | None Q /6 | None H /6 | None D /6 | Combined F /6 | Semantic-only F /6 | Perceptual-only F /6 | None F /6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RR | 6 | 5 | 3 | 3 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| DR | 6 | 6 | 3 | 3 | 6 | 6 | 6 | 0 | 0 | 6 | 6 |
| RD | 6 | 5 | 3 | 3 | 6 | 6 | 6 | 0 | 6 | 0 | 6 |
| DD | 6 | 6 | 3 | 3 | 6 | 6 | 6 | 0 | 0 | 0 | 6 |

None F is not an ownership endpoint. Counts above retain the planned denominator; the following availability and selected-subset counts must accompany them.

| Cell | Observed modes (combined/semantic/perceptual/none) /6 each | Delivered and both-quality subset | F within subset (combined/semantic/perceptual/none) | Primary witness | Reciprocal witness |
|---|---|---:|---|---:|---:|
| RR | 6/6/6/6 | 3 | 3/3/3/3 | 0 | 0 |
| DR | 6/6/6/6 | 3 | 0/0/3/3 | 3 | 0 |
| RD | 6/6/6/6 | 3 | 0/3/0/3 | 0 | 3 |
| DD | 6/6/6/6 | 3 | 0/0/0/3 | 0 | 0 |

## Predeclared conclusions

- Constructed-positive gate: **False**. Nonidentical RR controls: 6/6.
- Primary eligible witness count: 3; pairs [[73, 89], [127, 165], [309, 370]]. Repeated incremental-witness criterion: **False**.
- Reciprocal eligible witnesses: 3.
- New beta presence A: 0/24 observed; 0/24 unresolved. No calibrated FPR claim.
- Full predeclared useful-result conjunction: **False**.

A failed quality/delivery construction cannot establish that semantic binding is useless or that valid positives are rejected. Predicate disagreements outside the quality envelope are diagnostic only. No human preservation, arbitrary-owner authentication, attribution, T3 full-ownership robustness, external superiority or novelty follows.

## All planned cells

Quality columns show PSNR / SSIM / LPIPS. Outcomes are 1/0; absent values remain missing. Gate failure does not remove a row.

| Pair | Cell | Status | Recipient quality | Canonical quality | Both quality | D | F combined / semantic / perceptual | Semantic / own-instance status | Primary / reciprocal witness |
|---|---|---|---|---|---|---|---|---|---|
| 30-72 | RR | ok | 42.5882 / 0.976750 / 0.113084 | 37.9870 / 0.926332 / 0.258140 | 0 | 1 | 1 / 1 / 1 | match / match | 0 / 0 |
| 30-72 | DR | ok | 42.3764 / 0.969768 / 0.085040 | 39.4940 / 0.941405 / 0.203995 | 0 | 1 | 0 / 0 / 1 | uncertain / match | 0 / 0 |
| 30-72 | RD | ok | 42.0092 / 0.971744 / 0.109464 | 38.0726 / 0.927213 / 0.254396 | 0 | 1 | 0 / 1 / 0 | match / mismatch | 0 / 0 |
| 30-72 | DD | ok | 41.9687 / 0.966111 / 0.080469 | 39.5611 / 0.941849 / 0.199487 | 0 | 1 | 0 / 0 / 0 | uncertain / mismatch | 0 / 0 |
| 73-89 | RR | ok | 42.5157 / 0.994346 / 0.018044 | 36.4818 / 0.975591 / 0.054735 | 1 | 1 | 1 / 1 / 1 | match / match | 0 / 0 |
| 73-89 | DR | ok | 42.3145 / 0.993225 / 0.016227 | 37.7205 / 0.980014 / 0.040428 | 1 | 1 | 0 / 0 / 1 | uncertain / match | 1 / 0 |
| 73-89 | RD | ok | 41.8094 / 0.993266 / 0.018377 | 36.4003 / 0.975137 / 0.054927 | 1 | 1 | 0 / 1 / 0 | match / mismatch | 0 / 1 |
| 73-89 | DD | ok | 41.7954 / 0.992411 / 0.016317 | 37.6716 / 0.979820 / 0.040269 | 1 | 1 | 0 / 0 / 0 | uncertain / mismatch | 0 / 0 |
| 127-165 | RR | ok | 42.4235 / 0.984183 / 0.021936 | 36.8009 / 0.932709 / 0.072909 | 1 | 1 | 1 / 1 / 1 | match / match | 0 / 0 |
| 127-165 | DR | ok | 42.0746 / 0.975620 / 0.016184 | 38.4677 / 0.943011 / 0.052159 | 1 | 1 | 0 / 0 / 1 | mismatch / match | 1 / 0 |
| 127-165 | RD | ok | 41.7169 / 0.981436 / 0.021952 | 36.8061 / 0.931915 / 0.072555 | 1 | 1 | 0 / 1 / 0 | match / mismatch | 0 / 1 |
| 127-165 | DD | ok | 41.6590 / 0.974084 / 0.016319 | 38.4390 / 0.942352 / 0.052219 | 1 | 1 | 0 / 0 / 0 | mismatch / mismatch | 0 / 0 |
| 309-370 | RR | ok | 42.3972 / 0.987790 / 0.005926 | 36.6281 / 0.943565 / 0.020884 | 1 | 1 | 1 / 1 / 1 | match / match | 0 / 0 |
| 309-370 | DR | ok | 42.2792 / 0.985167 / 0.004786 | 37.7888 / 0.948281 / 0.016321 | 1 | 1 | 0 / 0 / 1 | uncertain / match | 1 / 0 |
| 309-370 | RD | ok | 42.2135 / 0.987165 / 0.005888 | 36.6488 / 0.943267 / 0.020652 | 1 | 1 | 0 / 1 / 0 | match / mismatch | 0 / 1 |
| 309-370 | DD | ok | 42.1557 / 0.984744 / 0.004655 | 37.8251 / 0.948227 / 0.015877 | 1 | 1 | 0 / 0 / 0 | uncertain / mismatch | 0 / 0 |
| 436-450 | RR | ok | 42.5623 / 0.973205 / 0.058333 | 37.5391 / 0.908351 / 0.172907 | 0 | 1 | 1 / 1 / 1 | match / match | 0 / 0 |
| 436-450 | DR | ok | 42.3722 / 0.965429 / 0.039012 | 39.3734 / 0.929712 / 0.121407 | 0 | 1 | 0 / 0 / 1 | uncertain / match | 0 / 0 |
| 436-450 | RD | ok | 41.5946 / 0.964936 / 0.054570 | 37.4944 / 0.905663 / 0.169326 | 0 | 1 | 0 / 1 / 0 | match / mismatch | 0 / 0 |
| 436-450 | DD | ok | 41.5236 / 0.958236 / 0.037499 | 39.2560 / 0.927103 / 0.120153 | 0 | 1 | 0 / 0 / 0 | uncertain / mismatch | 0 / 0 |
| 459-471 | RR | ok | 42.4735 / 0.975768 / 0.075982 | 37.4929 / 0.917369 / 0.190375 | 0 | 1 | 1 / 1 / 1 | match / match | 0 / 0 |
| 459-471 | DR | ok | 42.3470 / 0.969113 / 0.053978 | 39.1253 / 0.935445 / 0.131979 | 0 | 1 | 0 / 0 / 1 | mismatch / match | 0 / 0 |
| 459-471 | RD | ok | 41.8457 / 0.970221 / 0.071986 | 37.4832 / 0.916503 / 0.186177 | 0 | 1 | 0 / 1 / 0 | match / mismatch | 0 / 0 |
| 459-471 | DD | ok | 41.7230 / 0.963393 / 0.053100 | 39.0691 / 0.934043 / 0.131245 | 0 | 1 | 0 / 0 / 0 | mismatch / mismatch | 0 / 0 |

## Frozen target relationships and positive controls

Equality and Hamming distances below describe fixed pre-intervention payloads, not human semantic labels or a pair selection rule.

| Pair | qR / qD | q bit distance | hR / hD | h bit distance | RR changed pixels | RR target h differs from old operational h | RR classification |
|---|---|---:|---|---:|---:|---|---|
| 30-72 | bac09534 / 0ec0942e | 8 | 84f53204 / 7d97e7a8 | 18 | 242107 | 0 | construction_quality_failure |
| 73-89 | bdd49438 / 99c4b43c | 5 | 049db4c6 / f4a706e1 | 16 | 235800 | 0 | rewritten_positive_accepted |
| 127-165 | efd08760 / 9a5ca71c | 14 | 29be3609 / e5218fa7 | 20 | 235471 | 1 | rewritten_positive_accepted |
| 309-370 | 8ac69434 / daeca434 | 7 | 72704c94 / 5068023e | 12 | 229953 | 1 | rewritten_positive_accepted |
| 436-450 | ebe42c70 / 3885b430 | 12 | 6186bd33 / 2f6fc24a | 21 | 238820 | 1 | construction_quality_failure |
| 459-471 | 8a45e53c / bb54b73e | 9 | 400c95b3 / b1bf580c | 22 | 244582 | 1 | construction_quality_failure |

## Resources and provenance

Recorded resources: `{"minimum_available_ram_bytes": 4735823872, "peak_gpu_allocated_bytes": 2572754944, "peak_process_rss_bytes": 3117264896}`. The runtime checks live RSS, while the receipt also records peak RSS.

Source receipt: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261013-e3-binding-reissue-rc1/run.json`.

Receipt SHA-256: `5a20b4a7aa32eff5f007e149141fc0dd7a465ec80e0e46116d5b5c0c36c84db3`. Protocol SHA-256: `9ea2d79c84a43f94c064a98613d82061f99b8c6b4bbf3e32269692c9b4c30749`. Report renderer: `scripts/journal_binding_reissue_report.py`, SHA-256 `5fd0376f14928d8fc513247536763a323467b665e4ced1f9c6ce21843990eb99`.

All saved images, raw calls, targets and partial states remain in the source run. No rerun, pair replacement, target revision or threshold change was performed. E3/M2 and H2 are unchanged.

Terminal reason:

```text
Fixed schedule completed, regardless of measured quality/delivery/predicate failures
```
