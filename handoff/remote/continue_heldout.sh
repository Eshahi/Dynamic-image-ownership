#!/bin/bash
# Held-out continuation 1 on the rented GPU. On the server: bash /root/continue_heldout.sh
# Needs /root/write_continuation_approval.py and /root/check_rerun.py (copied from handoff/remote/).
set -euo pipefail
cd /workspace/m1b
. /workspace/venv/bin/activate
W="W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build"
PARENT="$W/m1b-confirm/artifacts/M1b-test/coco512-confirm-1"
OUT=/workspace/m1b-confirm/continuation-1
mkdir -p "$OUT"
[ "$(git rev-parse --short HEAD)" = "e26bd4b" ] || { echo "HEAD is not e26bd4b"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "checkout not clean"; exit 1; }
python scripts/m1b_prepare_package.py manifest --plan research/m1b-coco512-test-continuation-1.m1b-plan.json \
  --run-id coco512-confirm-rerun-1 --max-seconds 28800 --out "$OUT/execution-manifest.json" > "$OUT/manifest-info.txt" 2>&1
python /root/write_continuation_approval.py "$OUT/execution-manifest.json"
python scripts/m1b_prepare_package.py rerun-check --approved "$PARENT/execution-manifest.json" \
  --approval "C:/Users/Soroush/thesis-approvals/m1b-coco512-approval.json" --new "$OUT/execution-manifest.json" \
  --previous-run "$PARENT" > "$OUT/rerun-check.txt" 2>&1 || { cat "$OUT/rerun-check.txt"; exit 1; }
python /root/check_rerun.py "$OUT/rerun-check.txt"
nohup setsid python "C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/dispatch_experiment.py" dispatch \
  "$OUT/execution-manifest.json" --repo . --artifacts "$W/m1b-confirm/artifacts" --execute \
  --approval "C:/Users/Soroush/thesis-approvals/m1b-coco512-continuation-1.json" > "$OUT/dispatch.log" 2>&1 < /dev/null &
echo "dispatcher started, pid $!"
