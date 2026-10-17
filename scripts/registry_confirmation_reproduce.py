"""Reproduce frozen round-3 development scoring; no held-out inputs accepted."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()
    pins = json.loads((ROOT / "research/registry-confirmation/source-pins.json").read_text())
    for rel, digest in pins["files"].items():
        if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != digest:
            raise ValueError("Frozen source mismatch: " + rel)
    m = json.loads((BUILD / "agent-logs/round3-data-manifest.json").read_text())
    if m["schema"] != "round3-development-data-manifest-v1" or m["data_split"] != "development only; all40 evaluation":
        raise ValueError("Only the round-3 development manifest is accepted")
    expected = {"fresh_dir": BUILD / "dev-runs/20261017-round3-registry-fresh",
                "canonical_dir": BUILD / "assets/registry-round3-20261017/canonical",
                "analysis_dir": BUILD / "dev-runs/20261017-round3-registry-analysis"}
    for k, p in expected.items():
        if Path(m[k]).resolve() != p.resolve():
            raise ValueError("Unexpected development path: " + k)
    if Path(m["pointer_scores"]).resolve().parent != expected["analysis_dir"].resolve():
        raise ValueError("Unexpected pointer path")
    for p in m["descriptor_indexes"]:
        if Path(p).resolve().parent != expected["analysis_dir"].resolve():
            raise ValueError("Unexpected descriptor path")
    cmd = [sys.executable, str(ROOT / "scripts/m1b_registry_scorer.py"), "--mode", "evaluate",
           "--frozen", str(ROOT / "research/claude-round3-frozen-20261017.json"),
           "--output-dir", str(a.output_dir), "--fresh-dir", m["fresh_dir"],
           "--canonical-dir", m["canonical_dir"], "--pointer-scores", m["pointer_scores"],
           "--t4-glob", str(expected["analysis_dir"] / "images/T4-evaluation-*.png")]
    for p in m["descriptor_indexes"]: cmd += ["--index", p]
    cmd += ["--sources", *map(str, m["source_ids"]), "--near", *m["look_alike_ids"]]
    subprocess.run(cmd, cwd=ROOT, check=True)
    r = json.loads((a.output_dir / "run.json").read_text())
    s = r["summary"]["round3"]
    for model in ("sd15", "sd21"):
        assert s["cells"][model + "/0.2"]["F_R_source_majority"] == 39
        assert s["cells"][model + "/0.4"]["F_R_source_majority"] == 30
    for family, n in (("wrong_source", 59280), ("T4", 80), ("look_alike_different", 40)):
        assert s["negatives"][family]["n"] == n
        assert s["negatives"][family]["accepts"] == 0
    assert s["negatives"]["synthetic_sibling"]["accepted_clusters"] == ["sib:11", "sib:12"]
    assert r["plan_view"]["E1_E2_pass"] is True
    assert r["plan_view"]["negatives"]["synthetic_ambiguous"]["accepted_clusters"] == ["sib:11", "sib:12"]
    assert r["plan_view"]["E2_total"] == 0
    (a.output_dir / "reproduction-checks.json").write_text(json.dumps({"status": "passed", "scope": "round3 development only", "synthetic_ambiguity": "plan_view classifies accepted synthetic pairs as ambiguous"}, indent=2) + "\n")

if __name__ == "__main__": main()
