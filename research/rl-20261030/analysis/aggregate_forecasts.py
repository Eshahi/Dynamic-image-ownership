"""Validate and summarize five frozen subjective elicitation records (stdlib only)."""
from __future__ import annotations

import hashlib
import json
import re
import statistics
from pathlib import Path

RD = Path(__file__).resolve().parents[1]
FD = RD / "forecasts"
SCENARIOS = ("GO", "FAIL", "RESOURCE_STOP")
CANDIDATES = ("C03", "C04", "C09", "C18", "OVERALL")
METRICS = ("A1", "A2", "A3", "A4", "B1", "B2", "B3", "FUTURE_ACCEPT", "OWN_SUCCESS")
EXTRA_ROUTES = ("R02", "R05", "R06", "R08", "R09", "R10")
B_METRICS = ("B1", "B2", "B3", "FUTURE_ACCEPT")
INHERIT = {"R01": "C03", "R03": "C04", "R04": "C09", "R07": "C18"}


def check_triple(value, allow_null, label):
    if value is None:
        assert allow_null, f"Unexpected null: {label}"
        return
    assert not allow_null, f"Expected structural N/A: {label}"
    assert isinstance(value, list) and len(value) == 3, label
    assert all(type(x) in (int, float) and 0 <= x <= 1 for x in value), label
    assert value == sorted(value), f"Unordered quantiles: {label}"


def summarize(values):
    if values[0] is None:
        assert all(x is None for x in values)
        return None
    return {
        "median_quantiles": [statistics.median(x[i] for x in values) for i in range(3)],
        "central_range": [min(x[1] for x in values), max(x[1] for x in values)],
        "outer_envelope": [min(x[0] for x in values), max(x[2] for x in values)],
        "individual_quantiles": values,
    }


def summarize_products(values):
    if values[0] is None:
        assert all(x is None for x in values)
        return None
    return {"median": statistics.median(values), "range": [min(values), max(values)], "individual_central_products": values}


def pct(x):
    return f"{100*x:.2f}".rstrip("0").rstrip(".") + "%"


def describe(value):
    if value is None:
        return "N/A | N/A | N/A"
    q = value["median_quantiles"]
    r = value["central_range"]
    return f"{pct(q[1])} | {pct(r[0])}–{pct(r[1])} | {pct(q[0])} / {pct(q[1])} / {pct(q[2])}"


