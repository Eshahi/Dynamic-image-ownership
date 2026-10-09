"""Planning arithmetic only; reads no study images and changes no experiment output."""
import json
import math
from pathlib import Path
from scipy.stats import beta, binom


def interval(k, n, alpha=0.05):
    return {
        "successes": k, "independent_units": n, "rate": k / n,
        "one_sided_95_lower": float(beta.ppf(alpha, k, n - k + 1)) if k else 0.0,
        "one_sided_95_upper": float(beta.ppf(1 - alpha, k + 1, n - k)) if k < n else 1.0,
    }


result = {
    "purpose": "Descriptive arithmetic from reviewed M2 counts and prospective sample-size planning; not a new experiment or retrospective acceptance gate.",
    "source": "research/m2-coco512-results.md and thesis/tables/m2-t3.csv at 7f222fe",
    "bounds": {name: interval(k, n) for name, k, n in [
        ("T3_semantic_strength_0.2", 30, 30),
        ("T3_checked_strength_0.2", 27, 30),
        ("T3_semantic_strength_0.4", 21, 30),
        ("T3_checked_strength_0.4", 17, 30),
        ("T4_false_attribution", 0, 29), ("T5_false_match", 0, 27),
        ("clean_negative_each_cell", 0, 300),
        ("clean_positive", 299, 300), ("clean_joint_quality", 298, 300),
    ]},
    "zero_error_n_for_one_sided_upper_bound": {
        str(p): math.ceil(math.log(0.05) / math.log1p(-p))
        for p in [0.01, 0.001, 0.0001, 0.000001]
    },
    "zero_error_n_for_three_simultaneous_cells_bonferroni": {
        str(p): math.ceil(math.log(0.05 / 3) / math.log1p(-p)) for p in [0.01, 0.001]
    },
    "hypothetical_32_independent_fair_bit_hamming_tail": {
        "radius_6": float(binom.cdf(6, 32, 0.5)),
        "radius_10": float(binom.cdf(10, 32, 0.5)),
        "warning": "Not the F5 false-positive probability: dependent semantic codes and soft scores do not satisfy this toy null model.",
    },
}
out = Path(__file__).with_name("planning-statistics.json")
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
