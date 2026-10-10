# E2 fixed attenuation cached-screen analysis

Outcome completed; recorded qualification ineligible.
Recomputed scientific screen False; inclusive Stage A False.
Complete sources 12/12; complete condition cells 36/36; full calls 108/108.
Strict clean quality 12/12; exact clean q 12/12; exact operational h 12/12; exact q/h/both_match 12/12.
Joint fixed-q/content/read/found counts: {'clean': 12, 'sd15_vae': 12, 'sdxl_vae': 11}; each denominator is 12.
Separate intended-owner endpoint counts S/Q/J/H/full: {'clean': {'S': 12, 'Q': 12, 'J': 12, 'H': 12, 'F': 12}, 'sd15_vae': {'S': 12, 'Q': 12, 'J': 12, 'H': 0, 'F': 0}, 'sdxl_vae': {'S': 11, 'Q': 11, 'J': 11, 'H': 0, 'F': 0}}.
Negative calls 72/72: {'C0': {'planned': 36, 'completed': 36, 'any_detections': 0}, 'wrong_owner': {'planned': 36, 'completed': 36, 'any_detections': 0}}.

| Source | Status | Condition | S | Q | J | H | Full | Raw 59 errors | q errors | h errors |
|---|---|---|---|---|---|---|---|---|---|---|
| 147498 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 147498 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 12 |
| 147498 | ok | sdxl_vae | True | True | True | False | False | 0 | 0 | 13 |
| 6012 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 6012 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 18 |
| 6012 | ok | sdxl_vae | False | False | False | False | False | 5 | 0 | 15 |
| 1675 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 1675 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 13 |
| 1675 | ok | sdxl_vae | True | True | True | False | False | 0 | 0 | 12 |
| 4795 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 4795 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 15 |
| 4795 | ok | sdxl_vae | True | True | True | False | False | 2 | 0 | 10 |
| 25394 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 25394 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 18 |
| 25394 | ok | sdxl_vae | True | True | True | False | False | 0 | 0 | 17 |
| 80932 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 80932 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 15 |
| 80932 | ok | sdxl_vae | True | True | True | False | False | 0 | 0 | 16 |
| 109798 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 109798 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 14 |
| 109798 | ok | sdxl_vae | True | True | True | False | False | 0 | 0 | 12 |
| 134882 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 134882 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 14 |
| 134882 | ok | sdxl_vae | True | True | True | False | False | 3 | 0 | 12 |
| 177015 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 177015 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 14 |
| 177015 | ok | sdxl_vae | True | True | True | False | False | 1 | 0 | 18 |
| 190676 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 190676 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 13 |
| 190676 | ok | sdxl_vae | True | True | True | False | False | 2 | 0 | 12 |
| 468505 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 468505 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 15 |
| 468505 | ok | sdxl_vae | True | True | True | False | False | 1 | 0 | 8 |
| 499768 | ok | clean | True | True | True | True | True | 0 | 0 | 0 |
| 499768 | ok | sd15_vae | True | True | True | False | False | 0 | 0 | 16 |
| 499768 | ok | sdxl_vae | True | True | True | False | False | 4 | 0 | 15 |

| Source | E1 strict clean | E2 strict clean | E1 LPIPS | E2 LPIPS | E2 PSNR | E2 SSIM |
|---|---|---|---|---|---|---|
| 147498 | False | True | 0.1167193278670311 | 0.07615819573402405 | 43.44800671238413 | 0.9731999969292001 |
| 6012 | True | True | 0.012333380058407784 | 0.0076469480991363525 | 43.02591034416163 | 0.9855875499478142 |
| 1675 | True | True | 0.05042238160967827 | 0.0324997715651989 | 43.14618854295578 | 0.9764827278387397 |
| 4795 | True | True | 0.028644323348999023 | 0.01828400418162346 | 43.135359248395204 | 0.9852991235252145 |
| 25394 | True | True | 0.03122601844370365 | 0.01988041400909424 | 43.30837995965729 | 0.9771009131751305 |
| 80932 | True | True | 0.033503249287605286 | 0.02131139673292637 | 43.13587323491391 | 0.9825518496311684 |
| 109798 | True | True | 0.06883185356855392 | 0.043226663023233414 | 43.08139142648115 | 0.9683856706689383 |
| 134882 | True | True | 0.056741826236248016 | 0.039245810359716415 | 43.13195169302866 | 0.979144157307675 |
| 177015 | True | True | 0.024371465668082237 | 0.015757637098431587 | 43.07501129281427 | 0.9836867401418723 |
| 190676 | True | True | 0.053712692111730576 | 0.034943073987960815 | 42.42037586625134 | 0.9703459057335029 |
| 468505 | True | True | 0.058759622275829315 | 0.04035889729857445 | 42.42655460712 | 0.9714859266171038 |
| 499768 | True | True | 0.030635282397270203 | 0.020092979073524475 | 42.33949413678332 | 0.9842766569869155 |

