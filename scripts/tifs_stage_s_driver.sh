#!/usr/bin/env bash
# SERVER ONLY. Setup is a separate externally authorized step, never run here.
# Usage: bash scripts/tifs_stage_s_driver.sh ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD [rehearsal|full]
# RUN_ROOT/rehearsal and RUN_ROOT/screen are deliberately disjoint.
set -euo pipefail
[ "$#" -ge 4 ] && [ "$#" -le 5 ] || { echo 'Expected ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD [rehearsal|full]' >&2; exit 1; }
cd "$(dirname "$0")/.."
PY=${TIFS_PYTHON:-/workspace/venv/bin/python}
ASSETS=$1; RUN_ROOT=$2; START=$3; PRICE=$4
MODE=${5:-rehearsal}
case "$MODE" in rehearsal|full) ;; *) echo 'Mode must be rehearsal or full' >&2; exit 1 ;; esac
CONFIG=research/tifs-20261028/stage-s/frozen-config.json
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
  local opts=(--assets "$ASSETS" --out "$out" --config "$CONFIG" --instance-start-utc "$START" --max-hours 15 --hourly-usd "$PRICE")
  if [ "$mode" = rehearsal ]; then opts+=(--rehearsal); fi
  for action in prepare clean native threats secondary; do
    invoke "$out/$action.log" "$PY" scripts/tifs_stage_s.py --stage "$action" "${opts[@]}"
  done
  invoke "$out/manifest.log" "$PY" scripts/tifs_stage_s.py --stage manifest "${opts[@]}"
  for method in f6-noise f6-codec f6-generic f5-r2 v5-r3 wam vine-r; do
    invoke "$out/detect-$method.log" "$PY" scripts/tifs_stage_s_read.py --stage detect --method "$method" "${opts[@]}"
  done
  invoke "$out/quality.log" "$PY" scripts/tifs_stage_s_read.py --stage quality "${opts[@]}"
}
# Every invocation revalidates rehearsal and the time remaining on the ACTUAL instance
# clock. A stale GO file is never used to authorize a later screen/resume.
run_inventory rehearsal
[ "$INCOMPLETE" -eq 0 ] || exit 4
invoke "$RUN_ROOT/forecast.log" "$PY" scripts/tifs_stage_s_forecast.py --rehearsal-out "$RUN_ROOT/rehearsal" --config "$CONFIG" --instance-start-utc "$START" --destination "$RUN_ROOT/forecast.json"
[ "$INCOMPLETE" -eq 0 ] || exit 4
if [ "$MODE" = rehearsal ]; then exit 0; fi
run_inventory screen
RC=0
"$PY" scripts/tifs_stage_s_analyze.py --out "$RUN_ROOT/screen" --config "$CONFIG" >> "$RUN_ROOT/screen/analysis.log" 2>&1 || RC=$?
# Complete frozen analysis alone supplies GO/SCIENTIFIC_KILL. Never infer GO from exit0 stages.
case "$RC" in 0|2|3|4) exit "$RC" ;; *) exit "$RC" ;; esac
