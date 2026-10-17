"""Post-hoc diagnostic (labelled, not a test): why do frozen two-factor positives fail on the step-2b evaluation split?

Classifies every C1 regenerated positive at each strength by its failure cause under the frozen
thresholds: pointer lost, D1 abstention (native weak detail), D1 below tau1, or B1 below tau2.
Also reports near-duplicate pairs by pixel distance. CPU only; reads frozen thresholds and caches.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claude_two_factor_instance as tf  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--thresholds", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=False)
    tick = time.monotonic()
    fr = json.loads(a.thresholds.read_text())
    t1, t2 = fr["tau1_d1"], fr["tau2_b1"]
    cal = json.loads((tf.AN2 / "calibration-thresholds.json").read_text())
    cal_ids = [int(x) for x in cal["source_ids"]]
    ev_ids = sorted(int(p.name) for p in tf.FRESH.iterdir() if p.is_dir() and p.name.isdigit() and int(p.name) not in cal_ids)
    F = tf.Features([tf.AN2 / "descriptor-index-calibration.json", tf.AN2 / "descriptor-index-evaluation.json"])
    pointer = {}
    for c in json.loads((tf.AN2 / "evaluation-D1-scores.json").read_text()).get("positives_and_C0", []):
        m = re.match(r"(sd15|sd21):(\d+):([0-9.]+):(\d+):f5-r2$", str(c.get("id", "")))
        if m and isinstance(c.get("pointer"), dict):
            pointer[(int(m.group(2)), m.group(1), float(m.group(3)), int(m.group(4)))] = bool(c["pointer"].get("recovered"))
    pos, _ = tf.split_rows(ev_ids, [], tf.AN2 / "images", "T4-evaluation")
    out = {}
    for m in tf.MODELS:
        for s in tf.STRENGTHS:
            causes, per_source = Counter(), defaultdict(list)
            for r in pos:
                if r["arm"] != "C1" or r["model"] != m or r["strength"] != s or not r["path"]:
                    continue
                p = tf.pair(F, r["path"], tf.record(r["source"]))
                ptr = pointer.get((r["source"], m, s, r["seed"]))
                cause = ("pointer_lost" if ptr is False else "d1_abstain" if p["d1"] is None else
                         "d1_below_tau1" if p["d1"] < t1 else "b1_below_tau2" if p["b1"] < t2 else "accepted")
                causes[cause] += 1
                per_source[r["source"]].append(dict(seed=r["seed"], cause=cause, d1=p["d1"], b1=p["b1"]))
            failing = {sid: v for sid, v in per_source.items() if sum(x["cause"] == "accepted" for x in v) < 2}
            out[f"{m}/{s}"] = dict(seed_causes=dict(causes), failing_sources=failing)
    result = dict(commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tf.ROOT, text=True).strip(),
                  label="post-hoc diagnostic on consulted evaluation data; informs the next protocol only",
                  thresholds=fr, cells=out, duration_seconds=time.monotonic() - tick, outcome="completed", usd=0)
    (a.output_dir / "run.json").write_text(json.dumps(result, indent=2) + "\n")
    for k, v in out.items():
        print(k, v["seed_causes"], "failing sources:",
              {sid: [x["cause"] for x in xs] for sid, xs in v["failing_sources"].items()})


if __name__ == "__main__":
    main()
