# E3 full T3 descriptive analysis

Recomputed Stage B pass: False; recorded agreement: True.
Commit: b87d8245d5641a8b39d72d1d579050762a24512d; outcome: completed.

Image rows 144/144; full calls 208/216; negative detections 0 in 137/144 available calls.
Unavailable rows: 7; operational failures: 0.

| Strength | S | Exact Q | Joint Q/content | Source-majority S/Q/J (of 12) | Fixed S versus v5 |
|---|---:|---:|---:|---|---|
| 0.1 | 36/36 | 36/36 | 36/36 | {'S': 12, 'Q': 12, 'J': 12} | 29/29 versus 27/29 |
| 0.2 | 35/36 | 35/36 | 35/36 | {'S': 12, 'Q': 12, 'J': 12} | 28/28 versus 18/28 |

Cached selection: {'planned': 12, 'observed': 12, 'strict_quality': 12, 'clean_q_h_both': 12, 'sd15_vae_J': 12, 'sdxl_vae_J': 12, 'inherited_calls': 108, 'negative_calls': 72, 'negative_detections': 0}; branches {'retain': 11, 'contract_once': 1}.
Timing and reused ancestry: {'process_seconds': 142.34400000001187, 'parent_inclusive_seconds': 143.1796966, 'peak_allocated_bytes': 3814109696, 'cap_seconds': 900, 'gpu_cap_bytes': 10737418240, 'cached_composition_seconds': 0.09299999999348074, 'fresh_writer_seconds': None, 'ancestry': 'Selected cached E1 A/B marks and one E2 contraction; inherited timings are not fresh E3 writer cost'}. Inclusive cost/memory cap pass: True.

Strength 0.1 raw/decoded error histograms (nulls separate): {'raw_coded_bit_errors': {'observed': 36, 'null': 0, 'frequencies': {'0': 36}}, 'q_bit_errors': {'observed': 36, 'null': 0, 'frequencies': {'0': 36}}}.
Unavailable C1 slots: [].
Algebraic success/reasons: {'observed': 36, 'null': 0, 'frequencies': {'True': 36}}; {'observed': 36, 'null': 0, 'frequencies': {'ok': 36}}.
Content failures: []; score ranges: {'decoded_score': {'observed': 36, 'null_or_invalid': 0, 'minimum': 14.868106131437086, 'maximum': 17.39072548596224}, 'recomputed_score': {'observed': 36, 'null_or_invalid': 0, 'minimum': 3.3174062624233978, 'maximum': 9.898866142139722}, 'score': {'observed': 36, 'null_or_invalid': 0, 'minimum': 14.868106131437086, 'maximum': 17.39072548596224}}.
D2 retention: {'S': {'old_positive': 36, 'lost': [], 'gained': []}, 'Q': {'old_positive': 36, 'lost': [], 'gained': []}, 'J': {'old_positive': 36, 'lost': [], 'gained': []}}.
frozen_F5 retention: {'S': {'old_positive': 35, 'lost': [], 'gained': ['6012|0.1|2']}, 'Q': {'old_positive': 27, 'lost': [], 'gained': ['4795|0.1|0', '4795|0.1|1', '4795|0.1|2', '6012|0.1|0', '6012|0.1|1', '6012|0.1|2', '134882|0.1|0', '134882|0.1|1', '134882|0.1|2']}, 'J': {'old_positive': 27, 'lost': [], 'gained': ['4795|0.1|0', '4795|0.1|1', '4795|0.1|2', '6012|0.1|0', '6012|0.1|1', '6012|0.1|2', '134882|0.1|0', '134882|0.1|1', '134882|0.1|2']}}.
E1_A retention: {'S': {'old_positive': 6, 'lost': [], 'gained': []}, 'Q': {'old_positive': 6, 'lost': [], 'gained': []}, 'J': {'old_positive': 6, 'lost': [], 'gained': []}}.

Strength 0.2 raw/decoded error histograms (nulls separate): {'raw_coded_bit_errors': {'observed': 35, 'null': 0, 'frequencies': {'0': 35}}, 'q_bit_errors': {'observed': 35, 'null': 0, 'frequencies': {'0': 35}}}.
Unavailable C1 slots: [{'identity': '6012|0.2|0', 'reason': 'safety_blocked', 'interpretation': 'Unsuccessful planned slot; not an observed decoding/content failure'}].
Algebraic success/reasons: {'observed': 35, 'null': 0, 'frequencies': {'True': 35}}; {'observed': 35, 'null': 0, 'frequencies': {'ok': 35}}.
Content failures: []; score ranges: {'decoded_score': {'observed': 35, 'null_or_invalid': 0, 'minimum': 13.607337670290805, 'maximum': 17.1504490606036}, 'recomputed_score': {'observed': 35, 'null_or_invalid': 0, 'minimum': 3.7806324583688546, 'maximum': 10.038264910026237}, 'score': {'observed': 35, 'null_or_invalid': 0, 'minimum': 13.607337670290805, 'maximum': 17.1504490606036}}.
D2 retention: {'S': {'old_positive': 35, 'lost': ['6012|0.2|0'], 'gained': ['6012|0.2|2']}, 'Q': {'old_positive': 31, 'lost': [], 'gained': ['6012|0.2|1', '6012|0.2|2', '134882|0.2|1', '134882|0.2|2']}, 'J': {'old_positive': 31, 'lost': [], 'gained': ['6012|0.2|1', '6012|0.2|2', '134882|0.2|1', '134882|0.2|2']}}.
frozen_F5 retention: {'S': {'old_positive': 35, 'lost': ['6012|0.2|0'], 'gained': ['6012|0.2|2']}, 'Q': {'old_positive': 20, 'lost': [], 'gained': ['4795|0.2|0', '4795|0.2|1', '4795|0.2|2', '6012|0.2|1', '6012|0.2|2', '80932|0.2|2', '109798|0.2|1', '134882|0.2|0', '134882|0.2|1', '134882|0.2|2', '177015|0.2|0', '190676|0.2|1', '468505|0.2|0', '468505|0.2|1', '468505|0.2|2']}, 'J': {'old_positive': 20, 'lost': [], 'gained': ['4795|0.2|0', '4795|0.2|1', '4795|0.2|2', '6012|0.2|1', '6012|0.2|2', '80932|0.2|2', '109798|0.2|1', '134882|0.2|0', '134882|0.2|1', '134882|0.2|2', '177015|0.2|0', '190676|0.2|1', '468505|0.2|0', '468505|0.2|1', '468505|0.2|2']}}.
E1_A retention: {'S': {'old_positive': 6, 'lost': [], 'gained': []}, 'Q': {'old_positive': 6, 'lost': [], 'gained': []}, 'J': {'old_positive': 6, 'lost': [], 'gained': []}}.

Adaptive exploratory in-sample image-domain BCH selection. All 72 C1 generations are fresh; retained C0 pixels receive fresh calls when available. E1 ancestry optimized these same six seeds. Safety blocks remain unsuccessful planned slots, with unobserved negatives unresolved. Source majority is descriptive across twelve reused sources. No population FPR, generalization, T4/T5 preservation, M1a passage, human admissibility or latent-method claim follows.
stats.json retains exact lost/gained identities, failed-joint score details and selected lineage; full calls remain in the input record.

Record issues: []
Metadata issues: ['Scientific CLI comparator loop overwrote method label: frozen_F5']
