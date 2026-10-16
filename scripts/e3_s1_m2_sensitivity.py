"""Post-hoc source-cluster sensitivity of retained E3-S1 M2 endpoints.

Reads only the declared endpoints JSON, never images or detector inputs. S/J
are the saved outputs of frozen m1b_e3_s1_analysis.predicates(), not redefined
detector rules. The original primary analysis is left unchanged.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from math import comb
from pathlib import Path
import subprocess

METHODS = ("e3-s1", "v5-r3")
STRENGTHS = ("0.1", "0.2")
SEEDS = {3, 4, 5}
GATES = {
    "reported_primary": ("admitted", "strict_quality", "Q", "H", "F"),
    "without_clean_exact_H": ("admitted", "strict_quality", "Q", "F"),
    "ungated_S": (),
    "ungated_J": (),
}


def paired(a, b):
    if a.keys() != b.keys() or len(a) != 300:
        raise ValueError("expected the same 300 source IDs in both methods")
    wins = sum(a[u] and not b[u] for u in a)
    losses = sum(b[u] and not a[u] for u in a)
    discordant = wins + losses
    # Exact one-sided paired sign/McNemar test, E3 > v5, p0 = 1/2.
    p = sum(comb(discordant, k) for k in range(wins, discordant + 1)) / 2**discordant
    return dict(n=len(a), e3_success=sum(a.values()), v5_success=sum(b.values()),
                e3_only=wins, v5_only=losses,
                both=sum(a[u] and b[u] for u in a),
                neither=sum(not a[u] and not b[u] for u in a),
                difference_pp=100 * (wins-losses) / len(a),
                exact_one_sided_p=p)


def analyse(data):
    clean, calls, clean_summary, availability = {}, {}, {}, {}
    if data["analysis_version"] != "e3-s1-analysis-v1":
        raise ValueError("unexpected frozen analysis version")
    for method in METHODS:
        source = data["methods"][method]
        rows = source["clean_coverage"]["per_source"]
        clean[method] = {row["uid"]: row for row in rows}
        if len(rows) != 300 or len(clean[method]) != 300:
            raise ValueError("clean rows must contain 300 unique sources")
        for row in rows:
            if any(type(row[k]) is not bool for k in GATES["reported_primary"]):
                raise ValueError("missing or nonboolean clean endpoint")
            if row["primary_clean_admission"] != all(row[k] for k in GATES["reported_primary"]):
                raise ValueError("retained clean admission differs from frozen conjunction")
        clean_summary[method] = dict(
            counts={k: sum(row[k] for row in rows) for k in GATES["reported_primary"]},
            primary_admitted=sum(row["primary_clean_admission"] for row in rows),
            without_H_admitted=sum(all(row[k] for k in GATES["without_clean_exact_H"]) for row in rows),
            exact_H_failed=sum(not row["H"] for row in rows),
            H_is_only_primary_gate_failure=sum(not row["H"] and all(row[k] for k in GATES["without_clean_exact_H"]) for row in rows))
        calls[method] = {}
        availability[method] = {}
        for strength in STRENGTHS:
            by_source = defaultdict(dict)
            raw = source["t3"][strength]["raw_read_results"]
            for row in raw:
                uid, seed = row["uid"], row["seed"]
                if uid not in clean[method] or seed not in SEEDS or seed in by_source[uid]:
                    raise ValueError("unexpected or duplicate source-seed")
                if type(row.get("available")) is not bool:
                    raise ValueError("missing availability status")
                if row["available"] and any(type(row.get(k)) is not bool for k in ("S", "J")):
                    raise ValueError("available call lacks boolean endpoints")
                by_source[uid][seed] = row
            if len(raw) != 900 or by_source.keys() != clean[method].keys() or any(set(v) != SEEDS for v in by_source.values()):
                raise ValueError("incomplete fixed three-seed grid")
            calls[method][strength] = by_source
            availability[method][strength] = dict(
                planned_calls=len(raw), unavailable_calls=sum(not row["available"] for row in raw),
                sources_with_unavailable_calls=sum(any(not row["available"] for row in group.values()) for group in by_source.values()))
    comparisons = {}
    for strength in STRENGTHS:
        comparisons[strength] = {}
        for name, gates in GATES.items():
            rule = "J" if name == "ungated_J" else "S"
            states = {}
            for method in METHODS:
                states[method] = {
                    uid: all(row[k] for k in gates) and
                    sum(call.get(rule) is True for call in calls[method][strength][uid].values()) >= 2
                    for uid, row in clean[method].items()}
            result = paired(states[METHODS[0]], states[METHODS[1]])
            if name == "reported_primary":
                old = data["primary"][strength]
                for k in ("n", "e3_success", "v5_success", "e3_only", "v5_only", "both", "neither"):
                    if result[k] != old[k]:
                        raise ValueError(f"retained primary does not reproduce: {strength} {k}")
            comparisons[strength][name] = result
    # Descriptive post-hoc p values; no prospectively confirmatory testing claim.
    return dict(label="post-hoc sensitivity; fixed 300-source retained cohort",
                seed_rule="at least 2 of seeds 3, 4, 5; source is paired unit",
                predicates="frozen e3-s1-analysis-v1 saved S/J; no detector rerun",
                missing_rule="frozen planned-denominator rule: unavailable calls are not successes; never excluded",
                availability=availability, clean=clean_summary, comparisons=comparisons)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("endpoints", type=Path)
    parser.add_argument("--output", type=Path, help="new JSON path; will not overwrite")
    args = parser.parse_args()
    raw = args.endpoints.read_bytes()
    result = analyse(json.loads(raw))
    result["provenance"] = dict(
        input=str(args.endpoints.resolve()), input_sha256=hashlib.sha256(raw).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        checkout_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip())
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as output:
            output.write(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
