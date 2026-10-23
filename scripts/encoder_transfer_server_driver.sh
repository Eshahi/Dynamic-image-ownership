#!/usr/bin/env bash
# Stage-2a driver for the rented server (amendment 1d). Written by Claude (Opus 5.5), 2026-10-23,
# at the user's request: the server work must continue if the SSH connection drops.
#
# Run it inside tmux, so that it survives a lost SSH session:
#   tmux new -d -s stage2a "bash scripts/encoder_transfer_server_driver.sh <instance-start-utc> <hourly-usd>"
#
# It chains prepare -> smoke -> full stage-2a run (with its analysis) -> packed results, and is safe
# to start again at any point: every phase resumes from its journal and finished phases are skipped.
# Control files in $RUNS:
#   HOLD          set by the driver after three failures of one phase; it waits until the file is removed
#   BUGFIX_NOTE   provenance text passed as --bugfix-note after a committed implementation-only fix
#   FETCHED       written by Claude after copying the results home; the instance may then be stopped
#   STOP_DRIVER   asks the driver to exit at the next phase boundary
set -u
START="$1"
HOURLY="$2"
REPO=${REPO:-/workspace/thesis}
VENV=${VENV:-/workspace/venv}
ASSETS=${ASSETS:-/workspace/assets}
RUNS=${RUNS:-/workspace/runs}
MANIFEST=research/encoder-transfer-20261019/stage2a-config.json
SMOKE=$RUNS/stage2a-smoke
FULL=$RUNS/stage2a-full
LOG=$RUNS/driver.log
FETCH_WINDOW_HOURS=${FETCH_WINDOW_HOURS:-12}
mkdir -p "$RUNS"

note() { echo "$(date -u +%FT%TZ) $*" >> "$LOG"; }
status() {
  printf '{"utc":"%s","phase":"%s","detail":"%s","pid":%s}\n' "$(date -u +%FT%TZ)" "$1" "$2" "$$" > "$RUNS/driver-status.json.tmp"
  mv "$RUNS/driver-status.json.tmp" "$RUNS/driver-status.json"
}
outcome() { python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("outcome",""))' "$1/run.json" 2>/dev/null; }

run_phase() {
  local phase=$1 out=$2
  shift 2
  local attempt=0 rc=0
  while true; do
    [ -f "$RUNS/STOP_DRIVER" ] && { status stopped "stop requested before $phase"; note "stop requested"; exit 0; }
    attempt=$((attempt + 1))
    status "$phase" "attempt $attempt"
    note "phase $phase attempt $attempt"
    local extra=()
    [ -s "$RUNS/BUGFIX_NOTE" ] && extra=(--bugfix-note "$(cat "$RUNS/BUGFIX_NOTE")")
    ( cd "$REPO" && "$VENV/bin/python" scripts/encoder_transfer_test.py --manifest "$MANIFEST" --output-dir "$out" \
        --phase "$phase" --assets-root "$ASSETS" --instance-start-utc "$START" --hourly-usd "$HOURLY" "$@" "${extra[@]}" ) \
        >> "$RUNS/$phase.log" 2>&1
    rc=$?
    if [ $rc -eq 0 ]; then note "phase $phase done"; return 0; fi
    note "phase $phase failed with exit $rc; log tail:"
    tail -n 25 "$RUNS/$phase.log" >> "$LOG"
    if tail -n 60 "$RUNS/$phase.log" | grep -q "Compute budget exhausted"; then
      status budget_exhausted "$phase"; note "budget exhausted"; return 2
    fi
    if [ $attempt -ge 3 ]; then
      touch "$RUNS/HOLD"
      status hold "$phase failed $attempt times; waiting for Claude to fix and remove HOLD"
      note "holding after $attempt failures"
      while [ -f "$RUNS/HOLD" ]; do sleep 60; done
      attempt=0
      continue
    fi
    sleep 60
  done
}

note "driver started (pid $$), start $START, hourly $HOURLY"
if [ ! -f "$ASSETS/ready.json" ]; then
  run_phase prepare "$RUNS/prepare" || exit $?
fi
check_passed() { python3 -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get("passed") else 1)' "$RUNS/adapter-check.json" 2>/dev/null; }
until check_passed; do
  status adapter_check "clean embed/read of the amendment-1d adapters on one smoke source"
  ( cd "$REPO" && "$VENV/bin/python" scripts/encoder_transfer_adapter_check.py --manifest "$MANIFEST" \
      --assets-root "$ASSETS" --out "$RUNS/adapter-check.json" ) >> "$RUNS/adapter-check.log" 2>&1 && break
  touch "$RUNS/HOLD"
  status hold "adapter check failed; waiting for Claude to fix and remove HOLD"
  note "adapter check failed; holding"
  while [ -f "$RUNS/HOLD" ]; do sleep 60; done
done
if [ "$(outcome "$SMOKE")" != "smoke_completed" ]; then
  run_phase smoke "$SMOKE" || exit $?
fi
if [ "$(outcome "$FULL")" != "completed" ]; then
  run_phase run "$FULL" --smoke-dir "$SMOKE" || exit $?
fi

status packing "results"
(
  cd "$RUNS" &&
  tar -cf stage2a-results.tar stage2a-full/run.json stage2a-full/rows.jsonl stage2a-full/metrics.json \
      stage2a-full/effective-config.json stage2a-full/memory-phases.json stage2a-smoke/run.json \
      stage2a-smoke/rows.jsonl stage2a-smoke/smoke-timing.json driver.log $(ls ./*.log 2>/dev/null) "$ASSETS/download-ledger.json" 2>/dev/null
  tar -cf stage2a-images.tar stage2a-full/images
  sha256sum stage2a-results.tar stage2a-images.tar > stage2a-results.sha256
)
status done "results packed; waiting up to ${FETCH_WINDOW_HOURS} h for FETCHED"
note "results packed"

# Keep the instance (and its disk) until Claude has fetched the results; then stop it from inside
# if vast.ai provides the container key. Stopping keeps the disk; destroying is the user's action.
deadline=$(( $(date +%s) + FETCH_WINDOW_HOURS * 3600 ))
while [ ! -f "$RUNS/FETCHED" ] && [ "$(date +%s)" -lt "$deadline" ]; do sleep 120; done
if [ -n "${CONTAINER_API_KEY:-}" ] && [ -n "${CONTAINER_ID:-}" ] && command -v vastai >/dev/null 2>&1; then
  status stopping "fetched=$( [ -f "$RUNS/FETCHED" ] && echo yes || echo no )"
  note "stopping instance $CONTAINER_ID"
  vastai stop instance "$CONTAINER_ID" --api-key "$CONTAINER_API_KEY" >> "$LOG" 2>&1
else
  status done "results packed; no container key, so the user stops the instance"
fi
