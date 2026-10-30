"""Assemble the reviewed WP7 author bundles without losing their shared contracts."""
from pathlib import Path
import re
import os

rd = Path(__file__).resolve().parents[1]
sources = ["writer-routes.md", "security-routes.md", "allocation-baselines.md"]
intro = """# WP7 — Ten article routes

STATUS: COMPLETE

JUDGMENT: Article opportunity is broader than a new RL algorithm. The most promising forecast frame (R10) is a component-separation study with RL only a small arm; its compatibility and full cost remain unknown. The actionable shortlist offers narrower falsification screens, not demonstrated publishable results. R08 and R09 are explicit no-RL alternatives, with different costs and evidence maturity; their probabilities are not a matched-investment comparison with new RL research.

| Route | Main question | Requires F6 success? | Target |
|---|---|---|---|
| R01 | State/order writer mechanism | No, but feasibility is more plausible after GO | TIFS |
| R02 | Precise bounded RL-versus-gradient null | No | TIFS |
| R03 | Value of paid observations | No, but needs a useful feasible action menu | TIFS |
| R04 | Binding-conditioned attacker | No | TIFS |
| R05 | Constrained removal/forgery game | No | TIFS |
| R06 | Exact observation-conflict witnesses | No | TIFS |
| R07 | Decision-safe sequential experiment allocation | No | Pattern Recognition Letters |
| R08 | Existing negative-result article, no RL | No | TIFS; Access fit discussed separately |
| R09 | Frozen F6 article, no RL | Outcome determines defensible frame | TIFS |
| R10 | Compatible reader/carrier/objective contrasts; small RL arm | No | TIFS |

SOURCE: [Primary venue checks](articles/venue-status.md) establish scope and article-type fit. Current exact JCR and SJR category/year quartiles remain UNKNOWN after the logged retrieval attempts. Historical indexed 2024 SJR labels are explicitly dated, not current Q1 certification. IEEE Access is an unforecast fallback, not an interchangeable outlet for the TIFS probabilities.

The three shared contracts below belong to the route sections that follow. Each route supplies its claim, inspected closest works, evidence and cost dependencies, five objections, frozen probability chain, and decoration test. The underlying author bundles are retained as provenance; they are not additional routes. Quantities labelled JUDGMENT are subjective and uncalibrated. No new scientific result or F6 outcome is used.

"""
contexts = []
routes = {}
for name in sources:
    source = rd / "articles" / name
    raw = source.read_text(encoding="utf-8")
    def rebase(match):
        label, target = match.groups()
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            return match.group(0)
        path, sep, anchor = target.partition("#")
        resolved = (source.parent / path).resolve()
        if not resolved.exists():
            raise ValueError(f"Missing local link: {source}: {target}")
        relative = Path(os.path.relpath(resolved, rd)).as_posix()
        return f"[{label}]({relative}{sep}{anchor})"
    raw = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", rebase, raw)
    parts = re.split(r"(?=^## R\d{2}\b)", raw, flags=re.M)
    shared = parts[0].split("\n", 1)[1].strip()
    shared = re.sub(r"^## ", "### ", shared, flags=re.M)
    contexts.append(f"## Shared contract: {name}\n\n{shared}\n")
    for section in parts[1:]:
        key = re.match(r"## (R\d{2})", section).group(1)
        if key in routes:
            raise ValueError(key)
        routes[key] = section.strip() + "\n"
assert sorted(routes) == [f"R{i:02d}" for i in range(1, 11)]
output = intro + "\n".join(contexts) + "\n" + "\n".join(routes[k] for k in sorted(routes))
(rd / "07-article-routes.md").write_text(output, encoding="utf-8", newline="\n")
print(f"Assembled {len(routes)} routes, {len(output.splitlines())} lines; local links exist.")
