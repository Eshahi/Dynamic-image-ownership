"""f7c scoring on the server when the link is too slow to fetch 1.3 GB of images (2026-11-08).

--mode features (laptop): D1 and B1 of every distractor record, with the scorer's own Features class, plus each
                          file's SHA-256, written as gzipped JSON. B1 and D1 are all the frozen rule reads.
--mode score (server):    the unchanged f7c scorer (scripts/f7c_registry_score.py) with those precomputed distractor
                          features injected in place of the images; queries and records are computed on the server.
--mode check (server):    recompute features for a few uploaded distractor PNGs and compare with the laptop values.
"""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))


def setup(profile_run):
    import claude_two_factor_instance as tf
    if profile_run:
        tf.PROFILE_RUN = Path(profile_run)
    return tf


def vec(v):
    return None if v is None else [float(x) for x in v]


def features(a):
    tf = setup(None)
    import f7c_registry_score as s
    import f7_registry_test as t
    F = tf.Features([])
    rows = []
    for p in s.distractor_paths(a.assets):
        f = F.get(p)
        rows.append(dict(name=p.name, root=p.parent.name, sha256=t.sha256(p), D1=vec(f["D1"]), B1=vec(f["B1"])))
    with gzip.open(a.out, "wt", encoding="utf-8") as f:
        json.dump(dict(schema="f7c-distractor-features-v1", roots=list(s.DISTRACTOR_ROOTS), n=len(rows), rows=rows), f)
    print(len(rows), "distractors ->", a.out)


def load(path):
    import numpy as np
    with gzip.open(path, "rt", encoding="utf-8") as f:
        doc = json.load(f)
    return [dict(r, D1=None if r["D1"] is None else np.asarray(r["D1"]), B1=np.asarray(r["B1"])) for r in doc["rows"]]


def check(a):
    import numpy as np
    tf = setup(a.profile_run)
    F = tf.Features([])
    known = {r["name"]: r for r in load(a.features)}
    worst = 0.0
    for p in sorted(Path(a.check_dir).glob("*.png")):
        f, r = F.get(p), known[p.name]
        for k in ("D1", "B1"):
            if (f[k] is None) != (r[k] is None):
                raise SystemExit(f"{p.name} {k}: abstain differs")
            if f[k] is not None:
                worst = max(worst, float(np.max(np.abs(f[k] - r[k]))))
    print("checked", len(list(Path(a.check_dir).glob('*.png'))), "max abs difference", worst)


def score(a):
    tf = setup(a.profile_run)
    import f7c_registry_score as s
    import f7_registry_test as t
    rows = load(a.features)
    pseudo = [Path("distractor") / r["root"] / r["name"] for r in rows]
    sha = {str(p): r["sha256"] for p, r in zip(pseudo, rows)}
    real = t.sha256
    t.sha256 = lambda p: sha.get(str(p)) or real(p)
    scorer = s.Score(a.screen, [], pseudo)
    for p, r in zip(pseudo, rows):
        scorer.F.memo[str(p)] = dict(D1=r["D1"], B1=r["B1"], g64=None)
    started = datetime.now(timezone.utc).isoformat()
    result, out_rows = scorer.run()
    result["dropped_distractors"] = scorer.dropped_distractors
    a.out.mkdir(parents=True, exist_ok=False)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=Path(__file__).resolve().parent).stdout.strip() or a.commit
    (a.out / "rows.json").write_text(json.dumps(out_rows, indent=1, default=str))
    (a.out / "run.json").write_text(json.dumps(dict(protocol="research/f7-dual-carrier-20261102/REPLICATION-PROTOCOL.md",
        command=sys.argv, commit=commit, device="cpu (server)", usd="instance time", started_at_utc=started,
        finished_at_utc=datetime.now(timezone.utc).isoformat(), distractor_features=str(a.features),
        distractors=[str(p) for p in scorer.distractors], result=result), indent=1, default=str))
    print(json.dumps(dict(verdict=result["verdict"], gates=result["gates"]), indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("features", "check", "score"), required=True)
    ap.add_argument("--assets", type=Path, default=Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets"))
    ap.add_argument("--features", type=Path)
    ap.add_argument("--profile-run", type=Path)
    ap.add_argument("--check-dir", type=Path)
    ap.add_argument("--screen", type=Path)
    ap.add_argument("--commit", default="")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    dict(features=features, check=check, score=score)[a.mode](a)


if __name__ == "__main__":
    main()