def main():
    records, provenance = [], []
    freeze = (FD / "PACKET-FREEZE.md").read_text(encoding="utf-8-sig")
    for name, sha in re.findall(r"- `([^`]+)`: `([a-f0-9]{64})`", freeze):
        assert hashlib.sha256((FD / name).read_bytes()).hexdigest() == sha, f"Packet changed: {name}"
    assert len(re.findall(r"- `([^`]+)`: `([a-f0-9]{64})`", freeze)) == 4
    for i in range(1, 6):
        path = FD / f"F{i}.md"
        raw = path.read_text(encoding="utf-8-sig")
        blocks = re.findall(r"```json\s*(.*?)\s*```", raw, re.S)
        assert len(blocks) == 1, f"Expected one JSON block: {path.name}"
        record = json.loads(blocks[0])
        assert record["forecaster"] == f"F{i}"
        assert set(record["scenario_estimates"]) == set(SCENARIOS)
        assert set(record["route_estimates"]) == set(SCENARIOS)
        for scenario in SCENARIOS:
            estimates = record["scenario_estimates"][scenario]
            assert set(estimates) == set(CANDIDATES), (i, scenario)
            for candidate in CANDIDATES:
                assert set(estimates[candidate]) == set(METRICS), (i, scenario, candidate)
                for metric in METRICS:
                    na = (candidate in ("C09", "C18") and metric in ("A2", "A3", "A4")) or (candidate == "OVERALL" and metric == "OWN_SUCCESS")
                    check_triple(estimates[candidate][metric], na, (i, scenario, candidate, metric))
            assert estimates["C03"]["A2"] == estimates["C03"]["OWN_SUCCESS"], (i, scenario, "C03 own event")
            routes = record["route_estimates"][scenario]
            assert set(routes) == set(EXTRA_ROUTES)
            for route in EXTRA_ROUTES:
                assert set(routes[route]) == set(B_METRICS), (i, scenario, route)
                for metric in B_METRICS:
                    check_triple(routes[route][metric], False, (i, scenario, route, metric))
        records.append(record)
        provenance.append({"forecaster": f"F{i}", "file": str(path.relative_to(RD)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

    result = {"interpretation": "Subjective, uncalibrated coordinatewise summaries, not pooled posterior probabilities or confidence intervals.", "provenance": provenance, "candidates": {}, "routes": {}}
    for scenario in SCENARIOS:
        result["candidates"][scenario] = {}
        for candidate in CANDIDATES:
            rows = [r["scenario_estimates"][scenario][candidate] for r in records]
            out = {metric: summarize([r[metric] for r in rows]) for metric in METRICS}
            out["DEFENSE_CHAIN"] = summarize_products([None if r["A2"] is None else r["A2"][1]*r["A3"][1]*r["A4"][1] for r in rows])
            out["CURRENT_ACCEPT_CHAIN"] = summarize_products([r["B2"][1]*r["B3"][1] for r in rows])
            result["candidates"][scenario][candidate] = out
        result["routes"][scenario] = {}
        for n in range(1, 11):
            route = f"R{n:02d}"
            if route in INHERIT:
                parent = result["candidates"][scenario][INHERIT[route]]
                out = {metric: parent[metric] for metric in (*B_METRICS, "CURRENT_ACCEPT_CHAIN")}
                out["inherited_from"] = INHERIT[route]
            else:
                rows = [r["route_estimates"][scenario][route] for r in records]
                out = {metric: summarize([r[metric] for r in rows]) for metric in B_METRICS}
                out["CURRENT_ACCEPT_CHAIN"] = summarize_products([r["B2"][1]*r["B3"][1] for r in rows])
            result["routes"][scenario][route] = out
    (FD / "aggregate.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Full forecast aggregation", "", "DERIVED from five frozen subjective, uncalibrated forecasts. Central range is min–max of individual p50s. The quantile triplet is the coordinatewise median of five p10/p50/p90 triplets; it is not a pooled posterior interval. Raw records and hashes are in aggregate.json. No scenario weighting.", ""]
    for scenario in SCENARIOS:
        lines += [f"## {scenario}", "", "| Candidate | Item | Median p50 | Individual p50 range | Median p10 / p50 / p90 |", "|---|---|---:|---:|---:|"]
        for candidate, row in result["candidates"][scenario].items():
            for metric in METRICS:
                lines.append(f"| {candidate} | {metric} | {describe(row[metric])} |")
        lines += ["", "| Route | Item | Median p50 | Individual p50 range | Median p10 / p50 / p90 |", "|---|---|---:|---:|---:|"]
        for route, row in result["routes"][scenario].items():
            for metric in B_METRICS:
                lines.append(f"| {route} | {metric} | {describe(row[metric])} |")
        lines += ["", "Conditional central products, computed within each forecaster before aggregation. No quantile products, no extra A1 or B1 factor.", "", "| Candidate/route | Chain | Median central product | Range of central products |", "|---|---|---:|---:|"]
        for kind in ("candidates", "routes"):
            for item, row in result[kind][scenario].items():
                for chain in ("DEFENSE_CHAIN", "CURRENT_ACCEPT_CHAIN"):
                    if chain not in row:
                        continue
                    v = row[chain]
                    text = "N/A | N/A" if v is None else f"{pct(v['median'])} | {pct(v['range'][0])}–{pct(v['range'][1])}"
                    lines.append(f"| {item} | {chain} | {text} |")
        lines.append("")
    (FD / "aggregate-tables.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"forecasters": len(records), "scenarios": len(SCENARIOS), "packet_hashes_verified": 4, "triples_per_forecaster": 186, "structural_nulls_per_forecaster": 21, "outputs": ["forecasts/aggregate.json", "forecasts/aggregate-tables.md"]}))


if __name__ == "__main__":
    main()
