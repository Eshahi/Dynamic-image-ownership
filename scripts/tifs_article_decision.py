"""Prospective Round 2 article screen, pure JSON/statistics; no science imports.

These are fixed development margins, not significance/noninferiority tests.
The existing thesis decision is supplied, never overridden by this module.
"""
from __future__ import annotations

import statistics
import math


def gate(name, status, **detail):
    return dict(name=name, status=status, **detail)


def minimum(name, lower, upper, threshold):
    return gate(name, "pass" if lower >= threshold else "fail" if upper < threshold else "unknown",
                lower=lower, upper=upper, minimum=threshold)


def conjunction(gates):
    statuses = [g["status"] for g in gates]
    return "fail" if "fail" in statuses else "unknown" if "unknown" in statuses else "pass"


def disjunction(statuses):
    return "pass" if "pass" in statuses else "unknown" if "unknown" in statuses else "fail"


def evaluate(config, native, clean, negatives, threats, paired_metrics, thesis_verdict, inventory_complete):
    """Consume same saved-unit summaries used by main analysis, without image access.

    paired_metrics maps each arm to source-ordered clean metric dictionaries or
    None. Unknown comparisons can never be satisfied by dropping those sources.
    """
    spec = config["article_decision"]
    candidate, baseline = config["candidate"], spec["baseline"]
    cells = [c["id"] for c in config["cells"]]
    rules, n = config["decision"]["rules"], config["screen_n"]
    index = {(r["arm"], r["cell"], r["rule"]): r for r in native}
    clean_index = {r["arm"]: r for r in clean}
    viability = []
    for cell in cells:
        for rule in rules:
            row = index[baseline, cell, rule]
            viability.append(minimum(f"{rule}:{cell}:absolute", row["lower"], row["upper"], spec["baseline_absolute_min"]))
    for label, threshold in (("clean_F", spec["baseline_clean_F_min"]), ("strict_quality", n)):
        row = clean_index[baseline][label]
        viability.append(minimum(label, row["lower"], row["upper"], threshold))
    for row in negatives:
        if row["method"] == baseline:
            viability.append(gate(f"negative:{row['kind']}:{row['rule']}",
                "fail" if row["lower"] else "unknown" if row["missing"] else "pass"))
    for row in threats:
        if row["method"] == baseline and row["mode"] == "combined":
            counts = row["eligible_false_events"]
            viability.append(gate("threat:"+row["condition"], "fail" if counts["lower"] else
                "unknown" if row["quality_missing"] or counts["missing"] or row["pair_denominator"] != n else "pass"))
    # Explicit expected security inventory prevents an empty list being a pass.
    if sum(g["name"].startswith("negative:") for g in viability) != 4 or sum(g["name"].startswith("threat:") for g in viability) != 7:
        viability.append(gate("security_inventory", "unknown"))

    def comparison(left, right):
        retention = []
        superior_by_cell = []
        for cell in cells:
            superior = []
            for rule in rules:
                a, b = index[left, cell, rule], index[right, cell, rule]
                lo, hi = a["lower"]-b["upper"], a["upper"]-b["lower"]
                retention.append(minimum(f"{rule}:{cell}:retention", lo, hi, -spec["max_retention_loss"]))
                superior.append(minimum(f"{rule}:{cell}:gain", lo, hi, spec["retention_gain_min"]))
            if cell in config["decision"]["foreign_cells"]:
                superior_by_cell.append(dict(cell=cell, status=conjunction(superior), gates=superior))
        quality = []
        quality_edge = []
        for metric in ("lpips", "psnr_db"):
            pairs = list(zip(paired_metrics.get(left, []), paired_metrics.get(right, [])))
            values = [a[metric]-b[metric] for a,b in pairs if a is not None and b is not None
                      and type(a.get(metric)) in (int,float) and type(b.get(metric)) in (int,float)
                      and math.isfinite(a[metric]) and math.isfinite(b[metric])]
            median = statistics.median(values) if values else None
            full = len(pairs) == n and len(values) == n
            if metric == "lpips":
                ni = median <= spec["lpips_delta_max"] if full else None
                edge = median <= -spec["lpips_improvement_min"] if full else None
            else:
                ni = median >= -spec["psnr_loss_max_db"] if full else None
                edge = median >= spec["psnr_improvement_min_db"] if full else None
            for result, target in ((ni, quality), (edge, quality_edge)):
                target.append(gate(metric, "unknown" if result is None else "pass" if result else "fail",
                                   median_delta=median, observed=len(values), denominator=n))
        retention_edge = disjunction([r["status"] for r in superior_by_cell])
        quality_edge_status = conjunction(quality_edge)
        edge_status = disjunction([retention_edge, quality_edge_status])
        status = conjunction(retention + quality + [gate("prespecified_edge", edge_status)])
        return dict(left=left, right=right, status=status, retention=retention, quality_noninferiority=quality,
                    noninferiority_status=conjunction(retention+quality), strict_edge_status=edge_status,
                    retention_edge=retention_edge, gain_by_foreign_cell=superior_by_cell,
                    quality_edge=quality_edge_status, quality_superiority=quality_edge,
                    margin_role="fixed development thresholds; no inferential noninferiority claim")

    forward, reverse = comparison(candidate, baseline), comparison(baseline, candidate)
    viable = conjunction(viability)
    baseline_quality = conjunction([g for g in viability if g["name"] == "strict_quality"])
    baseline_security = conjunction([g for g in viability if g["name"].startswith(("negative:", "threat:", "security_inventory"))])
    parity_gates = [gate("inventory", "pass" if inventory_complete else "unknown")]
    for side in (forward, reverse):
        parity_gates.append(gate("noninferiority", side["noninferiority_status"]))
        edge = side["strict_edge_status"]
        parity_gates.append(gate("no_strict_edge", "unknown" if edge == "unknown" else "pass" if edge == "fail" else "fail"))
    parity_status = conjunction(parity_gates)
    parity = parity_status == "pass"
    flags = ["BOUND_CARRIER_ONLY_NOT_NOVEL"]
    if baseline_quality == "fail": flags.append("VINE_B_QUALITY_INELIGIBLE")
    if baseline_security == "fail": flags.append("VINE_B_SECURITY_SCREEN_FAIL")
    if parity: flags.append("NUMERICAL_PARITY")
    if thesis_verdict == "RESOURCE_STOP":
        label = "RESOURCE_STOP"
    elif not inventory_complete or thesis_verdict == "INCOMPLETE":
        label = "INCOMPLETE"
    elif thesis_verdict == "GO":
        if forward["status"] == "pass":
            label = "F6_GO_ARTICLE_CONDITIONAL_GO"
        elif viable == "pass" and reverse["status"] == "pass":
            label = "F6_GO_VINE_B_DOMINATES_ARTICLE_NO_GO"
        elif forward["status"] == "unknown" or viable == "unknown" or reverse["status"] == "unknown":
            label = "INCOMPLETE"
        else:
            label = "F6_GO_NO_ARTICLE_EDGE"
    elif viable == "pass":
        label = "F6_KILL_VINE_B_VIABLE_NOT_NOVEL"
    elif viable == "fail":
        label = "BOTH_FAIL"
    else:
        label = "INCOMPLETE"
    return dict(verdict=label, thesis_verdict=thesis_verdict, baseline_viability=viable,
                flags=flags, baseline_quality_status=baseline_quality, baseline_security_status=baseline_security,
                numerical_parity=parity, numerical_parity_status=parity_status,
                baseline_gates=viability, f6_over_vine_b=forward, vine_b_over_f6=reverse,
                novelty_status=spec["novelty_status"], human_quality_status="MISSING",
                binding_generalization="UNRESOLVED_WITHOUT_HUMAN_LABELS",
                scope="development comparative screen only; no fresh confirmation, security or publication approval",
                generic_bound_carrier_novelty="PREEMPTED; a VINE-B win is not an automatic article contribution")
