"""Insert a readable summary of the validated saved forecast aggregation."""
import json
from pathlib import Path

rd = Path(__file__).resolve().parents[1]
data = json.loads((rd / "forecasts/aggregate.json").read_text(encoding="utf-8"))
scenarios = ("GO", "FAIL", "RESOURCE_STOP")


def pct(x):
    return f"{100*x:.2f}".rstrip("0").rstrip(".") + "%"


def cell(v):
    if v is None:
        return "N/A"
    return f"{pct(v['median_quantiles'][1])} ({pct(v['central_range'][0])}–{pct(v['central_range'][1])})"


def chain(v):
    if v is None:
        return "N/A"
    return f"{pct(v['median'])} ({pct(v['range'][0])}–{pct(v['range'][1])})"


lines = ["## Results", "", "All five records passed schema, quantile, structural-N/A and unchanged-packet checks: 186 probability triples plus 21 structural nulls per forecaster, across three scenarios. Records: [F1](forecasts/F1.md), [F2](forecasts/F2.md), [F3](forecasts/F3.md), [F4](forecasts/F4.md), [F5](forecasts/F5.md). Parenthesized ranges below are **individual p50 ranges**, not uncertainty intervals.", "", "| F6 scenario | Overall A2: defensive development gain | Full A2→A3→A4 central chain | Overall future RL-informed article |", "|---|---:|---:|---:|"]
for s in scenarios:
    row = data["candidates"][s]["OVERALL"]
    lines.append(f"| {s} | {cell(row['A2'])} | {chain(row['DEFENSE_CHAIN'])} | {cell(row['FUTURE_ACCEPT'])} |")
lines += ["", "The full chain requires both excluded-family transfer and fresh-source confirmation after the stringent development result. Its small value is not a probability that RL can never improve any endpoint. The broader publication event can succeed through an informative null, attack or allocation result and therefore need not track the defensive chain.", "", "The elicited uncertainty within each forecaster is much wider than the central inter-forecaster spread:", "", "| F6 scenario | Event | Coordinatewise median p10 / p50 / p90 |", "|---|---|---:|"]
for s in scenarios:
    for m in ("A2", "FUTURE_ACCEPT"):
        q = data["candidates"][s]["OVERALL"][m]["median_quantiles"]
        lines.append(f"| {s} | Overall {m} | {' / '.join(pct(x) for x in q)} |")
lines += ["", "There is no corresponding elicited quantile triplet for the product chain: multiplying quantiles would fabricate one.", "", "## Candidate comparison", "", "A1 is full-campaign completion. OWN_SUCCESS is each candidate's distinct utility event: C03 defensive gain, C04 total-cost saving, C09 stronger valid forgery discovery, C18 prospective allocation saving. These columns must not be pooled as a common success rate.", "", "| Scenario | Candidate / venue | A1 completion | A2 defensive gain | OWN_SUCCESS | Future acceptance |", "|---|---|---:|---:|---:|---:|"]
for s in scenarios:
    for c in ("C03", "C04", "C09", "C18"):
        row = data["candidates"][s][c]
        venue = "PRL" if c == "C18" else "TIFS"
        lines.append(f"| {s} | {c} / {venue} | {cell(row['A1'])} | {cell(row['A2'])} | {cell(row['OWN_SUCCESS'])} | {cell(row['FUTURE_ACCEPT'])} |")
lines += ["", "All conditional A3/A4, novelty B1, desk B2 and review B3 quantiles for every candidate and overall are in the [full tables](forecasts/aggregate-tables.md); no metric is omitted from the elicitation.", "", "## No-RL alternatives and article-route comparison", "", "The existing negative article R08 costs zero new science hours in this forecast. R09 uses only the separately frozen 75-hour F6 scenario. The prospective RL routes permit substantial new work, so their larger future probabilities do not by themselves establish a better return on time or money.", "", "| Scenario | Route | Current-evidence B2×B3 central chain | Direct future acceptance |", "|---|---|---:|---:|"]
for s in scenarios:
    for r in ("R08", "R09"):
        row = data["routes"][s][r]
        lines.append(f"| {s} | {r} / TIFS | {chain(row['CURRENT_ACCEPT_CHAIN'])} | {cell(row['FUTURE_ACCEPT'])} |")
lines += ["", "| Route / named venue | GO future acceptance | FAIL future acceptance | RESOURCE_STOP future acceptance |", "|---|---:|---:|---:|"]
for i in range(1, 11):
    r = f"R{i:02d}"
    venue = "PRL" if r == "R07" else "TIFS"
    cells = " | ".join(cell(data["routes"][s][r]["FUTURE_ACCEPT"]) for s in scenarios)
    lines.append(f"| {r} / {venue} | {cells} |")
lines += ["", "## Where the judgments differ", "", "The forecasters agree on a plausible state-dependent or information-dependent mechanism but see no measured action advantage beyond strong controls. Their probabilities differ in how much credit they give that possibility and to a useful narrower paper when the strict utility event fails. F1–F5 each explain their reference classes and strongest simpler-method alternative in the raw memo.", "", "A concrete scenario disagreement is completion: F1 leaves A1 unchanged across F6 branches because RESOURCE_STOP has no specified cause; F2–F5 apply a modest feasibility discount for shared resource uncertainty. Both are explicit judgments, not observations of F6. For the zero-new-science R08 article, F1 treats the fixed evidence frame as invariant, while F4/F5 allow contextual framing to affect editorial prospects. The report preserves these differences instead of averaging away their reasons.", "", "Across the panel, the main unresolved quantities are controllable action advantage, full matched comparator and confirmation cost, all-source quality/negative performance, external binding labels, and residual novelty/significance. Most forecasters give R10's factor-separation study more article potential than a positive writer-policy claim, while recognizing that valid matched factorial arms may be infeasible. C18 is more buildable but still faces strong classical allocation controls. A broad interval is the appropriate statement of this missing evidence; agreement among the five does not calibrate the estimates.", "", "**JUDGMENT:** these forecasts support bounded falsification or diagnostic screens before any full RL program. They do not support replacing the frozen F6 study, promising a Q1 paper, or funding a 600-hour campaign on the strength of a short pilot. WP7 develops claim-specific routes; WP8 chooses at most two prospective screens with explicit operating conditions and later decision gates."]
path = rd / "06-probabilities.md"
original = path.read_text(encoding="utf-8-sig")
original = original.replace("This report is assembled during elicitation. Its numerical results and completion record are inserted only after all five bounded forecasts arrive and validation passes.", "All five forecasts are complete and validated. The frozen elicitation record is preserved unchanged; no scientific experiment or F6 observation was made.")
if "<!-- FORECAST_RESULTS -->" in original:
    assert original.count("<!-- FORECAST_RESULTS -->") == 1
    updated = original.replace("<!-- FORECAST_RESULTS -->", "\n".join(lines))
else:
    start = original.index("## Results\n")
    end = original.index("\n## Boundaries of use", start)
    updated = original[:start] + "\n".join(lines) + "\n" + original[end:]
path.write_text(updated.rstrip() + "\n", encoding="utf-8")
print("Inserted validated forecast summary into 06-probabilities.md")
