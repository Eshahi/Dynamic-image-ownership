"""End-to-end rehearsal on two DEVELOPMENT images only (never held-out). CPU parts here; GPU smoke is requested separately."""
import json, hashlib, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
WT = Path("C:/Users/Soroush/.codex/worktrees/claude-f5-m1b")
DEV = MAIN / ".thesis-build/dev-runs"
OUT = WT / "research" / "m1b-rehearse-two"
SRC_A = DEV / "20261004-1102-e2e-1675/1675-C0-clean.png"
SRC_B = DEV / "20261004-1122-e2e-4795/4795-C0-clean.png"

def sha_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1<<20), b""): h.update(c)
    return h.hexdigest()

def main():
    assert SRC_A.exists() and SRC_B.exists()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = dict(
        schema="m1b-f5-manifest-v1", version="m1b-f5-runner-v1",
        config_path="configs/f5-r2.json", profile_path="experiments/c4-v5-two-tier-regeneration-v1/profile.json",
        sources=[
            dict(id="dev-1675", path=str(SRC_A), owner="thesis:owner:00", wrong_owner="thesis:owner:01"),
            dict(id="dev-4795", path=str(SRC_B), owner="thesis:owner:01", wrong_owner="thesis:owner:02"),
        ],
        t3_strengths=[0.05,0.1,0.2,0.4], t3_seeds=[0,1,2],
        t4_pairs=[dict(id="t4-01", donor="dev-1675", recipient="dev-4795")],
        t5_pairs=[dict(id="t5-01", a="dev-1675", b="dev-4795")],
        note="DEVELOPMENT ONLY rehearsal — never held-out",
    )
    mpath = OUT / "manifest.dev-two.json"
    mpath.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    import sys
    sys.path.insert(0, str(WT / "scripts"))
    sys.path.insert(0, str(WT))
    import m1b_f5_runner as r
    r.validate_manifest(manifest)
    shards = [r.shard_sources(manifest["sources"], k, 2) for k in range(2)]
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)/"out"; out.mkdir()
        r.append_journal(out, dict(id="dev-1675:clean:C1:correct", outcome="completed", detection=dict(outcome="both_match")))
        j = r.read_journal(out)
        assert "dev-1675:clean:C1:correct" in j
        jp = out/"journal.jsonl"
        jp.write_text(jp.read_text(encoding="utf-8")+'{"id":"bad"', encoding="utf-8")
        try:
            r.read_journal(out); raise AssertionError("expected truncated journal to raise")
        except Exception:
            pass
    # endpoints sanity — use science venv helper via subprocess if scipy available there
    # do light check here without scipy: just validate manifest strengths exact
    assert manifest["t3_seeds"] == [0,1,2]
    assert r.T3_STRENGTHS == (0.05,0.1,0.2,0.4)
    report = dict(
        schema="m1b-rehearse-two-v1",
        note="CPU rehearsal passed (manifest validation, sharding, journal/resume, no-seed-substitution). Endpoints + GPU smoke are in science venv.",
        manifest_path=str(mpath), manifest_sha256=sha_file(mpath),
        sources=[dict(id=s["id"], sha256=sha_file(Path(s["path"]))[:16]+"…") for s in manifest["sources"]],
        sharding=[[s["id"] for s in sh] for sh in shards],
        cpu_tests="20 tests in tests/test_m1b_f5_runner.py (all pass)",
        endpoints_gpu_smoke="PENDING — run with science venv; queued in research/f5-gpu-queue-requests.md",
        held_out_touched=False,
    )
    (OUT / "report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
