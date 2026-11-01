# T4 final-margin association

MEASURED: {
  "design_median_cutoff": 1.0033376910542784,
  "primary": {
    "DESIGN": {
      "n": 30,
      "rho": 0.5506117908787542,
      "high_n": 15,
      "low_n": 15,
      "high_minus_low": 0.9768072869997777,
      "rule": "PREDICTIVE_LEAD_CAUSE_UNKNOWN"
    },
    "EVALUATE": {
      "n": 30,
      "rho": 0.6315906562847609,
      "high_n": 17,
      "low_n": 13,
      "high_minus_low": 0.7768209856260304,
      "rule": "PREDICTIVE_LEAD_CAUSE_UNKNOWN"
    }
  },
  "causal_status": "UNKNOWN: final-only reports lack per-stage residuals/margins and robust-only matched-total-quality counterfactual."
}

JUDGMENT: No causal attribution follows. Missing cells/calls and constant binary outcomes are retained. Q-STAGE is required to separate optimizer, clipping, rounding and second-write interference.
