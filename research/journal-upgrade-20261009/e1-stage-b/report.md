# E1 Stage B descriptive analysis

Run commit: 4bbc427ed7c4d3b8943285421e754cd35a86e5c7. Analysis commit: 0fa143ea8d300c83fd21ba0ec9656f0df5450910.

Evidence pass: False; inclusive Stage B pass: False. Verdict agreement: {'evidence': True, 'stage_b': True}.

Complete sources 12/12; strict clean quality 11/12; clean exact q/h/both 12/12; valid initializers 11/12; feasible finals 12/12.

Joint exact q: {'clean': 12, 'sd15_vae': 12, 'sdxl_vae': 12}. D2 positives 22; lost identities [].

Negative calls 72/72, including 12 inherited calls; arms: {'C0': {'planned': 36, 'completed': 36, 'any_detections': 0}, 'wrong_owner': {'planned': 36, 'completed': 36, 'any_detections': 0}}.

Timing and memory: {'run_duration_seconds': 811.0, 'parent_inclusive_seconds': 811.9078388, 'inclusive_cap_seconds': 3300, 'inclusive_cap_pass': True, 'peak_allocated_bytes': 7068902400, 'memory_cap_bytes': 10737418240, 'memory_cap_pass': True}.

| Source | Inherited | Status | Strict clean | Q/H/F clean | SD1.5 J/S | SDXL J/S |
|---|---|---|---|---|---|---|
| 1675 | True | ok | True | True/True/True | True/True | True/True |
| 4795 | False | ok | True | True/True/True | True/True | True/True |
| 6012 | False | ok | True | True/True/True | True/True | True/True |
| 25394 | False | ok | True | True/True/True | True/True | True/True |
| 80932 | False | ok | True | True/True/True | True/True | True/True |
| 109798 | False | ok | True | True/True/True | True/True | True/True |
| 134882 | False | ok | True | True/True/True | True/True | True/True |
| 147498 | False | ok | False | True/True/True | True/True | True/True |
| 177015 | False | ok | True | True/True/True | True/True | True/True |
| 190676 | False | ok | True | True/True/True | True/True | True/True |
| 468505 | False | ok | True | True/True/True | True/True | True/True |
| 499768 | True | ok | True | True/True/True | True/True | True/True |

Quality ranges:

```json
{
  "clean": {
    "psnr_db": {
      "min": 40.52578819306281,
      "max": 41.857726855021546,
      "numeric_count": 12,
      "unknown_or_nonnumeric": 0
    },
    "ssim_rgb": {
      "min": 0.956400544882013,
      "max": 0.9794165325347051,
      "numeric_count": 12,
      "unknown_or_nonnumeric": 0
    },
    "lpips": {
      "min": 0.012333380058407784,
      "max": 0.1167193278670311,
      "numeric_count": 12,
      "unknown_or_nonnumeric": 0
    },
    "infinite_psnr_count": 0
  },
  "sd15_vae": {
    "psnr_db": {
      "min": 19.587269654598472,
      "max": 26.640396956132456,
      "numeric_count": 12,
      "unknown_or_nonnumeric": 0
    },
    "ssim_rgb": {
      "min": 0.4604583517574678,
      "max": 0.755615966453205,
      "numeric_count": 12,
      "unknown_or_nonnumeric": 0
    },
    "lpips": {
      "min": 0.09342901408672333,
      "max": 0.31555238366127014,
      "numeric_count": 12,
      "unknown_or_nonnumeric": 0
    },
    "infinite_psnr_count": 0
  },
  "sdxl_vae": {
    "psnr_db": {
      "min": 20.819262327316647,
      "max": 28.556540786617855,
      "numeric_count": 12,
      "unknown_or_nonnumeric": 0
    },
    "ssim_rgb": {
      "min": 0.5314062809762848,
      "max": 0.8285133633516831,
      "numeric_count": 12,
      "unknown_or_nonnumeric": 0
    },
    "lpips": {
      "min": 0.06637543439865112,
      "max": 0.14579446613788605,
      "numeric_count": 12,
      "unknown_or_nonnumeric": 0
    },
    "infinite_psnr_count": 0
  }
}
```

Raw 59-bit and decoded q error histograms by condition:

```json
{
  "clean": {
    "raw_coded_bit_errors": {
      "histogram": {
        "0": 12
      },
      "available": 12,
      "unknown_or_missing": 0
    },
    "q_bit_errors": {
      "histogram": {
        "0": 12
      },
      "available": 12,
      "unknown_or_missing": 0
    },
    "exact_q_corrections": 0
  },
  "sd15_vae": {
    "raw_coded_bit_errors": {
      "histogram": {
        "0": 12
      },
      "available": 12,
      "unknown_or_missing": 0
    },
    "q_bit_errors": {
      "histogram": {
        "0": 12
      },
      "available": 12,
      "unknown_or_missing": 0
    },
    "exact_q_corrections": 0
  },
  "sdxl_vae": {
    "raw_coded_bit_errors": {
      "histogram": {
        "0": 9,
        "1": 2,
        "2": 1
      },
      "available": 12,
      "unknown_or_missing": 0
    },
    "q_bit_errors": {
      "histogram": {
        "0": 12
      },
      "available": 12,
      "unknown_or_missing": 0
    },
    "exact_q_corrections": 3
  }
}
```

Failed or incomplete sources:

```json
[]
```

Unavailable full calls:

```json
[]
```

Unavailable D2 evidence:

```json
[]
```

Issues:

```json
[]
```

Exploratory twelve-source clean/VAE prerequisite only; two inherited Stage A sources and ten new sources. Source failures remain in denominators. B passage requires Stage C and T4/T5 work before M1a; no new T3, M1a, T4 efficacy, calibrated FPR, latent-method or held-out claim follows. Null decoded words remain unknown.
