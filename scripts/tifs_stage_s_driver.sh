#!/usr/bin/env bash
# SERVER ONLY. Setup is a separate externally authorized step, never run here.
# Usage: bash scripts/tifs_stage_s_driver.sh ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD [rehearsal|full] [--user-choice PATH] [--selection PATH]
# RUN_ROOT/rehearsal and RUN_ROOT/screen are deliberately disjoint.
# START is the actual instance start shared with setup, Stage P and the freeze;
# never replace it with the time Stage S starts. Default cap is still 15 hours.
# --selection overrides the committed stage-p/selected-config.json if present.
# Choosing Stage P requires a successful selection before this Stage S driver.
set -euo pipefail
[ "$#" -ge 4 ] || { echo 'Expected ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD [rehearsal|full] [--user-choice PATH] [--selection PATH]' >&2; exit 1; }
cd "$(dirname "$0")/.."
PY=${TIFS_PYTHON:-/workspace/venv/bin/python}
ASSETS=$1; RUN_ROOT=$2; START=$3; PRICE=$4
shift 4
MODE=rehearsal
if [ "$#" -gt 0 ] && [[ "$1" != --* ]]; then MODE=$1; shift; fi
case "$MODE" in rehearsal|full) ;; *) echo 'Mode must be rehearsal or full' >&2; exit 1 ;; esac
CONFIG=research/tifs-20261028/stage-s/frozen-config.json
USER_CHOICE=
SELECTION=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --user-choice|--selection)
      [ "$#" -ge 2 ] && [ -n "$2" ] || { echo 'Choice/selection flag requires a path' >&2; exit 1; }
      if [ "$1" = --user-choice ]; then USER_CHOICE=$2; else SELECTION=$2; fi
      shift 2 ;;
    *) echo "Unknown driver argument: $1" >&2; exit 1 ;;
  esac
done
CHOICES=()
if [ -n "$USER_CHOICE" ]; then CHOICES+=(--user-choice "$USER_CHOICE"); fi
if [ -z "$SELECTION" ] && [ -f research/tifs-20261028/stage-p/selected-config.json ]; then
  SELECTION=research/tifs-20261028/stage-p/selected-config.json
fi
if [ -n "$SELECTION" ]; then CHOICES+=(--selection "$SELECTION"); fi
# Stdlib metadata validation only. Do not resolve selection in setup, but every
# runtime/forecast/analyzer below resolves and validates it before science work.
MAX_HOURS=$("$PY" -I - "$CONFIG" "$USER_CHOICE" <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, str(Path('scripts').resolve()))
from tifs_stage_s_setup import setup_choices
print(setup_choices(Path(sys.argv[1]), Path(sys.argv[2]) if sys.argv[2] else None)['max_instance_hours'])
PY
)
mkdir -p "$RUN_ROOT"
RUN_ROOT=$(cd "$RUN_ROOT" && pwd)
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1
# One process at a time owns the GPU. No readers overlap any producer or family.
INCOMPLETE=0
invoke() {
  local logfile=$1; shift
  local rc=0
  "$@" >> "$logfile" 2>&1 || rc=$?
  printf '%s exit=%s log=%s\n' "$(date -u +%FT%TZ)" "$rc" "$logfile" >> "$RUN_ROOT/driver.log"
  case "$rc" in
    0) ;;
    4) INCOMPLETE=1 ;; # Keep failed outcomes and finish the remaining fixed inventory.
    3) exit 3 ;;       # Never retry resource stops or lower the inventory.
    *) exit "$rc" ;; # Baseline/load/dependency failures are never silently bypassed.
  esac
}
run_inventory() {
  local mode=$1
  local out="$RUN_ROOT/$mode"
  mkdir -p "$out"
  local opts=(--assets "$ASSETS" --out "$out" --config "$CONFIG" --instance-start-utc "$START" --max-hours "$MAX_HOURS" --hourly-usd "$PRICE" "${CHOICES[@]}")
  if [ "$mode" = rehearsal ]; then opts+=(--rehearsal); fi
  for action in prepare clean native threats secondary; do
    invoke "$out/$action.log" "$PY" scripts/tifs_stage_s.py --stage "$action" "${opts[@]}"
  done
  invoke "$out/manifest.log" "$PY" scripts/tifs_stage_s.py --stage manifest "${opts[@]}"
  invoke "$out/detect.log" "$PY" scripts/tifs_stage_s_read.py --stage detect "${opts[@]}"
  invoke "$out/quality.log" "$PY" scripts/tifs_stage_s_read.py --stage quality "${opts[@]}"
}
# Every invocation revalidates rehearsal and the time remaining on the ACTUAL instance
# clock. A stale GO file is never used to authorize a later screen/resume.
run_inventory rehearsal
[ "$INCOMPLETE" -eq 0 ] || exit 4
invoke "$RUN_ROOT/forecast.log" "$PY" scripts/tifs_stage_s_forecast.py --rehearsal-out "$RUN_ROOT/rehearsal" --config "$CONFIG" --instance-start-utc "$START" --destination "$RUN_ROOT/forecast.json" "${CHOICES[@]}"
[ "$INCOMPLETE" -eq 0 ] || exit 4
if [ "$MODE" = rehearsal ]; then exit 0; fi
run_inventory screen
RC=0
"$PY" scripts/tifs_stage_s_analyze.py --out "$RUN_ROOT/screen" --config "$CONFIG" "${CHOICES[@]}" >> "$RUN_ROOT/screen/analysis.log" 2>&1 || RC=$?
# Complete frozen analysis alone supplies GO/SCIENTIFIC_KILL. Never infer GO from exit0 stages.
case "$RC" in 0|2|3|4) exit "$RC" ;; *) exit "$RC" ;; esac
