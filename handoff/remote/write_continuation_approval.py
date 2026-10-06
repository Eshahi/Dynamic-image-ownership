"""Write the approval for held-out continuation 1 (run from /workspace/m1b with the venv python).

The owner approved this in chat on 2026-10-06. Asked where the final run should continue, they answered
"Move to the rented GPU": stop the laptop run cleanly, then resume the same run on the rented GPU from its
journal, with the held-out photos allowed on the rented server. The original approval
(m1b-coco512-approval.json) also allows up to 2 continuations that reuse the run's journal.

Usage: python /root/write_continuation_approval.py <execution-manifest.json>
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, "scripts")
import m1b_coco512_worker as W  # noqa: E402

sys.path.insert(0, "C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/_runtime")
from thesis_agents.compute import approval_check  # noqa: E402

m = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
plan = json.loads(Path("research/m1b-coco512-test-continuation-1.m1b-plan.json").read_text(encoding="utf-8"))
now = datetime.now(timezone.utc).replace(microsecond=0)
digest = W.object_digest(m)
approval = dict(
    schema_version="1.0", experiment_id=m["experiment_id"], run_id=m["run_id"], execution_target="local",
    manifest_sha256=digest, decision="approve", timestamp=now.isoformat().replace("+00:00", "Z"),
    expires_at=(now + timedelta(days=7)).isoformat().replace("+00:00", "Z"),
    max_seconds=m["budget"]["max_seconds"], max_usd=0, actor="Soroush",
    source_ref=("Continuation 1 of the approved run coco512-confirm-1, approved by Soroush in chat on 2026-10-06 "
                "(\"Move to the rented GPU\": stop the laptop run, resume the same run on the rented GPU from its journal; "
                "held-out photos allowed on the rented server). Within the original approval's allowance of up to 2 "
                f"continuations. File written by the agent at the owner's instruction. Manifest {digest[:16]}."))
approval_check(approval, m)
out = Path(plan["approval_path"])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(approval, indent=1) + "\n", encoding="utf-8")
print("approval written and checked:", out, digest[:16])