E1 J comparator available 36/36; E1 positives 36; all preserved False; lost identities [{'source_id': 6012, 'condition': 'sdxl_vae'}].
Process duration 71.85900000002584 s; parent inclusive duration 72.6446495 s; 300 s cap passes: parent True, process True.
Peak allocated GPU 1718795776 bytes; 10 GiB cap pass True.

Raw/decoded error histograms (unknown/missing slots explicitly counted):
clean: {"exact_read_q_corrections": 0, "h_bit_errors": {"available": 12, "histogram": {"0": 12}, "unknown_or_missing": 0}, "q_bit_errors": {"available": 12, "histogram": {"0": 12}, "unknown_or_missing": 0}, "raw_coded_bit_errors": {"available": 12, "histogram": {"0": 12}, "unknown_or_missing": 0}, "valid_exact_code_corrections": 0}
sd15_vae: {"exact_read_q_corrections": 0, "h_bit_errors": {"available": 12, "histogram": {"12": 1, "13": 2, "14": 3, "15": 3, "16": 1, "18": 2}, "unknown_or_missing": 0}, "q_bit_errors": {"available": 12, "histogram": {"0": 12}, "unknown_or_missing": 0}, "raw_coded_bit_errors": {"available": 12, "histogram": {"0": 12}, "unknown_or_missing": 0}, "valid_exact_code_corrections": 0}
sdxl_vae: {"exact_read_q_corrections": 6, "h_bit_errors": {"available": 12, "histogram": {"10": 1, "12": 4, "13": 1, "15": 2, "16": 1, "17": 1, "18": 1, "8": 1}, "unknown_or_missing": 0}, "q_bit_errors": {"available": 12, "histogram": {"0": 12}, "unknown_or_missing": 0}, "raw_coded_bit_errors": {"available": 12, "histogram": {"0": 5, "1": 2, "2": 2, "3": 1, "4": 1, "5": 1}, "unknown_or_missing": 0}, "valid_exact_code_corrections": 7}

Exploratory same-twelve image-domain cached clean/VAE screen. No initializer qualification or feasible-ball requirement applies to E2. Exact q compares with original recorded q; exact h with frozen operational E1 h. Missing/failed slots remain in all planned denominators; unknown errors remain null. Fresh 36 C0 and 36 wrong-owner calls reuse the twelve sources and retained matched C0 pixels; zero observations do not calibrate population FPR. No T3 generalization, M1a, M1b, T4/T5 preservation, independent design-family passage or latent-method claim follows.

Run code commit: f7fb94ebd0152b29a6612e25689a24c5889cf44b; analysis code commit: 198ed72bc28d0c76b26352e533f9284d5f543736.
E1 B code commit: 4bbc427ed7c4d3b8943285421e754cd35a86e5c7.
Raw run: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1410-e2-attenuation-screen\run.json
Raw calls: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1410-e2-attenuation-screen\rows.jsonl
Inclusive wall: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1410-e2-attenuation-screen\parent-wall.json
E1 raw run: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1351-e1-bch-stage-b\run.json
E1 raw calls: W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1351-e1-bch-stage-b\rows.jsonl
Source image paths, fixed targets, errors, endpoint scalars, condition quality metrics, source-level E1 comparison and discrepancy details are in stats.json.
Issues: []
Discrepancies: []
